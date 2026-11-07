// Pico Board Explorer MicroSim
// CANVAS_HEIGHT: 580
// A top-down drawing of the Raspberry Pi Pico W with clickable hotspots on
// its main parts. Explore mode shows labels, hover names, and an infobox.
// "Quiz me" hides the labels and asks the student to click each named part,
// keeping score and a list of the parts that were missed.

// Canvas dimensions - REQUIRED structure
let canvasWidth = 400;
let drawHeight = 530;
let controlHeight = 50;
let canvasHeight = drawHeight + controlHeight;
let margin = 20;
let defaultTextSize = 16;

// Board geometry (recomputed from the width every frame)
const BOARD_ASPECT = 21 / 51;     // the Pico is 51 mm x 21 mm
let bx, by, bw, bh;
const boardTop = 112;

// Parts and their hotspots in normalized board coordinates (0-1).
// labelRow: which callout row the explore-mode label sits in.
const parts = [
  { id: 'usb', name: 'USB connector', labelRow: 'aboveA',
    rects: [{ x: -0.035, y: 0.33, w: 0.125, h: 0.34 }],
    info: 'The micro-USB connector brings 5 V power to the board and carries data to and from your computer. Thonny uses it to send programs and show print() output.',
    used: 'powering your clock and uploading code.' },
  { id: 'led', name: 'On-board LED', labelRow: 'aboveB',
    rects: [{ x: 0.125, y: 0.15, w: 0.06, h: 0.14 }],
    info: 'A tiny green LED that your program can turn on and off. On the Pico W it is wired through the wireless chip, so you use Pin("LED").',
    used: 'your first blink program and quick "is my code running?" checks.' },
  { id: 'bootsel', name: 'BOOTSEL button', labelRow: 'belowA',
    rects: [{ x: 0.2, y: 0.56, w: 0.085, h: 0.22 }],
    info: 'Holding BOOTSEL while you plug in the USB cable makes the Pico show up as a USB drive. You drag a .uf2 firmware file onto that drive to install MicroPython.',
    used: 'installing or updating the MicroPython firmware.' },
  { id: 'rp2040', name: 'RP2040 chip', labelRow: 'aboveA',
    rects: [{ x: 0.36, y: 0.32, w: 0.14, h: 0.34 }],
    info: 'The RP2040 is the microcontroller chip: the brain that runs your MicroPython program. It has two processor cores and 264 KB of RAM.',
    used: 'running every clock program in this book.' },
  { id: 'wireless', name: 'Wireless module', labelRow: 'aboveB',
    rects: [{ x: 0.6, y: 0.2, w: 0.38, h: 0.6 }],
    info: 'The metal can covers the CYW43439 chip that adds WiFi and Bluetooth. The zigzag line at the end of the board is its antenna.',
    used: 'setting the clock from internet time servers (NTP).' },
  { id: 'pins', name: 'Pin rows (2 x 20)', labelRow: 'belowB',
    rects: [{ x: 0.02, y: 0.0, w: 0.96, h: 0.12 }, { x: 0.02, y: 0.88, w: 0.96, h: 0.12 }],
    info: 'Forty pins, twenty along each long edge, connect the Pico to the outside world. They include GPIO pins, power pins (3V3, VSYS, VBUS), and ground pins.',
    used: 'wiring displays, buttons, sensors, and buzzers.' }
];

// State
let selected = null;
let quiz = null;      // {order, index, score, missed, feedback, reveal}
let quizButton;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));

  quizButton = createButton('Quiz me');
  quizButton.position(10, drawHeight + 12);
  quizButton.mousePressed(toggleQuiz);

  describe('A top-down drawing of a Raspberry Pi Pico W circuit board with six labeled parts: the USB connector, ' +
    'on-board LED, BOOTSEL button, RP2040 chip, wireless module, and the two rows of 20 pins. Hovering names a part, ' +
    'clicking shows a description, and a Quiz me button hides the labels and asks you to click named parts.', LABEL);
}

function computeBoard() {
  bw = min(canvasWidth - 60, 540);
  bh = bw * BOARD_ASPECT;
  bx = (canvasWidth - bw) / 2;
  by = boardTop;
}

// Convert a normalized hotspot rectangle to canvas pixels
function toPx(r) {
  return { x: bx + r.x * bw, y: by + r.y * bh, w: r.w * bw, h: r.h * bh };
}

function partAt(mx, my) {
  // Check small parts first so the LED and button win over the big pin rows
  const orderCheck = ['led', 'bootsel', 'usb', 'rp2040', 'wireless', 'pins'];
  for (const id of orderCheck) {
    const p = parts.find(q => q.id === id);
    for (const r of p.rects) {
      const q = toPx(r);
      if (mx >= q.x && mx <= q.x + q.w && my >= q.y && my <= q.y + q.h) return p;
    }
  }
  return null;
}

