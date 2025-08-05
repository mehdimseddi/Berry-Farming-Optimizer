# core/plant_calculator.py
import numpy as np
from abc import ABC, abstractmethod
from typing import List
from ..domain.entities import Account, PlantTarget
from ..config import PLANT_TARGETS
from ..logger import logger

class PlantTargetCalculator(ABC):
    @abstractmethod
    def calculate(self, accounts: List[Account], plant_targets: List[PlantTarget]) -> np.ndarray:
        pass

class RatioBasedPlantCalculator(PlantTargetCalculator):
    def calculate(self, accounts: List[Account], plant_targets: List[PlantTarget]) -> np.ndarray:
        total_seeds = np.sum([acc.seeds for acc in accounts], axis=0)
        requirements = np.array([[p.requirements for p in plant_targets]])
        requirements = np.array([[r.plain_spicy, r.very_spicy, r.very_bitter, r.plain_bitter, r.very_sweet, r.plain_sweet]
                                 for r in [p.requirements for p in plant_targets]])

        ratios = np.array([p.ratio for p in plant_targets])

        max_possible = []
        for req in requirements:
            with np.errstate(divide='ignore', invalid='ignore'):
                possible = total_seeds / req
                possible[req == 0] = np.inf
                max_plants = int(np.min(possible))
            max_possible.append(max_plants)

        max_possible = np.array(max_possible)
        scaling_factors = max_possible / ratios
        scaling = scaling_factors.min()
        target_plants = np.floor(ratios * scaling).astype(int)
        logger.info(f"Calculated target plants: {target_plants}")

        return target_plants