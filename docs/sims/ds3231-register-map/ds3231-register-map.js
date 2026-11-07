// DS3231 Register Map MicroSim
// CANVAS_HEIGHT: 610
// An interactive list of the DS3231 real-time clock registers 0x00 to 0x12.
// Each row shows the register's byte in hex and binary and what it means when decoded.
// Hover a row for its field name and range; click a row to see its bit fields.
// "Live values" fills the time registers from the browser clock in BCD.
// "Quiz me" shows a raw byte and asks the student to decode it.

// ---- Layout ----
let canvasWidth = 400;
let drawHeight = 560;
let controlHeight = 50;
let canvasHeight = drawHeight + controlHeight;
let margin = 10;
let defaultTextSize = 16;
const ROW_H = 22;
const TABLE_TOP = 86;

// ---- Controls ----
let liveCheckbox, quizButton, answerInput, checkButton;

// ---- State ----
let selected = -1;     // index of the clicked row
let hovered = -1;      // index of the row under the mouse
let quiz = null;       // { index, value, answer } while a quiz question is open
let quizFeedback = '';
let quizColor = 'black';
let tableRight = 0;    // x where the table ends (for the side panel)
let wideLayout = true;
let panelRect = null;  // where the bit panel is drawn (clicks there close it)

const GROUPS = {
  time: { name: 'Time', color: 'powderblue', band: 'steelblue' },
  alarm: { name: 'Alarms', color: 'moccasin', band: 'darkorange' },
  control: { name: 'Control', color: 'thistle', band: 'mediumorchid' },
  temp: { name: 'Temperature', color: 'mistyrose', band: 'indianred' }
};

const DAY_NAMES = ['', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const MONTH_NAMES = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July',
  'August', 'September', 'October', 'November', 'December'];

function bcd(b) { return (b >> 4) * 10 + (b & 0x0F); }
function toBcd(d) { return (Math.floor(d / 10) << 4) | (d % 10); }
function hex2(n) { return '0x' + n.toString(16).toUpperCase().padStart(2, '0'); }
function bin8(n) { const s = n.toString(2).padStart(8, '0'); return s.slice(0, 4) + ' ' + s.slice(4); }
function signed8(n) { return n & 0x80 ? n - 256 : n; }
function pad2(n) { return String(n).padStart(2, '0'); }

function hoursText(v) {
  if (v & 0x40) {                       // bit 6 set = 12-hour mode
    return bcd(v & 0x1F) + (v & 0x20 ? ' PM' : ' AM') + ' (12 h mode)';
  }
  return bcd(v & 0x3F) + ' h (24 h mode)';
}

