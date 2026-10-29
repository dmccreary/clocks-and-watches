// RGB565 Color Mixer MicroSim
// CANVAS_HEIGHT: 590
// Packs a 24-bit color into the 16-bit RGB565 format used by color TFT displays:
//   color = (r & 0xF8) << 8 | (g & 0xFC) << 3 | (b >> 3)
// Shows the original and the quantized color side by side, the 16 bits in
// 5-6-5 groups, how much detail each channel loses, and (optionally) the
// banding that appears in a smooth gradient.

// ---- Layout ----
let canvasWidth = 400;
let drawHeight = 440;
let controlHeight = 150;          // 4 rows x 35 + 10
let canvasHeight = drawHeight + controlHeight;
let margin = 10;
let sliderLeftMargin = 110;
let defaultTextSize = 16;

// ---- Controls ----
let rSlider, gSlider, bSlider, gradientCheckbox, predictButton, answerInput, checkButton;

// ---- Predict mode ----
let predictMode = false;
let revealed = true;
let feedback = '';
let feedbackColor = 'black';

function color565(r, g, b) { return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3); }
// Expand the 5- or 6-bit fields back to 0-255 for showing on this screen
function expand5(v5) { return (v5 << 3) | (v5 >> 2); }
function expand6(v6) { return (v6 << 2) | (v6 >> 4); }
function unpack(c) {
  return { r: expand5(c >> 11), g: expand6((c >> 5) & 0x3F), b: expand5(c & 0x1F) };
}
function hex4(n) { return '0x' + n.toString(16).toUpperCase().padStart(4, '0'); }

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  rSlider = createSlider(0, 255, 255, 1);
  gSlider = createSlider(0, 255, 128, 1);
  bSlider = createSlider(0, 255, 0, 1);
  const sliders = [rSlider, gSlider, bSlider];
  for (let i = 0; i < 3; i++) {
    sliders[i].position(sliderLeftMargin, drawHeight + 8 + i * 35);
    sliders[i].size(canvasWidth - sliderLeftMargin - 25);
    sliders[i].input(() => { if (predictMode) leavePredict(); });
  }

  gradientCheckbox = createCheckbox('Gradient', false);
  gradientCheckbox.position(10, drawHeight + 115);

  predictButton = createButton('Predict');
  predictButton.position(100, drawHeight + 113);
  predictButton.mousePressed(togglePredict);

  answerInput = createInput('');
  answerInput.position(205, drawHeight + 113);
  answerInput.size(70);
  answerInput.attribute('placeholder', 'hex');

  checkButton = createButton('Check');
  checkButton.position(295, drawHeight + 113);
  checkButton.mousePressed(checkAnswer);

  describe('Two color swatches show a 24-bit color and the same color after packing into 16-bit RGB565. ' +
    'Below them the 16 bits appear in red, green, and blue groups of 5, 6, and 5 bits, with the hex value and ' +
    'the color565() call. Sliders set red, green, and blue from 0 to 255.');
}

function togglePredict() {
  if (predictMode) { leavePredict(); return; }
  predictMode = true;
  revealed = false;
  rSlider.value(floor(random(256)));
  gSlider.value(floor(random(256)));
  bSlider.value(floor(random(256)));
  answerInput.value('');
  feedback = 'Predict the RGB565 hex value, type it, and press Check.';
  feedbackColor = 'black';
  predictButton.html('Exit Predict');
}

function leavePredict() {
  predictMode = false;
  revealed = true;
  feedback = '';
  predictButton.html('Predict');
}

