from openai import OpenAI
from fastapi import FastAPI,Request
import openai
import os
import wallet_fetcher


# api keys
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

class WalletQuery(BaseModel):
    wallet_address: str
    question: dict



@app.post("/analyze")
async def analyze_wallet(wallet_query: WalletQuery):
    wallet_data = fetch_web3_data(wallet_query.wallet_address)
    wallet_json = json.dumps(wallet_data, indent=2)

    prompt = f"""
    You are a helpful DeFi assistant.
    The following is the wallet data:
    {wallet_json}

    User question: {query.question}
    Provide a clear, concise, and actionable answer.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return {"response": response.choices[0].message["content"]}   
