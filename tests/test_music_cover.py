"""音乐翻唱测试：music-cover 基于参考音频生成翻唱版本。"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from modules.music import generate_music


def main() -> None:
    sample = ROOT / "output" / "music" / "indie_folk.mp3"
    if not sample.exists():
        print(f"[跳过] 未找到参考音频: {sample}")
        return

    out = generate_music(
        prompt="convert this indie folk into electronic dance music, strong beat, night party vibe",
        model="music-cover",
        audio_base64_path=str(sample),
        output_path=str(ROOT / "output" / "music" / "indie_to_edm_cover.mp3"),
        timeout=900,
    )
    print(f"翻唱生成: {out}")


if __name__ == "__main__":
    main()
