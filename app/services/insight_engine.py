from openai import OpenAI
from fastapi import FastAPI,Request
import uvicorn
import openai
import os
import wallet_fetcher
import json
import data_sources
from dotenv import load_dotenv
import os

load_dotenv()

# api keys
openai.api_key = os.getenv("OPENAI_API_KEY")


tokens = ["USDT", "USDC", "DAI"]

# sample wallet summary
wallet = wallet_fetcher.WalletQuery(
    wallet_address="0x3Dd5A3bbF75acaFd529E1ddB12B9463C0C0350dE",
    tokens=tokens,
    question="What should I do with my wallet?",
    debug=True
)

externalData = data_sources.fetch_all_data(os.getenv("ETHER_KEY"), tokens=tokens)


#@app.post("/analyze")
def analyze_wallet(wallet_query: wallet_fetcher.WalletQuery):


    wallet_summary = wallet.fetch_web3_data()
    wallet_transaction_history = wallet.fetch_web3_history()
    wallet_text = json.dumps(wallet_summary, indent=2)


    prompt = f"""
    You are a helpful DeFi assistant.
    The following is the wallet data:
    {wallet_text}

    The following is transaction history:
    {wallet_transaction_history}

    The following is the external data:
    {externalData}

    User question: {wallet.question}
    Provide a clear, concise, and actionable answer.
    """

    response = openai.chat.completions.create(  
    model="gpt-4",
    messages=[{
        "role": "user",
        "content": prompt
    }],
    max_tokens=150
)


    return {"response": response.choices[0].message.content.strip()}   


if __name__ == "__main__":
    print("Starting the FastAPI server...")
    print(analyze_wallet(wallet)["response"])