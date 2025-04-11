from eth_account import Account
from web3 import Web3

# acct = Account.create("PIJFAWPIOFJhofaeiofhwfiohWAOIFIO")
# print(acct.address)
# print(acct._private_key)

# acct = Account.from_key(b"B\x0b\xa0\xfb\xea\xe0\x8b\x83\xf2\xd4\x96-F\x94'%\xba%\xf44\xe6\x1c.\xef\t\xd5L}\\\xbd\xe7\x93")
# print("Address:", acct.address)

first_acct = Account.from_key(b"B\x0b\xa0\xfb\xea\xe0\x8b\x83\xf2\xd4\x96-F\x94'%\xba%\xf44\xe6\x1c.\xef\t\xd5L}\\\xbd\xe7\x93")
second_acct = Account.from_key(b'\xf6S\xb4\x16\x9c\xa5\xf8"\xd9>\'\xbfDYfi\xc0\xa19\xd52;\xa9|_\xb8\x8d)\x06\x02m0')

print(second_acct.address)

infura_url = "https://ethereum-sepolia-rpc.publicnode.com"
web3 = Web3(Web3.HTTPProvider(infura_url))

nonce = web3.eth.get_transaction_count(first_acct.address)
gas_price = web3.eth.gas_price
gas_limit = 21000 # Standard gas limit for simple ETH transfer

transaction = {
    "to": second_acct.address,
    "value": web3.to_wei(0.01, "ether"),
    "gas": gas_limit,
    "gasPrice": gas_price,
    "nonce": nonce,
    "chainId": 11155111 # Sepolia testnet chain ID
}

signed_transaction = web3.eth.account.sign_transaction(transaction, first_acct._private_key)
tx_hash = web3.eth.send_raw_transaction(signed_transaction.raw_transaction)
print(f"Transaction sent with hash: {web3.to_hex(tx_hash)}")
