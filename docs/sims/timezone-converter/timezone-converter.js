// Timezone Converter MicroSim
// CANVAS_HEIGHT: 525
// Converts a UTC time to local time with integer second arithmetic, the same way
// the Pico does: local_secs = utc_secs + offset_hours * 3600.
// A world strip map shows the 24 time-zone bands; bands already on the next
// (or still on the previous) calendar day are tinted so date rollovers are visible.

// ---- Layout ----
let canvasWidth = 400;
let drawHeight = 410;
let controlHeight = 115;          // 3 rows x 35 + 10
let canvasHeight = drawHeight + controlHeight;
let margin = 10;
let sliderLeftMargin = 150;
let defaultTextSize = 16;

// ---- Controls ----
let timeSlider, dateInput, zoneSelect, dstCheckbox, predictButton, answerInput, checkButton;

// ---- Zones from the Chapter 14 table (standard offset, daylight offset or null) ----
const ZONES = [
  { name: 'US Eastern', std: -5, dst: -4, abbr: ['EST', 'EDT'], city: 'New York', lon: -74, lat: 41 },
  { name: 'US Central (Minnesota)', std: -6, dst: -5, abbr: ['CST', 'CDT'], city: 'Minneapolis', lon: -93, lat: 45 },
  { name: 'US Mountain', std: -7, dst: -6, abbr: ['MST', 'MDT'], city: 'Denver', lon: -105, lat: 40 },
  { name: 'US Pacific', std: -8, dst: -7, abbr: ['PST', 'PDT'], city: 'Los Angeles', lon: -118, lat: 34 },
  { name: 'UTC', std: 0, dst: null, abbr: ['UTC', 'UTC'], city: 'London (winter)', lon: 0, lat: 51.5 },
  { name: 'Central Europe', std: 1, dst: 2, abbr: ['CET', 'CEST'], city: 'Berlin', lon: 13.4, lat: 52.5 },
  { name: 'India', std: 5.5, dst: null, abbr: ['IST', 'IST'], city: 'New Delhi', lon: 77, lat: 28.6 }
];

// Very rough continent outlines as [longitude, latitude] pairs (just enough to orient the map)
const LAND = [
  [[-168, 66], [-140, 70], [-95, 72], [-75, 62], [-60, 52], [-75, 45], [-80, 32], [-82, 25], [-97, 26], [-97, 19],
   [-92, 15], [-83, 9], [-78, 8], [-88, 14], [-105, 22], [-115, 30], [-124, 40], [-125, 50], [-135, 58], [-150, 60], [-165, 60]],
  [[-55, 60], [-43, 60], [-20, 70], [-22, 82], [-60, 82], [-72, 77]],
  [[-80, 10], [-62, 10], [-50, 0], [-35, -6], [-40, -22], [-58, -38], [-68, -55], [-75, -50], [-72, -30], [-81, -5]],
  [[-10, 36], [-9, 44], [-2, 48], [5, 54], [8, 58], [15, 69], [30, 71], [60, 70], [80, 73], [110, 77], [140, 72], [180, 68],
   [180, 62], [160, 58], [140, 52], [130, 42], [122, 30], [120, 22], [108, 18], [105, 10], [101, 2], [98, 10], [92, 22],
   [80, 15], [77, 8], [72, 20], [60, 25], [52, 25], [45, 13], [35, 29], [28, 36], [20, 40], [10, 38], [0, 38]],
  [[-17, 21], [-10, 35], [10, 37], [32, 31], [43, 12], [51, 12], [40, -15], [32, -28], [20, -35], [15, -28], [12, -6],
   [8, 4], [-8, 4], [-17, 14]],
  [[113, -22], [130, -12], [142, -11], [153, -27], [146, -39], [135, -35], [115, -34]]
];

const DAY_NAMES = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

