// Wrap-Around Dial MicroSim
// CANVAS_HEIGHT: 510
// A dial with n positions (12, 24 or 60). The buttons add or subtract from x,
// and the pointer lands on (x + step) % n. Predict mode asks the student to
// type the result before the pointer moves.

let canvasWidth = 400;
let drawHeight = 430;
let controlHeight = 80;
let canvasHeight = drawHeight + controlHeight;
let margin = 10;
let defaultTextSize = 16;

let n = 60;             // the modulus
let x = 58;             // current value on the dial
let shown = 58;         // pointer position used for the animation (not wrapped)
let target = 58;
let lastStep = null;    // {before, step, raw, after} for the equation panel
let pendingStep = null; // step waiting for a prediction
let feedback = '';
let feedbackColor = 'black';
let right = 0, total = 0;

let minusButton, plusButton, plusTenButton, resetButton, modSelect;
let predictCheckbox, answerInput, checkButton;

const START_VALUE = { 12: 11, 24: 22, 60: 58 };

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));

  minusButton = createButton('-1');
  minusButton.position(10, drawHeight + 8);
  minusButton.mousePressed(() => requestStep(-1));

  plusButton = createButton('+1');
  plusButton.position(50, drawHeight + 8);
  plusButton.mousePressed(() => requestStep(1));

  plusTenButton = createButton('+10');
  plusTenButton.position(90, drawHeight + 8);
  plusTenButton.mousePressed(() => requestStep(10));

  resetButton = createButton('Reset');
  resetButton.position(140, drawHeight + 8);
  resetButton.mousePressed(resetDial);

  modSelect = createSelect();
  modSelect.option('12');
  modSelect.option('24');
  modSelect.option('60');
  modSelect.selected('60');
  modSelect.position(290, drawHeight + 8);
  modSelect.changed(() => { n = int(modSelect.value()); resetDial(); });

  predictCheckbox = createCheckbox(' Predict', false);
  predictCheckbox.position(10, drawHeight + 47);
  predictCheckbox.changed(() => { pendingStep = null; feedback = ''; });

  answerInput = createInput('');
  answerInput.position(190, drawHeight + 45);
  answerInput.size(50);

  checkButton = createButton('Check');
  checkButton.position(255, drawHeight + 45);
  checkButton.mousePressed(checkAnswer);

  resetDial();
  describe('A circular dial numbered 0 to n minus 1 with a pointer on the current value x. ' +
    'Buttons add 1, subtract 1 or add 10, and the pointer moves to (x + step) % n, wrapping past 0. ' +
    'The equation is shown step by step beside the dial.', LABEL);
}

function resetDial() {
  x = START_VALUE[n];
  shown = x; target = x;
  lastStep = null;
  pendingStep = null;
  feedback = '';
  right = 0; total = 0;
  answerInput.value('');
}

function requestStep(step) {
  if (shown !== target) return;          // wait for the pointer to finish moving
  if (predictCheckbox.checked()) {
    pendingStep = step;
    answerInput.value('');
    feedback = 'Type where the pointer will land, then press Check.';
    feedbackColor = 'darkblue';
    return;
  }
  applyStep(step);
  feedback = '';
}

function applyStep(step) {
  const raw = x + step;
  const after = ((raw % n) + n) % n;       // Python's % never gives a negative answer
  lastStep = { before: x, step: step, raw: raw, after: after };
  target = shown + step;                   // animate the long way round if needed
  x = after;
}

function checkAnswer() {
  if (pendingStep === null) {
    feedback = predictCheckbox.checked() ? 'Press -1, +1 or +10 first to get a question.' :
      'Turn on Predict to check answers.';
    feedbackColor = 'firebrick';
    return;
  }
  const guess = answerInput.value().trim();
  if (guess === '' || isNaN(Number(guess))) {
    feedback = 'Type a whole number first.';
    feedbackColor = 'firebrick';
    return;
  }
  const step = pendingStep;
  pendingStep = null;
  applyStep(step);
  total++;
  if (Number(guess) === x) {
    right++;
    feedback = 'Correct! It lands on ' + x + '.';
    feedbackColor = 'darkgreen';
  } else {
    feedback = 'You said ' + guess + '. It lands on ' + x + '.';
    feedbackColor = 'firebrick';
  }
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
  textSize(24);
  text('Wrap-Around Dial', canvasWidth / 2, 8);

  // move the pointer toward its target, one small step per frame
  if (shown !== target) {
    const speed = max(0.15, abs(target - shown) * 0.08);
    shown = abs(target - shown) <= speed ? target : shown + Math.sign(target - shown) * speed;
  }

  const wide = canvasWidth >= 600;
  const cx = wide ? canvasWidth * 0.3 : canvasWidth / 2;
  const cy = wide ? 225 : 150;
  const r = wide ? min(170, canvasWidth * 0.25) : min(105, canvasWidth / 2 - 45);
  drawDial(cx, cy, r);
  if (wide) drawEquation(canvasWidth * 0.58, 55, canvasWidth * 0.42 - margin, 350);
  else drawEquation(margin, cy + r + 24, canvasWidth - 2 * margin, drawHeight - (cy + r + 30));

  // control labels
  noStroke();
  fill('black');
  textSize(16);
  textAlign(LEFT, CENTER);
  text('Modulus n:', 205, drawHeight + 18);
  text('Answer:', 120, drawHeight + 57);
  if (total > 0) text(right + ' / ' + total, 320, drawHeight + 57);
}

