// Tilt and Step Explorer MicroSim
// CANVAS_HEIGHT: 545
// Left: drag a 3D watch to tilt it and watch gravity move between the x, y and z axes.
// Right: a plot of acceleration magnitude |a| from a simulated walk, with a step threshold
// and a minimum time between steps. Steps are counted on upward threshold crossings.
// Opens paused with 5 seconds of walking data already captured; press Walk to keep walking.

let canvasWidth = 400;
let drawHeight = 430;
let controlHeight = 115;
let canvasHeight = drawHeight + controlHeight;
let margin = 25;
let sliderLeftMargin = 290;
let defaultTextSize = 16;

let walkButton, resetButton, thresholdSlider, gapSlider;
let isWalking = false;

// Watch orientation (degrees)
let pitch = 0;   // rotation about the x axis
let roll = 0;    // rotation about the y axis
let dragging = false;

// Accelerometer samples (50 per second)
const RATE = 50;
const WINDOW = 5 * RATE;
let mag = [];        // |a| in g
let trueStep = [];   // true when a real footstep starts at this sample
let simT = 0;        // simulated time in seconds
let nextStepT = 0.3;
let pending = [];    // scheduled bumps: {t, amp, width}

// Layout rectangles, recomputed each frame
let leftPanel, rightPanel;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));

  walkButton = createButton('Walk');
  walkButton.position(10, drawHeight + 6);
  walkButton.mousePressed(toggleWalk);

  resetButton = createButton('Reset');
  resetButton.position(75, drawHeight + 6);
  resetButton.mousePressed(resetAll);

  thresholdSlider = createSlider(1.0, 2.0, 1.2, 0.01);
  thresholdSlider.position(sliderLeftMargin, drawHeight + 43);
  thresholdSlider.size(canvasWidth - sliderLeftMargin - margin);

  gapSlider = createSlider(0, 600, 250, 10);
  gapSlider.position(sliderLeftMargin, drawHeight + 78);
  gapSlider.size(canvasWidth - sliderLeftMargin - margin);

  resetAll();

  describe('Left panel: a smartwatch that can be dragged to tilt, with bars for the x, y and z acceleration in g and a tilt label such as Face up or Wrist raised. Right panel: a plot of acceleration magnitude during a simulated walk, a dashed threshold line, and orange markers where steps are counted, compared with the real number of steps.');
}

function resetAll() {
  randomSeed(7);
  mag = [];
  trueStep = [];
  pending = [];
  simT = 0;
  nextStepT = 0.3;
  pitch = 0;
  roll = 0;
  // capture 5 seconds of walking so the first frame already shows a signal
  for (let i = 0; i < WINDOW; i++) addSample();
  isWalking = false;
  walkButton.html('Walk');
}

function toggleWalk() {
  isWalking = !isWalking;
  walkButton.html(isWalking ? 'Stop' : 'Walk');
}

// Simulated walking signal: each footstep is a main bump plus a smaller second bump
function addSample() {
  let isStep = false;
  if (simT >= nextStepT) {
    const a = random(0.25, 0.55);
    pending.push({ t: nextStepT + 0.06, amp: a, width: 0.045 });
    pending.push({ t: nextStepT + 0.19, amp: a * random(0.45, 0.75), width: 0.035 });
    nextStepT += random(0.47, 0.56);
    isStep = true;
  }
  let v = 1 + randomGaussian(0, 0.035);
  for (const b of pending) {
    const d = (simT - b.t) / b.width;
    v += b.amp * Math.exp(-0.5 * d * d);
  }
  pending = pending.filter(b => simT - b.t < 0.3);
  mag.push(v);
  trueStep.push(isStep);
  if (mag.length > WINDOW) {
    mag.shift();
    trueStep.shift();
  }
  simT += 1 / RATE;
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
  textSize(22);
  text('Tilt and Step Explorer', canvasWidth / 2, 8);

  if (isWalking) addSample();

  // Side by side on wide screens, stacked below 600 px
  if (canvasWidth >= 600) {
    const split = floor(canvasWidth * 0.42);
    leftPanel = { x: 8, y: 40, w: split - 12, h: drawHeight - 50 };
    rightPanel = { x: split + 4, y: 40, w: canvasWidth - split - 12, h: drawHeight - 50 };
  } else {
    leftPanel = { x: 8, y: 38, w: canvasWidth - 16, h: 180 };
    rightPanel = { x: 8, y: 224, w: canvasWidth - 16, h: drawHeight - 232 };
  }

  const acc = gravityVector();
  drawTiltPanel(leftPanel, acc);
  drawStepPanel(rightPanel);

  // control labels
  noStroke();
  fill('black');
  textAlign(LEFT, CENTER);
  textSize(defaultTextSize);
  text('Drag the watch to tilt it.', 140, drawHeight + 18);
  text('Step threshold: ' + nf(thresholdSlider.value(), 1, 2) + ' g', 10, drawHeight + 53);
  text('Min time between steps: ' + gapSlider.value() + ' ms', 10, drawHeight + 88);
}

