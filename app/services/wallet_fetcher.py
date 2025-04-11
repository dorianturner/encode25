from web3 import Web3

def fetch_web3_data():
    # Connect to an Ethereum node (replace with your node URL)
    infura_url = "https://mainnet.infura.io/v3/d65cc6290ab748b7a979ea98b59d54f8"
    web3 = Web3(Web3.HTTPProvider(infura_url))

    if not web3.is_connected():
        print("Failed to connect to the Ethereum network.")
        return

    # Get user input
    user_input = input("Enter Ethereum address or transaction hash: ").strip()

    if web3.is_address(user_input):
        # Fetch balance for an Ethereum address
        balance = web3.eth.get_balance(user_input)
        print(f"Balance of {user_input}: {web3.fromWei(balance, 'ether')} ETH")
    elif web3.isHex(user_input) and len(user_input) == 66:
        # Fetch transaction details for a transaction hash
        try:
            transaction = web3.eth.get_transaction(user_input)
            print(f"Transaction details for {user_input}:")
            print(transaction)
        except Exception as e:
            print(f"Error fetching transaction: {e}")
    else:
        print("Invalid input. Please enter a valid Ethereum address or transaction hash.")

def fetch_wallet_data(wallet_address):
    # Connect to an Ethereum node (replace with your node URL)
    infura_url = "https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID"
    web3 = Web3(Web3.HTTPProvider(infura_url))

    if not web3.isConnected():
        print("Failed to connect to the Ethereum network.")
        return

    # Fetch balance for the wallet address
    balance = web3.eth.get_balance(wallet_address)
    return web3.fromWei(balance, 'ether')

if __name__ == "__main__":
    fetch_web3_data()