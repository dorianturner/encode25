import asyncio
from flask import Flask, render_template, request, jsonify, Response
from services import insight_engine
from services import wallet_fetcher
from services.wallet_fetcher import WalletQuery, TOKEN_ADDRESSES
import json
# from services.tokens import tokens

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_address', methods=['POST'])
def submit_address():
    ethereum_address = request.form.get('ethereum_address')
    
    if not ethereum_address:
        return jsonify({"error": "No Ethereum address provided"}), 400
    
    # Default to these common tokens
    tokens = ["ETH", "USDT", "BNB", "USDC", "STETH", "WBTC", "LEO", "LINK", "TON", "SHIB", "USDS", "WSTETH", "OM", "BGB", "USDE", "WETH", "WBT", "WEETH", "OKB", "UNI", "DAI", "CBBTC", "PEPE", "ONDO", "GT", "NEAR", "TKX", "SUSDS", "BUIDL", "CRO", "MNT", "SUSDE", "AAVE", "RENDER", "ENA", "FDUSD", "LBTC", "FTN", "POL", "ARB", "SOLVBTC", "FET", "MKR", "NEXO", "BONK", "QNT", "WLD", "RSETH", "DEXE", "PYUSD", "MOVE", "INJ", "XAUT", "CRV", "GRT", "RETH", "IMX", "XSOLVBTC", "PAXG", "USD0", "XCN", "LDO", "JASMY", "SAND", "GALA", "USDX", "METH", "BTT", "CAKE", "FLOKI", "PENDLE", "TUSD", "PUMPBTC", "ENS", "MANA", "SPX", "TEL", "USDY", "RSR", "CLBTC", "NFT", "USYC", "OUSG", "STRK", "USR", "AXS", "TBTC", "CMETH", "CHZ", "OHM", "COMP", "VIRTUAL", "APE", "W", "BEAM", "OSETH", "PLUME", "MATIC", "FRAX", "USDD"]
    
    # Create WalletQuery instance
    wallet = WalletQuery(ethereum_address, tokens=tokens)
    
    # try:
    # Fetch wallet balance data
    wallet_data = wallet.fetch_web3_data()
    
    # Parse the JSON string back to a dictionary
    if wallet_data:
        wallet_data = json.loads(wallet_data)
    else:
        wallet_data = {"error": "No data found"}
        
    # Fetch transaction history (limit to recent transactions)
    # Combine data
    response_data = {
        "wallet": wallet_data,
    }
    
    return jsonify(response_data)
    
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

@app.route('/ask_question', methods=['POST'])
async def ask_question():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
        
    data = request.get_json()
    question = data.get('question', '').lower()
    address = data.get('address', '')
    
    if not question:
        return jsonify({"error": "No question provided"}), 400
    
    
    wallet = wallet_fetcher.WalletQuery(
        wallet_address=address,
        tokens=data.get('tokens'),
        question=question,
        debug=True
    )
    
    #THIS WOKRS:
    result = await insight_engine.analyze_wallet(wallet)
    #this doesnt work
    #result = await insight_engine.stream_output(wallet)
    return jsonify({"response":result.get('response')})
   # return jsonify({"response": "hello world"})

if __name__ == '__main__':
    app.run(debug=True)