import { Direction, CellType } from './Grid.js';

let _vehicleId = 0;

/** Driver personality types */
export const DriverType = {
    NORMAL: 'normal',
    AGGRESSIVE: 'aggressive',
    DISTRACTED: 'distracted',
};

/** Vehicle states */
export const VehicleState = {
    ENTERING: 'entering',
    SEARCHING: 'searching',
    PARKING: 'parking',
    PARKED: 'parked',
    UNPARKING: 'unparking',
    EXITING: 'exiting',
    CRASHED: 'crashed',
};

const DIR_DELTA = {
    [Direction.UP]: { dc: 0, dr: -1 },
    [Direction.DOWN]: { dc: 0, dr: 1 },
    [Direction.LEFT]: { dc: -1, dr: 0 },
    [Direction.RIGHT]: { dc: 1, dr: 0 },
};

const OPPOSITE = {
    [Direction.UP]: Direction.DOWN,
    [Direction.DOWN]: Direction.UP,
    [Direction.LEFT]: Direction.RIGHT,
    [Direction.RIGHT]: Direction.LEFT,
};

/**
 * A vehicle entity in the simulation.
 */
export default class Vehicle {
    constructor(col, row, direction, driverType = DriverType.NORMAL) {
        this.id = `V${++_vehicleId}`;
        this.col = col;
        this.row = row;
        this.prevCol = col;
        this.prevRow = row;
        this.direction = direction;
        this.driverType = driverType;
        this.state = VehicleState.ENTERING;
        /** @type {{col:number,row:number}|null} Target parking spot */
        this.targetSpot = null;
        /** Ticks remaining in current action (parking, waiting, etc.) */
        this.waitTicks = 0;
        /** How many ticks this vehicle stayed parked */
        this.parkDuration = 0;
        /** Max park duration (randomised on park) */
        this.maxParkDuration = 0;
        /** Color for rendering (assigned randomly) */
        this.color = Vehicle.randomColor();
        /** Whether this vehicle parked badly */
        this.badParking = false;
    }

    static randomColor() {
        const hue = Math.floor(Math.random() * 360);
        return `hsl(${hue}, 70%, 50%)`;
    }

    static resetIdCounter() {
        _vehicleId = 0;
    }

    /** Try to find & assign a free parking spot. Returns true if found. */
    assignSpot(grid, rng) {
        const freeSpots = grid.getFreeParkingSpots();
        if (freeSpots.length === 0) return false;
        const idx = Math.floor(rng() * freeSpots.length);
        this.targetSpot = { col: freeSpots[idx].col, row: freeSpots[idx].row };
        this.state = VehicleState.SEARCHING;
        return true;
    }

