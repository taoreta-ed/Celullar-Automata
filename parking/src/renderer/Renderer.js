import { CellType } from '../simulation/Grid.js';
import { VehicleState } from '../simulation/Vehicle.js';
import { PedestrianState } from '../simulation/Pedestrian.js';

// ─── Color Palette ───
const CELL_COLORS = {
    [CellType.EMPTY]: '#1a1a2e',
    [CellType.ROAD]: '#2d2d44',
    [CellType.PARKING_SPOT]: '#16213e',
    [CellType.SIDEWALK]: '#4a4a5a',
    [CellType.ENTRANCE]: '#0f3d3e',
    [CellType.EXIT]: '#3d0f0f',
    [CellType.OBSTACLE]: '#0f0f1a',
    [CellType.CROSSWALK]: '#2d2d44',
};

const CELL_COLORS_BLOCKED = {
    [CellType.ENTRANCE]: '#5c1a1a',
    [CellType.EXIT]: '#5c1a1a',
};

const VEHICLE_STATE_COLORS = {
    [VehicleState.CRASHED]: '#ff0040',
};

const SPOT_FREE_COLOR = '#1e3a5f';
const SPOT_OCCUPIED_COLOR = '#3b1a1a';
const SPOT_BORDER_COLOR = '#3a5a8a';

/**
 * Canvas-based top-down renderer for the parking simulation.
 */
