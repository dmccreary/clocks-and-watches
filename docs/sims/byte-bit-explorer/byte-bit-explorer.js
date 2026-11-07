// Byte Bit Explorer
// CANVAS_HEIGHT: 470
// Students toggle the 8 bits of a byte, apply set/clear/shift operations,
// predict the result, and watch the byte go onto a serial wire MSB-first or LSB-first.

let canvasWidth = 600;
let drawHeight = 355;
let controlHeight = 115;
let canvasHeight = drawHeight + controlHeight;
let margin = 20;
let defaultTextSize = 16;

let value = 0xC1;          // the byte being explored (0..255)
let selectedBit = 3;       // bit position used by Set bit / Clear bit
let lastCode = 'x = 0b11000001   # starting value 0xC1';

// Predict mode state
let pending = null;        // {code, before, after, label}
let feedback = '';
let feedbackColor = 'black';

// Serial send animation state (only runs after the student presses Send)
let sending = false;
let sendIndex = 8;         // number of bits already on the wire (8 = all shown)
let lastStepTime = 0;
let stepMs = 450;

// Controls
let bitSelect, setButton, clearButton, leftButton, rightButton;
let orderSelect, sendButton, randomButton;
let predictCheckbox, answerInput, checkButton;

// Layout values computed each frame
let boxW, boxH = 52, boxY = 66, boxX0;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  // Row 1: bit operations
  bitSelect = createSelect();
  for (let b = 7; b >= 0; b--) bitSelect.option('bit ' + b + ' (' + (1 << b) + ')', String(b));
  bitSelect.selected(String(selectedBit));
  bitSelect.changed(() => { selectedBit = int(bitSelect.value()); });
  setButton = createButton('Set bit');
  setButton.mousePressed(() => applyOp('set'));
  clearButton = createButton('Clear bit');
  clearButton.mousePressed(() => applyOp('clear'));
  leftButton = createButton('Shift left');
  leftButton.mousePressed(() => applyOp('left'));
  rightButton = createButton('Shift right');
  rightButton.mousePressed(() => applyOp('right'));

  // Row 2: transmission
  orderSelect = createSelect();
  orderSelect.option('MSB first');
  orderSelect.option('LSB first');
  orderSelect.selected('MSB first');
  orderSelect.changed(() => { sending = false; sendIndex = 8; });
  sendButton = createButton('Send byte');
  sendButton.mousePressed(startSend);
  randomButton = createButton('Random byte');
  randomButton.mousePressed(() => {
    if (pending) return;
    value = floor(random(256));
    lastCode = 'x = ' + bin8(value) + '   # new random value';
    feedback = '';
    sendIndex = 8; sending = false;
  });

  // Row 3: predict mode
  predictCheckbox = createCheckbox(' Predict mode', false);
  predictCheckbox.changed(() => {
    if (!predictCheckbox.checked() && pending) revealPending();
    feedback = predictCheckbox.checked()
      ? 'Pick an operation, then type the new decimal value.' : '';
    feedbackColor = 'black';
  });
  answerInput = createInput('', 'number');
  answerInput.size(70);
  checkButton = createButton('Check');
  checkButton.mousePressed(checkAnswer);

  positionControls();
  describe('Eight clickable bit boxes worth 128 down to 1 with decimal, hex and binary readouts, ' +
    'buttons to set, clear and shift bits, and a serial wire that shows the order the bits are sent.', LABEL);
}

function positionControls() {
  let y1 = drawHeight + 8, y2 = drawHeight + 43, y3 = drawHeight + 78;
  bitSelect.position(10, y1);
  setButton.position(130, y1);
  clearButton.position(200, y1);
  leftButton.position(280, y1);
  rightButton.position(365, y1);

  orderSelect.position(10, y2);
  sendButton.position(120, y2);
  randomButton.position(205, y2);

  predictCheckbox.position(10, y3);
  answerInput.position(140, y3);
  checkButton.position(225, y3);
}

function draw() {
  updateCanvasSize();

  // Drawing and control regions
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
  textSize(24);
  text('Byte Bit Explorer', canvasWidth / 2, 8);

  advanceSend();
  drawBitBoxes();
  drawReadouts();
  drawWire();
  drawControlLabels();
}

