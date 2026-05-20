# Pakistan 电商销售分析报告

## 1. 核心结论

- 数据集中共包含 584,524 条订单记录，按当前口径计算的净销售额为 1,619,746,781。
- 净销售额最高的月份是 2017-11，当月净销售额为 354,231,305。
- 净销售额最高的品类是 Mobiles & Tablets，贡献净销售额 612,454,081，占整体净销售额的 37.8%。
- 订单量最高的支付方式是 cod，订单占比为 46.5%，取消率为 8.0%。
- 取消订单共 201,313 单，退款订单共 67,579 单，需要结合品类和支付方式继续拆解。
- RFM 分层中销售贡献最高的客户群体是 高价值客户，贡献金额占比为 57.4%。

## 2. 销售趋势

月度销售表保存在 `output/tables/monthly_sales.csv`。建议重点观察净销售额峰值月份、订单量变化和取消率变化是否同步。

对应图表：

```text
output/figures/monthly_sales.png
```

## 3. 品类表现

品类销售表保存在 `output/tables/category_sales.csv`。Mobiles & Tablets 是当前最主要的收入来源，但仍需结合有效订单率和退款率判断品类质量。

对应图表：

```text
output/figures/top_categories.png
```

## 4. 取消和退款风险

按订单量不少于 1000 单的品类观察，取消率最高的品类是 Others，取消率为 62.9%。

相关表格：

- `output/tables/cancellation_by_category.csv`
- `output/tables/cancellation_by_payment.csv`

对应图表：

```text
output/figures/category_cancel_rate.png
```

## 5. 折扣影响

折扣分析表保存在 `output/tables/discount_impact.csv`。当前取消率最高的折扣区间是 0-5%，取消率为 68.4%。

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
