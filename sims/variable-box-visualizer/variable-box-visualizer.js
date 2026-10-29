// Variable Box Visualizer MicroSim
// CANVAS_HEIGHT: 490
// Step through a short Python program one assignment at a time and watch
// each variable's box change. "Predict first" mode asks the student to type
// the new value before the line runs.

let canvasWidth = 400;
let drawHeight = 410;
let controlHeight = 80;
let canvasHeight = drawHeight + controlHeight;
let margin = 10;
let defaultTextSize = 16;

// Preset programs. Each line is run by the tiny interpreter below.
const PRESETS = {
  'Basic assignments': ['x = 5', 'y = 3', 'x = y', 'y = 10', 'x = x + y'],
  'Counter with +=': ['seconds = 58', 'minutes = 4', 'seconds += 1', 'seconds += 1',
    'seconds %= 60', 'minutes += 1'],
  'Swap with temp': ['a = 7', 'b = 2', 'temp = a', 'a = b', 'b = temp'],
  'Swap the Python way': ['a = 7', 'b = 2', 'a, b = b, a']
};

const FILE_NAMES = {
  'Basic assignments': 'basics.py', 'Counter with +=': 'counter.py',
  'Swap with temp': 'swap_temp.py', 'Swap the Python way': 'swap_python.py'
};

let program = [];       // lines of the current preset
let nextLine = 0;       // index of the line that runs on the next Step
let vars = {};          // name -> value
let order = [];         // variable names in the order they were created
let history = {};       // name -> list of old values
let flash = {};         // name -> frames left to flash
let message = '';
let messageColor = 'black';
let predictRight = 0, predictTotal = 0;

let stepButton, resetButton, presetSelect, predictCheckbox, predictInput;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));

  stepButton = createButton('Step');
  stepButton.position(10, drawHeight + 8);
  stepButton.mousePressed(doStep);

  resetButton = createButton('Reset');
  resetButton.position(65, drawHeight + 8);
  resetButton.mousePressed(resetProgram);

  presetSelect = createSelect();
  for (const name of Object.keys(PRESETS)) presetSelect.option(name);
  presetSelect.position(130, drawHeight + 8);
  presetSelect.changed(resetProgram);

  predictCheckbox = createCheckbox(' Predict first', false);
  predictCheckbox.position(10, drawHeight + 45);
  predictCheckbox.changed(updateMessage);

  predictInput = createInput('');
  predictInput.position(250, drawHeight + 45);
  predictInput.size(70);

  resetProgram();
  describe('A step-through visualizer. A short Python program is listed on one side and a box for ' +
    'each variable on the other. Pressing Step runs the highlighted line and the changed box flashes, ' +
    'with its old value shown crossed out.', LABEL);
}

function resetProgram() {
  program = PRESETS[presetSelect.value()];
  nextLine = 0;
  vars = {}; order = []; history = {}; flash = {};
  predictRight = 0; predictTotal = 0;
  predictInput.value('');
  updateMessage();
}

// Message shown before the next step
function updateMessage() {
  if (nextLine >= program.length) {
    message = 'Program finished. Press Reset or pick another preset.';
    messageColor = 'darkgreen';
  } else if (predictCheckbox.checked()) {
    const target = targetsOf(program[nextLine])[0];
    message = 'Predict: what will ' + target + ' be after line ' + (nextLine + 1) +
      ' runs? Type it in the box, then press Step.';
    messageColor = 'darkblue';
  } else {
    message = 'Press Step to run line ' + (nextLine + 1) + '.';
    messageColor = 'black';
  }
}

function doStep() {
  if (nextLine >= program.length) return;
  const line = program[nextLine];
  const targets = targetsOf(line);
  let guess = null;
  if (predictCheckbox.checked()) {
    guess = predictInput.value().trim();
    if (guess === '') {
      message = 'Type your prediction for ' + targets[0] + ' in the box first.';
      messageColor = 'firebrick';
      return;
    }
  }
  let explanation;
  try {
    explanation = runLine(line);
  } catch (e) {
    message = 'Error on line ' + (nextLine + 1) + ': ' + e.message;
    messageColor = 'firebrick';
    return;
  }
  nextLine++;
  if (guess !== null) {
    predictTotal++;
    const actual = formatValue(vars[targets[0]]);
    if (guess === actual) {
      predictRight++;
      message = 'Correct! ' + targets[0] + ' is ' + actual + '. ' + explanation;
      messageColor = 'darkgreen';
    } else {
      message = 'Not quite: you said ' + guess + ', but ' + targets[0] + ' is ' + actual +
        '. ' + explanation;
      messageColor = 'firebrick';
    }
    predictInput.value('');
  } else {
    message = explanation;
    messageColor = 'black';
  }
  if (nextLine >= program.length) message += '  (Program finished.)';
}

