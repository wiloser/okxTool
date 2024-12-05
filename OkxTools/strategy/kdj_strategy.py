import pandas as pd
from .base_strategy import BaseStrategy

class KDJStrategy(BaseStrategy):
    """
    KDJ策略
    - K线突破D线做多
    - D线突破K线做空
    """
    def __init__(self, fastk=9, slowk=3, slowd=3):
        super().__init__()
        self.fastk = fastk
        self.slowk = slowk
        self.slowd = slowd

    def on_data(self, row):
        if row["K"] > row["D"] and row["J"] < 80:
            return 1  # K线上穿D线且J值不在超买区，买入信号
        elif row["K"] < row["D"] and row["J"] > 20:
            return -1  # K线下穿D线且J值不在超卖区，卖出信号
        return 0
