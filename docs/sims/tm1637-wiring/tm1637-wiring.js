// TM1637 Wiring Diagram
// CANVAS_HEIGHT: 555
// Students connect the four TM1637 module pins to the correct Raspberry Pi Pico pins.
// Drag a wire from a module pin to a Pico pin, or tap a module pin and then tap a Pico pin.

let canvasWidth = 700;
let drawHeight = 505;
let controlHeight = 50;
let canvasHeight = drawHeight + controlHeight;
let margin = 20;
let defaultTextSize = 16;

// Physical pin names of the Raspberry Pi Pico (pin 1 top-left, pin 40 top-right)
const picoPins = {
  1: 'GP0', 2: 'GP1', 3: 'GND', 4: 'GP2', 5: 'GP3', 6: 'GP4', 7: 'GP5', 8: 'GND', 9: 'GP6', 10: 'GP7',
  11: 'GP8', 12: 'GP9', 13: 'GND', 14: 'GP10', 15: 'GP11', 16: 'GP12', 17: 'GP13', 18: 'GND', 19: 'GP14', 20: 'GP15',
  21: 'GP16', 22: 'GP17', 23: 'GND', 24: 'GP18', 25: 'GP19', 26: 'GP20', 27: 'GP21', 28: 'GND', 29: 'GP22', 30: 'RUN',
  31: 'GP26', 32: 'GP27', 33: 'GND', 34: 'GP28', 35: 'ADC_VREF', 36: '3V3(OUT)', 37: '3V3_EN', 38: 'GND', 39: 'VSYS', 40: 'VBUS'
};

// The wiring table from the chapter
const modulePins = [
  { name: 'CLK', target: 4, color: 'gold', table: 'GP2 (pin 4), yellow wire' },
  { name: 'DIO', target: 5, color: 'limegreen', table: 'GP3 (pin 5), green wire' },
  { name: 'VCC', target: 36, color: 'red', table: '3V3(OUT) (pin 36), red wire' },
  { name: 'GND', target: 38, color: 'black', table: 'GND (pin 38), black wire' }
];

let connections = {};   // module pin name -> Pico physical pin number
let dragging = null;    // module pin name being dragged or armed by a tap
let dragMoved = false;
let message = 'Drag a wire from each module pin to the Pico pin in the wiring table.';
let messageColor = 'black';
let answerShown = false;

let answerButton, resetButton;

// virtual layout (scaled to fit narrow screens)
let vw = 700, s = 1;
let picoX, boardW = 112, pinY0 = 72, pinStep = 21;
let modX, modY = 170, modW = 220, modH = 130;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  answerButton = createButton('Show answer');
  answerButton.position(10, drawHeight + 12);
  answerButton.mousePressed(showAnswer);
  resetButton = createButton('Reset');
  resetButton.position(120, drawHeight + 12);
  resetButton.mousePressed(resetWires);

  describe('A Raspberry Pi Pico with all 40 pins labeled on the left and a TM1637 four-digit display ' +
    'module on the right. Students connect CLK, DIO, VCC and GND to the correct Pico pins. ' +
    'When all four are correct the display shows 12:34.', LABEL);
}

function draw() {
  updateCanvasSize();
  vw = max(canvasWidth, 640);
  s = canvasWidth / vw;
  picoX = 108;
  modX = vw - margin - modW;

  stroke('silver');
  strokeWeight(1);
  fill('aliceblue');
  rect(0, 0, canvasWidth, drawHeight);
  fill('white');
  rect(0, drawHeight, canvasWidth, controlHeight);

  push();
  scale(s);
  noStroke();
  fill('black');
  textAlign(CENTER, TOP);
  textSize(24);
  text('TM1637 Wiring', vw / 2 + 60, 10);

  drawPico();
  drawModule();
  drawWires();
  drawPicoPins();
  drawMessage();
  pop();

  // control-area status
  noStroke();
  fill('black');
  textSize(16);
  textAlign(LEFT, CENTER);
  let n = countCorrect();
  text('Correct wires: ' + n + ' of 4', 190, drawHeight + 24);
}

// ---------- Pico ----------
function pinPos(num) {
  if (num <= 20) return { x: picoX + 12, y: pinY0 + (num - 1) * pinStep, side: 'L' };
  return { x: picoX + boardW - 12, y: pinY0 + (40 - num) * pinStep, side: 'R' };
}

