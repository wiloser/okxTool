import pandas as pd
import numpy as np

class Backtester:
    """
    简单的回测框架
    """
    def __init__(self, strategy, data, initial_balance=10000, risk_per_trade=0.02):
        """
        初始化回测框架。
        :param strategy: 策略实例，需实现 `on_data()` 方法。
        :param data: 历史数据，Pandas DataFrame 格式。
        :param initial_balance: 初始资金。
        :param risk_per_trade: 每笔交易的风险占总资金的比例。
        """
        self.strategy = strategy
        self.data = data
        self.initial_balance = initial_balance
        self.risk_per_trade = risk_per_trade
        self.balance = initial_balance
        self.positions = []
        self.trades = []

    def calculate_position_size(self, stop_loss_distance):
        """
        根据风险管理计算头寸大小。
        """
        if stop_loss_distance <= 0:
            return 0
        risk_amount = self.balance * self.risk_per_trade
        position_size = risk_amount / stop_loss_distance
        return position_size

    def run(self):
        """
        运行回测。
        """
        for i, row in self.data.iterrows():
            signal = self.strategy.on_data(row)
            if signal == 1:  # 买入信号
                self.open_position(row["Close"], stop_loss=row["Close"] * 0.98, take_profit=row["Close"] * 1.02)
            elif signal == -1:  # 卖出信号
                self.close_positions(row["Close"])
            self.update_balance(row["Close"])
        return self.generate_report()

    def open_position(self, entry_price, stop_loss, take_profit):
        """
        开仓操作。
        """
        position_size = self.calculate_position_size(entry_price - stop_loss)
        if position_size > 0:
            position = {
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "size": position_size,
                "entry_balance": self.balance,
            }
            self.positions.append(position)
            self.trades.append({"type": "BUY", "price": entry_price, "size": position_size})

    def close_positions(self, close_price):
        """
        平仓操作。
        """
        for position in self.positions:
            self.trades.append({"type": "SELL", "price": close_price, "size": position["size"]})
            self.balance += position["size"] * (close_price - position["entry_price"])
        self.positions = []

    def update_balance(self, current_price):
        """
        更新账户余额，根据止损或止盈清算头寸。
        """
        for position in self.positions:
            if current_price <= position["stop_loss"] or current_price >= position["take_profit"]:
                self.close_positions(current_price)

    def generate_report(self):
        """
        生成回测报告。
        """
        total_trades = len(self.trades)
        profit_trades = sum([1 for t in self.trades if t["type"] == "SELL" and t["price"] > t["size"]])
        loss_trades = total_trades - profit_trades
        profit = self.balance - self.initial_balance

        report = {
            "Initial Balance": self.initial_balance,
            "Final Balance": self.balance,
            "Total Trades": total_trades,
            "Profit Trades": profit_trades,
            "Loss Trades": loss_trades,
            "Net Profit": profit,
        }
        return report
