// Mondaine railway clock: normalized dial geometry, deterministic stop-to-go cycle.
// CANVAS_HEIGHT: 580
let canvasWidth = 400;
let drawHeight = 500;
let controlHeight = 80;
let canvasHeight = drawHeight + controlHeight;
let margin = 25;
let sliderLeftMargin = 120;
let defaultTextSize = 16;
let startButton, replayButton, speedSlider;
let isRunning = false;
let elapsed = 0;
let lastTick = 0;
const BASE_MINUTES = 10 * 60 + 10;
const SWEEP = 58;
const ADVANCE_AT = 59;

// All angles derive from elapsed time, so skipped frames cannot lose a minute step.
function clockState(seconds) {
  const cycle = Math.floor(seconds / 60);
  const phase = seconds - cycle * 60;
  const advanced = phase >= ADVANCE_AT ? 1 : 0;
  const minutes = BASE_MINUTES + cycle + advanced;
  return { phase, holding: phase >= SWEEP,
    second: Math.min(phase / SWEEP, 1) * 360,
    minute: (minutes % 60) * 6,
    hour: (minutes % 720) * 0.5,
    minutes };
}

function setup() {
  updateCanvasSize();
  const main = document.querySelector('main');
  createCanvas(canvasWidth, canvasHeight).parent(main);
  startButton = createButton('Start');
  startButton.parent(main);
  startButton.position(10, drawHeight + 5);
  startButton.size(90, 28);
  startButton.mousePressed(() => {
    isRunning = !isRunning;
    lastTick = performance.now();
    startButton.html(isRunning ? 'Pause' : 'Start');
  });
  replayButton = createButton('Replay pause');
  replayButton.parent(main);
  replayButton.position(110, drawHeight + 5);
  replayButton.size(135, 28);
  replayButton.mousePressed(() => {
    elapsed = Math.floor(elapsed / 60) * 60 + 55;
    lastTick = performance.now();
  });
  speedSlider = createSlider(1, 10, 1, 1);
  speedSlider.parent(main);
  speedSlider.attribute('aria-label', 'Playback speed');
  speedSlider.position(sliderLeftMargin, drawHeight + 40);
  speedSlider.size(Math.max(60, canvasWidth - sliderLeftMargin - margin));
  for (const control of [startButton, replayButton]) control.style('font-size', '16px');
  describe('Swiss railway dial with sixty black marks, tapered black hour and minute hands, and a red paddle second hand. Start playback to observe a 58-second sweep, two-second stop at twelve, and a minute and hour step during the stop.');
  lastTick = performance.now();
}

function draw() {
  updateCanvasSize();
  const now = performance.now();
  if (isRunning && !document.hidden) elapsed += (now - lastTick) / 1000 * speedSlider.value();
  lastTick = now;
  const state = clockState(elapsed);
  background('white');
  stroke('silver'); strokeWeight(1); fill('aliceblue');
  rect(0, 0, canvasWidth - 1, drawHeight);
  fill('white'); rect(0, drawHeight, canvasWidth - 1, controlHeight - 1);
  fill('black'); textAlign(CENTER, TOP); textSize(canvasWidth < 380 ? 20 : 25);
  noStroke(); text('Swiss railway clock', canvasWidth / 2, 14);
  textSize(16); fill('dimgray');
  noStroke(); text('1952 dial study · stop-to-go motion', canvasWidth / 2, 47);
  const diameter = Math.min(canvasWidth - 36, 360);
  push(); translate(canvasWidth / 2, 255); scale(diameter / 100);
  // One unit a = 1/100 dial diameter. See accompanying source notes.
  fill('silver'); noStroke(); circle(0, 0, 104);
  fill('white'); circle(0, 0, 100);
  for (let i = 0; i < 60; i++) {
    push(); rotate(i * Math.PI / 30);
    const major = i % 5 === 0;
    const inner = major ? 36.5 : 45;
    const halfWidth = major ? 1.75 : 0.7;
    fill('black'); noStroke();
    rect(-halfWidth, -48.5, halfWidth * 2, 48.5 - inner);
    pop();
  }
  drawHand(state.hour, -12, 3.2, 32, 2.6);
  drawHand(state.minute, -12, 2.6, 46, 1.8);
  push(); rotate(state.second * Math.PI / 180);
  noStroke(); fill('red'); rect(-0.7, -31.25, 1.4, 47.75);
  circle(0, -31.25, 10.5); circle(0, 0, 3.5); pop();
  pop();
  textSize(16); textAlign(CENTER, TOP);
  fill('black');
  const status = !isRunning ? 'Paused — press Start' : state.holding ? 'HOLD AT 12' : 'SMOOTH SWEEP';
  noStroke(); text(status, canvasWidth / 2, 451);
  const time = `${String(Math.floor(state.minutes / 60) % 24).padStart(2, '0')}:${String(state.minutes % 60).padStart(2, '0')}`;
  noStroke(); text(`${time}  ·  Cycle ${state.phase.toFixed(1)} / 60 s`, canvasWidth / 2, 475);
  fill('black'); textAlign(LEFT, CENTER); textSize(defaultTextSize);
  noStroke(); text(`Speed: ${speedSlider.value()}×`, 10, drawHeight + 53);
}

function drawHand(degrees, tail, tailWidth, tip, tipWidth) {
  push(); rotate(degrees * Math.PI / 180); fill('black'); noStroke();
  quad(-tailWidth, -tail, tailWidth, -tail, tipWidth, -tip, -tipWidth, -tip);
  pop();
}

function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
  speedSlider.size(Math.max(60, canvasWidth - sliderLeftMargin - margin));
  redraw();
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) {
    const nextWidth = Math.floor(container.getBoundingClientRect().width);
    if (nextWidth !== canvasWidth) {
      canvasWidth = nextWidth;
      if (typeof width !== 'undefined' && typeof resizeCanvas === 'function' && startButton) resizeCanvas(canvasWidth, canvasHeight);
      if (speedSlider) speedSlider.size(Math.max(60, canvasWidth - sliderLeftMargin - margin));
    }
  }
}
