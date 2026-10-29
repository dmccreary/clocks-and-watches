// Sampling Rate Explorer MicroSim
// CANVAS_HEIGHT: 545
// Samples a sine wave at a chosen rate, rebuilds it as a staircase (what a DAC outputs),
// and shows the Nyquist limit, aliasing, and the data rate in bytes per second.
// Bloom level: Analyzing - students compare fidelity and memory cost as the rate changes.
// Static, slider-driven display: nothing animates, so there is no Start button.

let canvasWidth = 400;
let drawHeight = 430;
let controlHeight = 115;
let canvasHeight = drawHeight + controlHeight;
let margin = 25;
let sliderLeftMargin = 250;
let defaultTextSize = 16;

let freqSlider, rateSlider, bitSelect, heardCheckbox;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));

  // Row 1: wave frequency
  freqSlider = createSlider(100, 4000, 440, 10);
  freqSlider.position(sliderLeftMargin, drawHeight + 8);
  freqSlider.size(canvasWidth - sliderLeftMargin - margin);

  // Row 2: sampling rate
  rateSlider = createSlider(2000, 44100, 8000, 100);
  rateSlider.position(sliderLeftMargin, drawHeight + 43);
  rateSlider.size(canvasWidth - sliderLeftMargin - margin);

  // Row 3: bit depth and the "heard wave" overlay
  bitSelect = createSelect();
  bitSelect.option('16-bit samples', '16');
  bitSelect.option('8-bit samples', '8');
  bitSelect.selected('16');
  bitSelect.position(110, drawHeight + 78);

  heardCheckbox = createCheckbox('Show the wave you hear (after filtering)', false);
  heardCheckbox.position(260, drawHeight + 80);

  describe('A sine wave is sampled at the chosen sampling rate. Orange dots mark each sample and an orange staircase shows the rebuilt DAC output. Readouts give the Nyquist limit, the heard frequency and the data rate. If the frequency goes above half the sampling rate, a warning explains that the sound aliases to a lower, wrong pitch.');
}

