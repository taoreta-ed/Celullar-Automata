# Plan: Langton's Multi-Ant Simulation with Type-Based Behaviors

## TL;DR
Build a Python simulation of multiple ant types (queens, workers, reproducers, soldiers) following Langton's ant rules on a 500×500 grid. Use numpy for efficient grid operations and matplotlib for real-time visualization + final analysis. The system will track ant lifecycle (80-iteration lifespan), reproduction, death conditions, and cell collisions. Matplotlib is suitable given the medium grid size, though performance will be the main trade-off for real-time rendering.

---

## Phase 1: Project Structure & Core Data Models (Foundation)

**Files to create:**
- `langton/main.py` — Entry point, CLI arguments for grid size, initial conditions, run parameters
- `langton/ant.py` — `Ant` class hierarchy (base class + 4 subclasses: Queen, Worker, Reproducer, Soldier)
- `langton/grid.py` — `Grid` class managing the world state, ant positions, and Langton rules
- `langton/simulation.py` — `Simulation` class orchestrating main loop, lifecycle checks, birth/death
- `langton/visualization.py` — Real-time matplotlib animation + plot generation for final report
- `langton/config.py` — Configuration constants (initial densities, lifespan, probabilities, etc.)
- `langton/requirements.txt` — Dependencies (numpy, matplotlib)

