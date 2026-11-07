// Ohm's Law Explorer MicroSim
// CANVAS_HEIGHT: 495
// A battery and a resistor in one loop. Ohm's Law gives the current,
// I = V / R, and the power used is P = V * I.
// Dots travel around the loop (conventional current, + to -). Their speed
// grows with the current (square-root scale so small currents still move).
// The resistor box gets longer as the resistance goes up.

// Canvas dimensions - REQUIRED structure
let canvasWidth = 400;
let drawHeight = 380;
let controlHeight = 115;
let canvasHeight = drawHeight + controlHeight;
let margin = 20;
let sliderLeftMargin = 200;
let defaultTextSize = 16;

const NUM_DOTS = 22;
let phase = 0;              // distance the dots have moved along the loop
let isRunning = false;      // REQUIRED: MicroSims open paused
let quiz = null;            // {v, r, answered, msg, col}
let quizScore = 0, quizTries = 0;
const QUIZ_R = [10, 22, 47, 100, 150, 220, 330, 470, 680, 1000];

let startButton, quizButton, answerInput, checkButton, vSlider, rSlider;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));

  startButton = createButton('Start');
  startButton.position(10, drawHeight + 8);
  startButton.mousePressed(() => {
    isRunning = !isRunning;
    startButton.html(isRunning ? 'Pause' : 'Start');
  });

  quizButton = createButton('Quiz me');
  quizButton.position(72, drawHeight + 8);
  quizButton.mousePressed(newQuiz);

  answerInput = createInput('');
  answerInput.attribute('placeholder', 'mA');
  answerInput.size(70);
  answerInput.position(150, drawHeight + 9);
  answerInput.elt.addEventListener('keydown', e => { if (e.key === 'Enter') checkQuiz(); });

  checkButton = createButton('Check');
  checkButton.position(236, drawHeight + 8);
  checkButton.mousePressed(checkQuiz);

  vSlider = createSlider(0, 5, 3.3, 0.1);
  vSlider.position(sliderLeftMargin, drawHeight + 45);
  vSlider.size(canvasWidth - sliderLeftMargin - margin);
  vSlider.input(cancelQuiz);

  rSlider = createSlider(10, 1000, 330, 1);
  rSlider.position(sliderLeftMargin, drawHeight + 80);
  rSlider.size(canvasWidth - sliderLeftMargin - margin);
  rSlider.input(cancelQuiz);

  showQuizInputs(false);
  describe('A simple loop circuit with a battery and a resistor. Sliders set the voltage from 0 to 5 volts and the ' +
    'resistance from 10 to 1000 ohms. Readouts show the current in milliamps and the power in milliwatts. Dots ' +
    'move around the loop faster when the current is larger. The MicroSim opens paused: press Start. ' +
    'A Quiz me button hides the current and asks you to calculate it.', LABEL);
}

function showQuizInputs(on) {
  on ? answerInput.show() : answerInput.hide();
  on ? checkButton.show() : checkButton.hide();
}

function newQuiz() {
  const v = round(random(0.5, 5) * 10) / 10;
  const r = random(QUIZ_R);
  vSlider.value(v);
  rSlider.value(r);
  quiz = { v, r, answered: false, msg: 'V = ' + nf(v, 1, 1) + ' V and R = ' + r + ' Ω. Type the current in mA, then press Check.', col: 'darkblue' };
  answerInput.value('');
  showQuizInputs(true);
}

function cancelQuiz() {
  if (quiz && !quiz.answered) {
    quiz = null;
    showQuizInputs(false);
  }
}

function checkQuiz() {
  if (!quiz || quiz.answered) return;
  const guess = parseFloat(answerInput.value());
  if (isNaN(guess)) { quiz.msg = 'Type a number of milliamps, such as 12.5.'; quiz.col = 'firebrick'; return; }
  const mA = quiz.v / quiz.r * 1000;
  quizTries++;
  quiz.answered = true;
  if (abs(guess - mA) <= max(0.1, mA * 0.02)) {
    quizScore++;
    quiz.msg = 'Correct! I = ' + nf(quiz.v, 1, 1) + ' / ' + quiz.r + ' = ' + nf(mA, 1, 2) + ' mA.';
    quiz.col = 'darkgreen';
  } else {
    quiz.msg = 'Not quite. I = ' + nf(quiz.v, 1, 1) + ' / ' + quiz.r + ' = ' + nf(mA / 1000, 1, 4) + ' A = ' + nf(mA, 1, 2) + ' mA.';
    quiz.col = 'firebrick';
  }
}

