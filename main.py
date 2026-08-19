"""算法竞赛 AI 智能主持人 - 程序入口。

完整链路：排行榜 JSON → 数据解析 → 生成主持词 → TTS 语音 → 播放。

用法：
    python main.py                 # 普通播报（默认样例数据）
    python main.py 榜单.json        # 播报指定榜单
    python main.py --roll          # 滚榜模式（逐队揭晓，营造悬念）
"""

import argparse
import sys
import time

from src.parser import parse_leaderboard_file
from src.script import generate_roll_script, generate_script
from src.tts import init_engine, speak


def main():
    parser = argparse.ArgumentParser(description="算法竞赛 AI 智能主持人")
    parser.add_argument("json_path", nargs="?", default="data/sample_leaderboard.json",
                        help="排行榜 JSON 文件路径（默认样例数据）")
    parser.add_argument("--roll", action="store_true",
                        help="启用滚榜模式：从最后一名开始逐队揭晓，营造悬念")
    args = parser.parse_args()

    try:
        leaderboard = parse_leaderboard_file(args.json_path)
    except FileNotFoundError:
        print(f"找不到排行榜文件：{args.json_path}")
        sys.exit(1)
    except ValueError as exc:
        print(f"排行榜 JSON 解析失败：{exc}")
        sys.exit(1)

    engine = init_engine()

    if args.roll:
        segments = generate_roll_script(leaderboard)
        print("===== 滚榜主持词（逐段播报）=====")
        for seg in segments:
            print(seg)
        print("==================================")
        for seg in segments:
            speak(engine, seg)
            # 段间停顿，配合 TTS 让悬念/揭晓节奏更明显
            time.sleep(1.2)
    else:
        text = generate_script(leaderboard)
        print("===== 主持词 =====")
        print(text)
        print("==================")
        speak(engine, text)


if __name__ == "__main__":
    main()
