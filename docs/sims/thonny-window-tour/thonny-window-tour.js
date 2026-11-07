// Thonny Window Tour MicroSim
// CANVAS_HEIGHT: 565
// A drawn mockup of the Thonny IDE with seven numbered hotspots. Hover a
// hotspot to see its name; click it for a short description and a "Try this"
// step. "Quiz me" mode asks a question and the student clicks the right area.

let canvasWidth = 400;
let drawHeight = 520;
let controlHeight = 45;
let canvasHeight = drawHeight + controlHeight;
let margin = 10;
let defaultTextSize = 16;

// Hotspot rectangles are stored as fractions (0 to 1) of the mockup window,
// so they stay on the right part of the drawing at any canvas width.
const HOTSPOTS = [
  { id: 1, name: 'Interpreter selector', x: 0.56, y: 0.925, w: 0.435, h: 0.07,
    desc: 'This corner menu tells Thonny which Python runs your code. Choose ' +
      '"MicroPython (Raspberry Pi Pico)" so programs run on the Pico, not on your laptop.',
    tryThis: 'Click the corner menu and check that it names the Raspberry Pi Pico and a USB port.' },
  { id: 2, name: 'Editor', x: 0.285, y: 0.25, w: 0.71, h: 0.37,
    desc: 'The editor is where you write and change a whole program. Code here does nothing ' +
      'until you press Run, and you can save it to your computer or to the Pico.',
    tryThis: 'Type print("hello, clock") on line 1 and save the file as hello.py.' },
  { id: 3, name: 'Run button', x: 0.205, y: 0.13, w: 0.075, h: 0.105,
    desc: 'The green Run button (or the F5 key) sends the program in the editor to the Pico ' +
      'and starts it. Anything the program prints appears in the Shell.',
    tryThis: 'Press Run and look for your message in the Shell below the editor.' },
  { id: 4, name: 'Stop button', x: 0.47, y: 0.13, w: 0.075, h: 0.105,
    desc: 'The red Stop button (or Ctrl+C) interrupts a running program and gives you back ' +
      'the >>> prompt. Use it when a loop runs forever.',
    tryThis: 'Run a while True: loop, then press Stop to get the prompt back.' },
  { id: 5, name: 'Shell (REPL)', x: 0.285, y: 0.635, w: 0.71, h: 0.28,
    desc: 'The Shell is the REPL: type one line after >>> and the Pico runs it right away. ' +
      'It also shows everything your program prints, including error messages.',
    tryThis: 'Click after >>>, type 2 + 3 and press Enter. The Pico answers 5.' },
  { id: 6, name: 'Files: This computer', x: 0.005, y: 0.25, w: 0.27, h: 0.33,
    desc: 'This pane lists files saved on your laptop. A program stored here runs on the Pico ' +
      'only while Thonny is connected and you press Run.',
    tryThis: 'Open View > Files if this pane is hidden, then find the folder with your labs.' },
  { id: 7, name: 'Files: MicroPython device', x: 0.005, y: 0.585, w: 0.27, h: 0.33,
    desc: 'This pane lists files stored in the Pico\'s own flash memory. A file named main.py ' +
      'here runs by itself every time the Pico powers up, even with no computer attached.',
    tryThis: 'Right-click hello.py in the top pane and choose "Upload to /" to copy it to the Pico.' }
];

const QUESTIONS = [
  { q: 'Where would you type a quick test line?', answer: 5 },
  { q: 'Which button starts the program in the editor?', answer: 3 },
  { q: 'Where do you write a program you want to save?', answer: 2 },
  { q: 'How do you interrupt a loop that never ends?', answer: 4 },
  { q: 'Where do you choose MicroPython (Raspberry Pi Pico)?', answer: 1 },
  { q: 'Where would main.py go so the clock starts without a computer?', answer: 7 },
  { q: 'Where are the files saved on your laptop?', answer: 6 }
];

