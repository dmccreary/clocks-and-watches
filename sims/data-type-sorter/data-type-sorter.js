// Data Type Sorter MicroSim
// CANVAS_HEIGHT: 465
// Students drag Python value cards into the bin for their data type
// (int, float, str, bool, list, tuple). Correct drops turn green; wrong
// drops bounce back with a hint about what to look for.

let canvasWidth = 400;
let drawHeight = 420;
let controlHeight = 45;
let canvasHeight = drawHeight + controlHeight;
let margin = 15;
let defaultTextSize = 16;

// The six bins, with the clue students should look for
const TYPES = ['int', 'float', 'str', 'bool', 'list', 'tuple'];
const HINTS = {
  int: 'A whole number with no decimal point and no quotes is an int.',
  float: 'Look for a decimal point (or an e). That makes it a float.',
  str: 'Look for quote marks. Anything inside quotes is a str, even digits.',
  bool: 'True and False, capitalized and without quotes, are bool values.',
  list: 'Square brackets [ ] make a list.',
  tuple: 'Round parentheses with commas make a tuple.'
};
const BIN_COLORS = {
  int: 'steelblue', float: 'darkorange', str: 'seagreen',
  bool: 'mediumpurple', list: 'firebrick', tuple: 'teal'
};

// The deck: tricky cards ("42" in quotes, 3.0, "True") are included on purpose
const DECK = [
  { text: '42', type: 'int' },
  { text: '3.0', type: 'float' },
  { text: '"12:00"', type: 'str' },
  { text: 'True', type: 'bool' },
  { text: '[1, 2, 3]', type: 'list' },
  { text: '(2026, 9, 28)', type: 'tuple' },
  { text: '"42"', type: 'str' },
  { text: '-7', type: 'int' },
  { text: '0.5', type: 'float' },
  { text: 'False', type: 'bool' },
  { text: '"True"', type: 'str' },
  { text: '[]', type: 'list' },
  { text: '(14, 5)', type: 'tuple' },
  { text: '1e3', type: 'float' },
  { text: '60', type: 'int' },
  { text: '["Mon", "Tue"]', type: 'list' }
];

let deck = [];          // shuffled copy of DECK still to be sorted
let card = null;        // the card on top: {text, type, x, y, homeX, homeY}
let dragging = false;
let dragOffsetX = 0, dragOffsetY = 0;
let returning = false;  // card is sliding back after a wrong drop
let wrongThisCard = false;
let score = 0;          // cards sorted correctly on the first try
let sorted = 0;         // cards sorted so far
let streak = 0;
let bestStreak = 0;
let binCounts = {};
let binItems = {};     // bin name -> values sorted into it
let binFlash = {};      // bin name -> frame count left for a flash
let flashColor = {};
let message = 'Drag the card into the bin for its data type, or click a bin.';
let messageColor = 'black';
let restartButton;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));

  restartButton = createButton('Shuffle and Restart');
  restartButton.position(10, drawHeight + 10);
  restartButton.mousePressed(restart);

  restart();
  describe('A data type sorting game. A card shows a Python value such as 3.0 or "42". ' +
    'Drag the card into one of six bins labeled int, float, str, bool, list and tuple. ' +
    'Correct answers turn green and add to the score; wrong answers show a hint.', LABEL);
}

function restart() {
  deck = shuffle(DECK.slice());
  score = 0; sorted = 0; streak = 0; bestStreak = 0;
  binCounts = {}; binFlash = {}; flashColor = {};
  binItems = {};
  for (const t of TYPES) { binCounts[t] = 0; binItems[t] = []; }
  message = 'Drag the card into the bin for its data type, or click a bin.';
  messageColor = 'black';
  nextCard();
}

function nextCard() {
  wrongThisCard = false;
  dragging = false;
  returning = false;
  if (deck.length === 0) { card = null; return; }
  const c = deck[deck.length - 1];
  const home = cardHome();
  card = { text: c.text, type: c.type, x: home.x, y: home.y };
}

// ---------- layout helpers ----------
function cardHome() {
  return { x: canvasWidth / 2, y: 125 };
}

