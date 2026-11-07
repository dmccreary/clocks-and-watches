// Digit Scaling Explorer
// CANVAS_HEIGHT: 530
// Each pixel of an 8 x 8 font glyph is drawn as a scale x scale block, so the
// text width is 8 x scale x characters. Anything past x = 127 falls off the OLED.

let canvasWidth = 800;
let drawHeight = 450;
let controlHeight = 80;
let canvasHeight = drawHeight + controlHeight;
let margin = 20;
let sliderLeftMargin = 330;
let defaultTextSize = 16;

const OLED_W = 128, OLED_H = 64;

// 8 x 8 bitmap font: each glyph is 8 rows, each row a byte with the MSB as the left pixel.
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
  ' ': [0, 0, 0, 0, 0, 0, 0, 0],
  '.': [0, 0, 0, 0, 0, 0x18, 0x18, 0],
  '-': [0, 0, 0, 0x7E, 0, 0, 0, 0],
  '/': [0x02, 0x06, 0x0C, 0x18, 0x30, 0x60, 0x40, 0x00],
  'A': [0x18, 0x3C, 0x66, 0x66, 0x7E, 0x66, 0x66, 0x00],
  'P': [0x7C, 0x66, 0x66, 0x7C, 0x60, 0x60, 0x60, 0x00],
  'M': [0x63, 0x77, 0x7F, 0x6B, 0x63, 0x63, 0x63, 0x00]
};
const UNKNOWN = [0x7E, 0x42, 0x42, 0x42, 0x42, 0x42, 0x7E, 0x00];

let timeInput, scaleSlider, gridCheckbox;
let selectedChar = 0;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  timeInput = createInput('12:34');
  timeInput.size(90);
  timeInput.position(110, drawHeight + 10);
  timeInput.input(() => { selectedChar = 0; });

  scaleSlider = createSlider(1, 6, 3, 1);
  scaleSlider.position(sliderLeftMargin, drawHeight + 12);

  gridCheckbox = createCheckbox(' Show scaled blocks', false);
  gridCheckbox.position(10, drawHeight + 47);

  sizeSlider();
  describe('A 128 by 64 OLED preview showing a time string drawn with an 8 by 8 font enlarged by a ' +
    'scale factor, an enlarged view of one source glyph, and a width readout that turns red when ' +
    'the text is wider than 128 pixels.', LABEL);
}

function glyphFor(ch) {
  return FONT[ch.toUpperCase()] || UNKNOWN;
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
  text('Digit Scaling Explorer', canvasWidth / 2, 8);

  let msg = timeInput.value().slice(0, 16);
  let scale = scaleSlider.value();
  let n = msg.length;
  let textW = 8 * scale * n, textH = 8 * scale;
  // center the text when it fits, otherwise start at the left edge
  let x0 = max(0, floor((OLED_W - textW) / 2));
  let y0 = max(0, floor((OLED_H - textH) / 2));
  if (selectedChar >= n) selectedChar = max(0, n - 1);

  // preview scale: room for the screen plus up to 112 overflow pixels
  let k = previewScale();
  let sx = margin + 10, sy = 60;
  drawOled(sx, sy, k, msg, scale, x0, y0);

  // lower area: source glyph and readouts
  let compact = canvasWidth < 600;
  let lowY = sy + OLED_H * k + 56;
  drawGlyph(margin, lowY, msg, scale, compact ? 11 : 15);
  drawReadouts(margin + (compact ? 108 : 180), lowY - 4, n, scale, textW, textH, x0, compact);

  // control labels
  noStroke();
  fill('black');
  textSize(16);
  textAlign(LEFT, CENTER);
  text('Time string:', 10, drawHeight + 21);
  text('Scale: ' + scale, 240, drawHeight + 21);
}

