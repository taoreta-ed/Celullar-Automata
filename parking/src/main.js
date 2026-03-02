import './styles.css';
import Simulation, { DEFAULT_PARAMS } from './simulation/Simulation.js';
import Renderer from './renderer/Renderer.js';
import { EventLabel, Severity } from './simulation/EventSystem.js';

// ─── DOM Refs ───
const canvas = document.getElementById('sim-canvas');
const btnStart = document.getElementById('btn-start');
const btnPause = document.getElementById('btn-pause');
const btnReset = document.getElementById('btn-reset');
const eventList = document.getElementById('event-list');

// Stat counters
const statTick = document.getElementById('stat-tick');
const statVehicles = document.getElementById('stat-vehicles');
const statPedestrians = document.getElementById('stat-pedestrians');
const statEvents = document.getElementById('stat-events');
const statSeed = document.getElementById('stat-seed');

// Summary counters
const sumParked = document.getElementById('sum-parked');
const sumBad = document.getElementById('sum-bad');
const sumCollisions = document.getElementById('sum-collisions');
const sumPedHit = document.getElementById('sum-ped-hit');

// ─── Slider bindings ───
const sliders = [
    { id: 'param-arrival', valId: 'val-arrival', key: 'arrivalRate' },
    { id: 'param-bad', valId: 'val-bad', key: 'badDriverProbability' },
    { id: 'param-ped', valId: 'val-ped', key: 'pedestrianDensity' },
    { id: 'param-collision', valId: 'val-collision', key: 'collisionProbability' },
    { id: 'param-block', valId: 'val-block', key: 'blockageProbability' },
    { id: 'param-cross', valId: 'val-cross', key: 'pedestrianCrossProbability' },
    { id: 'param-speed', valId: 'val-speed', key: 'speed', isInt: true },
];

for (const s of sliders) {
    const el = document.getElementById(s.id);
    const valEl = document.getElementById(s.valId);
    el.addEventListener('input', () => {
        const v = s.isInt ? parseInt(el.value) : parseFloat(el.value);
        valEl.textContent = el.value;
    });
}

function getParams() {
    const params = {};
    for (const s of sliders) {
        const el = document.getElementById(s.id);
        params[s.key] = s.isInt ? parseInt(el.value) : parseFloat(el.value);
    }
    // Max ticks
    const ticksEl = document.getElementById('param-ticks');
    params.maxTicks = parseInt(ticksEl.value) || 300;
    document.getElementById('val-ticks').textContent = params.maxTicks;

    // Seed
    const seedEl = document.getElementById('param-seed');
    const seedVal = seedEl.value.trim();
    params.seed = seedVal ? parseInt(seedVal) : null;
    document.getElementById('val-seed').textContent = seedVal || '—';

    return params;
}

// ─── State ───
let sim = null;
let renderer = null;
let rafId = null;

function renderLoop() {
    if (renderer) renderer.render();
    rafId = requestAnimationFrame(renderLoop);
}

function updateStats() {
    if (!sim) return;
    statTick.textContent = sim.tick;
    statVehicles.textContent = sim.vehicles.length;
    statPedestrians.textContent = sim.pedestrians.length;
    statEvents.textContent = sim.eventLog.events.length;

    // Summary
    const summary = sim.eventLog.summary();
    sumParked.textContent = (summary.PARK_SUCCESS || 0);
    sumBad.textContent = (summary.PARK_BAD || 0) + (summary.DOUBLE_PARK || 0);
    sumCollisions.textContent = (summary.COLLISION || 0);
    sumPedHit.textContent = (summary.PEDESTRIAN_HIT || 0);
}

function addEventToLog(ev) {
    const div = document.createElement('div');
    div.className = `event-item severity-${ev.severity}`;
    div.innerHTML = `
    <span class="tick">${ev.tick}</span>
    <span class="msg">${EventLabel[ev.type] || ev.type}: ${ev.description}</span>
  `;
    // Prepend (newest first)
    eventList.prepend(div);

    // Cap the displayed events at 200
    while (eventList.children.length > 200) {
        eventList.removeChild(eventList.lastChild);
    }

    // Flash on renderer for dangerous events
    if (renderer && ev.severity === Severity.DANGER) {
        renderer.flash(ev.position.col, ev.position.row, '#ff0040', 10);
    } else if (renderer && ev.severity === Severity.WARNING) {
        renderer.flash(ev.position.col, ev.position.row, '#ffaa26', 6);
    }
}

function setControlsDisabled(disabled) {
    for (const s of sliders) {
        if (s.key === 'speed') continue; // speed can be changed live
        document.getElementById(s.id).disabled = disabled;
    }
    document.getElementById('param-ticks').disabled = disabled;
    document.getElementById('param-seed').disabled = disabled;
}

// ─── Start ───
btnStart.addEventListener('click', () => {
    if (sim && sim.running) return;

    if (!sim || sim.finished) {
        // Fresh simulation
        const params = getParams();
        sim = new Simulation(params);
        renderer = new Renderer(canvas, sim);
        statSeed.textContent = sim.seed;

        // Clear event list
        eventList.innerHTML = '';

        // Subscribe to events
        sim.eventLog.onEvent(addEventToLog);
        sim.onTick(updateStats);
        sim.onFinish(() => {
            btnStart.textContent = '▶ Iniciar';
            btnStart.disabled = true;
            btnPause.disabled = true;
            setControlsDisabled(false);
        });

        // Start render loop
        if (rafId) cancelAnimationFrame(rafId);
        renderLoop();
    }

    sim.start();
    btnStart.textContent = '▶ Reanud.';
    btnStart.disabled = true;
    btnPause.disabled = false;
    btnReset.disabled = false;
    setControlsDisabled(true);
});

btnPause.addEventListener('click', () => {
    if (!sim) return;
    sim.pause();
    btnStart.textContent = '▶ Reanud.';
    btnStart.disabled = false;
    btnPause.disabled = true;
});

btnReset.addEventListener('click', () => {
    if (sim) sim.pause();
    if (rafId) { cancelAnimationFrame(rafId); rafId = null; }
    sim = null;
    renderer = null;

    // Clear canvas
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Reset UI
    eventList.innerHTML = '';
    statTick.textContent = '0';
    statVehicles.textContent = '0';
    statPedestrians.textContent = '0';
    statEvents.textContent = '0';
    statSeed.textContent = '—';
    sumParked.textContent = '0';
    sumBad.textContent = '0';
    sumCollisions.textContent = '0';
    sumPedHit.textContent = '0';

    btnStart.textContent = '▶ Iniciar';
    btnStart.disabled = false;
    btnPause.disabled = true;
    btnReset.disabled = true;
    setControlsDisabled(false);
});

// Live speed change
document.getElementById('param-speed').addEventListener('input', (e) => {
    const ms = parseInt(e.target.value);
    if (sim) sim.setSpeed(ms);
});

// ─── Initial render: show the empty lot ───
function showEmptyLot() {
    const params = getParams();
    const preview = new Simulation(params);
    const previewRenderer = new Renderer(canvas, preview);
    statSeed.textContent = '—';
    previewRenderer.render();
    // Keep renderer reference so resize events still work
    renderer = previewRenderer;
    sim = null;
}

window.addEventListener('load', showEmptyLot);

