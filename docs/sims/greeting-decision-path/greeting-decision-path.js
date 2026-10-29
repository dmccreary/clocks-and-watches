// Greeting Decision Path MicroSim
// CANVAS_HEIGHT: 520
// Trace an if/elif/else chain one test at a time. A marker moves down the
// flowchart; the path taken turns green and tests that are never reached
// turn gray. "Reorder tests" shows why the order of elif tests matters.

let canvasWidth = 400;
let drawHeight = 440;
let controlHeight = 80;
let canvasHeight = drawHeight + controlHeight;
let margin = 10;
let sliderLeftMargin = 110;
let defaultTextSize = 16;

const NORMAL_ORDER = [
  { limit: 6, result: 'Night' },
  { limit: 12, result: 'Morning' },
  { limit: 18, result: 'Afternoon' }
];
const ELSE_RESULT = 'Evening';

let tests = NORMAL_ORDER;
let hour = 15;
let evaluated = 0;      // how many tests have been checked so far
let outcome = -1;       // index of the result box reached (3 = else), -1 = not done
let markerFrom = null;  // marker animation: from/to points and progress
let markerTo = null;
let markerT = 1;

let stepButton, resetButton, reorderCheckbox, hourSlider;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));

  stepButton = createButton('Step');
  stepButton.position(10, drawHeight + 8);
  stepButton.mousePressed(doStep);

  resetButton = createButton('Reset trace');
  resetButton.position(65, drawHeight + 8);
  resetButton.mousePressed(resetTrace);

  reorderCheckbox = createCheckbox(' Reorder tests', false);
  reorderCheckbox.position(170, drawHeight + 10);
  reorderCheckbox.changed(() => {
    tests = reorderCheckbox.checked() ? NORMAL_ORDER.slice().reverse() : NORMAL_ORDER;
    resetTrace();
  });

  hourSlider = createSlider(0, 23, 15, 1);
  hourSlider.position(sliderLeftMargin, drawHeight + 47);
  hourSlider.size(canvasWidth - sliderLeftMargin - 25);
  hourSlider.input(() => { hour = hourSlider.value(); resetTrace(); });

  resetTrace();
  describe('A flowchart of an if, elif, else chain that picks a greeting from the hour. ' +
    'Each press of Step checks one test, such as hour < 12, and a marker moves along the path ' +
    'taken. The chosen greeting box turns green.', LABEL);
}

function resetTrace() {
  evaluated = 0;
  outcome = -1;
  markerFrom = { kind: 'node', k: 0 };
  markerTo = markerFrom;
  markerT = 1;
}

function doStep() {
  if (outcome >= 0) return;
  const fromIdx = evaluated;
  const i = evaluated;
  const pass = (i < tests.length) ? hour < tests[i].limit : true;
  evaluated++;
  if (i >= tests.length) {
    outcome = tests.length;          // the else branch
  } else if (pass) {
    outcome = i;
  }
  // marker moves from the current node to the next one
  markerFrom = markerTo;
  markerTo = outcome >= 0 ? { kind: 'result', k: outcome } : { kind: 'node', k: evaluated };
  markerT = 0;
}

// ---------- layout ----------
function wide() { return canvasWidth >= 620; }
function flowX() { return wide() ? canvasWidth * 0.27 : canvasWidth * 0.33; }
function diamondW() { return min(150, canvasWidth * 0.32); }
function rowY(i) { return 72 + i * 80; }        // i = 0..2 diamonds, 3 = else
function resultBoxX() { return flowX() + diamondW() / 2 + 44; }
function resultBoxW() {
  const right = wide() ? canvasWidth * 0.6 : canvasWidth - margin;
  return right - resultBoxX();
}

// Marker stops are stored as logical places and turned into pixels each frame,
// so the marker stays in the right place when the window is resized.
// node k: 0 = start box, 1..3 = test k, 4 = else box; result k = result box k
function markerPoint(m) {
  if (m.kind === 'result') return { x: resultBoxX(), y: rowY(m.k) + 40 };
  if (m.k === 0) return { x: flowX() - diamondW() / 2, y: 46 };
  if (m.k > tests.length) return { x: flowX() - diamondW() * 0.35, y: rowY(m.k - 1) + 40 };
  return { x: flowX() - diamondW() / 2, y: rowY(m.k - 1) + 40 };
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
  text('Greeting Decision Path', wide() ? canvasWidth * 0.55 : canvasWidth / 2, 8);

  drawFlowchart();
  if (wide()) drawCode();
  drawMarker();
  drawMessage();

  // control labels
  noStroke();
  fill('black');
  textSize(16);
  textAlign(LEFT, CENTER);
  text('hour = ' + hour, 10, drawHeight + 57);
}