function pinColor(name) {
  if (name === 'GND') return 'black';
  if (name.startsWith('3V3') || name === 'VSYS' || name === 'VBUS') return 'red';
  if (name.startsWith('GP')) return 'seagreen';
  return 'gray';
}

function drawPico() {
  let top = pinY0 - 22, bottom = pinY0 + 19 * pinStep + 18;
  // USB connector
  stroke('dimgray');
  fill('silver');
  rect(picoX + boardW / 2 - 18, top - 10, 36, 16, 3);
  // board
  stroke('darkgreen');
  fill('forestgreen');
  rect(picoX, top, boardW, bottom - top, 6);
  // RP2040 chip
  noStroke();
  fill('black');
  rect(picoX + boardW / 2 - 22, pinY0 + 8 * pinStep, 44, 44, 3);
  fill('white');
  textAlign(CENTER, CENTER);
  textSize(10);
  text('RP2040', picoX + boardW / 2, pinY0 + 8 * pinStep + 22);
  textSize(14);
  text('Pico', picoX + boardW / 2, pinY0 + 3 * pinStep);
}

// pins and labels are drawn after the wires so the labels stay readable
function drawPicoPins() {
  let hoverPin = dragging ? pinUnderMouse() : null;
  for (let num = 1; num <= 40; num++) {
    let p = pinPos(num);
    let name = picoPins[num];
    let used = Object.values(connections).includes(num);
    stroke(num === hoverPin ? 'orange' : 'goldenrod');
    strokeWeight(num === hoverPin ? 3 : 1.5);
    fill(used ? 'gold' : 'white');
    circle(p.x, p.y, 11);
    strokeWeight(1);
    noStroke();
    textSize(12);
    let lbl = p.side === 'L' ? name + '  ' + num : num + '  ' + name;
    let tw = textWidth(lbl);
    let lx = p.side === 'L' ? picoX - 4 - tw : picoX + boardW + 4;
    fill(240, 248, 255, 215);
    rect(lx - 2, p.y - 8, tw + 4, 16, 3);
    fill(pinColor(name));
    textAlign(LEFT, CENTER);
    text(lbl, lx, p.y);
  }
}

// ---------- TM1637 module ----------
function modPinPos(i) {
  return { x: modX + 16, y: modY + 30 + i * 26 };
}

function drawModule() {
  stroke('navy');
  fill('royalblue');
  rect(modX, modY, modW, modH, 6);
  noStroke();
  fill('white');
  textAlign(LEFT, TOP);
  textSize(13);
  text('TM1637 module', modX + 52, modY + 6);

  // pins with highlight rings
  let glow = !allCorrect();
  for (let i = 0; i < 4; i++) {
    let p = modPinPos(i);
    let mp = modulePins[i];
    if (glow && !isCorrect(mp.name)) {
      noStroke();
      fill(255, 215, 0, 120);
      circle(p.x, p.y, 24);
    }
    stroke(dragging === mp.name ? 'orange' : 'black');
    strokeWeight(dragging === mp.name ? 3 : 1);
    fill('silver');
    circle(p.x, p.y, 13);
    strokeWeight(1);
    noStroke();
    fill('white');
    textAlign(LEFT, CENTER);
    textSize(14);
    text(mp.name, p.x + 12, p.y);
  }

  // four-digit display
  let dx = modX + 72, dy = modY + 30, dw = modW - 84, dh = 84;
  fill('black');
  rect(dx, dy, dw, dh, 4);
  let on = allCorrect();
  let digits = [1, 2, 3, 4];
  let cw = dw / 4;
  for (let i = 0; i < 4; i++) {
    drawDigit(dx + i * cw + cw * 0.18, dy + 12, cw * 0.62, dh - 24, on ? digits[i] : 8, on);
  }
  // colon flashes once per second when the display is working
  let colonOn = on && (floor(millis() / 500) % 2 === 0);
  fill(colonOn ? 'red' : color(60, 0, 0));
  circle(dx + dw / 2, dy + dh * 0.38, 6);
  circle(dx + dw / 2, dy + dh * 0.62, 6);
}

// segment patterns a..g
const segMap = {
  0: 'abcdef', 1: 'bc', 2: 'abdeg', 3: 'abcdg', 4: 'bcfg', 5: 'acdfg', 6: 'acdefg', 7: 'abc', 8: 'abcdefg', 9: 'abcdfg'
};

