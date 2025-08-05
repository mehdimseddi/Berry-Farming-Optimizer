# test_db.py
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("SUPABASE_DB_URL")
if not DATABASE_URL:
    raise RuntimeError("SUPABASE_DB_URL missing")

print("Using URL:", DATABASE_URL)

engine = create_async_engine(DATABASE_URL, echo=True)

async def test():
    async with engine.begin() as conn:
        result = await conn.exec_driver_sql("SELECT 1")
        print("Success:", result.scalar())

asyncio.run(test())