// Accelerometer reading for a still watch: gravity seen in the sensor's own axes.
// The sensor is mounted turned half a circle, so its x axis points to 9 o'clock,
// its y axis to 6 o'clock and its z axis out of the screen. With this mounting a
// raised wrist (screen tipped toward your eyes) gives a negative y reading, which
// matches the wrist_raised() rule in the chapter.
function gravityVector() {
  const th = radians(pitch);
  const ph = radians(roll);
  return {
    x: sin(ph) * cos(th),
    y: -sin(th),
    z: cos(th) * cos(ph)
  };
}

function tiltLabel(a) {
  if (a.y < -0.5 && abs(a.z) < 0.6) return ['Wrist raised: wake the screen', 'seagreen'];
  if (a.z > 0.8) return ['Face up (flat)', 'steelblue'];
  if (a.z < -0.8) return ['Face down', 'dimgray'];
  return ['Tilted', 'darkorange'];
}

function drawTiltPanel(p, a) {
  stroke('silver');
  fill(255, 255, 255, 200);
  rect(p.x, p.y, p.w, p.h, 10);

  const wide = canvasWidth >= 600;
  // watch area and bar area
  let wx, wy, wsize, bx, by, bw;
  if (wide) {
    wx = p.x + p.w / 2;
    wy = p.y + 120;
    wsize = min(p.w * 0.3, 62);
    bx = p.x + 12;
    by = p.y + 225;
    bw = p.w - 24;
  } else {
    wx = p.x + p.w * 0.25;
    wy = p.y + p.h / 2 + 14;
    wsize = min(p.w * 0.1, 40);
    bx = p.x + p.w * 0.5;
    by = p.y + 28;
    bw = p.w * 0.5 - 12;
  }
  drawWatch(wx, wy, wsize);

  // tilt label
  const lab = tiltLabel(a);
  noStroke();
  fill(lab[1]);
  textSize(16);
  textAlign(CENTER, TOP);
  if (wide) {
    text(lab[0], p.x + p.w / 2, p.y + 8);
  } else {
    textAlign(LEFT, TOP);
    text(lab[0], p.x + 10, p.y + 6);
  }

  // g bars
  const rows = [['x', a.x, 'crimson'], ['y', a.y, 'seagreen'], ['z', a.z, 'royalblue']];
  const rowH = wide ? 34 : 34;
  for (let i = 0; i < 3; i++) {
    const yy = by + i * rowH;
    noStroke();
    fill('black');
    textSize(15);
    textAlign(LEFT, TOP);
    text(rows[i][0] + ': ' + (rows[i][1] >= 0 ? '+' : '') + nf(rows[i][1], 1, 2) + ' g', bx, yy);
    const barX = bx;
    const barY = yy + 18;
    const barW = bw;
    stroke('silver');
    fill(235);
    rect(barX, barY, barW, 10, 3);
    const cx = barX + barW / 2;
    noStroke();
    fill(rows[i][2]);
    const len = (barW / 2) * constrain(rows[i][1], -1, 1);
    rect(min(cx, cx + len), barY, abs(len), 10);
    stroke('black');
    line(cx, barY - 2, cx, barY + 12);
  }
  noStroke();
  fill('black');
  textSize(14);
  textAlign(LEFT, TOP);
  const magNow = sqrt(a.x * a.x + a.y * a.y + a.z * a.z);
  const noteY = by + 3 * rowH + 2;
  if (noteY < p.y + p.h - 16) {
    text('|a| = ' + nf(magNow, 1, 2) + ' g at rest (any tilt)', bx, noteY);
  }
}