function drawDigit(x, y, w, h, d, lit) {
  let t = max(3, w * 0.16);
  let segs = {
    a: [x + t, y, w - 2 * t, t], d: [x + t, y + h - t, w - 2 * t, t], g: [x + t, y + h / 2 - t / 2, w - 2 * t, t],
    f: [x, y + t, t, h / 2 - t], b: [x + w - t, y + t, t, h / 2 - t],
    e: [x, y + h / 2, t, h / 2 - t], c: [x + w - t, y + h / 2, t, h / 2 - t]
  };
  for (let k of 'abcdefg') {
    let litSeg = lit && segMap[d].includes(k);
    fill(litSeg ? 'red' : color(60, 0, 0));
    rect(...segs[k], 2);
  }
}

// ---------- wires ----------
function wirePath(a, b) {
  // cubic curve from module pin a to Pico pin b, bowing outward from the pin side
  let side = b.x < picoX + boardW / 2 ? -1 : 1;
  let c1 = { x: a.x - 90, y: a.y };
  let c2 = { x: b.x + side * 60, y: b.y };
  if (side < 0) c2 = { x: b.x - 70, y: b.y - 10 };
  let pts = [];
  for (let i = 0; i <= 30; i++) {
    let t = i / 30, u = 1 - t;
    pts.push({
      x: u * u * u * a.x + 3 * u * u * t * c1.x + 3 * u * t * t * c2.x + t * t * t * b.x,
      y: u * u * u * a.y + 3 * u * u * t * c1.y + 3 * u * t * t * c2.y + t * t * t * b.y
    });
  }
  return pts;
}

function drawWirePts(pts, col, w) {
  noFill();
  stroke('dimgray');
  strokeWeight(w + 2);
  beginShape();
  for (let p of pts) vertex(p.x, p.y);
  endShape();
  stroke(col);
  strokeWeight(w);
  beginShape();
  for (let p of pts) vertex(p.x, p.y);
  endShape();
  strokeWeight(1);
}

function drawWires() {
  for (let i = 0; i < 4; i++) {
    let mp = modulePins[i];
    if (connections[mp.name]) {
      drawWirePts(wirePath(modPinPos(i), pinPos(connections[mp.name])), mp.color, 4);
    }
  }
  if (dragging && dragMoved) {
    let i = modulePins.findIndex(m => m.name === dragging);
    let a = modPinPos(i);
    stroke('orange');
    strokeWeight(3);
    line(a.x, a.y, mouseX / s, mouseY / s);
    strokeWeight(1);
  }
}

// ---------- message / table panel ----------
function drawMessage() {
  let x = modX - 40, y = modY + modH + 24, w = modW + 40;
  stroke('lightgray');
  fill(255, 255, 255, 230);
  rect(x, y, w, 172, 10);
  noStroke();
  fill('black');
  textAlign(LEFT, TOP);
  textSize(14);
  textStyle(BOLD);
  text('Wiring table', x + 10, y + 8);
  textStyle(NORMAL);
  textSize(13);
  for (let i = 0; i < 4; i++) {
    let mp = modulePins[i];
    fill(isCorrect(mp.name) ? 'darkgreen' : 'black');
    text((isCorrect(mp.name) ? '✓ ' : '• ') + mp.name + ' → ' + mp.table, x + 10, y + 30 + i * 18);
  }
  fill(messageColor);
  textSize(14);
  text(message, x + 10, y + 106, w - 20, 64);
}

// ---------- interaction ----------
function modPinUnderMouse() {
  let mx = mouseX / s, my = mouseY / s;
  for (let i = 0; i < 4; i++) {
    let p = modPinPos(i);
    if (dist(mx, my, p.x, p.y) < 14) return modulePins[i].name;
  }
  return null;
}

function pinUnderMouse() {
  let mx = mouseX / s, my = mouseY / s;
  for (let num = 1; num <= 40; num++) {
    let p = pinPos(num);
    if (dist(mx, my, p.x, p.y) < 10) return num;
  }
  return null;
}