// Loop geometry: a rectangle, battery on the left side, resistor on the top
function loopGeo() {
  const narrow = canvasWidth < 600;
  const left = margin + 40;
  const right = narrow ? canvasWidth - margin - 20 : canvasWidth * 0.58;
  const top = 96;
  const bottom = narrow ? 236 : 334;
  return { left, right, top, bottom, narrow };
}

// Point at distance d along the loop, going clockwise from the battery's + end
function loopPoint(g, d) {
  const w = g.right - g.left;
  const h = g.bottom - g.top;
  const per = 2 * (w + h);
  d = ((d % per) + per) % per;
  const startUp = h * 0.42;              // + terminal sits a little above the middle of the left side
  d = (d + startUp) % per;               // shift so d = 0 is at the + terminal
  // Clockwise from the bottom-left corner: up, right, down, left
  if (d < h) return { x: g.left, y: g.bottom - d };
  d -= h;
  if (d < w) return { x: g.left + d, y: g.top };
  d -= w;
  if (d < h) return { x: g.right, y: g.top + d };
  d -= h;
  return { x: g.right - d, y: g.bottom };
}

function draw() {
  updateCanvasSize();
  const v = vSlider.value();
  const r = rSlider.value();
  const amps = v / r;
  const mA = amps * 1000;
  const mW = v * amps * 1000;
  const g = loopGeo();

  // Dot speed in pixels per second: square-root scale, not to scale
  const speed = 300 * sqrt(amps / 0.5);
  if (isRunning) phase += speed * min(deltaTime, 100) / 1000;

  stroke('silver');
  strokeWeight(1);
  fill('aliceblue');
  rect(0, 0, canvasWidth, drawHeight);
  fill('white');
  rect(0, drawHeight, canvasWidth, controlHeight);

  noStroke();
  fill('black');
  textAlign(CENTER, TOP);
  textSize(g.narrow ? 19 : 22);
  text("Ohm's Law Explorer: I = V / R", canvasWidth / 2, 10);
  textSize(13);
  fill('dimgray');
  text(isRunning ? 'Dots show current flowing from + to − (speed not to scale).' : 'Paused: press Start to see the current flow.',
    canvasWidth / 2, 38);

  drawCircuit(g, v, r);
  drawDots(g);
  drawReadouts(g, v, r, mA, mW);

  // Control labels
  noStroke();
  fill('black');
  textAlign(LEFT, CENTER);
  textSize(defaultTextSize);
  text('Voltage: ' + nf(v, 1, 1) + ' V', 10, drawHeight + 55);
  text('Resistance: ' + r + ' Ω', 10, drawHeight + 90);
  if (quizTries > 0 || quiz) {
    textSize(15);
    text('Score: ' + quizScore + ' / ' + quizTries, 300, drawHeight + 20);
  }
}

