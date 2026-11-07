// I2C Conversation Animator
// CANVAS_HEIGHT: 530
// Step-through view of one I2C write transaction: START, 7-bit address + write bit,
// ACK, data byte, ACK, STOP. Only the addressed device answers; a wrong address gets no ACK.

let canvasWidth = 700;
let drawHeight = 450;
let controlHeight = 80;
let canvasHeight = drawHeight + controlHeight;
let margin = 20;
let defaultTextSize = 16;

const devices = [
  { name: 'OLED', addr: 0x3C },
  { name: 'RTC', addr: 0x68 },
  { name: 'Sensor', addr: 0x76 }
];
const targets = [
  { label: 'OLED display (0x3C)', addr: 0x3C },
  { label: 'RTC clock chip (0x68)', addr: 0x68 },
  { label: 'Sensor (0x76)', addr: 0x76 },
  { label: 'Wrong address (0x50)', addr: 0x50 }
];
const dataBytes = [0xA5, 0x30, 0x0F, 0xFF, 0x00];

let targetSelect, dataSelect, resetButton, backButton, nextButton;
let step = 0;          // 0 = idle, then one step per part of the transaction

// Slot list for the current transaction. Each slot: {type, val, field, driver}
let slots = [];
let steps = [];        // each step: {title, text, slotsShown}

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  targetSelect = createSelect();
  targets.forEach((t, i) => targetSelect.option(t.label, String(i)));
  targetSelect.selected('0');
  targetSelect.changed(rebuild);

  dataSelect = createSelect();
  dataBytes.forEach(b => dataSelect.option('data ' + hex2(b), String(b)));
  dataSelect.selected(String(0xA5));
  dataSelect.changed(rebuild);

  resetButton = createButton('Reset');
  resetButton.mousePressed(() => { step = 0; });
  backButton = createButton('Back');
  backButton.mousePressed(() => { step = max(0, step - 1); });
  nextButton = createButton('Next step');
  nextButton.mousePressed(() => { step = min(steps.length - 1, step + 1); });

  positionControls();
  rebuild();
  describe('A Pico and three I2C devices share SDA and SCL lines. Below, SCL and SDA waveforms ' +
    'are revealed one step at a time: start, address and write bit, acknowledge, data byte, ' +
    'acknowledge and stop.', LABEL);
}

function positionControls() {
  let y1 = drawHeight + 8, y2 = drawHeight + 43;
  targetSelect.position(75, y1);
  dataSelect.position(260, y1);
  resetButton.position(10, y2);
  backButton.position(75, y2);
  nextButton.position(135, y2);
}

