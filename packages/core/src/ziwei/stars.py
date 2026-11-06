"""安星。对应 iztro 的 `src/star/{majorStar,minorStar,adjectiveStar,decorativeStar}.ts`。

所有函数返回长度 12 的列表，索引 0 == 寅宫。
"""

from __future__ import annotations

from .calendar import get_ganzhi_by_solar_date
from .config import Config, DEFAULT_CONFIG
from .constants import EARTHLY_BRANCHES, GENDER_YIN_YANG, FiveElementsClass
from .data import EARTHLY_BRANCHES_INFO
from .location import (
    _horoscope_config,
    get_chang_qu_index,
    get_daily_star_index,
    get_gu_gua_index,
    get_huo_ling_index,
    get_kong_jie_index,
    get_kui_yue_index,
    get_lu_yang_tuo_ma_index,
    get_luan_xi_index,
    get_monthly_star_index,
    get_start_index,
    get_timely_star_index,
    get_yearly_star_index,
    get_zuo_you_index,
)
from .models import Star
from .palace import get_five_elements_class, get_soul_and_body
from .utils import (
    fix_earthly_branch_index,
    fix_index,
    fix_lunar_month_index,
    get_brightness,
    get_mutagen,
)


def init_stars() -> list[list[Star]]:
    return [[] for _ in range(12)]


# ── 14 主星 ─────────────────────────────────────────────────────────

# 安紫微诸星诀：紫微逆去天机星，隔一太阳武曲辰，连接天同空二宫，廉贞居处方是真
ZIWEI_GROUP = ("紫微", "天机", "", "太阳", "武曲", "天同", "", "", "廉贞")
# 安天府诸星诀：天府顺行有太阴，贪狼而后巨门临，随来天相天梁继，七杀空三是破军
TIANFU_GROUP = ("天府", "太阴", "贪狼", "巨门", "天相", "天梁", "七杀", "", "", "", "破军")


def get_major_star(
    solar_date: str,
    time_index: int,
    fix_leap: bool = True,
    config: Config = DEFAULT_CONFIG,
    from_palace: tuple[str, str] | None = None,
) -> list[list[Star]]:
    ziwei_index, tianfu_index = get_start_index(solar_date, time_index, fix_leap, config, from_palace)
    year_stem = get_ganzhi_by_solar_date(solar_date, time_index, config).yearly[0]
    stars = init_stars()

    for i, name in enumerate(ZIWEI_GROUP):
        if not name:
            continue
        idx = fix_index(ziwei_index - i)          # 紫微星系逆行
        stars[idx].append(Star(name=name, type="major", scope="origin",
                               brightness=get_brightness(name, idx, config),
                               mutagen=get_mutagen(name, year_stem, config)))

    for i, name in enumerate(TIANFU_GROUP):
        if not name:
            continue
        idx = fix_index(tianfu_index + i)          # 天府星系顺行
        stars[idx].append(Star(name=name, type="major", scope="origin",
                               brightness=get_brightness(name, idx, config),
                               mutagen=get_mutagen(name, year_stem, config)))
    return stars


# ── 14 辅星 ─────────────────────────────────────────────────────────

def get_minor_star(
    solar_date: str,
    time_index: int,
    fix_leap: bool = True,
    config: Config = DEFAULT_CONFIG,
) -> list[list[Star]]:
    stars = init_stars()
    gz = get_ganzhi_by_solar_date(solar_date, time_index, config)
    year_stem, year_branch = gz.yearly
    month_index = fix_lunar_month_index(solar_date, time_index, fix_leap)

    zuo, you = get_zuo_you_index(month_index + 1)
    chang, qu = get_chang_qu_index(time_index)
    kui, yue = get_kui_yue_index(year_stem)
    huo, ling = get_huo_ling_index(year_branch, time_index)
    kong, jie = get_kong_jie_index(time_index)
    lytm = get_lu_yang_tuo_ma_index(year_stem, year_branch)

    def add(idx: int, name: str, type_: str, with_mutagen: bool = False) -> None:
        stars[idx].append(Star(
            name=name, type=type_, scope="origin",
            brightness=get_brightness(name, idx, config),
            mutagen=get_mutagen(name, year_stem, config) if with_mutagen else "",
        ))

    # ⚠️ 顺序即输出顺序，跟上游逐项对齐，别重排
    add(zuo, "左辅", "soft", True)
    add(you, "右弼", "soft", True)
    add(chang, "文昌", "soft", True)
    add(qu, "文曲", "soft", True)
    add(kui, "天魁", "soft")
    add(yue, "天钺", "soft")
    add(lytm.lu_index, "禄存", "lucun")
    add(lytm.ma_index, "天马", "tianma")
    add(kong, "地空", "tough")
    add(jie, "地劫", "tough")
    add(huo, "火星", "tough")
    add(ling, "铃星", "tough")
    add(lytm.yang_index, "擎羊", "tough")
    add(lytm.tuo_index, "陀罗", "tough")
    return stars