function drawCircuit(g, v, r) {
  const h = g.bottom - g.top;
  const by = g.bottom - h * 0.42;   // + terminal y (matches loopPoint)
  // Resistor length grows with log(R)
  const rLen = map(log(r), log(10), log(1000), 40, min(170, (g.right - g.left) * 0.6));
  const rx = (g.left + g.right) / 2 - rLen / 2;

  // Wires (leave gaps for the battery and resistor)
  stroke('black');
  strokeWeight(3);
  noFill();
  line(g.left, g.top, rx, g.top);
  line(rx + rLen, g.top, g.right, g.top);
  line(g.right, g.top, g.right, g.bottom);
  line(g.right, g.bottom, g.left, g.bottom);
  line(g.left, g.top, g.left, by - 6);
  line(g.left, by + 16, g.left, g.bottom);

  // Battery: long plate (+) above, short plate (-) below
  strokeWeight(3);
  line(g.left - 22, by - 6, g.left + 22, by - 6);
  strokeWeight(6);
  line(g.left - 11, by + 16, g.left + 11, by + 16);
  noStroke();
  fill('black');
  textSize(16);
  textAlign(RIGHT, CENTER);
  text('+', g.left - 26, by - 8);
  text('−', g.left - 26, by + 16);
  textAlign(LEFT, CENTER);
  textSize(15);
  text(nf(v, 1, 1) + ' V', g.left + 28, by + 5);

  // Resistor: a box with a zigzag; longer box = more resistance
  stroke('saddlebrown');
  strokeWeight(2);
  fill('burlywood');
  rect(rx, g.top - 14, rLen, 28, 6);
  noFill();
  stroke('saddlebrown');
  beginShape();
  const n = max(4, floor(rLen / 14));
  vertex(rx + 4, g.top);
  for (let i = 0; i < n; i++) vertex(rx + 4 + (rLen - 8) * (i + 0.5) / n, g.top + (i % 2 === 0 ? -8 : 8));
  vertex(rx + rLen - 4, g.top);
  endShape();
  noStroke();
  fill('black');
  textAlign(CENTER, BOTTOM);
  textSize(15);
  text(r + ' Ω', rx + rLen / 2, g.top - 18);
}

function drawDots(g) {
  const w = g.right - g.left;
  const h = g.bottom - g.top;
  const per = 2 * (w + h);
  noStroke();
  for (let i = 0; i < NUM_DOTS; i++) {
    const p = loopPoint(g, phase + i * per / NUM_DOTS);
    fill(30, 144, 255, 230);
    circle(p.x, p.y, 10);
  }
}

function drawReadouts(g, v, r, mA, mW) {
  const x = g.narrow ? margin : g.right + 30;
  const y = g.narrow ? 262 : 80;
  const w = g.narrow ? canvasWidth - 2 * margin : canvasWidth - margin - x;
  const h = g.narrow ? drawHeight - y - 8 : drawHeight - y - 14;
  stroke('silver');
  strokeWeight(1);
  fill(255, 255, 255, 235);
  rect(x, y, w, h, 10);

  const hide = quiz && !quiz.answered;
  const tx = x + 12;
  noStroke();
  textAlign(LEFT, TOP);
  if (g.narrow) {
    textStyle(BOLD);
    textSize(17);
    fill('black');
    text('Current: ' + (hide ? '? mA' : nf(mA, 1, 2) + ' mA'), tx, y + 8);
    text('Power: ' + (hide ? '? mW' : nf(mW, 1, 1) + ' mW'), tx + w / 2, y + 8);
    textStyle(NORMAL);
    textSize(13);
    fill(quiz ? quiz.col : 'midnightblue');
    const msg = quiz ? quiz.msg : 'I = ' + nf(v, 1, 1) + ' V / ' + r + ' Ω = ' + nf(mA, 1, 2) + ' mA';
    text(msg, tx, y + 34, w - 24, h - 40);
    return;
  }
  fill('black');
  textSize(15);
  text('Current', tx, y + 10);
  textStyle(BOLD);
  textSize(30);
  text(hide ? '? mA' : nf(mA, 1, 2) + ' mA', tx, y + 30);
  textStyle(NORMAL);
  textSize(15);
  text('Power', tx, y + 76);
  textStyle(BOLD);
  textSize(24);
  text(hide ? '? mW' : nf(mW, 1, 1) + ' mW', tx, y + 96);
  textStyle(NORMAL);
  textSize(14);
  fill('midnightblue');
  if (!hide) {
    text('I = V / R = ' + nf(v, 1, 1) + ' / ' + r + ' = ' + nf(mA / 1000, 1, 4) + ' A', tx, y + 136, w - 24, 40);
    text('P = V × I = ' + nf(v, 1, 1) + ' × ' + nf(mA / 1000, 1, 4) + ' A', tx, y + 160, w - 24, 40);
  }
  if (quiz) {
    fill(quiz.col);
    textSize(15);
    text(quiz.msg, tx, y + 190, w - 24, h - 196);
  }
}

function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) {
    canvasWidth = container.offsetWidth;
    if (typeof vSlider !== 'undefined') {
      vSlider.size(canvasWidth - sliderLeftMargin - margin);
      rSlider.size(canvasWidth - sliderLeftMargin - margin);
    }
  }
}
