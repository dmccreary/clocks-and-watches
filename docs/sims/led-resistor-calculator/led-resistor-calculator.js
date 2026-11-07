// LED Resistor Calculator MicroSim
// CANVAS_HEIGHT: 450
// A supply, a current-limiting resistor, and an LED in one loop.
// Model: the LED drops a fixed forward voltage Vf, so the resistor gets the
// rest and sets the current:  I = (Vsupply - Vf) / R.
// Brightness follows the current; above 20 mA a warning appears.

// Canvas dimensions - REQUIRED structure
let canvasWidth = 400;
let drawHeight = 370;
let controlHeight = 80;
let canvasHeight = drawHeight + controlHeight;
let margin = 20;
let sliderLeftMargin = 190;
let defaultTextSize = 16;

const LEDS = {
  Red: { vf: 2.0, col: [230, 30, 30] },
  Yellow: { vf: 2.1, col: [250, 210, 0] },
  Green: { vf: 2.1, col: [40, 200, 60] },
  Blue: { vf: 3.1, col: [40, 90, 255] },
  White: { vf: 3.2, col: [240, 240, 255] }
};
const R_STD = [10, 22, 33, 47, 68, 100, 150, 220, 330, 470, 680, 1000, 2200];
const MAX_MA = 20;       // safe maximum for a typical 5 mm LED
const TARGET_MA = 10;    // the chapter's design target

let colorSelect, supplySelect, rSlider;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));

  colorSelect = createSelect();
  for (const k of Object.keys(LEDS)) colorSelect.option(k + ' LED (' + nf(LEDS[k].vf, 1, 1) + ' V)', k);
  colorSelect.selected('Red');
  colorSelect.position(10, drawHeight + 10);

  supplySelect = createSelect();
  supplySelect.option('3.3 V (Pico pin)', '3.3');
  supplySelect.option('5 V (USB)', '5');
  supplySelect.selected('3.3');
  supplySelect.position(190, drawHeight + 10);

  rSlider = createSlider(0, R_STD.length - 1, R_STD.indexOf(330), 1);
  rSlider.position(sliderLeftMargin, drawHeight + 45);
  rSlider.size(canvasWidth - sliderLeftMargin - margin);

  describe('An LED circuit with a power supply, a resistor, and an LED in a loop. Choosing the LED color, supply ' +
    'voltage, and a standard resistor value changes the calculated current. The LED glows brighter with more ' +
    'current, and a warning icon appears above the 20 milliamp safe maximum.', LABEL);
}

function fmtR(r) {
  return r >= 1000 ? nf(r / 1000, 1, 1) + ' kΩ' : r + ' Ω';
}

function draw() {
  updateCanvasSize();

  const led = LEDS[colorSelect.value()];
  const vs = parseFloat(supplySelect.value());
  const r = R_STD[rSlider.value()];
  const vr = max(0, vs - led.vf);
  const mA = vr / r * 1000;

  stroke('silver');
  strokeWeight(1);
  fill('aliceblue');
  rect(0, 0, canvasWidth, drawHeight);
  fill('white');
  rect(0, drawHeight, canvasWidth, controlHeight);

  noStroke();
  fill('black');
  textAlign(CENTER, TOP);
  textSize(canvasWidth >= 600 ? 22 : 19);
  text('LED Resistor Calculator', canvasWidth / 2, 10);

  const narrow = canvasWidth < 600;
  const circuitW = narrow ? canvasWidth : canvasWidth * 0.52;
  drawCircuit(circuitW, narrow ? 190 : 300, vs, r, led, mA);
  drawReadouts(narrow, circuitW, vs, r, led, vr, mA);

  noStroke();
  fill('black');
  textAlign(LEFT, CENTER);
  textSize(defaultTextSize);
  text('Resistor: ' + fmtR(r), 10, drawHeight + 55);
}

function drawCircuit(w, h, vs, r, led, mA) {
  const left = margin + 30;
  const right = w - margin - 30;
  const top = 64;
  const bottom = top + h - 40;
  const midY = (top + bottom) / 2;
  const sc = min(1, (right - left) / 300);

  stroke('black');
  strokeWeight(2.5);
  noFill();
  // Supply on the left side: long plate (+) on top, short plate (-) below
  line(left, top, left, midY - 12);
  line(left, midY + 12, left, bottom);
  line(left - 20, midY - 12, left + 20, midY - 12);
  strokeWeight(4);
  line(left - 11, midY + 12, left + 11, midY + 12);
  strokeWeight(2.5);
  noStroke();
  fill('black');
  textAlign(RIGHT, CENTER);
  textSize(15);
  text('+', left - 24, midY - 14);
  text('−', left - 24, midY + 14);
  textAlign(LEFT, CENTER);
  text(nf(vs, 1, 1) + ' V', left + 24, midY);

  // Top wire with the resistor
  const rx1 = left + (right - left) * 0.3;
  const rx2 = rx1 + 90 * sc;
  stroke('black');
  strokeWeight(2.5);
  line(left, top, rx1, top);
  noFill();
  stroke('peru');
  strokeWeight(3);
  beginShape();
  vertex(rx1, top);
  for (let i = 0; i < 6; i++) vertex(rx1 + (rx2 - rx1) * (i + 0.5) / 6, top + (i % 2 === 0 ? -11 : 11));
  vertex(rx2, top);
  endShape();
  stroke('black');
  strokeWeight(2.5);
  line(rx2, top, right, top);
  noStroke();
  fill('black');
  textAlign(CENTER, TOP);
  textSize(15);
  text(fmtR(r), (rx1 + rx2) / 2, top + 15);

  // Right side: LED pointing down, then back along the bottom wire
  const ly1 = midY - 22;
  const ly2 = midY + 18;
  stroke('black');
  strokeWeight(2.5);
  line(right, top, right, ly1);
  line(right, ly2, right, bottom);
  line(right, bottom, left, bottom);

  // Glow: brightness rises with current (square root looks more natural)
  const glow = constrain(sqrt(mA / MAX_MA), 0, 1.15);
  const [cr, cg, cb] = led.col;
  noStroke();
  if (glow > 0.02) {
    for (let k = 4; k >= 1; k--) {
      fill(cr, cg, cb, 40 * glow);
      circle(right, midY - 2, 30 + k * 18 * glow);
    }
  }
  // LED symbol filled with its color at the current brightness
  stroke('black');
  strokeWeight(2);
  fill(lerp(255, cr, glow * 0.9), lerp(255, cg, glow * 0.9), lerp(255, cb, glow * 0.9));
  triangle(right - 16, ly1, right + 16, ly1, right, ly2);
  line(right - 16, ly2, right + 16, ly2);
  noStroke();
  fill('black');
  textAlign(LEFT, CENTER);
  textSize(14);
  text('LED', right + 20, midY - 2);

  // Current direction arrow on the top wire
  if (mA > 0) {
    stroke('royalblue');
    strokeWeight(2);
    const ax = left + (rx1 - left) * 0.5;
    line(ax - 14, top - 14, ax + 10, top - 14);
    noStroke();
    fill('royalblue');
    triangle(ax + 14, top - 14, ax + 6, top - 19, ax + 6, top - 9);
  }

  // Warning icon above the safe maximum
  if (mA > MAX_MA) drawWarning(right - 46, top + 22);
}

