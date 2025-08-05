# backend/db/models.py
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from uuid import UUID, uuid4

class AccountBase(SQLModel):
    character_name: Optional[str] = None
    parent_account_name: Optional[str] = None
    plain_spicy: int = 0
    very_spicy: int = 0
    very_bitter: int = 0
    plain_bitter: int = 0
    very_sweet: int = 0
    plain_sweet: int = 0

class Account(AccountBase, table=True):
    __tablename__ = "accounts"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    allocations: List["Allocation"] = Relationship(back_populates="account")

class OptimizationSession(SQLModel, table=True):
    __tablename__ = "optimization_sessions"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    status: str = Field(default="success", regex="^(pending|success|failed)$")
    grouping_penalty_weight: Optional[int] = None
    total_leppa: Optional[int] = None
    total_cheri: Optional[int] = None
    total_pecha: Optional[int] = None
    total_strawbst: Optional[int] = None
    # created_at: Optional[datetime] = None
    allocations: List["Allocation"] = Relationship(
        back_populates="session",
        sa_relationship_kwargs={
            # "cascade": "delete",
            "passive_deletes": "all"
        }
    )
    transfers: List["Transfer"] = Relationship(
        back_populates="session",
        sa_relationship_kwargs={
            # "cascade": "delete",
            "passive_deletes": "all"
        }
    )

class Allocation(SQLModel, table=True):
    __tablename__ = "allocations"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    session_id: UUID = Field(foreign_key="optimization_sessions.id", ondelete="CASCADE")  # ✅ Fixed
    account_id: UUID = Field(foreign_key="accounts.id", ondelete="CASCADE")                # ✅ Fixed
    leppa: Optional[int] = None
    cheri: Optional[int] = None
    pecha: Optional[int] = None
    strawbst: Optional[int] = None
    final_plain_spicy: Optional[int] = None
    final_very_spicy: Optional[int] = None
    final_very_bitter: Optional[int] = None
    final_plain_bitter: Optional[int] = None
    final_very_sweet: Optional[int] = None
    final_plain_sweet: Optional[int] = None

    account: Account = Relationship(back_populates="allocations")
    session: OptimizationSession = Relationship(back_populates="allocations")

class Transfer(SQLModel, table=True):
    __tablename__ = "transfers"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    session_id: UUID = Field(foreign_key="optimization_sessions.id", ondelete="CASCADE")  # ✅ Fixed
    from_account_id: UUID = Field(foreign_key="accounts.id", ondelete="CASCADE")          # ✅ Fixed
    to_account_id: UUID = Field(foreign_key="accounts.id", ondelete="CASCADE")            # ✅ Fixed
    seed_type: str = Field(regex="^(plain_spicy|very_spicy|very_bitter|plain_bitter|very_sweet|plain_sweet)$")
    amount: int = Field(gt=0)
    # created_at: Optional[datetime] = None

    session: OptimizationSession = Relationship(back_populates="transfers")