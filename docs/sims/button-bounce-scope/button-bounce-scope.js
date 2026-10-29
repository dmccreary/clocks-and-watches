// Button Bounce Oscilloscope MicroSim
// CANVAS_HEIGHT: 545
// Each press of the button makes a burst of contact bounce: 3 to 13 rapid
// transitions over 1 to 15 ms. The scope captures the pin voltage like a
// single-shot oscilloscope triggered by the first falling edge. Each falling
// edge is checked against the debounce window: green edges are counted as
// presses, red ones are ignored. A 0.1 uF hardware filter can smooth the trace.

let canvasWidth = 400;
let drawHeight = 430;
let controlHeight = 115;
let canvasHeight = drawHeight + controlHeight;
let margin = 10;
let sliderLeftMargin = 240;
let defaultTextSize = 16;

const PRE_TRIGGER = 5;        // ms shown before the first edge
const HOLD_MS = 120;          // the finger holds the button down this long
const TAU_CHARGE = 5;         // ms: 50 kOhm pull-up x 0.1 uF
const TAU_DISCHARGE = 0.02;   // ms: the closed contact empties the capacitor almost at once
const V_HIGH = 2.0, V_LOW = 0.8;   // input thresholds (with hysteresis)
const DT = 0.01;              // ms per simulation sample

// A fixed first capture so the scope is not empty when the page opens
const EXAMPLE_EDGES = [0, 0.6, 1.1, 2.4, 2.9, 4.2, 4.8, 6.1, 7.3];

let capture = null;      // {edges, bounceMs, samples, falls}
let physicalPresses = 0;
let countedPresses = 0;
let lastAcceptedAt = -1e9;   // time (ms) of the last accepted press, across presses
let clockMs = 0;             // simulated time of the current press start

let pressButton, resetButton, spanSelect, filterCheckbox, windowSlider;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));

  pressButton = createButton('Press button');
  pressButton.position(10, drawHeight + 8);
  pressButton.mousePressed(() => doPress(randomBounce()));

  resetButton = createButton('Reset count');
  resetButton.position(115, drawHeight + 8);
  resetButton.mousePressed(resetCounts);

  spanSelect = createSelect();
  spanSelect.option('20 ms');
  spanSelect.option('50 ms');
  spanSelect.option('150 ms');
  spanSelect.selected('50 ms');
  spanSelect.position(270, drawHeight + 8);

  filterCheckbox = createCheckbox(' Hardware filter (0.1 µF capacitor)', false);
  filterCheckbox.position(10, drawHeight + 44);
  filterCheckbox.changed(() => { if (capture) capture = simulate(capture.edges); });

  windowSlider = createSlider(0, 100, 0, 1);
  windowSlider.position(sliderLeftMargin, drawHeight + 80);
  windowSlider.size(canvasWidth - sliderLeftMargin - 25);

  doPress(EXAMPLE_EDGES);
  describe('An oscilloscope trace of a button pin voltage. When the button is pressed the voltage ' +
    'bounces between 3.3 volts and 0 volts several times before staying low. Green marks show falling ' +
    'edges counted as presses and red marks show edges ignored by the debounce window. A counter compares ' +
    'physical presses with counted presses.', LABEL);
}

function resetCounts() {
  physicalPresses = 0;
  countedPresses = 0;
  lastAcceptedAt = -1e9;
  clockMs = 0;
  doPress(EXAMPLE_EDGES);
}

// Random bounce: an odd number of contact changes (3 to 13) spread over 1 to 15 ms,
// so the contact ends closed (low)
function randomBounce() {
  let n = floor(random(3, 13));
  if (n % 2 === 0) n += 1;
  const dur = random(1, 15);
  const edges = [0, dur];
  for (let i = 0; i < n - 2; i++) edges.push(random(0.05, dur - 0.05));
  edges.sort((a, b) => a - b);
  return edges;
}

// Run one press: simulate the capture, then count the falling edges the program sees
function doPress(edges) {
  clockMs += 2000;                       // presses happen a couple of seconds apart
  capture = simulate(edges);
  physicalPresses++;
  const win = windowSlider.value();
  for (const f of capture.falls) {
    const t = clockMs + f;
    if (t - lastAcceptedAt > win) {      // same test as ticks_diff(now, last) > DEBOUNCE_MS
      countedPresses++;
      lastAcceptedAt = t;
    }
  }
}

