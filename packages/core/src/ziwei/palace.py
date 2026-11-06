"""命宫 / 身宫 / 五行局 / 十二宫名 / 大限小限。

对应 iztro 的 `src/astro/palace.ts`。
"""

from __future__ import annotations

from dataclasses import dataclass

from .calendar import get_ganzhi_by_solar_date
from .config import Config, DEFAULT_CONFIG
from .constants import (
    EARTHLY_BRANCHES,
    GENDER_YIN_YANG,
    HEAVENLY_STEMS,
    PALACES,
    TIGER_RULE,
    YIN_INDEX,
    FiveElementsClass,
)
from .data import EARTHLY_BRANCHES_INFO
from .utils import fix_earthly_branch_index, fix_index, fix_lunar_month_index, get_age_index


@dataclass(frozen=True)
class SoulAndBody:
    soul_index: int
    body_index: int
    heavenly_stem_of_soul: str
    earthly_branch_of_soul: str


@dataclass(frozen=True)
class Decadal:
    """大限。"""

    range: tuple[int, int]
    heavenly_stem: str
    earthly_branch: str


def get_soul_and_body(
    solar_date: str,
    time_index: int,
    fix_leap: bool = True,
    config: Config = DEFAULT_CONFIG,
    from_palace: tuple[str, str] | None = None,
) -> SoulAndBody:
    """定命宫与身宫。

    1. 定寅首（五虎遁）：甲己年起丙寅，乙庚年起戊寅，丙辛年起庚寅，
       丁壬年起壬寅，戊癸年起甲寅。
    2. 安命身宫诀：寅起正月，顺数至生月，**逆**数生时为命宫；
       寅起正月，顺数至生月，**顺**数生时为身宫。

    ``from_palace`` 传入 (天干, 地支) 时，以该地支为命宫重排（地盘 / 人盘用）。
    """
    gz = get_ganzhi_by_solar_date(solar_date, time_index, config)
    earthly_branch_of_time = gz.hourly[1]
    heavenly_stem_of_year = gz.yearly[0]

    month_index = fix_lunar_month_index(solar_date, time_index, fix_leap)
    time_branch_index = EARTHLY_BRANCHES.index(earthly_branch_of_time)

    soul_index = fix_index(month_index - time_branch_index)
    body_index = fix_index(month_index + time_branch_index)

    if from_palace is not None:
        soul_index = fix_earthly_branch_index(from_palace[1])
        body_offset = (0, 2, 4, 6, 8, 10, 0, 2, 4, 6, 8, 10, 0)
        body_index = fix_index(body_offset[time_index] + soul_index)

    # 用五虎遁取寅宫天干，再顺数到命宫
    start_stem = TIGER_RULE[heavenly_stem_of_year]
    stem_index = fix_index(HEAVENLY_STEMS.index(start_stem) + soul_index, 10)

    return SoulAndBody(
        soul_index=soul_index,
        body_index=body_index,
        heavenly_stem_of_soul=HEAVENLY_STEMS[stem_index],
        earthly_branch_of_soul=EARTHLY_BRANCHES[fix_index(soul_index + YIN_INDEX)],
    )


def get_five_elements_class(heavenly_stem: str, earthly_branch: str) -> FiveElementsClass:
    """定五行局（以命宫干支纳音而定）。

    纳音取数口诀：
      甲乙丙丁一到五，子丑午未一来数，
      寅卯申酉二上走，辰巳戌亥三为足。
      干支相加多减五，五行木金水火土。

    干支数相加，超过 5 则减 5：
      1 木三局 · 2 金四局 · 3 水二局 · 4 火六局 · 5 土五局
    """
    table = (
        FiveElementsClass.木三局,
        FiveElementsClass.金四局,
        FiveElementsClass.水二局,
        FiveElementsClass.火六局,
        FiveElementsClass.土五局,
    )
    stem_number = HEAVENLY_STEMS.index(heavenly_stem) // 2 + 1
    branch_number = fix_index(EARTHLY_BRANCHES.index(earthly_branch), 6) // 2 + 1

    index = stem_number + branch_number
    while index > 5:
        index -= 5
    return table[index - 1]


def get_palace_names(soul_index: int) -> tuple[str, ...]:
    """从寅宫开始的十二宫名。"""
    return tuple(PALACES[fix_index(i - soul_index)] for i in range(12))


def get_horoscope(
    solar_date: str,
    time_index: int,
    gender: str,
    fix_leap: bool = True,
    config: Config = DEFAULT_CONFIG,
    from_palace: tuple[str, str] | None = None,
) -> tuple[list[Decadal | None], list[list[int] | None]]:
    """起大限与小限。

    大限由命宫起，**阳男阴女顺行，阴男阳女逆行**，每十年过一宫。
    起运虚岁 = 五行局数。
    """
    gz = get_ganzhi_by_solar_date(solar_date, time_index, config)
    stem_of_year, branch_of_year = gz.yearly

    sb = get_soul_and_body(solar_date, time_index, fix_leap, config, from_palace)
    base_stem = from_palace[0] if from_palace else sb.heavenly_stem_of_soul
    base_branch = from_palace[1] if from_palace else sb.earthly_branch_of_soul
    five_elements = get_five_elements_class(base_stem, base_branch)

    start_stem = TIGER_RULE[stem_of_year]
    forward = GENDER_YIN_YANG[gender] == EARTHLY_BRANCHES_INFO[branch_of_year]["yin_yang"]

    decadals: list[Decadal | None] = [None] * 12
    for i in range(12):
        idx = fix_index(sb.soul_index + i) if forward else fix_index(sb.soul_index - i)
        start = int(five_elements) + 10 * i
        stem_index = fix_index(HEAVENLY_STEMS.index(start_stem) + idx, 10)
        branch_index = fix_index(YIN_INDEX + idx)
        decadals[idx] = Decadal(
            range=(start, start + 9),
            heavenly_stem=HEAVENLY_STEMS[stem_index],
            earthly_branch=EARTHLY_BRANCHES[branch_index],
        )

    # 小限：男顺女逆（注意这里看的是性别本身，不是阴阳男女）
    age_index = get_age_index(branch_of_year)
    ages: list[list[int] | None] = [None] * 12
    for i in range(12):
        age = [12 * j + i + 1 for j in range(10)]
        idx = fix_index(age_index + i) if gender == "男" else fix_index(age_index - i)
        ages[idx] = age

    return decadals, ages
