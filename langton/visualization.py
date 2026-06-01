"""
Visualization module for Langton's ant simulation.
Handles:
- Real-time matplotlib animation
- Live statistics display
- Report generation (plots for isolation, overpopulation, stable scenarios)
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.figure import Figure
import numpy as np
import os
from datetime import datetime


class SimulationVisualizer:
    """Handles real-time visualization and report generation."""
    
    def __init__(self, simulation, output_dir='output'):
        """
        Initialize the visualizer.
        
        Args:
            simulation: Simulation object
            output_dir: Directory to save reports
        """
        self.simulation = simulation
        self.output_dir = output_dir
        self.is_running = False
        self.speed = 1  # Speed multiplier for animation
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Animation figure
        self.fig = None
        self.axes = None
        self.anim = None
    
    def setup_animation_figure(self):
        """Set up matplotlib figure for real-time animation."""
        self.fig = plt.figure(figsize=(16, 10))
        
        # Main grid subplot
        ax_grid = plt.subplot(2, 3, (1, 4))
        
        # Statistics subplots
        ax_pop = plt.subplot(2, 3, 2)
        ax_age = plt.subplot(2, 3, 3)
        ax_types = plt.subplot(2, 3, 5)
        ax_occupancy = plt.subplot(2, 3, 6)
        
        self.axes = {
            'grid': ax_grid,
            'population': ax_pop,
            'age': ax_age,
            'types': ax_types,
            'occupancy': ax_occupancy
        }
        
        self.fig.suptitle('Langton\'s Multi-Ant Simulation', fontsize=16)
        return self.fig
    
    def update_animation_frame(self, frame):
        """Update visualization for one animation frame."""
        # Run simulation steps
        for _ in range(self.speed):
            self.simulation.iterate()
            scenario = self.simulation.detect_scenario()
            if scenario:
                print(f"[Generation {self.simulation.generation}] Scenario detected: {scenario}")
        
        # Clear all subplots
        for ax in self.axes.values():
            ax.clear()
        
        # Update grid visualization
        self._plot_grid()
        
        # Update statistics plots
        self._plot_statistics()
        
        # Update title with current generation and info
        ant_count = self.simulation.grid.get_ant_count()
        scenario = self.simulation.detect_scenario()
        scenario_text = f" [SCENARIO: {scenario}]" if scenario else ""
        self.fig.suptitle(
            f'Langton\'s Multi-Ant Simulation - Gen {self.simulation.generation}, '
            f'Ants: {ant_count}{scenario_text}',
            fontsize=14
        )
        
        plt.tight_layout()
    
    def _plot_grid(self):
        """Plot the grid with ants."""
        ax = self.axes['grid']
        grid_state = self.simulation.grid.get_state_grid()
        ax.imshow(grid_state, origin='upper')
        ax.set_title('Grid (Ant Positions)')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
    
    def _plot_statistics(self):
        """Plot all statistics subplots."""
        stats = self.simulation.stats
        generations = stats['generation']
        
        if not generations:
            return
        
        # Population over time
        ax_pop = self.axes['population']
        ax_pop.plot(generations, stats['total_ants'], 'k-', label='Total', linewidth=2)
        ax_pop.plot(generations, stats['queen_count'], 'gold', label='Queen')
        ax_pop.plot(generations, stats['worker_count'], 'brown', label='Worker')
        ax_pop.plot(generations, stats['reproducer_count'], 'green', label='Reproducer')
        ax_pop.plot(generations, stats['soldier_count'], 'red', label='Soldier')
        ax_pop.set_title('Population Over Time')
        ax_pop.set_xlabel('Generation')
        ax_pop.set_ylabel('Count')
        ax_pop.legend(fontsize=8)
        ax_pop.grid(True, alpha=0.3)
        
        # Age distribution
        ax_age = self.axes['age']
        all_ants = self.simulation.grid.get_all_ants()
        if all_ants:
            ages = [ant.age for ant in all_ants]
            ax_age.hist(ages, bins=20, edgecolor='black', alpha=0.7)
            ax_age.set_title('Age Distribution (Current)')
            ax_age.set_xlabel('Age (iterations)')
            ax_age.set_ylabel('Frequency')
            ax_age.grid(True, alpha=0.3, axis='y')
        
        # Type distribution (pie chart)
        ax_types = self.axes['types']
        type_counts = [
            stats['queen_count'][-1],
            stats['worker_count'][-1],
            stats['reproducer_count'][-1],
            stats['soldier_count'][-1]
        ]
        labels = ['Queen', 'Worker', 'Reproducer', 'Soldier']
        colors = ['gold', 'brown', 'green', 'red']
        if sum(type_counts) > 0:
            ax_types.pie(type_counts, labels=labels, colors=colors, autopct='%1.1f%%')
            ax_types.set_title('Type Distribution (Current)')
        
        # Occupancy ratio
        ax_occupancy = self.axes['occupancy']
        ax_occupancy.plot(generations, stats['occupancy_ratio'], 'b-', linewidth=2)
        ax_occupancy.axhline(y=0.5, color='r', linestyle='--', label='Initial Target')
        ax_occupancy.set_title('Grid Occupancy Ratio')
        ax_occupancy.set_xlabel('Generation')
        ax_occupancy.set_ylabel('Occupancy')
        ax_occupancy.set_ylim([0, 1])
        ax_occupancy.legend()
        ax_occupancy.grid(True, alpha=0.3)
    
    def run_interactive_animation(self, num_generations=500):
        """
        Run interactive real-time animation (requires display).
        
        Args:
            num_generations: Number of generations to animate
        """
        self.setup_animation_figure()
        
        # Create animation
        self.anim = animation.FuncAnimation(
            self.fig, self.update_animation_frame,
            frames=num_generations, repeat=False, interval=100
        )
        
        plt.show()
    
    def generate_scenario_reports(self, run_name='scenario_report'):
        """
        Generate final report with 3 scenario plots.
        
        Args:
            run_name: Name for the report files
        """
        stats = self.simulation.stats
        
        if not stats['generation']:
            print("No simulation data to report.")
            return
        
        # Create figure with 3 scenario subplots
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        
        generations = stats['generation']
        
        # Plot 1: Population over time (all types)
        ax = axes[0]
        ax.plot(generations, stats['total_ants'], 'k-', label='Total', linewidth=2)
        ax.plot(generations, stats['queen_count'], 'gold', label='Queen')
        ax.plot(generations, stats['worker_count'], 'brown', label='Worker')
        ax.plot(generations, stats['reproducer_count'], 'green', label='Reproducer')
        ax.plot(generations, stats['soldier_count'], 'red', label='Soldier')
        ax.set_title('Population Dynamics')
        ax.set_xlabel('Generation')
        ax.set_ylabel('Count')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Plot 2: Age distribution at final generation
        ax = axes[1]
        all_ants = self.simulation.grid.get_all_ants()
        if all_ants:
            ages = [ant.age for ant in all_ants]
            ax.hist(ages, bins=30, edgecolor='black', alpha=0.7, color='skyblue')
            ax.set_title('Age Distribution (Final State)')
            ax.set_xlabel('Age (iterations)')
            ax.set_ylabel('Frequency')
            ax.grid(True, alpha=0.3, axis='y')
        
        # Plot 3: Grid occupancy ratio
        ax = axes[2]
        ax.plot(generations, stats['occupancy_ratio'], 'b-', linewidth=2)
        ax.fill_between(generations, stats['occupancy_ratio'], alpha=0.3)
        ax.set_title('Grid Occupancy Over Time')
        ax.set_xlabel('Generation')
        ax.set_ylabel('Occupancy Ratio')
        ax.set_ylim([0, 1])
        ax.grid(True, alpha=0.3)
        
        plt.suptitle('Langton\'s Multi-Ant Simulation - Final Report', fontsize=14)
        plt.tight_layout()
        
        # Save figure
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = os.path.join(self.output_dir, f'{run_name}_{timestamp}.png')
        plt.savefig(report_path, dpi=150, bbox_inches='tight')
        print(f"Report saved: {report_path}")
        
        return report_path
    
    def export_statistics_csv(self, filename='simulation_stats.csv'):
        """
        Export statistics to CSV file.
        
        Args:
            filename: Output CSV filename
        """
        import csv
        
        stats = self.simulation.stats
        output_path = os.path.join(self.output_dir, filename)
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=stats.keys())
            writer.writeheader()
            
            # Transpose stats dictionary to write rows
            num_rows = len(stats['generation'])
            for i in range(num_rows):
                row = {key: stats[key][i] for key in stats.keys()}
                writer.writerow(row)
        
        print(f"Statistics exported: {output_path}")
        return output_path
