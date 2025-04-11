from openai import OpenAI
from fastapi import FastAPI,Request
import openai
import os
import wallet_fetcher
import json

# api keys
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# sample wallet summary
wallet_summary = {
    "ETH Balance": "1.234 ETH",
    "Tokens": {
        "DAI": "56.7 DAI",
        "USDC": "100.25 USDC",
        "LINK": "12.55 LINK"
    },
    "Protocol Positions": {
        "Aave": {
            "Supplied": "50 DAI",
            "Borrowed": "10 USDC",
            "Health Factor": 2.3
        }
    }
}


# will have wallet class as a parameter
@app.post("/analyze")
async def analyze_wallet(wallet_query = ""):
    #wallet_data = fetch_web3_data(wallet_query.wallet_address)
    #wallet_json = json.dumps(wallet_data, indent=2)
    wallet_text = json.dumps(wallet_summary, indent=2)
    query = "What is the current balance of my wallet?"

    prompt = f"""
    You are a helpful DeFi assistant.
    The following is the wallet data:
    {wallet_text}

    User question: {query.question}
    Provide a clear, concise, and actionable answer.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return {"response": response.choices[0].message["content"]}   


if __name__ == "__main__":
    print("Starting the FastAPI server...")
    print(analyze_wallet())