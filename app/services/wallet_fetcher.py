import requests
from web3 import Web3
import json
import os
from tqdm import tqdm


TOKEN_ADDRESSES = json.load(open(f"{os.path.dirname(__file__)}/tokens.json"))
tokens = TOKEN_ADDRESSES.keys()

ERC20_ABI = [
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


# takes in wallet address, question? and list of tokens addresses
class WalletQuery:
    def __init__(
        self, wallet_address: str, question: str = "", debug: bool = False
    ):
        self.wallet_address = wallet_address
        self.question = question
        self.alchemy_api = f"https://eth-sepolia.g.alchemy.com/v2/{os.getenv('ALCHEMY')}"

        if debug:
            self.etherscan_api = "https://api-sepolia.etherscan.io/api?"
            self.infura_url = "https://ethereum-sepolia-rpc.publicnode.com"

        else:
            self.etherscan_api = "https://api.etherscan.io/api?"
            self.infura_url = (
                "https://mainnet.infura.io/v3/d65cc6290ab748b7a979ea98b59d54f8"
            )

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

            payload = {
                "jsonrpc": "2.0",
                "method": "alchemy_getTokenBalances",
                "params": [self.wallet_address, "erc20"],
                "id": 1,
            }

            headers = {"Content-Type": "application/json"}

            erc20_response = requests.post(self.alchemy_api, json = payload, headers=headers).json()

            # Fetch balances for each ERC-20 token
            token_balances = {}

            for token in erc20_response["result"]["tokenBalances"]:
                hex_balance = token["tokenBalance"]
                if int(hex_balance, 16) != 0:
                    token_address = token["contractAddress"]
                    # Get token metadata to properly format balance
                    metadata = self.get_token_metadata(token_address)
                    open("metadata.json", "a+").write(str(metadata))

                    decimals = metadata.get("decimals")  # Default to 18 decimals if not found

                    if decimals is None:
                        decimals = 18
                    else:
                        decimals = int(decimals)

                    # Convert hex balance to decimal
                    balance_int = int(hex_balance, 16)
                    formatted_balance = balance_int / (10**decimals)
                    # print(formatted_balance)
                    token_balances[token_address] = (formatted_balance, metadata["name"], metadata["logo"])

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

    def get_token_metadata(self, token_address):
        payload = {
            "jsonrpc": "2.0",
            "method": "alchemy_getTokenMetadata",
            "params": [token_address],
            "id": 1,
        }

        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(self.alchemy_api, json = payload, headers=headers)
            data = response.json()
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
                return json.dumps({"transactions": data["result"]}, indent=2)
            else:
                print("Etherscan error:", data["message"])
                return []
        except Exception as e:
            print(f"API request failed: {e}")
            return []

    def get_erc20_balance(self, web3, wallet_address, token_address):
        # ERC-20 ABI snippet required for balanceOf and decimals
        try:
            token_address = Web3.to_checksum_address(token_address)
            wallet_address = Web3.to_checksum_address(wallet_address)
            contract = web3.eth.contract(address=token_address, abi=ERC20_ABI)

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

    # print(WalletQuery.fetch_web3_data())

    # print(WalletQuery.fetch_web3_history())
