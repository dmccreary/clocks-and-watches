// Clock Mode State Machine - vis-network
// CANVAS_HEIGHT: 502
// Three clock modes (RUN, SET_HOUR, SET_MINUTE) drawn as circles with arrows
// labeled "Mode". The Mode button moves the highlighted state along the arrows,
// and the Cycle button changes the mock clock only in the setting modes.
// "Predict" asks the student to name the next state before it moves.

const MODES = ['RUN', 'SET_HOUR', 'SET_MINUTE'];

const STATE_INFO = {
  RUN: {
    shows: 'The current time, ticking normally.',
    mode: 'Mode goes to SET_HOUR.',
    cycle: 'Cycle does nothing here, so a bumped button cannot change the time by accident.'
  },
  SET_HOUR: {
    shows: 'The hour, highlighted (it flashes on a real clock).',
    mode: 'Mode goes to SET_MINUTE.',
    cycle: 'Cycle adds 1 to the hour and wraps: hour = (hour + 1) % 24.'
  },
  SET_MINUTE: {
    shows: 'The minute, highlighted (it flashes on a real clock).',
    mode: 'Mode goes back to RUN, and the new time starts ticking.',
    cycle: 'Cycle adds 1 to the minute and wraps: minute = (minute + 1) % 60.'
  }
};

let network, nodes, edges;
let mode = 0;
let hour = 12, minute = 0;
let waitingForPrediction = false;
let predictRight = 0, predictTotal = 0;

// ---------- environment ----------
function isInIframe() {
  try { return window.self !== window.top; } catch (e) { return true; }
}

const BASE_NODE = { background: 'lightsteelblue', border: 'steelblue' };
const ACTIVE_NODE = { background: 'gold', border: 'darkorange' };

function buildNetwork() {
  // y values are offset slightly so no labeled edge is perfectly horizontal
  // (vis-network can drop labels on perfectly horizontal edges)
  nodes = new vis.DataSet([
    { id: 'RUN', label: 'RUN' },
    { id: 'SET_HOUR', label: 'SET_HOUR' },
    { id: 'SET_MINUTE', label: 'SET_MINUTE' },
    // plain text notes that say what Cycle does in each state
    { id: 'cRUN', label: 'Cycle: no effect', shape: 'text', font: { size: 14, color: 'dimgray' },
      widthConstraint: { minimum: 160, maximum: 160 } },
    { id: 'cSET_HOUR', label: 'Cycle: hour + 1', shape: 'text', font: { size: 14, color: 'dimgray' },
      widthConstraint: { minimum: 160, maximum: 160 } },
    { id: 'cSET_MINUTE', label: 'Cycle: minute + 1', shape: 'text', font: { size: 14, color: 'dimgray' },
      widthConstraint: { minimum: 160, maximum: 160 } }
  ]);
  edges = new vis.DataSet([
    { id: 'm0', from: 'RUN', to: 'SET_HOUR', label: 'Mode press' },
    { id: 'm1', from: 'SET_HOUR', to: 'SET_MINUTE', label: 'Mode press' },
    { id: 'm2', from: 'SET_MINUTE', to: 'RUN', label: 'Mode press' }
  ]);
  placeNodes();
  const free = !isInIframe();
  const options = {
    layout: { improvedLayout: false },
    physics: { enabled: false },
    interaction: {
      dragNodes: false, dragView: free, zoomView: free,
      selectConnectedEdges: false, hover: true, navigationButtons: false
    },
    nodes: {
      shape: 'circle', margin: 10, borderWidth: 2,
      widthConstraint: { minimum: 104, maximum: 104 },
      color: BASE_NODE,
      font: { size: 16, face: 'Arial', color: 'black', bold: { size: 16 } }
    },
    edges: {
      arrows: { to: { enabled: true, scaleFactor: 0.9 } },
      color: { color: 'gray', highlight: 'gray', hover: 'gray' },
      width: 2,
      font: { size: 14, face: 'Arial', align: 'middle', background: 'aliceblue', strokeWidth: 0 },
      smooth: { enabled: true, type: 'curvedCW', roundness: 0.18 }
    }
  };
  network = new vis.Network(document.getElementById('network'), { nodes, edges }, options);
  network.once('afterDrawing', () => network.fit({ animation: false }));
  network.on('click', params => {
    if (params.nodes.length > 0 && STATE_INFO[params.nodes[0]]) showInfo(params.nodes[0]);
  });
}

// A tall triangle on wide screens, a flatter one when the diagram sits above the panel
function placeNodes() {
  const narrow = window.innerWidth <= 600;
  const P = narrow
    ? { RUN: [0, -60], SET_HOUR: [200, 50], SET_MINUTE: [-200, 62] }
    : { RUN: [0, -120], SET_HOUR: [140, 105], SET_MINUTE: [-140, 117] };
  const updates = [];
  for (const id of MODES) {
    const [x, y] = P[id];
    updates.push({ id, x, y });
    // the Cycle note sits just outside its circle
    // the notes are hidden on narrow screens, where the info panel explains Cycle instead
    updates.push({ id: 'c' + id, x, y: id === 'RUN' ? y - 76 : y + 76, hidden: narrow });
  }
  nodes.update(updates);
  if (network) network.fit({ animation: false });
}

