// NeoPixel Digit Layout MicroSim
// CANVAS_HEIGHT: 525
// One seven-segment digit built from a 14-pixel NeoPixel strip, two pixels per segment.
// Students see which pixels belong to each segment, which pixels light for each digit
// (using the same 0x3F-style segment bytes as Chapter 9), how the strip snakes through
// the digit, and can design their own wiring order and copy it as a Python SEG_PIXELS list.

// ---- Layout ----
let canvasWidth = 400;
let drawHeight = 440;
let controlHeight = 85;           // 2 rows x 35 + 15
let canvasHeight = drawHeight + controlHeight;
let margin = 10;
let defaultTextSize = 16;

// ---- Controls ----
let digitSelect, orderCheckbox, rewireButton, resetButton, copyButton;

// ---- Model ----
const SEG_NAMES = ['a', 'b', 'c', 'd', 'e', 'f', 'g'];
const DIGITS = [0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x07, 0x7F, 0x6F];
// Each segment runs from one corner to another of a 1 x 2 digit (x right, y down)
const SEG_ENDS = [
  [[0, 0], [1, 0]],   // a  top
  [[1, 0], [1, 1]],   // b  upper right
  [[1, 1], [1, 2]],   // c  lower right
  [[1, 2], [0, 2]],   // d  bottom
  [[0, 2], [0, 1]],   // e  lower left
  [[0, 1], [0, 0]],   // f  upper left
  [[0, 1], [1, 1]]    // g  middle
];
// pixelAt[s] = [pixel index at the 1/3 spot, pixel index at the 2/3 spot] of segment s
let pixelAt = [];
let selectedSeg = -1;
let rewiring = false;
let rewireOrder = [];
let message = '';

function setDefaultWiring() {
  pixelAt = SEG_ENDS.map((_, s) => [2 * s, 2 * s + 1]);
}

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);
  setDefaultWiring();

  digitSelect = createSelect();
  for (let d = 0; d <= 9; d++) digitSelect.option(String(d));
  digitSelect.selected('7');
  digitSelect.position(60, drawHeight + 10);

  orderCheckbox = createCheckbox('Show strip order', false);
  orderCheckbox.position(130, drawHeight + 12);

  rewireButton = createButton('Rewire');
  rewireButton.position(10, drawHeight + 47);
  rewireButton.mousePressed(toggleRewire);

  resetButton = createButton('Reset wiring');
  resetButton.position(90, drawHeight + 47);
  resetButton.mousePressed(() => {
    setDefaultWiring();
    rewiring = false;
    rewireButton.html('Rewire');
    message = 'Wiring reset to a to g order.';
  });

  copyButton = createButton('Copy SEG_PIXELS');
  copyButton.position(205, drawHeight + 47);
  copyButton.mousePressed(copyMapping);

  describe('A seven-segment digit made of 14 NeoPixels, two per segment, each labeled with its pixel number. ' +
    'A menu picks a digit from 0 to 9 and its segments light up. A checkbox draws the path of the strip ' +
    'through the digit, and the Python SEG_PIXELS list for the current wiring is shown.');
}

function segPixelsText() {
  const parts = pixelAt.map(p => '(' + min(p[0], p[1]) + ', ' + max(p[0], p[1]) + ')');
  return 'SEG_PIXELS = [' + parts.join(', ') + ']   # a to g';
}

function copyMapping() {
  const txt = segPixelsText();
  try {
    navigator.clipboard.writeText(txt).then(
      () => { message = 'Copied SEG_PIXELS to the clipboard.'; },
      () => { message = 'Copy blocked here: select the line in the panel instead.'; });
  } catch (e) {
    message = 'Copy blocked here: select the line in the panel instead.';
  }
}

function toggleRewire() {
  rewiring = !rewiring;
  rewireOrder = [];
  rewireButton.html(rewiring ? 'Cancel' : 'Rewire');
  message = rewiring ? 'Click the 7 segments in the order the strip passes through them.' : 'Rewire cancelled.';
}

