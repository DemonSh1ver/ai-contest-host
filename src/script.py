"""主持词生成。

输入：``Leaderboard``（由 ``src.parser`` 解析得到）。
输出：一段可直接交给 TTS 播报的中文文本。

当前版本：欢迎语 + 动态时间（北京时间）+ 逐队播报名次/队名/题数 + 结束语。
特殊队名读音映射、获奖名单播报等留待后续增强。
"""

from datetime import datetime

from .parser import Leaderboard

_CN_NUM = "零一二三四五六七八九"
_UNITS = ("", "十", "百", "千")


def _number_to_chinese_below_wan(num):
    """将 0 ~ 9999 的整数转为中文读数（不含「万」）。"""
    if num == 0:
        return "零"
    text = str(num)
    out = ""
    zero_pending = False
    for i, ch in enumerate(text):
        digit = int(ch)
        unit = _UNITS[len(text) - 1 - i]
        if digit == 0:
            # 个位 0 不读；中间 / 高位 0 仅在后面还有非零数字时读一次「零」
            zero_pending = bool(unit)
            continue
        if zero_pending:
            out += "零"
            zero_pending = False
        # 避免「一十」直接读作「十」（如 15 -> 十五）
        if not (digit == 1 and unit == "十" and not out):
            out += _CN_NUM[digit]
        out += unit
    return out


def number_to_chinese(num):
    """整数转中文读数（支持任意非负整数，用于播报名次、题数等）。

    示例：0->零，5->五，10->十，15->十五，1020->一千零二十，12345->一万二千三百四十五。
    """
    if num == 0:
        return "零"
    if num < 0:
        return "负" + number_to_chinese(-num)
    if num >= 10000:
        wan = num // 10000
        rest = num % 10000
        result = number_to_chinese(wan) + "万"
        if rest:
            # 余数不足千位时需补「零」，如 10005 -> 一万零五
            if rest < 1000:
                result += "零"
            result += number_to_chinese(rest)
        return result
    return _number_to_chinese_below_wan(num)


# ---------- 滚榜台词变体池 ----------
# 选择策略：按场次/揭晓序号固定轮换（确定性，便于测试与复现），
# 让不同场次、不同队伍听到的开场与悬念台词不完全雷同。

# 开场白（有竞赛名 / 无竞赛名）
_ROLL_OPENERS = (
    "欢迎来到{}第{}场颁奖现场，接下来就是最激动人心的滚榜环节！",
    "欢迎来到{}第{}场颁奖现场！大屏幕准备，滚榜时刻，一触即发！",
    "欢迎来到{}第{}场颁奖现场！接下来，榜单即将滚动，悬念由我们一一揭晓！",
)
_ROLL_OPENERS_NO_NAME = (
    "欢迎来到算法竞赛颁奖现场，接下来就是最激动人心的滚榜环节！",
    "欢迎来到算法竞赛颁奖现场！大屏幕准备，滚榜时刻，一触即发！",
)

# 铺垫语
_ROLL_PRELUDE = (
    "灯光就位，大屏幕准备，心跳加速，悬念即将揭晓。",
    "全场的目光聚焦大屏幕，每一次翻动，都是一次心跳。",
    "滚榜正式开始，让我们屏住呼吸，见证高光时刻！",
)

# 悬念语（按名次位置分组，各组内轮换）
_ROLL_TEASERS_LAST = (
    "首先，我们看向榜单末端，第{}名，会花落谁家呢？",
    "滚榜开启！我们从最后一名开始，第{}名，会是哪支队伍？",
)
_ROLL_TEASERS_MID = (
    "紧接着，战况越来越胶着，第{}名是——",
    "大屏幕上，第{}名的名字开始翻滚，是——",
    "现场气氛愈发紧张，第{}名，花落谁家？",
)
_ROLL_TEASERS_TOP3 = (
    "前三甲呼之欲出，第{}名，悬念拉满——",
    "领奖台近在咫尺，第{}名，究竟是谁？",
)
_ROLL_TEASERS_2ND = (
    "只剩最后两支队伍，亚军之争白热化！第{}名是——",
    "距离王座一步之遥，第{}名，会是他吗？",
)
_ROLL_TEASERS_1ST = (
    "终于到了最终时刻，全场屏住呼吸。本次比赛的冠军，第{}名，究竟是——",
    "全场起立！最终的悬念即将揭晓，本次比赛的冠军，第{}名，究竟是——",
)


def _format_time(now):
    """把时间格式化为中文播报文案（含动态日期与时刻）。"""
    month = number_to_chinese(now.month)
    day = number_to_chinese(now.day)
    hour = number_to_chinese(now.hour)
    minute = number_to_chinese(now.minute)
    if now.minute == 0:
        return "现在是北京时间{}月{}日，{}时整。".format(month, day, hour)
    return "现在是北京时间{}月{}日，{}时{}分。".format(month, day, hour, minute)


