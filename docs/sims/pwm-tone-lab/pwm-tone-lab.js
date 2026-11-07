// PWM Tone Lab MicroSim
// CANVAS_HEIGHT: 560
// Frequency sets the pitch of a PWM square wave; duty cycle sets how long each cycle is on.
// An oscilloscope trace, a piano keyboard and the note formula f = 440 x 2^(n/12) update live.
// Sound plays only after the learner presses Play (browsers require a click for audio).
// The trace is still until Play is pressed; while the tone plays the trace slowly scrolls.

let canvasWidth = 400;
let drawHeight = 445;
let controlHeight = 115;
let canvasHeight = drawHeight + controlHeight;
let margin = 25;
let sliderLeftMargin = 230;
let defaultTextSize = 16;

let playButton, noteSelect, formulaCheckbox, freqSlider, dutySlider;

// Audio state (created on the first Play click)
let audioCtx = null;
let osc = null;
let gainNode = null;
let isPlaying = false;
let lastDuty = -1;
let scrollPhase = 0;
let currentFreq = 440;   // exact frequency (slider positions are rounded)

const FMIN = 100;
const FMAX = 4000;
const NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
const KEY_LOW = 43;   // MIDI G2 (98 Hz)
const KEY_HIGH = 107; // MIDI B7 (3951 Hz)

function setup() {
  updateCanvasSize();
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(document.querySelector('main'));

  // Row 1: Play button, note jump menu, formula toggle
  playButton = createButton('Play');
  playButton.position(10, drawHeight + 6);
  playButton.mousePressed(togglePlay);

  noteSelect = createSelect();
  noteSelect.option('Jump to a note...', '');
  const notes = [['C4', 60], ['D4', 62], ['E4', 64], ['F4', 65], ['G4', 67], ['A4', 69],
    ['B4', 71], ['C5', 72], ['A5', 81], ['C6', 84], ['A6', 93], ['E7 (piezo loud zone)', 100]];
  for (const n of notes) noteSelect.option(n[0], String(n[1]));
  noteSelect.position(80, drawHeight + 7);
  noteSelect.changed(jumpToNote);

  formulaCheckbox = createCheckbox('Show formula', false);
  formulaCheckbox.position(270, drawHeight + 9);

  // Row 2: frequency on a log slider so every octave gets the same slider length
  freqSlider = createSlider(0, 1000, freqToSlider(currentFreq), 1);
  freqSlider.position(sliderLeftMargin, drawHeight + 43);
  freqSlider.size(canvasWidth - sliderLeftMargin - margin);
  freqSlider.input(() => {
    currentFreq = sliderToFreq(freqSlider.value());
    noteSelect.selected('');
    updateAudio();
  });

  // Row 3: duty cycle in percent
  dutySlider = createSlider(0, 100, 50, 1);
  dutySlider.position(sliderLeftMargin, drawHeight + 78);
  dutySlider.size(canvasWidth - sliderLeftMargin - margin);
  dutySlider.input(updateAudio);

  describe('PWM tone lab. An oscilloscope shows a square wave whose frequency and duty cycle are set by sliders. A piano keyboard highlights the nearest musical note, and readouts give the frequency, period, on time and off time. A Play button sounds the tone.');
}

function draw() {
  updateCanvasSize();

  stroke('silver');
  strokeWeight(1);
  fill('aliceblue');
  rect(0, 0, canvasWidth, drawHeight);
  fill('white');
  rect(0, drawHeight, canvasWidth, controlHeight);

  const f = currentFreq;
  const duty = dutySlider.value() / 100;
  const periodMs = 1000 / f;

  // Title
  noStroke();
  fill('black');
  textAlign(CENTER, TOP);
  textSize(22);
  text('PWM Tone Lab', canvasWidth / 2, 8);

  // Readout line
  fitText('Frequency: ' + fmtHz(f) + '   Period: ' + nf(periodMs, 1, 3) + ' ms   On: ' +
    nf(periodMs * duty, 1, 3) + ' ms   Off: ' + nf(periodMs * (1 - duty), 1, 3) + ' ms',
    canvasWidth / 2, 38, 16);

  // ---------- Oscilloscope ----------
  const sx0 = 50;
  const sx1 = canvasWidth - 15;
  const sy0 = 64;
  const sy1 = 234;
  drawScope(sx0, sy0, sx1, sy1, f, duty);

  if (isPlaying) scrollPhase += 0.004;

  // ---------- Note and formula ----------
  const midiExact = 69 + 12 * Math.log2(f / 440);
  const midi = round(midiExact);
  const cents = round((midiExact - midi) * 100);
  const n = midi - 69;
  const name = noteName(midi);

  noStroke();
  fill('black');
  textAlign(CENTER, TOP);
  textSize(16);
  let centsText = cents === 0 ? 'in tune' : (cents > 0 ? cents + ' cents sharp' : (-cents) + ' cents flat');
  fitText('Nearest note: ' + name + '   (n = ' + n + ' semitones from A4, ' + centsText + ')', canvasWidth / 2, 244, 16);

  if (formulaCheckbox.checked()) {
    const fNote = 440 * pow(2, n / 12);
    fill('darkblue');
    fitText('f = 440 × 2^(n/12) = 440 × 2^(' + n + '/12) = ' + nf(fNote, 1, 1) + ' Hz  (' + name + ')',
      canvasWidth / 2, 266, 16);
  }

  // ---------- Piano keyboard ----------
  drawKeyboard(15, 292, canvasWidth - 15, 425, midi);

  // ---------- Control labels ----------
  noStroke();
  fill('black');
  textAlign(LEFT, CENTER);
  textSize(defaultTextSize);
  text('Frequency (pitch): ' + fmtHz(f), 10, drawHeight + 53);
  text('Duty cycle: ' + dutySlider.value() + '% on', 10, drawHeight + 88);
}

