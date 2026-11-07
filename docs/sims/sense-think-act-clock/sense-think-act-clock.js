// Sense-Think-Act Clock MicroSim
// CANVAS_HEIGHT: 520
// Students drag eight clock parts from a tray into three columns:
// Sensors (input), Microcontroller (think), and Actuators (output).
// A correct drop snaps the card into place with a green outline; a wrong
// drop slides the card back to the tray with a hint. When every card is
// placed, "Next step" traces one signal through sense -> think -> act.

// Canvas dimensions - REQUIRED structure
let canvasWidth = 400;
let drawHeight = 470;
let controlHeight = 50;
let canvasHeight = drawHeight + controlHeight;
let margin = 10;
let defaultTextSize = 16;

// Layout values (recomputed every frame from the canvas width)
const colTop = 44;
const colH = 218;
const infoTop = 268;
const infoH = 52;
const trayTop = 328;
let colGap, colW, cardW;
const cardH = 36;

const roles = ['sensor', 'controller', 'actuator'];
const roleNames = {
  sensor: ['Sensors (input)', 'Sensors'],
  controller: ['Microcontroller (think)', 'Controller'],
  actuator: ['Actuators (output)', 'Actuators']
};
const roleColors = { sensor: 'lightcyan', controller: 'lavender', actuator: 'lemonchiffon' };

// Card data. tip = hover text (matches the chapter's definitions);
// info = shown after a correct drop; clue = second hint after a wrong drop.
const cardData = [
  { id: 'button', label: 'Push button', role: 'sensor',
    tip: 'A switch that reports "pressed" or "not pressed" to the Pico.',
    info: 'Correct! A push button is a sensor: it sends "pressed" or "not pressed" to the Pico.',
    clue: 'When you press a button, which way does that news travel?' },
  { id: 'light', label: 'Light sensor', role: 'sensor',
    tip: 'Measures how bright the room is and reports it to the Pico.',
    info: 'Correct! A light sensor measures the room and sends a brightness reading to the Pico.',
    clue: 'A light sensor measures the room. Who needs to know the result?' },
  { id: 'rtc', label: 'DS3231 RTC', role: 'sensor',
    tip: 'A real-time clock chip that keeps time and reports it to the Pico.',
    info: 'Correct! The DS3231 real-time clock reports the current time to the Pico, so it is an input.',
    clue: 'The Pico asks the RTC "what time is it?" Which part answers?' },
  { id: 'pico', label: 'Raspberry Pi Pico', short: 'Pico', role: 'controller',
    tip: 'The microcontroller board that runs your program and makes decisions.',
    info: 'Correct! The Pico is the microcontroller: it runs the program that decides what to do.',
    clue: 'This part runs your program. It is the brain, not an input or output.' },
  { id: 'leddisp', label: 'LED display', role: 'actuator',
    tip: 'Seven-segment digits that light up to show numbers the Pico sends.',
    info: 'Correct! An LED display only receives digits from the Pico, so it is an actuator.',
    clue: 'A display shows the time, but where does it get the digits from?' },
  { id: 'oled', label: 'OLED screen', role: 'actuator',
    tip: 'A small screen that draws text and graphics the Pico sends to it.',
    info: 'Correct! The OLED draws whatever the Pico sends, so it is an actuator.',
    clue: 'A screen shows things. Does it tell the Pico anything, or just listen?' },
  { id: 'buzzer', label: 'Buzzer', role: 'actuator',
    tip: 'Makes a beep when the Pico sends it a signal, for example an alarm.',
    info: 'Correct! The buzzer turns a signal from the Pico into sound, so it is an actuator.',
    clue: 'A buzzer changes the world by making sound. Who tells it when?' },
  { id: 'neopixel', label: 'NeoPixel strip', role: 'actuator',
    tip: 'A strip of color LEDs the Pico controls one pixel at a time.',
    info: 'Correct! The Pico sends colors to the NeoPixel strip, so it is an actuator.',
    clue: 'The strip glows in colors. Where do the color commands come from?' }
];

