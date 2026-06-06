from __future__ import annotations

import base64
import hashlib
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from minimax_client import LONG_TIMEOUT, get_client


def generate_image(
    prompt: str,
    output_dir: str = "output/images",
    model: str = "image-01",
    n: int = 1,
    aspect_ratio: str = "1:1",
    width: Optional[int] = None,
    height: Optional[int] = None,
    seed: Optional[int] = None,
    response_format: str = "url",
    prompt_optimizer: bool = False,
    style_type: Optional[str] = None,
    style_weight: float = 0.8,
) -> List[str]:
    """生成图片，返回保存的文件路径列表。"""
    client = get_client()
    payload: Dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "n": n,
        "response_format": response_format,
        "prompt_optimizer": prompt_optimizer,
    }
    if aspect_ratio:
        payload["aspect_ratio"] = aspect_ratio
    if width and height:
        payload["width"] = width
        payload["height"] = height
    if seed is not None:
        payload["seed"] = seed
    if style_type:
        payload["style"] = {"style_type": style_type, "style_weight": style_weight}

    resp = client.post("/v1/image_generation", payload, timeout=LONG_TIMEOUT)
    data = resp.get("data") or {}

    if response_format == "url" and data.get("image_urls"):
        return _persist_urls(client, data["image_urls"], output_dir, prompt)
    if response_format == "base64" and data.get("image_base64"):
        return _persist_b64(data["image_base64"], output_dir, prompt)

    raise RuntimeError(f"图片生成响应中未找到图片数据: {resp}")


def _prompt_slug(prompt: str) -> str:
    return hashlib.md5(prompt.encode("utf-8")).hexdigest()[:8]


def _persist_urls(client, urls: List[str], output_dir: str, prompt: str) -> List[str]:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    slug = _prompt_slug(prompt)
    saved: List[str] = []
    for idx, url in enumerate(urls):
        path = out_dir / f"{slug}_{stamp}_{idx}.png"
        client.download(url, str(path))
        saved.append(str(path))
    return saved


def _persist_b64(b64_list: List[str], output_dir: str, prompt: str) -> List[str]:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    slug = _prompt_slug(prompt)
    saved: List[str] = []
    for idx, b64 in enumerate(b64_list):
        path = out_dir / f"{slug}_{stamp}_{idx}.png"
        path.write_bytes(base64.b64decode(b64))
        saved.append(str(path))
    return saved
