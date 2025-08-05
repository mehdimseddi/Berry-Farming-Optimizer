# config.py
from .domain.entities import PlantTarget, SeedRequirements

SEED_NAMES = ['plain_spicy', 'very_spicy', 'very_bitter', 'plain_bitter', 'very_sweet', 'plain_sweet']
PLANT_NAMES = ['leppa', 'cheri', 'pecha', 'strawbst']

PLANT_TARGETS = [
    PlantTarget("leppa", 2.5, SeedRequirements.from_array([0, 1, 0, 1, 0, 1])),
    PlantTarget("cheri", 1.85, SeedRequirements.from_array([3, 0, 0, 0, 0, 0])),
    PlantTarget("pecha", 1.0, SeedRequirements.from_array([0, 0, 0, 0, 1, 1])),
    PlantTarget("strawbst", 1.0, SeedRequirements.from_array([0, 0, 1, 1, 0, 0]))
]

MAX_PLANTS_PER_ACCOUNT = 156