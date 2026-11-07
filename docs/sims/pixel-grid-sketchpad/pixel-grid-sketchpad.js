// Pixel Grid Sketchpad
// CANVAS_HEIGHT: 670
// A 128 x 64 monochrome OLED framebuffer. Each byte holds a vertical strip of 8 pixels
// (MONO_VLSB):  index = x + floor(y / 8) * 128,  bit = y mod 8.
// Click or drag to turn pixels on and off and watch the matching buffer byte change.

let canvasWidth = 800;
let drawHeight = 620;
let controlHeight = 50;
let canvasHeight = drawHeight + controlHeight;
let margin = 6;
let defaultTextSize = 16;

const W = 128, H = 64;
let buf = new Uint8Array(W * H / 8);   // 1,024 bytes

let cell = 6, gridX = 22, gridY = 58, mapY, rowH = 12;
let hoverX = -1, hoverY = -1, hoverByte = -1;
let paintValue = 1, painting = false;

let mode = 'draw';         // 'draw', 'code' or 'challenge'
let target = null;
let challengeMsg = '';
let challengeColor = 'black';
let score = 0, tries = 0;

let clearButton, exampleButton, codeButton, challengeButton;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);
  frameRate(30);

  clearButton = createButton('Clear');
  clearButton.position(10, drawHeight + 12);
  clearButton.mousePressed(() => { buf.fill(0); if (mode === 'code') mode = 'draw'; });
  exampleButton = createButton('Draw example');
  exampleButton.position(70, drawHeight + 12);
  exampleButton.mousePressed(drawExample);
  codeButton = createButton('Generate code');
  codeButton.position(180, drawHeight + 12);
  codeButton.mousePressed(toggleCode);
  challengeButton = createButton('Challenge');
  challengeButton.position(300, drawHeight + 12);
  challengeButton.mousePressed(toggleChallenge);

  drawExample();   // open with the chapter's border-and-diagonal drawing so the buffer map has content

  describe('A 128 by 64 pixel grid like an SSD1306 OLED. Below it, a map of the 1,024 framebuffer ' +
    'bytes, one column per x and one row per page of 8 rows. Hovering a pixel highlights the byte ' +
    'that stores it and shows the index and bit.', LABEL);
}

// ---------- framebuffer helpers ----------
function byteIndex(x, y) { return x + floor(y / 8) * W; }
function getPixel(x, y) { return (buf[byteIndex(x, y)] >> (y % 8)) & 1; }
function setPixel(x, y, v) {
  if (x < 0 || x >= W || y < 0 || y >= H) return;
  let i = byteIndex(x, y), b = y % 8;
  if (v) buf[i] |= (1 << b); else buf[i] &= ~(1 << b);
}

function drawExample() {
  buf.fill(0);
  // the border and diagonal from the chapter's pixel() example
  for (let x = 0; x < W; x++) { setPixel(x, 0, 1); setPixel(x, 63, 1); }
  for (let i = 0; i < 64; i++) setPixel(i * 2, i, 1);
  if (mode === 'code') mode = 'draw';
}

function toggleCode() {
  if (mode === 'code') { mode = 'draw'; codeButton.html('Generate code'); return; }
  mode = 'code';
  codeButton.html('Hide code');
  challengeButton.html('Challenge');
  let code = generateCode();
  console.log(code.join('\n'));
  try { navigator.clipboard.writeText(code.join('\n')).catch(() => {}); } catch (e) { /* ignore */ }
}

function toggleChallenge() {
  if (mode === 'challenge') {
    mode = 'draw';
    challengeButton.html('Challenge');
    return;
  }
  mode = 'challenge';
  challengeButton.html('Stop challenge');
  codeButton.html('Generate code');
  score = 0; tries = 0;
  newTarget();
  challengeMsg = 'Click the pixel at (' + target.x + ', ' + target.y + ').';
  challengeColor = 'black';
}

function newTarget() {
  target = { x: floor(random(W)), y: floor(random(H)) };
}

function generateCode() {
  let lines = ['oled.fill(0)'];
  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      if (getPixel(x, y)) lines.push('oled.pixel(' + x + ', ' + y + ', 1)');
    }
  }
  lines.push('oled.show()');
  return lines;
}

