// Bus Speed Race - Chart.js
// CANVAS_HEIGHT: 420
// Seconds needed to send one full frame over UART, I2C and SPI.
//   UART: bytes x 10 bits / baud   (start + 8 data + stop bits)
//   I2C:  bytes x 9 bits / clock   (8 data bits + 1 ACK bit)
//   SPI:  bytes x 8 bits / clock
// Bars turn green at 20 frames per second (0.05 s per frame) or faster.

const DISPLAYS = {
  oled: { name: '128x64 mono OLED', w: 128, h: 64, bpp: 1 },
  gc9a01: { name: '240x240 color', w: 240, h: 240, bpp: 16 },
  ili9341: { name: '320x240 color', w: 320, h: 240, bpp: 16 }
};
const UART_BAUD = 115200;
const GOOD_FPS = 20;
const COLORS = { good: '#2e8b57', ok: '#e69500', slow: '#c0392b' };

let chart;
let rows = [];   // computed results for the tooltip

function fmtTime(t) {
  if (t < 1) return (t * 1000).toFixed(t < 0.01 ? 2 : 1) + ' ms';
  return t.toFixed(2) + ' s';
}

function fmtHz(hz) {
  if (hz >= 1e6) return (hz / 1e6).toLocaleString() + ' MHz';
  return (hz / 1e3).toLocaleString() + ' kHz';
}

function compute() {
  const d = DISPLAYS[document.getElementById('display').value];
  const bytes = d.w * d.h * d.bpp / 8;
  const i2cHz = Number(document.getElementById('i2c').value) * 1000;
  const spiHz = Number(document.getElementById('spi').value) * 1e6;
  const narrow = window.innerWidth < 560;
  rows = [
    { bus: 'UART', label: narrow ? 'UART' : 'UART at 115,200 baud', bits: 10, rate: UART_BAUD,
      rateText: '115,200 baud', t: bytes * 10 / UART_BAUD },
    { bus: 'I2C', label: narrow ? 'I2C' : 'I2C at ' + fmtHz(i2cHz), bits: 9, rate: i2cHz,
      rateText: i2cHz.toLocaleString() + ' Hz', t: bytes * 9 / i2cHz },
    { bus: 'SPI', label: narrow ? 'SPI' : 'SPI at ' + fmtHz(spiHz), bits: 8, rate: spiHz,
      rateText: spiHz.toLocaleString() + ' Hz', t: bytes * 8 / spiHz }
  ];
  rows.forEach(r => { r.bytes = bytes; r.fps = 1 / r.t; });
  document.getElementById('i2cVal').textContent = fmtHz(i2cHz);
  document.getElementById('spiVal').textContent = fmtHz(spiHz);
  document.getElementById('readout').innerHTML = '<b>Max frames per second</b> for the ' + d.name + ': ' +
    rows.map(r => r.bus + ' <b>' + (r.fps < 10 ? r.fps.toFixed(2) : r.fps.toFixed(1)) + '</b>').join(' &nbsp;|&nbsp; ');
  return rows;
}

function barColor(fps) {
  if (fps >= GOOD_FPS) return COLORS.good;
  if (fps >= 1) return COLORS.ok;
  return COLORS.slow;
}

// draws the dashed "20 fps" line at 0.05 s
const targetLine = {
  id: 'targetLine',
  afterDatasetsDraw(c) {
    const x = c.scales.x.getPixelForValue(1 / GOOD_FPS);
    const { top, bottom } = c.chartArea;
    const ctx = c.ctx;
    ctx.save();
    ctx.strokeStyle = COLORS.good;
    ctx.setLineDash([5, 4]);
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(x, top);
    ctx.lineTo(x, bottom);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = COLORS.good;
    ctx.font = 'bold 13px Arial';
    ctx.textAlign = 'left';
    ctx.fillText('20 fps (50 ms)', x + 4, top + 12);
    ctx.restore();
  }
};

function update() {
  const r = compute();
  chart.data.labels = r.map(x => x.label);
  chart.data.datasets[0].data = r.map(x => x.t);
  chart.data.datasets[0].backgroundColor = r.map(x => barColor(x.fps));
  chart.update();
}

document.addEventListener('DOMContentLoaded', function () {
  const r = compute();
  const ctx = document.getElementById('chart');
  chart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: r.map(x => x.label),
      datasets: [{
        label: 'Seconds per frame',
        data: r.map(x => x.t),
        backgroundColor: r.map(x => barColor(x.fps)),
        borderColor: '#333',
        borderWidth: 1,
        barPercentage: 0.7
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 300 },
      layout: { padding: { right: 16, left: 4, top: 4 } },
      scales: {
        x: {
          type: 'logarithmic',
          min: 0.0001,
          max: 100,
          title: { display: true, text: 'Time to send one frame (log scale, less is faster)', font: { size: 14 } },
          // keep only the powers of ten so the labels stay horizontal
          afterBuildTicks: function (axis) {
            axis.ticks = [-4, -3, -2, -1, 0, 1, 2].map(p => ({ value: Math.pow(10, p) }));
          },
          ticks: {
            font: { size: 13 },
            maxRotation: 0,
            callback: function (v) {
              const names = { '-4': '0.1 ms', '-3': '1 ms', '-2': '10 ms', '-1': '100 ms', '0': '1 s', '1': '10 s', '2': '100 s' };
              return names[String(Math.round(Math.log10(v)))] || '';
            }
          }
        },
        y: { ticks: { font: { size: 14 } } }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            title: items => rows[items[0].dataIndex].bus,
            label: function (item) {
              const x = rows[item.dataIndex];
              return [
                'Time: ' + fmtTime(x.t) + ' per frame',
                '= ' + x.bytes.toLocaleString() + ' bytes x ' + x.bits + ' bits / ' + x.rateText,
                'Max ' + (x.fps < 10 ? x.fps.toFixed(2) : x.fps.toFixed(1)) + ' frames per second'
              ];
            }
          }
        }
      }
    },
    plugins: [targetLine]
  });

  document.getElementById('display').addEventListener('change', update);
  document.getElementById('i2c').addEventListener('input', update);
  document.getElementById('spi').addEventListener('input', update);
  window.addEventListener('resize', update);
});
