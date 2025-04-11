import requests
import json

def fetch_current_market_values(tokens=None):
    if tokens is None:
        tokens = {"ETH": "ethereum", "USDC": "usd-coin"}
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": ",".join(tokens.values()), "vs_currencies": "usd"}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        prices = response.json()
        price_list = [(symbol, prices.get(cg_id, {}).get("usd")) 
                      for symbol, cg_id in tokens.items() 
                      if prices.get(cg_id, {}).get("usd") is not None]
        return json.dumps(sorted(price_list, key=lambda x: x[1]), indent=2)
    except requests.RequestException as e:
        return f"Failed to fetch market data: {e}"

def fetch_gas_oracle(api_key):
    url = f"https://api.etherscan.io/v2/api?chainid=1&module=gastracker&action=gasoracle&apikey={api_key}"
    try:
        data = requests.get(url).json()
        if data.get("status") == "1":
            result = data["result"]
            return json.dumps(result, indent=2)
        return f"Error: {data.get('message')}"
    except requests.RequestException as e:
        return f"Failed to fetch gas prices: {e}"


def estimate_transaction_time(api_key, gas_price_wei):
    url = f"https://api.etherscan.io/v2/api?chainid=1&module=gastracker&action=gasestimate&gasprice={gas_price_wei}&apikey={api_key}"
    try:
        data = requests.get(url).json()
        if data.get("status") == "1":
            return data.get("result", "Unavailable")
        return f"Error: {data.get('message')}"
    except requests.RequestException as e:
        return f"Failed to fetch gas estimate: {e}"


if __name__ == "__main__":
    etherscan_api_key = "44UC4DPSTC296FKCM5CRI6D6C36YVMAN6R"

    market_values = fetch_current_market_values()
    print("Market Values:")
    if isinstance(market_values, list):
        for symbol, price in market_values:
            print(f"{symbol}: ${price:.2f}")
    else:
        print(market_values)

    gas_data = fetch_gas_oracle(etherscan_api_key)
    print("\nGas Oracle Data:")
    if isinstance(gas_data, dict):
        for key, value in gas_data.items():
            unit = " Gwei" if key != "gas_used_ratio" else ""
            print(f"{key.capitalize()}: {value}{unit}")
    else:
        print(gas_data)

    if isinstance(gas_data, dict):
        proposed_gas_wei = int(gas_data["proposed"] * 1e9)
        estimated_time = estimate_transaction_time(etherscan_api_key, proposed_gas_wei)
        print(f"\nEstimated confirmation time for {gas_data['proposed']} Gwei: {estimated_time} seconds")
    else:
        print("\nGas oracle data unavailable; cannot estimate transaction time.")
