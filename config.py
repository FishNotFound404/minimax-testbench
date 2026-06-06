import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent
load_dotenv(ROOT_DIR / ".env")

MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "").strip()
MINIMAX_GROUP_ID = os.getenv("MINIMAX_GROUP_ID", "").strip()
MINIMAX_BASE_URL = os.getenv("MINIMAX_BASE_URL", "https://api.minimaxi.com").rstrip("/")
MINIMAX_PAYG_API_KEY = os.getenv("MINIMAX_PAYG_API_KEY", "").strip()

OUTPUT_DIR = ROOT_DIR / "output"

DEFAULT_TIMEOUT = 60
LONG_TIMEOUT = 300

if not MINIMAX_API_KEY or MINIMAX_API_KEY in ("your_api_key_here", "your_token_plan_key_here"):
    print("[WARN] MINIMAX_API_KEY 未配置，请先在 .env 中设置 Token Plan 订阅 Key。")
