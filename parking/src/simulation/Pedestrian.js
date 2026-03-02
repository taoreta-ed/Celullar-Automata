import { CellType } from './Grid.js';

let _pedId = 0;

export const PedestrianState = {
    WALKING: 'walking',
    CROSSING: 'crossing',
    WAITING: 'waiting',
    USING_CROSSWALK: 'using_crosswalk',
    GOING_TO_VEHICLE: 'going_to_vehicle',
    HIT: 'hit',
    EXITED: 'exited',
};

const DELTAS = [
    { dc: 0, dr: -1 },
    { dc: 0, dr: 1 },
    { dc: -1, dr: 0 },
    { dc: 1, dr: 0 },
];

/**
 * A pedestrian entity in the simulation.
 */
export default class Pedestrian {
    constructor(col, row) {
        this.id = `P${++_pedId}`;
        this.col = col;
        this.row = row;
        this.prevCol = col;
        this.prevRow = row;
        this.state = PedestrianState.WALKING;
        /** Ticks remaining for current action */
        this.waitTicks = 0;
        /** Target destination (will wander if null) */
        this.target = null;
        /** Color for rendering */
        this.color = Pedestrian.randomColor();
        /** Whether this pedestrian has a vehicle (goes to parked car) */
        this.hasVehicle = false;
        /** Ticks alive (for auto-exit) */
        this.age = 0;
    }

    static randomColor() {
        const hues = [30, 45, 60, 15, 0];
        const hue = hues[Math.floor(Math.random() * hues.length)];
        return `hsl(${hue}, 50%, 65%)`;
    }

    static resetIdCounter() {
        _pedId = 0;
    }

    /**
     * Advance one tick. Returns event descriptors.
     */
    tick(grid, rng, params) {
        const events = [];

        if (this.state === PedestrianState.HIT || this.state === PedestrianState.EXITED) {
            return events;
        }

        this.age++;

        // Waiting state: count down
        if (this.state === PedestrianState.WAITING) {
            if (this.waitTicks > 0) {
                this.waitTicks--;
                return events;
            }
            this.state = PedestrianState.WALKING;
        }

        if (this.waitTicks > 0) {
            this.waitTicks--;
            return events;
        }

        // After ~60 ticks, start trying to exit
        if (this.age > 40 + Math.floor(rng() * 40)) {
            this.target = null; // wander toward edge
        }

        // If going to a vehicle, navigate toward target
        if (this.state === PedestrianState.GOING_TO_VEHICLE && this.target) {
            return this._navigateToTarget(grid, rng, params, events);
        }

        // Randomly decide to go to a parked vehicle
        if (!this.hasVehicle && rng() < 0.02) {
            const parkedCells = grid.findCells(CellType.PARKING_SPOT).filter(s => s.cell.parked);
            if (parkedCells.length > 0) {
                const target = parkedCells[Math.floor(rng() * parkedCells.length)];
                this.target = { col: target.col, row: target.row };
                this.hasVehicle = true;
                this.state = PedestrianState.GOING_TO_VEHICLE;
                return events;
            }
        }

        // Normal wandering
        const currentCell = grid.get(this.col, this.row);
        const candidates = [];

        for (const d of DELTAS) {
            const nc = this.col + d.dc;
            const nr = this.row + d.dr;
            const cell = grid.get(nc, nr);
            if (!cell) continue;
            // Avoid going back to previous position (reduces zig-zagging)
            if (nc === this.prevCol && nr === this.prevRow && rng() > 0.3) continue;

            // Sidewalks: strong preference
            if (cell.type === CellType.SIDEWALK) {
                candidates.push({ col: nc, row: nr, weight: 6, type: 'sidewalk' });
            }
            // Crosswalks: good option for crossing
            else if (cell.type === CellType.CROSSWALK || cell.crosswalk) {
                candidates.push({ col: nc, row: nr, weight: 4, type: 'crosswalk' });
            }
            // Road: risky, with probability check
            else if (cell.type === CellType.ROAD) {
                if (rng() < params.pedestrianCrossProbability) {
                    candidates.push({ col: nc, row: nr, weight: 1, type: 'road' });
                }
            }
            // Parking spot: can walk through
            else if (cell.type === CellType.PARKING_SPOT) {
                if (rng() < params.pedestrianCrossProbability * 0.5) {
                    candidates.push({ col: nc, row: nr, weight: 1, type: 'road' });
                }
            }
            // Exits and entrances: can leave
            else if (cell.type === CellType.EXIT || cell.type === CellType.ENTRANCE) {
                candidates.push({ col: nc, row: nr, weight: 1, type: 'exit' });
            }
        }

        if (candidates.length === 0) return events;

        // Weighted random pick
        const totalWeight = candidates.reduce((s, c) => s + c.weight, 0);
        let pick = rng() * totalWeight;
        let chosen = candidates[0];
        for (const c of candidates) {
            pick -= c.weight;
            if (pick <= 0) { chosen = c; break; }
        }

        // Determine state and generate events
        const targetCell = grid.get(chosen.col, chosen.row);

        if (chosen.type === 'crosswalk') {
            this.state = PedestrianState.USING_CROSSWALK;
            events.push({
                type: 'PEDESTRIAN_CROSSWALK',
                description: `${this.id} usando cruce peatonal en (${chosen.col},${chosen.row})`,
            });
        } else if (chosen.type === 'road') {
            // Before crossing road, maybe wait
            if (rng() < 0.3 && this.state !== PedestrianState.CROSSING) {
                this.state = PedestrianState.WAITING;
                this.waitTicks = 1 + Math.floor(rng() * 3);
                events.push({
                    type: 'PEDESTRIAN_WAIT',
                    description: `${this.id} esperando para cruzar en (${this.col},${this.row})`,
                });
                return events; // Don't move yet
            }
            this.state = PedestrianState.CROSSING;
            events.push({
                type: 'PEDESTRIAN_CROSS',
                description: `${this.id} cruzando la calle en (${chosen.col},${chosen.row})`,
            });
        } else if (chosen.type === 'exit') {
            if (this.col <= 1 || this.col >= grid.cols - 2) {
                this.state = PedestrianState.EXITED;
                events.push({
                    type: 'PEDESTRIAN_EXIT',
                    description: `${this.id} salió del estacionamiento`,
                });
            }
        } else {
            this.state = PedestrianState.WALKING;
        }

        this._moveTo(grid, chosen.col, chosen.row);
        return events;
    }

