# core/optimizer.py
from ortools.sat.python import cp_model
from typing import List, Dict, Any
from ..domain.entities import Account
import numpy as np
from ..logger import logger

class FarmingOptimizer:
    def __init__(self, plant_requirements: np.ndarray):
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        self.plant_requirements = plant_requirements  # 4x6 matrix

    def solve(self, accounts: List[Account], plant_targets: np.ndarray, grouping_penalty_weight: int = 10000) -> Dict[str, Any]:
        num_accounts = len(accounts)
        num_seed_types = 6
        num_plants = 4
        max_total_seeds = sum(sum(acc.seeds) for acc in accounts)

        # Variables
        transfer = [[[self.model.NewIntVar(0, max_total_seeds, f"t_{i}_{j}_{s}")
                      for s in range(num_seed_types)]
                     for j in range(num_accounts)]
                    for i in range(num_accounts)]

        final_seeds = [[self.model.NewIntVar(0, 1000, f"final_{j}_{s}")
                        for s in range(num_seed_types)]
                       for j in range(num_accounts)]

        plant_alloc = [[self.model.NewIntVar(0, plant_targets[p], f"alloc_{j}_{p}")
                        for p in range(num_plants)]
                       for j in range(num_accounts)]

        plant_used = [[self.model.NewBoolVar(f"used_{j}_{p}")
                       for p in range(num_plants)]
                      for j in range(num_accounts)]

        # Constraints

        # 1. Conservation: final = initial + in - out
        for j in range(num_accounts):
            for s in range(num_seed_types):
                incoming = sum(transfer[i][j][s] for i in range(num_accounts) if i != j)
                outgoing = sum(transfer[j][i][s] for i in range(num_accounts) if i != j)
                self.model.Add(
                    final_seeds[j][s] == accounts[j].seeds[s] + incoming - outgoing
                )

        # 2. Usage <= availability
        for j in range(num_accounts):
            for s in range(num_seed_types):
                used = sum(
                    plant_alloc[j][p] * self.plant_requirements[p][s]
                    for p in range(num_plants)
                )
                self.model.Add(used <= final_seeds[j][s])

        # 3. Meet global targets
        for p in range(num_plants):
            total = sum(plant_alloc[j][p] for j in range(num_accounts))
            self.model.Add(total == plant_targets[p])

        # 4. Max plants per account
        for j in range(num_accounts):
            self.model.Add(
                sum(plant_alloc[j][p] for p in range(num_plants)) <= 156
            )

        # 5. Plant used indicator
        for j in range(num_accounts):
            for p in range(num_plants):
                self.model.Add(plant_alloc[j][p] > 0).OnlyEnforceIf(plant_used[j][p])
                self.model.Add(plant_alloc[j][p] == 0).OnlyEnforceIf(plant_used[j][p].Not())

        # Objective
        total_transfer = sum(
            transfer[i][j][s]
            for i in range(num_accounts)
            for j in range(num_accounts) if i != j
            for s in range(num_seed_types)
        )

        grouping_penalty = sum(
            plant_used[j][p] for j in range(num_accounts) for p in range(num_plants)
        )

        self.model.Minimize(total_transfer + grouping_penalty_weight * grouping_penalty)

        # Solve
        status = self.solver.Solve(self.model)

        result = {"status": status, "solution": None}
        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            solution = {
                "plant_alloc": [[self.solver.Value(plant_alloc[j][p]) for p in range(num_plants)] for j in range(num_accounts)],
                "final_seeds": [[self.solver.Value(final_seeds[j][s]) for s in range(num_seed_types)] for j in range(num_accounts)],
                "transfers": [[[self.solver.Value(transfer[i][j][s]) for s in range(num_seed_types)]
                               for j in range(num_accounts)] for i in range(num_accounts)],
            }
            result["solution"] = solution
        logger.info(f"Optimization status: {status}, solution: {result['solution']}")
        return result