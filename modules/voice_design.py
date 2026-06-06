from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from minimax_client import LONG_TIMEOUT, get_client


def design_voice(
    prompt: str,
    preview_text: str,
    voice_id: Optional[str] = None,
) -> Dict[str, Any]:
    """通过自然语言描述生成新音色。"""
    client = get_client()
    payload: Dict[str, Any] = {
        "prompt": prompt,
        "preview_text": preview_text,
    }
    if voice_id:
        payload["voice_id"] = voice_id
    resp = client.post("/v1/voice_design", payload, timeout=LONG_TIMEOUT)
    trial_audio = resp.get("trial_audio")
    if trial_audio:
        out_dir = Path("output/audio")
        out_dir.mkdir(parents=True, exist_ok=True)
        vid = resp.get("voice_id", "designed")
        out = out_dir / f"design_preview_{vid}.mp3"
        try:
            out.write_bytes(bytes.fromhex(trial_audio))
            resp["_preview_path"] = str(out)
        except ValueError:
            pass
    return resp


def synthesize_with_designed_voice(
    text: str,
    voice_id: str,
    output_path: str = "output/audio/designed_output.mp3",
    model: str = "speech-2.6-hd",
    **kwargs: Any,
) -> str:
    """使用已设计的音色合成语音。"""
    from .tts import text_to_speech
    return text_to_speech(
        text=text,
        voice_id=voice_id,
        model=model,
        output_path=output_path,
        **kwargs,
    )
