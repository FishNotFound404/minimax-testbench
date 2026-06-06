"""视频 1080P + 运镜指令测试。"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from modules.video import generate_video


def main() -> None:
    out = generate_video(
        prompt=(
            "Aerial view of a misty mountain lake at sunrise, "
            "camera slowly pushes in [Push in] while a wooden boat drifts on the calm water, "
            "cinematic, golden hour lighting"
        ),
        output_path=str(ROOT / "output" / "videos" / "lake_1080p.mp4"),
        model="MiniMax-Hailuo-2.3",
        duration=6,
        resolution="1080P",
    )
    print(f"1080P 视频: {out}")


if __name__ == "__main__":
    main()