let selected = null;      // hotspot clicked in explore mode
let quizCheckbox, nextButton;
let quizIndex = 0;
let quizOrder = [];
let quizFeedback = '';
let quizFeedbackColor = 'black';
let quizRight = 0, quizTotal = 0;
let quizAnswered = false;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));

  quizCheckbox = createCheckbox(' Quiz me', false);
  quizCheckbox.position(10, drawHeight + 12);
  quizCheckbox.changed(startQuiz);

  nextButton = createButton('Next question');
  nextButton.position(110, drawHeight + 10);
  nextButton.mousePressed(nextQuestion);
  nextButton.attribute('disabled', '');
  startQuiz();

  describe('A labeled mockup of the Thonny editor window with seven numbered hotspots: interpreter ' +
    'selector, editor, Run button, Stop button, Shell, and the two Files panes for This computer and ' +
    'the MicroPython device. Clicking a hotspot shows what it is for.', LABEL);
}

function startQuiz() {
  quizRight = 0; quizTotal = 0;
  quizOrder = shuffle([...Array(QUESTIONS.length).keys()]);
  quizIndex = 0;
  quizAnswered = false;
  quizFeedback = '';
  selected = null;
  if (quizCheckbox.checked()) nextButton.removeAttribute('disabled');
  else nextButton.attribute('disabled', '');
}

function nextQuestion() {
  if (!quizCheckbox.checked()) return;
  quizIndex = (quizIndex + 1) % quizOrder.length;
  quizAnswered = false;
  quizFeedback = '';
  selected = null;
}

// ---------- geometry ----------
function mockRect() {
  const h = canvasWidth < 600 ? 250 : 320;
  return { x: margin, y: 45, w: canvasWidth - 2 * margin, h: h };
}

function toPx(m, nx, ny, nw, nh) {
  return { x: m.x + nx * m.w, y: m.y + ny * m.h, w: nw * m.w, h: nh * m.h };
}

function hotspotAt(px, py) {
  const m = mockRect();
  // test the small buttons first so they win over larger areas
  const ordered = [...HOTSPOTS].sort((a, b) => a.w * a.h - b.w * b.h);
  for (const hs of ordered) {
    const r = toPx(m, hs.x, hs.y, hs.w, hs.h);
    if (px >= r.x && px <= r.x + r.w && py >= r.y && py <= r.y + r.h) return hs;
  }
  return null;
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
  text('Thonny Window Tour', canvasWidth / 2, 10);

  const m = mockRect();
  drawMockup(m);

  const hover = (mouseY < drawHeight) ? hotspotAt(mouseX, mouseY) : null;
  drawHotspots(m, hover);
  drawInfoPanel(m);
  if (hover && !quizCheckbox.checked()) drawTooltip(hover.name);
  cursor(hover ? HAND : ARROW);

  if (quizCheckbox.checked() && quizTotal > 0) {
    noStroke();
    fill('black');
    textSize(16);
    textAlign(LEFT, CENTER);
    text('Score: ' + quizRight + ' / ' + quizTotal, 245, drawHeight + 22);
  }
}

