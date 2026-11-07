// Alarm State Machine - vis-network
// CANVAS_HEIGHT: 500
// Four states (IDLE, ARMED, RINGING, SNOOZED) joined by event arrows. Event buttons move the
// highlight along the matching arrow and update a small clock model; events with no arrow
// from the current state are reported as ignored. Clicking a state shows its variables.
// Nothing animates: the diagram only changes when the learner presses an event button.

const STATES = {
  IDLE: {
    color: 'gray', x: -210, y: 0,
    label: 'IDLE\n(alarm off)',
    info: 'The alarm is switched off. The clock keeps time, but the alarm time is never compared.',
    vars: { alarm_on: false, ringing: false, fired: false }
  },
  ARMED: {
    color: 'seagreen', x: 0, y: -135,
    label: 'ARMED',
    info: 'The alarm is on and waiting. Each loop compares the hour and minute with the alarm time.',
    vars: { alarm_on: true, ringing: false, fired: 'False, or True for the rest of a minute that just rang' }
  },
  RINGING: {
    color: 'crimson', x: 210, y: 0,
    label: 'RINGING',
    info: 'The tone is playing. It stops on Stop, on Snooze, or by itself after one minute.',
    vars: { alarm_on: true, ringing: true, fired: true }
  },
  SNOOZED: {
    color: 'darkorange', x: 0, y: 135,
    label: 'SNOOZED',
    info: 'The tone is silent and a new ring time, 9 minutes later, is stored.',
    vars: { alarm_on: true, ringing: false, fired: true }
  }
};

// Every arrow in the diagram: [id, from, to, label, roundness, curve type]
const EDGES = [
  ['e1', 'IDLE', 'ARMED', 'toggle alarm', 0.2],
  ['e2', 'ARMED', 'IDLE', 'toggle alarm', 0.2],
  ['e3', 'ARMED', 'RINGING', 'time matches', 0.2],
  ['e4', 'RINGING', 'ARMED', 'stop button', 0.15],
  ['e5', 'RINGING', 'ARMED', '60 seconds pass', 0.5, 'curvedCCW'],
  ['e6', 'RINGING', 'SNOOZED', 'snooze button', 0.2],
  ['e7', 'SNOOZED', 'RINGING', 'time matches', 0.2],
  ['e8', 'SNOOZED', 'ARMED', 'stop button', 0.12],
  ['e9', 'SNOOZED', 'IDLE', 'toggle alarm', 0.2]
];

// Time model (minutes since midnight)
const START_CLOCK = 7 * 60 + 29;
const ALARM = 7 * 60 + 30;
let clock, state, fired, snoozeAt, lastEdge, msg, msgClass;

let network, nodes, edges;

function resetModel() {
  clock = START_CLOCK;
  state = 'IDLE';
  fired = false;
  snoozeAt = null;
  lastEdge = null;
  msg = 'The alarm is off. Press <b>Toggle alarm</b> to arm it. Before each press, predict which arrow the highlight will follow.';
  msgClass = 'info';
}

function hhmm(m) {
  m = ((m % 1440) + 1440) % 1440;
  return String(Math.floor(m / 60)).padStart(2, '0') + ':' + String(m % 60).padStart(2, '0');
}

// The next time the alarm will ring: the snooze time, or the next 07:30 at or after now
function ringTarget() {
  if (snoozeAt !== null) return snoozeAt;
  let t = ALARM;
  while (t < clock) t += 1440;
  return t;
}

// Move along an arrow if one leaves the current state with this event label
function take(label, note) {
  const e = EDGES.find(x => x[1] === state && x[3] === label);
  if (!e) return false;
  const from = state;
  state = e[2];
  lastEdge = e[0];
  msg = '<b>' + label + '</b>: ' + from + ' &rarr; ' + state + '. ' + (note || '');
  msgClass = 'ok';
  return true;
}

