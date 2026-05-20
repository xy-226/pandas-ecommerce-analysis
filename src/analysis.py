from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

try:
    from clean_data import clean_data
    from load_data import PROJECT_ROOT, load_raw_data
except ImportError:  # pragma: no cover - helpful when imported as a package
    from .clean_data import clean_data
    from .load_data import PROJECT_ROOT, load_raw_data


OUTPUT_DIR = PROJECT_ROOT / "output"
TABLES_DIR = OUTPUT_DIR / "tables"
FIGURES_DIR = OUTPUT_DIR / "figures"
REPORTS_DIR = PROJECT_ROOT / "reports"

Y_AXIS_LABELS = {
    "orders": "订单量",
    "net_sales": "净销售额",
    "gross_sales": "总销售额",
    "discount_amount": "折扣金额",
    "cancel_rate": "取消率",
    "refund_rate": "退款率",
    "customers": "客户数",
}


def ensure_output_dirs() -> None:
    """确保输出表格和图表目录存在。"""
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def configure_chinese_font() -> None:
    """配置常见中文字体，避免图表标题出现乱码或方块。"""
    plt.rcParams["font.sans-serif"] = [
        "Microsoft YaHei",
        "SimHei",
        "Arial Unicode MS",
        "Noto Sans CJK SC",
        "DejaVu Sans",
    ]
    plt.rcParams["axes.unicode_minus"] = False


def summarize_monthly_sales(df: pd.DataFrame) -> pd.DataFrame:
    """按月份汇总销售趋势，用于观察订单量、销售额和客户数变化。"""
    return (
        df.groupby("order_period", dropna=False)
        .agg(
            orders=("item_id", "count"),
            valid_orders=("is_valid_sale", "sum"),
            cancelled_orders=("is_cancelled", "sum"),
            refunded_orders=("is_refunded", "sum"),
            gross_sales=("gross_sales", "sum"),
            net_sales=("net_sales", "sum"),
            discount_amount=("discount_amount", "sum"),
            customers=("customer_id", "nunique"),
        )
        .reset_index()
        .assign(
            valid_rate=lambda data: data["valid_orders"] / data["orders"],
            cancel_rate=lambda data: data["cancelled_orders"] / data["orders"],
            refund_rate=lambda data: data["refunded_orders"] / data["orders"],
        )
        .sort_values("order_period")
    )


def summarize_category_sales(df: pd.DataFrame) -> pd.DataFrame:
    """按商品品类汇总销售表现，用于识别核心收入品类。"""
    return (
        df.groupby("category_name_1", dropna=False)
        .agg(
            orders=("item_id", "count"),
            valid_orders=("is_valid_sale", "sum"),
            net_sales=("net_sales", "sum"),
            gross_sales=("gross_sales", "sum"),
            avg_order_value=("grand_total", "mean"),
            customers=("customer_id", "nunique"),
        )
        .reset_index()
        .assign(
            valid_rate=lambda data: data["valid_orders"] / data["orders"],
            net_sales_share=lambda data: data["net_sales"] / data["net_sales"].sum(),
        )
        .sort_values("net_sales", ascending=False)
    )


def summarize_payment_methods(df: pd.DataFrame) -> pd.DataFrame:
    """按支付方式汇总订单表现，用于观察支付偏好和取消率。"""
    return (
        df.groupby("payment_method", dropna=False)
        .agg(
            orders=("item_id", "count"),
            valid_orders=("is_valid_sale", "sum"),
            cancelled_orders=("is_cancelled", "sum"),
            net_sales=("net_sales", "sum"),
            avg_order_value=("grand_total", "mean"),
        )
        .reset_index()
        .assign(
            cancel_rate=lambda data: data["cancelled_orders"] / data["orders"],
            order_share=lambda data: data["orders"] / data["orders"].sum(),
        )
        .sort_values("orders", ascending=False)
    )


