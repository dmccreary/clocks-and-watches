// NTP Stratum Hierarchy - vis-network
// CANVAS_HEIGHT: 560
// A top-down tree showing how time flows from a stratum 0 reference clock,
// through stratum 1 and 2 servers, to a Pico W client. Clicking a node explains
// its role. "Send request" steps a packet from the Pico to the chosen server and
// back, showing the four NTP timestamps (T1-T4) and how network delay limits accuracy.

// ---- Graph data (fixed positions form the stratum tiers) ----
const NODE_INFO = {
    s0: { title: 'Stratum 0: Atomic clock / GPS',
          text: 'The reference clocks: atomic clocks in national labs and the atomic clocks on GPS satellites. They are not on the internet. Servers connect to them by cable or radio.',
          accuracy: 'Nanoseconds', errorMs: 0 },
    s1a: { title: 'Stratum 1: time.nist.gov',
           text: 'A server wired directly to an atomic clock (here, the NIST clock in Boulder, Colorado). It is one step from the reference.',
           accuracy: 'About 0.01 ms (10 microseconds) of UTC', errorMs: 0.01 },
    s1b: { title: 'Stratum 1: GPS-disciplined server',
           text: 'A server with a GPS receiver on the roof. It gets time from the satellites, which carry atomic clocks.',
           accuracy: 'About 0.01 ms of UTC', errorMs: 0.01 },
    s2a: { title: 'Stratum 2: pool server A',
           text: 'Syncs from a stratum 1 server over the internet. Most servers you reach through pool.ntp.org are stratum 2 or 3.',
           accuracy: 'About 1 to 10 ms of UTC', errorMs: 2 },
    s2b: { title: 'Stratum 2: pool server B',
           text: 'Another volunteer server in the NTP pool. Each step down the tree adds a little delay and error.',
           accuracy: 'About 1 to 10 ms of UTC', errorMs: 2 },
    s2c: { title: 'Stratum 2: pool server C',
           text: 'A stratum 2 server that syncs from the GPS-disciplined stratum 1 server.',
           accuracy: 'About 1 to 10 ms of UTC', errorMs: 2 },
    s2d: { title: 'Stratum 2: pool server D',
           text: 'A stratum 2 server. Your Pico usually talks to a server like this one.',
           accuracy: 'About 1 to 10 ms of UTC', errorMs: 2 },
    pico: { title: 'Your Pico W (client)',
            text: 'The client. ntptime.settime() sends one 48-byte UDP request to port 123 and sets the internal clock from the reply. The Pico never serves time to anyone else.',
            accuracy: 'Limited by network delay: usually within a few tens of ms', errorMs: null }
};

const STRATUM_COLORS = {
    0: { background: '#ffe08a', border: '#c99a00' },
    1: { background: '#ffc7a8', border: '#d55e00' },
    2: { background: '#cfe3f7', border: '#0072b2' },
    3: { background: '#c9f0dc', border: '#009e73' }
};

function makeNode(id, label, x, y, stratum) {
    return { id, label, x, y, color: { ...STRATUM_COLORS[stratum],
        highlight: { background: 'gold', border: 'black' } }, stratum };
}

const nodes = new vis.DataSet([
    makeNode('s0', 'Atomic clock / GPS\nstratum 0', 0, -205, 0),
    makeNode('s1a', 'time.nist.gov\nstratum 1', -130, -100, 1),
    makeNode('s1b', 'GPS server\nstratum 1', 130, -104, 1),
    makeNode('s2a', 'Pool A\nstratum 2', -195, 2, 2),
    makeNode('s2b', 'Pool B\nstratum 2', -65, 6, 2),
    makeNode('s2c', 'Pool C\nstratum 2', 65, 2, 2),
    makeNode('s2d', 'Pool D\nstratum 2', 195, 6, 2),
    makeNode('pico', 'Your Pico W\n(client)', 0, 120, 3),
    { id: 'pkt', label: '', x: 0, y: 120, shape: 'dot', size: 11, hidden: true,
      color: { background: 'crimson', border: 'darkred' }, font: { size: 14, color: 'darkred', strokeWidth: 3, strokeColor: 'white' } }
]);

