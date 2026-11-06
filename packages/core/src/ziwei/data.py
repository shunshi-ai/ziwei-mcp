"""天干 / 地支 / 星耀的静态属性表。

移植自 iztro 的 `src/data/heavenlyStems.ts`、`earthlyBranches.ts`、`stars.ts`。
"""

from __future__ import annotations

# ── 十天干 ──────────────────────────────────────────────────────────
# mutagen 顺序固定为【禄，权，科，忌】
# 戊己土居中央，故无冲，crash 为 None。
HEAVENLY_STEMS_INFO: dict[str, dict] = {
    "甲": {"yin_yang": "阳", "five_elements": "木", "crash": "庚",
           "mutagen": ("廉贞", "破军", "武曲", "太阳")},
    "乙": {"yin_yang": "阴", "five_elements": "木", "crash": "辛",
           "mutagen": ("天机", "天梁", "紫微", "太阴")},
    "丙": {"yin_yang": "阳", "five_elements": "火", "crash": "壬",
           "mutagen": ("天同", "天机", "文昌", "廉贞")},
    "丁": {"yin_yang": "阴", "five_elements": "火", "crash": "癸",
           "mutagen": ("太阴", "天同", "天机", "巨门")},
    "戊": {"yin_yang": "阳", "five_elements": "土", "crash": None,
           "mutagen": ("贪狼", "太阴", "右弼", "天机")},
    "己": {"yin_yang": "阴", "five_elements": "土", "crash": None,
           "mutagen": ("武曲", "贪狼", "天梁", "文曲")},
    "庚": {"yin_yang": "阳", "five_elements": "金", "crash": "甲",
           "mutagen": ("太阳", "武曲", "太阴", "天同")},
    "辛": {"yin_yang": "阴", "five_elements": "金", "crash": "乙",
           "mutagen": ("巨门", "太阳", "文曲", "文昌")},
    "壬": {"yin_yang": "阳", "five_elements": "水", "crash": "丙",
           "mutagen": ("天梁", "紫微", "左辅", "武曲")},
    "癸": {"yin_yang": "阴", "five_elements": "水", "crash": "丁",
           "mutagen": ("破军", "巨门", "太阴", "贪狼")},
}

# ⚠️ 中州派（王亭之）四化表。
# 与通行本的分歧【只在「科」，且只有戊 / 庚 / 壬 三个天干】：
#   戊 科：右弼 → 太阳
#   庚 科：太阴 → 天府
#   壬 科：左辅 → 天府
# 禄 / 权 / 忌 三十项与通行本完全一致。
#
# ⚠️ iztro 的 `algorithm: 'zhongzhou'` 开关**不切这张表**（庚仍为太阴科），
# 那是上游的缺口；本移植把它补上了。
ZHONGZHOU_MUTAGEN: dict[str, tuple[str, str, str, str]] = {
    "甲": ("廉贞", "破军", "武曲", "太阳"),
    "乙": ("天机", "天梁", "紫微", "太阴"),
    "丙": ("天同", "天机", "文昌", "廉贞"),
    "丁": ("太阴", "天同", "天机", "巨门"),
    "戊": ("贪狼", "太阴", "太阳", "天机"),
    "己": ("武曲", "贪狼", "天梁", "文曲"),
    "庚": ("太阳", "武曲", "天府", "天同"),
    "辛": ("巨门", "太阳", "文曲", "文昌"),
    "壬": ("天梁", "紫微", "天府", "武曲"),
    "癸": ("破军", "巨门", "太阴", "贪狼"),
}

# ── 十二地支 ────────────────────────────────────────────────────────
# soul  = 命主（通行本以「命宫地支」定，中州派以「生年年支」定）
# body  = 身主（两派一致，均以生年年支定）
EARTHLY_BRANCHES_INFO: dict[str, dict] = {
    "子": {"yin_yang": "阳", "five_elements": "水", "crash": "午",
           "soul": "贪狼", "body": "火星",
           "inside": "胆", "outside": "下体",
           "health_tip": "生殖系统、膀胱、尿道之疾病，听觉障碍"},
    "丑": {"yin_yang": "阴", "five_elements": "土", "crash": "未",
           "soul": "巨门", "body": "天相",
           "inside": "肝", "outside": "小腿、脚（右）",
           "health_tip": "胸部、肋膜炎、胃病、脚部"},
    "寅": {"yin_yang": "阳", "five_elements": "木", "crash": "申",
           "soul": "禄存", "body": "天梁",
           "inside": "肺", "outside": "大腿（右）",
           "health_tip": "胆囊、关节、胫部、神经痛、风湿"},
    "卯": {"yin_yang": "阴", "five_elements": "木", "crash": "酉",
           "soul": "文曲", "body": "天同",
           "inside": "大肠", "outside": "腰（右）、背",
           "health_tip": "肝病、颜面神经、失眠、神经衰弱"},
    "辰": {"yin_yang": "阳", "five_elements": "土", "crash": "戌",
           "soul": "廉贞", "body": "文昌",
           "inside": "胃", "outside": "胸、胳膊（右）",
           "health_tip": "消化系统、脊椎、皮肤疾病"},
    "巳": {"yin_yang": "阴", "five_elements": "火", "crash": "亥",
           "soul": "武曲", "body": "天机",
           "inside": "脾", "outside": "左肩",
           "health_tip": "喉头、牙病、感冒"},
    "午": {"yin_yang": "阳", "five_elements": "火", "crash": "子",
           "soul": "破军", "body": "火星",
           "inside": "心", "outside": "头",
           "health_tip": "心脏、视觉、味觉障碍、火难"},
    "未": {"yin_yang": "阴", "five_elements": "土", "crash": "丑",
           "soul": "武曲", "body": "天相",
           "inside": "小肠", "outside": "脸",
           "health_tip": "消化系统、胰脏、健忘症、疲倦、手腕、嘴唇"},
    "申": {"yin_yang": "阳", "five_elements": "金", "crash": "寅",
           "soul": "廉贞", "body": "天梁",
           "inside": "膀胱", "outside": "胸、胳膊（左）",
           "health_tip": "呼吸系统、肺部、消化系统、大肠"},
    "酉": {"yin_yang": "阴", "five_elements": "金", "crash": "卯",
           "soul": "文曲", "body": "天同",
           "inside": "肾", "outside": "腰（左）、腹",
           "health_tip": "吐血、痢血、小肠之疾、脑出血、头腕部"},
    "戌": {"yin_yang": "阳", "five_elements": "土", "crash": "辰",
           "soul": "禄存", "body": "文昌",
           "inside": "心包", "outside": "大腿（左）",
           "health_tip": "下半身之疾、子宫、痔疮、脚部"},
    "亥": {"yin_yang": "阴", "five_elements": "水", "crash": "巳",
           "soul": "巨门", "body": "天机",
           "inside": "三焦", "outside": "小腿、脚（左）",
           "health_tip": "排泄机能障碍、肾脏、尿道、偏头痛"},
}

