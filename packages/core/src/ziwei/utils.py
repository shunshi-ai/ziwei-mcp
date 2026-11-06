"""索引运算与查表工具。对应 iztro 的 `src/utils/index.ts`。"""

from __future__ import annotations

from .config import Config, DEFAULT_CONFIG
from .constants import EARTHLY_BRANCHES, MUTAGEN, YIN_INDEX
from .data import HEAVENLY_STEMS_INFO, STARS_INFO, ZHONGZHOU_MUTAGEN
from .calendar import solar2lunar


def fix_index(index: int, max_: int = 12) -> int:
    """把索引锁进 ``0 ~ max_-1``。12 是宫位数也是地支数，故为默认值。"""
    return index % max_


def fix_earthly_branch_index(branch: str) -> int:
    """地支 → 宫位索引。宫位从寅宫起算，所以要减去寅的地支序号。"""
    return fix_index(EARTHLY_BRANCHES.index(branch) - YIN_INDEX)


def fix_lunar_month_index(solar_date: str, time_index: int, fix_leap: bool = True) -> int:
    """农历月 → 宫位索引（正月建寅，故正月 → 0）。

    ``fix_leap`` 打开时，闰月**十五之后**按下个月算。
    ⚠️ 晚子时(``time_index == 12``)不做这个调整 —— 上游如此，照抄。
    """
    ld = solar2lunar(solar_date)
    need_add = ld.is_leap and fix_leap and ld.lunar_day > 15 and time_index != 12
    return fix_index(ld.lunar_month + 1 - YIN_INDEX + (1 if need_add else 0))


def fix_lunar_day_index(lunar_day: int, time_index: int) -> int:
    """农历日 → 索引。晚子时已经算作次日，所以不再减一。"""
    return lunar_day if time_index >= 12 else lunar_day - 1


def time_to_index(hour: int) -> int:
    """小时(0~23) → 时辰索引(0~12)。0 点是早子时，23 点是晚子时。"""
    if hour == 0:
        return 0
    if hour == 23:
        return 12
    return (hour + 1) // 2


def get_target_mutagens(stem: str, config: Config = DEFAULT_CONFIG) -> tuple[str, ...]:
    """取该天干的四化表【禄，权，科，忌】。

    优先级：用户自定义 > 流派表 > 通行本。

    ⚠️ 上游 iztro 的 ``algorithm='zhongzhou'`` **不切这一张表**，
    导致开了中州派开关庚干仍是「太阴科」。本移植补上了这一支。
    """
    if stem in config.mutagens:
        return tuple(config.mutagens[stem])
    if config.algorithm == "zhongzhou":
        return ZHONGZHOU_MUTAGEN[stem]
    return tuple(HEAVENLY_STEMS_INFO[stem]["mutagen"])


def get_mutagen(star_name: str, stem: str, config: Config = DEFAULT_CONFIG) -> str:
    """该星在该年干下的四化，没有则返回空串。"""
    target = get_target_mutagens(stem, config)
    return MUTAGEN[target.index(star_name)] if star_name in target else ""


def get_mutagens_by_stem(stem: str, config: Config = DEFAULT_CONFIG) -> tuple[str, ...]:
    """该天干四化的四颗星，顺序为【禄，权，科，忌】。"""
    return get_target_mutagens(stem, config)


def get_brightness(star_name: str, index: int, config: Config = DEFAULT_CONFIG) -> str:
    """星耀在某宫的亮度，无亮度表的星返回空串。"""
    table = config.brightness.get(star_name) or STARS_INFO.get(star_name, {}).get("brightness")
    if not table:
        return ""
    return table[fix_index(index)]


def get_age_index(earthly_branch_of_year: str) -> int:
    """起小限的起始宫位索引。

    小限一年一度逢，男顺女逆不相同，
    寅午戌人辰上起，申子辰人自戌宫，
    巳酉丑人未宫始，亥卯未人起丑宫。
    """
    if earthly_branch_of_year in ("寅", "午", "戌"):
        return fix_earthly_branch_index("辰")
    if earthly_branch_of_year in ("申", "子", "辰"):
        return fix_earthly_branch_index("戌")
    if earthly_branch_of_year in ("巳", "酉", "丑"):
        return fix_earthly_branch_index("未")
    if earthly_branch_of_year in ("亥", "卯", "未"):
        return fix_earthly_branch_index("丑")
    return -1
