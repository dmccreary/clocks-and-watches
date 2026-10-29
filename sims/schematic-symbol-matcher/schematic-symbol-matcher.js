// Schematic Symbol Matcher MicroSim
// CANVAS_HEIGHT: 470
// A schematic of the book's first LED circuit: Pico pin GP15 -> 330 ohm
// resistor -> LED -> ground. Click a symbol to reveal its name and a drawing
// of the real part. Match mode shows a part and asks for its symbol.
// "Trace the current" moves a dot from GP15 through each part to ground.

// Canvas dimensions - REQUIRED structure
let canvasWidth = 400;
let drawHeight = 420;
let controlHeight = 50;
let canvasHeight = drawHeight + controlHeight;
let margin = 15;
let defaultTextSize = 16;

const wireY = 120;      // y of the main wire in the schematic
const panelTop = 236;

const parts = [
  { id: 'gpio', name: 'GPIO pin GP15',
    info: 'A general-purpose input/output pin on the Pico. When the program sets GP15 high, the pin supplies 3.3 V.',
    tip: 'Drawn as a box (the chip) with a labeled line for the pin.' },
  { id: 'res', name: 'Resistor (330 Ω)',
    info: 'Limits how much current can flow, so the LED and the Pico pin are not damaged.',
    tip: 'Drawn as a zigzag line. The value is written next to it.' },
  { id: 'led', name: 'LED',
    info: 'A light-emitting diode. Current flows only from the anode (long leg) to the cathode (short leg).',
    tip: 'The triangle points the way current flows; the bar is the cathode. Arrows mean light comes out.' },
  { id: 'gnd', name: 'Ground (GND)',
    info: 'The 0 V return path. Current must get back to ground to complete the circuit.',
    tip: 'Drawn as three stacked lines that get shorter, like an upside-down triangle.' }
];

let revealed = {};          // id -> true once clicked in Explore mode
let selected = null;        // part shown in the info panel
let match = null;           // {target, score, asked, feedback, answered}
let trace = null;           // {start}
let ledLit = false;
let modeButton, traceButton, hideButton;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));

  modeButton = createButton('Match mode');
  modeButton.position(10, drawHeight + 12);
  modeButton.mousePressed(toggleMatch);

  traceButton = createButton('Trace the current');
  traceButton.position(110, drawHeight + 12);
  traceButton.mousePressed(() => { trace = { start: millis() }; ledLit = false; });

  hideButton = createButton('Hide labels');
  hideButton.position(250, drawHeight + 12);
  hideButton.mousePressed(() => { revealed = {}; selected = null; ledLit = false; trace = null; });

  describe('A schematic diagram of an LED circuit: a Pico pin labeled GP15 connects through a zigzag resistor ' +
    'symbol and a triangle-and-bar LED symbol to a ground symbol. Clicking a symbol reveals its name and a drawing ' +
    'of the real part. A Match mode shows a part and asks which symbol it is, and a Trace button moves a dot along ' +
    'the path of the current.', LABEL);
}

// Horizontal positions of each symbol, scaled to the width
function L() {
  const w = canvasWidth;
  const sc = min(1, w / 700);
  return {
    sc,
    chipX: margin, chipW: 90 * sc, pinEnd: margin + 90 * sc + 50 * sc,
    resX1: w * 0.30, resX2: w * 0.30 + 100 * sc,
    ledX1: w * 0.58, ledX2: w * 0.58 + 50 * sc,
    gndX: w - margin - 50 * sc, gndY: wireY + 55
  };
}

function hitBoxes() {
  const g = L();
  return {
    gpio: { x: g.chipX, y: wireY - 50, w: g.pinEnd - g.chipX, h: 100 },
    res: { x: g.resX1 - 6, y: wireY - 30, w: g.resX2 - g.resX1 + 12, h: 60 },
    led: { x: g.ledX1 - 10, y: wireY - 45, w: g.ledX2 - g.ledX1 + 30, h: 80 },
    gnd: { x: g.gndX - 30, y: g.gndY - 12, w: 60, h: 46 }
  };
}

