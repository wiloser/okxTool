import pandas as pd

def normalize_data(data):
    """
    标准化数据。
    """
    df = pd.DataFrame(data)
    return (df - df.mean()) / df.std()
