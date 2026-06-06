"""音乐自动写词测试：只给 prompt，不传 lyrics，让模型自动写词。"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from modules.music import generate_music


def main() -> None:
    out = generate_music(
        prompt="夏日海边、轻松愉快、清新吉他、男声主唱",
        lyrics=None,
        lyrics_optimizer=True,
        output_path=str(ROOT / "output" / "music" / "summer_optimizer.mp3"),
        model="music-2.6",
    )
    print(f"自动写词版: {out}")

    out2 = generate_music(
        prompt="电子舞曲、节奏强烈、夜晚派对、无歌词纯音乐",
        output_path=str(ROOT / "output" / "music" / "edm_instrumental.mp3"),
        model="music-2.6",
        is_instrumental=True,
    )
    print(f"纯音乐版: {out2}")


if __name__ == "__main__":
    main()