// ---------- tiny interpreter ----------
// Handles: name = expr, name op= expr (op is + - * // %), and a, b = expr, expr
function targetsOf(line) {
  const m = line.match(/^(.*?)(\/\/=|\+=|-=|\*=|%=|=)/);
  return m[1].split(',').map(s => s.trim());
}

function runLine(line) {
  const m = line.match(/^(.*?)(\/\/=|\+=|-=|\*=|%=|=)(.*)$/);
  if (!m) throw new Error('not an assignment');
  const targets = m[1].split(',').map(s => s.trim());
  const op = m[2];
  const rhs = m[3].trim();
  const shown = substitute(rhs);
  let values;
  if (op === '=') {
    const v = evaluate(rhs);
    values = targets.length > 1 ? v : [v];
    if (targets.length > 1 && (!Array.isArray(v) || v.length !== targets.length)) {
      throw new Error('cannot unpack');
    }
  } else {
    const name = targets[0];
    if (!(name in vars)) throw new Error("name '" + name + "' is not defined");
    const right = evaluate(rhs);
    values = [applyOp(op.slice(0, -1), vars[name], right)];
  }
  const before = vars[targets[0]];
  // remember old values, then assign all at once (so a, b = b, a works)
  for (let i = 0; i < targets.length; i++) {
    const name = targets[i];
    if (name in vars) {
      if (vars[name] !== values[i]) history[name].push(vars[name]);
    } else {
      order.push(name);
      history[name] = [];
    }
  }
  for (let i = 0; i < targets.length; i++) {
    vars[targets[i]] = values[i];
    flash[targets[i]] = 50;
  }
  // build a plain-English explanation
  if (op === '=') {
    if (targets.length > 1) {
      return 'The right side (' + shown + ') is built first, then unpacked: ' +
        targets.map((t, i) => t + ' = ' + formatValue(values[i])).join(', ') + '.';
    }
    if (shown === formatValue(values[0])) {
      return targets[0] + ' now refers to ' + formatValue(values[0]) + '.';
    }
    return targets[0] + ' = ' + shown + ' = ' + formatValue(values[0]) + '.';
  }
  const name = targets[0];
  const old = before;
  return name + ' ' + op + ' ' + rhs + ' means ' + name + ' = ' + name + ' ' + op.slice(0, -1) +
    ' ' + rhs + ' = ' + formatValue(old) + ' ' + op.slice(0, -1) + ' ' + shown + ' = ' +
    formatValue(values[0]) + '.';
}

function applyOp(op, a, b) {
  if (op === '+') return a + b;
  if (op === '-') return a - b;
  if (op === '*') return a * b;
  if (op === '//') return Math.floor(a / b);
  if (op === '%') return ((a % b) + b) % b;   // Python modulo is never negative
  throw new Error('unknown operator ' + op);
}

// Replace names with their current values, for the explanation text
function substitute(expr) {
  return expr.replace(/[A-Za-z_]\w*/g, n => (n in vars ? formatValue(vars[n]) : n));
}

// Evaluate an expression of ints, names, + - * // % and parentheses.
// A comma at the top level builds a tuple (returned as an array).
function evaluate(expr) {
  const tokens = expr.match(/\d+|[A-Za-z_]\w*|\/\/|[-+*%(),]/g) || [];
  let pos = 0;
  function peek() { return tokens[pos]; }
  function next() { return tokens[pos++]; }
  function tuple() {
    const items = [sum()];
    while (peek() === ',') { next(); items.push(sum()); }
    return items.length > 1 ? items : items[0];
  }
  function sum() {
    let v = term();
    while (peek() === '+' || peek() === '-') { const op = next(); v = applyOp(op, v, term()); }
    return v;
  }
  function term() {
    let v = unary();
    while (peek() === '*' || peek() === '//' || peek() === '%') {
      const op = next(); v = applyOp(op, v, unary());
    }
    return v;
  }
  function unary() {
    if (peek() === '-') { next(); return -unary(); }
    return atom();
  }
  function atom() {
    const t = next();
    if (t === undefined) throw new Error('incomplete expression');
    if (/^\d+$/.test(t)) return parseInt(t, 10);
    if (t === '(') { const v = tuple(); next(); return v; }
    if (t in vars) return vars[t];
    throw new Error("name '" + t + "' is not defined");
  }
  const result = tuple();
  if (pos < tokens.length) throw new Error('unexpected ' + tokens[pos]);
  return result;
}