function ignored(eventName) {
  lastEdge = null;
  msg = 'No arrow labeled <b>' + eventName + '</b> leaves ' + state + ', so the event is ignored and the state does not change.';
  msgClass = 'bad';
}

function onToggle() {
  if (state === 'IDLE') {
    fired = false;
    take('toggle alarm', 'alarm_on becomes True.');
  } else if (state === 'ARMED' || state === 'SNOOZED') {
    snoozeAt = null;
    take('toggle alarm', 'alarm_on becomes False and any snooze is cancelled.');
  } else {
    ignored('toggle alarm');
    msg += ' In this design you must press Stop or Snooze first.';
  }
  refresh();
}

function onMatch() {
  if (state === 'RINGING') {
    ignored('time matches');
    msg += ' It is already ringing.';
  } else if (state === 'IDLE') {
    clock = ringTarget();
    ignored('time matches');
    msg = 'The clock reaches ' + hhmm(ALARM) + ', but alarm_on is False, so no arrow leaves IDLE. Nothing rings.';
  } else if (clock === ringTarget() && fired) {
    lastEdge = null;
    msg = 'The time still matches ' + hhmm(clock) + ', but <b>fired</b> is True, so the alarm does not start again. Let 60 seconds pass first.';
    msgClass = 'bad';
  } else {
    clock = ringTarget();
    fired = true;
    take('time matches', 'The clock reads ' + hhmm(clock) + '. fired becomes True.');
  }
  refresh();
}

function onStop() {
  if (state === 'RINGING' || state === 'SNOOZED') {
    const wasSnoozed = state === 'SNOOZED';
    snoozeAt = null;
    take('stop button', wasSnoozed ? 'The snooze is cancelled; the alarm stays armed for tomorrow.'
      : 'ringing becomes False. fired stays True, so it will not restart this minute.');
  } else {
    ignored('stop button');
  }
  refresh();
}

function onSnooze() {
  if (state === 'RINGING') {
    snoozeAt = clock + 9;
    take('snooze button', 'It will ring again at ' + hhmm(snoozeAt) + ' (9 minutes later).');
  } else {
    ignored('snooze button');
  }
  refresh();
}

function onMinute() {
  clock += 1;
  // the matching minute is over, so the fired flag resets
  if (clock !== ringTarget()) fired = false;
  if (state === 'RINGING') {
    fired = false;
    snoozeAt = null;
    take('60 seconds pass', 'The clock reads ' + hhmm(clock) + '. The alarm gives up after one minute.');
  } else if ((state === 'ARMED' || state === 'SNOOZED') && clock === ringTarget()) {
    fired = true;
    take('time matches', 'A minute passed and the clock now reads ' + hhmm(clock) + ', which matches the ring time.');
  } else {
    lastEdge = null;
    msg = 'A minute passes. The clock reads ' + hhmm(clock) + '. No arrow is labeled "60 seconds pass" from ' +
      state + ', so the state stays the same.';
    msgClass = 'info';
  }
  refresh();
}

function onReset() {
  resetModel();
  refresh();
}

// ---------- Drawing ----------
function nodeStyle(id) {
  const s = STATES[id];
  const active = id === state;
  return {
    id: id,
    label: s.label,
    color: {
      background: active ? s.color : 'white',
      border: s.color,
      highlight: { background: active ? s.color : 'white', border: s.color },
      hover: { background: active ? s.color : 'aliceblue', border: s.color }
    },
    font: { color: active ? 'white' : 'black', size: 18, bold: active },
    borderWidth: active ? 4 : 3
  };
}

function edgeStyle(e) {
  const active = e[0] === lastEdge;
  return {
    id: e[0],
    color: { color: active ? 'darkorange' : 'gray', highlight: 'darkorange', hover: 'dimgray' },
    width: active ? 5 : 2,
    font: { size: 15, color: active ? 'darkorange' : 'black', background: 'white', strokeWidth: 0, bold: active }
  };
}