// ---- Predict mode ----
let predictMode = false;
let revealed = true;
let feedback = '';
let feedbackColor = 'black';

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  // Row 1: UTC time of day in minutes (15-minute steps)
  timeSlider = createSlider(0, 1425, 90, 15);
  timeSlider.position(sliderLeftMargin, drawHeight + 8);
  timeSlider.size(canvasWidth - sliderLeftMargin - 25);
  timeSlider.input(() => { if (predictMode) leavePredict(); });

  // Row 2: UTC date and the zone
  dateInput = createInput('2026-01-15', 'date');
  dateInput.position(10, drawHeight + 42);
  dateInput.size(130);
  dateInput.input(() => { if (predictMode) leavePredict(); });

  zoneSelect = createSelect();
  for (let i = 0; i < ZONES.length; i++) zoneSelect.option(ZONES[i].name, String(i));
  zoneSelect.selected('1');
  zoneSelect.position(165, drawHeight + 43);
  zoneSelect.changed(() => { if (predictMode) leavePredict(); });

  // Row 3: DST and Predict mode
  dstCheckbox = createCheckbox('DST on', false);
  dstCheckbox.position(10, drawHeight + 80);

  predictButton = createButton('Predict');
  predictButton.position(95, drawHeight + 78);
  predictButton.mousePressed(togglePredict);

  answerInput = createInput('');
  answerInput.position(200, drawHeight + 78);
  answerInput.size(60);
  answerInput.attribute('placeholder', 'HH:MM');

  checkButton = createButton('Check');
  checkButton.position(280, drawHeight + 78);
  checkButton.mousePressed(checkAnswer);

  describe('A world map with 24 time-zone bands, a digital clock for UTC and one for the selected zone. ' +
    'A slider sets the UTC time; when the local time crosses midnight the local date changes and is highlighted.');
}

// ---- Time arithmetic (integer seconds, like time.time() on the Pico) ----
function utcSeconds() {
  const parts = (dateInput.value() || '2026-01-15').split('-').map(Number);
  const daySecs = Date.UTC(parts[0], parts[1] - 1, parts[2]) / 1000;
  return daySecs + timeSlider.value() * 60;
}

function zone() { return ZONES[parseInt(zoneSelect.value(), 10)]; }

function offsetHours(z) {
  return (dstCheckbox.checked() && z.dst !== null) ? z.dst : z.std;
}

// Break seconds since 1970 into fields using the UTC calendar
function fields(secs) {
  const d = new Date(secs * 1000);
  return { y: d.getUTCFullYear(), mo: d.getUTCMonth(), d: d.getUTCDate(), wd: d.getUTCDay(),
    h: d.getUTCHours(), m: d.getUTCMinutes(), dayNum: Math.floor(secs / 86400) };
}

function hhmm(f) { return String(f.h).padStart(2, '0') + ':' + String(f.m).padStart(2, '0'); }
function dateText(f) { return DAY_NAMES[f.wd] + ' ' + MONTHS[f.mo] + ' ' + f.d + ', ' + f.y; }
function offsetText(o) {
  const sign = o < 0 ? '−' : '+';
  const a = Math.abs(o);
  return sign + Math.floor(a) + (a % 1 ? ':30' : '');
}

// ---- Predict mode ----
function togglePredict() {
  if (predictMode) { leavePredict(); return; }
  predictMode = true;
  revealed = false;
  timeSlider.value(floor(random(96)) * 15);
  answerInput.value('');
  feedback = 'Predict the local time, type it as HH:MM, and press Check.';
  feedbackColor = 'black';
  predictButton.html('Exit Predict');
}

function leavePredict() {
  predictMode = false;
  revealed = true;
  feedback = '';
  predictButton.html('Predict');
}

