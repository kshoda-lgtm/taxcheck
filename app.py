"""
TaxCheck - 収入の壁チェッカー（Streamlitアプリ）
"""

import streamlit as st
import sys
from pathlib import Path

# バックエンドモジュールをインポート
sys.path.append(str(Path(__file__).parent / "backend"))
from calculator_parttime import calculate_parttime_tax
from calculator_freelance import calculate_freelance_tax
from walls_data import INCOME_WALLS_PARTTIME, INCOME_WALLS_FREELANCE, EXPENSE_RATES_BY_BUSINESS

# ページ設定
st.set_page_config(
    page_title="TaxCheck - 収入の壁チェッカー",
    page_icon="💰",
    layout="wide"
)

# タイトル
st.title("💰 TaxCheck - 収入の壁チェッカー")
st.markdown("### 学生バイト・フリーランスの税金・社会保険が一目でわかる！")

# サイドバーでバージョン選択
st.sidebar.title("📋 メニュー")
app_mode = st.sidebar.radio(
    "計算タイプを選択",
    ["アルバイト・パート版", "業務委託版", "収入の壁について"]
)

# セッションステートの初期化
if 'monthly_incomes' not in st.session_state:
    st.session_state.monthly_incomes = [0] * 12

if 'monthly_revenues' not in st.session_state:
    st.session_state.monthly_revenues = [0] * 12

if 'monthly_expenses' not in st.session_state:
    st.session_state.monthly_expenses = [0] * 12


def display_walls_info():
    """収入の壁の情報を表示"""
    st.header("📊 収入の壁について")

    tab1, tab2 = st.tabs(["アルバイト・パート版", "業務委託版"])

    with tab1:
        st.subheader("アルバイト・パートの5本柱")

        for wall in INCOME_WALLS_PARTTIME:
            with st.expander(f"**{wall['name']}** - {wall['category']}", expanded=False):
                st.markdown(f"**金額**: {wall['amount']:,}円")
                st.markdown(f"**説明**: {wall['description']}")

                if wall['impacts']['self']:
                    st.markdown(f"**本人への影響**: {wall['impacts']['self']}")
                if wall['impacts']['family']:
                    st.markdown(f"**家族への影響**: {wall['impacts']['family']}")

                if 'conditions' in wall:
                    st.markdown("**条件**:")
                    for condition in wall['conditions']:
                        st.markdown(f"- {condition}")

        st.markdown("---")
        st.markdown("### 典型的な境界早見表")

        table_data = [
            ("〜103万円", "所得税なし", "扶養OK"),
            ("103〜106万円", "所得税あり", "社保は条件次第"),
            ("106〜130万円", "所得税あり", "学生除外なら社保なし"),
            ("130〜150万円", "扶養喪失リスク", "親の負担増"),
            ("150〜201万円", "所得税＋住民税発生", "完全自立ゾーン"),
        ]

        for income_range, impact, detail in table_data:
            col1, col2, col3 = st.columns(3)
            col1.markdown(f"**{income_range}**")
            col2.markdown(impact)
            col3.markdown(detail)

    with tab2:
        st.subheader("業務委託の5本柱")

        for wall in INCOME_WALLS_FREELANCE:
            with st.expander(f"**{wall['name']}** - {wall['category']}", expanded=False):
                st.markdown(f"**金額**: {wall['amount']:,}円")
                st.markdown(f"**説明**: {wall['description']}")

                if 'note' in wall:
                    st.markdown(f"**注意**: {wall['note']}")

                if wall['impacts']['self']:
                    st.markdown(f"**本人への影響**: {wall['impacts']['self']}")
                if wall['impacts']['family']:
                    st.markdown(f"**家族への影響**: {wall['impacts']['family']}")


