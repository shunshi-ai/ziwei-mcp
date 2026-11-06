"""规则层单测 —— 不依赖 iztro，纯粹钉住口诀。

对拍 iztro 的测试在 test_vs_iztro.py。
"""

import pytest

import ziwei
from ziwei.config import Config
from ziwei.constants import FiveElementsClass
from ziwei.location import (
    get_gu_gua_index,
    get_huagai_xianchi_index,
    get_huo_ling_index,
    get_kui_yue_index,
    get_lu_yang_tuo_ma_index,
    get_luan_xi_index,
    get_start_index,
)
from ziwei.palace import get_five_elements_class, get_palace_names, get_soul_and_body
from ziwei.utils import (
    fix_earthly_branch_index,
    fix_index,
    get_mutagens_by_stem,
    time_to_index,
)


class TestIndex:
    def test_fix_index_wraps(self):
        assert fix_index(-1) == 11
        assert fix_index(12) == 0
        assert fix_index(13) == 1
        assert fix_index(-1, 10) == 9

    def test_yin_is_origin(self):
        """紫微斗数以寅宫为第一宫，寅的索引必须是 0。"""
        assert fix_earthly_branch_index("寅") == 0
        assert fix_earthly_branch_index("子") == 10
        assert fix_earthly_branch_index("丑") == 11

    @pytest.mark.parametrize("hour,expected", [
        (0, 0),    # 早子时
        (1, 1), (2, 1),
        (9, 5), (10, 5),
        (22, 11),
        (23, 12),  # 晚子时
    ])
    def test_time_to_index(self, hour, expected):
        assert time_to_index(hour) == expected


class TestFiveElements:
    @pytest.mark.parametrize("stem,branch,expected", [
        # 口诀举例：丙子=水二局，辛未=土五局，庚申=木三局
        ("丙", "子", FiveElementsClass.水二局),
        ("辛", "未", FiveElementsClass.土五局),
        ("庚", "申", FiveElementsClass.木三局),
    ])
    def test_nayin(self, stem, branch, expected):
        assert get_five_elements_class(stem, branch) == expected

    def test_value_is_start_age(self):
        """局数即起运虚岁。"""
        assert int(FiveElementsClass.水二局) == 2
        assert int(FiveElementsClass.火六局) == 6


class TestMutagen:
    def test_default_is_tongxingben(self):
        # 庚：阳禄、武权、阴科、同忌
        assert get_mutagens_by_stem("庚") == ("太阳", "武曲", "太阴", "天同")

    def test_zhongzhou_switches_ke(self):
        """中州派开关必须真的切四化表 —— 上游 iztro 这里是漏的。"""
        cfg = Config(algorithm="zhongzhou")
        assert get_mutagens_by_stem("庚", cfg) == ("太阳", "武曲", "天府", "天同")

    def test_divergence_is_only_ke_and_only_three_stems(self):
        """两派分歧【只在科】【只有戊庚壬】—— 这是流派判别的唯一指纹。"""
        zz = Config(algorithm="zhongzhou")
        differing = []
        for stem in "甲乙丙丁戊己庚辛壬癸":
            a, b = get_mutagens_by_stem(stem), get_mutagens_by_stem(stem, zz)
            if a != b:
                differing.append(stem)
                # 差异必须落在索引 2（科）
                assert [i for i in range(4) if a[i] != b[i]] == [2], stem
        assert differing == ["戊", "庚", "壬"]

    def test_user_override_beats_school(self):
        cfg = Config(algorithm="zhongzhou",
                     mutagens={"庚": ("巨门", "巨门", "巨门", "巨门")})
        assert get_mutagens_by_stem("庚", cfg)[2] == "巨门"