// Give pixels 2k and 2k+1 to the k-th segment in strip order. Within a segment,
// the strip enters at the end closest to where the previous segment left off.
function applyRewire(order) {
  let prev = [0, 0];            // the strip enters at the top-left corner
  const newAt = [];
  order.forEach((s, k) => {
    const A = spotUnit(s, 0), B = spotUnit(s, 1);
    if (dist(prev[0], prev[1], A[0], A[1]) <= dist(prev[0], prev[1], B[0], B[1])) {
      newAt[s] = [2 * k, 2 * k + 1]; prev = B;
    } else {
      newAt[s] = [2 * k + 1, 2 * k]; prev = A;
    }
  });
  pixelAt = newAt;
}

// Unit-space position of a segment's pixel spot (0 = 1/3 along, 1 = 2/3 along)
function spotUnit(s, which) {
  const [p, q] = SEG_ENDS[s];
  const f = which === 0 ? 1 / 3 : 2 / 3;
  return [p[0] + (q[0] - p[0]) * f, p[1] + (q[1] - p[1]) * f];
}

// Total length of wire from pixel 0 to 13, in segment lengths
function pathLength() {
  const pos = pixelPositionsUnit();
  let L = 0;
  for (let i = 1; i < 14; i++) L += dist(pos[i - 1][0], pos[i - 1][1], pos[i][0], pos[i][1]);
  return L;
}

function pixelPositionsUnit() {
  const pos = [];
  for (let s = 0; s < 7; s++) for (let w = 0; w < 2; w++) pos[pixelAt[s][w]] = spotUnit(s, w);
  return pos;
}

// ---- Drawing geometry ----
let geo = { ox: 0, oy: 0, u: 100, t: 24 };
function toScreen(p) { return [geo.ox + p[0] * geo.u, geo.oy + p[1] * geo.u]; }

function segPolygon(s) {
  const [p, q] = SEG_ENDS[s].map(toScreen);
  const len = dist(p[0], p[1], q[0], q[1]);
  const ux = (q[0] - p[0]) / len, uy = (q[1] - p[1]) / len, nx = -uy, ny = ux;
  const h = geo.t / 2, gap = 4;
  const a = [p[0] + ux * gap, p[1] + uy * gap], b = [q[0] - ux * gap, q[1] - uy * gap];
  return [
    a,
    [a[0] + ux * h + nx * h, a[1] + uy * h + ny * h],
    [b[0] - ux * h + nx * h, b[1] - uy * h + ny * h],
    b,
    [b[0] - ux * h - nx * h, b[1] - uy * h - ny * h],
    [a[0] + ux * h - nx * h, a[1] + uy * h - ny * h]
  ];
}

function segmentAt(mx, my) {
  for (let s = 0; s < 7; s++) {
    const [p, q] = SEG_ENDS[s].map(toScreen);
    const vx = q[0] - p[0], vy = q[1] - p[1];
    const t = ((mx - p[0]) * vx + (my - p[1]) * vy) / (vx * vx + vy * vy);
    if (t < 0.08 || t > 0.92) continue;
    if (dist(mx, my, p[0] + t * vx, p[1] + t * vy) < geo.t * 0.7) return s;
  }
  return -1;
}