    /**
     * Advance one tick. Returns a list of event descriptors to be logged.
     * @param {import('./Grid.js').default} grid
     * @param {()=>number} rng  seeded random
     * @param {object} params   simulation parameters
     * @returns {{type:string, description:string}[]}
     */
    tick(grid, rng, params) {
        const events = [];

        // ─── Crashed: do nothing ───
        if (this.state === VehicleState.CRASHED) return events;

        // ─── Parked: wait for park duration ───
        if (this.state === VehicleState.PARKED) {
            this.parkDuration++;
            if (this.parkDuration >= this.maxParkDuration) {
                this.state = VehicleState.UNPARKING;
                const cell = grid.get(this.col, this.row);
                if (cell) {
                    cell.parked = false;
                    cell.vehicle = null;
                }
            }
            return events;
        }

        // ─── Parking (animation ticks) ───
        if (this.state === VehicleState.PARKING) {
            if (this.waitTicks > 0) {
                this.waitTicks--;
                return events;
            }
            // Finished parking
            this.state = VehicleState.PARKED;
            this.parkDuration = 0;
            this.maxParkDuration = 10 + Math.floor(rng() * 40);
            const cell = grid.get(this.col, this.row);
            if (cell) cell.parked = true;
            return events;
        }

        // ─── Movement ───
        const nextPos = this._decideNextPosition(grid, rng, params);
        if (!nextPos) return events; // stuck

        // Check for wrong-way driving
        const nextCell = grid.get(nextPos.col, nextPos.row);
        if (nextCell && nextCell.directions.length > 0) {
            const movingDir = this._getMoveDirection(nextPos);
            if (movingDir && !nextCell.directions.includes(movingDir)) {
                if (this.driverType !== DriverType.NORMAL || rng() < params.badDriverProbability * 0.3) {
                    events.push({
                        type: 'WRONG_WAY',
                        description: `${this.id} circulando en dirección equivocada en (${nextPos.col},${nextPos.row})`,
                    });
                } else {
                    return events; // Normal drivers won't go wrong way
                }
            }
        }

        // Collision detection
        if (nextCell && nextCell.vehicle && nextCell.vehicle.id !== this.id) {
            if (rng() < params.collisionProbability) {
                events.push({
                    type: 'COLLISION',
                    description: `Colisión entre ${this.id} y ${nextCell.vehicle.id} en (${nextPos.col},${nextPos.row})`,
                    entityIds: [this.id, nextCell.vehicle.id],
                });
                this.state = VehicleState.CRASHED;
                nextCell.vehicle.state = VehicleState.CRASHED;
            }
            return events; // Can't move into occupied cell
        }

        // Pedestrian hit detection
        if (nextCell && nextCell.pedestrian) {
            events.push({
                type: 'PEDESTRIAN_HIT',
                description: `${this.id} atropelló al peatón ${nextCell.pedestrian.id} en (${nextPos.col},${nextPos.row})`,
                entityIds: [this.id, nextCell.pedestrian.id],
            });
            nextCell.pedestrian.state = 'hit';
        }

        // ─── Move ───
        this._moveTo(grid, nextPos.col, nextPos.row);

        // ─── Check if arrived at target parking spot ───
        if (
            this.state === VehicleState.SEARCHING &&
            this.targetSpot &&
            this.col === this.targetSpot.col &&
            this.row === this.targetSpot.row
        ) {
            // Decide if bad parking based on driver type
            const badParkChance =
                this.driverType === DriverType.AGGRESSIVE
                    ? params.badDriverProbability * 2
                    : this.driverType === DriverType.DISTRACTED
                        ? params.badDriverProbability * 1.5
                        : params.badDriverProbability * 0.3;

            if (rng() < badParkChance) {
                this.badParking = true;
                events.push({
                    type: 'PARK_BAD',
                    description: `${this.id} (${this.driverType}) se estacionó mal en cajón #${grid.get(this.col, this.row)?.spotId || '?'}`,
                });
            } else {
                events.push({
                    type: 'PARK_SUCCESS',
                    description: `${this.id} estacionado correctamente en cajón #${grid.get(this.col, this.row)?.spotId || '?'}`,
                });
            }
            this.state = VehicleState.PARKING;
            this.waitTicks = 2; // parking animation
        }

        // ─── Check if reached exit ───
        if (nextCell && nextCell.type === CellType.EXIT) {
            events.push({
                type: 'VEHICLE_EXIT',
                description: `${this.id} salió del estacionamiento`,
            });
            this.state = VehicleState.EXITING; // will be removed by Simulation
        }

        return events;
    }

    /**
     * Decide the next cell to move to.
     */
    _decideNextPosition(grid, rng, params) {
        // If searching and have a target, navigate toward it
        if (this.state === VehicleState.SEARCHING && this.targetSpot) {
            return this._navigateToward(grid, this.targetSpot, rng);
        }

        // If unparking or exiting, head toward nearest exit
        if (this.state === VehicleState.UNPARKING || this.state === VehicleState.EXITING) {
            const exits = grid.getExits();
            if (exits.length > 0) {
                // Find nearest exit
                let nearest = exits[0];
                let minDist = Math.abs(exits[0].col - this.col) + Math.abs(exits[0].row - this.row);
                for (const ex of exits) {
                    const d = Math.abs(ex.col - this.col) + Math.abs(ex.row - this.row);
                    if (d < minDist) { minDist = d; nearest = ex; }
                }
                return this._navigateToward(grid, { col: nearest.col, row: nearest.row }, rng);
            }
        }

        // Default: follow road direction
        return this._followRoad(grid, rng);
    }

