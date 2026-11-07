// Pico Startup Sequence - Mermaid flowchart with click callbacks
// CANVAS_HEIGHT: 548
// Shows what happens from power-on to a running clock. Every node has a
// Mermaid click directive that fills the info panel. A toggle switches between
// "Has main.py" and "No main.py" and highlights the part of the path that changes.

const STEP_INFO = {
  P: { title: 'Power on',
    text: 'The Pico gets power from the USB cable or from a battery on VSYS. The RP2040 chip wakes up ' +
      'and starts the program stored at the very beginning of its flash memory.' },
  F: { title: 'MicroPython firmware starts',
    text: 'That program is the MicroPython firmware (the <code>.uf2</code> file you installed). It sets up ' +
      'the chip, mounts the file system in flash, and gets ready to run Python files. This takes well ' +
      'under a second.' },
  B: { title: 'Run boot.py',
    text: 'If a file named <code>boot.py</code> exists, it runs first. It is meant for low-level setup and ' +
      'is usually empty or missing. Most clocks never need it.' },
  M: { title: 'Is there a main.py?',
    text: 'MicroPython looks for a file named exactly <code>main.py</code> in the top folder of the Pico. ' +
      'This one check decides whether your program starts by itself.' },
  R: { title: 'Run main.py',
    text: 'Your clock program starts on its own, with no computer and no Run button. This is how a ' +
      'finished clock works when it is plugged into a wall adapter.' },
  L: { title: 'Main loop runs',
    text: 'A <code>while True:</code> loop reads the time, updates the display and checks the buttons, ' +
      'over and over, forever. The clock is now running.' },
  U: { title: 'USB connected to Thonny?',
    text: 'If the Pico is plugged into a computer running Thonny, pressing Stop or Ctrl+C interrupts ' +
      '<code>main.py</code>. On battery power nothing can interrupt it, so the loop keeps going.' },
  Q: { title: 'REPL prompt',
    text: 'The <code>&gt;&gt;&gt;</code> prompt waits for you to type a line or press Run in Thonny. With ' +
      'no <code>main.py</code>, the Pico comes straight here after booting, and with no computer ' +
      'attached it simply sits idle.' }
};

// Which nodes and edges are on the path, and which part changes, for each mode.
// Edge numbers follow the order of the arrows in the diagram text below.
const PATHS = {
  yes: { active: ['P', 'F', 'B', 'M', 'R', 'L', 'U', 'Q'], changed: ['R', 'L', 'U'],
    activeEdges: [0, 1, 2, 3, 4, 5, 6, 7], changedEdges: [3, 4, 5] },
  no: { active: ['P', 'F', 'B', 'M', 'Q'], changed: ['Q'],
    activeEdges: [0, 1, 2, 8], changedEdges: [8] }
};

let mode = 'yes';
let renderCount = 0;

function diagramText() {
  const p = PATHS[mode];
  const lines = [
    'flowchart TD',
    '  P("Power on"):::cls_P',
    '  F["Firmware starts"]:::cls_F',
    '  B["Run boot.py"]:::cls_B',
    '  M{{"main.py on the Pico?"}}:::cls_M',
    '  R["Run main.py"]:::cls_R',
    '  L["Main loop: clock ticks"]:::cls_L',
    '  U{{"USB connected to Thonny?"}}:::cls_U',
    '  Q(">>> REPL prompt"):::cls_Q',
    '  P --> F',
    '  F --> B',
    '  B --> M',
    '  M -->|Yes| R',
    '  R --> L',
    '  L --> U',
    '  U -->|No| L',
    '  U -->|Yes: Stop or Ctrl+C| Q',
    '  M -->|No| Q'
  ];
  // style each node for the current mode
  for (const id of Object.keys(STEP_INFO)) {
    let style;
    if (!p.active.includes(id)) {
      style = 'fill:gainsboro,stroke:darkgray,stroke-width:1px,stroke-dasharray:5 4,color:gray';
    } else if (p.changed.includes(id)) {
      style = 'fill:steelblue,stroke:darkorange,stroke-width:5px,color:white';
    } else {
      style = 'fill:steelblue,stroke:midnightblue,stroke-width:2px,color:white';
    }
    lines.push('  classDef cls_' + id + ' ' + style + ',font-size:16px');
  }
  // style each arrow
  for (let e = 0; e <= 8; e++) {
    let style;
    if (!p.activeEdges.includes(e)) style = 'stroke:darkgray,stroke-width:1px,stroke-dasharray:5 4';
    else if (p.changedEdges.includes(e)) style = 'stroke:darkorange,stroke-width:4px';
    else style = 'stroke:midnightblue,stroke-width:2px';
    lines.push('  linkStyle ' + e + ' ' + style + ',font-size:15px');
  }
  // a click directive for every node calls showStep(nodeId)
  for (const id of Object.keys(STEP_INFO)) {
    lines.push('  click ' + id + ' showStep "Click for details"');
  }
  return lines.join('\n');
}

// Called by Mermaid's click directives with the node id
function showStep(id) {
  const info = STEP_INFO[id];
  if (!info) return;
  const onPath = PATHS[mode].active.includes(id);
  const card = document.getElementById('info-card');
  card.innerHTML = '<h3>' + info.title + '</h3><p>' + info.text + '</p>' +
    (onPath ? '' : '<p class="placeholder">This step is skipped when there is no main.py.</p>');
  // move the card down near the clicked node on wide screens
  const node = findNode(id);
  const panel = document.getElementById('info');
  if (node && window.innerWidth > 600) {
    const nodeTop = node.getBoundingClientRect().top - panel.getBoundingClientRect().top;
    const maxTop = panel.clientHeight - card.offsetHeight - 24;
    card.style.top = Math.max(0, Math.min(nodeTop - 20, maxTop)) + 'px';
  } else {
    card.style.top = '0px';
  }
}
window.showStep = showStep;

function findNode(id) {
  const nodes = document.querySelectorAll('#diagram .node');
  for (const n of nodes) {
    if (new RegExp('-' + id + '-\\d+$').test(n.id)) return n;
  }
  return null;
}

async function renderDiagram() {
  const el = document.getElementById('diagram');
  renderCount++;
  const { svg, bindFunctions } = await mermaid.render('startup-svg-' + renderCount, diagramText());
  el.innerHTML = svg;
  if (bindFunctions) bindFunctions(el);
}

document.addEventListener('DOMContentLoaded', function () {
  mermaid.initialize({
    startOnLoad: false,
    securityLevel: 'loose',      // needed for click callbacks
    theme: 'default',
    flowchart: { useMaxWidth: true, htmlLabels: true, curve: 'basis', nodeSpacing: 40, rankSpacing: 30, padding: 8 },
    themeVariables: { fontSize: '16px', fontFamily: 'Arial, Helvetica, sans-serif' }
  });
  document.querySelectorAll('input[name="mainpy"]').forEach(function (r) {
    r.addEventListener('change', function () {
      mode = this.value;
      renderDiagram();
      const card = document.getElementById('info-card');
      card.style.top = '0px';
      card.innerHTML = mode === 'yes'
        ? '<h3>Has main.py</h3><p>The Pico runs your clock by itself. The orange steps are the part ' +
          'that only happens because <code>main.py</code> exists.</p><p class="placeholder">Click any step for details.</p>'
        : '<h3>No main.py</h3><p>After booting, the Pico skips straight to the REPL prompt (orange) and ' +
          'waits. The gray steps never run.</p><p class="placeholder">Click any step for details.</p>';
    });
  });
  renderDiagram();
});