const edges = new vis.DataSet([
    { id: 'e1', from: 's0', to: 's1a' },
    { id: 'e2', from: 's0', to: 's1b' },
    { id: 'e3', from: 's1a', to: 's2a' },
    { id: 'e4', from: 's1a', to: 's2b' },
    { id: 'e5', from: 's1b', to: 's2c' },
    { id: 'e6', from: 's1b', to: 's2d' },
    { id: 'link', from: 'pico', to: 's2c', dashes: [6, 5], color: { color: 'crimson' }, width: 2, arrows: { to: false } }
]);

// ---- Request/reply stepper state ----
// step 0: idle, 1: request reached server, 2: server replied, 3: reply reached Pico
let step = 0;
let network;
let stamps = null;            // timestamps for the current exchange
const PICO_OFFSET_MS = -2350; // the Pico's clock starts 2.350 s slow
const PROCESSING_MS = 1;      // server time between receive (T2) and transmit (T3)
let animating = false;

function isInIframe() {
    try { return window.self !== window.top; } catch (e) { return true; }
}

function serverId() { return document.getElementById('server').value; }
function delayMs() { return parseInt(document.getElementById('delay').value, 10); }

// Format a time of day (ms after 12:00:00 true time) as hh:mm:ss.mmm
function clockString(ms) {
    const base = 12 * 3600 * 1000 + ms;
    const h = Math.floor(base / 3600000), m = Math.floor(base / 60000) % 60, s = Math.floor(base / 1000) % 60;
    const f = Math.round(base % 1000);
    return String(h).padStart(2, '0') + ':' + String(m).padStart(2, '0') + ':' + String(s).padStart(2, '0') + '.' + String(f).padStart(3, '0');
}

// Real networks are rarely symmetric: here the request takes 20% longer than the reply
function computeStamps() {
    const d = delayMs();
    const up = d * 1.2, down = d * 0.8;
    const t1 = 0;                                 // Pico clock when the request leaves
    const trueSend = t1 - PICO_OFFSET_MS;         // true time at that moment
    const t2 = trueSend + up;                     // server clock (accurate)
    const t3 = t2 + PROCESSING_MS;
    const t4 = t1 + up + PROCESSING_MS + down;    // Pico clock when the reply arrives
    const delta = (t4 - t1) - (t3 - t2);          // round-trip delay
    const theta = ((t2 - t1) + (t3 - t4)) / 2;    // estimated offset of the Pico clock
    return { t1, t2, t3, t4, delta, theta, trueOffset: -PICO_OFFSET_MS };
}

function renderStamps() {
    const box = document.getElementById('stamps');
    const id = serverId();
    const serverErr = NODE_INFO[id].errorMs;
    const d = delayMs();
    if (!stamps || step === 0) {
        box.innerHTML = '<strong>Press Send request</strong> to step a packet from the Pico to ' +
            NODE_INFO[id].title.split(': ')[1] + ' and back.<br>' +
            'Accuracy limit at this delay: about <strong>&plusmn;' + (d + serverErr).toFixed(2) + ' ms</strong> ' +
            '(half the ' + (2 * d) + ' ms round trip + server error).';
        return;
    }
    const s = stamps;
    let html = '<div>T1 Pico sends: <span class="t">' + clockString(s.t1) + '</span> (Pico clock)</div>';
    if (step >= 1) html += '<div>T2 server receives: <span class="t">' + clockString(s.t2) + '</span></div>';
    if (step >= 2) html += '<div>T3 server replies: <span class="t">' + clockString(s.t3) + '</span></div>';
    if (step >= 3) {
        html += '<div>T4 Pico receives: <span class="t">' + clockString(s.t4) + '</span> (Pico clock)</div>';
        const err = Math.abs(s.theta - s.trueOffset);
        html += '<div>Round trip = (T4&minus;T1)&minus;(T3&minus;T2) = <strong>' + s.delta.toFixed(0) + ' ms</strong></div>';
        html += '<div>Correction: <strong>+' + (s.theta / 1000).toFixed(3) + ' s</strong> (true: +' + (s.trueOffset / 1000).toFixed(3) +
            ' s, off by ' + err.toFixed(1) + ' ms)</div>';
        html += '<div>Error limit: &plusmn;' + (s.delta / 2 + serverErr).toFixed(1) + ' ms</div>';
    }
    box.innerHTML = html;
}

