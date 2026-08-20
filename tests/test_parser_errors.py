"""src/parser.py 的异常输入测试。

Day 3 任务：记录 parser 在非法 JSON / 错误 teams 类型下的真实失败结果。
所有用例均以 parser 实际抛出的异常类型与错误信息为准，不做虚构。
运行方式：
    python -m unittest discover -s tests -v
"""

import json
import unittest

from src.parser import parse_leaderboard_text


class TestParserFailureCases(unittest.TestCase):
    """parser 异常输入下的真实失败结果。"""

    def test_invalid_json_raises_json_decode_error(self):
        with self.assertRaises(json.JSONDecodeError) as ctx:
            parse_leaderboard_text("{bad json")
        # 真实失败信息片段
        self.assertIn("Expecting property name", str(ctx.exception))

    def test_top_level_not_object_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            parse_leaderboard_text("[1, 2, 3]")
        self.assertEqual(str(ctx.exception), "排行榜 JSON 顶层必须是对象")

    def test_teams_not_list_int_raises_value_error(self):
        """teams 类型错误（int）：错误信息明确指出实际类型。"""
        with self.assertRaises(ValueError) as ctx:
            parse_leaderboard_text('{"teams": 123}')
        self.assertEqual(
            str(ctx.exception),
            "排行榜 JSON 的 teams 必须是列表，实际为 int",
        )

    def test_teams_not_list_string_raises_value_error(self):
        """teams 类型错误（str）：错误信息明确指出实际类型。"""
        with self.assertRaises(ValueError) as ctx:
            parse_leaderboard_text('{"teams": "not a list"}')
        self.assertEqual(
            str(ctx.exception),
            "排行榜 JSON 的 teams 必须是列表，实际为 str",
        )

    def test_too_many_teams_raises_value_error(self):
        """队伍数量超上限（6 支 > 5 支上限）。"""
        text = (
            '{"teams":['
            + ",".join('{"rank":%d,"name":"t%d"}' % (i, i) for i in range(1, 7))
            + "]}"
        )
        with self.assertRaises(ValueError) as ctx:
            parse_leaderboard_text(text)
        msg = str(ctx.exception)
        self.assertIn("队伍数量超过上限", msg)
        self.assertIn("实际 6 支", msg)

    def test_missing_teams_returns_empty_leaderboard(self):
        """teams 缺失：返回空榜单，不报错。"""
        lb = parse_leaderboard_text("{}")
        self.assertEqual(lb.teams, [])
        self.assertEqual(lb.contest_name, "")

    def test_missing_team_fields_use_defaults(self):
        """单队所有字段缺失：使用默认值。"""
        lb = parse_leaderboard_text('{"teams":[{}]}')
        t = lb.teams[0]
        self.assertEqual(t.rank, 0)
        self.assertEqual(t.name, "未知队伍")
        self.assertEqual(t.solved, 0)
        self.assertEqual(t.penalty, 0)


if __name__ == "__main__":
    unittest.main()