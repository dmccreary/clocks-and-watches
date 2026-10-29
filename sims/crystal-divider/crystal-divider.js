// Crystal Divider MicroSim
// CANVAS_HEIGHT: 480
// A 32,768 Hz quartz crystal feeds a chain of 15 divide-by-two stages.
// Each stage output is a square wave at half the frequency of the stage
// before it, so after 15 stages the signal is exactly 1 Hz (32,768 = 2^15).
// A crystal error in parts per million (ppm) makes every stage run slightly
// fast, and the clock that counts the 1 Hz ticks gains time.

// Canvas dimensions - REQUIRED structure
let canvasWidth = 400;
let drawHeight = 400;
let controlHeight = 80;
let canvasHeight = drawHeight + controlHeight;
let margin = 20;
let sliderLeftMargin = 210;
let defaultTextSize = 16;

// Model constants
const CRYSTAL_HZ = 32768;
const NUM_BOXES = 16;           // the crystal plus 15 divide-by-two stages
const SLOW_FACTOR = 1 / 4096;   // slow motion: the crystal box flashes 8 times a second
const DAY_SECONDS = 86400;
const DAY_ANIM_SECONDS = 3;     // "Run one day" fast-forwards a day in 3 real seconds

// Simulation state
let isRunning = false;          // REQUIRED: MicroSims open paused
let trueTime = 0;               // seconds of perfect time since Reset
let dayAnim = null;             // {start, from} while "Run one day" is fast-forwarding
let dayMessage = '';

// Controls
let startButton, resetButton, dayButton, slowCheckbox, ppmSlider;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));

  startButton = createButton('Start');
  startButton.position(10, drawHeight + 8);
  startButton.mousePressed(toggleRun);

  resetButton = createButton('Reset');
  resetButton.position(72, drawHeight + 8);
  resetButton.mousePressed(resetSim);

  dayButton = createButton('Run one day');
  dayButton.position(132, drawHeight + 8);
  dayButton.mousePressed(runOneDay);

  slowCheckbox = createCheckbox('Slow motion', false);
  slowCheckbox.position(245, drawHeight + 10);

  ppmSlider = createSlider(0, 100, 30, 1);
  ppmSlider.position(sliderLeftMargin, drawHeight + 45);
  ppmSlider.size(canvasWidth - sliderLeftMargin - margin);
  ppmSlider.input(() => { dayMessage = ''; });

  describe('A chain of sixteen boxes shows a 32,768 hertz crystal being divided by two fifteen times down to 1 hertz. ' +
    'Each box flashes at its own rate. A perfect clock and a crystal clock count the 1 hertz ticks, and a readout ' +
    'shows how many seconds per day the crystal clock drifts for the chosen parts-per-million error. ' +
    'The MicroSim opens paused: press Start.', LABEL);
}

function draw() {
  updateCanvasSize();

  // Advance time only while running (or while fast-forwarding a day)
  const ppm = ppmSlider.value();
  const dt = min(deltaTime, 100) / 1000;
  let speed = slowCheckbox.checked() ? SLOW_FACTOR : 1;
  if (dayAnim) {
    const p = constrain((millis() - dayAnim.start) / (DAY_ANIM_SECONDS * 1000), 0, 1);
    trueTime = dayAnim.from + p * DAY_SECONDS;
    speed = DAY_SECONDS / DAY_ANIM_SECONDS;
    if (p >= 1) {
      const drift = DAY_SECONDS * ppm / 1e6;
      dayMessage = 'One day later the crystal clock is ' + nf(drift, 1, 2) + ' s ahead.';
      dayAnim = null;
      isRunning = false;
      startButton.html('Start');
    }
  } else if (isRunning) {
    trueTime += dt * speed;
  }
  const crystalTime = trueTime * (1 + ppm / 1e6);

  // Drawing area and control area backgrounds
  stroke('silver');
  strokeWeight(1);
  fill('aliceblue');
  rect(0, 0, canvasWidth, drawHeight);
  fill('white');
  rect(0, drawHeight, canvasWidth, controlHeight);

  // Title
  noStroke();
  fill('black');
  textAlign(CENTER, TOP);
  const narrowTitle = canvasWidth < 600;
  textSize(narrowTitle ? 18 : 22);
  text('Crystal Divider: 32,768 Hz down to 1 Hz', canvasWidth / 2, 10);
  textSize(14);
  fill('dimgray');
  text(narrowTitle ? 'Each arrow divides by 2. Pale = too fast to see.'
    : 'Each arrow is one divide-by-2 stage. Pale boxes flash too fast to see.', canvasWidth / 2, 40);

  drawChain(crystalTime, speed);
  drawClockPanel(crystalTime, ppm);

  // Control labels
  noStroke();
  fill('black');
  textAlign(LEFT, CENTER);
  textSize(defaultTextSize);
  text('Crystal error: ' + ppm + ' ppm', 10, drawHeight + 55);
}

