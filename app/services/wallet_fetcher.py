from web3 import Web3

def fetch_web3_data(eth_addr: str, debug = False):
    # Connect to an Ethereum node (replace with your node URL)
    infura_url = "https://mainnet.infura.io/v3/d65cc6290ab748b7a979ea98b59d54f8"
    
    if debug:
        infura_url = "https://ethereum-sepolia-rpc.publicnode.com"

    web3 = Web3(Web3.HTTPProvider(infura_url))

    if not web3.is_connected():
        print("Failed to connect to the Ethereum network.")
        return

    if web3.is_address(eth_addr):
        # Fetch balance for an Ethereum address
        balance = web3.eth.get_balance(eth_addr)
        print(f"Balance of {eth_addr}: {web3.from_wei(balance, 'ether')} ETH")
    elif len(eth_addr) == 66:
        # Fetch transaction details for a transaction hash
        try:
            transaction = web3.eth.get_transaction(eth_addr)
            print(f"Transaction details for {eth_addr}:")
            print(transaction)
        except Exception as e:
            print(f"Error fetching transaction: {e}")
    else:
        print("Invalid input. Please enter a valid Ethereum address or transaction hash.")


if __name__ == "__main__":
    fetch_web3_data("0x3Dd5A3bbF75acaFd529E1ddB12B9463C0C0350dE")
    fetch_web3_data("0x3Dd5A3bbF75acaFd529E1ddB12B9463C0C0350dE", debug=True)
