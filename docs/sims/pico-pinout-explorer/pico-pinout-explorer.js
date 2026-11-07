// Pico Pinout Explorer MicroSim
// CANVAS_HEIGHT: 540
// A top-down drawing of the Raspberry Pi Pico with all 40 pins. Hover a pin to
// see its GP number, physical number and special functions; click it to see
// the MicroPython line that configures it. A filter highlights I2C, SPI, UART,
// ADC or PWM pins, and quiz mode asks the student to find a GP number.

let canvasWidth = 400;
let drawHeight = 495;
let controlHeight = 45;
let canvasHeight = drawHeight + controlHeight;
let margin = 10;
let defaultTextSize = 16;

// Physical pins 1-20 run down the left side (USB at the top);
// pins 21-40 run up the right side, so pin 40 is top right.
const LEFT_PINS = ['GP0', 'GP1', 'GND', 'GP2', 'GP3', 'GP4', 'GP5', 'GND', 'GP6', 'GP7',
  'GP8', 'GP9', 'GND', 'GP10', 'GP11', 'GP12', 'GP13', 'GND', 'GP14', 'GP15'];
const RIGHT_PINS = ['GP16', 'GP17', 'GND', 'GP18', 'GP19', 'GP20', 'GP21', 'GND', 'GP22', 'RUN',
  'GP26', 'GP27', 'AGND', 'GP28', 'ADC_VREF', '3V3(OUT)', '3V3_EN', 'GND', 'VSYS', 'VBUS'];

const NOTES = {
  'GND': 'Ground (0 V). Every circuit needs a path back to ground.',
  'AGND': 'Analog ground, a quiet ground for the ADC pins.',
  'VBUS': '5 V straight from the USB cable. Only live when USB is plugged in.',
  'VSYS': 'Main power input, 1.8 to 5.5 V. A battery pack connects here.',
  '3V3(OUT)': '3.3 V output for sensors and displays. Keep the total under 300 mA.',
  '3V3_EN': 'Connect to ground to switch off the 3.3 V regulator.',
  'ADC_VREF': 'Reference voltage for the ADC, normally 3.3 V.',
  'RUN': 'Connect to ground to reset the Pico. A reset button goes here.'
};

const COLORS = {
  gpio: 'royalblue', power: 'crimson', ground: 'black', adc: 'forestgreen', control: 'gray'
};

let pins = [];          // {phys, label, kind, gp, funcs, side, row}
let hoverPin = null;
let selectedPin = null;
let filterSelect, quizCheckbox, newQuestionButton;
let quizTarget = null;
let quizMessage = '';
let quizColor = 'black';
let quizRight = 0, quizTotal = 0;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  buildPins();

  filterSelect = createSelect();
  for (const f of ['Show all', 'I2C', 'SPI', 'UART', 'ADC', 'PWM']) filterSelect.option(f);
  filterSelect.position(10, drawHeight + 10);

  quizCheckbox = createCheckbox(' Quiz mode', false);
  quizCheckbox.position(110, drawHeight + 12);
  quizCheckbox.changed(() => {
    quizRight = 0; quizTotal = 0;
    if (quizCheckbox.checked()) newQuestion(); else quizTarget = null;
  });

  newQuestionButton = createButton('New question');
  newQuestionButton.position(225, drawHeight + 10);
  newQuestionButton.mousePressed(() => { if (quizCheckbox.checked()) newQuestion(); });

  describe('A drawing of the Raspberry Pi Pico board with its 40 pins. Each pin is labeled with its ' +
    'name, such as GP15 or GND, and colored by type: blue GPIO, red power, black ground, green ADC. ' +
    'Hovering or clicking a pin shows its physical pin number, special functions and a MicroPython line.',
    LABEL);
}

// ---------- pin data ----------
function buildPins() {
  pins = [];
  for (let i = 0; i < 20; i++) pins.push(makePin(i + 1, LEFT_PINS[i], 'left', i));
  for (let i = 0; i < 20; i++) pins.push(makePin(21 + i, RIGHT_PINS[i], 'right', 19 - i));
}

function makePin(phys, label, side, row) {
  const p = { phys, label, side, row, gp: null, funcs: [] };
  if (label.startsWith('GP')) {
    const n = int(label.slice(2));
    p.gp = n;
    p.kind = (n >= 26) ? 'adc' : 'gpio';
    p.funcs = gpioFunctions(n);
  } else if (label === 'GND' || label === 'AGND') {
    p.kind = 'ground';
  } else if (['VBUS', 'VSYS', '3V3(OUT)', 'ADC_VREF'].includes(label)) {
    p.kind = 'power';
  } else {
    p.kind = 'control';
  }
  return p;
}