// ---------- draw ----------
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
  text('Pixel Grid Sketchpad', canvasWidth / 2, 6);

  cell = max(2, floor((canvasWidth - gridX - margin) / W));
  mapY = gridY + H * cell + 50;
  updateHover();

  drawScreen();
  drawInfoLine();
  if (mode === 'code') drawCodePanel();
  else drawByteMap();
  drawBottomText();
}

function updateHover() {
  hoverX = hoverY = hoverByte = -1;
  let gx = floor((mouseX - gridX) / cell), gy = floor((mouseY - gridY) / cell);
  if (gx >= 0 && gx < W && gy >= 0 && gy < H) {
    hoverX = gx; hoverY = gy; hoverByte = byteIndex(gx, gy);
    return;
  }
  // hovering a byte in the map selects that byte
  let mx = floor((mouseX - gridX) / cell), page = floor((mouseY - mapY) / rowH);
  if (mode !== 'code' && mx >= 0 && mx < W && page >= 0 && page < 8) hoverByte = mx + page * W;
}

function drawScreen() {
  let gw = W * cell, gh = H * cell;
  noStroke();
  fill('black');
  rect(gridX, gridY, gw, gh);
  // lit pixels
  fill(150, 220, 255);
  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      if (getPixel(x, y)) rect(gridX + x * cell, gridY + y * cell, cell, cell);
    }
  }
  // grid lines (only when cells are big enough to see)
  if (cell >= 4) {
    stroke(45);
    for (let x = 0; x <= W; x++) line(gridX + x * cell, gridY, gridX + x * cell, gridY + gh);
    for (let y = 0; y <= H; y++) line(gridX, gridY + y * cell, gridX + gw, gridY + y * cell);
  }
  // page boundaries every 8 rows
  stroke(110, 110, 160);
  for (let p = 0; p <= 8; p++) line(gridX, gridY + p * 8 * cell, gridX + gw, gridY + p * 8 * cell);

  // highlight the byte (vertical strip of 8 pixels) under the mouse
  if (hoverByte >= 0) {
    let bx = hoverByte % W, page = floor(hoverByte / W);
    noFill();
    stroke('orange');
    strokeWeight(2);
    rect(gridX + bx * cell - 1, gridY + page * 8 * cell - 1, cell + 2, 8 * cell + 2);
    if (hoverX >= 0) {
      stroke('red');
      rect(gridX + hoverX * cell, gridY + hoverY * cell, cell, cell);
    }
    strokeWeight(1);
  }

  // tick labels
  noStroke();
  fill('dimgray');
  textSize(11);
  textAlign(CENTER, BOTTOM);
  let step = cell >= 4 ? 16 : 32;
  for (let x = 0; x <= W; x += step) text(x, gridX + min(x, W - 0.5) * cell, gridY - 2);
  textAlign(RIGHT, CENTER);
  for (let y = 0; y <= H; y += 16) text(y, gridX - 3, gridY + min(y, H - 0.5) * cell);
  textAlign(LEFT, BOTTOM);
  text('x', 3, gridY - 2);
}

function drawInfoLine() {
  noStroke();
  fill('black');
  textSize(canvasWidth < 600 ? 12 : 14);
  textAlign(LEFT, CENTER);
  let y = gridY + H * cell + 15;
  let msg;
  if (mode === 'challenge') {
    msg = 'Challenge: click (' + target.x + ', ' + target.y + ')   Score: ' + score + ' of ' + tries;
  } else if (hoverX >= 0) {
    let page = floor(hoverY / 8);
    msg = '(x, y) = (' + hoverX + ', ' + hoverY + ')   index = ' + hoverX + ' + ' + page + ' × 128 = ' +
      hoverByte + '   bit = ' + hoverY + ' mod 8 = ' + (hoverY % 8) + '   byte = ' + bin8(buf[hoverByte]);
  } else if (hoverByte >= 0) {
    msg = 'byte ' + hoverByte + ' = column x = ' + (hoverByte % W) + ', page ' + floor(hoverByte / W) +
      ' (rows ' + floor(hoverByte / W) * 8 + '-' + (floor(hoverByte / W) * 8 + 7) + ')   value = ' + bin8(buf[hoverByte]);
  } else {
    msg = 'Hover over a pixel to see its byte index and bit. Click or drag to draw.';
  }
  text(msg, gridX, y);
}