function cardSize() {
  return { w: min(220, canvasWidth - 120), h: 60 };
}

// Bins: one row of six when wide, two rows of three when narrow
function binRects() {
  const rects = [];
  const twoRows = canvasWidth < 560;
  const cols = twoRows ? 3 : 6;
  const gap = 8;
  const top = 245;
  const areaH = drawHeight - top - 10;
  const rows = twoRows ? 2 : 1;
  const w = (canvasWidth - 2 * margin - (cols - 1) * gap) / cols;
  const h = (areaH - (rows - 1) * gap) / rows;
  for (let i = 0; i < TYPES.length; i++) {
    const r = floor(i / cols), c = i % cols;
    rects.push({ type: TYPES[i], x: margin + c * (w + gap), y: top + r * (h + gap), w: w, h: h });
  }
  return rects;
}

function binAt(px, py) {
  for (const b of binRects()) {
    if (px >= b.x && px <= b.x + b.w && py >= b.y && py <= b.y + b.h) return b.type;
  }
  return null;
}

// ---------- drawing ----------
function draw() {
  updateCanvasSize();

  // drawing region and control region backgrounds
  stroke('silver');
  strokeWeight(1);
  fill('aliceblue');
  rect(0, 0, canvasWidth, drawHeight);
  fill('white');
  rect(0, drawHeight, canvasWidth, controlHeight);

  // title
  noStroke();
  fill('black');
  textAlign(CENTER, TOP);
  textSize(24);
  text('Data Type Sorter', canvasWidth / 2, 10);

  // score line
  textSize(16);
  textAlign(CENTER, TOP);
  fill('dimgray');
  text('Score: ' + score + ' / ' + sorted + '    Streak: ' + streak +
    '    Best: ' + bestStreak + '    Cards left: ' + deck.length, canvasWidth / 2, 42);

  drawBins();
  drawStack();
  drawMessage();
  drawCard();

  // slide the card home after a wrong drop
  if (returning && card) {
    const home = cardHome();
    card.x = lerp(card.x, home.x, 0.25);
    card.y = lerp(card.y, home.y, 0.25);
    if (dist(card.x, card.y, home.x, home.y) < 1) {
      card.x = home.x; card.y = home.y; returning = false;
    }
  } else if (card && !dragging) {
    // keep the card centered when the window is resized
    const home = cardHome();
    card.x = home.x; card.y = home.y;
  }

  // control area label
  noStroke();
  fill('black');
  textSize(16);
  textAlign(LEFT, CENTER);
  if (canvasWidth >= 560) {
    text('16 cards. Tricky ones are included on purpose.', 175, drawHeight + 22);
  }
}

function drawBins() {
  const hoverType = (dragging && card) ? binAt(mouseX, mouseY) : null;
  for (const b of binRects()) {
    let bg = 'white';
    if (binFlash[b.type] > 0) {
      bg = flashColor[b.type];
      binFlash[b.type]--;
    } else if (hoverType === b.type) {
      bg = 'lightyellow';
    }
    stroke(BIN_COLORS[b.type]);
    strokeWeight(hoverType === b.type ? 4 : 2);
    fill(bg);
    rect(b.x, b.y, b.w, b.h, 8);
    // colored header band with the type name
    noStroke();
    fill(BIN_COLORS[b.type]);
    rect(b.x + 2, b.y + 2, b.w - 4, 30, 6, 6, 0, 0);
    fill('white');
    textAlign(CENTER, CENTER);
    textSize(18);
    textStyle(BOLD);
    text(b.type, b.x + b.w / 2, b.y + 17);
    textStyle(NORMAL);
    // the values sorted into this bin so far (newest last)
    fill('black');
    const items = binItems[b.type];
    if (items.length === 0) {
      fill('gray');
      textSize(16);
      text('empty', b.x + b.w / 2, b.y + 32 + (b.h - 32) / 2);
    } else {
      const lineH = 20;
      const fit = max(1, floor((b.h - 40) / lineH));
      const shown = items.slice(-fit);
      textFont('monospace');
      for (let i = 0; i < shown.length; i++) {
        const label = (i === 0 && items.length > fit) ? '+' + (items.length - fit + 1) + ' more' : shown[i];
        // shrink long values (like a tuple) so they stay inside the bin
        let ts = b.w < 110 ? 13 : 15;
        textSize(ts);
        while (textWidth(label) > b.w - 10 && ts > 10) { ts--; textSize(ts); }
        text(label, b.x + b.w / 2, b.y + 46 + i * lineH);
      }
      textFont('sans-serif');
    }
  }
}