function showInfo(id) {
    const info = NODE_INFO[id];
    if (!info) return;
    document.getElementById('info').innerHTML = '<h4>' + info.title + '</h4>' + info.text +
        '<br><strong>Typical accuracy:</strong> ' + info.accuracy;
}

// Move the packet dot from one node to another over `ms` milliseconds
function animatePacket(fromId, toId, label, ms, done) {
    const p1 = network.getPositions([fromId])[fromId];
    const p2 = network.getPositions([toId])[toId];
    nodes.update({ id: 'pkt', hidden: false, label });
    animating = true;
    const start = performance.now();
    function frame(now) {
        const f = Math.min(1, (now - start) / ms);
        const e = f < 0.5 ? 2 * f * f : 1 - Math.pow(-2 * f + 2, 2) / 2;   // ease in-out
        network.moveNode('pkt', p1.x + (p2.x - p1.x) * e, p1.y + (p2.y - p1.y) * e);
        if (f < 1) requestAnimationFrame(frame);
        else { animating = false; if (done) done(); }
    }
    requestAnimationFrame(frame);
}

const BUTTON_LABELS = ['Send request', 'Next: server replies', 'Next: reply travels back', 'Send another request'];

function stepForward() {
    if (animating) return;
    const id = serverId();
    const btn = document.getElementById('step-btn');
    if (step === 0 || step === 3) {
        stamps = computeStamps();
        step = 1;
        animatePacket('pico', id, 'request (T1)', 900, () => renderStamps());
    } else if (step === 1) {
        step = 2;
        nodes.update({ id: 'pkt', label: 'reply (T2, T3)' });
    } else if (step === 2) {
        step = 3;
        animatePacket(id, 'pico', 'reply (T2, T3)', 900, () => { nodes.update({ id: 'pkt', hidden: true }); renderStamps(); });
    }
    btn.textContent = BUTTON_LABELS[step];
    renderStamps();
}

function resetExchange() {
    step = 0;
    stamps = null;
    nodes.update({ id: 'pkt', hidden: true });
    document.getElementById('step-btn').textContent = BUTTON_LABELS[0];
    renderStamps();
}

document.addEventListener('DOMContentLoaded', function () {
    const select = document.getElementById('server');
    ['s2a', 's2b', 's2c', 's2d', 's1a', 's1b'].forEach(id => {
        const opt = document.createElement('option');
        opt.value = id;
        opt.textContent = NODE_INFO[id].title.replace(': ', ' - ').replace('Stratum ', 'S');
        select.appendChild(opt);
    });
    select.value = 's2c';

    const free = !isInIframe();
    network = new vis.Network(document.getElementById('network'), { nodes, edges }, {
        layout: { improvedLayout: false },
        physics: { enabled: false },
        interaction: {
            dragNodes: false, dragView: free, zoomView: free,
            navigationButtons: window.innerWidth >= 640, selectConnectedEdges: false, hover: true
        },
        nodes: {
            shape: 'box', margin: 8, borderWidth: 2,
            font: { size: 16, face: 'Arial', multi: false },
            widthConstraint: { maximum: 160 }
        },
        edges: {
            arrows: { to: { enabled: true, scaleFactor: 0.8 } },
            color: { color: '#555' }, width: 2, smooth: false
        }
    });

    network.once('afterDrawing', () => network.fit({ animation: false }));
    window.addEventListener('resize', () => network.fit({ animation: false }));

    network.on('click', params => {
        const id = params.nodes.find(n => n !== 'pkt');
        if (id) showInfo(id);
    });

    select.addEventListener('change', () => {
        edges.update({ id: 'link', to: select.value });
        showInfo(select.value);
        resetExchange();
    });
    document.getElementById('delay').addEventListener('input', () => {
        document.getElementById('delay-value').textContent = delayMs();
        resetExchange();
    });
    document.getElementById('step-btn').addEventListener('click', stepForward);

    document.getElementById('info').innerHTML = '<h4>Click any box</h4>Click a server or the Pico to read its role and typical accuracy. ' +
        'Arrows show time flowing down from the reference clock.';
    renderStamps();
});