// Build the voltage samples and the digital falling edges for one capture
function simulate(edges) {
  const total = PRE_TRIGGER + 150;
  const samples = [];
  const falls = [];
  const useFilter = filterCheckbox.checked();
  let v = 3.3;
  let digital = 1;
  let ei = 0;
  let closed = false;
  for (let t = -PRE_TRIGGER; t <= total - PRE_TRIGGER; t += DT) {
    // contact state from the bounce edges (and the clean release after HOLD_MS)
    while (ei < edges.length && edges[ei] <= t) { closed = !closed; ei++; }
    const isClosed = closed && t < HOLD_MS;
    if (useFilter) {
      const target = isClosed ? 0 : 3.3;
      const tau = isClosed ? TAU_DISCHARGE : TAU_CHARGE;
      v += (target - v) * (1 - Math.exp(-DT / tau));
    } else {
      v = isClosed ? 0 : 3.3;
    }
    // the input buffer turns the voltage into 0 or 1
    if (digital === 1 && v < V_LOW) { digital = 0; falls.push(t); }
    else if (digital === 0 && v > V_HIGH) digital = 1;
    samples.push(v);
  }
  return { edges, bounceMs: edges[edges.length - 1] - edges[0], samples, falls };
}

// Which falling edges of this capture a window would accept (for the markers)
function judgeFalls(win) {
  const out = [];
  let last = -1e9;
  for (const f of capture.falls) {
    const ok = f - last > win;
    out.push({ t: f, ok });
    if (ok) last = f;
  }
  return out;
}

// ---------- drawing ----------
function draw() {
  updateCanvasSize();

  stroke('silver');
  strokeWeight(1);
  fill('aliceblue');
  rect(0, 0, canvasWidth, drawHeight);
  fill('white');
  rect(0, drawHeight, canvasWidth, controlHeight);

  noStroke();
  fill('black');
  textAlign(CENTER, TOP);
  textSize(22);
  text('Button Bounce Oscilloscope', canvasWidth / 2, 8);

  drawScope(margin, 40, canvasWidth - 2 * margin, 210);
  drawStats(margin, 290, canvasWidth - 2 * margin, drawHeight - 298);

  // control labels
  noStroke();
  fill('black');
  textSize(16);
  textAlign(LEFT, CENTER);
  text('Span:', 225, drawHeight + 19);
  text('Debounce window: ' + windowSlider.value() + ' ms', 10, drawHeight + 91);
}

