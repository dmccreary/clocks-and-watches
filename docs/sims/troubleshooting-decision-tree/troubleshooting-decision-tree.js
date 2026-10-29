// Troubleshooting Decision Tree - Mermaid
// CANVAS_HEIGHT: 600
// A clickable troubleshooting tree for Pico clocks. The overview shows the five symptom
// families; clicking a symptom draws that branch as a Mermaid flowchart. Every node has a
// Mermaid click directive that selects it, highlights the path from the root, shows the
// reasoning and the test to run, and updates the breadcrumb. "Start over" returns to the root.

// Each node: label (short, shown in the diagram), parent, answer (edge label from the parent),
// kind (root, symptom, question, fix), why (reasoning), test (what to do), ch (chapter to review)
const TREE = {
  R: { label: 'What is the symptom?', kind: 'root',
    why: 'Start by naming what you actually see. Each symptom points to a different family of causes, so the first question narrows the search.',
    test: 'Write the symptom down in one sentence before touching any wires or code.' },

  S1: { label: 'Nothing on the display', parent: 'R', kind: 'symptom',
    why: 'A blank screen can come from power, wiring, or code. Check them in that order: cheapest and most likely first.',
    test: 'Look for the power LED on the Pico and any backlight glow on the display.' },
  S1Q1: { label: 'Does the 3.3 V rail read 3.3 V?', parent: 'S1', kind: 'question',
    why: 'Without power nothing else matters, and a meter check takes ten seconds.',
    test: 'Set a multimeter to DC volts. Black probe on GND, red probe on 3V3(OUT). Expect 3.2 to 3.4 V.' },
  S1F1: { label: 'Fix the power: cable, port, VSYS/3V3 wiring', parent: 'S1Q1', answer: 'no', kind: 'fix', ch: 'Chapters 2 and 18',
    why: 'Try another USB cable (some are charge-only), another port, and check the power wires on the breadboard.',
    test: 'Re-measure the rail after each change.' },
  S1Q2: { label: 'Does the I2C scan find the display?', parent: 'S1Q1', answer: 'yes', kind: 'question',
    why: 'If the Pico cannot see the display on the bus, no drawing code can reach it.',
    test: 'In the REPL run i2c.scan(). An SSD1306 OLED usually answers at 0x3C (60). For SPI displays, check that the backlight lights.' },
  S1F2: { label: 'Swap SDA/SCL, add ground, check the pin pair', parent: 'S1Q2', answer: 'no', kind: 'fix', ch: 'Chapter 8',
    why: 'Swapped data and clock wires, a missing ground, or pins from two different I2C buses are the usual culprits.',
    test: 'Fix one wire at a time and run the scan again.' },
  S1Q3: { label: 'Does the code call show() after drawing?', parent: 'S1Q2', answer: 'yes', kind: 'question',
    why: 'Drawing commands only change the frame buffer in RAM. Nothing appears until show() sends it to the screen.',
    test: 'Search your code for show() and add print("shown") right after it.' },
  S1F3: { label: 'Add oled.show() after drawing', parent: 'S1Q3', answer: 'no', kind: 'fix', ch: 'Chapter 11',
    why: 'Call show() once after all the drawing for a frame is done.',
    test: 'Draw a rectangle border, call show(), and look for it.' },
  S1F4: { label: 'Check driver, size and contrast settings', parent: 'S1Q3', answer: 'yes', kind: 'fix', ch: 'Chapters 11 and 15',
    why: 'The wrong driver, a wrong width and height, or a contrast or backlight setting of zero can leave a working screen dark.',
    test: 'Run the kit\'s known-good example program for your display.' },

  S2: { label: 'Wrong image', parent: 'R', kind: 'symptom',
    why: 'If something appears but it looks wrong, the bus is working. The problem is in how the pixels are encoded or sent.',
    test: 'Draw a simple test pattern: a red, a green and a blue rectangle and a white border.' },
  S2Q1: { label: 'Shapes right but colors wrong?', parent: 'S2', kind: 'question',
    why: 'Swapped red and blue, or swapped bytes, keep the shapes intact but scramble the colors.',
    test: 'Fill the screen with pure red (0xF800). Does it look red?' },
  S2F1: { label: 'Fix RGB/BGR order or byte swap', parent: 'S2Q1', answer: 'yes', kind: 'fix', ch: 'Chapter 15',
    why: 'Change the color order setting in the driver, or swap the two bytes of each 16-bit color.',
    test: 'Repeat the red, green and blue fill test.' },
  S2Q2: { label: 'Random or noisy pixels?', parent: 'S2Q1', answer: 'no', kind: 'question',
    why: 'Fast signals on long jumper wires get corrupted, which shows up as speckles or garbage.',
    test: 'Lower the SPI baudrate (for example to 10 MHz) and redraw. Does the noise go away?' },
  S2F2: { label: 'Lower the SPI baudrate; shorten wires', parent: 'S2Q2', answer: 'yes', kind: 'fix', ch: 'Chapters 8 and 11',
    why: 'Use the highest baudrate that stays clean, and keep data wires short.',
    test: 'Raise the baudrate in steps until noise returns, then back off.' },
  S2F3: { label: 'Check width, height, rotation, offsets', parent: 'S2Q2', answer: 'no', kind: 'fix', ch: 'Chapter 11',
    why: 'An image that is shifted, mirrored or cut off usually means the driver was told the wrong size or rotation.',
    test: 'Draw a one-pixel border around the whole screen and see which edges are missing.' },

  S3: { label: 'Wrong time', parent: 'R', kind: 'symptom',
    why: 'How the time is wrong tells you why: a default date, a whole-hour offset, or slow drift each have a different cause.',
    test: 'Compare the clock with a phone and write down the exact difference.' },
  S3Q1: { label: 'Shows 2021 or 1970 after power-up?', parent: 'S3', kind: 'question',
    why: 'That is a default date. It means nothing set the clock after power was lost.',
    test: 'Unplug the clock, plug it back in, and print time.localtime() before any sync.' },
  S3F1: { label: 'Add an RTC or sync NTP at boot', parent: 'S3Q1', answer: 'yes', kind: 'fix', ch: 'Chapters 6, 13 and 14',
    why: 'Read the DS3231 at startup, or connect to WiFi and sync with NTP before showing the time.',
    test: 'Repeat the power-cycle test.' },
  S3Q2: { label: 'Off by whole hours?', parent: 'S3Q1', answer: 'no', kind: 'question',
    why: 'Whole-hour errors come from the time zone or daylight saving time, not from a slow clock.',
    test: 'Is the error exactly 1, 5, 6 or some other whole number of hours?' },
  S3F2: { label: 'Fix the time zone or DST offset', parent: 'S3Q2', answer: 'yes', kind: 'fix', ch: 'Chapter 14',
    why: 'NTP gives UTC. Add your time zone offset, and the DST hour when it applies. Thonny may also set local time instead of UTC.',
    test: 'Check the clock on both sides of a DST change date.' },
  S3Q3: { label: 'Drifts a few seconds a day?', parent: 'S3Q2', answer: 'no', kind: 'question',
    why: 'Slow, steady drift comes from the crystal. Sudden jumps point at code.',
    test: 'Note the error now and again after 24 hours.' },
  S3F3: { label: 'Use the DS3231 or sync NTP regularly', parent: 'S3Q3', answer: 'yes', kind: 'fix', ch: 'Chapters 13 and 14',
    why: 'The DS3231 is temperature compensated and far more accurate than the Pico crystal; NTP corrects any drift.',
    test: 'Measure the drift again over a day.' },
  S3F4: { label: 'Test rollovers: midnight, noon, month end', parent: 'S3Q3', answer: 'no', kind: 'fix', ch: 'Chapter 20',
    why: 'Jumps at special moments are bugs in the time math, such as 12-hour conversion or day rollover.',
    test: 'Set the time to 23:59:50 and watch midnight pass.' },

  S4: { label: 'Buttons misbehave', parent: 'R', kind: 'symptom',
    why: 'Button problems are either electrical (bounce, pull-ups) or logic (the mode state machine).',
    test: 'Write a tiny test program that only prints the button value.' },
  S4Q1: { label: 'One press counts as several?', parent: 'S4', kind: 'question',
    why: 'Metal contacts bounce for a few milliseconds, which looks like many fast presses.',
    test: 'Print a counter each time a press is detected, then press once.' },
  S4F1: { label: 'Debounce: ignore presses within 50 ms', parent: 'S4Q1', answer: 'yes', kind: 'fix', ch: 'Chapter 7',
    why: 'Record the time of the last accepted press with ticks_ms() and ignore any press that comes too soon.',
    test: 'Press 10 times and check the counter reads 10.' },
  S4Q2: { label: 'Pressing does nothing at all?', parent: 'S4Q1', answer: 'no', kind: 'question',
    why: 'If value() never changes, the problem is the wiring or the pull-up, not the logic.',
    test: 'Print button.value() in a loop while pressing and releasing.' },
  S4F2: { label: 'Use Pin.PULL_UP; wire button to GND', parent: 'S4Q2', answer: 'yes', kind: 'fix', ch: 'Chapter 7',
    why: 'Without a pull-up the input floats. With PULL_UP the pin reads 1 until the button connects it to ground.',
    test: 'Repeat the value() test: expect 1 released and 0 pressed.' },
  S4F3: { label: 'Check the mode state machine logic', parent: 'S4Q2', answer: 'no', kind: 'fix', ch: 'Chapter 7',
    why: 'The button works, so trace which state the program is in and which event it receives.',
    test: 'Print the state name after every button event.' },

  S5: { label: 'Random resets', parent: 'R', kind: 'symptom',
    why: 'A clock that restarts is either losing power for an instant or crashing in code.',
    test: 'Note exactly what the clock was doing just before each reset.' },
  S5Q1: { label: 'Resets when WiFi, backlight or buzzer turns on?', parent: 'S5', kind: 'question',
    why: 'A sudden load can pull the supply voltage down for a moment. This is called a brownout.',
    test: 'Watch the 3.3 V rail with a multimeter while the load turns on.' },
  S5F1: { label: 'Stronger supply, short wires, add a capacitor', parent: 'S5Q1', answer: 'yes', kind: 'fix', ch: 'Chapter 18',
    why: 'Use a better USB supply or fresh batteries, shorten the power wires, and add a capacitor near the load.',
    test: 'Turn the load on and off 20 times without a reset.' },
  S5Q2: { label: 'Thonny shows a traceback?', parent: 'S5Q1', answer: 'no', kind: 'question',
    why: 'A crash followed by a restart looks like a reset. The traceback names the real cause.',
    test: 'Run the program from Thonny and read the last line of the error.' },
  S5F2: { label: 'Fix the error; wrap network code in try/except', parent: 'S5Q2', answer: 'yes', kind: 'fix', ch: 'Chapters 3 and 14',
    why: 'Network calls fail sometimes. Catch the error and keep the last good value instead of crashing.',
    test: 'Turn the WiFi router off and check the clock keeps running.' },
  S5F3: { label: 'Check memory: print gc.mem_free()', parent: 'S5Q2', answer: 'no', kind: 'fix', ch: 'Chapter 20',
    why: 'If free memory shrinks over time the program eventually runs out and stops.',
    test: 'Print gc.mem_free() every minute for an hour.' }
};

