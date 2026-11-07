// Resistor Color Code Decoder MicroSim
// CANVAS_HEIGHT: 420
// A large four-band resistor. Band 1 and band 2 are digits, band 3 is the
// multiplier (a power of ten), and band 4 is the tolerance.
//   value = (10 * digit1 + digit2) * multiplier
// Click a band to cycle its color. Two quiz modes: read a random resistor
// and type its value, or set the bands to match a value.

// Canvas dimensions - REQUIRED structure
let canvasWidth = 400;
let drawHeight = 340;
let controlHeight = 80;
let canvasHeight = drawHeight + controlHeight;
let margin = 20;
let defaultTextSize = 16;

// Color code lookup tables
const DIGITS = [
  { name: 'black', c: [20, 20, 20] }, { name: 'brown', c: [120, 70, 30] },
  { name: 'red', c: [210, 30, 30] }, { name: 'orange', c: [245, 130, 20] },
  { name: 'yellow', c: [245, 220, 20] }, { name: 'green', c: [30, 150, 60] },
  { name: 'blue', c: [30, 80, 210] }, { name: 'violet', c: [140, 60, 190] },
  { name: 'gray', c: [140, 140, 140] }, { name: 'white', c: [250, 250, 250] }
];
const MULTS = [
  { name: 'black', m: 1, c: [20, 20, 20] }, { name: 'brown', m: 10, c: [120, 70, 30] },
  { name: 'red', m: 100, c: [210, 30, 30] }, { name: 'orange', m: 1e3, c: [245, 130, 20] },
  { name: 'yellow', m: 1e4, c: [245, 220, 20] }, { name: 'green', m: 1e5, c: [30, 150, 60] },
  { name: 'blue', m: 1e6, c: [30, 80, 210] }, { name: 'gold', m: 0.1, c: [212, 175, 55] },
  { name: 'silver', m: 0.01, c: [192, 192, 200] }
];
const TOLS = [
  { name: 'gold', t: 5, c: [212, 175, 55] }, { name: 'silver', t: 10, c: [192, 192, 200] },
  { name: 'brown', t: 1, c: [120, 70, 30] }, { name: 'red', t: 2, c: [210, 30, 30] }
];
const E12 = [10, 12, 15, 18, 22, 27, 33, 39, 47, 56, 68, 82];

// Band state: indexes into the tables. Start at 330 ohms, gold (+/-5%).
let bands = [3, 3, 1, 0];

let mode = 'explore';   // 'explore' | 'read' | 'set'
let answered = true;    // in quiz modes: has the current question been checked?
let feedback = '';
let feedbackColor = 'black';
let score = 0, tries = 0;
let modeSelect, randomButton, valueInput, checkButton;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));

  modeSelect = createSelect();
  modeSelect.option('Explore', 'explore');
  modeSelect.option('Quiz: read the bands', 'read');
  modeSelect.option('Quiz: set the bands', 'set');
  modeSelect.position(10, drawHeight + 10);
  modeSelect.changed(changeMode);

  randomButton = createButton('Random resistor');
  randomButton.position(185, drawHeight + 9);
  randomButton.mousePressed(newQuestion);

  valueInput = createInput('');
  valueInput.attribute('placeholder', 'e.g. 4.7k');
  valueInput.size(110);
  valueInput.position(110, drawHeight + 46);
  valueInput.elt.addEventListener('keydown', e => { if (e.key === 'Enter') checkAnswer(); });

  checkButton = createButton('Check');
  checkButton.position(240, drawHeight + 45);
  checkButton.mousePressed(checkAnswer);

  changeMode();
  describe('A large four-band resistor drawing. Clicking a band cycles its color. A readout shows the resistance ' +
    'and tolerance, for example 330 ohms plus or minus 5 percent. Quiz modes ask you to read a random resistor ' +
    'or to set the bands to match a value, with a score counter.', LABEL);
}

function bandValue() {
  return (10 * bands[0] + bands[1]) * MULTS[bands[2]].m;
}

function fmtOhms(v) {
  const r = n => parseFloat(n.toPrecision(3)).toString();
  if (v >= 1e6) return r(v / 1e6) + ' MΩ';
  if (v >= 1e3) return r(v / 1e3) + ' kΩ';
  return r(v) + ' Ω';
}

