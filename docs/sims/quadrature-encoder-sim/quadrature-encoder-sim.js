// Quadrature Encoder Simulator MicroSim
// CANVAS_HEIGHT: 465
// Turn a rotary encoder knob (drag it, or use Step CW / Step CCW) and watch
// the A and B signals. Each new state is added to the right of the traces, so
// students can step through the sequence. At every falling edge of A a line
// shows the value of B, which tells the direction: B = 1 adds 1, B = 0 subtracts 1.

let canvasWidth = 400;
let drawHeight = 420;
let controlHeight = 45;
let canvasHeight = drawHeight + controlHeight;
let margin = 10;
let defaultTextSize = 16;

// The four states in clockwise order, as (A, B). Counterclockwise walks backward.
const SEQ = [[0, 0], [1, 0], [1, 1], [0, 1]];
const QUARTER_DEG = 4.5;     // one state change per 4.5 degrees: 4 changes per 18-degree click

let pos = 0;                 // quarter-steps turned so far (negative = counterclockwise)
let value = 0;               // the counter in the program
let history = [];            // states shown on the traces: {a, b, edge: null | {b, delta}}
let lastEvent = '';
let dragging = false;
let dragAngle = 0;           // angle where the drag started
let dragAccum = 0;           // degrees turned since the last state change

let ccwButton, cwButton, resetButton, tableCheckbox;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));

  ccwButton = createButton('Step CCW');
  ccwButton.position(10, drawHeight + 10);
  ccwButton.mousePressed(() => stepDetent(-1));

  cwButton = createButton('Step CW');
  cwButton.position(95, drawHeight + 10);
  cwButton.mousePressed(() => stepDetent(1));

  resetButton = createButton('Reset');
  resetButton.position(172, drawHeight + 10);
  resetButton.mousePressed(resetEncoder);

  tableCheckbox = createCheckbox(' Show table', false);
  tableCheckbox.position(240, drawHeight + 12);

  resetEncoder();
  describe('A rotary encoder knob on the left and two square-wave traces, A and B, on the right. ' +
    'Turning the knob adds new A and B states to the traces. At each falling edge of A a marker shows ' +
    'the value of B, and the counter goes up by one when B is 1 or down by one when B is 0.', LABEL);
}

// The opening state shows one example clockwise click so the traces are not empty
function resetEncoder() {
  pos = 0;
  value = 0;
  history = [{ a: 0, b: 0, edge: null }, { a: 0, b: 0, edge: null }];
  stepDetent(1);
  lastEvent = 'Example: one clockwise click, so A and B went 00, 10, 11, 01, 00. A fell while B = 1, ' +
    'so value went up to 1. Now press Step CW or Step CCW, or drag the knob.';
}

function state() {
  return SEQ[((pos % 4) + 4) % 4];
}

// One quarter-step: A and B change to the next (or previous) state
function quarterStep(dir) {
  const before = state();
  pos += dir;
  const after = state();
  let edge = null;
  if (before[0] === 1 && after[0] === 0) {
    // falling edge of A: read B, exactly like the chapter's interrupt handler
    const delta = after[1] === 1 ? 1 : -1;
    value += delta;
    edge = { b: after[1], delta };
    lastEvent = 'A fell while B = ' + after[1] + ', so value ' + (delta > 0 ? '+= 1' : '-= 1') +
      (delta > 0 ? ' (clockwise).' : ' (counterclockwise).');
  } else {
    lastEvent = 'A = ' + after[0] + ', B = ' + after[1] + '. No falling edge on A, so the value does not change.';
  }
  history.push({ a: after[0], b: after[1], edge });
  if (history.length > 200) history.shift();
}

// One click of the knob (18 degrees) is a full cycle of four state changes
function stepDetent(dir) {
  for (let i = 0; i < 4; i++) quarterStep(dir);
}

// ---------- layout ----------
function knobGeom() {
  const narrow = canvasWidth < 600;
  const r = narrow ? 50 : 60;
  return { x: margin + r + 18, y: narrow ? 128 : 130, r };
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
  text('Quadrature Encoder Simulator', canvasWidth / 2, 8);

  const k = knobGeom();
  drawKnob(k);
  drawTraces(k.x + k.r + 30, 62, canvasWidth - margin - (k.x + k.r + 30), k);
  drawBottom();
}

