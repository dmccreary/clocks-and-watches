// HSV Color Wheel MicroSim
// CANVAS_HEIGHT: 600
// Hue is an angle around the wheel (0 = red at 12 o'clock, clockwise like a clock),
// saturation is the distance from the center, and value is the brightness.
// Colors are computed with the same integer hsv_to_rgb() function as the
// MicroPython code in Chapter 16, and a 12-pixel virtual NeoPixel ring shows
// the rainbow from the 16-rainbow-ring.py program.

// ---- Layout ----
let canvasWidth = 400;
let drawHeight = 450;
let controlHeight = 150;          // 4 rows x 35 + 10
let canvasHeight = drawHeight + controlHeight;
let margin = 10;
let sliderLeftMargin = 150;
let defaultTextSize = 16;

// ---- Controls ----
let hueSlider, satSlider, valSlider, rotateButton;

// ---- State ----
let isRunning = false;            // the Rotate animation opens paused
let offset = 0;                   // rainbow offset in degrees, as in the rainbow program
let offsetTimer = 0;
let wheelImg = null;
let wheelKey = '';                // size and value the wheel image was drawn for
let wheel = { cx: 0, cy: 0, r: 100 };
let dragging = false;
const RING_N = 12;

// The integer conversion from Chapter 16 (h: 0-359, s and v: 0-255)
function hsvToRgb(h, s, v) {
  if (s === 0) return [v, v, v];
  const region = Math.floor(h / 60);
  const rem = Math.floor((h % 60) * 255 / 60);
  const p = Math.floor(v * (255 - s) / 255);
  const q = Math.floor(v * (255 - Math.floor(s * rem / 255)) / 255);
  const t = Math.floor(v * (255 - Math.floor(s * (255 - rem) / 255)) / 255);
  if (region === 0) return [v, t, p];
  if (region === 1) return [q, v, p];
  if (region === 2) return [p, v, t];
  if (region === 3) return [p, q, v];
  if (region === 4) return [t, p, v];
  return [v, p, q];
}

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));
  textSize(defaultTextSize);

  hueSlider = createSlider(0, 359, 30, 1);
  satSlider = createSlider(0, 255, 255, 1);
  valSlider = createSlider(0, 255, 200, 1);
  [hueSlider, satSlider, valSlider].forEach((s, i) => {
    s.position(sliderLeftMargin, drawHeight + 8 + i * 35);
    s.size(canvasWidth - sliderLeftMargin - 25);
  });

  rotateButton = createButton('Rotate');
  rotateButton.position(10, drawHeight + 113);
  rotateButton.mousePressed(() => {
    isRunning = !isRunning;
    rotateButton.html(isRunning ? 'Stop' : 'Rotate');
    offsetTimer = millis();
  });

  describe('A color wheel where hue is the angle and saturation is the distance from the center, with a ' +
    'draggable marker and a swatch of the chosen color. Readouts show the RGB values from the integer ' +
    'hsv_to_rgb function and the matching NeoPixel code line. A ring of 12 virtual pixels shows a rainbow.');
}

// Draw the wheel into an image once per size/value change (it is slow to compute per frame)
function buildWheel(d, v) {
  const key = d + ':' + v;
  if (key === wheelKey && wheelImg) return;
  wheelKey = key;
  wheelImg = createImage(d, d);
  wheelImg.loadPixels();
  const R = d / 2;
  for (let y = 0; y < d; y++) {
    for (let x = 0; x < d; x++) {
      const dx = x - R + 0.5, dy = y - R + 0.5;
      const rr = Math.sqrt(dx * dx + dy * dy);
      const idx = 4 * (y * d + x);
      if (rr > R) { wheelImg.pixels[idx + 3] = 0; continue; }
      let ang = Math.atan2(dx, -dy) * 180 / Math.PI;   // 0 at top, clockwise
      if (ang < 0) ang += 360;
      const c = hsvToRgb(Math.floor(ang) % 360, Math.min(255, Math.floor(rr / R * 255)), v);
      wheelImg.pixels[idx] = c[0];
      wheelImg.pixels[idx + 1] = c[1];
      wheelImg.pixels[idx + 2] = c[2];
      wheelImg.pixels[idx + 3] = 255;
    }
  }
  wheelImg.updatePixels();
}