let current = 'R';
let renderCount = 0;

function children(id) {
  return Object.keys(TREE).filter(k => TREE[k].parent === id);
}

function pathTo(id) {
  const p = [];
  let k = id;
  while (k) {
    p.unshift(k);
    k = TREE[k].parent;
  }
  return p;
}

// Which symptom branch does this node belong to (null for the root)?
function branchOf(id) {
  const p = pathTo(id);
  return p.length > 1 ? p[1] : null;
}

function shape(id) {
  const n = TREE[id];
  const t = '"' + n.label + '"';
  if (n.kind === 'root') return id + '([' + t + '])';
  if (n.kind === 'symptom') return id + '(' + t + ')';
  if (n.kind === 'question') return id + '{{' + t + '}}';
  return id + '[' + t + ']';
}

function buildMermaid() {
  const branch = branchOf(current);
  const lines = [];
  let ids;
  if (!branch) {
    lines.push('flowchart LR');
    ids = ['R'].concat(children('R'));
    for (const s of children('R')) lines.push('  ' + shape('R') + ' --> ' + shape(s));
  } else {
    lines.push('flowchart TD');
    ids = ['R'];
    const walk = (id) => {
      for (const c of children(id)) {
        ids.push(c);
        const lab = TREE[c].answer ? ' -- ' + TREE[c].answer + ' --> ' : ' --> ';
        lines.push('  ' + shape(id) + lab + shape(c));
        walk(c);
      }
    };
    ids.push(branch);
    lines.push('  ' + shape('R') + ' --> ' + shape(branch));
    walk(branch);
  }
  // styles: kind colors, then the path from the root, then the current node
  lines.push('  classDef kroot fill:#e5e7eb,stroke:#555,color:#111,font-size:16px');
  lines.push('  classDef ksymptom fill:#dbeafe,stroke:#1d4f91,color:#111,font-size:16px');
  lines.push('  classDef kquestion fill:#ffedd5,stroke:#c2410c,color:#111,font-size:16px');
  lines.push('  classDef kfix fill:#dcfce7,stroke:#166534,color:#111,font-size:16px');
  lines.push('  classDef onpath stroke:#1d4f91,stroke-width:3px');
  lines.push('  classDef current fill:#fde68a,stroke:#b45309,stroke-width:4px,color:#111');
  const path = pathTo(current);
  for (const id of ids) {
    let cls = 'k' + TREE[id].kind;
    if (id === current) cls = 'current';
    else if (path.includes(id)) cls = cls + ',onpath';
    lines.push('  class ' + id + ' ' + cls.split(',')[0]);
    if (cls.includes(',onpath')) lines.push('  class ' + id + ' onpath');
  }
  // every node is clickable through a Mermaid click directive
  for (const id of ids) lines.push('  click ' + id + ' call pick("' + id + '")');
  lines.push('  linkStyle default font-size:15px');
  return lines.join('\n');
}

