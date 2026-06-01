"""
Grid class managing the simulation world state.
Handles:
- Cell occupancy tracking
- Hidden Langton cell state (black=0, white=1)
- Langton movement rules
- Ant placement, movement, and removal
"""

import numpy as np
import random
from config import GRID_SIZE, DIRECTIONS, DIRECTION_TURNS, DIRECTION_NAMES


class Grid:
    """Represents the simulation world."""
    
    def __init__(self, grid_size=GRID_SIZE, seed=None):
        """
        Initialize the grid.
        
        Args:
            grid_size: Width/height of the grid.
            seed: Random seed for reproducibility
        """
        self.grid_size = grid_size

        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        # Cell occupancy: True if an ant is present, False otherwise
        self.occupancy = np.zeros((self.grid_size, self.grid_size), dtype=bool)
        
        # Langton cell state: 0=black (turn left), 1=white (turn right)
        # Initialized randomly (50% black, 50% white) per requirement #2
        self.cell_state = np.random.choice([0, 1], size=(self.grid_size, self.grid_size))
        
        # Store ants: dict mapping (x, y) -> Ant object
        # Max 1 ant per cell per requirement #7
        self.ants = {}
    
    def is_valid_position(self, x, y):
        """Check if position is within grid bounds."""
        return 0 <= x < self.grid_size and 0 <= y < self.grid_size
    
    def get_ant(self, x, y):
        """Get ant at position (x, y), or None if empty."""
        return self.ants.get((x, y), None)
    
    def place_ant(self, ant, x, y):
        """
        Place an ant at position (x, y).
        
        Args:
            ant: Ant object
            x, y: Grid position
        
        Returns:
            True if placement successful, False if cell occupied
        """
        if not self.is_valid_position(x, y):
            return False
        
        if self.occupancy[y, x]:
            return False  # Cell already occupied
        
        ant.move(x, y)
        self.ants[(x, y)] = ant
        self.occupancy[y, x] = True
        return True
    
    def remove_ant(self, x, y):
        """Remove ant at position (x, y)."""
        if (x, y) in self.ants:
            del self.ants[(x, y)]
        self.occupancy[y, x] = False
    
    def move_ant(self, ant, new_x, new_y):
        """
        Move ant to new position.
        
        Args:
            ant: Ant object
            new_x, new_y: Target position
        
        Returns:
            True if move successful, False if target occupied
        """
        if not self.is_valid_position(new_x, new_y):
            return False
        
        if self.occupancy[new_y, new_x]:
            return False  # Target occupied
        
        # Remove from old position
        old_x, old_y = ant.x, ant.y
        if (old_x, old_y) in self.ants:
            del self.ants[(old_x, old_y)]
        self.occupancy[old_y, old_x] = False
        
        # Place at new position
        ant.move(new_x, new_y)
        self.ants[(new_x, new_y)] = ant
        self.occupancy[new_y, new_x] = True
        return True
    
    def flip_cell_state(self, x, y):
        """Flip cell state from black (0) to white (1) or vice versa."""
        if self.is_valid_position(x, y):
            self.cell_state[y, x] = 1 - self.cell_state[y, x]
    
    def get_cell_state(self, x, y):
        """Get cell state at (x, y): 0=black, 1=white."""
        if self.is_valid_position(x, y):
            return self.cell_state[y, x]
        return 1  # Default to white if out of bounds
    
    def apply_langton_rule(self, ant):
        """
        Apply Langton's rule to an ant:
        1. Check current cell color
        2. Turn left (black) or right (white)
        3. Flip cell color
        4. Move forward in new direction
        
        Returns:
            (new_x, new_y) if move successful, None if blocked
        """
        x, y = ant.x, ant.y
        cell_color = self.get_cell_state(x, y)
        
        # Determine turn direction based on cell color
        turn_direction = 'L' if cell_color == 0 else 'R'
        
        # Turn ant
        new_direction = DIRECTION_TURNS[ant.direction][turn_direction]
        ant.turn(new_direction)
        
        # Flip cell color
        self.flip_cell_state(x, y)
        
        # Calculate forward position
        dx, dy = DIRECTIONS[ant.direction]
        new_x = (x + dx) % self.grid_size  # Wrap around (toroidal grid)
        new_y = (y + dy) % self.grid_size
        
        return (new_x, new_y)
    
    def attempt_movement_with_collision(self, ant):
        """
        Try to move ant following Langton rule.
        If target cell is occupied, try 3 other random directions.
        If all 4 directions occupied, ant waits (no movement).
        
        Args:
            ant: Ant object
        
        Returns:
            True if ant moved, False if stuck (all directions occupied)
        """
        x, y = ant.x, ant.y
        current_direction = ant.direction
        
        # Apply Langton rule to get target position
        target_x, target_y = self.apply_langton_rule(ant)
        
        # Try to move to target
        if not self.occupancy[target_y, target_x]:
            self.move_ant(ant, target_x, target_y)
            return True
        
        # Target occupied: try 3 other random directions
        # Get remaining 3 directions
        remaining_directions = [d for d in DIRECTION_NAMES if d != ant.direction]
        random.shuffle(remaining_directions)
        
        for direction in remaining_directions:
            ant.turn(direction)
            dx, dy = DIRECTIONS[direction]
            test_x = (x + dx) % self.grid_size
            test_y = (y + dy) % self.grid_size
            
            if not self.occupancy[test_y, test_x]:
                self.move_ant(ant, test_x, test_y)
                return True
        
        # All directions occupied: revert to original direction and wait
        ant.turn(current_direction)
        return False
    
    def get_all_ants(self):
        """Return list of all ants in the grid."""
        return list(self.ants.values())
    
    def get_ant_count(self):
        """Return total number of ants."""
        return len(self.ants)
    
    def get_occupancy_ratio(self):
        """Return fraction of occupied cells."""
        return np.sum(self.occupancy) / (self.grid_size * self.grid_size)
    
    def get_ant_by_type(self, ant_type):
        """Return list of all ants of a specific type."""
        return [ant for ant in self.ants.values() if ant.ant_type == ant_type]
    
    def get_state_grid(self):
        """
        Return a grid for visualization: each cell value is the ant color (if present).
        Used by visualization to render the world.
        
        Returns:
            2D numpy array of RGB tuples (or zeros for empty cells)
        """
        state_grid = np.zeros((self.grid_size, self.grid_size, 3), dtype=np.uint8)
        
        for (x, y), ant in self.ants.items():
            state_grid[y, x] = ant.color
        
        return state_grid