function draw() {
  updateCanvasSize();

  // Rotate: add 5 degrees every 40 ms, like offset = (offset + 5) % 360 with sleep_ms(40)
  if (isRunning) {
    while (millis() - offsetTimer >= 40) {
      offset = (offset + 5) % 360;
      offsetTimer += 40;
    }
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
  text('HSV Color Wheel', canvasWidth / 2, 8);

  const h = hueSlider.value(), s = satSlider.value(), v = valSlider.value();
  const rgb = hsvToRgb(h, s, v);
  const wide = canvasWidth >= 600;

  // ---- Layout ----
  let d, ringCx, ringCy, ringR, colX, colY, colW;
  if (wide) {
    d = 290;
    wheel = { cx: margin + 15 + d / 2, cy: 45 + d / 2, r: d / 2 };
    colX = wheel.cx + d / 2 + 25; colY = 42; colW = canvasWidth - colX - margin;
    ringR = 62; ringCx = colX + colW / 2; ringCy = drawHeight - ringR - 32;
  } else {
    d = 170;
    wheel = { cx: margin + 5 + d / 2, cy: 40 + d / 2, r: d / 2 };
    ringR = 56; ringCx = (wheel.cx + d / 2 + canvasWidth) / 2; ringCy = wheel.cy;
    colX = margin; colY = 40 + d + 14; colW = canvasWidth - 2 * margin;
  }

  // ---- Wheel and marker ----
  buildWheel(d, v);
  image(wheelImg, wheel.cx - d / 2, wheel.cy - d / 2);
  noFill();
  stroke('gray');
  circle(wheel.cx, wheel.cy, d);
  // Hue labels
  noStroke();
  fill('dimgray');
  textSize(12);
  textAlign(CENTER, CENTER);
  for (const a of [0, 120, 240]) {
    const lx = wheel.cx + (wheel.r + 10) * sin(radians(a)), ly = wheel.cy - (wheel.r + 10) * cos(radians(a));
    text(a, lx, ly);
  }
  const mr = s / 255 * wheel.r;
  const mx = wheel.cx + mr * sin(radians(h)), my = wheel.cy - mr * cos(radians(h));
  stroke('black');
  strokeWeight(2);
  line(wheel.cx, wheel.cy, mx, my);
  fill(rgb[0], rgb[1], rgb[2]);
  stroke('white');
  strokeWeight(3);
  circle(mx, my, 18);
  stroke('black');
  strokeWeight(1);
  noFill();
  circle(mx, my, 22);

  // ---- 12-pixel ring ----
  drawRing(ringCx, ringCy, ringR, s, v);

  // ---- Swatch and readouts ----
  let y = colY;
  const swH = wide ? 56 : 40;
  const swW = wide ? colW : 90;
  stroke('gray');
  fill(rgb[0], rgb[1], rgb[2]);
  rect(colX, y, swW, swH, 6);
  noStroke();
  textAlign(LEFT, TOP);
  const tx = wide ? colX : colX + swW + 10;
  const tw = wide ? colW : colW - swW - 10;
  if (wide) y += swH + 8;
  textSize(wide ? 16 : 14);
  fill('black');
  text('R = ' + rgb[0] + '   G = ' + rgb[1] + '   B = ' + rgb[2], tx, y, tw);
  y += wide ? 24 : 20;
  fill('indigo');
  textSize(wide ? 15 : 13);
  text('np[i] = (' + rgb.join(', ') + ')', tx, y, tw);
  y += wide ? 24 : (swH - 20 + 10);
  if (!wide) y = colY + swH + 8;

  // The steps inside hsv_to_rgb, so students can follow the integer math
  const region = Math.floor(h / 60), rem = Math.floor((h % 60) * 255 / 60);
  fill('dimgray');
  textSize(wide ? 14 : 12);
  const regionNames = ['red to yellow', 'yellow to green', 'green to cyan', 'cyan to blue', 'blue to magenta', 'magenta to red'];
  text('region = ' + h + ' // 60 = ' + region + ' (' + regionNames[region] + ')', wide ? colX : colX, y, colW);
  y += wide ? 20 : 17;
  text('rem = (' + h + ' % 60) * 255 // 60 = ' + rem, colX, y, colW);
  y += wide ? 20 : 17;
  text('p = v(255 - s)/255 = ' + Math.floor(v * (255 - s) / 255) + ' (the lowest channel)', colX, y, colW);
  y += wide ? 26 : 20;
  fill('black');
  textSize(wide ? 14 : 12);
  text('Ring: hue = (i * 360 // 12 + offset) % 360, offset = ' + offset + (isRunning ? ' (rotating)' : ''), colX, y, colW);

  // ---- Control labels ----
  noStroke();
  fill('black');
  textAlign(LEFT, CENTER);
  textSize(defaultTextSize);
  text('Hue: ' + h + '°', 10, drawHeight + 18);
  text('Saturation: ' + s, 10, drawHeight + 53);
  text('Value: ' + v, 10, drawHeight + 88);
  if (canvasWidth >= 600) {
    textSize(14);
    fill('dimgray');
    text('Drag the marker on the wheel to set hue and saturation.', 100, drawHeight + 125);
  }
}

function drawRing(cx, cy, R, s, v) {
  // Pixel 0 at the top (12 o'clock), numbered clockwise like the ring in the chapter
  noFill();
  stroke(60);
  strokeWeight(14);
  circle(cx, cy, 2 * R);
  strokeWeight(1);
  const pd = R * 0.42;
  for (let i = 0; i < RING_N; i++) {
    const hue = (Math.floor(i * 360 / RING_N) + offset) % 360;
    const c = hsvToRgb(hue, s, v);
    const a = radians(i * 360 / RING_N);
    const x = cx + R * sin(a), y = cy - R * cos(a);
    stroke('black');
    fill(c[0], c[1], c[2]);
    circle(x, y, pd);
    noStroke();
    fill('black');
    textAlign(CENTER, CENTER);
    textSize(10);
    text(i, cx + (R - pd * 0.95) * sin(a), cy - (R - pd * 0.95) * cos(a));
  }
  noStroke();
  fill('black');
  textSize(12);
  textAlign(CENTER, CENTER);
  text('12-pixel\nring', cx, cy);
}

// ---- Dragging the marker on the wheel ----
function setFromMouse() {
  const dx = mouseX - wheel.cx, dy = mouseY - wheel.cy;
  let ang = degrees(Math.atan2(dx, -dy));
  if (ang < 0) ang += 360;
  hueSlider.value(Math.floor(ang) % 360);
  satSlider.value(Math.min(255, Math.round(Math.sqrt(dx * dx + dy * dy) / wheel.r * 255)));
}

function mousePressed() {
  if (dist(mouseX, mouseY, wheel.cx, wheel.cy) <= wheel.r) {
    dragging = true;
    setFromMouse();
  }
}

function mouseDragged() {
  if (dragging) setFromMouse();
}

function mouseReleased() {
  dragging = false;
}

function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
  [hueSlider, satSlider, valSlider].forEach(s => s.size(canvasWidth - sliderLeftMargin - 25));
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) canvasWidth = Math.floor(container.getBoundingClientRect().width);
}
