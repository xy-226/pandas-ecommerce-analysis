# Pakistan 电商销售数据分析

## 项目简介

本项目使用 Python、pandas 和 matplotlib 分析 `Pakistan Largest Ecommerce Dataset`。项目包含两部分：一部分是在 notebook 中记录探索性分析过程，另一部分是将成熟的读取、清洗和分析逻辑整理到 `src/` 中，形成可以重复运行的正式脚本。

通过这个项目，可以观察电商订单的销售趋势、订单状态、商品品类、支付方式、客户价值和折扣相关指标，并将结果导出为 CSV 表格和 PNG 图表。

## 数据来源

数据集：`Pakistan Largest Ecommerce Dataset`

原始数据文件位于：

```text
data/raw/Pakistan Largest Ecommerce Dataset.csv
```

## 分析目标

本项目主要回答以下问题：

- 销售额和订单量随月份如何变化？
- 哪些商品品类贡献了最高的净销售额？
- 订单状态如何分布，取消和退款订单占比如何？
- 哪些支付方式使用最多，不同支付方式的取消率如何？
- 哪些客户贡献了较高的净销售额？

## 项目结构

```text
pandas-ecommerce-analysis/
|-- data/
|   `-- raw/
|       `-- Pakistan Largest Ecommerce Dataset.csv
|-- notebooks/
|   `-- 01_eda.ipynb
|-- output/
|   |-- figures/
|   `-- tables/
|-- src/
|   |-- analysis.py
|   |-- clean_data.py
|   `-- load_data.py
|-- README.md
`-- requirements.txt
```

## 文件说明

- `notebooks/01_eda.ipynb`：用于记录探索性分析过程，保留了逐步读取、检查、清洗和分析数据的代码，适合展示分析思路。
- `src/load_data.py`：负责读取原始 CSV 数据，并统一维护数据文件路径。
- `src/clean_data.py`：负责清洗字段名、缺失值、日期、数值字段，并生成销售状态标记和派生指标。
- `src/analysis.py`：负责执行正式分析流程，包括月度销售、品类销售、支付方式、订单状态和客户汇总。
- `output/tables/`：保存正式脚本生成的分析表格。
- `output/figures/`：保存正式脚本生成的分析图表。

## Notebook 和 src 的关系

`notebooks/01_eda.ipynb` 偏向探索和记录思考过程，因此可以保留手动读取、清洗和分析代码。

`src/` 偏向正式复现和代码沉淀，用来把 notebook 中已经验证过、比较稳定的逻辑整理成函数和脚本。

简单理解：

```text
notebook = 探索过程和分析笔记
src      = 可复用、可重复运行的正式代码
output   = 正式脚本生成的结果
```

## 环境安装

建议使用项目自带虚拟环境，或自行创建新的虚拟环境后安装依赖：

```bash
pip install -r requirements.txt
```

如果使用当前项目里的 `.venv`，可以直接通过下面的命令运行分析。

## 运行正式分析脚本

```bash
.venv\Scripts\python.exe src\analysis.py
```

脚本会自动完成以下流程：

1. 读取 `data/raw/Pakistan Largest Ecommerce Dataset.csv`
2. 清洗原始字段和异常值
3. 生成多个分析汇总表
4. 生成关键图表
5. 将结果写入 `output/`

## 输出结果

表格输出：

- `output/tables/monthly_sales.csv`：按月份汇总订单量、有效订单量、取消订单量、退款订单量、销售额和客户数。
- `output/tables/category_sales.csv`：按商品品类汇总订单量、有效订单量、净销售额、总销售额、平均订单金额和客户数。
- `output/tables/payment_method_summary.csv`：按支付方式汇总订单量、有效订单量、取消订单量、净销售额、平均订单金额和取消率。
- `output/tables/order_status_summary.csv`：按订单状态汇总订单量、销售额和订单占比。
- `output/tables/customer_summary.csv`：按客户汇总订单数、有效订单数、净销售额、首次下单时间和最近下单时间。

图表输出：

- `output/figures/monthly_sales.png`：月度净销售额趋势图。
- `output/figures/top_categories.png`：净销售额最高的前 10 个品类。
- `output/figures/order_status_distribution.png`：订单状态分布。
- `output/figures/payment_methods.png`：订单量最高的前 10 种支付方式。

## 数据清洗说明

原始文件使用 `latin1` 编码。清洗阶段主要做了以下处理：

- 将原始列名统一转换为 snake_case，例如 `Customer ID` 转为 `customer_id`。
- 将 `\N`、空字符串、`NULL` 等标记统一识别为缺失值。
- 将 `created_at`、`Working Date`、`Customer Since` 转换为日期类型。
- 将 `price`、`qty_ordered`、`grand_total`、`discount_amount`、` MV ` 等字段转换为数值类型。
- 根据订单状态生成 `is_valid_sale`、`is_cancelled`、`is_refunded` 等分析标记。
- 生成 `gross_sales`、`net_sales`、`discount_rate` 等派生指标。

## 指标口径说明

- 有效销售订单：`complete`、`received`、`paid`、`closed`。
- 取消订单：`canceled`、`payment_review`、`pending_paypal`。
- 退款订单：`order_refunded`、`refund`。
- 净销售额：只有有效销售订单计入 `net_sales`，取消和退款订单的净销售额按 0 处理。
- 总销售额：使用 `price * qty_ordered` 计算，用于观察原始商品金额规模。

这些口径集中写在 `src/clean_data.py` 中，后续如果想调整业务定义，只需要修改对应的状态集合。
