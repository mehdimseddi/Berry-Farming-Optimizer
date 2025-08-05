# backend/db/repository.py
from .models import Account, OptimizationSession, Allocation, Transfer
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
from fastapi import HTTPException
import uuid

# === ACCOUNTS ===
async def save_accounts(session: AsyncSession, accounts_data: List[dict]) -> List[Account]:
    db_accounts = []
    for acc in accounts_data:
        db_acc = Account(
            character_name=acc.get("character_name"),
            parent_account_name=acc.get("parent_account_name"),
            plain_spicy=acc["seeds"][0],
            very_spicy=acc["seeds"][1],
            very_bitter=acc["seeds"][2],
            plain_bitter=acc["seeds"][3],
            very_sweet=acc["seeds"][4],
            plain_sweet=acc["seeds"][5]
        )
        session.add(db_acc)
        db_accounts.append(db_acc)
    await session.commit()
    return db_accounts

async def get_all_accounts(session: AsyncSession) -> List[Account]:
    result = await session.exec(select(Account))
    return result.all()

# === OPTIMIZATION RESULTS ===
async def save_optimization_result(
    session: AsyncSession,
    request: dict,
    response: dict
) -> OptimizationSession:
    try:
        opt_session = OptimizationSession(
            status="success",
            grouping_penalty_weight=request.get("grouping_penalty_weight"),
            total_leppa=response["targets"]["leppa"],
            total_cheri=response["targets"]["cheri"],
            total_pecha=response["targets"]["pecha"],
            total_strawbst=response["targets"]["strawbst"]
        )
        session.add(opt_session)
        await session.flush()  # Get ID

        # Save allocations
        for alloc in response["allocations"]:
            account_id = uuid.UUID(alloc["account_id"])  # Assume you pass UUIDs
            allocation = Allocation(
                session_id=opt_session.id,
                account_id=account_id,
                leppa=alloc["plants"].get("leppa"),
                cheri=alloc["plants"].get("cheri"),
                pecha=alloc["plants"].get("pecha"),
                strawbst=alloc["plants"].get("strawbst"),
                final_plain_spicy=alloc["final_seeds"]["plain_spicy"],
                final_very_spicy=alloc["final_seeds"]["very_spicy"],
                final_very_bitter=alloc["final_seeds"]["very_bitter"],
                final_plain_bitter=alloc["final_seeds"]["plain_bitter"],
                final_very_sweet=alloc["final_seeds"]["very_sweet"],
                final_plain_sweet=alloc["final_seeds"]["plain_sweet"]
            )
            session.add(allocation)

        # Save transfers
        for tx in response["transfers"]:
            transfer = Transfer(
                session_id=opt_session.id,
                from_account_id=uuid.UUID(tx["from_account"]),
                to_account_id=uuid.UUID(tx["to_account"]),
                seed_type=tx["seed_type"],
                amount=tx["amount"]
            )
            session.add(transfer)

        await session.commit()
        return opt_session

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Save failed: {str(e)}")