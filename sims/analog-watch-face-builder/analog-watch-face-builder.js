// Analog Watch Face Builder MicroSim
// CANVAS_HEIGHT: 545
// A 360 x 360 round display (like the GC9B72 in the Chrono Smart Clock Kit) with
// tick marks, numerals, and three hands placed with polar geometry.
// On a direct write display the old second hand is erased by drawing it again in
// black. "Erase mode" shows, in yellow, the pixels of other items that the erase
// destroys. The readout uses bounding-circle overlap tests to list needed repairs.

// ---- Layout ----
let canvasWidth = 400;
let drawHeight = 430;
let controlHeight = 115;          // 3 rows x 35 + 10
let canvasHeight = drawHeight + controlHeight;
let margin = 10;
let defaultTextSize = 16;

// ---- Display geometry (in display pixels, 360 x 360) ----
const DISPLAY = 360;
const FACE_C = 180;             // center of the display (named FACE_C so p5's CENTER constant still works)
const SAFE_RADIUS = 168;
const NUMERAL_SIZE = 26;          // text size of the numerals
const NUMERAL_HALF = 14;          // bounding-circle radius of one numeral
const HOUR_LEN = 60;
const HOUR_TICK = 20, MINUTE_TICK = 10;
const TAIL = 18;                  // second hand tail behind the center

const PALETTES = {
  'Classic': { tick: 'white', minorTick: 'gray', numeral: 'white', hands: 'white', second: 'red' },
  'Ocean': { tick: 'paleturquoise', minorTick: 'teal', numeral: 'deepskyblue', hands: 'lightcyan', second: 'orange' },
  'Sunset': { tick: 'gold', minorTick: 'peru', numeral: 'orange', hands: 'lemonchiffon', second: 'magenta' }
};

// ---- Controls ----
let tickSlider, numeralSlider, minuteSlider, secondSlider;
let playButton, stepButton, eraseCheckbox, paletteSelect;

// ---- State ----
let isRunning = false;            // opens paused
let clockSecs = 10 * 3600 + 9 * 60 + 30;   // 10:09:30
let lastTick = 0;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  tickSlider = createSlider(120, 180, 162, 1);
  numeralSlider = createSlider(80, 170, 118, 1);
  minuteSlider = createSlider(40, 170, 92, 1);
  secondSlider = createSlider(40, 175, 138, 1);

  playButton = createButton('Play');
  playButton.mousePressed(togglePlay);
  stepButton = createButton('Step +1 s');
  stepButton.mousePressed(() => { clockSecs += 1; });
  eraseCheckbox = createCheckbox('Erase mode', false);
  paletteSelect = createSelect();
  for (const name of Object.keys(PALETTES)) paletteSelect.option(name);
  paletteSelect.selected('Classic');

  positionControls();

  describe('A round 360 by 360 watch display with tick marks, numerals, and hour, minute, and second hands. ' +
    'Sliders set the tick radius, numeral radius, and hand lengths. Erase mode shows in yellow the parts of ' +
    'other items that are damaged when the old second hand is erased, and a readout lists the repairs needed.');
}

function togglePlay() {
  isRunning = !isRunning;
  playButton.html(isRunning ? 'Pause' : 'Play');
  lastTick = millis();
}

// Two slider columns; labels are drawn in draw()
function sliderGeometry() {
  const colW = canvasWidth / 2;
  const labelW = canvasWidth < 600 ? 98 : 168;
  return { colW, labelW, sliderW: max(40, colW - labelW - 18) };
}

function positionControls() {
  const g = sliderGeometry();
  tickSlider.position(g.labelW, drawHeight + 8);
  numeralSlider.position(g.colW + g.labelW, drawHeight + 8);
  minuteSlider.position(g.labelW, drawHeight + 43);
  secondSlider.position(g.colW + g.labelW, drawHeight + 43);
  for (const s of [tickSlider, numeralSlider, minuteSlider, secondSlider]) s.size(g.sliderW);
  playButton.position(10, drawHeight + 78);
  stepButton.position(70, drawHeight + 78);
  eraseCheckbox.position(160, drawHeight + 80);
  paletteSelect.position(canvasWidth < 600 ? 270 : 300, drawHeight + 79);
}

