// ─── Event Types ───
export const EventType = {
    PARK_SUCCESS: 'PARK_SUCCESS',
    PARK_BAD: 'PARK_BAD',
    DOUBLE_PARK: 'DOUBLE_PARK',
    COLLISION: 'COLLISION',
    PEDESTRIAN_CROSS: 'PEDESTRIAN_CROSS',
    PEDESTRIAN_HIT: 'PEDESTRIAN_HIT',
    ENTRANCE_BLOCKED: 'ENTRANCE_BLOCKED',
    EXIT_BLOCKED: 'EXIT_BLOCKED',
    WRONG_WAY: 'WRONG_WAY',
    VEHICLE_ENTER: 'VEHICLE_ENTER',
    VEHICLE_EXIT: 'VEHICLE_EXIT',
    PEDESTRIAN_ENTER: 'PEDESTRIAN_ENTER',
    PEDESTRIAN_EXIT: 'PEDESTRIAN_EXIT',
};

// Severity levels
export const Severity = {
    INFO: 'info',
    WARNING: 'warning',
    DANGER: 'danger',
};

const SEVERITY_MAP = {
    [EventType.PARK_SUCCESS]: Severity.INFO,
    [EventType.VEHICLE_ENTER]: Severity.INFO,
    [EventType.VEHICLE_EXIT]: Severity.INFO,
    [EventType.PEDESTRIAN_ENTER]: Severity.INFO,
    [EventType.PEDESTRIAN_EXIT]: Severity.INFO,
    [EventType.PEDESTRIAN_CROSS]: Severity.WARNING,
    [EventType.PARK_BAD]: Severity.WARNING,
    [EventType.DOUBLE_PARK]: Severity.WARNING,
    [EventType.WRONG_WAY]: Severity.WARNING,
    [EventType.ENTRANCE_BLOCKED]: Severity.WARNING,
    [EventType.EXIT_BLOCKED]: Severity.WARNING,
    [EventType.COLLISION]: Severity.DANGER,
    [EventType.PEDESTRIAN_HIT]: Severity.DANGER,
};

// Labels in Spanish for the UI
export const EventLabel = {
    [EventType.PARK_SUCCESS]: '🅿️ Estacionamiento correcto',
    [EventType.PARK_BAD]: '⚠️ Mal estacionado',
    [EventType.DOUBLE_PARK]: '⚠️ Doble estacionamiento',
    [EventType.COLLISION]: '💥 Colisión',
    [EventType.PEDESTRIAN_CROSS]: '🚶 Peatón cruzando calle',
    [EventType.PEDESTRIAN_HIT]: '🚨 Peatón atropellado',
    [EventType.ENTRANCE_BLOCKED]: '🚧 Entrada bloqueada',
    [EventType.EXIT_BLOCKED]: '🚧 Salida bloqueada',
    [EventType.WRONG_WAY]: '⛔ Dirección equivocada',
    [EventType.VEHICLE_ENTER]: '🚗 Vehículo ingresó',
    [EventType.VEHICLE_EXIT]: '🚗 Vehículo salió',
    [EventType.PEDESTRIAN_ENTER]: '🚶 Peatón ingresó',
    [EventType.PEDESTRIAN_EXIT]: '🚶 Peatón salió',
};

/**
 * A single simulation event.
 */
export class SimEvent {
    /**
     * @param {number} tick
     * @param {string} type   One of EventType values.
     * @param {{col:number, row:number}} position
     * @param {string[]} entityIds
     * @param {string} description
     */
    constructor(tick, type, position, entityIds, description) {
        this.tick = tick;
        this.type = type;
        this.severity = SEVERITY_MAP[type] || Severity.INFO;
        this.position = position;
        this.entityIds = entityIds;
        this.description = description;
        this.timestamp = Date.now();
    }
}

/**
 * Accumulates events and allows querying / exporting.
 */
export default class EventLog {
    constructor() {
        /** @type {SimEvent[]} */
        this.events = [];
        /** @type {((ev: SimEvent) => void)[]} */
        this._listeners = [];
    }

    /** Subscribe to new events. */
    onEvent(fn) {
        this._listeners.push(fn);
    }

    /** Log a new event and notify listeners. */
    log(tick, type, position, entityIds, description) {
        const ev = new SimEvent(tick, type, position, entityIds, description);
        this.events.push(ev);
        for (const fn of this._listeners) fn(ev);
        return ev;
    }

    /** Get events filtered by type(s). */
    filter(types) {
        const set = new Set(Array.isArray(types) ? types : [types]);
        return this.events.filter((e) => set.has(e.type));
    }

    /** Summary counts. */
    summary() {
        const counts = {};
        for (const e of this.events) {
            counts[e.type] = (counts[e.type] || 0) + 1;
        }
        return counts;
    }

    /** Export to a plain object. */
    toJSON() {
        return {
            total: this.events.length,
            summary: this.summary(),
            events: this.events,
        };
    }

    /** Reset the log. */
    clear() {
        this.events = [];
    }
}