function draw() {
  updateCanvasSize();
  computeBoard();

  // Backgrounds
  stroke('silver');
  strokeWeight(1);
  fill('aliceblue');
  rect(0, 0, canvasWidth, drawHeight);
  fill('white');
  rect(0, drawHeight, canvasWidth, controlHeight);

  // Title
  noStroke();
  fill('black');
  textAlign(CENTER, TOP);
  textSize(canvasWidth >= 600 ? 22 : 18);
  text('Raspberry Pi Pico W Board Explorer', canvasWidth / 2, 10);

  // Prompt line
  textSize(canvasWidth >= 600 ? 16 : 14);
  if (quiz && quiz.index < quiz.order.length) {
    fill('darkblue');
    textStyle(BOLD);
    text('Click the ' + quiz.order[quiz.index].name, canvasWidth / 2, 40);
    textStyle(NORMAL);
  } else if (!quiz) {
    fill('dimgray');
    text('Hover to name a part. Click a part to learn what it does.', canvasWidth / 2, 40);
  }

  drawBoard();
  const hover = (mouseY < drawHeight) ? partAt(mouseX, mouseY) : null;
  drawHighlights(hover);
  if (!quiz) drawLabels();
  drawInfoBox();
  if (!quiz && hover) drawTooltip(hover);

  // Control-area status
  noStroke();
  fill('black');
  textAlign(LEFT, CENTER);
  textSize(defaultTextSize);
  if (quiz) {
    const asked = min(quiz.index, quiz.order.length);
    text('Score: ' + quiz.score + ' / ' + asked, 110, drawHeight + 25);
  } else {
    fill('dimgray');
    text('Explore mode', 110, drawHeight + 25);
  }
}

function drawBoard() {
  // Green circuit board
  stroke('darkgreen');
  strokeWeight(2);
  fill('seagreen');
  rect(bx, by, bw, bh, bh * 0.06);

  // Castellated pin pads: 20 on each long edge
  const pinR = max(3, bw * 0.011);
  for (let i = 0; i < 20; i++) {
    const px = bx + bw * (0.045 + i * (0.91 / 19));
    for (const py of [by + bh * 0.06, by + bh * 0.94]) {
      stroke('darkgoldenrod');
      strokeWeight(1);
      fill('gold');
      circle(px, py, pinR * 2.2);
      fill('darkgreen');
      noStroke();
      circle(px, py, pinR * 0.9);
    }
  }

  // Micro-USB connector, sticking out of the left end
  const u = toPx(parts[0].rects[0]);
  stroke('dimgray');
  strokeWeight(1);
  fill('silver');
  rect(u.x, u.y, u.w, u.h, 3);
  fill('gray');
  rect(u.x + u.w * 0.15, u.y + u.h * 0.3, u.w * 0.5, u.h * 0.4, 2);

  // On-board LED
  const l = toPx(parts[1].rects[0]);
  stroke('dimgray');
  fill('palegreen');
  rect(l.x + l.w * 0.15, l.y + l.h * 0.2, l.w * 0.7, l.h * 0.6, 2);

  // BOOTSEL push button
  const b = toPx(parts[2].rects[0]);
  fill('whitesmoke');
  stroke('dimgray');
  rect(b.x, b.y, b.w, b.h, 3);
  fill('white');
  circle(b.x + b.w / 2, b.y + b.h / 2, min(b.w, b.h) * 0.7);

  // RP2040: black square chip with its logo dot
  const c = toPx(parts[3].rects[0]);
  fill(30);
  stroke(10);
  rect(c.x, c.y, c.w, c.h, 2);
  noStroke();
  fill(200);
  textAlign(CENTER, CENTER);
  textSize(max(8, c.w * 0.18));
  text('RP2040', c.x + c.w / 2, c.y + c.h / 2);

  // Flash memory chip (drawn for realism, not a hotspot)
  fill(40);
  rect(c.x - c.w * 0.75, c.y + c.h * 0.1, c.w * 0.5, c.h * 0.4, 2);

  // Wireless module: metal shield plus the zigzag antenna
  const w = toPx(parts[4].rects[0]);
  stroke('gray');
  strokeWeight(1);
  fill('lightgray');
  rect(w.x, w.y, w.w * 0.68, w.h, 3);
  noFill();
  stroke('gold');
  strokeWeight(2);
  const ax = w.x + w.w * 0.76;
  const aw = w.w * 0.2;
  beginShape();
  for (let k = 0; k <= 8; k++) {
    vertex(ax + (k % 2) * aw, w.y + k * (w.h / 8));
  }
  endShape();

  // Silkscreen text
  noStroke();
  fill('white');
  textAlign(LEFT, CENTER);
  textSize(max(9, bw * 0.022));
  text('Pico W', bx + bw * 0.36, by + bh * 0.78);
}

function drawHighlights(hover) {
  noFill();
  // Explore: selected part in blue; hover outline in orange
  if (!quiz && selected) outlinePart(selected, 'blue', 3);
  if (!quiz && hover && hover !== selected) outlinePart(hover, 'orange', 2);
  // Quiz: show the correct answer after a wrong click
  if (quiz && quiz.reveal) outlinePart(quiz.reveal, 'orangered', 4);
  if (quiz && quiz.lastCorrect) outlinePart(quiz.lastCorrect, 'limegreen', 4);
}

