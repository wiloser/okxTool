from .base_strategy import BaseStrategy


class RSIStrategy(BaseStrategy):
    """
    RSI交易策略
    包含RSI指标计算和交易信号生成
    """

    def __init__(self, period=14, overbought=70, oversold=30, debug_mode=False):
        super().__init__(debug_mode=debug_mode)
        self.period = period
        self.overbought = overbought
        self.oversold = oversold
        self.position = None

    def prepare_data(self, data):
        """
        准备策略所需的指标数据
        :param data: DataFrame, 包含 Close 价格数据
        :return: DataFrame, 增加了RSI指标的数据
        """
        df = data.copy()

        # 计算RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        return df.dropna()

    def on_data(self, row):
        signals = []
        if self.debug_mode:
            print(f"Processing row: RSI={row['RSI']}, Position={self.position}")

        if row['RSI'] < self.oversold and not self.position:
            if self.debug_mode:
                print(f"Buy Signal Generated: Price={row['Close']}")
            signals.append({
                'type': 'long',
                'price': row['Close'],
                'stop_loss': row['Close'] * 0.95,
                'take_profit': row['Close'] * 1.10
            })
            self.position = 'long'

        elif row['RSI'] > self.overbought and self.position == 'long':
            print(f"Sell Signal Generated: Price={row['Close']}")
            signals.append({
                'type': 'exit',
                'price': row['Close'],
                'stop_loss': row['Close'] * 0.95,
                'take_profit': row['Close'] * 1.05
            })
            self.position = None

        return signals

    def run_backtest(self, data, backtester):
        """
        运行回测的完整流程
        :param data: DataFrame, 原始数据
        :param backtester: Backtester实例
        :return: dict, 回测结果
        """
        # 准备数据（计算指标）
        prepared_data = self.prepare_data(data)

        # 运行回测
        results = backtester.run(prepared_data, self)

        return results
