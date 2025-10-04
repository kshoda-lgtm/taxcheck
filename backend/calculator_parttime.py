"""
アルバイト・パート版の税金・社会保険料計算ロジック
"""

from typing import Dict, List, Optional
from walls_data import get_next_wall, get_exceeded_walls


def calculate_income_tax(taxable_income: int) -> int:
    """
    所得税を計算

    Args:
        taxable_income: 課税所得（円）

    Returns:
        所得税額（円）
    """
    if taxable_income <= 0:
        return 0
    elif taxable_income <= 1950000:
        return int(taxable_income * 0.05)
    elif taxable_income <= 3300000:
        return int(taxable_income * 0.10 - 97500)
    elif taxable_income <= 6950000:
        return int(taxable_income * 0.20 - 427500)
    elif taxable_income <= 9000000:
        return int(taxable_income * 0.23 - 636000)
    else:
        return int(taxable_income * 0.33 - 1536000)


def calculate_resident_tax(annual_income: int) -> int:
    """
    住民税を計算（簡易版）

    Args:
        annual_income: 年収（円）

    Returns:
        住民税額（円）
    """
    # 給与所得控除
    if annual_income <= 1625000:
        employment_income_deduction = 550000
    elif annual_income <= 1800000:
        employment_income_deduction = int(annual_income * 0.4 - 100000)
    elif annual_income <= 3600000:
        employment_income_deduction = int(annual_income * 0.3 + 80000)
    elif annual_income <= 6600000:
        employment_income_deduction = int(annual_income * 0.2 + 440000)
    elif annual_income <= 8500000:
        employment_income_deduction = int(annual_income * 0.1 + 1100000)
    else:
        employment_income_deduction = 1950000

    # 所得
    income = annual_income - employment_income_deduction

    # 基礎控除（住民税は43万円）
    basic_deduction = 430000

    # 課税所得
    taxable_income = max(income - basic_deduction, 0)

    # 住民税（所得割10%）
    if taxable_income == 0:
        return 0

    # 所得割10% + 均等割5,000円（簡易計算）
    return int(taxable_income * 0.10 + 5000)


def check_social_insurance_requirement(
    monthly_income: int,
    weekly_hours: float,
    is_student: bool,
    company_size: str
) -> Dict:
    """
    106万円の壁の社会保険加入要件をチェック

    Args:
        monthly_income: 月収（円）
        weekly_hours: 週の勤務時間
        is_student: 学生かどうか
        company_size: 企業規模（"small" | "medium" | "large"）

    Returns:
        加入要件のチェック結果
    """
    conditions = {
        "weeklyHours": weekly_hours >= 20,
        "monthlyIncome": monthly_income >= 88000,
        "employmentPeriod": True,  # 2ヶ月超は入力で判定困難なためTrue
        "notStudent": not is_student,  # 学生除外特例（夜間・通信制除く）
        "companySize": company_size == "large"  # 101人以上
    }

    # すべての条件を満たす場合、加入義務あり
    is_required = all(conditions.values())

    return {
        "isRequired": is_required,
        "conditions": conditions
    }


def calculate_social_insurance(monthly_income: int) -> Dict:
    """
    社会保険料を計算（概算）

    Args:
        monthly_income: 月収（円）

    Returns:
        社会保険料の内訳
    """
    # 健康保険料（本人負担：約5%）
    health_insurance = int(monthly_income * 0.05)

    # 厚生年金保険料（本人負担：約9.15%）
    pension_insurance = int(monthly_income * 0.0915)

    return {
        "healthInsurance": health_insurance,
        "pensionInsurance": pension_insurance,
        "total": health_insurance + pension_insurance
    }