function nodeState(i) {
  // 'taken' = checked and true, 'false' = checked and false,
  // 'skipped' = never reached because an earlier test was true, 'pending' = not yet
  if (i < evaluated) {
    if (i === outcome) return 'taken';
    return 'false';
  }
  if (outcome >= 0) return 'skipped';
  return 'pending';
}

function drawFlowchart() {
  const cx = flowX();
  const dw = diamondW();
  const dh = 56;
  const rx = resultBoxX();
  const rw = resultBoxW();

  // start box
  stroke('dimgray');
  strokeWeight(2);
  fill('white');
  rectMode(CENTER);
  rect(cx, 46, dw, 28, 14);
  rectMode(CORNER);
  noStroke();
  fill('black');
  textSize(16);
  textAlign(CENTER, CENTER);
  textFont('monospace');
  text('hour = ' + hour, cx, 47);
  textFont('sans-serif');

  for (let i = 0; i <= tests.length; i++) {
    const y = rowY(i) + 40;
    const state = nodeState(i);
    const reached = (i < evaluated) || (i === evaluated && outcome < 0);
    // arrow into this node from above
    const prevY = i === 0 ? 60 : rowY(i - 1) + 40 + dh / 2;
    arrow(cx, prevY, cx, y - (i < tests.length ? dh / 2 : 18),
      (i < evaluated) ? 'seagreen' : (outcome >= 0 && i > outcome ? 'lightgray' : 'gray'));
    if (i > 0) {
      noStroke();
      fill(i <= evaluated && (outcome < 0 || outcome >= i) ? 'firebrick' : 'silver');
      textSize(14);
      textAlign(LEFT, CENTER);
      text('False', cx + 6, (prevY + y - dh / 2) / 2);
    }

    let fillC = 'white', strokeC = 'steelblue';
    if (state === 'taken') { fillC = 'palegreen'; strokeC = 'seagreen'; }
    else if (state === 'false') { fillC = 'mistyrose'; strokeC = 'firebrick'; }
    else if (state === 'skipped') { fillC = 'gainsboro'; strokeC = 'silver'; }
    else if (reached) { fillC = 'lightyellow'; strokeC = 'darkorange'; }

    if (i < tests.length) {
      // diamond test
      stroke(strokeC);
      strokeWeight(state === 'pending' && !reached ? 2 : 3);
      fill(fillC);
      quad(cx, y - dh / 2, cx + dw / 2, y, cx, y + dh / 2, cx - dw / 2, y);
      noStroke();
      fill(state === 'skipped' ? 'gray' : 'black');
      textFont('monospace');
      textSize(16);
      textAlign(CENTER, CENTER);
      text('hour < ' + tests[i].limit, cx, y + 1);
      textFont('sans-serif');
      // evaluated value, shown to the left on wide screens
      if (i < evaluated && wide()) {
        const ok = hour < tests[i].limit;
        fill(ok ? 'seagreen' : 'firebrick');
        textSize(15);
        textAlign(RIGHT, CENTER);
        text(hour + ' < ' + tests[i].limit + ' is ' + (ok ? 'True' : 'False'), cx - dw / 2 - 16, y);
      }
      // True arrow to the result box
      arrow(cx + dw / 2, y, rx, y, state === 'taken' ? 'seagreen' : (state === 'skipped' ? 'lightgray' : 'gray'));
      noStroke();
      fill(state === 'taken' ? 'seagreen' : 'silver');
      textSize(14);
      textAlign(CENTER, BOTTOM);
      text('True', (cx + dw / 2 + rx) / 2, y - 3);
    } else {
      // else box
      stroke(strokeC);
      strokeWeight(state === 'pending' && !reached ? 2 : 3);
      fill(fillC);
      rectMode(CENTER);
      rect(cx, y, dw * 0.7, 34, 6);
      rectMode(CORNER);
      noStroke();
      fill('black');
      textFont('monospace');
      textSize(16);
      textAlign(CENTER, CENTER);
      text('else', cx, y + 1);
      textFont('sans-serif');
      arrow(cx + dw * 0.35, y, rx, y, state === 'taken' ? 'seagreen' : 'gray');
    }
    // result box
    const resultName = i < tests.length ? tests[i].result : ELSE_RESULT;
    const won = outcome === i;
    stroke(won ? 'seagreen' : (outcome >= 0 ? 'silver' : 'steelblue'));
    strokeWeight(won ? 4 : 2);
    fill(won ? 'palegreen' : 'white');
    rect(rx, y - 20, rw, 40, 6);
    noStroke();
    fill(outcome >= 0 && !won ? 'gray' : 'black');
    textSize(rw < 140 ? 14 : 16);
    textAlign(CENTER, CENTER);
    textFont('monospace');
    text('"' + resultName + '"', rx + rw / 2, y + 1);
    textFont('sans-serif');
  }
}