// ---------- bit boxes ----------
function drawBitBoxes() {
  let gap = 6;
  boxW = min(72, (canvasWidth - 2 * margin - 7 * gap) / 8);
  let total = 8 * boxW + 7 * gap;
  boxX0 = (canvasWidth - total) / 2;
  let shown = pending ? pending.before : value;

  for (let i = 0; i < 8; i++) {
    let bit = 7 - i;
    let x = boxX0 + i * (boxW + gap);
    let on = (shown >> bit) & 1;
    // place-value label above
    noStroke();
    fill('dimgray');
    textAlign(CENTER, BOTTOM);
    textSize(boxW < 45 ? 13 : 16);
    text(1 << bit, x + boxW / 2, boxY - 4);
    // box
    stroke(bit === selectedBit ? 'darkorange' : 'gray');
    strokeWeight(bit === selectedBit ? 3 : 1);
    fill(on ? 'steelblue' : 'white');
    rect(x, boxY, boxW, boxH, 6);
    noStroke();
    fill(on ? 'white' : 'gray');
    textAlign(CENTER, CENTER);
    textSize(26);
    text(on, x + boxW / 2, boxY + boxH / 2);
    // bit number below
    fill('dimgray');
    textAlign(CENTER, TOP);
    textSize(boxW < 45 ? 12 : 14);
    text((boxW < 45 ? 'b' : 'bit ') + bit, x + boxW / 2, boxY + boxH + 3);
  }
  strokeWeight(1);
  // MSB / LSB tags
  noStroke();
  fill('black');
  textSize(13);
  textAlign(LEFT, BOTTOM);
  text('MSB', boxX0, boxY - 20);
  textAlign(RIGHT, BOTTOM);
  text('LSB', boxX0 + total, boxY - 20);
}

// ---------- decimal / hex / binary readouts ----------
function drawReadouts() {
  let y = boxY + boxH + 30;
  noStroke();
  textAlign(CENTER, TOP);
  textSize(18);
  fill('black');
  let line;
  if (pending) {
    line = 'Decimal: ?     Hex: ?     Binary: ?';
  } else {
    line = 'Decimal: ' + value + '     Hex: ' + hex2(value) + '     Binary: ' + bin8(value);
  }
  if (textWidth(line) > canvasWidth - 20) {
    textSize(15);
    line = pending ? 'Dec ?   Hex ?   Bin ?' :
      'Dec ' + value + '   Hex ' + hex2(value) + '   Bin ' + bin8(value);
  }
  text(line, canvasWidth / 2, y);

  // code line for the last operation
  textSize(15);
  fill('darkslateblue');
  let code = pending ? pending.code + '   # what is x now?' : lastCode;
  text(code, canvasWidth / 2, y + 28);

  // feedback line
  if (feedback) {
    fill(feedbackColor);
    textSize(15);
    text(feedback, canvasWidth / 2, y + 50);
  }
}

// ---------- serial wire ----------
function orderedBits() {
  // returns list of {bit, val} in the order they go onto the wire
  let shown = pending ? pending.before : value;
  let list = [];
  let msbFirst = orderSelect.value() === 'MSB first';
  for (let k = 0; k < 8; k++) {
    let bit = msbFirst ? 7 - k : k;
    list.push({ bit: bit, val: (shown >> bit) & 1 });
  }
  return list;
}

function drawWire() {
  let top = 238;
  let senderW = min(80, canvasWidth * 0.14);
  let left = margin + senderW + 8;
  let right = canvasWidth - margin - senderW - 8;
  let slotW = (right - left) / 8;
  let hiY = top + 22, loY = top + 62;

  // sender and receiver boxes
  stroke('gray');
  fill('lavender');
  rect(margin, hiY - 8, senderW, 56, 6);
  rect(canvasWidth - margin - senderW, hiY - 8, senderW, 56, 6);
  noStroke();
  fill('black');
  textAlign(CENTER, CENTER);
  textSize(14);
  text('Sender', margin + senderW / 2, hiY + 6);
  text('Receiver', canvasWidth - margin - senderW / 2, hiY + 6);
  textSize(12);
  text('(Pico)', margin + senderW / 2, hiY + 26);
  text('(device)', canvasWidth - margin - senderW / 2, hiY + 26);

  // heading
  textSize(14);
  textAlign(LEFT, BOTTOM);
  fill('black');
  text('Data wire, ' + orderSelect.value() + ' (time runs left to right):', margin, top + 6);

  let bits = orderedBits();
  // waveform
  stroke('seagreen');
  strokeWeight(3);
  noFill();
  let prevY = null;
  for (let k = 0; k < 8; k++) {
    if (k >= sendIndex) break;
    let y = bits[k].val ? hiY : loY;
    let x0 = left + k * slotW, x1 = x0 + slotW;
    if (prevY !== null && prevY !== y) line(x0, prevY, x0, y);
    line(x0, y, x1, y);
    prevY = y;
  }
  strokeWeight(1);
  // slot grid and labels
  for (let k = 0; k < 8; k++) {
    let x0 = left + k * slotW;
    stroke('lightgray');
    line(x0, hiY - 6, x0, loY + 6);
    noStroke();
    textAlign(CENTER, TOP);
    textSize(slotW < 40 ? 11 : 13);
    fill('dimgray');
    text(ordinal(k + 1), x0 + slotW / 2, loY + 8);
    if (k < sendIndex) {
      fill('black');
      textSize(slotW < 40 ? 12 : 14);
      text('b' + bits[k].bit + '=' + bits[k].val, x0 + slotW / 2, loY + 26);
    }
  }
  stroke('lightgray');
  line(right, hiY - 6, right, loY + 6);

  // moving pulse marker while sending
  if (sending && sendIndex < 8) {
    let frac = constrain((millis() - lastStepTime) / stepMs, 0, 1);
    let x = left + (sendIndex + frac) * slotW;
    noStroke();
    fill('darkorange');
    circle(x, (hiY + loY) / 2, 12);
  }

  // high / low labels
  noStroke();
  fill('dimgray');
  textSize(11);
  textAlign(RIGHT, CENTER);
  text('1', left - 2, hiY);
  text('0', left - 2, loY);
}

