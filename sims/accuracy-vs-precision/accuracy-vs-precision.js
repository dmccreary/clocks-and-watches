// Accuracy vs Precision Targets MicroSim
// CANVAS_HEIGHT: 535
// A dartboard-style target where the bullseye is the true time.
// Each dot is one clock "reading". Bias moves the whole cloud away from the
// bullseye (a clock that is consistently fast); Spread scatters the dots
// (random error from tick to tick). Students compare the two kinds of error.

// ---- Layout ----
let canvasWidth = 400;
let drawHeight = 420;
let controlHeight = 115;          // 3 rows x 35 + 10
let canvasHeight = drawHeight + controlHeight;
let margin = 25;
let sliderLeftMargin = 230;
let defaultTextSize = 16;

// ---- Controls ----
let biasSlider, spreadSlider, readingsButton;

// ---- Model ----
// Readings are stored in "seconds of error" so they do not depend on the canvas size.
// Ring spacing on the target is 1 second.
const MAX_ERROR = 5;               // outer ring = 5 seconds off
const NUM_READINGS = 20;
const ACCURACY_LIMIT = 1.0;        // average must land within 1 s of true time
const PRECISION_LIMIT = 1.0;       // readings must cluster within 1 s (std. dev.)
const BIAS_ANGLE = -Math.PI / 4;   // bias pushes the cloud up and to the right
let readings = [];

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  // Row 1: bias slider (seconds the clock is consistently off)
  biasSlider = createSlider(0, 4, 0.5, 0.1);
  biasSlider.position(sliderLeftMargin, drawHeight + 8);
  biasSlider.size(canvasWidth - sliderLeftMargin - margin);
  biasSlider.input(takeReadings);

  // Row 2: spread slider (random error from reading to reading)
  spreadSlider = createSlider(0.1, 3, 0.4, 0.1);
  spreadSlider.position(sliderLeftMargin, drawHeight + 43);
  spreadSlider.size(canvasWidth - sliderLeftMargin - margin);
  spreadSlider.input(takeReadings);

  // Row 3: drop a fresh set of 20 readings
  readingsButton = createButton('Take 20 readings');
  readingsButton.position(10, drawHeight + 78);
  readingsButton.mousePressed(takeReadings);

  takeReadings();   // a meaningful first frame: 20 dots already on the target

  describe('A dartboard target whose bullseye is the true time. Twenty dots show clock readings. ' +
    'Sliders set the bias (how far the clock is consistently off) and the spread (random error). ' +
    'A label classifies the result as accurate, precise, both, or neither.');
}

// Gaussian random readings: center = bias, spread = standard deviation
function takeReadings() {
  const bias = biasSlider.value();
  const spread = spreadSlider.value();
  readings = [];
  for (let i = 0; i < NUM_READINGS; i++) {
    readings.push({
      x: bias * Math.cos(BIAS_ANGLE) + randomGaussian(0, spread),
      y: bias * Math.sin(BIAS_ANGLE) + randomGaussian(0, spread)
    });
  }
}

// Statistics computed from the dots actually shown
function stats() {
  let mx = 0, my = 0;
  for (const r of readings) { mx += r.x; my += r.y; }
  mx /= readings.length; my /= readings.length;
  let sum = 0;
  for (const r of readings) sum += (r.x - mx) ** 2 + (r.y - my) ** 2;
  const sd = Math.sqrt(sum / readings.length);
  return { mx, my, avgOff: Math.hypot(mx, my), sd };
}

