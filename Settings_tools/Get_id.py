import asyncio
import twitchio
import os
from dotenv import load_dotenv

load_dotenv('./configuration.env')
CLIENT_ID: str = os.getenv("CLIENT_ID")
CLIENT_SECRET: str = os.getenv("CLIENT_SECRET")
BOT_LOGIN: str = os.getenv("BOT_LOGIN")
OWNER_LOGIN: str = os.getenv("OWNER_LOGIN")

async def main() -> None:
    async with twitchio.Client(client_id=CLIENT_ID, client_secret=CLIENT_SECRET) as client:
        await client.login()
        user = await client.fetch_users(logins=[OWNER_LOGIN,BOT_LOGIN])
        for u in user:
            print(f"User: {u.name} - ID: {u.id}")

if __name__ == "__main__":
    asyncio.run(main())