# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import logging

from .domain.entities import Account
from .services.farming_service import FarmingService
from .core.plant_calculator import RatioBasedPlantCalculator
from .core.optimizer import FarmingOptimizer
from .schemas import AccountInput, OptimizationResponse, OptimizationRequest
from .logger import logger

# Initialize components
calculator = RatioBasedPlantCalculator()
optimizer = FarmingOptimizer(plant_requirements=None)
farming_service = FarmingService(calculator, optimizer)

app = FastAPI(
    title="Farming Optimization API",
    description="Optimize plant allocation and seed transfers across accounts.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {
        "message": "🌱 Farming Optimization Backend",
        "docs": "/docs"
    }

@app.post("/optimize", response_model=OptimizationResponse)
def optimize_farming(request: OptimizationRequest):
    logger.info(f"Received optimization request with {len(request.accounts)} accounts")

    try:
        accounts = [
            Account(
                id=i,
                seeds=acc.seeds,
                character_name=acc.character_name,
                parent_account_name=acc.parent_account_name
            )
            for i, acc in enumerate(request.accounts)
        ]

        # Pass dynamic penalty to service
        result = farming_service.run(accounts, grouping_penalty_weight=request.grouping_penalty_weight)

        return result

    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")