function drawScope(x, y, w, h) {
  const span = int(spanSelect.value());
  const tMin = -PRE_TRIGGER, tMax = span - PRE_TRIGGER;
  const left = x + 46, right = x + w - 10, top = y + 12, bottom = y + h - 12;
  const tx = t => map(t, tMin, tMax, left, right);
  const vy = v => map(v, 0, 3.3, bottom, top);

  // screen
  noStroke();
  fill(20);
  rect(x, y, w, h, 6);
  // grid
  stroke(60);
  const step = span <= 20 ? 2 : (span <= 50 ? 5 : 10);
  for (let t = 0; t <= tMax; t += step) line(tx(t), top, tx(t), bottom);
  for (let v = 0; v <= 3.3; v += 1.1) line(left, vy(v), right, vy(v));
  // debounce windows after each accepted edge
  const win = windowSlider.value();
  const judged = judgeFalls(win);
  noStroke();
  for (const j of judged) {
    if (!j.ok || win <= 0) continue;
    fill(80, 140, 255, 70);
    const a = tx(j.t), b = min(right, tx(j.t + win));
    if (b > a) rect(a, top, b - a, bottom - top);
  }
  // thresholds
  if (filterCheckbox.checked()) {
    stroke('darkorange');
    drawingContext.setLineDash([4, 4]);
    line(left, vy(V_HIGH), right, vy(V_HIGH));
    line(left, vy(V_LOW), right, vy(V_LOW));
    drawingContext.setLineDash([]);
  }
  // trace: for each pixel column draw the min-max range so fast edges stay visible
  stroke('yellow');
  strokeWeight(2);
  const n = capture.samples.length;
  let prevY = null;
  for (let px = left; px <= right; px++) {
    const t0 = map(px, left, right, tMin, tMax), t1 = map(px + 1, left, right, tMin, tMax);
    const i0 = constrain(floor((t0 - tMin) / DT), 0, n - 1), i1 = constrain(floor((t1 - tMin) / DT), 0, n - 1);
    let lo = 99, hi = -1;
    for (let i = i0; i <= max(i0, i1); i++) { lo = min(lo, capture.samples[i]); hi = max(hi, capture.samples[i]); }
    if (prevY !== null) line(px - 1, prevY, px, vy(capture.samples[i0]));
    line(px, vy(lo), px, vy(hi));
    prevY = vy(capture.samples[max(i0, i1)]);
  }
  strokeWeight(1);
  // falling-edge markers: green = counted, red = ignored
  for (const j of judged) {
    if (j.t > tMax) continue;
    const mx = tx(j.t);
    noStroke();
    fill(j.ok ? 'limegreen' : 'red');
    triangle(mx, bottom + 2, mx - 6, bottom + 12, mx + 6, bottom + 12);
  }
  // labels
  noStroke();
  fill('white');
  textSize(13);
  textAlign(RIGHT, CENTER);
  text('3.3 V', left - 4, vy(3.3));
  text('0 V', left - 4, vy(0));
  fill('black');
  textAlign(CENTER, TOP);
  for (let t = 0; t <= tMax; t += step * 2) text(t + ' ms', tx(t), y + h + 3);
  const hidden = capture.falls.filter(f => f > tMax).length;
  if (hidden > 0) {
    fill('dimgray');
    textAlign(RIGHT, TOP);
    text('+' + hidden + ' edge(s) off screen', x + w, y + h + 18);
  }
}

function drawStats(x, y, w, h) {
  stroke('silver');
  fill('white');
  rect(x, y, w, h, 8);
  noStroke();
  textAlign(LEFT, TOP);
  const win = windowSlider.value();
  const judged = judgeFalls(win);
  const thisCount = judged.filter(j => j.ok).length;
  textSize(canvasWidth < 500 ? 15 : 18);
  fill('black');
  textStyle(BOLD);
  text('Physical presses: ' + physicalPresses + '     Presses counted: ', x + 10, y + 10);
  const lab = 'Physical presses: ' + physicalPresses + '     Presses counted: ';
  fill(countedPresses === physicalPresses ? 'darkgreen' : 'firebrick');
  text(countedPresses, x + 10 + textWidth(lab.trimEnd()) + 8, y + 10);
  textStyle(NORMAL);
  textSize(15);
  fill('black');
  const transitions = capture.edges.length;
  const detail = 'This press: ' + transitions + ' contact changes over ' + capture.bounceMs.toFixed(1) +
    ' ms; ' + capture.falls.length + ' falling edge' + (capture.falls.length === 1 ? '' : 's') +
    ' reached the pin.';
  text(detail, x + 10, y + 38, w - 20);
  const vY = y + 42 + countLines(detail, w - 20) * textLeading();
  fill(thisCount === 1 ? 'darkgreen' : 'firebrick');
  let verdict;
  if (thisCount === 1) {
    verdict = 'With a ' + win + ' ms window this press counts once. ' +
      (capture.falls.length === 1 ? 'Only one clean edge reached the pin.' : 'The window covers the whole bounce.');
  } else {
    verdict = 'With a ' + win + ' ms window this press counts ' + thisCount +
      ' times. Make the window longer than the bounce.';
  }
  text(verdict, x + 10, vY, w - 20);
}

// Count how many lines text() will use when wrapping words inside width w
function countLines(str, w) {
  let lines = 1, current = '';
  for (const word of str.split(' ')) {
    const trial = current ? current + ' ' + word : word;
    if (textWidth(trial) > w && current) { lines++; current = word; }
    else current = trial;
  }
  return lines;
}

// ---------- responsive ----------
function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
  windowSlider.size(canvasWidth - sliderLeftMargin - 25);
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) canvasWidth = container.offsetWidth;
}
