// E-Paper Refresh Lab MicroSim
// CANVAS_HEIGHT: 535
// A 152 x 152 e-paper clock is updated once a minute with a full refresh, a partial refresh,
// or a mix (a full refresh after every N partials). Partial refreshes are fast but leave a
// little ghosting each time; a full refresh flashes the screen and clears the ghosts.
// Simple ghost model: each partial adds 1.6 percent, a full refresh resets it to 0.
// Opens paused; "Advance one minute" steps once and "Run a day" fast-forwards 24 hours.

let canvasWidth = 400;
let drawHeight = 420;
let controlHeight = 115;
let canvasHeight = drawHeight + controlHeight;
let margin = 25;
let sliderLeftMargin = 260;
let defaultTextSize = 16;

let stepButton, runButton, resetButton, modeSelect, nSlider;

const GHOST_PER_PARTIAL = 1.6;
const FULL_SEC = 2.0;
const PARTIAL_SEC = 0.3;
const START_MIN = 7 * 60;

let clockMin, ghost, partials, fulls, sinceFull, history, oldTimes, minutesRun;
let running = false;
let runLeft = 0;
let flashFrames = 0;
let lastType = '';

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));

  stepButton = createButton('Advance one minute');
  stepButton.position(10, drawHeight + 6);
  stepButton.mousePressed(() => { if (!running) { refreshOnce(true); } });

  runButton = createButton('Run a day');
  runButton.position(170, drawHeight + 6);
  runButton.mousePressed(toggleRun);

  resetButton = createButton('Reset');
  resetButton.position(260, drawHeight + 6);
  resetButton.mousePressed(resetAll);

  modeSelect = createSelect();
  modeSelect.option('Always full refresh', 'full');
  modeSelect.option('Always partial refresh', 'partial');
  modeSelect.option('Mixed: full every N partials', 'mixed');
  modeSelect.selected('mixed');
  modeSelect.position(130, drawHeight + 44);
  modeSelect.changed(resetAll);

  nSlider = createSlider(2, 60, 30, 1);
  nSlider.position(sliderLeftMargin, drawHeight + 78);
  nSlider.size(canvasWidth - sliderLeftMargin - margin);
  nSlider.input(resetAll);

  resetAll();

  describe('An e-paper clock preview with faint ghost digits, a ghost level meter from 0 to 100 percent, readouts of partial and full refresh counts and total refresh time, and a timeline of recent refresh events with the ghost level drawn above them. Buttons advance one minute or run a whole day.');
}

function resetAll() {
  clockMin = START_MIN;
  ghost = 0;
  partials = 0;
  fulls = 0;
  sinceFull = 0;
  minutesRun = 0;
  history = [];
  oldTimes = [];
  running = false;
  runLeft = 0;
  flashFrames = 0;
  lastType = '';
  runButton.html('Run a day');
}

function toggleRun() {
  if (running) {
    running = false;
    runButton.html('Run a day');
  } else {
    running = true;
    runLeft = 1440;
    runButton.html('Pause');
  }
}

function timeText(m) {
  m = m % 1440;
  return nf(floor(m / 60), 2) + ':' + nf(m % 60, 2);
}

// One minute passes: the clock changes and the panel is refreshed by the chosen rule
function refreshOnce(animate) {
  const mode = modeSelect.value();
  const oldT = timeText(clockMin);
  clockMin = (clockMin + 1) % 1440;
  minutesRun++;
  let type;
  if (mode === 'full') type = 'full';
  else if (mode === 'partial') type = 'partial';
  else type = sinceFull >= nSlider.value() ? 'full' : 'partial';

  if (type === 'full') {
    fulls++;
    ghost = 0;
    sinceFull = 0;
    oldTimes = [];
    if (animate) flashFrames = 24;
  } else {
    partials++;
    sinceFull++;
    ghost = min(100, ghost + GHOST_PER_PARTIAL);
    oldTimes.unshift(oldT);
    if (oldTimes.length > 6) oldTimes.pop();
  }
  lastType = type;
  history.push({ type, ghost });
  if (history.length > 400) history.shift();
}

function draw() {
  updateCanvasSize();

  stroke('silver');
  strokeWeight(1);
  fill('aliceblue');
  rect(0, 0, canvasWidth, drawHeight);
  fill('white');
  rect(0, drawHeight, canvasWidth, controlHeight);

  if (running) {
    for (let k = 0; k < 4 && runLeft > 0; k++) {
      refreshOnce(false);
      runLeft--;
    }
    if (runLeft <= 0) {
      running = false;
      runButton.html('Run a day');
    }
  }

  noStroke();
  fill('black');
  textAlign(CENTER, TOP);
  textSize(22);
  text('E-Paper Refresh Lab', canvasWidth / 2, 8);

  const narrow = canvasWidth < 600;
  const S = narrow ? min(170, canvasWidth * 0.45) : min(230, canvasWidth * 0.36);
  const px = 14;
  const py = 42;
  drawPanel(px, py, S);
  drawReadouts(px + S + 22, py, canvasWidth - (px + S + 22) - 12, S, narrow);
  drawTimeline(12, py + S + 18, canvasWidth - 24, drawHeight - (py + S + 18) - 10);

  // control labels
  noStroke();
  fill('black');
  textAlign(LEFT, CENTER);
  textSize(defaultTextSize);
  text('Refresh mode:', 10, drawHeight + 53);
  const mixed = modeSelect.value() === 'mixed';
  fill(mixed ? 'black' : 'silver');
  text('Full refresh after ' + nSlider.value() + ' partials', 10, drawHeight + 88);
  if (mixed) nSlider.removeAttribute('disabled');
  else nSlider.attribute('disabled', '');
}