def summarize_order_status(df: pd.DataFrame) -> pd.DataFrame:
    """按订单状态汇总订单量和销售额，用于评估取消、退款等订单结构。"""
    total_orders = len(df)
    return (
        df.groupby("status", dropna=False)
        .agg(
            orders=("item_id", "count"),
            net_sales=("net_sales", "sum"),
            gross_sales=("gross_sales", "sum"),
        )
        .reset_index()
        .assign(order_share=lambda data: data["orders"] / total_orders)
        .sort_values("orders", ascending=False)
    )


def summarize_customers(df: pd.DataFrame) -> pd.DataFrame:
    """按客户汇总消费贡献，用于识别高价值客户。"""
    return (
        df.groupby("customer_id", dropna=True)
        .agg(
            orders=("item_id", "count"),
            valid_orders=("is_valid_sale", "sum"),
            net_sales=("net_sales", "sum"),
            first_order=("order_date", "min"),
            last_order=("order_date", "max"),
        )
        .reset_index()
        .sort_values("net_sales", ascending=False)
    )


def summarize_cancellation_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """按品类拆解取消和退款情况，用于定位履约或转化风险较高的品类。"""
    return (
        df.groupby("category_name_1", dropna=False)
        .agg(
            orders=("item_id", "count"),
            valid_orders=("is_valid_sale", "sum"),
            cancelled_orders=("is_cancelled", "sum"),
            refunded_orders=("is_refunded", "sum"),
            net_sales=("net_sales", "sum"),
        )
        .reset_index()
        .assign(
            cancel_rate=lambda data: data["cancelled_orders"] / data["orders"],
            refund_rate=lambda data: data["refunded_orders"] / data["orders"],
        )
        .sort_values(["cancel_rate", "orders"], ascending=[False, False])
    )


def summarize_cancellation_by_payment(df: pd.DataFrame) -> pd.DataFrame:
    """按支付方式拆解取消和退款情况，用于观察支付方式与订单风险的关系。"""
    return (
        df.groupby("payment_method", dropna=False)
        .agg(
            orders=("item_id", "count"),
            valid_orders=("is_valid_sale", "sum"),
            cancelled_orders=("is_cancelled", "sum"),
            refunded_orders=("is_refunded", "sum"),
            net_sales=("net_sales", "sum"),
        )
        .reset_index()
        .assign(
            cancel_rate=lambda data: data["cancelled_orders"] / data["orders"],
            refund_rate=lambda data: data["refunded_orders"] / data["orders"],
        )
        .sort_values(["cancel_rate", "orders"], ascending=[False, False])
    )


def summarize_discount_impact(df: pd.DataFrame) -> pd.DataFrame:
    """按折扣率区间汇总订单表现，用于观察折扣力度与订单结果的关系。"""
    discount_rate = df["discount_rate"].fillna(0).clip(lower=0)
    bins = [-0.01, 0, 0.05, 0.15, 0.30, float("inf")]
    labels = ["无折扣", "0-5%", "5-15%", "15-30%", "30%以上"]
    discount_data = df.assign(discount_bucket=pd.cut(discount_rate, bins=bins, labels=labels))

    return (
        discount_data.groupby("discount_bucket", observed=False)
        .agg(
            orders=("item_id", "count"),
            valid_orders=("is_valid_sale", "sum"),
            cancelled_orders=("is_cancelled", "sum"),
            refunded_orders=("is_refunded", "sum"),
            gross_sales=("gross_sales", "sum"),
            net_sales=("net_sales", "sum"),
            avg_discount_rate=("discount_rate", "mean"),
            avg_order_value=("grand_total", "mean"),
        )
        .reset_index()
        .assign(
            valid_rate=lambda data: data["valid_orders"] / data["orders"],
            cancel_rate=lambda data: data["cancelled_orders"] / data["orders"],
            refund_rate=lambda data: data["refunded_orders"] / data["orders"],
        )
    )


