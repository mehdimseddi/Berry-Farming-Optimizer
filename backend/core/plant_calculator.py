# core/plant_calculator.py
import numpy as np
from abc import ABC, abstractmethod
from typing import List
from ..domain.entities import Account, PlantTarget
from ..config import MAX_PLANTS_PER_ACCOUNT
from ..logger import logger

class PlantTargetCalculator(ABC):
    @abstractmethod
    def calculate(self, accounts: List[Account], plant_targets: List[PlantTarget]) -> np.ndarray:
        pass

# core/plant_calculator.py

class RatioBasedPlantCalculator(PlantTargetCalculator):
    def calculate(self, accounts: List[Account], plant_targets: List[PlantTarget]) -> np.ndarray:
        total_seeds = np.sum([acc.seeds for acc in accounts], axis=0)
        requirements = np.array([
            [r.plain_spicy, r.very_spicy, r.very_bitter, r.plain_bitter, r.very_sweet, r.plain_sweet]
            for r in [p.requirements for p in plant_targets]
        ])
        ratios = np.array([p.ratio for p in plant_targets])

        num_accounts = len(accounts)
        max_total_plants = num_accounts * 156  # MAX_PLANTS_PER_ACCOUNT

        # Step 1: Binary search on scaling factor to find max feasible target

        # --- Compute max_possible_scale ---
        max_per_plant = []
        for req in requirements:
            with np.errstate(divide='ignore', invalid='ignore'):
                possible = np.where(req > 0, total_seeds // req, np.inf)
                max_for_plant = possible.min() if possible[possible != np.inf].size > 0 else 0
            max_per_plant.append(max_for_plant)
        max_per_plant = np.array(max_per_plant)

        scaling_factors = max_per_plant / ratios
        finite_factors = scaling_factors[(scaling_factors != np.inf) & (scaling_factors >= 0)]
        if len(finite_factors) == 0:
            return np.zeros(4, dtype=int)

        max_possible_scale = int(np.min(finite_factors)) + 1
        # Cap by total plant capacity
        max_by_capacity = max_total_plants // sum(ratios) + 1
        high = min(max_possible_scale, max_by_capacity)
        low = 0
        best = np.zeros(4, dtype=int)

        while low <= high:
            mid = (low + high) // 2
            candidate = np.floor(ratios * mid).astype(int)
            total_plants = candidate.sum()

            if total_plants > max_total_plants:
                high = mid - 1
                continue

            # Check seed feasibility: total required <= available
            required_seeds = candidate @ requirements  # Shape: [6]
            if (required_seeds <= total_seeds).all():
                best = candidate
                low = mid + 1
            else:
                high = mid - 1
        logger.info(f"available seeds: {[acc.seeds for acc in accounts]}")
        logger.info(f"Final feasible target plants: {best}")
        return best