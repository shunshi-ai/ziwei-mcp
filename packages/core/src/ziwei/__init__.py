"""shunshi-ziwei —— 紫微斗数排盘引擎（纯计算，无 IO / 无 LLM）。

移植自 iztro (MIT © SylarLong)，并做了三处有意的改动：

1. **配置不再是全局可变状态** —— 逐层显式传递，Web 服务里可以同时服务两个流派。
2. **中州派开关补全** —— 上游的 ``algorithm='zhongzhou'`` 不切四化表
   （庚干仍为「太阴科」），本移植切了。
3. **流派随盘返回** —— ``Astrolabe.algorithm`` 让调用方不必猜这张盘是哪一派排的。
"""

from .astro import by_lunar, by_solar
from .config import Config, DEFAULT_CONFIG
from .constants import CHINESE_TIME, EARTHLY_BRANCHES, HEAVENLY_STEMS, FiveElementsClass
from .models import Astrolabe, Palace, Star
from .utils import get_mutagens_by_stem, time_to_index

__all__ = [
    "by_solar",
    "by_lunar",
    "Config",
    "DEFAULT_CONFIG",
    "Astrolabe",
    "Palace",
    "Star",
    "FiveElementsClass",
    "CHINESE_TIME",
    "HEAVENLY_STEMS",
    "EARTHLY_BRANCHES",
    "time_to_index",
    "get_mutagens_by_stem",
]