// 3D watch: a thin box with two straps, rotated by pitch and roll, drawn back to front
function drawWatch(cx, cy, s) {
  const th = radians(pitch);
  const ph = radians(roll);
  const cam = radians(-50);   // tilt the camera so the watch looks three-dimensional
  const rot = (p) => {
    // roll about y, then pitch about x (device frame to world frame)
    let x = p[0] * cos(ph) + p[2] * sin(ph);
    let y = p[1];
    let z = -p[0] * sin(ph) + p[2] * cos(ph);
    let y2 = y * cos(th) - z * sin(th);
    let z2 = y * sin(th) + z * cos(th);
    // camera tilt
    let y3 = y2 * cos(cam) - z2 * sin(cam);
    let z3 = y2 * sin(cam) + z2 * cos(cam);
    return [x, y3, z3];
  };
  const proj = (p) => [cx + p[0] * s, cy - p[1] * s];

  const box = (x0, x1, y0, y1, z0, z1) => [
    [x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
    [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]
  ];
  let digits = null;
  // Draw each box with back-face culling; straps first, then the body on top of them
  const drawBox = (pts, col, topCol, isBody) => {
    const r = pts.map(rot);
    const quads = [[4, 5, 6, 7, topCol], [0, 3, 2, 1, col], [0, 1, 5, 4, col],
      [2, 3, 7, 6, col], [1, 2, 6, 5, col], [0, 4, 7, 3, col]];
    for (let qi = 0; qi < quads.length; qi++) {
      const q = quads[qi];
      const ps = [r[q[0]], r[q[1]], r[q[2]], r[q[3]]].map(proj);
      // screen-space winding tells us whether the face points toward the viewer
      const cross = (ps[1][0] - ps[0][0]) * (ps[2][1] - ps[0][1]) - (ps[1][1] - ps[0][1]) * (ps[2][0] - ps[0][0]);
      if (cross > 0) continue;
      stroke(40);
      strokeWeight(1);
      fill(q[4]);
      beginShape();
      for (const pp of ps) vertex(pp[0], pp[1]);
      endShape(CLOSE);
      // clock digits on the screen when it faces us
      if (isBody && qi === 0 && abs(cross) > s * s * 0.6) {
        const c = proj(rot([0, 0, 0.18]));
        digits = { x: c[0], y: c[1] + s * 0.38 * min(1, abs(cross) / (s * s * 2.25)),
          size: s * 0.3 * min(1, abs(cross) / (s * s * 2.25)) + 4 };
      }
    }
  };
  drawBox(box(-0.42, 0.42, -1.6, -0.6, -0.05, 0.05), 'dimgray', 'gray', false);  // lower strap
  drawBox(box(-0.42, 0.42, 0.6, 1.6, -0.05, 0.05), 'dimgray', 'gray', false);    // upper strap
  drawBox(box(-0.75, 0.75, -0.75, 0.75, -0.18, 0.18), 'slategray', 'black', true); // body, screen on top

  // axis arrows from the watch centre in the watch's own frame
  const axes = [[[-1.3, 0, 0], 'crimson', 'x'], [[0, -1.3, 0], 'seagreen', 'y'], [[0, 0, 1.3], 'royalblue', 'z']];
  const o = proj(rot([0, 0, 0.18]));
  for (const ax of axes) {
    const e = proj(rot([ax[0][0], ax[0][1], ax[0][2] + 0.18]));
    stroke(ax[1]);
    strokeWeight(3);
    line(o[0], o[1], e[0], e[1]);
    noStroke();
    fill(ax[1]);
    circle(e[0], e[1], 7);
    textSize(14);
    textAlign(CENTER, CENTER);
    text(ax[2], e[0] + (e[0] - o[0]) * 0.15, e[1] + (e[1] - o[1]) * 0.15 - 2);
  }
  strokeWeight(1);
  // clock digits drawn last, below the axis origin, so the arrows do not cover them
  if (digits) {
    noStroke();
    fill('lime');
    textAlign(CENTER, CENTER);
    textSize(digits.size);
    text('10:09', digits.x, digits.y);
  }
}

function drawStepPanel(p) {
  stroke('silver');
  fill('white');
  rect(p.x, p.y, p.w, p.h, 10);

  const th = thresholdSlider.value();
  const gapMs = gapSlider.value();

  // plot area
  const x0 = p.x + 44;
  const x1 = p.x + p.w - 10;
  const y0 = p.y + 44;
  const y1 = p.y + p.h - 46;
  const gMin = 0.6;
  const gMax = 2.0;
  const toY = (g) => map(g, gMin, gMax, y1, y0);
  const toX = (i) => map(i, 0, WINDOW - 1, x0, x1);

  // grid
  stroke(225);
  for (let g = 0.75; g <= 2.0; g += 0.25) line(x0, toY(g), x1, toY(g));
  noStroke();
  fill('black');
  textSize(13);
  textAlign(RIGHT, CENTER);
  for (let g = 1.0; g <= 2.0; g += 0.5) text(nf(g, 1, 1) + ' g', x0 - 4, toY(g));
  textAlign(CENTER, TOP);
  text('last 5 seconds', (x0 + x1) / 2, y1 + 3);

  // signal
  stroke('steelblue');
  strokeWeight(1.5);
  noFill();
  beginShape();
  for (let i = 0; i < mag.length; i++) vertex(toX(i), toY(constrain(mag[i], gMin, gMax)));
  endShape();
  strokeWeight(1);

  // threshold
  stroke('crimson');
  strokeWeight(2);
  drawingContext.setLineDash([7, 5]);
  line(x0, toY(th), x1, toY(th));
  drawingContext.setLineDash([]);
  strokeWeight(1);

  // count upward crossings separated by at least gapMs
  let counted = 0;
  let actual = 0;
  let lastT = -1e9;
  for (let i = 1; i < mag.length; i++) {
    if (trueStep[i]) actual++;
    if (mag[i - 1] < th && mag[i] >= th) {
      const tMs = (i * 1000) / RATE;
      if (tMs - lastT >= gapMs) {
        counted++;
        lastT = tMs;
        noStroke();
        fill('darkorange');
        const xx = toX(i);
        triangle(xx - 6, y0 - 12, xx + 6, y0 - 12, xx, y0 - 2);
        stroke('darkorange');
        line(xx, y0, xx, y1);
      }
    }
  }

  // header and readout
  noStroke();
  fill('black');
  textSize(16);
  textAlign(LEFT, TOP);
  text('Acceleration magnitude |a|', p.x + 10, p.y + 6);
  const ok = counted === actual;
  fill(ok ? 'darkgreen' : 'crimson');
  textAlign(LEFT, BOTTOM);
  text('Counted: ' + counted + '   Real steps: ' + actual + (ok ? '  (match)' : (counted > actual ? '  (too many)' : '  (too few)')),
    p.x + 10, p.y + p.h - 6);
  if (!isWalking) {
    fill('dimgray');
    textAlign(RIGHT, BOTTOM);
    textSize(14);
    if (p.w > 420) text('Paused: press Walk', p.x + p.w - 10, p.y + p.h - 6);
  }
}

// Dragging inside the watch panel tilts the watch
function mousePressed() {
  dragging = leftPanel && mouseX > leftPanel.x && mouseX < leftPanel.x + leftPanel.w &&
    mouseY > leftPanel.y && mouseY < leftPanel.y + leftPanel.h;
}

function mouseDragged() {
  if (!dragging) return;
  roll = constrain(roll + (mouseX - pmouseX) * 0.8, -90, 90);
  pitch = constrain(pitch - (mouseY - pmouseY) * 0.8, -180, 180);
  return false;
}

function mouseReleased() {
  dragging = false;
}

function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
  thresholdSlider.size(canvasWidth - sliderLeftMargin - margin);
  gapSlider.size(canvasWidth - sliderLeftMargin - margin);
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) {
    canvasWidth = Math.floor(container.getBoundingClientRect().width);
  }
}
