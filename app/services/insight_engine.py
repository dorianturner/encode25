from openai import OpenAI, AsyncOpenAI
from fastapi import FastAPI,Request
import openai
import asyncio
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

async def fetch_web3_data_async():
    # If wallet.fetch_web3_data() is synchronous, you can run it in an executor.
    return await asyncio.to_thread(wallet.fetch_web3_data)

async def fetch_web3_history_async():
    # Similarly for other synchronous functions
    return await asyncio.to_thread(wallet.fetch_web3_history)

async def fetch_all_data_async():
    # Run the synchronous fetch_all_data function in an executor
    return await asyncio.to_thread(data_sources.fetch_all_data, os.getenv("ETHER_KEY"), tokens=tokens)


# externalData = data_sources.fetch_all_data(os.getenv("ETHER_KEY"), tokens=tokens)

client = AsyncOpenAI()  # Initialize once

async def fetch_concurrently():
    """Fetch all data in parallel"""
    return await asyncio.gather(
        fetch_web3_data_async(),
        fetch_web3_history_async(),
        fetch_all_data_async()
    )

async def analyze_wallet(wallet_query: wallet_fetcher.WalletQuery, callback=None):
    # Fetch data concurrently
    wallet_summary, wallet_transaction_history, external_data = await fetch_concurrently()
    
    # Truncate and summarize
    def summarize(data, max_chars=1500):
        text = json.dumps(data, indent=2)
        return text[:max_chars] + ("\n...[truncated]" if len(text) > max_chars else "")

    print(summarize(wallet_transaction_history[-50:]))
    prompt = f"""
    **Wallet Summary**:
    {summarize(wallet_summary)}
    
    **Recent Transactions** (last 5):
    {', '.join([f'{t["hash"]} ({t["block_number"]})' for t in wallet_transaction_history[-50:]])}
    
    **External Data**:
    {summarize(external_data)}
    

    **Question**: {wallet_query.question}
    Take into account the following:
    - the given external data
    - the recent transactions
    - the wallet summary
    - the tokens in the wallet (recommend what other tokens it should invest in)
    TAKE into account past transactions and the current market trends.
    - Provide a detailed analysis of the wallet's performance and suggest improvements.
    Do not output the ETH balance or the market values, 
    but mention gas fees and the transaction history. 
    """
    
    # Retry logic with exponential backoff
    retries = 3
    delay = 5

    try:
            stream = await client.chat.completions.create(
                model="gpt-4o-mini",  # Use latest optimized model
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                stream= True,  # Enable streaming
                temperature=0.7,  # Adjust as needed
            )
            
            result = ""
            async for chunk in stream:
                content = chunk.choices[0].delta.content or ""
                if callback:
                    await callback(content)
                result += content
            
            return {"response": result.strip()}


    except Exception as e:
            print(f"Attempt failed: {str(e)}")
            await asyncio.sleep(delay)
            delay *= 2
    
    return {"error": "Request failed after retries"}

async def stream_output():
    queue = asyncio.Queue()
    
    async def callback(chunk):
        print(chunk, end="", flush=True)
        await queue.put(chunk)
    
    async def monitor():
        while True:
            if queue.empty() and asyncio.current_task().cancelled():
                break
            await asyncio.sleep(0.1)

    analysis_task = asyncio.create_task(analyze_wallet(wallet, callback=callback))
    monitor_task = asyncio.create_task(monitor())

    await asyncio.gather(analysis_task, monitor_task)
    return await analysis_task

if __name__ == "__main__":
    async def main():
        result = await stream_output()
        print("\n\nFinal Result:")
        print(result["response"])
    asyncio.run(main())
    
    
# print("Starting the FastAPI server...")
# result = asyncio.run(analyze_wallet(wallet))
# print(result["response"])


# def analyze_wallet(wallet_query : wallet_fetcher.WalletQuery):
#     # 1. Fetch data with truncation
#     wallet_summary = wallet_query.fetch_web3_data() or {}
#     wallet_transaction_history = wallet_query.fetch_web3_history() or []
#     external_data = externalData or {}  # Define your external data source
    
#     # 2. Summarize/truncate
#     def summarize(data, max_chars=1500):
#         text = json.dumps(data, indent=2)
#         return text[:max_chars] + ("\n...[truncated]" if len(text) > max_chars else "")
    
#     prompt = f"""
#     **Wallet Summary**:
#     {summarize(wallet_summary)}
    
#     **Recent Transactions** (last 5):
#     {summarize(wallet_transaction_history[-50:])}
    
#     **External Data**:
#     {summarize(external_data)}
    
#     **Question**: {wallet_query.question}
#     """
    
#     # 3. Add retry logic
#     retries = 3
#     delay = 5
    
#     for attempt in range(retries):
#         try:
#             response = openai.chat.completions.create(
#                 model="gpt-4o-mini",  # More efficient than gpt-4o
#                 messages=[{"role": "user", "content": prompt}],
#                 max_tokens=500
#             )
#             return {"response": response.choices[0].message.content.strip()}
            
#         except Exception as e:
#             print(f"Attempt {attempt+1} failed: {str(e)}")
#             time.sleep(delay)
#             delay *= 2
    
#     return {"error": "Request failed after retries"}