function draw() {
  updateCanvasSize();
  stroke('silver');
  strokeWeight(1);
  fill('aliceblue');
  rect(0, 0, canvasWidth, drawHeight);
  fill('white');
  rect(0, drawHeight, canvasWidth, controlHeight);

  const wide = canvasWidth >= 600;
  geo.u = wide ? 140 : 80;
  geo.t = geo.u * 0.2;
  geo.ox = wide ? margin + geo.t + 30 : (canvasWidth - geo.u) / 2;
  geo.oy = 40 + geo.t + 12;

  const digit = parseInt(digitSelect.value(), 10);
  const pattern = DIGITS[digit];
  const hoverSeg = segmentAt(mouseX, mouseY);

  // Dark backing board for the digit
  fill(35);
  noStroke();
  rect(geo.ox - geo.t - 12, geo.oy - geo.t - 12, geo.u + 2 * geo.t + 24, 2 * geo.u + 2 * geo.t + 24, 10);

  // Segments
  for (let s = 0; s < 7; s++) {
    const on = (pattern >> s) & 1;
    const poly = segPolygon(s);
    fill(on ? color(120, 20, 20) : color(60));
    if (s === selectedSeg) { stroke('gold'); strokeWeight(3); }
    else if (s === hoverSeg) { stroke('lightyellow'); strokeWeight(2); }
    else { stroke(90); strokeWeight(1); }
    beginShape();
    for (const v of poly) vertex(v[0], v[1]);
    endShape(CLOSE);
    // Segment letter beside the segment
    const mid = toScreen(spotUnit(s, 0).map((c, i) => (c + spotUnit(s, 1)[i]) / 2));
    const [p, q] = SEG_ENDS[s];
    const horiz = p[1] === q[1];
    noStroke();
    fill('silver');
    textAlign(CENTER, CENTER);
    textSize(13);
    if (horiz) text(SEG_NAMES[s], mid[0], mid[1] + (s === 3 ? geo.t * 0.95 : -geo.t * 0.95));
    else text(SEG_NAMES[s], mid[0] + (p[0] === 1 ? geo.t * 0.95 : -geo.t * 0.95), mid[1]);
  }

  // Strip path
  const posU = pixelPositionsUnit();
  if (orderCheckbox.checked()) {
    stroke('deepskyblue');
    strokeWeight(2);
    noFill();
    for (let i = 1; i < 14; i++) {
      const a = toScreen(posU[i - 1]), b = toScreen(posU[i]);
      line(a[0], a[1], b[0], b[1]);
      // arrowhead at the middle of each link
      const mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2, ang = atan2(b[1] - a[1], b[0] - a[0]);
      push();
      translate(mx, my);
      rotate(ang);
      fill('deepskyblue');
      noStroke();
      triangle(6, 0, -4, -4, -4, 4);
      pop();
    }
    // Data-in arrow to pixel 0
    const p0 = toScreen(posU[0]);
    stroke('deepskyblue');
    line(p0[0] - geo.t * 1.6, p0[1] - geo.t * 1.2, p0[0], p0[1]);
    noStroke();
    fill('deepskyblue');
    textSize(12);
    textAlign(RIGHT, BOTTOM);
    text('DIN', p0[0] - geo.t * 1.6, p0[1] - geo.t * 1.2);
  }

  // Pixels with their numbers
  for (let s = 0; s < 7; s++) {
    const on = (pattern >> s) & 1;
    for (let w = 0; w < 2; w++) {
      const p = toScreen(spotUnit(s, w));
      stroke(on ? 'white' : 'gray');
      strokeWeight(1.5);
      fill(on ? 'red' : 'dimgray');
      circle(p[0], p[1], geo.t * 0.95);
      noStroke();
      fill('white');
      textAlign(CENTER, CENTER);
      textSize(max(11, geo.t * 0.5));
      text(pixelAt[s][w], p[0], p[1] + 1);
    }
  }

  // Title (drawn after the backing board)
  noStroke();
  fill('black');
  textAlign(CENTER, TOP);
  textSize(22);
  text('NeoPixel Digit Layout', canvasWidth / 2, 8);

  // Info panel
  let px, py, pw, ph;
  if (wide) {
    px = geo.ox + geo.u + geo.t + 40; py = 40; pw = canvasWidth - px - margin; ph = drawHeight - py - 10;
  } else {
    px = margin; py = geo.oy + 2 * geo.u + geo.t + 18; pw = canvasWidth - 2 * margin; ph = drawHeight - py - 6;
  }
  drawPanel(px, py, pw, ph, digit, pattern, wide);

  // Control labels
  noStroke();
  fill('black');
  textAlign(LEFT, CENTER);
  textSize(defaultTextSize);
  text('Digit:', 10, drawHeight + 21);
}

