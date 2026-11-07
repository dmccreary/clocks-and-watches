// Design Decision Matrix MicroSim
// CANVAS_HEIGHT: 545
// A weighted decision matrix for comparing clock designs. Each criterion has a weight (0-5)
// set with a slider and each design gets a 1-5 score per criterion from a menu. The bar chart
// shows each design's weighted total (sum of weight x score) and highlights the winner.
// The Sensitivity button finds the smallest single weight change that would flip the winner.
// The matrix of controls lives in the control region below the chart. No animation.

let canvasWidth = 400;
let drawHeight = 280;
let controlHeight = 265;
let canvasHeight = drawHeight + controlHeight;
let margin = 25;
let defaultTextSize = 16;

const CRITERIA = ['Readability', 'Cost', 'Power', 'Accuracy', 'User experience'];
const MAX_DESIGNS = 4;
const DESIGN_COLORS = ['steelblue', 'darkorange', 'seagreen', 'mediumpurple'];

const PRESETS = {
  worked: {
    label: 'Worked example',
    designs: ['LED clock', 'Round watch'],
    weights: [4, 2, 1, 3, 0],
    scores: [[5, 5, 4, 3, 3], [4, 2, 2, 5, 4]]
  },
  desk: {
    label: 'Four desk clocks',
    designs: ['LED clock', 'Round watch', 'E-paper', 'OLED desk'],
    weights: [3, 3, 2, 2, 3],
    scores: [[5, 5, 4, 3, 2], [4, 2, 2, 5, 5], [3, 3, 5, 4, 4], [3, 4, 3, 3, 3]]
  },
  wearable: {
    label: 'Wearable priorities',
    designs: ['LED clock', 'Round watch', 'E-paper', 'OLED desk'],
    weights: [3, 1, 5, 2, 4],
    scores: [[2, 5, 2, 3, 1], [4, 2, 2, 5, 5], [3, 3, 5, 4, 3], [4, 4, 3, 3, 3]]
  },
  blank: {
    label: 'Blank (all 3s)',
    designs: ['Design A', 'Design B', 'Design C', 'Design D'],
    weights: [3, 3, 3, 3, 3],
    scores: [[3, 3, 3, 3, 3], [3, 3, 3, 3, 3], [3, 3, 3, 3, 3], [3, 3, 3, 3, 3]]
  }
};

let designs = [];
let weightSliders = [];
let scoreSelects = [];    // [design][criterion]
let presetSelect, sensButton;
let sensText = [];

// layout columns (recomputed on resize)
let sliderX = 130, sliderW = 140, colX0 = 330, colW = 110;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));

  for (let r = 0; r < CRITERIA.length; r++) {
    const s = createSlider(0, 5, 3, 0.5);
    s.input(clearSensitivity);
    weightSliders.push(s);
  }
  for (let d = 0; d < MAX_DESIGNS; d++) {
    const col = [];
    for (let r = 0; r < CRITERIA.length; r++) {
      const sel = createSelect();
      for (let v = 1; v <= 5; v++) sel.option(String(v));
      sel.changed(clearSensitivity);
      col.push(sel);
    }
    scoreSelects.push(col);
  }

  presetSelect = createSelect();
  for (const k of Object.keys(PRESETS)) presetSelect.option(PRESETS[k].label, k);
  presetSelect.selected('worked');
  presetSelect.changed(() => loadPreset(presetSelect.value()));

  sensButton = createButton('Sensitivity');
  sensButton.mousePressed(runSensitivity);

  layoutControls();
  loadPreset('worked');

  describe('A weighted decision matrix comparing clock designs. Rows are criteria such as readability, cost, power, accuracy and user experience, each with a weight slider from 0 to 5, and each design has a score menu from 1 to 5. A bar chart shows each design\'s weighted total with the winner highlighted, and a Sensitivity button reports how much one weight must change before the winner flips.');
}

