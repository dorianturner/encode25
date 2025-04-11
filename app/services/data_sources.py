import requests
import json


# Fetch all coins from CoinGecko API
def fetch_all_coins():
    url = "https://api.coingecko.com/api/v3/coins/list"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching coins list: {response.status_code}")
        return []

# Create a mapping of token symbols to CoinGecko IDs
def create_token_mapping(tokens):
    all_coins = fetch_all_coins()
    
    # Create a dictionary for mapping symbols to CoinGecko IDs
    token_mapping = {}
    
    # Loop through the list of tokens and find the corresponding CoinGecko ID
    for token in tokens:
        for coin in all_coins:
            if coin["symbol"].upper() == token.upper():  # Case insensitive match
                token_mapping[token] = coin["id"]
                break
    
    return token_mapping


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

def fetch_all_data(etherscan_api_key, tokens=None):
    if tokens is None:
        tokens = {"ETH": "ethereum", "USDC": "usd-coin"}
    else:
        tokens = create_token_mapping(tokens)
    # Fetch market values
    market_values = []
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": ",".join(tokens.values()), "vs_currencies": "usd"}
        response = requests.get(url, params=params)
        response.raise_for_status()
        prices = response.json()
        market_values = [
            {"symbol": symbol, "price_usd": prices[cg_id]["usd"]}
            for symbol, cg_id in tokens.items()
            if prices.get(cg_id, {}).get("usd") is not None
        ]
    except requests.RequestException as e:
        market_values = f"Market data error: {str(e)}"

    # Fetch gas oracle data
    gas_data = {}
    try:
        url = f"https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey={etherscan_api_key}"
        response = requests.get(url)
        data = response.json()
        if data.get("status") == "1":
            gas_data = data["result"]
        else:
            gas_data = f"Gas oracle error: {data.get('message', 'Unknown error')}"
    except requests.RequestException as e:
        gas_data = f"Gas data error: {str(e)}"

    # Estimate transaction time
    estimated_time = "N/A"
    if isinstance(gas_data, dict) and "ProposeGasPrice" in gas_data:
        try:
            proposed_gas = gas_data["ProposeGasPrice"]
            if proposed_gas.isdigit():  # Handle both string and numeric responses
                gas_price_wei = int(proposed_gas) * 10**9
                url = f"https://api.etherscan.io/api?module=gastracker&action=gasestimate&gasprice={gas_price_wei}&apikey={etherscan_api_key}"
                response = requests.get(url)
                data = response.json()
                if data.get("status") == "1":
                    estimated_time = data.get("result", "Unavailable")
        except (ValueError, AttributeError, requests.RequestException) as e:
            estimated_time = f"Estimation error: {str(e)}"

    return json.dumps({
        "market_values": market_values,
        "gas_oracle": gas_data,
        "estimated_confirmation_time": estimated_time
    }, indent=2)

# if __name__ == "__main__":
#     etherscan_api_key = "44UC4DPSTC296FKCM5CRI6D6C36YVMAN6R"

#     market_values = fetch_current_market_values()
#     print("Market Values:")
#     if isinstance(market_values, list):
#         for symbol, price in market_values:
#             print(f"{symbol}: ${price:.2f}")
#     else:
#         print(market_values)

#     gas_data = fetch_gas_oracle(etherscan_api_key)
#     print("\nGas Oracle Data:")
#     if isinstance(gas_data, dict):
#         for key, value in gas_data.items():
#             unit = " Gwei" if key != "gas_used_ratio" else ""
#             print(f"{key.capitalize()}: {value}{unit}")
#     else:
#         print(gas_data)

#     if isinstance(gas_data, dict):
#         proposed_gas_wei = int(gas_data["proposed"] * 1e9)
#         estimated_time = estimate_transaction_time(etherscan_api_key, proposed_gas_wei)
#         print(f"\nEstimated confirmation time for {gas_data['proposed']} Gwei: {estimated_time} seconds")
#     else:
#         print("\nGas oracle data unavailable; cannot estimate transaction time.")


#     all_data = fetch_all_data(etherscan_api_key)
#     print(f"\nAll Data: {all_data}")
