from openai import OpenAI
import openai
import asyncio
import json
from services import wallet_fetcher
from services import data_sources
import os

# api keys
openai.api_key = os.getenv("OPENAI_API_KEY")

tokens = ["USDT", "USDC", "DAI"]

#our wallet address
#address = "0x3Dd5A3bbF75acaFd529E1ddB12B9463C0C0350dE"
address = "0x4838B106FCe9647Bdf1E7877BF73cE8B0BAD5f97"
# sample wallet summary
test_wallet = wallet_fetcher.WalletQuery(
    wallet_address=address,
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

client = OpenAI()  # Initialize once

async def fetch_concurrently(walet = test_wallet):
    """Fetch all data in parallel"""
    return await asyncio.gather(
        fetch_web3_history_async(walet),
        fetch_all_data_async()
    )

async def get_stream(wallet_query: wallet_fetcher.WalletQuery):
    # Fetch data concurrently
    wallet_summary = await wallet_query.fetch_web3_data()
    wallet_transaction_history, external_data = await fetch_concurrently(wallet_query)
    
    wallet_transaction_history = wallet_transaction_history["transactions"][-5:]

    # Truncate and summarize
    def summarize(data, max_chars=1500):
        text = json.dumps(data, indent=2)
        return text[:max_chars] + ("\n...[truncated]" if len(text) > max_chars else "")

    prompt = f"""
        You are an AI assistant helping a beginner crypto user make informed, responsible decisions about their wallet activity.

        Inputs:
        - Wallet Summary:
        {wallet_summary['ERC-20 Token Balances']}

        - Recent Transactions (last 5):
        {', '.join([f'{t["hash"]} (Block #{t["blockNumber"]})' for t in wallet_transaction_history])}

        - External Market & Risk Data:
        {summarize(external_data)}

        - User Question:
        {wallet_query.question}

        Your task:
        - Answer the user's question with sensible, beginner-friendly advice.
        - Use the provided data only to inform your response — do NOT directly quote or refer to specific hashes, block numbers, or summaries.
        - Give specific guidance that helps the user make better long-term decisions.
        - You should make reference to the users token balances and token prices if relevant to the advice given.
        - Keep your explanation clear, simple, and focused on reducing risk and improving understanding.

        Do not speculate or add information beyond what’s relevant to the question.
    """

    # Retry logic with exponential backoff

    stream = client.chat.completions.create(
        model="gpt-4o-mini",  # Use latest optimized model
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        stream= True,  # Enable streaming
        temperature=0.7,  # Adjust as needed
    )

    return stream

    # wallet_summary = await wallet_query.fetch_web3_data()
    # wallet_transaction_history, external_data = await fetch_concurrently(wallet_query)
    # wallet_transaction_history = wallet_transaction_history["transactions"][-5:]
    
    # def summarize(data, max_chars=1500):
    #     text = json.dumps(data, indent=2)
    #     return text[:max_chars] + ("\n...[truncated]" if len(text) > max_chars else "")
    
    # # Step 1: Get wallet summary
    # summarize_prompt = f"""Summarize this Ethereum wallet and its 5 most recent transactions.
    # Wallet Summary:
    # {summarize(wallet_summary)}
    # Transactions:
    # {json.dumps(wallet_transaction_history)}
    # """
    
    # print("-1")
    
    # # Call the OpenAI API for the summary
    # summary_response = await openai.Completion.acreate(
    #     model="gpt-4o-mini",
    #     prompt=summarize_prompt,
    #     max_tokens=150,
    #     temperature=0.7
    # )
    # summary = summary_response.choices[0].text.strip()
    
    # print("0")
    
    # # Step 2: Use the summary for analysis
    # analysis_prompt = f"""You are a DeFi portfolio AI assistant. Based on the following wallet summary and external data, answer the user's question with actionable insights.
    # Wallet Summary:
    # {summary}
    # External Data:
    # {summarize(external_data)}
    # Question:
    # {wallet_query.question}
    # Include:
    # - Investment strategy tips
    # - Token recommendations
    # - Risk flags
    # - Notable gas fees
    # """
    
    # print("1")
    
    # # Call the OpenAI API for the analysis
    # analysis_response = await openai.Completion.acreate(
    #     model="gpt-4o-mini",
    #     prompt=analysis_prompt,
    #     max_tokens=150,
    #     temperature=0.7
    # )
    # analysis = analysis_response.choices[0].text.strip()
    
    # print("2")
    
    # # Use OpenAI API directly for final streaming
    # response = openai.Completion.create(
    #     model="gpt-4o-mini",
    #     prompt=analysis,  # Use the analysis result as the prompt
    #     max_tokens=500,
    #     temperature=0.7,
    #     stream=True
    # )
    
    # print("3")
    # print("YOOOOOOOOO")
    
    # return response