// Clock Architecture Explorer - vis-network
// CANVAS_HEIGHT: 448
// Five blocks every clock in the book shares: Power Supply, Microcontroller,
// Time Source, Display, and Input. Power flows from the supply to every
// block; time and button data flow into the microcontroller; display data
// flows out. Choosing a clock relabels each block with the real part.

const BLOCKS = {
  power: { name: 'Power Supply', x: 0, y: -175, color: '#ffebee', border: '#c62828',
    job: 'Provides the electricity every other block needs.' },
  mcu: { name: 'Microcontroller', x: 0, y: 25, color: '#ede7f6', border: '#4a148c',
    job: 'Runs the program: reads the time and the buttons, then decides what to show.' },
  time: { name: 'Time Source', x: -225, y: -70, color: '#e0f2f1', border: '#00695c',
    job: 'Tells the program what time it is.' },
  display: { name: 'Display', x: 225, y: 120, color: '#fff8e1', border: '#ef6c00',
    job: 'An actuator that shows the time to a person.' },
  input: { name: 'Input', x: -225, y: 130, color: '#e3f2fd', border: '#1565c0',
    job: 'Sensors such as buttons that let a person set the time or change modes.' }
};

// Real parts for each clock, plus the chapter that covers that block
const CHAPTERS = {
  ch02: ['02-electronics-fundamentals', 'Chapter 2: Electronics Fundamentals'],
  ch05: ['05-pico-platform', 'Chapter 5: The Pico Platform'],
  ch06: ['06-getting-time', 'Chapter 6: Getting the Time in MicroPython'],
  ch07: ['07-buttons-state-machines', 'Chapter 7: Buttons, Interrupts, and State Machines'],
  ch09: ['09-led-displays', 'Chapter 9: LED Displays and the First Digital Clock'],
  ch11: ['11-oled-framebuffers', 'Chapter 11: OLED Displays and Framebuffers'],
  ch13: ['13-real-time-clocks', 'Chapter 13: Real-Time Clocks and the DS3231'],
  ch14: ['14-wifi-ntp', 'Chapter 14: WiFi, NTP, and Time Accuracy'],
  ch15: ['15-color-displays', 'Chapter 15: Color Displays and Smartwatch Faces'],
  ch18: ['18-sensors-power', 'Chapter 18: Sensors, Power, and Low-Power Design']
};

const CLOCKS = {
  generic: {
    power: ['', 'ch02'], mcu: ['', 'ch05'], time: ['', 'ch06'], display: ['', 'ch09'], input: ['', 'ch07']
  },
  led4: {
    power: ['USB 5 V cable', 'ch02'],
    mcu: ['Raspberry Pi Pico', 'ch05'],
    time: ['Pico internal clock', 'ch06'],
    display: ['TM1637 4-digit LED', 'ch09'],
    input: ['Two push buttons', 'ch07']
  },
  oled: {
    power: ['USB 5 V cable', 'ch02'],
    mcu: ['Raspberry Pi Pico', 'ch05'],
    time: ['DS3231 RTC', 'ch13'],
    display: ['SSD1306 OLED', 'ch11'],
    input: ['Three push buttons', 'ch07']
  },
  watch: {
    power: ['LiPo battery', 'ch18'],
    mcu: ['Pico W (with WiFi)', 'ch05'],
    time: ['NTP over WiFi', 'ch14'],
    display: ['GC9A01 round LCD', 'ch15'],
    input: ['Side buttons', 'ch07']
  }
};

// Extra sentence about the chosen part, shown in the infobox
const PART_NOTES = {
  led4: {
    power: 'A USB cable from a computer or phone charger supplies 5 V.',
    time: 'The Pico counts time itself, so the clock must be set again after power is lost.',
    display: 'The TM1637 chip drives four seven-segment digits using just two data wires.',
    input: 'One button changes the hour and one changes the minute.'
  },
  oled: {
    time: 'The DS3231 keeps accurate time on its own coin-cell battery, even when the Pico is off.',
    display: 'A small screen the Pico draws on over the I2C bus.',
    input: 'Buttons for mode, increment, and decrement.'
  },
  watch: {
    power: 'A small rechargeable battery, so the watch can leave the desk.',
    mcu: 'The Pico W adds a WiFi radio to the same RP2040 chip.',
    time: 'The watch asks an internet time server for the exact time, then keeps counting.',
    display: 'A round color screen, perfect for an analog watch face.'
  }
};

