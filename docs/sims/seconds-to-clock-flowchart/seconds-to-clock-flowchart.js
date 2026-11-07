// Seconds-to-Clock Flowchart - Mermaid MicroSim
// CANVAS_HEIGHT: 540
// Steps a number of seconds since midnight through the algorithm
//   hours = seconds // 3600, left = seconds % 3600,
//   minutes = left // 60, seconds = left % 60
// Each press of "Next step" runs one box, writes its value into the box,
// and highlights it. Clicking a box (Mermaid click directive) explains it.

// One-sentence explanation for each node (shown when a box is clicked)
const nodeInfo = {
  S: 'The algorithm starts with one number: how many seconds have passed since midnight (0 to 86,399).',
  H: 'There are 3,600 seconds in an hour, so whole-number division by 3,600 counts the complete hours.',
  L: 'The remainder (%) keeps the seconds that did not fit into a whole hour, so nothing is lost.',
  M: 'There are 60 seconds in a minute, so whole-number division of the leftover seconds by 60 counts the minutes.',
  SEC: 'The remainder after dividing the leftover by 60 is the seconds that did not make a full minute.',
  SHOW: 'The three numbers are joined with colons, each padded to two digits, so 9 shows as 09.'
};

const nodeTitles = {
  S: 'Start: total seconds',
  H: 'hours = seconds // 3600',
  L: 'left = seconds % 3600',
  M: 'minutes = left // 60',
  SEC: 'seconds = left % 60',
  SHOW: 'Show hours:minutes:seconds'
};

const order = ['S', 'H', 'L', 'M', 'SEC', 'SHOW'];
let step = 0;            // number of boxes already run (0 = none)
let total = 45296;
let renderCount = 0;

function pad2(n) {
  return String(n).padStart(2, '0');
}

// Compute every intermediate value for the current input
function computeValues(t) {
  const hours = Math.floor(t / 3600);
  const left = t % 3600;
  const minutes = Math.floor(left / 60);
  const seconds = left % 60;
  return {
    S: String(t),
    H: String(hours),
    L: String(left),
    M: String(minutes),
    SEC: String(seconds),
    SHOW: pad2(hours) + ':' + pad2(minutes) + ':' + pad2(seconds),
    hours, left, minutes, seconds
  };
}

// Mermaid uses % for comments, so write it with an entity code inside labels
function esc(s) {
  return s.replace(/%/g, '#37;');
}

function buildDefinition() {
  const v = computeValues(total);
  let def = 'flowchart TD\n';
  order.forEach((id, i) => {
    const valueLine = i < step ? '<b>= ' + v[id] + '</b>' : '= ?';
    const shape = (id === 'S' || id === 'SHOW') ? ['([', '])'] : ['[', ']'];
    def += `    ${id}${shape[0]}"${esc(nodeTitles[id])}<br/>${valueLine}"${shape[1]}\n`;
  });
  def += '    S --> H --> L --> M --> SEC --> SHOW\n';
  order.forEach((id, i) => {
    let cls = 'pending';
    if (i === step - 1) cls = 'current';
    else if (i < step - 1) cls = 'done';
    def += `    class ${id} ${cls}\n`;
    def += `    click ${id} call showNodeInfo("${id}")\n`;
  });
  def += '    classDef pending fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#0d2a4a,font-size:16px\n';
  def += '    classDef current fill:#ffd54f,stroke:#e65100,stroke-width:4px,color:#000,font-size:16px\n';
  def += '    classDef done fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px,color:#1b3a1d,font-size:16px\n';
  return def;
}

async function renderDiagram() {
  const el = document.getElementById('diagram');
  try {
    const { svg, bindFunctions } = await mermaid.render('flowSvg' + (renderCount++), buildDefinition());
    el.innerHTML = svg;
    // Scale the drawing to fit the panel in both directions
    const svgEl = el.querySelector('svg');
    if (svgEl) {
      svgEl.removeAttribute('height');
      svgEl.setAttribute('preserveAspectRatio', 'xMidYMin meet');
    }
    if (bindFunctions) bindFunctions(el);
  } catch (err) {
    el.textContent = 'Diagram could not be drawn: ' + err.message;
  }
}

