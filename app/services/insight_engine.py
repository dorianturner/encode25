from openai import OpenAI
from fastapi import FastAPI,Request
import openai
import wallet_fetcher
import json
import data_sources
from dotenv import load_dotenv
import os
import time

load_dotenv()

# api keys
openai.api_key = os.getenv("OPENAI_API_KEY")


tokens = ["USDT", "USDC", "DAI"]

#our wallet address
#address = "0x3Dd5A3bbF75acaFd529E1ddB12B9463C0C0350dE"
address = "0x4838B106FCe9647Bdf1E7877BF73cE8B0BAD5f97"
# sample wallet summary
wallet = wallet_fetcher.WalletQuery(
    wallet_address=address,
    tokens=tokens,
    question="What should I do with my wallet?",
    debug=True
)

externalData = data_sources.fetch_all_data(os.getenv("ETHER_KEY"), tokens=tokens)




def analyze_wallet(wallet_query : wallet_fetcher.WalletQuery):
    # 1. Fetch data with truncation
    wallet_summary = wallet_query.fetch_web3_data() or {}
    wallet_transaction_history = wallet_query.fetch_web3_history() or []
    external_data = externalData or {}  # Define your external data source
    
    # 2. Summarize/truncate
    def summarize(data, max_chars=1500):
        text = json.dumps(data, indent=2)
        return text[:max_chars] + ("\n...[truncated]" if len(text) > max_chars else "")
    
    prompt = f"""
    **Wallet Summary**:
    {summarize(wallet_summary)}
    
    **Recent Transactions** (last 5):
    {summarize(wallet_transaction_history[-50:])}
    
    **External Data**:
    {summarize(external_data)}
    
    **Question**: {wallet_query.question}
    """
    
    # 3. Add retry logic
    retries = 3
    delay = 5
    
    for attempt in range(retries):
        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",  # More efficient than gpt-4o
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            return {"response": response.choices[0].message.content.strip()}
            
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {str(e)}")
            time.sleep(delay)
            delay *= 2
    
    return {"error": "Request failed after retries"}

if __name__ == "__main__":
    print("Starting the FastAPI server...")
    print(analyze_wallet(wallet)["response"])