const EDGES = [
  { from: 'power', to: 'time', kind: 'power' },
  { from: 'power', to: 'input', kind: 'power' },
  { from: 'power', to: 'mcu', kind: 'power' },
  { from: 'power', to: 'display', kind: 'power' },
  { from: 'time', to: 'mcu', kind: 'data', label: 'data in' },
  { from: 'input', to: 'mcu', kind: 'data', label: 'data in' },
  { from: 'mcu', to: 'display', kind: 'data', label: 'data out' }
];

let network, nodes, edges;
let currentClock = 'generic';
let selectedBlock = null;

function isInIframe() {
  try { return window.self !== window.top; } catch (e) { return true; }
}

function nodeLabel(id) {
  const part = CLOCKS[currentClock][id][0];
  return part ? '<b>' + BLOCKS[id].name + '</b>\n' + part : '<b>' + BLOCKS[id].name + '</b>';
}

function buildNodes() {
  return Object.keys(BLOCKS).map(id => {
    const b = BLOCKS[id];
    return {
      id, x: b.x, y: b.y, label: nodeLabel(id), shape: 'box', margin: 12,
      widthConstraint: { minimum: 140, maximum: 175 },
      font: { multi: 'html', size: 16, color: '#222', bold: { size: 17, color: '#111' } },
      color: { background: b.color, border: b.border,
        highlight: { background: b.color, border: '#ff6f00' },
        hover: { background: b.color, border: b.border } },
      borderWidth: 3
    };
  });
}

function buildEdges() {
  return EDGES.map((e, i) => ({
    id: 'e' + i, from: e.from, to: e.to,
    label: e.kind === 'power' ? 'power' : e.label,
    dashes: e.kind === 'power',
    width: e.kind === 'power' ? 2 : 3,
    color: { color: e.kind === 'power' ? '#c62828' : '#1565c0' },
    font: { size: 15, color: e.kind === 'power' ? '#b71c1c' : '#0d47a1', background: 'aliceblue', strokeWidth: 0 },
    arrows: { to: { enabled: true, scaleFactor: 0.9 } },
    smooth: false
  }));
}

function showInfo(id) {
  selectedBlock = id;
  const b = BLOCKS[id];
  const [part, chKey] = CLOCKS[currentClock][id];
  const [chDir, chName] = CHAPTERS[chKey];
  const note = (PART_NOTES[currentClock] || {})[id];
  let html = '<h4>' + b.name + '</h4>';
  if (part) html += '<div class="part">' + part + '</div>';
  html += b.job;
  if (note) html += ' ' + note;
  html += '<div style="margin-top:6px">Read more: <a href="../../chapters/' + chDir + '/" target="_top">' + chName + '</a></div>';
  document.getElementById('info').innerHTML = html;
}

function onClockChange() {
  currentClock = document.getElementById('clockSelect').value;
  nodes.update(Object.keys(BLOCKS).map(id => ({ id, label: nodeLabel(id) })));
  if (selectedBlock) showInfo(selectedBlock);
}

function fitView() {
  network.fit({ animation: false });
  const scale = network.getScale() * 0.9;
  const pos = network.getViewPosition();
  network.moveTo({ position: { x: pos.x, y: pos.y + 26 / scale }, scale, animation: false });
}

function initializeNetwork() {
  nodes = new vis.DataSet(buildNodes());
  edges = new vis.DataSet(buildEdges());
  const mouseOK = !isInIframe();
  const options = {
    layout: { improvedLayout: false },
    physics: { enabled: false },
    interaction: {
      hover: true,
      dragNodes: false,
      dragView: mouseOK,
      zoomView: mouseOK,
      // Navigation buttons cover the small diagram on phones, so show them only on wider screens
      navigationButtons: window.innerWidth >= 600,
      selectConnectedEdges: false
    },
    nodes: { shadow: { enabled: true, color: 'rgba(0,0,0,0.15)', size: 4, x: 1, y: 1 } }
  };
  network = new vis.Network(document.getElementById('network'), { nodes, edges }, options);
  network.once('afterDrawing', fitView);
  network.on('click', params => {
    if (params.nodes.length > 0) showInfo(params.nodes[0]);
  });
}

window.addEventListener('resize', () => { if (network) fitView(); });

document.addEventListener('DOMContentLoaded', () => {
  initializeNetwork();
  document.getElementById('clockSelect').addEventListener('change', onClockChange);
});
