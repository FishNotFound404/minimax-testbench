import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from flask import Flask, abort, jsonify, render_template, request, send_from_directory

from config import OUTPUT_DIR
from minimax_client import MiniMaxAPIError
from modules import (
    design_voice,
    generate_image,
    generate_music,
    generate_video,
    list_voices,
    synthesize_with_cloned_voice,
    synthesize_with_designed_voice,
    text_to_speech,
    upload_voice_sample,
)


app = Flask(__name__, static_folder="static", template_folder="templates")


TYPE_DIRS = {
    "audio": "audio",
    "music": "music",
    "images": "images",
    "videos": "videos",
}

MIME_BY_EXT = {
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
}


def _safe_filename(prefix: str, ext: str = ".mp3") -> str:
    return f"{prefix}_{time.strftime('%Y%m%d_%H%M%S')}{ext}"


def _list_dir(sub: str) -> list:
    d = OUTPUT_DIR / sub
    if not d.exists():
        return []
    items = []
    for p in d.iterdir():
        if p.is_file() and not p.name.startswith("."):
            stat = p.stat()
            items.append(
                {
                    "name": p.name,
                    "size": stat.st_size,
                    "mtime": stat.st_mtime,
                    "ext": p.suffix.lower(),
                    "url": f"/files/{sub}/{p.name}",
                }
            )
    items.sort(key=lambda x: x["mtime"], reverse=True)
    return items


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/files")
def api_files():
    return jsonify({key: _list_dir(sub) for key, sub in TYPE_DIRS.items()})


@app.route("/files/<kind>/<path:filename>")
def serve_file(kind, filename):
    if kind not in TYPE_DIRS:
        abort(404)
    return send_from_directory(OUTPUT_DIR / TYPE_DIRS[kind], filename)


