"""滚榜揭晓顺序模块（MVP 版）。

本项目的重点是「主持人说话」，滚榜模块只负责一件关键的事：
根据已经给出的最终排行榜，生成「从最后一名到第一名」的倒序揭晓顺序，
供主持词按节奏逐队播报。

MVP 边界（与第 1 天一致）：
- 输入的排行榜 JSON 默认已经是计算完成的最终榜单（rank 即最终名次）；
- 本模块不重新计算得分、排名、罚时；
- 不模拟封榜期间的提交变化；
- 不实现 ICPC 罚时规则。
"""

from dataclasses import dataclass
from typing import List

from .parser import Team


@dataclass
class RollStep:
    """滚榜中的一步：本步揭晓哪一队、揭晓后完整榜单。"""

    step: int               # 第几步（从 1 开始，对应倒序名次）
    revealed_team: str      # 本步揭晓的队伍名
    ranking: List[Team]     # 揭晓后的完整榜单快照（从第 1 名起）


def reveal_order(teams: List[Team]) -> List[RollStep]:
    """给出滚榜的揭晓顺序：从最后一名到第一名，逐步揭晓。

    只根据输入榜单的名次（rank）倒序，不重新计算排名。
    返回每一步的榜单快照（MVP 下每步快照相同，即最终榜单）。
    """
    ordered = sorted(teams, key=lambda t: t.rank if t.rank > 0 else float("inf"))
    steps: List[RollStep] = []

    for idx, team in enumerate(reversed(ordered), start=1):
        steps.append(
            RollStep(
                step=idx,
                revealed_team=team.name,
                ranking=list(ordered),
            )
        )

    return steps


def build_team(name: str, rank: int = 0, solved: int = 0, penalty: int = 0) -> Team:
    """便捷构造一支队伍。"""
    return Team(rank=rank, name=name, solved=solved, penalty=penalty)


def format_ranking(teams: List[Team]) -> str:
    """把榜单格式化为多行文本（名次、队名、过题数、罚时）。"""
    lines = []
    for i, t in enumerate(teams, start=1):
        lines.append(f"第{i}名：{t.name}，解出{t.solved}题，罚时{t.penalty}")
    return "\n".join(lines)


def run_example() -> None:
    """运行一个可复现的滚榜揭晓顺序示例（4 支队伍）。"""
    teams = [
        build_team("AC 冲鸭", rank=1, solved=5, penalty=300),
        build_team("不会就选C", rank=2, solved=4, penalty=260),
        build_team("红名大神", rank=3, solved=4, penalty=400),
        build_team("摸鱼队", rank=4, solved=3, penalty=180),
    ]

    print("=== 最终榜单 ===")
    print(format_ranking(sorted(teams, key=lambda t: t.rank)))
    print()

    steps = reveal_order(teams)
    for s in steps:
        print(f"--- 第 {s.step} 步：揭晓 {s.revealed_team} ---")
        print(format_ranking(s.ranking))
        print()

    print("=== 揭晓顺序 ===")
    print(" -> ".join(s.revealed_team for s in steps))


if __name__ == "__main__":
    run_example()
