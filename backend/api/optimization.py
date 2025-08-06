# backend/api/optimization.py
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID
from fastapi import Path

from ..logger import logger
from ..schemas import OptimizationRequest
from ..db.models import OptimizationSession, Allocation, Transfer
from ..db.session import get_session
from ..db.repository import delete_optimization_session, get_all_accounts as get_accounts_from_db, save_optimization_result
from ..domain.entities import Account
from sqlmodel import select, desc
from ..schemas import OptimizationResponse, PlantTargetOutput, AccountAllocationOutput, TransferOutput

from ..services.farming_service import FarmingService
from ..core.plant_calculator import RatioBasedPlantCalculator
from ..core.optimizer import FarmingOptimizer
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/optimize", tags=["Optimization"])

# Initialize components
calculator = RatioBasedPlantCalculator()
optimizer = FarmingOptimizer(plant_requirements=None)
farming_service = FarmingService(calculator, optimizer)


async def get_latest_optimization_session(session: AsyncSession) -> Optional[OptimizationSession]:
    result = await session.exec(
        select(OptimizationSession)
        .order_by(desc(OptimizationSession.created_at))
        .limit(1)
        .options(
            selectinload(OptimizationSession.allocations).joinedload(Allocation.account),
            selectinload(OptimizationSession.transfers).joinedload(Transfer.from_account),
            selectinload(OptimizationSession.transfers).joinedload(Transfer.to_account)
        )
    )
    return result.first()

# backend/api/optimization.py

@router.get("/latest", response_model=OptimizationResponse)
async def get_latest_optimization(
    session: AsyncSession = Depends(get_session)
):
    try:
        # Get the latest session with all related data
        opt_session = await get_latest_optimization_session(session)
        logger.info(f"Latest optimization session: {opt_session if opt_session else 'None'}")
        
        if not opt_session:
            return {
                "success": False,
                "message": "No optimization sessions found",
                "status_code": 404
            }

        # Debug logging
        logger.info(f"Number of allocations: {len(opt_session.allocations)}")
        logger.info(f"Number of transfers: {len(opt_session.transfers)}")
        
        # Format allocations
        allocations = []
        for alloc in opt_session.allocations:
            account = alloc.account
            allocations.append({
                "account_id": str(account.id),
                "character_name": account.character_name,
                "parent_account_name": account.parent_account_name,
                "plants": {
                    "leppa": alloc.leppa or 0,
                    "cheri": alloc.cheri or 0,
                    "pecha": alloc.pecha or 0,
                    "strawbst": alloc.strawbst or 0
                },
                "total_plants": (alloc.leppa or 0) + (alloc.cheri or 0) + 
                               (alloc.pecha or 0) + (alloc.strawbst or 0),
                "final_seeds": {
                    "plain_spicy": alloc.final_plain_spicy or 0,
                    "very_spicy": alloc.final_very_spicy or 0,
                    "very_bitter": alloc.final_very_bitter or 0,
                    "plain_bitter": alloc.final_plain_bitter or 0,
                    "very_sweet": alloc.final_very_sweet or 0,
                    "plain_sweet": alloc.final_plain_sweet or 0
                }
            })

        # Format transfers
        transfers = []
        for tx in opt_session.transfers:
            transfers.append({
                "from_account": str(tx.from_account_id),
                "from_character": tx.from_account.character_name if tx.from_account else None,
                "to_account": str(tx.to_account_id),
                "to_character": tx.to_account.character_name if tx.to_account else None,
                "seed_type": tx.seed_type,
                "amount": tx.amount
            })

        return {
            "success": True,
            "message": "Latest optimization results retrieved",
            "session_id": str(opt_session.id),
            "targets": {
                "leppa": opt_session.total_leppa or 0,
                "cheri": opt_session.total_cheri or 0,
                "pecha": opt_session.total_pecha or 0,
                "strawbst": opt_session.total_strawbst or 0
            },
            "allocations": allocations,
            "transfers": transfers,
            "status_code": 200
        }

    except Exception as e:
        logger.error(f"Error getting latest optimization: {e}")
        return {
            "success": False,
            "message": "Internal server error",
            "status_code": 500
        }
    
@router.post("/", response_model=OptimizationResponse)
async def optimize_farming(
    request: OptimizationRequest,
    session: AsyncSession = Depends(get_session)
):
    logger.info("Received optimization request using all database accounts")

    try:
        # ✅ Load all accounts from the database
        db_accounts = await get_accounts_from_db(session)
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
    

@router.delete("/{session_id}", status_code=204)
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
            uuid_id = UUID(session_id)
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