// A simplified drawing of the Thonny window
function drawMockup(m) {
  const ts = constrain(m.w / 55, 10, 14);
  // window frame
  stroke('gray');
  fill('white');
  rect(m.x, m.y, m.w, m.h, 6);
  // title bar
  const tb = toPx(m, 0, 0, 1, 0.07);
  noStroke();
  fill(225);
  rect(tb.x + 1, tb.y + 1, tb.w - 2, tb.h, 6, 6, 0, 0);
  const dots = ['tomato', 'gold', 'mediumseagreen'];
  for (let i = 0; i < 3; i++) {
    fill(dots[i]);
    circle(tb.x + 12 + i * 14, tb.y + tb.h / 2 + 1, 9);
  }
  fill(60);
  textSize(ts);
  textAlign(CENTER, CENTER);
  text('Thonny  -  /Users/you/labs/hello.py  @  1 : 1', tb.x + tb.w / 2, tb.y + tb.h / 2 + 1);
  // menu bar
  const mb = toPx(m, 0, 0.07, 1, 0.055);
  fill(245);
  rect(mb.x + 1, mb.y, mb.w - 2, mb.h);
  fill(40);
  textAlign(LEFT, CENTER);
  text('File   Edit   View   Run   Tools   Help', mb.x + 10, mb.y + mb.h / 2);
  // toolbar with icons
  const bar = toPx(m, 0, 0.125, 1, 0.115);
  fill(238);
  rect(bar.x + 1, bar.y, bar.w - 2, bar.h);
  const iconY = bar.y + bar.h / 2;
  const iconR = min(bar.h * 0.7, 28);
  drawToolIcon(toPx(m, 0.03, 0, 0, 0).x, iconY, iconR, 'new');
  drawToolIcon(toPx(m, 0.09, 0, 0, 0).x, iconY, iconR, 'open');
  drawToolIcon(toPx(m, 0.15, 0, 0, 0).x, iconY, iconR, 'save');
  drawToolIcon(toPx(m, 0.2425, 0, 0, 0).x, iconY, iconR, 'run');
  drawToolIcon(toPx(m, 0.32, 0, 0, 0).x, iconY, iconR, 'debug');
  drawToolIcon(toPx(m, 0.38, 0, 0, 0).x, iconY, iconR, 'step');
  drawToolIcon(toPx(m, 0.5075, 0, 0, 0).x, iconY, iconR, 'stop');

  // Files panes
  const top = toPx(m, 0.005, 0.25, 0.27, 0.33);
  const bot = toPx(m, 0.005, 0.585, 0.27, 0.33);
  drawFilePane(top, 'This computer', ['labs/', 'hello.py', 'clock.py'], ts);
  drawFilePane(bot, 'MicroPython device', ['lib/', 'main.py', 'config.py'], ts);

  // Editor
  const ed = toPx(m, 0.285, 0.25, 0.71, 0.37);
  stroke(200);
  fill('white');
  rect(ed.x, ed.y, ed.w, ed.h);
  noStroke();
  fill(230);
  rect(ed.x + 1, ed.y + 1, min(90, ed.w * 0.3), ts + 8);
  fill(40);
  textAlign(LEFT, CENTER);
  textSize(ts);
  text('hello.py', ed.x + 8, ed.y + 1 + (ts + 8) / 2);
  const code = ['NAME = "hello.py"', 'print("hello, clock")', 'hour = 15', 'print(hour * 60)'];
  textFont('monospace');
  const lh = (ed.h - ts - 14) / 5;
  for (let i = 0; i < code.length; i++) {
    const y = ed.y + ts + 14 + i * lh + lh / 2;
    fill('gray');
    textAlign(RIGHT, CENTER);
    text(i + 1, ed.x + 22, y);
    fill(i === 1 ? 'darkgreen' : 'black');
    textAlign(LEFT, CENTER);
    text(code[i], ed.x + 30, y);
  }
  textFont('sans-serif');

  // Shell
  const sh = toPx(m, 0.285, 0.635, 0.71, 0.28);
  stroke(200);
  fill(250);
  rect(sh.x, sh.y, sh.w, sh.h);
  noStroke();
  fill(230);
  rect(sh.x + 1, sh.y + 1, 60, ts + 8);
  fill(40);
  textAlign(LEFT, CENTER);
  text('Shell', sh.x + 8, sh.y + 1 + (ts + 8) / 2);
  textFont('monospace');
  const shellLines = ['MicroPython v1.24.1; Raspberry Pi Pico', '>>> %Run -c $EDITOR_CONTENT',
    'hello, clock', '>>> |'];
  const slh = (sh.h - ts - 12) / 4;
  for (let i = 0; i < shellLines.length; i++) {
    fill(i === 2 ? 'darkgreen' : 40);
    text(shellLines[i], sh.x + 8, sh.y + ts + 12 + i * slh + slh / 2, sh.w - 12);
  }
  textFont('sans-serif');

  // status bar with interpreter selector
  const st = toPx(m, 0, 0.925, 1, 0.075);
  fill(235);
  rect(st.x + 1, st.y, st.w - 2, st.h - 1, 0, 0, 6, 6);
  fill(40);
  textAlign(RIGHT, CENTER);
  textSize(ts);
  text('MicroPython (Raspberry Pi Pico)  -  Board CDC @ COM3  v', st.x + st.w - 26, st.y + st.h / 2);
}

