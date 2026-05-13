from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "Pakistan Largest Ecommerce Dataset.csv"


def load_raw_data(path: str | Path = RAW_DATA_PATH) -> pd.DataFrame:
    """读取原始电商订单 CSV 数据。"""
    return pd.read_csv(path, encoding="latin1", low_memory=False)


if __name__ == "__main__":
    data = load_raw_data()
    print(f"已读取 {data.shape[0]:,} 行、{data.shape[1]:,} 列数据")
