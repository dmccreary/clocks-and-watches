// Hysteresis Demonstrator MicroSim
// CANVAS_HEIGHT: 560
// A noisy light reading drifts slowly up and down. Two outputs decide "bright" or "dim":
// one uses a single threshold (the midpoint), the other switches up above the upper
// threshold and back down below the lower one (hysteresis). Switch counts compare them.
// Opens paused with a full window of readings; press Start to scroll new readings in.

let canvasWidth = 400;
let drawHeight = 410;
let controlHeight = 150;
let canvasHeight = drawHeight + controlHeight;
let margin = 25;
let sliderLeftMargin = 240;
let defaultTextSize = 16;

let startButton, lockCheckbox, noiseSlider, upperSlider, lowerSlider;
let isRunning = false;

const N = 400;            // readings shown in the window
let base = [];            // slowly varying true light level
let z = [];               // unit Gaussian noise for each reading (scaled by the slider)
let tIndex = 0;

const YMIN = 12000;
const YMAX = 44000;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));

  startButton = createButton('Start');
  startButton.position(10, drawHeight + 6);
  startButton.mousePressed(toggleRun);

  lockCheckbox = createCheckbox('Lock thresholds together (no gap)', false);
  lockCheckbox.position(80, drawHeight + 9);
  lockCheckbox.changed(applyLock);

  noiseSlider = createSlider(0, 5000, 1500, 50);
  noiseSlider.position(sliderLeftMargin, drawHeight + 43);
  noiseSlider.size(canvasWidth - sliderLeftMargin - margin);

  upperSlider = createSlider(20000, 40000, 30000, 250);
  upperSlider.position(sliderLeftMargin, drawHeight + 78);
  upperSlider.size(canvasWidth - sliderLeftMargin - margin);
  upperSlider.input(keepOrder);

  lowerSlider = createSlider(16000, 40000, 26000, 250);
  lowerSlider.position(sliderLeftMargin, drawHeight + 113);
  lowerSlider.size(canvasWidth - sliderLeftMargin - margin);
  lowerSlider.input(keepOrder);

  // fill the window with readings so the first frame already shows the effect
  randomSeed(3);
  for (let i = 0; i < N; i++) addReading();

  describe('A scrolling chart of a noisy light sensor reading with an upper and a lower threshold line and a shaded dead zone between them. Below it, two on and off traces: single threshold, which chatters near the line, and with hysteresis, which switches cleanly. Counters show how many times each output switched.');
}

function addReading() {
  const t = tIndex++;
  base.push(28000 + 7000 * sin(TWO_PI * t / 520) + 1800 * sin(TWO_PI * t / 157));
  z.push(randomGaussian(0, 1));
  if (base.length > N) {
    base.shift();
    z.shift();
  }
}

function toggleRun() {
  isRunning = !isRunning;
  startButton.html(isRunning ? 'Pause' : 'Start');
}

// The lower threshold can never be above the upper one
function keepOrder() {
  if (lockCheckbox.checked()) {
    lowerSlider.value(upperSlider.value());
  } else if (lowerSlider.value() > upperSlider.value()) {
    lowerSlider.value(upperSlider.value());
  }
}

function applyLock() {
  if (lockCheckbox.checked()) {
    lowerSlider.attribute('disabled', '');
  } else {
    lowerSlider.removeAttribute('disabled');
    if (lowerSlider.value() === upperSlider.value()) {
      lowerSlider.value(max(16000, upperSlider.value() - 4000));
    }
  }
  keepOrder();
}