function drawFilePane(r, title, files, ts) {
  stroke(200);
  fill('white');
  rect(r.x, r.y, r.w, r.h);
  noStroke();
  fill(225);
  rect(r.x + 1, r.y + 1, r.w - 2, ts + 8);
  fill(30);
  textAlign(LEFT, CENTER);
  textStyle(BOLD);
  // shrink the pane title until it fits beside the numbered badge
  let hs = ts;
  textSize(hs);
  while (textWidth(title) > r.w - 32 && hs > 8) { hs -= 0.5; textSize(hs); }
  text(title, r.x + 6, r.y + 1 + (ts + 8) / 2);
  textStyle(NORMAL);
  textSize(ts);
  const lh = (r.h - ts - 10) / (files.length + 0.5);
  for (let i = 0; i < files.length; i++) {
    fill(files[i].endsWith('/') ? 'saddlebrown' : 40);
    text(files[i], r.x + 12, r.y + ts + 10 + (i + 0.5) * lh);
  }
}

function drawToolIcon(x, y, s, kind) {
  push();
  rectMode(CENTER);
  if (kind === 'run') {
    noStroke();
    fill('forestgreen');
    circle(x, y, s);
    fill('white');
    triangle(x - s * 0.15, y - s * 0.25, x - s * 0.15, y + s * 0.25, x + s * 0.28, y);
  } else if (kind === 'stop') {
    noStroke();
    fill('firebrick');
    circle(x, y, s);
    fill('white');
    rect(x, y, s * 0.4, s * 0.4);
  } else if (kind === 'new') {
    stroke(90); fill('white');
    rect(x, y, s * 0.6, s * 0.8);
  } else if (kind === 'open') {
    stroke(90); fill('khaki');
    rect(x, y + s * 0.05, s * 0.85, s * 0.6, 2);
  } else if (kind === 'save') {
    stroke(90); fill('steelblue');
    rect(x, y, s * 0.75, s * 0.75, 2);
    fill('white'); noStroke();
    rect(x, y - s * 0.15, s * 0.45, s * 0.25);
  } else if (kind === 'debug') {
    noStroke(); fill('darkslateblue');
    ellipse(x, y, s * 0.5, s * 0.75);
  } else if (kind === 'step') {
    stroke('darkslateblue'); strokeWeight(3); noFill();
    arc(x, y, s * 0.6, s * 0.6, PI, TWO_PI);
    strokeWeight(1);
  }
  pop();
}

function drawHotspots(m, hover) {
  const quiz = quizCheckbox.checked();
  const q = quiz ? QUESTIONS[quizOrder[quizIndex]] : null;
  for (const hs of HOTSPOTS) {
    const r = toPx(m, hs.x, hs.y, hs.w, hs.h);
    const isSel = selected && selected.id === hs.id;
    const showAnswer = quiz && quizAnswered && q.answer === hs.id;
    if (hover && hover.id === hs.id) {
      stroke('darkorange'); strokeWeight(3); fill(255, 200, 0, 50);
    } else if (isSel || showAnswer) {
      stroke('royalblue'); strokeWeight(3); fill(65, 105, 225, 40);
    } else {
      stroke('darkorange'); strokeWeight(1); noFill();
      drawingContext.setLineDash([5, 4]);
    }
    rect(r.x, r.y, r.w, r.h, 4);
    drawingContext.setLineDash([]);
    strokeWeight(1);
    // numbered badge
    // badge sits in the top-right corner so it never hides the area's own label
    const bx = r.x + r.w - 11, by = r.y + 11;
    stroke('white');
    fill(isSel || showAnswer ? 'royalblue' : 'darkorange');
    circle(bx, by, 20);
    noStroke();
    fill('white');
    textSize(13);
    textStyle(BOLD);
    textAlign(CENTER, CENTER);
    text(hs.id, bx, by + 1);
    textStyle(NORMAL);
  }
}

