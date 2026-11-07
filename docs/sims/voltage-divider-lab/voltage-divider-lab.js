// Voltage Divider Lab MicroSim
// CANVAS_HEIGHT: 495
// Two resistors in series between Vin and ground. The output is taken from
// the point between them:  Vout = Vin * R2 / (R1 + R2).
// A bar-graph voltmeter shows Vout against the Pico's 3.3 V input limit.

// Canvas dimensions - REQUIRED structure
let canvasWidth = 400;
let drawHeight = 380;
let controlHeight = 115;
let canvasHeight = drawHeight + controlHeight;
let margin = 20;
let sliderLeftMargin = 215;
let defaultTextSize = 16;

// Standard E24 resistor values from 100 ohms to 10 kilohms (log spaced)
const E24 = [10, 11, 12, 13, 15, 16, 18, 20, 22, 24, 27, 30, 33, 36, 39, 43, 47, 51, 56, 62, 68, 75, 82, 91];
const R_VALUES = [];
for (const decade of [10, 100]) for (const v of E24) R_VALUES.push(v * decade);
R_VALUES.push(10000);

const SAFE_V = 3.3;     // Pico GPIO logic level
const LIMIT_V = 3.6;    // above this a Pico pin is at real risk

let vinSlider, r1Slider, r2Slider;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));

  vinSlider = createSlider(0, 5, 5, 0.1);
  vinSlider.position(sliderLeftMargin, drawHeight + 8);
  vinSlider.size(canvasWidth - sliderLeftMargin - margin);

  r1Slider = createSlider(0, R_VALUES.length - 1, R_VALUES.indexOf(1000), 1);
  r1Slider.position(sliderLeftMargin, drawHeight + 43);
  r1Slider.size(canvasWidth - sliderLeftMargin - margin);

  r2Slider = createSlider(0, R_VALUES.length - 1, R_VALUES.indexOf(2000), 1);
  r2Slider.position(sliderLeftMargin, drawHeight + 78);
  r2Slider.size(canvasWidth - sliderLeftMargin - margin);

  describe('A voltage divider circuit: resistor R1 on top connected to the input voltage, resistor R2 below it connected ' +
    'to ground, and a probe at the point between them. A bar-graph voltmeter shows the output voltage with a red zone ' +
    'above the Pico safe limit of 3.3 volts, and a label says whether the output is safe for a Pico pin.', LABEL);
}

function fmtR(r) {
  return r >= 1000 ? nf(r / 1000, 1, r % 1000 === 0 ? 1 : (r % 100 === 0 ? 1 : 2)) + ' kΩ' : r + ' Ω';
}

function draw() {
  updateCanvasSize();

  const vin = vinSlider.value();
  const r1 = R_VALUES[r1Slider.value()];
  const r2 = R_VALUES[r2Slider.value()];
  const vout = vin * r2 / (r1 + r2);
  const mA = vin / (r1 + r2) * 1000;

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
  textSize(canvasWidth >= 600 ? 22 : 19);
  text('Voltage Divider Lab', canvasWidth / 2, 10);

  const split = canvasWidth * (canvasWidth >= 600 ? 0.55 : 0.52);
  drawCircuit(split, vin, r1, r2, vout, mA);
  drawMeter(split, vout);
  drawFormula(vin, r1, r2, vout);

  // Slider labels
  noStroke();
  fill('black');
  textAlign(LEFT, CENTER);
  textSize(defaultTextSize);
  text('Input voltage Vin: ' + nf(vin, 1, 1) + ' V', 10, drawHeight + 18);
  text('R1 (top): ' + fmtR(r1), 10, drawHeight + 53);
  text('R2 (bottom): ' + fmtR(r2), 10, drawHeight + 88);
}

// Draw a vertical zigzag resistor between y1 and y2 at x
function resistorV(x, y1, y2, label, col) {
  const lead = 12;
  const zz = 6;
  const w = 10;
  stroke('black');
  strokeWeight(2);
  line(x, y1, x, y1 + lead);
  line(x, y2 - lead, x, y2);
  noFill();
  stroke(col);
  strokeWeight(3);
  beginShape();
  vertex(x, y1 + lead);
  const step = (y2 - y1 - 2 * lead) / zz;
  for (let i = 0; i < zz; i++) {
    vertex(x + (i % 2 === 0 ? w : -w), y1 + lead + step * (i + 0.5));
  }
  vertex(x, y2 - lead);
  endShape();
  noStroke();
  fill('black');
  textAlign(LEFT, CENTER);
  textSize(canvasWidth >= 600 ? 16 : 14);
  text(label, x + 18, (y1 + y2) / 2);
}

