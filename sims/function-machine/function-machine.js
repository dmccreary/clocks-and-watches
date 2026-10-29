// Function Machine MicroSim
// CANVAS_HEIGHT: 450
// A function drawn as a machine: argument tokens drop into input chutes named
// after the parameters, the machine works, and the return value comes out the
// output chute. Students can also write their own one-line lambda.

let canvasWidth = 400;
let drawHeight = 335;
let controlHeight = 115;
let canvasHeight = drawHeight + controlHeight;
let margin = 10;
let defaultTextSize = 16;

// Built-in functions from Chapter 4. Each body is a Python expression that the
// small whitelisted evaluator below can run.
const FUNCTIONS = {
  'to_12_hour(hour24)': { name: 'to_12_hour', params: ['hour24'], body: '(hour24 + 11) % 12 + 1', args: ['15'] },
  'split_seconds(total)': { name: 'split_seconds', params: ['total'],
    body: 'total // 3600, total % 3600 // 60, total % 60', args: ['45296'] },
  'add(a, b)': { name: 'add', params: ['a', 'b'], body: 'a + b', args: ['9', '5'] },
  'Write your own (lambda)': { name: 'my_func', params: [], body: '', args: ['7'], custom: true }
};

let fn;                 // the selected function description
let argValues = [];     // parsed argument values for the current run
let result = null;      // the return value (number or tuple)
let errorText = '';
let phase = 'idle';     // idle, in, work, out, done
let phaseFrame = 0;
let gearAngle = 0;

let fnSelect, runButton, argInputs = [], lambdaInput;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));

  fnSelect = createSelect();
  for (const k of Object.keys(FUNCTIONS)) fnSelect.option(k);
  fnSelect.position(10, drawHeight + 8);
  fnSelect.changed(chooseFunction);

  runButton = createButton('Run');
  runButton.position(230, drawHeight + 8);
  runButton.mousePressed(runMachine);

  for (let i = 0; i < 2; i++) {
    const inp = createInput('');
    inp.size(70);
    inp.input(() => { phase = 'idle'; errorText = ''; result = null; });
    argInputs.push(inp);
  }

  lambdaInput = createInput('lambda m: m * 60');
  lambdaInput.position(10, drawHeight + 80);
  lambdaInput.size(min(300, canvasWidth - 30));
  lambdaInput.input(() => { parseLambda(); phase = 'idle'; result = null; positionArgInputs(); });

  chooseFunction();
  describe('A function drawn as a machine. Argument tokens labeled with parameter names enter on the ' +
    'left, the machine runs the return expression, and the return value comes out on the right. ' +
    'Below the machine the Python definition and the call are shown.', LABEL);
}

function chooseFunction() {
  const base = FUNCTIONS[fnSelect.value()];
  fn = { name: base.name, params: base.params.slice(), body: base.body, custom: !!base.custom };
  errorText = '';
  if (fn.custom) {
    lambdaInput.show();
    parseLambda();
  } else {
    lambdaInput.hide();
  }
  for (let i = 0; i < 2; i++) argInputs[i].value(base.args[i] || '');
  if (fn.custom) {
    argInputs[0].value('7');
    argInputs[1].value('3');
  }
  phase = 'idle';
  result = null;
  positionArgInputs();
}

// Read "lambda p: expression" (one or two parameters)
function parseLambda() {
  const m = lambdaInput.value().match(/^\s*lambda\s+([A-Za-z_]\w*)\s*(?:,\s*([A-Za-z_]\w*))?\s*:\s*(.+)$/);
  if (!m) {
    fn.params = [];
    fn.body = '';
    errorText = 'Write it like: lambda m: m * 60   (one or two parameter names, a colon, then one expression)';
    return;
  }
  fn.params = m[2] ? [m[1], m[2]] : [m[1]];
  fn.body = m[3].trim();
  errorText = '';
}

