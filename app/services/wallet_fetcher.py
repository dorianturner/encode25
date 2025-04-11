import requests
from web3 import Web3

class WalletQuery:
    def __init__(self, wallet_address: str, question: str, debug: bool = False):
        self.wallet_address = wallet_address
        self.question = question
        
        if debug:
            self.etherscan_api = "https://api-sepolia.etherscan.io/api?"
            self.infura_url = "https://ethereum-sepolia-rpc.publicnode.com"
        else:
            self.etherscan_api = "https://api.etherscan.io/api?"
            self.infura_url = "https://mainnet.infura.io/v3/d65cc6290ab748b7a979ea98b59d54f8"

        self.web3 = Web3(Web3.HTTPProvider(self.infura_url))


    def fetch_web3_data(self):
        if not self.web3.is_connected():
            print("Failed to connect to the Ethereum network.")
            return

        if self.web3.is_address(self.wallet_address):
            # Fetch balance for an Ethereum address
            balance = self.web3.eth.get_balance(self.wallet_address)
            return {self.web3.from_wei(balance, 'ether')} 
        elif len(eth_addr) == 66:
            # Fetch transaction details for a transaction hash
            try:
                transaction = self.web3.eth.get_transaction(self.wallet_address)
                if transaction is None:
                    print("Transaction not found.")
                    return
                # Fetch transaction receipt
                return(transaction)
            except Exception as e:
                print(f"Error fetching transaction: {e}")
        else:
            print("Invalid input. Please enter a valid Ethereum address or transaction hash.")


    def fetch_web3_history(self):
        API_KEY = "44UC4DPSTC296FKCM5CRI6D6C36YVMAN6R"  # Get free key from etherscan.io

        url = f"{self.etherscan_api}module=account&action=txlist&address={self.wallet_address}&startblock=0&endblock=99999999&sort=asc&apikey={API_KEY}"
    
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            if data['status'] == '1':
                return data['result']
            else:
                print("Etherscan error:", data['message'])
                return []
        except Exception as e:
            print(f"API request failed: {e}")
            return []



if __name__ == "__main__":
    address = "0x3Dd5A3bbF75acaFd529E1ddB12B9463C0C0350dE"
    WalletQuery = WalletQuery(address, "What is the current balance of my wallet?", debug=True)
 
    print(WalletQuery.fetch_web3_data())

    print(WalletQuery.fetch_web3_history())