function outlinePart(p, col, wt) {
  noFill();
  stroke(col);
  strokeWeight(wt);
  for (const r of p.rects) {
    const q = toPx(r);
    rect(q.x - 3, q.y - 3, q.w + 6, q.h + 6, 4);
  }
}

// Explore-mode callout labels with leader lines
function drawLabels() {
  const rowsY = {
    aboveA: by - 46, aboveB: by - 22,
    belowA: by + bh + 22, belowB: by + bh + 46
  };
  textSize(canvasWidth >= 600 ? 15 : 12);
  for (const p of parts) {
    const r = toPx(p.rects[p.labelRow.startsWith('below') ? p.rects.length - 1 : 0]);
    const ax = r.x + r.w / 2;
    const ay = p.labelRow.startsWith('above') ? r.y : r.y + r.h;
    const ly = rowsY[p.labelRow];
    const tw = textWidth(p.name) + 10;
    const lx = constrain(ax, tw / 2 + 4, canvasWidth - tw / 2 - 4);
    stroke('dimgray');
    strokeWeight(1);
    line(ax, ay, lx, ly);
    fill('white');
    rect(lx - tw / 2, ly - 10, tw, 20, 4);
    noStroke();
    fill('black');
    textAlign(CENTER, CENTER);
    text(p.name, lx, ly);
  }
}

function drawInfoBox() {
  const top = by + bh + 64;
  const h = drawHeight - top - 10;
  stroke('silver');
  strokeWeight(1);
  fill(255, 255, 255, 235);
  rect(margin, top, canvasWidth - 2 * margin, h, 10);
  noStroke();
  textAlign(LEFT, TOP);
  const tx = margin + 12;
  const tw = canvasWidth - 2 * margin - 24;
  const small = canvasWidth < 600;
  if (quiz) {
    fill('black');
    textSize(small ? 14 : 16);
    let msg = quiz.feedback || 'Labels are hidden. Click the part named above the board.';
    if (quiz.index >= quiz.order.length) {
      msg = 'Quiz complete! You scored ' + quiz.score + ' out of ' + quiz.order.length + '. ' +
        (quiz.missed.length ? 'Review these parts: ' + quiz.missed.join(', ') + '.' : 'You found every part on the first try.') +
        ' Press Explore to see the labels again.';
    }
    text(msg, tx, top + 10, tw, h - 16);
  } else if (selected) {
    fill('darkblue');
    textStyle(BOLD);
    textSize(small ? 15 : 17);
    text(selected.name, tx, top + 8);
    textStyle(NORMAL);
    fill('black');
    textSize(small ? 13 : 15);
    text(selected.info, tx, top + 32, tw, h - 36);
    // "Used in this book for..." line sits under the description
    const lines = ceil(textWidth(selected.info) / tw) + 1;
    textStyle(BOLD);
    fill('darkgreen');
    text('Used in this book for ' + selected.used, tx, top + 34 + lines * (small ? 16 : 19), tw, 40);
    textStyle(NORMAL);
  } else {
    fill('dimgray');
    textSize(small ? 14 : 16);
    text('Click any part of the board to see what it does and how this book uses it.', tx, top + 10, tw, h - 16);
  }
}

function drawTooltip(p) {
  textSize(14);
  const w = textWidth(p.name) + 14;
  const x = constrain(mouseX + 12, 2, canvasWidth - w - 2);
  const y = mouseY - 30 < 0 ? mouseY + 16 : mouseY - 30;
  stroke('dimgray');
  strokeWeight(1);
  fill('lightyellow');
  rect(x, y, w, 22, 4);
  noStroke();
  fill('black');
  textAlign(LEFT, CENTER);
  text(p.name, x + 7, y + 11);
}

function mousePressed() {
  if (mouseY < 0 || mouseY > drawHeight || mouseX < 0 || mouseX > canvasWidth) return;
  const p = partAt(mouseX, mouseY);
  if (!quiz) {
    if (p) selected = p;
    return;
  }
  if (quiz.index >= quiz.order.length || !p) return;
  const target = quiz.order[quiz.index];
  quiz.reveal = null;
  quiz.lastCorrect = null;
  if (p === target) {
    quiz.score++;
    quiz.lastCorrect = p;
    quiz.feedback = 'Correct! That is the ' + target.name + '.';
  } else {
    quiz.missed.push(target.name);
    quiz.reveal = target;
    quiz.feedback = 'Not quite: you clicked the ' + p.name + '. The ' + target.name + ' is outlined in red.';
  }
  quiz.index++;
  if (quiz.index < quiz.order.length) {
    quiz.feedback += ' Next: click the ' + quiz.order[quiz.index].name + '.';
  } else {
    quizButton.html('Explore');
  }
}

function toggleQuiz() {
  if (quiz) {
    quiz = null;                    // leave the quiz (finished or not)
    quizButton.html('Quiz me');
    return;
  }
  quiz = { order: shuffle(parts.slice()), index: 0, score: 0, missed: [], feedback: '', reveal: null, lastCorrect: null };
  selected = null;
  quizButton.html('Stop quiz');
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