function drawByteMap() {
  let gw = W * cell;
  noStroke();
  fill('black');
  textSize(12);
  textAlign(LEFT, BOTTOM);
  text('Framebuffer: 1,024 bytes = 8 pages × 128 columns (one cell per byte)', gridX, mapY - 2);
  for (let p = 0; p < 8; p++) {
    for (let x = 0; x < W; x++) {
      let v = buf[x + p * W];
      if (v) fill(30, 90, 150, 90 + 165 * (popcount(v) / 8));
      else fill('white');
      rect(gridX + x * cell, mapY + p * rowH, cell, rowH);
    }
    fill('dimgray');
    textSize(10);
    textAlign(RIGHT, CENTER);
    text('p' + p, gridX - 3, mapY + p * rowH + rowH / 2);
  }
  noFill();
  stroke('silver');
  rect(gridX, mapY, gw, 8 * rowH);
  if (hoverByte >= 0) {
    stroke('orange');
    strokeWeight(2);
    rect(gridX + (hoverByte % W) * cell - 1, mapY + floor(hoverByte / W) * rowH - 1, cell + 2, rowH + 2);
    strokeWeight(1);
  }
}

function drawCodePanel() {
  let code = generateCode();
  let gw = W * cell;
  stroke('lightgray');
  fill(255, 255, 255, 240);
  rect(gridX, mapY - 18, gw, 8 * rowH + 20, 6);
  noStroke();
  fill('darkslateblue');
  textSize(12);
  textAlign(LEFT, TOP);
  let cols = max(1, floor(gw / 150));
  let rows = 5;
  let maxShown = cols * rows;
  let body = code.slice(1, code.length - 1);
  let shown = body.slice(0, maxShown - 2);
  let items = ['oled.fill(0)'].concat(shown);
  if (body.length > shown.length) items.push('... ' + (body.length - shown.length) + ' more');
  items.push('oled.show()');
  for (let i = 0; i < items.length; i++) {
    let c = floor(i / rows), r = i % rows;
    text(items[i], gridX + 8 + c * 150, mapY - 12 + r * 18);
  }
}

function drawBottomText() {
  noStroke();
  textSize(14);
  textAlign(LEFT, TOP);
  let y = mapY + 8 * rowH + 8;
  if (mode === 'challenge') {
    fill(challengeColor);
    text(challengeMsg, gridX, y);
  } else if (mode === 'code') {
    fill('black');
    text(countOn() + ' pixels on. Full listing printed to the browser console (and copied if allowed).', gridX, y);
  } else {
    fill('dimgray');
    text('Pixels on: ' + countOn() + ' of 8,192.  Darker map cells hold more lit bits.', gridX, y);
  }
}

// ---------- mouse ----------
function mousePressed() {
  updateHover();
  if (hoverX < 0) return;
  if (mode === 'challenge') {
    tries++;
    if (hoverX === target.x && hoverY === target.y) {
      score++;
      let idx = byteIndex(hoverX, hoverY);
      challengeMsg = 'Correct! (' + hoverX + ', ' + hoverY + ') is bit ' + (hoverY % 8) + ' of byte ' + idx + '. Next target shown above.';
      challengeColor = 'darkgreen';
      newTarget();
    } else {
      challengeMsg = 'You clicked (' + hoverX + ', ' + hoverY + '). x counts from the left edge, y from the top. Try again.';
      challengeColor = 'firebrick';
    }
    return;
  }
  if (mode === 'code') { mode = 'draw'; codeButton.html('Generate code'); }
  paintValue = getPixel(hoverX, hoverY) ? 0 : 1;
  setPixel(hoverX, hoverY, paintValue);
  painting = true;
}

function mouseDragged() {
  if (!painting || mode !== 'draw') return;
  let gx = floor((mouseX - gridX) / cell), gy = floor((mouseY - gridY) / cell);
  setPixel(gx, gy, paintValue);
}

function mouseReleased() { painting = false; }

// ---------- helpers ----------
function popcount(v) { let c = 0; while (v) { c += v & 1; v >>= 1; } return c; }
function countOn() { let c = 0; for (let i = 0; i < buf.length; i++) c += popcount(buf[i]); return c; }
function bin8(v) { return '0b' + v.toString(2).padStart(8, '0'); }

function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) canvasWidth = max(360, container.offsetWidth);
}
