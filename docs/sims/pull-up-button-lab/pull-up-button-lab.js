// Pull-Up Button Lab MicroSim
// CANVAS_HEIGHT: 470
// A schematic of GP14 with the Pico's internal pull-up resistor to 3.3 V and a
// push button to ground. Toggle the button and the pull-up to see the pin
// voltage and what button.value() returns. With the pull-up off and the button
// open, the input floats and its reading flickers randomly.

let canvasWidth = 400;
let drawHeight = 425;
let controlHeight = 45;
let canvasHeight = drawHeight + controlHeight;
let margin = 10;
let defaultTextSize = 16;

const VIH = 2.0;   // RP2040 reads 1 above about 2.0 V
const VIL = 0.8;   // and 0 below about 0.8 V
const R_PULLUP = 50000;

let pressed = false;
let pullUp = true;
let voltage = 3.3;
let reading = 1;
let readings = [];      // recent value() readings for the strip chart
let frameCounter = 0;

let pressButton, pullCheckbox;

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));

  pressButton = createButton('Press button');
  pressButton.position(10, drawHeight + 10);
  pressButton.mousePressed(() => {
    pressed = !pressed;
    pressButton.html(pressed ? 'Release button' : 'Press button');
  });

  pullCheckbox = createCheckbox(' Internal pull-up (Pin.PULL_UP)', true);
  pullCheckbox.position(140, drawHeight + 12);
  pullCheckbox.changed(() => { pullUp = pullCheckbox.checked(); });

  for (let i = 0; i < 40; i++) readings.push(1);
  describe('A circuit diagram: GP14 connects through the internal pull-up resistor to 3.3 volts and ' +
    'through a push button to ground. A voltage bar and a value() readout show the pin state. ' +
    'With the pull-up off and the button open, the voltage jumps around and the reading flickers.', LABEL);
}

// Work out the pin voltage and the digital reading for the current switches
function updatePin() {
  if (pressed) {
    voltage = 0;                    // the button shorts the pin to ground
  } else if (pullUp) {
    voltage = 3.3;                  // no current flows, so no voltage drop
  } else {
    // floating: the voltage wanders with noise picked up from the room
    if (frameCounter % 3 === 0) {
      voltage += (1.65 - voltage) * 0.15 + random(-0.7, 0.7);
      if (random() < 0.08) voltage = random(0, 3.3);
      voltage = constrain(voltage, 0, 3.3);
    }
  }
  // the input has hysteresis: in the middle zone it keeps its last answer
  if (voltage >= VIH) reading = 1;
  else if (voltage <= VIL) reading = 0;
  else if (!pullUp && !pressed && random() < 0.1) reading = 1 - reading;
}

