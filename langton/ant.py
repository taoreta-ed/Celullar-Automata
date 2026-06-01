"""
Ant class hierarchy for Langton's multi-ant simulation.
Base class + 4 subclasses: Queen, Worker, Reproducer, Soldier
"""

from config import ANT_COLORS, DIRECTIONS, DIRECTION_NAMES, LIFESPAN


class Ant:
    """Base Ant class with shared properties and methods."""
    
    def __init__(self, x, y, ant_type, direction='N'):
        """
        Initialize an ant.
        
        Args:
            x, y: Grid position
            ant_type: One of 'queen', 'worker', 'reproducer', 'soldier'
            direction: One of 'N', 'E', 'S', 'W' (default: North)
        """
        self.x = x
        self.y = y
        self.ant_type = ant_type
        self.direction = direction
        self.age = 0
        self.lifespan = LIFESPAN
        self.color = ANT_COLORS.get(ant_type, (128, 128, 128))
    
    def age_one_iteration(self):
        """Increment age by 1 iteration."""
        self.age += 1
    
    def is_alive(self):
        """Check if ant is still alive (age < lifespan)."""
        return self.age < self.lifespan
    
    def move(self, new_x, new_y):
        """Move ant to new position."""
        self.x = new_x
        self.y = new_y
    
    def turn(self, direction):
        """Turn ant to face new direction."""
        self.direction = direction
    
    def get_position(self):
        """Return (x, y) tuple."""
        return (self.x, self.y)
    
    def get_direction_offset(self):
        """Return (dx, dy) offset for current facing direction."""
        return DIRECTIONS[self.direction]
    
    def __repr__(self):
        return f"Ant({self.ant_type}, age={self.age}, pos=({self.x},{self.y}), dir={self.direction})"


class Queen(Ant):
    """Queen ant: can reproduce with reproducer ants."""
    
    def __init__(self, x, y, direction='N'):
        super().__init__(x, y, 'queen', direction)


class Worker(Ant):
    """Worker ant: standard moving ant, no special behavior."""
    
    def __init__(self, x, y, direction='N'):
        super().__init__(x, y, 'worker', direction)


class Reproducer(Ant):
    """Reproducer ant: can reproduce with queen ants (opposite facing direction)."""
    
    def __init__(self, x, y, direction='N'):
        super().__init__(x, y, 'reproducer', direction)


class Soldier(Ant):
    """Soldier ant: standard moving ant, no special behavior."""
    
    def __init__(self, x, y, direction='N'):
        super().__init__(x, y, 'soldier', direction)


# Factory function to create ant by type
def create_ant(x, y, ant_type, direction='N'):
    """
    Factory function to create an ant of the specified type.
    
    Args:
        x, y: Grid position
        ant_type: One of 'queen', 'worker', 'reproducer', 'soldier'
        direction: One of 'N', 'E', 'S', 'W'
    
    Returns:
        Ant instance of the specified type
    """
    ant_classes = {
        'queen': Queen,
        'worker': Worker,
        'reproducer': Reproducer,
        'soldier': Soldier
    }
    
    if ant_type not in ant_classes:
        raise ValueError(f"Unknown ant type: {ant_type}")
    
    return ant_classes[ant_type](x, y, direction)
