# domain/entities.py
from dataclasses import dataclass
from typing import List, Optional

@dataclass(frozen=True)
class SeedRequirements:
    """Seed requirements per plant type."""
    plain_spicy: int
    very_spicy: int
    very_bitter: int
    plain_bitter: int
    very_sweet: int
    plain_sweet: int

    @classmethod
    def from_array(cls, arr):
        return cls(*arr)

@dataclass(frozen=True)
class PlantTarget:
    name: str
    ratio: float
    requirements: SeedRequirements

@dataclass
class Account:
    id: int
    seeds: List[int]  # [p_s, v_s, v_b, p_b, v_sw, p_sw]
    character_name: Optional[str] = None
    parent_account_name: Optional[str] = None

    def __post_init__(self):
        if len(self.seeds) != 6:
            raise ValueError("Seeds must be a list of 6 integers.")
        if any(s < 0 for s in self.seeds):
            raise ValueError("Seed counts cannot be negative.")