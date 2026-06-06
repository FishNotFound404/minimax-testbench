"""测试声音设计：通过自然语言描述生成新音色。"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from modules.voice_design import design_voice, synthesize_with_designed_voice


def main() -> None:
    resp = design_voice(
        prompt="温柔知性的青年女性，声音略带磁性，语速平稳，适合深夜电台。",
        preview_text="晚上好，今天我们来聊聊星空与梦想。",
    )
    print(f"声音设计结果: {resp}")
    voice_id = resp.get("voice_id")
    if not voice_id:
        print("未获得 voice_id，跳过合成。")
        return

    out = synthesize_with_designed_voice(
        text="这段话用我们刚刚设计的音色来朗读。",
        voice_id=voice_id,
        output_path=str(ROOT / "output" / "audio" / f"designed_{voice_id}.mp3"),
    )
    print(f"已生成: {out}")


if __name__ == "__main__":
    main()
