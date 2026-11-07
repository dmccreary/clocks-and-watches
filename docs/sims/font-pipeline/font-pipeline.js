// Font Pipeline - Mermaid
// CANVAS_HEIGHT: 440
// Steps from a TrueType font on your computer to large text on the OLED, using
// Peter Hinch's font_to_py.py converter and writer.py. Every node has a Mermaid click
// directive that fills the info panel. A second view estimates the font module's size.

const DIAGRAM = `
flowchart LR
    subgraph PC["On your computer"]
        direction TB
        TTF["TrueType font file<br/>FreeSans.ttf"]:::file
        F2P["font_to_py.py<br/>height 32<br/>-c 0123456789:"]:::tool
        MODF["Generated module<br/>freesans32.py"]:::file
        TTF --> F2P --> MODF
    end
    COPY["Copy to the Pico<br/>mpremote or Thonny"]:::copy
    subgraph PICO["On the Pico"]
        direction TB
        IMP["import freesans32"]:::code
        WR["Writer(oled, freesans32)"]:::code
        SCR["Text on screen<br/>12:34"]:::screen
        IMP --> WR --> SCR
    end
    PC --> COPY --> PICO

    click TTF call showInfo("TTF")
    click F2P call showInfo("F2P")
    click MODF call showInfo("MODF")
    click COPY call showInfo("COPY")
    click IMP call showInfo("IMP")
    click WR call showInfo("WR")
    click SCR call showInfo("SCR")

    classDef file fill:#fff3c4,stroke:#b38600,stroke-width:2px,color:#000,font-size:16px
    classDef tool fill:#ffe0cc,stroke:#c05000,stroke-width:2px,color:#000,font-size:16px
    classDef copy fill:#e8dcff,stroke:#5b3fa0,stroke-width:2px,color:#000,font-size:16px
    classDef code fill:#dbe8ff,stroke:#1f4e9c,stroke-width:2px,color:#000,font-size:16px
    classDef screen fill:#222,stroke:#000,stroke-width:2px,color:#96dcff,font-size:16px
`;

const nodeInfo = {
  TTF: { title: 'TrueType font file', cmd: '',
    text: 'A .ttf or .otf file on your computer describes letter shapes as smooth outlines, not pixels. It can be drawn at any size, but the Pico cannot read it directly.' },
  F2P: { title: 'font_to_py.py converter', cmd: 'python font_to_py.py FreeSans.ttf 32 freesans32.py -c 0123456789:',
    text: 'Runs on your computer, not the Pico. It draws each character at the height you choose (32 pixels here) and saves the bitmaps. -c lists only the characters you need, which keeps the file small.' },
  MODF: { title: 'Generated module', cmd: 'freesans32.py',
    text: 'A normal Python file that holds the bitmaps as bytes, plus each character\'s width. Open it and you will see long rows of \\x.. byte values.' },
  COPY: { title: 'Copy to the Pico', cmd: 'mpremote cp freesans32.py :',
    text: 'Put the font module (and writer.py) on the Pico\'s flash, using mpremote or Thonny\'s file panel. Chapter 4 shows how.' },
  IMP: { title: 'import on the Pico', cmd: 'import writer\nimport freesans32',
    text: 'Importing loads the font data into RAM. Bigger fonts with more characters use more memory, so import only the fonts the screen needs.' },
  WR: { title: 'Writer', cmd: 'wri = writer.Writer(oled, freesans32)\nwriter.Writer.set_textpos(oled, 10, 4)\nwri.printstring("12:34")',
    text: 'The Writer copies each character\'s bitmap into the OLED framebuffer at the text position (row, column). Make one Writer per font.' },
  SCR: { title: 'Text on screen', cmd: 'oled.show()',
    text: 'Like any drawing, the large digits appear only after show() sends the framebuffer to the display.' }
};

window.showInfo = function (id) {
  const n = nodeInfo[id];
  if (!n) return;
  document.querySelectorAll('#diagram .node').forEach(el => el.classList.remove('selected'));
  const el = document.querySelector('#diagram .node[data-step="' + id + '"]');
  if (el) el.classList.add('selected');
  document.getElementById('info').innerHTML =
    '<div class="info-title">' + n.title + '</div>' +
    '<div class="info-text">' + n.text + '</div>' +
    (n.cmd ? '<code class="cmd">' + n.cmd.replace(/</g, '&lt;') + '</code>' : '');
};

// ---------- memory estimate view ----------
const RAM_BYTES = 264 * 1024;

function uniqueChars(s) {
  return Array.from(new Set(Array.from(s))).length;
}

function updateMemory() {
  const h = Number(document.getElementById('height').value);
  const n = uniqueChars(document.getElementById('chars').value);
  const w = Math.ceil(0.6 * h);                  // average glyph width estimate
  const rowBytes = Math.ceil(w / 8);              // each pixel row is padded to whole bytes
  const glyphBytes = h * rowBytes;
  const overhead = 6;                             // width field + index entry per character
  const total = n * (glyphBytes + overhead);
  document.getElementById('heightVal').textContent = h + ' px';
  document.getElementById('memSteps').innerHTML =
    'Average width &asymp; 0.6 &times; ' + h + ' = <b>' + w + ' px</b>, so each row needs ' +
    'ceil(' + w + ' / 8) = <b>' + rowBytes + ' byte' + (rowBytes > 1 ? 's' : '') + '</b><br>' +
    'One glyph &asymp; ' + h + ' rows &times; ' + rowBytes + ' = <b>' + glyphBytes + ' bytes</b> + ' + overhead + ' bytes of index<br>' +
    n + ' characters &times; ' + (glyphBytes + overhead) + ' = <b>' + total.toLocaleString() + ' bytes &asymp; ' +
    (total / 1024).toFixed(1) + ' KB</b>';
  const pct = 100 * total / RAM_BYTES;
  const bar = document.getElementById('memBar');
  bar.style.width = Math.min(100, Math.max(0.5, pct)) + '%';
  bar.style.background = pct > 20 ? '#c0392b' : (pct > 5 ? '#e69500' : '#2e8b57');
  document.getElementById('memBarLabel').innerHTML = 'About <b>' + pct.toFixed(1) +
    '%</b> of the Pico\'s 264 KB of RAM once imported.';
}

function showView(v) {
  document.getElementById('pipelineView').style.display = v === 'pipe' ? 'flex' : 'none';
  document.getElementById('memoryView').style.display = v === 'mem' ? 'block' : 'none';
  document.getElementById('pipeBtn').classList.toggle('active', v === 'pipe');
  document.getElementById('memBtn').classList.toggle('active', v === 'mem');
  if (v === 'mem') updateMemory();
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
    node.setAttribute('data-step', id);
    node.addEventListener('mouseenter', () => window.showInfo(id));
  });

  document.getElementById('pipeBtn').addEventListener('click', () => showView('pipe'));
  document.getElementById('memBtn').addEventListener('click', () => showView('mem'));
  document.getElementById('height').addEventListener('input', updateMemory);
  document.getElementById('chars').addEventListener('input', updateMemory);
  document.getElementById('digitsBtn').addEventListener('click', () => {
    document.getElementById('chars').value = '0123456789:';
    updateMemory();
  });
  document.getElementById('asciiBtn').addEventListener('click', () => {
    let s = '';
    for (let c = 32; c < 127; c++) s += String.fromCharCode(c);
    document.getElementById('chars').value = s;
    updateMemory();
  });
  updateMemory();
});
