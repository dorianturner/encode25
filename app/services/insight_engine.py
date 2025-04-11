from openai import OpenAI
from fastapi import FastAPI,Request
import uvicorn
import openai
import os
import wallet_fetcher
import json
import data_sources

# api keys
openai.api_key = "random_key"


tokens = ["USDT", "USDC", "DAI"]

# sample wallet summary
wallet = wallet_fetcher.WalletQuery(
    wallet_address="0x4838B106FCe9647Bdf1E7877BF73cE8B0BAD5f97",
    tokens=tokens,
    question="What should I do with my wallet?",
    debug=True
)

externalData = data_sources.fetch_all_data("44UC4DPSTC296FKCM5CRI6D6C36YVMAN6R", tokens=tokens)


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