function positionArgInputs() {
  textSize(16);
  let xPos = 10;
  for (let i = 0; i < 2; i++) {
    if (i < fn.params.length) {
      xPos += textWidth(fn.params[i] + ' =') + 8;
      argInputs[i].position(xPos, drawHeight + 44);
      argInputs[i].show();
      xPos += 90;
    } else {
      argInputs[i].hide();
    }
  }
}

function runMachine() {
  errorText = '';
  result = null;
  if (fn.params.length === 0) {
    parseLambda();
    if (errorText) return;
  }
  argValues = [];
  const env = {};
  for (let i = 0; i < fn.params.length; i++) {
    const txt = argInputs[i].value().trim();
    if (!/^-?(\d+\.?\d*|\.\d+)$/.test(txt)) {
      errorText = 'The argument for ' + fn.params[i] + ' must be a number, like 15 or 2.5.';
      phase = 'idle';
      return;
    }
    const val = { v: Number(txt), f: txt.includes('.') };
    argValues.push(val);
    env[fn.params[i]] = val;
  }
  try {
    result = evaluate(fn.body, env);
  } catch (e) {
    errorText = e.message;
    phase = 'idle';
    return;
  }
  phase = 'in';
  phaseFrame = 0;
}

// ---------- whitelisted expression evaluator ----------
// Allowed: numbers, the parameter names, + - * / // %, parentheses, and commas
// (a comma at the top level returns a tuple, like Python). Nothing else runs.
function evaluate(expr, env) {
  if (/[^\w\s.+\-*/%(),]/.test(expr)) {
    throw new Error('Only numbers, parameter names, + - * / // % ( ) and commas are allowed.');
  }
  const tokens = expr.match(/\d+\.?\d*|\.\d+|[A-Za-z_]\w*|\/\/|[-+*/%(),]/g) || [];
  let pos = 0;
  const peek = () => tokens[pos];
  const next = () => tokens[pos++];
  function tuple() {
    const items = [sum()];
    while (peek() === ',') { next(); if (peek() === undefined || peek() === ')') break; items.push(sum()); }
    return items.length > 1 ? items : items[0];
  }
  function sum() {
    let v = term();
    while (peek() === '+' || peek() === '-') v = op(next(), v, term());
    return v;
  }
  function term() {
    let v = unary();
    while (['*', '/', '//', '%'].includes(peek())) v = op(next(), v, unary());
    return v;
  }
  function unary() {
    if (peek() === '-') { next(); const u = unary(); return { v: -u.v, f: u.f }; }
    if (peek() === '+') { next(); return unary(); }
    return atom();
  }
  function atom() {
    const t = next();
    if (t === undefined) throw new Error('The expression ends too soon.');
    if (/^(\d|\.)/.test(t)) return { v: Number(t), f: t.includes('.') };
    if (t === '(') {
      const v = tuple();
      if (next() !== ')') throw new Error('A ( is missing its ).');
      return v;
    }
    if (/^[A-Za-z_]/.test(t)) {
      if (t in env) return env[t];
      throw new Error("NameError: name '" + t + "' is not defined. Use only the parameter names.");
    }
    throw new Error('Unexpected ' + t);
  }
  function op(o, a, b) {
    if (Array.isArray(a) || Array.isArray(b)) throw new Error('TypeError: cannot do math with a tuple.');
    const f = a.f || b.f;
    if ((o === '/' || o === '//' || o === '%') && b.v === 0) throw new Error('ZeroDivisionError: division by zero');
    if (o === '+') return { v: a.v + b.v, f };
    if (o === '-') return { v: a.v - b.v, f };
    if (o === '*') return { v: a.v * b.v, f };
    if (o === '/') return { v: a.v / b.v, f: true };
    if (o === '//') return { v: Math.floor(a.v / b.v), f };
    if (o === '%') return { v: a.v - b.v * Math.floor(a.v / b.v), f };
    throw new Error('Unknown operator ' + o);
  }
  const value = tuple();
  if (pos < tokens.length) throw new Error('SyntaxError near "' + tokens[pos] + '"');
  return value;
}

