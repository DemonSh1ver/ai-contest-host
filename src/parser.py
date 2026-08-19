"""排行榜 JSON 解析模块。

解析方式决策：使用 Python 标准库 ``json``，无第三方依赖。

真实排行榜 JSON 字段不固定，故解析层做两层容错：
1. 结构容错：队伍列表可放在 ``teams`` / ``rankings`` / ``rows`` 等任意常见键下；
2. 字段容错：单个队伍记录支持多组字段别名，缺失字段回退默认值。

约定数据格式（详见 data/sample_leaderboard.json）：
{
  "contest": {"name": "竞赛名称", "round": 1},
  "teams": [
    {"rank": 1, "name": "队伍名", "solved": 5, "penalty": 1234, "score": 0.0, "school": ""},
    ...
  ]
}
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Tuple, Union


@dataclass
class Team:
    """单个参赛队伍信息。"""

    rank: int
    name: str
    solved: int = 0
    penalty: int = 0
    score: float = 0.0
    school: str = ""


@dataclass
class Leaderboard:
    """解析后的排行榜数据。"""

    contest_name: str = ""
    round_no: int = 1
    teams: List[Team] = field(default_factory=list)


# 字段别名：标准名 -> 可能的键（按优先级排列，含中英文常见写法）
_RANK_KEYS = ("rank", "ranking", "排名", "名次")
_NAME_KEYS = ("name", "team", "team_name", "队名", "队伍", "名称")
_SOLVED_KEYS = ("solved", "accepted", "pass", "ac", "通过", "解题数")
_PENALTY_KEYS = ("penalty", "time", "罚时")
_SCORE_KEYS = ("score", "points", "分数", "总分")
_SCHOOL_KEYS = ("school", "university", "学校")

# 队伍容器键（顶层可能用这些键之一存队伍列表）
_TEAM_CONTAINER_KEYS = ("teams", "rankings", "rows", "list", "data", "队伍", "榜单")


def _pick(data: dict, keys: Tuple[str, ...]) -> Any:
    """按优先级取字典中第一个存在的键对应的值，取不到返回 None。"""
    for key in keys:
        if key in data:
            return data[key]
    return None


def _to_int(value: Any, default: int) -> int:
    """尽力转 int，失败回退默认值。"""
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _to_float(value: Any, default: float) -> float:
    """尽力转 float，失败回退默认值。"""
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _extract_contest(data: dict) -> Tuple[str, int]:
    """从顶层对象或其 contest 子对象提取竞赛名称与场次。"""
    contest = data.get("contest")
    if not isinstance(contest, dict):
        contest = {}
    name = str(_pick(contest, ("name", "title", "名称", "标题")) or "")
    round_no = _to_int(_pick(contest, ("round", "round_no", "场次", "轮次")), 1)
    return name, round_no


def _parse_team(item: Any) -> Team:
    """解析单条队伍记录，支持字典与简单列表两种形态。"""
    if isinstance(item, dict):
        return Team(
            rank=_to_int(_pick(item, _RANK_KEYS), 0),
            name=str(_pick(item, _NAME_KEYS) or "未知队伍"),
            solved=_to_int(_pick(item, _SOLVED_KEYS), 0),
            penalty=_to_int(_pick(item, _PENALTY_KEYS), 0),
            score=_to_float(_pick(item, _SCORE_KEYS), 0.0),
            school=str(_pick(item, _SCHOOL_KEYS) or ""),
        )
    if isinstance(item, list):
        # 简单列表形态：[rank, name, solved, penalty]
        return Team(
            rank=_to_int(item[0] if len(item) > 0 else None, 0),
            name=str(item[1] if len(item) > 1 else "未知队伍"),
            solved=_to_int(item[2] if len(item) > 2 else None, 0),
            penalty=_to_int(item[3] if len(item) > 3 else None, 0),
        )
    return Team(rank=0, name=str(item) if item else "未知队伍")


def _find_teams_container(data: dict) -> list:
    """在顶层数据中定位队伍列表，找不到返回空列表。"""
    for key in _TEAM_CONTAINER_KEYS:
        value = data.get(key)
        if isinstance(value, list):
            return value
    return []


def parse_leaderboard_text(text: str) -> Leaderboard:
    """从 JSON 字符串解析排行榜。

    抛出 ``json.JSONDecodeError``（JSON 非法）或 ``ValueError``（顶层不是对象）。
    """
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("排行榜 JSON 顶层必须是对象")

    contest_name, round_no = _extract_contest(data)
    teams = [_parse_team(item) for item in _find_teams_container(data)]
    # 保证按名次升序输出（rank 缺失/为 0 的队伍排到最后）
    teams.sort(key=lambda t: t.rank if t.rank > 0 else float("inf"))
    return Leaderboard(contest_name=contest_name, round_no=round_no, teams=teams)


def parse_leaderboard_file(path: Union[str, Path]) -> Leaderboard:
    """从 JSON 文件解析排行榜（自动兼容 UTF-8 BOM）。"""
    return parse_leaderboard_text(Path(path).read_text(encoding="utf-8-sig"))
