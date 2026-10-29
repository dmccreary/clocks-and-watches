// Sync Interval Calculator - Chart.js
// CANVAS_HEIGHT: 500
// A sawtooth chart of clock error over 3 days. Error grows at the drift rate
// between syncs and drops back to zero at each NTP sync.
//   worst-case error (s) = ppm x sync interval (s) / 1,000,000
//   interval for a goal  = goal (s) x 1,000,000 / ppm

const HOURS_SHOWN = 72;   // 3 days
const GOAL = 1;           // seconds of error we are willing to accept
let chart;

function errorAfterHours(ppm, hours) {
    return ppm * hours * 3600 / 1e6;
}

// Sawtooth: rise for one interval, drop to zero (two points at the same x), repeat
function sawtooth(ppm, intervalH) {
    const pts = [];
    let t = 0;
    while (t < HOURS_SHOWN) {
        const next = Math.min(t + intervalH, HOURS_SHOWN);
        pts.push({ x: t, y: 0 });
        pts.push({ x: next, y: errorAfterHours(ppm, next - t) });
        t = next;
    }
    return pts;
}

function syncPoints(intervalH) {
    const pts = [];
    for (let t = 0; t <= HOURS_SHOWN + 1e-9; t += intervalH) pts.push({ x: t, y: 0 });
    return pts;
}

function fmt(n) {
    if (n >= 100) return n.toFixed(0);
    if (n >= 10) return n.toFixed(1);
    return n.toFixed(2);
}

function refresh() {
    const ppm = parseInt(document.getElementById('drift').value, 10);
    const intervalH = parseInt(document.getElementById('interval').value, 10);
    document.getElementById('drift-value').textContent = ppm;
    document.getElementById('interval-value').textContent = intervalH;

    const worst = errorAfterHours(ppm, intervalH);
    const neededH = GOAL * 1e6 / ppm / 3600;

    chart.data.datasets[0].data = sawtooth(ppm, intervalH);
    chart.data.datasets[0].label = 'Clock error (' + ppm + ' ppm)';
    chart.data.datasets[1].data = syncPoints(intervalH);
    chart.options.scales.y.suggestedMax = Math.max(worst, GOAL) * 1.15;
    chart.update('none');

    const ok = worst <= GOAL;
    document.getElementById('readout').innerHTML =
        '<span>Worst-case error: <strong>' + fmt(worst) + ' seconds</strong> ' +
        '<span class="' + (ok ? 'ok' : 'bad') + '">(' + (ok ? 'meets' : 'misses') + ' the 1 s goal)</span></span>' +
        '<span>Sync interval needed for 1 s accuracy: <strong>' + fmt(neededH) + ' hours</strong></span>';
}

document.addEventListener('DOMContentLoaded', function () {
    const narrow = window.innerWidth < 560;
    chart = new Chart(document.getElementById('chart'), {
        type: 'line',
        data: {
            datasets: [
                {
                    label: 'Clock error',
                    data: [],
                    borderColor: '#d55e00',
                    backgroundColor: 'rgba(213, 94, 0, 0.12)',
                    fill: true,
                    borderWidth: 3,
                    pointRadius: 0,
                    pointHoverRadius: 5,
                    tension: 0
                },
                {
                    label: 'NTP sync',
                    data: [],
                    showLine: false,
                    pointStyle: 'triangle',
                    pointRadius: 8,
                    pointHoverRadius: 9,
                    borderColor: '#0072b2',
                    backgroundColor: '#0072b2'
                },
                {
                    label: '1 s goal',
                    data: [{ x: 0, y: GOAL }, { x: HOURS_SHOWN, y: GOAL }],
                    borderColor: 'green',
                    backgroundColor: 'green',
                    borderDash: [6, 4],
                    borderWidth: 2,
                    pointRadius: 0,
                    pointHoverRadius: 0
                }
            ]
        },
        options: {
            responsive: true,
            layout: { padding: { right: 10 } },
            maintainAspectRatio: false,
            animation: false,
            interaction: { mode: 'nearest', intersect: false },
            scales: {
                x: {
                    type: 'linear', min: 0, max: HOURS_SHOWN,
                    ticks: { stepSize: 12, font: { size: 13 } },
                    title: { display: true, text: 'Time (hours)', font: { size: 15 } }
                },
                y: {
                    beginAtZero: true,
                    ticks: { font: { size: 13 } },
                    title: { display: true, text: 'Clock error (seconds)', font: { size: 15 } }
                }
            },
            plugins: {
                legend: { position: 'top', labels: { font: { size: narrow ? 12 : 14 }, boxWidth: narrow ? 12 : 18 } },
                tooltip: {
                    filter: item => item.dataset.label !== '1 s goal',
                    callbacks: {
                        title: items => items.length ? 'Hour ' + items[0].parsed.x.toFixed(1) : '',
                        label: item => item.datasetIndex === 1 ? 'Sync: error reset to 0 s'
                            : 'Error: ' + fmt(item.parsed.y) + ' s'
                    }
                }
            }
        }
    });

    const preset = document.getElementById('preset');
    const drift = document.getElementById('drift');
    preset.addEventListener('change', () => {
        if (preset.value !== 'custom') drift.value = preset.value;
        refresh();
    });
    drift.addEventListener('input', () => {
        const match = [...preset.options].find(o => o.value === drift.value);
        preset.value = match ? match.value : 'custom';
        refresh();
    });
    document.getElementById('interval').addEventListener('input', refresh);
    refresh();
});