function classify(s) {
  const accurate = s.avgOff <= ACCURACY_LIMIT;
  const precise = s.sd <= PRECISION_LIMIT;
  if (accurate && precise) return { text: 'Accurate and precise', col: 'green' };
  if (precise) return { text: 'Precise but not accurate', col: 'darkorange' };
  if (accurate) return { text: 'Accurate on average but not precise', col: 'royalblue' };
  return { text: 'Neither accurate nor precise', col: 'firebrick' };
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

  // Responsive layout: target left + panel right when wide, stacked when narrow
  const wide = canvasWidth >= 600;
  let cx, cy, radius, px, py, pw;
  if (wide) {
    radius = min(175, canvasWidth * 0.3);
    cx = margin + radius + 10;
    cy = 45 + radius + 5;
    px = cx + radius + 30;
    py = 70;
    pw = canvasWidth - px - margin;
  } else {
    radius = min(110, (canvasWidth - 2 * margin) / 2);
    cx = canvasWidth / 2;
    cy = 45 + radius;
    px = margin;
    py = cy + radius + 12;
    pw = canvasWidth - 2 * margin;
  }
  const scale = radius / MAX_ERROR;  // pixels per second of error

  drawTarget(cx, cy, radius, scale);

  // Readings
  const s = stats();
  stroke('black');
  strokeWeight(1);
  fill('gold');
  for (const r of readings) {
    const dx = constrain(r.x * scale, -radius, radius);
    const dy = constrain(r.y * scale, -radius, radius);
    circle(cx + dx, cy + dy, 11);
  }
  // Average of the readings (a cross)
  stroke('purple');
  strokeWeight(3);
  const ax = cx + constrain(s.mx * scale, -radius, radius);
  const ay = cy + constrain(s.my * scale, -radius, radius);
  line(ax - 8, ay - 8, ax + 8, ay + 8);
  line(ax - 8, ay + 8, ax + 8, ay - 8);
  strokeWeight(1);

  // Title (drawn after the target)
  noStroke();
  fill('black');
  textAlign(CENTER, TOP);
  textSize(24);
  text('Accuracy vs Precision Targets', canvasWidth / 2, 10);

  drawPanel(px, py, pw, wide, s);

  // Control labels
  noStroke();
  fill('black');
  textAlign(LEFT, CENTER);
  textSize(defaultTextSize);
  text('Bias (consistently off): ' + biasSlider.value().toFixed(1) + ' s', 10, drawHeight + 18);
  text('Spread (random error): ' + spreadSlider.value().toFixed(1) + ' s', 10, drawHeight + 53);
  if (canvasWidth >= 600) {
    textSize(14);
    fill('dimgray');
    text('Each dot is one reading; the bullseye is the true time.', 170, drawHeight + 90);
  }
}

function drawTarget(cx, cy, radius, scale) {
  // Rings every 1 second of error, alternating colors like a dartboard
  noStroke();
  for (let ring = MAX_ERROR; ring >= 1; ring--) {
    fill(ring % 2 === 0 ? 'white' : 'lightsteelblue');
    stroke('slategray');
    circle(cx, cy, ring * scale * 2);
  }
  // Bullseye
  fill('crimson');
  noStroke();
  circle(cx, cy, scale * 0.5);
  // Ring labels
  noStroke();
  fill('dimgray');
  textAlign(LEFT, CENTER);
  textSize(12);
  for (let ring = 1; ring <= MAX_ERROR; ring++) {
    text(ring + ' s', cx + 3, cy + ring * scale - 7);
  }
}

function drawPanel(px, py, pw, wide, s) {
  const result = classify(s);
  const lineH = wide ? 26 : 21;
  const h = wide ? 320 : 5 * lineH + 16;
  fill(255, 255, 255, 230);
  stroke(200);
  rect(px, py, pw, h, 10);
  noStroke();
  textAlign(LEFT, TOP);
  let y = py + 10;

  fill(result.col);
  textSize(wide ? 20 : 17);
  text(result.text, px + 12, y, pw - 24);
  y += wide ? 62 : lineH + 2;

  fill('black');
  textSize(wide ? 16 : 15);
  text('Average reading is ' + s.avgOff.toFixed(2) + ' s from true time', px + 12, y, pw - 24);
  y += wide ? 48 : lineH;
  text('Readings scatter by ' + s.sd.toFixed(2) + ' s (std. dev.)', px + 12, y, pw - 24);
  y += wide ? 48 : lineH;

  if (wide) {
    fill('dimgray');
    textSize(14);
    text('Accurate: average within ' + ACCURACY_LIMIT + ' s of the bullseye.', px + 12, y, pw - 24);
    y += 40;
    text('Precise: readings cluster within ' + PRECISION_LIMIT + ' s of each other.', px + 12, y, pw - 24);
    y += 44;
    fill('crimson');
    text('Red bullseye = true time', px + 12, y, pw - 24);
    y += 24;
    fill('purple');
    text('X = average of the 20 readings', px + 12, y, pw - 24);
  } else {
    fill('purple');
    textSize(14);
    text('Red = true time, X = average reading', px + 12, y, pw - 24);
    y += lineH;
    fill('dimgray');
    text('Accurate: within 1 s. Precise: spread under 1 s.', px + 12, y, pw - 24);
  }
}

function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
  biasSlider.size(canvasWidth - sliderLeftMargin - margin);
  spreadSlider.size(canvasWidth - sliderLeftMargin - margin);
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) canvasWidth = Math.floor(container.getBoundingClientRect().width);
}
