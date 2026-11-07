// Logic Analyzer Trace Reader MicroSim
// CANVAS_HEIGHT: 525
// Four captured logic analyzer traces: three I2C writes to an OLED at 0x3C (SCL and SDA) and
// one button on GP14. An annotation band decodes START, address, R/W, ACK or NACK, data and
// STOP. Click any part of the waveform to name it, then choose a diagnosis and press Check.
// Capture names stay hidden until the diagnosis is correct. Static: nothing animates.

let canvasWidth = 400;
let drawHeight = 410;
let controlHeight = 115;
let canvasHeight = drawHeight + controlHeight;
let margin = 25;
let sliderLeftMargin = 90;
let defaultTextSize = 16;

let captureSelect, diagSelect, checkButton, panSlider;
let captures = [];
let cur = 0;
let selected = -1;          // index of the clicked segment
let feedback = ['', '', '', ''];
let solved = [false, false, false, false];

// plot geometry (set every frame)
let plotX0 = 70, plotX1 = 380, unitPx = 2, viewStart = 0;

const DIAGNOSES = [
  ['Choose a diagnosis...', ''],
  ['Everything worked', 'good'],
  ['No ACK: wrong address or not connected', 'nack'],
  ['Slow edges: pull-ups missing or weak', 'slow'],
  ['Contact bounce on the input', 'bounce'],
  ['SDA and SCL wires swapped', 'swap']
];

const INFO = {
  START: 'START condition: SDA falls while SCL is still high. Every I2C message begins this way.',
  ADDR: 'Address: 7 bits, most significant bit first, each read while SCL is high. ',
  RW: 'Read/Write bit: 0 means the controller is going to write to the device.',
  ACK: 'ACK: on the ninth clock the controller lets go of SDA and the device pulls it low to say "got it".',
  NACK: 'NACK: on the ninth clock nobody pulled SDA low, so no device answered this address.',
  STOP: 'STOP condition: SDA rises while SCL is high. The bus is free again.'
};

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));

  buildCaptures();

  captureSelect = createSelect();
  for (let i = 0; i < captures.length; i++) captureSelect.option(captureLabel(i), String(i));
  captureSelect.position(sliderLeftMargin, drawHeight + 7);
  captureSelect.changed(() => {
    cur = int(captureSelect.value());
    selected = -1;
    panSlider.value(0);
    diagSelect.selected('');
  });

  diagSelect = createSelect();
  for (const d of DIAGNOSES) diagSelect.option(d[0], d[1]);
  diagSelect.position(sliderLeftMargin, drawHeight + 42);

  checkButton = createButton('Check');
  checkButton.mousePressed(checkDiagnosis);

  panSlider = createSlider(0, 1000, 0, 1);
  panSlider.position(sliderLeftMargin, drawHeight + 80);
  panSlider.size(canvasWidth - sliderLeftMargin - margin);
  layoutControls();

  describe('A logic analyzer view with two stacked digital traces, SCL and SDA, a time axis, and a colored annotation band that decodes the I2C start, address, read or write bit, acknowledge, data bytes and stop. Clicking part of the waveform explains it. A diagnosis menu and Check button give feedback on what went wrong in each capture.');
}

function captureLabel(i) {
  const base = ['Capture 1: OLED write', 'Capture 2: OLED write', 'Capture 3: OLED write', 'Capture 4: button on GP14'][i];
  return solved[i] ? base + ' (' + captures[i].title + ')' : base;
}

// ---------- Build the four captures ----------
function buildCaptures() {
  captures = [
    i2cCapture([0x78, 0x00, 0xAF], [true, true, true], false, 'good', 'good write to 0x3C'),
    i2cCapture([0x78, 0x00, 0xAF], [true, true, true], true, 'slow', 'missing pull-ups, slow edges'),
    i2cCapture([0x7A, 0x00, 0xAF], [false], false, 'nack', 'wrong address, no ACK'),
    bounceCapture()
  ];
}

