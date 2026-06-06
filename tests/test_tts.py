"""测试 TTS 语音合成。"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from modules.tts import text_to_speech, list_voices


def main() -> None:
    voices = list_voices("all")
    print(f"系统音色: {len(voices['system'])} 个")
    for v in voices["system"][:5]:
        print(f"  - {v.get('voice_id')} | {v.get('voice_name')}")
    print(f"克隆音色: {len(voices['cloned'])} 个")
    print(f"文生音色: {len(voices['generated'])} 个")

    text = "你好，欢迎使用 MiniMax 多模态能力测试项目。"
    out = text_to_speech(
        text=text,
        voice_id="male-qn-qingse",
        model="speech-2.6-hd",
        output_path=str(ROOT / "output" / "audio" / "tts_hello.mp3"),
    )
    print(f"已生成: {out}")


if __name__ == "__main__":
    main()
