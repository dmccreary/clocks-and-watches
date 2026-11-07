// BCD Converter MicroSim
// CANVAS_HEIGHT: 535
// Compares ordinary binary with BCD (binary-coded decimal) for the numbers 0-59,
// the range used by the seconds and minutes registers of a DS3231 RTC.
// The conversions use the same shift and mask operations as the MicroPython code:
//   bcd_to_dec(b) = (b >> 4) * 10 + (b & 0x0F)
//   dec_to_bcd(d) = ((d // 10) << 4) | (d % 10)

// ---- Layout ----
let canvasWidth = 400;
let drawHeight = 420;
let controlHeight = 115;          // 3 rows x 35 + 10
let canvasHeight = drawHeight + controlHeight;
let margin = 25;
let sliderLeftMargin = 120;
let defaultTextSize = 16;

// ---- Controls ----
let numberSlider, hexInput, asIntCheckbox, predictButton, answerInput, checkButton;

// ---- State ----
let value = 45;                   // the decimal number being shown
let hexMessage = '';              // feedback for the hex input
let predictMode = false;          // true while the student is predicting
let predictTarget = 0;
let feedback = '';                // feedback for the Predict mode
let feedbackColor = 'black';
let revealed = false;

function decToBcd(d) { return (Math.floor(d / 10) << 4) | (d % 10); }
function bcdToDec(b) { return (b >> 4) * 10 + (b & 0x0F); }
function hex2(n) { return '0x' + n.toString(16).toUpperCase().padStart(2, '0'); }
function bin8(n) { const s = n.toString(2).padStart(8, '0'); return s.slice(0, 4) + ' ' + s.slice(4); }

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  // Row 1: the decimal number
  numberSlider = createSlider(0, 59, value, 1);
  numberSlider.position(sliderLeftMargin, drawHeight + 8);
  numberSlider.size(canvasWidth - sliderLeftMargin - margin);
  numberSlider.input(() => {
    if (predictMode) togglePredict();   // moving the slider leaves Predict mode
    value = numberSlider.value();
    hexInput.value(hex2(decToBcd(value)).slice(2));
    hexMessage = '';
  });

  // Row 2: type a raw BCD byte in hex, and the "read as integer" mistake
  hexInput = createInput(hex2(decToBcd(value)).slice(2));
  hexInput.position(112, drawHeight + 43);
  hexInput.size(45);
  hexInput.input(readHexInput);

  asIntCheckbox = createCheckbox('Read BCD byte as integer', false);
  asIntCheckbox.position(172, drawHeight + 45);

  // Row 3: Predict mode
  predictButton = createButton('Predict');
  predictButton.position(10, drawHeight + 78);
  predictButton.mousePressed(togglePredict);

  answerInput = createInput('');
  answerInput.position(192, drawHeight + 78);
  answerInput.size(55);
  answerInput.attribute('placeholder', 'hex');

  checkButton = createButton('Check');
  checkButton.position(262, drawHeight + 78);
  checkButton.mousePressed(checkAnswer);

  describe('Two rows of eight bit lights. The top row shows a number from 0 to 59 in ordinary binary; ' +
    'the bottom row shows the same number in BCD, with the tens digit in the high nibble and the ones digit ' +
    'in the low nibble. Readouts show the hex bytes and the conversion formulas.');
}

// Interpret the hex box as a raw BCD byte, as if it came from an RTC register
function readHexInput() {
  if (predictMode) return;
  const txt = hexInput.value().trim().replace(/^0x/i, '');
  if (!/^[0-9a-fA-F]{1,2}$/.test(txt)) {
    hexMessage = 'Type one byte in hex, such as 45';
    return;
  }
  const b = parseInt(txt, 16);
  const hi = b >> 4, lo = b & 0x0F;
  if (hi > 9 || lo > 9) {
    hexMessage = hex2(b) + ' is not valid BCD: each nibble must be 0 to 9';
  } else if (bcdToDec(b) > 59) {
    hexMessage = hex2(b) + ' decodes to ' + bcdToDec(b) + ', above 59 (not a valid second)';
  } else {
    value = bcdToDec(b);
    numberSlider.value(value);
    hexMessage = 'Decoded ' + hex2(b) + ' as BCD = ' + value;
  }
}