function checkAnswer() {
  if (!predictMode) { feedback = 'Press Predict first.'; feedbackColor = 'black'; return; }
  const txt = answerInput.value().trim().replace(/^0x/i, '');
  if (!/^[0-9a-fA-F]{1,4}$/.test(txt)) { feedback = 'Type 4 hex digits, such as FC00.'; feedbackColor = 'firebrick'; return; }
  const c = color565(rSlider.value(), gSlider.value(), bSlider.value());
  revealed = true;
  if (parseInt(txt, 16) === c) {
    feedback = 'Correct! ' + hex4(c) + '. Press Exit Predict, then Predict for another color.';
    feedbackColor = 'green';
  } else {
    feedback = 'Not quite: the answer is ' + hex4(c) + '. Check each group of bits below.';
    feedbackColor = 'firebrick';
  }
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
  textSize(22);
  text('RGB565 Color Mixer', canvasWidth / 2, 8);

  const r = rSlider.value(), g = gSlider.value(), b = bSlider.value();
  const c = color565(r, g, b);
  const q = unpack(c);
  const hidden = predictMode && !revealed;
  const narrow = canvasWidth < 600;

  // ---- Swatches ----
  const sw = (canvasWidth - 3 * margin) / 2, sy = 58, sh = narrow ? 64 : 78;
  noStroke();
  fill('black');
  textAlign(LEFT, BOTTOM);
  textSize(narrow ? 13 : 15);
  text('24-bit color (8-8-8): ' + r + ', ' + g + ', ' + b, margin, sy - 4);
  text(hidden ? 'After RGB565: ?' : 'After RGB565: ' + q.r + ', ' + q.g + ', ' + q.b, 2 * margin + sw, sy - 4);
  stroke('gray');
  fill(r, g, b);
  rect(margin, sy, sw, sh, 6);
  if (hidden) fill('lightgray'); else fill(q.r, q.g, q.b);
  rect(2 * margin + sw, sy, sw, sh, 6);
  if (hidden) {
    noStroke();
    fill('dimgray');
    textAlign(CENTER, CENTER);
    textSize(28);
    text('?', 2 * margin + sw * 1.5, sy + sh / 2);
  }

  // ---- The 16 bits in 5-6-5 groups ----
  const by = sy + sh + 30;
  const cellW = min(44, (canvasWidth - 2 * margin) / 16);
  const bx = (canvasWidth - cellW * 16) / 2;
  const groupColors = [[255, 205, 205], [205, 240, 205], [205, 220, 255]];
  for (let i = 0; i < 16; i++) {
    const bit = 15 - i;
    const group = bit >= 11 ? 0 : (bit >= 5 ? 1 : 2);
    stroke('gray');
    fill(groupColors[group]);
    rect(bx + i * cellW, by, cellW, 32);
    noStroke();
    textAlign(CENTER, CENTER);
    fill('black');
    textSize(min(18, cellW * 0.7));
    text(hidden ? '?' : (c >> bit) & 1, bx + i * cellW + cellW / 2, by + 16);
    fill('dimgray');
    textSize(10);
    text(bit, bx + i * cellW + cellW / 2, by - 8);
  }
  // Group labels
  textSize(narrow ? 12 : 14);
  textAlign(CENTER, TOP);
  fill('firebrick');
  text('Red: 5 bits', bx + cellW * 2.5, by + 36);
  fill('darkgreen');
  text('Green: 6 bits', bx + cellW * 8, by + 36);
  fill('navy');
  text('Blue: 5 bits', bx + cellW * 13.5, by + 36);

  // ---- Readouts ----
  let y = by + 60;
  textAlign(LEFT, TOP);
  textSize(narrow ? 13 : 16);
  fill('black');
  const binStr = hidden ? '????? ?????? ?????' :
    (c >> 11).toString(2).padStart(5, '0') + ' ' + ((c >> 5) & 0x3F).toString(2).padStart(6, '0') + ' ' +
    (c & 0x1F).toString(2).padStart(5, '0');
  text('Binary: ' + binStr + '    Hex: ' + (hidden ? '0x????' : hex4(c)), margin, y);
  y += narrow ? 20 : 24;
  fill('indigo');
  text('color565(' + r + ', ' + g + ', ' + b + ')  returns  ' + (hidden ? '?' : hex4(c)), margin, y);
  y += narrow ? 20 : 24;

  if (predictMode && feedback) {
    fill(feedbackColor);
    text(feedback, margin, y, canvasWidth - 2 * margin);
  } else {
    // Detail lost: the low bits that are dropped from each channel
    fill('black');
    const lost = 'Kept: R ' + (r & 0xF8) + ' (lost ' + (r & 7) + '), G ' + (g & 0xFC) + ' (lost ' + (g & 3) +
      '), B ' + (b & 0xF8) + ' (lost ' + (b & 7) + ')';
    text(lost, margin, y, canvasWidth - 2 * margin);
    y += narrow ? 20 : 24;
    fill('dimgray');
    text('8 bits dropped per pixel: 65,536 colors instead of 16,777,216', margin, y, canvasWidth - 2 * margin);
  }

  // ---- Gradient: a smooth 8-bit ramp versus the banded RGB565 ramp ----
  const gy = drawHeight - 66;
  if (gradientCheckbox.checked()) {
    const lx = narrow ? 70 : 110, gw = canvasWidth - lx - margin;
    noStroke();
    fill('black');
    textAlign(LEFT, CENTER);
    textSize(narrow ? 12 : 14);
    text(narrow ? '8-bit' : '8-bit ramp', margin, gy + 13);
    text(narrow ? 'RGB565' : 'RGB565 ramp', margin, gy + 44);
    const smooth = new Set(), banded = new Set();
    noStroke();
    for (let x = 0; x < gw; x++) {
      const t = x / (gw - 1);
      const rr = round(r * t), gg = round(g * t), bb = round(b * t);
      fill(rr, gg, bb);
      rect(lx + x, gy, 1.5, 26);
      const cq = color565(rr, gg, bb);
      const qq = unpack(cq);
      fill(qq.r, qq.g, qq.b);
      rect(lx + x, gy + 31, 1.5, 26);
      smooth.add(rr + ',' + gg + ',' + bb);
      banded.add(cq);
    }
    fill('black');
    textAlign(LEFT, BOTTOM);
    textSize(narrow ? 12 : 14);
    text('Shades in the ramp: ' + smooth.size + ' in 8-bit, only ' + banded.size + ' in RGB565', lx, gy - 3);
    noFill();
    stroke('gray');
    rect(lx, gy, gw, 26);
    rect(lx, gy + 31, gw, 26);
  } else {
    noStroke();
    fill('dimgray');
    textAlign(LEFT, TOP);
    textSize(14);
    text('Check Gradient to compare a smooth ramp with the banded RGB565 version.', margin, gy + 20, canvasWidth - 2 * margin);
  }

  // ---- Control labels ----
  noStroke();
  textAlign(LEFT, CENTER);
  textSize(defaultTextSize);
  fill('firebrick');
  text('Red: ' + r, 10, drawHeight + 18);
  fill('darkgreen');
  text('Green: ' + g, 10, drawHeight + 53);
  fill('navy');
  text('Blue: ' + b, 10, drawHeight + 88);
}

function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
  for (const s of [rSlider, gSlider, bSlider]) s.size(canvasWidth - sliderLeftMargin - 25);
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) canvasWidth = Math.floor(container.getBoundingClientRect().width);
}