// Read values such as 330, 4.7k, 4k7, 1M, 2.2 kΩ
function parseOhms(s) {
  s = s.trim().replace(/\u03A9|ohms?/gi, '').replace(/\s+/g, '').toLowerCase();
  const mult = u => (u === 'k' ? 1e3 : (u === 'm' ? 1e6 : 1));
  let m = s.match(/^(\d+)([kmr])(\d+)$/);          // "4k7" style
  if (m) return parseFloat(m[1] + '.' + m[3]) * mult(m[2]);
  m = s.match(/^(\d*\.?\d+)([km]?)$/);              // "4.7k" or "470" style
  if (m) return parseFloat(m[1]) * mult(m[2]);
  return NaN;
}

function randomBands() {
  const pair = random(E12);
  return [floor(pair / 10), pair % 10, floor(random(5)), floor(random(4))];
}

let target = null;   // set-mode target in ohms

function newQuestion() {
  if (mode === 'explore') {
    bands = randomBands();
    return;
  }
  answered = false;
  feedback = '';
  valueInput.value('');
  if (mode === 'read') {
    bands = randomBands();
    feedback = 'What is this resistor’s value? Type it below and press Check.';
  } else {
    const b = randomBands();
    target = (10 * b[0] + b[1]) * MULTS[b[2]].m;
    valueInput.value(fmtOhms(target).replace(' ', ''));
    bands = [1, 0, 0, 0];
    feedback = 'Click the bands to make ' + fmtOhms(target) + ', then press Check. (You may type your own value in the box.)';
  }
  feedbackColor = 'darkblue';
}

function changeMode() {
  mode = modeSelect.value();
  score = 0;
  tries = 0;
  if (mode === 'explore') {
    valueInput.hide();
    checkButton.hide();
    answered = true;
    feedback = 'Click any band to change its color.';
    feedbackColor = 'dimgray';
  } else {
    valueInput.show();
    checkButton.show();
    newQuestion();
  }
}

function checkAnswer() {
  if (mode === 'explore' || answered) return;
  const actual = bandValue();
  if (mode === 'read') {
    const guess = parseOhms(valueInput.value());
    if (isNaN(guess)) { feedback = 'Type a number such as 470, 4.7k, or 1M.'; feedbackColor = 'firebrick'; return; }
    tries++;
    if (abs(guess - actual) <= actual * 0.005) {
      score++;
      feedback = 'Correct! ' + explain() + ' Press Random resistor for another.';
      feedbackColor = 'darkgreen';
    } else {
      feedback = 'Not quite: you typed ' + fmtOhms(guess) + '. ' + explain() + ' Press Random resistor to try another.';
      feedbackColor = 'firebrick';
    }
  } else {
    const want = parseOhms(valueInput.value());
    if (isNaN(want)) { feedback = 'Type a target such as 470, 4.7k, or 1M.'; feedbackColor = 'firebrick'; return; }
    tries++;
    if (abs(want - actual) <= want * 0.005) {
      score++;
      feedback = 'Correct! ' + explain() + ' Press Random resistor for another.';
      feedbackColor = 'darkgreen';
    } else {
      feedback = 'Not yet: your bands make ' + fmtOhms(actual) + ', not ' + fmtOhms(want) + '. Press Random resistor to try another.';
      feedbackColor = 'firebrick';
    }
  }
  answered = true;
}

function explain() {
  const d1 = DIGITS[bands[0]].name, d2 = DIGITS[bands[1]].name, m = MULTS[bands[2]];
  return d1 + '-' + d2 + ' = ' + (10 * bands[0] + bands[1]) + ', ' + m.name + ' = ×' + fmtMult(m.m) + ', so ' + fmtOhms(bandValue()) + '.';
}

function fmtMult(m) {
  if (m >= 1e6) return (m / 1e6) + 'M';
  if (m >= 1e3) return (m / 1e3) + 'k';
  return String(m);
}

