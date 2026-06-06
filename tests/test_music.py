"""测试音乐生成。"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from modules.music import generate_music


def main() -> None:
    out = generate_music(
        prompt="独立民谣,忧郁,内省,渴望,独自漫步,咖啡馆",
        lyrics=(
            "[verse]\n"
            "街灯微亮晚风轻抚\n"
            "影子拉长独自漫步\n"
            "旧外套裹着深深忧郁\n"
            "不知去向渴望何处\n"
            "[chorus]\n"
            "推开木门香气弥漫\n"
            "熟悉的角落陌生人看\n"
        ),
        output_path=str(ROOT / "output" / "music" / "indie_folk.mp3"),
        model="music-2.6",
    )
    print(f"已生成: {out}")


if __name__ == "__main__":
    main()
