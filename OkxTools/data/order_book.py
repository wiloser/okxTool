import time

import requests

ORDER_BOOK_URL = "https://www.okx.com/api/v5/market/books"

def fetch_order_book(inst_id, retries=5, backoff=2):
    """
    获取指定交易对的订单簿数据。
    """
    params = {"instId": inst_id}
    for attempt in range(retries):
        try:
            response = requests.get(ORDER_BOOK_URL, params=params, timeout=10)
            response.raise_for_status()
            json_data = response.json()
            if json_data['code'] != '0':
                print(f"Error from API: {json_data['msg']}")
                return None
            return json_data["data"]
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}. Retrying {attempt + 1}/{retries}...")
            time.sleep(backoff * (attempt + 1))
    print("Max retries exceeded. Could not fetch order book.")
    return None
