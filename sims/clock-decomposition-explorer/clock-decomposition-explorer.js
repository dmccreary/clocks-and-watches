// Clock Decomposition Explorer - vis-network
// CANVAS_HEIGHT: 492
// A decomposition tree for a digital clock: the whole problem, five
// sub-problems, and two or three small tasks under each one. Clicking a
// box explains it; hovering shows its path back to the root; choosing a
// symptom pulses the task most likely to contain that bug.
// Design note: the tree runs left-to-right instead of top-down so its
// 13 small tasks fit the 450 px tall canvas at a readable font size.

const COLORS = {
  root: { background: '#6a1b9a', border: '#4a148c', font: 'white' },
  child: { background: '#00897b', border: '#00695c', font: 'white' },
  task: { background: '#e0f2f1', border: '#00897b', font: '#0b3d36' },
  path: '#ff6f00',
  bug: '#d32f2f'
};

// Tree data: parent, label, definition, and how to test the piece alone
const tree = {
  root: { label: 'Digital Clock', parent: null, level: 0,
    def: 'The whole problem: show the correct time and let a person set it.',
    test: 'You cannot test the whole clock at once until each piece below works on its own.' },
  keep: { label: 'Keep Time', parent: 'root', level: 1,
    def: 'Know what time it is right now, counted as seconds since midnight.',
    test: 'Print the seconds count once a second and compare it with a phone clock.' },
  split: { label: 'Split Time', parent: 'root', level: 1,
    def: 'Turn the total seconds into separate hours, minutes, and seconds.',
    test: 'Feed in 45296 and check that you get 12, 34, and 56.' },
  format: { label: 'Format Time', parent: 'root', level: 1,
    def: 'Choose how the numbers look, such as 12-hour or 24-hour style with leading zeros.',
    test: 'Give it hour 15 and check that 12-hour mode shows 3 and 24-hour mode shows 15.' },
  drawt: { label: 'Draw Time', parent: 'root', level: 1,
    def: 'Light up the display so the formatted time can be seen.',
    test: 'Send a fixed string such as "88:88" and check every segment lights.' },
  input: { label: 'Handle Input', parent: 'root', level: 1,
    def: 'React to button presses so a person can set the time or change modes.',
    test: 'Print a message on each press and check that one press prints exactly once.' },

  count: { label: 'Count seconds', parent: 'keep', level: 2,
    def: 'Add one to the seconds count every time a second passes.',
    test: 'Let it run for 60 seconds next to a stopwatch and compare.' },
  rtc: { label: 'Read the RTC', parent: 'keep', level: 2,
    def: 'Ask the real-time clock chip for the current time.',
    test: 'Read the chip twice, one second apart, and check the seconds went up by one.' },
  sync: { label: 'Sync over WiFi', parent: 'keep', level: 2,
    def: 'Get the exact time from an internet time server to correct drift.',
    test: 'Sync, then print the time and compare it with time.gov.' },
  hours: { label: 'Compute hours', parent: 'split', level: 2,
    def: 'Use seconds // 3600 to find the whole hours.',
    test: 'Try 0, 3599, and 3600 and check you get 0, 0, and 1.' },
  minutes: { label: 'Compute minutes', parent: 'split', level: 2,
    def: 'Use (seconds % 3600) // 60 to find the minutes past the hour.',
    test: 'Try 3660 and check you get 1 minute, not 61.' },
  secs: { label: 'Compute seconds', parent: 'split', level: 2,
    def: 'Use seconds % 60 to find the seconds past the minute.',
    test: 'Try 59 and 60 and check you get 59 and 0.' },
  mode: { label: '12/24-hour mode', parent: 'format', level: 2,
    def: 'Convert hours 13 to 23 into 1 to 11 PM when 12-hour style is chosen.',
    test: 'Check hours 0, 12, and 15 in both modes.' },
  zeros: { label: 'Add leading zeros', parent: 'format', level: 2,
    def: 'Pad single digits so 9:5 shows as 09:05.',
    test: 'Format minute 5 and check you get "05".' },
  digits: { label: 'Draw digits', parent: 'drawt', level: 2,
    def: 'Turn each digit into the segments or pixels that show it.',
    test: 'Show 0 to 9 one at a time and check each shape.' },
  colon: { label: 'Flash the colon', parent: 'drawt', level: 2,
    def: 'Turn the colon on and off once a second so you can see the clock is running.',
    test: 'Watch the colon for ten seconds; it should blink ten times.' },
  bright: { label: 'Set brightness', parent: 'drawt', level: 2,
    def: 'Choose how bright the display is, for example dimmer at night.',
    test: 'Step through every brightness level and check each one looks different.' },
  buttons: { label: 'Read buttons', parent: 'input', level: 2,
    def: 'Check each button pin to see whether it is pressed.',
    test: 'Print the pin value while you press and release the button.' },
  debounce: { label: 'Debounce presses', parent: 'input', level: 2,
    def: 'Ignore the quick bounces a button makes so one press counts once.',
    test: 'Press 10 times and check the count is exactly 10.' }
};