    /**
     * Navigate toward a specific target (e.g., a parked vehicle).
     */
    _navigateToTarget(grid, rng, params, events) {
        if (!this.target) return events;

        const dc = Math.sign(this.target.col - this.col);
        const dr = Math.sign(this.target.row - this.row);

        // If arrived
        if (dc === 0 && dr === 0) {
            this.state = PedestrianState.WALKING;
            this.target = null;
            return events;
        }

        // Try to move toward target
        const candidates = [];
        if (dc !== 0) candidates.push({ col: this.col + dc, row: this.row });
        if (dr !== 0) candidates.push({ col: this.col, row: this.row + dr });

        for (const pos of candidates) {
            const cell = grid.get(pos.col, pos.row);
            if (!cell) continue;
            if (
                cell.type === CellType.SIDEWALK ||
                cell.type === CellType.CROSSWALK ||
                cell.type === CellType.ROAD ||
                cell.type === CellType.PARKING_SPOT
            ) {
                if (cell.type === CellType.CROSSWALK) {
                    this.state = PedestrianState.USING_CROSSWALK;
                    events.push({
                        type: 'PEDESTRIAN_CROSSWALK',
                        description: `${this.id} usando cruce peatonal en (${pos.col},${pos.row})`,
                    });
                } else if (cell.type === CellType.ROAD || cell.type === CellType.PARKING_SPOT) {
                    this.state = PedestrianState.CROSSING;
                    events.push({
                        type: 'PEDESTRIAN_CROSS',
                        description: `${this.id} cruzando la calle en (${pos.col},${pos.row})`,
                    });
                }
                this._moveTo(grid, pos.col, pos.row);
                return events;
            }
        }

        // Fallback: random adjacent walkable cell
        for (const d of DELTAS) {
            const nc = this.col + d.dc;
            const nr = this.row + d.dr;
            const cell = grid.get(nc, nr);
            if (cell && cell.isWalkablePed) {
                this._moveTo(grid, nc, nr);
                return events;
            }
        }

        return events;
    }

    _moveTo(grid, col, row) {
        const oldCell = grid.get(this.col, this.row);
        if (oldCell && oldCell.pedestrian === this) oldCell.pedestrian = null;

        this.prevCol = this.col;
        this.prevRow = this.row;
        this.col = col;
        this.row = row;

        const newCell = grid.get(col, row);
        if (newCell) newCell.pedestrian = this;
    }
}
