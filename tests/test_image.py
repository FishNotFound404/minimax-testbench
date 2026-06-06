"""测试图片生成。"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from modules.image import generate_image


def main() -> None:
    out = generate_image(
        prompt="赛博朋克风格的城市夜景，霓虹灯反射在湿润的街道上，电影感构图",
        output_dir=str(ROOT / "output" / "images"),
        model="image-01",
        n=1,
        aspect_ratio="16:9",
    )
    for p in out:
        print(f"已生成: {p}")


if __name__ == "__main__":
    main()
