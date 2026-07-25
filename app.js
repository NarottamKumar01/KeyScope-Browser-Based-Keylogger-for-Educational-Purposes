/**
 * Keyboard Event Demonstration - Core Application Engine
 */

// State Variables
let sessionActive = false;
let startTime = null;
let durationTimer = null;
let durationSeconds = 0;
let eventCount = 0;
let eventLog = [];
let keyFrequency = {};
let modifierStates = {
    Control: false,
    Shift: false,
    Alt: false,
    Meta: false
};
let keyPressHistory = []; // Timestamps of keys for KPS calculation
let kpsInterval = null;

// DOM Elements
const statusIndicator = document.getElementById("status-indicator");
const statusText = document.getElementById("status-text");
const startTimeEl = document.getElementById("start-time");
const durationEl = document.getElementById("duration");
const eventsCountEl = document.getElementById("events-count");
const kpsValueEl = document.getElementById("kps-value");

const btnStart = document.getElementById("btn-start");
const btnStop = document.getElementById("btn-stop");
const btnClear = document.getElementById("btn-clear");
const btnExportTxt = document.getElementById("btn-export-txt");
const btnExportJson = document.getElementById("btn-export-json");

const soundToggle = document.getElementById("sound-toggle");
const soundProfile = document.getElementById("sound-profile");

const goalFraction = document.getElementById("goal-fraction");
const goalTargetInput = document.getElementById("goal-target");
const goalProgressFill = document.getElementById("goal-progress-fill");
const goalPercentage = document.getElementById("goal-percentage");

const eventLogTerminal = document.getElementById("event-log-terminal");
const emptyChartMsg = document.getElementById("empty-chart-msg");
const barChartList = document.getElementById("bar-chart-list");
const themeToggle = document.getElementById("theme-toggle");

const modCtrl = document.getElementById("mod-ctrl");
const modShift = document.getElementById("mod-shift");
const modAlt = document.getElementById("mod-alt");
const modMeta = document.getElementById("mod-meta");

// Web Audio API Context
let audioCtx = null;

function initAudio() {
    if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (audioCtx.state === 'suspended') {
        audioCtx.resume();
    }
}

/**
 * Web Audio Switch Synthesizer
 */
function playSwitchSound(switchType) {
    if (!soundToggle.checked) return;
    
    try {
        initAudio();
        
        const now = audioCtx.currentTime;
        
        switch (switchType) {
            case "cherry-blue": // Tactile & Clicky
                playClickySound(now, 1.0, 1500, 0.005, 180, 0.04);
                break;
            case "cherry-brown": // Tactile & Quiet
                playClickySound(now, 0.6, 900, 0.008, 140, 0.055);
                break;
            case "cherry-red": // Linear & Smooth
                playLinearSound(now, 0.5, 120, 0.045);
                break;
            case "typewriter": // Retro Typewriter
                playTypewriterSound(now);
                break;
            case "bubble-wrap": // Bubble Wrap Pop
                playBubblePopSound(now);
                break;
        }
    } catch (e) {
        console.error("Audio error:", e);
    }
}