class TestStarLocation:
    def test_lu_yang_tuo_are_adjacent(self):
        """禄前羊刃当，禄后陀罗府 —— 擎羊陀罗永远夹着禄存。"""
        for stem in "甲乙丙丁戊己庚辛壬癸":
            r = get_lu_yang_tuo_ma_index(stem, "子")
            assert r.yang_index == fix_index(r.lu_index + 1)
            assert r.tuo_index == fix_index(r.lu_index - 1)

    def test_tianma_only_in_four_horse_palaces(self):
        """天马只落四马地【寅申巳亥】。"""
        allowed = {fix_earthly_branch_index(b) for b in "寅申巳亥"}
        for branch in "子丑寅卯辰巳午未申酉戌亥":
            assert get_lu_yang_tuo_ma_index("甲", branch).ma_index in allowed

    def test_hongluan_tianxi_are_opposite(self):
        """对宫天喜不差移 —— 红鸾天喜恒隔六宫。"""
        for branch in "子丑寅卯辰巳午未申酉戌亥":
            h, x = get_luan_xi_index(branch)
            assert x == fix_index(h + 6)

    def test_kui_yue_cover_all_stems(self):
        for stem in "甲乙丙丁戊己庚辛壬癸":
            k, y = get_kui_yue_index(stem)
            assert k >= 0 and y >= 0, stem

    def test_huo_ling_cover_all_branches(self):
        for branch in "子丑寅卯辰巳午未申酉戌亥":
            h, l = get_huo_ling_index(branch, 0)
            assert h >= 0 and l >= 0, branch

    def test_huagai_xianchi_gugua_cover_all_branches(self):
        for branch in "子丑寅卯辰巳午未申酉戌亥":
            assert all(i >= 0 for i in get_huagai_xianchi_index(branch)), branch
            assert all(i >= 0 for i in get_gu_gua_index(branch)), branch

    def test_ziwei_tianfu_relation(self):
        """天府星位置与紫微星相对。"""
        for day in range(1, 29):
            zi, fu = get_start_index(f"1990-3-{day}", 5)
            assert fu == fix_index(12 - zi)


class TestPalaceNames:
    def test_twelve_unique_names(self):
        names = get_palace_names(0)
        assert len(names) == 12 and len(set(names)) == 12
        assert names[0] == "命宫"

    def test_soul_palace_follows_soul_index(self):
        for soul_index in range(12):
            assert get_palace_names(soul_index)[soul_index] == "命宫"

    def test_order_is_counterclockwise(self):
        """宫名逆时针排：命宫的下一个宫位(顺时针)是父母。"""
        names = get_palace_names(0)
        assert names[1] == "父母"
        assert names[11] == "兄弟"


class TestSchoolDifference:
    """两派在本命盘上的可观测差异，只有这么几处。"""

    DATE, TI, GENDER = "1990-3-24", 5, "男"

    def test_soul_star_source_differs(self):
        """命主：通行本按命宫地支，中州派按生年年支。"""
        a = ziwei.by_solar(self.DATE, self.TI, self.GENDER)
        b = ziwei.by_solar(self.DATE, self.TI, self.GENDER,
                           config=Config(algorithm="zhongzhou"))
        from ziwei.data import EARTHLY_BRANCHES_INFO
        assert a.soul == EARTHLY_BRANCHES_INFO[a.earthly_branch_of_soul_palace]["soul"]
        # 中州派用年支：庚午年 → 午 → 破军
        assert b.soul == EARTHLY_BRANCHES_INFO["午"]["soul"]

    def test_body_star_is_school_agnostic(self):
        """身主两派一致，都按生年年支。"""
        a = ziwei.by_solar(self.DATE, self.TI, self.GENDER)
        b = ziwei.by_solar(self.DATE, self.TI, self.GENDER,
                           config=Config(algorithm="zhongzhou"))
        assert a.body == b.body

    def test_zhongzhou_drops_jielu_kongwang(self):
        """中州派没有截路空亡，改用一颗截空。"""
        b = ziwei.by_solar(self.DATE, self.TI, self.GENDER,
                           config=Config(algorithm="zhongzhou"))
        names = {s.name for p in b.palaces for s in p.adjective_stars}
        assert "截路" not in names and "空亡" not in names
        assert {"截空", "劫杀", "大耗", "龙德"} <= names

    def test_default_has_jielu_kongwang(self):
        a = ziwei.by_solar(self.DATE, self.TI, self.GENDER)
        names = {s.name for p in a.palaces for s in p.adjective_stars}
        assert "截路" in names and "空亡" in names
        assert "截空" not in names

    def test_zhongzhou_renames_dahao_to_suipo(self):
        b = ziwei.by_solar(self.DATE, self.TI, self.GENDER,
                           config=Config(algorithm="zhongzhou"))
        assert "岁破" in {p.suiqian12 for p in b.palaces}
        a = ziwei.by_solar(self.DATE, self.TI, self.GENDER)
        assert "大耗" in {p.suiqian12 for p in a.palaces}

    def test_algorithm_travels_with_the_chart(self):
        """流派随盘返回，调用方不用猜。"""
        assert ziwei.by_solar(self.DATE, self.TI, self.GENDER).algorithm == "default"
        assert ziwei.by_solar(self.DATE, self.TI, self.GENDER,
                              config=Config(algorithm="zhongzhou")).algorithm == "zhongzhou"