let cards = [];
let dragging = null;
let dragOffset = { x: 0, y: 0 };
let message = 'Drag each part from the tray into the column where it belongs.';
let messageColor = 'black';
let flowStep = 0;        // 0 = not started, 1..3 = sense/think/act
let flowAnim = null;     // {from:{x,y}, to:{x,y}, start}
let resetButton, nextButton;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));

  resetButton = createButton('Reset');
  resetButton.position(10, drawHeight + 12);
  resetButton.mousePressed(resetCards);

  nextButton = createButton('Next step');
  nextButton.position(80, drawHeight + 12);
  nextButton.mousePressed(nextFlowStep);
  nextButton.attribute('disabled', '');

  resetCards();
  describe('A drag-and-drop sorting activity with three columns labeled Sensors, Microcontroller, and Actuators. ' +
    'Eight clock parts start in a tray at the bottom. Correct drops snap into the column with a green outline; ' +
    'wrong drops return to the tray with a hint. After all parts are sorted, the Next step button traces a ' +
    'signal from the light sensor to the Pico to the LED display.', LABEL);
}

function resetCards() {
  const order = shuffle([...Array(cardData.length).keys()]);
  cards = cardData.map((d, i) => ({
    ...d, state: 'tray', home: order.indexOf(i), slot: -1, x: 0, y: 0, misses: 0, anim: null
  }));
  dragging = null;
  flowStep = 0;
  flowAnim = null;
  message = 'Drag each part from the tray into the column where it belongs.';
  messageColor = 'black';
  if (nextButton) nextButton.attribute('disabled', '');
}

function computeLayout() {
  colGap = canvasWidth >= 600 ? 44 : 22;
  colW = (canvasWidth - 2 * margin - 2 * colGap) / 3;
  const trayW = (canvasWidth - 2 * margin - 3 * 10) / 4;
  cardW = min(180, colW - 12, trayW);
}

function colX(r) {
  return margin + roles.indexOf(r) * (colW + colGap);
}

function homePos(card) {
  const r = floor(card.home / 4);
  const c = card.home % 4;
  const totalW = 4 * cardW + 3 * 10;
  const x0 = (canvasWidth - totalW) / 2;
  return { x: x0 + c * (cardW + 10), y: trayTop + 30 + r * (cardH + 14) };
}

function slotPos(card) {
  return { x: colX(card.role) + (colW - cardW) / 2, y: colTop + 34 + card.slot * (cardH + 8) };
}

function cardPos(card) {
  if (card.state === 'drag') return { x: card.x, y: card.y };
  if (card.state === 'placed') return slotPos(card);
  if (card.state === 'return' && card.anim) {
    const t = constrain((millis() - card.anim.start) / 350, 0, 1);
    const h = homePos(card);
    if (t >= 1) { card.state = 'tray'; card.anim = null; return h; }
    const e = 1 - pow(1 - t, 3);
    return { x: lerp(card.anim.x, h.x, e), y: lerp(card.anim.y, h.y, e) };
  }
  return homePos(card);
}

function draw() {
  updateCanvasSize();
  computeLayout();

  // Backgrounds
  stroke('silver');
  strokeWeight(1);
  fill('aliceblue');
  rect(0, 0, canvasWidth, drawHeight);
  fill('white');
  rect(0, drawHeight, canvasWidth, controlHeight);

  // Title
  noStroke();
  fill('black');
  textAlign(CENTER, TOP);
  textSize(canvasWidth >= 600 ? 22 : 17);
  text('Sense, Think, Act: Sort the Clock Parts', canvasWidth / 2, 10);

  drawColumns();
  drawInfoStrip();
  drawTray();

  // Cards: placed and tray cards first, the dragged card last (on top)
  for (const c of cards) if (c !== dragging) drawCard(c);
  if (dragging) drawCard(dragging);

  drawFlowDot();
  drawTooltip();

  // Control-area status
  noStroke();
  fill('dimgray');
  textAlign(LEFT, CENTER);
  textSize(15);
  const placed = cards.filter(c => c.state === 'placed').length;
  text('Placed: ' + placed + ' of 8', 180, drawHeight + 25);
}

