// NTP Sync Flow - Mermaid flowchart with click callbacks
// CANVAS_HEIGHT: 690
// The steps of a WiFi time sync on a Pico W, with retry branches for WiFi and
// NTP failures. Every node has a Mermaid `click` directive that shows its code.
// The "WiFi fails" and "NTP fails" toggles light up the retry and fallback paths.

let wifiFails = false;
let ntpFails = false;
let renderCount = 0;

// Code shown when a node is clicked (matches the main-w.py program in Chapter 14)
const STEPS = {
    Start: { title: 'Start', text: 'The program starts when the Pico W powers up and runs main.py.',
        code: 'NAME = "main-w.py"\nVERSION = "1.0"\nprint("{} v{}".format(NAME, VERSION))' },
    Secrets: { title: 'Read secrets.py', text: 'The WiFi name and password live in a separate file that is never shared.',
        code: '# secrets.py holds:\n#   SSID = "MyNetwork"\n#   PASSWORD = "my-password"\nimport secrets' },
    Connect: { title: 'Connect to WiFi', text: 'Turn on the radio in station (client) mode and ask to join the network.',
        code: 'wlan = network.WLAN(network.STA_IF)\nwlan.active(True)\nwlan.connect(secrets.SSID, secrets.PASSWORD)' },
    WifiOK: { title: 'Connected before timeout?', text: 'Joining takes a few seconds. Wait in a loop, but give up after a timeout so the clock never hangs.',
        code: 'start = time.time()\nwhile not wlan.isconnected():\n    if time.time() - start > timeout:\n        return False      # gave up\n    time.sleep(0.5)\nreturn True' },
    WifiRetry: { title: 'WiFi retries left?', text: 'A busy router or a weak signal often works on the second try. Count attempts so you stop eventually.',
        code: 'for attempt in range(3):\n    if connect():\n        break\n    time.sleep(5)        # wait, then try again' },
    Settime: { title: 'ntptime.settime()', text: 'Ask an NTP server for the time and set the internal RTC to UTC.',
        code: 'import ntptime\nntptime.settime()        # RTC now holds UTC' },
    NtpOK: { title: 'NTP reply received?', text: 'If the server does not answer, settime() raises an OSError such as ETIMEDOUT. Catch it instead of crashing.',
        code: 'try:\n    ntptime.settime()\n    return True\nexcept OSError:\n    return False' },
    NtpRetry: { title: 'NTP retries left?', text: 'Try the server a few times with a short pause between attempts.',
        code: 'def sync():\n    for _ in range(3):\n        try:\n            ntptime.settime()\n            return True\n        except OSError:\n            time.sleep(2)\n    return False' },
    Keep: { title: 'Keep running on last known time', text: 'The RTC keeps counting from its last good time. A clock that keeps ticking is better than one that stops. Try again at the next sync.',
        code: 'if connect() and sync():\n    print("Synced")\nelse:\n    print("Sync failed; using existing time")' },
    Apply: { title: 'Apply time zone offset and DST', text: 'The RTC holds UTC. Convert to local time only when you display it.',
        code: 'utc = time.time()\noffset = STD_OFFSET + (1 if is_dst_us(utc, STD_OFFSET) else 0)\nlocal = time.localtime(utc + offset * 3600)' },
    Display: { title: 'Update display', text: 'Draw the local time on the clock face, once a second.',
        code: 'h, m, s = local_now()[3:6]\nprint(f"{h:02d}:{m:02d}:{s:02d}")   # or draw it' },
    Wait: { title: 'Wait N hours', text: 'Crystals drift, so sync again on a schedule. Every 6 to 24 hours is plenty, and polite to shared servers.',
        code: 'SYNC_HOURS = 12\nif time.time() - last_sync > SYNC_HOURS * 3600:\n    # go back to Connect to WiFi\n    last_sync = time.time()' }
};

// Edge order matters: linkStyle uses these indices
const EDGES = [
    'Start --> Secrets',                       // 0
    'Secrets --> Connect',                     // 1
    'Connect --> WifiOK',                      // 2
    'WifiOK -- yes --> Settime',               // 3
    'WifiOK -- no --> WifiRetry',              // 4
    'WifiRetry -- yes --> Connect',            // 5
    'WifiRetry -- no --> Keep',                // 6
    'Settime --> NtpOK',                       // 7
    'NtpOK -- yes --> Apply',                  // 8
    'NtpOK -- no --> NtpRetry',                // 9
    'NtpRetry -- yes --> Settime',             // 10
    'NtpRetry -- no --> Keep',                 // 11
    'Apply --> Display',                       // 12
    'Keep --> Display',                        // 13
    'Display --> Wait',                        // 14
    'Wait -- next sync --> Connect'            // 15
];