// Register table: fields are [high bit, low bit, name]
const REGS = [
  { addr: 0x00, name: 'Seconds', group: 'time', range: '00 to 59 (BCD)', value: 0x30,
    fields: [[7, 7, '0'], [6, 4, '10 Seconds'], [3, 0, 'Seconds']],
    decode: v => bcd(v & 0x7F) + ' s',
    info: 'The seconds count. The high nibble holds the tens digit and the low nibble holds the ones digit.' },
  { addr: 0x01, name: 'Minutes', group: 'time', range: '00 to 59 (BCD)', value: 0x05,
    fields: [[7, 7, '0'], [6, 4, '10 Minutes'], [3, 0, 'Minutes']],
    decode: v => bcd(v & 0x7F) + ' min',
    info: 'The minutes count, stored in BCD just like the seconds.' },
  { addr: 0x02, name: 'Hours', group: 'time', range: '00 to 23, or 1 to 12 with AM/PM', value: 0x14,
    fields: [[7, 7, '0'], [6, 6, '12/24 select'], [5, 5, '20 Hour / PM'], [4, 4, '10 Hour'], [3, 0, 'Hour']],
    decode: hoursText,
    info: 'Bit 6 selects 12-hour mode. In 24-hour mode bit 5 is the 20-hour digit, so mask with & 0x3F before decoding.' },
  { addr: 0x03, name: 'Day of week', group: 'time', range: '1 to 7', value: 0x01,
    fields: [[7, 3, '0'], [2, 0, 'Day']],
    decode: v => (v & 7) + ' = ' + (DAY_NAMES[v & 7] || '?'),
    info: 'A plain counter from 1 to 7. The chip does not care which day is 1; this book uses Monday = 1.' },
  { addr: 0x04, name: 'Date', group: 'time', range: '01 to 31 (BCD)', value: 0x28,
    fields: [[7, 6, '0'], [5, 4, '10 Date'], [3, 0, 'Date']],
    decode: v => 'day ' + bcd(v & 0x3F),
    info: 'The day of the month in BCD. The chip knows how many days each month has, including leap years.' },
  { addr: 0x05, name: 'Month / Century', group: 'time', range: '01 to 12 (BCD) + century bit', value: 0x09,
    fields: [[7, 7, 'Century'], [6, 5, '0'], [4, 4, '10 Month'], [3, 0, 'Month']],
    decode: v => bcd(v & 0x1F) + ' = ' + (MONTH_NAMES[bcd(v & 0x1F)] || '?'),
    info: 'The month in BCD. Bit 7 flips when the year rolls over from 99 to 00, so mask with & 0x1F.' },
  { addr: 0x06, name: 'Year', group: 'time', range: '00 to 99 (BCD)', value: 0x26,
    fields: [[7, 4, '10 Year'], [3, 0, 'Year']],
    decode: v => String(2000 + bcd(v)),
    info: 'The last two digits of the year in BCD. Add 2000 to get the full year.' },
  { addr: 0x07, name: 'Alarm 1 Seconds', group: 'alarm', range: '00 to 59 + mask bit', value: 0x00,
    fields: [[7, 7, 'A1M1 mask'], [6, 4, '10 Seconds'], [3, 0, 'Seconds']],
    decode: v => ':' + pad2(bcd(v & 0x7F)) + (v & 0x80 ? ' (ignored)' : ''),
    info: 'Alarm 1 fires when the seconds match this value. Setting the mask bit (bit 7) means "any second".' },
  { addr: 0x08, name: 'Alarm 1 Minutes', group: 'alarm', range: '00 to 59 + mask bit', value: 0x30,
    fields: [[7, 7, 'A1M2 mask'], [6, 4, '10 Minutes'], [3, 0, 'Minutes']],
    decode: v => pad2(bcd(v & 0x7F)) + ' min' + (v & 0x80 ? ' (ignored)' : ''),
    info: 'The minutes Alarm 1 must match. Same BCD layout as the minutes register plus a mask bit.' },
  { addr: 0x09, name: 'Alarm 1 Hours', group: 'alarm', range: 'hours + mask bit', value: 0x07,
    fields: [[7, 7, 'A1M3 mask'], [6, 6, '12/24 select'], [5, 5, '20 Hour / PM'], [4, 4, '10 Hour'], [3, 0, 'Hour']],
    decode: v => hoursText(v & 0x7F).replace(' (24 h mode)', '') + (v & 0x80 ? ' (ignored)' : ''),
    info: 'The hour Alarm 1 must match. Here the alarm is set for 07:30:00.' },
  { addr: 0x0A, name: 'Alarm 1 Day/Date', group: 'alarm', range: 'day or date + mask bit', value: 0x80,
    fields: [[7, 7, 'A1M4 mask'], [6, 6, 'DY/DT'], [5, 4, '10 Date'], [3, 0, 'Day or Date']],
    decode: v => (v & 0x80 ? 'every day' : (v & 0x40 ? 'day ' + (v & 0x0F) : 'date ' + bcd(v & 0x3F))),
    info: 'Mask bit set means the alarm ignores the day, so it fires every day. DY/DT chooses day of week or date.' },
  { addr: 0x0B, name: 'Alarm 2 Minutes', group: 'alarm', range: '00 to 59 + mask bit', value: 0x80,
    fields: [[7, 7, 'A2M2 mask'], [6, 4, '10 Minutes'], [3, 0, 'Minutes']],
    decode: v => (v & 0x80 ? 'any minute' : pad2(bcd(v & 0x7F)) + ' min'),
    info: 'Alarm 2 has no seconds register; it always fires at second 00. With all mask bits set it fires once a minute.' },
  { addr: 0x0C, name: 'Alarm 2 Hours', group: 'alarm', range: 'hours + mask bit', value: 0x80,
    fields: [[7, 7, 'A2M3 mask'], [6, 6, '12/24 select'], [5, 5, '20 Hour / PM'], [4, 4, '10 Hour'], [3, 0, 'Hour']],
    decode: v => (v & 0x80 ? 'any hour' : hoursText(v)),
    info: 'The hour Alarm 2 must match, with the same layout as the Hours register plus a mask bit.' },
  { addr: 0x0D, name: 'Alarm 2 Day/Date', group: 'alarm', range: 'day or date + mask bit', value: 0x80,
    fields: [[7, 7, 'A2M4 mask'], [6, 6, 'DY/DT'], [5, 4, '10 Date'], [3, 0, 'Day or Date']],
    decode: v => (v & 0x80 ? 'every day' : (v & 0x40 ? 'day ' + (v & 0x0F) : 'date ' + bcd(v & 0x3F))),
    info: 'Day or date for Alarm 2. Mask bit set means "any day".' },
  { addr: 0x0E, name: 'Control', group: 'control', range: '8 on/off flags', value: 0x1C,
    fields: [[7, 7, 'EOSC'], [6, 6, 'BBSQW'], [5, 5, 'CONV'], [4, 4, 'RS2'], [3, 3, 'RS1'], [2, 2, 'INTCN'], [1, 1, 'A2IE'], [0, 0, 'A1IE']],
    decode: v => (v & 0x04 ? 'INT pin mode' : 'square wave') + (v & 0x80 ? ', osc off' : ''),
    info: 'Each bit is a switch. INTCN = 1 makes the SQW pin an alarm interrupt; A1IE and A2IE enable the alarms; EOSC = 1 stops the clock on battery.' },
  { addr: 0x0F, name: 'Status', group: 'control', range: '8 on/off flags', value: 0x88,
    fields: [[7, 7, 'OSF'], [6, 4, '0'], [3, 3, 'EN32kHz'], [2, 2, 'BSY'], [1, 1, 'A2F'], [0, 0, 'A1F']],
    decode: v => (v & 0x80 ? 'osc stopped once' : 'osc OK') + (v & 0x03 ? ', alarm fired' : ''),
    info: 'OSF = 1 means the oscillator stopped at some point (for example, the battery was removed), so the time may be wrong. A1F and A2F are set when an alarm fires.' },
  { addr: 0x10, name: 'Aging Offset', group: 'control', range: '-128 to 127 (signed)', value: 0x00,
    fields: [[7, 7, 'Sign'], [6, 0, 'Data']],
    decode: v => signed8(v) + ' (trim)',
    info: 'A signed trim value for calibration. Positive values slow the oscillator slightly, negative values speed it up.' },
  { addr: 0x11, name: 'Temperature MSB', group: 'temp', range: '-128 to 127 °C (signed)', value: 0x19,
    fields: [[7, 7, 'Sign'], [6, 0, 'Whole degrees']],
    decode: v => signed8(v) + ' °C',
    info: 'The whole-degree part of the chip temperature, as a signed (two\'s complement) number, not BCD.' },
  { addr: 0x12, name: 'Temperature LSB', group: 'temp', range: '0, 0.25, 0.5, 0.75 °C', value: 0x40,
    fields: [[7, 6, 'Quarter degrees'], [5, 0, '0']],
    decode: v => '+' + ((v >> 6) * 0.25).toFixed(2) + ' °C',
    info: 'The top two bits add 0.25 °C steps. Temperature = MSB + (LSB >> 6) * 0.25. With 0x19 and 0x40 that is 25.25 °C.' }
];

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  liveCheckbox = createCheckbox('Live values', false);
  liveCheckbox.position(10, drawHeight + 15);

  quizButton = createButton('Quiz me');
  quizButton.position(125, drawHeight + 12);
  quizButton.mousePressed(newQuiz);

  answerInput = createInput('');
  answerInput.position(205, drawHeight + 12);
  answerInput.size(60);
  answerInput.attribute('placeholder', 'answer');

  checkButton = createButton('Check');
  checkButton.position(285, drawHeight + 12);
  checkButton.mousePressed(checkQuiz);

  describe('A table of the DS3231 real-time clock registers 0x00 to 0x12, color-coded into time, alarm, ' +
    'control, and temperature groups. Each row shows the byte in hex and binary and its decoded meaning. ' +
    'Clicking a row shows the bit fields of that register.');
}