function fmt(val) {
  if (Array.isArray(val)) return '(' + val.map(fmt).join(', ') + ')';
  if (val.f) {
    if (Number.isInteger(val.v)) return val.v.toFixed(1);
    return String(Math.round(val.v * 1e6) / 1e6);
  }
  return String(val.v);
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
  text('Function Machine', canvasWidth / 2, 8);

  // advance the animation (only after Run is pressed)
  if (phase !== 'idle' && phase !== 'done') {
    phaseFrame++;
    if (phase === 'work') gearAngle += 0.12;
    const len = phase === 'work' ? 35 : 40;
    if (phaseFrame >= len) {
      phaseFrame = 0;
      phase = phase === 'in' ? 'work' : (phase === 'work' ? 'out' : 'done');
    }
  }

  drawMachine();
  drawCodeCard();

  // control labels
  noStroke();
  fill('black');
  textSize(16);
  textAlign(LEFT, CENTER);
  let xPos = 10;
  for (let i = 0; i < fn.params.length; i++) {
    text(fn.params[i] + ' =', xPos, drawHeight + 55);
    xPos += textWidth(fn.params[i] + ' =') + 98;
  }
  if (fn.params.length === 0) {
    fill('gray');
    text('Type a lambda below to get parameters.', 10, drawHeight + 55);
  }
  if (!fn.custom) {
    fill('gray');
    text('Pick "Write your own" to type a lambda.', 10, drawHeight + 92);
  }
}

function drawMachine() {
  const mw = min(220, canvasWidth * 0.3);
  const mh = 120;
  const mx = canvasWidth / 2 - mw / 2;
  const my = 62;
  const nIn = max(1, fn.params.length);

  // input chutes on the left
  for (let i = 0; i < fn.params.length; i++) {
    const cy = my + (i + 1) * mh / (nIn + 1);
    stroke('dimgray');
    strokeWeight(2);
    fill('lightsteelblue');
    rect(mx - 50, cy - 16, 50, 32);
    noStroke();
    fill('black');
    textSize(14);
    textAlign(CENTER, BOTTOM);
    text(fn.params[i], mx - 25, cy - 18);
    // token travels from the left edge into the chute
    const label = (phase === 'idle') ? argInputs[i].value() : fmt(argValues[i]);
    let tx;
    if (phase === 'idle') tx = mx - 90;
    else if (phase === 'in') tx = lerp(mx - 90, mx + 10, ease(phaseFrame / 40));
    else tx = null;   // already inside the machine
    if (tx !== null && label !== '') drawToken(tx, cy, label, 'gold');
  }

  // output chute on the right
  const oy = my + mh / 2;
  stroke('dimgray');
  strokeWeight(2);
  fill('lightsteelblue');
  rect(mx + mw, oy - 16, 50, 32);
  noStroke();
  fill('black');
  textSize(14);
  textAlign(CENTER, BOTTOM);
  text('return', mx + mw + 25, oy - 18);

  // machine body
  stroke('dimgray');
  strokeWeight(3);
  fill(phase === 'work' ? 'moccasin' : 'white');
  rect(mx, my, mw, mh, 12);
  noStroke();
  fill('black');
  textAlign(CENTER, TOP);
  textStyle(BOLD);
  textFont('monospace');
  let ns = 16;
  textSize(ns);
  while (textWidth(fn.name + '()') > mw - 12 && ns > 10) { ns--; textSize(ns); }
  text(fn.name + '()', mx + mw / 2, my + 8);
  textStyle(NORMAL);
  textFont('sans-serif');
  drawGear(mx + mw / 2 - 22, my + 72, 22, gearAngle);
  drawGear(mx + mw / 2 + 20, my + 66, 16, -gearAngle * 1.4);

  // result token
  if ((phase === 'out' || phase === 'done') && result !== null) {
    // keep the whole token on screen, even a wide tuple
    textSize(16);
    textFont('monospace');
    const half = max(40, textWidth(fmt(result)) + 18) / 2;
    textFont('sans-serif');
    const tx = phase === 'out' ? lerp(mx + mw - 10, mx + mw + 110, ease(phaseFrame / 40)) : mx + mw + 110;
    drawToken(min(tx, canvasWidth - half - 6), oy, fmt(result), 'palegreen');
  } else if (phase === 'idle') {
    drawToken(min(mx + mw + 110, canvasWidth - 60), oy, '?', 'white');
  }

  // status line under the machine
  noStroke();
  textSize(16);
  textAlign(CENTER, TOP);
  if (errorText) {
    fill('firebrick');
    text(errorText, margin, my + mh + 12, canvasWidth - 2 * margin);
  } else if (phase === 'idle') {
    fill('dimgray');
    text('Set the arguments and press Run.', canvasWidth / 2, my + mh + 12);
  } else if (phase === 'done') {
    fill('darkgreen');
    text('Returned ' + fmt(result) + (Array.isArray(result) ? ' (a tuple: several values at once)' : ''),
      canvasWidth / 2, my + mh + 12);
  } else {
    fill('darkorange');
    text(phase === 'in' ? 'Arguments go in...' : (phase === 'work' ? 'Running the body...' : 'Return value comes out...'),
      canvasWidth / 2, my + mh + 12);
  }
}

