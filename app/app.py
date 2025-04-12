from urllib.request import Request
from services import wallet_fetcher
from flask import Flask, render_template, request, jsonify
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import StreamingResponse
from services.wallet_fetcher import WalletQuery
from services import insight_engine
from services.news import fetch_crypto_news
import json
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from a2wsgi import ASGIMiddleware
# from services.tokens import tokens

flask_app = Flask(__name__)


@flask_app.route('/')
def index():
    news_items = fetch_crypto_news()
    return render_template('index.html', news_items=news_items)


@flask_app.route('/submit_address', methods=['POST'])
async def submit_address():
    ethereum_address = request.form.get('ethereum_address')
    
    if not ethereum_address:
        return jsonify({"error": "No Ethereum address provided"}), 400
    
    # Default to these common tokens
    wallet = WalletQuery(ethereum_address)
    
    # try:
    # Fetch wallet balance data
    wallet_data = await wallet.fetch_web3_data()
    
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

# @app.route('/ask_question', methods=['POST'])
# async def ask_question():
#     if not request.is_json:
#         return jsonify({"error": "Request must be JSON"}), 400
        
#     data = request.get_json()
#     question = data.get('question', '').lower()
#     address = data.get('address', '')
    
#     if not question:
#         return jsonify({"error": "No question provided"}), 400
    
    
#     wallet = wallet_fetcher.WalletQuery(
#         wallet_address=address,
#         question=question,
#     )
    
#     #THIS WOKRS:
#     result = await insight_engine.analyze_wallet(wallet)
#     #this doesnt work
#     #result = await insight_engine.stream_output(wallet)
#     return jsonify({"response":result.get('response')})
#    # return jsonify({"response": "hello world"})

# streaming endpoint
# @app.route('/ask_question_stream',methods=['POST'])
# async def ask_question_stream(request: Request):
#     data = await request.json()
#     question = data.get('question', '').lower()
#     address = data.get('address', '')
    
#     if not question:
#         return {"error": "No question provided"}
    
#     wallet = wallet_fetcher.WalletQuery(
#         wallet_address=address,
#         tokens=data.get('tokens'),
#         question=question,
#     )
    
#     async def generate():
#         async for chunk in analyze_wallet_stream(wallet):
#             yield chunk

#     return StreamingResponse(generate(), media_type="text/event-stream")



fastapi_app = FastAPI()


@fastapi_app.post("/ask_question_stream")
async def ask_question_stream(question_data: dict):
    question = question_data.get('question', '').lower()
    address = question_data.get('address', '')
    
    if not question:
        raise HTTPException(status_code=400, detail="No question provided")
    
    wallet = wallet_fetcher.WalletQuery(
        wallet_address=address,
        question=question,
    )  
    
    async def generate():
        stream = await insight_engine.get_stream(wallet)
        
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
    
    return StreamingResponse(generate(), media_type="text/event-stream")

flask_app.wsgi_app = DispatcherMiddleware(flask_app.wsgi_app, {
    '/flask': flask_app,
    '/api': ASGIMiddleware(fastapi_app),
})

if __name__ == '__main__':
    flask_app.run()