function partAt(mx, my) {
  const hb = hitBoxes();
  for (const p of parts) {
    const b = hb[p.id];
    if (mx >= b.x && mx <= b.x + b.w && my >= b.y && my <= b.y + b.h) return p;
  }
  return null;
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
  textSize(canvasWidth >= 600 ? 22 : 18);
  text('Schematic Symbol Matcher: LED Circuit', canvasWidth / 2, 10);

  const hover = mouseY < drawHeight ? partAt(mouseX, mouseY) : null;
  drawSchematic(hover);
  drawTrace();
  drawPanel();

  noStroke();
  fill('black');
  textAlign(LEFT, CENTER);
  textSize(defaultTextSize);
  if (match) text('Score: ' + match.score + ' / ' + match.asked, 255, drawHeight + 25);
}

function drawSchematic(hover) {
  const g = L();
  const hb = hitBoxes();
  // Hover / selection outlines
  for (const p of parts) {
    const b = hb[p.id];
    if (p === hover || (!match && p === selected)) {
      noFill();
      stroke(p === selected && !match ? 'royalblue' : 'orange');
      strokeWeight(2);
      rect(b.x, b.y, b.w, b.h, 6);
    }
  }

  stroke('black');
  strokeWeight(2.5);
  // Chip body with pin GP15
  fill('white');
  rect(g.chipX, wireY - 40, g.chipW, 80, 4);
  line(g.chipX + g.chipW, wireY, g.pinEnd, wireY);
  noStroke();
  fill('black');
  textAlign(CENTER, CENTER);
  textSize(16 * g.sc + 2);
  text('Pico', g.chipX + g.chipW / 2, wireY);
  textSize(13 * g.sc + 2);
  textAlign(CENTER, BOTTOM);
  text('GP15', (g.chipX + g.chipW + g.pinEnd) / 2, wireY - 4);

  // Wire to the resistor
  stroke('black');
  strokeWeight(2.5);
  line(g.pinEnd, wireY, g.resX1, wireY);
  // Resistor zigzag
  noFill();
  beginShape();
  vertex(g.resX1, wireY);
  const n = 6;
  const step = (g.resX2 - g.resX1) / n;
  for (let i = 0; i < n; i++) vertex(g.resX1 + step * (i + 0.5), wireY + (i % 2 === 0 ? -12 : 12));
  vertex(g.resX2, wireY);
  endShape();
  noStroke();
  fill('black');
  textAlign(CENTER, TOP);
  textSize(13 * g.sc + 2);
  text('330 Ω', (g.resX1 + g.resX2) / 2, wireY + 16);

  // Wire to the LED
  stroke('black');
  strokeWeight(2.5);
  line(g.resX2, wireY, g.ledX1, wireY);
  // LED: triangle pointing right, bar at the tip, two light arrows
  const tH = 34 * g.sc + 6;
  fill(ledLit ? 'red' : 'white');
  triangle(g.ledX1, wireY - tH / 2, g.ledX1, wireY + tH / 2, g.ledX2, wireY);
  line(g.ledX2, wireY - tH / 2, g.ledX2, wireY + tH / 2);
  strokeWeight(2);
  for (const dx of [0, 12]) {
    const ax = g.ledX1 + 14 * g.sc + dx;
    const ay = wireY - tH / 2 - 4;
    line(ax, ay, ax + 12, ay - 14);
    line(ax + 12, ay - 14, ax + 5, ay - 12);
    line(ax + 12, ay - 14, ax + 11, ay - 7);
  }
  if (ledLit) {
    noStroke();
    fill(255, 0, 0, 60);
    circle((g.ledX1 + g.ledX2) / 2, wireY, tH * 2.2);
  }

  // Wire to ground
  stroke('black');
  strokeWeight(2.5);
  line(g.ledX2, wireY, g.gndX, wireY);
  line(g.gndX, wireY, g.gndX, g.gndY);
  line(g.gndX - 22, g.gndY, g.gndX + 22, g.gndY);
  line(g.gndX - 14, g.gndY + 8, g.gndX + 14, g.gndY + 8);
  line(g.gndX - 6, g.gndY + 16, g.gndX + 6, g.gndY + 16);

  // Name tags: "?" until revealed (always "?" in match mode)
  const tags = {
    gpio: [(g.chipX + g.pinEnd) / 2, wireY + 52],
    res: [(g.resX1 + g.resX2) / 2, wireY + 40],
    led: [(g.ledX1 + g.ledX2) / 2, wireY + 40],
    gnd: [g.gndX, g.gndY + 26]
  };
  textSize(canvasWidth >= 600 ? 15 : 12);
  for (const p of parts) {
    const [tx, ty] = tags[p.id];
    const show = !match && revealed[p.id];
    const label = show ? p.name : '?';
    const tw = textWidth(label) + 12;
    const x = constrain(tx - tw / 2, 2, canvasWidth - tw - 2);
    stroke(show ? 'seagreen' : 'gray');
    strokeWeight(1);
    fill(show ? 'honeydew' : 'white');
    rect(x, ty, tw, 22, 5);
    noStroke();
    fill('black');
    textAlign(CENTER, CENTER);
    text(label, x + tw / 2, ty + 11);
  }
}

