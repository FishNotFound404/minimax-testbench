from __future__ import annotations

import base64
from pathlib import Path
from typing import Any, Dict

from minimax_client import LONG_TIMEOUT, get_client


def upload_voice_sample(
    file_path: str,
    voice_id: str,
    text: str = "",
    model: str = "speech-2.6-hd",
    need_noise_reduction: bool = False,
    need_volume_normalization: bool = False,
) -> Dict[str, Any]:
    """上传参考音频后做音色快速复刻。

    流程: 1) multipart 上传音频到 /v1/files/upload (purpose=voice_clone)
          2) 拿 file_id 调 /v1/voice_clone
    """
    client = get_client()
    upload_resp = client.upload(
        "/v1/files/upload",
        file_path=file_path,
        purpose="voice_clone",
    )
    file_id = upload_resp.get("file", {}).get("file_id")
    if not file_id:
        raise RuntimeError(f"音频上传失败: {upload_resp}")

    payload: Dict[str, Any] = {
        "file_id": file_id,
        "voice_id": voice_id,
        "need_noise_reduction": need_noise_reduction,
        "need_volume_normalization": need_volume_normalization,
    }
    if text:
        payload["text"] = text
        payload["model"] = model

    clone_resp = client.post("/v1/voice_clone", payload, timeout=LONG_TIMEOUT)
    clone_resp["_file_id"] = file_id
    return clone_resp


def synthesize_with_cloned_voice(
    text: str,
    voice_id: str,
    output_path: str = "output/audio/cloned_output.mp3",
    model: str = "speech-2.6-hd",
    **kwargs: Any,
) -> str:
    """使用已克隆的音色合成语音。"""
    from .tts import text_to_speech
    return text_to_speech(
        text=text,
        voice_id=voice_id,
        model=model,
        output_path=output_path,
        **kwargs,
    )
