// Weather Station Layout MicroSim
// CANVAS_HEIGHT: 545
// Students design a 152 x 152 e-paper weather display by dragging and resizing three panels
// (time, indoor temperature and humidity, forecast), choose how often each one updates, and
// press "Simulate day" to count the refreshes and WiFi connections in 24 hours and estimate
// the battery life on a 500 mAh cell. Opens paused; the day only runs after the button.

let canvasWidth = 400;
let drawHeight = 430;
let controlHeight = 115;
let canvasHeight = drawHeight + controlHeight;
let margin = 25;
let defaultTextSize = 16;

let simButton, resetButton, timeSelect, indoorSelect, forecastSelect;

const EPD = 152;          // e-paper panel is 152 x 152 pixels
const DEFAULT_PANELS = [
  { id: 'time', name: 'Time', x: 6, y: 6, w: 140, h: 52 },
  { id: 'indoor', name: 'Indoor', x: 6, y: 64, w: 68, h: 82 },
  { id: 'forecast', name: 'Forecast', x: 80, y: 64, w: 66, h: 82 }
];
let panels = [];

// screen geometry (set every frame)
let sx = 10, sy = 40, ss = 380, scaleF = 2.5;

// interaction
let dragIdx = -1;
let dragMode = '';        // 'move' or 'resize'
let dragOffX = 0, dragOffY = 0;
let hoverIdx = -1;

// day simulation
let simRunning = false;
let simMinute = 0;        // minutes since midnight in the simulated day
let simDone = false;
let counts = null;
let events = [];          // [{m, type}] for the timeline

// ---------- Simple energy model (stated in the docs) ----------
const SLEEP_MA = 0.3;          // Pico in deep sleep between updates, RTC running
const WAKE_MAH = 25 * 0.2 / 3600;          // Pico awake 0.2 s per update
const WIFI_MAH = 70 * 4 / 3600;            // WiFi on for 4 s per forecast fetch
const FULL_MAH = 10 * 2.0 / 3600;          // full refresh: 10 mA for 2 s
const PARTIALS_PER_FULL = 30;              // full refresh after every 30 partial refreshes
function partialMah(areaFrac) {            // partial refresh: 10 mA for 0.25 s + 0.5 s x area
  return 10 * (0.25 + 0.5 * areaFrac) / 3600;
}

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));

  simButton = createButton('Simulate day');
  simButton.position(10, drawHeight + 6);
  simButton.mousePressed(toggleSim);

  resetButton = createButton('Reset layout');
  resetButton.position(125, drawHeight + 6);
  resetButton.mousePressed(resetLayout);

  timeSelect = createSelect();
  for (const o of [['1 min', 1], ['5 min', 5], ['15 min', 15]]) timeSelect.option(o[0], String(o[1]));
  timeSelect.selected('1');
  timeSelect.position(110, drawHeight + 43);
  timeSelect.changed(clearResults);

  indoorSelect = createSelect();
  for (const o of [['1 min', 1], ['5 min', 5], ['10 min', 10], ['30 min', 30]]) indoorSelect.option(o[0], String(o[1]));
  indoorSelect.selected('10');
  indoorSelect.position(320, drawHeight + 43);
  indoorSelect.changed(clearResults);

  forecastSelect = createSelect();
  for (const o of [['30 min', 30], ['1 hour', 60], ['3 hours', 180], ['6 hours', 360]]) forecastSelect.option(o[0], String(o[1]));
  forecastSelect.selected('60');
  forecastSelect.position(140, drawHeight + 78);
  forecastSelect.changed(clearResults);

  resetLayout();

  describe('A mock 152 by 152 pixel e-paper weather display with three draggable, resizable panels: time, indoor temperature and humidity, and the forecast. Hovering a panel shows its data source and update interval. A Simulate day button runs a 24 hour timeline that counts partial refreshes, full refreshes and WiFi connections, and estimates battery life on a 500 mAh cell.');
}

function resetLayout() {
  panels = DEFAULT_PANELS.map(p => Object.assign({}, p));
  clearResults();
}

function clearResults() {
  simRunning = false;
  simDone = false;
  simMinute = 0;
  counts = null;
  events = [];
  simButton.html('Simulate day');
}

function toggleSim() {
  if (simRunning) {
    simRunning = false;
    simButton.html('Continue');
    return;
  }
  if (!counts || simDone) startDay();
  simRunning = true;
  simButton.html('Pause');
}

function startDay() {
  simMinute = 0;
  simDone = false;
  events = [];
  counts = { time: 0, indoor: 0, forecast: 0, wifi: 0, partial: 0, full: 0,
    wakes: 0, mahWake: 0, mahPartial: 0, mahFull: 0, mahWifi: 0, sincefull: 0 };
}