// Fill the time registers from the browser clock, encoded in BCD
function fillLiveValues() {
  const d = new Date();
  REGS[0].value = toBcd(d.getSeconds());
  REGS[1].value = toBcd(d.getMinutes());
  REGS[2].value = toBcd(d.getHours());
  REGS[3].value = ((d.getDay() + 6) % 7) + 1;          // Monday = 1 ... Sunday = 7
  REGS[4].value = toBcd(d.getDate());
  REGS[5].value = toBcd(d.getMonth() + 1);
  REGS[6].value = toBcd(d.getFullYear() % 100);
}

function newQuiz() {
  const ranges = [[0, 59], [0, 59], [0, 23], null, [1, 31], [1, 12], [0, 99]];
  let index = floor(random(7));
  if (index === 3) index = 0;                           // day of week is not BCD
  const r = ranges[index];
  const answer = floor(random(r[0] + 10, r[1] + 1));    // two-digit values are more interesting
  quiz = { index, value: toBcd(answer), answer };
  quizFeedback = '';
  answerInput.value('');
  selected = -1;
}

function checkQuiz() {
  if (!quiz) {
    quizFeedback = 'Press Quiz me first.';
    quizColor = 'black';
    return;
  }
  const guess = parseInt(answerInput.value().trim(), 10);
  if (isNaN(guess)) {
    quizFeedback = 'Type the decoded decimal value, such as 45.';
    quizColor = 'firebrick';
    return;
  }
  const v = quiz.value;
  if (guess === quiz.answer) {
    quizFeedback = 'Correct! ' + hex2(v) + ' = ' + (v >> 4) + ' x 10 + ' + (v & 0x0F) + ' = ' + quiz.answer + '. Press Quiz me for another.';
    quizColor = 'green';
  } else if (guess === v) {
    quizFeedback = 'That is the byte read as an integer (' + v + '). Decode BCD: ' + (v >> 4) + ' x 10 + ' + (v & 0x0F) + ' = ' + quiz.answer + '.';
    quizColor = 'firebrick';
  } else {
    quizFeedback = 'Not quite. High nibble ' + (v >> 4) + ' is the tens digit, low nibble ' + (v & 0x0F) + ' is the ones: ' + quiz.answer + '.';
    quizColor = 'firebrick';
  }
}