# ── 杂耀 ────────────────────────────────────────────────────────────

def get_adjective_star(
    solar_date: str,
    time_index: int,
    gender: str,
    fix_leap: bool = True,
    config: Config = DEFAULT_CONFIG,
) -> list[list[Star]]:
    stars = init_stars()
    gz = get_ganzhi_by_solar_date(solar_date, time_index, config)
    year_branch = gz.yearly[1]

    y = get_yearly_star_index(solar_date, time_index, gender, fix_leap, config)
    m = get_monthly_star_index(solar_date, time_index, fix_leap)
    santai, bazuo, enguang, tiangui = get_daily_star_index(solar_date, time_index, fix_leap)
    taifu, fenggao = get_timely_star_index(time_index)
    hongluan, tianxi = get_luan_xi_index(year_branch)
    suiqian12, _ = get_yearly12(solar_date, config)

    def add(idx: int, name: str, type_: str = "adjective") -> None:
        stars[idx].append(Star(name=name, type=type_, scope="origin"))

    # ⚠️ 以下顺序照抄上游，是输出顺序的一部分
    add(hongluan, "红鸾", "flower")
    add(tianxi, "天喜", "flower")
    add(m["天姚"], "天姚", "flower")
    add(y["咸池"], "咸池", "flower")
    add(m["月解"], "解神", "helper")
    add(santai, "三台")
    add(bazuo, "八座")
    add(enguang, "恩光")
    add(tiangui, "天贵")
    add(y["龙池"], "龙池")
    add(y["凤阁"], "凤阁")
    add(y["天才"], "天才")
    add(y["天寿"], "天寿")
    add(taifu, "台辅")
    add(fenggao, "封诰")
    add(m["天巫"], "天巫")
    add(y["华盖"], "华盖")
    add(y["天官"], "天官")
    add(y["天福"], "天福")
    add(y["天厨"], "天厨")
    add(m["天月"], "天月")
    add(y["天德"], "天德")
    add(y["月德"], "月德")
    add(y["天空"], "天空")
    add(y["旬空"], "旬空")

    if config.algorithm != "zhongzhou":
        # 中州派没有截路空亡
        add(y["截路"], "截路")
        add(y["空亡"], "空亡")
    else:
        # 中州派特有：龙德跟着岁前十二神走
        add(suiqian12.index("龙德"), "龙德")
        add(y["截空"], "截空")
        add(y["劫杀"], "劫杀")
        add(y["大耗"], "大耗")

    add(y["孤辰"], "孤辰")
    add(y["寡宿"], "寡宿")
    add(y["蜚廉"], "蜚廉")
    add(y["破碎"], "破碎")
    add(m["天刑"], "天刑")
    add(m["阴煞"], "阴煞")
    add(y["天哭"], "天哭")
    add(y["天虚"], "天虚")
    add(y["天使"], "天使")
    add(y["天伤"], "天伤")
    add(y["年解"], "年解", "helper")
    return stars


# ── 长生 12 神 / 博士 12 神 / 流年十二神 ────────────────────────────

CHANGSHENG12 = ("长生", "沐浴", "冠带", "临官", "帝旺", "衰",
                "病", "死", "墓", "绝", "胎", "养")

BOSHI12 = ("博士", "力士", "青龙", "小耗", "将军", "奏书",
           "飞廉", "喜神", "病符", "大耗", "伏兵", "官府")

