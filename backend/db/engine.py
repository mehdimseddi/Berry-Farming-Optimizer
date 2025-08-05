# backend/db/engine.py
from uuid import uuid4
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel
import os
from dotenv import load_dotenv

load_dotenv() 

DATABASE_URL = os.getenv("SUPABASE_DB_URL")  # postgresql+asyncpg://user:pass@host/db
if not DATABASE_URL:
    raise RuntimeError("SUPABASE_DB_URL must be set")

# ✅ Add connect_args with asyncpg options
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    connect_args={
            "prepared_statement_name_func": lambda: f"__asyncpg_{uuid4()}__",
            "statement_cache_size": 0,
            "prepared_statement_cache_size": 0,
        },
)