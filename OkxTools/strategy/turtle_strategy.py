import pandas as pd
from .base_strategy import BaseStrategy

class TurtleStrategy(BaseStrategy):
    """
    海龟交易策略
    - 20日突破做多
    - 10日突破做空
    """
    def __init__(self, entry_window=20, exit_window=10):
        super().__init__()
        self.entry_window = entry_window
        self.exit_window = exit_window

    def on_data(self, row):
        if row["Close"] > row[f"High_{self.entry_window}"]:
            return 1  # 突破20日高点，买入信号
        elif row["Close"] < row[f"Low_{self.exit_window}"]:
            return -1  # 跌破10日低点，卖出信号
        return 0