// Draws a square wave over a fixed 10 ms window (1 ms per division)
function drawScope(x0, y0, x1, y1, f, duty) {
  const windowMs = 10;
  stroke('dimgray');
  fill('black');
  rect(x0, y0, x1 - x0, y1 - y0, 4);

  // grid
  stroke(0, 90, 0);
  for (let i = 1; i < 10; i++) {
    const x = map(i, 0, 10, x0, x1);
    line(x, y0, x, y1);
  }
  const yHigh = y0 + 30;
  const yLow = y1 - 30;
  line(x0, yHigh, x1, yHigh);
  line(x0, yLow, x1, yLow);

  // trace
  stroke('lime');
  strokeWeight(2);
  noFill();
  beginShape();
  const periodMs = 1000 / f;
  if (duty <= 0 || duty >= 1) {
    const y = duty >= 1 ? yHigh : yLow;
    vertex(x0, y);
    vertex(x1, y);
  } else {
    // walk through every rising and falling edge inside the window
    const shift = (scrollPhase * windowMs) % periodMs;
    let high = levelAt(0, shift, periodMs, duty);
    vertex(x0, high ? yHigh : yLow);
    const edges = [];
    for (let k = 0; k * periodMs - shift < windowMs + periodMs; k++) {
      edges.push(k * periodMs - shift);                    // rising edge
      edges.push(k * periodMs + duty * periodMs - shift);  // falling edge
    }
    edges.sort((a, b) => a - b);
    for (const t of edges) {
      if (t <= 0 || t >= windowMs) continue;
      const x = map(t, 0, windowMs, x0, x1);
      const next = levelAt(t + 1e-6, shift, periodMs, duty);
      if (next === high) continue;
      vertex(x, high ? yHigh : yLow);
      vertex(x, next ? yHigh : yLow);
      high = next;
    }
    vertex(x1, high ? yHigh : yLow);
  }
  endShape();
  strokeWeight(1);

  // labels
  noStroke();
  fill('black');
  textSize(14);
  textAlign(RIGHT, CENTER);
  text('3.3 V', x0 - 4, yHigh);
  text('0 V', x0 - 4, yLow);
  textAlign(RIGHT, TOP);
  fill('lime');
  text('1 ms per division', x1 - 6, y0 + 4);
  textAlign(LEFT, TOP);
  text(isPlaying ? 'PLAYING' : 'Silent: press Play', x0 + 6, y0 + 4);
}

// Draws centered text, shrinking the font so it never runs past the canvas edges
function fitText(str, x, y, size) {
  textSize(size);
  const w = textWidth(str);
  if (w > canvasWidth - 16) textSize(size * (canvasWidth - 16) / w);
  text(str, x, y);
  textSize(size);
}

// True when the PWM output is high at time t (ms)
function levelAt(t, shift, periodMs, duty) {
  const phase = (((t + shift) % periodMs) + periodMs) % periodMs / periodMs;
  return phase < duty;
}

