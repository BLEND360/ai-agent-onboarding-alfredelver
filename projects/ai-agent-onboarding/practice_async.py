import asyncio
import aiohttp

async def fetch_example():
    url = "https://api.github.com/repos/python/cpython"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            print(f"Fetched: {data['name']}")
            return data
    
# Running it
asyncio.run(fetch_example())

