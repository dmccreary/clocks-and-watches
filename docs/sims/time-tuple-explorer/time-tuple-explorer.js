// Time Tuple Explorer MicroSim
// CANVAS_HEIGHT: 500
// The eight fields of MicroPython's time.localtime() tuple drawn as boxes,
// filled from the browser's clock. Click a box to see the expression that
// extracts it, drag across boxes to make a slice like now[3:6], or turn on
// "Quiz me" to practice the index of each field.

let canvasWidth = 400;
let drawHeight = 420;
let controlHeight = 80;
let canvasHeight = drawHeight + controlHeight;
let margin = 10;
let defaultTextSize = 16;

const FIELDS = [
  { name: 'year', range: '2000 and up' },
  { name: 'month', range: '1 to 12' },
  { name: 'mday', range: '1 to 31 (day of the month)' },
  { name: 'hour', range: '0 to 23' },
  { name: 'minute', range: '0 to 59' },
  { name: 'second', range: '0 to 59' },
  { name: 'weekday', range: '0 to 6 (Monday is 0)' },
  { name: 'yearday', range: '1 to 366' }
];
const DAY_NAMES = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

let now = [];               // the 8 values
let sliceStart = 3, sliceStop = 6;
let selectedIndex = null;   // a single clicked box
let mode = 'slice';         // 'slice' or 'single' (what the info panel shows)
let dragFrom = null;
let dragTo = null;
let hoverIndex = null;

let liveCheckbox, quizCheckbox, newQuestionButton, startSelect, stopSelect;
let quizField = null;
let quizMessage = '';
let quizColor = 'black';
let quizRight = 0, quizTotal = 0;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  readClock();

  liveCheckbox = createCheckbox(' Live clock', false);
  liveCheckbox.position(10, drawHeight + 10);

  quizCheckbox = createCheckbox(' Quiz me', false);
  quizCheckbox.position(120, drawHeight + 10);
  quizCheckbox.changed(() => {
    quizRight = 0; quizTotal = 0;
    if (quizCheckbox.checked()) newQuestion();
  });

  newQuestionButton = createButton('New question');
  newQuestionButton.position(215, drawHeight + 8);
  newQuestionButton.mousePressed(() => { if (quizCheckbox.checked()) newQuestion(); });

  startSelect = createSelect();
  stopSelect = createSelect();
  for (let i = 0; i <= 8; i++) {
    if (i < 8) startSelect.option(String(i));
    if (i > 0) stopSelect.option(String(i));
  }
  startSelect.selected('3');
  stopSelect.selected('6');
  startSelect.position(120, drawHeight + 46);
  stopSelect.position(180, drawHeight + 46);
  startSelect.changed(() => { sliceStart = int(startSelect.value()); mode = 'slice'; });
  stopSelect.changed(() => { sliceStop = int(stopSelect.value()); mode = 'slice'; });

  describe('Eight labeled boxes showing the fields of the MicroPython time tuple: year, month, day, ' +
    'hour, minute, second, weekday and day of year, with their index numbers 0 to 7. A small analog ' +
    'and digital clock show the same time. Selecting boxes shows the matching Python index or slice.', LABEL);
}

// Fill the tuple from the browser's clock, the same way localtime() would on the Pico
function readClock() {
  const d = new Date();
  const y = d.getFullYear();
  const yearday = Math.round((Date.UTC(y, d.getMonth(), d.getDate()) - Date.UTC(y, 0, 0)) / 86400000);
  now = [y, d.getMonth() + 1, d.getDate(), d.getHours(), d.getMinutes(), d.getSeconds(),
    (d.getDay() + 6) % 7, yearday];
}

function newQuestion() {
  let f;
  do { f = floor(random(8)); } while (f === quizField);
  quizField = f;
  quizMessage = 'Click the box for "' + FIELDS[f].name + '". What is its index?';
  quizColor = 'darkblue';
}

// ---------- layout ----------
function boxRects() {
  const narrow = canvasWidth < 620;
  const perRow = narrow ? 4 : 8;
  const gap = 6;
  const w = (canvasWidth - 2 * margin - (perRow - 1) * gap) / perRow;
  const h = narrow ? 56 : 66;
  const rects = [];
  for (let i = 0; i < 8; i++) {
    const r = floor(i / perRow), c = i % perRow;
    rects.push({ x: margin + c * (w + gap), y: 62 + r * 100, w, h, row: r });
  }
  return rects;
}

function boxAt(mx, my) {
  const rs = boxRects();
  for (let i = 0; i < 8; i++) {
    const r = rs[i];
    if (mx >= r.x && mx <= r.x + r.w && my >= r.y - 20 && my <= r.y + r.h + 22) return i;
  }
  return null;
}