// Which task most likely holds each bug, and why
const symptoms = {
  hour: { node: 'mode', why: 'The minutes and seconds are right, so Keep Time and Split Time work. A clock showing 3:05 instead of 15:05 is a Format Time bug in the 12/24-hour step.' },
  colon: { node: 'colon', why: 'The digits still change, so time is kept and drawn. Only the colon task is broken, inside Draw Time.' },
  buttons: { node: 'buttons', why: 'The clock still runs, so the problem is in Handle Input. Start with Read buttons: check the pin number and wiring.' },
  slow: { node: 'count', why: 'Every digit is drawn correctly but falls behind, so the bug is in Keep Time. Check how seconds are counted, for example a sleep(1) loop that also spends time drawing.' }
};

let network, nodes, edges;
let pulseTimer = null;
let bugNode = null;

function isInIframe() {
  try { return window.self !== window.top; } catch (e) { return true; }
}

// Lay the tree out left to right: tasks in one column, sub-problems
// centered on their tasks, and the root centered on everything.
function buildData() {
  const ids = Object.keys(tree);
  const tasks = ids.filter(id => tree[id].level === 2);
  const spacing = 34;
  const y0 = -((tasks.length - 1) * spacing) / 2;
  const pos = {};
  tasks.forEach((id, i) => { pos[id] = { x: 140, y: y0 + i * spacing }; });
  ids.filter(id => tree[id].level === 1).forEach(id => {
    const kids = tasks.filter(t => tree[t].parent === id);
    const avg = kids.reduce((s, k) => s + pos[k].y, 0) / kids.length;
    pos[id] = { x: -90, y: avg };
  });
  pos.root = { x: -300, y: 4 };

  const nodeList = ids.map(id => {
    const t = tree[id];
    const c = t.level === 0 ? COLORS.root : (t.level === 1 ? COLORS.child : COLORS.task);
    return {
      id, label: t.label, x: pos[id].x, y: pos[id].y,
      shape: 'box',
      margin: t.level === 0 ? 14 : (t.level === 1 ? 9 : 6),
      font: { size: t.level === 0 ? 20 : (t.level === 1 ? 17 : 15), color: c.font, bold: t.level < 2 },
      color: { background: c.background, border: c.border,
        highlight: { background: c.background, border: COLORS.path },
        hover: { background: c.background, border: c.border } },
      borderWidth: 2,
      widthConstraint: t.level === 2 ? { minimum: 150 } : undefined
    };
  });
  const edgeList = ids.filter(id => tree[id].parent).map(id => ({
    id: 'e-' + id, from: tree[id].parent, to: id, color: { color: '#78909c' }, width: 2
  }));
  return { nodeList, edgeList };
}

function baseNodeStyle(id) {
  const t = tree[id];
  const c = t.level === 0 ? COLORS.root : (t.level === 1 ? COLORS.child : COLORS.task);
  return { id, color: { background: c.background, border: c.border,
    highlight: { background: c.background, border: COLORS.path },
    hover: { background: c.background, border: c.border } }, borderWidth: 2 };
}

function pathToRoot(id) {
  const path = [];
  let cur = id;
  while (cur) { path.push(cur); cur = tree[cur].parent; }
  return path;
}

