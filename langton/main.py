"""
Main entry point for Langton's multi-ant simulation.
Provides CLI interface for running simulations with various options.
"""

import argparse
import os
import sys
from datetime import datetime
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
        help='Initial occupancy ratio (0-1, default: 0.5 for 50%%)'
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
        '--log-file', type=str, default=None,
        help='Optional file to save console output summary'
    )
    
    parser.add_argument(
        '--quiet', '-q', action='store_true',
        help='Suppress status messages'
    )
    
    args = parser.parse_args()
    
    # Open log file if requested
    log_file_handle = None
    if args.log_file:
        os.makedirs(os.path.dirname(args.log_file) or '.', exist_ok=True)
        log_file_handle = open(args.log_file, 'w', encoding='utf-8')

    def log(message=''):
        if not args.quiet:
            print(message)
        if log_file_handle is not None:
            log_file_handle.write(f"{message}\n")

    # Validate arguments
    if not (0 < args.occupancy <= 1):
        log("Error: Occupancy must be between 0 and 1")
        if log_file_handle is not None:
            log_file_handle.close()
        sys.exit(1)
    
    if args.iterations < 1:
        print("Error: Iterations must be at least 1")
        sys.exit(1)
    
    def build_run_name(seed, grid_size, iterations, occupancy, toroidal):
        occupancy_str = f"{occupancy:.2f}".rstrip('0').rstrip('.')
        toroidal_tag = 'toroidal' if toroidal else 'notor'
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"S{seed}_G{grid_size}_I{iterations}_O{occupancy_str}_{toroidal_tag}_{timestamp}"

    # Run simulation(s)
    for batch_num in range(args.batch):
        if args.batch > 1:
            log(f"\n{'='*60}")
            log(f"Run {batch_num + 1}/{args.batch}")
            log(f"{'='*60}")
        
        # Create simulation
        seed = args.seed + batch_num if args.batch > 1 else args.seed
        sim = Simulation(
            grid_size=args.grid_size,
            occupancy_ratio=args.occupancy,
            seed=seed,
            toroidal=args.toroidal
        )
        run_name = build_run_name(seed, args.grid_size, args.iterations, args.occupancy, args.toroidal)
        
        log(f"Initialized grid {args.grid_size}x{args.grid_size}")
        log(f"Initial ants: {sim.initial_ant_count}")
        log(f"Occupancy: {sim.grid.get_occupancy_ratio():.2%}")
        
        # Create visualizer
        visualizer = SimulationVisualizer(sim, output_dir=args.output_dir)
        
        # Run visualization or headless simulation
        if args.visualize:
            log(f"Starting interactive visualization for {args.iterations} iterations...")
            visualizer.run_interactive_animation(num_generations=args.iterations)
        else:
            log(f"Running simulation for {args.iterations} iterations...")
            sim.run(args.iterations)
            
            final_scenario = sim.detect_scenario()
            log(f"Final ant count: {sim.grid.get_ant_count()}")
            log(f"Final occupancy: {sim.grid.get_occupancy_ratio():.2%}")
            if len(sim.stats['generation']) >= 80:
                log(f"Iteración 80: {sim.stats['total_ants'][79]} hormigas")
            else:
                log(f"Iteración 80: no disponible (solo {len(sim.stats['generation'])} iteraciones)")
            if final_scenario:
                log(f"Detected scenario: {final_scenario}")
        
        # Generate reports
        if args.report:
            log("Generating report...")
            visualizer.generate_scenario_reports(run_name=run_name)
        
        if args.csv:
            log("Exporting statistics...")
            visualizer.export_statistics_csv(filename=f'{run_name}.csv')
    
    log("\nDone!")
    if log_file_handle is not None:
        log_file_handle.close()


if __name__ == '__main__':
    main()
