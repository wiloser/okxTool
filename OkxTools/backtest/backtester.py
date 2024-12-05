class Backtester:
    """
    回测框架，支持更复杂的交易信号和风险管理
    """

    def __init__(self, initial_balance=10000, risk_per_trade=0.02):
        """
        初始化回测框架。
        :param initial_balance: 初始资金
        :param risk_per_trade: 每笔交易的风险占总资金的比例
        """
        self.initial_balance = initial_balance
        self.risk_per_trade = risk_per_trade
        self.balance = initial_balance
        self.positions = []
        self.trades = []
        self.equity_curve = []

    def calculate_position_size(self, stop_loss_distance):
        """
        根据风险管理计算头寸大小
        :param stop_loss_distance: 止损距离
        :return: 头寸大小
        """
        if stop_loss_distance <= 0:
            return 0
        risk_amount = self.balance * self.risk_per_trade
        position_size = risk_amount / stop_loss_distance
        return position_size

    def open_position(self, timestamp, signal):
        """
        开仓操作
        :param timestamp: 交易时间
        :param signal: 交易信号字典，包含type, price, stop_loss, take_profit等信息
        """
        if signal['type'] != 'long':  # 目前只支持做多
            return

        stop_loss_distance = abs(signal['price'] - signal['stop_loss'])
        position_size = self.calculate_position_size(stop_loss_distance)

        if position_size > 0:
            position = {
                'entry_time': timestamp,
                'entry_price': signal['price'],
                'stop_loss': signal['stop_loss'],
                'take_profit': signal['take_profit'],
                'size': position_size,
                'type': signal['type'],
                'entry_balance': self.balance
            }
            self.positions.append(position)

            # 记录交易
            self.trades.append({
                'entry_time': timestamp,
                'entry_price': signal['price'],
                'type': 'BUY',
                'size': position_size,
                'balance': self.balance
            })

    def close_position(self, timestamp, position, current_price, reason='signal'):
        """
        平仓操作
        :param timestamp: 交易时间
        :param position: 持仓信息
        :param current_price: 当前价格
        :param reason: 平仓原因（'signal', 'stop_loss', 'take_profit'）
        """
        profit = (current_price - position['entry_price']) * position['size']
        self.balance += profit

        # 记录交易
        self.trades.append({
            'exit_time': timestamp,
            'entry_time': position['entry_time'],
            'entry_price': position['entry_price'],
            'exit_price': current_price,
            'type': 'SELL',
            'size': position['size'],
            'profit': profit,
            'balance': self.balance,
            'reason': reason
        })

        return profit

    def run(self, data, strategy):
        """
        运行回测
        :param data: DataFrame, 包含策略所需的所有数据
        :param strategy: 策略实例
        :return: dict, 回测报告
        """
        for timestamp, row in data.iterrows():
            # 更新持仓状态
            positions_to_remove = []
            for i, position in enumerate(self.positions):
                # 检查是否触及止损
                if row['Close'] <= position['stop_loss']:
                    self.close_position(timestamp, position, position['stop_loss'], 'stop_loss')
                    positions_to_remove.append(i)
                # 检查是否触及止盈
                elif row['Close'] >= position['take_profit']:
                    self.close_position(timestamp, position, position['take_profit'], 'take_profit')
                    positions_to_remove.append(i)

            # 移除已平仓的位置
            for i in sorted(positions_to_remove, reverse=True):
                self.positions.pop(i)

            # 获取策略信号
            signals = strategy.on_data(row)
            if signals:
                for signal in signals:
                    if signal['type'] == 'exit' and self.positions:
                        for position in self.positions[:]:
                            self.close_position(timestamp, position, row['Close'], 'signal')
                        self.positions = []
                    elif signal['type'] == 'long' and not self.positions:
                        self.open_position(timestamp, signal)

            # 记录权益曲线
            self.equity_curve.append({
                'timestamp': timestamp,
                'balance': self.balance
            })

        return self.generate_report()

    def generate_report(self):
        """
        生成回测报告
        :return: dict, 回测统计数据
        """
        if not self.trades:
            return {
                'initial_balance': self.initial_balance,
                'final_balance': self.balance,
                'total_return': 0,
                'total_trades': 0,
                'win_rate': 0,
                'average_profit': 0,
                'max_drawdown': 0
            }

        # 计算交易统计
        profitable_trades = [t for t in self.trades if t.get('profit', 0) > 0]
        losing_trades = [t for t in self.trades if t.get('profit', 0) <= 0]

        # 计算最大回撤
        peak = self.initial_balance
        max_drawdown = 0
        for point in self.equity_curve:
            if point['balance'] > peak:
                peak = point['balance']
            drawdown = (peak - point['balance']) / peak * 100
            max_drawdown = max(max_drawdown, drawdown)

        # 计算平均盈利和平均亏损
        avg_profit = sum(t['profit'] for t in profitable_trades) / len(profitable_trades) if profitable_trades else 0
        avg_loss = sum(t['profit'] for t in losing_trades) / len(losing_trades) if losing_trades else 0

        # 计算盈亏比
        profit_factor = abs(avg_profit / avg_loss) if avg_loss != 0 else 0

        return {
            'initial_balance': self.initial_balance,
            'final_balance': self.balance,
            'total_return': ((self.balance - self.initial_balance) / self.initial_balance) * 100,
            'total_trades': len(self.trades) // 2,  # 买入和卖出算一次交易
            'profitable_trades': len(profitable_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(profitable_trades) / len(self.trades) * 100 if self.trades else 0,
            'average_profit': avg_profit,
            'average_loss': avg_loss,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'equity_curve': self.equity_curve
        }