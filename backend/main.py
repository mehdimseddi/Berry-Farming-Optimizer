# main.py
from uuid import uuid4
from fastapi import FastAPI
from contextlib import asynccontextmanager

from .logger import logger

from .api import accounts, optimization


# Lifespan context to manage client lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    # You can run migrations here later
    yield
    logger.info("Shutting down...")

app = FastAPI(
    title="Farming Optimization API",
    description="Optimize plant allocation and seed transfers across accounts.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(accounts.router)         # GET/POST /accounts
app.include_router(optimization.router)


@app.get("/")
def read_root():
    return {
        "message": "🌱 Farming Optimization Backend",
        "docs": "/docs"
    }   

    
