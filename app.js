const API_HISTORY = '/api/usb-history';
const API_ADD = '/api/whitelist/add';
const API_REMOVE = '/api/whitelist/remove';

const btnRescan = document.getElementById('btn-rescan');
const timelineList = document.getElementById('timeline-list');
const metricTotal = document.getElementById('metric-total');
const metricWhitelisted = document.getElementById('metric-whitelisted');
const metricThreats = document.getElementById('metric-threats');
const cardThreats = document.getElementById('card-threats');
const chronicleCount = document.getElementById('chronicle-count');

let previouslySeenSerials = null;

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

async function updateDeviceSecurity(serialNumber, trustState) {
    const apiTarget = trustState ? API_ADD : API_REMOVE;
    try {
        const response = await fetch(apiTarget, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ serial_number: serialNumber })
        });

        if (response.ok) {
            await fetchUsbData();
        } else {
            alert('Database Action Unresolved');
        }
    } catch (error) {
        console.error(error);
        alert('Network error: State change could not be committed.');
    }
}

btnRescan.addEventListener('click', fetchUsbData);
window.addEventListener('DOMContentLoaded', () => {
    fetchUsbData();
    setInterval(fetchUsbData, 2000);
});