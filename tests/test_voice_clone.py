"""测试音色克隆：先上传参考音频，再用克隆音色合成。"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from modules.voice_clone import synthesize_with_cloned_voice, upload_voice_sample


SAMPLE_AUDIO = ROOT / "samples" / "ref_voice.wav"
CLONE_VOICE_ID = "MyCloneDemo001"


def main() -> None:
    if not SAMPLE_AUDIO.exists():
        print(f"[跳过] 未找到参考音频: {SAMPLE_AUDIO}")
        print("请将一段 10 秒~5 分钟、mp3/m4a/wav 格式的清晰人声放到该路径。")
        return

    print(f"上传参考音频 {SAMPLE_AUDIO} ...")
    resp = upload_voice_sample(
        file_path=str(SAMPLE_AUDIO),
        voice_id=CLONE_VOICE_ID,
        text="这是一段用于克隆的参考音频。",
    )
    print(f"克隆结果: {resp}")

    if resp.get("base_resp", {}).get("status_code") != 0:
        print("克隆接口未通过（可能账号未开通该权限），跳过后续合成。")
        return

    out = synthesize_with_cloned_voice(
        text="这是使用克隆音色合成的测试语音。",
        voice_id=CLONE_VOICE_ID,
        output_path=str(ROOT / "output" / "audio" / "cloned_hello.mp3"),
    )
    print(f"已生成: {out}")


if __name__ == "__main__":
    main()