function draw() {
  updateCanvasSize();

  // Drawing and control regions
  stroke('silver');
  strokeWeight(1);
  fill('aliceblue');
  rect(0, 0, canvasWidth, drawHeight);
  fill('white');
  rect(0, drawHeight, canvasWidth, controlHeight);

  const f = freqSlider.value();
  const fs = rateSlider.value();
  const bits = int(bitSelect.value());
  const nyquist = fs / 2;
  const aliasing = f > nyquist;

  // Heard (aliased) frequency and its sign
  const r = f % fs;
  let fHeard = r;
  let heardSign = 1;
  if (r > fs / 2) {
    fHeard = fs - r;
    heardSign = -1;
  }

  // Choose a time window: 3 cycles of the wave, longer when aliasing so the slow alias shows
  let T = 3 / f;
  if (aliasing) {
    const aliasWindow = fHeard > 0 ? 1.5 / fHeard : 60 / fs;
    T = max(T, min(aliasWindow, 60 / fs));
  }

  // Plot geometry
  const px0 = 70;
  const px1 = canvasWidth - 20;
  const py0 = 64;
  const py1 = 258;
  const pmid = (py0 + py1) / 2;
  const amp = (py1 - py0) / 2 - 12;

  // Title
  noStroke();
  fill('black');
  textAlign(CENTER, TOP);
  textSize(22);
  text('Sampling Rate Explorer', canvasWidth / 2, 8);

  // Plot background and axes
  stroke('silver');
  fill('white');
  rect(px0, py0, px1 - px0, py1 - py0);
  stroke(210);
  line(px0, pmid, px1, pmid);
  line(px0, pmid - amp, px1, pmid - amp);
  line(px0, pmid + amp, px1, pmid + amp);

  noStroke();
  fill('black');
  textSize(14);
  textAlign(RIGHT, CENTER);
  text('+1', px0 - 6, pmid - amp);
  text('0', px0 - 6, pmid);
  text('-1', px0 - 6, pmid + amp);
  push();
  translate(18, pmid);
  rotate(-HALF_PI);
  textAlign(CENTER, CENTER);
  text('Amplitude', 0, 0);
  pop();

  // Time axis ticks (milliseconds)
  textAlign(CENTER, TOP);
  const tMs = T * 1000;
  const step = niceStep(tMs / 5);
  for (let t = 0; t <= tMs + 1e-9; t += step) {
    const x = map(t, 0, tMs, px0, px1);
    stroke('silver');
    line(x, py1, x, py1 + 4);
    noStroke();
    text(formatMs(t, step), x, py1 + 6);
  }
  text('Time (ms)', (px0 + px1) / 2, py1 + 22);

  const toX = (t) => map(t, 0, T, px0, px1);
  const toY = (v) => pmid - v * amp;

  // 1. Original smooth wave
  noFill();
  stroke('steelblue');
  strokeWeight(2);
  beginShape();
  const nPix = int(px1 - px0) * 2;
  for (let i = 0; i <= nPix; i++) {
    const t = (i / nPix) * T;
    vertex(toX(t), toY(sin(TWO_PI * f * t)));
  }
  endShape();

  // 2. Samples and staircase (zero-order hold, like a simple DAC)
  const levels = pow(2, bits - 1) - 1;
  const nSamples = floor(T * fs) + 1;
  const spacing = (px1 - px0) / (T * fs);
  stroke('darkorange');
  strokeWeight(2);
  noFill();
  beginShape();
  for (let n = 0; n < nSamples; n++) {
    const t = n / fs;
    const v = round(sin(TWO_PI * f * t) * levels) / levels;
    const xa = toX(t);
    const xb = min(toX((n + 1) / fs), px1);
    vertex(xa, toY(v));
    vertex(xb, toY(v));
  }
  endShape();

  if (spacing >= 4) {
    noStroke();
    fill('darkorange');
    const d = constrain(spacing * 0.6, 4, 9);
    for (let n = 0; n < nSamples; n++) {
      const t = n / fs;
      const v = round(sin(TWO_PI * f * t) * levels) / levels;
      circle(toX(t), toY(v), d);
    }
  }

  // 3. Heard wave: what a smoothing filter rebuilds from the samples
  if (heardCheckbox.checked()) {
    stroke('crimson');
    strokeWeight(2.5);
    drawingContext.setLineDash([8, 6]);
    noFill();
    beginShape();
    for (let i = 0; i <= nPix; i++) {
      const t = (i / nPix) * T;
      vertex(toX(t), toY(heardSign * sin(TWO_PI * fHeard * t)));
    }
    endShape();
    drawingContext.setLineDash([]);
  }
  strokeWeight(1);

  // Legend along the top of the plot
  drawLegend(px0, 36);

  // ---------- Readout panel ----------
  const panelY = 296;
  const panelH = drawHeight - panelY - 10;
  const colW = (canvasWidth - 30) / 2;

  stroke('silver');
  fill(255, 255, 255, 230);
  rect(10, panelY, colW - 5, panelH, 10);
  rect(15 + colW, panelY, colW - 5, panelH, 10);

  noStroke();
  fill('black');
  textAlign(LEFT, TOP);
  textSize(16);
  const lx = 22;
  text('Nyquist limit: ' + fmt(nyquist) + ' Hz', lx, panelY + 10);
  text('Samples per cycle: ' + nf(fs / f, 1, 1), lx, panelY + 34);
  text('Levels per sample: ' + fmt(pow(2, bits)), lx, panelY + 58);
  if (aliasing) {
    fill('crimson');
    text('You hear: ' + fmt(round(fHeard)) + ' Hz (wrong!)', lx, panelY + 82);
  } else {
    fill('darkgreen');
    text('You hear: ' + fmt(f) + ' Hz (correct)', lx, panelY + 82);
  }

  // Data rate bar
  const bytesPerSec = fs * (bits / 8);
  const maxRate = 44100 * 2;
  const bx = 27 + colW;
  const bw = colW - 30;
  fill('black');
  text('Data rate: ' + fmt(bytesPerSec) + ' bytes/s', bx, panelY + 10);
  stroke('silver');
  fill(235);
  rect(bx, panelY + 36, bw, 18, 4);
  noStroke();
  fill(bytesPerSec > 32000 ? 'darkorange' : 'seagreen');
  rect(bx, panelY + 36, bw * (bytesPerSec / maxRate), 18, 4);
  fill('black');
  textSize(14);
  text('0', bx, panelY + 57);
  textAlign(RIGHT, TOP);
  text('88,200 (CD rate, 16-bit)', bx + bw, panelY + 57);
  textAlign(LEFT, TOP);
  textSize(16);
  text('1 s of mono sound = ' + nf(bytesPerSec / 1024, 1, 1) + ' KB of RAM', bx, panelY + 82);

  // Aliasing warning banner across the plot
  if (aliasing) {
    const msg = 'ALIASING: ' + fmt(f) + ' Hz is above the Nyquist limit of ' +
      fmt(nyquist) + ' Hz';
    textSize(16);
    const w = textWidth(msg) + 24;
    stroke('crimson');
    strokeWeight(2);
    fill(255, 235, 235);
    rect((px0 + px1) / 2 - w / 2, py1 - 40, w, 28, 6);
    strokeWeight(1);
    noStroke();
    fill('crimson');
    textAlign(CENTER, CENTER);
    text(msg, (px0 + px1) / 2, py1 - 26);
  }

  // ---------- Control labels ----------
  noStroke();
  fill('black');
  textAlign(LEFT, CENTER);
  textSize(defaultTextSize);
  text('Wave frequency: ' + fmt(f) + ' Hz', 10, drawHeight + 18);
  text('Sampling rate: ' + fmt(fs) + ' samples/s', 10, drawHeight + 53);
  text('Bit depth:', 10, drawHeight + 89);
}