function loadPreset(key) {
  const p = PRESETS[key];
  designs = p.designs.slice();
  for (let r = 0; r < CRITERIA.length; r++) weightSliders[r].value(p.weights[r]);
  for (let d = 0; d < MAX_DESIGNS; d++) {
    for (let r = 0; r < CRITERIA.length; r++) {
      const sel = scoreSelects[d][r];
      if (d < designs.length) {
        sel.selected(String(p.scores[d][r]));
        sel.show();
      } else {
        sel.hide();
      }
    }
  }
  clearSensitivity();
}

function clearSensitivity() {
  sensText = [];
}

function layoutControls() {
  const narrow = canvasWidth < 560;
  sliderX = narrow ? 108 : 130;
  sliderW = narrow ? 58 : constrain(canvasWidth * 0.2, 70, 160);
  colX0 = sliderX + sliderW + (narrow ? 34 : 42);
  colW = max(44, (canvasWidth - colX0 - 10) / MAX_DESIGNS);
  for (let r = 0; r < CRITERIA.length; r++) {
    const y = drawHeight + 38 + r * 36;
    weightSliders[r].position(sliderX, y);
    weightSliders[r].size(sliderW);
    for (let d = 0; d < MAX_DESIGNS; d++) {
      scoreSelects[d][r].position(colX0 + d * colW + colW / 2 - 21, y - 2);
    }
  }
  const by = drawHeight + 38 + CRITERIA.length * 36 + 4;
  presetSelect.position(80, by);
  sensButton.position(min(300, canvasWidth - 110), by - 1);
}

// weights, scores and weighted totals
function computeModel() {
  const w = weightSliders.map(s => Number(s.value()));
  const sc = [];
  const totals = [];
  for (let d = 0; d < designs.length; d++) {
    const row = scoreSelects[d].map(sel => Number(sel.value()));
    sc.push(row);
    totals.push(row.reduce((a, v, r) => a + v * w[r], 0));
  }
  let winner = 0;
  for (let d = 1; d < totals.length; d++) if (totals[d] > totals[winner]) winner = d;
  const tied = totals.filter(t => t === totals[winner]).length > 1;
  return { w, sc, totals, winner, tied };
}