function draw() {
  updateCanvasSize();
  frameCounter++;
  updatePin();
  // sample value() ten times a second, like the chapter's loop with sleep(0.1)
  if (frameCounter % 6 === 0) {
    readings.push(reading);
    if (readings.length > 40) readings.shift();
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
  textSize(24);
  text('Pull-Up Button Lab', canvasWidth / 2, 8);

  // the configuration line, as it would appear in the program
  textFont('monospace');
  textSize(canvasWidth < 500 ? 13 : 15);
  fill('darkblue');
  text(pullUp ? 'button = Pin(14, Pin.IN, Pin.PULL_UP)' : 'button = Pin(14, Pin.IN)   # no pull',
    canvasWidth / 2, 38);
  textFont('sans-serif');

  const colW = canvasWidth < 600 ? canvasWidth * 0.58 : canvasWidth * 0.55;
  drawSchematic(colW);
  drawMeter(colW);
  drawExplanation();
}

function drawSchematic(colW) {
  const nx = max(colW * 0.38, 112);  // x of the vertical wire
  const top = 78, nodeY = 205, gndY = 312;
  const wireOn = color('black');
  const wireOff = color(170);
  const live = voltage > VIH ? color('crimson') : (voltage < VIL ? color('black') : color('darkorange'));

  // dashed box: parts inside the Pico
  stroke('steelblue');
  strokeWeight(1);
  drawingContext.setLineDash([6, 5]);
  noFill();
  rect(nx - 60, top - 20, colW - (nx - 60) - 6, nodeY - top + 52, 8);
  drawingContext.setLineDash([]);
  noStroke();
  fill('steelblue');
  textSize(13);
  textAlign(RIGHT, TOP);
  text('inside the Pico', colW - 12, top - 16);

  // 3.3 V supply
  stroke('crimson');
  strokeWeight(3);
  line(nx - 22, top, nx + 22, top);
  noStroke();
  fill('crimson');
  textSize(16);
  textAlign(RIGHT, CENTER);
  text('3.3 V', nx - 28, top);

  // pull-up enable switch (closed when PULL_UP is on)
  stroke(pullUp ? wireOn : wireOff);
  strokeWeight(2);
  line(nx, top, nx, top + 14);
  fill('white');
  circle(nx, top + 16, 5);
  circle(nx, top + 40, 5);
  if (pullUp) line(nx, top + 18, nx, top + 38);
  else line(nx, top + 18, nx + 16, top + 34);
  noStroke();
  fill(pullUp ? 'darkgreen' : 'gray');
  textSize(13);
  textAlign(LEFT, CENTER);
  text(pullUp ? 'PULL_UP on' : 'PULL_UP off', nx + 12, top + 26);

  // resistor zigzag
  stroke(pullUp ? wireOn : wireOff);
  strokeWeight(2);
  noFill();
  const rTop = top + 44, rBot = nodeY - 22;
  line(nx, top + 42, nx, rTop + 6);
  beginShape();
  vertex(nx, rTop + 6);
  const zig = 8;
  for (let i = 0; i < zig; i++) {
    vertex(nx + (i % 2 === 0 ? 10 : -10), rTop + 6 + (i + 0.5) * (rBot - rTop - 12) / zig);
  }
  vertex(nx, rBot - 6);
  endShape();
  line(nx, rBot - 6, nx, nodeY);
  noStroke();
  fill(pullUp ? 'black' : 'gray');
  textSize(14);
  textAlign(LEFT, CENTER);
  text('about 50 kΩ', nx + 16, (rTop + rBot) / 2);

  // node and wire to the input buffer
  stroke(live);
  strokeWeight(3);
  line(nx, nodeY, colW - 70, nodeY);
  noStroke();
  fill(live);
  circle(nx, nodeY, 10);
  // GP14 pad on the box edge
  fill('gold');
  stroke('goldenrod');
  strokeWeight(1);
  rect(nx - 66, nodeY - 9, 18, 18, 3);
  noStroke();
  fill('black');
  textSize(14);
  textAlign(RIGHT, CENTER);
  text('GP14', nx - 70, nodeY);
  // input buffer triangle and value()
  const bx = colW - 70;
  stroke('black');
  strokeWeight(2);
  fill('white');
  triangle(bx, nodeY - 14, bx, nodeY + 14, bx + 24, nodeY);
  noStroke();
  fill('black');
  textSize(14);
  textAlign(LEFT, CENTER);
  text('value()', bx + 26, nodeY - 18);

  // wire from node down to the button
  stroke(pressed ? 'black' : wireOff);
  strokeWeight(2);
  line(nx, nodeY, nx, nodeY + 34);
  // push button symbol
  const by1 = nodeY + 34, by2 = nodeY + 70;
  fill('white');
  stroke('black');
  circle(nx, by1, 6);
  circle(nx, by2, 6);
  strokeWeight(3);
  if (pressed) line(nx - 2, by1 + 3, nx - 2, by2 - 3);
  else line(nx - 2, by1 + 3, nx - 22, by2 - 6);
  strokeWeight(2);
  line(nx - 34, by1 - 6, nx - 34, by2 + 6);       // little press bar
  line(nx - 34, (by1 + by2) / 2, nx - 14, (by1 + by2) / 2);
  noStroke();
  fill(pressed ? 'darkgreen' : 'black');
  textSize(14);
  textAlign(LEFT, CENTER);
  text(pressed ? 'button pressed' : 'button open', nx + 12, (by1 + by2) / 2);
  // ground
  stroke('black');
  strokeWeight(2);
  line(nx, by2 + 3, nx, gndY);
  line(nx - 18, gndY, nx + 18, gndY);
  line(nx - 11, gndY + 6, nx + 11, gndY + 6);
  line(nx - 4, gndY + 12, nx + 4, gndY + 12);
  noStroke();
  fill('black');
  textAlign(LEFT, CENTER);
  text('GND (0 V)', nx + 24, gndY + 4);

  // current arrow when current flows
  if (pressed && pullUp) {
    fill('darkorange');
    textSize(13);
    textAlign(RIGHT, CENTER);
    const uA = round(3.3 / R_PULLUP * 1e6);
    text('current ' + uA + ' µA ↓', nx - 14, (rTop + rBot) / 2);
  }
}

function drawMeter(colW) {
  const x0 = colW + 10;
  const w = canvasWidth - x0 - margin;
  // value() readout
  stroke('silver');
  strokeWeight(1);
  fill('white');
  rect(x0, 62, w, 64, 8);
  noStroke();
  fill('black');
  textFont('monospace');
  textSize(15);
  textAlign(LEFT, CENTER);
  text('button.value()', x0 + 10, 80);
  textSize(30);
  textStyle(BOLD);
  fill(reading === 1 ? 'crimson' : 'black');
  text(reading, x0 + 10, 108);
  textStyle(NORMAL);
  textFont('sans-serif');
  textSize(14);
  fill('dimgray');
  const floating = !pullUp && !pressed;
  const wideBox = w > 200;
  const note = floating ? (wideBox ? 'floating: random!' : 'random!') : (reading === 1 ? (wideBox ? 'high (not pressed)' : 'high') :
    (wideBox ? 'low (pressed)' : 'low'));
  text(note, x0 + 38, 110);

  // voltage bar
  const barX = x0 + 4, barY = 150, barW = 34, barH = 160;
  stroke('gray');
  fill('white');
  rect(barX, barY, barW, barH);
  // the middle zone where the reading is not guaranteed
  noStroke();
  fill(255, 165, 0, 50);
  const yVIH = barY + barH * (1 - VIH / 3.3), yVIL = barY + barH * (1 - VIL / 3.3);
  rect(barX, yVIH, barW, yVIL - yVIH);
  const level = barH * voltage / 3.3;
  fill(voltage > VIH ? 'crimson' : (voltage < VIL ? 'dimgray' : 'darkorange'));
  rect(barX + 3, barY + barH - level, barW - 6, level);
  // labels
  fill('black');
  textSize(13);
  textAlign(LEFT, CENTER);
  text('3.3 V', barX + barW + 5, barY);
  text('0 V', barX + barW + 5, barY + barH);
  stroke('darkorange');
  line(barX - 2, yVIH, barX + barW + 2, yVIH);
  line(barX - 2, yVIL, barX + barW + 2, yVIL);
  noStroke();
  fill('darkorange');
  text('2.0 V', barX + barW + 5, yVIH);
  text('0.8 V', barX + barW + 5, yVIL);
  fill('black');
  textSize(14);
  textAlign(LEFT, TOP);
  text('Pin voltage: ' + voltage.toFixed(2) + ' V', x0, barY + barH + 8);

  // strip chart of recent readings (wide screens only)
  const sx = barX + barW + 50, sw = canvasWidth - margin - sx - 4;
  if (sw > 90) {
    stroke('silver');
    fill('white');
    rect(sx, barY, sw, barH);
    noStroke();
    fill('black');
    textSize(13);
    textAlign(CENTER, BOTTOM);
    text('value() over the last 4 s', sx + sw / 2, barY - 2);
    stroke('royalblue');
    strokeWeight(2);
    noFill();
    beginShape();
    for (let i = 0; i < readings.length; i++) {
      const px = sx + 6 + i * (sw - 12) / (readings.length - 1);
      const py = readings[i] === 1 ? barY + 30 : barY + barH - 30;
      if (i > 0) vertex(px, readings[i - 1] === 1 ? barY + 30 : barY + barH - 30);
      vertex(px, py);
    }
    endShape();
    strokeWeight(1);
    noStroke();
    fill('dimgray');
    textAlign(LEFT, CENTER);
    text('1', sx + 2, barY + 18);
    text('0', sx + 2, barY + barH - 18);
  }
}

function drawExplanation() {
  let msg;
  if (pullUp && !pressed) {
    msg = 'The pull-up joins GP14 to 3.3 V through about 50 kΩ. No current flows, so there is no ' +
      'voltage drop: the pin rests at 3.3 V and value() is 1.';
  } else if (pullUp && pressed) {
    msg = 'The button joins GP14 straight to ground. A tiny current flows through the resistor, the pin ' +
      'drops to 0 V and value() is 0. Pressed reads 0: this is called active low.';
  } else if (!pullUp && pressed) {
    msg = 'The button holds GP14 at 0 V, so value() is 0. But nothing will pull the pin back up when you ' +
      'let go. Press Release button to see what happens.';
  } else {
    msg = 'Nothing connects GP14 to a voltage, so the input is floating. It picks up electrical noise and ' +
      'value() flips between 0 and 1 by itself. Turn the pull-up back on to fix it.';
  }
  stroke('silver');
  strokeWeight(1);
  fill('white');
  rect(margin, 340, canvasWidth - 2 * margin, drawHeight - 348, 8);
  noStroke();
  fill(!pullUp && !pressed ? 'firebrick' : 'black');
  textSize(16);
  textAlign(LEFT, TOP);
  text(msg, margin + 10, 348, canvasWidth - 2 * margin - 20);
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
