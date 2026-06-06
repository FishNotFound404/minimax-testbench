from __future__ import annotations

import base64
from pathlib import Path
from typing import Any, Dict, Optional

from minimax_client import LONG_TIMEOUT, get_client


def generate_music(
    prompt: Optional[str] = None,
    output_path: str = "output/music/music_output.mp3",
    model: str = "music-2.6",
    lyrics: Optional[str] = None,
    is_instrumental: bool = False,
    lyrics_optimizer: bool = False,
    audio_url: Optional[str] = None,
    audio_base64_path: Optional[str] = None,
    audio_format: str = "mp3",
    sample_rate: int = 44100,
    bitrate: int = 256000,
    output_format: str = "hex",
    timeout: Optional[int] = None,
) -> str:
    """生成音乐。"""
    client = get_client()
    payload: Dict[str, Any] = {
        "model": model,
        "stream": False,
        "output_format": output_format,
        "audio_setting": {
            "sample_rate": sample_rate,
            "bitrate": bitrate,
            "format": audio_format,
        },
    }
    if prompt:
        payload["prompt"] = prompt
    if lyrics:
        payload["lyrics"] = lyrics
    if is_instrumental:
        payload["is_instrumental"] = True
    if lyrics_optimizer:
        payload["lyrics_optimizer"] = True
    if audio_url:
        payload["audio_url"] = audio_url
    if audio_base64_path:
        payload["audio_base64"] = base64.b64encode(
            Path(audio_base64_path).read_bytes()
        ).decode("utf-8")

    resp = client.post("/v1/music_generation", payload, timeout=timeout or LONG_TIMEOUT)
    data = resp.get("data") or {}
    if data.get("audio"):
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(bytes.fromhex(data["audio"]))
        return str(out)
    if data.get("status") == 1:
        raise RuntimeError("音乐仍在生成中（hex 模式不会分块，请改用 url 并轮询）。")
    raise RuntimeError(f"音乐生成响应中未找到音频数据: {resp}")