// I2C at 100 kHz: one bit every 10 microseconds. SDA changes while SCL is low.
function i2cCapture(bytes, acks, slow, answer, title) {
  const scl = [[0, 1]];
  const sda = [[0, 1]];
  const segs = [];
  const bits = [];
  const setSDA = (t, v) => { if (sda[sda.length - 1][1] !== v) sda.push([t, v]); };

  // START
  sda.push([4, 0]);
  scl.push([8, 0]);
  segs.push({ t0: 0, t1: 9, label: 'START', col: 'mediumseagreen', info: INFO.START });
  let t = 9;
  for (let b = 0; b < bytes.length; b++) {
    const start = t;
    for (let i = 7; i >= 0; i--) {
      const v = (bytes[b] >> i) & 1;
      setSDA(t + 1, v);
      scl.push([t + 4, 1]);
      scl.push([t + 8, 0]);
      bits.push({ t: t + 6, v });
      t += 10;
    }
    if (b === 0) {
      const addr = bytes[0] >> 1;
      const bin = (addr >>> 0).toString(2).padStart(7, '0');
      segs.push({ t0: start, t1: start + 70, label: 'Address 0x' + hexByte(addr), col: 'steelblue',
        info: INFO.ADDR + 'Here the bits are ' + bin + ' = 0x' + hexByte(addr) + '. An SSD1306 OLED usually listens at 0x3C.' });
      segs.push({ t0: start + 70, t1: start + 80, label: (bytes[0] & 1) ? 'R' : 'W', col: 'slateblue', info: INFO.RW });
    } else {
      const d = bytes[b];
      const what = d === 0x00 ? 'For an SSD1306 this control byte means "the next bytes are commands".' :
        (d === 0xAF ? 'This is the SSD1306 "display ON" command.' : '');
      segs.push({ t0: start, t1: start + 80, label: 'Data 0x' + hexByte(d), col: 'darkorange',
        info: 'Data byte 0x' + hexByte(d) + ', sent most significant bit first. ' + what });
    }
    // ninth clock: acknowledge
    const ack = acks[b];
    setSDA(t + 1, ack ? 0 : 1);
    scl.push([t + 4, 1]);
    scl.push([t + 8, 0]);
    bits.push({ t: t + 6, v: ack ? 0 : 1 });
    segs.push({ t0: t, t1: t + 10, label: ack ? 'ACK' : 'NACK', col: ack ? 'seagreen' : 'crimson', info: ack ? INFO.ACK : INFO.NACK });
    t += 10;
    if (!ack) break;
  }
  // STOP
  setSDA(t + 1, 0);
  scl.push([t + 4, 1]);
  sda.push([t + 7, 1]);
  segs.push({ t0: t, t1: t + 10, label: 'STOP', col: 'mediumseagreen', info: INFO.STOP });
  t += 10;
  return { kind: 'i2c', ch: ['SCL', 'SDA'], unit: 'us', total: t + 6, minPx: 2.4,
    lines: [scl, sda], slow, segs, bits, answer, title };
}

// A push button on GP14 with a pull-up: pressed = low. Times in microseconds.
function bounceCapture() {
  const btn = [[0, 1], [2000, 0], [2250, 1], [2400, 0], [2700, 1], [2850, 0], [3300, 1], [3400, 0],
    [8000, 1], [8200, 0], [8350, 1], [8500, 0], [8600, 1]];
  // the program counts a press on every falling edge
  const cnt = [[0, 0]];
  for (let i = 1; i < btn.length; i++) {
    if (btn[i][1] === 0) {
      cnt.push([btn[i][0] + 30, 1]);
      cnt.push([btn[i][0] + 150, 0]);
    }
  }
  const segs = [
    { t0: 0, t1: 2000, label: 'Released', col: 'gray', info: 'Released: the pull-up resistor holds GP14 at 3.3 V (logic 1).' },
    { t0: 2000, t1: 3400, label: 'Press', col: 'crimson', info: 'Press: the metal contacts touch, bounce apart and touch again several times in about 1.5 ms. Each fall from 1 to 0 looks like a new press.' },
    { t0: 3400, t1: 8000, label: 'Held down', col: 'steelblue', info: 'Held down: the contacts have settled, so GP14 stays at 0 V (logic 0).' },
    { t0: 8000, t1: 8600, label: 'Release', col: 'darkorange', info: 'Release: the contacts bounce again as they separate, adding more false falling edges.' },
    { t0: 8600, t1: 12000, label: 'Released', col: 'gray', info: 'Released again. One real press produced six counted presses on the second channel.' }
  ];
  return { kind: 'gpio', ch: ['GP14', 'Count'], unit: 'ms', total: 12000, minPx: 0.05,
    lines: [btn, cnt], slow: false, segs, bits: [], answer: 'bounce', title: 'contact bounce' };
}

function hexByte(v) {
  return v.toString(16).toUpperCase().padStart(2, '0');
}