function drawOled(sx, sy, k, msg, scale, x0, y0) {
  let sw = OLED_W * k, sh = OLED_H * k;
  // overflow zone to the right of the screen
  noStroke();
  fill(255, 235, 235);
  rect(sx + sw, sy, 112 * k, sh);
  fill('firebrick');
  textSize(12);
  textAlign(LEFT, TOP);
  text('off the screen (x > 127)', sx + sw + 6, sy + sh + 12);
  // module bezel and screen
  fill('midnightblue');
  rect(sx - 8, sy - 8, sw + 16, sh + 16, 6);
  fill('black');
  rect(sx, sy, sw, sh);

  // lit pixels
  for (let c = 0; c < msg.length; c++) {
    let g = glyphFor(msg[c]);
    for (let r = 0; r < 8; r++) {
      for (let b = 0; b < 8; b++) {
        if (!((g[r] >> (7 - b)) & 1)) continue;
        let px = x0 + (c * 8 + b) * scale, py = y0 + r * scale;
        if (px >= OLED_W + 112) continue;
        if (px < OLED_W) fill(150, 220, 255);
        else fill(220, 60, 60, 150);
        let w = min(scale, OLED_W + 112 - px);
        rect(sx + px * k, sy + py * k, w * k, scale * k);
      }
    }
  }
  // optional grid of scaled blocks over the text area
  if (gridCheckbox.checked() && scale > 1) {
    stroke(90, 90, 120);
    strokeWeight(1);
    let maxX = min(OLED_W + 112, x0 + msg.length * 8 * scale);
    for (let x = x0; x <= maxX; x += scale) line(sx + x * k, sy + y0 * k, sx + x * k, sy + (y0 + 8 * scale) * k);
    for (let y = y0; y <= y0 + 8 * scale; y += scale) line(sx + x0 * k, sy + y * k, sx + maxX * k, sy + y * k);
  }
  // selected character outline
  if (msg.length) {
    noFill();
    stroke('orange');
    strokeWeight(2);
    let cx = x0 + selectedChar * 8 * scale;
    rect(sx + cx * k, sy + y0 * k, 8 * scale * k, 8 * scale * k);
    strokeWeight(1);
  }
  // screen edge marker
  stroke('red');
  strokeWeight(2);
  line(sx + sw, sy - 8, sx + sw, sy + sh + 8);
  strokeWeight(1);
  noStroke();
  fill('dimgray');
  textSize(12);
  textAlign(CENTER, BOTTOM);
  text('x = 0', sx, sy - 10);
  text('x = 128', sx + sw, sy - 10);
  textAlign(LEFT, TOP);
  text('128 × 64 OLED', sx, sy + sh + 12);
}

function previewScale() {
  return min(3, (canvasWidth - 2 * margin - 20) / 240);
}

function drawGlyph(x, y, msg, scale, cs) {
  let ch = msg.length ? msg[selectedChar] : ' ';
  let g = glyphFor(ch);
  noStroke();
  fill('black');
  textSize(cs < 14 ? 12 : 14);
  textAlign(LEFT, BOTTOM);
  text((cs < 14 ? 'Glyph "' : 'Source glyph "') + ch + '" (8 × 8)', x, y - 4);
  for (let r = 0; r < 8; r++) {
    for (let b = 0; b < 8; b++) {
      let on = (g[r] >> (7 - b)) & 1;
      stroke('lightgray');
      fill(on ? 'steelblue' : 'white');
      rect(x + b * cs, y + r * cs, cs, cs);
    }
  }
  noStroke();
  fill('dimgray');
  textSize(12);
  textAlign(LEFT, TOP);
  text(cs < 14 ? '1 square → ' + scale + '×' + scale : 'each square → ' + scale + ' × ' + scale + ' block', x, y + 8 * cs + 4);
}

function drawReadouts(x, y, n, scale, textW, textH, x0, compact) {
  let fits = textW <= OLED_W;
  let lh = compact ? 19 : 24;
  noStroke();
  textAlign(LEFT, TOP);
  textSize(compact ? 15 : 18);
  fill(fits ? 'darkgreen' : 'firebrick');
  textStyle(BOLD);
  text('Width = 8 \u00D7 ' + scale + ' \u00D7 ' + n + ' = ' + textW + ' px', x, y);
  textStyle(NORMAL);
  textSize(compact ? 13 : 15);
  let yy = y + lh + 2;
  text(fits ? 'Fits: ' + (OLED_W - textW) + ' px to spare' : 'Too wide by ' + (textW - OLED_W) + ' px', x, yy);
  fill(textH <= OLED_H ? 'black' : 'firebrick');
  text('Height = 8 \u00D7 ' + scale + ' = ' + textH + ' px of 64', x, yy + lh);
  fill('black');
  let maxChars = floor(OLED_W / (8 * scale));
  text('Max characters at scale ' + scale + ': ' + maxChars, x, yy + 2 * lh);
  text('Text starts at x = ' + x0 + (fits ? ' (centered)' : ' (left edge)'), x, yy + 3 * lh);
  if (!compact) {
    fill('dimgray');
    textSize(13);
    text('Hover a character to see its glyph.', x, yy + 4 * lh + 4);
  }
}

function mouseMoved() {
  // pick the glyph under the mouse
  let msg = timeInput.value().slice(0, 16);
  let scale = scaleSlider.value();
  let k = previewScale();
  let sx = margin + 10, sy = 60;
  let textW = 8 * scale * msg.length;
  let x0 = max(0, floor((OLED_W - textW) / 2));
  let px = (mouseX - sx) / k, py = (mouseY - sy) / k;
  if (py < 0 || py > OLED_H) return;
  let c = floor((px - x0) / (8 * scale));
  if (c >= 0 && c < msg.length) selectedChar = c;
}

function sizeSlider() {
  if (typeof scaleSlider !== 'undefined') scaleSlider.size(canvasWidth - sliderLeftMargin - margin);
}

function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) {
    canvasWidth = max(360, container.offsetWidth);
    sizeSlider();
  }
}