function drawKeyboard(x0, y0, x1, y1, activeMidi) {
  // count white keys
  const whites = [];
  for (let m = KEY_LOW; m <= KEY_HIGH; m++) if (!isBlack(m)) whites.push(m);
  const kw = (x1 - x0) / whites.length;
  const kh = y1 - y0 - 18;
  const clampedActive = constrain(activeMidi, KEY_LOW, KEY_HIGH);

  // white keys
  stroke('gray');
  for (let i = 0; i < whites.length; i++) {
    fill(whites[i] === clampedActive ? 'gold' : 'white');
    rect(x0 + i * kw, y0, kw, kh, 0, 0, 3, 3);
  }
  // black keys
  for (let i = 0; i < whites.length; i++) {
    const m = whites[i] + 1;
    if (m <= KEY_HIGH && isBlack(m)) {
      fill(m === clampedActive ? 'gold' : 'black');
      rect(x0 + (i + 1) * kw - kw * 0.32, y0, kw * 0.64, kh * 0.6, 0, 0, 2, 2);
    }
  }
  // octave labels under each C
  noStroke();
  fill('black');
  textSize(12);
  textAlign(CENTER, TOP);
  for (let i = 0; i < whites.length; i++) {
    if (whites[i] % 12 === 0) text(noteName(whites[i]), x0 + i * kw + kw / 2, y0 + kh + 3);
  }
  // marker over the active key
  let idx = -1;
  for (let i = 0; i < whites.length; i++) {
    if (whites[i] === clampedActive || whites[i] + 1 === clampedActive) idx = i;
  }
  if (idx >= 0) {
    const cx = whites[idx] === clampedActive ? x0 + idx * kw + kw / 2 : x0 + (idx + 1) * kw;
    fill('crimson');
    triangle(cx - 6, y0 - 9, cx + 6, y0 - 9, cx, y0 - 1);
  }
}

function isBlack(m) {
  return [1, 3, 6, 8, 10].includes(((m % 12) + 12) % 12);
}

function noteName(m) {
  return NOTE_NAMES[((m % 12) + 12) % 12] + (floor(m / 12) - 1);
}

function sliderToFreq(v) {
  return FMIN * pow(FMAX / FMIN, v / 1000);
}

function freqToSlider(f) {
  return round(1000 * Math.log(f / FMIN) / Math.log(FMAX / FMIN));
}

function fmtHz(f) {
  return (f < 1000 ? nf(f, 1, 1) : nf(round(f), 1, 0)) + ' Hz';
}

function jumpToNote() {
  const v = noteSelect.value();
  if (v === '') return;
  currentFreq = 440 * pow(2, (int(v) - 69) / 12);
  freqSlider.value(freqToSlider(currentFreq));
  updateAudio();
}

// ---------- Web Audio ----------
// A plain OscillatorNode 'square' wave is always 50% duty, so we build a custom
// PeriodicWave from the Fourier series of a pulse wave with the chosen duty cycle.
function pulseWave(duty) {
  const N = 48;
  const real = new Float32Array(N);
  const imag = new Float32Array(N);
  for (let n = 1; n < N; n++) {
    real[n] = (2 / (n * Math.PI)) * Math.sin(n * Math.PI * duty);
  }
  return audioCtx.createPeriodicWave(real, imag);
}

function togglePlay() {
  if (!isPlaying) {
    if (!audioCtx) {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    audioCtx.resume();
    osc = audioCtx.createOscillator();
    gainNode = audioCtx.createGain();
    gainNode.gain.value = 0;
    osc.connect(gainNode);
    gainNode.connect(audioCtx.destination);
    lastDuty = -1;
    isPlaying = true;
    updateAudio();
    osc.start();
    playButton.html('Stop');
  } else {
    stopTone();
  }
}

function stopTone() {
  if (osc) {
    gainNode.gain.setTargetAtTime(0, audioCtx.currentTime, 0.01);
    osc.stop(audioCtx.currentTime + 0.05);
    osc = null;
  }
  isPlaying = false;
  playButton.html('Play');
}

function updateAudio() {
  if (!isPlaying || !osc) return;
  const f = currentFreq;
  const d = dutySlider.value();
  osc.frequency.setTargetAtTime(f, audioCtx.currentTime, 0.01);
  if (d !== lastDuty && d > 0 && d < 100) {
    osc.setPeriodicWave(pulseWave(d / 100));
    lastDuty = d;
  }
  // 0% and 100% duty never switch, so the speaker does not vibrate: silence
  const level = (d === 0 || d === 100) ? 0 : 0.08;
  gainNode.gain.setTargetAtTime(level, audioCtx.currentTime, 0.02);
}

function windowResized() {
  updateCanvasSize();
  resizeCanvas(canvasWidth, canvasHeight);
  freqSlider.size(canvasWidth - sliderLeftMargin - margin);
  dutySlider.size(canvasWidth - sliderLeftMargin - margin);
}

function updateCanvasSize() {
  const container = document.querySelector('main');
  if (container) {
    canvasWidth = Math.floor(container.getBoundingClientRect().width);
  }
}
