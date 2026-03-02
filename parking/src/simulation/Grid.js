// ─── Cell Types ───
export const CellType = {
    ROAD: 'road',
    PARKING_SPOT: 'parking_spot',
    SIDEWALK: 'sidewalk',
    ENTRANCE: 'entrance',
    EXIT: 'exit',
    OBSTACLE: 'obstacle',
    EMPTY: 'empty',
    CROSSWALK: 'crosswalk',
};

// Road directions a vehicle can travel on a given cell
export const Direction = {
    UP: 'up',
    DOWN: 'down',
    LEFT: 'left',
    RIGHT: 'right',
};

/**
 * Represents a single cell in the parking lot grid.
 */
class Cell {
    constructor(type = CellType.EMPTY, directions = []) {
        this.type = type;
        /** @type {string[]} Allowed travel directions for vehicles */
        this.directions = directions;
        /** @type {import('./Vehicle.js').default|null} */
        this.vehicle = null;
        /** @type {import('./Pedestrian.js').default|null} */
        this.pedestrian = null;
        /** Is this parking spot occupied? */
        this.parked = false;
        /** Is this entrance/exit currently blocked? */
        this.blocked = false;
        /** Parking spot id (for labelling) */
        this.spotId = null;
        /** Reserved type: false, 'disability' */
        this.reserved = false;
        /** Is this a crosswalk cell? */
        this.crosswalk = false;
    }

    get isOccupied() {
        return this.vehicle !== null;
    }

    get isWalkable() {
        return this.type === CellType.SIDEWALK || this.type === CellType.ROAD;
    }

    get isDrivable() {
        return (
            this.type === CellType.ROAD ||
            this.type === CellType.ENTRANCE ||
            this.type === CellType.EXIT ||
            this.type === CellType.PARKING_SPOT ||
            this.type === CellType.CROSSWALK
        );
    }

    get isWalkablePed() {
        return (
            this.type === CellType.SIDEWALK ||
            this.type === CellType.CROSSWALK ||
            this.type === CellType.ROAD
        );
    }
}

/**
 * The 2-D grid that represents the parking lot layout.
 */
export default class Grid {
    /**
     * @param {number} cols
     * @param {number} rows
     */
    constructor(cols, rows) {
        this.cols = cols;
        this.rows = rows;
        /** @type {Cell[][]} row-major */
        this.cells = [];
        for (let r = 0; r < rows; r++) {
            const row = [];
            for (let c = 0; c < cols; c++) {
                row.push(new Cell());
            }
            this.cells.push(row);
        }
    }

    /** Get cell at (col, row). Returns null if out of bounds. */
    get(col, row) {
        if (col < 0 || col >= this.cols || row < 0 || row >= this.rows) return null;
        return this.cells[row][col];
    }

    /** Set a cell's type and allowed directions. */
    set(col, row, type, directions = []) {
        const cell = this.get(col, row);
        if (cell) {
            cell.type = type;
            cell.directions = directions;
        }
    }