function drawPanel(x, y, S) {
  // bezel and paper
  noStroke();
  fill('dimgray');
  rect(x - 6, y - 6, S + 12, S + 12, 8);

  // a full refresh flashes black and white before showing the new image
  if (flashFrames > 0) {
    fill(floor(flashFrames / 4) % 2 === 0 ? 'black' : 'white');
    rect(x, y, S, S);
    flashFrames--;
    return;
  }
  fill('whitesmoke');
  rect(x, y, S, S);

  textAlign(CENTER, CENTER);
  textStyle(BOLD);
  textSize(S * 0.27);
  // ghosts of earlier digits: stronger for higher ghost level and more recent images
  for (let i = oldTimes.length - 1; i >= 0; i--) {
    const a = 255 * (ghost / 100) * 0.55 * pow(0.7, i);
    fill(0, 0, 0, a);
    text(oldTimes[i], x + S / 2 + (i + 1) * 0.6, y + S * 0.42);
  }
  fill('black');
  text(timeText(clockMin), x + S / 2, y + S * 0.42);
  textStyle(NORMAL);
  textSize(max(12, S * 0.075));
  fill(60);
  text('Tue 14 May', x + S / 2, y + S * 0.7);
  textSize(12);
  fill('gray');
  text('152 x 152 e-paper', x + S / 2, y + S - 12);
}

function drawReadouts(x, y, w, h, narrow) {
  stroke('silver');
  fill('white');
  rect(x, y - 6, w, h + 12, 8);

  const ts = narrow ? 13 : 16;
  const lh = narrow ? 18 : 23;
  let yy = y + 4;
  const xx = x + 10;
  noStroke();
  fill('black');
  textAlign(LEFT, TOP);
  textSize(ts);

  // ghost meter
  text('Ghost level: ' + nf(ghost, 1, 0) + '%', xx, yy);
  yy += lh;
  const mw = w - 20;
  stroke('silver');
  fill(235);
  rect(xx, yy, mw, 14, 4);
  noStroke();
  fill(ghost < 30 ? 'seagreen' : (ghost < 50 ? 'orange' : 'crimson'));
  rect(xx, yy, mw * ghost / 100, 14, 4);
  stroke('black');
  const mark = xx + mw * 0.5;
  line(mark, yy - 3, mark, yy + 17);
  noStroke();
  fill('dimgray');
  textSize(12);
  textAlign(CENTER, TOP);
  text('ghosts noticeable', mark, yy + 17);
  textAlign(LEFT, TOP);
  textSize(ts);
  yy += lh + 14;

  fill('black');
  const totalSec = partials * PARTIAL_SEC + fulls * FULL_SEC;
  text('Minutes run: ' + minutesRun + (running ? '  (running)' : ''), xx, yy); yy += lh;
  text('Partial refreshes: ' + partials, xx, yy); yy += lh;
  text('Full refreshes (flashes): ' + fulls, xx, yy); yy += lh;
  text((narrow ? 'Refresh time: ' : 'Total refresh time: ') + nf(totalSec, 1, 1) + ' s' + (totalSec >= 120 && !narrow ? ' (' + nf(totalSec / 60, 1, 1) + ' min)' : ''), xx, yy); yy += lh;
  if (lastType !== '') {
    fill(lastType === 'full' ? 'darkblue' : 'dimgray');
    text('Last update: ' + (lastType === 'full' ? 'full refresh (' + FULL_SEC + ' s, flash)' : 'partial refresh (' + PARTIAL_SEC + ' s)'), xx, yy, w - 20);
  } else {
    fill('dimgray');
    text('Press Advance one minute or Run a day.', xx, yy, w - 20);
  }
}

function drawTimeline(x, y, w, h) {
  stroke('silver');
  fill('white');
  rect(x, y, w, h, 8);
  noStroke();
  fill('black');
  textSize(14);
  textAlign(LEFT, TOP);
  const title = w < 560 ? 'Recent refreshes (dark = full) and ghost level' :
    'Recent refreshes, up to 120 (tall dark = full, short gray = partial), and ghost level';
  text(title, x + 8, y + 5);

  const gx0 = x + 10;
  const gx1 = x + w - 10;
  const gy0 = y + 26;
  const gy1 = y + h - 8;
  const n = 120;
  const shown = history.slice(-n);
  const step = (gx1 - gx0) / n;

  // ghost line
  stroke('crimson');
  strokeWeight(2);
  noFill();
  beginShape();
  for (let i = 0; i < shown.length; i++) {
    vertex(gx0 + (i + 0.5) * step, map(shown[i].ghost, 0, 100, gy1 - 22, gy0));
  }
  endShape();
  strokeWeight(1);

  // event ticks
  for (let i = 0; i < shown.length; i++) {
    const xx = gx0 + (i + 0.5) * step;
    if (shown[i].type === 'full') {
      stroke('darkblue');
      strokeWeight(max(1, step * 0.6));
      line(xx, gy1 - 18, xx, gy1);
    } else {
      stroke('silver');
      strokeWeight(max(1, step * 0.5));
      line(xx, gy1 - 7, xx, gy1);
    }
  }
  strokeWeight(1);
  if (shown.length === 0) {
    noStroke();
    fill('dimgray');
    textAlign(CENTER, CENTER);
    text('No refreshes yet', (gx0 + gx1) / 2, (gy0 + gy1) / 2);
  }
}

function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
  nSlider.size(canvasWidth - sliderLeftMargin - margin);
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) {
    canvasWidth = Math.floor(container.getBoundingClientRect().width);
  }
}