function ease(t) { t = constrain(t, 0, 1); return t * t * (3 - 2 * t); }

function drawToken(x, y, label, c) {
  textSize(16);
  textFont('monospace');
  const w = max(40, textWidth(label) + 18);
  stroke('dimgray');
  strokeWeight(2);
  fill(c);
  rect(x - w / 2, y - 15, w, 30, 15);
  noStroke();
  fill('black');
  textAlign(CENTER, CENTER);
  text(label, x, y + 1);
  textFont('sans-serif');
}

function drawGear(x, y, r, a) {
  push();
  translate(x, y);
  rotate(a);
  stroke('dimgray');
  strokeWeight(1);
  fill('silver');
  for (let i = 0; i < 8; i++) {
    push();
    rotate(i * TWO_PI / 8);
    rect(-3, -r - 5, 6, 8);
    pop();
  }
  circle(0, 0, 2 * r);
  fill('white');
  circle(0, 0, r * 0.6);
  pop();
}

function drawCodeCard() {
  const x = margin, y = 222, w = canvasWidth - 2 * margin, h = drawHeight - 230;
  stroke('silver');
  fill(40);
  rect(x, y, w, h, 8);
  noStroke();
  textFont('monospace');
  textSize(canvasWidth < 500 ? 13 : 15);
  textAlign(LEFT, TOP);
  const lines = [];
  if (fn.custom) {
    lines.push(fn.name + ' = ' + lambdaInput.value().trim());
  } else {
    lines.push('def ' + fn.name + '(' + fn.params.join(', ') + '):');
    lines.push('    return ' + fn.body);
  }
  const callArgs = fn.params.map((p, i) => (phase === 'idle' ? argInputs[i].value() : fmt(argValues[i])));
  let call = fn.name + '(' + callArgs.join(', ') + ')';
  if (phase === 'done' && result !== null) call += '   # returns ' + fmt(result);
  for (let i = 0; i < lines.length; i++) {
    fill(i === 0 ? 'lightskyblue' : 'white');
    text(lines[i], x + 10, y + 10 + i * 22, w - 20);
  }
  fill('khaki');
  text(call, x + 10, y + h - 30, w - 20);
  textFont('sans-serif');
}

// ---------- responsive ----------
function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
  lambdaInput.size(min(300, canvasWidth - 30));
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) canvasWidth = container.offsetWidth;
}