    /**
     * Build a default parking lot layout.
     *
     * Layout (30 × 22):
     *  - Row 0: top wall (obstacle)
     *  - Row 1: sidewalk strip
     *  - Rows 2-3: driving lane (→)
     *  - Rows 4-5: parking spots (top row, facing down)
     *  - Rows 6-7: driving lane (←)
     *  - Rows 8-9: parking spots
     *  - Rows 10-11: driving lane (→)
     *  - Rows 12-13: parking spots
     *  - Rows 14-15: driving lane (←)
     *  - Rows 16-17: parking spots
     *  - Rows 18-19: driving lane (→)
     *  - Row 20: sidewalk strip
     *  - Row 21: bottom wall (obstacle)
     *
     *  Columns 0,29: walls (obstacles)
     *  Column 1: entrance (row 2-3), exit (row 18-19)
     *  Column 28: exit (row 2-3), entrance (row 18-19)
     *  Columns 1 & 28: vertical connector roads
     */
    static createDefault() {
        const cols = 30;
        const rows = 22;
        const grid = new Grid(cols, rows);

        // Helper to fill a range
        const fill = (c1, c2, r1, r2, type, dirs = []) => {
            for (let r = r1; r <= r2; r++)
                for (let c = c1; c <= c2; c++)
                    grid.set(c, r, type, dirs);
        };

        // ─── Walls / borders ───
        fill(0, cols - 1, 0, 0, CellType.OBSTACLE);       // top wall
        fill(0, cols - 1, rows - 1, rows - 1, CellType.OBSTACLE); // bottom wall
        fill(0, 0, 0, rows - 1, CellType.OBSTACLE);        // left wall
        fill(cols - 1, cols - 1, 0, rows - 1, CellType.OBSTACLE); // right wall

        // ─── Sidewalks ───
        fill(1, cols - 2, 1, 1, CellType.SIDEWALK);
        fill(1, cols - 2, rows - 2, rows - 2, CellType.SIDEWALK);

        // ─── Define lanes and parking rows ───
        const laneRows = [
            { rows: [2, 3], dir: Direction.RIGHT },
            { rows: [6, 7], dir: Direction.LEFT },
            { rows: [10, 11], dir: Direction.RIGHT },
            { rows: [14, 15], dir: Direction.LEFT },
            { rows: [18, 19], dir: Direction.RIGHT },
        ];

        const parkingRows = [
            { rows: [4, 5] },
            { rows: [8, 9] },
            { rows: [12, 13] },
            { rows: [16, 17] },
        ];

        // Fill lane roads
        for (const lane of laneRows) {
            for (const r of lane.rows) {
                fill(2, cols - 3, r, r, CellType.ROAD, [lane.dir]);
            }
        }

        // Fill parking spots
        let spotCounter = 1;
        for (const pr of parkingRows) {
            for (let c = 3; c <= cols - 4; c += 2) {
                for (const r of pr.rows) {
                    grid.set(c, r, CellType.PARKING_SPOT);
                    const cell = grid.get(c, r);
                    cell.spotId = spotCounter;
                }
                spotCounter++;
                // Road between pairs for manoeuvring
                for (const r of pr.rows) {
                    const roadCell = grid.get(c + 1, r);
                    if (roadCell && roadCell.type === CellType.EMPTY) {
                        grid.set(c + 1, r, CellType.ROAD, [Direction.UP, Direction.DOWN]);
                    }
                }
            }
        }

        // ─── Vertical connector roads on columns 1 and cols-2 ───
        for (let r = 2; r <= rows - 3; r++) {
            grid.set(1, r, CellType.ROAD, [Direction.UP, Direction.DOWN]);
            grid.set(cols - 2, r, CellType.ROAD, [Direction.UP, Direction.DOWN]);
        }

        // ─── Entrances & Exits ───
        // Left side: entrance at top, exit at bottom
        grid.set(0, 2, CellType.ENTRANCE, [Direction.RIGHT]);
        grid.set(0, 3, CellType.ENTRANCE, [Direction.RIGHT]);
        // Right side: exit at top, entrance at bottom
        grid.set(cols - 1, 2, CellType.EXIT, [Direction.RIGHT]);
        grid.set(cols - 1, 3, CellType.EXIT, [Direction.RIGHT]);
        grid.set(cols - 1, 18, CellType.ENTRANCE, [Direction.LEFT]);
        grid.set(cols - 1, 19, CellType.ENTRANCE, [Direction.LEFT]);
        grid.set(0, 18, CellType.EXIT, [Direction.LEFT]);
        grid.set(0, 19, CellType.EXIT, [Direction.LEFT]);

        // ─── Reserved disability spots (♿) near entrances ───
        // First 2 spots in the first parking row (near top-left entrance)
        const reservedSpotIds = [1, 2];
        for (const pr of [parkingRows[0]]) {
            let count = 0;
            for (let c = 3; c <= cols - 4 && count < 2; c += 2) {
                for (const r of pr.rows) {
                    const cell = grid.get(c, r);
                    if (cell && cell.type === CellType.PARKING_SPOT) {
                        cell.reserved = 'disability';
                    }
                }
                count++;
            }
        }
        // Last 2 spots in the last parking row (near bottom-right entrance)
        for (const pr of [parkingRows[3]]) {
            let count = 0;
            for (let c = cols - 4; c >= 3 && count < 2; c -= 2) {
                for (const r of pr.rows) {
                    const cell = grid.get(c, r);
                    if (cell && cell.type === CellType.PARKING_SPOT) {
                        cell.reserved = 'disability';
                    }
                }
                count++;
            }
        }

        // ─── Crosswalks ───
        // Vertical crosswalks connecting sidewalks to lanes at a few column positions
        const crosswalkCols = [5, 15, 25];
        for (const cc of crosswalkCols) {
            // Top sidewalk → first lane
            grid.set(cc, 1, CellType.CROSSWALK, [Direction.UP, Direction.DOWN]);
            const topCell = grid.get(cc, 1);
            if (topCell) topCell.crosswalk = true;
            // Bottom sidewalk → last lane
            grid.set(cc, rows - 2, CellType.CROSSWALK, [Direction.UP, Direction.DOWN]);
            const botCell = grid.get(cc, rows - 2);
            if (botCell) botCell.crosswalk = true;
        }

        return grid;
    }

    /** Get all cells of a given type. Returns {col, row, cell}[]. */
    findCells(type) {
        const results = [];
        for (let r = 0; r < this.rows; r++) {
            for (let c = 0; c < this.cols; c++) {
                if (this.cells[r][c].type === type) {
                    results.push({ col: c, row: r, cell: this.cells[r][c] });
                }
            }
        }
        return results;
    }

    /** Get all free parking spots (optionally excluding reserved). */
    getFreeParkingSpots(includeReserved = true) {
        return this.findCells(CellType.PARKING_SPOT).filter(
            (s) => !s.cell.parked && !s.cell.isOccupied && (includeReserved || !s.cell.reserved)
        );
    }

    /** Get all free reserved disability spots. */
    getFreeReservedSpots() {
        return this.findCells(CellType.PARKING_SPOT).filter(
            (s) => !s.cell.parked && !s.cell.isOccupied && s.cell.reserved === 'disability'
        );
    }

    /** Get crosswalk cells. */
    getCrosswalks() {
        return this.findCells(CellType.CROSSWALK);
    }

    /** Get entrance cells. */
    getEntrances() {
        return this.findCells(CellType.ENTRANCE).filter((e) => !e.cell.blocked);
    }

    /** Get exit cells. */
    getExits() {
        return this.findCells(CellType.EXIT).filter((e) => !e.cell.blocked);
    }
}
