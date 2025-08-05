# schemas.py
from pydantic import BaseModel
from typing import List, Optional

class AccountInput(BaseModel):
    id: Optional[str] = None  # Can be UUID string or omitted
    seeds: List[int]  # length 6: [p_spicy, v_spicy, v_bitter, p_bitter, v_sweet, p_sweet]
    character_name: Optional[str] = None
    parent_account_name: Optional[str] = None

class PlantTargetOutput(BaseModel):
    leppa: int
    cheri: int
    pecha: int
    strawbst: int

class AccountAllocationOutput(BaseModel):
    account_id: int
    character_name: Optional[str] = None
    parent_account_name: Optional[str] = None
    plants: dict
    total_plants: int
    final_seeds: dict

class TransferOutput(BaseModel):
    from_account: int
    to_account: int
    seed_type: str
    amount: int

class OptimizationRequest(BaseModel):
    accounts: List[AccountInput]
    grouping_penalty_weight: Optional[int] = 10000

class OptimizationResponse(BaseModel):
    success: bool
    message: str
    targets: Optional[PlantTargetOutput] = None
    allocations: Optional[List[AccountAllocationOutput]] = None
    transfers: Optional[List[TransferOutput]] = None
    status_code: int