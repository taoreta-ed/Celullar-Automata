"""
Simulation class orchestrating the main simulation loop.
Handles:
- Grid initialization with ant distribution
- Iteration loop (movement → reproduction → aging → death)
- Statistics tracking
- Scenario detection (isolation, overpopulation, stable)
"""

import random
import numpy as np
from config import (
    GRID_SIZE, OCCUPANCY_RATIO, ANT_DENSITIES, LIFESPAN,
    REPRODUCTION_PROBABILITY, OPPOSITE_DIRECTIONS, QUEEN_ENCOUNTER_SAME_AGE_PROB,
    QUEEN_ENCOUNTER_OLD_AGE_THRESHOLD, QUEEN_ENCOUNTER_OLD_AGE_PROB,
    ISOLATION_THRESHOLD, OVERPOPULATION_GRID_THRESHOLD, OVERPOPULATION_DEATH_RATE,
    STABLE_POPULATION_VARIANCE, STABLE_GENERATIONS_REQUIRED
)
from grid import Grid
from ant import create_ant


class Simulation:
    """Main simulation orchestrator."""
    
    def __init__(self, grid_size=GRID_SIZE, occupancy_ratio=OCCUPANCY_RATIO, seed=None):
        """
        Initialize the simulation.
        
        Args:
            grid_size: Size of grid (grid_size x grid_size)
            occupancy_ratio: Fraction of grid initially occupied
            seed: Random seed for reproducibility
        """
        self.grid = Grid(seed=seed)
        self.generation = 0
        self.initial_ant_count = 0
        
        # Statistics tracking
        self.stats = {
            'generation': [],
            'total_ants': [],
            'queen_count': [],
            'worker_count': [],
            'reproducer_count': [],
            'soldier_count': [],
            'births': [],
            'deaths': [],
            'avg_age': [],
            'occupancy_ratio': []
        }
        
        # Initialize grid with ants
        self._initialize_ants(occupancy_ratio)
        self.initial_ant_count = self.grid.get_ant_count()
    
    def _initialize_ants(self, occupancy_ratio):
        """
        Initialize the grid with ants following the density distribution.
        
        Args:
            occupancy_ratio: Fraction of grid cells to initially occupy (requirement #3)
        """
        # Calculate number of ants to place
        total_cells = GRID_SIZE * GRID_SIZE
        num_ants_to_place = int(total_cells * occupancy_ratio)
        
        # Shuffle all positions in the grid
        positions = [(x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE)]
        random.shuffle(positions)
        positions = positions[:num_ants_to_place]
        
        # Assign ant types based on densities
        ant_type_counts = {
            'queen': int(num_ants_to_place * ANT_DENSITIES['queen']),
            'worker': int(num_ants_to_place * ANT_DENSITIES['worker']),
            'reproducer': int(num_ants_to_place * ANT_DENSITIES['reproducer']),
            'soldier': int(num_ants_to_place * ANT_DENSITIES['soldier'])
        }
        
        # Adjust for rounding errors
        total_assigned = sum(ant_type_counts.values())
        if total_assigned < num_ants_to_place:
            ant_type_counts['worker'] += (num_ants_to_place - total_assigned)
        
        # Create ant type list (shuffled)
        ant_types = []
        for ant_type, count in ant_type_counts.items():
            ant_types.extend([ant_type] * count)
        random.shuffle(ant_types)
        
        # Place ants
        for i, (x, y) in enumerate(positions):
            if i < len(ant_types):
                ant_type = ant_types[i]
                direction = random.choice(['N', 'E', 'S', 'W'])
                ant = create_ant(x, y, ant_type, direction)
                self.grid.place_ant(ant, x, y)
    
    def iterate(self):
        """Execute one simulation iteration."""
        self.generation += 1
        
        births = 0
        deaths = 0
        
        # Phase 1: Movement (apply Langton rules)
        ants_to_process = self.grid.get_all_ants().copy()
        for ant in ants_to_process:
            if (ant.x, ant.y) in self.grid.ants:  # Verify ant still exists
                self.grid.attempt_movement_with_collision(ant)
        
        # Phase 2: Reproduction (requirement #4) - optimized with spatial search
        # Only check reproducers that could be near queens (within Manhattan distance 1)
        reproducers = self.grid.get_ant_by_type('reproducer')
        
        for reproducer in reproducers:
            if (reproducer.x, reproducer.y) not in self.grid.ants:
                continue  # Reproducer dead
            
            # Check only adjacent positions for queens
            adjacent_positions = [
                (reproducer.x - 1, reproducer.y - 1), (reproducer.x, reproducer.y - 1), (reproducer.x + 1, reproducer.y - 1),
                (reproducer.x - 1, reproducer.y),     (reproducer.x, reproducer.y),     (reproducer.x + 1, reproducer.y),
                (reproducer.x - 1, reproducer.y + 1), (reproducer.x, reproducer.y + 1), (reproducer.x + 1, reproducer.y + 1)
            ]
            
            for adj_x, adj_y in adjacent_positions:
                # Wrap coordinates
                adj_x = adj_x % 500
                adj_y = adj_y % 500
                
                queen = self.grid.get_ant(adj_x, adj_y)
                if queen and queen.ant_type == 'queen':
                    # Check if they have opposite facing directions
                    if reproducer.direction == OPPOSITE_DIRECTIONS.get(queen.direction):
                        # 50% probability to reproduce
                        if random.random() < REPRODUCTION_PROBABILITY:
                            # Spawn new ant nearby (within 1 cell of reproducer)
                            new_ant_type = random.choice(['queen', 'worker', 'reproducer', 'soldier'])
                            new_direction = random.choice(['N', 'E', 'S', 'W'])
                            
                            # Try to place new ant in a nearby free cell
                            placed = False
                            for dx in [-1, 0, 1]:
                                for dy in [-1, 0, 1]:
                                    if dx == 0 and dy == 0:
                                        continue
                                    new_x = (reproducer.x + dx) % 500
                                    new_y = (reproducer.y + dy) % 500
                                    
                                    if not self.grid.occupancy[new_y, new_x]:
                                        new_ant = create_ant(new_x, new_y, new_ant_type, new_direction)
                                        self.grid.place_ant(new_ant, new_x, new_y)
                                        births += 1
                                        placed = True
                                        break
                                if placed:
                                    break
        
        # Phase 3: Aging
        for ant in self.grid.get_all_ants():
            ant.age_one_iteration()
        
        # Phase 4: Death by age (requirement #5 - 80 iteration lifespan)
        ants_to_remove = []
        for ant in self.grid.get_all_ants():
            if not ant.is_alive():
                ants_to_remove.append(ant)
        
        for ant in ants_to_remove:
            self.grid.remove_ant(ant.x, ant.y)
            deaths += 1
        
        # Phase 5: Queen encounter rules (requirement #6) - optimized spatial check
        queens = self.grid.get_ant_by_type('queen')
        checked_pairs = set()  # Track checked queen pairs to avoid duplicates
        
        for i, queen1 in enumerate(queens):
            if (queen1.x, queen1.y) not in self.grid.ants:
                continue  # Queen already dead
            
            # Only check adjacent queen locations (not all pairs)
            adjacent_positions = [
                (queen1.x - 1, queen1.y - 1), (queen1.x, queen1.y - 1), (queen1.x + 1, queen1.y - 1),
                (queen1.x - 1, queen1.y),                               (queen1.x + 1, queen1.y),
                (queen1.x - 1, queen1.y + 1), (queen1.x, queen1.y + 1), (queen1.x + 1, queen1.y + 1)
            ]
            
            for adj_x, adj_y in adjacent_positions:
                # Wrap coordinates
                adj_x = adj_x % 500
                adj_y = adj_y % 500
                
                queen2 = self.grid.get_ant(adj_x, adj_y)
                if queen2 and queen2.ant_type == 'queen' and queen1 is not queen2:
                    # Create a consistent pair identifier
                    pair_id = (min(id(queen1), id(queen2)), max(id(queen1), id(queen2)))
                    if pair_id in checked_pairs:
                        continue
                    checked_pairs.add(pair_id)
                    
                    # They meet: apply rule
                    if queen1.age < QUEEN_ENCOUNTER_OLD_AGE_THRESHOLD and \
                       queen2.age < QUEEN_ENCOUNTER_OLD_AGE_THRESHOLD:
                        # Both young: 50% probability one dies
                        if random.random() < QUEEN_ENCOUNTER_SAME_AGE_PROB:
                            victim = random.choice([queen1, queen2])
                            if (victim.x, victim.y) in self.grid.ants:
                                self.grid.remove_ant(victim.x, victim.y)
                                deaths += 1
                    else:
                        # At least one old: 20% probability both die
                        if random.random() < QUEEN_ENCOUNTER_OLD_AGE_PROB:
                            for queen in [queen1, queen2]:
                                if (queen.x, queen.y) in self.grid.ants:
                                    self.grid.remove_ant(queen.x, queen.y)
                                    deaths += 1
        
        # Record statistics
        self._record_stats(births, deaths)
    
    def _record_stats(self, births, deaths):
        """Record statistics for this iteration."""
        all_ants = self.grid.get_all_ants()
        type_counts = {
            'queen': len([a for a in all_ants if a.ant_type == 'queen']),
            'worker': len([a for a in all_ants if a.ant_type == 'worker']),
            'reproducer': len([a for a in all_ants if a.ant_type == 'reproducer']),
            'soldier': len([a for a in all_ants if a.ant_type == 'soldier'])
        }
        
        avg_age = np.mean([a.age for a in all_ants]) if all_ants else 0
        
        self.stats['generation'].append(self.generation)
        self.stats['total_ants'].append(len(all_ants))
        self.stats['queen_count'].append(type_counts['queen'])
        self.stats['worker_count'].append(type_counts['worker'])
        self.stats['reproducer_count'].append(type_counts['reproducer'])
        self.stats['soldier_count'].append(type_counts['soldier'])
        self.stats['births'].append(births)
        self.stats['deaths'].append(deaths)
        self.stats['avg_age'].append(avg_age)
        self.stats['occupancy_ratio'].append(self.grid.get_occupancy_ratio())
    
    def detect_scenario(self):
        """
        Detect which scenario the system is in.
        
        Returns:
            'isolation', 'overpopulation', 'stable', or None
        """
        if len(self.stats['total_ants']) < 2:
            return None
        
        current_pop = self.stats['total_ants'][-1]
        
        # Isolation: population drops below 10% of initial
        if current_pop < self.initial_ant_count * ISOLATION_THRESHOLD:
            return 'isolation'
        
        # Overpopulation: grid occupancy > 80% AND rapid death rate
        if len(self.stats['occupancy_ratio']) > 0:
            if self.stats['occupancy_ratio'][-1] > OVERPOPULATION_GRID_THRESHOLD:
                if len(self.stats['deaths']) > 0 and self.stats['deaths'][-1] > 0:
                    death_rate = self.stats['deaths'][-1] / (current_pop + self.stats['deaths'][-1]) \
                        if (current_pop + self.stats['deaths'][-1]) > 0 else 0
                    if death_rate > OVERPOPULATION_DEATH_RATE:
                        return 'overpopulation'
        
        # Stable state: population within ±5% for 50+ consecutive generations
        if len(self.stats['total_ants']) >= STABLE_GENERATIONS_REQUIRED:
            recent_pops = self.stats['total_ants'][-STABLE_GENERATIONS_REQUIRED:]
            avg_pop = np.mean(recent_pops)
            variance = np.std(recent_pops) / avg_pop if avg_pop > 0 else 0
            
            if variance <= STABLE_POPULATION_VARIANCE:
                return 'stable'
        
        return None
    
    def run(self, num_iterations):
        """
        Run the simulation for a specified number of iterations.
        
        Args:
            num_iterations: Number of iterations to run
        """
        for _ in range(num_iterations):
            self.iterate()
    
    def get_stats(self):
        """Return statistics dictionary."""
        return self.stats
    
    def get_grid(self):
        """Return the grid object."""
        return self.grid