// Draw the 16 boxes: 2 rows of 8 when wide, 4 rows of 4 when narrow
function drawChain(crystalTime, speed) {
  const cols = canvasWidth >= 600 ? 8 : 4;
  const rows = NUM_BOXES / cols;
  const gap = 18;
  const boxW = (canvasWidth - 2 * margin - (cols - 1) * gap) / cols;
  const top = 66;
  const areaH = 196;
  const rowStep = areaH / rows;
  const boxH = min(56, rowStep - 14);

  for (let i = 0; i < NUM_BOXES; i++) {
    const r = floor(i / cols);
    const c = i % cols;
    const x = margin + c * (boxW + gap);
    const y = top + r * rowStep;
    const freq = CRYSTAL_HZ / pow(2, i);

    // Square-wave state of this stage: on for the first half of each period
    const visibleRate = freq * speed;          // flashes per real second
    const tooFast = visibleRate > 8;
    const on = floor(crystalTime * freq * 2) % 2 === 0;

    // Arrow to the next box in the same row
    stroke('slategray');
    strokeWeight(2);
    fill('slategray');
    if (c < cols - 1 && i < NUM_BOXES - 1) {
      const ax = x + boxW + 2;
      const ay = y + boxH / 2;
      line(ax, ay, ax + gap - 6, ay);
      triangle(ax + gap - 4, ay, ax + gap - 9, ay - 4, ax + gap - 9, ay + 4);
    } else if (i < NUM_BOXES - 1) {
      // Wrap arrow from the end of this row to the start of the next row
      const yMid = y + boxH + (rowStep - boxH) / 2;
      noFill();
      line(x + boxW / 2, y + boxH, x + boxW / 2, yMid);
      line(x + boxW / 2, yMid, margin + boxW / 2, yMid);
      line(margin + boxW / 2, yMid, margin + boxW / 2, y + rowStep - 3);
      fill('slategray');
      triangle(margin + boxW / 2, y + rowStep, margin + boxW / 2 - 4, y + rowStep - 6, margin + boxW / 2 + 4, y + rowStep - 6);
    }

    // Box fill shows the stage output
    if (tooFast) fill('lemonchiffon');
    else fill(on ? 'gold' : 'white');
    stroke(i === NUM_BOXES - 1 ? 'darkorange' : (i === 0 ? 'mediumpurple' : 'gray'));
    strokeWeight(i === NUM_BOXES - 1 || i === 0 ? 3 : 1);
    rect(x, y, boxW, boxH, 6);

    // Frequency label, sized to fit the box
    noStroke();
    fill('black');
    textAlign(CENTER, CENTER);
    const label = freq.toLocaleString('en-US') + ' Hz';
    let ts = 15;
    textSize(ts);
    while (textWidth(label) > boxW - 6 && ts > 9) { ts--; textSize(ts); }
    if (i === 0 && boxH >= 40) {
      text(label, x + boxW / 2, y + boxH / 2 + 8);
      textSize(min(ts, 12));
      text('crystal', x + boxW / 2, y + boxH / 2 - 9);
    } else if (i === NUM_BOXES - 1 && boxH >= 40) {
      text(label, x + boxW / 2, y + boxH / 2 + 8);
      textSize(min(ts, 12));
      text('1 tick/s', x + boxW / 2, y + boxH / 2 - 9);
    } else {
      text(label, x + boxW / 2, y + boxH / 2);
    }
  }
}

// Perfect clock vs crystal clock, plus the drift readouts
function drawClockPanel(crystalTime, ppm) {
  const py = 272;
  const ph = 120;
  stroke('silver');
  strokeWeight(1);
  fill(255, 255, 255, 230);
  rect(margin, py, canvasWidth - 2 * margin, ph, 10);

  const narrow = canvasWidth < 600;
  const colW = (canvasWidth - 2 * margin) / 2;
  const x1 = margin + 14;
  const x2 = margin + colW + 10;

  noStroke();
  textAlign(LEFT, TOP);
  textSize(narrow ? 14 : 16);
  fill('black');
  text('Perfect clock', x1, py + 10);
  text('Crystal clock', x1, py + 62);
  textSize(narrow ? 22 : 28);
  fill('darkslategray');
  text(formatTime(floor(trueTime)), x1, py + 28);
  fill(crystalTime - trueTime >= 0.5 ? 'firebrick' : 'darkslategray');
  text(formatTime(floor(crystalTime)), x1, py + 80);

  const driftDay = DAY_SECONDS * ppm / 1e6;
  textSize(narrow ? 14 : 16);
  fill('black');
  textStyle(BOLD);
  text('Drift per day: ' + nf(driftDay, 1, 2) + ' s', x2, py + 10);
  textStyle(NORMAL);
  text('Drift per 30 days: ' + nf(driftDay * 30 / 60, 1, 2) + ' min', x2, py + 32);
  let status;
  if (dayAnim) status = 'Fast-forwarding one day...';
  else if (dayMessage) status = dayMessage;
  else if (!isRunning) status = 'Paused: press Start.';
  else status = slowCheckbox.checked() ? 'Running in slow motion (1/4096 speed).' : 'Running in real time.';
  fill(dayMessage && !dayAnim ? 'firebrick' : 'dimgray');
  text(status, x2, py + 58, canvasWidth - margin - x2 - 8, 60);
}

function formatTime(totalSeconds) {
  const h = floor(totalSeconds / 3600);
  const m = floor((totalSeconds % 3600) / 60);
  const s = totalSeconds % 60;
  return nf(h, 2) + ':' + nf(m, 2) + ':' + nf(s, 2);
}

function toggleRun() {
  if (dayAnim) return;
  isRunning = !isRunning;
  dayMessage = '';
  startButton.html(isRunning ? 'Pause' : 'Start');
}

function resetSim() {
  trueTime = 0;
  dayAnim = null;
  dayMessage = '';
  isRunning = false;            // Reset returns to the paused opening state
  startButton.html('Start');
}

function runOneDay() {
  if (dayAnim) return;
  dayMessage = '';
  dayAnim = { start: millis(), from: trueTime };
}

function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) {
    canvasWidth = container.offsetWidth;
    if (typeof ppmSlider !== 'undefined') {
      ppmSlider.size(canvasWidth - sliderLeftMargin - margin);
    }
  }
}
