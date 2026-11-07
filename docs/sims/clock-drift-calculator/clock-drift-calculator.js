// Drift Calculator - Chart.js
// CANVAS_HEIGHT: 530
// Accumulated drift (seconds) versus elapsed days for three clock sources,
// plus an optional custom ppm value. drift = ppm x elapsed seconds / 1,000,000.
// A dotted line marks "1 minute off" so students can compare how long each
// source lasts before it needs to be reset.

const SECONDS_PER_DAY = 86400;
const MINUTE = 60; // seconds of error that count as "1 minute off"

const SOURCES = [
    { name: 'Pico crystal', ppm: 30, color: '#d55e00' },
    { name: 'DS1307', ppm: 20, color: '#0072b2' },
    { name: 'DS3231', ppm: 2, color: '#009e73' }
];
const CUSTOM_COLOR = '#9b59b6';

let chart;

// Drift in seconds after `days` for a clock that is off by `ppm`
function driftSeconds(ppm, days) {
    return ppm * days * SECONDS_PER_DAY / 1e6;
}

// Days until the drift reaches one minute
function daysUntilMinute(ppm) {
    return MINUTE * 1e6 / (ppm * SECONDS_PER_DAY);
}

// 101 points from day 0 to the chosen number of days (the line is straight,
// but extra points make hover tooltips useful anywhere along it)
function linePoints(ppm, days) {
    const pts = [];
    for (let i = 0; i <= 100; i++) {
        const d = days * i / 100;
        pts.push({ x: d, y: driftSeconds(ppm, d) });
    }
    return pts;
}

function fmt(n) {
    if (n >= 100) return n.toFixed(0);
    if (n >= 10) return n.toFixed(1);
    return n.toFixed(2);
}

function buildDatasets(days, customPpm) {
    const sets = SOURCES.map(s => ({
        label: s.name + ' (' + s.ppm + ' ppm)',
        data: linePoints(s.ppm, days),
        borderColor: s.color,
        backgroundColor: s.color,
        borderWidth: 3,
        pointRadius: 0,
        pointHoverRadius: 5,
        tension: 0
    }));
    if (customPpm > 0) {
        sets.push({
            label: 'Custom (' + customPpm + ' ppm)',
            data: linePoints(customPpm, days),
            borderColor: CUSTOM_COLOR,
            backgroundColor: CUSTOM_COLOR,
            borderWidth: 3,
            borderDash: [8, 4],
            pointRadius: 0,
            pointHoverRadius: 5,
            tension: 0
        });
    }
    // Horizontal "1 minute off" reference line
    sets.push({
        label: '1 minute off',
        data: [{ x: 0, y: MINUTE }, { x: days, y: MINUTE }],
        borderColor: 'gray',
        backgroundColor: 'gray',
        borderWidth: 2,
        borderDash: [3, 4],
        pointRadius: 0,
        pointHoverRadius: 0,
        tension: 0
    });
    return sets;
}

function updateReadout(days, customPpm) {
    const rows = SOURCES.map(s => ({ name: s.name, ppm: s.ppm, color: s.color }));
    if (customPpm > 0) rows.push({ name: 'Custom', ppm: customPpm, color: CUSTOM_COLOR });
    let html = '<table><tr><th>Source</th><th>Drift after ' + days + ' days</th><th>Days until 1 minute off</th></tr>';
    for (const r of rows) {
        const drift = driftSeconds(r.ppm, days);
        const until = daysUntilMinute(r.ppm);
        const passed = drift >= MINUTE ? ' (passed)' : '';
        html += '<tr><td><span class="chip" style="background:' + r.color + '"></span>' + r.name +
            ' (' + r.ppm + ' ppm)</td><td>' + fmt(drift) + ' s</td><td>' + fmt(until) + ' days' + passed + '</td></tr>';
    }
    html += '</table>';
    document.getElementById('readout').innerHTML = html;
}

function refresh() {
    const days = parseInt(document.getElementById('days').value, 10);
    const customPpm = parseFloat(document.getElementById('custom').value) || 0;
    document.getElementById('days-value').textContent = days;

    // Remember which lines the student hid with the legend
    const hidden = {};
    chart.data.datasets.forEach((ds, i) => { hidden[ds.label.split(' (')[0]] = !chart.isDatasetVisible(i); });

    chart.data.datasets = buildDatasets(days, customPpm);
    chart.data.datasets.forEach(ds => { ds.hidden = !!hidden[ds.label.split(' (')[0]]; });
    chart.options.scales.x.max = days;
    // Always keep the 1-minute line in view
    const maxDrift = Math.max(...SOURCES.map(s => driftSeconds(s.ppm, days)), customPpm > 0 ? driftSeconds(customPpm, days) : 0);
    chart.options.scales.y.suggestedMax = Math.max(maxDrift, MINUTE) * 1.08;
    chart.update('none');
    updateReadout(days, customPpm);
}

document.addEventListener('DOMContentLoaded', function () {
    const days = 60;
    chart = new Chart(document.getElementById('chart'), {
        type: 'line',
        data: { datasets: buildDatasets(days, 0) },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false,
            interaction: { mode: 'nearest', axis: 'x', intersect: false },
            scales: {
                x: {
                    type: 'linear', min: 0, max: days,
                    title: { display: true, text: 'Elapsed days', font: { size: 15 } },
                    ticks: { font: { size: 13 } }
                },
                y: {
                    beginAtZero: true,
                    suggestedMax: 160,
                    title: { display: true, text: 'Accumulated drift (seconds)', font: { size: 15 } },
                    ticks: { font: { size: 13 } }
                }
            },
            plugins: {
                legend: { position: 'top', labels: { font: { size: window.innerWidth < 560 ? 12 : 14 }, boxWidth: window.innerWidth < 560 ? 12 : 18 } },
                tooltip: {
                    filter: item => item.dataset.label !== '1 minute off',
                    callbacks: {
                        title: items => items.length ? 'Day ' + items[0].parsed.x.toFixed(1) : '',
                        label: item => item.dataset.label + ': ' + fmt(item.parsed.y) + ' s'
                    }
                }
            }
        }
    });

    document.getElementById('days').addEventListener('input', refresh);
    document.getElementById('custom').addEventListener('input', refresh);
    refresh();
});
