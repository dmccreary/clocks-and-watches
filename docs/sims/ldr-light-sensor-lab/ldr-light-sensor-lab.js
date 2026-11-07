// LDR Light Sensor Lab MicroSim
// CANVAS_HEIGHT: 535
// A light-dependent resistor (LDR) and a fixed resistor form a voltage divider into ADC0 (GP26).
// Room brightness sets the LDR resistance (1 megohm in the dark down to 500 ohms in sunlight),
// and the divider formula Vout = 3.3 x Rfixed / (Rldr + Rfixed) gives the voltage and ADC reading.
// Static and slider-driven; a checkbox hides the answers so students can predict first.

let canvasWidth = 400;
let drawHeight = 420;
let controlHeight = 115;
let canvasHeight = drawHeight + controlHeight;
let margin = 25;
let sliderLeftMargin = 300;
let defaultTextSize = 16;

let lightSlider, fixedSlider, hideCheckbox;

// Standard resistor values (kilohms) for the fixed resistor slider
const FIXED_K = [1, 1.5, 2.2, 3.3, 4.7, 6.8, 10, 15, 22, 33, 47, 68, 100];

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));

  lightSlider = createSlider(0, 100, 82, 1);
  lightSlider.position(sliderLeftMargin, drawHeight + 8);
  lightSlider.size(canvasWidth - sliderLeftMargin - margin);

  fixedSlider = createSlider(0, FIXED_K.length - 1, 6, 1);
  fixedSlider.position(sliderLeftMargin, drawHeight + 43);
  fixedSlider.size(canvasWidth - sliderLeftMargin - margin);

  hideCheckbox = createCheckbox('Hide Vout and the ADC reading (predict first)', false);
  hideCheckbox.position(10, drawHeight + 80);

  describe('A voltage divider schematic: 3.3 volts, a light-dependent resistor, the ADC pin GP26, a fixed resistor and ground. Beside it a room whose brightness follows a slider, a gauge showing the ADC reading from 0 to 65535, and readouts of the LDR resistance, the output voltage and the raw ADC value worked through the divider formula.');
}

// Brightness 0..100 maps logarithmically from 1 megohm (dark) to 500 ohms (sunlight)
// The value is rounded to 2 significant figures so the readouts match hand calculations.
function ldrOhms(b) {
  const r = 1e6 * pow(500 / 1e6, b / 100);
  const p = pow(10, floor(Math.log10(r)) - 1);
  return round(r / p) * p;
}

function lightName(b) {
  if (b < 15) return 'Dark room';
  if (b < 35) return 'Dim room';
  if (b < 60) return 'Room lights on';
  if (b < 86) return 'Bright room';
  if (b < 94) return 'Daylight by a window';
  return 'Direct sunlight';
}

// Volts with 2 decimals, or 3 below 1 V so small readings still calculate correctly
function vText(v) {
  return nf(v, 1, v < 1 ? 3 : 2);
}

function ohmsText(r) {
  if (r >= 1e6) return nf(r / 1e6, 1, 2) + ' MΩ';
  if (r >= 1000) return (r >= 100000 ? nf(r / 1000, 1, 0) : nf(r / 1000, 1, 1)) + ' kΩ';
  return nf(r, 1, 0) + ' Ω';
}

function draw() {
  updateCanvasSize();

  stroke('silver');
  strokeWeight(1);
  fill('aliceblue');
  rect(0, 0, canvasWidth, drawHeight);
  fill('white');
  rect(0, drawHeight, canvasWidth, controlHeight);

  const b = lightSlider.value();
  const rL = ldrOhms(b);
  const rF = FIXED_K[fixedSlider.value()] * 1000;
  const vout = 3.3 * rF / (rL + rF);
  const adc = round(vout / 3.3 * 65535);
  const hide = hideCheckbox.checked();

  noStroke();
  fill('black');
  textAlign(CENTER, TOP);
  textSize(22);
  text('LDR Light Sensor Lab', canvasWidth / 2, 8);

  // 2 x 2 grid of panels: schematic | room, readouts | gauge
  const gx = 8;
  const gy = 40;
  const gw = (canvasWidth - 24) / 2;
  const gh1 = 200;
  const gh2 = drawHeight - gy - gh1 - 16;
  const narrow = canvasWidth < 600;
  const cells = [
    { x: gx, y: gy, w: gw, h: gh1 },
    { x: gx + gw + 8, y: gy, w: gw, h: gh1 },
    { x: gx, y: gy + gh1 + 8, w: narrow ? canvasWidth - 16 : gw, h: gh2 },
    { x: gx + gw + 8, y: gy + gh1 + 8, w: gw, h: gh2 }
  ];
  if (narrow) cells.pop();   // on narrow screens the readouts take the whole row
  for (const c of cells) {
    stroke('silver');
    fill('white');
    rect(c.x, c.y, c.w, c.h, 8);
  }

  drawSchematic(cells[0], rL, rF, vout, hide);
  drawRoom(cells[1], b);
  drawReadouts(cells[2], rL, rF, vout, adc, hide);
  if (!narrow) drawGauge(cells[3], adc, hide);

  // control labels
  noStroke();
  fill('black');
  textAlign(LEFT, CENTER);
  textSize(defaultTextSize);
  text('Brightness: ' + lightName(b), 10, drawHeight + 18);
  text('Fixed resistor: ' + ohmsText(rF), 10, drawHeight + 53);
}