function drawColumns() {
  for (const r of roles) {
    const x = colX(r);
    stroke('gray');
    strokeWeight(1);
    fill(roleColors[r]);
    rect(x, colTop, colW, colH, 10);
    noStroke();
    fill('black');
    textAlign(CENTER, TOP);
    textStyle(BOLD);
    textSize(canvasWidth >= 600 ? 16 : 14);
    text(roleNames[r][canvasWidth >= 700 ? 0 : 1], x + colW / 2, colTop + 8);
    textStyle(NORMAL);
  }
  // Arrows left to right between the columns
  const ay = colTop + colH / 2;
  for (let i = 0; i < 2; i++) {
    const x1 = margin + (i + 1) * colW + i * colGap + 4;
    const x2 = x1 + colGap - 8;
    stroke('slategray');
    strokeWeight(4);
    line(x1, ay, x2 - 6, ay);
    noStroke();
    fill('slategray');
    triangle(x2, ay, x2 - 10, ay - 8, x2 - 10, ay + 8);
  }
}

function drawInfoStrip() {
  stroke('silver');
  strokeWeight(1);
  fill(255, 255, 255, 235);
  rect(margin, infoTop, canvasWidth - 2 * margin, infoH, 8);
  noStroke();
  fill(messageColor);
  textAlign(LEFT, CENTER);
  textSize(canvasWidth >= 600 ? 15 : 13);
  text(message, margin + 10, infoTop + 4, canvasWidth - 2 * margin - 20, infoH - 8);
}

function drawTray() {
  noStroke();
  fill('dimgray');
  textAlign(LEFT, TOP);
  textSize(14);
  text('Parts tray', margin + 4, trayTop + 6);
  if (cards.length && cards.every(o => o.state === 'placed')) {
    fill('darkgreen');
    textAlign(CENTER, CENTER);
    textSize(18);
    text('All parts sorted. Sense, think, act!', canvasWidth / 2, trayTop + 70);
  }
}

function drawCard(c) {
  const p = cardPos(c);
  if (c.state !== 'placed') { c.x = p.x; c.y = p.y; }
  if (c.state === 'placed') {
    stroke('green');
    strokeWeight(3);
    fill('honeydew');
  } else {
    stroke(c === dragging ? 'royalblue' : 'gray');
    strokeWeight(c === dragging ? 2 : 1);
    fill('white');
  }
  rect(p.x, p.y, cardW, cardH, 6);
  noStroke();
  fill('black');
  textAlign(CENTER, CENTER);
  const label = (c.short && cardW < 130) ? c.short : c.label;
  let ts = 15;
  textSize(ts);
  while (textWidth(label) > cardW - 8 && ts > 10) { ts--; textSize(ts); }
  text(label, p.x + cardW / 2, p.y + cardH / 2);
  // The card the signal is visiting gets an orange outline
  if (flowStep > 0 && c.id === flowCards[flowStep - 1] && !flowAnim) {
    noFill();
    stroke('orangered');
    strokeWeight(3);
    rect(p.x - 3, p.y - 3, cardW + 6, cardH + 6, 8);
  }
}

function cardAt(mx, my, wantPlaced) {
  for (let i = cards.length - 1; i >= 0; i--) {
    const c = cards[i];
    if ((c.state === 'placed') !== wantPlaced) continue;
    const p = cardPos(c);
    if (mx >= p.x && mx <= p.x + cardW && my >= p.y && my <= p.y + cardH) return c;
  }
  return null;
}

