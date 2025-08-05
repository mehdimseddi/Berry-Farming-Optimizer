# schemas.py
from pydantic import BaseModel, field_validator
from typing import List, Optional

class AccountInput(BaseModel):
    id: Optional[str] = None  # Can be UUID string or omitted
    seeds: List[int]  # length 6: [p_spicy, v_spicy, v_bitter, p_bitter, v_sweet, p_sweet]
    character_name: Optional[str] = None
    parent_account_name: Optional[str] = None

    @field_validator('seeds')
    def check_seeds_length(cls, v):
        if len(v) != 6:
            raise ValueError('Seeds must contain exactly 6 integers.')
        if any(s < 0 for s in v):
            raise ValueError('Seed counts cannot be negative.')
        return v

class PlantTargetOutput(BaseModel):
    leppa: int
    cheri: int
    pecha: int
    strawbst: int

class AccountAllocationOutput(BaseModel):
    account_id: str
    character_name: Optional[str] = None
    parent_account_name: Optional[str] = None
    plants: dict
    total_plants: int
    final_seeds: dict

class TransferOutput(BaseModel):
    from_account: str
    to_account: str
    seed_type: str
    amount: int

class OptimizationRequest(BaseModel):
    # accounts: List[AccountInput]    # accounts is no longer needed in the request
    grouping_penalty_weight: Optional[int] = 10000

class OptimizationResponse(BaseModel):
    success: bool
    message: str
    targets: Optional[PlantTargetOutput] = None
    allocations: Optional[List[AccountAllocationOutput]] = None
    transfers: Optional[List[TransferOutput]] = None
    status_code: int