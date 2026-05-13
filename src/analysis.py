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

Y_AXIS_LABELS = {
    "orders": "订单量",
    "net_sales": "净销售额",
    "gross_sales": "总销售额",
    "discount_amount": "折扣金额",
}


def ensure_output_dirs() -> None:
    """确保输出表格和图表目录存在。"""
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)


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
        .assign(cancel_rate=lambda data: data["cancelled_orders"] / data["orders"])
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


def save_table(table: pd.DataFrame, filename: str) -> Path:
    """保存分析表格到 output/tables。"""
    path = TABLES_DIR / filename
    table.to_csv(path, index=False)
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


def run_analysis() -> dict[str, pd.DataFrame]:
    """执行完整分析流程：读取数据、清洗数据、生成表格和图表。"""
    ensure_output_dirs()
    configure_chinese_font()
    raw = load_raw_data()
    df = clean_data(raw)

    # 每个表格对应一个独立分析主题，便于在报告或 notebook 中单独引用。
    tables = {
        "monthly_sales": summarize_monthly_sales(df),
        "category_sales": summarize_category_sales(df),
        "payment_method_summary": summarize_payment_methods(df),
        "order_status_summary": summarize_order_status(df),
        "customer_summary": summarize_customers(df),
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

    return tables


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    results = run_analysis()
    print("分析完成。")
    for name, table in results.items():
        print(f"- {name}: {len(table):,} 行")
