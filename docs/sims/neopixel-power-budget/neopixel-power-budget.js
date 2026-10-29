// NeoPixel Power Budget MicroSim
// CANVAS_HEIGHT: 515
// Click pixels on a virtual NeoPixel strip to light them. The current estimate uses
// 20 mA per color channel at full value, so one pixel draws
//   I = (R + G + B) / 255 x 20 mA x brightness
// and full white draws 60 mA. A gauge shows the total against the USB limit:
// green below 400 mA, yellow to 500 mA, red above 500 mA.

// ---- Layout ----
let canvasWidth = 400;
let drawHeight = 430;
let controlHeight = 85;           // 2 rows x 35 + 15
let canvasHeight = drawHeight + controlHeight;
let margin = 10;
let sliderLeftMargin = 160;
let defaultTextSize = 16;

// ---- Controls ----
let lengthSelect, colorInput, lightAllButton, brightnessSlider;

// ---- Model ----
const MA_PER_CHANNEL = 20;        // mA for one channel at 255
const GAUGE_MAX = 1000;           // mA at the right end of the gauge
let lit = [];                     // true/false for each pixel
let pixelBoxes = [];              // screen positions for click testing

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  lengthSelect = createSelect();
  for (const n of [12, 30, 60, 144]) lengthSelect.option(String(n));
  lengthSelect.selected('30');
  lengthSelect.position(70, drawHeight + 10);
  lengthSelect.changed(() => resizeStrip(parseInt(lengthSelect.value(), 10)));

  colorInput = createInput('#ff0000', 'color');
  colorInput.position(185, drawHeight + 7);
  colorInput.size(44, 26);

  lightAllButton = createButton('Light all');
  lightAllButton.position(245, drawHeight + 9);
  lightAllButton.mousePressed(toggleAll);

  brightnessSlider = createSlider(0, 100, 100, 1);
  brightnessSlider.position(sliderLeftMargin, drawHeight + 47);
  brightnessSlider.size(canvasWidth - sliderLeftMargin - 25);

  resizeStrip(30);
  lit[0] = lit[5] = lit[10] = true;   // the chapter's example: three lit pixels

  describe('A virtual NeoPixel strip. Clicking a pixel lights it in the chosen color. A gauge shows the total ' +
    'current in milliamps with green, yellow, and red zones for the 500 mA USB limit, and the formula is shown ' +
    'with the numbers filled in.');
}

function resizeStrip(n) {
  const old = lit;
  lit = [];
  for (let i = 0; i < n; i++) lit.push(i < old.length ? old[i] : false);
  updateLightAllLabel();
}

function toggleAll() {
  const allOn = lit.every(x => x);
  lit = lit.map(() => !allOn);
  updateLightAllLabel();
}

function updateLightAllLabel() {
  lightAllButton.html(lit.length && lit.every(x => x) ? 'Clear all' : 'Light all');
}

function chosenRGB() {
  const c = color(colorInput.value());
  return [round(red(c)), round(green(c)), round(blue(c))];
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
  text('NeoPixel Power Budget', canvasWidth / 2, 8);

  const wide = canvasWidth >= 600;
  const [r, g, b] = chosenRGB();
  const bright = brightnessSlider.value() / 100;
  const n = lit.length;
  const litCount = lit.filter(x => x).length;
  const perPixel = (r + g + b) / 255 * MA_PER_CHANNEL * bright;
  const total = litCount * perPixel;

  // ---- The strip, wrapped into rows ----
  const pitch = wide ? 25 : 18;
  const perRow = max(1, floor((canvasWidth - 2 * margin - 10) / pitch));
  const rows = ceil(n / perRow);
  const stripX = (canvasWidth - min(n, perRow) * pitch) / 2;
  const stripY = 42;
  // Black strip backing for each row
  noStroke();
  fill(30);
  for (let row = 0; row < rows; row++) {
    const count = min(perRow, n - row * perRow);
    rect(stripX - 3, stripY + row * pitch - 1, count * pitch + 6, pitch - 2, 4);
  }
  pixelBoxes = [];
  let hoverIndex = -1;
  // Show the lit color at a visible brightness even when the real setting is very dim
  const shown = max(bright, 0.3);
  for (let i = 0; i < n; i++) {
    const x = stripX + (i % perRow) * pitch + pitch / 2;
    const y = stripY + floor(i / perRow) * pitch + pitch / 2 - 2;
    pixelBoxes.push({ x, y, r: pitch * 0.42 });
    if (dist(mouseX, mouseY, x, y) < pitch * 0.45) hoverIndex = i;
    stroke(i === hoverIndex ? 'gold' : 80);
    strokeWeight(i === hoverIndex ? 2 : 1);
    if (lit[i]) fill(r * shown, g * shown, b * shown);
    else fill(55);
    rect(x - pitch * 0.38, y - pitch * 0.38, pitch * 0.76, pitch * 0.76, 3);
  }
  strokeWeight(1);
  cursor(hoverIndex >= 0 ? HAND : ARROW);
  const stripBottom = stripY + rows * pitch;
  noStroke();
  fill('dimgray');
  textAlign(LEFT, TOP);
  textSize(13);
  text(hoverIndex >= 0 ? 'Pixel ' + hoverIndex + ': click to ' + (lit[hoverIndex] ? 'turn off' : 'light') :
    'Click pixels to light them. ' + litCount + ' of ' + n + ' lit.', margin, stripBottom + 4);

  // ---- Gauge and readout ----
  let gx, gy, gr, tx, ty, tw;
  if (wide) {
    gr = 105; gx = margin + 20 + gr; gy = drawHeight - 32;
    tx = gx + gr + 30; ty = stripBottom + 30; tw = canvasWidth - tx - margin;
  } else {
    gr = 70; gx = canvasWidth / 2; gy = drawHeight - 22;
    tx = margin; ty = stripBottom + 24; tw = canvasWidth - 2 * margin;
  }
  drawGauge(gx, gy, gr, total);
  drawReadout(tx, ty, tw, wide, r, g, b, bright, litCount, perPixel, total, n);

  // ---- Control labels ----
  noStroke();
  fill('black');
  textAlign(LEFT, CENTER);
  textSize(defaultTextSize);
  text('Pixels:', 10, drawHeight + 21);
  text('Color:', 135, drawHeight + 21);
  text('Brightness: ' + brightnessSlider.value() + '%', 10, drawHeight + 57);
}

