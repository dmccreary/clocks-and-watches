// Polar to Screen Converter
// CANVAS_HEIGHT: 630
// Converts a clock-style polar position (r, theta clockwise from 12 o'clock) to pixel
// coordinates on a 240 x 240 screen whose origin is the top-left corner:
//   x = cx + r * sin(theta)      y = cy - r * cos(theta)
// Values are truncated toward zero, like int() in the chapter's MicroPython code.

let canvasWidth = 700;
let drawHeight = 480;
let controlHeight = 150;
let canvasHeight = drawHeight + controlHeight;
let margin = 20;
let sliderLeftMargin = 150;
let defaultTextSize = 16;

const SCREEN = 240, CX = 120, CY = 120;

let radiusSlider, angleSlider, formulaCheckbox, predictCheckbox, newButton;
let xInput, yInput, checkButton;
let revealed = true;      // in Predict mode the answer stays hidden until Check
let feedback = '';
let feedbackColor = 'black';

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  radiusSlider = createSlider(0, 120, 100, 1);
  radiusSlider.position(sliderLeftMargin, drawHeight + 10);
  radiusSlider.input(onSliderChange);
  angleSlider = createSlider(0, 359, 90, 1);
  angleSlider.position(sliderLeftMargin, drawHeight + 45);
  angleSlider.input(onSliderChange);

  formulaCheckbox = createCheckbox(' Show formula', true);
  formulaCheckbox.position(10, drawHeight + 80);
  predictCheckbox = createCheckbox(' Predict mode', false);
  predictCheckbox.position(150, drawHeight + 80);
  predictCheckbox.changed(() => {
    revealed = !predictCheckbox.checked();
    feedback = predictCheckbox.checked() ? 'Type your x and y, then press Check.' : '';
    feedbackColor = 'black';
  });
  newButton = createButton('New point');
  newButton.position(290, drawHeight + 78);
  newButton.mousePressed(newPoint);

  xInput = createInput('', 'number');
  xInput.size(60);
  xInput.position(40, drawHeight + 114);
  yInput = createInput('', 'number');
  yInput.size(60);
  yInput.position(150, drawHeight + 114);
  checkButton = createButton('Check');
  checkButton.position(230, drawHeight + 113);
  checkButton.mousePressed(checkPrediction);

  sizeSliders();
  describe('A 240 by 240 pixel screen grid with the origin at the top-left. A line runs from the ' +
    'center (120, 120) to a point set by a radius and a clock angle measured clockwise from 12. ' +
    'The point is labeled with its pixel coordinates and its polar coordinates.', LABEL);
}

function onSliderChange() {
  if (predictCheckbox.checked()) {
    revealed = false;
    feedback = 'Type your x and y, then press Check.';
    feedbackColor = 'black';
  }
}

function newPoint() {
  radiusSlider.value(floor(random(2, 13)) * 10);
  angleSlider.value(floor(random(0, 24)) * 15);
  if (!predictCheckbox.checked()) predictCheckbox.checked(true);
  revealed = false;
  xInput.value('');
  yInput.value('');
  feedback = 'New point. Type your x and y, then press Check.';
  feedbackColor = 'black';
}

function computePoint() {
  let r = radiusSlider.value();
  let deg = angleSlider.value();
  let a = radians(deg);
  let sx = r * sin(a), cy = r * cos(a);
  return { r: r, deg: deg, sx: sx, cy: cy, x: CX + Math.trunc(sx), y: CY - Math.trunc(cy) };
}