// Resistor geometry (recomputed every frame)
function geo() {
  const bodyW = min(canvasWidth - 100, 520);
  const bodyH = min(96, bodyW * 0.22);
  const bx = (canvasWidth - bodyW) / 2;
  const by = 60;
  const bw = bodyW * 0.075;
  const xs = [0.17, 0.31, 0.45, 0.78].map(f => bx + f * bodyW);
  return { bodyW, bodyH, bx, by, bw, xs };
}

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
  textSize(canvasWidth >= 600 ? 22 : 19);
  text('Resistor Color Code Decoder', canvasWidth / 2, 10);

  const g = geo();
  // Leads
  stroke('gray');
  strokeWeight(5);
  line(8, g.by + g.bodyH / 2, canvasWidth - 8, g.by + g.bodyH / 2);
  // Body
  stroke('burlywood');
  strokeWeight(2);
  fill(232, 206, 160);
  rect(g.bx, g.by, g.bodyW, g.bodyH, g.bodyH / 2.5);

  // Bands
  const hover = bandAt(mouseX, mouseY);
  const cols = [DIGITS[bands[0]].c, DIGITS[bands[1]].c, MULTS[bands[2]].c, TOLS[bands[3]].c];
  const names = [DIGITS[bands[0]].name, DIGITS[bands[1]].name, MULTS[bands[2]].name, TOLS[bands[3]].name];
  const roles = canvasWidth >= 600 ? ['1st digit', '2nd digit', 'Multiplier', 'Tolerance'] : ['1st', '2nd', 'Mult.', 'Tol.'];
  for (let i = 0; i < 4; i++) {
    stroke(i === hover ? 'orange' : 'dimgray');
    strokeWeight(i === hover ? 3 : 1);
    fill(cols[i]);
    rect(g.xs[i] - g.bw / 2, g.by + 2, g.bw, g.bodyH - 4, 2);
    noStroke();
    fill('black');
    textAlign(CENTER, TOP);
    textSize(canvasWidth >= 600 ? 14 : 11);
    text(roles[i], g.xs[i], g.by + g.bodyH + 8);
    textStyle(BOLD);
    text(names[i], g.xs[i], g.by + g.bodyH + 26);
    textStyle(NORMAL);
  }

  // Readout (hidden while a quiz question is open)
  const ry = g.by + g.bodyH + 58;
  textAlign(CENTER, TOP);
  if (mode === 'explore' || answered) {
    textStyle(BOLD);
    textSize(canvasWidth >= 600 ? 34 : 26);
    fill('black');
    text(fmtOhms(bandValue()) + '  ±' + TOLS[bands[3]].t + '%', canvasWidth / 2, ry);
    textStyle(NORMAL);
    textSize(canvasWidth >= 600 ? 15 : 13);
    fill('midnightblue');
    text((10 * bands[0] + bands[1]) + ' × ' + fmtMult(MULTS[bands[2]].m) + ' = ' + fmtOhms(bandValue()),
      canvasWidth / 2, ry + 42);
  } else {
    textStyle(BOLD);
    textSize(canvasWidth >= 600 ? 34 : 26);
    fill('silver');
    text('? Ω', canvasWidth / 2, ry);
    textStyle(NORMAL);
  }

  // Feedback / instructions
  fill(feedbackColor);
  textSize(canvasWidth >= 600 ? 15 : 13);
  text(feedback, margin, ry + 66, canvasWidth - 2 * margin, 60);

  // Control labels
  noStroke();
  fill('black');
  textAlign(LEFT, CENTER);
  textSize(defaultTextSize);
  if (mode !== 'explore') {
    text('Your value:', 10, drawHeight + 58);
    text('Score: ' + score + ' / ' + tries, 305, drawHeight + 58);
  }
}

function bandAt(mx, my) {
  if (my < 0 || my > drawHeight) return -1;
  const g = geo();
  for (let i = 0; i < 4; i++) {
    if (abs(mx - g.xs[i]) <= g.bw / 2 + 4 && my >= g.by - 4 && my <= g.by + g.bodyH + 4) return i;
  }
  return -1;
}

function mousePressed() {
  const i = bandAt(mouseX, mouseY);
  if (i < 0) return;
  if (mode === 'read') return;                 // reading quiz: bands are fixed
  if (mode === 'set' && answered) return;      // wait for the next question
  if (i === 0) bands[0] = bands[0] % 9 + 1;    // first digit is never black
  if (i === 1) bands[1] = (bands[1] + 1) % 10;
  if (i === 2) bands[2] = (bands[2] + 1) % MULTS.length;
  if (i === 3) bands[3] = (bands[3] + 1) % TOLS.length;
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
