class BaseStrategy:
    """
    策略基类，所有自定义策略应继承此类。
    """

    def __init__(self):
        pass

    def on_data(self, data):
        """
        处理数据的策略逻辑。
        """
        raise NotImplementedError("on_data() must be implemented in subclasses")

    def on_order(self, order):
        """
        处理订单的策略逻辑。
        """
        pass

    def prepare_data(self, data):
        """
        准备策略所需的指标数据
        """
        pass