// Synthesize a tactile switch sound (Click + Clack)
function playClickySound(time, clickVol, clickFreq, clickDecay, clackFreq, clackDecay) {
    // 1. High frequency click (switch contact)
    const clickOsc = audioCtx.createOscillator();
    const clickGain = audioCtx.createGain();
    
    clickOsc.type = 'triangle';
    clickOsc.frequency.setValueAtTime(clickFreq, time);
    clickOsc.frequency.exponentialRampToValueAtTime(clickFreq * 0.5, time + clickDecay);
    
    clickGain.gain.setValueAtTime(clickVol * 0.15, time);
    clickGain.gain.exponentialRampToValueAtTime(0.0001, time + clickDecay);
    
    clickOsc.connect(clickGain);
    clickGain.connect(audioCtx.destination);
    clickOsc.start(time);
    clickOsc.stop(time + clickDecay);
    
    // 2. Low frequency clack (bottom out)
    const clackOsc = audioCtx.createOscillator();
    const clackGain = audioCtx.createGain();
    
    clackOsc.type = 'sine';
    clackOsc.frequency.setValueAtTime(clackFreq, time + 0.002);
    clackOsc.frequency.exponentialRampToValueAtTime(clackFreq * 0.6, time + clackDecay);
    
    clackGain.gain.setValueAtTime(clickVol * 0.25, time + 0.002);
    clackGain.gain.exponentialRampToValueAtTime(0.0001, time + clackDecay);
    
    // Add simple filter to make it softer
    const filter = audioCtx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.setValueAtTime(800, time);
    
    clackOsc.connect(filter);
    filter.connect(clackGain);
    clackGain.connect(audioCtx.destination);
    
    clackOsc.start(time + 0.002);
    clackOsc.stop(time + clackDecay);
}

// Synthesize linear bottom-out sound (No sharp click)
function playLinearSound(time, vol, clackFreq, clackDecay) {
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    const filter = audioCtx.createBiquadFilter();
    
    osc.type = 'triangle';
    osc.frequency.setValueAtTime(clackFreq, time);
    osc.frequency.exponentialRampToValueAtTime(clackFreq * 0.7, time + clackDecay);
    
    gain.gain.setValueAtTime(vol * 0.35, time);
    gain.gain.exponentialRampToValueAtTime(0.0001, time + clackDecay);
    
    filter.type = 'lowpass';
    filter.frequency.setValueAtTime(500, time);
    
    osc.connect(filter);
    filter.connect(gain);
    gain.connect(audioCtx.destination);
    
    osc.start(time);
    osc.stop(time + clackDecay);
}

// Synthesize retro typewriter mechanical key sound
function playTypewriterSound(time) {
    // 1. High click sound
    const clickOsc = audioCtx.createOscillator();
    const clickGain = audioCtx.createGain();
    clickOsc.type = 'sine';
    clickOsc.frequency.setValueAtTime(2500, time);
    clickOsc.frequency.exponentialRampToValueAtTime(800, time + 0.015);
    
    clickGain.gain.setValueAtTime(0.2, time);
    clickGain.gain.exponentialRampToValueAtTime(0.0001, time + 0.015);
    
    clickOsc.connect(clickGain);
    clickGain.connect(audioCtx.destination);
    clickOsc.start(time);
    clickOsc.stop(time + 0.015);

    // 2. Metallic resonant ring
    const ringOsc = audioCtx.createOscillator();
    const ringGain = audioCtx.createGain();
    const filter = audioCtx.createBiquadFilter();
    
    ringOsc.type = 'triangle';
    ringOsc.frequency.setValueAtTime(650, time);
    
    ringGain.gain.setValueAtTime(0.12, time + 0.005);
    ringGain.gain.exponentialRampToValueAtTime(0.0001, time + 0.12);
    
    filter.type = 'bandpass';
    filter.frequency.setValueAtTime(700, time);
    filter.Q.setValueAtTime(5, time);
    
    ringOsc.connect(filter);
    filter.connect(ringGain);
    ringGain.connect(audioCtx.destination);
    
    ringOsc.start(time + 0.005);
    ringOsc.stop(time + 0.12);
}

// Synthesize bubble wrap pop
function playBubblePopSound(time) {
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    
    osc.type = 'sine';
    // Fast frequency sweep up
    osc.frequency.setValueAtTime(500, time);
    osc.frequency.exponentialRampToValueAtTime(1300, time + 0.015);
    
    gain.gain.setValueAtTime(0.25, time);
    gain.gain.exponentialRampToValueAtTime(0.0001, time + 0.025);
    
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start(time);
    osc.stop(time + 0.025);
}


/**
 * Helper: Resolve API endpoint URL (supports VS Code Live Server, direct file, or Python server)
 */
