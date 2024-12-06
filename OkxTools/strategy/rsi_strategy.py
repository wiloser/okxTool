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
        signals = []

        if row['RSI'] < self.oversold and not self.position:
            signals.append({
                'type': 'long',
                'price': row['Close'],
                'stop_loss': row['Close'] * 0.95,
                'take_profit': row['Close'] * 1.10
            })
            self.position = 'long'

        elif row['RSI'] > self.overbought and self.position == 'long':
            signals.append({
                'type': 'exit',
                'price': row['Close'],
                'stop_loss': row['Close'] * 0.95,
                'take_profit': row['Close'] * 1.05
            })
            self.position = None

        return signals