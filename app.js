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
        
        const metaItem = document.createElement('div');
        metaItem.className = 'meta-item';
        
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', '12');
        svg.setAttribute('height', '12');
        svg.setAttribute('viewBox', '0 0 24 24');
        svg.setAttribute('fill', 'none');
        svg.setAttribute('stroke', 'currentColor');
        svg.setAttribute('stroke-width', '2');
        svg.setAttribute('stroke-linecap', 'round');
        svg.setAttribute('stroke-linejoin', 'round');
        
        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('x', '3');
        rect.setAttribute('y', '4');
        rect.setAttribute('width', '18');
        rect.setAttribute('height', '18');
        rect.setAttribute('rx', '2');
        rect.setAttribute('ry', '2');
        
        const line1 = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line1.setAttribute('x1', '16');
        line1.setAttribute('y1', '2');
        line1.setAttribute('x2', '16');
        line1.setAttribute('y2', '6');
        
        const line2 = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line2.setAttribute('x1', '8');
        line2.setAttribute('y1', '2');
        line2.setAttribute('x2', '8');
        line2.setAttribute('y2', '6');
        
        const line3 = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line3.setAttribute('x1', '3');
        line3.setAttribute('y1', '10');
        line3.setAttribute('x2', '21');
        line3.setAttribute('y2', '10');
        
        svg.appendChild(rect);
        svg.appendChild(line1);
        svg.appendChild(line2);
        svg.appendChild(line3);
        
        const timeSpan = document.createElement('span');
        timeSpan.textContent = 'Last Connected: ' + device.last_connected;
        
        metaItem.appendChild(svg);
        metaItem.appendChild(timeSpan);
        meta.appendChild(metaItem);
        
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
window.addEventListener('DOMContentLoaded', fetchUsbData);