// Special functions follow the RP2040 function table, which repeats in groups of 4 pins
function gpioFunctions(n) {
  const f = [];
  f.push((n % 4 < 2 ? 'I2C0' : 'I2C1') + (n % 2 === 0 ? ' SDA' : ' SCL'));
  const spiBank = ((n >= 8 && n <= 15) || n >= 24) ? 'SPI1' : 'SPI0';
  f.push(spiBank + ' ' + ['RX', 'CSn', 'SCK', 'TX'][n % 4]);
  const uartBank = (n <= 3 || (n >= 12 && n <= 19) || n >= 28) ? 'UART0' : 'UART1';
  if (n % 4 < 2) f.push(uartBank + ' ' + (n % 4 === 0 ? 'TX' : 'RX'));
  f.push('PWM' + (floor(n / 2) % 8) + ' ' + (n % 2 === 0 ? 'A' : 'B'));
  if (n >= 26) f.push('ADC' + (n - 26));
  return f;
}

function matchesFilter(p) {
  const f = filterSelect.value();
  if (f === 'Show all') return true;
  return p.funcs.some(fn => fn.startsWith(f));
}

// The MicroPython line that sets up this pin for the current filter
function codeFor(p) {
  if (p.gp === null) return ['# ' + p.label + ' is not programmable:', '# it supplies power, ground or control.'];
  const n = p.gp;
  const f = filterSelect.value();
  if (f === 'I2C') {
    const bank = n % 4 < 2 ? 0 : 1;
    const sda = n % 2 === 0 ? n : n - 1;
    return ['from machine import Pin, I2C', 'i2c = I2C(' + bank + ', sda=Pin(' + sda + '), scl=Pin(' + (sda + 1) + '))'];
  }
  if (f === 'SPI') {
    const base = n - (n % 4);
    const bank = ((n >= 8 && n <= 15) || n >= 24) ? 1 : 0;
    const exposed = [base, base + 2, base + 3].every(g => pins.some(q => q.gp === g));
    if (!exposed) return ['# GP' + (base + 3) + ' is not on the header,', '# so use a different SPI group of 4 pins.'];
    return ['from machine import Pin, SPI', 'spi = SPI(' + bank + ', sck=Pin(' + (base + 2) + '), mosi=Pin(' +
      (base + 3) + '), miso=Pin(' + base + '))'];
  }
  if (f === 'UART') {
    if (n % 4 > 1) return ['# GP' + n + ' is a UART CTS/RTS pin.', '# Use GP' + (n - 2) + ' and GP' + (n - 1) + ' for TX and RX.'];
    const base = n - (n % 4);
    const bank = (n <= 3 || (n >= 12 && n <= 19) || n >= 28) ? 0 : 1;
    return ['from machine import Pin, UART', 'uart = UART(' + bank + ', 9600, tx=Pin(' + base + '), rx=Pin(' + (base + 1) + '))'];
  }
  if (f === 'ADC') {
    if (n < 26) return ['# GP' + n + ' cannot read analog voltages.', '# Only GP26, GP27 and GP28 have the ADC.'];
    return ['from machine import ADC', 'pot = ADC(' + n + ')    # read with pot.read_u16()'];
  }
  if (f === 'PWM') {
    return ['from machine import Pin, PWM', 'pwm = PWM(Pin(' + n + '))  # then pwm.freq(1000)'];
  }
  return ['led = Pin(' + n + ', Pin.OUT)', 'button = Pin(' + n + ', Pin.IN, Pin.PULL_UP)'];
}

function newQuestion() {
  const gpioPins = pins.filter(p => p.gp !== null && p !== quizTarget);
  quizTarget = random(gpioPins);
  quizMessage = 'Click the pin labeled GP' + quizTarget.gp + '.';
  quizColor = 'darkblue';
  selectedPin = null;
}

// ---------- layout ----------
function layout() {
  const narrow = canvasWidth < 600;
  const pitch = narrow ? 14.5 : 17;
  const bw = narrow ? 96 : 120;
  const bx = narrow ? canvasWidth / 2 - bw / 2 : margin + 92;
  const by = 58;
  const pinTop = by + 22;
  const bh = 19 * pitch + 44;
  return { narrow, pitch, bw, bx, by, bh, pinTop };
}