function valueOf(i) {
  if (quiz && quiz.index === i) return quiz.value;
  return REGS[i].value;
}

function draw() {
  updateCanvasSize();
  if (liveCheckbox.checked()) fillLiveValues();

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
  text('DS3231 Register Map', canvasWidth / 2, 8);

  wideLayout = canvasWidth >= 640;
  drawLegend();
  drawTable();
  if (selected >= 0) drawBitPanel(selected);
  else {
    panelRect = null;
    if (wideLayout) drawPanelHint();
  }
  drawStatus();
}

function drawLegend() {
  const keys = Object.keys(GROUPS);
  textSize(14);
  textAlign(LEFT, CENTER);
  let x = margin;
  const y = 46;
  for (const k of keys) {
    fill(GROUPS[k].color);
    stroke(GROUPS[k].band);
    rect(x, y - 8, 16, 16, 3);
    noStroke();
    fill('black');
    text(GROUPS[k].name, x + 22, y);
    x += textWidth(GROUPS[k].name) + 44;
  }
}

// Column layout depends on width: wide shows binary, narrow compresses to two columns
function columns() {
  if (wideLayout) {
    return { addr: margin + 14, name: margin + 58, hex: margin + 196, bin: margin + 244, mean: margin + 334, right: margin + 470 };
  }
  return { addr: margin + 14, name: margin + 58, hex: canvasWidth - 170, bin: -1, mean: canvasWidth - 122, right: canvasWidth - margin };
}

