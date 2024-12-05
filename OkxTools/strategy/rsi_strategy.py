from .base_strategy import BaseStrategy


class RSIStrategy(BaseStrategy):
    """
    RSI交易策略
    包含RSI指标计算和交易信号生成
    """

    def __init__(self, period=14, overbought=70, oversold=30):
        super().__init__()
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
        """
        根据当前数据生成交易信号
        :param row: Series, 当前数据行，包含RSI值
        :return: list, 交易信号列表
        """
        signals = []

        # RSI低于超卖线且当前无持仓，生成买入信号
        if row['RSI'] < self.oversold and not self.position:
            signals.append({
                'type': 'long',
                'price': row['Close'],
                'stop_loss': row['Close'] * 0.95,  # 5%止损
                'take_profit': row['Close'] * 1.10  # 10%止盈
            })
            self.position = 'long'

        # RSI高于超买线且持有多仓，生成卖出信号
        elif row['RSI'] > self.overbought and self.position == 'long':
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