function formatValue(v) {
  if (Array.isArray(v)) return '(' + v.join(', ') + ')';
  return String(v);
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
  textSize(24);
  text('Variable Box Visualizer', canvasWidth / 2, 10);

  const wide = canvasWidth >= 600;
  const lineH = 26;
  const codeX = margin;
  const codeY = 48;
  const codeW = wide ? canvasWidth * 0.5 - 1.5 * margin : canvasWidth - 2 * margin;
  const codeH = wide ? 280 : program.length * lineH + 36;
  drawCode(codeX, codeY, codeW, codeH, lineH);

  if (wide) {
    drawBoxes(canvasWidth * 0.5 + margin / 2, codeY, canvasWidth * 0.5 - 1.5 * margin, codeH, true);
  } else {
    drawBoxes(margin, codeY + codeH + 8, canvasWidth - 2 * margin, 330 - (codeY + codeH + 8), false);
  }

  // message panel
  stroke('silver');
  fill('white');
  rect(margin, 336, canvasWidth - 2 * margin, 66, 8);
  noStroke();
  fill(messageColor);
  textSize(16);
  textAlign(LEFT, CENTER);
  text(message, margin + 10, 338, canvasWidth - 2 * margin - 20, 62);

  // control labels
  noStroke();
  fill('black');
  textSize(16);
  textAlign(LEFT, CENTER);
  text('Your prediction:', 130, drawHeight + 56);
  if (predictTotal > 0 && canvasWidth >= 450) {
    text('Right: ' + predictRight + ' / ' + predictTotal, 335, drawHeight + 56);
  }
}

function drawCode(x, y, w, h, lineH) {
  stroke('silver');
  fill(40);
  rect(x, y, w, h, 8);
  noStroke();
  fill('lightgray');
  textSize(14);
  textAlign(LEFT, TOP);
  text(FILE_NAMES[presetSelect.value()], x + 10, y + 7);
  textFont('monospace');
  for (let i = 0; i < program.length; i++) {
    const ly = y + 30 + i * lineH;
    if (i === nextLine) {
      fill('khaki');
      rect(x + 4, ly - 3, w - 8, lineH - 2, 4);
    }
    textSize(16);
    textAlign(LEFT, TOP);
    if (i === nextLine) fill('black');
    else if (i < nextLine) fill('darkgray');
    else fill('white');
    text(String(i + 1).padStart(2, ' ') + '  ' + program[i], x + 12, ly + 1);
    if (i < nextLine) {
      fill('lightgreen');
      textAlign(RIGHT, TOP);
      text('done', x + w - 10, ly + 1);
    } else if (i === nextLine) {
      fill('black');
      textAlign(RIGHT, TOP);
      text('next', x + w - 10, ly + 1);
    }
  }
  textFont('sans-serif');
}

function drawBoxes(x, y, w, h, column) {
  noStroke();
  fill('black');
  textSize(16);
  textAlign(LEFT, TOP);
  if (order.length === 0) {
    fill('gray');
    textAlign(CENTER, CENTER);
    text('No variables yet. Each name gets a box when it is first assigned.', x + 10, y, w - 20, h);
    return;
  }
  const n = order.length;
  // column layout: one box per row; row layout: boxes side by side
  const boxW = column ? min(150, w * 0.45) : min(150, (w - (n - 1) * 10) / n);
  const boxH = column ? min(56, h / n - 34) : min(56, h - 46);
  for (let i = 0; i < n; i++) {
    const name = order[i];
    let bx, by;
    if (column) { bx = x + 10; by = y + 24 + i * (h / n); }
    else { bx = x + i * (boxW + 10); by = y + 22; }
    // name label above the box
    noStroke();
    fill('black');
    textSize(16);
    textAlign(LEFT, BOTTOM);
    textStyle(BOLD);
    text(name, bx, by - 2);
    textStyle(NORMAL);
    // the box itself flashes when its value changes
    const f = flash[name] || 0;
    stroke(f > 0 ? 'darkorange' : 'steelblue');
    strokeWeight(f > 0 ? 4 : 2);
    fill(f > 0 ? 'lightyellow' : 'white');
    rect(bx, by, boxW, boxH, 6);
    strokeWeight(1);
    if (f > 0) flash[name] = f - 1;
    noStroke();
    fill('black');
    textAlign(CENTER, CENTER);
    textSize(24);
    textFont('monospace');
    text(formatValue(vars[name]), bx + boxW / 2, by + boxH / 2);
    textFont('sans-serif');
    // old values, crossed out
    const old = history[name];
    if (old.length > 0) {
      const oldText = 'was ' + old.join(', ');
      textSize(14);
      fill('gray');
      if (column) {
        textAlign(LEFT, CENTER);
        const tx = bx + boxW + 10;
        text(oldText, tx, by + boxH / 2);
        stroke('gray');
        line(tx + textWidth('was '), by + boxH / 2, tx + textWidth(oldText), by + boxH / 2);
      } else {
        textAlign(CENTER, TOP);
        const tx = bx + boxW / 2;
        text(oldText, tx, by + boxH + 4);
        stroke('gray');
        const half = textWidth(oldText) / 2;
        line(tx - half + textWidth('was '), by + boxH + 12, tx + half, by + boxH + 12);
      }
      noStroke();
    }
  }
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