**Key Design Decisions:**
- Ant types stored in a single list per grid cell (max 1 ant per cell per requirement #7)
- Langton rules applied per ant during movement phase (not exposed to user; "background labels")
- Ant state: `{type, age, x, y, direction, color}`
- Grid cells track occupancy but NOT Langton's black/white state (hidden)

---

## Phase 2: Implement Core Simulation Engine

### Step 1: Ant Class Hierarchy (depends on config.py)
- Base `Ant` class: age, position, direction, type-specific color, lifetime (80 iterations)
- Subclasses override behavior if needed (Queen, Worker, Reproducer, Soldier)
- Each ant tracks: current position, age, direction (0°/90°/180°/270°)

### Step 2: Grid State Management (depends on ant.py)
- 500×500 numpy boolean array tracking cell occupancy
- Hidden Langton state per cell: {black=0, white=1} initialized randomly
- Methods: `place_ant(ant, x, y)`, `remove_ant(x, y)`, `get_ant(x, y)`
- Rule application: Turn left/right, move forward based on cell color

### Step 3: Simulation Core Loop (depends on grid.py, ant.py)
Each iteration:
1. **Movement phase**: For each ant, apply Langton rule → turn → attempt move
   - If target cell occupied → random selection from 3 other directions (req #7)
   - If all 4 directions occupied → wait (no movement this iteration)
2. **Reproduction phase**: Detect reproducers ↔ queen pairs with opposite facing directions (e.g., reproducer facing North ↔ queen facing South) → 50% probability create new ant (spawned at reproducer's position)
3. **Aging phase**: Increment all ant ages
4. **Death phase**: Remove ants with age ≥ 80
5. **Queen encounter phase**: Two queens in same/adjacent cell:
   - Both age < 60 → 50% probability one dies
   - Either age ≥ 60 → 20% probability both die (req #6)

**Parallel opportunities:** Movement, aging, and death checks can be vectorized with numpy.

---

## Phase 3: Visualization & Analysis

### Step 1: Real-time Animation (depends on simulation.py)
- Matplotlib figure with FuncAnimation
- Grid displayed as 500×500 heatmap using ant-color colormap
- Controls: play/pause, speed slider (iterations per frame)
- Display: Current generation, ant counts by type, average age per type
- **Performance note:** At 500×500 with ~2500 ants + live updates, expect 1–5 FPS; acceptable for exploratory visualization but not real-time gaming

### Step 2: Statistics Tracking (depends on simulation.py)
- Per-iteration log: `{generation, queen_count, worker_count, reproducer_count, soldier_count, births, deaths, avg_age}`
- Trigger detection: Identify iteration ranges where:
  - **(a) Death by isolation:** Ant count drops below 10% of initial
  - **(b) Death by overpopulation:** Grid occupancy > 80% + rapid death rate
  - **(c) Stable state:** Population steady ±5% for 50+ consecutive generations

### Step 3: Final Report Generation
- Save three scenario plots (isolation, overpopulation, stable):
  - **Population over time** (line chart: all types + total)
  - **Age distribution** (histogram: ant age bins)
  - **Grid heatmap** (final snapshot)
- Save video/GIF of 100 key iterations showing transition
- CSV export of full statistics

---

## Phase 4: Configuration & Parameter Tuning

**Default initial parameters (from req #8 - to be optimized):**
```
Queen density: 1% (5–10 ants on 500×500)
Worker density: 55%
Reproducer density: 9%
Soldier density: 35%
Occupancy: 50% of grid (62,500 cells)
Lifespan: 80 iterations
Initial direction: Random per ant
Initial Langton state: Random per cell (50% black, 50% white)
```

**Optimization approach:**
1. Run 3 baseline simulations with default params → observe outcome (isolation/overpop/stable)
2. Adjust densities (±5% per type) and re-run
3. Log convergence speed and system stability metric
4. Save best-performing params to `config_optimized.json`

**User input modes:**
- CLI flags: `--grid-size 500 --init-file custom.json --run-iterations 1000`
- Interactive: Load preset scenarios (isolated/stable/dense)

---

## Implementation Steps (Ready for Execution)

1. **Create `config.py`** — Define all constants (densities, colors, lifespan, probabilities)
2. **Create `ant.py`** — Implement `Ant` base class + 4 subclasses with `move()`, `age()` methods
3. **Create `grid.py`** — Implement `Grid` class with Langton rules, occupancy tracking, placement/removal
4. **Create `simulation.py`** — Main loop orchestrating one iteration (movement → birth → death → aging)
5. **Create `visualization.py`** — Real-time animation function + report generation utilities
6. **Create `main.py`** — Entry point, argument parsing, run simulation, save reports
7. **Create `requirements.txt`** — List dependencies (numpy, matplotlib)
8. **Integration & testing** — Run 50-iteration baseline, verify counts and behavior
9. **Parameter optimization** — Adjust config.py values to find stable state (20–30 runs)
10. **Generate report** — Run final simulations for 3 scenarios, export plots + CSV

---

## Verification Strategy

### Automated Checks (per iteration):
- ✓ Total ants ≤ 50% grid (62,500)
- ✓ No ant at age > 80 exists
- ✓ No two ants occupy same cell
- ✓ Births only occur between reproducers ↔ queen with opposite facing directions
- ✓ Directions are one of {0°, 90°, 180°, 270°}

### Manual Validation:
1. Run 100 iterations with visualization → observe movement patterns match Langton rule
2. Verify queen encounter rule: observe two queen cells → one or both disappear (age-dependent)
3. Confirm collision handling: ant hits occupied cell → observe turn to free direction or wait
4. Check final report: 3 plots show distinct dynamics (isolation has declining curve, overpop has spike+crash, stable is flat)

---

## Key Architecture Decisions

| Decision | Rationale | Trade-offs |
|----------|-----------|-----------|
| **Matplotlib for visualization** | Available in workspace; sufficient for 500×500 + exploratory speed control | 1–5 FPS real-time (slower than canvas-based) |
| **Numpy arrays for grid** | Vectorized operations; memory-efficient for 500×500; enables fast occupancy checks | Slight overhead for small grids (<100×100) |
| **Hidden Langton state** | Cleaner UX; user sees only ants + colors; rules applied transparently | Must track background cells carefully; potential debugging complexity |
| **Single list per cell** | Enforces 1 ant/cell; simplifies collision logic | Requires array of optional pointers (could use None) |
| **Configurable initial conditions** | User can test edge cases (100% one type, different grid sizes) | More setup code; more test scenarios |

---

## Scope: Included / Excluded

### ✅ Included:
- 4 ant types with initial density distribution
- Langton rule movement (hidden labels)
- 50% occupancy distribution (configurable)
- Birth condition (reproducer + queen at 180°)
- 80-iteration lifespan
- Queen encounter rules (age-dependent survival)
- Cell collision handling + direction randomization
- Real-time animation + final report generation
- Three scenario analysis (isolation/overpopulation/stable)
- Parameter optimization guidance

### ❌ Explicitly Excluded (out of scope):
- Pheromone trails (not in Langton's rules)
- Ant communication/signaling
- Food sources or resource management
- Spatial clustering analysis (statistical analysis beyond what's in req #9)
- 3D visualization
- Parallel processing (single-threaded simulation)

---

## Further Considerations

1. **Matplotlib Performance Trade-off?**
   - At 500×500 + FPS updates, matplotlib renders ~1–5 FPS. Acceptable for exploration; if real-time is critical, could switch to Pygame/Pyglet later.
   - **Recommendation:** Start with matplotlib (already available); profile after Phase 3. If too slow, refactor `visualization.py` to use Pygame in Phase 4.

---

## User Preferences & Confirmed Choices

✅ **Visualization**: Real-time + final analysis (both modes)  
✅ **Initial conditions**: Configurable (50% random placement or habitat-based)  
✅ **Primary goals**: System dynamics + emergent behavior  
✅ **Grid size**: 500×500 (balanced performance)  
✅ **Dependencies**: matplotlib (already in workspace)  
✅ **Langton rule**: Standard black/white cells (hidden state)—ants track cell colors internally but users see only ant movements  
✅ **Reproduction geometry**: Reproducer + Queen must have opposite facing directions (e.g., reproducer facing North, queen facing South) to breed