function drawGauge(cx, cy, R, total) {
  const zones = [[0, 400, 'mediumseagreen'], [400, 500, 'gold'], [500, GAUGE_MAX, 'tomato']];
  noFill();
  strokeCap(SQUARE);
  strokeWeight(R * 0.22);
  for (const [a, b, col] of zones) {
    stroke(col);
    arc(cx, cy, 2 * R, 2 * R, PI + PI * a / GAUGE_MAX, PI + PI * b / GAUGE_MAX);
  }
  strokeCap(ROUND);
  // Tick labels
  noStroke();
  fill('dimgray');
  textSize(11);
  textAlign(CENTER, CENTER);
  for (const v of [0, 250, 500, 750, 1000]) {
    const a = PI + PI * v / GAUGE_MAX;
    text(v, cx + (R + 16) * cos(a), cy + (R + 16) * sin(a) + (v === 0 || v === 1000 ? -2 : 0));
  }
  // Needle
  const val = min(total, GAUGE_MAX);
  const a = PI + PI * val / GAUGE_MAX;
  stroke('black');
  strokeWeight(3);
  line(cx, cy, cx + R * 0.95 * cos(a), cy + R * 0.95 * sin(a));
  noStroke();
  fill('black');
  circle(cx, cy, 10);
  // Value
  textAlign(CENTER, BOTTOM);
  textSize(R > 80 ? 22 : 15);
  text(round(total) + ' mA', cx, cy - R * 0.38);
  if (total > GAUGE_MAX) {
    fill('firebrick');
    textSize(13);
    text('off scale', cx, cy - R * 0.16);
  }
}

function drawReadout(x, y, w, wide, r, g, b, bright, litCount, perPixel, total, n) {
  noStroke();
  textAlign(LEFT, TOP);
  const ts = wide ? 15 : 12;
  const lineH = wide ? 22 : 16;
  textSize(ts);
  fill('black');
  text('I = lit pixels × (R+G+B)/255 × 20 mA × brightness', x, y, w);
  y += wide ? 2 * lineH - 4 : lineH + 2;
  fill('indigo');
  text('= ' + litCount + ' × (' + r + '+' + g + '+' + b + ')/255 × 20 mA × ' + bright.toFixed(2), x, y, w);
  y += wide ? 2 * lineH - 4 : lineH + 2;
  text('= ' + litCount + ' × ' + perPixel.toFixed(1) + ' mA = ' + round(total) + ' mA', x, y, w);
  y += lineH + 6;

  let verdict, col;
  if (total < 400) { verdict = 'OK to run from USB power.'; col = 'green'; }
  else if (total <= 500) { verdict = 'Close to the 500 mA USB limit: risky.'; col = 'darkgoldenrod'; }
  else { verdict = 'Too much for USB: use a separate 5 V supply and tie its ground to the Pico.'; col = 'firebrick'; }
  textSize(wide ? 16 : 13);
  fill(col);
  textStyle(BOLD);
  text(verdict, x, y, w);
  textStyle(NORMAL);
  if (wide) {
    y += 2 * lineH + 4;
    fill('dimgray');
    textSize(14);
    const worst = n * 60 * bright;
    text('Worst case, all ' + n + ' pixels white at this brightness: ' + round(worst) + ' mA', x, y, w);
  }
}

function mousePressed() {
  if (mouseY < 0 || mouseY > drawHeight || mouseX < 0 || mouseX > canvasWidth) return;
  for (let i = 0; i < pixelBoxes.length; i++) {
    const p = pixelBoxes[i];
    if (dist(mouseX, mouseY, p.x, p.y) < p.r * 1.1) {
      lit[i] = !lit[i];
      updateLightAllLabel();
      return;
    }
  }
}

function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
  brightnessSlider.size(canvasWidth - sliderLeftMargin - 25);
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) canvasWidth = Math.floor(container.getBoundingClientRect().width);
}
