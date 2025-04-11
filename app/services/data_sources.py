import requests

def fetch_current_market_values(tokens: dict = None):
    """
    Fetch and print the current market values in USD for specified tokens.
    
    Args:
        tokens (dict): A mapping of token symbols to CoinGecko IDs. 
                       Defaults to Ethereum (ETH) and USDC.
                       e.g. {"ETH": "ethereum", "USDC": "usd-coin"}
    """
    if tokens is None:
        tokens = {
          "ETH": "ethereum", 
          "USDC": "usd-coin",
          "BTC": "bitcoin"
        }
    
    # Prepare parameters for the CoinGecko API
    url = "https://api.coingecko.com/api/v3/simple/price"
    ids = ",".join(tokens.values())
    params = {
        "ids": ids,
        "vs_currencies": "usd"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        prices = response.json()

        # Print token market values in order of importance (as defined in tokens dict)
        for symbol, cg_id in tokens.items():
            usd_price = prices.get(cg_id, {}).get("usd")
            if usd_price is not None:
                print(f"Current market value of {symbol}: ${usd_price}")
            else:
                print(f"Price data for {symbol} is unavailable.")
    except requests.RequestException as e:
        print(f"Failed to fetch market data: {e}")

if __name__ == "__main__":
    fetch_current_market_values()