// ---------- drawing ----------
function draw() {
  updateCanvasSize();
  if (liveCheckbox.checked()) readClock();

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
  text(canvasWidth < 560 ? 'Time Tuple Explorer' : 'Time Tuple Explorer:  now = time.localtime()', canvasWidth / 2, 8);

  hoverIndex = (mouseY >= 0 && mouseY < drawHeight) ? boxAt(mouseX, mouseY) : null;
  cursor(hoverIndex !== null ? HAND : ARROW);
  drawBoxes();

  const narrow = canvasWidth < 620;
  const lowerY = narrow ? 268 : 190;
  const clockR = narrow ? 44 : 62;
  const clockX = margin + clockR + (narrow ? 14 : 8);
  drawClock(clockX, lowerY + clockR + 6, clockR);
  drawInfo(clockX + clockR + 18, lowerY, canvasWidth - (clockX + clockR + 18) - margin, drawHeight - lowerY - 8);

  // control labels
  noStroke();
  fill('black');
  textSize(16);
  textAlign(LEFT, CENTER);
  text('Slice:  now[', 10, drawHeight + 57);
  text(':', 168, drawHeight + 57);
  text(']', 228, drawHeight + 57);
  if (quizCheckbox.checked() && quizTotal > 0) text(quizRight + ' / ' + quizTotal, 330, drawHeight + 20);
}

function inSlice(i) {
  if (mode !== 'slice') return false;
  return i >= sliceStart && i < sliceStop;
}

function drawBoxes() {
  const rs = boxRects();
  const narrow = canvasWidth < 620;
  for (let i = 0; i < 8; i++) {
    const r = rs[i];
    const picked = (mode === 'single' && selectedIndex === i) || inSlice(i);
    const quizShow = quizCheckbox.checked();
    // index above the box
    noStroke();
    fill(picked ? 'darkorange' : 'dimgray');
    textSize(15);
    textStyle(BOLD);
    textAlign(CENTER, BOTTOM);
    text('[' + i + ']', r.x + r.w / 2, r.y - 3);
    textStyle(NORMAL);
    // the box
    stroke(hoverIndex === i ? 'darkorange' : (picked ? 'darkorange' : 'steelblue'));
    strokeWeight(hoverIndex === i || picked ? 3 : 2);
    fill(picked ? 'lightyellow' : 'white');
    rect(r.x, r.y, r.w, r.h, 6);
    noStroke();
    fill('black');
    textSize(narrow ? 22 : 26);
    textAlign(CENTER, CENTER);
    textFont('monospace');
    text(now[i], r.x + r.w / 2, r.y + r.h / 2);
    textFont('sans-serif');
    // field name under the box (hidden during the quiz so the index is not given away)
    fill('black');
    textSize(14);
    textAlign(CENTER, TOP);
    text(quizShow ? '?' : FIELDS[i].name, r.x + r.w / 2, r.y + r.h + 3);
  }
  // bracket under the slice, one piece per row
  if (mode === 'slice' && sliceStop > sliceStart) {
    for (const row of [0, 1]) {
      const inRow = [];
      for (let i = sliceStart; i < sliceStop; i++) if (rs[i].row === row) inRow.push(i);
      if (inRow.length === 0) continue;
      const a = rs[inRow[0]], b = rs[inRow[inRow.length - 1]];
      const by = a.y + a.h + 22;
      stroke('darkorange');
      strokeWeight(3);
      noFill();
      line(a.x + 2, by - 5, a.x + 2, by);
      line(a.x + 2, by, b.x + b.w - 2, by);
      line(b.x + b.w - 2, by - 5, b.x + b.w - 2, by);
      strokeWeight(1);
    }
  }
}

function drawClock(cx, cy, r) {
  stroke('steelblue');
  strokeWeight(3);
  fill('white');
  circle(cx, cy, 2 * r);
  for (let i = 0; i < 12; i++) {
    const a = i * TWO_PI / 12 - HALF_PI;
    stroke('black');
    strokeWeight(2);
    line(cx + (r - 8) * cos(a), cy + (r - 8) * sin(a), cx + (r - 2) * cos(a), cy + (r - 2) * sin(a));
  }
  const h = now[3] % 12 + now[4] / 60, m = now[4] + now[5] / 60, s = now[5];
  const hand = (val, max, len, wgt, c) => {
    const a = val / max * TWO_PI - HALF_PI;
    stroke(c);
    strokeWeight(wgt);
    line(cx, cy, cx + len * cos(a), cy + len * sin(a));
  };
  hand(h, 12, r * 0.5, 5, 'black');
  hand(m, 60, r * 0.75, 3, 'black');
  hand(s, 60, r * 0.85, 1, 'crimson');
  strokeWeight(1);
  noStroke();
  fill('black');
  circle(cx, cy, 6);
  // digital time and date underneath
  textAlign(CENTER, TOP);
  textFont('monospace');
  textSize(18);
  text(nf(now[3], 2) + ':' + nf(now[4], 2) + ':' + nf(now[5], 2), cx, cy + r + 8);
  textSize(r < 50 ? 12 : 14);
  text(DAY_NAMES[now[6]] + ' ' + now[0] + '-' + nf(now[1], 2) + '-' + nf(now[2], 2), cx, cy + r + 30);
  textFont('sans-serif');
  if (!liveCheckbox.checked()) {
    fill('dimgray');
    textSize(12);
    text('(snapshot at load)', cx, cy + r + 50);
  }
}