// Points along the current path: pin -> resistor -> LED -> ground
function tracePath() {
  const g = L();
  return [
    { x: g.chipX + g.chipW, y: wireY, part: 'gpio' },
    { x: g.resX1, y: wireY, part: 'res' },
    { x: g.ledX1, y: wireY, part: 'led' },
    { x: g.ledX2 + 4, y: wireY, part: 'gnd' },
    { x: g.gndX, y: wireY, part: 'gnd' },
    { x: g.gndX, y: g.gndY, part: 'gnd' }
  ];
}

const traceCaptions = {
  gpio: 'GP15 goes high: the pin pushes current out at 3.3 V.',
  res: 'The 330 Ω resistor limits the current to about 4 mA.',
  led: 'Current flows through the LED from anode to cathode, and it lights up.',
  gnd: 'Current returns to ground (0 V), completing the circuit.'
};
let traceCaption = '';

function drawTrace() {
  if (!trace) return;
  const pts = tracePath();
  let total = 0;
  const seg = [];
  for (let i = 0; i < pts.length - 1; i++) {
    const d = dist(pts[i].x, pts[i].y, pts[i + 1].x, pts[i + 1].y);
    seg.push(d);
    total += d;
  }
  const t = constrain((millis() - trace.start) / 4500, 0, 1);
  let along = t * total;
  let p = pts[pts.length - 1];
  let partId = 'gnd';
  for (let i = 0; i < seg.length; i++) {
    if (along <= seg[i]) {
      const f = seg[i] === 0 ? 0 : along / seg[i];
      p = { x: lerp(pts[i].x, pts[i + 1].x, f), y: lerp(pts[i].y, pts[i + 1].y, f) };
      partId = pts[i].part;
      break;
    }
    along -= seg[i];
  }
  // The LED lights once the dot reaches it
  const g = L();
  if (p.x >= g.ledX1 || p.y > wireY) ledLit = true;
  traceCaption = traceCaptions[partId];
  noStroke();
  fill(255, 140, 0, 90);
  circle(p.x, p.y, 24);
  fill('darkorange');
  circle(p.x, p.y, 12);
  if (t >= 1) {
    trace = null;
    traceCaption = 'Current flowed from GP15 through the resistor and LED to ground. Press Trace again to repeat.';
  }
}

function drawPanel() {
  const top = panelTop;
  const h = drawHeight - top - 10;
  stroke('silver');
  strokeWeight(1);
  fill(255, 255, 255, 235);
  rect(margin, top, canvasWidth - 2 * margin, h, 10);

  const picW = min(170, (canvasWidth - 2 * margin) * 0.38);
  const picX = margin + 10;
  const picY = top + 10;
  const tx = picX + picW + 14;
  const tw = canvasWidth - margin - tx - 10;
  const small = canvasWidth < 600;

  let shown = null;
  let heading = '';
  let body = '';
  if (trace || (traceCaption && !match)) {
    heading = 'Trace the current';
    body = traceCaption;
  } else if (match) {
    shown = match.target;
    heading = match.answered ? (match.correct ? 'Correct!' : 'Not quite.') : 'Which symbol is this part?';
    body = match.feedback || 'Click the symbol in the schematic that matches this part.';
  } else if (selected) {
    shown = selected;
    heading = selected.name;
    body = selected.info + '\n' + selected.tip;
  } else {
    heading = 'Click a symbol';
    body = 'Each symbol hides its name. Click one to reveal its name and see the real part it stands for.';
  }

  if (shown) drawPartPicture(shown.id, picX, picY, picW, h - 20);
  const textX = shown ? tx : margin + 14;
  const textW = shown ? tw : canvasWidth - 2 * margin - 28;
  noStroke();
  fill(match && match.answered ? (match.correct ? 'darkgreen' : 'firebrick') : 'darkblue');
  textAlign(LEFT, TOP);
  textStyle(BOLD);
  textSize(small ? 15 : 17);
  text(heading, textX, top + 10, textW, 24);
  textStyle(NORMAL);
  fill('black');
  textSize(small ? 13 : 15);
  text(body, textX, top + 36, textW, h - 44);
}

