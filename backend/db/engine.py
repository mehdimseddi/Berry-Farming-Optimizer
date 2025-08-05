# backend/db/engine.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlmodel import SQLModel
import os
from dotenv import load_dotenv

load_dotenv() 

DATABASE_URL = os.getenv("SUPABASE_DB_URL")  # postgresql+asyncpg://user:pass@host/db
if not DATABASE_URL:
    raise RuntimeError("SUPABASE_DB_URL must be set")

engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=True)