// Called by the Mermaid click directives
window.pick = function (id) {
  if (!TREE[id]) return;
  current = id;
  render();
};

function showInfo(id, preview) {
  const n = TREE[id];
  const kindName = { root: 'Start', symptom: 'Symptom', question: 'Question', fix: 'Suggested fix' }[n.kind];
  let html = '<span class="kind k-' + n.kind + '">' + kindName + (preview ? ' (preview)' : '') + '</span>';
  html += '<h3>' + n.label + '</h3>';
  html += '<div class="label">' + (n.kind === 'fix' ? 'What to do' : 'Why ask this') + '</div><div>' + n.why + '</div>';
  html += '<div class="label">' + (n.kind === 'fix' ? 'Confirm it worked' : 'Test to run') + '</div><div>' + n.test + '</div>';
  if (n.ch) html += '<div class="label">Review</div><div>' + n.ch + '</div>';
  const kids = children(id);
  if (!preview) {
    if (n.kind === 'root') html += '<div class="hint">Click the symptom you see.</div>';
    else if (kids.length) html += '<div class="hint">Run the test, then click the ' +
      (kids.some(k => TREE[k].answer) ? '<b>yes</b> or <b>no</b>' : 'next') + ' box below this one.</div>';
    else html += '<div class="hint">Apply the fix and test again. If the problem remains, press Start over.</div>';
  }
  html += '<div class="legend">Key: <span class="sw" style="background:#dbeafe"></span>symptom' +
    '<span class="sw" style="background:#ffedd5"></span>question<span class="sw" style="background:#dcfce7"></span>fix' +
    '<span class="sw" style="background:#fde68a"></span>you are here</div>';
  document.getElementById('info').innerHTML = html;
}

