"""
収入の壁マスターデータ
"""

# アルバイト・パート版の収入の壁（5本柱）
INCOME_WALLS_PARTTIME = [
    {
        "amount": 1030000,
        "name": "103万円の壁",
        "category": "所得税",
        "description": "基礎控除48万円＋給与所得控除55万円を超え、所得税が発生",
        "impacts": {
            "self": "本人に所得税が発生（源泉徴収）",
            "family": None
        },
        "color": "#FFE082",  # 黄色
        "level": 1
    },
    {
        "amount": 1060000,
        "name": "106万円の壁",
        "category": "社会保険",
        "description": "大企業（従業員101人以上）で週20時間以上勤務＋月収8.8万円以上で社会保険加入義務",
        "conditions": [
            "週20時間以上勤務",
            "月88,000円以上",
            "2ヶ月超雇用",
            "学生でない（学生除外特例あり）",
            "従業員101人以上の企業"
        ],
        "impacts": {
            "self": "本人に年間約15〜17万円の社会保険料負担（学生除外特例あり）",
            "family": None
        },
        "color": "#FFAB91",  # オレンジ
        "level": 2
    },
    {
        "amount": 1300000,
        "name": "130万円の壁",
        "category": "扶養・社会保険",
        "description": "親の社会保険の扶養から外れる",
        "impacts": {
            "self": "国民健康保険・年金に加入必要",
            "family": "親の健康保険料が上がる"
        },
        "color": "#EF5350",  # 赤
        "level": 3
    },
    {
        "amount": 1500000,
        "name": "150万円の壁",
        "category": "配偶者控除",
        "description": "配偶者控除を受けている場合、控除が減少",
        "impacts": {
            "self": None,
            "family": "親の税負担が増加（配偶者特別控除の減額）"
        },
        "color": "#C62828",  # 濃い赤
        "level": 4
    },
    {
        "amount": 2010000,
        "name": "201万円の壁",
        "category": "住民税",
        "description": "住民税の均等割＋所得割が発生",
        "impacts": {
            "self": "本人に住民税が発生（市区町村により基準100〜204万円）",
            "family": None
        },
        "color": "#4A148C",  # 紫
        "level": 5
    }
]

# 業務委託版の収入の壁
INCOME_WALLS_FREELANCE = [
    {
        "amount": 480000,
        "name": "48万円の壁",
        "category": "所得税",
        "description": "基礎控除48万円を超え、所得税が発生",
        "impacts": {
            "self": "本人に所得税が発生",
            "family": None
        },
        "color": "#FFE082",  # 黄色
        "level": 1
    },
    {
        "amount": 1030000,
        "name": "103万円の壁",
        "category": "扶養控除",
        "description": "親の扶養控除が外れる（給与所得換算）",
        "note": "事業所得48万円が給与所得103万円相当",
        "impacts": {
            "self": None,
            "family": "親の税負担が年間5〜16万円増"
        },
        "color": "#FFAB91",  # オレンジ
        "level": 2
    },
    {
        "amount": 1130000,
        "name": "113万円の壁",
        "category": "所得税",
        "description": "青色申告特別控除65万円を使っても所得税が発生",
        "note": "113万円 - 65万円（青色控除）- 48万円（基礎控除）= 0円",
        "impacts": {
            "self": "青色申告でも所得税が発生",
            "family": None
        },
        "color": "#FFB74D",  # 薄いオレンジ
        "level": 3
    },
    {
        "amount": 1300000,
        "name": "130万円の壁",
        "category": "社会保険扶養",
        "description": "親の社会保険の扶養から外れる",
        "impacts": {
            "self": "国民健康保険・国民年金に加入必要",
            "family": "親の健康保険料が上がる"
        },
        "color": "#EF5350",  # 赤
        "level": 4
    },
    {
        "amount": 2900000,
        "name": "290万円の壁",
        "category": "個人事業税",
        "description": "個人事業税が発生（事業主控除290万円）",
        "note": "業種により税率3〜5%",
        "impacts": {
            "self": "個人事業税が発生（所得×税率3〜5%）",
            "family": None
        },
        "color": "#4A148C",  # 紫
        "level": 5
    }
]

# 業種別経費率マスターデータ
EXPENSE_RATES_BY_BUSINESS = {
    "writer": {
        "name": "ライター",
        "averageRate": 15.0,  # %
        "rangeMin": 10.0,
        "rangeMax": 20.0,
        "commonExpenses": [
            "書籍代・資料代",
            "インターネット通信費",
            "カフェ作業費",
            "PC・周辺機器"
        ]
    },
    "designer": {
        "name": "デザイナー",
        "averageRate": 22.5,
        "rangeMin": 15.0,
        "rangeMax": 30.0,
        "commonExpenses": [
            "Adobe Creative Cloud等ソフトウェア",
            "素材購入費",
            "PC・タブレット・周辺機器",
            "通信費"
        ]
    },
    "engineer": {
        "name": "エンジニア",
        "averageRate": 17.5,
        "rangeMin": 10.0,
        "rangeMax": 25.0,
        "commonExpenses": [
            "サーバー・ドメイン費用",
            "開発ツール・ライセンス",
            "PC・周辺機器",
            "技術書・研修費"
        ]
    },
    "video_editor": {
        "name": "動画編集",
        "averageRate": 30.0,
        "rangeMin": 20.0,
        "rangeMax": 40.0,
        "commonExpenses": [
            "動画編集ソフトウェア",
            "素材・音源購入費",
            "高性能PC・ストレージ",
            "通信費"
        ]
    },
    "other": {
        "name": "その他",
        "averageRate": 20.0,
        "rangeMin": 10.0,
        "rangeMax": 30.0,
        "commonExpenses": [
            "業務に必要な経費を計上",
            "通信費",
            "PC・周辺機器",
            "交通費"
        ]
    }
}


def get_next_wall(current_income: int, wall_type: str = "parttime") -> dict:
    """
    現在の収入から次の壁を取得

    Args:
        current_income: 現在の収入（円）
        wall_type: "parttime" または "freelance"

    Returns:
        次の壁の情報（dict）または None
    """
    walls = INCOME_WALLS_PARTTIME if wall_type == "parttime" else INCOME_WALLS_FREELANCE

    for wall in walls:
        if current_income < wall["amount"]:
            return {
                **wall,
                "remaining": wall["amount"] - current_income
            }

    return None


def get_exceeded_walls(current_income: int, wall_type: str = "parttime") -> list:
    """
    現在の収入で超えた壁を取得

    Args:
        current_income: 現在の収入（円）
        wall_type: "parttime" または "freelance"

    Returns:
        超えた壁のリスト
    """
    walls = INCOME_WALLS_PARTTIME if wall_type == "parttime" else INCOME_WALLS_FREELANCE

    exceeded = []
    for wall in walls:
        if current_income >= wall["amount"]:
            exceeded.append(wall)

    return exceeded