function angleFor(v) {
  return -HALF_PI + TWO_PI * v / n;
}

function drawDial(cx, cy, r) {
  // face
  stroke('steelblue');
  strokeWeight(3);
  fill('white');
  circle(cx, cy, 2 * r);
  // ticks and labels
  const labelEvery = n === 60 ? 5 : 1;
  for (let v = 0; v < n; v++) {
    const a = angleFor(v);
    const major = v % labelEvery === 0;
    stroke(major ? 'black' : 'gray');
    strokeWeight(major ? 2 : 1);
    const r1 = r - (major ? 12 : 7);
    line(cx + r1 * cos(a), cy + r1 * sin(a), cx + r * cos(a), cy + r * sin(a));
    if (major) {
      noStroke();
      fill(v === 0 ? 'firebrick' : 'black');
      textSize(n === 24 ? 13 : 15);
      textStyle(v === 0 ? BOLD : NORMAL);
      textAlign(CENTER, CENTER);
      const rl = r - (n === 24 ? 24 : 28);
      text(v, cx + rl * cos(a), cy + rl * sin(a));
      textStyle(NORMAL);
    }
  }
  // arc showing the last move
  if (lastStep) {
    const a1 = angleFor(lastStep.before);
    const a2 = angleFor(lastStep.before + (shown - (target - lastStep.step)));
    noFill();
    stroke(255, 140, 0, 160);
    strokeWeight(8);
    if (a2 > a1) arc(cx, cy, 2 * (r + 9), 2 * (r + 9), a1, a2);
    else if (a2 < a1) arc(cx, cy, 2 * (r + 9), 2 * (r + 9), a2, a1);
  }
  // pointer
  const a = angleFor(shown);
  stroke('darkorange');
  strokeWeight(5);
  line(cx, cy, cx + (r - 60) * cos(a), cy + (r - 60) * sin(a));
  noStroke();
  fill('darkorange');
  circle(cx, cy, 14);
  // value in a bubble at the pointer tip
  const vx = cx + (r - 60) * cos(a), vy = cy + (r - 60) * sin(a);
  fill('darkorange');
  circle(vx, vy, 34);
  fill('white');
  textSize(16);
  textStyle(BOLD);
  textAlign(CENTER, CENTER);
  const shownValue = ((Math.round(shown) % n) + n) % n;
  text(shownValue, vx, vy + 1);
  textStyle(NORMAL);
}

function drawEquation(px, py, pw, ph) {
  stroke('silver');
  strokeWeight(1);
  fill('white');
  rect(px, py, pw, ph, 8);
  noStroke();
  const wide = canvasWidth >= 600;
  const lh = wide ? 30 : 22;
  let y = py + 10;
  textAlign(LEFT, TOP);
  textFont('monospace');
  textSize(wide ? 18 : 16);

  if (pendingStep !== null) {
    fill('darkblue');
    text('x = ' + x, px + 12, y); y += lh;
    text('(' + x + (pendingStep < 0 ? ' - ' : ' + ') + abs(pendingStep) + ') % ' + n + ' = ?', px + 12, y);
    y += lh;
  } else if (lastStep) {
    const s = lastStep;
    const op = s.step < 0 ? ' - ' : ' + ';
    fill('black');
    text('x = (x' + op + abs(s.step) + ') % ' + n, px + 12, y); y += lh;
    text('  = (' + s.before + op + abs(s.step) + ') % ' + n, px + 12, y); y += lh;
    if (wide) { text('  = ' + s.raw + ' % ' + n, px + 12, y); y += lh; }
    fill('darkorange');
    textStyle(BOLD);
    text('  = ' + s.after, px + 12, y); y += lh;
    textStyle(NORMAL);
  } else {
    fill('black');
    text('x = ' + x, px + 12, y); y += lh;
    text('x = (x + step) % ' + n, px + 12, y); y += lh;
  }
  textFont('sans-serif');
  textSize(16);

  // plain-English explanation
  let note = '';
  if (pendingStep === null && lastStep) {
    const s = lastStep;
    if (s.raw >= n) note = s.raw + ' is past ' + (n - 1) + ', so it wraps: ' + s.raw + ' - ' + n + ' = ' + s.after + '.';
    else if (s.raw < 0) note = s.raw + ' is below 0. Python\'s % still gives ' + s.after + ', so the pointer wraps backward.';
    else note = s.raw + ' is between 0 and ' + (n - 1) + ', so no wrap is needed.';
  } else if (pendingStep === null) {
    note = 'Press -1, +1 or +10. The answer is always between 0 and ' + (n - 1) + '.';
  }
  fill('black');
  if (note) { text(note, px + 12, y + 4, pw - 24); y += wide ? 70 : 42; }
  if (feedback) {
    fill(feedbackColor);
    textStyle(BOLD);
    text(feedback, px + 12, y + 4, pw - 24);
    textStyle(NORMAL);
  }
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
