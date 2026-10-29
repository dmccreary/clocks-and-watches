// Breadboard Connectivity Explorer MicroSim
// CANVAS_HEIGHT: 540
// A half-size breadboard: 30 numbered columns, rows a-e and f-j on either
// side of the center channel, and two power rails along each long edge.
// Inside, metal strips join each column of five (a-e or f-j) and each whole
// rail. Hover a hole to light up everything it touches, click two holes to
// add a jumper wire, or press Challenge to test yourself.

// Canvas dimensions - REQUIRED structure
let canvasWidth = 400;
let drawHeight = 460;
let controlHeight = 80;
let canvasHeight = drawHeight + controlHeight;
let margin = 10;
let defaultTextSize = 16;

const COLS = 30;
const ROW_NAMES = 'abcdefghij';
// Rails: 0 = top -, 1 = top +, 2 = bottom +, 3 = bottom -
const RAIL_NAMES = ['top − rail', 'top + rail', 'bottom + rail', 'bottom − rail'];
const RAIL_COLORS = ['royalblue', 'crimson', 'crimson', 'royalblue'];

// Layout (recomputed every frame)
let px, py, boardX, boardY, boardW, boardH;
const yRow = {};   // y for each line of holes, keyed 'r0'..'r3' and 'm0'..'m9'

let holes = [];       // every hole: {kind, col, row, rail, idx, net, name}
let jumpers = [];     // {a, b} hole objects
let pending = null;   // first end of a jumper being placed
let jumperMsg = 'Hover a hole to see what it connects to. Click two holes to add a jumper wire.';

// Challenge mode state
let challenge = null; // {a, b, jumper, answered, correct, answer}
let score = 0;
let asked = 0;

let xrayBox, clearButton, modeButton, yesButton, noButton, nextButton;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  buildHoles();

  xrayBox = createCheckbox('X-ray view', false);
  xrayBox.position(10, drawHeight + 10);

  clearButton = createButton('Clear jumpers');
  clearButton.position(120, drawHeight + 8);
  clearButton.mousePressed(() => { jumpers = []; pending = null; jumperMsg = 'Jumpers cleared.'; });

  modeButton = createButton('Challenge');
  modeButton.position(232, drawHeight + 8);
  modeButton.mousePressed(toggleChallenge);

  yesButton = createButton('Yes');
  yesButton.position(10, drawHeight + 44);
  yesButton.mousePressed(() => answer(true));
  noButton = createButton('No');
  noButton.position(62, drawHeight + 44);
  noButton.mousePressed(() => answer(false));
  nextButton = createButton('Next question');
  nextButton.position(110, drawHeight + 44);
  nextButton.mousePressed(newChallenge);
  showChallengeButtons(false);

  describe('A top-down half-size breadboard with 30 columns, rows a to j split by a center channel, and two power ' +
    'rails on the top and bottom edges. Hovering a hole highlights every hole electrically connected to it. ' +
    'Clicking two holes adds a jumper wire. An X-ray option shows the hidden metal strips, and a Challenge mode ' +
    'asks whether two marked holes are connected.', LABEL);
}

// Every hole on the board, with the metal strip ("net") it belongs to
function buildHoles() {
  holes = [];
  for (let r = 0; r < 4; r++) {
    for (let k = 0; k < 25; k++) {
      const col = floor(k / 5) * 6 + (k % 5) + 1;   // groups of five with a gap
      holes.push({ kind: 'rail', rail: r, idx: k, col, net: 'R' + r, name: RAIL_NAMES[r] + ' (hole ' + (k + 1) + ')' });
    }
  }
  for (let c = 0; c < COLS; c++) {
    for (let r = 0; r < 10; r++) {
      holes.push({ kind: 'main', col: c, row: r, net: (r < 5 ? 'T' : 'B') + c, name: ROW_NAMES[r] + (c + 1) });
    }
  }
}

function computeLayout() {
  const labelW = 22;
  px = min(22, (canvasWidth - 2 * margin - 2 * labelW) / COLS);
  py = 21;
  boardW = COLS * px + 2 * labelW;
  boardX = (canvasWidth - boardW) / 2;
  boardY = 64;
  let y = boardY + py * 0.7;
  yRow.r0 = y; y += py;
  yRow.r1 = y; y += py * 1.6;              // gap holds the column numbers
  for (let r = 0; r < 5; r++) { yRow['m' + r] = y; y += py; }
  y += py * 0.5;                           // center channel
  for (let r = 5; r < 10; r++) { yRow['m' + r] = y; y += py; }
  y += py * 0.6;                           // gap holds the column numbers
  yRow.r2 = y; y += py;
  yRow.r3 = y;
  boardH = y + py * 0.7 - boardY;
}

