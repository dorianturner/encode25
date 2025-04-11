from openai import OpenAI
from fastapi import FastAPI,Request
import uvicorn
import openai
import os
import wallet_fetcher
import json

# api keys
openai.api_key = "secret-key"

#app = FastAPI()

# sample wallet summary
wallet = wallet_fetcher.WalletQuery(
    wallet_address="0x3Dd5A3bbF75acaFd529E1ddB12B9463C0C0350dE",
    tokens=["USDT", "USDC", "DAI"],
    question="What is the current balance of my wallet?",
    debug=True
)



# will have wallet class as a parameter
#@app.post("/analyze")
def analyze_wallet(wallet_query: wallet_fetcher.WalletQuery):
    #wallet_data = fetch_web3_data(wallet_query.wallet_address)
    #wallet_json = json.dumps(wallet_data, indent=2)

    wallet_summary = wallet.fetch_web3_data()
    wallet_text = json.dumps(wallet_summary, indent=2)


    prompt = f"""
    You are a helpful DeFi assistant.
    The following is the wallet data:
    {wallet_text}

    User question: {wallet.question}
    Provide a clear, concise, and actionable answer.
    """

    response = openai.chat.completions.create(  # ✅ Correct endpoint
    model="gpt-4",
    messages=[{
        "role": "user",
        "content": prompt
    }],
    max_tokens=150
)


    return {"response": response.choices[0].message.content.strip()}   


if __name__ == "__main__":
    # uvicorn.run(app,host="0.0.0.0", port=8000, log_level="info")
    print("Starting the FastAPI server...")
    print(analyze_wallet(wallet)["response"])