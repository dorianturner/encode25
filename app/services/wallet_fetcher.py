from web3 import Web3

class WalletQuery:
    def __init__(self, wallet_address: str, question: str):
        self.wallet_address = wallet_address
        self.question = question

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


    def fetch_web3_history(address: str, debug = False):
    # Connect to an Ethereum node (replace with your node URL)
        infura_url = "https://mainnet.infura.io/v3/d65cc6290ab748b7a979ea98b59d54f8"

        if debug:
            infura_url = "https://ethereum-sepolia-rpc.publicnode.com"

        web3 = Web3(Web3.HTTPProvider(infura_url))

        if not web3.is_connected():
            print("Failed to connect to the Ethereum network.")
            return

        if web3.is_address(address):
            # Get the latest block number
            try:
                latest_block = web3.eth.block_number
            except Exception as e:
                raise ConnectionError(f"Failed to get latest block: {str(e)}")
        
            transactions = []
        
            # Check last 100 blocks (adjust as needed)
            for block_num in range(latest_block, latest_block - 100, -1):
                try:
                    block = web3.eth.get_block(block_num, full_transactions=True)
                
                    for tx in block.transactions:
                        if tx['from'] == address or tx.get('to') == address:
                            transactions.append(tx)
            
                except Exception as e:
                    print(f"Error processing block {block_num}: {str(e)}")
                    continue

            return transactions
        else:
            print("Invalid input. Please enter a valid Ethereum address or transaction hash.")



if __name__ == "__main__":
    address = "0x3Dd5A3bbF75acaFd529E1ddB12B9463C0C0350dE"
    WalletQuery = WalletQuery(address, "What is the current balance of my wallet?")
 
    WalletQuery.fetch_web3_data(address, debug=True)

   
    print(WalletQuery.fetch_web3_history(address, debug=True))
