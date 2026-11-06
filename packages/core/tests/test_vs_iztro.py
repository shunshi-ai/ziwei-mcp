"""对拍上游 iztro。

两层：
1. **冻结黄金样本**（默认跑）—— 值由 py-iztro 生成并提交进仓库，
   不需要装 py-iztro / pythonmonkey 也能跑，CI 里就是这一层在守。
2. **实时对拍**（装了 py-iztro 才跑）—— 随机盘逐字段比，用于本地改动后自检。

⚠️ py-iztro 打包的是 iztro **2.5.0**，其默认 `yearDivide` / `horoscopeDivide`
都是 `exact`；上游在 2.6.0 把默认改成了 `normal`。我们按 2.6.0 port，
所以对拍时必须显式把配置调回 2.5.0 的基准，否则差的是基准不是算法。
"""

import json
from pathlib import Path

import pytest

import ziwei
from ziwei.config import Config

GOLDEN = Path(__file__).parent / "golden_iztro_2_5_0.json"
CFG_2_5_0 = Config(year_divide="exact", horoscope_divide="exact")


def _norm_ours(a: ziwei.Astrolabe) -> dict:
    """我们的输出 → 与黄金样本同一种中性形状。"""
    d = a.to_dict()
    d.pop("algorithm", None)      # 上游没有这个字段，是我们加的
    for p in d["palaces"]:
        for kind in ("majorStars", "minorStars", "adjectiveStars"):
            p[kind] = [[s["name"], s.get("brightness", ""), s.get("mutagen", "")]
                       for s in p[kind]]
    return d


def _load():
    return json.loads(GOLDEN.read_text(encoding="utf-8"))


def _case_id(c):
    return f"{c['tag']}-{c['solarDate']}-t{c['timeIndex']}-{c['gender']}"


_DATA = _load()


@pytest.mark.parametrize("case", _DATA["cases"], ids=_case_id)
def test_matches_golden(case):
    ours = _norm_ours(ziwei.by_solar(
        case["solarDate"], case["timeIndex"], case["gender"], config=CFG_2_5_0))
    assert ours == case["expected"]


def test_golden_covers_every_edge_class():
    """黄金样本必须覆盖到所有已知易错面，少一类就是测试在退化。"""
    tags = {c["tag"] for c in _DATA["cases"]}
    required = {"全时辰", "立春窗口", "初一窗口", "晚子时", "农历月末", "区间端点"}
    assert required <= tags, f"缺少覆盖: {required - tags}"
    assert any(t.startswith("闰") for t in tags), "缺少闰月覆盖"
    # 全时辰 0~12 一个不能少
    assert {c["timeIndex"] for c in _DATA["cases"]} == set(range(13))


def test_golden_config_matches_what_we_compare_with():
    """防止有人改了黄金样本的基准却没改这里的配置。"""
    cfg = _DATA["config"]
    assert cfg["year_divide"] == CFG_2_5_0.year_divide
    assert cfg["horoscope_divide"] == CFG_2_5_0.horoscope_divide
    assert cfg["algorithm"] == CFG_2_5_0.algorithm
    assert cfg["day_divide"] == CFG_2_5_0.day_divide


# ── 实时对拍（可选） ────────────────────────────────────────────────

try:
    from py_iztro import Astro as _Astro
    _HAS_IZTRO = True
except Exception:
    _HAS_IZTRO = False


@pytest.mark.skipif(not _HAS_IZTRO, reason="未安装 py-iztro，跳过实时对拍")
def test_live_random_sample():
    """随机 200 盘实时对拍。本地改完算法先跑这个。"""
    import datetime
    import random

    astro = _Astro()
    rnd = random.Random(20260902)
    start = datetime.date(1920, 1, 1).toordinal()
    end = datetime.date(2050, 12, 31).toordinal()

    for _ in range(200):
        d = datetime.date.fromordinal(rnd.randint(start, end))
        ds = f"{d.year}-{d.month}-{d.day}"
        ti = rnd.randint(0, 12)
        g = rnd.choice(["男", "女"])
        ours = _norm_ours(ziwei.by_solar(ds, ti, g, config=CFG_2_5_0))
        theirs = json.loads(json.dumps(
            _norm_theirs(astro.by_solar(ds, ti, g)), ensure_ascii=False))
        assert ours == theirs, f"{ds} t{ti} {g}"


def _norm_theirs(r) -> dict:
    def stars(lst):
        return [[s.name, getattr(s, "brightness", "") or "", getattr(s, "mutagen", "") or ""]
                for s in lst]
    return {
        "gender": r.gender, "solarDate": r.solar_date, "lunarDate": r.lunar_date,
        "chineseDate": r.chinese_date, "time": r.time, "timeRange": r.time_range,
        "sign": r.sign, "zodiac": r.zodiac,
        "earthlyBranchOfSoulPalace": r.earthly_branch_of_soul_palace,
        "earthlyBranchOfBodyPalace": r.earthly_branch_of_body_palace,
        "soul": r.soul, "body": r.body, "fiveElementsClass": r.five_elements_class,
        "palaces": [{
            "index": p.index, "name": p.name,
            "isBodyPalace": p.is_body_palace, "isOriginalPalace": p.is_original_palace,
            "heavenlyStem": p.heavenly_stem, "earthlyBranch": p.earthly_branch,
            "majorStars": stars(p.major_stars), "minorStars": stars(p.minor_stars),
            "adjectiveStars": stars(p.adjective_stars),
            "changsheng12": p.changsheng12, "boshi12": p.boshi12,
            "jiangqian12": p.jiangqian12, "suiqian12": p.suiqian12,
            "decadal": None if p.decadal is None else {
                "range": list(p.decadal.range),
                "heavenlyStem": p.decadal.heavenly_stem,
                "earthlyBranch": p.decadal.earthly_branch},
            "ages": list(p.ages),
        } for p in r.palaces],
    }