function mousePressed() {
  if (mouseY > drawHeight || mouseY < 0) return;
  let m = modPinUnderMouse();
  if (m) {
    if (isCorrect(m)) {
      message = m + ' is already connected correctly.';
      messageColor = 'darkgreen';
      return;
    }
    dragging = m;
    dragMoved = false;
    message = 'Now drop (or tap) the ' + m + ' wire on a Pico pin.';
    messageColor = 'black';
    return;
  }
  // tap-tap mode: a module pin is armed, now a Pico pin is tapped
  let p = pinUnderMouse();
  if (dragging && p) {
    tryConnect(dragging, p);
    dragging = null;
  }
}

function mouseDragged() {
  if (dragging) dragMoved = true;
}

function mouseReleased() {
  if (!dragging || !dragMoved) return;
  let p = pinUnderMouse();
  if (p) tryConnect(dragging, p);
  else {
    message = 'Release the wire on one of the round Pico pins.';
    messageColor = 'black';
  }
  dragging = null;
  dragMoved = false;
}

function tryConnect(name, num) {
  let mp = modulePins.find(m => m.name === name);
  let pinName = picoPins[num];
  let usedBy = Object.keys(connections).find(k => connections[k] === num);
  if (usedBy) {
    message = 'Pin ' + num + ' already has the ' + usedBy + ' wire.';
    messageColor = 'firebrick';
    return;
  }
  let ok = num === mp.target || (name === 'GND' && pinName === 'GND');
  if (ok) {
    connections[name] = num;
    message = name + ' → ' + pinName + ' (pin ' + num + '). Correct!' +
      (name === 'GND' && num !== 38 ? ' Any GND pin works; the table uses pin 38.' : '');
    messageColor = 'darkgreen';
    if (allCorrect()) {
      message = 'All four wires are correct. The display shows 12:34 with a flashing colon.';
    }
  } else {
    message = hintFor(name, num, pinName);
    messageColor = 'firebrick';
  }
}

function hintFor(name, num, pinName) {
  let isPower = pinName.startsWith('3V3') || pinName === 'VSYS' || pinName === 'VBUS' || pinName === 'ADC_VREF';
  if (name === 'VCC') {
    if (pinName === 'GND') return 'VCC needs 3.3 V, not GND.';
    if (pinName === 'VBUS' || pinName === 'VSYS') return pinName + ' carries about 5 V. Use 3V3(OUT), pin 36, so signals stay at 3.3 V.';
    if (pinName === '3V3_EN') return '3V3_EN switches the regulator on and off. It is not a power output. Use pin 36.';
    if (pinName === 'ADC_VREF') return 'ADC_VREF is a reference for the analog pins, not a supply. Use pin 36.';
    return 'VCC needs power (3.3 V), not a signal pin. Look for 3V3(OUT), pin 36.';
  }
  if (name === 'GND') return 'GND must go to a ground pin (black wire), such as pin 38.';
  let want = name === 'CLK' ? 'GP2 (pin 4)' : 'GP3 (pin 5)';
  if (pinName === 'GND') return name + ' is a signal. It needs a GPIO pin, not GND.';
  if (isPower) return 'Never connect a signal pin to power. ' + name + ' goes to ' + want + '.';
  if (name === 'CLK' && num === 5) return 'That is GP3, the DIO pin in the table. CLK goes to GP2 (pin 4).';
  if (name === 'DIO' && num === 4) return 'That is GP2, the CLK pin in the table. DIO goes to GP3 (pin 5).';
  if (pinName.startsWith('GP')) return pinName + ' works only if you change the code. The table uses ' + want + '.';
  return pinName + ' is not a GPIO pin. ' + name + ' goes to ' + want + '.';
}

function isCorrect(name) { return !!connections[name]; }
function countCorrect() { return modulePins.filter(m => isCorrect(m.name)).length; }
function allCorrect() { return countCorrect() === 4; }

function showAnswer() {
  for (let mp of modulePins) {
    // keep a correct GND wire where the student put it
    if (!connections[mp.name]) {
      let usedBy = Object.keys(connections).find(k => connections[k] === mp.target);
      if (usedBy) delete connections[usedBy];
      connections[mp.name] = mp.target;
    }
  }
  answerShown = true;
  message = 'Answer shown: red to 3V3(OUT), black to GND, yellow to GP2, green to GP3.';
  messageColor = 'black';
}

function resetWires() {
  connections = {};
  dragging = null;
  answerShown = false;
  message = 'Drag a wire from each module pin to the Pico pin in the wiring table.';
  messageColor = 'black';
}

function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) canvasWidth = max(360, container.offsetWidth);
}