function pinPos(p, L) {
  const y = L.pinTop + p.row * L.pitch;
  const x = p.side === 'left' ? L.bx + 9 : L.bx + L.bw - 9;
  return { x, y };
}

function pinAt(mx, my) {
  const L = layout();
  for (const p of pins) {
    const pos = pinPos(p, L);
    // the pad and its outside label both count as the pin
    const x0 = p.side === 'left' ? L.bx - 84 : pos.x - 8;
    const x1 = p.side === 'left' ? pos.x + 8 : L.bx + L.bw + 84;
    if (mx >= x0 && mx <= x1 && abs(my - pos.y) <= L.pitch / 2) return p;
  }
  return null;
}

// ---------- drawing ----------
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
  text('Pico Pinout Explorer', canvasWidth / 2, 6);
  drawLegend();

  const L = layout();
  hoverPin = (mouseY >= 0 && mouseY < drawHeight) ? pinAt(mouseX, mouseY) : null;
  cursor(hoverPin ? HAND : ARROW);
  drawBoard(L);
  drawInfoPanel(L);

  if (quizCheckbox.checked() && quizTotal > 0) {
    noStroke();
    fill('black');
    textSize(16);
    textAlign(LEFT, CENTER);
    text(quizRight + ' / ' + quizTotal, 340, drawHeight + 22);
  }
}

function drawLegend() {
  const items = [['GPIO', 'gpio'], ['Power', 'power'], ['Ground', 'ground'], ['ADC', 'adc'], ['Control', 'control']];
  textSize(13);
  let total = 0;
  for (const it of items) total += 18 + textWidth(it[0]) + 12;
  let x = canvasWidth / 2 - total / 2;
  for (const it of items) {
    noStroke();
    fill(COLORS[it[1]]);
    rect(x, 33, 13, 13, 3);
    fill('black');
    textAlign(LEFT, CENTER);
    text(it[0], x + 17, 40);
    x += 18 + textWidth(it[0]) + 12;
  }
}

function drawBoard(L) {
  // green board
  stroke('darkgreen');
  strokeWeight(2);
  fill('seagreen');
  rect(L.bx, L.by, L.bw, L.bh, 6);
  // USB connector at the top
  noStroke();
  fill('silver');
  rect(L.bx + L.bw / 2 - 16, L.by - 8, 32, 18, 3);
  fill('white');
  textSize(10);
  textAlign(CENTER, CENTER);
  text('USB', L.bx + L.bw / 2, L.by + 1);
  // RP2040 chip and BOOTSEL button
  fill(40);
  const chip = L.bw * 0.42;
  rect(L.bx + L.bw / 2 - chip / 2, L.by + L.bh * 0.45, chip, chip, 3);
  fill('whitesmoke');
  circle(L.bx + L.bw / 2, L.by + L.bh * 0.22, 14);
  if (!L.narrow) {   // chip and button names only fit on the larger drawing
    fill('white');
    textSize(10);
    text('RP2040', L.bx + L.bw / 2, L.by + L.bh * 0.45 + chip / 2);
    text('BOOTSEL', L.bx + L.bw / 2, L.by + L.bh * 0.22 + 15);
  }

  const quiz = quizCheckbox.checked();
  for (const p of pins) {
    const pos = pinPos(p, L);
    const dim = !matchesFilter(p);
    const isHover = hoverPin === p;
    const isSel = selectedPin === p;
    const c = color(COLORS[p.kind]);
    if (dim) c.setAlpha(50);
    // pad
    stroke(isHover || isSel ? 'gold' : 'goldenrod');
    strokeWeight(isHover || isSel ? 3 : 1);
    fill(isHover || isSel ? 'gold' : 'khaki');
    circle(pos.x, pos.y, L.pitch - 4);
    // physical pin number just inside the board
    noStroke();
    fill('white');
    textSize(L.narrow ? 10 : 12);
    textAlign(p.side === 'left' ? LEFT : RIGHT, CENTER);
    text(p.phys, p.side === 'left' ? pos.x + 9 : pos.x - 9, pos.y);
    // name label outside the board
    const lw = 74, lh = L.pitch - 3;
    const lx = p.side === 'left' ? L.bx - 6 - lw : L.bx + L.bw + 6;
    stroke(isHover || isSel ? 'gold' : 'white');
    strokeWeight(isHover || isSel ? 2 : 1);
    fill(c);
    rect(lx, pos.y - lh / 2, lw, lh, 3);
    noStroke();
    const label = (quiz && p.gp !== null) ? '?' : p.label;
    const tc = color('white');
    if (dim) tc.setAlpha(120);
    fill(tc);
    textSize(L.narrow ? 11 : 13);
    textAlign(CENTER, CENTER);
    text(label, lx + lw / 2, pos.y + 1);
  }
}