function drawInfoPanel(m) {
  const px = margin, py = m.y + m.h + 8;
  const pw = canvasWidth - 2 * margin, ph = drawHeight - py - 8;
  stroke('silver');
  fill('white');
  rect(px, py, pw, ph, 8);
  noStroke();
  textAlign(LEFT, TOP);
  if (quizCheckbox.checked()) {
    const q = QUESTIONS[quizOrder[quizIndex]];
    fill('darkblue');
    textSize(18);
    textStyle(BOLD);
    text('Quiz: ' + q.q, px + 12, py + 10, pw - 24);
    const qLines = countLines('Quiz: ' + q.q, pw - 24);
    const fy = py + 22 + qLines * textLeading();
    textStyle(NORMAL);
    textSize(16);
    fill(quizFeedbackColor);
    text(quizFeedback || 'Click the part of the Thonny window that answers the question.',
      px + 12, fy, pw - 24);
    return;
  }
  if (!selected) {
    fill('black');
    textSize(18);
    textStyle(BOLD);
    text('Explore the Thonny window', px + 12, py + 10, pw - 24);
    textStyle(NORMAL);
    textSize(16);
    text('Hover over a numbered area to see its name. Click it to learn what it does and ' +
      'get a step to try. Turn on "Quiz me" when you are ready to test yourself.',
      px + 12, py + 38, pw - 24);
    return;
  }
  fill('royalblue');
  textSize(18);
  textStyle(BOLD);
  text(selected.id + '. ' + selected.name, px + 12, py + 10, pw - 24);
  textStyle(NORMAL);
  textSize(16);
  fill('black');
  text(selected.desc, px + 12, py + 36, pw - 24);
  // place the "Try this" line under however many lines the description wrapped to
  const lines = countLines(selected.desc, pw - 24);
  fill('darkgreen');
  text('Try this: ' + selected.tryThis, px + 12, py + 44 + lines * textLeading(), pw - 24);
}

// Count how many lines text() will use when wrapping words inside width w
function countLines(str, w) {
  const words = str.split(' ');
  let lines = 1, current = '';
  for (const word of words) {
    const trial = current ? current + ' ' + word : word;
    if (textWidth(trial) > w && current) { lines++; current = word; }
    else current = trial;
  }
  return lines;
}

function drawTooltip(label) {
  textSize(16);
  const w = textWidth(label) + 16;
  let x = mouseX + 14, y = mouseY + 14;
  if (x + w > canvasWidth - 4) x = mouseX - w - 6;
  if (y + 28 > drawHeight) y = mouseY - 34;
  stroke('dimgray');
  fill('lightyellow');
  rect(x, y, w, 26, 5);
  noStroke();
  fill('black');
  textAlign(LEFT, CENTER);
  text(label, x + 8, y + 13);
}

function mousePressed() {
  if (mouseY < 0 || mouseY > drawHeight || mouseX < 0 || mouseX > canvasWidth) return;
  const hs = hotspotAt(mouseX, mouseY);
  if (!hs) return;
  if (quizCheckbox.checked()) {
    if (quizAnswered) return;
    const q = QUESTIONS[quizOrder[quizIndex]];
    const right = HOTSPOTS.find(h => h.id === q.answer);
    quizTotal++;
    quizAnswered = true;
    if (hs.id === q.answer) {
      quizRight++;
      quizFeedback = 'Correct! That is the ' + right.name + '. ' + right.desc.split('. ')[0] +
        '. Press "Next question".';
      quizFeedbackColor = 'darkgreen';
    } else {
      quizFeedback = 'Not quite. You clicked the ' + hs.name + '. The answer is area ' + right.id +
        ', the ' + right.name + ' (outlined in blue). Press "Next question".';
      quizFeedbackColor = 'firebrick';
    }
  } else {
    selected = hs;
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