function checkAnswer() {
  if (!predictMode) { feedback = 'Press Predict first.'; feedbackColor = 'black'; return; }
  const m = answerInput.value().trim().match(/^(\d{1,2}):?(\d{2})$/);
  if (!m) { feedback = 'Type the time as HH:MM, for example 19:30.'; feedbackColor = 'firebrick'; return; }
  const z = zone();
  const local = fields(utcSeconds() + Math.round(offsetHours(z) * 3600));
  const utc = fields(utcSeconds());
  revealed = true;
  const dayNote = local.dayNum < utc.dayNum ? ' on the previous day' : (local.dayNum > utc.dayNum ? ' on the next day' : '');
  if (parseInt(m[1], 10) === local.h && parseInt(m[2], 10) === local.m) {
    feedback = 'Correct! ' + hhmm(local) + dayNote + '. Press Exit Predict, then Predict for another.';
    feedbackColor = 'green';
  } else {
    feedback = 'Not quite: ' + hhmm(utc) + ' UTC ' + offsetText(offsetHours(z)) + ' h = ' + hhmm(local) + dayNote + '.';
    feedbackColor = 'firebrick';
  }
}

// ---- Drawing ----
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
  text('Timezone Converter', canvasWidth / 2, 8);

  const wide = canvasWidth >= 600;
  const z = zone();
  const off = offsetHours(z);
  const utcSecs = utcSeconds();
  const utc = fields(utcSecs);
  const local = fields(utcSecs + Math.round(off * 3600));

  const mapX = margin, mapY = 38, mapW = canvasWidth - 2 * margin, mapH = wide ? 180 : 110;
  drawMap(mapX, mapY, mapW, mapH, z, off, utcSecs, wide);

  // Clocks: side by side when wide, stacked when narrow
  const hidden = predictMode && !revealed;
  const rolled = local.dayNum !== utc.dayNum;
  if (wide) {
    const cy = mapY + mapH + 34, cw = (canvasWidth - 3 * margin) / 2, ch = 112;
    drawClock(margin, cy, cw, ch, 'UTC (what ntptime.settime() gives)', utc, false, false, 40);
    drawClock(2 * margin + cw, cy, cw, ch, z.abbr[off === z.std ? 0 : 1] + ' (UTC ' + offsetText(off) + ')  ' + z.city,
      local, hidden, rolled, 40);
  } else {
    const cw = canvasWidth - 2 * margin, ch = 92;
    drawClock(margin, mapY + mapH + 8, cw, ch, 'UTC', utc, false, false, 32);
    drawClock(margin, mapY + mapH + 8 + ch + 6, cw, ch, z.abbr[off === z.std ? 0 : 1] + ' (UTC ' + offsetText(off) + ')',
      local, hidden, rolled, 32);
  }

  // Message line: the conversion as arithmetic, or Predict feedback
  noStroke();
  textAlign(LEFT, TOP);
  textSize(wide ? 15 : 13);
  let msg, col = 'black';
  if (predictMode && feedback) { msg = feedback; col = feedbackColor; }
  else {
    const dayNote = local.dayNum < utc.dayNum ? ' (previous day!)' : (local.dayNum > utc.dayNum ? ' (next day!)' : '');
    msg = hhmm(utc) + ' UTC ' + offsetText(off) + ' h = ' + hhmm(local) + ' ' + MONTHS[local.mo] + ' ' + local.d + dayNote +
      (z.dst === null && dstCheckbox.checked() ? '   ' + z.name + ' has no DST.' : '');
    if (dayNote) col = 'darkorange';
  }
  fill(col);
  text(msg, margin, drawHeight - (wide ? 24 : 22), canvasWidth - 2 * margin);

  // Control labels
  noStroke();
  fill('black');
  textAlign(LEFT, CENTER);
  textSize(defaultTextSize);
  text('UTC time: ' + hhmm(utc), 10, drawHeight + 18);
}

function lonToX(lon, mapX, mapW) { return mapX + (lon + 180) / 360 * mapW; }
function latToY(lat, mapY, mapH) { return mapY + (80 - lat) / 140 * mapH; }

