"""测试视频生成（异步任务，长时等待）。"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from modules.video import generate_video


def main() -> None:
    out = generate_video(
        prompt="A cute orange cat stretches lazily in the warm sunlight, cinematic slow motion, soft bokeh background",
        output_path=str(ROOT / "output" / "videos" / "cat_stretch.mp4"),
        model="MiniMax-Hailuo-2.3",
        duration=6,
        resolution="768P",
    )
    print(f"已生成: {out}")


if __name__ == "__main__":
    main()