function draw() {
  updateCanvasSize();

  stroke('silver');
  strokeWeight(1);
  fill('aliceblue');
  rect(0, 0, canvasWidth, drawHeight);
  fill('white');
  rect(0, drawHeight, canvasWidth, controlHeight);

  if (isRunning) addReading();

  const noise = noiseSlider.value();
  const upper = upperSlider.value();
  const lower = lowerSlider.value();
  const single = (upper + lower) / 2;
  const reading = base.map((b, i) => b + noise * z[i]);

  noStroke();
  fill('black');
  textAlign(CENTER, TOP);
  textSize(22);
  text('Hysteresis Demonstrator', canvasWidth / 2, 8);

  // ---------- Light reading chart ----------
  const x0 = 70;
  const x1 = canvasWidth - 15;
  const y0 = 40;
  const y1 = 212;
  const toX = (i) => map(i, 0, N - 1, x0, x1);
  const toY = (v) => map(constrain(v, YMIN, YMAX), YMIN, YMAX, y1, y0);

  stroke('silver');
  fill('white');
  rect(x0, y0, x1 - x0, y1 - y0);

  // dead zone
  noStroke();
  fill(230, 220, 250);
  rect(x0, toY(upper), x1 - x0, toY(lower) - toY(upper));

  // y axis labels
  fill('black');
  textSize(13);
  textAlign(RIGHT, CENTER);
  for (let v = 15000; v <= 40000; v += 5000) {
    stroke(235);
    line(x0, toY(v), x1, toY(v));
    noStroke();
    text(nf(v / 1000, 1, 0) + 'k', x0 - 4, toY(v));
  }
  push();
  translate(14, (y0 + y1) / 2);
  rotate(-HALF_PI);
  textAlign(CENTER, CENTER);
  textSize(14);
  text('Light reading', 0, 0);
  pop();

  // reading line
  stroke('steelblue');
  strokeWeight(1.5);
  noFill();
  beginShape();
  for (let i = 0; i < N; i++) vertex(toX(i), toY(reading[i]));
  endShape();

  // thresholds
  strokeWeight(2);
  drawingContext.setLineDash([8, 5]);
  stroke('crimson');
  line(x0, toY(upper), x1, toY(upper));
  stroke('royalblue');
  line(x0, toY(lower), x1, toY(lower));
  drawingContext.setLineDash([2, 4]);
  stroke('dimgray');
  line(x0, toY(single), x1, toY(single));
  drawingContext.setLineDash([]);
  strokeWeight(1);

  // threshold legend (top left of chart)
  drawLegend(x0 + 6, y0 + 4, [['crimson', 'upper'], ['royalblue', 'lower'], ['dimgray', 'single (midpoint)']]);

  // ---------- Outputs ----------
  // single threshold: bright whenever the reading is above the midpoint
  const outSingle = reading.map(v => v > single);
  // hysteresis: switch up above upper, back down below lower, otherwise keep the old state
  const outHyst = [];
  let state = reading[0] > single;
  for (let i = 0; i < N; i++) {
    if (!state && reading[i] > upper) state = true;
    else if (state && reading[i] < lower) state = false;
    outHyst.push(state);
  }
  const cSingle = countSwitches(outSingle);
  const cHyst = countSwitches(outHyst);

  drawTrace(outSingle, 'Single threshold', cSingle, x0, x1, 232, 'darkorange');
  drawTrace(outHyst, 'With hysteresis', cHyst, x0, x1, 302, 'seagreen');

  // status line
  noStroke();
  fill('black');
  textSize(15);
  textAlign(LEFT, TOP);
  const gap = upper - lower;
  text('Dead zone (gap): ' + gap + '    Switches: single ' + cSingle + ', hysteresis ' + cHyst,
    10, 382);
  if (!isRunning) {
    fill('dimgray');
    textAlign(RIGHT, TOP);
    if (canvasWidth > 640) text('Paused: press Start', canvasWidth - 12, 382);
  }

  // control labels
  noStroke();
  fill('black');
  textAlign(LEFT, CENTER);
  textSize(defaultTextSize);
  text('Noise amount: ' + noise, 10, drawHeight + 53);
  text('Upper threshold: ' + upper, 10, drawHeight + 88);
  text('Lower threshold: ' + lower, 10, drawHeight + 123);
}

function countSwitches(arr) {
  let c = 0;
  for (let i = 1; i < arr.length; i++) if (arr[i] !== arr[i - 1]) c++;
  return c;
}

// One on/off trace with its label and switch count
function drawTrace(out, label, count, x0, x1, top, col) {
  const h = 44;
  stroke('silver');
  fill('white');
  rect(x0, top + 18, x1 - x0, h);
  noStroke();
  fill('black');
  textSize(15);
  textAlign(LEFT, TOP);
  text(label + ': ' + count + ' switches', x0, top);
  textSize(13);
  textAlign(RIGHT, CENTER);
  text('bright', x0 - 4, top + 26);
  text('dim', x0 - 4, top + 18 + h - 8);

  const yOn = top + 26;
  const yOff = top + 18 + h - 8;
  stroke(col);
  strokeWeight(2.5);
  noFill();
  beginShape();
  for (let i = 0; i < out.length; i++) {
    const x = map(i, 0, out.length - 1, x0, x1);
    const y = out[i] ? yOn : yOff;
    if (i > 0 && out[i] !== out[i - 1]) vertex(x, out[i - 1] ? yOn : yOff);
    vertex(x, y);
  }
  endShape();
  strokeWeight(1);
}

function drawLegend(x, y, items) {
  textSize(13);
  let w = 0;
  for (const it of items) w += textWidth(it[1]) + 36;
  noStroke();
  fill(255, 255, 255, 220);
  rect(x - 4, y - 2, w, 20, 4);
  let cx = x;
  for (const it of items) {
    stroke(it[0]);
    strokeWeight(2);
    drawingContext.setLineDash(it[1].startsWith('single') ? [2, 3] : [6, 4]);
    line(cx, y + 8, cx + 22, y + 8);
    drawingContext.setLineDash([]);
    strokeWeight(1);
    noStroke();
    fill('black');
    textAlign(LEFT, CENTER);
    text(it[1], cx + 26, y + 8);
    cx += textWidth(it[1]) + 36;
  }
}

function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
  noiseSlider.size(canvasWidth - sliderLeftMargin - margin);
  upperSlider.size(canvasWidth - sliderLeftMargin - margin);
  lowerSlider.size(canvasWidth - sliderLeftMargin - margin);
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) {
    canvasWidth = Math.floor(container.getBoundingClientRect().width);
  }
}