function drawKnob(k) {
  // detent marks every 18 degrees
  for (let d = 0; d < 360; d += 18) {
    const a = radians(d) - HALF_PI;
    stroke('gray');
    strokeWeight(1);
    line(k.x + (k.r + 4) * cos(a), k.y + (k.r + 4) * sin(a), k.x + (k.r + 10) * cos(a), k.y + (k.r + 10) * sin(a));
  }
  stroke(dragging ? 'darkorange' : 'dimgray');
  strokeWeight(3);
  fill('dimgray');
  circle(k.x, k.y, 2 * k.r);
  fill('silver');
  noStroke();
  circle(k.x, k.y, 2 * k.r * 0.7);
  // pointer line shows the knob angle
  const a = radians(pos * QUARTER_DEG + dragAccum) - HALF_PI;
  stroke('crimson');
  strokeWeight(5);
  line(k.x, k.y, k.x + k.r * 0.85 * cos(a), k.y + k.r * 0.85 * sin(a));
  strokeWeight(1);
  noStroke();
  fill('dimgray');
  textSize(13);
  textAlign(CENTER, TOP);
  text('drag to turn', k.x, k.y + k.r + 12);
  // counter
  fill('black');
  textSize(16);
  textFont('monospace');
  text('value = ' + value, k.x, k.y + k.r + 32);
  textFont('sans-serif');
  // current A and B
  const s = state();
  textSize(15);
  fill('royalblue');
  text('A = ' + s[0] + '   B = ' + s[1], k.x, k.y + k.r + 54);
}

function drawTraces(x0, y0, w, k) {
  const segW = 24;
  const n = max(2, floor((w - 40) / segW));
  const shown = history.slice(-n);
  const traceH = 40;
  const lanes = [{ name: 'A', key: 'a', y: y0 + 10, c: 'royalblue' }, { name: 'B', key: 'b', y: y0 + 80, c: 'seagreen' }];
  // panel
  stroke('silver');
  fill('white');
  rect(x0, y0, w, 190, 6);
  for (const lane of lanes) {
    noStroke();
    fill(lane.c);
    textSize(18);
    textStyle(BOLD);
    textAlign(LEFT, CENTER);
    text(lane.name, x0 + 10, lane.y + traceH / 2);
    textStyle(NORMAL);
    fill('gray');
    textSize(11);
    text('1', x0 + 28, lane.y + 4);
    text('0', x0 + 28, lane.y + traceH - 4);
    // square wave: one segment per state
    stroke(lane.c);
    strokeWeight(3);
    noFill();
    beginShape();
    for (let i = 0; i < shown.length; i++) {
      const sx = x0 + 40 + i * segW;
      const sy = shown[i][lane.key] === 1 ? lane.y + 4 : lane.y + traceH - 4;
      vertex(sx, sy);
      vertex(sx + segW, sy);
    }
    endShape();
    strokeWeight(1);
  }
  // newest state marker
  const lastX = x0 + 40 + shown.length * segW;
  stroke('darkorange');
  strokeWeight(2);
  line(lastX, y0 + 6, lastX, y0 + 130);
  noStroke();
  fill('darkorange');
  textSize(12);
  textAlign(CENTER, BOTTOM);
  text('now', lastX, y0 - 2);
  // falling edges of A: a dashed line through both traces with the value of B
  for (let i = 1; i < shown.length; i++) {
    const e = shown[i].edge;
    if (!e) continue;
    const ex = x0 + 40 + i * segW;
    stroke('purple');
    strokeWeight(2);
    drawingContext.setLineDash([4, 3]);
    line(ex, y0 + 4, ex, y0 + 126);
    drawingContext.setLineDash([]);
    strokeWeight(1);
    noStroke();
    fill(e.delta > 0 ? 'darkgreen' : 'firebrick');
    textSize(13);
    textAlign(CENTER, TOP);
    text('B=' + e.b, ex, y0 + 146);
    text(e.delta > 0 ? '+1' : '−1', ex, y0 + 164);
  }
  noStroke();
  fill('gray');
  textSize(12);
  textAlign(LEFT, TOP);
  text('state changes →', x0 + 40, y0 + 132);
}