function checkPrediction() {
  if (!predictCheckbox.checked()) {
    feedback = 'Turn on Predict mode (or press New point) to practice.';
    feedbackColor = 'black';
    return;
  }
  let p = computePoint();
  let gx = parseFloat(xInput.value()), gy = parseFloat(yInput.value());
  if (isNaN(gx) || isNaN(gy)) {
    feedback = 'Type a number in both boxes.';
    feedbackColor = 'firebrick';
    return;
  }
  let okX = abs(gx - p.x) <= 1, okY = abs(gy - p.y) <= 1;
  revealed = true;
  if (okX && okY) {
    feedback = 'Correct! The point is at (' + p.x + ', ' + p.y + ').';
    feedbackColor = 'darkgreen';
  } else {
    feedback = 'Answer: (' + p.x + ', ' + p.y + '). ' + (okX ? 'x was right. ' : 'Check x. ') +
      (okY ? 'y was right.' : 'Check y: screen y grows downward.');
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

  let wide = canvasWidth >= 620;
  let G = wide ? min(drawHeight - 100, canvasWidth * 0.55) : min(canvasWidth - 70, 240);
  let gx = wide ? 50 : (canvasWidth - G) / 2 + 10;
  let gy = 58;

  noStroke();
  fill('black');
  textAlign(CENTER, TOP);
  textSize(24);
  text('Polar to Screen Converter', canvasWidth / 2, 8);

  let p = computePoint();
  drawGrid(gx, gy, G);
  drawPoint(gx, gy, G, p);
  if (wide) drawPanel(gx + G + 30, gy, canvasWidth - (gx + G + 30) - margin, p);
  else drawPanel(margin, gy + G + 14, canvasWidth - 2 * margin, p);

  // control labels
  noStroke();
  fill('black');
  textSize(16);
  textAlign(LEFT, CENTER);
  text('Radius r: ' + p.r, 10, drawHeight + 20);
  text('Angle θ: ' + p.deg + '°', 10, drawHeight + 55);
  text('x =', 10, drawHeight + 125);
  text('y =', 120, drawHeight + 125);
  // feedback line at the bottom of the drawing region
  if (feedback) {
    textSize(15);
    fill(feedbackColor);
    textAlign(CENTER, CENTER);
    text(feedback, canvasWidth / 2, drawHeight - 14);
  }
}

function drawGrid(gx, gy, G) {
  let k = G / SCREEN;
  // screen
  stroke('dimgray');
  fill('black');
  rect(gx, gy, G, G);
  // grid lines every 20 px, labels every 40 px
  for (let v = 0; v <= SCREEN; v += 20) {
    stroke(v % 40 === 0 ? color(70) : color(40));
    line(gx + v * k, gy, gx + v * k, gy + G);
    line(gx, gy + v * k, gx + G, gy + v * k);
  }
  noStroke();
  fill('dimgray');
  textSize(11);
  textAlign(CENTER, BOTTOM);
  for (let v = 0; v <= SCREEN; v += 40) text(v, gx + v * k, gy - 2);
  textAlign(RIGHT, CENTER);
  for (let v = 0; v <= SCREEN; v += 40) text(v, gx - 4, gy + v * k);
  // axis names
  fill('black');
  textSize(13);
  textAlign(LEFT, BOTTOM);
  text('x →', gx + G + 16, gy - 2);
  textAlign(CENTER, TOP);
  text('y ↓', gx - 20, gy + G + 6);
  textAlign(LEFT, BOTTOM);
  fill('dimgray');
  text('(0, 0)', gx - 44, gy - 14);

  // clock reference labels on the screen
  fill('gray');
  textSize(12);
  textAlign(CENTER, CENTER);
  text('12', gx + CX * k, gy + 8);
  text('3', gx + G - 8, gy + CY * k);
  text('6', gx + CX * k, gy + G - 8);
  text('9', gx + 8, gy + CY * k);
}

function drawPoint(gx, gy, G, p) {
  let k = G / SCREEN;
  let cxs = gx + CX * k, cys = gy + CY * k;
  // radius circle
  noFill();
  stroke(90, 90, 140);
  circle(cxs, cys, 2 * p.r * k);
  // angle arc from 12 o'clock, clockwise
  if (p.deg > 0 && p.r > 0) {
    stroke('darkorange');
    strokeWeight(2);
    let ar = min(30, p.r * k);
    arc(cxs, cys, 2 * ar, 2 * ar, -HALF_PI, -HALF_PI + radians(p.deg));
    strokeWeight(1);
  }
  // center
  noStroke();
  fill('white');
  circle(cxs, cys, 6);

  let show = revealed || !predictCheckbox.checked();
  if (!show) {
    // only the direction hint: a short dashed ray
    noStroke();
    fill('yellow');
    textSize(14);
    textAlign(CENTER, CENTER);
    text('?', cxs + (p.sx * k) * 0.5 + 10, cys - (p.cy * k) * 0.5);
    return;
  }
  let px = gx + p.x * k, py = gy + p.y * k;
  // projections to the axes
  stroke('gold');
  drawingContext.setLineDash([4, 4]);
  line(px, py, px, gy);
  line(px, py, gx, py);
  drawingContext.setLineDash([]);
  // radius line
  stroke('lime');
  strokeWeight(3);
  line(cxs, cys, px, py);
  strokeWeight(1);
  noStroke();
  fill('orangered');
  circle(px, py, 12);
  // labels on axes
  fill('darkorange');
  textSize(12);
  textAlign(CENTER, BOTTOM);
  text(p.x, px, gy - 14);
  textAlign(RIGHT, CENTER);
  text(p.y, gx - 26, py);
  // point label
  let lbl = '(' + p.x + ', ' + p.y + ')';
  textSize(14);
  let tw = textWidth(lbl);
  let lx = px + 10, ly = py - 12;
  if (lx + tw > gx + G - 2) lx = px - 10 - tw;
  if (ly < gy + 12) ly = py + 14;
  fill(0, 0, 0, 170);
  rect(lx - 3, ly - 9, tw + 6, 18, 3);
  fill('white');
  textAlign(LEFT, CENTER);
  text(lbl, lx, ly);
}

function drawPanel(x, y, w, p) {
  let lines = [];
  let show = revealed || !predictCheckbox.checked();
  let compact = canvasWidth < 620;
  lines.push(['Polar: r = ' + p.r + ', \u03B8 = ' + p.deg + '\u00B0', 'black', true]);
  lines.push(['Screen: ' + (show ? 'x = ' + p.x + ', y = ' + p.y : 'x = ?, y = ?'), 'black', true]);
  if (!compact) lines.push(['center (cx, cy) = (120, 120)', 'dimgray', false]);
  if (formulaCheckbox.checked()) {
    if (!compact) lines.push(['x = cx + r \u00D7 sin \u03B8', 'royalblue', false]);
    lines.push([(compact ? 'x' : '  ') + ' = 120 + ' + p.r + ' \u00D7 sin(' + p.deg + '\u00B0)', 'royalblue', false]);
    lines.push([show ? '   = 120 + ' + fmtSigned(Math.trunc(p.sx)) + ' = ' + p.x : '   = ?', 'royalblue', false]);
    if (!compact) lines.push(['y = cy \u2212 r \u00D7 cos \u03B8', 'crimson', false]);
    lines.push([(compact ? 'y' : '  ') + ' = 120 \u2212 ' + p.r + ' \u00D7 cos(' + p.deg + '\u00B0)', 'crimson', false]);
    lines.push([show ? '   = 120 \u2212 ' + fmtSigned(Math.trunc(p.cy)) + ' = ' + p.y : '   = ?', 'crimson', false]);
  }
  let lh = compact ? 18 : 24;
  let h = lines.length * lh + 14;
  stroke('lightgray');
  fill(255, 255, 255, 235);
  rect(x, y, w, h, 10);
  noStroke();
  textAlign(LEFT, TOP);
  textSize(compact ? 14 : 16);
  for (let i = 0; i < lines.length; i++) {
    fill(lines[i][1]);
    textStyle(lines[i][2] ? BOLD : NORMAL);
    text(lines[i][0], x + 10, y + 8 + i * lh);
  }
  textStyle(NORMAL);
}

function fmtSigned(v) {
  return v < 0 ? '(' + v + ')' : String(v);
}

function sizeSliders() {
  if (typeof radiusSlider === 'undefined') return;
  radiusSlider.size(canvasWidth - sliderLeftMargin - margin);
  angleSlider.size(canvasWidth - sliderLeftMargin - margin);
}

function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) {
    canvasWidth = max(360, container.offsetWidth);
    sizeSliders();
  }
}
