"""一键启动 minimax-testbench 的 Web UI。

用法：
    python start.py
    py start.py              # Windows Python Launcher

执行步骤：
1. 校验 Python 版本（要求 3.10+）
2. 若 .env 不存在，从 .env.example 复制一份
3. 校验依赖是否已安装；缺失则提示并退出（避免静默安装到全局环境）
4. 启动 app.py，Ctrl+C 退出
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MIN_PY = (3, 10)
APP_ENTRY = ROOT / "app.py"
ENV_FILE = ROOT / ".env"
ENV_EXAMPLE = ROOT / ".env.example"
REQUIREMENTS = ROOT / "requirements.txt"


def info(msg: str) -> None:
    print(f"[start] {msg}")


def warn(msg: str) -> None:
    print(f"[start][warn] {msg}", file=sys.stderr)


def fail(msg: str) -> "None":
    print(f"[start][error] {msg}", file=sys.stderr)
    sys.exit(1)


def check_python() -> None:
    if sys.version_info < MIN_PY:
        major, minor = MIN_PY
        current = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        fail(
            f"需要 Python {major}.{minor}+，当前是 {current}。\n"
            f"  下载：https://www.python.org/downloads/"
        )


def ensure_env() -> None:
    if ENV_FILE.exists():
        return
    if not ENV_EXAMPLE.exists():
        fail(f"找不到 {ENV_EXAMPLE.name}，无法初始化 .env")
    shutil.copy2(ENV_EXAMPLE, ENV_FILE)
    info(f"已从 {ENV_EXAMPLE.name} 复制 .env，请填入 API Key 后重新运行")
    sys.exit(0)


def check_dependencies() -> None:
    try:
        from flask import Flask  # noqa: F401
    except ImportError:
        cmd = f"{sys.executable} -m pip install -r {REQUIREMENTS.name}"
        fail(
            "依赖未安装。\n"
            f"  请先执行：{cmd}"
        )


def run_app() -> int:
    info("启动 Flask Web UI（按 Ctrl+C 停止）")
    info("打开 http://127.0.0.1:5001/ 即可使用")
    return subprocess.call([sys.executable, str(APP_ENTRY)], cwd=str(ROOT))


def main() -> None:
    print("=" * 50)
    print("  minimax-testbench 一键启动")
    print("=" * 50)
    check_python()
    ensure_env()
    check_dependencies()
    raise SystemExit(run_app())


if __name__ == "__main__":
    main()