def score_by_quantile(series: pd.Series, high_value_is_good: bool = True) -> pd.Series:
    """将连续指标按五分位打分，分数越高代表表现越好。"""
    labels = [1, 2, 3, 4, 5] if high_value_is_good else [5, 4, 3, 2, 1]
    ranked = series.rank(method="first")
    return pd.qcut(ranked, q=5, labels=labels).astype(int)


def summarize_rfm_segments(df: pd.DataFrame) -> pd.DataFrame:
    """基于最近购买、购买频次和消费金额进行 RFM 客户分层。"""
    valid_sales = df.loc[
        df["is_valid_sale"] & df["customer_id"].notna() & df["order_date"].notna()
    ].copy()

    snapshot_date = valid_sales["order_date"].max() + pd.Timedelta(days=1)
    rfm = (
        valid_sales.groupby("customer_id")
        .agg(
            last_order=("order_date", "max"),
            frequency=("item_id", "count"),
            monetary=("net_sales", "sum"),
        )
        .reset_index()
    )
    rfm["recency"] = (snapshot_date - rfm["last_order"]).dt.days
    rfm["r_score"] = score_by_quantile(rfm["recency"], high_value_is_good=False)
    rfm["f_score"] = score_by_quantile(rfm["frequency"], high_value_is_good=True)
    rfm["m_score"] = score_by_quantile(rfm["monetary"], high_value_is_good=True)
    rfm["rfm_score"] = rfm["r_score"] + rfm["f_score"] + rfm["m_score"]

    def segment(row: pd.Series) -> str:
        if row["r_score"] >= 4 and row["f_score"] >= 4 and row["m_score"] >= 4:
            return "高价值客户"
        if row["r_score"] >= 4 and row["f_score"] <= 2:
            return "新近客户"
        if row["r_score"] <= 2 and row["f_score"] >= 4:
            return "需唤醒高频客户"
        if row["m_score"] >= 4:
            return "高消费客户"
        if row["r_score"] <= 2:
            return "沉睡客户"
        return "普通客户"

    rfm["segment"] = rfm.apply(segment, axis=1)
    return rfm.sort_values(["rfm_score", "monetary"], ascending=[False, False])


def summarize_rfm_segment_overview(rfm: pd.DataFrame) -> pd.DataFrame:
    """汇总 RFM 分层结果，用于快速查看各类客户规模和销售贡献。"""
    return (
        rfm.groupby("segment")
        .agg(
            customers=("customer_id", "count"),
            avg_recency=("recency", "mean"),
            avg_frequency=("frequency", "mean"),
            monetary=("monetary", "sum"),
            avg_monetary=("monetary", "mean"),
        )
        .reset_index()
        .assign(
            customer_share=lambda data: data["customers"] / data["customers"].sum(),
            monetary_share=lambda data: data["monetary"] / data["monetary"].sum(),
        )
        .sort_values("monetary", ascending=False)
    )


def save_table(table: pd.DataFrame, filename: str) -> Path:
    """保存分析表格到 output/tables。"""
    path = TABLES_DIR / filename
    table.to_csv(path, index=False, encoding="utf-8-sig")
    return path


def save_bar_chart(
    data: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    filename: str,
    top_n: int | None = None,
) -> Path:
    """保存柱状图，常用于展示 Top N 类别或状态分布。"""
    plot_data = data.head(top_n) if top_n else data
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.bar(plot_data[x].astype(str), plot_data[y])
    ax.set_title(title)
    ax.set_xlabel("")
    ax.set_ylabel(Y_AXIS_LABELS.get(y, y.replace("_", " ").title()))
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    path = FIGURES_DIR / filename
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def save_horizontal_bar_chart(
    data: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    filename: str,
    top_n: int | None = None,
) -> Path:
    """保存横向柱状图，适合展示名称较长的类别。"""
    plot_data = data.head(top_n) if top_n else data
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.barh(plot_data[y].astype(str), plot_data[x])
    ax.invert_yaxis()
    ax.set_title(title)
    ax.set_xlabel(Y_AXIS_LABELS.get(x, x.replace("_", " ").title()))
    ax.set_ylabel("")
    fig.tight_layout()
    path = FIGURES_DIR / filename
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def save_line_chart(data: pd.DataFrame, x: str, y: str, title: str, filename: str) -> Path:
    """保存折线图，常用于展示按时间变化的趋势。"""
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(data[x].astype(str), data[y], marker="o", linewidth=2)
    ax.set_title(title)
    ax.set_xlabel("")
    ax.set_ylabel(Y_AXIS_LABELS.get(y, y.replace("_", " ").title()))
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    path = FIGURES_DIR / filename
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def format_number(value: float) -> str:
    """将大数字格式化成更适合报告阅读的形式。"""
    return f"{value:,.0f}"


