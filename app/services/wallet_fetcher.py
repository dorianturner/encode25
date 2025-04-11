import requests
from web3 import Web3
import json
import os

TOKEN_ADDRESSES = json.load(open(f"{os.path.dirname(__file__)}/tokens.json"))


# takes in wallet address, question? and list of tokens addresses
class WalletQuery:
    def __init__(
        self, wallet_address: str, tokens=None, question: str = "", debug: bool = False
    ):
        self.wallet_address = wallet_address
        self.question = question

        if debug:
            self.etherscan_api = "https://api-sepolia.etherscan.io/api?"
            self.infura_url = "https://ethereum-sepolia-rpc.publicnode.com"
        else:
            self.etherscan_api = "https://api.etherscan.io/api?"
            self.infura_url = (
                "https://mainnet.infura.io/v3/d65cc6290ab748b7a979ea98b59d54f8"
            )

        self.tokens = tokens if tokens else []
        self.web3 = Web3(Web3.HTTPProvider(self.infura_url))

    def fetch_web3_data(self):
        if not self.web3.is_connected():
            print("Failed to connect to the Ethereum network.")
            return

        if self.web3.is_address(self.wallet_address):
            # Fetch balance for an Ethereum address
            balance = self.web3.eth.get_balance(self.wallet_address)
            # convert to float to allow json serialization
            eth_balance = float(self.web3.from_wei(balance, "ether"))

            response = {"ETH Balance": eth_balance}

            # Fetch balances for each ERC-20 token
            token_balances = {}
            for token_name in self.tokens:
                if token_name not in TOKEN_ADDRESSES:
                    print(f"Token {token_name} is not in the predefined list.")
                    continue
                # Fetch token balance using the token address
                token_address = TOKEN_ADDRESSES[token_name]
                token_balance = self.get_erc20_balance(
                    self.web3, self.wallet_address, token_address
                )

                if token_balance:
                    print(type(token_balance))
                    token_balances[token_address] = token_balance

            if token_balances:
                response["ERC-20 Token Balances"] = token_balances

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

    def fetch_web3_history(self):
        API_KEY = os.getenv("ETHER_SCAN")

        url = f"{self.etherscan_api}module=account&action=txlist&address={self.wallet_address}&startblock=0&endblock=99999999&sort=asc&apikey={API_KEY}"

        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            if data["status"] == "1":
                return json.dumps({"transactions": data["result"]}, indent=2)
            else:
                print("Etherscan error:", data["message"])
                return []
        except Exception as e:
            print(f"API request failed: {e}")
            return []

    def get_erc20_balance(self, web3, wallet_address, token_address):
        # ERC-20 ABI snippet required for balanceOf and decimals
        erc20_abi = [
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function",
            },
            {
                "constant": True,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "type": "function",
            },
        ]

        try:
            token_address = Web3.to_checksum_address(token_address)
            wallet_address = Web3.to_checksum_address(wallet_address)
            contract = web3.eth.contract(address=token_address, abi=erc20_abi)

            balance = contract.functions.balanceOf(wallet_address).call()
            decimals = contract.functions.decimals().call()

            return float(balance) / (10**decimals)

        except Exception as e:
            print(f"[Error] Could not fetch balance for {token_address}: {e}")
            return 0.0


if __name__ == "__main__":
    # address = "0x3Dd5A3bbF75acaFd529E1ddB12B9463C0C0350dE"
    address = "0x4838B106FCe9647Bdf1E7877BF73cE8B0BAD5f97"
    WalletQuery = WalletQuery(address)

    print(WalletQuery.fetch_web3_data())

    print(WalletQuery.fetch_web3_history())