// Which edges and nodes are "lit" for each scenario
function scenario() {
    if (wifiFails) {
        return { edges: [0, 1, 2, 4, 5, 6, 13, 14, 15], nodes: ['WifiRetry', 'Keep'], fail: true,
            status: 'WiFi fails: the Pico retries the connection, then keeps running on its last known time and tries again at the next sync.' };
    }
    if (ntpFails) {
        return { edges: [0, 1, 2, 3, 7, 9, 10, 11, 13, 14, 15], nodes: ['NtpRetry', 'Keep'], fail: true,
            status: 'NTP fails: WiFi works, but the server does not answer. The Pico retries settime(), then carries on with the time it has.' };
    }
    return { edges: [0, 1, 2, 3, 7, 8, 12, 14, 15], nodes: [], fail: false,
        status: 'Everything works: connect, sync, convert to local time, display, and wait for the next sync.' };
}

function buildDiagram() {
    const sc = scenario();
    const lines = [
        'flowchart TD',
        '    Start([Start]):::start',
        '    Secrets[Read secrets.py]',
        '    Connect[Connect to WiFi]',
        '    WifiOK{{WiFi connected<br/>before timeout?}}',
        '    WifiRetry{{WiFi retries left?}}',
        '    Settime["ntptime.settime()"]',
        '    NtpOK{{NTP reply received?}}',
        '    NtpRetry{{NTP retries left?}}',
        '    Keep[Keep running on<br/>last known time]',
        '    Apply[Apply time zone<br/>offset and DST]',
        '    Display[Update display]',
        '    Wait[Wait N hours]'
    ];
    EDGES.forEach(e => lines.push('    ' + e));
    lines.push('    classDef default fill:#ffffff,stroke:#5b6b7f,stroke-width:2px,color:#111,font-size:15px');
    lines.push('    classDef start fill:#e6f4ea,stroke:#009e73,stroke-width:2px,color:#111');
    lines.push('    classDef failnode fill:#ffe0cc,stroke:#d55e00,stroke-width:3px,color:#111');
    if (sc.nodes.length) lines.push('    class ' + sc.nodes.join(',') + ' failnode');
    // Grey out every edge, then color the scenario's path
    lines.push('    linkStyle default stroke:#bbbbbb,stroke-width:2px');
    const color = sc.fail ? '#d55e00' : '#009e73';
    lines.push('    linkStyle ' + sc.edges.join(',') + ' stroke:' + color + ',stroke-width:4px');
    // Mermaid click directives: each node calls showStep with its id
    Object.keys(STEPS).forEach(id => lines.push('    click ' + id + ' call showStep("' + id + '")'));
    return lines.join('\n');
}

// Called by the Mermaid click directives (must be global)
window.showStep = function (id) {
    const s = STEPS[id];
    if (!s) return;
    const esc = t => t.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    document.getElementById('panel').innerHTML = '<h3>' + esc(s.title) + '</h3>' + esc(s.text) +
        '<pre>' + esc(s.code) + '</pre>';
};

async function render() {
    const sc = scenario();
    document.getElementById('status').textContent = sc.status;
    const el = document.getElementById('diagram');
    renderCount += 1;
    const { svg, bindFunctions } = await mermaid.render('ntpflow' + renderCount, buildDiagram());
    el.innerHTML = svg;
    if (bindFunctions) bindFunctions(el);
    // Hovering a node previews its code too (clicking keeps working through the click directives)
    el.querySelectorAll('.node').forEach(node => {
        const id = (node.id.match(/flowchart-(.+)-\d+$/) || [])[1];
        if (STEPS[id]) node.addEventListener('mouseenter', () => window.showStep(id));
    });
}

function setToggle(btn, on) {
    btn.classList.toggle('on', on);
    btn.setAttribute('aria-pressed', on ? 'true' : 'false');
}

document.addEventListener('DOMContentLoaded', function () {
    mermaid.initialize({
        startOnLoad: false,
        securityLevel: 'loose',      // required for click callbacks
        theme: 'default',
        flowchart: { useMaxWidth: true, htmlLabels: true, curve: 'basis', nodeSpacing: 24, rankSpacing: 28 }
    });
    const wifiBtn = document.getElementById('wifi-fail');
    const ntpBtn = document.getElementById('ntp-fail');
    wifiBtn.addEventListener('click', () => {
        wifiFails = !wifiFails;
        if (wifiFails) { ntpFails = false; setToggle(ntpBtn, false); }
        setToggle(wifiBtn, wifiFails);
        render();
    });
    ntpBtn.addEventListener('click', () => {
        ntpFails = !ntpFails;
        if (ntpFails) { wifiFails = false; setToggle(wifiBtn, false); }
        setToggle(ntpBtn, ntpFails);
        render();
    });
    render();
});