function togglePredict() {
  predictMode = !predictMode;
  if (predictMode) {
    predictTarget = floor(random(10, 60));
    value = predictTarget;
    numberSlider.value(value);
    answerInput.value('');
    feedback = 'Type the BCD byte for ' + predictTarget + ' in hex, then press Check.';
    feedbackColor = 'black';
    revealed = false;
    hexInput.value('??');
    predictButton.html('Exit Predict');
  } else {
    feedback = '';
    revealed = true;
    predictButton.html('Predict');
    hexInput.value(hex2(decToBcd(value)).slice(2));
  }
}

function checkAnswer() {
  if (!predictMode) {
    feedback = 'Press Predict first to get a number.';
    feedbackColor = 'black';
    return;
  }
  const txt = answerInput.value().trim().replace(/^0x/i, '');
  const guess = parseInt(txt, 16);
  const correct = decToBcd(predictTarget);
  if (isNaN(guess)) {
    feedback = 'Type a hex byte such as 37.';
    feedbackColor = 'firebrick';
    return;
  }
  revealed = true;
  if (guess === correct) {
    feedback = 'Correct! ' + predictTarget + ' in BCD is ' + hex2(correct) + '. Press Exit Predict, then Predict again for a new number.';
    feedbackColor = 'green';
  } else if (guess === predictTarget) {
    feedback = 'That is the ordinary binary value (' + hex2(predictTarget) + '). BCD puts ' +
      Math.floor(predictTarget / 10) + ' in the high nibble: ' + hex2(correct) + '.';
    feedbackColor = 'firebrick';
  } else {
    feedback = 'Not quite. ' + predictTarget + ' in BCD is ' + hex2(correct) + ' (tens digit, then ones digit).';
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

  noStroke();
  fill('black');
  textAlign(CENTER, TOP);
  textSize(24);
  text('BCD Converter', canvasWidth / 2, 10);

  const bin = value;
  const bcd = decToBcd(value);
  const hideBcd = predictMode && !revealed;

  // Big decimal number
  textSize(20);
  textAlign(CENTER, TOP);
  text('Decimal number: ' + value, canvasWidth / 2, 44);

  // Bit rows
  const labelW = canvasWidth < 600 ? 92 : 150;
  const cellW = min(64, (canvasWidth - labelW - margin) / 8);
  const x0 = labelW;
  drawBitRow('Regular binary', bin, x0, 105, cellW, labelW,
    ['128', '64', '32', '16', '8', '4', '2', '1'], false, false);
  drawBitRow('BCD', bcd, x0, 200, cellW, labelW,
    ['80', '40', '20', '10', '8', '4', '2', '1'], true, hideBcd);

  // Nibble captions under the BCD row
  noStroke();
  textAlign(CENTER, TOP);
  textSize(14);
  fill('indigo');
  text(hideBcd ? 'tens digit = ?' : 'tens digit = ' + (bcd >> 4), x0 + cellW * 2, 248);
  fill('darkgreen');
  text(hideBcd ? 'ones digit = ?' : 'ones digit = ' + (bcd & 0x0F), x0 + cellW * 6, 248);

  // Readout panel
  const py = 272;
  fill(255, 255, 255, 230);
  stroke(200);
  rect(10, py, canvasWidth - 20, drawHeight - py - 8, 10);
  noStroke();
  fill('black');
  textAlign(LEFT, TOP);
  textSize(canvasWidth < 600 ? 14 : 16);
  const tw = canvasWidth - 44;
  let y = py + 8;
  text('Binary: ' + bin8(bin) + ' = ' + hex2(bin), 22, y, tw);
  y += 22;
  if (hideBcd) {
    text('BCD: ???? ???? = 0x??', 22, y, tw);
  } else {
    text('BCD: ' + bin8(bcd) + ' = ' + hex2(bcd), 22, y, tw);
  }
  y += 22;

  if (predictMode) {
    fill(feedbackColor);
    text(feedback, 22, y, tw);
  } else if (asIntCheckbox.checked()) {
    fill('firebrick');
    text('Wrong! Reading the BCD byte ' + hex2(bcd) + ' as an integer gives ' + bcd +
      ', not ' + value + '.', 22, y, tw);
    y += canvasWidth < 600 ? 40 : 22;
    fill('black');
    text('Fix: bcd_to_dec(' + hex2(bcd) + ') = (' + hex2(bcd) + ' >> 4) * 10 + (' + hex2(bcd) +
      ' & 0x0F) = ' + (bcd >> 4) + ' * 10 + ' + (bcd & 0x0F) + ' = ' + value, 22, y, tw);
  } else {
    fill('indigo');
    text('dec_to_bcd(' + value + ') = ((' + value + ' // 10) << 4) | (' + value + ' % 10) = (' +
      Math.floor(value / 10) + ' << 4) | ' + (value % 10) + ' = ' + hex2(bcd), 22, y, tw);
    y += canvasWidth < 600 ? 40 : 24;
    fill('darkgreen');
    text('bcd_to_dec(' + hex2(bcd) + ') = (' + hex2(bcd) + ' >> 4) * 10 + (' + hex2(bcd) +
      ' & 0x0F) = ' + value, 22, y, tw);
  }
  if (hexMessage && !predictMode) {
    fill('dimgray');
    textSize(14);
    text(hexMessage, 22, drawHeight - 30, tw);
  }

  // Control labels
  noStroke();
  fill('black');
  textAlign(LEFT, CENTER);
  textSize(defaultTextSize);
  text('Number: ' + value, 10, drawHeight + 18);
  text('BCD byte: 0x', 10, drawHeight + 53);
  text('Answer: 0x', 108, drawHeight + 90);
}

// One row of eight bit lights with weights above each bit
function drawBitRow(label, byteVal, x0, y, cellW, labelW, weights, nibbleShading, hidden) {
  const cellH = 42;
  // Row label
  noStroke();
  fill('black');
  textAlign(LEFT, CENTER);
  textSize(canvasWidth < 600 ? 14 : 17);
  text(label, 10, y + cellH / 2, labelW - 12);

  // Nibble shading behind the cells
  for (let n = 0; n < 2; n++) {
    if (nibbleShading) fill(n === 0 ? 'lavender' : 'honeydew');
    else fill(n === 0 ? 'whitesmoke' : 'gainsboro');
    noStroke();
    rect(x0 + n * 4 * cellW, y - 22, cellW * 4, cellH + 26, 6);
  }

  for (let i = 0; i < 8; i++) {
    const bit = (byteVal >> (7 - i)) & 1;
    const cx = x0 + i * cellW + cellW / 2;
    // weight label
    noStroke();
    fill('dimgray');
    textAlign(CENTER, CENTER);
    textSize(12);
    text(weights[i], cx, y - 11);
    // the light
    stroke('dimgray');
    strokeWeight(1);
    if (hidden) fill('lightgray');
    else if (bit) fill(nibbleShading ? (i < 4 ? 'mediumpurple' : 'mediumseagreen') : 'orange');
    else fill('white');
    const d = min(cellW - 8, cellH - 6);
    circle(cx, y + cellH / 2 + 2, d);
    noStroke();
    fill(hidden ? 'dimgray' : (bit ? 'white' : 'gray'));
    textSize(min(18, d * 0.6));
    text(hidden ? '?' : bit, cx, y + cellH / 2 + 3);
  }
  strokeWeight(1);
}

function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
  numberSlider.size(canvasWidth - sliderLeftMargin - margin);
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) canvasWidth = Math.floor(container.getBoundingClientRect().width);
}
