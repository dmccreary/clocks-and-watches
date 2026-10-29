// Sleep vs Ticks Timeline MicroSim
// CANVAS_HEIGHT: 480
// Two programs blink an LED once a second. The top one uses sleep(1) and can
// only notice a button press between sleeps. The bottom one checks
// ticks_diff() on every short pass of its loop, so it notices a press within
// a few milliseconds. A red bar shows each program's delay (latency).

let canvasWidth = 400;
let drawHeight = 400;
let controlHeight = 80;
let canvasHeight = drawHeight + controlHeight;
let margin = 10;
let sliderLeftMargin = 200;
let defaultTextSize = 16;

const SLEEP_PERIOD = 1004;   // ms per pass of the sleep loop: 4 ms of work + 1000 ms asleep
const SLEEP_WORK = 4;
const TICKS_PASS = 10;       // ms per pass of the non-blocking loop
const WINDOW_MS = 3000;      // how much simulated time is visible

let simTime = 3400;          // simulated milliseconds since the Pico started
let isRunning = false;       // MicroSims open paused
let presses = [];            // {t, sleepDone, ticksDone}

let startButton, pressButton, resetButton, speedSlider;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));

  startButton = createButton('Start');
  startButton.position(10, drawHeight + 8);
  startButton.mousePressed(toggleRun);

  pressButton = createButton('Press button');
  pressButton.position(75, drawHeight + 8);
  pressButton.mousePressed(pressTheButton);

  resetButton = createButton('Reset');
  resetButton.position(185, drawHeight + 8);
  resetButton.mousePressed(resetSim);

  speedSlider = createSlider(0.05, 1, 0.25, 0.05);
  speedSlider.position(sliderLeftMargin, drawHeight + 47);
  speedSlider.size(canvasWidth - sliderLeftMargin - 25);

  describe('Two timelines. The top program sleeps for one second at a time, shown as long gray blocks; ' +
    'the bottom program checks the time every 10 milliseconds, shown as many small blue blocks. ' +
    'When the button is pressed, a red bar shows how long each program takes to notice.', LABEL);
}

function toggleRun() {
  isRunning = !isRunning;
  startButton.html(isRunning ? 'Pause' : 'Start');
}

function resetSim() {
  simTime = 3400;
  presses = [];
  isRunning = false;
  startButton.html('Start');
}

// The press is noticed the next time each loop checks the button
function pressTheButton() {
  if (!isRunning) toggleRun();
  const t = simTime;
  const sleepDone = Math.ceil(t / SLEEP_PERIOD) * SLEEP_PERIOD + 1;
  const ticksDone = Math.ceil(t / TICKS_PASS) * TICKS_PASS + 1;
  presses.push({ t, sleepDone, ticksDone });
  if (presses.length > 20) presses.shift();
}

// ---------- drawing ----------
function draw() {
  updateCanvasSize();
  if (isRunning) simTime += deltaTime * speedSlider.value();

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
  text(canvasWidth < 560 ? 'Sleep vs Ticks' : 'Sleep vs Ticks: Who Notices the Button?', canvasWidth / 2, 8);

  const x0 = 62, x1 = canvasWidth - margin - 4;
  const narrow = canvasWidth < 600;
  drawLane(x0, x1, 70, 'sleep', narrow ? 'loop: check button, toggle LED, sleep(1)' :
    'while True:  check button;  led.toggle();  sleep(1)');
  drawLane(x0, x1, 166, 'ticks', narrow ? 'loop: check button; ticks_diff() >= 1000?' :
    'while True:  check button;  if ticks_diff(now, last) >= 1000: led.toggle()');
  drawAxis(x0, x1, 230);
  drawStats();

  if (!isRunning) {
    noStroke();
    fill('darkorange');
    textSize(16);
    textAlign(RIGHT, TOP);
    text('Paused: press Start', canvasWidth - margin, 33);
  }

  noStroke();
  fill('black');
  textSize(16);
  textAlign(LEFT, CENTER);
  text('Speed: ' + speedSlider.value().toFixed(2) + 'x real time', 10, drawHeight + 57);
}

function timeToX(t, x0, x1) {
  return map(t, simTime - WINDOW_MS, simTime, x0, x1);
}

