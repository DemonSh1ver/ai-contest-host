"""排行榜 JSON 解析模块（简化版）。

选型：Python 标准库 ``json``，零第三方依赖。

本项目的重点是「主持人说话」（主持词 + 播报），解析只是入口，保持简单：
- 约定榜单就是 ``teams`` 键下的队伍列表，每队含 rank / name / solved / penalty；
- 只做最基础的字段读取，不做过度容错。

约定数据格式（详见 data/sample_leaderboard.json）：
{
  "contest": {"name": "竞赛名称", "round": 1},
  "teams": [
    {"rank": 1, "name": "队伍名", "solved": 5, "penalty": 1234}
  ]
}
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Union

# 实际用例队伍数量上限（项目报告要求至少 3 支、不超过 5 支）
MAX_TEAMS = 5


@dataclass
class Team:
    """单个参赛队伍信息。"""

    rank: int
    name: str
    solved: int = 0
    penalty: int = 0


@dataclass
class Leaderboard:
    """解析后的排行榜数据。"""

    contest_name: str = ""
    round_no: int = 1
    teams: List[Team] = field(default_factory=list)


def parse_leaderboard_text(text: str) -> Leaderboard:
    """从 JSON 字符串解析排行榜。"""
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("排行榜 JSON 顶层必须是对象")

    contest = data.get("contest") or {}
    name = str(contest.get("name", ""))
    round_no = int(contest.get("round", 1))

    teams_raw = data.get("teams", [])
    if not isinstance(teams_raw, list):
        raise ValueError(
            f"排行榜 JSON 的 teams 必须是列表，实际为 {type(teams_raw).__name__}"
        )

    teams = []
    for item in teams_raw:
        teams.append(
            Team(
                rank=int(item.get("rank", 0)),
                name=str(item.get("name", "未知队伍")),
                solved=int(item.get("solved", 0)),
                penalty=int(item.get("penalty", 0)),
            )
        )

    if len(teams) > MAX_TEAMS:
        raise ValueError(f"队伍数量超过上限（最多 {MAX_TEAMS} 支），实际 {len(teams)} 支")

    teams.sort(key=lambda t: t.rank if t.rank > 0 else float("inf"))
    return Leaderboard(contest_name=name, round_no=round_no, teams=teams)


def parse_leaderboard_file(path: Union[str, Path]) -> Leaderboard:
    """从 JSON 文件解析排行榜。"""
    return parse_leaderboard_text(Path(path).read_text(encoding="utf-8-sig"))
