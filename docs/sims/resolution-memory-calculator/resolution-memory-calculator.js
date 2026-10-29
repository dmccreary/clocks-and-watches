// Resolution and Memory Calculator - Chart.js
// CANVAS_HEIGHT: 470
// Framebuffer size = width x height x bits per pixel / 8 bytes.
// Compared with the Raspberry Pi Pico's 264 KB of RAM (red line) and a practical
// 200 KB limit (yellow line) that leaves room for MicroPython and your program.
// KB here means 1,024 bytes.

const DISPLAYS = [
  { chip: 'SSD1306', name: 'SSD1306 OLED', w: 128, h: 64 },
  { chip: 'ST7735', name: 'ST7735 TFT', w: 160, h: 128 },
  { chip: 'GC9A01', name: 'GC9A01 round', w: 240, h: 240 },
  { chip: 'ILI9341', name: 'ILI9341 TFT', w: 320, h: 240 },
  { chip: 'GC9B72', name: 'GC9B72 watch', w: 360, h: 360 }
];
const RAM_KB = 264;
const PRACTICAL_KB = 200;
const COLORS = { good: '#2e8b57', tight: '#e69500', bad: '#c0392b' };

let chart;
let rows = [];

function barColor(kb) {
  if (kb > RAM_KB) return COLORS.bad;
  if (kb >= PRACTICAL_KB) return COLORS.tight;
  return COLORS.good;
}

function fmtKB(kb) {
  return kb < 10 ? kb.toFixed(2) : kb.toFixed(1);
}

function buildRows() {
  const bpp = Number(document.getElementById('bpp').value);
  const cw = Math.round(Number(document.getElementById('cw').value));
  const ch = Math.round(Number(document.getElementById('ch').value));
  const narrow = window.innerWidth < 560;
  rows = DISPLAYS.map(d => ({ ...d }));
  if (cw > 0 && ch > 0 && cw <= 2000 && ch <= 2000) rows.push({ chip: 'Custom', name: 'Custom', w: cw, h: ch, custom: true });
  rows.forEach(r => {
    r.bpp = bpp;
    r.bytes = r.w * r.h * bpp / 8;
    r.kb = r.bytes / 1024;
    r.label = narrow ? [r.chip, r.w + 'x' + r.h] : [r.name, r.w + ' x ' + r.h];
  });

  const custom = rows.find(r => r.custom);
  let msg;
  if (!custom) {
    msg = 'Type a width and height to add a custom bar.';
  } else {
    const verdict = custom.kb > RAM_KB ? '<span style="color:#c0392b"><b>does not fit</b></span> in the 264 KB of RAM.'
      : custom.kb >= PRACTICAL_KB ? '<span style="color:#b36b00"><b>barely fits</b></span>: almost no RAM left for your program.'
        : '<span style="color:#2e8b57"><b>fits</b></span> with room to spare.';
    msg = 'Custom ' + custom.w + ' x ' + custom.h + ' at ' + bpp + ' bpp = ' + custom.bytes.toLocaleString() +
      ' bytes = <b>' + fmtKB(custom.kb) + ' KB</b>, which ' + verdict;
  }
  document.getElementById('readout').innerHTML = msg;
  return rows;
}

// red and yellow limit lines plus a value label above each bar
const limitLines = {
  id: 'limitLines',
  afterDatasetsDraw(c) {
    const ctx = c.ctx;
    const { left, right } = c.chartArea;
    const lines = [[RAM_KB, COLORS.bad, '264 KB total RAM'], [PRACTICAL_KB, '#d4a000', '200 KB practical limit']];
    ctx.save();
    lines.forEach(([v, col, text]) => {
      const y = c.scales.y.getPixelForValue(v);
      ctx.strokeStyle = col;
      ctx.lineWidth = 2;
      ctx.setLineDash(v === RAM_KB ? [] : [6, 4]);
      ctx.beginPath();
      ctx.moveTo(left, y);
      ctx.lineTo(right, y);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.fillStyle = col;
      ctx.font = 'bold 12px Arial';
      ctx.textAlign = 'left';
      ctx.fillText(text, left + 6, y - 4);
    });
    // value labels
    const meta = c.getDatasetMeta(0);
    ctx.fillStyle = '#222';
    ctx.font = '12px Arial';
    ctx.textAlign = 'center';
    meta.data.forEach((bar, i) => {
      ctx.fillText(fmtKB(rows[i].kb) + ' KB', bar.x, bar.y - 5);
    });
    ctx.restore();
  }
};

function update() {
  const r = buildRows();
  const maxKB = Math.max(...r.map(x => x.kb));
  chart.data.labels = r.map(x => x.label);
  chart.data.datasets[0].data = r.map(x => x.kb);
  chart.data.datasets[0].backgroundColor = r.map(x => barColor(x.kb));
  chart.options.scales.y.max = Math.max(300, Math.ceil(maxKB * 1.12 / 50) * 50);
  chart.update();
}

document.addEventListener('DOMContentLoaded', function () {
  const r = buildRows();
  chart = new Chart(document.getElementById('chart'), {
    type: 'bar',
    data: {
      labels: r.map(x => x.label),
      datasets: [{
        label: 'Framebuffer size (KB)',
        data: r.map(x => x.kb),
        backgroundColor: r.map(x => barColor(x.kb)),
        borderColor: '#333',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 300 },
      layout: { padding: { top: 8, right: 10 } },
      scales: {
        y: {
          min: 0,
          max: Math.max(300, Math.ceil(Math.max(...r.map(x => x.kb)) * 1.12 / 50) * 50),
          title: { display: true, text: 'Framebuffer size (KB)', font: { size: 14 } },
          ticks: { font: { size: 13 } }
        },
        x: { ticks: { font: { size: 12 }, maxRotation: 0, autoSkip: false } }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            title: items => rows[items[0].dataIndex].name + ' (' + rows[items[0].dataIndex].w + ' x ' + rows[items[0].dataIndex].h + ')',
            label: function (item) {
              const x = rows[item.dataIndex];
              return [
                x.w + ' x ' + x.h + ' x ' + x.bpp + ' / 8 = ' + x.bytes.toLocaleString() + ' bytes',
                '= ' + fmtKB(x.kb) + ' KB (1 KB = 1,024 bytes)',
                'Uses ' + Math.round(100 * x.kb / RAM_KB) + '% of the Pico\'s 264 KB RAM'
              ];
            }
          }
        }
      }
    },
    plugins: [limitLines]
  });

  document.getElementById('bpp').addEventListener('change', update);
  document.getElementById('cw').addEventListener('input', update);
  document.getElementById('ch').addEventListener('input', update);
  window.addEventListener('resize', update);
});
