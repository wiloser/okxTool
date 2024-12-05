from .base_strategy import BaseStrategy


class MACDStrategy(BaseStrategy):
    """
    MACD交易策略
    包含MACD指标计算和交易信号生成
    """

    def __init__(self, fast=12, slow=26, signal=9):
        super().__init__()
        self.fast = fast
        self.slow = slow
        self.signal = signal
        self.position = None

    def prepare_data(self, data):
        """
        准备策略所需的指标数据
        :param data: DataFrame, 包含 Close 价格数据
        :return: DataFrame, 增加了MACD指标的数据
        """
        df = data.copy()

        # 计算EMA
        exp1 = df['Close'].ewm(span=self.fast, adjust=False).mean()
        exp2 = df['Close'].ewm(span=self.slow, adjust=False).mean()

        # 计算MACD线和信号线
        df['MACD'] = exp1 - exp2
        df['MACD_Signal'] = df['MACD'].ewm(span=self.signal, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']

        return df.dropna()

    def on_data(self, row):
        """
        根据当前数据生成交易信号
        :param row: Series, 当前数据行，包含MACD相关值
        :return: list, 交易信号列表
        """
        signals = []

        # MACD金叉且在零轴上方，生成买入信号
        if (row['MACD'] > row['MACD_Signal'] and
                row['MACD'] > 0 and
                not self.position):
            signals.append({
                'type': 'long',
                'price': row['Close'],
                'stop_loss': row['Close'] * 0.95,
                'take_profit': row['Close'] * 1.08
            })
            self.position = 'long'

        # MACD死叉且在零轴下方，生成卖出信号
        elif (row['MACD'] < row['MACD_Signal'] and
              row['MACD'] < 0 and
              self.position == 'long'):
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