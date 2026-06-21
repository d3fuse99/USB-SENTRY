const API_HISTORY = '/api/usb-history';
const API_ADD = '/api/whitelist/add';
const API_REMOVE = '/api/whitelist/remove';
const API_LOGS = '/api/logs';
const API_AUTH_STATUS = '/api/auth/status';
const API_AUTH_SETUP = '/api/auth/setup';
const API_AUTH_UNLOCK = '/api/auth/unlock';
const API_AUTH_LOCK = '/api/auth/lock';

const btnRescan = document.getElementById('btn-rescan');
const timelineList = document.getElementById('timeline-list');
const metricTotal = document.getElementById('metric-total');
const metricWhitelisted = document.getElementById('metric-whitelisted');
const metricThreats = document.getElementById('metric-threats');
const cardThreats = document.getElementById('card-threats');
const chronicleCount = document.getElementById('chronicle-count');
const btnLockControl = document.getElementById('btn-lock-control');
const lockText = document.getElementById('lock-text');
const authModal = document.getElementById('auth-modal');
const modalTitle = document.getElementById('modal-title');
const authPasswordInput = document.getElementById('auth-password');
const setupMessage = document.getElementById('setup-message');
const unlockMessage = document.getElementById('unlock-message');
const unlockDurationGroup = document.getElementById('unlock-duration-group');
const unlockDurationSelect = document.getElementById('unlock-duration');
const logConsole = document.getElementById('log-console');
const warningsDiv = document.getElementById('password-warnings');

let previouslySeenSerials = null;
let isSystemUnlocked = false;
let isAuthSetupMode = false;
let secondsLeft = 0;
let timerInterval = null;

const toastContainer = document.createElement('div');
toastContainer.className = 'toast-container';
document.body.appendChild(toastContainer);

function showToast(name, serial) {
    const toast = document.createElement('div');
    toast.className = 'toast-alert';
    
    const title = document.createElement('strong');
    title.style.color = 'var(--accent-threat)';
    title.textContent = '⚠ BREACH DETECTED!';
    
    const text = document.createElement('span');
    text.textContent = 'Unauthorized device connected: ' + name;
    
    const subtext = document.createElement('small');
    subtext.style.color = 'var(--text-muted)';
    subtext.textContent = 'Serial: ' + serial;
    
    toast.appendChild(title);
    toast.appendChild(text);
    toast.appendChild(subtext);
    
    toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.style.transition = 'opacity 0.5s';
        toast.style.opacity = '0';
        setTimeout(() => { toast.remove(); }, 500);
    }, 5000);
}

async function fetchUsbData() {
    const svgIcon = btnRescan.querySelector('svg');
    svgIcon.style.transform = 'rotate(360deg)';
    setTimeout(() => { svgIcon.style.transform = 'rotate(0deg)'; }, 400);

    try {
        const response = await fetch(API_HISTORY);
        if (!response.ok) {
            throw new Error('API Response Error');
        }
        const devices = await response.json();
        renderTimeline(devices);
        await updateAuthStatus();
        await fetchLogs();
    } catch (error) {
        console.error(error);
        timelineList.textContent = '';
        const emptyDiv = document.createElement('div');
        emptyDiv.className = 'empty-state';
        
        const titleDiv = document.createElement('div');
        titleDiv.style.color = 'var(--accent-threat)';
        titleDiv.style.fontWeight = 'bold';
        titleDiv.style.fontSize = '16px';
        titleDiv.textContent = 'ENDPOINT INTERACTION ERROR';
        
        const descDiv = document.createElement('div');
        descDiv.textContent = 'Could not capture data from local port 9090. Verify server.py is running.';
        
        emptyDiv.appendChild(titleDiv);
        emptyDiv.appendChild(descDiv);
        timelineList.appendChild(emptyDiv);
    }
}

async function updateAuthStatus() {
    try {
        const response = await fetch(API_AUTH_STATUS);
        if (response.ok) {
            const data = await response.json();
            isSystemUnlocked = data.is_unlocked;
            secondsLeft = data.seconds_left;
            
            if (!data.is_configured) {
                isAuthSetupMode = true;
                openAuthModal();
            }
            
            updateLockUI();
        }
    } catch (error) {
        console.error(error);
    }
}

