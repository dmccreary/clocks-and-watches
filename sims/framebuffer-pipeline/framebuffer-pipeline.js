// Framebuffer Pipeline - Mermaid
// CANVAS_HEIGHT: 545
// The path from a drawing call to lit pixels on an SSD1306 OLED. Every node has a Mermaid
// click directive that fills the info panel. A toggle highlights the "Before show()" state
// (only the RAM buffer has changed) and the "After show()" state (the bytes reach the panel).

const DIAGRAM = `
flowchart LR
    subgraph PICO["Inside the Pico"]
        direction TB
        PROG["Your program<br/>clock.py"]:::code
        DRAW["Drawing calls<br/>oled.text()<br/>oled.pixel()"]:::code
        FB["Framebuffer in RAM<br/>1,024 bytes"]:::ram
        SHOW["oled.show()"]:::code
        PROG --> DRAW --> FB --> SHOW
    end
    BUS["I2C or SPI bus<br/>about 1,030 bytes<br/>per show()"]:::bus
    subgraph MOD["OLED module"]
        direction TB
        CTRL["SSD1306 controller<br/>memory, 1,024 bytes"]:::chip
        PANEL["OLED panel<br/>8,192 pixels"]:::panel
        CTRL --> PANEL
    end
    PICO --> BUS --> MOD

    click PROG call showInfo("PROG")
    click DRAW call showInfo("DRAW")
    click FB call showInfo("FB")
    click SHOW call showInfo("SHOW")
    click BUS call showInfo("BUS")
    click CTRL call showInfo("CTRL")
    click PANEL call showInfo("PANEL")

    classDef code fill:#dbe8ff,stroke:#1f4e9c,stroke-width:2px,color:#000,font-size:16px
    classDef ram fill:#fff3c4,stroke:#b38600,stroke-width:2px,color:#000,font-size:16px
    classDef bus fill:#e8dcff,stroke:#5b3fa0,stroke-width:2px,color:#000,font-size:16px
    classDef chip fill:#d8f3dc,stroke:#2d6a4f,stroke-width:2px,color:#000,font-size:16px
    classDef panel fill:#222,stroke:#000,stroke-width:2px,color:#96dcff,font-size:16px
`;

const nodeInfo = {
  PROG: { title: 'Your program', bytes: 'Bytes: none yet. It only decides what to draw.',
    text: 'Your MicroPython code reads the time and decides what the screen should show, for example "12:35".' },
  DRAW: { title: 'Drawing calls', bytes: 'Bytes: changes a few bytes in RAM per call.',
    text: 'oled.fill(), oled.text() and oled.pixel() only change bytes in the framebuffer. They do not touch the display, so they are fast and nothing appears yet.' },
  FB: { title: 'Framebuffer in RAM', bytes: 'Bytes: 128 x 64 / 8 = 1,024 bytes.',
    text: 'A bytearray in the Pico\'s RAM holding one bit per pixel. Each byte is a vertical strip of 8 pixels in one column (MONO_VLSB layout).' },
  SHOW: { title: 'oled.show()', bytes: 'Bytes: copies all 1,024 bytes every call.',
    text: 'The only step that talks to the hardware. It sends a few setup commands, then the whole buffer. Call it once per frame, after all the drawing.' },
  BUS: { title: 'I2C or SPI bus', bytes: 'Bytes: about 1,024 data + a few command bytes.',
    text: 'The wires carry the buffer to the module. At 400 kHz I2C this takes about 23 ms (9 clocks per byte). At 10 MHz SPI it takes under 1 ms.' },
  CTRL: { title: 'SSD1306 controller memory', bytes: 'Bytes: stores the same 1,024 bytes.',
    text: 'The driver chip on the module keeps its own copy of the screen (its display RAM) and keeps refreshing the panel from it, even if the Pico stops.' },
  PANEL: { title: 'OLED panel', bytes: 'Bytes: none. 8,192 pixels glow or stay dark.',
    text: 'Each lit bit becomes a glowing pixel. The panel changes only when new bytes reach the controller, which happens only after show().' }
};

const BEFORE_NODES = ['PROG', 'DRAW', 'FB'];
const AFTER_NODES = ['SHOW', 'BUS', 'CTRL', 'PANEL'];
let phase = 'before';
let nodeEls = {};

// called by the Mermaid click directives (needs securityLevel: 'loose')
window.showInfo = function (id) {
  const n = nodeInfo[id];
  if (!n) return;
  document.getElementById('info').innerHTML =
    '<div class="info-title">' + n.title + '</div>' +
    '<div class="info-text">' + n.text + '</div>' +
    '<div class="bytes">' + n.bytes + '</div>';
};

function setPhase(p) {
  phase = p;
  document.getElementById('beforeBtn').classList.toggle('active', p === 'before');
  document.getElementById('afterBtn').classList.toggle('active', p === 'after');
  const hot = p === 'before' ? BEFORE_NODES : BEFORE_NODES.concat(AFTER_NODES);
  Object.keys(nodeEls).forEach(id => {
    const el = nodeEls[id];
    const isHot = hot.includes(id);
    el.classList.toggle('dim', !isHot);
    el.classList.toggle('hot', p === 'after' ? AFTER_NODES.includes(id) : isHot);
  });
  const state = document.getElementById('state');
  if (p === 'before') {
    state.innerHTML = '<b>Before show():</b> <span class="why">the program drew "12:35" into RAM. ' +
      'The panel still shows the old picture.</span>' +
      '<div class="screens">' +
      '<div class="screen"><div class="oled changed">12:35</div>framebuffer (RAM)</div>' +
      '<div class="screen"><div class="oled">12:34</div>OLED panel</div></div>';
  } else {
    state.innerHTML = '<b>After show():</b> <span class="why">all 1,024 bytes crossed the bus, ' +
      'so the panel now matches the buffer.</span>' +
      '<div class="screens">' +
      '<div class="screen"><div class="oled">12:35</div>framebuffer (RAM)</div>' +
      '<div class="screen"><div class="oled changed">12:35</div>OLED panel</div></div>';
  }
}

document.addEventListener('DOMContentLoaded', async function () {
  mermaid.initialize({
    startOnLoad: false,
    securityLevel: 'loose',
    theme: 'default',
    flowchart: { useMaxWidth: true, htmlLabels: true, curve: 'basis', nodeSpacing: 30, rankSpacing: 40,
      subGraphTitleMargin: { top: 10, bottom: 14 } }
  });
  const el = document.getElementById('diagram');
  el.textContent = DIAGRAM;
  await mermaid.run({ nodes: [el] });

  document.querySelectorAll('#diagram .node').forEach(node => {
    const id = (node.id.match(/flowchart-(.+)-\d+$/) || [])[1];
    if (!nodeInfo[id]) return;
    nodeEls[id] = node;
    node.addEventListener('mouseenter', () => window.showInfo(id));
  });
  document.getElementById('beforeBtn').addEventListener('click', () => setPhase('before'));
  document.getElementById('afterBtn').addEventListener('click', () => setPhase('after'));
  setPhase('before');
});