// ---- Geometry helpers (display pixels; angle in degrees clockwise from 12) ----
function polar(angleDeg, radius) {
  const a = radians(angleDeg);
  return { x: FACE_C + radius * sin(a), y: FACE_C - radius * cos(a) };
}

// Distance from point p to the segment from the center out to radius len at angleDeg
function distToHand(p, angleDeg, len) {
  const e = polar(angleDeg, len);
  const vx = e.x - FACE_C, vy = e.y - FACE_C;
  const t = constrain(((p.x - FACE_C) * vx + (p.y - FACE_C) * vy) / (vx * vx + vy * vy), 0, 1);
  return dist(p.x, p.y, FACE_C + t * vx, FACE_C + t * vy);
}

// The radial interval [r1, r2] of a hand that lies inside a numeral's bounding circle
function chordInside(p, angleDeg, len, r) {
  // Project the numeral center onto the hand's direction
  const a = radians(angleDeg);
  const ux = sin(a), uy = -cos(a);
  const along = (p.x - FACE_C) * ux + (p.y - FACE_C) * uy;
  const perp2 = sq(dist(p.x, p.y, FACE_C, FACE_C)) - along * along;
  if (perp2 > r * r) return null;
  const half = sqrt(r * r - perp2);
  const r1 = max(0, along - half), r2 = min(len, along + half);
  return r2 > r1 ? [r1, r2] : null;
}

// ---- Overlap analysis on bounding circles ----
function analyze(tickOuter, numR, minLen, secLen) {
  const issues = [];
  const numInner = numR - NUMERAL_HALF, numOuter = numR + NUMERAL_HALF;
  if (secLen > numInner) issues.push('Second hand (' + secLen + ') crosses the numerals (inner edge ' + numInner + ')');
  if (minLen > numInner) issues.push('Minute hand (' + minLen + ') crosses the numerals (inner edge ' + numInner + ')');
  if (secLen > tickOuter - MINUTE_TICK) issues.push('Second hand reaches the tick marks (inner edge ' + (tickOuter - MINUTE_TICK) + ')');
  else if (secLen > tickOuter - HOUR_TICK) issues.push('Second hand reaches the hour marks (inner edge ' + (tickOuter - HOUR_TICK) + ')');
  if (minLen > tickOuter - HOUR_TICK) issues.push('Minute hand reaches the tick marks');
  if (numOuter > tickOuter - HOUR_TICK) issues.push('Numerals overlap the hour marks (always, not just on erase)');
  if (tickOuter > SAFE_RADIUS) issues.push('Ticks extend past the safe radius ' + SAFE_RADIUS + ' (hidden by bezel)');
  if (numOuter > SAFE_RADIUS) issues.push('Numerals extend past the safe radius');
  return issues;
}