function refresh() {
  if (nodes) {
    nodes.update(Object.keys(STATES).map(nodeStyle));
    edges.update(EDGES.map(edgeStyle));
  }
  const ringNext = state === 'IDLE' ? '--:--' : hhmm(ringTarget());
  document.getElementById('clock').innerHTML =
    '<div class="big">' + hhmm(clock) + '</div>' +
    '<div class="row">Alarm set for ' + hhmm(ALARM) + '</div>' +
    '<div class="row">Rings next at ' + ringNext + (snoozeAt !== null ? ' (snoozed)' : '') + '</div>';
  const v = (b) => b ? '<span class="t">True</span>' : '<span class="f">False</span>';
  document.getElementById('vars').innerHTML =
    'state&nbsp;&nbsp;&nbsp;&nbsp;= <b>' + state + '</b><br>' +
    'alarm_on = ' + v(state !== 'IDLE') + '<br>' +
    'ringing&nbsp;&nbsp;= ' + v(state === 'RINGING') + '<br>' +
    'fired&nbsp;&nbsp;&nbsp;&nbsp;= ' + v(fired);
  const m = document.getElementById('msg');
  m.className = msgClass;
  m.innerHTML = msg;
}

function showStateInfo(id) {
  const s = STATES[id];
  const fmt = (val) => val === true ? '<span class="t">True</span>' :
    (val === false ? '<span class="f">False</span>' : val);
  msg = '<b>' + id + '</b>: ' + s.info + '<br>alarm_on = ' + fmt(s.vars.alarm_on) +
    ', ringing = ' + fmt(s.vars.ringing) + ', fired = ' + fmt(s.vars.fired);
  msgClass = 'info';
  refresh();
}

function isInIframe() {
  try { return window.self !== window.top; } catch (e) { return true; }
}

document.addEventListener('DOMContentLoaded', function () {
  resetModel();

  nodes = new vis.DataSet(Object.keys(STATES).map(id => {
    const n = nodeStyle(id);
    n.x = STATES[id].x;
    n.y = STATES[id].y;
    return n;
  }));
  edges = new vis.DataSet(EDGES.map(e => {
    const s = edgeStyle(e);
    s.from = e[1];
    s.to = e[2];
    s.label = e[3];
    s.smooth = { enabled: true, type: e[5] || 'curvedCW', roundness: e[4] };
    return s;
  }));

  const mouseOK = !isInIframe();
  const options = {
    layout: { improvedLayout: false },
    physics: { enabled: false },
    interaction: {
      selectConnectedEdges: false,
      zoomView: mouseOK,
      dragView: mouseOK,
      dragNodes: false,
      navigationButtons: true,
      hover: true
    },
    nodes: {
      shape: 'box',
      margin: 12,
      widthConstraint: { minimum: 110 },
      font: { face: 'Arial', multi: true },
      shadow: { enabled: true, color: 'rgba(0,0,0,0.2)', size: 5, x: 2, y: 2 }
    },
    edges: {
      arrows: { to: { enabled: true, scaleFactor: 1.0 } },
      font: { face: 'Arial', align: 'horizontal' }
    }
  };

  network = new vis.Network(document.getElementById('network'), { nodes, edges }, options);
  network.once('afterDrawing', () => network.fit({ animation: false }));
  network.on('click', (params) => {
    if (params.nodes.length > 0) showStateInfo(params.nodes[0]);
  });
  // keep the whole diagram in view whenever the container changes size
  network.on('resize', () => network.fit({ animation: false }));
  window.addEventListener('resize', () => network.fit({ animation: false }));

  document.getElementById('btnToggle').addEventListener('click', onToggle);
  document.getElementById('btnMatch').addEventListener('click', onMatch);
  document.getElementById('btnStop').addEventListener('click', onStop);
  document.getElementById('btnSnooze').addEventListener('click', onSnooze);
  document.getElementById('btnMinute').addEventListener('click', onMinute);
  document.getElementById('btnReset').addEventListener('click', onReset);

  refresh();
});