function holeXY(h) {
  const x = boardX + 22 + (h.col + 0.5) * px;
  const y = h.kind === 'rail' ? yRow['r' + h.rail] : yRow['m' + h.row];
  return { x, y };
}

function holeAt(mx, my) {
  for (const h of holes) {
    const p = holeXY(h);
    if (abs(mx - p.x) <= px / 2 && abs(my - p.y) <= py / 2) return h;
  }
  return null;
}

// All nets joined to a starting net through jumpers (breadth-first search)
function connectedNets(net, jumperList) {
  const seen = new Set([net]);
  const queue = [net];
  while (queue.length) {
    const n = queue.shift();
    for (const j of jumperList) {
      for (const [p, q] of [[j.a.net, j.b.net], [j.b.net, j.a.net]]) {
        if (p === n && !seen.has(q)) { seen.add(q); queue.push(q); }
      }
    }
  }
  return seen;
}

function activeJumpers() {
  return challenge ? (challenge.jumper ? [challenge.jumper] : []) : jumpers;
}

function draw() {
  updateCanvasSize();
  computeLayout();

  // Backgrounds
  stroke('silver');
  strokeWeight(1);
  fill('aliceblue');
  rect(0, 0, canvasWidth, drawHeight);
  fill('white');
  rect(0, drawHeight, canvasWidth, controlHeight);

  // Title and status line
  noStroke();
  fill('black');
  textAlign(CENTER, TOP);
  textSize(canvasWidth >= 600 ? 22 : 18);
  text('Breadboard Connectivity Explorer', canvasWidth / 2, 8);

  const hover = (mouseY > 0 && mouseY < drawHeight) ? holeAt(mouseX, mouseY) : null;
  const hideAnswers = challenge && !challenge.answered;

  drawBoard();
  if (xrayBox.checked() && !hideAnswers) drawStrips();

  // Which holes to light up
  let lit = new Set();
  let focus = null;
  if (challenge && challenge.answered) focus = challenge.a;
  else if (!hideAnswers && hover) focus = hover;
  if (focus) lit = connectedNets(focus.net, activeJumpers());

  drawHoles(lit, focus, hover);
  drawJumpers();
  if (challenge) drawChallengeMarks();
  drawStatus(hover, lit, focus);

  // Score in the control area
  noStroke();
  fill('black');
  textAlign(LEFT, CENTER);
  textSize(defaultTextSize);
  if (challenge) text('Score: ' + score + ' / ' + asked, 235, drawHeight + 56);
  else { fill('dimgray'); text('Free play', 235, drawHeight + 56); }
}

function drawBoard() {
  stroke('darkgray');
  strokeWeight(1);
  fill('whitesmoke');
  rect(boardX, boardY, boardW, boardH, 8);
  // Center channel
  noStroke();
  fill('gainsboro');
  rect(boardX + 6, yRow.m4 + py * 0.55, boardW - 12, py * 0.4, 3);
  // Rail stripes
  strokeWeight(2);
  for (let r = 0; r < 4; r++) {
    stroke(RAIL_COLORS[r]);
    const y = yRow['r' + r] + (r === 0 || r === 2 ? -py * 0.55 : py * 0.55);
    line(boardX + 24, y, boardX + boardW - 24, y);
  }
  // Rail symbols at both ends
  noStroke();
  textSize(16);
  textAlign(CENTER, CENTER);
  for (let r = 0; r < 4; r++) {
    fill(RAIL_COLORS[r]);
    const s = (r === 0 || r === 3) ? '−' : '+';
    text(s, boardX + 11, yRow['r' + r]);
    text(s, boardX + boardW - 11, yRow['r' + r]);
  }
  // Row letters
  fill('dimgray');
  textSize(min(14, py * 0.7));
  for (let r = 0; r < 10; r++) {
    text(ROW_NAMES[r], boardX + 11, yRow['m' + r]);
    text(ROW_NAMES[r], boardX + boardW - 11, yRow['m' + r]);
  }
  // Column numbers above row a and below row j
  textSize(px >= 18 ? 12 : 9);
  for (let c = 0; c < COLS; c++) {
    if (c === 0 || (c + 1) % 5 === 0) {
      const x = boardX + 22 + (c + 0.5) * px;
      text(c + 1, x, yRow.m0 - py * 0.85);
      text(c + 1, x, yRow.m9 + py * 0.8);
    }
  }
}