function updateLockUI() {
    if (isSystemUnlocked) {
        btnLockControl.className = 'btn btn-whitelist';
        
        const minutes = Math.floor(secondsLeft / 60);
        const seconds = secondsLeft % 60;
        const timeStr = (minutes < 10 ? '0' : '') + minutes + ':' + (seconds < 10 ? '0' : '') + seconds;
        
        lockText.textContent = 'UNLOCKED (' + timeStr + ')';
        
        btnLockControl.querySelector('svg').innerHTML = `
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
            <path d="M7 11V7a5 5 0 0 1 9.9-1"/>
        `;
    } else {
        btnLockControl.className = 'btn btn-remove';
        lockText.textContent = 'PORTS ARMED';
        
        btnLockControl.querySelector('svg').innerHTML = `
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
        `;
    }
}

function toggleLockState() {
    if (isSystemUnlocked) {
        lockSystemEarly();
    } else {
        openAuthModal();
    }
}

async function lockSystemEarly() {
    try {
        const response = await fetch(API_AUTH_LOCK, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        if (response.ok) {
            await fetchUsbData();
        }
    } catch (error) {
        console.error(error);
    }
}

async function fetchLogs() {
    try {
        const response = await fetch(API_LOGS);
        if (response.ok) {
            const logs = await response.json();
            renderLogs(logs);
        }
    } catch (error) {
        console.error(error);
    }
}

function renderLogs(logs) {
    logConsole.textContent = '';
    
    if (logs.length === 0) {
        const noLogs = document.createElement('div');
        noLogs.style.color = 'var(--text-muted)';
        noLogs.textContent = 'System log is empty. Standing by.';
        logConsole.appendChild(noLogs);
        return;
    }
    
    const sortedLogs = [...logs].reverse();
    sortedLogs.forEach(entry => {
        const entryDiv = document.createElement('div');
        entryDiv.className = 'log-entry';
        
        const timeSpan = document.createElement('span');
        timeSpan.className = 'log-time';
        timeSpan.textContent = '[' + entry.timestamp + ']';
        
        const textSpan = document.createElement('span');
        textSpan.className = 'log-text';
        textSpan.textContent = entry.message;
        
        entryDiv.appendChild(timeSpan);
        entryDiv.appendChild(textSpan);
        logConsole.appendChild(entryDiv);
    });
}

function openAuthModal() {
    if (authModal.style.display === 'flex') {
        return;
    }
    authModal.style.display = 'flex';
    authPasswordInput.value = '';
    authPasswordInput.type = 'password';
    document.getElementById('eye-icon').innerHTML = `<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>`;
    authPasswordInput.focus();
    checkKeyboardLayout(null);
    
    if (isAuthSetupMode) {
        modalTitle.textContent = 'INITIAL SECURITY SETUP';
        setupMessage.style.display = 'block';
        unlockMessage.style.display = 'none';
        unlockDurationGroup.style.display = 'none';
    } else {
        modalTitle.textContent = 'AUTHORIZE SYSTEM UNLOCK';
        setupMessage.style.display = 'none';
        unlockMessage.style.display = 'block';
        unlockDurationGroup.style.display = 'block';
    }
}

function closeAuthModal() {
    if (isAuthSetupMode) {
        alert('Initial security setup is mandatory. Please set a Master Password.');
        return;
    }
    authModal.style.display = 'none';
}

function togglePasswordVisibility() {
    const type = authPasswordInput.type === 'password' ? 'text' : 'password';
    authPasswordInput.type = type;
    
    const eyeIcon = document.getElementById('eye-icon');
    if (type === 'text') {
        eyeIcon.innerHTML = `<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.45 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/>`;
    } else {
        eyeIcon.innerHTML = `<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>`;
    }
}

function checkKeyboardLayout(event) {
    warningsDiv.textContent = '';
    warningsDiv.style.display = 'none';
    
    const warnings = [];
    
    if (event && event.getModifierState && event.getModifierState('CapsLock')) {
        warnings.push('⚠ Warning: Caps Lock is ON');
    }
    
    const cyrillicRegex = /[а-яА-ЯёЁіІїЇєЄґҐ]/;
    if (cyrillicRegex.test(authPasswordInput.value)) {
        warnings.push('⚠ Warning: Cyrillic layout detected (RU/UA)');
    }
    
    if (warnings.length > 0) {
        warningsDiv.style.display = 'block';
        warnings.forEach(w => {
            const d = document.createElement('div');
            d.textContent = w;
            warningsDiv.appendChild(d);
        });
    }
}

async function submitAuth() {
    const password = authPasswordInput.value;
    if (!password || password.length < 4) {
        alert('Password must be at least 4 characters long.');
        return;
    }
    
    if (isAuthSetupMode) {
        try {
            const response = await fetch(API_AUTH_SETUP, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password: password })
            });
            if (response.ok) {
                isAuthSetupMode = false;
                authModal.style.display = 'none';
                alert('Master Password set successfully! System armed.');
                await fetchUsbData();
            } else {
                const err = await response.json();
                alert('Setup failed: ' + (err.error || 'Unknown Error'));
            }
        } catch (error) {
            console.error(error);
            alert('Setup failed due to network error.');
        }
    } else {
        const duration = parseInt(unlockDurationSelect.value);
        try {
            const response = await fetch(API_AUTH_UNLOCK, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password: password, duration: duration })
            });
            if (response.ok) {
                authModal.style.display = 'none';
                await fetchUsbData();
            } else {
                const err = await response.json();
                alert('Unlock failed: ' + (err.error || 'Invalid Password'));
            }
        } catch (error) {
            console.error(error);
            alert('Unlock failed due to network error.');
        }
    }
}