def generate_script(lb, now=None):
    """根据排行榜生成完整主持词文本。

    ``now`` 可注入固定时间（用于测试）；默认取当前系统时间，
    因此每次播报的日期与时刻都是动态信息。
    """
    if now is None:
        now = datetime.now()
    lines = []
    if lb.contest_name:
        lines.append("欢迎来到{}第{}场颁奖播报。".format(lb.contest_name, number_to_chinese(lb.round_no)))
    else:
        lines.append("欢迎来到算法竞赛现场。")
    lines.append(_format_time(now))
    lines.append("现在公布本次比赛的排行榜。")
    for team in lb.teams:
        lines.append(
            "第{}名，{}，解出{}题。".format(
                number_to_chinese(team.rank), team.name, number_to_chinese(team.solved)
            )
        )
    lines.append("播报完毕，恭喜各位选手。")
    return "\n".join(lines)


def _reveal_line(team, solved_cn):
    """普通名次的揭晓句（含零题特例，为坚持到底的队伍加戏）。"""
    if team.solved == 0:
        return "{}！虽然一题未解，但坚持到最后一刻，同样值得掌声！".format(team.name)
    return "{}！解出{}题。".format(team.name, solved_cn)


def _champion_line(team, solved_cn):
    """冠军揭晓句。"""
    if team.solved == 0:
        return "{}！冠军诞生！让我们把最热烈的掌声送给他！".format(team.name)
    return "{}！解出{}题！王者登基，让我们把最热烈的掌声送给他！".format(team.name, solved_cn)


def generate_roll_script(lb, now=None):
    """生成「滚榜」式主持词，返回逐段列表，每段单独播报以营造悬念。

    滚榜特色（ICPC / CCPC 颁奖名场面）：从最后一名开始逐队揭晓，
    每队拆成「名次悬念」+「揭晓」两段，中间由 TTS 停顿制造紧张感；
    台词随名次推进递进（榜尾悬念 -> 前三呼之欲出 -> 冠军王座）。

    增强点：
    - 开场 / 铺垫 / 各名次位置台词均有多套变体，按场次与揭晓序号轮换；
    - 连续两支队伍解题数相同时，悬念句强调「罚时决胜」；
    - 零题队伍揭晓时给予「坚持到底」特写。

    ``now`` 可注入固定时间（用于测试）；默认取当前系统时间。
    """
    if now is None:
        now = datetime.now()
    teams = list(lb.teams)
    count = len(teams)
    segments = []
    if lb.contest_name:
        segments.append(_ROLL_OPENERS[lb.round_no % len(_ROLL_OPENERS)].format(
            lb.contest_name, number_to_chinese(lb.round_no)))
    else:
        segments.append(_ROLL_OPENERS_NO_NAME[lb.round_no % len(_ROLL_OPENERS_NO_NAME)])
    segments.append(_format_time(now))
    segments.append(_ROLL_PRELUDE[lb.round_no % len(_ROLL_PRELUDE)])

    for i, team in enumerate(reversed(teams)):  # 从最后一名开始揭晓
        rank_cn = number_to_chinese(team.rank)
        solved_cn = number_to_chinese(team.solved)
        if count == 1:
            segments.append(_ROLL_TEASERS_1ST[i % len(_ROLL_TEASERS_1ST)].format(rank_cn))
            segments.append(_champion_line(team, solved_cn))
        elif i == 0:
            segments.append(_ROLL_TEASERS_LAST[i % len(_ROLL_TEASERS_LAST)].format(rank_cn))
            segments.append(_reveal_line(team, solved_cn))
        elif i == count - 1:
            segments.append(_ROLL_TEASERS_1ST[i % len(_ROLL_TEASERS_1ST)].format(rank_cn))
            segments.append(_champion_line(team, solved_cn))
        elif i == count - 2:
            segments.append(_ROLL_TEASERS_2ND[i % len(_ROLL_TEASERS_2ND)].format(rank_cn))
            segments.append("{}！解出{}题，可惜与冠军擦肩而过。".format(team.name, solved_cn))
        elif i == count - 3:
            segments.append(_ROLL_TEASERS_TOP3[i % len(_ROLL_TEASERS_TOP3)].format(rank_cn))
            segments.append("{}！解出{}题，强势站上领奖台。".format(team.name, solved_cn))
        else:
            prev = teams[count - i]  # 已揭晓的上一位（排名低一位的队伍）
            if team.solved > 0 and prev.solved == team.solved:
                segments.append("同样的解题数，比拼的就是罚时！第{}名是——".format(rank_cn))
            else:
                segments.append(_ROLL_TEASERS_MID[i % len(_ROLL_TEASERS_MID)].format(rank_cn))
            segments.append(_reveal_line(team, solved_cn))
    segments.append("滚榜结束！恭喜所有获奖队伍，我们下一场再会！")
    return segments