function getApiUrl(endpoint) {
    if (window.location.protocol.startsWith("http") && (window.location.port === "8000" || window.location.port === "8001")) {
        return endpoint;
    }
    return `http://localhost:8000${endpoint}`;
}

/**
 * Helper: Get current formatted time
 */
function getFormattedTime() {
    const now = new Date();
    return now.toTimeString().split(' ')[0];
}

/**
 * Helper: Format seconds to HH:MM:SS
 */
function formatDuration(s) {
    const hrs = Math.floor(s / 3600).toString().padStart(2, '0');
    const mins = Math.floor((s % 3600) / 60).toString().padStart(2, '0');
    const secs = (s % 60).toString().padStart(2, '0');
    return `${hrs}:${mins}:${secs}`;
}

/**
 * Log event to standard scrollable log terminal
 */
function logToTerminal(message, className = "") {
    const line = document.createElement("div");
    line.className = `terminal-line ${className}`;
    line.textContent = `[${getFormattedTime()}] ${message}`;
    eventLogTerminal.appendChild(line);
    
    // Maintain maximum length
    while (eventLogTerminal.children.length > 120) {
        eventLogTerminal.removeChild(eventLogTerminal.firstChild);
    }
    
    // Auto-scroll
    eventLogTerminal.scrollTop = eventLogTerminal.scrollHeight;
}

/**
 * Start event capturing session
 */
function startSession() {
    if (sessionActive) return;
    
    sessionActive = true;
    startTime = new Date();
    startTimeEl.textContent = startTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    
    statusIndicator.className = "status-indicator running";
    statusText.textContent = "Running";
    statusText.className = "stat-value text-glow text-accent";
    
    btnStart.disabled = true;
    btnStop.disabled = false;
    
    logToTerminal("Session recording started. Ready to capture keys.", "system-msg");
    
    // Start duration counter
    durationTimer = setInterval(() => {
        durationSeconds++;
        durationEl.textContent = formatDuration(durationSeconds);
    }, 1000);
    
    // Start rolling Keys Per Second calculator
    kpsInterval = setInterval(updateKps, 200);
    
    // Resume sound context if closed
    initAudio();
}

/**
 * Stop/Pause session
 */
function stopSession() {
    if (!sessionActive) return;
    
    sessionActive = false;
    clearInterval(durationTimer);
    clearInterval(kpsInterval);
    
    statusIndicator.className = "status-indicator stopped";
    statusText.textContent = "Stopped";
    statusText.className = "stat-value text-glow";
    
    btnStart.disabled = false;
    btnStop.disabled = true;
    
    logToTerminal("Session recording stopped.", "system-msg");
    
    // Reset live KPS display to 0
    kpsValueEl.textContent = "0.0";
}

/**
 * Clear session stats and logs
 */
function clearSession() {
    stopSession();
    
    startTime = null;
    durationSeconds = 0;
    eventCount = 0;
    eventLog = [];
    keyFrequency = {};
    keyPressHistory = [];
    
    // Clear modifier key variables
    for (let key in modifierStates) {
        modifierStates[key] = false;
    }
    updateModifierPills();
    
    // Reset virtual keys
    document.querySelectorAll(".key").forEach(k => k.classList.remove("active"));
    
    // Reset UI fields
    startTimeEl.textContent = "--:--:--";
    durationEl.textContent = "00:00:00";
    eventsCountEl.textContent = "0";
    kpsValueEl.textContent = "0.0";
    
    statusIndicator.className = "status-indicator ready";
    statusText.textContent = "Ready";
    statusText.className = "stat-value text-glow";
    
    // Reset Progress Goal
    updateGoalProgress();
    
    // Clear terminal
    eventLogTerminal.innerHTML = "";
    logToTerminal("Dashboard cleared and ready. Click 'Start Session' and type.", "system-msg");
    
    // Clear frequency chart
    updateFrequencyChart();
}

