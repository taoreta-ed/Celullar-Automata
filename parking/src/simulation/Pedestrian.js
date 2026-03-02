import { CellType } from './Grid.js';

let _pedId = 0;

export const PedestrianState = {
    WALKING: 'walking',
    CROSSING: 'crossing',
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
    }

    static randomColor() {
        const hues = [30, 45, 60, 15, 0]; // skin-like hues
        const hue = hues[Math.floor(Math.random() * hues.length)];
        return `hsl(${hue}, 50%, 65%)`;
    }

    static resetIdCounter() {
        _pedId = 0;
    }

    /**
     * Advance one tick. Returns event descriptors.
     * @param {import('./Grid.js').default} grid
     * @param {()=>number} rng
     * @param {object} params
     * @returns {{type:string, description:string}[]}
     */
    tick(grid, rng, params) {
        const events = [];

        if (this.state === PedestrianState.HIT || this.state === PedestrianState.EXITED) {
            return events;
        }

        if (this.waitTicks > 0) {
            this.waitTicks--;
            return events;
        }

        // Decide next move
        const currentCell = grid.get(this.col, this.row);

        // Choose candidate cells
        const candidates = [];
        for (const d of DELTAS) {
            const nc = this.col + d.dc;
            const nr = this.row + d.dr;
            const cell = grid.get(nc, nr);
            if (!cell) continue;

            // Pedestrians normally stick to sidewalks
            if (cell.type === CellType.SIDEWALK) {
                candidates.push({ col: nc, row: nr, weight: 5 });
            }
            // Crossing a road — risky but possible
            else if (cell.type === CellType.ROAD || cell.type === CellType.PARKING_SPOT) {
                // Probability of crossing
                if (rng() < params.pedestrianCrossProbability) {
                    candidates.push({ col: nc, row: nr, weight: 1 });
                }
            }
            // Exits — pedestrians can leave
            else if (cell.type === CellType.EXIT || cell.type === CellType.ENTRANCE) {
                candidates.push({ col: nc, row: nr, weight: 1 });
            }
        }

        if (candidates.length === 0) return events;

        // Weighted random pick (prefer sidewalks)
        const totalWeight = candidates.reduce((s, c) => s + c.weight, 0);
        let pick = rng() * totalWeight;
        let chosen = candidates[0];
        for (const c of candidates) {
            pick -= c.weight;
            if (pick <= 0) { chosen = c; break; }
        }

        // Check if crossing a road
        const targetCell = grid.get(chosen.col, chosen.row);
        if (targetCell && (targetCell.type === CellType.ROAD || targetCell.type === CellType.PARKING_SPOT)) {
            this.state = PedestrianState.CROSSING;
            events.push({
                type: 'PEDESTRIAN_CROSS',
                description: `${this.id} cruzando la calle en (${chosen.col},${chosen.row})`,
            });
        } else {
            this.state = PedestrianState.WALKING;
        }

        // Check if leaving the grid
        if (targetCell && (targetCell.type === CellType.EXIT || targetCell.type === CellType.ENTRANCE)) {
            if (this.col <= 1 || this.col >= grid.cols - 2) {
                this.state = PedestrianState.EXITED;
                events.push({
                    type: 'PEDESTRIAN_EXIT',
                    description: `${this.id} salió del estacionamiento`,
                });
            }
        }

        // Move
        this._moveTo(grid, chosen.col, chosen.row);

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