function drawLegend(x, y) {
  textSize(14);
  textAlign(LEFT, CENTER);
  let cx = x;
  const items = [
    ['line', 'steelblue', 'original wave'],
    ['dot', 'darkorange', 'samples + DAC staircase']
  ];
  if (heardCheckbox.checked()) items.push(['dash', 'crimson', 'heard wave']);
  // light background so the legend stays readable over the waves
  let total = 0;
  for (const it of items) total += 30 + textWidth(it[2]) + 14;
  noStroke();
  fill(255, 255, 255, 220);
  rect(x - 4, y - 2, total, 22, 4);
  for (const it of items) {
    if (it[0] === 'line') {
      stroke(it[1]); strokeWeight(2); line(cx, y + 9, cx + 22, y + 9);
    } else if (it[0] === 'dot') {
      noStroke(); fill(it[1]); circle(cx + 11, y + 9, 8);
    } else {
      stroke(it[1]); strokeWeight(2);
      drawingContext.setLineDash([5, 4]);
      line(cx, y + 9, cx + 22, y + 9);
      drawingContext.setLineDash([]);
    }
    strokeWeight(1);
    noStroke();
    fill('black');
    text(it[2], cx + 28, y + 9);
    cx += 30 + textWidth(it[2]) + 14;
  }
}

// Pick a round tick step (1, 2, 5 x 10^k)
function niceStep(raw) {
  const p = pow(10, floor(Math.log10(raw)));
  const m = raw / p;
  if (m < 1.5) return p;
  if (m < 3.5) return 2 * p;
  if (m < 7.5) return 5 * p;
  return 10 * p;
}

function formatMs(t, step) {
  const decimals = step >= 1 ? 0 : (step >= 0.1 ? 1 : 2);
  return nf(t, 1, decimals);
}

// Format a number with thousands separators
function fmt(n) {
  return Number(n).toLocaleString('en-US');
}

function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
  freqSlider.size(canvasWidth - sliderLeftMargin - margin);
  rateSlider.size(canvasWidth - sliderLeftMargin - margin);
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) {
    canvasWidth = Math.floor(container.getBoundingClientRect().width);
  }
}
