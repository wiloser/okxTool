import pandas as pd

from .base_strategy import BaseStrategy

class EMACrossoverStrategy(BaseStrategy):
    """
    简单均线交叉策略
    """
    def __init__(self, short_window=10, long_window=50):
        self.short_window = short_window
        self.long_window = long_window

    def on_data(self, row):
        """
        接收数据并生成交易信号：
        1 -> 买入信号
        -1 -> 卖出信号
        0 -> 无操作
        """
        if row["EMA_Short"] > row["EMA_Long"]:
            return 1  # 买入信号
        elif row["EMA_Short"] < row["EMA_Long"]:
            return -1  # 卖出信号
        else:
            return 0
