// Unit Circle Explorer
// CANVAS_HEIGHT: 490
// Sine and cosine are the vertical and horizontal parts of a point on a circle of radius 1.
// One angle variable drives the circle, the cos/sin bars and the two graphs.
// Step-through design: the angle slider and +/- 15 degree step buttons replace continuous play.

let canvasWidth = 700;
let drawHeight = 410;
let controlHeight = 80;
let canvasHeight = drawHeight + controlHeight;
let margin = 20;
let sliderLeftMargin = 250;
let defaultTextSize = 16;

let angleSlider, backButton, fwdButton, unitSelect, triangleCheckbox, valuesCheckbox;

const SIN_COLOR = 'crimson';
const COS_COLOR = 'royalblue';

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  backButton = createButton('-15°');
  backButton.position(10, drawHeight + 8);
  backButton.mousePressed(() => stepAngle(-15));
  fwdButton = createButton('+15°');
  fwdButton.position(62, drawHeight + 8);
  fwdButton.mousePressed(() => stepAngle(15));

  angleSlider = createSlider(0, 360, 30, 1);
  angleSlider.position(sliderLeftMargin, drawHeight + 10);
  angleSlider.size(canvasWidth - sliderLeftMargin - margin);

  unitSelect = createSelect();
  unitSelect.option('Degrees');
  unitSelect.option('Radians');
  unitSelect.selected('Degrees');
  unitSelect.position(10, drawHeight + 46);
  unitSelect.changed(() => {
    let rad = unitSelect.value() === 'Radians';
    backButton.html(rad ? '-π/12' : '-15°');
    fwdButton.html(rad ? '+π/12' : '+15°');
  });

  triangleCheckbox = createCheckbox(' Right triangle', true);
  triangleCheckbox.position(110, drawHeight + 46);
  valuesCheckbox = createCheckbox(' Values', true);
  valuesCheckbox.position(250, drawHeight + 46);

  describe('A unit circle with a radius at an adjustable angle. A blue horizontal bar shows cosine ' +
    'and a red vertical bar shows sine. Two graphs plot sine and cosine against the angle with a ' +
    'marker at the current angle.', LABEL);
}

function stepAngle(d) {
  let a = angleSlider.value() + d;
  if (a > 360) a -= 360;
  if (a < 0) a += 360;
  angleSlider.value(a);
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
  text('Unit Circle Explorer', canvasWidth / 2, 8);

  let deg = angleSlider.value();
  let th = radians(deg);
  let wide = canvasWidth >= 600;

  // ---- layout ----
  let cx, cy, R, gx, gy, gw, gh, gap;
  if (wide) {
    let cw = canvasWidth * 0.5;
    R = min(cw / 2 - 55, 122);
    cx = cw / 2 + 15;
    cy = 88 + R;
    gx = cw + 30; gw = canvasWidth - gx - margin - 10;
    gy = 58; gh = (drawHeight - gy - 30) / 2 - 14; gap = 40;
  } else {
    R = min(canvasWidth / 2 - 60, 80);
    cx = canvasWidth / 2;
    cy = 88 + R;
    gx = 46; gw = (canvasWidth - 46 - margin - 40) / 2;
    gy = cy + R + 66; gh = drawHeight - gy - 22; gap = 0;
  }

  drawCircle(cx, cy, R, th);
  if (wide) {
    drawGraph(gx, gy, gw, gh, 'sin', deg);
    drawGraph(gx, gy + gh + gap, gw, gh, 'cos', deg);
  } else {
    drawGraph(gx, gy, gw, gh, 'sin', deg);
    drawGraph(gx + gw + 40, gy, gw, gh, 'cos', deg);
  }
  if (valuesCheckbox.checked()) drawValues(deg, th, cx);

  // control label
  noStroke();
  fill('black');
  textSize(16);
  textAlign(LEFT, CENTER);
  text('Angle: ' + angleText(deg), 120, drawHeight + 20);
}

function angleText(deg) {
  if (unitSelect.value() === 'Radians') return nf(radians(deg), 1, 2) + ' rad';
  return deg + '°';
}

