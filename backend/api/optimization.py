# backend/api/optimization.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID
from fastapi import Path

from ..logger import logger
from ..schemas import OptimizationRequest
from ..db.session import get_session
from ..db.repository import delete_optimization_session, get_all_accounts as get_accounts_from_db, save_optimization_result
from ..domain.entities import Account
from ..schemas import OptimizationResponse  # You may want a dedicated response schema

from ..services.farming_service import FarmingService
from ..core.plant_calculator import RatioBasedPlantCalculator
from ..core.optimizer import FarmingOptimizer

router = APIRouter(prefix="/optimize", tags=["Optimization"])

# Initialize components
calculator = RatioBasedPlantCalculator()
optimizer = FarmingOptimizer(plant_requirements=None)
farming_service = FarmingService(calculator, optimizer)

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