def display_parttime_app():
    """アルバイト・パート版のアプリを表示"""
    st.header("💼 アルバイト・パート版")

    # 基本情報入力
    st.subheader("1. 基本情報")
    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input("年齢", min_value=15, max_value=100, value=20)
        is_student = st.checkbox("学生である")
        dependent_type = st.selectbox(
            "扶養区分",
            ["なし", "親の扶養", "配偶者の扶養"],
            index=1
        )

    with col2:
        company_size = st.selectbox(
            "勤務先の従業員数",
            ["50人以下", "51〜100人", "101人以上"],
            index=0
        )
        weekly_hours = st.number_input(
            "週の勤務時間",
            min_value=0.0,
            max_value=40.0,
            value=15.0,
            step=0.5
        )

    # 扶養区分をコードに変換
    dependent_map = {
        "なし": "none",
        "親の扶養": "parent",
        "配偶者の扶養": "spouse"
    }
    dependent_code = dependent_map[dependent_type]

    # 企業規模をコードに変換
    company_size_map = {
        "50人以下": "small",
        "51〜100人": "medium",
        "101人以上": "large"
    }
    company_size_code = company_size_map[company_size]

    # 収入入力
    st.subheader("2. 月別収入入力")

    input_mode = st.radio("入力方法", ["年収一括入力", "月別入力"])

    if input_mode == "年収一括入力":
        annual_income = st.number_input(
            "年収（円）",
            min_value=0,
            max_value=10000000,
            value=1000000,
            step=10000
        )
    else:
        st.markdown("各月の収入を入力してください")
        cols = st.columns(4)
        months = ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"]

        for i, month in enumerate(months):
            col_idx = i % 4
            with cols[col_idx]:
                st.session_state.monthly_incomes[i] = st.number_input(
                    month,
                    min_value=0,
                    max_value=1000000,
                    value=st.session_state.monthly_incomes[i],
                    step=10000,
                    key=f"income_{i}"
                )

        annual_income = sum(st.session_state.monthly_incomes)
        st.markdown(f"**年間合計**: {annual_income:,}円")

    # 計算ボタン
    if st.button("💡 計算する", type="primary"):
        # 計算実行
        result = calculate_parttime_tax(
            age=age,
            annual_income=annual_income,
            is_student=is_student,
            dependent_type=dependent_code,
            company_size=company_size_code,
            weekly_hours=weekly_hours
        )

        # 結果表示
        st.markdown("---")
        st.subheader("📊 計算結果")

        # サマリー
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("年収", f"{result['totalIncome']:,}円")
        with col2:
            st.metric("所得税", f"{result['incomeTax']:,}円")
        with col3:
            st.metric("住民税", f"{result['residentTax']:,}円")
        with col4:
            st.metric("社会保険料", f"{result['socialInsurance']['total']:,}円")

        # 手取り額（大きく表示）
        st.markdown("### 💰 手取り額")
        st.markdown(f"# {result['netIncome']:,}円")

        # 社会保険加入判定
        if result['socialInsurance']['isRequired']:
            st.warning("⚠️ 社会保険加入義務があります（106万円の壁）")

            st.markdown("**加入条件チェック**:")
            conditions = result['socialInsurance']['conditions']
            st.markdown(f"- 週20時間以上: {'✅' if conditions['weeklyHours'] else '❌'}")
            st.markdown(f"- 月88,000円以上: {'✅' if conditions['monthlyIncome'] else '❌'}")
            st.markdown(f"- 2ヶ月超雇用: {'✅' if conditions['employmentPeriod'] else '❌'}")
            st.markdown(f"- 学生でない: {'✅' if conditions['notStudent'] else '❌'}")
            st.markdown(f"- 101人以上の企業: {'✅' if conditions['companySize'] else '❌'}")

        # 超えた壁
        if result['wallsExceeded']:
            st.markdown("### 🚨 超えた壁")
            for wall in result['wallsExceeded']:
                st.error(f"**{wall['name']}**: {wall['impact']}")

        # 次の壁
        if result['nextWall']:
            st.markdown("### 🎯 次の壁まで")
            st.info(f"**{result['nextWall']['name']}** まで あと **{result['nextWall']['remaining']:,}円**")

        # アドバイス
        st.markdown("### 💡 アドバイス")
        st.info(result['advice'])


