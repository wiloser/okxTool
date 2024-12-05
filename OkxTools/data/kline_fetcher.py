import requests
import csv
import json
import time
from tqdm import tqdm
import os
import pandas as pd

# REST API 地址
KLINE_URL = "https://www.okx.com/api/v5/market/history-candles"
INSTRUMENTS_URL = "https://www.okx.com/api/v5/public/instruments"

# 创建数据目录
if not os.path.exists('data/csv'):
    os.makedirs('data/csv')
if not os.path.exists('data/json'):
    os.makedirs('data/json')


def get_klines(inst_id, bar, limit=100, before=None, after=None, retries=5, backoff=2):
    """
    获取历史 K 线数据，增加重试机制。
    """
    params = {
        "instId": inst_id,
        "bar": bar,
        "limit": str(limit)
    }
    if before:
        params["before"] = str(before)
    if after:
        params["after"] = str(after)

    for attempt in range(retries):
        try:
            response = requests.get(KLINE_URL, params=params, timeout=10)
            response.raise_for_status()
            json_data = response.json()

            if json_data['code'] != '0':
                print(f"Error from API: {json_data['msg']}")
                return None

            return json_data["data"]
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}. Retrying {attempt + 1}/{retries}...")
            time.sleep(backoff * (attempt + 1))  # 指数退避
    print("Max retries exceeded. Could not fetch data.")
    return None


def fetch_all_instruments(inst_type="SPOT"):
    """
    获取当前交易所所有交易品种，并保存为 JSON 文件。
    """
    params = {
        "instType": inst_type
    }
    try:
        response = requests.get(INSTRUMENTS_URL, params=params, timeout=10)
        response.raise_for_status()
        json_data = response.json()

        if json_data['code'] != '0':
            print(f"Error fetching instruments: {json_data['msg']}")
            return None

        instruments = json_data.get("data", [])
        output_file = os.path.join("data/json", f"okx_{inst_type.lower()}_instruments.json")

        # 保存为 JSON 文件
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(instruments, f, ensure_ascii=False, indent=4)

        print(f"Instruments data saved to {output_file}")
        return instruments
    except requests.exceptions.RequestException as e:
        print(f"Request error while fetching instruments: {e}")
        return None


def fetch_existing_data(csv_file):
    """
    检查 CSV 文件中已有数据，并返回最新的时间戳
    """
    if not os.path.exists(csv_file):
        return None, []

    try:
        data = pd.read_csv(csv_file)
        if data.empty:
            return None, []

        # 获取最新的时间戳
        last_timestamp = data["Timestamp"].max()
        return last_timestamp, data.values.tolist()
    except Exception as e:
        print(f"Error reading existing data: {e}")
        return None, []


def fetch_past_klines(inst_id, bar, csv_file):
    """
    从当前时间向过去获取所有历史 K 线数据，并保存到 CSV 文件
    """
    # 检查现有数据
    last_existing_timestamp, existing_data = fetch_existing_data(csv_file)
    all_data = []
    total_records = 0  # 用于统计总数据条数

    # 使用 tqdm 显示进度条
    with tqdm(desc=f"Fetching ***{inst_id}-{bar}*** historical data", unit="records", leave=True) as pbar:
        start_after = None
        while True:
            # 调用 API 获取数据
            data = get_klines(inst_id, bar, limit=100, after=start_after)
            if not data:
                print("\nNo more data available or error occurred.")
                break

            # 如果请求的数据早于现有数据的时间戳，停止
            if last_existing_timestamp and int(data[-1][0]) <= last_existing_timestamp:
                print("\nRequested data is older than existing data. Stopping...")
                break

            # 将新数据添加到 all_data 列表
            all_data.extend(data)
            total_records += len(data)
            start_after = int(data[-1][0])  # 更新最后时间戳

            # 更新进度条
            pbar.update(len(data))
            pbar.set_postfix(total=total_records)

            # 如果返回的数据量不足100，说明已经获取到最早的记录
            if len(data) < 100:
                print("\nReached the earliest available data.")
                break

            # 避免频繁请求
            time.sleep(0.1)

    # 合并现有数据和新数据
    combined_data = existing_data + all_data

    # 保存数据到 CSV 文件
    with open(csv_file, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Open", "High", "Low", "Close", "Volume1", "Volume2", "Volume3", "f"])
        writer.writerows(combined_data)
    print(f"\nData saved to {csv_file}")


if __name__ == "__main__":
    # 获取所有现货交易品种并保存为 JSON 文件
    print("Fetching all instruments...")
    fetch_all_instruments(inst_type="SPOT")

    # 获取历史 K 线数据
    inst_id = "BTC-USDT-SWAP"  # 替换为您的交易对
    bar = "1D"  # 时间间隔
    csv_file = os.path.join("data/csv", f"{inst_id}_{bar}_klines_past.csv")

    print("Fetching past historical K-line data...")
    fetch_past_klines(inst_id, bar, csv_file)