class TestDayDivide:
    """晚子时。"""

    def test_forward_differs_from_early_zi(self):
        """默认 forward：晚子时算次日，与当日早子时是两张盘。"""
        early = ziwei.by_solar("1990-3-24", 0, "男")
        late = ziwei.by_solar("1990-3-24", 12, "男")
        assert early.earthly_branch_of_soul_palace != late.earthly_branch_of_soul_palace \
            or [s.name for p in early.palaces for s in p.major_stars] \
            != [s.name for p in late.palaces for s in p.major_stars]

    def test_current_makes_late_zi_same_as_early_zi(self):
        """day_divide='current'：晚子时算当日，退化成当日早子时。"""
        cfg = Config(day_divide="current")
        early = ziwei.by_solar("1990-3-24", 0, "男", config=cfg)
        late = ziwei.by_solar("1990-3-24", 12, "男", config=cfg)
        assert [p.to_dict()["majorStars"] for p in early.palaces] == \
               [p.to_dict()["majorStars"] for p in late.palaces]
        assert early.earthly_branch_of_soul_palace == late.earthly_branch_of_soul_palace

    def test_time_label_still_reflects_late_zi(self):
        """即使按当日排盘，时辰标签仍要显示晚子时，不能骗用户。"""
        a = ziwei.by_solar("1990-3-24", 12, "男", config=Config(day_divide="current"))
        assert a.time == "晚子时" and a.time_range == "23:00~00:00"


class TestYearDivide:
    """年分界 —— 立春 vs 正月初一。"""

    def test_lichun_window_produces_different_year(self):
        """1961-2-4 是立春，但正月初一在 2-15。两种分界给出不同年支。"""
        normal = ziwei.by_solar("1961-2-4", 5, "女")                     # 初一分界
        exact = ziwei.by_solar("1961-2-4", 5, "女",
                               config=Config(year_divide="exact"))       # 立春分界
        assert normal.zodiac == "鼠" and exact.zodiac == "牛"

    def test_outside_window_identical(self):
        """窗口之外两种分界必须一致。"""
        for ds in ("1990-6-15", "2001-9-1", "1975-12-25"):
            a = ziwei.by_solar(ds, 5, "男")
            b = ziwei.by_solar(ds, 5, "男", config=Config(year_divide="exact"))
            assert a.zodiac == b.zodiac, ds


class TestInputValidation:
    def test_reject_bad_gender(self):
        with pytest.raises(ValueError, match="gender"):
            ziwei.by_solar("1990-3-24", 5, "male")

    def test_reject_bad_time_index(self):
        with pytest.raises(ValueError, match="time_index"):
            ziwei.by_solar("1990-3-24", 13, "男")

    def test_reject_bad_config(self):
        with pytest.raises(ValueError, match="流派"):
            Config(algorithm="wangtingzhi")

    def test_config_is_immutable(self):
        """配置不可变 —— 这是我们相对上游全局可变状态的核心改动。"""
        import dataclasses
        cfg = Config()
        with pytest.raises(dataclasses.FrozenInstanceError):
            cfg.algorithm = "zhongzhou"


class TestShape:
    def test_twelve_palaces_full_star_count(self):
        a = ziwei.by_solar("1990-3-24", 5, "男")
        assert len(a.palaces) == 12
        assert sum(len(p.major_stars) for p in a.palaces) == 14
        assert sum(len(p.minor_stars) for p in a.palaces) == 14
        assert sum(len(p.adjective_stars) for p in a.palaces) == 38

    def test_exactly_one_body_palace(self):
        a = ziwei.by_solar("1990-3-24", 5, "男")
        assert sum(1 for p in a.palaces if p.is_body_palace) == 1

    def test_every_palace_has_all_twelve_gods(self):
        a = ziwei.by_solar("1990-3-24", 5, "男")
        for p in a.palaces:
            assert p.changsheng12 and p.boshi12 and p.jiangqian12 and p.suiqian12

    def test_decadals_cover_all_palaces(self):
        a = ziwei.by_solar("1990-3-24", 5, "男")
        assert all(p.decadal is not None for p in a.palaces)
        starts = sorted(p.decadal.range[0] for p in a.palaces)
        # 起运岁 = 五行局，之后每宫 +10
        assert starts == [starts[0] + 10 * i for i in range(12)]

    def test_by_lunar_matches_by_solar(self):
        # 1990 农历二月廿八 == 阳历 1990-3-24
        assert ziwei.by_lunar("1990-2-28", 5, "男").to_dict() == \
               ziwei.by_solar("1990-3-24", 5, "男").to_dict()

    def test_palace_lookup(self):
        a = ziwei.by_solar("1990-3-24", 5, "男")
        assert a.palace("命宫").name == "命宫"
        assert a.palace("身宫").is_body_palace
        assert a.palace("不存在的宫") is None