function drawBottom() {
  const py = 268, ph = drawHeight - py - 8;
  stroke('silver');
  fill('white');
  rect(margin, py, canvasWidth - 2 * margin, ph, 8);
  noStroke();
  textAlign(LEFT, TOP);
  if (!tableCheckbox.checked()) {
    fill('black');
    textSize(16);
    text(lastEvent, margin + 12, py + 10, canvasWidth - 2 * margin - 24);
    const nextY = py + 18 + countLines(lastEvent, canvasWidth - 2 * margin - 24) * textLeading();
    fill('dimgray');
    textSize(15);
    const tip = 'Each click of the knob is four state changes. The program only looks when A falls from 1 to 0: ' +
      'then B is 1 if you turned clockwise and 0 if you turned counterclockwise.';
    // only draw the tip when it fits in the panel (it does not on narrow screens)
    if (nextY + countLines(tip, canvasWidth - 2 * margin - 24) * textLeading() < py + ph - 4) {
      text(tip, margin + 12, nextY, canvasWidth - 2 * margin - 24);
    }
    return;
  }
  // state sequence table: clockwise and counterclockwise rows
  const s = ((pos % 4) + 4) % 4;
  const rows = [
    { label: 'Clockwise', order: [0, 1, 2, 3], fall: 2 },
    { label: 'Counterclockwise', order: [0, 3, 2, 1], fall: 3 }
  ];
  const narrow = canvasWidth < 600;
  const labelW = narrow ? 0 : 200;
  const boxW = narrow ? 52 : 64;
  const gapW = (canvasWidth - 2 * margin - 24 - labelW - 4 * boxW) / 4;
  for (let r = 0; r < 2; r++) {
    const row = rows[r];
    const y = py + (narrow ? 24 : 16) + r * 70;
    noStroke();
    fill('black');
    textSize(15);
    textAlign(LEFT, narrow ? BOTTOM : CENTER);
    text(row.label + ' (A B):', margin + 12, narrow ? y - 2 : y + 18);
    for (let i = 0; i < 4; i++) {
      const st = row.order[i];
      const bx = margin + 12 + labelW + i * (boxW + gapW);
      stroke(st === s ? 'darkorange' : 'steelblue');
      strokeWeight(st === s ? 3 : 1);
      fill(st === s ? 'lightyellow' : 'white');
      rect(bx, y, boxW, 36, 5);
      noStroke();
      fill('black');
      textFont('monospace');
      textSize(18);
      textAlign(CENTER, CENTER);
      text(SEQ[st][0] + ' ' + SEQ[st][1], bx + boxW / 2, y + 18);
      textFont('sans-serif');
      // arrow to the next state, with the falling edge of A marked
      const ax0 = bx + boxW + 3, ax1 = bx + boxW + gapW - 3;
      const isFall = i === row.fall;
      stroke(isFall ? 'purple' : 'gray');
      strokeWeight(isFall ? 3 : 1);
      line(ax0, y + 18, ax1, y + 18);
      noStroke();
      fill(isFall ? 'purple' : 'gray');
      triangle(ax1, y + 18, ax1 - 7, y + 14, ax1 - 7, y + 22);
      if (isFall) {
        textSize(12);
        textAlign(CENTER, TOP);
        text('A falls, B=' + SEQ[row.order[(i + 1) % 4]][1], (ax0 + ax1) / 2 - (narrow ? 8 : 0), y + 40);
      }
    }
  }
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

// ---------- knob dragging ----------
function mousePressed() {
  const k = knobGeom();
  if (dist(mouseX, mouseY, k.x, k.y) <= k.r + 10) {
    dragging = true;
    dragAngle = degrees(atan2(mouseY - k.y, mouseX - k.x));
    dragAccum = 0;
  }
}

function mouseDragged() {
  if (!dragging) return;
  const k = knobGeom();
  const a = degrees(atan2(mouseY - k.y, mouseX - k.x));
  let d = a - dragAngle;
  if (d > 180) d -= 360;
  if (d < -180) d += 360;
  dragAngle = a;
  dragAccum += d;
  // every 4.5 degrees of turning is one state change
  while (dragAccum >= QUARTER_DEG) { quarterStep(1); dragAccum -= QUARTER_DEG; }
  while (dragAccum <= -QUARTER_DEG) { quarterStep(-1); dragAccum += QUARTER_DEG; }
}

function mouseReleased() {
  dragging = false;
  dragAccum = 0;
}

// ---------- responsive ----------
function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) canvasWidth = container.offsetWidth;
}