function drawMap(mapX, mapY, mapW, mapH, z, off, utcSecs, wide) {
  const utcDay = Math.floor(utcSecs / 86400);
  // Ocean
  noStroke();
  fill('lightcyan');
  rect(mapX, mapY, mapW, mapH);
  // Time-zone bands -12 ... +12, each 15 degrees wide; tint bands on a different date
  for (let k = -12; k <= 12; k++) {
    const x1 = lonToX(max(-180, k * 15 - 7.5), mapX, mapW);
    const x2 = lonToX(min(180, k * 15 + 7.5), mapX, mapW);
    const day = Math.floor((utcSecs + k * 3600) / 86400);
    if (day < utcDay) fill(200, 180, 255, 110);        // still yesterday
    else if (day > utcDay) fill(150, 230, 150, 110);   // already tomorrow
    else fill(k % 2 === 0 ? color(255, 255, 255, 60) : color(0, 0, 0, 18));
    rect(x1, mapY, x2 - x1, mapH);
  }
  // Land
  fill('tan');
  stroke('sienna');
  strokeWeight(1);
  for (const poly of LAND) {
    beginShape();
    for (const [lon, lat] of poly) vertex(lonToX(lon, mapX, mapW), latToY(lat, mapY, mapH));
    endShape(CLOSE);
  }
  // Selected zone band (India's +5.5 band is centered on 82.5 degrees)
  const bx1 = lonToX(off * 15 - 7.5, mapX, mapW), bx2 = lonToX(off * 15 + 7.5, mapX, mapW);
  stroke('darkorange');
  strokeWeight(2);
  fill(255, 200, 0, 70);
  rect(bx1, mapY, bx2 - bx1, mapH);
  // City marker
  const cx = lonToX(z.lon, mapX, mapW), cy = latToY(z.lat, mapY, mapH);
  stroke('white');
  fill('crimson');
  circle(cx, cy, 10);
  strokeWeight(1);
  // Map border
  noFill();
  stroke('gray');
  rect(mapX, mapY, mapW, mapH);

  // Offset labels above the bands and local hours below them
  noStroke();
  textAlign(CENTER, TOP);
  const step = wide ? 2 : 4;
  for (let k = -11; k <= 11; k++) {      // the half-width +-12 bands are too narrow to label
    const x = lonToX(k * 15, mapX, mapW);
    if (k % step === 0) {
      fill('dimgray');
      textSize(11);
      text((k > 0 ? '+' : '') + k, x, mapY + 2);
    }
    if (wide) {
      const f = fields(utcSecs + k * 3600);
      fill(k === off ? 'darkorange' : 'black');
      textSize(k === off ? 13 : 11);
      text(f.h, x, mapY + mapH + 3);
    }
  }
  if (wide) {
    textAlign(LEFT, TOP);
    textSize(12);
    fill('dimgray');
    text('Local hour in each band:', mapX, mapY + mapH + 17);
    fill(130, 100, 220);
    text('purple = previous day', mapX + 150, mapY + mapH + 17);
    fill(40, 140, 40);
    text('green = next day', mapX + 290, mapY + mapH + 17);
  }
}

function drawClock(x, y, w, h, label, f, hidden, rolled, big) {
  fill(255, 255, 255, 235);
  stroke(rolled ? 'darkorange' : 200);
  strokeWeight(rolled ? 3 : 1);
  rect(x, y, w, h, 10);
  strokeWeight(1);
  noStroke();
  fill('dimgray');
  textAlign(LEFT, TOP);
  textSize(14);
  text(label, x + 10, y + 7, w - 20);
  // Time
  fill('black');
  textAlign(CENTER, TOP);
  textSize(big);
  text(hidden ? '??:??' : hhmm(f), x + w / 2, y + 26);
  // Date (highlighted when it differs from the UTC date)
  textSize(15);
  if (hidden) {
    fill('dimgray');
    text('Predict the local time', x + w / 2, y + h - 24);
  } else {
    if (rolled) {
      fill('moccasin');
      rectMode(CENTER);
      rect(x + w / 2, y + h - 15, min(w - 20, 220), 22, 5);
      rectMode(CORNER);
      fill('darkorange');
    } else fill('black');
    text(dateText(f), x + w / 2, y + h - 24);
  }
}

function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
  timeSlider.size(canvasWidth - sliderLeftMargin - 25);
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) canvasWidth = Math.floor(container.getBoundingClientRect().width);
}
