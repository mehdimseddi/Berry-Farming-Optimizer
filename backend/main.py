# main.py
from uuid import uuid4
import uuid
from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List

from .domain.entities import Account
from .services.farming_service import FarmingService
from .core.plant_calculator import RatioBasedPlantCalculator
from .core.optimizer import FarmingOptimizer
from .schemas import AccountInput, OptimizationResponse, OptimizationRequest
from .logger import logger

from .db.session import get_session
from .db.repository import add_account, get_all_accounts, save_optimization_result, delete_account, delete_all_accounts, delete_optimization_session, update_account_in_db
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import Path



# Initialize components
calculator = RatioBasedPlantCalculator()
optimizer = FarmingOptimizer(plant_requirements=None)
farming_service = FarmingService(calculator, optimizer)

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

@app.get("/")
def read_root():
    return {
        "message": "🌱 Farming Optimization Backend",
        "docs": "/docs"
    }

@app.post("/optimize", response_model=OptimizationResponse)
async def optimize_farming(
    request: OptimizationRequest,
    session: AsyncSession = Depends(get_session)
):
    logger.info("Received optimization request using all database accounts")

    try:
        # ✅ Load all accounts from the database
        db_accounts = await get_all_accounts(session)
        if not db_accounts:
            raise HTTPException(status_code=400, detail="No accounts found in database. Please add accounts first.")

        # Convert ORM models to domain entities (with UUIDs)
        accounts = [
            Account(
                id=acc.id,
                seeds=[
                    acc.plain_spicy, acc.very_spicy, acc.very_bitter,
                    acc.plain_bitter, acc.very_sweet, acc.plain_sweet
                ],
                character_name=acc.character_name,
                parent_account_name=acc.parent_account_name
            )
            for acc in db_accounts
        ]

        # Run optimization
        result = farming_service.run(
            accounts,
            grouping_penalty_weight=request.grouping_penalty_weight
        )

        # ✅ Save result to database
        try:
            # Convert to dict safely
            request_dict = request.model_dump()
            await save_optimization_result(session, request_dict, result)
            logger.info(f"Optimization saved for {len(accounts)} accounts")
        except Exception as e:
            logger.warning(f"Failed to save optimization result: {e}")

        return result

    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error during optimization: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    

@app.get("/accounts", response_model=List[AccountInput])
async def load_accounts(session: AsyncSession = Depends(get_session)):
    try:
        accounts = await get_all_accounts(session)
        return [
            AccountInput(
                character_name=a.character_name,
                parent_account_name=a.parent_account_name,
                seeds=[
                    a.plain_spicy, a.very_spicy, a.very_bitter,
                    a.plain_bitter, a.very_sweet, a.plain_sweet
                ]
            )
            for a in accounts
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load accounts: {str(e)}")
    
@app.post("/accounts", response_model=AccountInput)
async def create_account(
    account_input: AccountInput,
    session: AsyncSession = Depends(get_session)
):
    """
    Add a new farm account to the database.
    """
    try:
        # Convert Pydantic model to dict for repository
        account_data = account_input.model_dump()
        db_account = await add_account(session, account_data)

        logger.info("Account result saved to database.")
        return AccountInput(
            id=str(db_account.id),
            character_name=db_account.character_name,
            parent_account_name=db_account.parent_account_name,
            seeds=[
                db_account.plain_spicy, db_account.very_spicy, db_account.very_bitter,
                db_account.plain_bitter, db_account.very_sweet, db_account.plain_sweet
            ]
        )
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    

@app.delete("/accounts/{account_id}", status_code=204)
async def delete_account_route(
    account_id: str = Path(..., description="The UUID of the account to delete"),
    session: AsyncSession = Depends(get_session)
):
    """
    Delete an account by ID.
    """
    try:
        # Validate UUID format
        try:
            uuid_id = uuid.UUID(account_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid UUID format")

        deleted = await delete_account(session, uuid_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Account not found")
        
        return  # 204 No Content
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting account {account_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# backend/main.py

@app.put("/accounts/{account_id}", response_model=AccountInput)
async def update_account(
    account_id: str,
    account_input: AccountInput,
    session: AsyncSession = Depends(get_session)
):
    """
    Update an existing account by ID.
    """
    try:
        # Validate UUID format
        try:
            uuid_id = uuid.UUID(account_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid UUID format")

        updated_account = await update_account_in_db(session, uuid_id, account_input.model_dump())
        if not updated_account:
            raise HTTPException(status_code=404, detail="Account not found")

        logger.info(f"Account {account_id} updated successfully.")

        return AccountInput(
            id=str(updated_account.id),
            character_name=updated_account.character_name,
            parent_account_name=updated_account.parent_account_name,
            seeds=[
                updated_account.plain_spicy,
                updated_account.very_spicy,
                updated_account.very_bitter,
                updated_account.plain_bitter,
                updated_account.very_sweet,
                updated_account.plain_sweet
            ]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating account {account_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@app.delete("/accounts", status_code=200)
async def delete_all_accounts_route(session: AsyncSession = Depends(get_session)):
    """
    Delete all accounts. Returns count of deleted accounts.
    """
    try:
        count = await delete_all_accounts(session)
        return {"deleted_count": count, "message": f"Successfully deleted {count} account(s)"}
    except Exception as e:
        logger.error(f"Error deleting all accounts: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@app.delete("/optimization-sessions/{session_id}", status_code=204)
async def delete_optimization_session_route(
    session_id: str = Path(..., description="The UUID of the optimization session to delete"),
    session: AsyncSession = Depends(get_session)
):
    """
    Delete an optimization session and all related allocations and transfers.
    """
    try:
        # Validate UUID format
        try:
            uuid_id = uuid.UUID(session_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid UUID format")

        deleted = await delete_optimization_session(session, uuid_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Optimization session not found")
        
        return  # 204 No Content
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting optimization session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")