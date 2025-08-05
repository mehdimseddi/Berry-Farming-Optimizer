# backend/api/accounts.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID
from fastapi import Path

from ..logger import logger
from ..schemas import AccountInput
from ..db.session import get_session
from ..db.repository import delete_account, get_all_accounts, add_account, update_account_in_db, delete_all_accounts

router = APIRouter(prefix="/accounts", tags=["Accounts"])

@router.get("/", response_model=List[AccountInput])
async def load_accounts(session: AsyncSession = Depends(get_session)):
    try:
        accounts = await get_all_accounts(session)
        return [
            AccountInput(
                id=str(a.id),
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
    

@router.post("/", response_model=AccountInput)
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


@router.put("/{account_id}", response_model=AccountInput)
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
            uuid_id = UUID(account_id)
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


@router.delete("/", status_code=200)
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
    

@router.delete("/{account_id}", status_code=204)
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
            uuid_id = UUID(account_id)
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