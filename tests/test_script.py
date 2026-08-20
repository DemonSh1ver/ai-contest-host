"""src/script.py 的单元测试。

覆盖主持词生成的两条路径（普通模式 + 滚榜模式）与数字转中文工具函数。
运行方式（在项目根目录执行）：
    python -m unittest discover -s tests -v
"""

import unittest

from src.parser import Leaderboard, Team
from src.roll import reveal_order
from src.script import (
    _num_to_cn,
    _rank_cn,
    _solved_cn,
    generate_script,
    generate_roll_script,
)


def make_team(rank, name, solved, penalty=0):
    return Team(rank=rank, name=name, solved=solved, penalty=penalty)


def make_lb(*teams):
    return Leaderboard(contest_name="示例高校新生算法竞赛", round_no=1, teams=list(teams))


class TestNumToCn(unittest.TestCase):
    """数字转中文读数。"""

    def test_single_digit(self):
        self.assertEqual(_num_to_cn(0), "零")
        self.assertEqual(_num_to_cn(1), "一")
        self.assertEqual(_num_to_cn(9), "九")

    def test_ten(self):
        self.assertEqual(_num_to_cn(10), "十")

    def test_teens(self):
        self.assertEqual(_num_to_cn(11), "十一")
        self.assertEqual(_num_to_cn(19), "十九")

    def test_tens(self):
        self.assertEqual(_num_to_cn(20), "二十")
        self.assertEqual(_num_to_cn(21), "二十一")
        self.assertEqual(_num_to_cn(99), "九十九")

    def test_negative(self):
        self.assertEqual(_num_to_cn(-3), "负三")


class TestRankSolvedCn(unittest.TestCase):
    """名次与题数的中文读法。"""

    def test_rank_cn(self):
        self.assertEqual(_rank_cn(1), "第一名")
        self.assertEqual(_rank_cn(5), "第五名")

    def test_solved_cn(self):
        self.assertEqual(_solved_cn(5), "五题")
        self.assertEqual(_solved_cn(0), "零题")


class TestGenerateScript(unittest.TestCase):
    """普通模式主持词（正序播报）。"""

    def setUp(self):
        self.lb = make_lb(
            make_team(1, "AC 冲鸭", 5, 300),
            make_team(2, "不会就选C", 4, 260),
        )

    def test_contains_all_sections(self):
        text = generate_script(self.lb)
        self.assertIn("各位老师", text)   # 开场（赛后滚榜）
        self.assertIn("滚榜环节", text)   # 开场（赛后滚榜）
        self.assertIn("第一名", text)     # 逐队揭晓
        self.assertIn("冠军", text)       # 结果
        self.assertIn("颁奖", text)       # 颁奖
        self.assertIn("圆满结束", text)   # 结束

    def test_rank_and_solved_in_chinese(self):
        text = generate_script(self.lb)
        self.assertIn("第一名，AC 冲鸭，解出五题", text)

    def test_zero_solved_special_line(self):
        lb = make_lb(make_team(1, "摸鱼队", 0, 0))
        text = generate_script(lb)
        self.assertIn("还没有解出题目", text)

    def test_empty_teams_still_has_opening_and_closing(self):
        text = generate_script(make_lb())
        self.assertIn("各位老师", text)
        self.assertIn("圆满结束", text)


class TestGenerateRollScript(unittest.TestCase):
    """滚榜模式主持词：从最后一名到第一名逐队揭晓。"""

    def test_reveal_from_last_to_first(self):
        lb = make_lb(
            make_team(1, "AC 冲鸭", 5, 300),
            make_team(2, "不会就选C", 4, 260),
            make_team(3, "红名大神", 4, 400),
            make_team(4, "摸鱼队", 3, 180),
        )
        # 与 main.py 用法一致：reveal_order 接收 List[Team]
        steps = reveal_order(lb.teams)
        text = generate_roll_script(lb, steps)

        # 揭晓顺序应为：摸鱼队 -> 红名大神 -> 不会就选C -> AC 冲鸭
        self.assertLess(text.index("摸鱼队"), text.index("红名大神"))
        self.assertLess(text.index("红名大神"), text.index("不会就选C"))
        self.assertLess(text.index("不会就选C"), text.index("AC 冲鸭"))


if __name__ == "__main__":
    unittest.main()
