from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from minimax_client import LONG_TIMEOUT, get_client


def _save_audio_hex(hex_str: str, output_path: str) -> str:
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(bytes.fromhex(hex_str))
    return str(out)


def text_to_speech(
    text: str,
    voice_id: str = "male-qn-qingse",
    model: str = "speech-2.6-hd",
    output_path: str = "output/audio/tts_output.mp3",
    speed: float = 1.0,
    vol: float = 1.0,
    pitch: int = 0,
    emotion: Optional[str] = None,
    audio_format: str = "mp3",
    sample_rate: int = 32000,
    bitrate: int = 128000,
    channel: int = 1,
    stream: bool = False,
    language_boost: Optional[str] = None,
    output_format: str = "hex",
) -> str:
    """文本转语音，返回音频文件路径。"""
    client = get_client()
    voice_setting: Dict[str, Any] = {
        "voice_id": voice_id,
        "speed": speed,
        "vol": vol,
        "pitch": pitch,
    }
    if emotion:
        voice_setting["emotion"] = emotion
    payload: Dict[str, Any] = {
        "model": model,
        "text": text,
        "stream": stream,
        "voice_setting": voice_setting,
        "audio_setting": {
            "sample_rate": sample_rate,
            "bitrate": bitrate,
            "format": audio_format,
            "channel": channel,
        },
        "output_format": output_format,
    }
    if language_boost:
        payload["language_boost"] = language_boost

    resp = client.post("/v1/t2a_v2", payload, timeout=LONG_TIMEOUT)

    if resp.get("data", {}).get("audio"):
        if output_format == "hex":
            return _save_audio_hex(resp["data"]["audio"], output_path)
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        client.download(resp["data"]["audio"], str(out))
        return str(out)
    if resp.get("data", {}).get("audio_url"):
        return client.download(resp["data"]["audio_url"], output_path)

    raise RuntimeError(f"TTS 响应中未找到音频数据: {resp}")


def list_voices(voice_type: str = "all") -> Dict[str, List[Dict[str, Any]]]:
    """获取当前账号可用的全部音色（系统 + 复刻 + 文生）。"""
    client = get_client()
    resp = client.post(
        "/v1/get_voice",
        {"voice_type": voice_type},
    )
    return {
        "system": resp.get("system_voice", []),
        "cloned": resp.get("voice_cloning", []),
        "generated": resp.get("voice_generation", []),
    }
