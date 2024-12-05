import pandas as pd
from .base_strategy import BaseStrategy

class DualThrustStrategy(BaseStrategy):
    """
    Dual Thrust策略
    - 突破上轨做多
    - 突破下轨做空
    """
    def __init__(self, lookback=20, k1=0.7, k2=0.7):
        super().__init__()
        self.lookback = lookback
        self.k1 = k1
        self.k2 = k2

    def on_data(self, row):
        if row["Close"] > row["Upper_Band"]:
            return 1  # 突破上轨，买入信号
        elif row["Close"] < row["Lower_Band"]:
            return -1  # 突破下轨，卖出信号
        return 0