function showCrumbs() {
  const p = pathTo(current);
  const parts = p.map(id => {
    const ans = TREE[id].answer ? '<span class="ans">' + TREE[id].answer + '</span> → ' : '';
    return ans + '<span class="crumb">' + TREE[id].label + '</span>';
  });
  document.getElementById('crumbs').innerHTML = 'Path: ' + parts.join(' &rsaquo; ');
}

async function render() {
  const el = document.getElementById('diagram');
  const code = buildMermaid();
  renderCount++;
  const { svg, bindFunctions } = await mermaid.render('tdt' + renderCount, code);
  el.innerHTML = svg;
  if (bindFunctions) bindFunctions(el);
  const s = el.querySelector('svg');
  if (s) {
    s.removeAttribute('height');
    s.style.maxWidth = '100%';
    s.style.height = '100%';
  }
  // hover preview of any node's details; leaving restores the selected node
  el.querySelectorAll('.node').forEach(node => {
    const m = node.id.match(/flowchart-(.+)-\d+$/);
    if (!m || !TREE[m[1]]) return;
    node.addEventListener('mouseenter', () => { if (m[1] !== current) showInfo(m[1], true); });
    node.addEventListener('mouseleave', () => showInfo(current, false));
  });
  showInfo(current, false);
  showCrumbs();
}

document.addEventListener('DOMContentLoaded', function () {
  mermaid.initialize({
    startOnLoad: false,
    securityLevel: 'loose',
    theme: 'default',
    flowchart: { useMaxWidth: true, htmlLabels: true, curve: 'basis', wrappingWidth: 170, rankSpacing: 28, nodeSpacing: 22, padding: 6 }
  });
  document.getElementById('startOver').addEventListener('click', () => { current = 'R'; render(); });
  render();
});