// Faint metal strips seen in X-ray mode
function drawStrips() {
  noStroke();
  fill(176, 196, 222, 150);
  for (let c = 0; c < COLS; c++) {
    const x = boardX + 22 + (c + 0.5) * px;
    rect(x - px * 0.18, yRow.m0 - py * 0.4, px * 0.36, yRow.m4 - yRow.m0 + py * 0.8, 3);
    rect(x - px * 0.18, yRow.m5 - py * 0.4, px * 0.36, yRow.m9 - yRow.m5 + py * 0.8, 3);
  }
  for (let r = 0; r < 4; r++) {
    const y = yRow['r' + r];
    rect(boardX + 22 + px * 0.6, y - py * 0.18, COLS * px - px * 1.2, py * 0.36, 3);
  }
}

function drawHoles(lit, focus, hover) {
  const s = max(5, min(px, py) * 0.48);
  for (const h of holes) {
    const p = holeXY(h);
    let c = 'dimgray';
    if (lit.has(h.net)) c = 'gold';
    if (focus && h === focus) c = 'darkorange';
    if (pending && h === pending) c = 'limegreen';
    stroke(c === 'dimgray' ? 'gray' : 'black');
    strokeWeight(1);
    fill(c);
    rect(p.x - s / 2, p.y - s / 2, s, s, 1);
  }
}

function drawJumpers() {
  const list = activeJumpers();
  for (const j of list) {
    const a = holeXY(j.a);
    const b = holeXY(j.b);
    // A curved wire sampled as a quadratic curve that bows upward
    const mx = (a.x + b.x) / 2;
    const my = (a.y + b.y) / 2 - max(20, dist(a.x, a.y, b.x, b.y) * 0.25);
    noFill();
    stroke('forestgreen');
    strokeWeight(4);
    beginShape();
    for (let t = 0; t <= 1.0001; t += 0.05) {
      const x = (1 - t) * (1 - t) * a.x + 2 * (1 - t) * t * mx + t * t * b.x;
      const y = (1 - t) * (1 - t) * a.y + 2 * (1 - t) * t * my + t * t * b.y;
      vertex(x, y);
    }
    endShape();
    noStroke();
    fill('forestgreen');
    circle(a.x, a.y, 8);
    circle(b.x, b.y, 8);
  }
}

function drawChallengeMarks() {
  for (const [h, label] of [[challenge.a, 'A'], [challenge.b, 'B']]) {
    const p = holeXY(h);
    noFill();
    stroke('magenta');
    strokeWeight(3);
    circle(p.x, p.y, max(16, px * 0.9));
    noStroke();
    fill('magenta');
    textStyle(BOLD);
    textSize(15);
    if (h.kind === 'rail') {
      // Rail holes: put the letter to the left so it does not cover the column numbers
      textAlign(RIGHT, CENTER);
      text(label, p.x - max(8, px * 0.45) - 2, p.y);
    } else {
      textAlign(CENTER, BOTTOM);
      text(label, p.x, p.y - 9);
    }
    textStyle(NORMAL);
  }
}

function drawStatus(hover, lit, focus) {
  noStroke();
  textAlign(CENTER, TOP);
  textSize(canvasWidth >= 600 ? 15 : 13);
  let msg;
  let col = 'black';
  if (challenge) {
    if (!challenge.answered) {
      msg = 'Are hole A (' + challenge.a.name + ') and hole B (' + challenge.b.name + ') connected?';
      col = 'darkmagenta';
    } else {
      msg = (challenge.correct ? 'Correct! ' : 'Not quite. ') + challenge.explain;
      col = challenge.correct ? 'darkgreen' : 'firebrick';
    }
  } else if (hover) {
    const count = holes.filter(h => lit.has(h.net)).length;
    msg = hover.name + ' is connected to ' + (count - 1) + ' other holes' +
      (lit.size > 1 ? ' (through a jumper).' : '.');
  } else {
    msg = jumperMsg;
  }
  fill(col);
  text(msg, margin, 36, canvasWidth - 2 * margin, 26);

  // Footer note under the board
  fill('dimgray');
  textSize(13);
  text('Rows a-e in a column share one strip; rows f-j share another. Each rail is one long strip.',
    margin, boardY + boardH + 8, canvasWidth - 2 * margin, 40);
}

function mousePressed() {
  if (challenge || mouseY < 0 || mouseY > drawHeight || mouseX < 0 || mouseX > canvasWidth) return;
  const h = holeAt(mouseX, mouseY);
  if (!h) return;
  if (!pending) {
    pending = h;
    jumperMsg = 'First end at ' + h.name + '. Now click the hole for the other end.';
    return;
  }
  if (pending === h) {
    pending = null;
    jumperMsg = 'Jumper cancelled.';
    return;
  }
  const already = connectedNets(pending.net, jumpers).has(h.net);
  if (jumpers.length >= 8) jumpers.shift();
  jumpers.push({ a: pending, b: h });
  jumperMsg = already
    ? 'Jumper ' + pending.name + ' to ' + h.name + ': they were ALREADY connected, so this wire changes nothing.'
    : 'Jumper ' + pending.name + ' to ' + h.name + ': these holes are now connected.';
  pending = null;
}