@app.route("/api/voices")
def api_voices():
    try:
        voices = list_voices("all")
        return jsonify(
            {
                "system": [v for v in voices.get("system", []) if v.get("voice_id")],
                "cloned": voices.get("cloned", []),
                "generated": voices.get("generated", []),
            }
        )
    except MiniMaxAPIError as e:
        return jsonify({"error": str(e), "code": e.status_code}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/tts", methods=["POST"])
def api_tts():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"ok": False, "error": "文本不能为空"}), 400
    try:
        out = text_to_speech(
            text=text,
            voice_id=data.get("voice_id", "male-qn-qingse"),
            model=data.get("model", "speech-2.6-hd"),
            output_path=str(OUTPUT_DIR / "audio" / _safe_filename("tts_web")),
            speed=float(data.get("speed", 1.0)),
            vol=float(data.get("vol", 1.0)),
            pitch=int(data.get("pitch", 0)),
            emotion=data.get("emotion") or None,
        )
        return jsonify({"ok": True, "path": out, "url": f"/files/audio/{Path(out).name}"})
    except MiniMaxAPIError as e:
        return jsonify({"ok": False, "error": str(e), "code": e.status_code}), 502
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/voice_design", methods=["POST"])
def api_voice_design():
    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()
    preview_text = (data.get("preview_text") or "").strip()
    if not prompt or not preview_text:
        return jsonify({"ok": False, "error": "prompt 和 preview_text 必填"}), 400
    try:
        resp = design_voice(
            prompt=prompt,
            preview_text=preview_text,
            voice_id=(data.get("voice_id") or "").strip() or None,
        )
        voice_id = resp.get("voice_id")
        preview_url = None
        if resp.get("_preview_path"):
            preview_url = f"/files/audio/{Path(resp['_preview_path']).name}"
        return jsonify(
            {
                "ok": True,
                "voice_id": voice_id,
                "preview_url": preview_url,
                "raw": {k: v for k, v in resp.items() if not k.startswith("_")},
            }
        )
    except MiniMaxAPIError as e:
        return jsonify({"ok": False, "error": str(e), "code": e.status_code}), 502
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/voice_design_synth", methods=["POST"])
def api_voice_design_synth():
    data = request.get_json(silent=True) or {}
    voice_id = (data.get("voice_id") or "").strip()
    text = (data.get("text") or "").strip()
    if not voice_id or not text:
        return jsonify({"ok": False, "error": "voice_id 和 text 必填"}), 400
    try:
        out = synthesize_with_designed_voice(
            text=text,
            voice_id=voice_id,
            output_path=str(OUTPUT_DIR / "audio" / _safe_filename("tts_designed")),
        )
        return jsonify({"ok": True, "path": out, "url": f"/files/audio/{Path(out).name}"})
    except MiniMaxAPIError as e:
        return jsonify({"ok": False, "error": str(e), "code": e.status_code}), 502
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/voice_clone", methods=["POST"])
def api_voice_clone():
    data = request.get_json(silent=True) or {}
    voice_id = (data.get("voice_id") or "").strip()
    ref_path = (data.get("ref_path") or "").strip()
    text = (data.get("text") or "这是一段用于克隆的参考音频。").strip()
    if not voice_id or not ref_path:
        return jsonify({"ok": False, "error": "voice_id 和 ref_path 必填"}), 400
    full_ref = (OUTPUT_DIR / "audio" / Path(ref_path).name) if not Path(ref_path).is_absolute() else Path(ref_path)
    if not full_ref.exists():
        return jsonify({"ok": False, "error": f"参考音频不存在: {full_ref}"}), 400
    try:
        resp = upload_voice_sample(
            file_path=str(full_ref),
            voice_id=voice_id,
            text=text,
        )
        if resp.get("base_resp", {}).get("status_code") != 0:
            return jsonify({"ok": False, "error": resp.get("base_resp", {}).get("status_msg", "克隆失败"), "raw": resp}), 400
        out = synthesize_with_cloned_voice(
            text="这是使用克隆音色合成的测试语音。",
            voice_id=voice_id,
            output_path=str(OUTPUT_DIR / "audio" / _safe_filename("tts_cloned")),
        )
        return jsonify(
            {
                "ok": True,
                "voice_id": voice_id,
                "audio_url": f"/files/audio/{Path(out).name}",
            }
        )
    except MiniMaxAPIError as e:
        return jsonify({"ok": False, "error": str(e), "code": e.status_code}), 502
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/music", methods=["POST"])
def api_music():
    data = request.get_json(silent=True) or {}
    try:
        kwargs = {
            "prompt": (data.get("prompt") or "").strip() or None,
            "model": data.get("model", "music-2.6"),
            "is_instrumental": bool(data.get("is_instrumental")),
            "lyrics_optimizer": bool(data.get("lyrics_optimizer")),
            "lyrics": (data.get("lyrics") or "").strip() or None,
            "output_path": str(OUTPUT_DIR / "music" / _safe_filename("music_web", ".mp3")),
        }
        out = generate_music(**kwargs)
        return jsonify({"ok": True, "path": out, "url": f"/files/music/{Path(out).name}"})
    except MiniMaxAPIError as e:
        return jsonify({"ok": False, "error": str(e), "code": e.status_code}), 502
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/music_cover", methods=["POST"])
def api_music_cover():
    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()
    ref_name = (data.get("ref_name") or "").strip()
    if not prompt or not ref_name:
        return jsonify({"ok": False, "error": "prompt 和 ref_name 必填"}), 400
    candidates = list((OUTPUT_DIR / "music").glob("*")) + list((OUTPUT_DIR / "audio").glob("*"))
    ref = next((p for p in candidates if p.name == ref_name), None)
    if not ref:
        return jsonify({"ok": False, "error": f"参考音频不存在: {ref_name}"}), 400
    try:
        out = generate_music(
            prompt=prompt,
            model="music-cover",
            audio_base64_path=str(ref),
            output_path=str(OUTPUT_DIR / "music" / _safe_filename("cover_web", ".mp3")),
            timeout=900,
        )
        return jsonify({"ok": True, "path": out, "url": f"/files/music/{Path(out).name}"})
    except MiniMaxAPIError as e:
        return jsonify({"ok": False, "error": str(e), "code": e.status_code}), 502
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/image", methods=["POST"])
def api_image():
    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()
    if not prompt:
        return jsonify({"ok": False, "error": "prompt 必填"}), 400
    try:
        out = generate_image(
            prompt=prompt,
            output_dir=str(OUTPUT_DIR / "images"),
            model=data.get("model", "image-01"),
            n=int(data.get("n", 1)),
            aspect_ratio=data.get("aspect_ratio", "1:1"),
        )
        return jsonify(
            {
                "ok": True,
                "files": [{"url": f"/files/images/{Path(p).name}", "name": Path(p).name} for p in out],
            }
        )
    except MiniMaxAPIError as e:
        return jsonify({"ok": False, "error": str(e), "code": e.status_code}), 502
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/video", methods=["POST"])
def api_video():
    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()
    if not prompt:
        return jsonify({"ok": False, "error": "prompt 必填"}), 400
    try:
        out = generate_video(
            prompt=prompt,
            output_path=str(OUTPUT_DIR / "videos" / _safe_filename("video_web", ".mp4")),
            model=data.get("model", "MiniMax-Hailuo-2.3"),
            duration=int(data.get("duration", 6)),
            resolution=data.get("resolution", "768P"),
            wait_timeout=900,
        )
        return jsonify({"ok": True, "path": out, "url": f"/files/videos/{Path(out).name}"})
    except MiniMaxAPIError as e:
        return jsonify({"ok": False, "error": str(e), "code": e.status_code}), 502
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "not found"}), 404


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)
