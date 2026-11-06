"""排盘配置。

⚠️ 与上游 iztro 的一处**有意偏离**：
iztro 把配置存成模块级可变全局（`_algorithm` / `_yearDivide` ...），
在 Web 服务里同时服务两个流派的请求会互相踩。
本移植把配置做成不可变对象，逐层显式传递。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Algorithm = Literal["default", "zhongzhou"]
Divide = Literal["normal", "exact"]
DayDivide = Literal["current", "forward"]
AgeDivide = Literal["normal", "birthday"]


@dataclass(frozen=True)
class Config:
    """紫微排盘配置。默认值与 iztro 2.6.0 对齐。

    algorithm
        ``default``   —— 以《紫微斗数全书》通行本安星（**我们的默认**）
        ``zhongzhou`` —— 以中州派（王亭之）安星

    year_divide
        年干支分界。``normal`` = 正月初一换年柱（紫微传统，iztro 默认）；
        ``exact`` = 立春换年柱（八字传统）。
        ⚠️ 两者最多相差两周多，落在窗口里的人年柱/生肖会不同。

    horoscope_divide
        流耀 / 月干支分界，取值同上。

    day_divide
        ``forward`` —— 晚子时(23:00~24:00)算次日（iztro 默认）
        ``current`` —— 晚子时算当日

    age_divide
        小限分界。``normal`` 只看年份；``birthday`` 以生日为界。
    """

    algorithm: Algorithm = "default"
    year_divide: Divide = "normal"
    horoscope_divide: Divide = "normal"
    day_divide: DayDivide = "forward"
    age_divide: AgeDivide = "normal"

    # 自定义覆盖：{天干: (禄, 权, 科, 忌)}
    mutagens: dict[str, tuple[str, str, str, str]] = field(default_factory=dict)
    # 自定义覆盖：{星名: 12 个亮度}，按宫位地支从寅起
    brightness: dict[str, tuple[str, ...]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.algorithm not in ("default", "zhongzhou"):
            raise ValueError(f"未知流派: {self.algorithm}")
        if self.year_divide not in ("normal", "exact"):
            raise ValueError(f"未知年分界: {self.year_divide}")
        if self.horoscope_divide not in ("normal", "exact"):
            raise ValueError(f"未知流耀分界: {self.horoscope_divide}")
        if self.day_divide not in ("current", "forward"):
            raise ValueError(f"未知日分界: {self.day_divide}")
        if self.age_divide not in ("normal", "birthday"):
            raise ValueError(f"未知小限分界: {self.age_divide}")


DEFAULT_CONFIG = Config()