def display_freelance_app():
    """業務委託版のアプリを表示"""
    st.header("🖥️ 業務委託版")

    # 基本情報入力
    st.subheader("1. 基本情報")
    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input("年齢", min_value=15, max_value=100, value=20)
        is_student = st.checkbox("学生である")
        dependent_type = st.selectbox(
            "扶養区分",
            ["なし", "親の扶養", "配偶者の扶養"],
            index=1
        )

    with col2:
        tax_filing_type = st.selectbox(
            "確定申告の種類",
            ["白色申告", "青色申告（10万円控除）", "青色申告（65万円控除）"],
            index=2
        )
        business_type = st.selectbox(
            "事業種類",
            ["ライター", "デザイナー", "エンジニア", "動画編集", "その他"],
            index=0
        )

    # 確定申告タイプをコードに変換
    tax_filing_map = {
        "白色申告": "white",
        "青色申告（10万円控除）": "blue10",
        "青色申告（65万円控除）": "blue65"
    }
    tax_filing_code = tax_filing_map[tax_filing_type]

    # 事業種類をコードに変換
    business_type_map = {
        "ライター": "writer",
        "デザイナー": "designer",
        "エンジニア": "engineer",
        "動画編集": "video_editor",
        "その他": "other"
    }
    business_type_code = business_type_map[business_type]

    # 売上・経費入力
    st.subheader("2. 売上・経費入力")

    input_mode = st.radio("入力方法", ["年間一括入力", "月別入力"])

    if input_mode == "年間一括入力":
        col1, col2 = st.columns(2)
        with col1:
            annual_revenue = st.number_input(
                "年間売上（円）",
                min_value=0,
                max_value=50000000,
                value=1500000,
                step=10000
            )
        with col2:
            annual_expense = st.number_input(
                "年間経費（円）",
                min_value=0,
                max_value=annual_revenue,
                value=300000,
                step=10000
            )
    else:
        st.markdown("各月の売上・経費を入力してください")

        tab1, tab2 = st.tabs(["売上", "経費"])

        with tab1:
            cols = st.columns(4)
            months = ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"]

            for i, month in enumerate(months):
                col_idx = i % 4
                with cols[col_idx]:
                    st.session_state.monthly_revenues[i] = st.number_input(
                        month,
                        min_value=0,
                        max_value=10000000,
                        value=st.session_state.monthly_revenues[i],
                        step=10000,
                        key=f"revenue_{i}"
                    )

            annual_revenue = sum(st.session_state.monthly_revenues)
            st.markdown(f"**年間合計売上**: {annual_revenue:,}円")

        with tab2:
            cols = st.columns(4)

            for i, month in enumerate(months):
                col_idx = i % 4
                with cols[col_idx]:
                    st.session_state.monthly_expenses[i] = st.number_input(
                        month,
                        min_value=0,
                        max_value=10000000,
                        value=st.session_state.monthly_expenses[i],
                        step=10000,
                        key=f"expense_{i}"
                    )

            annual_expense = sum(st.session_state.monthly_expenses)
            st.markdown(f"**年間合計経費**: {annual_expense:,}円")

    # 扶養区分をコードに変換
    dependent_map = {
        "なし": "none",
        "親の扶養": "parent",
        "配偶者の扶養": "spouse"
    }
    dependent_code = dependent_map[dependent_type]

    # 計算ボタン
    if st.button("💡 計算する", type="primary"):
        # 計算実行
        result = calculate_freelance_tax(
            age=age,
            annual_revenue=annual_revenue,
            annual_expense=annual_expense,
            is_student=is_student,
            dependent_type=dependent_code,
            tax_filing_type=tax_filing_code,
            business_type=business_type_code
        )

        # 結果表示
        st.markdown("---")
        st.subheader("📊 計算結果")

        # サマリー
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("年間売上", f"{result['totalRevenue']:,}円")
            st.metric("年間経費", f"{result['totalExpense']:,}円")
            st.metric(f"経費率", f"{result['expenseRate']}%")

        with col2:
            st.metric("青色申告特別控除", f"{result['blueFilingDeduction']:,}円")
            st.metric("事業所得", f"{result['businessIncome']:,}円")

        with col3:
            st.metric("所得税", f"{result['incomeTax']:,}円")
            st.metric("住民税", f"{result['residentTax']:,}円")
            st.metric("個人事業税", f"{result['businessTax']:,}円")

        # 社会保険料
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("国民健康保険料", f"{result['healthInsurance']:,}円")
        with col2:
            pension_display = 0 if result['studentPensionExemption'] else result['pensionInsurance']
            st.metric("国民年金保険料", f"{pension_display:,}円")
            if result['studentPensionExemption']:
                st.caption("（学生納付特例適用）")
        with col3:
            st.metric("合計税金", f"{result['totalTax']:,}円")

        # 手取り額（大きく表示）
        st.markdown("### 💰 手取り額")
        st.markdown(f"# {result['netIncome']:,}円")

        # 経費率チェック
        if result['expenseRate'] < result['industryAverageExpenseRate']:
            st.warning(f"⚠️ 経費率が業種平均（{result['industryAverageExpenseRate']}%）より低いです")
            st.info(f"適切な経費計上で、あと{result['remainingExpenseCapacity']:,}円計上できる可能性があります")

        # 青色申告vs白色申告比較
        st.markdown("### 📊 青色申告 vs 白色申告")

        comparison = result['blueVsWhiteComparison']

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("#### 白色申告")
            st.markdown(f"所得: {comparison['white']['income']:,}円")
            st.markdown(f"税額: {comparison['white']['tax']:,}円")
            st.markdown(f"手取り: {comparison['white']['netIncome']:,}円")

        with col2:
            st.markdown("#### 青色10万円")
            st.markdown(f"所得: {comparison['blue10']['income']:,}円")
            st.markdown(f"税額: {comparison['blue10']['tax']:,}円")
            st.markdown(f"手取り: {comparison['blue10']['netIncome']:,}円")
            st.success(f"節税額: {comparison['savingsBlue10']:,}円")

        with col3:
            st.markdown("#### 青色65万円")
            st.markdown(f"所得: {comparison['blue65']['income']:,}円")
            st.markdown(f"税額: {comparison['blue65']['tax']:,}円")
            st.markdown(f"手取り: {comparison['blue65']['netIncome']:,}円")
            st.success(f"節税額: {comparison['savingsBlue65']:,}円")

        # 超えた壁
        if result['wallsExceeded']:
            st.markdown("### 🚨 超えた壁")
            for wall in result['wallsExceeded']:
                st.error(f"**{wall['name']}**: {wall['impact']}")

        # 次の壁
        if result['nextWall']:
            st.markdown("### 🎯 次の壁まで")
            st.info(f"**{result['nextWall']['name']}** まで あと **{result['nextWall']['remaining']:,}円**")

        # 確定申告
        st.markdown("### 📝 確定申告")
        if result['confirmationRequired']:
            st.warning("確定申告が必要です（期限: 翌年3月15日）")
        else:
            st.success("確定申告は不要です")

        # アドバイス
        st.markdown("### 💡 アドバイス")
        st.info(result['advice'])


# メイン処理
if app_mode == "アルバイト・パート版":
    display_parttime_app()
elif app_mode == "業務委託版":
    display_freelance_app()
else:
    display_walls_info()

# フッター
st.markdown("---")
st.markdown("© 2025 TaxCheck - 収入の壁チェッカー | 🤖 Generated with [Claude Code](https://claude.com/claude-code)")
st.caption("⚠️ このアプリは簡易計算ツールです。正確な税額計算には税理士への相談が必要です。")
