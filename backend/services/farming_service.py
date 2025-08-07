# services/farming_service.py
from typing import Any, Dict, List
from ..core.plant_calculator import PlantTargetCalculator, RatioBasedPlantCalculator
from ..core.optimizer import FarmingOptimizer
from ..domain.entities import Account, PlantTarget
from ..config import PLANT_TARGETS, PLANT_NAMES, SEED_NAMES
import numpy as np
from ortools.sat.python import cp_model

class FarmingService:
    def __init__(
        self,
        calculator: PlantTargetCalculator,
        optimizer: FarmingOptimizer
    ):
        self.calculator = calculator
        self.optimizer = optimizer

    def run(self, accounts: List[Account], grouping_penalty_weight: int = 10000) -> dict:
        try:
            target_plants, ideal_target, shortfall = self.calculator.calculate(accounts, PLANT_TARGETS)
            plant_targets_ordered = [int(x) for x in [target_plants[0], target_plants[1], target_plants[2], target_plants[3]]]

            requirements_matrix = np.array([
                [p.requirements.plain_spicy, p.requirements.very_spicy,
                 p.requirements.very_bitter, p.requirements.plain_bitter,
                 p.requirements.very_sweet, p.requirements.plain_sweet]
                for p in PLANT_TARGETS
            ])
            
            # Only show positive values (deficit); 0 if surplus
            seed_shortage = {seed_name: int(max(0, short)) 
                            for seed_name, short in zip(SEED_NAMES, shortfall)}
            
            self.optimizer.plant_requirements = requirements_matrix

            result = self.optimizer.solve(accounts,
                                           np.array(plant_targets_ordered),
                                           grouping_penalty_weight=grouping_penalty_weight)

            if result["status"] == cp_model.OPTIMAL or result["status"] == cp_model.FEASIBLE:  # FEASIBLE or OPTIMAL
                structured = self._format_solution(result["solution"], accounts)
                return {
                    "success": True,
                    "message": "Optimization completed successfully.",
                    "targets": {
                        "leppa": plant_targets_ordered[0],
                        "cheri": plant_targets_ordered[1],
                        "pecha": plant_targets_ordered[2],
                        "strawbst": plant_targets_ordered[3]
                    },
                    "ideal_targets": {
                    "leppa": int(ideal_target[0]),
                    "cheri": int(ideal_target[1]),
                    "pecha": int(ideal_target[2]),
                    "strawbst": int(ideal_target[3])
                },
                "seed_shortage": seed_shortage,
                    "allocations": structured["allocations"],
                    "transfers": structured["transfers"],
                    "status_code": 200
                }
            else:
                return {
                    "success": False,
                    "message": "No feasible solution found.",
                    "status_code": 422
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error during optimization: {str(e)}",
                "status_code": 500
            }

    def _format_solution(self, sol: dict, accounts: List[Account]) -> Dict[str, Any]:
        allocations = []
        seed_names = ['plain_spicy', 'very_spicy', 'very_bitter', 'plain_bitter', 'very_sweet', 'plain_sweet']
        plant_names = ['leppa', 'cheri', 'pecha', 'strawbst']

        for j, account in enumerate(accounts):
            plants = {}
            total = 0
            for p, name in enumerate(plant_names):
                count = sol["plant_alloc"][j][p]
                if count > 0:
                    plants[name] = count
                total += count
            final_seeds = {seed_names[s]: sol["final_seeds"][j][s] for s in range(6)}
            allocations.append({
                "account_id": str(account.id),  # ← UUID as string
                "character_name": account.character_name,
                "parent_account_name": account.parent_account_name,
                "plants": plants,
                "total_plants": total,
                "final_seeds": final_seeds
            })

        transfers = []
        for i, from_acc in enumerate(accounts):
            for j, to_acc in enumerate(accounts):
                if i == j:
                    continue
                for s in range(6):
                    val = sol["transfers"][i][j][s]
                    if val > 0:
                        transfers.append({
                            "from_account": str(from_acc.id),   # ← UUID
                            "from_character": from_acc.character_name,
                            "to_account": str(to_acc.id),       # ← UUID
                            "to_character": to_acc.character_name,
                            "seed_type": seed_names[s],
                            "amount": val
                        })

        return {
            "allocations": allocations,
            "transfers": transfers
        }