function drawStack() {
  if (!card) return;
  const s = cardSize();
  const home = cardHome();
  // shadow cards hint that there is a stack underneath
  const behind = min(deck.length - 1, 3);
  for (let i = behind; i >= 1; i--) {
    stroke('silver');
    strokeWeight(1);
    fill('whitesmoke');
    rect(home.x - s.w / 2 + i * 4, home.y - s.h / 2 + i * 4, s.w, s.h, 8);
  }
}

function drawCard() {
  if (!card) {
    noStroke();
    fill('darkgreen');
    textAlign(CENTER, CENTER);
    textSize(22);
    text('Deck complete! ' + score + ' of ' + sorted + ' right on the first try.',
      canvasWidth / 2, 120);
    textSize(16);
    fill('black');
    text('Press "Shuffle and Restart" to play again.', canvasWidth / 2, 150);
    return;
  }
  const s = cardSize();
  stroke(dragging ? 'goldenrod' : 'dimgray');
  strokeWeight(dragging ? 3 : 2);
  fill(wrongThisCard ? 'mistyrose' : 'white');
  rect(card.x - s.w / 2, card.y - s.h / 2, s.w, s.h, 8);
  noStroke();
  fill('black');
  textAlign(CENTER, CENTER);
  textSize(24);
  textFont('monospace');
  textStyle(BOLD);
  text(card.text, card.x, card.y);
  textStyle(NORMAL);
  textFont('sans-serif');
}

function drawMessage() {
  noStroke();
  fill(messageColor);
  textAlign(CENTER, CENTER);
  textSize(16);
  // wrap the message inside a box under the card
  rectMode(CORNER);
  text(message, margin, 168, canvasWidth - 2 * margin, 70);
}

// ---------- interaction ----------
function mousePressed() {
  if (!card || returning) return;
  if (mouseY > drawHeight || mouseX < 0 || mouseX > canvasWidth) return;
  const s = cardSize();
  if (abs(mouseX - card.x) <= s.w / 2 && abs(mouseY - card.y) <= s.h / 2) {
    dragging = true;
    dragOffsetX = card.x - mouseX;
    dragOffsetY = card.y - mouseY;
    return;
  }
  // clicking a bin sends the card there (an alternative to dragging)
  const t = binAt(mouseX, mouseY);
  if (t) dropInto(t);
}

function mouseDragged() {
  if (dragging && card) {
    card.x = constrain(mouseX + dragOffsetX, 0, canvasWidth);
    card.y = constrain(mouseY + dragOffsetY, 0, drawHeight);
  }
}

function mouseReleased() {
  if (!dragging || !card) return;
  dragging = false;
  const t = binAt(mouseX, mouseY);
  if (t) {
    dropInto(t);
  } else {
    returning = true;
  }
}

function dropInto(binType) {
  if (binType === card.type) {
    binCounts[binType]++;
    binItems[binType].push(card.text);
    binFlash[binType] = 30;
    flashColor[binType] = 'palegreen';
    sorted++;
    if (!wrongThisCard) {
      score++;
      streak++;
      bestStreak = max(bestStreak, streak);
    }
    message = 'Correct! type(' + card.text + ') is <class \'' + card.type + '\'>.';
    messageColor = 'darkgreen';
    deck.pop();
    nextCard();
  } else {
    binFlash[binType] = 30;
    flashColor[binType] = 'mistyrose';
    if (!wrongThisCard) streak = 0;
    wrongThisCard = true;
    message = 'Not ' + binType + '. Hint: ' + HINTS[card.type];
    messageColor = 'firebrick';
    returning = true;
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
