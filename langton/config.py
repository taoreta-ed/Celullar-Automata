"""
Configuration constants for Langton's multi-ant simulation.
All values here can be adjusted for parameter tuning (requirement #8).
"""

import numpy as np

# ============================================================================
# GRID CONFIGURATION
# ============================================================================
GRID_SIZE = 100  # 100x100 grid by default
OCCUPANCY_RATIO = 0.5  # 50% of grid cells initially occupied (requirement #3)
MAX_ANTS = int(GRID_SIZE * GRID_SIZE * OCCUPANCY_RATIO)

# ============================================================================
# ANT TYPE DENSITIES (requirement #1 - initial distribution)
# ============================================================================
# Proportion of each ant type among all ants
ANT_DENSITIES = {
    'queen': 0.01,        # 1% queens
    'worker': 0.55,       # 55% workers
    'reproducer': 0.09,   # 9% reproducers
    'soldier': 0.35       # 35% soldiers
}

# ============================================================================
# ANT PROPERTIES
# ============================================================================
LIFESPAN = 80  # Each ant lives for 80 iterations (requirement #5)

# Colors for visualization (RGB)
ANT_COLORS = {
    'queen': (255, 215, 0),        # Gold
    'worker': (139, 69, 19),       # Brown
    'reproducer': (0, 128, 0),     # Green
    'soldier': (192, 0, 0)         # Crimson red
}

# ============================================================================
# LANGTON RULES (requirement #2 - hidden cell state)
# ============================================================================
# Standard Langton ant rule:
# - On white cell (1): turn right, flip to black
# - On black cell (0): turn left, flip to white
DIRECTIONS = {
    'N': (0, -1),    # North (up)
    'E': (1, 0),     # East (right)
    'S': (0, 1),     # South (down)
    'W': (-1, 0)     # West (left)
}

DIRECTION_NAMES = ['N', 'E', 'S', 'W']
DIRECTION_TURNS = {
    'N': {'L': 'W', 'R': 'E'},
    'E': {'L': 'N', 'R': 'S'},
    'S': {'L': 'E', 'R': 'W'},
    'W': {'L': 'S', 'R': 'N'}
}

# ============================================================================
# REPRODUCTION RULES (requirement #4)
# ============================================================================
REPRODUCTION_PROBABILITY = 0.5  # 50% chance reproducer + queen reproduce
# Queen and reproducer must have opposite facing directions (180°)
OPPOSITE_DIRECTIONS = {
    'N': 'S',
    'S': 'N',
    'E': 'W',
    'W': 'E'
}

# ============================================================================
# DEATH RULES
# ============================================================================

# Queen encounter rule (requirement #6)
QUEEN_ENCOUNTER_SAME_AGE_PROB = 0.5  # Both age < 60: 50% survival
QUEEN_ENCOUNTER_OLD_AGE_THRESHOLD = 60  # Age threshold for old queens
QUEEN_ENCOUNTER_OLD_AGE_PROB = 0.2  # Age >= 60: 20% survival for both

# Collision handling (requirement #7)
# If target cell occupied, try 3 other directions randomly
# If all 4 directions occupied, wait (no movement this iteration)

# ============================================================================
# SIMULATION PARAMETERS
# ============================================================================
DEFAULT_ITERATIONS = 300  # Default number of iterations to run
RANDOM_SEED = 42  # For reproducibility during development

# ============================================================================
# SCENARIO DETECTION THRESHOLDS
# ============================================================================
# For requirement #9: identify three scenarios

# Death by isolation: population drops below X% of initial
ISOLATION_THRESHOLD = 0.10  # 10% of initial population

# Overpopulation: grid occupancy > X% AND rapid death rate
OVERPOPULATION_GRID_THRESHOLD = 0.80  # 80% grid occupancy
OVERPOPULATION_DEATH_RATE = 0.15  # Death rate > 15% per iteration

# Stable state: population within X% for Y consecutive generations
STABLE_POPULATION_VARIANCE = 0.05  # ±5%
STABLE_GENERATIONS_REQUIRED = 50  # 50 consecutive generations
