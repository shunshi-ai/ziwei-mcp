"""排盘入口。对应 iztro 的 `src/astro/astro.ts`。"""

from __future__ import annotations

from .calendar import (
    get_ganzhi_by_solar_date,
    get_lunar_cn_string,
    get_sign,
    get_zodiac,
    lunar2solar,
    solar2lunar,
)
from .config import Config, DEFAULT_CONFIG
from .constants import CHINESE_TIME, EARTHLY_BRANCHES, HEAVENLY_STEMS, TIME_RANGE, YIN_INDEX
from .data import EARTHLY_BRANCHES_INFO
from .models import Astrolabe, Palace
from .palace import get_five_elements_class, get_horoscope, get_palace_names, get_soul_and_body
from .stars import (
    get_adjective_star,
    get_boshi12,
    get_changsheng12,
    get_major_star,
    get_minor_star,
    get_yearly12,
)
from .utils import fix_index


def by_solar(
    solar_date: str,
    time_index: int,
    gender: str,
    fix_leap: bool = True,
    config: Config = DEFAULT_CONFIG,
) -> Astrolabe:
    """按阳历排本命盘。

    Args:
        solar_date: ``YYYY-M-D``
        time_index: 时辰序号 0~12（0 早子时，12 晚子时）
        gender: ``男`` 或 ``女``
        fix_leap: 闰月调整——闰月十五之后按下个月算
        config: 流派与分界配置
    """
    if gender not in ("男", "女"):
        raise ValueError(f"gender 只能是 男 / 女，收到 {gender!r}")
    if not 0 <= time_index <= 12:
        raise ValueError(f"time_index 必须在 0~12，收到 {time_index}")

    # 晚子时算当日时，按当日早子时排
    t_index = 0 if (config.day_divide == "current" and time_index >= 12) else time_index

    gz = get_ganzhi_by_solar_date(solar_date, t_index, config)
    stem_of_year, branch_of_year = gz.yearly

    sb = get_soul_and_body(solar_date, t_index, fix_leap, config)
    palace_names = get_palace_names(sb.soul_index)

    major = get_major_star(solar_date, t_index, fix_leap, config)
    minor = get_minor_star(solar_date, t_index, fix_leap, config)
    adjective = get_adjective_star(solar_date, t_index, gender, fix_leap, config)
    changsheng12 = get_changsheng12(solar_date, t_index, gender, fix_leap, config)
    boshi12 = get_boshi12(solar_date, gender, config)
    suiqian12, jiangqian12 = get_yearly12(solar_date, config)
    decadals, ages = get_horoscope(solar_date, t_index, gender, fix_leap, config)

    soul_stem_index = HEAVENLY_STEMS.index(sb.heavenly_stem_of_soul)
    palaces: list[Palace] = []
    for i in range(12):
        stem = HEAVENLY_STEMS[fix_index(soul_stem_index - sb.soul_index + i, 10)]
        branch = EARTHLY_BRANCHES[fix_index(YIN_INDEX + i)]
        palaces.append(Palace(
            index=i,
            name=palace_names[i],
            is_body_palace=sb.body_index == i,
            # 来因宫：宫干与年干相同，且不在子丑二宫（子丑无天干可循）
            is_original_palace=branch not in ("子", "丑") and stem == stem_of_year,
            heavenly_stem=stem,
            earthly_branch=branch,
            major_stars=major[i],
            minor_stars=minor[i],
            adjective_stars=adjective[i],
            changsheng12=changsheng12[i],
            boshi12=boshi12[i],
            jiangqian12=jiangqian12[i],
            suiqian12=suiqian12[i],
            decadal=decadals[i],
            ages=ages[i] or [],
        ))

    branch_of_soul_palace = EARTHLY_BRANCHES[fix_index(sb.soul_index + YIN_INDEX)]
    branch_of_body_palace = EARTHLY_BRANCHES[fix_index(sb.body_index + YIN_INDEX)]

    # 命主：通行本以命宫地支定，中州派以生年年支定
    soul_branch = branch_of_year if config.algorithm == "zhongzhou" else branch_of_soul_palace
    soul = EARTHLY_BRANCHES_INFO[soul_branch]["soul"]
    # 身主：两派一致，均以生年年支定
    body = EARTHLY_BRANCHES_INFO[branch_of_year]["body"]

    return Astrolabe(
        gender=gender,
        solar_date=solar_date,
        lunar_date=get_lunar_cn_string(solar_date),
        chinese_date=str(gz),
        time=CHINESE_TIME[time_index],
        time_range=TIME_RANGE[time_index],
        sign=get_sign(solar_date),
        zodiac=get_zodiac(branch_of_year),
        earthly_branch_of_soul_palace=branch_of_soul_palace,
        earthly_branch_of_body_palace=branch_of_body_palace,
        soul=soul,
        body=body,
        five_elements_class=get_five_elements_class(
            sb.heavenly_stem_of_soul, sb.earthly_branch_of_soul).name,
        palaces=palaces,
        algorithm=config.algorithm,
    )


def by_lunar(
    lunar_date: str,
    time_index: int,
    gender: str,
    is_leap_month: bool = False,
    fix_leap: bool = True,
    config: Config = DEFAULT_CONFIG,
) -> Astrolabe:
    """按农历排本命盘。``lunar_date`` 形如 ``2000-7-17``。"""
    return by_solar(lunar2solar(lunar_date, is_leap_month), time_index, gender, fix_leap, config)