function checkDiagnosis() {
  const c = captures[cur];
  const pick = diagSelect.value();
  if (pick === '') {
    feedback[cur] = 'Choose a diagnosis from the menu first.';
    return;
  }
  if (pick === c.answer) {
    solved[cur] = true;
    const why = {
      good: 'Correct: the device pulled SDA low on the ninth clock after every byte, and the message ends with a clean STOP.',
      slow: 'Correct: the rising edges curve up slowly instead of jumping. Pull-up resistors are what pull the lines high, so missing or weak ones make every rise slow, and at higher speeds bits are misread.',
      nack: 'Correct: the address is 0x3D, not 0x3C, and SDA stays high on the ninth clock. No device answered, so the controller sent STOP.',
      bounce: 'Correct: one press made the input fall six times, so the program counted six presses. A debounce delay fixes this.'
    }[c.answer];
    feedback[cur] = why;
    // reveal the capture name in the menu
    const opts = captureSelect.elt.options;
    opts[cur].text = captureLabel(cur);
  } else {
    const hint = {
      good: 'Not quite. Click each ACK box: who is holding SDA low on the ninth clock? Are the edges sharp?',
      slow: 'Not quite. The decode is fine, so look at the shape of the edges. Do the lines jump up, or curve up?',
      nack: 'Not quite. Click the address and read its value, then look at SDA on the ninth clock.',
      bounce: 'Not quite. This capture is a button, not I2C. Count the falling edges during one press.'
    }[c.answer];
    feedback[cur] = hint;
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

  const c = captures[cur];

  noStroke();
  fill('black');
  textAlign(CENTER, TOP);
  textSize(22);
  text('Logic Analyzer Trace Reader', canvasWidth / 2, 8);

  // horizontal scaling and scrolling
  plotX0 = 70;
  plotX1 = canvasWidth - 12;
  const plotW = plotX1 - plotX0;
  unitPx = max(plotW / c.total, c.minPx);
  const viewSpan = plotW / unitPx;
  const maxStart = max(0, c.total - viewSpan);
  viewStart = maxStart * panSlider.value() / 1000;
  if (maxStart <= 0) panSlider.attribute('disabled', '');
  else panSlider.removeAttribute('disabled');
  const tx = (t) => plotX0 + (t - viewStart) * unitPx;

  // trace area background
  const bandY = 40;
  const ch0 = { top: 86, bot: 136 };
  const ch1 = { top: 158, bot: 208 };
  stroke('silver');
  fill('black');
  rect(plotX0 - 4, bandY - 2, plotW + 8, 232, 4);

  drawingContext.save();
  drawingContext.beginPath();
  drawingContext.rect(plotX0, bandY - 2, plotW, 232);
  drawingContext.clip();

  // annotation band and selection highlight
  for (let i = 0; i < c.segs.length; i++) {
    const s = c.segs[i];
    const x0 = tx(s.t0);
    const x1 = tx(s.t1);
    noStroke();
    fill(s.col);
    rect(x0 + 1, bandY + 2, x1 - x0 - 2, 30, 3);
    fill('white');
    textSize(13);
    textAlign(CENTER, CENTER);
    // short boxes use the standard one-letter I2C abbreviations: S, A, N, P
    const short = { START: 'S', ACK: 'A', NACK: 'N', STOP: 'P' }[s.label] || s.label;
    if (textWidth(s.label) < x1 - x0 - 4) text(s.label, (x0 + x1) / 2, bandY + 17);
    else if (textWidth(short) < x1 - x0 - 2) text(short, (x0 + x1) / 2, bandY + 17);
    if (i === selected) {
      fill(255, 255, 0, 60);
      rect(x0, bandY, x1 - x0, 226);
      stroke('yellow');
      noFill();
      rect(x0, bandY, x1 - x0, 226);
    }
  }

  // threshold guides on the I2C channels
  if (c.kind === 'i2c') {
    stroke(70);
    drawingContext.setLineDash([2, 4]);
    for (const ch of [ch0, ch1]) {
      const yth = lerp(ch.bot, ch.top, 0.7);
      line(plotX0, yth, plotX1, yth);
    }
    drawingContext.setLineDash([]);
  }

  // traces
  drawTrace(c.lines[0], ch0, tx, c.slow, 'yellow', c.total);
  drawTrace(c.lines[1], ch1, tx, c.slow, 'cyan', c.total);

  // bit values under SDA
  noStroke();
  fill('white');
  textSize(13);
  textAlign(CENTER, TOP);
  for (const b of c.bits) text(b.v, tx(b.t), ch1.bot + 4);

  // time axis
  stroke(90);
  const tickStep = c.unit === 'us' ? 50 : 1000;
  for (let t = tickStep; t <= c.total; t += tickStep) {
    const x = tx(t);
    if (x > plotX1 - 18) continue;
    stroke(90);
    line(x, ch1.bot + 22, x, ch1.bot + 26);
    noStroke();
    fill('lightgray');
    textSize(12);
    text(c.unit === 'us' ? t + ' µs' : (t / 1000) + ' ms', x, ch1.bot + 26);
  }
  drawingContext.restore();

  // channel names
  noStroke();
  fill('black');
  textSize(15);
  textAlign(RIGHT, CENTER);
  text(c.ch[0], plotX0 - 8, (ch0.top + ch0.bot) / 2);
  text(c.ch[1], plotX0 - 8, (ch1.top + ch1.bot) / 2);
  textSize(12);
  text('decode', plotX0 - 8, bandY + 17);

  // info box
  const iy = bandY + 240;
  const ih = drawHeight - iy - 8;
  stroke('silver');
  fill('white');
  rect(10, iy, canvasWidth - 20, ih, 8);
  noStroke();
  textAlign(LEFT, TOP);
  textSize(15);
  fill('black');
  const msg = selected >= 0 ? c.segs[selected].info : 'Click any part of the waveform to name it (S = start, A = ACK, N = no ACK, P = stop). Then choose a diagnosis and press Check.';
  text(msg, 20, iy + 8, canvasWidth - 40, 60);
  if (feedback[cur]) {
    fill(feedback[cur].startsWith('Correct') ? 'darkgreen' : 'firebrick');
    text(feedback[cur], 20, iy + 54, canvasWidth - 40, ih - 58);
  }

  // control labels
  noStroke();
  fill('black');
  textAlign(LEFT, CENTER);
  textSize(defaultTextSize);
  text('Capture:', 10, drawHeight + 18);
  text('Diagnosis:', 10, drawHeight + 53);
  fill(maxStart > 0 ? 'black' : 'silver');
  text('Scroll:', 10, drawHeight + 90);
}

// Digital trace; for weak pull-ups, rising edges curve up like a charging capacitor
function drawTrace(edges, ch, tx, slow, col, total) {
  stroke(col);
  strokeWeight(2);
  noFill();
  const y = (v) => lerp(ch.bot, ch.top, v);
  beginShape();
  vertex(tx(0), y(edges[0][1]));
  for (let i = 1; i < edges.length; i++) {
    const [t, v] = edges[i];
    const prev = edges[i - 1][1];
    const next = i + 1 < edges.length ? edges[i + 1][0] : total;
    vertex(tx(t), y(prev));
    if (slow && v === 1 && prev === 0) {
      // RC rise with a time constant of 2.5 microseconds
      const tau = 2.5;
      for (let dt = 0; dt <= min(next - t, 12); dt += 0.25) {
        vertex(tx(t + dt), y(1 - Math.exp(-dt / tau)));
      }
    } else {
      vertex(tx(t), y(v));
    }
  }
  vertex(tx(total), y(edges[edges.length - 1][1]));
  endShape();
  strokeWeight(1);
}

function mousePressed() {
  if (mouseY < 38 || mouseY > 270 || mouseX < plotX0 || mouseX > plotX1) return;
  const t = viewStart + (mouseX - plotX0) / unitPx;
  const segs = captures[cur].segs;
  selected = -1;
  for (let i = 0; i < segs.length; i++) {
    if (t >= segs[i].t0 && t < segs[i].t1) selected = i;
  }
}

function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
  panSlider.size(canvasWidth - sliderLeftMargin - margin);
  layoutControls();
}

// Keep the diagnosis menu and Check button inside the canvas on narrow screens
function layoutControls() {
  const maxSel = canvasWidth - sliderLeftMargin - 80;
  diagSelect.style('max-width', maxSel + 'px');
  captureSelect.style('max-width', (canvasWidth - sliderLeftMargin - 10) + 'px');
  const selW = min(diagSelect.elt.offsetWidth || 280, maxSel);
  checkButton.position(sliderLeftMargin + selW + 10, drawHeight + 41);
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) {
    canvasWidth = Math.floor(container.getBoundingClientRect().width);
  }
}
