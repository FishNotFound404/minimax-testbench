"""一键启动 minimax-testbench 的 Web UI。

用法：
    python start.py
    py start.py              # Windows Python Launcher
    uv run start.py          # uv 模式下：自动同步依赖并启动

执行步骤：
1. 若 .env 不存在，从 .env.example 复制一份并提示用户填入 API Key
2. 优先使用 uv：执行 `uv run python app.py`，uv 会按需同步依赖
3. 回退：若未安装 uv，则要求系统已通过 pip 安装好依赖，再启动 app.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APP_ENTRY = ROOT / "app.py"
ENV_FILE = ROOT / ".env"
ENV_EXAMPLE = ROOT / ".env.example"


def info(msg: str) -> None:
    print(f"[start] {msg}")


def warn(msg: str) -> None:
    print(f"[start][warn] {msg}", file=sys.stderr)


def fail(msg: str) -> "None":
    print(f"[start][error] {msg}", file=sys.stderr)
    sys.exit(1)


def which(cmd: str) -> str | None:
    return shutil.which(cmd)


def ensure_env() -> None:
    if ENV_FILE.exists():
        return
    if not ENV_EXAMPLE.exists():
        fail(f"找不到 {ENV_EXAMPLE.name}，无法初始化 .env")
    shutil.copy2(ENV_EXAMPLE, ENV_FILE)
    info(f"已从 {ENV_EXAMPLE.name} 复制 .env，请填入 API Key 后重新运行")
    sys.exit(0)


def run_with_uv() -> int:
    info("使用 uv 启动：uv run 会按需同步 pyproject.toml 中的依赖")
    info("打开 http://127.0.0.1:5001/ 即可使用")
    return subprocess.call(["uv", "run", "python", str(APP_ENTRY)], cwd=str(ROOT))


def run_with_pip() -> int:
    try:
        from flask import Flask  # noqa: F401
    except ImportError:
        fail(
            "未检测到 uv，且依赖未安装。\n"
            "  推荐：先安装 uv (https://docs.astral.sh/uv/) 后重新运行；\n"
            f"  或者：{sys.executable} -m pip install -r {ROOT / 'pyproject.toml'}"
        )
    info("启动 Flask Web UI（按 Ctrl+C 停止）")
    info("打开 http://127.0.0.1:5001/ 即可使用")
    return subprocess.call([sys.executable, str(APP_ENTRY)], cwd=str(ROOT))


def main() -> None:
    print("=" * 50)
    print("  minimax-testbench 一键启动")
    print("=" * 50)
    ensure_env()
    if which("uv"):
        raise SystemExit(run_with_uv())
    warn("未检测到 uv，将使用系统 Python 启动。")
    warn("推荐安装 uv 以获得自动依赖同步：https://docs.astral.sh/uv/")
    raise SystemExit(run_with_pip())


if __name__ == "__main__":
    main()