function drawCircle(cx, cy, R, th) {
  let px = cx + R * cos(th);
  let py = cy - R * sin(th);

  // axes
  stroke('lightgray');
  line(cx - R - 14, cy, cx + R + 14, cy);
  line(cx, cy - R - 14, cx, cy + R + 14);
  // circle
  noFill();
  stroke('dimgray');
  strokeWeight(2);
  circle(cx, cy, 2 * R);
  strokeWeight(1);
  noStroke();
  fill('dimgray');
  textSize(12);
  textAlign(LEFT, TOP);
  text('1', cx + R + 3, cy + 2);
  text('-1', cx - R - 16, cy + 2);
  textAlign(LEFT, BOTTOM);
  text('1', cx + 4, cy - R - 2);

  // angle arc
  noFill();
  stroke('darkorange');
  strokeWeight(2);
  if (th > 0.001) arc(cx, cy, 44, 44, -th, 0);
  strokeWeight(1);

  // right triangle legs
  if (triangleCheckbox.checked()) {
    strokeWeight(4);
    stroke(COS_COLOR);
    line(cx, cy, px, cy);
    stroke(SIN_COLOR);
    line(px, cy, px, py);
    strokeWeight(1);
    // right-angle mark
    if (abs(px - cx) > 14 && abs(py - cy) > 14) {
      noFill();
      stroke('black');
      let sx = px > cx ? -9 : 9, sy = py < cy ? -9 : 9;
      rect(min(px, px + sx), min(cy, cy + sy), 9, 9);
    }
  }
  // projection guide lines to the bars
  stroke('silver');
  drawingContext.setLineDash([4, 4]);
  line(px, py, px, cy + R + 22);
  line(px, py, cx - R - 22, py);
  drawingContext.setLineDash([]);

  // radius and point
  stroke('black');
  strokeWeight(2);
  line(cx, cy, px, py);
  strokeWeight(1);
  noStroke();
  fill('darkorange');
  circle(px, py, 14);

  // cos bar (horizontal, below the circle)
  let by = cy + R + 22;
  stroke('lightgray');
  strokeWeight(10);
  line(cx - R, by, cx + R, by);
  stroke(COS_COLOR);
  line(cx, by, px, by);
  strokeWeight(1);
  noStroke();
  fill(COS_COLOR);
  textSize(14);
  textAlign(CENTER, TOP);
  text('cos', cx, by + 8);

  // sin bar (vertical, left of the circle)
  let bx = cx - R - 22;
  stroke('lightgray');
  strokeWeight(10);
  line(bx, cy - R, bx, cy + R);
  stroke(SIN_COLOR);
  line(bx, cy, bx, py);
  strokeWeight(1);
  noStroke();
  fill(SIN_COLOR);
  textAlign(RIGHT, CENTER);
  text('sin', bx - 8, cy);
}

function drawGraph(x, y, w, h, which, deg) {
  let col = which === 'sin' ? SIN_COLOR : COS_COLOR;
  // frame
  stroke('lightgray');
  fill('white');
  rect(x, y, w, h);
  // zero line
  let midY = y + h / 2;
  stroke('gainsboro');
  line(x, midY, x + w, midY);
  // tick labels
  let rad = unitSelect.value() === 'Radians';
  let tickLabels = rad ? ['0', 'π/2', 'π', '3π/2', '2π'] : ['0', '90', '180', '270', '360'];
  noStroke();
  fill('dimgray');
  textSize(11);
  textAlign(CENTER, TOP);
  for (let i = 0; i <= 4; i++) {
    let tx = x + (w * i) / 4;
    stroke('gainsboro');
    line(tx, y, tx, y + h);
    noStroke();
    text(tickLabels[i], tx, y + h + 3);
  }
  textAlign(RIGHT, CENTER);
  text('1', x - 4, y + 4);
  text('0', x - 4, midY);
  text('-1', x - 4, y + h - 4);
  // curve
  noFill();
  stroke(col);
  strokeWeight(2);
  beginShape();
  for (let d = 0; d <= 360; d += 4) {
    let v = which === 'sin' ? sin(radians(d)) : cos(radians(d));
    vertex(x + (w * d) / 360, midY - v * (h / 2 - 4));
  }
  endShape();
  strokeWeight(1);
  // current angle marker
  let v = which === 'sin' ? sin(radians(deg)) : cos(radians(deg));
  let mx = x + (w * deg) / 360, my = midY - v * (h / 2 - 4);
  stroke('darkorange');
  line(mx, y, mx, y + h);
  stroke(col);
  strokeWeight(3);
  line(mx, midY, mx, my);
  strokeWeight(1);
  noStroke();
  fill('darkorange');
  circle(mx, my, 10);
  // name
  fill(col);
  textSize(14);
  textAlign(LEFT, BOTTOM);
  text(which + '(angle)', x, y - 2);
}

function drawValues(deg, th, cx) {
  let c = cos(th), s = sin(th);
  if (abs(c) < 0.0005) c = 0;
  if (abs(s) < 0.0005) s = 0;
  noStroke();
  textSize(14);
  textAlign(CENTER, TOP);
  fill('black');
  text('angle = ' + angleText(deg) + '    point = (' + nf(c, 1, 2) + ', ' + nf(s, 1, 2) + ')', cx, 38);
  let a = 'cos = ' + nf(c, 1, 3), b = 'sin = ' + nf(s, 1, 3);
  let gapW = 24;
  let total = textWidth(a) + gapW + textWidth(b);
  textAlign(LEFT, TOP);
  fill(COS_COLOR);
  text(a, cx - total / 2, 56);
  fill(SIN_COLOR);
  text(b, cx - total / 2 + textWidth(a) + gapW, 56);
}

function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) {
    canvasWidth = max(360, container.offsetWidth);
    if (typeof angleSlider !== 'undefined') angleSlider.size(canvasWidth - sliderLeftMargin - margin);
  }
}
