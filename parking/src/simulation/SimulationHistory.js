/**
 * Manages simulation history using localStorage.
 * Each record stores params, seed, summary, and timestamp.
 */

const STORAGE_KEY = 'parking_sim_history';

/**
 * @typedef {object} SimulationRecord
 * @property {string} id         Unique ID (timestamp-based)
 * @property {number} timestamp  When the simulation finished
 * @property {number} seed       PRNG seed used
 * @property {object} params     Simulation parameters
 * @property {number} totalTicks Ticks completed
 * @property {object} eventSummary  Counts per event type
 * @property {number} totalEvents   Total events
 * @property {number} totalVehiclesCreated
 * @property {number} totalPedestriansCreated
 */

export default class SimulationHistory {
    /** Load all records from localStorage. */
    static getAll() {
        try {
            const raw = localStorage.getItem(STORAGE_KEY);
            return raw ? JSON.parse(raw) : [];
        } catch {
            return [];
        }
    }

    /** Save a simulation record. */
    static save(sim) {
        const records = SimulationHistory.getAll();
        const record = SimulationHistory._buildRecord(sim);
        records.unshift(record); // newest first

        // Cap at 100 records to avoid filling localStorage
        if (records.length > 100) records.length = 100;

        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(records));
        } catch (e) {
            console.warn('Could not save simulation to localStorage:', e);
        }
        return record;
    }

    /** Get a record by ID. */
    static getById(id) {
        return SimulationHistory.getAll().find((r) => r.id === id) || null;
    }

    /** Delete a record by ID. */
    static deleteById(id) {
        const records = SimulationHistory.getAll().filter((r) => r.id !== id);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(records));
    }

    /** Clear all records. */
    static clearAll() {
        localStorage.removeItem(STORAGE_KEY);
    }

    /** Export all records as a downloadable JSON file. */
    static exportAllAsJSON() {
        const records = SimulationHistory.getAll();
        SimulationHistory._downloadJSON(records, 'parking_sim_history.json');
    }

    /** Export a single simulation (full event log included). */
    static exportSimulationJSON(sim) {
        const data = {
            ...SimulationHistory._buildRecord(sim),
            events: sim.eventLog.events.map((e) => ({
                tick: e.tick,
                type: e.type,
                severity: e.severity,
                position: e.position,
                entityIds: e.entityIds,
                description: e.description,
            })),
        };
        SimulationHistory._downloadJSON(data, `sim_${sim.seed}_${Date.now()}.json`);
    }

    /** Build a summary record from a simulation instance. */
    static _buildRecord(sim) {
        const summary = sim.eventLog.summary();
        return {
            id: `sim_${Date.now()}_${sim.seed}`,
            timestamp: Date.now(),
            seed: sim.seed,
            params: { ...sim.params },
            totalTicks: sim.tick,
            eventSummary: summary,
            totalEvents: sim.eventLog.events.length,
            totalVehiclesCreated: sim.eventLog.events.filter(
                (e) => e.type === 'VEHICLE_ENTER'
            ).length,
            totalPedestriansCreated: sim.eventLog.events.filter(
                (e) => e.type === 'PEDESTRIAN_ENTER'
            ).length,
        };
    }

    /** Trigger a JSON file download in the browser. */
    static _downloadJSON(data, filename) {
        const blob = new Blob([JSON.stringify(data, null, 2)], {
            type: 'application/json',
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}
