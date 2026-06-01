# Cellular Automata - Langton's Ant Simulation

This folder contains a multi-ant Langton simulation built in Python.

## What it does

- Simulates a **500×500 toroidal grid** by default
- Uses a hidden Langton cell state per cell (black / white)
- Moves multiple ant types using Langton rules + conflict handling
- Implements:
  - **Queen, worker, reproducer, soldier** ant roles
  - **Reproduction rules** for reproducer + queen interactions
  - **Death by age** after 80 iterations
  - **Collision handling** when target cells are occupied
  - **Scenario detection** for isolation, overpopulation, and stability

## Usage

From the `langton` folder run:

```bash
python main.py --iterations 500 --grid-size 500 --occupancy 0.5
```

Options:

- `--iterations`, `-i`: number of iterations to run
- `--grid-size`, `-g`: size of the grid (N×N)
- `--occupancy`, `-o`: initial occupancy ratio between `0` and `1`
- `--visualize`, `-v`: run real-time animation with matplotlib
- `--report`, `-r`: save a final report image with plots
- `--csv`, `-c`: export simulation statistics as CSV
- `--output-dir`: output directory for saved reports and CSV files
- `--seed`, `-s`: random seed for reproducible runs

Example with report generation:

```bash
python main.py --iterations 300 --grid-size 200 --occupancy 0.3 --report
```

Example with visualization:

```bash
python main.py --iterations 200 --grid-size 100 --occupancy 0.25 --visualize
```

## Notes

- `--grid-size` is now respected throughout the simulation, including movement and reproduction wrapping.
- `--occupancy` controls the fraction of initially occupied cells.
- Initial ant type ratios are defined in `config.py`:
  - queens: 1%
  - workers: 55%
  - reproducers: 9%
  - soldiers: 35%
- The final report includes:
  - population dynamics over time
  - age distribution of surviving ants
  - occupancy ratio history
  - snapshot of the final grid

## Files

- `main.py`: command-line entry point
- `simulation.py`: simulation loop and rules
- `grid.py`: grid data structure and Langton movement
- `visualization.py`: animation and report generation
- `config.py`: tune constants and behavior

## Requirements

- Python 3.x
- `numpy`
- `matplotlib`

Install dependencies with:

```bash
pip install numpy matplotlib
```