function arrow(x1, y1, x2, y2, c) {
  stroke(c);
  strokeWeight(2);
  line(x1, y1, x2, y2);
  const a = atan2(y2 - y1, x2 - x1);
  noStroke();
  fill(c);
  push();
  translate(x2, y2);
  rotate(a);
  triangle(0, 0, -9, -5, -9, 5);
  pop();
}

function drawMarker() {
  if (markerT < 1) markerT = min(1, markerT + 0.08);
  const e = markerT * markerT * (3 - 2 * markerT);
  const a = markerPoint(markerFrom), b = markerPoint(markerTo);
  stroke('white');
  strokeWeight(2);
  fill('darkorange');
  circle(lerp(a.x, b.x, e), lerp(a.y, b.y, e), 18);
  strokeWeight(1);
}

function codeLines() {
  const lines = ['hour = ' + hour];
  for (let i = 0; i < tests.length; i++) {
    lines.push((i === 0 ? 'if' : 'elif') + ' hour < ' + tests[i].limit + ':');
    lines.push('    greeting = "' + tests[i].result + '"');
  }
  lines.push('else:');
  lines.push('    greeting = "' + ELSE_RESULT + '"');
  lines.push('print(greeting)');
  return lines;
}

function drawCode() {
  const x = canvasWidth * 0.63, y = 40, w = canvasWidth - x - margin, h = 300;
  stroke('silver');
  fill(40);
  rect(x, y, w, h, 8);
  const lines = codeLines();
  // which line is "active" right now
  let active = 0;
  if (outcome >= 0) active = outcome < tests.length ? 2 + outcome * 2 : 2 + tests.length * 2;
  else if (evaluated > 0 || markerT < 1) active = 1 + evaluated * 2;
  if (outcome < 0 && evaluated === 0) active = 0;
  if (evaluated >= tests.length && outcome < 0) active = 1 + tests.length * 2;
  textFont('monospace');
  textSize(15);
  textAlign(LEFT, TOP);
  const lh = (h - 20) / lines.length;
  for (let i = 0; i < lines.length; i++) {
    const ly = y + 10 + i * lh;
    if (i === active) {
      noStroke();
      fill('khaki');
      rect(x + 4, ly - 2, w - 8, lh, 4);
      fill('black');
    } else {
      noStroke();
      fill('white');
    }
    text(lines[i], x + 10, ly + 3);
  }
  textFont('sans-serif');
}

function drawMessage() {
  let msg, c = 'black';
  if (evaluated === 0) {
    msg = 'Predict the greeting for hour = ' + hour + ', then press Step to check the first test.';
  } else if (outcome < 0) {
    const t = tests[evaluated - 1];
    msg = 'Test ' + evaluated + ': ' + hour + ' < ' + t.limit + ' is False, so Python moves on. Press Step.';
    c = 'firebrick';
  } else if (outcome < tests.length) {
    const t = tests[outcome];
    msg = hour + ' < ' + t.limit + ' is True, so greeting = "' + t.result + '". ' +
      (tests.length - outcome - 1 > 0 ? 'The remaining tests are skipped.' : 'The else is skipped.');
    c = 'darkgreen';
  } else {
    msg = 'Every test was False, so the else block runs: greeting = "' + ELSE_RESULT + '".';
    c = 'darkgreen';
  }
  if (reorderCheckbox.checked() && outcome >= 0 && (tests[outcome] ? tests[outcome].result : ELSE_RESULT) !== correctGreeting()) {
    msg += ' With this order the answer is wrong: it should be "' + correctGreeting() + '".';
    c = 'darkred';
  }
  noStroke();
  fill(c);
  textSize(16);
  textAlign(LEFT, TOP);
  text(msg, margin + 4, 384, canvasWidth - 2 * margin - 8, 54);
}

function correctGreeting() {
  for (const t of NORMAL_ORDER) if (hour < t.limit) return t.result;
  return ELSE_RESULT;
}

// ---------- responsive ----------
function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
  hourSlider.size(canvasWidth - sliderLeftMargin - 25);
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) canvasWidth = container.offsetWidth;
}