// Build the 20-slot bit list and the step script for the chosen target and byte
function rebuild() {
  step = 0;
  let t = targets[int(targetSelect.value())];
  let data = int(dataSelect.value());
  let hit = devices.find(d => d.addr === t.addr);
  slots = [];
  slots.push({ type: 'start', field: 'S' });
  for (let b = 6; b >= 0; b--) slots.push({ type: 'bit', val: (t.addr >> b) & 1, field: 'addr', driver: 'pico' });
  slots.push({ type: 'bit', val: 0, field: 'W', driver: 'pico' });
  slots.push({ type: 'bit', val: hit ? 0 : 1, field: hit ? 'ACK' : 'NACK', driver: hit ? 'dev' : 'none' });
  if (hit) {
    for (let b = 7; b >= 0; b--) slots.push({ type: 'bit', val: (data >> b) & 1, field: 'data', driver: 'pico' });
    slots.push({ type: 'bit', val: 0, field: 'ACK', driver: 'dev' });
  }
  slots.push({ type: 'stop', field: 'P' });

  let addrBits = t.addr.toString(2).padStart(7, '0');
  steps = [
    { title: 'Bus idle', shown: 0,
      text: 'Both lines rest HIGH because of the pull-up resistors. Press Next step to begin.' },
    { title: 'START condition', shown: 1,
      text: 'The Pico pulls SDA low while SCL is still high. Every device wakes up and starts listening.' },
    { title: 'Address ' + hex2(t.addr) + ' + write bit', shown: 9,
      text: 'The Pico sends ' + addrBits + ' (' + hex2(t.addr) + ') then 0 for "write". ' +
        'SDA changes only while SCL is low; devices read it when SCL goes high.' }
  ];
  if (hit) {
    steps.push({ title: 'ACK from ' + hit.name, shown: 10,
      text: 'Only the ' + hit.name + ' matches ' + hex2(t.addr) + ', so it pulls SDA low for one clock: "I am here." The others stay quiet.' });
    steps.push({ title: 'Data byte ' + hex2(data), shown: 18,
      text: 'The Pico sends 8 data bits, MSB first: ' + data.toString(2).padStart(8, '0') + ' (' + hex2(data) + ').' });
    steps.push({ title: 'ACK for the data', shown: 19,
      text: 'The ' + hit.name + ' pulls SDA low again to say it received the byte.' });
    steps.push({ title: 'STOP condition', shown: 20,
      text: 'SDA rises while SCL is high. The bus is free again. Total: 20 clock slots for 1 data byte.' });
  } else {
    steps.push({ title: 'No ACK (NACK)', shown: 10,
      text: 'No device has address ' + hex2(t.addr) + ', so nobody pulls SDA low: a NACK. ' +
        'MicroPython raises OSError EIO.' });
    steps.push({ title: 'STOP condition', shown: 11,
      text: 'The Pico gives up and sends STOP. No data byte was sent.' });
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

  noStroke();
  fill('black');
  textAlign(CENTER, TOP);
  textSize(24);
  text('I2C Conversation Animator', canvasWidth / 2, 8);

  drawBus();
  drawWaveforms();
  drawExplanation();

  // control labels
  noStroke();
  fill('black');
  textSize(15);
  textAlign(LEFT, CENTER);
  text('Talk to:', 10, drawHeight + 19);
  textAlign(LEFT, CENTER);
  text('Step ' + step + ' of ' + (steps.length - 1), 240, drawHeight + 54);
}

// ---------- bus diagram ----------
function drawBus() {
  let top = 44;
  let picoW = canvasWidth < 520 ? 70 : 92, picoH = 104;
  let sdaY = top + 30, sclY = top + 58;
  let lineEnd = canvasWidth - margin;
  let cur = steps[step];
  let shownSlots = slots.slice(0, cur.shown);
  let lastSlot = shownSlots.length ? shownSlots[shownSlots.length - 1] : null;
  let t = targets[int(targetSelect.value())];
  let hit = devices.find(d => d.addr === t.addr);
  let ackShown = step >= 3 && hit;

  // Pico
  stroke('darkgreen');
  fill('mediumseagreen');
  rect(margin, top, picoW, picoH, 6);
  noStroke();
  fill('white');
  textAlign(CENTER, CENTER);
  textSize(16);
  text('Pico', margin + picoW / 2, top + picoH / 2 - 10);
  textSize(12);
  text('controller', margin + picoW / 2, top + picoH / 2 + 10);

  // who is driving SDA in the latest step
  let sdaColor = 'gray';
  if (lastSlot && lastSlot.driver === 'pico') sdaColor = 'steelblue';
  if (lastSlot && lastSlot.driver === 'dev') sdaColor = 'darkorange';
  if (lastSlot && (lastSlot.type === 'start' || lastSlot.type === 'stop')) sdaColor = 'steelblue';

  strokeWeight(4);
  stroke(sdaColor);
  line(margin + picoW, sdaY, lineEnd, sdaY);
  stroke(step > 0 && step < steps.length - 1 ? 'mediumpurple' : 'gray');
  line(margin + picoW, sclY, lineEnd, sclY);
  strokeWeight(1);
  noStroke();
  fill('black');
  textSize(13);
  textAlign(LEFT, BOTTOM);
  text('SDA (data)', margin + picoW + 6, sdaY - 3);
  text('SCL (clock)', margin + picoW + 6, sclY - 3);

  // devices
  let x0 = margin + picoW + (canvasWidth < 520 ? 70 : 100);
  let avail = lineEnd - x0;
  let w = min(130, avail / 3 - 10);
  for (let i = 0; i < 3; i++) {
    let d = devices[i];
    let cx = x0 + (i + 0.5) * (avail / 3);
    let by = top + 76;
    stroke('dimgray');
    strokeWeight(2);
    line(cx - 10, sdaY, cx - 10, by);
    line(cx + 10, sclY, cx + 10, by);
    fill('dimgray');
    circle(cx - 10, sdaY, 7);
    circle(cx + 10, sclY, 7);
    strokeWeight(1);
    let selected = ackShown && hit === d;
    stroke(selected ? 'darkorange' : 'gray');
    strokeWeight(selected ? 3 : 1);
    fill(selected ? 'gold' : (step >= 3 ? 'gainsboro' : 'white'));
    rect(cx - w / 2, by, w, 46, 6);
    strokeWeight(1);
    noStroke();
    fill('black');
    textAlign(CENTER, CENTER);
    textSize(w < 85 ? 13 : 15);
    text(d.name, cx, by + 14);
    text(hex2(d.addr), cx, by + 32);
    if (step >= 3) {
      textSize(12);
      fill(selected ? 'darkorange' : 'dimgray');
      text(selected ? 'ACK!' : 'not me', cx, by + 58);
    }
  }
}

// ---------- waveforms ----------
function drawWaveforms() {
  let top = 190;
  let labelW = 44;
  let left = margin + labelW;
  let right = canvasWidth - margin;
  let n = 20;                       // fixed 20 slots so the picture does not jump
  let slotW = (right - left) / n;
  let sclHi = top + 34, sclLo = top + 62;
  let sdaHi = top + 96, sdaLo = top + 124;
  let shown = steps[step].shown;

  // labels and guide lines
  noStroke();
  fill('black');
  textSize(14);
  textAlign(LEFT, CENTER);
  text('SCL', margin, (sclHi + sclLo) / 2);
  text('SDA', margin, (sdaHi + sdaLo) / 2);
  stroke('gainsboro');
  for (let k = 0; k <= n; k++) {
    let x = left + k * slotW;
    line(x, sclHi - 4, x, sdaLo + 4);
  }

  // field labels above the SCL trace
  let groups = groupFields();
  noStroke();
  textAlign(CENTER, BOTTOM);
  textSize(slotW < 20 ? 11 : 13);
  for (let g of groups) {
    if (g.start >= shown) continue;
    let gx0 = left + g.start * slotW, gx1 = left + min(g.end, shown) * slotW;
    fill(g.color);
    rect(gx0 + 1, top + 4, gx1 - gx0 - 2, 18, 3);
    fill('white');
    let lbl = g.label;
    if (textWidth(lbl) > gx1 - gx0 - 4) lbl = g.short;
    text(lbl, (gx0 + gx1) / 2, top + 20);
  }

  // traces: idle before first slot, then each revealed slot
  strokeWeight(3);
  noFill();
  for (let k = 0; k < shown; k++) {
    let s = slots[k];
    let x0 = left + k * slotW, x1 = x0 + slotW;
    let prevSda = k === 0 ? 1 : sdaLevelAtEnd(slots[k - 1]);
    // SCL
    stroke('mediumpurple');
    if (s.type === 'start') {
      polyline([[x0, sclHi], [x0 + slotW * 0.75, sclHi], [x0 + slotW * 0.75, sclLo], [x1, sclLo]]);
    } else if (s.type === 'stop') {
      polyline([[x0, sclLo], [x0 + slotW * 0.25, sclLo], [x0 + slotW * 0.25, sclHi], [x1, sclHi]]);
    } else {
      polyline([[x0, sclLo], [x0 + slotW * 0.25, sclLo], [x0 + slotW * 0.25, sclHi],
        [x0 + slotW * 0.75, sclHi], [x0 + slotW * 0.75, sclLo], [x1, sclLo]]);
    }
    // SDA
    let col = s.driver === 'dev' ? 'darkorange' : (s.driver === 'none' ? 'firebrick' : 'steelblue');
    stroke(col);
    let yPrev = prevSda ? sdaHi : sdaLo;
    if (s.type === 'start') {
      polyline([[x0, sdaHi], [x0 + slotW * 0.4, sdaHi], [x0 + slotW * 0.4, sdaLo], [x1, sdaLo]]);
    } else if (s.type === 'stop') {
      polyline([[x0, yPrev], [x0 + slotW * 0.1, yPrev], [x0 + slotW * 0.1, sdaLo], [x0 + slotW * 0.6, sdaLo],
        [x0 + slotW * 0.6, sdaHi], [x1, sdaHi]]);
    } else {
      let y = s.val ? sdaHi : sdaLo;
      polyline([[x0, yPrev], [x0 + slotW * 0.1, yPrev], [x0 + slotW * 0.1, y], [x1, y]]);
    }
  }
  // idle line for the part not yet sent (dashed look via light color)
  stroke('lightgray');
  let xs = left + shown * slotW;
  if (shown < n) {
    let endSda = shown === 0 ? 1 : sdaLevelAtEnd(slots[shown - 1]);
    let endScl = shown === 0 ? 1 : (slots[shown - 1].type === 'stop' ? 1 : 0);
    line(xs, endScl ? sclHi : sclLo, right, endScl ? sclHi : sclLo);
    line(xs, endSda ? sdaHi : sdaLo, right, endSda ? sdaHi : sdaLo);
  }
  strokeWeight(1);

  // bit values under SDA
  noStroke();
  textAlign(CENTER, TOP);
  textSize(slotW < 20 ? 11 : 13);
  for (let k = 0; k < shown; k++) {
    let s = slots[k];
    if (s.type !== 'bit') continue;
    fill(s.driver === 'dev' ? 'darkorange' : (s.driver === 'none' ? 'firebrick' : 'black'));
    text(s.val, left + (k + 0.5) * slotW, sdaLo + 6);
  }

  // legend
  textSize(13);
  textAlign(LEFT, TOP);
  let ly = sdaLo + 26;
  fill('steelblue'); rect(left, ly + 3, 14, 10);
  fill('black'); text('Pico drives SDA', left + 20, ly);
  fill('darkorange'); rect(left + 150, ly + 3, 14, 10);
  fill('black'); text('device drives SDA (ACK)', left + 170, ly);
}

function sdaLevelAtEnd(s) {
  if (s.type === 'start') return 0;
  if (s.type === 'stop') return 1;
  return s.val;
}

function groupFields() {
  let t = targets[int(targetSelect.value())];
  let data = int(dataSelect.value());
  let groups = [];
  let k = 0;
  while (k < slots.length) {
    let f = slots[k].field;
    let start = k;
    while (k < slots.length && slots[k].field === f) k++;
    let g = { start: start, end: k };
    if (f === 'S') { g.label = 'START'; g.short = 'S'; g.color = 'seagreen'; }
    else if (f === 'addr') { g.label = 'Address ' + hex2(t.addr); g.short = hex2(t.addr); g.color = 'steelblue'; }
    else if (f === 'W') { g.label = 'W'; g.short = 'W'; g.color = 'slategray'; }
    else if (f === 'ACK') { g.label = 'ACK'; g.short = 'A'; g.color = 'darkorange'; }
    else if (f === 'NACK') { g.label = 'NACK'; g.short = 'N'; g.color = 'firebrick'; }
    else if (f === 'data') { g.label = 'Data ' + hex2(data); g.short = hex2(data); g.color = 'royalblue'; }
    else if (f === 'P') { g.label = 'STOP'; g.short = 'P'; g.color = 'seagreen'; }
    groups.push(g);
  }
  return groups;
}

function polyline(pts) {
  beginShape();
  for (let p of pts) vertex(p[0], p[1]);
  endShape();
}

// ---------- explanation panel ----------
function drawExplanation() {
  let y = 362;
  let cur = steps[step];
  stroke('lightgray');
  fill(255, 255, 255, 230);
  rect(margin, y, canvasWidth - 2 * margin, 82, 10);
  noStroke();
  fill('black');
  textAlign(LEFT, TOP);
  textSize(16);
  textStyle(BOLD);
  text(cur.title, margin + 12, y + 8);
  textStyle(NORMAL);
  textSize(canvasWidth < 520 ? 13 : 14);
  text(cur.text, margin + 12, y + 30, canvasWidth - 2 * margin - 24, 52);
}

function hex2(v) { return '0x' + v.toString(16).toUpperCase().padStart(2, '0'); }

function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
  positionControls();
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) canvasWidth = max(360, container.offsetWidth);
}