function draw() {
  updateCanvasSize();

  // Advance the clock one second per real second while playing
  if (isRunning && millis() - lastTick >= 1000) {
    clockSecs += 1;
    lastTick += 1000;
  }

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
  text('Analog Watch Face Builder', canvasWidth / 2, 8);

  const tickOuter = tickSlider.value(), numR = numeralSlider.value();
  const minLen = minuteSlider.value(), secLen = secondSlider.value();
  const pal = PALETTES[paletteSelect.value()];
  const erase = eraseCheckbox.checked();

  // Responsive placement of the round display and the readout panel
  const wide = canvasWidth >= 600;
  let D, dx, dy, px, py, pw, ph;
  if (wide) {
    D = min(drawHeight - 50, canvasWidth * 0.52);
    dx = margin + 5; dy = 40;
    px = dx + D + 15; py = 40; pw = canvasWidth - px - margin; ph = D;
  } else {
    D = min(canvasWidth - 2 * margin, 250);
    dx = (canvasWidth - D) / 2; dy = 36;
    px = margin; py = dy + D + 6; pw = canvasWidth - 2 * margin; ph = drawHeight - py - 6;
  }
  const k = D / DISPLAY;   // screen pixels per display pixel

  push();
  translate(dx, dy);
  scale(k);
  drawFace(tickOuter, numR, minLen, secLen, pal, erase);
  pop();

  const damaged = erase ? damageList(tickOuter, numR, secLen) : [];
  drawReadout(px, py, pw, ph, analyze(tickOuter, numR, minLen, secLen), damaged, erase, wide);

  // Slider labels
  const g = sliderGeometry();
  const short = canvasWidth < 600;
  noStroke();
  fill('black');
  textAlign(LEFT, CENTER);
  textSize(short ? 14 : defaultTextSize);
  text((short ? 'Ticks ' : 'Tick outer: ') + tickOuter, 8, drawHeight + 18);
  text((short ? 'Numerals ' : 'Numeral radius: ') + numR, g.colW + 8, drawHeight + 18);
  text((short ? 'Min hand ' : 'Minute hand: ') + minLen, 8, drawHeight + 53);
  text((short ? 'Sec hand ' : 'Second hand: ') + secLen, g.colW + 8, drawHeight + 53);
}

// Everything inside the round display, in display pixels
function drawFace(tickOuter, numR, minLen, secLen, pal, erase) {
  const s = clockSecs % 60, m = Math.floor(clockSecs / 60) % 60, h = Math.floor(clockSecs / 3600) % 12;
  const secA = s * 6, minA = m * 6 + s * 0.1, hourA = h * 30 + m * 0.5;
  const oldSecA = ((s + 59) % 60) * 6;

  // The glass: a black circle on a dark bezel
  noStroke();
  fill(40);
  rect(0, 0, DISPLAY, DISPLAY, 24);
  fill('black');
  circle(FACE_C, FACE_C, DISPLAY);
  // Faint safe-radius ring
  noFill();
  stroke(70, 90, 120);
  strokeWeight(1.5);
  drawingContext.setLineDash([6, 6]);
  circle(FACE_C, FACE_C, SAFE_RADIUS * 2);
  drawingContext.setLineDash([]);

  // Ticks
  strokeCap(SQUARE);
  for (let i = 0; i < 60; i++) {
    const major = i % 5 === 0;
    const p1 = polar(i * 6, tickOuter), p2 = polar(i * 6, tickOuter - (major ? HOUR_TICK : MINUTE_TICK));
    stroke(major ? pal.tick : pal.minorTick);
    strokeWeight(major ? 4 : 2);
    line(p1.x, p1.y, p2.x, p2.y);
  }
  // Numerals
  noStroke();
  fill(pal.numeral);
  textAlign(CENTER, CENTER);
  textSize(NUMERAL_SIZE);
  for (let n = 1; n <= 12; n++) {
    const p = polar(n * 30, numR);
    text(n, p.x, p.y + 1);
  }

  // Erase mode: draw the OLD second hand in black, then mark what it destroyed in yellow
  if (erase) {
    const e = polar(oldSecA, secLen), t = polar(oldSecA + 180, TAIL);
    stroke('black');
    strokeWeight(5);
    strokeCap(ROUND);
    line(t.x, t.y, e.x, e.y);
    // Damage to the tick mark under the old hand
    const oldS = (s + 59) % 60;
    const inner = tickOuter - (oldS % 5 === 0 ? HOUR_TICK : MINUTE_TICK);
    stroke('yellow');
    strokeWeight(5);
    if (secLen > inner) {
      const a = polar(oldSecA, inner), b = polar(oldSecA, min(secLen, tickOuter));
      line(a.x, a.y, b.x, b.y);
    }
    // Damage to numerals whose bounding circle the old hand passes through
    for (let n = 1; n <= 12; n++) {
      const c = polar(n * 30, numR);
      const chord = chordInside(c, oldSecA, secLen, NUMERAL_HALF);
      if (chord) {
        const a = polar(oldSecA, chord[0]), b = polar(oldSecA, chord[1]);
        stroke('yellow');
        strokeWeight(5);
        line(a.x, a.y, b.x, b.y);
        noFill();
        strokeWeight(2);
        circle(c.x, c.y, NUMERAL_HALF * 2);
      }
    }
  }

  // Hands
  strokeCap(ROUND);
  stroke(pal.hands);
  strokeWeight(8);
  let p = polar(hourA, HOUR_LEN);
  line(FACE_C, FACE_C, p.x, p.y);
  strokeWeight(5);
  p = polar(minA, minLen);
  line(FACE_C, FACE_C, p.x, p.y);
  stroke(pal.second);
  strokeWeight(2.5);
  p = polar(secA, secLen);
  const tail = polar(secA + 180, TAIL);
  line(tail.x, tail.y, p.x, p.y);
  noStroke();
  fill(pal.second);
  circle(FACE_C, FACE_C, 10);
}

