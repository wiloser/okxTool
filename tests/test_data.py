from OkxTools import fetch_past_klines

if __name__ == "__main__":
    import os

    inst_id = "BTC-USDT-SWAP"
    bar = "1D"
    csv_file = os.path.join("data/csv", f"{inst_id}_{bar}_klines_past.csv")

    fetch_past_klines(inst_id, bar, csv_file)
