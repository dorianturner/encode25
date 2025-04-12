from openai import OpenAI, AsyncOpenAI
from fastapi import FastAPI,Request
import openai
import asyncio
import json
from services import wallet_fetcher
from services import data_sources
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
test_wallet = wallet_fetcher.WalletQuery(
    wallet_address=address,
    tokens=tokens,
    question="What should I do with my wallet?",
    debug=True
)

async def fetch_web3_data_async(wallet):
    return await asyncio.to_thread(wallet.fetch_web3_data)

async def fetch_web3_history_async(wallet):
    return await asyncio.to_thread(wallet.fetch_web3_history)

async def fetch_all_data_async():
    return await asyncio.to_thread(data_sources.fetch_all_data, os.getenv("ETHER_KEY"), tokens=tokens)


# externalData = data_sources.fetch_all_data(os.getenv("ETHER_KEY"), tokens=tokens)

client = AsyncOpenAI()  # Initialize once

async def fetch_concurrently(walet = test_wallet):
    """Fetch all data in parallel"""
    return await asyncio.gather(
        fetch_web3_data_async(walet),
        fetch_web3_history_async(walet),
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

async def stream_output(wallet: wallet_fetcher.WalletQuery = test_wallet):
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



# if __name__ == "__main__":
#     async def main():
#         result = await stream_output()
#         print("\n\nFinal Result:")
#         print(result["response"])
#     asyncio.run(main())
    
    