// Called by the Mermaid click directive
window.showNodeInfo = function (id) {
  const box = document.getElementById('nodeInfo');
  box.innerHTML = '<h4>' + nodeTitles[id] + '</h4>' + nodeInfo[id];
};

// Explain what the step that just ran did, using the real numbers
function updateStepText() {
  const v = computeValues(total);
  const box = document.getElementById('stepText');
  const next = order[step];
  const predict = next
    ? '<br/><i>Predict the next value, then press Next step.</i>'
    : '<br/><i>Done! Try a new number or press Reset.</i>';
  let html = '';
  switch (step) {
    case 0:
      html = '<h4>Step 0 of 6</h4>Press <b>Next step</b> to start tracing ' + total + ' seconds through the algorithm.';
      box.innerHTML = html;
      return;
    case 1:
      html = 'Start with <span class="result">' + total + '</span> seconds since midnight.';
      break;
    case 2:
      html = total + ' // 3600 = <span class="result">' + v.hours + '</span><br/>because ' +
        v.hours + ' &times; 3600 = ' + (v.hours * 3600) + ' fits, but ' + (v.hours + 1) +
        ' &times; 3600 = ' + ((v.hours + 1) * 3600) + ' is too big.';
      break;
    case 3:
      html = total + ' % 3600 = <span class="result">' + v.left + '</span><br/>because ' +
        total + ' &minus; ' + (v.hours * 3600) + ' = ' + v.left + ' seconds are left over.';
      break;
    case 4:
      html = v.left + ' // 60 = <span class="result">' + v.minutes + '</span><br/>because ' +
        v.minutes + ' &times; 60 = ' + (v.minutes * 60) + ' fits.';
      break;
    case 5:
      html = v.left + ' % 60 = <span class="result">' + v.seconds + '</span><br/>because ' +
        v.left + ' &minus; ' + (v.minutes * 60) + ' = ' + v.seconds + '.';
      break;
    case 6:
      html = 'The clock shows <span class="result">' + v.SHOW + '</span>';
      break;
  }
  box.innerHTML = '<h4>Step ' + step + ' of 6: ' + nodeTitles[order[step - 1]] + '</h4>' + html + predict;
}

function nextStep() {
  if (step < order.length) {
    step++;
    window.showNodeInfo(order[step - 1]);
    updateStepText();
    renderDiagram();
  }
}

function resetSteps() {
  step = 0;
  updateStepText();
  renderDiagram();
  document.getElementById('nodeInfo').innerHTML =
    '<h4>Step details</h4>Click any box in the flowchart to see what that step does.';
}

function readInput() {
  const input = document.getElementById('secInput');
  const msg = document.getElementById('inputMsg');
  const n = Number(input.value);
  if (input.value === '' || !Number.isInteger(n) || n < 0 || n > 86399) {
    msg.textContent = 'Enter a whole number from 0 to 86399.';
    return;
  }
  msg.textContent = '';
  total = n;
  resetSteps();
}

document.addEventListener('DOMContentLoaded', () => {
  mermaid.initialize({
    startOnLoad: false,
    securityLevel: 'loose',      // required for click ... call directives
    theme: 'default',
    flowchart: { useMaxWidth: true, htmlLabels: true, curve: 'basis', nodeSpacing: 30, rankSpacing: 26 }
  });
  document.getElementById('nextBtn').addEventListener('click', nextStep);
  document.getElementById('resetBtn').addEventListener('click', resetSteps);
  document.getElementById('secInput').addEventListener('change', readInput);
  document.getElementById('secInput').addEventListener('keyup', (e) => { if (e.key === 'Enter') readInput(); });
  updateStepText();
  renderDiagram();
});