function clearPath() {
  nodes.update(Object.keys(tree).filter(id => id !== bugNode).map(baseNodeStyle));
  edges.update(edges.getIds().map(eid => ({ id: eid, color: { color: '#78909c' }, width: 2 })));
}

function showPath(id) {
  clearPath();
  const path = pathToRoot(id);
  nodes.update(path.filter(n => n !== bugNode).map(n => ({ id: n, borderWidth: 4,
    color: { ...baseNodeStyle(n).color, border: COLORS.path } })));
  edges.update(path.filter(n => tree[n].parent).map(n => ({ id: 'e-' + n, color: { color: COLORS.path }, width: 4 })));
}

function showInfo(id) {
  const t = tree[id];
  const where = pathToRoot(id).reverse().map(n => tree[n].label).join(' &rarr; ');
  document.getElementById('info').innerHTML =
    '<h4>' + t.label + '</h4>' + t.def +
    '<div class="hint"><b>Test it alone:</b> ' + t.test + '</div>' +
    '<div style="margin-top:6px;font-size:13px;color:#555">' + where + '</div>';
}

function markBug(id, on) {
  const s = baseNodeStyle(id);
  if (on) {
    s.color = { ...s.color, border: COLORS.bug, background: '#ffebee' };
    s.borderWidth = 5;
    s.font = { color: '#b71c1c' };
  } else {
    s.font = { color: COLORS.task.font };
  }
  nodes.update(s);
}

function onSymptom() {
  const key = document.getElementById('symptom').value;
  if (pulseTimer) { clearInterval(pulseTimer); pulseTimer = null; }
  if (bugNode) { const old = bugNode; bugNode = null; markBug(old, false); }
  clearPath();
  if (!key) return;
  const s = symptoms[key];
  bugNode = s.node;
  showPath(bugNode);
  // Pulse the suspect box three times, then leave it marked in red
  let n = 0;
  pulseTimer = setInterval(() => {
    markBug(s.node, n % 2 === 0);
    n++;
    if (n > 6) { clearInterval(pulseTimer); pulseTimer = null; markBug(s.node, true); }
  }, 300);
  const t = tree[s.node];
  document.getElementById('info').innerHTML =
    '<h4>Suspect: ' + t.label + '</h4>' + s.why +
    '<div class="hint"><b>Test it alone:</b> ' + t.test + '</div>';
}

function initializeNetwork() {
  const { nodeList, edgeList } = buildData();
  nodes = new vis.DataSet(nodeList);
  edges = new vis.DataSet(edgeList);
  const mouseOK = !isInIframe();
  const options = {
    layout: { improvedLayout: false },
    physics: { enabled: false },
    interaction: {
      hover: true,
      dragNodes: false,
      dragView: mouseOK,
      zoomView: mouseOK,
      navigationButtons: true,
      selectConnectedEdges: false,
      tooltipDelay: 200
    },
    edges: {
      arrows: { to: { enabled: false } },
      smooth: { type: 'cubicBezier', forceDirection: 'horizontal', roundness: 0.5 }
    },
    nodes: { shadow: { enabled: true, color: 'rgba(0,0,0,0.15)', size: 4, x: 1, y: 1 } }
  };
  network = new vis.Network(document.getElementById('network'), { nodes, edges }, options);
  network.once('afterDrawing', fitView);

  network.on('hoverNode', params => showPath(params.node));
  network.on('blurNode', () => { clearPath(); if (bugNode) showPath(bugNode); });
  network.on('click', params => {
    if (params.nodes.length > 0) {
      showInfo(params.nodes[0]);
      showPath(params.nodes[0]);
    }
  });
}

// Fit the tree, then shrink it a little and lift it so the navigation
// buttons along the bottom edge do not cover the lowest boxes.
function fitView() {
  network.fit({ animation: false });
  const scale = network.getScale() * 0.9;
  const pos = network.getViewPosition();
  network.moveTo({ position: { x: pos.x, y: pos.y + 22 / scale }, scale, animation: false });
}

window.addEventListener('resize', () => { if (network) fitView(); });

document.addEventListener('DOMContentLoaded', () => {
  initializeNetwork();
  document.getElementById('symptom').addEventListener('change', onSymptom);
});