function drawInfo(px, py, pw, ph) {
  stroke('silver');
  strokeWeight(1);
  fill('white');
  rect(px, py, pw, ph, 8);
  noStroke();
  textAlign(LEFT, TOP);
  const tx = px + 12, tw = pw - 24;
  let y = py + 10;
  const big = canvasWidth < 500 ? 15 : 17;

  if (quizCheckbox.checked()) {
    fill(quizColor);
    textSize(big + 1);
    textStyle(BOLD);
    text(quizMessage, tx, y, tw);
    textStyle(NORMAL);
    return;
  }
  if (hoverIndex !== null && dragFrom === null) {
    fill('dimgray');
    textSize(14);
    text('Hovering: ' + FIELDS[hoverIndex].name + ', range ' + FIELDS[hoverIndex].range, tx, py + ph - 40, tw);
  }
  textFont('monospace');
  if (mode === 'single' && selectedIndex !== null) {
    const f = FIELDS[selectedIndex];
    fill('black');
    textSize(big);
    text('now[' + selectedIndex + ']', tx, y); y += 26;
    fill('darkorange');
    textStyle(BOLD);
    text('→ ' + now[selectedIndex], tx, y); y += 30;
    textStyle(NORMAL);
    textFont('sans-serif');
    fill('black');
    textSize(16);
    text(f.name + ': ' + f.range, tx, y, tw); y += 46;
    fill('dimgray');
    text('Drag across several boxes to make a slice.', tx, y, tw);
    return;
  }
  // slice view
  const vals = now.slice(sliceStart, sliceStop);
  const names = FIELDS.slice(sliceStart, sliceStop).map(f => f.name);
  fill('black');
  textSize(big);
  text('now[' + sliceStart + ':' + sliceStop + ']', tx, y); y += 26;
  fill('darkorange');
  textStyle(BOLD);
  let tupleText = vals.length === 0 ? '()' : (vals.length === 1 ? '(' + vals[0] + ',)' : '(' + vals.join(', ') + ')');
  text('→ ' + tupleText, tx, y, tw); y += textWidth('→ ' + tupleText) > tw ? 50 : 30;
  textStyle(NORMAL);
  fill('darkgreen');
  if (vals.length >= 2) {
    const unpack = names.join(', ') + ' = now[' + sliceStart + ':' + sliceStop + ']';
    text(unpack, tx, y, tw);
    y += textWidth(unpack) > tw ? 46 : 26;
  }
  textFont('sans-serif');
  fill('black');
  textSize(15);
  let note;
  if (vals.length === 0) note = 'Empty tuple: the stop index must be bigger than the start.';
  else if (vals.length === 1) note = 'A one-item slice is still a tuple, written with a comma.';
  else note = 'The slice starts at index ' + sliceStart + ' and stops before index ' + sliceStop + ', so it has ' +
    vals.length + ' items.';
  text(note, tx, y, tw);
}

// ---------- mouse ----------
function mousePressed() {
  if (mouseY < 0 || mouseY > drawHeight || mouseX < 0 || mouseX > canvasWidth) return;
  const i = boxAt(mouseX, mouseY);
  if (i === null) return;
  if (quizCheckbox.checked()) {
    quizTotal++;
    if (i === quizField) {
      quizRight++;
      quizMessage = 'Correct! ' + FIELDS[i].name + ' is now[' + i + '] = ' + now[i] + '. Press New question.';
      quizColor = 'darkgreen';
    } else {
      quizMessage = 'That box is now[' + i + '], the ' + FIELDS[i].name + '. Try again: find "' +
        FIELDS[quizField].name + '".';
      quizColor = 'firebrick';
    }
    return;
  }
  dragFrom = i;
  dragTo = i;
}

function mouseDragged() {
  if (dragFrom === null) return;
  const i = boxAt(mouseX, mouseY);
  if (i !== null && i !== dragTo) {
    dragTo = i;
    setSlice(min(dragFrom, dragTo), max(dragFrom, dragTo) + 1);
  }
}

function mouseReleased() {
  if (dragFrom === null) return;
  if (dragTo === dragFrom) {
    selectedIndex = dragFrom;
    mode = 'single';
  }
  dragFrom = null;
  dragTo = null;
}

function setSlice(a, b) {
  sliceStart = a;
  sliceStop = b;
  startSelect.selected(String(a));
  stopSelect.selected(String(b));
  mode = 'slice';
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
