"""滚榜揭晓顺序模块（简化版）。

本项目的重点是「主持人说话」，滚榜模块只负责一件关键的事：
给出「从最后一名到第一名」的揭晓顺序，供主持词按节奏逐队播报。

封榜与滚榜规则（从简）：
1. 封榜：比赛结束前 60 分钟榜单冻结，封榜期间的提交对外隐藏；
2. 滚榜：从当前榜单最后一名开始，向第一名倒序逐队揭晓；
3. 每揭晓一队，解开该队封榜期间的隐藏提交，更新其过题数；
4. 重排后继续，直到所有队伍揭晓完毕，得到最终排名。

排名规则：过题数多者在前；同题数时罚时少者在前。
罚时计算从简：每条封榜内通过提交按「通过时刻 + 失败次数 × 20」累加，
但这一细节不影响「说话」，仅用于最终排序，故不展开。
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class TeamState:
    """一支队伍的榜单状态。"""

    name: str
    solved: int = 0
    penalty: int = 0


def _sort_key(team: TeamState):
    """排序键：过题数降序、罚时升序。"""
    return (-team.solved, team.penalty)


def _sort_teams(teams: List[TeamState]) -> List[TeamState]:
    """按「过题数降序、罚时升序」排序。"""
    return sorted(teams, key=_sort_key)


@dataclass
class RollStep:
    """滚榜中的一步：本步揭晓哪一队、揭晓后完整榜单。"""

    step: int                     # 第几步（从 1 开始，对应倒序名次）
    revealed_team: str            # 本步揭晓的队伍名
    ranking: List[TeamState]      # 揭晓后的完整榜单（从第 1 名起）


def reveal_order(teams: List[TeamState]) -> List[RollStep]:
    """给出滚榜的揭晓顺序：从最后一名到第一名，逐步揭晓。

    每揭晓一队后重排一次，返回每一步的榜单快照。
    不展开罚时计算细节，只保证揭晓顺序与最终排名正确。
    """
    teams = _sort_teams(list(teams))
    steps: List[RollStep] = []

    # 从最后一名向第一名倒序揭晓
    for idx, team in enumerate(reversed(teams), start=1):
        steps.append(
            RollStep(
                step=idx,
                revealed_team=team.name,
                ranking=_sort_teams(teams),
            )
        )

    return steps


def build_team(name: str, solved: int = 0, penalty: int = 0) -> TeamState:
    """便捷构造一支队伍。"""
    return TeamState(name=name, solved=solved, penalty=penalty)


def format_ranking(teams: List[TeamState]) -> str:
    """把榜单格式化为多行文本（名次、队名、过题数、罚时）。"""
    lines = []
    for i, t in enumerate(teams, start=1):
        lines.append(f"第{i}名：{t.name}，解出{t.solved}题，罚时{t.penalty}")
    return "\n".join(lines)


def run_example() -> None:
    """运行一个可复现的滚榜揭晓顺序示例（4 支队伍）。"""
    teams = [
        build_team("AC 冲鸭", solved=5, penalty=300),
        build_team("不会就选C", solved=4, penalty=260),
        build_team("红名大神", solved=4, penalty=400),
        build_team("摸鱼队", solved=3, penalty=180),
    ]

    print("=== 封榜瞬间榜单 ===")
    print(format_ranking(_sort_teams(teams)))
    print()

    steps = reveal_order(teams)
    for s in steps:
        print(f"--- 第 {s.step} 步：揭晓 {s.revealed_team} ---")
        print(format_ranking(s.ranking))
        print()

    print("=== 最终排名 ===")
    print(format_ranking(steps[-1].ranking))


if __name__ == "__main__":
    run_example()
