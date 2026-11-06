"""星耀落宫索引。对应 iztro 的 `src/star/location.ts`。

本模块只算「第几宫」，不产出星耀对象；所有索引都以**寅宫为 0**。
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass

from .calendar import get_ganzhi_by_solar_date, get_total_days_of_lunar_month, solar2lunar
from .config import Config, DEFAULT_CONFIG
from .constants import EARTHLY_BRANCHES, HEAVENLY_STEMS, PALACES, YIN_INDEX
from .palace import get_five_elements_class, get_soul_and_body
from .utils import (
    fix_earthly_branch_index,
    fix_index,
    fix_lunar_day_index,
    fix_lunar_month_index,
)


def _horoscope_config(config: Config) -> Config:
    """流耀专用配置。

    ⚠️ 上游刻意如此：流年神煞与年系杂耀取年干支时用的是 ``horoscopeDivide``，
    而命宫 / 主星取年干支用的是 ``yearDivide``。两者可以不同，别合并。
    """
    return dataclasses.replace(config, year_divide=config.horoscope_divide)


# ── 紫微 / 天府 ─────────────────────────────────────────────────────

def get_start_index(
    solar_date: str,
    time_index: int,
    fix_leap: bool = True,
    config: Config = DEFAULT_CONFIG,
    from_palace: tuple[str, str] | None = None,
) -> tuple[int, int]:
    """起紫微星诀 → (紫微索引, 天府索引)。

    - 六五四三二，酉午亥辰丑，
    - 局数除日数，商数宫前走；
    - 若见数无余，便要起虎口，
    - 日数小于局，还直宫中守。
    """
    sb = get_soul_and_body(solar_date, time_index, fix_leap, config)
    lunar_day = solar2lunar(solar_date).lunar_day

    base_stem = from_palace[0] if from_palace else sb.heavenly_stem_of_soul
    base_branch = from_palace[1] if from_palace else sb.earthly_branch_of_soul
    five_elements_value = int(get_five_elements_class(base_stem, base_branch))

    # 晚子时算次日 → 农历日 +1；若溢出当月则跨月
    day = lunar_day + 1 if (time_index == 12 and config.day_divide != "current") else lunar_day
    max_days = get_total_days_of_lunar_month(solar_date)
    if day > max_days:
        day -= max_days

    offset = -1
    remainder = -1
    quotient = 0
    while remainder != 0:
        offset += 1
        divisor = day + offset
        quotient = divisor // five_elements_value
        remainder = divisor % five_elements_value

    quotient %= 12
    ziwei_index = quotient - 1
    # 补数为偶则顺行，为奇则逆回
    ziwei_index += offset if offset % 2 == 0 else -offset
    ziwei_index = fix_index(ziwei_index)

    # 天府与紫微相对
    tianfu_index = fix_index(12 - ziwei_index)
    return ziwei_index, tianfu_index


# ── 年干系 ──────────────────────────────────────────────────────────

@dataclass(frozen=True)
class LuYangTuoMa:
    lu_index: int
    yang_index: int
    tuo_index: int
    ma_index: int


def get_lu_yang_tuo_ma_index(stem: str, branch: str) -> LuYangTuoMa:
    """禄存、擎羊、陀罗（按年干）与天马（按年支）。

    - 甲禄到寅宫，乙禄居卯府。丙戊禄在巳，丁己禄在午。
    - 庚禄定居申，辛禄酉上补。壬禄亥中藏，癸禄居子户。
    - 禄前羊刃当，禄后陀罗府。

    天马只落四马地【寅申巳亥】：
    - 寅午戌流马在申，申子辰流马在寅，巳酉丑流马在亥，亥卯未流马在巳。
    """
    ma_map = {
        ("寅", "午", "戌"): "申",
        ("申", "子", "辰"): "寅",
        ("巳", "酉", "丑"): "亥",
        ("亥", "卯", "未"): "巳",
    }
    ma_index = 0
    for group, target in ma_map.items():
        if branch in group:
            ma_index = fix_earthly_branch_index(target)
            break

    lu_map = {"甲": "寅", "乙": "卯", "丙": "巳", "戊": "巳", "丁": "午",
              "己": "午", "庚": "申", "辛": "酉", "壬": "亥", "癸": "子"}
    lu_index = fix_earthly_branch_index(lu_map[stem])

    return LuYangTuoMa(
        lu_index=lu_index,
        yang_index=fix_index(lu_index + 1),
        tuo_index=fix_index(lu_index - 1),
        ma_index=ma_index,
    )


def get_kui_yue_index(stem: str) -> tuple[int, int]:
    """天魁天钺（按年干）。

    甲戊庚之年丑未，乙己之年子申，辛年午寅，壬癸之年卯巳，丙丁之年亥酉。
    """
    table = {
        ("甲", "戊", "庚"): ("丑", "未"),
        ("乙", "己"): ("子", "申"),
        ("辛",): ("午", "寅"),
        ("丙", "丁"): ("亥", "酉"),
        ("壬", "癸"): ("卯", "巳"),
    }
    for group, (kui, yue) in table.items():
        if stem in group:
            return fix_earthly_branch_index(kui), fix_earthly_branch_index(yue)
    return -1, -1


# ── 月系 / 时系 ─────────────────────────────────────────────────────

def get_zuo_you_index(lunar_month: int) -> tuple[int, int]:
    """左辅右弼（按生月）：辰上顺正寻左辅，戌上逆正右弼当。"""
    zuo = fix_index(fix_earthly_branch_index("辰") + (lunar_month - 1))
    you = fix_index(fix_earthly_branch_index("戌") - (lunar_month - 1))
    return zuo, you


def get_chang_qu_index(time_index: int) -> tuple[int, int]:
    """文昌文曲（按时支）：辰上顺时文曲位，戌上逆时觅文昌。"""
    chang = fix_index(fix_earthly_branch_index("戌") - fix_index(time_index))
    qu = fix_index(fix_earthly_branch_index("辰") + fix_index(time_index))
    return chang, qu


def get_timely_star_index(time_index: int) -> tuple[int, int]:
    """台辅、封诰（按时支）。"""
    taifu = fix_index(fix_earthly_branch_index("午") + fix_index(time_index))
    fenggao = fix_index(fix_earthly_branch_index("寅") + fix_index(time_index))
    return taifu, fenggao


def get_kong_jie_index(time_index: int) -> tuple[int, int]:
    """地空地劫（按时支）：亥上子时顺安劫，逆回便是地空亡。"""
    t = fix_index(time_index)
    hai = fix_earthly_branch_index("亥")
    return fix_index(hai - t), fix_index(hai + t)


def get_huo_ling_index(branch: str, time_index: int) -> tuple[int, int]:
    """火星铃星（按年支起子时位，再顺数到生时）。

    - 申子辰人寅戌扬，寅午戌人丑卯方，
    - 巳酉丑人卯戌位，亥卯未人酉戌房。
    """
    t = fix_index(time_index)
    table = {
        ("寅", "午", "戌"): ("丑", "卯"),
        ("申", "子", "辰"): ("寅", "戌"),
        ("巳", "酉", "丑"): ("卯", "戌"),
        ("亥", "未", "卯"): ("酉", "戌"),
    }
    for group, (huo, ling) in table.items():
        if branch in group:
            return (fix_index(fix_earthly_branch_index(huo) + t),
                    fix_index(fix_earthly_branch_index(ling) + t))
    return -1, -1


def get_daily_star_index(
    solar_date: str, time_index: int, fix_leap: bool = True
) -> tuple[int, int, int, int]:
    """日系星：三台、八座、恩光、天贵。

    - 由左辅之宫位起初一，顺行至生日安三台；由右弼起初一，逆行至生日安八座。
    - 由文昌起初一，顺行至生日**再退一步**起恩光；文曲同法起天贵。
    """
    lunar_day = solar2lunar(solar_date).lunar_day
    month_index = fix_lunar_month_index(solar_date, time_index, fix_leap)

    zuo, you = get_zuo_you_index(month_index + 1)
    chang, qu = get_chang_qu_index(time_index)
    day_index = fix_lunar_day_index(lunar_day, time_index)

    santai = fix_index((zuo + day_index) % 12)
    bazuo = fix_index((you - day_index) % 12)
    enguang = fix_index(((chang + day_index) % 12) - 1)
    tiangui = fix_index(((qu + day_index) % 12) - 1)
    return santai, bazuo, enguang, tiangui


def get_monthly_star_index(
    solar_date: str, time_index: int, fix_leap: bool = True
) -> dict[str, int]:
    """月系星：月解、天姚、天刑、阴煞、天月、天巫。"""
    m = fix_lunar_month_index(solar_date, time_index, fix_leap)

    return {
        # 正二在申三四在戌，五六在子七八在寅，九十月坐于辰宫，十一十二在午宫
        "月解": fix_index(fix_earthly_branch_index(("申", "戌", "子", "寅", "辰", "午")[m // 2])),
        # 天姚丑宫起正月，天刑从酉起正月，顺至生月
        "天姚": fix_index(fix_earthly_branch_index("丑") + m),
        "天刑": fix_index(fix_earthly_branch_index("酉") + m),
        # 正七月在寅，二八月在子，三九月在戌，四十月在申，五十一在午，六十二在辰
        "阴煞": fix_index(fix_earthly_branch_index(("寅", "子", "戌", "申", "午", "辰")[m % 6])),
        # 一犬二蛇三在龙，四虎五羊六兔宫。七猪八羊九在虎，十马冬犬腊寅中
        "天月": fix_index(fix_earthly_branch_index(
            ("戌", "巳", "辰", "寅", "未", "卯", "亥", "未", "寅", "午", "戌", "寅")[m])),
        # 正五九月在巳，二六十月在申，三七十一在寅，四八十二在亥
        "天巫": fix_index(fix_earthly_branch_index(("巳", "申", "寅", "亥")[m % 4])),
    }


# ── 年支系 ──────────────────────────────────────────────────────────

def get_luan_xi_index(branch: str) -> tuple[int, int]:
    """红鸾天喜：卯上起子逆数之，数到当生太岁支；对宫天喜不差移。"""
    hongluan = fix_index(fix_earthly_branch_index("卯") - EARTHLY_BRANCHES.index(branch))
    return hongluan, fix_index(hongluan + 6)


def get_huagai_xianchi_index(branch: str) -> tuple[int, int]:
    """华盖、咸池。

    华盖：子辰申年在辰，丑巳酉年在丑，寅午戌年在戌，卯未亥年在未。
    咸池：子辰申年在酉，丑巳酉年在午，寅午戌年在卯，卯未亥年在子。
    """
    table = {
        ("寅", "午", "戌"): ("戌", "卯"),
        ("申", "子", "辰"): ("辰", "酉"),
        ("巳", "酉", "丑"): ("丑", "午"),
        ("亥", "未", "卯"): ("未", "子"),
    }
    for group, (hg, xc) in table.items():
        if branch in group:
            return fix_earthly_branch_index(hg), fix_earthly_branch_index(xc)
    return -1, -1


def get_gu_gua_index(branch: str) -> tuple[int, int]:
    """孤辰、寡宿：寅卯辰年安巳丑，巳午未年安申辰，申酉戌年安亥未，亥子丑年安寅戌。"""
    table = {
        ("寅", "卯", "辰"): ("巳", "丑"),
        ("巳", "午", "未"): ("申", "辰"),
        ("申", "酉", "戌"): ("亥", "未"),
        ("亥", "子", "丑"): ("寅", "戌"),
    }
    for group, (gu, gua) in table.items():
        if branch in group:
            return fix_earthly_branch_index(gu), fix_earthly_branch_index(gua)
    return -1, -1


def get_jiesha_adj_index(branch: str) -> int:
    """劫杀（中州派杂耀）。

    申子辰人蛇开口、亥卯未人猴速走、寅午戌人猪面黑、巳酉丑人虎咆哮。
    """
    if branch in ("申", "子", "辰"):
        return 3   # 巳
    if branch in ("亥", "卯", "未"):
        return 6   # 申
    if branch in ("寅", "午", "戌"):
        return 9   # 亥
    return 0       # 巳酉丑 → 寅


def get_dahao_index(branch: str) -> int:
    """大耗（中州派杂耀）：年支之对宫，阳支顺行前一位，阴支逆行后一位。"""
    matched = ("未", "午", "酉", "申", "亥", "戌",
               "丑", "子", "卯", "寅", "巳", "辰")[EARTHLY_BRANCHES.index(branch)]
    return fix_index(EARTHLY_BRANCHES.index(matched) - YIN_INDEX)


def get_nianjie_index(branch: str) -> int:
    """年解：解神从戌上起子，逆数至当生年太岁。"""
    table = ("戌", "酉", "申", "未", "午", "巳", "辰", "卯", "寅", "丑", "子", "亥")
    return fix_index(fix_earthly_branch_index(table[EARTHLY_BRANCHES.index(branch)]))


def get_tianshi_tianshang_index(
    gender: str, branch: str, soul_index: int, config: Config = DEFAULT_CONFIG
) -> tuple[int, int]:
    """天使、天伤。

    通行本：天伤居仆役、天使居疾厄，夹迁移宫。
    中州派：凡阳男阴女依此诀；**阴男阳女则天伤居疾厄、天使居仆役**（互换）。
    """
    yinyang = EARTHLY_BRANCHES.index(branch) % 2  # 0 阳 1 阴
    same = yinyang == (0 if gender == "男" else 1)

    tianshang = fix_index(PALACES.index("仆役") + soul_index)
    tianshi = fix_index(PALACES.index("疾厄") + soul_index)

    if config.algorithm == "zhongzhou" and not same:
        tianshi, tianshang = tianshang, tianshi
    return tianshi, tianshang


def get_yearly_star_index(
    solar_date: str,
    time_index: int,
    gender: str,
    fix_leap: bool = True,
    config: Config = DEFAULT_CONFIG,
) -> dict[str, int]:
    """年系杂耀的全部索引。"""
    gz = get_ganzhi_by_solar_date(solar_date, time_index, _horoscope_config(config))
    stem, branch = gz.yearly
    branch_i = EARTHLY_BRANCHES.index(branch)
    stem_i = HEAVENLY_STEMS.index(stem)

    sb = get_soul_and_body(solar_date, time_index, fix_leap, config)
    huagai, xianchi = get_huagai_xianchi_index(branch)
    guchen, guasu = get_gu_gua_index(branch)

    jielu = fix_index(fix_earthly_branch_index(("申", "午", "辰", "寅", "子")[stem_i % 5]))
    kongwang = fix_index(fix_earthly_branch_index(("酉", "未", "巳", "卯", "丑")[stem_i % 5]))

    # 旬空
    xunkong = fix_index(fix_earthly_branch_index(branch) + HEAVENLY_STEMS.index("癸") - stem_i + 1)
    yinyang = branch_i % 2
    if yinyang != xunkong % 2:
        xunkong = fix_index(xunkong + 1)

    tianshi, tianshang = get_tianshi_tianshang_index(gender, branch, sb.soul_index, config)

    return {
        "咸池": xianchi,
        "华盖": huagai,
        "孤辰": guchen,
        "寡宿": guasu,
        # 天才由命宫起子、天寿由身宫起子，顺行至生年支
        "天才": fix_index(sb.soul_index + branch_i),
        "天寿": fix_index(sb.body_index + branch_i),
        # 甲丁食蛇口，乙戊辛马方。丙从鼠口得，己食于猴房。庚食虎头上，壬鸡癸猪堂
        "天厨": fix_index(fix_earthly_branch_index(
            ("巳", "午", "子", "巳", "午", "申", "寅", "午", "酉", "亥")[stem_i])),
        # 子午卯酉年安巳宫，寅申巳亥年安酉宫，辰戌丑未年安丑宫
        "破碎": fix_index(fix_earthly_branch_index(("巳", "丑", "酉")[branch_i % 3])),
        # 子丑寅年在申酉戌，卯辰巳年在巳午未，午未申年在寅卯辰，酉戌亥年在亥子丑
        "蜚廉": fix_index(fix_earthly_branch_index(
            ("申", "酉", "戌", "巳", "午", "未", "寅", "卯", "辰", "亥", "子", "丑")[branch_i])),
        # 龙池从辰宫起子顺行，凤阁从戌宫起子逆行
        "龙池": fix_index(fix_earthly_branch_index("辰") + branch_i),
        "凤阁": fix_index(fix_earthly_branch_index("戌") - branch_i),
        # 天哭天虚起午宫，哭逆行兮虚顺转
        "天哭": fix_index(fix_earthly_branch_index("午") - branch_i),
        "天虚": fix_index(fix_earthly_branch_index("午") + branch_i),
        # 甲喜羊鸡乙龙猴，丙年蛇鼠一窝谋，丁虎擒猪戊玉兔，
        # 己鸡居然与虎俦，庚猪马辛鸡蛇走，壬犬马癸马蛇游
        "天官": fix_index(fix_earthly_branch_index(
            ("未", "辰", "巳", "寅", "卯", "酉", "亥", "酉", "戌", "午")[stem_i])),
        "天福": fix_index(fix_earthly_branch_index(
            ("酉", "申", "子", "亥", "卯", "寅", "午", "巳", "午", "巳")[stem_i])),
        "天德": fix_index(fix_earthly_branch_index("酉") + branch_i),
        "月德": fix_index(fix_earthly_branch_index("巳") + branch_i),
        # 天空：生年支顺数的前一位
        "天空": fix_index(fix_earthly_branch_index(branch) + 1),
        "截路": jielu,
        "空亡": kongwang,
        "旬空": xunkong,
        "天伤": tianshang,
        "天使": tianshi,
        # 中州派没有截路空亡，只有一颗截空：生年阳干在阳宫，阴干在阴宫
        "截空": jielu if yinyang == 0 else kongwang,
        "劫杀": get_jiesha_adj_index(branch),
        "年解": get_nianjie_index(branch),
        "大耗": get_dahao_index(branch),
    }


def get_chang_qu_index_by_stem(stem: str) -> tuple[int, int]:
    """流昌流曲（按大限 / 流年天干）。

    - 流昌起巳位，甲乙顺流去，不用四墓宫。
    - 流曲起酉位，甲乙逆行踪，亦不用四墓。
    """
    table = {
        "甲": ("巳", "酉"), "乙": ("午", "申"),
        "丙": ("申", "午"), "戊": ("申", "午"),
        "丁": ("酉", "巳"), "己": ("酉", "巳"),
        "庚": ("亥", "卯"), "辛": ("子", "寅"),
        "壬": ("寅", "子"), "癸": ("卯", "亥"),
    }
    chang, qu = table[stem]
    return fix_earthly_branch_index(chang), fix_earthly_branch_index(qu)
