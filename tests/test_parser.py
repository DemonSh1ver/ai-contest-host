"""src.parser 模块单元测试。"""

import json
import unittest

from src.parser import parse_leaderboard_file, parse_leaderboard_text


class TestParseLeaderboardText(unittest.TestCase):
    def test_standard_sample(self):
        lb = parse_leaderboard_text(
            '{"contest": {"name": "测试赛", "round": 1},'
            ' "teams": [{"rank": 1, "name": "甲队", "solved": 5, "penalty": 1234}]}'
        )
        self.assertEqual(lb.contest_name, "测试赛")
        self.assertEqual(lb.round_no, 1)
        self.assertEqual(len(lb.teams), 1)
        team = lb.teams[0]
        self.assertEqual((team.rank, team.name, team.solved, team.penalty), (1, "甲队", 5, 1234))

    def test_chinese_keys_and_defaults(self):
        lb = parse_leaderboard_text('{"队伍":[{"名次":1,"队名":"甲队","通过":3},{"排名":"2","名称":"乙队"}]}')
        self.assertEqual([(t.rank, t.name, t.solved) for t in lb.teams], [(1, "甲队", 3), (2, "乙队", 0)])

    def test_list_entries(self):
        lb = parse_leaderboard_text('{"rankings": [[1,"A",4,800],[2,"B",3,500]]}')
        self.assertEqual(
            [(t.rank, t.name, t.solved, t.penalty) for t in lb.teams],
            [(1, "A", 4, 800), (2, "B", 3, 500)],
        )

    def test_sort_by_rank(self):
        lb = parse_leaderboard_text('{"teams":[{"rank":3,"name":"x"},{"rank":1,"name":"y"}]}')
        self.assertEqual([t.rank for t in lb.teams], [1, 3])

    def test_top_level_must_be_object(self):
        with self.assertRaises(ValueError):
            parse_leaderboard_text("[1,2,3]")

    def test_invalid_json(self):
        with self.assertRaises(json.JSONDecodeError):
            parse_leaderboard_text("{not json")


class TestParseLeaderboardFile(unittest.TestCase):
    def test_sample_file(self):
        lb = parse_leaderboard_file("data/sample_leaderboard.json")
        self.assertEqual(len(lb.teams), 5)
        self.assertEqual(lb.contest_name, "示例高校新生算法竞赛")
        self.assertEqual(lb.teams[0].name, "AC 冲鸭")
        self.assertEqual([t.rank for t in lb.teams], [1, 2, 3, 4, 5])


if __name__ == "__main__":
    unittest.main()
