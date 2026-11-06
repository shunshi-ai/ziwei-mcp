"""历法层 —— 农历转换与干支纪年。

对应 iztro 依赖的 `lunar-lite`。上游 lunar-lite 建在 `lunar-typescript` 上，
本移植建在同一作者(6tail)的 `lunar-python` 上，两者算法同源、API 同名，
所以这一层是**逐行等价**而不是重新实现历法。
"""

from __future__ import annotations

from dataclasses import dataclass

from lunar_python import Lunar, LunarMonth, LunarYear, Solar

from .config import Config, DEFAULT_CONFIG
from .constants import EARTHLY_BRANCHES, HEAVENLY_STEMS, TIGER_RULE, ZODIAC

# 农历月支固定从寅起（正月建寅）
MONTHLY_EARTHLY_BRANCHES = ("寅", "卯", "辰", "巳", "午", "未",
                            "申", "酉", "戌", "亥", "子", "丑")


@dataclass(frozen=True)
class LunarDate:
    lunar_year: int
    lunar_month: int   # 恒为正数，是否闰月看 is_leap
    lunar_day: int
    is_leap: bool

    def __str__(self) -> str:
        return f"{self.lunar_year}-{self.lunar_month}-{self.lunar_day}"


@dataclass(frozen=True)
class GanZhiDate:
    """四柱干支。每项为 (天干, 地支)。"""

    yearly: tuple[str, str]
    monthly: tuple[str, str]
    daily: tuple[str, str]
    hourly: tuple[str, str]

    def __str__(self) -> str:
        return " ".join("".join(p) for p in
                        (self.yearly, self.monthly, self.daily, self.hourly))


def normalize_date(date_str: str) -> tuple[int, int, int]:
    """把 ``YYYY-M-D`` / ``YYYY/M/D`` / ``YYYY.M.D`` 拆成三个整数。"""
    parts = [p for p in date_str.replace("/", "-").replace(".", "-").split("-") if p]
    if len(parts) < 3:
        raise ValueError(f"无法解析日期: {date_str!r}")
    return int(parts[0]), int(parts[1]), int(parts[2])


def solar2lunar(date_str: str) -> LunarDate:
    y, m, d = normalize_date(date_str)
    lunar = Solar.fromYmd(y, m, d).getLunar()
    return LunarDate(
        lunar_year=lunar.getYear(),
        lunar_month=abs(lunar.getMonth()),
        lunar_day=lunar.getDay(),
        is_leap=lunar.getMonth() < 0,
    )


def lunar2solar(date_str: str, is_leap_month: bool = False) -> str:
    y, m, d = normalize_date(date_str)
    lunar = Lunar.fromYmd(y, m, d)
    leap_month = LunarYear.fromYear(lunar.getYear()).getLeapMonth()
    if leap_month > 0 and leap_month == m and is_leap_month:
        lunar = Lunar.fromYmd(y, -m, d)
    solar = lunar.getSolar()
    return f"{solar.getYear()}-{solar.getMonth()}-{solar.getDay()}"


def get_total_days_of_lunar_month(date_str: str) -> int:
    """该阳历日期所在**农历月**的总天数（29 或 30）。"""
    ld = solar2lunar(date_str)
    month = LunarMonth.fromYm(ld.lunar_year,
                              -ld.lunar_month if ld.is_leap else ld.lunar_month)
    return month.getDayCount() if month else 0


def get_zodiac(earthly_branch_of_year: str) -> str:
    return ZODIAC[EARTHLY_BRANCHES.index(earthly_branch_of_year)]


def get_sign(date_str: str) -> str:
    """星座。"""
    y, m, d = normalize_date(date_str)
    return Solar.fromYmd(y, m, d).getXingZuo() + "座"


def _fix_stem_index(index: int) -> int:
    return index % 10


def _monthly_ganzhi(yearly_gan: str, lunar, divide: str) -> tuple[str, str]:
    """月干支。

    ``exact`` 按节气（交节换月）；``normal`` 按农历初一换月，自己起五虎遁。
    """
    if divide == "exact":
        return (lunar.getMonthGanExact(), lunar.getMonthZhiExact())

    # 闰月且过十五，按下个月算
    fix_leap = 1 if (lunar.getMonth() < 0 and lunar.getDay() > 15) else 0
    month_abs = abs(lunar.getMonth())
    gan = HEAVENLY_STEMS[
        _fix_stem_index(HEAVENLY_STEMS.index(TIGER_RULE[yearly_gan]) + month_abs - 1 + fix_leap)
    ]
    zhi = MONTHLY_EARTHLY_BRANCHES[month_abs - 1 + fix_leap]
    return (gan, zhi)


def get_ganzhi_by_solar_date(
    date_str: str,
    time_index: int,
    config: Config = DEFAULT_CONFIG,
) -> GanZhiDate:
    """阳历 → 四柱干支。

    ⚠️ 与 lunar-lite 完全一致的两个细节，改了就对不上盘：
    1. 小时取 ``max(time_index * 2 - 1, 0)``、分钟固定 30
       （即取时辰的中点，避开边界）
    2. 日柱用 ``getDayGanExact``（23:00 换日），不是 ``getDayGan``
    """
    y, m, d = normalize_date(date_str)
    hour = max(time_index * 2 - 1, 0)
    lunar = Solar.fromYmdHms(y, m, d, hour, 30, 0).getLunar()

    if config.year_divide == "normal":
        yearly = (lunar.getYearGan(), lunar.getYearZhi())
    else:
        yearly = (lunar.getYearGanByLiChun(), lunar.getYearZhiByLiChun())

    return GanZhiDate(
        yearly=yearly,
        monthly=_monthly_ganzhi(yearly[0], lunar, config.horoscope_divide),
        daily=(lunar.getDayGanExact(), lunar.getDayZhiExact()),
        hourly=(lunar.getTimeGan(), lunar.getTimeZhi()),
    )


def get_lunar_cn_string(date_str: str) -> str:
    """农历中文串，如 ``一九九〇年二月廿八``。"""
    y, m, d = normalize_date(date_str)
    return Solar.fromYmd(y, m, d).getLunar().toString()
