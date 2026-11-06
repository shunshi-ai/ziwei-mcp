"""输出数据模型。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from .palace import Decadal

StarType = Literal["major", "soft", "tough", "adjective", "flower", "helper", "lucun", "tianma"]
Scope = Literal["origin", "decadal", "yearly", "monthly", "daily", "hourly"]


@dataclass
class Star:
    name: str
    type: StarType
    scope: Scope = "origin"
    brightness: str = ""
    mutagen: str = ""

    def to_dict(self) -> dict:
        d = {"name": self.name, "type": self.type, "scope": self.scope}
        if self.brightness:
            d["brightness"] = self.brightness
        if self.mutagen:
            d["mutagen"] = self.mutagen
        return d


@dataclass
class Palace:
    index: int
    name: str
    is_body_palace: bool
    is_original_palace: bool          # 来因宫
    heavenly_stem: str
    earthly_branch: str
    major_stars: list[Star] = field(default_factory=list)
    minor_stars: list[Star] = field(default_factory=list)
    adjective_stars: list[Star] = field(default_factory=list)
    changsheng12: str = ""
    boshi12: str = ""
    jiangqian12: str = ""
    suiqian12: str = ""
    decadal: Decadal | None = None
    ages: list[int] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "name": self.name,
            "isBodyPalace": self.is_body_palace,
            "isOriginalPalace": self.is_original_palace,
            "heavenlyStem": self.heavenly_stem,
            "earthlyBranch": self.earthly_branch,
            "majorStars": [s.to_dict() for s in self.major_stars],
            "minorStars": [s.to_dict() for s in self.minor_stars],
            "adjectiveStars": [s.to_dict() for s in self.adjective_stars],
            "changsheng12": self.changsheng12,
            "boshi12": self.boshi12,
            "jiangqian12": self.jiangqian12,
            "suiqian12": self.suiqian12,
            "decadal": None if self.decadal is None else {
                "range": list(self.decadal.range),
                "heavenlyStem": self.decadal.heavenly_stem,
                "earthlyBranch": self.decadal.earthly_branch,
            },
            "ages": self.ages,
        }


@dataclass
class Astrolabe:
    """一张本命盘。"""

    gender: str
    solar_date: str
    lunar_date: str
    chinese_date: str
    time: str
    time_range: str
    sign: str
    zodiac: str
    earthly_branch_of_soul_palace: str
    earthly_branch_of_body_palace: str
    soul: str                 # 命主
    body: str                 # 身主
    five_elements_class: str
    palaces: list[Palace]
    algorithm: str            # 本盘用的流派，随盘带走，别让调用方猜

    def palace(self, name: str) -> Palace | None:
        """按宫名取宫。``身宫`` 是标记不是宫名，单独处理。"""
        if name == "身宫":
            return next((p for p in self.palaces if p.is_body_palace), None)
        return next((p for p in self.palaces if p.name == name), None)

    def to_dict(self) -> dict:
        return {
            "gender": self.gender,
            "solarDate": self.solar_date,
            "lunarDate": self.lunar_date,
            "chineseDate": self.chinese_date,
            "time": self.time,
            "timeRange": self.time_range,
            "sign": self.sign,
            "zodiac": self.zodiac,
            "earthlyBranchOfSoulPalace": self.earthly_branch_of_soul_palace,
            "earthlyBranchOfBodyPalace": self.earthly_branch_of_body_palace,
            "soul": self.soul,
            "body": self.body,
            "fiveElementsClass": self.five_elements_class,
            "algorithm": self.algorithm,
            "palaces": [p.to_dict() for p in self.palaces],
        }