function drawSchematic(c, rL, rF, vout, hide) {
  const x = c.x + min(70, c.w * 0.22);
  const top = c.y + 26;
  const bot = c.y + c.h - 22;
  const nodeY = (top + bot) / 2;
  const s = min(1, c.w / 330);

  stroke('black');
  strokeWeight(2);
  // 3.3 V rail
  line(x - 14, top, x + 14, top);
  line(x, top, x, top + 14);
  // LDR body (box) between top+14 and nodeY-14
  const ldrTop = top + 14;
  const ldrBot = nodeY - 12;
  line(x, ldrBot, x, nodeY);
  noFill();
  stroke('saddlebrown');
  rect(x - 9, ldrTop, 18, ldrBot - ldrTop, 3);
  // light arrows pointing at the LDR
  stroke('goldenrod');
  for (let k = 0; k < 2; k++) {
    const ay = ldrTop + 10 + k * 14;
    line(x - 34, ay - 10, x - 14, ay);
    line(x - 14, ay, x - 21, ay - 1);
    line(x - 14, ay, x - 18, ay - 6);
  }
  // node to fixed resistor
  stroke('black');
  const rTop = nodeY + 12;
  const rBot = bot - 14;
  line(x, nodeY, x, rTop);
  // fixed resistor zigzag
  noFill();
  stroke('black');
  beginShape();
  vertex(x, rTop);
  const zz = 6;
  for (let i = 1; i <= zz; i++) {
    const yy = rTop + (rBot - rTop) * (i - 0.5) / zz;
    vertex(x + (i % 2 ? 8 : -8), yy);
  }
  vertex(x, rBot);
  endShape();
  line(x, rBot, x, bot);
  // ground symbol
  line(x - 14, bot, x + 14, bot);
  line(x - 9, bot + 5, x + 9, bot + 5);
  line(x - 4, bot + 10, x + 4, bot + 10);
  // node dot and wire to the ADC pin
  noStroke();
  fill('black');
  circle(x, nodeY, 8);
  stroke('black');
  const pinX = c.x + c.w - 16;
  line(x, nodeY, pinX - 8, nodeY);
  fill('darkgreen');
  noStroke();
  triangle(pinX - 8, nodeY - 5, pinX - 8, nodeY + 5, pinX, nodeY);
  strokeWeight(1);

  // labels
  noStroke();
  fill('black');
  textSize(max(12, 15 * s + 1));
  textAlign(LEFT, CENTER);
  text('3.3 V', x + 18, top);
  fill('saddlebrown');
  text('LDR ' + ohmsText(rL), x + 16, (ldrTop + ldrBot) / 2);
  fill('black');
  text('Fixed ' + ohmsText(rF), x + 16, (rTop + rBot) / 2);
  text('GND', x + 18, bot + 4);
  fill('darkgreen');
  textAlign(RIGHT, BOTTOM);
  text('GP26 (ADC0)', pinX, nodeY - 4);
  textAlign(RIGHT, TOP);
  text(hide ? 'Vout = ?' : 'Vout = ' + vText(vout) + ' V', pinX, nodeY + 5);
}

