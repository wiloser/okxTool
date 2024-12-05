import requests

TICKER_URL = "https://www.okx.com/api/v5/market/ticker"

def fetch_ticker(inst_id, retries=5, backoff=2):
    """
    获取指定交易对的实时行情数据。
    """
    params = {"instId": inst_id}
    for attempt in range(retries):
        try:
            response = requests.get(TICKER_URL, params=params, timeout=10)
            response.raise_for_status()
            json_data = response.json()
            if json_data['code'] != '0':
                print(f"Error from API: {json_data['msg']}")
                return None
            return json_data["data"]
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}. Retrying {attempt + 1}/{retries}...")
            time.sleep(backoff * (attempt + 1))
    print("Max retries exceeded. Could not fetch ticker.")
    return None
