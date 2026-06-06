"""TTS 多音色+情绪对比测试。"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from modules.tts import list_voices, text_to_speech


def main() -> None:
    voices = list_voices("system")
    target_voices = {
        "male-qn-qingse": "清澈男声",
        "female-shaonv": "少女音",
        "Chinese (Mandarin)_News_Anchor": "新闻女声",
    }
    available_ids = {v["voice_id"] for v in voices["system"]}
    use_voices = {k: v for k, v in target_voices.items() if k in available_ids}

    text = "今天的天气真好，我们一起去公园散步吧。"
    out_dir = ROOT / "output" / "audio"
    out_dir.mkdir(parents=True, exist_ok=True)

    for vid, label in use_voices.items():
        slug = vid.split("_")[-1].lower()
        path = out_dir / f"tts_{slug}_neutral.mp3"
        text_to_speech(
            text=text,
            voice_id=vid,
            model="speech-2.6-hd",
            output_path=str(path),
        )
        print(f"[neutral] {label} ({vid}) -> {path.name}")

    emotions = ["happy", "sad", "angry"]
    for emo in emotions:
        path = out_dir / f"tts_qingse_{emo}.mp3"
        text_to_speech(
            text=text,
            voice_id="male-qn-qingse",
            model="speech-2.6-hd",
            output_path=str(path),
            emotion=emo,
        )
        print(f"[emotion={emo}] -> {path.name}")


if __name__ == "__main__":
    main()
