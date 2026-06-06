"""TTS 多音字测试：pronunciation_dict 临时覆盖读音。"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from modules.tts import text_to_speech


def main() -> None:
    cases = [
        {
            "name": "default",
            "text": "这个数据处理起来有危险，处长说不能马虎。",
            "dict": None,
        },
        {
            "name": "custom",
            "text": "这个数据处理(chu3)(li3)起来有(dangerous)，处长(chu3)(zhang3)说不能马虎。",
            "dict": None,
        },
    ]
    out_dir = ROOT / "output" / "audio"
    for c in cases:
        out = out_dir / f"tts_polyphone_{c['name']}.mp3"
        text_to_speech(
            text=c["text"],
            voice_id="male-qn-qingse",
            model="speech-2.6-hd",
            output_path=str(out),
        )
        print(f"[{c['name']}] -> {out.name}")


if __name__ == "__main__":
    main()