function drawTable() {
  const c = columns();
  tableRight = c.right;
  const narrowFont = !wideLayout && canvasWidth < 460;

  // Header
  noStroke();
  fill('black');
  textAlign(LEFT, CENTER);
  textSize(13);
  textStyle(BOLD);
  text('Addr', c.addr, TABLE_TOP - 12);
  text('Field', c.name, TABLE_TOP - 12);
  text('Hex', c.hex, TABLE_TOP - 12);
  if (c.bin > 0) text('Binary', c.bin, TABLE_TOP - 12);
  text('Meaning', c.mean, TABLE_TOP - 12);
  textStyle(NORMAL);

  hovered = -1;
  for (let i = 0; i < REGS.length; i++) {
    const r = REGS[i];
    const g = GROUPS[r.group];
    const y = TABLE_TOP + i * ROW_H;
    const inPanel = panelRect && mouseX > panelRect.x && mouseX < panelRect.x + panelRect.w &&
      mouseY > panelRect.y && mouseY < panelRect.y + panelRect.h;
    const over = !inPanel && mouseX > margin && mouseX < c.right && mouseY > y && mouseY < y + ROW_H;
    if (over) hovered = i;
    const isQuiz = quiz && quiz.index === i;

    // Row background and group band
    stroke('white');
    fill(i === selected ? 'gold' : (over ? 'lightyellow' : g.color));
    rect(margin, y, c.right - margin, ROW_H);
    noStroke();
    fill(g.band);
    rect(margin, y, 8, ROW_H);

    const v = valueOf(i);
    fill('black');
    textSize(narrowFont ? 12 : 14);
    textAlign(LEFT, CENTER);
    text(hex2(r.addr), c.addr, y + ROW_H / 2);
    text(r.name, c.name, y + ROW_H / 2);
    textStyle(BOLD);
    fill(isQuiz ? 'crimson' : 'black');
    text(hex2(v), c.hex, y + ROW_H / 2);
    textStyle(NORMAL);
    fill('black');
    if (c.bin > 0) text(bin8(v), c.bin, y + ROW_H / 2);
    fill(isQuiz ? 'crimson' : 'dimgray');
    let meaning = isQuiz ? '?? decode it!' : r.decode(v);
    while (meaning.length > 3 && textWidth(meaning) > c.right - c.mean - 4) meaning = meaning.slice(0, -2) + '…';
    text(meaning, c.mean, y + ROW_H / 2);
  }
  cursor(hovered >= 0 ? HAND : ARROW);
}

function drawPanelHint() {
  const px = tableRight + 12, pw = canvasWidth - px - margin;
  fill(255, 255, 255, 230);
  stroke(200);
  rect(px, TABLE_TOP - 22, pw, 150, 10);
  noStroke();
  fill('dimgray');
  textSize(15);
  textAlign(LEFT, TOP);
  text('Click any row to see what each of its 8 bits means.\n\nThe colored band on the left of each row shows its group.',
    px + 12, TABLE_TOP - 10, pw - 24);
}