// Simple drawings of the real parts (stand-ins for photos)
function drawPartPicture(id, x, y, w, h) {
  stroke('gainsboro');
  strokeWeight(1);
  fill('white');
  rect(x, y, w, h, 8);
  const cx = x + w / 2;
  const cy = y + h / 2;
  if (id === 'res') {
    stroke('gray');
    strokeWeight(3);
    line(x + 8, cy, x + w - 8, cy);
    noStroke();
    fill('tan');
    rect(cx - w * 0.28, cy - 12, w * 0.56, 24, 10);
    const bands = ['orange', 'orange', 'saddlebrown', 'goldenrod'];
    bands.forEach((c, i) => {
      fill(c);
      rect(cx - w * 0.2 + i * w * 0.11 + (i === 3 ? w * 0.04 : 0), cy - 12, w * 0.05, 24);
    });
  } else if (id === 'led') {
    stroke('silver');
    strokeWeight(3);
    line(cx - 8, cy + 6, cx - 8, y + h - 8);     // long leg: anode
    line(cx + 8, cy + 6, cx + 8, y + h - 30);    // short leg: cathode
    noStroke();
    fill(220, 20, 60, 220);
    rect(cx - 18, cy - 30, 36, 38, 18, 18, 2, 2);
    fill(200, 0, 40);
    rect(cx - 22, cy + 4, 44, 6, 2);
    fill('black');
    textAlign(CENTER, TOP);
    textSize(11);
    text('+', cx - 18, y + h - 22);
    text('−', cx + 18, y + h - 40);
  } else if (id === 'gpio') {
    noStroke();
    fill('seagreen');
    rect(x + 10, cy - 30, w - 20, 60, 4);
    for (let i = 0; i < 8; i++) {
      const px = x + 22 + i * ((w - 44) / 7);
      fill(i === 4 ? 'orangered' : 'gold');
      circle(px, cy + 20, i === 4 ? 12 : 8);
    }
    fill('white');
    textAlign(CENTER, CENTER);
    textSize(12);
    text('Pico edge pins', cx, cy - 12);
    fill('black');
    textSize(12);
    text('GP15 = pin 20', cx, cy + 42);
  } else if (id === 'gnd') {
    stroke(30);
    strokeWeight(5);
    noFill();
    beginShape();
    vertex(x + 14, cy - 20);
    vertex(cx, cy - 10);
    vertex(x + w - 30, cy + 10);
    endShape();
    noStroke();
    fill(20);
    rect(x + w - 34, cy + 2, 22, 16, 3);
    fill('black');
    textAlign(CENTER, TOP);
    textSize(12);
    text('black wire to a GND pin', cx, cy + 26);
  }
}

function mousePressed() {
  if (mouseY < 0 || mouseY > drawHeight || mouseX < 0 || mouseX > canvasWidth) return;
  const p = partAt(mouseX, mouseY);
  if (!p) return;
  if (!match) {
    revealed[p.id] = true;
    selected = p;
    traceCaption = '';
    return;
  }
  if (match.answered) { nextMatch(); return; }
  match.answered = true;
  match.asked++;
  match.correct = (p === match.target);
  if (match.correct) {
    match.score++;
    match.feedback = 'That is the ' + match.target.name + ' symbol. ' + match.target.tip + ' Click any symbol for the next part.';
  } else {
    match.feedback = 'You clicked the ' + p.name + ' symbol. ' + match.target.tip + ' Click any symbol for the next part.';
  }
}

function nextMatch() {
  let t;
  do { t = random(parts); } while (match && match.target === t);
  match.target = t;
  match.answered = false;
  match.feedback = '';
}

function toggleMatch() {
  trace = null;
  traceCaption = '';
  ledLit = false;
  if (match) {
    match = null;
    modeButton.html('Match mode');
    hideButton.show();
    return;
  }
  match = { target: null, score: 0, asked: 0, answered: false, feedback: '' };
  nextMatch();
  modeButton.html('Explore');
  hideButton.hide();             // the score uses this space in Match mode
}

function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) {
    canvasWidth = container.offsetWidth;
  }
}
