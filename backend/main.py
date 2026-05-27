# main.py
from uuid import uuid4
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from .logger import logger
from .db.engine import engine
from .db.models import Account, OptimizationSession, Allocation, Transfer

from .api import accounts, optimization


# Lifespan context to manage client lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    logger.info("Shutting down...")

app = FastAPI(
    title="Farming Optimization API",
    description="Optimize plant allocation and seed transfers across accounts.",
    version="1.0.0",
    lifespan=lifespan
)

# ✅ Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173",
                   "https://berry-farming-optimizer.netlify.app"],  # 👈 Allow Vite frontend
    allow_credentials=True,
    allow_methods=["*"],  # Allows: GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],  # Allows all headers
)

app.include_router(accounts.router)         # GET/POST /accounts
app.include_router(optimization.router)


@app.get("/")
def read_root():
    return {
        "message": "🌱 Farming Optimization Backend",
        "docs": "/docs"
    }   

    