function drawCircuit(split, vin, r1, r2, vout, mA) {
  const cx = split * 0.32;
  const railY = 64;
  const midY = 200;
  const gndY = 322;

  // Top rail (Vin)
  stroke('firebrick');
  strokeWeight(4);
  line(margin, railY, split - 20, railY);
  noStroke();
  fill('firebrick');
  textAlign(LEFT, BOTTOM);
  textSize(15);
  text('Vin = ' + nf(vin, 1, 1) + ' V', margin, railY - 4);

  stroke('black');
  strokeWeight(2);
  line(cx, railY, cx, railY + 14);
  resistorV(cx, railY + 14, midY - 8, 'R1 = ' + fmtR(r1), 'peru');
  line(cx, midY - 8, cx, midY + 8);
  resistorV(cx, midY + 8, gndY - 14, 'R2 = ' + fmtR(r2), 'sienna');
  stroke('black');
  strokeWeight(2);
  line(cx, gndY - 14, cx, gndY);

  // Ground symbol
  line(cx - 18, gndY, cx + 18, gndY);
  line(cx - 11, gndY + 6, cx + 11, gndY + 6);
  line(cx - 4, gndY + 12, cx + 4, gndY + 12);
  noStroke();
  fill('black');
  textAlign(LEFT, CENTER);
  textSize(14);
  text('Ground (0 V)', cx + 24, gndY + 6);

  // Probe wire from the midpoint to the meter
  stroke('royalblue');
  strokeWeight(3);
  line(cx, midY, split - 10, midY);
  noStroke();
  fill('royalblue');
  circle(cx, midY, 11);
  textAlign(CENTER, BOTTOM);
  textSize(15);
  text('Vout', (cx + split) / 2 + 22, midY - 4);

  // Current through the divider
  fill('black');
  textAlign(LEFT, TOP);
  textSize(15);
  text('Current: ' + nf(mA, 1, 2) + ' mA', margin, gndY + 22);
}

function drawMeter(split, vout) {
  const right = canvasWidth - margin;
  const mw = min(70, (right - split) * 0.35);
  const mx = split + (right - split) * 0.18;
  const top = 64;
  const bottom = 300;
  const vToY = v => map(v, 0, 5, bottom, top);

  // Scale zones: safe (green), no margin (amber), too high (red)
  noStroke();
  fill(220, 245, 220);
  rect(mx, vToY(SAFE_V), mw, bottom - vToY(SAFE_V));
  fill(255, 236, 179);
  rect(mx, vToY(LIMIT_V), mw, vToY(SAFE_V) - vToY(LIMIT_V));
  fill(255, 205, 210);
  rect(mx, top, mw, vToY(LIMIT_V) - top);

  // Bar showing Vout
  const barCol = vout <= SAFE_V ? 'seagreen' : (vout <= LIMIT_V ? 'orange' : 'crimson');
  fill(barCol);
  rect(mx + mw * 0.2, vToY(vout), mw * 0.6, bottom - vToY(vout));
  noFill();
  stroke('gray');
  strokeWeight(1);
  rect(mx, top, mw, bottom - top);

  // Tick marks every volt
  textSize(13);
  for (let v = 0; v <= 5; v++) {
    stroke('gray');
    line(mx - 6, vToY(v), mx, vToY(v));
    noStroke();
    fill('black');
    textAlign(RIGHT, CENTER);
    text(v + ' V', mx - 8, vToY(v));
  }
  // 3.3 V limit line
  stroke('crimson');
  strokeWeight(2);
  drawingContext.setLineDash([6, 4]);
  line(mx - 4, vToY(SAFE_V), mx + mw + 8, vToY(SAFE_V));
  drawingContext.setLineDash([]);
  noStroke();
  fill('crimson');
  textAlign(LEFT, CENTER);
  textSize(13);
  text('3.3 V', mx + mw + 10, vToY(SAFE_V));

  // Readout and verdict
  const cxm = mx + mw / 2;
  fill('black');
  textAlign(CENTER, TOP);
  textStyle(BOLD);
  textSize(canvasWidth >= 600 ? 20 : 16);
  text('Vout = ' + nf(vout, 1, 2) + ' V', min(cxm + 20, right - 70), bottom + 8);
  textStyle(NORMAL);
  let verdict, vcol;
  if (vout <= SAFE_V) { verdict = 'Safe for Pico'; vcol = 'darkgreen'; }
  else if (vout <= LIMIT_V) { verdict = 'Just over 3.3 V: no margin'; vcol = 'chocolate'; }
  else { verdict = 'Too high!'; vcol = 'crimson'; }
  fill(vcol);
  textStyle(BOLD);
  textSize(canvasWidth >= 600 ? 18 : 14);
  text(verdict, min(cxm + 20, right - 70), bottom + 34);
  textStyle(NORMAL);
}

function drawFormula(vin, r1, r2, vout) {
  noStroke();
  fill('midnightblue');
  textAlign(CENTER, CENTER);
  textSize(canvasWidth >= 600 ? 15 : 12);
  const s = 'Vout = ' + nf(vin, 1, 1) + ' × ' + r2 + ' / (' + r1 + ' + ' + r2 + ') = ' + nf(vout, 1, 2) + ' V';
  text(s, canvasWidth / 2, drawHeight - 14);
}

function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) {
    canvasWidth = container.offsetWidth;
    if (typeof vinSlider !== 'undefined') {
      const w = canvasWidth - sliderLeftMargin - margin;
      vinSlider.size(w);
      r1Slider.size(w);
      r2Slider.size(w);
    }
  }
}
