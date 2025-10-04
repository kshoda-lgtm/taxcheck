"""
業務委託版の税金・社会保険料計算ロジック
"""

from typing import Dict, List, Optional
from walls_data import get_next_wall, get_exceeded_walls, EXPENSE_RATES_BY_BUSINESS


def calculate_income_tax_freelance(taxable_income: int) -> int:
    """
    所得税を計算（事業所得ベース）

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


def calculate_resident_tax_freelance(business_income: int) -> int:
    """
    住民税を計算（事業所得ベース）

    Args:
        business_income: 事業所得（円）

    Returns:
        住民税額（円）
    """
    # 基礎控除（住民税は43万円）
    basic_deduction = 430000

    # 課税所得
    taxable_income = max(business_income - basic_deduction, 0)

    # 住民税（所得割10%）
    if taxable_income == 0:
        return 0

    # 所得割10% + 均等割5,000円（簡易計算）
    return int(taxable_income * 0.10 + 5000)


def calculate_business_tax(business_income: int, business_type: str) -> int:
    """
    個人事業税を計算

    Args:
        business_income: 事業所得（円）
        business_type: 事業種類

    Returns:
        個人事業税額（円）
    """
    # 事業主控除290万円
    business_deduction = 2900000

    # 課税所得
    taxable_income = max(business_income - business_deduction, 0)

    if taxable_income == 0:
        return 0

    # 業種別税率（ここでは5%で統一）
    tax_rate = 0.05

    return int(taxable_income * tax_rate)


def calculate_national_health_insurance(business_income: int) -> int:
    """
    国民健康保険料を計算（概算）

    Args:
        business_income: 事業所得（円）

    Returns:
        国民健康保険料（円）
    """
    # 基礎控除
    basic_deduction = 430000

    # 所得
    income = max(business_income - basic_deduction, 0)

    # 国民健康保険料（所得の約10% + 均等割）
    # ※市区町村により異なるため簡易計算
    income_based = int(income * 0.10)
    flat_rate = 40000  # 均等割（概算）

    return income_based + flat_rate


def calculate_national_pension() -> int:
    """
    国民年金保険料を計算

    Returns:
        国民年金保険料（円/年）
    """
    # 2024年度の国民年金保険料（月額16,980円）
    return 16980 * 12


def calculate_freelance_tax(
    age: int,
    annual_revenue: int,
    annual_expense: int,
    is_student: bool = False,
    dependent_type: str = "none",
    tax_filing_type: str = "white",
    business_type: str = "other"
) -> Dict:
    """
    業務委託・フリーランスの税金・社会保険料を計算

    Args:
        age: 年齢
        annual_revenue: 年間売上（円）
        annual_expense: 年間経費（円）
        is_student: 学生かどうか
        dependent_type: 扶養区分（"parent" | "spouse" | "none"）
        tax_filing_type: 申告種類（"white" | "blue10" | "blue65"）
        business_type: 事業種類（"writer" | "designer" | "engineer" | "video_editor" | "other"）

    Returns:
        計算結果
    """
    # 青色申告特別控除
    if tax_filing_type == "blue65":
        blue_filing_deduction = 650000
    elif tax_filing_type == "blue10":
        blue_filing_deduction = 100000
    else:
        blue_filing_deduction = 0

    # 事業所得
    business_income = annual_revenue - annual_expense - blue_filing_deduction

    # 基礎控除
    basic_deduction = 480000

    # 課税所得
    taxable_income = max(business_income - basic_deduction, 0)

    # 所得税
    income_tax = calculate_income_tax_freelance(taxable_income)

    # 住民税
    resident_tax = calculate_resident_tax_freelance(business_income)

    # 個人事業税
    business_tax = calculate_business_tax(business_income, business_type)

    # 国民健康保険料
    health_insurance = calculate_national_health_insurance(business_income)

    # 国民年金保険料
    pension_insurance = calculate_national_pension()

    # 学生納付特例（所得118万円以下）
    student_pension_exemption = is_student and business_income <= 1180000

    # 手取り額
    total_tax = income_tax + resident_tax + business_tax
    total_insurance = health_insurance + (0 if student_pension_exemption else pension_insurance)
    net_income = annual_revenue - annual_expense - total_tax - total_insurance

    # 経費率
    expense_rate = (annual_expense / annual_revenue * 100) if annual_revenue > 0 else 0

    # 業種平均経費率
    industry_data = EXPENSE_RATES_BY_BUSINESS.get(business_type, EXPENSE_RATES_BY_BUSINESS["other"])
    industry_average_expense_rate = industry_data["averageRate"]

    # 残り経費計上可能額（業種平均まで）
    remaining_expense_capacity = max(
        int(annual_revenue * industry_average_expense_rate / 100) - annual_expense,
        0
    )

    # 超えた壁（所得ベース）
    exceeded_walls = get_exceeded_walls(business_income, "freelance")

    # 次の壁（所得ベース）
    next_wall = get_next_wall(business_income, "freelance")

    # 青色申告vs白色申告の比較
    blue_vs_white_comparison = compare_blue_vs_white(
        annual_revenue, annual_expense, business_income, income_tax, total_tax, net_income, tax_filing_type
    )

    # 確定申告が必要かどうか
    confirmation_required = business_income > 480000  # 基礎控除を超える場合

    # アドバイス生成
    advice = generate_advice_freelance(
        business_income,
        exceeded_walls,
        next_wall,
        is_student,
        dependent_type,
        tax_filing_type,
        expense_rate,
        industry_average_expense_rate,
        remaining_expense_capacity
    )

    return {
        "totalRevenue": annual_revenue,
        "totalExpense": annual_expense,
        "expenseRate": round(expense_rate, 1),
        "industryAverageExpenseRate": industry_average_expense_rate,
        "blueFilingDeduction": blue_filing_deduction,
        "businessIncome": business_income,
        "incomeTax": income_tax,
        "residentTax": resident_tax,
        "businessTax": business_tax,
        "healthInsurance": health_insurance,
        "pensionInsurance": pension_insurance,
        "studentPensionExemption": student_pension_exemption,
        "totalTax": total_tax,
        "totalInsurance": total_insurance if not student_pension_exemption else health_insurance,
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
        "blueVsWhiteComparison": blue_vs_white_comparison,
        "remainingExpenseCapacity": remaining_expense_capacity,
        "confirmationRequired": confirmation_required,
        "advice": advice
    }


def compare_blue_vs_white(
    revenue: int,
    expense: int,
    current_income: int,
    current_income_tax: int,
    current_total_tax: int,
    current_net_income: int,
    current_type: str
) -> Dict:
    """
    青色申告vs白色申告の比較

    Args:
        revenue: 売上
        expense: 経費
        current_income: 現在の事業所得
        current_income_tax: 現在の所得税
        current_total_tax: 現在の合計税額
        current_net_income: 現在の手取り
        current_type: 現在の申告タイプ

    Returns:
        比較結果
    """
    # 白色申告の場合
    white_income = revenue - expense
    white_taxable_income = max(white_income - 480000, 0)
    white_income_tax = calculate_income_tax_freelance(white_taxable_income)
    white_resident_tax = calculate_resident_tax_freelance(white_income)
    white_total_tax = white_income_tax + white_resident_tax
    white_net_income = revenue - expense - white_total_tax

    # 青色申告10万円の場合
    blue10_income = revenue - expense - 100000
    blue10_taxable_income = max(blue10_income - 480000, 0)
    blue10_income_tax = calculate_income_tax_freelance(blue10_taxable_income)
    blue10_resident_tax = calculate_resident_tax_freelance(blue10_income)
    blue10_total_tax = blue10_income_tax + blue10_resident_tax
    blue10_net_income = revenue - expense - blue10_total_tax

    # 青色申告65万円の場合
    blue65_income = revenue - expense - 650000
    blue65_taxable_income = max(blue65_income - 480000, 0)
    blue65_income_tax = calculate_income_tax_freelance(blue65_taxable_income)
    blue65_resident_tax = calculate_resident_tax_freelance(blue65_income)
    blue65_total_tax = blue65_income_tax + blue65_resident_tax
    blue65_net_income = revenue - expense - blue65_total_tax

    # 節税額
    savings_blue10 = white_total_tax - blue10_total_tax
    savings_blue65 = white_total_tax - blue65_total_tax

    return {
        "white": {
            "income": white_income,
            "tax": white_total_tax,
            "netIncome": white_net_income
        },
        "blue10": {
            "income": blue10_income,
            "tax": blue10_total_tax,
            "netIncome": blue10_net_income
        },
        "blue65": {
            "income": blue65_income,
            "tax": blue65_total_tax,
            "netIncome": blue65_net_income
        },
        "savingsBlue10": savings_blue10,
        "savingsBlue65": savings_blue65
    }


def generate_advice_freelance(
    business_income: int,
    exceeded_walls: List,
    next_wall: Optional[Dict],
    is_student: bool,
    dependent_type: str,
    tax_filing_type: str,
    expense_rate: float,
    industry_average: float,
    remaining_expense: int
) -> str:
    """
    状況に応じたアドバイスを生成（業務委託版）

    Args:
        business_income: 事業所得
        exceeded_walls: 超えた壁のリスト
        next_wall: 次の壁
        is_student: 学生かどうか
        dependent_type: 扶養区分
        tax_filing_type: 申告タイプ
        expense_rate: 経費率
        industry_average: 業種平均経費率
        remaining_expense: 残り経費計上可能額

    Returns:
        アドバイス文
    """
    advice_parts = []

    # 所得に関するアドバイス
    if business_income < 480000:
        advice_parts.append(f"現在の所得は{business_income:,}円です。基礎控除48万円以下のため所得税は発生しません。")
    elif business_income < 1030000:
        advice_parts.append(f"所得が48万円を超えているため所得税が発生します。")
    elif business_income < 1300000:
        if dependent_type == "parent":
            advice_parts.append("103万円（給与所得換算）を超えているため、親の扶養控除が外れます。親の税負担が年間5〜16万円増える可能性があります。")
    elif business_income < 2900000:
        advice_parts.append("130万円を超えているため、親の社会保険扶養から外れます。国民健康保険・国民年金に加入が必要です。")
    else:
        advice_parts.append("290万円を超えているため、個人事業税が発生します。")

    # 青色申告に関するアドバイス
    if tax_filing_type == "white" and business_income > 480000:
        advice_parts.append(f"青色申告65万円控除を使えば、年間約{abs(business_income * 0.15):,.0f}円の節税が可能です。")

    # 経費に関するアドバイス
    if expense_rate < industry_average and remaining_expense > 0:
        advice_parts.append(f"経費率が業種平均({industry_average}%)より低いです。適切な経費計上であと{remaining_expense:,}円計上できる可能性があります。")

    # 学生納付特例
    if is_student and business_income <= 1180000:
        advice_parts.append("学生納付特例により、国民年金の納付を猶予できます。")

    # 次の壁へのアドバイス
    if next_wall:
        advice_parts.append(f"次の壁は{next_wall['name']}（あと{next_wall['remaining']:,}円）です。")

    return " ".join(advice_parts) if advice_parts else "適切に収入管理ができています。"


if __name__ == "__main__":
    # テスト実行
    result = calculate_freelance_tax(
        age=20,
        annual_revenue=1500000,
        annual_expense=300000,
        is_student=True,
        dependent_type="parent",
        tax_filing_type="blue65",
        business_type="writer"
    )

    print("=== 計算結果（業務委託版） ===")
    print(f"年間売上: {result['totalRevenue']:,}円")
    print(f"年間経費: {result['totalExpense']:,}円")
    print(f"経費率: {result['expenseRate']}%")
    print(f"業種平均経費率: {result['industryAverageExpenseRate']}%")
    print(f"青色申告特別控除: {result['blueFilingDeduction']:,}円")
    print(f"事業所得: {result['businessIncome']:,}円")
    print(f"所得税: {result['incomeTax']:,}円")
    print(f"住民税: {result['residentTax']:,}円")
    print(f"個人事業税: {result['businessTax']:,}円")
    print(f"国民健康保険料: {result['healthInsurance']:,}円")
    print(f"国民年金保険料: {result['pensionInsurance']:,}円")
    print(f"学生納付特例: {'適用' if result['studentPensionExemption'] else '適用外'}")
    print(f"手取り: {result['netIncome']:,}円")
    print(f"\n超えた壁:")
    for wall in result['wallsExceeded']:
        print(f"  - {wall['name']}: {wall['impact']}")
    print(f"\n次の壁: {result['nextWall']['name'] if result['nextWall'] else 'なし'}")
    if result['nextWall']:
        print(f"  あと{result['nextWall']['remaining']:,}円")
    print(f"\n確定申告: {'必要' if result['confirmationRequired'] else '不要'}")
    print(f"\nアドバイス: {result['advice']}")
    print(f"\n=== 青色申告vs白色申告 ===")
    print(f"白色申告: 税額{result['blueVsWhiteComparison']['white']['tax']:,}円 / 手取り{result['blueVsWhiteComparison']['white']['netIncome']:,}円")
    print(f"青色10万円: 税額{result['blueVsWhiteComparison']['blue10']['tax']:,}円 / 手取り{result['blueVsWhiteComparison']['blue10']['netIncome']:,}円 (節税{result['blueVsWhiteComparison']['savingsBlue10']:,}円)")
    print(f"青色65万円: 税額{result['blueVsWhiteComparison']['blue65']['tax']:,}円 / 手取り{result['blueVsWhiteComparison']['blue65']['netIncome']:,}円 (節税{result['blueVsWhiteComparison']['savingsBlue65']:,}円)")
