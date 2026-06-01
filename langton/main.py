"""
Main entry point for Langton's multi-ant simulation.
Provides CLI interface for running simulations with various options.
"""

import argparse
import sys
from simulation import Simulation
from visualization import SimulationVisualizer
from config import DEFAULT_ITERATIONS, RANDOM_SEED


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Langton\'s Multi-Ant Simulation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --iterations 500 --visualize
  python main.py --iterations 1000 --report --seed 42
  python main.py --batch 3 --iterations 200  # Run 3 simulations
        """
    )
    
    parser.add_argument(
        '--iterations', '-i', type=int, default=DEFAULT_ITERATIONS,
        help=f'Number of iterations to run (default: {DEFAULT_ITERATIONS})'
    )
    
    parser.add_argument(
        '--seed', '-s', type=int, default=RANDOM_SEED,
        help=f'Random seed for reproducibility (default: {RANDOM_SEED})'
    )
    
    parser.add_argument(
        '--grid-size', '-g', type=int, default=100,
        help='Grid size (N x N, default: 100)'
    )
    
    parser.add_argument(
        '--occupancy', '-o', type=float, default=0.5,
        help='Initial occupancy ratio (0-1, default: 0.5 for 50%)'
    )
    
    parser.add_argument(
        '--visualize', '-v', action='store_true',
        help='Run interactive real-time visualization'
    )

    parser.add_argument(
        '--toroidal', dest='toroidal', action='store_true',
        help='Enable toroidal wrap-around (default)'
    )
    parser.add_argument(
        '--no-toroidal', dest='toroidal', action='store_false',
        help='Disable toroidal wrap; edges are boundaries'
    )
    parser.set_defaults(toroidal=True)
    
    parser.add_argument(
        '--report', '-r', action='store_true',
        help='Generate final report with plots'
    )
    
    parser.add_argument(
        '--csv', '-c', action='store_true',
        help='Export statistics to CSV'
    )
    
    parser.add_argument(
        '--output-dir', type=str, default='output',
        help='Output directory for reports (default: output)'
    )
    
    parser.add_argument(
        '--batch', '-b', type=int, default=1,
        help='Run multiple simulations (for parameter exploration)'
    )
    
    parser.add_argument(
        '--quiet', '-q', action='store_true',
        help='Suppress status messages'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not (0 < args.occupancy <= 1):
        print("Error: Occupancy must be between 0 and 1")
        sys.exit(1)
    
    if args.iterations < 1:
        print("Error: Iterations must be at least 1")
        sys.exit(1)
    
    # Run simulation(s)
    for batch_num in range(args.batch):
        if args.batch > 1 and not args.quiet:
            print(f"\n{'='*60}")
            print(f"Run {batch_num + 1}/{args.batch}")
            print(f"{'='*60}")
        
        # Create simulation
        seed = args.seed + batch_num if args.batch > 1 else args.seed
        sim = Simulation(
            grid_size=args.grid_size,
            occupancy_ratio=args.occupancy,
            seed=seed,
            toroidal=args.toroidal
        )
        
        if not args.quiet:
            print(f"Initialized grid {args.grid_size}x{args.grid_size}")
            print(f"Initial ants: {sim.initial_ant_count}")
            print(f"Occupancy: {sim.grid.get_occupancy_ratio():.2%}")
        
        # Create visualizer
        visualizer = SimulationVisualizer(sim, output_dir=args.output_dir)
        
        # Run visualization or headless simulation
        if args.visualize:
            if not args.quiet:
                print(f"Starting interactive visualization for {args.iterations} iterations...")
            visualizer.run_interactive_animation(num_generations=args.iterations)
        else:
            if not args.quiet:
                print(f"Running simulation for {args.iterations} iterations...")
            sim.run(args.iterations)
            
            if not args.quiet:
                final_scenario = sim.detect_scenario()
                print(f"Final ant count: {sim.grid.get_ant_count()}")
                print(f"Final occupancy: {sim.grid.get_occupancy_ratio():.2%}")
                if final_scenario:
                    print(f"Detected scenario: {final_scenario}")
        
        # Generate reports
        if args.report:
            if not args.quiet:
                print("Generating report...")
            visualizer.generate_scenario_reports(run_name=f'run_{batch_num+1}')
        
        if args.csv:
            if not args.quiet:
                print("Exporting statistics...")
            visualizer.export_statistics_csv(filename=f'stats_{batch_num+1}.csv')
    
    if not args.quiet:
        print("\nDone!")


if __name__ == '__main__':
    main()