/**
 * Live Keys-Per-Second calculator (rolling 1-second window)
 */
function updateKps() {
    const now = Date.now();
    // Filter keypresses older than 1 second (1000ms)
    keyPressHistory = keyPressHistory.filter(t => now - t < 1000);
    const kps = keyPressHistory.length;
    kpsValueEl.textContent = kps.toFixed(1);
}

/**
 * Update the modifier pills visual highlight
 */
function updateModifierPills() {
    if (modifierStates.Control) modCtrl.classList.add("active");
    else modCtrl.classList.remove("active");
    
    if (modifierStates.Shift) modShift.classList.add("active");
    else modShift.classList.remove("active");
    
    if (modifierStates.Alt) modAlt.classList.add("active");
    else modAlt.classList.remove("active");
    
    if (modifierStates.Meta) modMeta.classList.add("active");
    else modMeta.classList.remove("active");
}

/**
 * Update Key Frequency analytics chart
 */
function updateFrequencyChart() {
    // Sort keys by frequency
    const sortedKeys = Object.entries(keyFrequency)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5); // Show top 5 keys
        
    if (sortedKeys.length === 0) {
        emptyChartMsg.style.display = "block";
        barChartList.style.display = "none";
        return;
    }
    
    emptyChartMsg.style.display = "none";
    barChartList.style.display = "flex";
    barChartList.innerHTML = "";
    
    const maxVal = sortedKeys[0][1];
    
    sortedKeys.forEach(([key, count]) => {
        const percentage = maxVal > 0 ? (count / maxVal) * 100 : 0;
        
        const row = document.createElement("div");
        row.className = "bar-chart-row";
        row.innerHTML = `
            <span class="bar-key-label" title="${key}">${key}</span>
            <div class="bar-container">
                <div class="bar-fill" style="width: ${percentage}%"></div>
            </div>
            <span class="bar-count-label">${count}</span>
        `;
        barChartList.appendChild(row);
    });
}

/**
 * Update Keyboard Goal Progress fill
 */
function updateGoalProgress() {
    const target = parseInt(goalTargetInput.value) || 200;
    goalFraction.textContent = `${eventCount} / ${target}`;
    
    let percent = target > 0 ? (eventCount / target) * 100 : 0;
    percent = Math.min(Math.round(percent), 100);
    
    goalProgressFill.style.width = `${percent}%`;
    goalPercentage.textContent = `${percent}% Completed`;
    
    // Sparkle pulse when goal reached!
    if (percent >= 100) {
        goalProgressFill.style.animation = "flash 1.0s infinite alternate";
    } else {
        goalProgressFill.style.animation = "none";
    }
}

/**
 * Key Event Handler (keydown / keyup)
 */
