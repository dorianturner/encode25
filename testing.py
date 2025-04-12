import requests
import json

# Address of which we want to find token balances
address = input("Enter address: ")

# Alchemy URL for making requests --> Replace with your API Key at the end
url = "https://eth-mainnet.g.alchemy.com/v2/grTRsl_qai0Z0B06jgmm-QYUNAT_mrXy"


def main():
    # Prepare the request options for token balances
    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "alchemy_getTokenBalances",
        "params": [address],
    }

    headers = {"accept": "application/json", "content-type": "application/json"}

    # Fetching the token balances
    response = requests.post(url, json=payload, headers=headers).json()

    # Getting balances from the response
    balances = response["result"]

    # Remove tokens with zero balance
    non_zero_balances = [
        token for token in balances["tokenBalances"] if token["tokenBalance"] != "0"
    ]

    print(f"Token balances of {address}: \n")

    # Counter for SNo of final output
    i = 1

    # Loop through all tokens with non-zero balance
    for token in non_zero_balances:
        # Get balance of token (hex string)
        hex_balance = token["tokenBalance"]

        # Prepare request for token metadata
        metadata_payload = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "alchemy_getTokenMetadata",
            "params": [token["contractAddress"]],
        }

        # Get token metadata
        metadata_response = requests.post(
            url, json=metadata_payload, headers=headers
        ).json()
        metadata = metadata_response["result"]

        # Convert hex balance to integer
        if hex_balance.startswith("0x"):
            balance = int(hex_balance, 16)
        else:
            balance = int(hex_balance)

        if metadata["decimals"] == None:
            decimals = 18
        else:
            decimals = metadata["decimals"]

        # Compute token balance in human-readable format
        if decimals > 0:
            balance = balance / (10**decimals)
            balance = round(balance, 2)
        else:
            balance = int(balance)

        # Print name, balance, and symbol of token
        print(f"{i}. {metadata['name']}: {balance} {metadata['symbol']}")
        i += 1


if __name__ == "__main__":
    main()
