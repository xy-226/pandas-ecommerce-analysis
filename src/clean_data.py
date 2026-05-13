from __future__ import annotations

import re

import pandas as pd


MISSING_MARKERS = ["\\N", "", "nan", "None", "NULL"]

# 不同订单状态在业务分析中的归类口径。
VALID_SALES_STATUSES = {"complete", "received", "paid", "closed"}
CANCELLED_STATUSES = {"canceled", "payment_review", "pending_paypal"}
REFUNDED_STATUSES = {"order_refunded", "refund"}


def normalize_column_name(column: str) -> str:
    """将原始字段名统一转换为 snake_case，方便后续用 pandas 处理。"""
    column = column.strip()
    column = re.sub(r"[^0-9a-zA-Z]+", "_", column)
    return column.strip("_").lower()


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """清洗并扩展原始订单数据，返回可直接用于分析的数据表。"""
    cleaned = df.copy()

    # 统一字段命名，避免原始列名里的空格、大小写和特殊符号影响分析。
    cleaned.columns = [normalize_column_name(column) for column in cleaned.columns]

    # 将常见的文本型缺失值标记统一转成 pandas 的缺失值。
    cleaned = cleaned.replace(MISSING_MARKERS, pd.NA)

    # 原始日期字段格式比较固定，显式指定格式可以减少解析歧义。
    date_formats = {
        "created_at": "%m/%d/%Y",
        "working_date": "%m/%d/%Y",
        "customer_since": "%b-%y",
    }
    for column, date_format in date_formats.items():
        if column in cleaned.columns:
            cleaned[column] = pd.to_datetime(
                cleaned[column],
                errors="coerce",
                format=date_format,
            )

    # 数值字段中可能混有逗号分隔符，先去掉逗号再转换为数值。
    numeric_columns = [
        "price",
        "qty_ordered",
        "grand_total",
        "discount_amount",
        "mv",
        "year",
        "month",
        "customer_id",
    ]
    for column in numeric_columns:
        if column in cleaned.columns:
            cleaned[column] = (
                cleaned[column]
                .astype("string")
                .str.replace(",", "", regex=False)
                .pipe(pd.to_numeric, errors="coerce")
            )

    # 文本字段统一去除首尾空格，避免同一取值被拆成多个类别。
    text_columns = [
        "status",
        "sku",
        "category_name_1",
        "sales_commission_code",
        "payment_method",
        "bi_status",
        "m_y",
        "fy",
    ]
    for column in text_columns:
        if column in cleaned.columns:
            cleaned[column] = cleaned[column].astype("string").str.strip()

    if "category_name_1" in cleaned.columns:
        cleaned["category_name_1"] = cleaned["category_name_1"].fillna("未知品类")

    if "created_at" in cleaned.columns:
        # 增加年月维度，便于按月份观察趋势。
        cleaned["order_date"] = cleaned["created_at"]
        cleaned["order_year"] = cleaned["created_at"].dt.year
        cleaned["order_month"] = cleaned["created_at"].dt.month
        cleaned["order_period"] = cleaned["created_at"].dt.to_period("M").astype("string")

    if "status" in cleaned.columns:
        # 将订单状态拆成布尔标记，后续每个分析函数都可以复用。
        status = cleaned["status"].str.lower()
        cleaned["is_valid_sale"] = status.isin(VALID_SALES_STATUSES)
        cleaned["is_cancelled"] = status.isin(CANCELLED_STATUSES)
        cleaned["is_refunded"] = status.isin(REFUNDED_STATUSES)

    if {"price", "qty_ordered"}.issubset(cleaned.columns):
        # 商品总金额口径：单价乘以购买数量。
        cleaned["gross_sales"] = cleaned["price"] * cleaned["qty_ordered"]

    if "grand_total" in cleaned.columns:
        # 净销售额只统计有效销售订单，取消和退款订单不计入收入贡献。
        cleaned["net_sales"] = cleaned["grand_total"].where(
            cleaned.get("is_valid_sale", True),
            0,
        )

    if {"discount_amount", "gross_sales"}.issubset(cleaned.columns):
        # 折扣率用于后续观察折扣力度，分母为 0 时保留为缺失值。
        cleaned["discount_rate"] = (
            cleaned["discount_amount"] / cleaned["gross_sales"].replace(0, pd.NA)
        ).clip(lower=0)

    return cleaned