function drawRoom(c, b) {
  const t = b / 100;
  // wall colour from night navy to warm daylight
  const night = color('midnightblue');
  const day = color('lightyellow');
  const wall = lerpColor(night, day, pow(t, 0.8));
  noStroke();
  fill(wall);
  rect(c.x + 1, c.y + 1, c.w - 2, c.h - 2, 8);
  // floor
  fill(lerpColor(color(40, 30, 30), color('burlywood'), t));
  rect(c.x + 1, c.y + c.h * 0.74, c.w - 2, c.h * 0.26 - 1, 0, 0, 8, 8);

  // window with sky
  const wx = c.x + c.w * 0.58;
  const wy = c.y + 30;
  const ww = c.w * 0.32;
  const wh = c.h * 0.36;
  stroke('saddlebrown');
  strokeWeight(3);
  fill(lerpColor(color('black'), color('skyblue'), constrain((t - 0.55) / 0.35, 0, 1)));
  rect(wx, wy, ww, wh);
  line(wx + ww / 2, wy, wx + ww / 2, wy + wh);
  line(wx, wy + wh / 2, wx + ww, wy + wh / 2);
  strokeWeight(1);
  if (t > 0.85) {
    noStroke();
    fill('gold');
    circle(wx + ww * 0.72, wy + wh * 0.3, wh * 0.36);
    // sunbeam on the floor
    fill(255, 240, 150, 120);
    quad(wx, wy + wh, wx + ww, wy + wh, wx + ww * 0.6, c.y + c.h - 4, wx - ww * 0.6, c.y + c.h - 4);
  }

  // lamp
  const lx = c.x + c.w * 0.22;
  const ly = c.y + c.h * 0.74;
  stroke('dimgray');
  strokeWeight(3);
  line(lx, ly, lx, ly - c.h * 0.36);
  line(lx - 14, ly, lx + 14, ly);
  strokeWeight(1);
  const lampOn = t >= 0.35;
  if (lampOn) {
    noStroke();
    for (let r = 5; r > 0; r--) {
      fill(255, 230, 120, 25 * t);
      circle(lx, ly - c.h * 0.4, r * 22 * (0.6 + t));
    }
  }
  fill(lampOn ? 'khaki' : 'gray');
  stroke('dimgray');
  quad(lx - 18, ly - c.h * 0.33, lx + 18, ly - c.h * 0.33, lx + 10, ly - c.h * 0.47, lx - 10, ly - c.h * 0.47);

  // sensor on the wall
  noStroke();
  fill('saddlebrown');
  circle(c.x + c.w * 0.45, c.y + c.h * 0.55, 12);
  fill(t > 0.45 ? 'black' : 'white');
  textSize(13);
  textAlign(CENTER, TOP);
  text('LDR', c.x + c.w * 0.45, c.y + c.h * 0.55 + 9);

  // caption
  fill(t > 0.45 ? 'black' : 'white');
  textSize(16);
  textAlign(LEFT, TOP);
  text(lightName(b), c.x + 10, c.y + 8);
}

function drawReadouts(c, rL, rF, vout, adc, hide) {
  const s = min(1, c.w / 380);
  noStroke();
  fill('black');
  textAlign(LEFT, TOP);
  let y = c.y + 10;
  const x = c.x + 10;
  const kL = nf(rL / 1000, 1, rL >= 100000 ? 0 : 1);
  const kF = nf(rF / 1000, 1, 1);
  textSize(max(14, 16 * s));
  text('R_LDR = ' + ohmsText(rL), x, y);
  y += 26;
  text('Vout = 3.3 × R_fixed / (R_LDR + R_fixed)', x, y);
  y += 24;
  fill('darkblue');
  text('     = 3.3 × ' + kF + ' / (' + kL + ' + ' + kF + ')', x, y);
  y += 24;
  text(hide ? '     = ? V' : '     = ' + vText(vout) + ' V', x, y);
  y += 30;
  fill('black');
  text(hide ? 'ADC = Vout / 3.3 × 65535 = ?' : 'ADC = ' + vText(vout) + ' / 3.3 × 65535 = ' + adc.toLocaleString('en-US'), x, y);
  y += 26;
  fill('dimgray');
  textSize(max(12, 14 * s));
  text('(values in kΩ; brighter light means a smaller R_LDR)', x, y);
}

function drawGauge(c, adc, hide) {
  const cx = c.x + c.w / 2;
  const r = min(c.w * 0.38, c.h - 50);
  const cy = c.y + r + 22;
  // dial arc segments
  noFill();
  strokeWeight(14);
  strokeCap(SQUARE);
  const segs = [['midnightblue', 0, 0.25], ['steelblue', 0.25, 0.5], ['gold', 0.5, 0.75], ['orange', 0.75, 1]];
  for (const sg of segs) {
    stroke(sg[0]);
    arc(cx, cy, r * 2, r * 2, PI + PI * sg[1], PI + PI * sg[2]);
  }
  strokeCap(ROUND);
  strokeWeight(1);
  // ticks
  noStroke();
  fill('black');
  textSize(12);
  textAlign(CENTER, CENTER);
  const ticks = [0, 16384, 32768, 49152, 65535];
  for (const tv of ticks) {
    const a = PI + PI * tv / 65535;
    text(tv === 65535 ? '65535' : (tv === 0 ? '0' : (tv / 1024) + 'k'), cx + cos(a) * (r + 18), cy + sin(a) * (r + 14));
  }
  // needle
  if (!hide) {
    const a = PI + PI * adc / 65535;
    stroke('crimson');
    strokeWeight(3);
    line(cx, cy, cx + cos(a) * (r - 12), cy + sin(a) * (r - 12));
    strokeWeight(1);
  }
  noStroke();
  fill('black');
  circle(cx, cy, 10);
  textSize(16);
  textAlign(CENTER, TOP);
  text(hide ? 'ADC reading: ?' : 'ADC reading: ' + adc.toLocaleString('en-US'), cx, cy + 8);
}

function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
  lightSlider.size(canvasWidth - sliderLeftMargin - margin);
  fixedSlider.size(canvasWidth - sliderLeftMargin - margin);
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) {
    canvasWidth = Math.floor(container.getBoundingClientRect().width);
  }
}
