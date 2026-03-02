import Grid, { CellType } from './Grid.js';
import Vehicle, { DriverType, VehicleState } from './Vehicle.js';
import Pedestrian, { PedestrianState } from './Pedestrian.js';
import EventLog, { EventType } from './EventSystem.js';

/**
 * Simple seeded PRNG (mulberry32).
 */
function mulberry32(seed) {
    let s = seed | 0;
    return () => {
        s = (s + 0x6d2b79f5) | 0;
        let t = Math.imul(s ^ (s >>> 15), 1 | s);
        t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
}

/** Default parameters */
export const DEFAULT_PARAMS = {
    arrivalRate: 0.3,           // probability a new car arrives each tick
    badDriverProbability: 0.15, // base probability of bad behaviour
    pedestrianDensity: 0.15,    // probability a new pedestrian appears each tick
    collisionProbability: 0.05, // probability of collision when conflict occurs
    blockageProbability: 0.02,  // probability an entrance/exit gets blocked
    pedestrianCrossProbability: 0.1, // probability a pedestrian crosses a road
    maxTicks: 300,              // simulation length
    seed: null,                 // null = random seed
    speed: 200,                 // ms between ticks
};

/**
 * Main simulation controller.
 */
export default class Simulation {
    /**
     * @param {object} params  Merged with DEFAULT_PARAMS.
     */
    constructor(params = {}) {
        this.params = { ...DEFAULT_PARAMS, ...params };
        this.tick = 0;
        this.running = false;
        this.finished = false;

        // Seed
        const seed = this.params.seed ?? Math.floor(Math.random() * 2 ** 32);
        this.seed = seed;
        this.rng = mulberry32(seed);

        // Reset entity counters
        Vehicle.resetIdCounter();
        Pedestrian.resetIdCounter();

        // Core objects
        this.grid = Grid.createDefault();
        this.eventLog = new EventLog();

        /** @type {Vehicle[]} */
        this.vehicles = [];
        /** @type {Pedestrian[]} */
        this.pedestrians = [];

        /** Interval id for the run loop */
        this._interval = null;

        /** @type {((sim: Simulation) => void)[]} */
        this._tickListeners = [];
        /** @type {((sim: Simulation) => void)[]} */
        this._finishListeners = [];
    }

    // ─── Lifecycle ───

    onTick(fn) { this._tickListeners.push(fn); }
    onFinish(fn) { this._finishListeners.push(fn); }

    start() {
        if (this.running || this.finished) return;
        this.running = true;
        this._interval = setInterval(() => this._step(), this.params.speed);
    }

    pause() {
        this.running = false;
        if (this._interval) { clearInterval(this._interval); this._interval = null; }
    }

    reset(params = {}) {
        this.pause();
        Object.assign(this, new Simulation({ ...this.params, ...params }));
    }

    setSpeed(ms) {
        this.params.speed = ms;
        if (this.running) {
            clearInterval(this._interval);
            this._interval = setInterval(() => this._step(), ms);
        }
    }

    // ─── Main step ───

    _step() {
        if (!this.running || this.finished) return;

        this.tick++;

        // 1. Possibly spawn new vehicle
        this._maybeSpawnVehicle();

        // 2. Possibly spawn new pedestrian
        this._maybeSpawnPedestrian();

        // 3. Possibly block/unblock an entrance or exit
        this._maybeToggleBlockage();

        // 4. Move all vehicles
        for (const v of this.vehicles) {
            const evts = v.tick(this.grid, this.rng, this.params);
            for (const e of evts) {
                this.eventLog.log(
                    this.tick,
                    EventType[e.type] || e.type,
                    { col: v.col, row: v.row },
                    e.entityIds || [v.id],
                    e.description
                );
            }
        }

        // 5. Move all pedestrians
        for (const p of this.pedestrians) {
            const evts = p.tick(this.grid, this.rng, this.params);
            for (const e of evts) {
                this.eventLog.log(
                    this.tick,
                    EventType[e.type] || e.type,
                    { col: p.col, row: p.row },
                    e.entityIds || [p.id],
                    e.description
                );
            }
        }

        // 6. Cleanup: remove exited vehicles / pedestrians
        this.vehicles = this.vehicles.filter((v) => {
            if (v.state === VehicleState.EXITING) {
                const cell = this.grid.get(v.col, v.row);
                if (cell && cell.vehicle === v) cell.vehicle = null;
                return false;
            }
            return true;
        });
        this.pedestrians = this.pedestrians.filter((p) => {
            if (p.state === PedestrianState.EXITED) {
                const cell = this.grid.get(p.col, p.row);
                if (cell && cell.pedestrian === p) cell.pedestrian = null;
                return false;
            }
            return true;
        });

        // 7. Notify listeners
        for (const fn of this._tickListeners) fn(this);

        // 8. Check end condition
        if (this.tick >= this.params.maxTicks) {
            this.finished = true;
            this.pause();
            for (const fn of this._finishListeners) fn(this);
        }
    }

    _maybeSpawnVehicle() {
        if (this.rng() > this.params.arrivalRate) return;

        const entrances = this.grid.getEntrances();
        if (entrances.length === 0) return;

        // Pick a random entrance
        const ent = entrances[Math.floor(this.rng() * entrances.length)];
        const cell = ent.cell;
        if (cell.isOccupied) return; // entrance already busy

        // Determine driver type
        const r = this.rng();
        let driverType = DriverType.NORMAL;
        if (r < this.params.badDriverProbability * 0.5) driverType = DriverType.AGGRESSIVE;
        else if (r < this.params.badDriverProbability) driverType = DriverType.DISTRACTED;

        const dir = cell.directions[0] || 'right';
        const vehicle = new Vehicle(ent.col, ent.row, dir, driverType);
        cell.vehicle = vehicle;

        // Assign a parking spot
        vehicle.assignSpot(this.grid, this.rng);

        this.vehicles.push(vehicle);
        this.eventLog.log(
            this.tick,
            EventType.VEHICLE_ENTER,
            { col: ent.col, row: ent.row },
            [vehicle.id],
            `${vehicle.id} (${driverType}) ingresó al estacionamiento`
        );
    }

    _maybeSpawnPedestrian() {
        if (this.rng() > this.params.pedestrianDensity) return;

        // Spawn on a random sidewalk cell
        const sidewalks = this.grid.findCells(CellType.SIDEWALK);
        if (sidewalks.length === 0) return;

        const sw = sidewalks[Math.floor(this.rng() * sidewalks.length)];
        if (sw.cell.pedestrian) return; // already occupied

        const ped = new Pedestrian(sw.col, sw.row);
        sw.cell.pedestrian = ped;
        this.pedestrians.push(ped);

        this.eventLog.log(
            this.tick,
            EventType.PEDESTRIAN_ENTER,
            { col: sw.col, row: sw.row },
            [ped.id],
            `${ped.id} ingresó al estacionamiento`
        );
    }

    _maybeToggleBlockage() {
        if (this.rng() > this.params.blockageProbability) return;

        // Find all entrances and exits
        const all = [
            ...this.grid.findCells(CellType.ENTRANCE),
            ...this.grid.findCells(CellType.EXIT),
        ];
        if (all.length === 0) return;

        const target = all[Math.floor(this.rng() * all.length)];
        target.cell.blocked = !target.cell.blocked;

        if (target.cell.blocked) {
            const evType =
                target.cell.type === CellType.ENTRANCE
                    ? EventType.ENTRANCE_BLOCKED
                    : EventType.EXIT_BLOCKED;
            this.eventLog.log(
                this.tick,
                evType,
                { col: target.col, row: target.row },
                [],
                `${target.cell.type === CellType.ENTRANCE ? 'Entrada' : 'Salida'} en (${target.col},${target.row}) bloqueada`
            );
        }
    }
}