function drawTooltip() {
  if (dragging || mouseY > drawHeight) return;
  const c = cardAt(mouseX, mouseY, true);
  if (!c) return;
  textSize(14);
  const w = min(textWidth(c.tip) + 16, canvasWidth - 2 * margin);
  const lines = ceil((textWidth(c.tip) + 16) / w);
  const h = 22 * lines;
  let x = constrain(mouseX + 12, margin, canvasWidth - margin - w);
  let y = mouseY + 18;
  if (y + h > drawHeight - 4) y = mouseY - h - 8;
  stroke('dimgray');
  strokeWeight(1);
  fill('lightyellow');
  rect(x, y, w, h, 5);
  noStroke();
  fill('black');
  textAlign(LEFT, CENTER);
  text(c.tip, x + 8, y + 2, w - 12, h - 4);
}

function mousePressed() {
  if (mouseY > drawHeight || mouseX < 0 || mouseX > canvasWidth) return;
  const c = cardAt(mouseX, mouseY, false);
  if (c) {
    dragging = c;
    const p = cardPos(c);
    dragOffset = { x: mouseX - p.x, y: mouseY - p.y };
    c.state = 'drag';
    c.x = p.x;
    c.y = p.y;
    cards.push(cards.splice(cards.indexOf(c), 1)[0]);   // bring to front
  }
}

function mouseDragged() {
  if (!dragging) return;
  dragging.x = constrain(mouseX - dragOffset.x, 0, canvasWidth - cardW);
  dragging.y = constrain(mouseY - dragOffset.y, 0, drawHeight - cardH);
  return false;
}

function mouseReleased() {
  if (!dragging) return;
  const c = dragging;
  dragging = null;
  const cx = c.x + cardW / 2;
  const cy = c.y + cardH / 2;
  let target = null;
  for (const r of roles) {
    const x = colX(r);
    if (cx >= x && cx <= x + colW && cy >= colTop && cy <= colTop + colH) target = r;
  }
  if (target === c.role) {
    c.state = 'placed';
    c.slot = cards.filter(o => o.state === 'placed' && o.role === c.role && o !== c).length;
    message = c.info;
    messageColor = 'darkgreen';
    if (cards.every(o => o.state === 'placed')) {
      message = 'All eight parts sorted! Press Next step to follow one signal through sense, think, act.';
      messageColor = 'darkgreen';
      nextButton.removeAttribute('disabled');
    }
  } else {
    c.state = 'return';
    c.anim = { x: c.x, y: c.y, start: millis() };
    if (target) {
      c.misses++;
      message = c.misses === 1
        ? 'Not quite. Does this part send data to the Pico or receive it?'
        : 'Hint: ' + c.clue;
      messageColor = 'firebrick';
    }
  }
}

// Worked example from the chapter: an auto-dimming clock
const flowText = [
  '',
  'Sense: the light sensor reports "the room is dark" to the Pico.',
  'Think: the Pico compares the reading to a limit and decides the display is too bright.',
  'Act: the Pico tells the LED display to lower its brightness. Press Next step to repeat the loop.'
];
const flowCards = ['light', 'pico', 'leddisp'];

function cardCenter(id) {
  const c = cards.find(o => o.id === id);
  const p = cardPos(c);
  return { x: p.x + cardW / 2, y: p.y - 2 };   // sit on the card's top edge, not over its label
}

function nextFlowStep() {
  if (!cards.every(o => o.state === 'placed')) return;
  const from = flowStep > 0 ? cardCenter(flowCards[flowStep - 1]) : null;
  flowStep = flowStep % 3 + 1;
  flowAnim = from ? { from, start: millis() } : null;
  message = flowText[flowStep];
  messageColor = 'midnightblue';
}

function drawFlowDot() {
  if (flowStep === 0) return;
  const to = cardCenter(flowCards[flowStep - 1]);
  let p = to;
  if (flowAnim) {
    const t = constrain((millis() - flowAnim.start) / 700, 0, 1);
    p = { x: lerp(flowAnim.from.x, to.x, t), y: lerp(flowAnim.from.y, to.y, t) };
    if (t >= 1) flowAnim = null;
  }
  noStroke();
  fill(255, 69, 0, 70);
  circle(p.x, p.y, 26);
  fill('orangered');
  circle(p.x, p.y, 12);
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
