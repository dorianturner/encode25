from flask import Flask, render_template, request, jsonify
from services.wallet_fetcher import WalletQuery, TOKEN_ADDRESSES
import json

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
    tokens = ["USDC", "DAI", "USDT", "WETH"]
    
    # Create WalletQuery instance
    wallet = WalletQuery(ethereum_address, tokens=tokens)
    
    try:
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
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ask_question', methods=['POST'])
def ask_question():
    question = request.form.get('question')
    address = request.form.get('address')
    
    if not question:
        return jsonify({"error": "No question provided"}), 400
    
    # This is a simple implementation. In a real app, you would use
    # an LLM or AI model to analyze the wallet data and answer the question
    responses = {
        "risk": {
            "badge": "badge-warning",
            "badge_text": "Moderate Risk",
            "text": "Your risk level on protocol X is moderate. Consider reallocating some assets to lower-risk options.",
            "buttons": [
                {"type": "primary", "text": "Show recommendations"},
                {"type": "default", "text": "Learn more"}
            ]
        },
        "yield": {
            "badge": "badge-success",
            "badge_text": "Yield Analysis",
            "text": "Based on your portfolio, you could earn an additional 3.2% APY by moving some USDC to Protocol Y's stablecoin pool.",
            "buttons": [
                {"type": "primary", "text": "View details"},
                {"type": "default", "text": "Compare platforms"}
            ]
        },
        "default": {
            "text": "I can help you analyze your DeFi portfolio and provide insights. Please ask about your assets, risks, yields, or investment opportunities.",
            "buttons": [
                {"type": "default", "text": "View suggestions"}
            ]
        }
    }
    
    response_key = "default"
    if "risk" in question.lower():
        response_key = "risk"
    elif any(term in question.lower() for term in ["apy", "yield", "interest", "earn"]):
        response_key = "yield"
    
    return jsonify(responses[response_key])

if __name__ == '__main__':
    app.run(debug=True)