function renderTimeline(devices) {
    devices.sort((a, b) => {
        if (a.last_connected === 'Unknown' || !a.last_connected) return 1;
        if (b.last_connected === 'Unknown' || !b.last_connected) return -1;
        return new Date(b.last_connected) - new Date(a.last_connected);
    });

    const total = devices.length;
    const whitelisted = devices.filter(d => d.is_whitelisted).length;
    const threats = total - whitelisted;

    metricTotal.textContent = total;
    metricWhitelisted.textContent = whitelisted;
    metricThreats.textContent = threats;
    chronicleCount.textContent = total + (total === 1 ? ' record' : ' records');

    if (threats > 0) {
        cardThreats.classList.add('threat-active');
    } else {
        cardThreats.classList.remove('threat-active');
    }

    if (devices.length === 0) {
        timelineList.textContent = '';
        const emptyDiv = document.createElement('div');
        emptyDiv.className = 'empty-state';
        
        const titleDiv = document.createElement('div');
        titleDiv.textContent = '0 NO DISCOVERED USB ENTRIES';
        
        const descDiv = document.createElement('div');
        descDiv.textContent = 'Target key USBSTOR path appears completely blank.';
        
        emptyDiv.appendChild(titleDiv);
        emptyDiv.appendChild(descDiv);
        timelineList.appendChild(emptyDiv);
        return;
    }

    if (previouslySeenSerials === null) {
        previouslySeenSerials = new Set();
        devices.forEach(d => {
            previouslySeenSerials.add(d.serial_number);
        });
    } else {
        devices.forEach(d => {
            const serial = d.serial_number;
            if (!previouslySeenSerials.has(serial)) {
                previouslySeenSerials.add(serial);
                if (!d.is_whitelisted) {
                    showToast(d.device_name, serial);
                }
            }
        });
    }

    timelineList.textContent = '';
    const timelineDiv = document.createElement('div');
    timelineDiv.className = 'timeline';

    devices.forEach(device => {
        const isTrusted = device.is_whitelisted;
        const cardClass = isTrusted ? 'whitelisted' : 'unauthorized';
        
        const card = document.createElement('div');
        card.className = 'timeline-card ' + cardClass;
        
        const info = document.createElement('div');
        info.className = 'device-info';
        
        const titleRow = document.createElement('div');
        titleRow.className = 'device-title-row';
        
        const title = document.createElement('h3');
        title.className = 'device-title';
        title.textContent = device.device_name;
        
        const badge = document.createElement('span');
        if (isTrusted) {
            badge.className = 'badge badge-whitelisted';
            badge.textContent = '✓ Whitelisted';
        } else {
            badge.className = 'badge badge-unauthorized';
            badge.textContent = '⚠ UNAUTHORIZED DEVICE';
        }
        
        titleRow.appendChild(title);
        titleRow.appendChild(badge);
        
        const serial = document.createElement('div');
        serial.className = 'device-serial';
        serial.textContent = device.serial_number;
        
        const meta = document.createElement('div');
        meta.className = 'device-meta';
        
        const lastConnMeta = document.createElement('div');
        lastConnMeta.className = 'meta-item';
        
        const svgClock = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svgClock.setAttribute('width', '12');
        svgClock.setAttribute('height', '12');
        svgClock.setAttribute('viewBox', '0 0 24 24');
        svgClock.setAttribute('fill', 'none');
        svgClock.setAttribute('stroke', 'currentColor');
        svgClock.setAttribute('stroke-width', '2');
        svgClock.setAttribute('stroke-linecap', 'round');
        svgClock.setAttribute('stroke-linejoin', 'round');
        
        const circleClock = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circleClock.setAttribute('cx', '12');
        circleClock.setAttribute('cy', '12');
        circleClock.setAttribute('r', '10');
        
        const polyClock = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
        polyClock.setAttribute('points', '12 6 12 12 16 14');
        
        svgClock.appendChild(circleClock);
        svgClock.appendChild(polyClock);
        
        const lastConnText = document.createElement('span');
        lastConnText.textContent = 'Last: ' + device.last_connected;
        
        lastConnMeta.appendChild(svgClock);
        lastConnMeta.appendChild(lastConnText);
        
        const firstConnMeta = document.createElement('div');
        firstConnMeta.className = 'meta-item';
        
        const svgDoc = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svgDoc.setAttribute('width', '12');
        svgDoc.setAttribute('height', '12');
        svgDoc.setAttribute('viewBox', '0 0 24 24');
        svgDoc.setAttribute('fill', 'none');
        svgDoc.setAttribute('stroke', 'currentColor');
        svgDoc.setAttribute('stroke-width', '2');
        svgDoc.setAttribute('stroke-linecap', 'round');
        svgDoc.setAttribute('stroke-linejoin', 'round');
        
        const pathDoc = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        pathDoc.setAttribute('d', 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z');
        
        const polyDoc = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
        polyDoc.setAttribute('points', '14 2 14 8 20 8');
        
        svgDoc.appendChild(pathDoc);
        svgDoc.appendChild(polyDoc);
        
        const firstConnText = document.createElement('span');
        firstConnText.textContent = 'First: ' + device.first_connected;
        
        firstConnMeta.appendChild(svgDoc);
        firstConnMeta.appendChild(firstConnText);
        
        const typeMeta = document.createElement('div');
        typeMeta.className = 'meta-item';
        
        const typeText = document.createElement('span');
        typeText.style.color = 'var(--accent-info)';
        typeText.textContent = '[' + (device.is_usbstor ? 'STORAGE' : 'HID/OTHER') + ']';
        typeMeta.appendChild(typeText);

        meta.appendChild(lastConnMeta);
        meta.appendChild(firstConnMeta);
        meta.appendChild(typeMeta);
        
        info.appendChild(titleRow);
        info.appendChild(serial);
        info.appendChild(meta);
        
        const actions = document.createElement('div');
        actions.className = 'device-actions';
        
        const actionBtn = document.createElement('button');
        if (isTrusted) {
            actionBtn.className = 'btn btn-remove';
            actionBtn.textContent = 'Remove from Whitelist';
            actionBtn.onclick = () => updateDeviceSecurity(device.serial_number, false);
        } else {
            actionBtn.className = 'btn btn-whitelist';
            actionBtn.textContent = 'Trust & Whitelist Device';
            actionBtn.onclick = () => updateDeviceSecurity(device.serial_number, true);
        }
        actions.appendChild(actionBtn);
        
        card.appendChild(info);
        card.appendChild(actions);
        
        timelineDiv.appendChild(card);
    });
    
    timelineList.appendChild(timelineDiv);
}

authPasswordInput.addEventListener('keyup', checkKeyboardLayout);
authPasswordInput.addEventListener('keydown', checkKeyboardLayout);

btnRescan.addEventListener('click', fetchUsbData);
window.addEventListener('DOMContentLoaded', () => {
    fetchUsbData();
    setInterval(fetchUsbData, 2000);
});