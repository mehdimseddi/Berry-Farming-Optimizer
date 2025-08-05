# backend/db/repository.py
from .models import Account, OptimizationSession, Allocation, Transfer
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
from fastapi import HTTPException
from uuid import UUID
from sqlmodel import select

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

async def add_account(session: AsyncSession, account_data: dict) -> Account:
    """
    Add a single account to the database.
    """
    try:
        db_acc = Account(
            character_name=account_data.get("character_name"),
            parent_account_name=account_data.get("parent_account_name"),
            plain_spicy=account_data["seeds"][0],
            very_spicy=account_data["seeds"][1],
            very_bitter=account_data["seeds"][2],
            plain_bitter=account_data["seeds"][3],
            very_sweet=account_data["seeds"][4],
            plain_sweet=account_data["seeds"][5]
        )
        session.add(db_acc)
        await session.commit()
        await session.refresh(db_acc)
        return db_acc
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save account: {str(e)}")
    
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
            try:
                account_id = UUID(alloc["account_id"])
            except ValueError:
                raise HTTPException(status_code=422, detail=f"Invalid UUID: {alloc['account_id']}")
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
                from_account_id=UUID(tx["from_account"]),
                to_account_id=UUID(tx["to_account"]),
                seed_type=tx["seed_type"],
                amount=tx["amount"]
            )
            session.add(transfer)

        await session.commit()
        return opt_session

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Save failed: {str(e)}")
    

# === DELETE ACCOUNTS ===
async def delete_account(session: AsyncSession, account_id: UUID) -> bool:
    """
    Delete a single account by ID.
    Returns True if deleted, False if not found.
    """
    result = await session.exec(select(Account).where(Account.id == account_id))
    account = result.one_or_none()
    if not account:
        return False

    await session.delete(account)
    await session.commit()
    return True


async def delete_all_accounts(session: AsyncSession) -> int:
    """
    Delete all accounts and return the number deleted.
    Note: Does NOT cascade to allocations/transfers unless DB has ON DELETE CASCADE.
    """
    result = await session.exec(select(Account))
    accounts = result.all()
    count = len(accounts)

    for account in accounts:
        await session.delete(account)
    
    await session.commit()
    return count

# === OPTIMIZATION SESSIONS ===
async def delete_optimization_session(session: AsyncSession, session_id: UUID) -> bool:
    """
    Delete an optimization session by ID (and its related allocations/transfers via CASCADE).
    Returns True if deleted, False if not found.
    """
    result = await session.exec(
        select(OptimizationSession).where(OptimizationSession.id == session_id)
    )
    opt_session = result.one_or_none()
    if not opt_session:
        return False

    await session.delete(opt_session)
    await session.commit()
    return True