def calculate_parttime_tax(
    age: int,
    annual_income: int,
    monthly_income: Optional[int] = None,
    is_student: bool = False,
    dependent_type: str = "none",
    company_size: str = "small",
    weekly_hours: float = 0
) -> Dict:
    """
    アルバイト・パートの税金・社会保険料を計算

    Args:
        age: 年齢
        annual_income: 年収（円）
        monthly_income: 月収（円）※社会保険判定用
        is_student: 学生かどうか
        dependent_type: 扶養区分（"parent" | "spouse" | "none"）
        company_size: 企業規模（"small" | "medium" | "large"）
        weekly_hours: 週の勤務時間

    Returns:
        計算結果
    """
    # 月収が指定されていない場合は年収から計算
    if monthly_income is None:
        monthly_income = annual_income // 12

    # 給与所得控除
    if annual_income <= 1625000:
        employment_income_deduction = 550000
    elif annual_income <= 1800000:
        employment_income_deduction = int(annual_income * 0.4 - 100000)
    elif annual_income <= 3600000:
        employment_income_deduction = int(annual_income * 0.3 + 80000)
    elif annual_income <= 6600000:
        employment_income_deduction = int(annual_income * 0.2 + 440000)
    elif annual_income <= 8500000:
        employment_income_deduction = int(annual_income * 0.1 + 1100000)
    else:
        employment_income_deduction = 1950000

    # 所得
    income = annual_income - employment_income_deduction

    # 基礎控除
    basic_deduction = 480000

    # 勤労学生控除（学生で所得75万円以下の場合）
    student_deduction = 270000 if (is_student and income <= 750000) else 0

    # 課税所得
    taxable_income = max(income - basic_deduction - student_deduction, 0)

    # 所得税
    income_tax = calculate_income_tax(taxable_income)

    # 住民税
    resident_tax = calculate_resident_tax(annual_income)

    # 社会保険加入判定（106万円の壁）
    social_insurance_check = check_social_insurance_requirement(
        monthly_income, weekly_hours, is_student, company_size
    )

    # 社会保険料計算
    social_insurance = {"healthInsurance": 0, "pensionInsurance": 0, "total": 0}
    if social_insurance_check["isRequired"]:
        monthly_si = calculate_social_insurance(monthly_income)
        social_insurance = {
            "healthInsurance": monthly_si["healthInsurance"] * 12,
            "pensionInsurance": monthly_si["pensionInsurance"] * 12,
            "total": monthly_si["total"] * 12
        }
        social_insurance_type = "106万"
    elif annual_income >= 1300000:
        # 130万円の壁（扶養から外れる）
        # 国民健康保険・国民年金に加入
        # ※ここでは簡易計算として年間20万円と仮定
        social_insurance = {
            "healthInsurance": 100000,
            "pensionInsurance": 203760,  # 2024年度の国民年金保険料
            "total": 303760
        }
        social_insurance_type = "130万"
    else:
        social_insurance_type = None

    # 手取り額
    net_income = annual_income - income_tax - resident_tax - social_insurance["total"]

    # 超えた壁
    exceeded_walls = get_exceeded_walls(annual_income, "parttime")

    # 次の壁
    next_wall = get_next_wall(annual_income, "parttime")

    # アドバイス生成
    advice = generate_advice(
        annual_income, exceeded_walls, next_wall, is_student, dependent_type
    )

    return {
        "totalIncome": annual_income,
        "monthlyAverage": monthly_income,
        "incomeTax": income_tax,
        "residentTax": resident_tax,
        "socialInsurance": {
            "isRequired": social_insurance_check["isRequired"],
            "type": social_insurance_type,
            **social_insurance,
            "conditions": social_insurance_check["conditions"]
        },
        "netIncome": net_income,
        "wallsExceeded": [
            {
                "amount": wall["amount"],
                "name": wall["name"],
                "impact": wall["impacts"]["self"] or wall["impacts"]["family"]
            }
            for wall in exceeded_walls
        ],
        "nextWall": next_wall,
        "advice": advice
    }


def generate_advice(
    annual_income: int,
    exceeded_walls: List,
    next_wall: Optional[Dict],
    is_student: bool,
    dependent_type: str
) -> str:
    """
    状況に応じたアドバイスを生成

    Args:
        annual_income: 年収
        exceeded_walls: 超えた壁のリスト
        next_wall: 次の壁
        is_student: 学生かどうか
        dependent_type: 扶養区分

    Returns:
        アドバイス文
    """
    if annual_income < 1030000:
        if next_wall and next_wall["amount"] == 1030000:
            return f"現在の年収は{annual_income:,}円です。103万円の壁まであと{next_wall['remaining']:,}円です。このまま働いても扶養内で所得税もかかりません。"
        return "安全圏です。このまま働いても問題ありません。"

    elif annual_income < 1060000:
        if dependent_type == "parent":
            return f"103万円を超えています。本人に所得税が発生し、親の扶養控除も外れるため、親の税負担が年間5〜16万円増えます。106万円の壁まであと{next_wall['remaining']:,}円です。"
        return "103万円を超えています。所得税が発生します。"

    elif annual_income < 1300000:
        if is_student:
            return "106万円を超えていますが、学生の場合は学生除外特例により社会保険加入義務はありません（夜間・通信制除く）。130万円の壁まで注意しましょう。"
        return "106万円を超えています。大企業で条件を満たすと社会保険加入義務が発生します（年間約15万円の負担）。"

    elif annual_income < 1500000:
        return "130万円を超えています。親の社会保険扶養から外れ、国民健康保険・国民年金に加入する必要があります（年間約30万円の負担）。"

    else:
        return "150万円を超えています。配偶者控除も減少し、完全自立ゾーンです。"


if __name__ == "__main__":
    # テスト実行
    result = calculate_parttime_tax(
        age=20,
        annual_income=1200000,
        is_student=True,
        dependent_type="parent",
        company_size="large",
        weekly_hours=25
    )

    print("=== 計算結果 ===")
    print(f"年収: {result['totalIncome']:,}円")
    print(f"所得税: {result['incomeTax']:,}円")
    print(f"住民税: {result['residentTax']:,}円")
    print(f"社会保険料: {result['socialInsurance']['total']:,}円")
    print(f"手取り: {result['netIncome']:,}円")
    print(f"\n超えた壁:")
    for wall in result['wallsExceeded']:
        print(f"  - {wall['name']}: {wall['impact']}")
    print(f"\n次の壁: {result['nextWall']['name'] if result['nextWall'] else 'なし'}")
    if result['nextWall']:
        print(f"  あと{result['nextWall']['remaining']:,}円")
    print(f"\nアドバイス: {result['advice']}")
