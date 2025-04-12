import requests
from web3 import Web3
import json
import os
import asyncio
import aiohttp


# takes in wallet address, question? and list of tokens addresses
class WalletQuery:
    def __init__(self, wallet_address: str, question: str = "", debug: bool = False):
        self.wallet_address = wallet_address
        self.question = question

        if debug:
            self.etherscan_api = "https://api-sepolia.etherscan.io/api?"
            self.infura_url = "https://ethereum-sepolia-rpc.publicnode.com"
            self.alchemy_api = (
                f"https://eth-sepolia.g.alchemy.com/v2/{os.getenv('ALCHEMY')}"
            )
            self.covalent_api = "https://api.covalenthq.com/v1/eth-sepolia/address/"
        else:
            self.etherscan_api = "https://api.etherscan.io/api?"
            self.infura_url = (
                "https://mainnet.infura.io/v3/d65cc6290ab748b7a979ea98b59d54f8"
            )
            self.alchemy_api = (
                f"https://eth-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY')}"
            )
            self.covalent_api = "https://api.covalenthq.com/v1/eth-mainnet/address/"

        self.web3 = Web3(Web3.HTTPProvider(self.infura_url))

    async def fetch_web3_data(self):
        if not self.web3.is_connected():
            print("Failed to connect to the Ethereum network.")
            return

        if self.web3.is_address(self.wallet_address):
            # Fetch balance for an Ethereum address
            balance = self.web3.eth.get_balance(self.wallet_address)
            # convert to float to allow json serialization
            eth_balance = float(self.web3.from_wei(balance, "ether"))
            response = {"ETH Balance": eth_balance}

            payload = {
                "jsonrpc": "2.0",
                "method": "alchemy_getTokenBalances",
                "params": [self.wallet_address, "erc20"],
                "id": 1,
            }

            headers = {"Content-Type": "application/json"}

            erc20_response = requests.post(self.alchemy_api, json=payload, headers=headers).json()

            tokens = [
                token
                for token in erc20_response["result"]["tokenBalances"]
                if int(token["tokenBalance"], 16) != 0
            ]

            async with aiohttp.ClientSession() as session:
                tasks = [
                    self.get_token_metadata(session, token["contractAddress"])
                    for token in tokens
                ]

                metadata_results = await asyncio.gather(*tasks)

            coingecko_ids = ",".join(map(lambda x: x["name"].lower().replace(" ", "-"), metadata_results))
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {"ids": "ethereum," + coingecko_ids, "vs_currencies": "usd"}
            usd_prices = requests.get(url, params = params).json()
            token_balances = []

            for token, metadata in zip(tokens, metadata_results):
                token_address = token["contractAddress"]
                hex_balance = token["tokenBalance"]

                decimals = metadata.get("decimals")

                if decimals is None:
                    decimals = 18
                else:
                    decimals = int(decimals)

                balance_int = int(hex_balance, 16)
                coingecko_id = metadata["name"].lower().replace(" ", "-")
                formatted_balance = balance_int / (10**decimals)
                token_balances.append(
                    (
                        token_address,
                        formatted_balance,
                        metadata.get("name"),
                        metadata.get("symbol"),
                        metadata.get("logo"),
                        usd_prices[coingecko_id]["usd"]
                    )
                )

            if token_balances:
                response["ERC-20 Token Balances"] = sorted(
                    token_balances, key=lambda x: x[1], reverse=True
                )

            return json.dumps(response, indent=2)

        elif len(self.wallet_address) == 66:
            # Fetch transaction details for a transaction hash
            try:
                transaction = self.web3.eth.get_transaction(self.wallet_address)
                if transaction is None:
                    print("Transaction not found.")
                    return
                # Fetch transaction receipt
                return transaction
            except Exception as e:
                print(f"Error fetching transaction: {e}")
        else:
            print(
                "Invalid input. Please enter a valid Ethereum address or transaction hash."
            )

    async def get_token_metadata(self, session, token_address):
        payload = {
            "jsonrpc": "2.0",
            "method": "alchemy_getTokenMetadata",
            "params": [token_address],
            "id": 1,
        }

        headers = {"Content-Type": "application/json"}

        try:
            async with session.post(
                self.alchemy_api, json=payload, headers=headers
            ) as response:
                data = await response.json()
                return data.get("result", {})
        except:
            return {}

    def fetch_web3_history(self):
        API_KEY = os.getenv("ETHER_SCAN")

        url = f"{self.etherscan_api}module=account&action=txlist&address={self.wallet_address}&startblock=0&endblock=99999999&sort=asc&apikey={API_KEY}"

        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            if data["status"] == "1":
                return {"transactions": data["result"]}
            else:
                print("Etherscan error:", data["message"])
                return []
        except Exception as e:
            print(f"API request failed: {e}")
            return []

    def fetch_web3_value_history(self):
        API_KEY = os.getenv("COVALENT")

        url = f"{self.covalent_api}/{self.wallet_address}/portfolio_v2/"

        headers = {"Authorization": f"Bearer {API_KEY}"}

        try:
            response = requests.get(url, headers=headers).json()
            data = []

            for item in response["data"]["items"]:
                for holding in item["holdings"]:
                    date = holding["timestamp"][:10]  # Just get YYYY-MM-DD
                    value = holding["close"]["quote"]
                    data.append({"date": date, "value": value})

            return sorted(data, key=lambda x: x["date"])

        except Exception as e:
            print(f"Error: {e}")
            return []


if __name__ == "__main__":
    # address = "0x3Dd5A3bbF75acaFd529E1ddB12B9463C0C0350dE"
    address = "0x4838B106FCe9647Bdf1E7877BF73cE8B0BAD5f97"
    WalletQuery = WalletQuery(address)

    # print(WalletQuery.fetch_web3_data())

    # print(WalletQuery.fetch_web3_history())
