"""主持词生成模块。

依据「AI 算法竞赛主持人」Prompt 规范实现，职责是：根据榜单数据与滚榜
揭晓顺序，生成可直接交给 TTS 引擎播报的中文主持词。

严格遵守以下约束：
- 每句话尽量简短，避免过长复合句；
- 不使用 Markdown、表格、代码、表情符号；
- 数字、英文缩写尽量转成适合中文朗读的表达（如「第 5 名」->「第五名」）；
- 不编造选手姓名、成绩、排名等任何事实，信息不足时使用通用主持词；
- 按「捆绑顺序」生成：开场 -> 逐队揭晓（滚榜）-> 结果 -> 颁奖 -> 结束。

输出为纯文本字符串，可直接交给 TTS。
"""

from typing import List

from .parser import Leaderboard, Team
from .roll import RollStep, _sort_teams


# 数字转中文读数，用于把「第 5 名」「5 题」读成「第五名」「五题」
_CN_NUM = "零一二三四五六七八九"


def _num_to_cn(num: int) -> str:
    """把 0 ~ 99 的整数转成中文读数（用于名次、题数等小数字）。"""
    if num < 0:
        return "负" + _num_to_cn(-num)
    if num < 10:
        return _CN_NUM[num]
    if num < 20:
        return "十" + ("" if num == 10 else _CN_NUM[num % 10])
    tens = _CN_NUM[num // 10]
    ones = _CN_NUM[num % 10]
    return tens + "十" + ("" if num % 10 == 0 else ones)


def _rank_cn(rank: int) -> str:
    """名次的中文读法：第 1 名 -> 第一名。"""
    return "第" + _num_to_cn(rank) + "名"


def _solved_cn(solved: int) -> str:
    """题数的中文读法：5 题 -> 五题。"""
    return _num_to_cn(solved) + "题"


# ---------- 各环节主持词 ----------

def _opening(lb: Leaderboard) -> str:
    """开场：简短介绍比赛，调动现场气氛。"""
    if lb.contest_name:
        return f"各位选手，大家好！欢迎来到{lb.contest_name}比赛现场。比赛即将开始，请各位选手做好准备。"
    return "各位选手，大家好！欢迎来到本次算法竞赛现场。比赛即将开始，请各位选手做好准备。"


def _reveal_line(team: Team) -> str:
    """逐队揭晓句：报出队名与成绩，适合朗读。"""
    if team.solved == 0:
        return f"{_rank_cn(team.rank)}，{team.name}。虽然还没有解出题目，但坚持到最后，同样值得掌声。"
    return f"{_rank_cn(team.rank)}，{team.name}，解出{_solved_cn(team.solved)}。"


def _result_line(lb: Leaderboard) -> str:
    """结果：只播报真实结果（冠军队伍）。"""
    if lb.teams:
        champion = lb.teams[0]
        return f"经过激烈角逐，比赛结果已经产生。让我们恭喜冠军队伍，{champion.name}！"
    return "经过激烈角逐，本轮比赛结果已经产生。让我们恭喜取得优异成绩的选手。"


def _award_line(lb: Leaderboard) -> str:
    """颁奖：播报前三名（如有）。"""
    top = lb.teams[:3]
    if not top:
        return "接下来进入颁奖环节。让我们为所有获奖选手鼓掌。"
    names = "、".join(t.name for t in top)
    return f"接下来进入颁奖环节。让我们把掌声送给{names}！"


def _closing() -> str:
    """结束：简短总结并感谢选手。"""
    return "本次算法竞赛到这里就圆满结束了。感谢各位选手的精彩表现，我们下次再见！"


# ---------- 主入口 ----------

def generate_script(lb: Leaderboard) -> str:
    """按「捆绑顺序」生成完整主持词：开场 -> 逐队揭晓 -> 结果 -> 颁奖 -> 结束。

    逐队揭晓按榜单正序（第 1 名到第 N 名）播报，适合非滚榜场景。
    返回可直接交给 TTS 的纯文本，各句之间用换行分隔。
    """
    lines: List[str] = [_opening(lb)]

    for team in lb.teams:
        lines.append(_reveal_line(team))

    lines.append(_result_line(lb))
    lines.append(_award_line(lb))
    lines.append(_closing())
    return "\n".join(lines)


def generate_roll_script(lb: Leaderboard, steps: List[RollStep]) -> str:
    """按「滚榜」方式生成主持词：从最后一名到第一名逐队揭晓。

    依据 ``roll.reveal_order`` 给出的揭晓顺序，每揭晓一队播报一句，
    依次营造悬念与氛围。最终同样以结果、颁奖、结束收尾。

    返回可直接交给 TTS 的纯文本。
    """
    lines: List[str] = [_opening(lb)]

    for step in steps:
        # 按揭晓顺序找到该队当前状态
        team = next((t for t in step.ranking if t.name == step.revealed_team), None)
        if team is None:
            continue
        lines.append(_reveal_line(team))

    lines.append(_result_line(lb))
    lines.append(_award_line(lb))
    lines.append(_closing())
    return "\n".join(lines)