// ---------- Challenge mode ----------

function showChallengeButtons(on) {
  for (const b of [yesButton, noButton, nextButton]) on ? b.show() : b.hide();
}

function toggleChallenge() {
  if (challenge) {
    challenge = null;
    modeButton.html('Challenge');
    showChallengeButtons(false);
    clearButton.removeAttribute('disabled');
    return;
  }
  score = 0;
  asked = 0;
  pending = null;
  modeButton.html('Free play');
  clearButton.attribute('disabled', '');
  showChallengeButtons(true);
  newChallenge();
}

function mainHole(col, row) {
  return holes.find(h => h.kind === 'main' && h.col === col && h.row === row);
}
function railHole(rail, idx) {
  return holes.find(h => h.kind === 'rail' && h.rail === rail && h.idx === idx);
}

// Build a question from one of several common situations
function newChallenge() {
  const c = floor(random(COLS));
  const c2 = (c + 1 + floor(random(COLS - 2))) % COLS;
  const top = random() < 0.5;
  const r = top ? floor(random(5)) : 5 + floor(random(5));
  const sameHalfRow = () => (top ? floor(random(5)) : 5 + floor(random(5)));
  const kinds = ['sameStrip', 'acrossGap', 'sameRow', 'sameRail', 'twoRails', 'viaJumper', 'railToStrip'];
  const kind = random(kinds);
  let a, b, jumper = null, explain = '';
  if (kind === 'sameStrip') {
    let r2 = sameHalfRow();
    if (r2 === r) r2 = top ? (r + 1) % 5 : 5 + ((r - 4) % 5);
    a = mainHole(c, r); b = mainHole(c, r2);
    explain = 'Both holes are in column ' + (c + 1) + ' on the same side of the channel, so one metal strip joins them.';
  } else if (kind === 'acrossGap') {
    a = mainHole(c, floor(random(5))); b = mainHole(c, 5 + floor(random(5)));
    explain = 'Same column, but the center channel separates the a-e strip from the f-j strip.';
  } else if (kind === 'sameRow') {
    a = mainHole(c, r); b = mainHole(c2, r);
    explain = 'Same row letter, different columns. Strips run along columns, not rows, so these are not joined.';
  } else if (kind === 'sameRail') {
    const rail = floor(random(4));
    const i = floor(random(10));
    a = railHole(rail, i); b = railHole(rail, 15 + floor(random(10)));
    explain = 'Both holes are on the same rail, and a rail is one long strip down the whole board.';
  } else if (kind === 'twoRails') {
    a = railHole(1, floor(random(25))); b = railHole(0, floor(random(25)));
    explain = 'The + rail and the − rail are separate strips. Joining them would short the power supply!';
  } else if (kind === 'viaJumper') {
    a = mainHole(c, r);
    const r3 = top ? 5 + floor(random(5)) : floor(random(5));
    b = mainHole(c2, r3);
    const ja = mainHole(c, top ? (r + 1) % 5 : 5 + ((r - 4) % 5));
    const jb = mainHole(c2, r3 < 5 ? (r3 + 2) % 5 : 5 + ((r3 - 3) % 5));
    jumper = { a: ja, b: jb };
    explain = 'The green jumper links column ' + (c + 1) + "'s strip to column " + (c2 + 1) + "'s strip, so A and B are connected.";
  } else {
    a = railHole(top ? 1 : 2, floor(random(25)));
    b = mainHole(c, r);
    explain = 'A rail and a column strip are separate until you add a jumper wire between them.';
  }
  const conn = connectedNets(a.net, jumper ? [jumper] : []).has(b.net);
  challenge = { a, b, jumper, answered: false, correct: false, answer: conn, explain };
  yesButton.removeAttribute('disabled');
  noButton.removeAttribute('disabled');
  nextButton.attribute('disabled', '');
}

function answer(saidYes) {
  if (!challenge || challenge.answered) return;
  challenge.answered = true;
  challenge.correct = (saidYes === challenge.answer);
  asked++;
  if (challenge.correct) score++;
  yesButton.attribute('disabled', '');
  noButton.attribute('disabled', '');
  nextButton.removeAttribute('disabled');
}

function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) {
    canvasWidth = container.offsetWidth;
  }
}
