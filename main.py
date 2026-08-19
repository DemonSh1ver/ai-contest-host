"""程序入口：串联 解析 -> 滚榜 -> 主持词 -> TTS 播放。

用法：
    python main.py                     # 播放 data/sample_leaderboard.json（普通模式）
    python main.py path/to.json        # 播放指定榜单（普通模式）
    python main.py --roll              # 滚榜模式（从最后一名逐队揭晓）
    python main.py path/to.json --roll # 指定榜单 + 滚榜模式
"""

import sys

from src.parser import parse_leaderboard_file
from src.roll import reveal_order
from src.script import generate_script, generate_roll_script
from src.tts import init_engine, speak

DEFAULT_PATH = "data/sample_leaderboard.json"


def main(argv):
    path = DEFAULT_PATH
    roll_mode = False

    for arg in argv:
        if arg == "--roll":
            roll_mode = True
        else:
            path = arg

    lb = parse_leaderboard_file(path)

    if roll_mode:
        steps = reveal_order(lb.teams)
        text = generate_roll_script(lb, steps)
    else:
        text = generate_script(lb)

    print("=" * 40)
    print(text)
    print("=" * 40)

    engine = init_engine()
    speak(engine, text)


if __name__ == "__main__":
    main(sys.argv[1:])