    /**
   * Lane-aware navigation toward a target cell.
   * Priority: 1) follow road dir AND approach target, 2) follow road dir,
   * 3) directionless cell toward target, 4) any drivable cell.
   */
    _navigateToward(grid, target, rng) {
        const currentCell = grid.get(this.col, this.row);

        // Build all possible next positions with metadata
        const allMoves = [];
        for (const [dirName, delta] of Object.entries(DIR_DELTA)) {
            const nc = this.col + delta.dc;
            const nr = this.row + delta.dr;
            const cell = grid.get(nc, nr);
            if (!cell || !cell.isDrivable || cell.isOccupied || cell.blocked) continue;
            // Avoid going back to previous position
            if (nc === this.prevCol && nr === this.prevRow) continue;

            // Is this move along one of the current cell's allowed directions?
            const followsCurrentDir = currentCell && currentCell.directions.includes(dirName);
            // Does the destination cell allow this direction of travel?
            const destAllowsDir = cell.directions.length === 0 || cell.directions.includes(dirName);
            // Does this move reduce distance to target?
            const closerToTarget =
                Math.abs(nc - target.col) + Math.abs(nr - target.row) <
                Math.abs(this.col - target.col) + Math.abs(this.row - target.row);

            allMoves.push({
                col: nc,
                row: nr,
                followsCurrentDir,
                destAllowsDir,
                closerToTarget,
                isCompliant: followsCurrentDir && destAllowsDir,
            });
        }

        if (allMoves.length === 0) return null;

        // Priority 1: compliant + closer to target
        const p1 = allMoves.filter((m) => m.isCompliant && m.closerToTarget);
        if (p1.length > 0) return p1[Math.floor(rng() * p1.length)];

        // Priority 2: compliant (following traffic flow even if not closer)
        const p2 = allMoves.filter((m) => m.isCompliant);
        if (p2.length > 0) return p2[Math.floor(rng() * p2.length)];

        // Priority 3: dest allows dir + closer (e.g., entering a parking spot)
        const p3 = allMoves.filter((m) => m.destAllowsDir && m.closerToTarget);
        if (p3.length > 0) return p3[Math.floor(rng() * p3.length)];

        // Priority 4: dest allows dir
        const p4 = allMoves.filter((m) => m.destAllowsDir);
        if (p4.length > 0) return p4[Math.floor(rng() * p4.length)];

        // Priority 5: any move (this will be flagged as wrong-way)
        return allMoves[Math.floor(rng() * allMoves.length)];
    }

    /** Follow the current cell's allowed direction(s). */
    _followRoad(grid, rng) {
        const cell = grid.get(this.col, this.row);
        if (!cell || cell.directions.length === 0) {
            return this._navigateToward(grid, { col: this.col, row: this.row }, rng);
        }

        // Pick a random allowed direction
        const dir = cell.directions[Math.floor(rng() * cell.directions.length)];
        const delta = DIR_DELTA[dir];
        const nc = this.col + delta.dc;
        const nr = this.row + delta.dr;
        const nextCell = grid.get(nc, nr);
        if (nextCell && nextCell.isDrivable && !nextCell.isOccupied && !nextCell.blocked) {
            return { col: nc, row: nr };
        }
        return null;
    }

    /** Get the direction of movement from current pos to target pos. */
    _getMoveDirection(pos) {
        const dc = pos.col - this.col;
        const dr = pos.row - this.row;
        if (dc > 0) return Direction.RIGHT;
        if (dc < 0) return Direction.LEFT;
        if (dr > 0) return Direction.DOWN;
        if (dr < 0) return Direction.UP;
        return null;
    }

    /** Move the vehicle on the grid. */
    _moveTo(grid, col, row) {
        const oldCell = grid.get(this.col, this.row);
        if (oldCell && oldCell.vehicle === this) oldCell.vehicle = null;

        this.prevCol = this.col;
        this.prevRow = this.row;
        this.col = col;
        this.row = row;
        this.direction = this._getMoveDirection({ col, row }) || this.direction;

        const newCell = grid.get(col, row);
        if (newCell) newCell.vehicle = this;
    }
}