JIANGQIAN12 = ("将星", "攀鞍", "岁驿", "息神", "华盖", "劫煞",
               "灾煞", "天煞", "指背", "咸池", "月煞", "亡神")


def get_changsheng12_start_index(five_elements: FiveElementsClass) -> int:
    """水二局长生在申，木三局在亥，金四局在巳，土五局在申，火六局在寅。"""
    return fix_earthly_branch_index(
        {2: "申", 3: "亥", 4: "巳", 5: "申", 6: "寅"}[int(five_elements)]
    )


def get_changsheng12(
    solar_date: str,
    time_index: int,
    gender: str,
    fix_leap: bool = True,
    config: Config = DEFAULT_CONFIG,
    from_palace: tuple[str, str] | None = None,
) -> list[str]:
    """长生十二神。阳男阴女顺行，阴男阳女逆行。"""
    # ⚠️ 上游此处固定用 time_index=0 取年干支，照抄
    year_branch = get_ganzhi_by_solar_date(solar_date, 0, config).yearly[1]
    sb = get_soul_and_body(solar_date, time_index, fix_leap, config, from_palace)
    base_stem = from_palace[0] if from_palace else sb.heavenly_stem_of_soul
    base_branch = from_palace[1] if from_palace else sb.earthly_branch_of_soul
    five_elements = get_five_elements_class(base_stem, base_branch)

    start = get_changsheng12_start_index(five_elements)
    forward = GENDER_YIN_YANG[gender] == EARTHLY_BRANCHES_INFO[year_branch]["yin_yang"]

    result = [""] * 12
    for i, name in enumerate(CHANGSHENG12):
        idx = fix_index(i + start) if forward else fix_index(start - i)
        result[idx] = name
    return result


def get_boshi12(solar_date: str, gender: str, config: Config = DEFAULT_CONFIG) -> list[str]:
    """博士十二神。从禄存起，阳男阴女顺行，阴男阳女逆行。"""
    gz = get_ganzhi_by_solar_date(solar_date, 0, config)
    year_stem, year_branch = gz.yearly
    lu_index = get_lu_yang_tuo_ma_index(year_stem, year_branch).lu_index
    forward = GENDER_YIN_YANG[gender] == EARTHLY_BRANCHES_INFO[year_branch]["yin_yang"]

    result = [""] * 12
    for i, name in enumerate(BOSHI12):
        idx = fix_index(lu_index + i) if forward else fix_index(lu_index - i)
        result[idx] = name
    return result


def get_yearly12(solar_date: str, config: Config = DEFAULT_CONFIG) -> tuple[list[str], list[str]]:
    """岁前十二神 与 将前十二神。

    岁前：流年地支起岁建，岁前首先是晦气，丧门贯索及官符，
          小耗大耗龙德继，白虎天德连吊客，病符居后须当记。
    将前：寅午戌年将星午，申子辰年子将星，巳酉丑将酉上驻，亥卯未将卯上停。

    ⚠️ 中州派把「大耗」叫「岁破」。
    """
    gz = get_ganzhi_by_solar_date(solar_date, 0, _horoscope_config(config))
    year_branch = gz.yearly[1]

    dahao = "岁破" if config.algorithm == "zhongzhou" else "大耗"
    suiqian_names = ("岁建", "晦气", "丧门", "贯索", "官符", "小耗",
                     dahao, "龙德", "白虎", "天德", "吊客", "病符")

    suiqian12 = [""] * 12
    base = fix_earthly_branch_index(year_branch)
    for i, name in enumerate(suiqian_names):
        suiqian12[fix_index(base + i)] = name

    jq_start = {
        ("寅", "午", "戌"): "午", ("申", "子", "辰"): "子",
        ("巳", "酉", "丑"): "酉", ("亥", "卯", "未"): "卯",
    }
    start = -1
    for group, target in jq_start.items():
        if year_branch in group:
            start = fix_earthly_branch_index(target)
            break
    start = fix_index(start)

    jiangqian12 = [""] * 12
    for i, name in enumerate(JIANGQIAN12):
        jiangqian12[fix_index(start + i)] = name

    return suiqian12, jiangqian12
