import pandas as pd
from .base_strategy import BaseStrategy

class BollingerBandsStrategy(BaseStrategy):
    """
    布林带策略
    - 价格突破上轨，超买信号
    - 价格突破下轨，超卖信号
    """
    def __init__(self, window=20, num_std=2):
        super().__init__()
        self.window = window
        self.num_std = num_std

    def on_data(self, row):
        if row["Close"] < row["BB_Lower"]:
            return 1  # 价格触及下轨，买入信号
        elif row["Close"] > row["BB_Upper"]:
            return -1  # 价格触及上轨，卖出信号
        return 0