// ---------- state updates ----------
function highlight() {
  const current = MODES[mode];
  nodes.update(MODES.map(m => ({
    id: m,
    color: m === current ? ACTIVE_NODE : BASE_NODE,
    borderWidth: m === current ? 5 : 2,
    font: { size: 16, color: 'black', bold: m === current }
  })));
  edges.update(MODES.map((m, i) => ({
    id: 'm' + i,
    color: { color: m === current ? 'darkorange' : 'gray' },
    width: m === current ? 4 : 2
  })));
  // the mock clock
  document.getElementById('hh').textContent = String(hour).padStart(2, '0');
  document.getElementById('mm').textContent = String(minute).padStart(2, '0');
  document.getElementById('hh').className = current === 'SET_HOUR' ? 'setting' : '';
  document.getElementById('mm').className = current === 'SET_MINUTE' ? 'setting' : '';
  document.getElementById('modeLabel').textContent = 'mode: ' + current;
}

function showInfo(state) {
  const info = STATE_INFO[state];
  document.getElementById('info').innerHTML =
    '<h3>' + state + (state === MODES[mode] ? ' (current state)' : '') + '</h3>' +
    '<p><b>Display:</b> ' + info.shows + '</p>' +
    '<p><b>Mode:</b> ' + info.mode + '</p>' +
    '<p><b>Cycle:</b> ' + info.cycle + '</p>';
}

function setFeedback(text, color) {
  const f = document.getElementById('feedback');
  f.textContent = text;
  f.style.color = color;
}

function doModeTransition() {
  const before = MODES[mode];
  mode = (mode + 1) % MODES.length;
  document.getElementById('code').textContent =
    'mode = (mode + 1) % 3   # ' + before + ' -> ' + MODES[mode];
  highlight();
  showInfo(MODES[mode]);
}

function pressMode() {
  if (waitingForPrediction) return;
  if (document.getElementById('predict').checked) {
    waitingForPrediction = true;
    document.getElementById('predictBox').style.display = 'block';
    setFeedback('', 'black');
    return;
  }
  doModeTransition();
  setFeedback('', 'black');
}

function answerPrediction(guess) {
  if (!waitingForPrediction) return;
  waitingForPrediction = false;
  document.getElementById('predictBox').style.display = 'none';
  const from = MODES[mode];
  const next = MODES[(mode + 1) % MODES.length];
  predictTotal++;
  if (guess === next) {
    predictRight++;
    setFeedback('Correct! ' + from + ' -> ' + next + '  (' + predictRight + ' / ' + predictTotal + ')', 'darkgreen');
  } else {
    setFeedback('Not quite: from ' + from + ', Mode goes to ' + next + '.  (' + predictRight + ' / ' +
      predictTotal + ')', 'firebrick');
  }
  doModeTransition();
}

function pressCycle() {
  if (waitingForPrediction) return;
  const current = MODES[mode];
  let code;
  if (current === 'SET_HOUR') {
    hour = (hour + 1) % 24;
    code = 'hour = (hour + 1) % 24   # now ' + hour;
    setFeedback('Hour changed to ' + hour + '.', 'darkgreen');
  } else if (current === 'SET_MINUTE') {
    minute = (minute + 1) % 60;
    code = 'minute = (minute + 1) % 60   # now ' + minute;
    setFeedback('Minute changed to ' + minute + '.', 'darkgreen');
  } else {
    code = '# RUN: the cycle press is ignored';
    setFeedback('Cycle does nothing in RUN mode.', 'dimgray');
  }
  document.getElementById('code').textContent = code;
  highlight();
}

document.addEventListener('DOMContentLoaded', function () {
  buildNetwork();
  highlight();
  document.getElementById('info').innerHTML =
    '<h3>Try it</h3><p>Press <b>Mode</b> to move the gold highlight along the arrows, and <b>Cycle</b> ' +
    'to change the clock. Click any state to read what the display shows there and what each button does.</p>';
  document.getElementById('modeBtn').addEventListener('click', pressMode);
  document.getElementById('cycleBtn').addEventListener('click', pressCycle);
  document.getElementById('predict').addEventListener('change', () => {
    predictRight = 0; predictTotal = 0;
    waitingForPrediction = false;
    document.getElementById('predictBox').style.display = 'none';
    setFeedback(document.getElementById('predict').checked ? 'Predict is on: press Mode.' : '', 'darkblue');
  });
  document.querySelectorAll('#predictBox button').forEach(b =>
    b.addEventListener('click', () => answerPrediction(b.dataset.state)));
  window.addEventListener('resize', placeNodes);
});
