from flask import Flask, request, jsonify
from walletFetcher import WalletQuery

app = Flask(__name__)

def get_wallet_data(address: str, debug: bool = False):
    wallet_query = WalletQuery(address, debug)
    balance_data = wallet_query.fetch_web3_data()
    history_data = wallet_query.fetch_web3_history()
    return {
        "address": address,
        "balance": balance_data,
        "history": history_data
    }

@app.route('/api/wallet', methods=['GET'])
def wallet_endpoint():
    address = request.args.get('address')
    debug_mode = request.args.get('debug', 'false').lower() == 'true'
    if not address:
        return jsonify({"error": "No address provided."}), 400
    data = get_wallet_data(address, debug_mode)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
