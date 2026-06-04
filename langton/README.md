# Langton's Multi-Ant Simulation

A Python simulation of multiple ant types following Langton's ant rules on a 100×100 grid by default.

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
python main.py --report --csv
```

### 3. Run with Real-Time Visualization
```bash
python main.py --visualize
```

### 4. Run Multiple Simulations (parameter exploration)
```bash
python main.py --batch 3 --iterations 200 --report
```

### 5. Reproducible Runs with Seed
```bash
python main.py --seed 42 --report --csv
```

The default settings are `--grid-size 100` and `--iterations 500`.

## Command-Line Options

```
--iterations, -i       Number of iterations (default: 500)
--seed, -s            Random seed (default: 42)
--grid-size, -g       Grid size N×N (default: 100)
--occupancy, -o       Initial occupancy ratio 0-1 (default: 0.5)
--visualize, -v       Run interactive visualization
--toroidal            Enable toroidal wrap-around (default)
--no-toroidal         Disable toroidal wrap; edges are boundaries
--report, -r          Generate final report with plots
--csv, -c             Export statistics to CSV
--output-dir          Directory for reports (default: output)
--log-file            Optional file to save summary output from the run
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
   python main.py --report --csv --seed 42
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
- Performance: ~1-5 FPS real-time visualization at 100×100

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

## Explicación

- **Por qué esa cantidad de hormigas iniciales:** Los porcentajes iniciales están en `config.py` bajo `ANT_DENSITIES`. Se eligieron para crear dinámicas interesantes: las reinas (`queen`) son raras (1%) para que sus encuentros sean significativos; las trabajadoras (`worker`) son mayoría para mantener la población y la actividad; las reproductoras (`reproducer`) están en una proporción moderada para permitir nacimientos controlados; las soldadas (`soldier`) están en una proporción alta para aumentar interacciones y colisiones. El número inicial de hormigas se calcula como `int(N * N * occupancy * density)` donde `N` es `--grid-size`.

- **¿Qué es la ocupancia?** La *ocupancia* es la fracción de celdas del tablero que están ocupadas por hormigas en un instante dado. Matemáticamente:

   ocupancia = (celdas ocupadas) / (N * N)

   - Rango: 0 → 1 (por ejemplo, `0.5` = 50%).
   - Se controla inicialmente con `--occupancy` o `config.py` → `OCCUPANCY_RATIO`.
   - Efecto: mayor ocupancia implica más colisiones y riesgo de sobrepoblación; menor ocupancia puede llevar al aislamiento o extinción.

- **Escenarios y cómo los determinamos:** La detección de escenarios utiliza umbrales en `config.py`.
   - *Aislamiento* (isolation): la población total cae por debajo de `ISOLATION_THRESHOLD` (p. ej. 10%) del tamaño inicial. Se detecta comparando `total_ants` contra `initial_ants * ISOLATION_THRESHOLD`.
   - *Sobrepoblación* (overpopulation): la ocupancia de la grilla supera `OVERPOPULATION_GRID_THRESHOLD` (p. ej. 80%) Y la tasa de muertes recientes supera `OVERPOPULATION_DEATH_RATE` (p. ej. 15%). La tasa de muerte se mide como `deaths_this_iter / ants_previous_iter`.
   - *Estado estable* (stable): la población se mantiene dentro de ±`STABLE_POPULATION_VARIANCE` durante `STABLE_GENERATIONS_REQUIRED` generaciones consecutivas (p. ej. ±5% durante 50 generaciones).

- **Qué vemos en los reportes y CSVs:**
   - El PNG del reporte contiene: (1) dinámica de población por tipo a lo largo de las generaciones; (2) distribución de edades en el estado final; (3) evolución de la ocupancia en el tiempo; (4) una instantánea visual de la grilla final y un resumen textual con números clave y el último escenario detectado.
   - El CSV (`output/stats_*.csv`) exporta por generación las métricas: `generation`, `total_ants`, `queen_count`, `worker_count`, `reproducer_count`, `soldier_count`, `births`, `deaths`, `avg_age`, `occupancy_ratio`.
   - En consola se muestran detecciones de escenarios en tiempo real y estadísticas finales cuando la ejecución termina.

## Reglas de movimiento y envoltura

- **Regla de movimiento (Langton):**
   1. La hormiga lee el color de la celda actual (oculta): negro = `0`, blanco = `1`.
   2. Gira: si la celda es negra gira a la izquierda; si es blanca gira a la derecha.
   3. Invierte el color de la celda actual (black ↔ white).
   4. Avanza una celda en la nueva dirección.

- **Colisiones:** si la celda objetivo está ocupada, la hormiga prueba hasta 3 direcciones alternativas (en orden aleatorio). Si todas las direcciones libres están ocupadas o fuera de los límites (cuando la envoltura está desactivada), la hormiga se queda en su sitio esta iteración.

- **Envoltura toroidal:** por defecto la grilla es toroidal (los bordes se conectan): al avanzar fuera del borde la hormiga aparece por el lado opuesto. Puedes desactivar esta envoltura con la opción `--no-toroidal`; en ese modo, el borde actúa como límite y un intento de avanzar fuera de la grilla se considera bloqueado (la hormiga seguirá la lógica de colisiones para buscar otra dirección).

Ejemplos:

```bash
# Ejecutar con envoltura toroidal (por defecto)
python main.py --iterations 200 --grid-size 100 --occupancy 0.3 --report

# Ejecutar SIN envoltura (bordes son límites)
python main.py --iterations 200 --grid-size 100 --occupancy 0.3 --no-toroidal --report
```