# ── 星耀亮度 / 五行 / 阴阳 ──────────────────────────────────────────
# brightness 按宫位地支排序，**从寅开始**（即索引 0 == 寅宫）
STARS_INFO: dict[str, dict] = {
    "紫微": {"brightness": ("旺", "旺", "得", "旺", "庙", "庙", "旺", "旺", "得", "旺", "平", "庙"),
             "five_elements": "土", "yin_yang": "阴"},
    "天机": {"brightness": ("得", "旺", "利", "平", "庙", "陷", "得", "旺", "利", "平", "庙", "陷"),
             "five_elements": "木", "yin_yang": "阴"},
    "太阳": {"brightness": ("旺", "庙", "旺", "旺", "旺", "得", "得", "陷", "不", "陷", "陷", "不"),
             "five_elements": "", "yin_yang": ""},
    "武曲": {"brightness": ("得", "利", "庙", "平", "旺", "庙", "得", "利", "庙", "平", "旺", "庙"),
             "five_elements": "金", "yin_yang": "阴"},
    "天同": {"brightness": ("利", "平", "平", "庙", "陷", "不", "旺", "平", "平", "庙", "旺", "不"),
             "five_elements": "水", "yin_yang": "阳"},
    "廉贞": {"brightness": ("庙", "平", "利", "陷", "平", "利", "庙", "平", "利", "陷", "平", "利"),
             "five_elements": "火", "yin_yang": "阴"},
    "天府": {"brightness": ("庙", "得", "庙", "得", "旺", "庙", "得", "旺", "庙", "得", "庙", "庙"),
             "five_elements": "土", "yin_yang": "阳"},
    "太阴": {"brightness": ("旺", "陷", "陷", "陷", "不", "不", "利", "不", "旺", "庙", "庙", "庙"),
             "five_elements": "水", "yin_yang": "阴"},
    "贪狼": {"brightness": ("平", "利", "庙", "陷", "旺", "庙", "平", "利", "庙", "陷", "旺", "庙"),
             "five_elements": "水", "yin_yang": ""},
    "巨门": {"brightness": ("庙", "庙", "陷", "旺", "旺", "不", "庙", "庙", "陷", "旺", "旺", "不"),
             "five_elements": "土", "yin_yang": "阴"},
    "天相": {"brightness": ("庙", "陷", "得", "得", "庙", "得", "庙", "陷", "得", "得", "庙", "庙"),
             "five_elements": "水", "yin_yang": ""},
    "天梁": {"brightness": ("庙", "庙", "庙", "陷", "庙", "旺", "陷", "得", "庙", "陷", "庙", "旺"),
             "five_elements": "土", "yin_yang": ""},
    "七杀": {"brightness": ("庙", "旺", "庙", "平", "旺", "庙", "庙", "庙", "庙", "平", "旺", "庙"),
             "five_elements": "", "yin_yang": ""},
    "破军": {"brightness": ("得", "陷", "旺", "平", "庙", "旺", "得", "陷", "旺", "平", "庙", "旺"),
             "five_elements": "水", "yin_yang": ""},
    "文昌": {"brightness": ("陷", "利", "得", "庙", "陷", "利", "得", "庙", "陷", "利", "得", "庙")},
    "文曲": {"brightness": ("平", "旺", "得", "庙", "陷", "旺", "得", "庙", "陷", "旺", "得", "庙")},
    "火星": {"brightness": ("庙", "利", "陷", "得", "庙", "利", "陷", "得", "庙", "利", "陷", "得")},
    "铃星": {"brightness": ("庙", "利", "陷", "得", "庙", "利", "陷", "得", "庙", "利", "陷", "得")},
    "擎羊": {"brightness": ("", "陷", "庙", "", "陷", "庙", "", "陷", "庙", "", "陷", "庙")},
    "陀罗": {"brightness": ("陷", "", "庙", "陷", "", "庙", "陷", "", "庙", "陷", "", "庙")},
}
