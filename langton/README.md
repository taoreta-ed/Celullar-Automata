# Langton's Multi-Ant Simulation

A Python simulation of multiple ant types following Langton's ant rules on a 500×500 grid.

## Features

- **4 Ant Types**: Queens (1%), Workers (55%), Reproducers (9%), Soldiers (35%)
- **Langton Rules**: Hidden black/white cell states govern ant behavior
- **Reproduction**: Reproducers + Queens with opposite facing directions breed
- **Lifespan**: Each ant lives for 80 iterations
- **Queen Encounters**: Age-dependent survival rules
- **Collision Handling**: Ants redirect when cells are occupied
- **Real-time Visualization**: Live matplotlib animation with statistics
- **Scenario Detection**: Identifies isolation, overpopulation, or stable states

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run a Simulation (headless, no visualization)
```bash
python main.py --iterations 500 --report --csv
```

### 3. Run with Real-Time Visualization
```bash
python main.py --iterations 500 --visualize
```

### 4. Run Multiple Simulations (parameter exploration)
```bash
python main.py --batch 3 --iterations 200 --report
```

## Command-Line Options

```
--iterations, -i       Number of iterations (default: 500)
--seed, -s            Random seed (default: 42)
--grid-size, -g       Grid size N×N (default: 500)
--occupancy, -o       Initial occupancy ratio 0-1 (default: 0.5)
--visualize, -v       Run interactive visualization
--report, -r          Generate final report with plots
--csv, -c             Export statistics to CSV
--output-dir          Directory for reports (default: output)
--batch, -b           Number of simulations to run
--quiet, -q           Suppress status messages
```

## Project Structure

- `config.py` — Configuration constants (densities, rules, thresholds)
- `ant.py` — Ant class hierarchy (Queen, Worker, Reproducer, Soldier)
- `grid.py` — Grid state management and Langton rules
- `simulation.py` — Main simulation loop and lifecycle logic
- `visualization.py` — Matplotlib animation and report generation
- `main.py` — CLI entry point
- `requirements.txt` — Python dependencies

## Parameter Tuning

All initial parameters in `config.py` are designed for optimization (requirement #8):

- **ANT_DENSITIES**: Initial proportion of each type
- **LIFESPAN**: Iterations each ant survives
- **REPRODUCTION_PROBABILITY**: Chance of successful breeding
- **SCENARIO_THRESHOLDS**: Isolation/overpopulation/stability detection

Edit `config.py` and re-run simulations to find stable equilibrium.

## Example Workflow

1. **Run baseline with default parameters**:
   ```bash
   python main.py --iterations 1000 --report --csv --seed 42
   ```

2. **Analyze the report** in `output/` for which scenario occurs

3. **Adjust `config.py`** (e.g., increase reproducer density) and re-run

4. **Compare results** across multiple runs to find stable configuration

5. **Generate final 3-scenario report** with optimized parameters

## Output

- **PNG Reports**: Population dynamics, age distribution, occupancy ratio
- **CSV Statistics**: Detailed per-iteration counts and metrics
- **Console Output**: Real-time scenario detection and statistics

## Implementation Notes

- Ant positions: Toroidal grid (wraps at edges)
- Cell state: Hidden black/white (not shown to user)
- Movement: Attempted sequentially; collisions redirected
- Reproduction: Spawned adjacent to reproducer when rule fires
- Performance: ~1-5 FPS real-time visualization at 500×500

## Requirements (from specification)

✅ Requirement #1: 4 ant types with initial density distribution  
✅ Requirement #2: Langton rules with hidden cell labels  
✅ Requirement #3: 50% occupancy distribution (configurable)  
✅ Requirement #4: Birth via reproducer ↔ queen at opposite directions  
✅ Requirement #5: 80-iteration lifespan  
✅ Requirement #6: Queen encounter rules (age-dependent)  
✅ Requirement #7: Cell collision handling + direction retry  
✅ Requirement #8: Configurable parameters for optimization  
✅ Requirement #9: Three scenario detection + report generation  

---

**Status**: Phase 1-3 complete. Phase 4 (parameter optimization) is exploratory.
