from OkxTools.backtest.backtester import Backtester
from OkxTools.strategy.ema_crossover import EMACrossoverStrategy
import pandas as pd

# 加载 CSV 数据
csv_file = "data/csv/BTC-USDT-SWAP_1D_klines_past.csv"  # 替换为你的实际文件路径
data = pd.read_csv(csv_file)

# 检查并重命名列，确保与回测框架兼容
data.columns = ["Timestamp", "Open", "High", "Low", "Close", "Volume1", "Volume2", "Volume3", "f"]
data = data[["Timestamp", "Open", "High", "Low", "Close"]]  # 保留必要的列

# 确保时间戳格式正确
data["Timestamp"] = pd.to_datetime(data["Timestamp"])

# 计算短期和长期 EMA
data["EMA_Short"] = data["Close"].ewm(span=10, adjust=False).mean()
data["EMA_Long"] = data["Close"].ewm(span=50, adjust=False).mean()

# 初始化策略和回测
strategy = EMACrossoverStrategy(short_window=10, long_window=50)
backtester = Backtester(strategy=strategy, data=data)

# 运行回测并生成报告
report = backtester.run()
print(report)