function drawControlLabels() {
  noStroke();
  fill('black');
  textSize(14);
  textAlign(LEFT, CENTER);
  if (predictCheckbox.checked()) {
    text(pending ? 'Type the new value in decimal' : 'Choose an operation', 295, drawHeight + 90);
  }
}

// ---------- operations ----------
function applyOp(op) {
  if (pending) {
    feedback = 'Type your prediction and press Check first.';
    feedbackColor = 'firebrick';
    return;
  }
  let n = selectedBit;
  let before = value, after, code;
  if (op === 'set') { after = value | (1 << n); code = 'x = x | (1 << ' + n + ')'; }
  if (op === 'clear') { after = value & ~(1 << n) & 0xFF; code = 'x = x & ~(1 << ' + n + ')'; }
  if (op === 'left') { after = (value << 1) & 0xFF; code = 'x = (x << 1) & 0xFF'; }
  if (op === 'right') { after = value >> 1; code = 'x = x >> 1'; }
  sending = false; sendIndex = 8;

  if (predictCheckbox.checked()) {
    pending = { code: code, before: before, after: after };
    feedback = 'x was ' + before + '. Predict the decimal result.';
    feedbackColor = 'black';
    answerInput.value('');
  } else {
    value = after;
    lastCode = code + '   # ' + bin8(before) + ' -> ' + bin8(after);
    feedback = '';
  }
}

function checkAnswer() {
  if (!pending) {
    feedback = predictCheckbox.checked() ? 'Choose an operation first.' : 'Turn on Predict mode to practice.';
    feedbackColor = 'black';
    return;
  }
  let guess = int(answerInput.value());
  let correct = guess === pending.after;
  revealPending();
  if (correct) {
    feedback = 'Correct! ' + pending_last_text();
    feedbackColor = 'darkgreen';
  } else {
    feedback = 'Not quite: you typed ' + (isNaN(guess) ? 'nothing' : guess) + ', the answer is ' + value + '.';
    feedbackColor = 'firebrick';
  }
}

let revealed = null;
function revealPending() {
  value = pending.after;
  lastCode = pending.code + '   # ' + bin8(pending.before) + ' -> ' + bin8(pending.after);
  revealed = pending;
  pending = null;
}
function pending_last_text() {
  return revealed ? revealed.before + ' became ' + revealed.after + '.' : '';
}

function startSend() {
  sending = true;
  sendIndex = 0;
  lastStepTime = millis();
}

function advanceSend() {
  if (!sending) return;
  if (millis() - lastStepTime >= stepMs) {
    sendIndex++;
    lastStepTime = millis();
    if (sendIndex >= 8) { sendIndex = 8; sending = false; }
  }
}

// ---------- canvas clicks toggle bits ----------
function mousePressed() {
  if (mouseY < boxY || mouseY > boxY + boxH) return;
  for (let i = 0; i < 8; i++) {
    let x = boxX0 + i * (boxW + 6);
    if (mouseX >= x && mouseX <= x + boxW) {
      let bit = 7 - i;
      selectedBit = bit;
      bitSelect.selected(String(bit));
      if (pending) return;
      let before = value;
      value ^= (1 << bit);
      lastCode = 'x = x ^ (1 << ' + bit + ')   # ' + bin8(before) + ' -> ' + bin8(value);
      sending = false; sendIndex = 8;
      return;
    }
  }
}

// ---------- helpers ----------
function bin8(v) { return '0b' + v.toString(2).padStart(8, '0'); }
function hex2(v) { return '0x' + v.toString(16).toUpperCase().padStart(2, '0'); }
function ordinal(n) { return n + (n === 1 ? 'st' : n === 2 ? 'nd' : n === 3 ? 'rd' : 'th'); }

function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) canvasWidth = max(360, container.offsetWidth);
}
