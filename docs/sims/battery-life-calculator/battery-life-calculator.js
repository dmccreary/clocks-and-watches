// Battery Life Calculator - Chart.js
// CANVAS_HEIGHT: 530
// Students choose the parts in a clock, the backlight brightness, the fraction of time asleep
// and the battery size. A stacked bar shows each part's average current, and a second chart
// compares the runtime "Before" (a saved design) with "Now".
// Runtime (hours) = capacity (mAh) x 0.8 / average current (mA). Static: no animation.

// Each part: awake current (mA) and current while the Pico is asleep (mA)
const PARTS = [
  { id: 'pico', name: 'Pico running MicroPython', awake: 25, asleep: 1.5, on: true, color: 'steelblue' },
  { id: 'wifi', name: 'WiFi radio on (Pico W)', awake: 60, asleep: 0, on: false, color: 'mediumpurple' },
  { id: 'oled', name: 'Small OLED display', awake: 15, asleep: 0, on: false, color: 'teal' },
  { id: 'tft', name: 'Color TFT backlight', awake: 60, asleep: 0, on: true, color: 'darkorange', backlight: true },
  { id: 'rtc', name: 'DS3231 RTC', awake: 0.2, asleep: 0.2, on: true, color: 'seagreen' },
  { id: 'buzz', name: 'Piezo buzzer (sounding)', awake: 15, asleep: 0, on: false, color: 'crimson' },
  { id: 'pixel', name: 'NeoPixel (1 LED, half white)', awake: 30, asleep: 0, on: false, color: 'goldenrod' }
];
const BACKLIGHT_MAX = 80;   // mA at 100% brightness

let stackChart, compareChart;
let before = null;          // { hours, label }

function readState() {
  const bl = Number(document.getElementById('backlight').value);
  const sl = Number(document.getElementById('sleep').value) / 100;
  const cap = Number(document.getElementById('battery').value);
  const rows = [];
  let total = 0;
  for (const p of PARTS) {
    const on = document.getElementById('cb-' + p.id).checked;
    const awake = p.backlight ? BACKLIGHT_MAX * bl / 100 : p.awake;
    const avg = on ? awake * (1 - sl) + p.asleep * sl : 0;
    rows.push({ p, on, awake, avg });
    total += avg;
  }
  const hours = total > 0 ? cap * 0.8 / total : Infinity;
  return { bl, sl, cap, rows, total, hours };
}

function hoursText(h) {
  if (!isFinite(h)) return 'forever (no load)';
  if (h >= 48) return h.toFixed(0) + ' hours (' + (h / 24).toFixed(1) + ' days)';
  return h.toFixed(1) + ' hours';
}

function update() {
  const s = readState();
  document.getElementById('blVal').textContent = s.bl + '% (' + (BACKLIGHT_MAX * s.bl / 100).toFixed(0) + ' mA)';
  document.getElementById('slVal').textContent = Math.round(s.sl * 100) + '%';
  document.getElementById('runtime').textContent = 'Estimated runtime: ' + hoursText(s.hours);
  document.getElementById('total').innerHTML = 'Average current: <b>' + s.total.toFixed(1) + ' mA</b> &nbsp; (' +
    s.cap + ' mAh × 0.8 ÷ ' + s.total.toFixed(1) + ' mA)';

  // name the biggest consumer so students know where to look for savings
  const on = s.rows.filter(r => r.avg > 0).sort((a, b) => b.avg - a.avg);
  document.getElementById('hint').textContent = on.length ?
    'Biggest draw: ' + on[0].p.name + ' (' + on[0].avg.toFixed(1) + ' mA, ' +
    Math.round(100 * on[0].avg / s.total) + '% of the total)' : 'Add a part to start.';

  // stacked bar: one dataset per part
  stackChart.data.datasets = s.rows.filter(r => r.on).map(r => ({
    label: r.p.name.replace(' (Pico W)', '').replace(' running MicroPython', ''),
    data: [Number(r.avg.toFixed(2))],
    backgroundColor: r.p.color,
    borderColor: 'white',
    borderWidth: 1
  }));
  stackChart.update();

  // before / now comparison
  const nowH = isFinite(s.hours) ? s.hours : 0;
  compareChart.data.datasets[0].data = [before.hours, nowH];
  compareChart.data.datasets[0].backgroundColor = ['silver', nowH >= before.hours ? 'seagreen' : 'crimson'];
  compareChart.update();
}

function saveBefore() {
  const s = readState();
  before = { hours: isFinite(s.hours) ? s.hours : 0 };
  update();
}

function resetAll() {
  for (const p of PARTS) document.getElementById('cb-' + p.id).checked = p.on;
  document.getElementById('backlight').value = 75;
  document.getElementById('sleep').value = 0;
  document.getElementById('battery').value = '500';
  saveBefore();
}

document.addEventListener('DOMContentLoaded', function () {
  // build the part checkboxes
  const box = document.getElementById('parts');
  for (const p of PARTS) {
    const div = document.createElement('div');
    div.className = 'part';
    const ma = p.backlight ? '0-80 mA' : (p.awake + ' mA');
    div.innerHTML = '<input type="checkbox" id="cb-' + p.id + '"' + (p.on ? ' checked' : '') + '>' +
      '<label for="cb-' + p.id + '">' + p.name + '</label><span class="ma">' + ma + '</span>';
    box.appendChild(div);
    div.querySelector('input').addEventListener('change', update);
  }
  document.getElementById('backlight').addEventListener('input', update);
  document.getElementById('sleep').addEventListener('input', update);
  document.getElementById('battery').addEventListener('change', update);
  document.getElementById('saveBtn').addEventListener('click', saveBefore);
  document.getElementById('resetBtn').addEventListener('click', resetAll);

  Chart.defaults.font.size = 13;
  Chart.defaults.animation = false;

  stackChart = new Chart(document.getElementById('stackChart'), {
    type: 'bar',
    data: { labels: ['Average'], datasets: [] },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: { display: true, text: 'Average current by part (mA)' },
        legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 12 } } }
      },
      scales: {
        x: { stacked: true, beginAtZero: true, title: { display: false } },
        y: { stacked: true, display: false }
      }
    }
  });

  compareChart = new Chart(document.getElementById('compareChart'), {
    type: 'bar',
    data: {
      labels: ['Before', 'Now'],
      datasets: [{ label: 'Runtime (hours)', data: [0, 0], backgroundColor: ['silver', 'seagreen'] }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: { display: true, text: 'Runtime before and after your changes' },
        legend: { display: false },
        tooltip: { callbacks: { label: (c) => hoursText(c.parsed.y) } }
      },
      scales: {
        y: { beginAtZero: true, title: { display: true, text: 'Runtime (hours)' } }
      }
    }
  });

  resetAll();
});