// Bit-field panel: right side when wide, an overlay over the lower table when narrow
function drawBitPanel(i) {
  const r = REGS[i];
  const v = valueOf(i);
  let px, py, pw, ph;
  if (wideLayout) {
    px = tableRight + 12; py = TABLE_TOP - 22; pw = canvasWidth - px - margin; ph = 19 * ROW_H + 22;
  } else {
    px = margin; pw = canvasWidth - 2 * margin; ph = 250;
    py = i < 10 ? TABLE_TOP + 10 * ROW_H + 4 : TABLE_TOP + 2;   // keep the clicked row visible
  }
  panelRect = { x: px, y: py, w: pw, h: ph };
  fill(255, 255, 255);
  stroke('gray');
  rect(px, py, pw, ph, 10);
  noStroke();
  fill('black');
  textAlign(LEFT, TOP);
  textSize(17);
  textStyle(BOLD);
  text(hex2(r.addr) + '  ' + r.name, px + 12, py + 10, pw - 24);
  textStyle(NORMAL);

  // Eight bit boxes, MSB on the left, shaded by field
  const boxW = min(36, (pw - 24) / 8);
  const bx = px + 12, by = py + 38;
  for (let b = 7; b >= 0; b--) {
    const fieldIndex = r.fields.findIndex(f => b <= f[0] && b >= f[1]);
    const x = bx + (7 - b) * boxW;
    stroke('gray');
    fill(fieldIndex % 2 === 0 ? 'lavender' : 'honeydew');
    rect(x, by, boxW, 28);
    noStroke();
    fill('black');
    textAlign(CENTER, CENTER);
    textSize(16);
    text((v >> b) & 1, x + boxW / 2, by + 14);
    fill('dimgray');
    textSize(11);
    text('b' + b, x + boxW / 2, by + 38);
  }

  // Field list
  textAlign(LEFT, TOP);
  textSize(14);
  let y = by + 50;
  for (let k = 0; k < r.fields.length; k++) {
    const [hi, lo, name] = r.fields[k];
    const width = hi - lo + 1;
    const fv = (v >> lo) & ((1 << width) - 1);
    const bits = fv.toString(2).padStart(width, '0');
    const label = (hi === lo ? 'bit ' + hi : 'bits ' + hi + '-' + lo) + '  ' + name + ' = ' + bits + (width > 1 ? ' = ' + fv : '');
    fill(k % 2 === 0 ? 'indigo' : 'darkgreen');
    text(label, px + 12, y, pw - 24);
    y += 20;
  }
  y += 6;
  fill('black');
  text('Decoded: ' + r.decode(v), px + 12, y, pw - 24);
  y += 26;
  fill('dimgray');
  text(r.info, px + 12, y, pw - 24);
}

function drawStatus() {
  const y0 = TABLE_TOP + REGS.length * ROW_H + 8;
  textAlign(LEFT, TOP);
  textSize(14);
  noStroke();
  fill('black');
  if (hovered >= 0) {
    const r = REGS[hovered];
    text(hex2(r.addr) + ' ' + r.name + ': range ' + r.range + '. Click for bit details.', margin, y0, canvasWidth - 2 * margin);
  } else {
    fill('dimgray');
    text('Hover a row to see its field and range. Click a row for its bits.', margin, y0, canvasWidth - 2 * margin);
  }
  if (quiz) {
    const r = REGS[quiz.index];
    const prompt = 'Quiz: register ' + hex2(r.addr) + ' (' + r.name + ') holds ' + hex2(quiz.value) + '. What decimal value is that?';
    fill(quizFeedback ? quizColor : 'crimson');
    text(quizFeedback ? quizFeedback : prompt, margin, y0 + 22, canvasWidth - 2 * margin);
  } else if (quizFeedback) {
    fill(quizColor);
    text(quizFeedback, margin, y0 + 22, canvasWidth - 2 * margin);
  }
}

// Which register row is at (mx, my)? -1 if none (or if the bit panel covers that point)
function rowAt(mx, my) {
  if (panelRect && mx > panelRect.x && mx < panelRect.x + panelRect.w &&
    my > panelRect.y && my < panelRect.y + panelRect.h) return -1;
  if (mx < margin || mx > columns().right) return -1;
  const i = Math.floor((my - TABLE_TOP) / ROW_H);
  return (my >= TABLE_TOP && i >= 0 && i < REGS.length) ? i : -1;
}

function mousePressed() {
  if (mouseY < 0 || mouseY > drawHeight || mouseX < 0 || mouseX > canvasWidth) return;
  const row = rowAt(mouseX, mouseY);
  if (row >= 0) {
    selected = (selected === row) ? -1 : row;
  } else if (selected >= 0) {
    selected = -1;   // click anywhere else closes the bit panel
  }
}

function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) canvasWidth = Math.floor(container.getBoundingClientRect().width);
}