// Which panels must be redrawn when panel i updates (itself plus any panel it overlaps)
function redrawSet(i) {
  const set = [i];
  for (let j = 0; j < panels.length; j++) {
    if (j !== i && overlaps(panels[i], panels[j])) set.push(j);
  }
  return set;
}

function overlaps(a, b) {
  return a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h;
}

function areaFrac(set) {
  // bounding box of the panels that must be redrawn
  let x0 = EPD, y0 = EPD, x1 = 0, y1 = 0;
  for (const k of set) {
    const p = panels[k];
    x0 = min(x0, p.x); y0 = min(y0, p.y);
    x1 = max(x1, p.x + p.w); y1 = max(y1, p.y + p.h);
  }
  return ((x1 - x0) * (y1 - y0)) / (EPD * EPD);
}

// Advance the simulated day by one minute and count what happens
function stepMinute() {
  const m = simMinute;
  const intervals = { time: int(timeSelect.value()), indoor: int(indoorSelect.value()), forecast: int(forecastSelect.value()) };
  const due = [];
  for (let i = 0; i < panels.length; i++) {
    if (m % intervals[panels[i].id] === 0) due.push(i);
  }
  if (due.length > 0) {
    counts.wakes++;
    counts.mahWake += WAKE_MAH;
    // all due panels share one wake-up; redraw their union
    let set = [];
    for (const i of due) for (const k of redrawSet(i)) if (!set.includes(k)) set.push(k);
    for (const i of due) counts[panels[i].id]++;
    if (due.some(i => panels[i].id === 'forecast')) {
      counts.wifi++;
      counts.mahWifi += WIFI_MAH;
      events.push({ m, type: 'wifi' });
    }
    if (counts.sincefull >= PARTIALS_PER_FULL || m === 0) {
      counts.full++;
      counts.mahFull += FULL_MAH;
      counts.sincefull = 0;
      events.push({ m, type: 'full' });
    } else {
      counts.partial++;
      counts.mahPartial += partialMah(areaFrac(set));
      counts.sincefull++;
    }
  }
  simMinute++;
  if (simMinute >= 1440) {
    simRunning = false;
    simDone = true;
    simButton.html('Simulate day');
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

  if (simRunning) {
    for (let k = 0; k < 6 && simRunning; k++) stepMinute();
  }

  noStroke();
  fill('black');
  textAlign(CENTER, TOP);
  textSize(22);
  text('Weather Station Layout', canvasWidth / 2, 8);

  // layout: screen left and info right, or screen on top for narrow canvases
  const wide = canvasWidth >= 600;
  if (wide) {
    ss = min(drawHeight - 52, canvasWidth * 0.5 - 20);
    sx = 10;
    sy = 40;
  } else {
    ss = min(canvasWidth - 20, 220);
    sx = (canvasWidth - ss) / 2;
    sy = 38;
  }
  scaleF = ss / EPD;

  drawScreen();
  const info = wide ? { x: sx + ss + 14, y: 40, w: canvasWidth - (sx + ss + 14) - 10, h: drawHeight - 50 }
    : { x: 8, y: sy + ss + 8, w: canvasWidth - 16, h: drawHeight - (sy + ss + 8) - 6 };
  drawInfo(info);

  // control labels
  noStroke();
  fill('black');
  textAlign(LEFT, CENTER);
  textSize(defaultTextSize);
  text('Time every:', 10, drawHeight + 53);
  text('Indoor every:', 215, drawHeight + 53);
  text('Forecast every:', 10, drawHeight + 88);
  textSize(14);
  fill('dimgray');
  if (canvasWidth > 560) text('Drag a panel to move it; drag its corner to resize.', 250, drawHeight + 18);
}

function drawScreen() {
  // bezel
  noStroke();
  fill('dimgray');
  rect(sx - 6, sy - 6, ss + 12, ss + 12, 8);
  fill('whitesmoke');
  rect(sx, sy, ss, ss);

  const clockMin = simRunning || simDone ? simMinute % 1440 : 7 * 60 + 42;

  for (let i = 0; i < panels.length; i++) {
    const p = panels[i];
    const x = sx + p.x * scaleF;
    const y = sy + p.y * scaleF;
    const w = p.w * scaleF;
    const h = p.h * scaleF;
    let overlap = false;
    for (let j = 0; j < panels.length; j++) if (j !== i && overlaps(p, panels[j])) overlap = true;

    stroke(overlap ? 'crimson' : (i === hoverIdx ? 'steelblue' : 'black'));
    strokeWeight(i === hoverIdx || overlap ? 2 : 1);
    fill(255, 255, 255, 120);
    rect(x, y, w, h, 3);
    strokeWeight(1);
    drawPanelContent(p, x, y, w, h, clockMin);
    // resize handle
    noStroke();
    fill(i === hoverIdx ? 'steelblue' : 'gray');
    triangle(x + w, y + h - 12, x + w, y + h, x + w - 12, y + h);
  }
}

function drawPanelContent(p, x, y, w, h, clockMin) {
  noStroke();
  fill('black');
  textAlign(CENTER, CENTER);
  if (p.id === 'time') {
    const t = nf(floor(clockMin / 60), 2) + ':' + nf(clockMin % 60, 2);
    textSize(max(8, min(h * 0.8, w / 2.9)));
    textStyle(BOLD);
    text(t, x + w / 2, y + h / 2 + 2);
    textStyle(NORMAL);
  } else if (p.id === 'indoor') {
    const ts = max(8, min(h / 4.2, w / 5));
    textSize(ts * 0.7);
    text('Indoor', x + w / 2, y + h * 0.18);
    textSize(ts);
    text('21.5°C', x + w / 2, y + h * 0.47);
    text('45% RH', x + w / 2, y + h * 0.77);
  } else {
    const r = min(w, h) * 0.22;
    const cx = x + w / 2;
    const cy = y + h * 0.36;
    // sun with a cloud
    stroke('black');
    strokeWeight(max(1, r * 0.12));
    for (let a = 0; a < 8; a++) {
      const ang = a * QUARTER_PI;
      line(cx - r * 0.3 + cos(ang) * r * 0.75, cy - r * 0.2 + sin(ang) * r * 0.75,
        cx - r * 0.3 + cos(ang) * r * 1.0, cy - r * 0.2 + sin(ang) * r * 1.0);
    }
    noStroke();
    fill('black');
    circle(cx - r * 0.3, cy - r * 0.2, r);
    fill('whitesmoke');
    stroke('black');
    strokeWeight(max(1, r * 0.1));
    ellipse(cx + r * 0.25, cy + r * 0.35, r * 1.5, r * 0.8);
    strokeWeight(1);
    noStroke();
    fill('black');
    textSize(max(8, min(h / 5, w / 5.2)));
    text('H 18° L 9°', cx, y + h * 0.8);
  }
}

function intervalText(id) {
  const v = int((id === 'time' ? timeSelect : (id === 'indoor' ? indoorSelect : forecastSelect)).value());
  if (v >= 60) return v / 60 + (v === 60 ? ' hour' : ' hours');
  return v + (v === 1 ? ' minute' : ' minutes');
}

function drawInfo(c) {
  stroke('silver');
  fill('white');
  rect(c.x, c.y, c.w, c.h, 8);
  noStroke();
  const x = c.x + 10;
  let y = c.y + 8;
  const narrow = canvasWidth < 600;
  const ts = narrow ? 13 : 15;
  const lh = narrow ? 17 : 21;
  textAlign(LEFT, TOP);
  textSize(ts);

  // hover info, or the readability check
  const timeP = panels.find(p => p.id === 'time');
  const digitPx = round(min(timeP.h * 0.8, timeP.w / 2.9) * 0.72);
  if (hoverIdx >= 0) {
    const p = panels[hoverIdx];
    fill('steelblue');
    const src = { time: 'DS3231 real-time clock (no WiFi)', indoor: 'DHT22 sensor on a GPIO pin',
      forecast: 'Open-Meteo over WiFi (about 4 s of WiFi per fetch)' };
    text(p.name + ': ' + src[p.id], x, y, c.w - 20);
    y += narrow ? lh * 2 : (textWidth(p.name + ': ' + src[p.id]) > c.w - 20 ? lh * 2 : lh);
    fill('black');
    text('Updates every ' + intervalText(p.id) + '. Panel ' + p.w + ' x ' + p.h + ' px.', x, y);
    y += lh;
  } else {
    fill('dimgray');
    text('Hover a panel to see its data source.', x, y);
    y += lh;
    fill(digitPx >= 24 ? 'darkgreen' : 'crimson');
    text('Time digits ' + digitPx + ' px tall: ' + (digitPx >= 24 ? 'readable across a room' : 'too small to read from afar'), x, y, c.w - 20);
    y += narrow ? lh : lh;
  }
  // overlap warning
  let anyOverlap = false;
  for (let i = 0; i < panels.length; i++) for (let j = i + 1; j < panels.length; j++) if (overlaps(panels[i], panels[j])) anyOverlap = true;
  if (anyOverlap) {
    fill('crimson');
    text('Panels overlap: updating one also redraws the other.', x, y, c.w - 20);
    y += lh;
  }
  y += 4;

  // results
  fill('black');
  if (!counts) {
    text('Press Simulate day to run 24 hours and count', x, y);
    y += lh;
    text('refreshes and WiFi connections.', x, y);
    y += lh;
  } else {
    const hh = nf(floor(simMinute / 60), 2) + ':' + nf(simMinute % 60, 2);
    textStyle(BOLD);
    text(simDone ? 'Results for 24 hours' : 'Simulated time ' + hh + (simRunning ? '' : ' (paused)'), x, y);
    textStyle(NORMAL);
    y += lh;
    text('Updates: time ' + counts.time + ', indoor ' + counts.indoor + ', forecast ' + counts.forecast, x, y);
    y += lh;
    text('Refreshes: ' + counts.partial + ' partial, ' + counts.full + ' full', x, y);
    y += lh;
    text('WiFi connections: ' + counts.wifi, x, y);
    y += lh;
    if (simDone) {
      const sleepMah = SLEEP_MA * 24;
      const total = sleepMah + counts.mahWake + counts.mahPartial + counts.mahFull + counts.mahWifi;
      const days = 500 * 0.8 / total;
      if (!narrow) {
        fill('dimgray');
        text('mAh per day: sleep ' + nf(sleepMah, 1, 1) + ', wake ' + nf(counts.mahWake, 1, 1) +
          ', refresh ' + nf(counts.mahPartial + counts.mahFull, 1, 1) + ', WiFi ' + nf(counts.mahWifi, 1, 1), x, y, c.w - 20);
        y += lh * (textWidth('mAh per day: sleep 0.0, wake 0.0, refresh 0.0, WiFi 0.0') > c.w - 20 ? 2 : 1);
      }
      fill('darkgreen');
      textSize(narrow ? 15 : 18);
      textStyle(BOLD);
      text('Battery life (500 mAh): ' + nf(days, 1, 1) + ' days', x, y);
      textStyle(NORMAL);
      textSize(ts);
      y += lh + 4;
    }
  }

  // 24-hour timeline
  const tx0 = c.x + 10;
  const tx1 = c.x + c.w - 10;
  const ty = c.y + c.h - (narrow ? 22 : 34);
  if (ty > y + 4) {
    stroke('silver');
    fill(240);
    rect(tx0, ty, tx1 - tx0, 12, 3);
    if (counts) {
      noStroke();
      fill(200, 225, 245);
      rect(tx0, ty, (tx1 - tx0) * simMinute / 1440, 12, 3);
      for (const e of events) {
        const xx = map(e.m, 0, 1440, tx0, tx1);
        stroke(e.type === 'wifi' ? 'mediumpurple' : 'black');
        strokeWeight(e.type === 'wifi' ? 2 : 1);
        if (e.type === 'wifi') line(xx, ty - 4, xx, ty + 6);
        else line(xx, ty + 6, xx, ty + 16);
      }
      strokeWeight(1);
    }
    noStroke();
    fill('black');
    textSize(12);
    textAlign(LEFT, TOP);
    if (!narrow) {
      text('0:00', tx0, ty + 16);
      textAlign(RIGHT, TOP);
      text('24:00', tx1, ty + 16);
      textAlign(CENTER, TOP);
      fill('dimgray');
      text('purple = WiFi fetch, black = full refresh', (tx0 + tx1) / 2, ty + 16);
    }
  }
}

// ---------- Mouse interaction: move and resize panels ----------
function screenToEpd(mx, my) {
  return [(mx - sx) / scaleF, (my - sy) / scaleF];
}

function panelAt(mx, my) {
  const e = screenToEpd(mx, my);
  for (let i = panels.length - 1; i >= 0; i--) {
    const p = panels[i];
    if (e[0] >= p.x && e[0] <= p.x + p.w && e[1] >= p.y && e[1] <= p.y + p.h) return i;
  }
  return -1;
}

function mouseMoved() {
  hoverIdx = panelAt(mouseX, mouseY);
}

function mousePressed() {
  const i = panelAt(mouseX, mouseY);
  if (i < 0) return;
  const p = panels[i];
  const e = screenToEpd(mouseX, mouseY);
  const handle = 14 / scaleF;
  dragIdx = i;
  if (e[0] > p.x + p.w - handle && e[1] > p.y + p.h - handle) {
    dragMode = 'resize';
  } else {
    dragMode = 'move';
    dragOffX = e[0] - p.x;
    dragOffY = e[1] - p.y;
  }
}

function mouseDragged() {
  if (dragIdx < 0) return;
  const p = panels[dragIdx];
  const e = screenToEpd(mouseX, mouseY);
  if (dragMode === 'move') {
    p.x = round(constrain(e[0] - dragOffX, 0, EPD - p.w));
    p.y = round(constrain(e[1] - dragOffY, 0, EPD - p.h));
  } else {
    p.w = round(constrain(e[0] - p.x, 30, EPD - p.x));
    p.h = round(constrain(e[1] - p.y, 20, EPD - p.y));
  }
  hoverIdx = dragIdx;
  clearResults();
  return false;
}

function mouseReleased() {
  dragIdx = -1;
}

function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) {
    canvasWidth = Math.floor(container.getBoundingClientRect().width);
  }
}