function drawWarning(x, y) {
  stroke('darkred');
  strokeWeight(2);
  fill('gold');
  triangle(x, y + 32, x + 18, y, x + 36, y + 32);
  noStroke();
  fill('darkred');
  textAlign(CENTER, CENTER);
  textStyle(BOLD);
  textSize(20);
  text('!', x + 18, y + 20);
  textStyle(NORMAL);
}

function drawReadouts(narrow, circuitW, vs, r, led, vr, mA) {
  const x = narrow ? margin : circuitW + 4;
  const y = narrow ? 238 : 56;
  const w = narrow ? canvasWidth - 2 * margin : canvasWidth - circuitW - margin - 4;
  const h = narrow ? drawHeight - y - 8 : drawHeight - y - 10;
  stroke('silver');
  strokeWeight(1);
  fill(255, 255, 255, 235);
  rect(x, y, w, h, 10);

  const tx = x + 12;
  noStroke();
  textAlign(LEFT, TOP);
  textSize(narrow ? 13 : 15);
  fill('black');
  let ly = y + 10;
  const lh = narrow ? 17 : 22;

  // Current, big
  let status, scol;
  if (vs <= led.vf) { status = 'LED off: supply is below its forward voltage'; scol = 'dimgray'; }
  else if (mA > MAX_MA) { status = 'Too much current! Above 20 mA'; scol = 'crimson'; }
  else if (mA < 2) { status = 'Very dim'; scol = 'darkgoldenrod'; }
  else { status = 'Safe current'; scol = 'darkgreen'; }
  textStyle(BOLD);
  textSize(narrow ? 18 : 22);
  fill(mA > MAX_MA ? 'crimson' : 'black');
  text('Current: ' + (mA >= 100 ? nf(mA, 1, 0) : nf(mA, 1, 1)) + ' mA', tx, ly);
  ly += narrow ? 24 : 30;
  textSize(narrow ? 14 : 16);
  fill(scol);
  text(status, tx, ly, w - 20, 40);
  textStyle(NORMAL);
  ly += narrow ? 22 : 28;

  textSize(narrow ? 13 : 15);
  fill('black');
  if (narrow) {
    text('Vf = ' + nf(led.vf, 1, 1) + ' V,  resistor gets ' + nf(vr, 1, 1) + ' V', tx, ly);
    ly += lh;
  } else {
    text('LED forward voltage: ' + nf(led.vf, 1, 1) + ' V', tx, ly); ly += lh;
    text('Voltage on resistor: ' + nf(vr, 1, 1) + ' V', tx, ly); ly += lh;
  }
  fill('midnightblue');
  text('I = (' + nf(vs, 1, 1) + ' − ' + nf(led.vf, 1, 1) + ') / ' + r + ' Ω', tx, ly);
  ly += lh + (narrow ? 2 : 8);

  // Resistor needed for the 10 mA target
  fill('black');
  if (vs > led.vf) {
    const need = (vs - led.vf) / (TARGET_MA / 1000);
    const pick = R_STD.find(v => v >= need) || R_STD[R_STD.length - 1];
    textStyle(BOLD);
    text('For ' + TARGET_MA + ' mA you need ' + nf(need, 1, 0) + ' Ω', tx, ly);
    textStyle(NORMAL);
    ly += lh;
    text('Nearest standard value at or above: ' + fmtR(pick), tx, ly, w - 20, 40);
  } else {
    text('Choose a higher supply voltage to light this LED.', tx, ly, w - 20, 40);
  }

  // Brightness bar
  if (!narrow) {
    const by = y + h - 34;
    const bw = w - 24;
    fill('black');
    textSize(13);
    text('Brightness', tx, by - 17);
    stroke('gray');
    noFill();
    rect(tx, by, bw, 14, 4);
    noStroke();
    fill(mA > MAX_MA ? 'crimson' : 'orange');
    rect(tx, by, bw * constrain(mA / MAX_MA, 0, 1), 14, 4);
  }
}

function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) {
    canvasWidth = container.offsetWidth;
    if (typeof rSlider !== 'undefined') rSlider.size(canvasWidth - sliderLeftMargin - margin);
  }
}