function handleKeyEvent(e, type) {
    // Auto-start session on first keypress if inactive
    if (!sessionActive && type === "keydown") {
        startSession();
    }
    if (!sessionActive) return;
    
    // Manage modifier keys state
    modifierStates.Control = e.ctrlKey;
    modifierStates.Shift = e.shiftKey;
    modifierStates.Alt = e.altKey;
    modifierStates.Meta = e.metaKey;
    updateModifierPills();
    
    const code = e.code;
    const keyName = e.key;
    
    // Highlight the virtual key
    // We try to find the key by its exact code
    const vKey = document.querySelector(`.key[data-code="${code}"]`);
    
    if (type === "keydown") {
        if (vKey) {
            // Prevent class piling
            if (!vKey.classList.contains("active")) {
                vKey.classList.add("active");
                // Play sound
                playSwitchSound(soundProfile.value);
            }
        }
        
        // Prevent default actions for standard navigation/webpage hotkeys during active recording
        // (like spacebar scrolling down, tab indexing, or slash quick search)
        if (["Space", "Tab", "Slash", "ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(code)) {
            e.preventDefault();
        }
        
        // Count events only on keydown, avoiding holding-repeat spamming
        if (!e.repeat) {
            eventCount++;
            eventsCountEl.textContent = eventCount;
            
            // Add to KPS history
            keyPressHistory.push(Date.now());
            updateKps();
            
            // Goal progress update
            updateGoalProgress();
            
            // Heatmap calculation
            const displayKeyLabel = keyName === " " ? "Space" : keyName;
            keyFrequency[displayKeyLabel] = (keyFrequency[displayKeyLabel] || 0) + 1;
            updateFrequencyChart();
            
            // Log details
            const modStr = [];
            if (e.ctrlKey) modStr.push("Ctrl");
            if (e.shiftKey) modStr.push("Shift");
            if (e.altKey) modStr.push("Alt");
            if (e.metaKey) modStr.push("Meta");
            const modifierSummary = modStr.length > 0 ? modStr.join("+") : "None";
            
            const logEntry = {
                timestamp: getFormattedTime(),
                rawTimestamp: new Date().toISOString(),
                type: "keydown",
                key: keyName,
                code: code,
                modifiers: modifierSummary
            };
            eventLog.push(logEntry);
            
            logToTerminal(`keydown: "${keyName}" | code: ${code} | mods: ${modifierSummary}`, "event-keydown");
        }
        
    } else if (type === "keyup") {
        if (vKey) {
            vKey.classList.remove("active");
        }
        
        // Log keyup event
        const logEntry = {
            timestamp: getFormattedTime(),
            rawTimestamp: new Date().toISOString(),
            type: "keyup",
            key: keyName,
            code: code
        };
        eventLog.push(logEntry);
    }
}

/**
 * Export Logs (TXT or JSON)
 */
function downloadFile(content, mimeType, filename) {
    const a = document.createElement("a");
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function exportAsTxt() {
    if (eventLog.length === 0) {
        alert("Event log is empty. Please capture some keystrokes first.");
        return;
    }
    
    let txt = `======================================================\n`;
    txt += `       KEYBOARD EVENT DEMONSTRATION LOG SESSION       \n`;
    txt += `======================================================\n`;
    txt += `Start Time : ${startTime ? startTime.toLocaleString() : "Unknown"}\n`;
    txt += `Duration   : ${formatDuration(durationSeconds)}\n`;
    txt += `Total Keys : ${eventCount} keystrokes\n`;
    txt += `------------------------------------------------------\n\n`;
    
    eventLog.forEach(evt => {
        if (evt.type === "keydown") {
            txt += `[${evt.timestamp}] KEYDOWN - Key: "${evt.key}" | Code: ${evt.code} | Modifiers: ${evt.modifiers}\n`;
        } else {
            txt += `[${evt.timestamp}] KEYUP   - Key: "${evt.key}" | Code: ${evt.code}\n`;
        }
    });
    
    const filename = `keyboard_log_${new Date().toISOString().slice(0, 10)}.txt`;
    downloadFile(txt, "text/plain;charset=utf-8", filename);
}

function exportAsJson() {
    if (eventLog.length === 0) {
        alert("Event log is empty. Please capture some keystrokes first.");
        return;
    }
    
    const sessionData = {
        sessionMeta: {
            app: "Keyboard Event Demonstration",
            startTime: startTime ? startTime.toISOString() : null,
            endTime: new Date().toISOString(),
            durationSeconds: durationSeconds,
            totalKeystrokes: eventCount,
            keyFrequency: keyFrequency
        },
        logs: eventLog
    };
    
    const jsonStr = JSON.stringify(sessionData, null, 2);
    const filename = `keyboard_log_${new Date().toISOString().slice(0, 10)}.json`;
    downloadFile(jsonStr, "application/json;charset=utf-8", filename);
}

// Attach Event Listeners
window.addEventListener("keydown", (e) => handleKeyEvent(e, "keydown"));
window.addEventListener("keyup", (e) => handleKeyEvent(e, "keyup"));

btnStart.addEventListener("click", startSession);
btnStop.addEventListener("click", stopSession);
btnClear.addEventListener("click", clearSession);
btnExportTxt.addEventListener("click", exportAsTxt);
btnExportJson.addEventListener("click", exportAsJson);

goalTargetInput.addEventListener("change", updateGoalProgress);
goalTargetInput.addEventListener("keyup", updateGoalProgress);

// Toggle Theme (Dark / Light)
themeToggle.addEventListener("click", () => {
    const currentTheme = document.documentElement.getAttribute("data-theme");
    const newTheme = currentTheme === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", newTheme);
    themeToggle.innerHTML = newTheme === "dark" ? "<span>🌙</span>" : "<span>☀️</span>";
    
    logToTerminal(`Theme switched to ${newTheme} mode.`, "system-msg");
});

// Click on virtual keys in UI triggers a sound feedback if active
document.querySelectorAll(".key").forEach(keyBtn => {
    keyBtn.addEventListener("mousedown", () => {
        if (!sessionActive) return;
        const code = keyBtn.getAttribute("data-code");
        
        // Dispatch synthetic event for keydown
        // Web audio context needs activation
        playSwitchSound(soundProfile.value);
        
        keyBtn.classList.add("active");
    });
    
    keyBtn.addEventListener("mouseup", () => {
        keyBtn.classList.remove("active");
    });
    
    keyBtn.addEventListener("mouseleave", () => {
        keyBtn.classList.remove("active");
    });
});

/**
 * =========================================================================
 * NEW FUNCTIONALITY: Tabs, Keylogger Sandbox & Detector Controls
 * =========================================================================
 */

// Tab Routing Controller
const navButtons = document.querySelectorAll(".nav-btn");
const tabContents = document.querySelectorAll(".tab-content");

navButtons.forEach(btn => {
    btn.addEventListener("click", () => {
        const targetTabId = btn.getAttribute("data-target");
        
        // Update active nav button
        navButtons.forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        
        // Update active content layout
        tabContents.forEach(content => {
            if (content.id === targetTabId) {
                content.classList.add("active");
            } else {
                content.classList.remove("active");
            }
        });
        
        // If switching to detector tab, run a quick status ping or log
        if (targetTabId === "tab-detector") {
            logScanConsole("Ready to perform system diagnostic auditing.");
        }
    });
});

// Keylogger Sandbox Interactions
let sandboxActive = false;
let sandboxSelectedMethod = "hook";
let sandboxPollInterval = null;
let sandboxLoggedCount = 0;

const simOptions = document.querySelectorAll(".sim-option");
const btnStartSandbox = document.getElementById("btn-start-sandbox");
const btnStopSandbox = document.getElementById("btn-stop-sandbox");
const btnClearSandbox = document.getElementById("btn-clear-sandbox");
const sandboxConsole = document.getElementById("sandbox-console-output");
const sandboxStatusDot = document.getElementById("sandbox-status-dot");
const sandboxStatusText = document.getElementById("sandbox-status-text");
const sandboxInterceptBadge = document.getElementById("sandbox-intercept-badge");

// Handle selecting method
simOptions.forEach(opt => {
    opt.addEventListener("click", () => {
        if (sandboxActive) return; // Prevent changing during active simulator
        simOptions.forEach(o => o.classList.remove("active"));
        opt.classList.add("active");
        sandboxSelectedMethod = opt.getAttribute("data-method");
    });
});

function logSandboxConsole(msg, className = "") {
    const line = document.createElement("div");
    line.className = `console-line ${className}`;
    line.textContent = `[${getFormattedTime()}] ${msg}`;
    sandboxConsole.appendChild(line);
    sandboxConsole.scrollTop = sandboxConsole.scrollHeight;
}

btnStartSandbox.addEventListener("click", async () => {
    if (sandboxActive) return;
    
    logSandboxConsole(`Launching Keylogger Simulator [Method: ${sandboxSelectedMethod}]...`, "system-msg");
    
    try {
        const res = await fetch(getApiUrl(`/api/logger/start?method=${sandboxSelectedMethod}`));
        const data = await res.json();
        
        if (data.status === "success") {
            sandboxActive = true;
            btnStartSandbox.disabled = true;
            btnStopSandbox.disabled = false;
            
            sandboxStatusDot.className = "status-dot online";
            sandboxStatusText.textContent = `Simulator Status: Online (${sandboxSelectedMethod.toUpperCase()})`;
            
            logSandboxConsole("Simulator successfully running! Keystrokes are now intercepted globally.", "system-msg");
            logSandboxConsole("Open Notepad or any editor and start typing.", "system-msg");
            
            // Poll for keystroke events from backend
            sandboxLoggedCount = 0;
            sandboxInterceptBadge.textContent = "Buffer empty";
            sandboxPollInterval = setInterval(pollSandboxEvents, 400);
        } else {
            logSandboxConsole(`Failed to start simulator: ${data.message}`, "console-line");
        }
    } catch (e) {
        logSandboxConsole(`⚠️ Python Security Server is offline. Please run 'python app.py' in your VS Code terminal to enable Win32 simulation.`, "console-line");
    }
});

btnStopSandbox.addEventListener("click", async () => {
    if (!sandboxActive) return;
    
    logSandboxConsole("Stopping simulator...", "system-msg");
    clearInterval(sandboxPollInterval);
    
    try {
        const res = await fetch(getApiUrl("/api/logger/stop"));
        const data = await res.json();
        
        if (data.status === "success") {
            sandboxActive = false;
            btnStartSandbox.disabled = false;
            btnStopSandbox.disabled = true;
            
            sandboxStatusDot.className = "status-dot offline";
            sandboxStatusText.textContent = "Simulator Status: Offline";
            
            logSandboxConsole("Simulator halted and cleaned up.", "system-msg");
        }
    } catch (e) {
        logSandboxConsole(`Connection error: ${e.message}`, "console-line");
    }
});

btnClearSandbox.addEventListener("click", () => {
    sandboxConsole.innerHTML = "";
    sandboxLoggedCount = 0;
    sandboxInterceptBadge.textContent = "Buffer empty";
    logSandboxConsole("Intercept log cleared.", "system-msg");
});

async function pollSandboxEvents() {
    try {
        const res = await fetch(getApiUrl("/api/logger/events"));
        const data = await res.json();
        
        if (data.events && data.events.length > 0) {
            data.events.forEach(evt => {
                sandboxLoggedCount++;
                let keyStr = evt.key;
                if (keyStr === "\n[ENTER]\n") keyStr = "[ENTER]";
                
                logSandboxConsole(`Intercepted Key: "${keyStr}" | Virtual Code: 0x${evt.code.toString(16).toUpperCase()}`, "intercept-msg");
            });
            sandboxInterceptBadge.textContent = `${sandboxLoggedCount} keys intercepted`;
        }
    } catch (e) {
        console.error("Polling error:", e);
    }
}

// Security Detection Suite Interactions
const btnRunScan = document.getElementById("btn-run-scan");
const scanConsole = document.getElementById("scan-console-log");
const healthStatus = document.getElementById("health-status");
const rawSinkCount = document.getElementById("raw-sink-count");
const flaggedCount = document.getElementById("flagged-count");
const processTableBody = document.getElementById("process-table-body");
const threatGaugePct = document.getElementById("threat-gauge-pct");
const gaugeFillCircle = document.getElementById("gauge-fill-circle");

function logScanConsole(msg, className = "") {
    const line = document.createElement("div");
    line.className = `console-line ${className}`;
    line.textContent = `[${getFormattedTime()}] ${msg}`;
    scanConsole.appendChild(line);
    scanConsole.scrollTop = scanConsole.scrollHeight;
}

btnRunScan.addEventListener("click", async () => {
    btnRunScan.disabled = true;
    scanConsole.innerHTML = "";
    logScanConsole("Initializing heuristic scan parameters...", "system-msg");
    
    // Set loading visual states
    updateThreatGauge(0);
    healthStatus.textContent = "Scanning...";
    healthStatus.className = "summary-value";
    
    try {
        const res = await fetch(getApiUrl("/api/detector/scan"));
        const report = await res.json();
        
        // Print logs incrementally with tiny delays to look cool & premium
        let i = 0;
        function printNextLog() {
            if (i < report.logs.length) {
                logScanConsole(report.logs[i], "system-msg");
                i++;
                setTimeout(printNextLog, 120);
            } else {
                finalizeScan(report);
            }
        }
        printNextLog();
        
    } catch (e) {
        logScanConsole(`⚠️ Python Security Server is offline. Please run 'python app.py' in your VS Code terminal to enable system diagnostics.`, "console-line");
        btnRunScan.disabled = false;
        healthStatus.textContent = "Offline";
        healthStatus.className = "summary-value health-warning";
    }
});

function finalizeScan(report) {
    btnRunScan.disabled = false;
    
    // Update summary labels
    rawSinkCount.textContent = report.raw_input_sinks;
    flaggedCount.textContent = report.reports.length;
    
    healthStatus.textContent = report.status;
    if (report.status === "Secure") {
        healthStatus.className = "summary-value health-secure";
    } else if (report.status === "Warning") {
        healthStatus.className = "summary-value health-warning";
    } else {
        healthStatus.className = "summary-value health-critical";
    }
    
    // Animate risk meter
    updateThreatGauge(report.threat_level);
    
    // Render suspicious process table
    processTableBody.innerHTML = "";
    
    if (report.reports.length === 0) {
        processTableBody.innerHTML = `
            <tr>
                <td colspan="4" class="empty-table-msg">Scan complete. No suspicious keylogging vectors detected in active memory namespaces.</td>
            </tr>
        `;
    } else {
        report.reports.forEach(p => {
            const tr = document.createElement("tr");
            
            // Get threat color class
            let pillClass = "threat-index-low";
            if (p.threat_score >= 70) pillClass = "threat-index-high";
            else if (p.threat_score >= 35) pillClass = "threat-index-med";
            
            // Render list of detection reasons
            let reasonsHtml = `<ul class="reasons-list">`;
            p.reasons.forEach(r => {
                reasonsHtml += `<li>${r}</li>`;
            });
            reasonsHtml += `</ul>`;
            
            tr.innerHTML = `
                <td style="font-weight:700;">${p.name}</td>
                <td style="font-family:'JetBrains Mono', monospace; color:var(--text-secondary);">${p.pid}</td>
                <td>
                    <span class="threat-index-pill ${pillClass}">${p.threat_score}%</span>
                </td>
                <td>${reasonsHtml}</td>
            `;
            processTableBody.appendChild(tr);
        });
    }
    logScanConsole(`Scan complete. Audit threat index settled at ${report.threat_level}%.`, "system-msg");
}

function updateThreatGauge(score) {
    threatGaugePct.textContent = `${score}%`;
    
    // Circle circumference = 2 * PI * R = 2 * 3.14159 * 50 = 314.16
    const circumference = 314.16;
    const offset = circumference - (score / 100) * circumference;
    gaugeFillCircle.style.strokeDashoffset = offset;
    
    // Update stroke color dynamically
    if (score >= 70) {
        gaugeFillCircle.style.stroke = "var(--accent-danger)";
    } else if (score >= 35) {
        gaugeFillCircle.style.stroke = "var(--accent-warning)";
    } else {
        gaugeFillCircle.style.stroke = "var(--accent-success)";
    }
}

