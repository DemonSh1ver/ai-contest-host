"""src.script 模块单元测试。"""

import unittest
from datetime import datetime

from src.parser import Leaderboard, Team
from src.script import generate_roll_script, generate_script, number_to_chinese


class TestNumberToChinese(unittest.TestCase):
    def test_numbers(self):
        cases = {
            0: "零",
            1: "一",
            5: "五",
            10: "十",
            15: "十五",
            20: "二十",
            100: "一百",
            101: "一百零一",
            110: "一百一十",
            1000: "一千",
            1001: "一千零一",
            1020: "一千零二十",
            1234: "一千二百三十四",
            10000: "一万",
            10005: "一万零五",
            12345: "一万二千三百四十五",
        }
        for num, expected in cases.items():
            self.assertEqual(number_to_chinese(num), expected, f"number={num}")

    def test_negative(self):
        self.assertEqual(number_to_chinese(-5), "负五")


class TestGenerateScript(unittest.TestCase):
    def setUp(self):
        self.lb = Leaderboard(
            contest_name="测试赛",
            round_no=1,
            teams=[
                Team(rank=1, name="甲队", solved=5),
                Team(rank=2, name="乙队", solved=3),
            ],
        )

    def test_script_content(self):
        text = generate_script(self.lb)
        self.assertIn("欢迎来到测试赛第一场颁奖播报", text)
        self.assertIn("第一名，甲队，解出五题。", text)
        self.assertIn("第二名，乙队，解出三题。", text)
        self.assertIn("播报完毕，恭喜各位选手。", text)

    def test_no_contest_name(self):
        lb = Leaderboard(teams=[Team(rank=1, name="甲队", solved=1)])
        text = generate_script(lb)
        self.assertIn("欢迎来到算法竞赛现场", text)
        self.assertNotIn("颁奖播报", text)

    def test_dynamic_time_injected(self):
        fixed = datetime(2026, 8, 19, 14, 5)
        text = generate_script(self.lb, now=fixed)
        self.assertIn("现在是北京时间八月十九日，十四时五分。", text)

    def test_dynamic_time_whole_hour(self):
        fixed = datetime(2026, 8, 19, 9, 0)
        text = generate_script(self.lb, now=fixed)
        self.assertIn("现在是北京时间八月十九日，九时整。", text)

    def test_dynamic_time_uses_current_by_default(self):
        text = generate_script(self.lb)
        self.assertIn("现在是北京时间", text)


class TestRollScript(unittest.TestCase):
    def setUp(self):
        self.lb = Leaderboard(
            contest_name="测试赛",
            round_no=1,
            teams=[
                Team(rank=1, name="甲队", solved=5),
                Team(rank=2, name="乙队", solved=3),
                Team(rank=3, name="丙队", solved=2),
            ],
        )

    def test_roll_reveals_last_first(self):
        fixed = datetime(2026, 8, 19, 14, 5)
        segments = generate_roll_script(self.lb, now=fixed)
        # 开场 + 时间 + 铺垫 + 每队2段 + 结束 = 3 + 2*3 + 1
        self.assertEqual(len(segments), 3 + 2 * 3 + 1)
        # 第一段名次悬念提到的是最后一名（第三名）
        self.assertIn("第三名", segments[3])
        # 揭晓顺序：丙队 -> 乙队 -> 甲队
        self.assertIn("丙队", segments[4])
        self.assertIn("乙队", segments[6])
        self.assertIn("甲队", segments[8])
        # 冠军段有悬念与掌声台词
        self.assertIn("冠军", segments[7])
        self.assertIn("掌声", segments[8])

    def test_roll_uses_current_time_by_default(self):
        segments = generate_roll_script(self.lb)
        self.assertIn("现在是北京时间", segments[1])


if __name__ == "__main__":
    unittest.main()