export default class Renderer {
    /**
     * @param {HTMLCanvasElement} canvas
     * @param {import('../simulation/Simulation.js').default} simulation
     */
    constructor(canvas, simulation) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.sim = simulation;
        this.cellSize = 0;
        this.offsetX = 0;
        this.offsetY = 0;
        /** Flash effects for events */
        this.flashes = []; // {col, row, color, remaining}
        this._resize();
        window.addEventListener('resize', () => this._resize());
    }

    /** Recalculate cell size to fit. */
    _resize() {
        const container = this.canvas.parentElement;
        if (!container) return;
        const w = container.clientWidth;
        const h = container.clientHeight;
        this.canvas.width = w;
        this.canvas.height = h;

        const grid = this.sim.grid;
        const cellW = w / grid.cols;
        const cellH = h / grid.rows;
        this.cellSize = Math.floor(Math.min(cellW, cellH));
        this.offsetX = Math.floor((w - this.cellSize * grid.cols) / 2);
        this.offsetY = Math.floor((h - this.cellSize * grid.rows) / 2);
    }

    /** Add a flash effect at a position. */
    flash(col, row, color = '#ff0040', duration = 8) {
        this.flashes.push({ col, row, color, remaining: duration });
    }

    /** Full render of one frame. */
    render() {
        const ctx = this.ctx;
        const cs = this.cellSize;
        const grid = this.sim.grid;

        // Clear
        ctx.fillStyle = '#0a0a15';
        ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // ─── Draw cells ───
        for (let r = 0; r < grid.rows; r++) {
            for (let c = 0; c < grid.cols; c++) {
                const cell = grid.cells[r][c];
                const x = this.offsetX + c * cs;
                const y = this.offsetY + r * cs;

                // Base color
                let color = CELL_COLORS[cell.type] || '#1a1a2e';

                // Special cases
                if (cell.type === CellType.PARKING_SPOT) {
                    color = cell.parked ? SPOT_OCCUPIED_COLOR : SPOT_FREE_COLOR;
                }
                if (cell.blocked && CELL_COLORS_BLOCKED[cell.type]) {
                    color = CELL_COLORS_BLOCKED[cell.type];
                }

                ctx.fillStyle = color;
                ctx.fillRect(x, y, cs, cs);

                // Parking spot border
                if (cell.type === CellType.PARKING_SPOT) {
                    ctx.strokeStyle = SPOT_BORDER_COLOR;
                    ctx.lineWidth = 1;
                    ctx.strokeRect(x + 0.5, y + 0.5, cs - 1, cs - 1);
                }

                // Spot ID label
                if (cell.type === CellType.PARKING_SPOT && cell.spotId && cs > 14) {
                    ctx.fillStyle = '#ffffff30';
                    ctx.font = `${Math.max(8, cs * 0.35)}px monospace`;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';

                    // If reserved, draw ♿ instead of or next to ID
                    if (cell.reserved === 'disability') {
                        ctx.fillStyle = '#4cc9f0';
                        ctx.fillText('♿', x + cs / 2, y + cs / 2);
                    } else {
                        ctx.fillText(cell.spotId, x + cs / 2, y + cs / 2);
                    }
                }

                // Crosswalk stripes
                if (cell.type === CellType.CROSSWALK && cs > 10) {
                    ctx.fillStyle = '#ffffff40';
                    const stripeW = cs * 0.15;
                    const gap = cs * 0.15;
                    for (let sy = y + gap; sy < y + cs - gap; sy += stripeW + gap) {
                        ctx.fillRect(x + cs * 0.2, sy, cs * 0.6, stripeW);
                    }
                }

                // Entrance / Exit labels
                if ((cell.type === CellType.ENTRANCE || cell.type === CellType.EXIT) && cs > 14) {
                    ctx.fillStyle = cell.blocked ? '#ff4040' : '#ffffff60';
                    ctx.font = `bold ${Math.max(8, cs * 0.3)}px sans-serif`;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    const label = cell.type === CellType.ENTRANCE ? 'IN' : 'OUT';
                    ctx.fillText(label, x + cs / 2, y + cs / 2);
                    if (cell.blocked) {
                        ctx.fillStyle = '#ff4040';
                        ctx.fillText('🚧', x + cs / 2, y + cs / 2);
                    }
                }

                // Road direction arrows
                if (cell.type === CellType.ROAD && cell.directions.length > 0 && cs > 18) {
                    ctx.fillStyle = '#ffffff15';
                    ctx.font = `${Math.max(8, cs * 0.4)}px sans-serif`;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    const arrows = {
                        up: '↑', down: '↓', left: '←', right: '→',
                    };
                    const label = cell.directions.map((d) => arrows[d] || '').join('');
                    ctx.fillText(label, x + cs / 2, y + cs / 2);
                }

                // Grid lines
                ctx.strokeStyle = '#ffffff08';
                ctx.lineWidth = 0.5;
                ctx.strokeRect(x, y, cs, cs);
            }
        }

        // ─── Draw vehicles ───
        for (const v of this.sim.vehicles) {
            const x = this.offsetX + v.col * cs;
            const y = this.offsetY + v.row * cs;
            const pad = cs * 0.1;

            // Vehicle body
            const vColor = VEHICLE_STATE_COLORS[v.state] || v.color;
            ctx.fillStyle = vColor;

            // Rounded rect
            const rx = x + pad;
            const ry = y + pad;
            const rw = cs - pad * 2;
            const rh = cs - pad * 2;
            const radius = cs * 0.15;
            ctx.beginPath();
            ctx.moveTo(rx + radius, ry);
            ctx.lineTo(rx + rw - radius, ry);
            ctx.quadraticCurveTo(rx + rw, ry, rx + rw, ry + radius);
            ctx.lineTo(rx + rw, ry + rh - radius);
            ctx.quadraticCurveTo(rx + rw, ry + rh, rx + rw - radius, ry + rh);
            ctx.lineTo(rx + radius, ry + rh);
            ctx.quadraticCurveTo(rx, ry + rh, rx, ry + rh - radius);
            ctx.lineTo(rx, ry + radius);
            ctx.quadraticCurveTo(rx, ry, rx + radius, ry);
            ctx.closePath();
            ctx.fill();

            // Direction indicator (windshield)
            ctx.fillStyle = '#00000050';
            const ws = cs * 0.2;
            switch (v.direction) {
                case 'up':
                    ctx.fillRect(rx + rw * 0.2, ry, rw * 0.6, ws);
                    break;
                case 'down':
                    ctx.fillRect(rx + rw * 0.2, ry + rh - ws, rw * 0.6, ws);
                    break;
                case 'left':
                    ctx.fillRect(rx, ry + rh * 0.2, ws, rh * 0.6);
                    break;
                case 'right':
                    ctx.fillRect(rx + rw - ws, ry + rh * 0.2, ws, rh * 0.6);
                    break;
            }

            // Bad parking indicator
            if (v.badParking && (v.state === VehicleState.PARKING || v.state === VehicleState.PARKED)) {
                ctx.strokeStyle = '#ffaa00';
                ctx.lineWidth = 2;
                ctx.setLineDash([3, 2]);
                ctx.strokeRect(rx - 1, ry - 1, rw + 2, rh + 2);
                ctx.setLineDash([]);
            }

            // Crashed indicator
            if (v.state === VehicleState.CRASHED) {
                ctx.fillStyle = '#ff0040';
                ctx.font = `${cs * 0.5}px sans-serif`;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText('💥', x + cs / 2, y + cs / 2);
            }
        }

        // ─── Draw pedestrians ───
        for (const p of this.sim.pedestrians) {
            const x = this.offsetX + p.col * cs + cs / 2;
            const y = this.offsetY + p.row * cs + cs / 2;
            const r = cs * 0.2;

            ctx.beginPath();
            ctx.arc(x, y, r, 0, Math.PI * 2);
            ctx.fillStyle = p.state === PedestrianState.HIT ? '#ff0040' : p.color;
            ctx.fill();
            ctx.strokeStyle = '#ffffff40';
            ctx.lineWidth = 1;
            ctx.stroke();

            if (p.state === PedestrianState.CROSSING || p.state === PedestrianState.USING_CROSSWALK) {
                ctx.beginPath();
                ctx.arc(x, y, r + 3, 0, Math.PI * 2);
                ctx.strokeStyle = p.state === PedestrianState.USING_CROSSWALK ? '#4cc9f080' : '#ffaa0080';
                ctx.lineWidth = 1.5;
                ctx.stroke();
            }

            if (p.state === PedestrianState.WAITING) {
                const pulse = (Math.sin(Date.now() / 150) + 1) / 2;
                ctx.beginPath();
                ctx.arc(x, y, r + 4 * pulse, 0, Math.PI * 2);
                ctx.strokeStyle = `rgba(255, 255, 255, ${0.5 * (1 - pulse)})`;
                ctx.lineWidth = 2;
                ctx.stroke();
            }

            if (p.state === PedestrianState.GOING_TO_VEHICLE) {
                ctx.setLineDash([2, 2]);
                ctx.beginPath();
                ctx.arc(x, y, r + 2, 0, Math.PI * 2);
                ctx.strokeStyle = '#c9a96e';
                ctx.lineWidth = 1;
                ctx.stroke();
                ctx.setLineDash([]);
            }
        }

        // ─── Draw flashes ───
        this.flashes = this.flashes.filter((f) => {
            f.remaining--;
            const alpha = f.remaining / 8;
            const x = this.offsetX + f.col * cs;
            const y = this.offsetY + f.row * cs;
            ctx.fillStyle = f.color + Math.floor(alpha * 80).toString(16).padStart(2, '0');
            ctx.fillRect(x - cs * 0.5, y - cs * 0.5, cs * 2, cs * 2);
            return f.remaining > 0;
        });
    }
}