function runSensitivity() {
  const m = computeModel();
  if (designs.length < 2) return;
  let best = null;      // smallest weight change that makes a challenger win
  let tieOnly = null;   // a tie that can only just be reached at the end of the slider
  for (let c = 0; c < CRITERIA.length; c++) {
    for (let d = 0; d < designs.length; d++) {
      if (d === m.winner) continue;
      const lead = m.totals[m.winner] - m.totals[d];
      const diff = m.sc[d][c] - m.sc[m.winner][c];   // how much d gains per unit of weight
      if (diff === 0) continue;
      const change = lead / diff;                      // weight change that makes them tie
      const newW = m.w[c] + change;
      // to flip, the weight must be able to go past the tie point and stay within 0..5
      const canFlip = change > 0 ? newW < 5 : newW > 0;
      if (newW >= 0 && newW <= 5 && canFlip) {
        if (!best || abs(change) < abs(best.change)) best = { c, d, change, newW };
      } else if (newW >= 0 && newW <= 5) {
        if (!tieOnly || abs(change) < abs(tieOnly.change)) tieOnly = { c, d, change, newW };
      }
    }
  }
  if (!best) {
    sensText = ['No single weight change between 0 and 5 can flip the winner, so ' +
      designs[m.winner] + ' is a robust choice.'];
    if (tieOnly) {
      sensText.push('Closest call: with ' + CRITERIA[tieOnly.c] + ' at ' + nf(tieOnly.newW, 1, 1) + ', ' +
        designs[tieOnly.d] + ' would only tie.');
    }
  } else {
    const dir = best.change > 0 ? 'rises' : 'falls';
    sensText = ['Most sensitive weight: ' + CRITERIA[best.c] + '. If it ' + dir + ' from ' +
      nf(m.w[best.c], 1, 1) + ' to ' + String(Number(best.newW.toFixed(2))) + ', ' + designs[best.d] + ' ties ' +
      designs[m.winner] + '; ' + (best.change > 0 ? 'any higher' : 'any lower') + ' and ' + designs[best.d] + ' wins.'];
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

  const m = computeModel();

  noStroke();
  fill('black');
  textAlign(CENTER, TOP);
  textSize(22);
  text('Design Decision Matrix', canvasWidth / 2, 8);

  // ---------- Bar chart of weighted totals ----------
  const maxTotal = 5 * m.w.reduce((a, b) => a + b, 0);
  const cx0 = 120;
  const cx1 = canvasWidth - 60;
  const cy0 = 44;
  const barH = 26;
  const gap = 10;
  textSize(15);
  for (let d = 0; d < designs.length; d++) {
    const y = cy0 + d * (barH + gap);
    const win = d === m.winner && !m.tied;
    noStroke();
    fill('black');
    textAlign(RIGHT, CENTER);
    text(designs[d], cx0 - 8, y + barH / 2);
    stroke('silver');
    fill(240);
    rect(cx0, y, cx1 - cx0, barH, 4);
    const len = maxTotal > 0 ? (cx1 - cx0) * m.totals[d] / maxTotal : 0;
    stroke(win ? 'goldenrod' : 'gray');
    strokeWeight(win ? 3 : 1);
    fill(DESIGN_COLORS[d]);
    rect(cx0, y, len, barH, 4);
    strokeWeight(1);
    noStroke();
    fill('black');
    textAlign(LEFT, CENTER);
    text(nf(m.totals[d], 1, m.totals[d] % 1 === 0 ? 0 : 1) + (win ? '  ★' : ''), cx0 + len + 6, y + barH / 2);
  }
  noStroke();
  fill('dimgray');
  textSize(13);
  textAlign(LEFT, TOP);
  const axisY = cy0 + designs.length * (barH + gap);
  text(canvasWidth < 560 ? 'Total = sum of weight × score (max ' + maxTotal + ')' :
    'Weighted total = sum of (weight × score). Longest possible bar = ' + maxTotal, cx0, axisY);

  // winner and sensitivity
  let ty = axisY + 26;
  textSize(16);
  if (m.tied) {
    fill('darkorange');
    text('Tie at the top: change a weight or score to break it.', 12, ty);
  } else {
    fill('darkgreen');
    text('Winner: ' + designs[m.winner] + ' with ' + nf(m.totals[m.winner], 1, m.totals[m.winner] % 1 === 0 ? 0 : 1) + ' points', 12, ty);
  }
  ty += 22;
  fill('black');
  textSize(14);
  if (sensText.length) {
    for (const line of sensText) {
      text(line, 12, ty, canvasWidth - 24);
      ty += textWidth(line) > canvasWidth - 24 ? 36 : 18;
    }
  } else {
    fill('dimgray');
    text('Press Sensitivity to see how close the decision is.', 12, ty);
  }

  // ---------- Matrix headers and labels in the control region ----------
  noStroke();
  fill('black');
  textSize(15);
  textStyle(BOLD);
  textAlign(LEFT, CENTER);
  text('Criterion', 10, drawHeight + 18);
  textAlign(CENTER, CENTER);
  text('Weight', sliderX + sliderW / 2 + 16, drawHeight + 18);
  textSize(constrain(colW / 5.5, 11, 15));
  for (let d = 0; d < designs.length; d++) {
    fill(DESIGN_COLORS[d]);
    const name = colW < 85 ? designs[d].split(' ')[0] : designs[d];
    text(name, colX0 + d * colW + colW / 2, drawHeight + 18);
  }
  textStyle(NORMAL);
  textSize(canvasWidth < 560 ? 13 : 15);
  for (let r = 0; r < CRITERIA.length; r++) {
    const y = drawHeight + 38 + r * 36 + 9;
    fill('black');
    textAlign(LEFT, CENTER);
    text(CRITERIA[r], 10, y);
    text(nf(Number(weightSliders[r].value()), 1, 1), sliderX + sliderW + 6, y);
    if (r < CRITERIA.length - 1) {
      stroke(235);
      line(8, y + 18, canvasWidth - 8, y + 18);
      noStroke();
    }
  }
  const by = drawHeight + 38 + CRITERIA.length * 36 + 4;
  fill('black');
  textAlign(LEFT, CENTER);
  text('Preset:', 10, by + 10);
}

function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
  layoutControls();
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) {
    canvasWidth = Math.floor(container.getBoundingClientRect().width);
  }
}