function drawInfoPanel(L) {
  let px, py, pw, ph;
  if (L.narrow) {
    px = margin; py = L.by + L.bh + 8; pw = canvasWidth - 2 * margin; ph = drawHeight - py - 6;
  } else {
    px = L.bx + L.bw + 92; py = L.by; pw = canvasWidth - px - margin; ph = drawHeight - py - 10;
  }
  stroke('silver');
  strokeWeight(1);
  fill('white');
  rect(px, py, pw, ph, 8);
  noStroke();
  textAlign(LEFT, TOP);
  const tx = px + 10, tw = pw - 20;
  let y = py + 8;
  const big = L.narrow ? 16 : 18;
  const body = L.narrow ? 14 : 16;
  const lineGap = L.narrow ? 18 : 22;

  if (quizCheckbox.checked()) {
    fill(quizColor);
    textSize(big);
    textStyle(BOLD);
    text(quizMessage, tx, y, tw);
    textStyle(NORMAL);
    y += lineGap * 2;
    fill('dimgray');
    textSize(body);
    text('GP labels are hidden. Use what you know: GP numbers count up the left side ' +
      'and skip the ground pins.', tx, y, tw);
    return;
  }

  const p = hoverPin || selectedPin;
  if (!p) {
    fill('black');
    textSize(big);
    textStyle(BOLD);
    text('Hover over a pin', tx, y, tw);
    textStyle(NORMAL);
    y += lineGap + 4;
    textSize(body);
    text('See its GP number, physical pin number and special functions. Click a pin to see ' +
      'the MicroPython code that sets it up. Code uses the GP number, never the physical number.', tx, y, tw);
    return;
  }
  fill(COLORS[p.kind]);
  textSize(big);
  textStyle(BOLD);
  const title = p.gp !== null ? 'GP' + p.gp + '  (physical pin ' + p.phys + ')' : p.label + '  (physical pin ' + p.phys + ')';
  text(title, tx, y, tw);
  textStyle(NORMAL);
  y += lineGap + 2;
  fill('black');
  textSize(body);
  if (p.gp !== null) {
    text('Functions: ' + p.funcs.join(', '), tx, y, tw);
    y += lineGap * (L.narrow || textWidth('Functions: ' + p.funcs.join(', ')) > tw ? 2 : 1) + 4;
  } else {
    text(NOTES[p.label], tx, y, tw);
    y += lineGap * (textWidth(NOTES[p.label]) > tw ? 2 : 1) + 4;
  }
  // code is shown for the clicked pin (or the hovered one on wide screens)
  if (selectedPin === p || !L.narrow) {
    textFont('monospace');
    textSize(L.narrow ? 12 : 14);
    fill(selectedPin === p ? 'darkgreen' : 'gray');
    for (const line of codeFor(p)) {
      text(line, tx, y, tw);
      y += textWidth(line) > tw ? lineGap * 2 : lineGap;
    }
    textFont('sans-serif');
    if (selectedPin !== p) {
      textSize(14);
      fill('gray');
      text('(click the pin to pin this code)', tx, y, tw);
    }
  }
  if (!L.narrow) {
    fill('dimgray');
    textSize(14);
    text('The onboard LED is GP25 (Pin("LED") on a Pico W). It is not on a header pin.',
      tx, py + ph - 48, tw);
  }
}

function mousePressed() {
  if (mouseY < 0 || mouseY > drawHeight || mouseX < 0 || mouseX > canvasWidth) return;
  const p = pinAt(mouseX, mouseY);
  if (!p) return;
  if (quizCheckbox.checked() && quizTarget) {
    quizTotal++;
    if (p === quizTarget) {
      quizRight++;
      quizMessage = 'Correct! GP' + p.gp + ' is physical pin ' + p.phys + '. Press New question.';
      quizColor = 'darkgreen';
      selectedPin = p;
    } else {
      quizMessage = 'That is ' + (p.gp !== null ? 'GP' + p.gp : p.label) + ' (pin ' + p.phys +
        '). Find GP' + quizTarget.gp + '.';
      quizColor = 'firebrick';
    }
    return;
  }
  selectedPin = p;
}

// ---------- responsive ----------
function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) canvasWidth = container.offsetWidth;
}