def format_percent(value: float) -> str:
    """将比例格式化为百分比。"""
    return f"{value:.1%}"


def generate_markdown_report(tables: dict[str, pd.DataFrame]) -> Path:
    """根据汇总结果生成一份中文 Markdown 分析报告。"""
    monthly = tables["monthly_sales"]
    category = tables["category_sales"]
    payment = tables["payment_method_summary"]
    status = tables["order_status_summary"]
    rfm_overview = tables["rfm_segment_overview"]
    cancellation_category = tables["cancellation_by_category"]
    discount = tables["discount_impact"]

    total_orders = int(status["orders"].sum())
    total_net_sales = float(monthly["net_sales"].sum())
    peak_month = monthly.loc[monthly["net_sales"].idxmax()]
    top_category = category.iloc[0]
    top_payment = payment.iloc[0]
    top_segment = rfm_overview.iloc[0]
    cancelled_orders = int(cancellation_category["cancelled_orders"].sum())
    refunded_orders = int(cancellation_category["refunded_orders"].sum())
    high_risk_category = cancellation_category.loc[
        cancellation_category["orders"] >= 1000
    ].iloc[0]
    discount_highest_cancel = discount.loc[discount["cancel_rate"].idxmax()]

    report = f"""# Pakistan 电商销售分析报告

## 1. 核心结论

- 数据集中共包含 {format_number(total_orders)} 条订单记录，按当前口径计算的净销售额为 {format_number(total_net_sales)}。
- 净销售额最高的月份是 {peak_month['order_period']}，当月净销售额为 {format_number(peak_month['net_sales'])}。
- 净销售额最高的品类是 {top_category['category_name_1']}，贡献净销售额 {format_number(top_category['net_sales'])}，占整体净销售额的 {format_percent(top_category['net_sales_share'])}。
- 订单量最高的支付方式是 {top_payment['payment_method']}，订单占比为 {format_percent(top_payment['order_share'])}，取消率为 {format_percent(top_payment['cancel_rate'])}。
- 取消订单共 {format_number(cancelled_orders)} 单，退款订单共 {format_number(refunded_orders)} 单，需要结合品类和支付方式继续拆解。
- RFM 分层中销售贡献最高的客户群体是 {top_segment['segment']}，贡献金额占比为 {format_percent(top_segment['monetary_share'])}。

## 2. 销售趋势

月度销售表保存在 `output/tables/monthly_sales.csv`。建议重点观察净销售额峰值月份、订单量变化和取消率变化是否同步。

对应图表：

```text
output/figures/monthly_sales.png
```

## 3. 品类表现

品类销售表保存在 `output/tables/category_sales.csv`。{top_category['category_name_1']} 是当前最主要的收入来源，但仍需结合有效订单率和退款率判断品类质量。

对应图表：

```text
output/figures/top_categories.png
```

## 4. 取消和退款风险

按订单量不少于 1000 单的品类观察，取消率最高的品类是 {high_risk_category['category_name_1']}，取消率为 {format_percent(high_risk_category['cancel_rate'])}。

相关表格：

- `output/tables/cancellation_by_category.csv`
- `output/tables/cancellation_by_payment.csv`

对应图表：

```text
output/figures/category_cancel_rate.png
```

## 5. 折扣影响

折扣分析表保存在 `output/tables/discount_impact.csv`。当前取消率最高的折扣区间是 {discount_highest_cancel['discount_bucket']}，取消率为 {format_percent(discount_highest_cancel['cancel_rate'])}。

这个结果不能直接说明折扣导致取消，但可以作为后续继续分析促销活动、品类和订单状态的入口。

## 6. 客户价值

RFM 客户分层表保存在：

- `output/tables/rfm_segments.csv`
- `output/tables/rfm_segment_overview.csv`

RFM 分析使用三个指标：

- Recency：最近一次购买距离数据截止日期的天数，越小越好。
- Frequency：有效购买次数，越高越好。
- Monetary：有效净销售额贡献，越高越好。

对应图表：

```text
output/figures/rfm_segments.png
```

## 7. 后续分析建议

- 继续拆解高取消率品类，查看是否集中在某些月份、支付方式或价格区间。
- 对高价值客户和沉睡客户分别设计不同运营策略。
- 将 notebook 中有价值的探索结论继续沉淀到 `src/`，保持探索过程和正式脚本同步演进。
"""

    path = REPORTS_DIR / "ecommerce_analysis_report.md"
    path.write_text(report, encoding="utf-8")
    return path