function drawLane(x0, x1, y, kind, label) {
  const h = 42;
  // code label above the lane
  noStroke();
  fill('dimgray');
  textFont('monospace');
  textSize(13);
  textAlign(LEFT, BOTTOM);
  text(label, x0, y - 4);
  textFont('sans-serif');

  // lane background
  stroke('silver');
  fill('white');
  rect(x0, y, x1 - x0, h);

  const tStart = simTime - WINDOW_MS;
  noStroke();
  if (kind === 'sleep') {
    for (let k = floor(tStart / SLEEP_PERIOD); k * SLEEP_PERIOD <= simTime; k++) {
      const a = k * SLEEP_PERIOD;
      // short "working" block: check the button and toggle the LED
      const wx0 = max(x0, timeToX(a, x0, x1));
      const wx1 = min(x1, timeToX(min(a + SLEEP_WORK, simTime), x0, x1));
      if (wx1 > x0 && wx0 < x1) {
        fill('royalblue');
        rect(wx0, y + 2, max(3, wx1 - wx0), h - 4);
      }
      // long sleeping block
      const sx0 = max(x0, timeToX(a + SLEEP_WORK, x0, x1));
      const sx1 = min(x1, timeToX(min(a + SLEEP_PERIOD, simTime), x0, x1));
      if (sx1 > sx0 + 1) {
        fill('lightgray');
        rect(sx0 + 2, y + 2, sx1 - sx0 - 2, h - 4);
        if (sx1 - sx0 > 90) {
          fill('dimgray');
          textSize(14);
          textAlign(CENTER, CENTER);
          text('sleeping', (sx0 + sx1) / 2, y + h / 2);
        }
      }
    }
  } else {
    for (let j = floor(tStart / TICKS_PASS); j * TICKS_PASS < simTime; j++) {
      const bx0 = timeToX(j * TICKS_PASS, x0, x1);
      const bx1 = timeToX(min((j + 1) * TICKS_PASS, simTime), x0, x1);
      if (bx1 < x0) continue;
      fill(j % 2 === 0 ? 'royalblue' : 'cornflowerblue');
      rect(max(x0, bx0), y + 2, max(1, bx1 - max(x0, bx0) - 0.5), h - 4);
    }
    // the LED toggles every 1000 ms, at the first pass that sees ticks_diff >= 1000
    for (let s = ceil(tStart / 1000) * 1000; s <= simTime; s += 1000) {
      const tx = timeToX(s, x0, x1);
      stroke('gold');
      strokeWeight(3);
      line(tx, y + 2, tx, y + h - 2);
      strokeWeight(1);
      noStroke();
    }
  }

  // red latency bars for button presses
  for (const p of presses) {
    const done = kind === 'sleep' ? p.sleepDone : p.ticksDone;
    if (p.t < tStart - 1500) continue;
    const px = timeToX(p.t, x0, x1);
    const ex = timeToX(min(done, simTime), x0, x1);
    if (ex >= x0) {
      fill(220, 20, 60, 200);
      rect(max(x0, px), y + h - 12, max(3, ex - max(x0, px)), 10);
    }
    if (px >= x0) {
      stroke('crimson');
      strokeWeight(2);
      drawingContext.setLineDash([4, 3]);
      line(px, y - 2, px, y + h + 2);
      drawingContext.setLineDash([]);
      strokeWeight(1);
      noStroke();
    }
    // only the newest press gets a text label, so labels never pile up
    if (p === presses[presses.length - 1] && ex >= x0 && ex <= x1 + 1) {
      fill('crimson');
      textSize(13);
      textAlign(LEFT, TOP);
      const lat = round(min(done, simTime) - p.t);
      const lab = done <= simTime ? 'noticed after ' + round(done - p.t) + ' ms' : 'waiting... ' + lat + ' ms';
      text(lab, min(ex + 3, x1 - textWidth(lab)), y + h + 2);
    }
  }

  // LED icon at the left of the lane
  const ledOn = kind === 'sleep' ? floor(simTime / SLEEP_PERIOD) % 2 === 0 : floor(simTime / 1000) % 2 === 0;
  stroke('dimgray');
  fill(ledOn ? 'gold' : 'dimgray');
  circle(30, y + h / 2, 26);
  noStroke();
  fill(ledOn ? 'black' : 'white');
  textSize(11);
  textAlign(CENTER, CENTER);
  text('LED', 30, y + h / 2);
  fill('black');
  textSize(13);
  text(kind === 'sleep' ? 'sleep' : 'ticks', 30, y + h + 12);
}

function drawAxis(x0, x1, y) {
  stroke('gray');
  line(x0, y, x1, y);
  noStroke();
  fill('dimgray');
  textSize(13);
  textAlign(CENTER, TOP);
  const tStart = simTime - WINDOW_MS;
  for (let s = ceil(tStart / 500) * 500; s <= simTime; s += 500) {
    const tx = timeToX(s, x0, x1);
    stroke('gray');
    line(tx, y, tx, y + 5);
    noStroke();
    text((s / 1000).toFixed(1) + ' s', tx, y + 7);
  }
}

function drawStats() {
  const px = margin, py = 262, pw = canvasWidth - 2 * margin, ph = drawHeight - py - 8;
  stroke('silver');
  fill('white');
  rect(px, py, pw, ph, 8);
  noStroke();
  textAlign(LEFT, TOP);
  textSize(16);
  const done = presses.filter(p => p.sleepDone <= simTime);
  if (presses.length === 0) {
    fill('black');
    text('Press Start, then press the button a few times. Watch how long each program takes to ' +
      'notice. Blue blocks are the program working; gray blocks are sleep(1), when it cannot ' +
      'see anything.', px + 10, py + 10, pw - 20);
    return;
  }
  const last = presses[presses.length - 1];
  fill('black');
  textStyle(BOLD);
  text('Last press', px + 10, py + 10);
  textStyle(NORMAL);
  const sl = last.sleepDone <= simTime ? round(last.sleepDone - last.t) + ' ms' : 'still asleep...';
  const tk = last.ticksDone <= simTime ? round(last.ticksDone - last.t) + ' ms' : 'checking...';
  fill('crimson');
  text('sleep(1) loop noticed it after: ' + sl, px + 10, py + 34, pw - 20);
  fill('royalblue');
  text('ticks_diff loop noticed it after: ' + tk, px + 10, py + 56, pw - 20);
  if (done.length > 0) {
    const avgS = done.reduce((a, p) => a + p.sleepDone - p.t, 0) / done.length;
    const avgT = done.reduce((a, p) => a + p.ticksDone - p.t, 0) / done.length;
    fill('black');
    text('Average over ' + done.length + (done.length === 1 ? ' press: ' : ' presses: ') +
      round(avgS) + ' ms vs ' + round(avgT) + ' ms', px + 10, py + 84, pw - 20);
  }
}

// ---------- responsive ----------
function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
  speedSlider.size(canvasWidth - sliderLeftMargin - 25);
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) canvasWidth = container.offsetWidth;
}
