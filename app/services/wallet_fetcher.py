import requests
from web3 import Web3
import json

# List of common ERC-20 tokens and their contract addresses
TOKEN_ADDRESSES = {
    "USDT": "0xdac17f958d2ee523a2206206994597c13d831ec7",
    "USDC": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
    "BUSD": "0x4fabb145d64652a948d72533023f6e7a623c7c53",
    "SHIB": "0x95ad61b0a150d79219dcf64e1e6cc01f0b64c4ce",
    "DAI": "0x6b175474e89094c44da98b954eedeac495271d0f",
    "MATIC": "0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0",
    "STETH": "0xae7ab96520de3a18e5e111b5eaab095312d7fe84",
    "UNI": "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984",
    "WBTC": "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599",
    "OKB": "0x75231f58b43240c9718dd58b4967c5114342a86c",
    "LEO": "0x2af5d2ad76741191d15dfe7bf6ac92d4bd912ca3",
    "LINK": "0x514910771af9ca656af840dff83e8264ecf986ca",
    "CRO": "0xa0b73e1ff0b80914ab6fe0444e65848c4c34450b",
    "QNT": "0x4a220e6096b25eadb88358cb44068a3248254675",
    "APE": "0x4d224452801aced8b2f0aebe155379bb5d594381",
    "XCN": "0xa2cd3d43c775978a96bdbf12d733d5a1ed94fb18",
    "FRAX": "0x853d955acef822db058eb8505911ed77f175b99e",
    "SAND": "0x3845badade8e6dff049820680d1f14bd3903a5d0",
    "MANA": "0x0f5d2fb29fb7d3cfee444a200298f468908cc942",
    "AXS": "0xbb0e17ef65f82ab018d8edd776e8dd940327b28b",
    "CHZ": "0x3506424f91fd33084466f402d5d97f05f8e3b4af",
    "AAVE": "0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9",
}


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
