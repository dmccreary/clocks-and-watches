// Bounding Box and Partial Update
// CANVAS_HEIGHT: 540
// A 128 x 64 OLED clock with four items (hours, minutes, seconds, date). Each item has a
// bounding box (x, y, w, h). A full redraw repaints all 8,192 pixels; a partial update
// erases and redraws only the boxes of the items that changed.

let canvasWidth = 800;
let drawHeight = 460;
let controlHeight = 80;
let canvasHeight = drawHeight + controlHeight;
let margin = 20;
let defaultTextSize = 16;

const OLED_W = 128, OLED_H = 64;

// 8 x 8 glyphs (rows top to bottom, MSB = left pixel)
const FONT = {
  '0': [0x3C, 0x66, 0x6E, 0x76, 0x66, 0x66, 0x3C, 0x00],
  '1': [0x18, 0x38, 0x18, 0x18, 0x18, 0x18, 0x7E, 0x00],
  '2': [0x3C, 0x66, 0x06, 0x0C, 0x30, 0x60, 0x7E, 0x00],
  '3': [0x3C, 0x66, 0x06, 0x1C, 0x06, 0x66, 0x3C, 0x00],
  '4': [0x0C, 0x1C, 0x3C, 0x6C, 0x7E, 0x0C, 0x0C, 0x00],
  '5': [0x7E, 0x60, 0x7C, 0x06, 0x06, 0x66, 0x3C, 0x00],
  '6': [0x3C, 0x66, 0x60, 0x7C, 0x66, 0x66, 0x3C, 0x00],
  '7': [0x7E, 0x06, 0x0C, 0x18, 0x30, 0x30, 0x30, 0x00],
  '8': [0x3C, 0x66, 0x66, 0x3C, 0x66, 0x66, 0x3C, 0x00],
  '9': [0x3C, 0x66, 0x66, 0x3E, 0x06, 0x66, 0x3C, 0x00],
  ':': [0x00, 0x18, 0x18, 0x00, 0x00, 0x18, 0x18, 0x00],
  '-': [0, 0, 0, 0x7E, 0, 0, 0, 0],
  ' ': [0, 0, 0, 0, 0, 0, 0, 0]
};

// Screen items and their bounding boxes on the 128 x 64 display
const items = [
  { key: 'hours', x: 8, y: 8, scale: 2, chars: 2, color: 'orange' },
  { key: 'minutes', x: 56, y: 8, scale: 2, chars: 2, color: 'limegreen' },
  { key: 'seconds', x: 96, y: 16, scale: 1, chars: 2, color: 'magenta' },
  { key: 'date', x: 24, y: 44, scale: 1, chars: 10, color: 'deepskyblue' }
];
const colon = { x: 40, y: 8, scale: 2 };

let hh = 10, mm = 42, ss = 57;
let lastRedrawn = { full: null, partial: null };
let lastChanged = [];
let flashRects = [];
let flashStart = -10000;
const FLASH_MS = 800;

let advanceButton, jumpButton, modeSelect, boxCheckbox;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  advanceButton = createButton('Advance one second');
  advanceButton.position(10, drawHeight + 10);
  advanceButton.mousePressed(advanceSecond);
  jumpButton = createButton('Jump to :59');
  jumpButton.position(165, drawHeight + 10);
  jumpButton.mousePressed(() => { ss = 59; flashRects = []; });

  modeSelect = createSelect();
  modeSelect.option('Partial update');
  modeSelect.option('Full redraw');
  modeSelect.selected('Partial update');
  modeSelect.position(118, drawHeight + 45);

  boxCheckbox = createCheckbox(' Bounding boxes', true);
  boxCheckbox.position(240, drawHeight + 47);

  describe('A 128 by 64 OLED clock showing hours, minutes, seconds and a date, each with a colored ' +
    'bounding box. Advancing one second flashes the pixels that are redrawn: the whole screen in ' +
    'full redraw mode, or only the changed boxes in partial update mode. A counter shows how many ' +
    'pixels were redrawn.', LABEL);
}

function itemText(key) {
  if (key === 'hours') return nf(hh, 2);
  if (key === 'minutes') return nf(mm, 2);
  if (key === 'seconds') return nf(ss, 2);
  return '2026-10-28';
}

function itemBox(it) {
  return { x: it.x, y: it.y, w: 8 * it.scale * it.chars, h: 8 * it.scale };
}

function advanceSecond() {
  let changed = ['seconds'];
  ss++;
  if (ss === 60) {
    ss = 0; mm++; changed.push('minutes');
    if (mm === 60) { mm = 0; hh = (hh % 12) + 1; changed.push('hours'); }
  }
  lastChanged = changed;
  if (modeSelect.value() === 'Full redraw') {
    flashRects = [{ x: 0, y: 0, w: OLED_W, h: OLED_H }];
    lastRedrawn.full = OLED_W * OLED_H;
  } else {
    flashRects = items.filter(it => changed.includes(it.key)).map(itemBox);
    lastRedrawn.partial = flashRects.reduce((a, r) => a + r.w * r.h, 0);
  }
  flashStart = millis();
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
  textSize(24);
  text('Bounding Box and Partial Update', canvasWidth / 2, 8);

  let wide = canvasWidth >= 600;
  let k = wide ? min(3.4, (canvasWidth * 0.5 - 40) / OLED_W) : (canvasWidth - 2 * margin - 16) / OLED_W;
  let sx = margin + 8, sy = 58;
  drawOled(sx, sy, k);
  if (wide) {
    drawPanel(sx + OLED_W * k + 28, sy - 8, canvasWidth - (sx + OLED_W * k + 28) - margin, false);
    drawBars(sx - 8, sy + OLED_H * k + 44, OLED_W * k + 16);
  } else {
    drawPanel(margin, sy + OLED_H * k + 40, canvasWidth - 2 * margin, true);
  }

  noStroke();
  fill('black');
  textSize(16);
  textAlign(LEFT, CENTER);
  text('Update mode:', 10, drawHeight + 56);
}

