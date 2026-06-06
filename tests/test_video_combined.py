"""视频组合运镜测试：[左摇,推进] + 自然语言描述。"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from modules.video import generate_video


def main() -> None:
    out = generate_video(
        prompt=(
            "A futuristic cityscape at night, neon signs reflect on wet streets, "
            "camera starts low and pushes forward [Push in] while slowly panning left [Pan left], "
            "flying cars pass overhead, cinematic anamorphic lens, 8K detail"
        ),
        output_path=str(ROOT / "output" / "videos" / "city_combo.mp4"),
        model="MiniMax-Hailuo-2.3",
        duration=6,
        resolution="1080P",
    )
    print(f"组合运镜 1080P: {out}")


if __name__ == "__main__":
    main()