function drawPanel(px, py, pw, ph, digit, pattern, wide) {
  fill(255, 255, 255, 235);
  stroke(200);
  rect(px, py, pw, ph, 10);
  noStroke();
  textAlign(LEFT, TOP);
  const lineH = wide ? 22 : 17;
  let y = py + 10;
  const tw = pw - 24;
  textSize(wide ? 16 : 13);

  // Digit pattern
  const lit = [], litPixels = [];
  for (let s = 0; s < 7; s++) if ((pattern >> s) & 1) { lit.push(SEG_NAMES[s]); litPixels.push(...pixelAt[s]); }
  litPixels.sort((a, b) => a - b);
  fill('black');
  text('Digit ' + digit + ': DIGITS[' + digit + '] = 0x' + pattern.toString(16).toUpperCase().padStart(2, '0') +
    ' = 0b' + pattern.toString(2).padStart(7, '0'), px + 12, y, tw);
  y += lineH;
  text('Segments on: ' + lit.join(', '), px + 12, y, tw);
  y += lineH;
  fill('firebrick');
  text('Pixels lit: ' + litPixels.join(', '), px + 12, y, tw);
  y += wide ? (textWidth('Pixels lit: ' + litPixels.join(', ')) > tw ? 2 : 1) * lineH + 6 : lineH + 2;

  // Selected segment / rewire status
  fill('indigo');
  if (rewiring) {
    text('Rewiring: click segment ' + (rewireOrder.length + 1) + ' of 7' +
      (rewireOrder.length ? ' (so far: ' + rewireOrder.map(s => SEG_NAMES[s]).join(' > ') + ')' : ''), px + 12, y, tw);
  } else if (selectedSeg >= 0) {
    text('Segment ' + SEG_NAMES[selectedSeg] + ' contains pixels ' + min(...pixelAt[selectedSeg]) + ' and ' +
      max(...pixelAt[selectedSeg]) + '.', px + 12, y, tw);
  } else {
    text('Click a segment to see its pixels.', px + 12, y, tw);
  }
  y += wide ? 2 * lineH : lineH + 2;

  // The mapping as Python
  fill('black');
  textSize(wide ? 14 : 11);
  text(segPixelsText(), px + 12, y, tw);
  y += wide ? 44 : 30;
  fill('dimgray');
  textSize(wide ? 14 : 12);
  text('Strip path length: ' + pathLength().toFixed(1) + ' segment lengths' + (wide ? ' (shorter is easier to build)' : ''), px + 12, y, tw);
  y += wide ? 42 : lineH;
  if (message) {
    fill('darkgreen');
    text(message, px + 12, y, tw);
  }
}

function mousePressed() {
  if (mouseY < 0 || mouseY > drawHeight || mouseX < 0 || mouseX > canvasWidth) return;
  const s = segmentAt(mouseX, mouseY);
  if (s < 0) return;
  if (rewiring) {
    if (rewireOrder.includes(s)) { message = 'Segment ' + SEG_NAMES[s] + ' is already wired.'; return; }
    rewireOrder.push(s);
    if (rewireOrder.length === 7) {
      applyRewire(rewireOrder);
      rewiring = false;
      rewireButton.html('Rewire');
      message = 'New wiring: ' + rewireOrder.map(x => SEG_NAMES[x]).join(' > ') + '. Turn on Show strip order to check it.';
    } else {
      message = '';
    }
  } else {
    selectedSeg = (selectedSeg === s) ? -1 : s;
  }
}

function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) canvasWidth = Math.floor(container.getBoundingClientRect().width);
}