def run_analysis() -> dict[str, pd.DataFrame]:
    """执行完整分析流程：读取数据、清洗数据、生成表格和图表。"""
    ensure_output_dirs()
    configure_chinese_font()
    raw = load_raw_data()
    df = clean_data(raw)

    rfm_segments = summarize_rfm_segments(df)

    # 每个表格对应一个独立分析主题，便于在报告或 notebook 中单独引用。
    tables = {
        "monthly_sales": summarize_monthly_sales(df),
        "category_sales": summarize_category_sales(df),
        "payment_method_summary": summarize_payment_methods(df),
        "order_status_summary": summarize_order_status(df),
        "customer_summary": summarize_customers(df),
        "cancellation_by_category": summarize_cancellation_by_category(df),
        "cancellation_by_payment": summarize_cancellation_by_payment(df),
        "discount_impact": summarize_discount_impact(df),
        "rfm_segments": rfm_segments,
        "rfm_segment_overview": summarize_rfm_segment_overview(rfm_segments),
    }

    for name, table in tables.items():
        save_table(table, f"{name}.csv")

    # 图表保留英文文件名，图表标题使用中文，方便浏览和展示。
    save_line_chart(
        tables["monthly_sales"],
        "order_period",
        "net_sales",
        "月度净销售额趋势",
        "monthly_sales.png",
    )
    save_bar_chart(
        tables["category_sales"],
        "category_name_1",
        "net_sales",
        "净销售额最高的前 10 个品类",
        "top_categories.png",
        top_n=10,
    )
    save_bar_chart(
        tables["order_status_summary"],
        "status",
        "orders",
        "订单状态分布",
        "order_status_distribution.png",
        top_n=10,
    )
    save_bar_chart(
        tables["payment_method_summary"],
        "payment_method",
        "orders",
        "订单量最高的前 10 种支付方式",
        "payment_methods.png",
        top_n=10,
    )
    save_horizontal_bar_chart(
        tables["cancellation_by_category"].loc[
            tables["cancellation_by_category"]["orders"] >= 1000
        ],
        "cancel_rate",
        "category_name_1",
        "订单量不少于 1000 的品类取消率",
        "category_cancel_rate.png",
        top_n=10,
    )
    save_bar_chart(
        tables["rfm_segment_overview"],
        "segment",
        "customers",
        "RFM 客户分层规模",
        "rfm_segments.png",
    )

    generate_markdown_report(tables)

    return tables


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    results = run_analysis()
    print("分析完成。")
    for name, table in results.items():
        print(f"- {name}: {len(table):,} 行")
