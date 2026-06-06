from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, Optional

from minimax_client import LONG_TIMEOUT, get_client


VALID_STATUS_SUCCESS = {"success"}
VALID_STATUS_FAIL = {"fail"}
VALID_STATUS_PENDING = {"preparing", "queueing", "processing"}


def generate_video(
    prompt: str,
    output_path: str = "output/videos/video_output.mp4",
    model: str = "MiniMax-Hailuo-2.3",
    duration: int = 6,
    resolution: str = "768P",
    prompt_optimizer: bool = True,
    wait_timeout: int = 1800,
    poll_interval: float = 8.0,
) -> str:
    """提交视频生成任务并等待完成，返回视频文件路径。"""
    client = get_client()
    payload: Dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "duration": duration,
        "resolution": resolution,
        "prompt_optimizer": prompt_optimizer,
    }
    resp = client.post("/v1/video_generation", payload, timeout=LONG_TIMEOUT)
    task_id = resp.get("task_id")
    if not task_id:
        raise RuntimeError(f"视频生成提交失败: {resp}")
    return _poll_video_task(client, task_id, output_path, wait_timeout, poll_interval)


def query_video_task(task_id: str) -> Dict[str, Any]:
    """查询单个视频生成任务状态。"""
    client = get_client()
    return client.get("/v1/query/video_generation", {"task_id": task_id})


def retrieve_video_file(file_id: int) -> Dict[str, Any]:
    """通过 file_id 拿到视频下载链接。"""
    client = get_client()
    return client.get("/v1/files/retrieve", {"file_id": file_id})


def _poll_video_task(
    client,
    task_id: str,
    output_path: str,
    timeout: int,
    interval: float,
) -> str:
    deadline = time.time() + timeout
    last_resp: Dict[str, Any] = {}
    while time.time() < deadline:
        time.sleep(interval)
        last_resp = query_video_task(task_id)
        status = (last_resp.get("status") or "").lower()
        if status in VALID_STATUS_SUCCESS:
            file_id = last_resp.get("file_id")
            if not file_id:
                raise RuntimeError(f"任务完成但未返回 file_id: {last_resp}")
            file_resp = retrieve_video_file(int(file_id))
            download_url = (file_resp.get("file") or {}).get("download_url")
            if not download_url:
                raise RuntimeError(f"未拿到下载链接: {file_resp}")
            out = Path(output_path)
            out.parent.mkdir(parents=True, exist_ok=True)
            return client.download(download_url, str(out))
        if status in VALID_STATUS_FAIL:
            raise RuntimeError(f"视频生成任务失败: {last_resp}")
        print(f"  ... 视频任务 {task_id} 状态: {status}")
    raise TimeoutError(f"等待视频生成任务超时: {task_id}，最后响应: {last_resp}")