function drawGlyphs(str, x, y, scale, sx, sy, k) {
  for (let c = 0; c < str.length; c++) {
    let g = FONT[str[c]] || FONT[' '];
    for (let r = 0; r < 8; r++) {
      for (let b = 0; b < 8; b++) {
        if ((g[r] >> (7 - b)) & 1) {
          rect(sx + (x + (c * 8 + b) * scale) * k, sy + (y + r * scale) * k, scale * k, scale * k);
        }
      }
    }
  }
}

function drawOled(sx, sy, k) {
  let sw = OLED_W * k, sh = OLED_H * k;
  noStroke();
  fill('midnightblue');
  rect(sx - 8, sy - 8, sw + 16, sh + 16, 6);
  fill('black');
  rect(sx, sy, sw, sh);

  fill(150, 220, 255);
  noStroke();
  for (let it of items) drawGlyphs(itemText(it.key), it.x, it.y, it.scale, sx, sy, k);
  drawGlyphs(':', colon.x, colon.y, colon.scale, sx, sy, k);

  // red flash on the redrawn pixels, fading out
  let age = millis() - flashStart;
  if (age < FLASH_MS) {
    let a = map(age, 0, FLASH_MS, 170, 0);
    fill(255, 40, 40, a);
    for (let r of flashRects) rect(sx + r.x * k, sy + r.y * k, r.w * k, r.h * k);
  }

  if (boxCheckbox.checked()) {
    noFill();
    strokeWeight(2);
    for (let it of items) {
      let b = itemBox(it);
      stroke(it.color);
      rect(sx + b.x * k, sy + b.y * k, b.w * k, b.h * k);
    }
    strokeWeight(1);
  }
  noStroke();
  fill('dimgray');
  textSize(12);
  textAlign(LEFT, TOP);
  text('128 × 64 OLED preview (each square is one pixel)', sx - 8, sy + sh + 12);
}

function drawPanel(x, y, w, compact) {
  let mode = modeSelect.value();
  let lh = compact ? 17 : 21;
  let lines = [];
  let cur = mode === 'Full redraw' ? lastRedrawn.full : lastRedrawn.partial;
  lines.push(['Mode: ' + mode, 'black', true]);
  if (cur === null) {
    lines.push(['Press Advance one second', 'dimgray', false]);
    lines.push(['to redraw a frame.', 'dimgray', false]);
  } else {
    lines.push(['Pixels redrawn: ' + nfc(cur), mode === 'Full redraw' ? 'firebrick' : 'darkgreen', true]);
    lines.push(['= ' + nf(100 * cur / 8192, 1, 1) + '% of 8,192 pixels', 'black', false]);
  }
  if (!compact) {
    lines.push(['Last frame in each mode:', 'black', true]);
    lines.push(['  Full redraw: ' + (lastRedrawn.full === null ? '-' : nfc(lastRedrawn.full) + ' px'), 'black', false]);
    lines.push(['  Partial update: ' + (lastRedrawn.partial === null ? '-' : nfc(lastRedrawn.partial) + ' px'), 'black', false]);
  }
  lines.push(['Bounding boxes (x, y, w, h):', 'black', true]);
  for (let it of items) {
    let b = itemBox(it);
    let mark = lastChanged.includes(it.key) ? '  ← changed' : '';
    lines.push(['  ' + it.key + ' (' + b.x + ', ' + b.y + ', ' + b.w + ', ' + b.h + ') = ' + (b.w * b.h) + ' px' + mark, it.color === 'limegreen' ? 'green' : (it.color === 'deepskyblue' ? 'dodgerblue' : (it.color === 'orange' ? 'darkorange' : 'darkmagenta')), false]);
  }
  lines.push(['show() still sends all 1,024 bytes.', 'dimgray', false]);

  let h = lines.length * lh + 14;
  stroke('lightgray');
  fill(255, 255, 255, 235);
  rect(x, y, w, h, 10);
  noStroke();
  textAlign(LEFT, TOP);
  textSize(compact ? 13 : 14);
  for (let i = 0; i < lines.length; i++) {
    fill(lines[i][1]);
    textStyle(lines[i][2] ? BOLD : NORMAL);
    text(lines[i][0], x + 10, y + 8 + i * lh);
  }
  textStyle(NORMAL);
}

// bar comparison of the last frame in each mode (wide layout only)
function drawBars(x, y, w) {
  noStroke();
  fill('black');
  textSize(14);
  textStyle(BOLD);
  textAlign(LEFT, TOP);
  text('Pixels redrawn in the last frame', x, y);
  textStyle(NORMAL);
  let rows = [['Full redraw', lastRedrawn.full, 'firebrick'], ['Partial update', lastRedrawn.partial, 'seagreen']];
  let labelW = 110, barMax = w - labelW - 60;
  for (let i = 0; i < 2; i++) {
    let yy = y + 26 + i * 30;
    fill('black');
    textSize(13);
    textAlign(LEFT, CENTER);
    text(rows[i][0], x, yy + 10);
    fill('gainsboro');
    rect(x + labelW, yy, barMax, 20, 3);
    if (rows[i][1] !== null) {
      fill(rows[i][2]);
      rect(x + labelW, yy, max(2, barMax * rows[i][1] / 8192), 20, 3);
    }
    fill('black');
    textAlign(LEFT, CENTER);
    text(rows[i][1] === null ? '-' : nfc(rows[i][1]), x + labelW + barMax + 6, yy + 10);
  }
}

function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) canvasWidth = max(360, container.offsetWidth);
}