// What the erase of the previous second hand position destroyed
function damageList(tickOuter, numR, secLen) {
  const s = clockSecs % 60, oldS = (s + 59) % 60, oldA = oldS * 6;
  const list = [];
  const inner = tickOuter - (oldS % 5 === 0 ? HOUR_TICK : MINUTE_TICK);
  if (secLen > inner) list.push('tick ' + oldS);
  for (let n = 1; n <= 12; n++) {
    if (chordInside(polar(n * 30, numR), oldA, secLen, NUMERAL_HALF)) list.push('numeral ' + n);
  }
  return list;
}

function drawReadout(px, py, pw, ph, issues, damaged, erase, wide) {
  fill(255, 255, 255, 235);
  stroke(200);
  rect(px, py, pw, ph, 10);
  noStroke();
  textAlign(LEFT, TOP);
  let y = py + 10;
  const lineH = wide ? 21 : 17;
  textSize(wide ? 18 : 15);
  if (issues.length === 0) {
    fill('green');
    text('Repairs needed: none', px + 12, y, pw - 24);
    y += lineH + 6;
    fill('black');
    textSize(wide ? 15 : 13);
    text('The hands never reach the numerals or ticks, so erasing a hand never damages them.', px + 12, y, pw - 24);
    y += wide ? 60 : 32;
  } else {
    fill('firebrick');
    text('Repairs needed:', px + 12, y, pw - 24);
    y += lineH + 4;
    textSize(wide ? 14 : 12);
    fill('black');
    for (const msg of issues) {
      text('• ' + msg, px + 12, y, pw - 24);
      y += (wide ? (textWidth(msg) > pw - 40 ? 2 : 1) * 18 : (textWidth(msg) > pw - 40 ? 2 : 1) * 15) + 3;
    }
    y += 6;
  }
  textSize(wide ? 14 : 12);
  if (erase) {
    fill('darkgoldenrod');
    text('Yellow = pixels erased by the old second hand. ' +
      (damaged.length ? 'Redraw: ' + damaged.join(', ') + '.' : 'Nothing damaged this second.'), px + 12, y, pw - 24);
  } else if (wide) {
    fill('dimgray');
    text('Turn on Erase mode, then press Step to see what each erase destroys. The dashed ring is the safe radius (168).',
      px + 12, y, pw - 24);
  }
  // Time readout at the bottom of the panel
  const s = clockSecs % 60, m = Math.floor(clockSecs / 60) % 60, h = Math.floor(clockSecs / 3600) % 24;
  fill('dimgray');
  textSize(13);
  textAlign(RIGHT, BOTTOM);
  text((isRunning ? 'Playing ' : 'Paused ') + nf(h, 2) + ':' + nf(m, 2) + ':' + nf(s, 2), px + pw - 10, py + ph - 6);
}

function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
  positionControls();
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) canvasWidth = Math.floor(container.getBoundingClientRect().width);
}
