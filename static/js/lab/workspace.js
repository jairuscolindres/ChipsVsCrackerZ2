/* ===================================================================
   ChipsvsCrackerZ — Lab Workspace JavaScript
   Handles: Tabs, Wokwi embed, Serial output, Flag submit, Resize,
            Hint reveals
   =================================================================== */

document.addEventListener('DOMContentLoaded', () => {

    // ── TAB SWITCHING ──
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('tab--active'));
            document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('tab-pane--active'));

            tab.classList.add('tab--active');
            const pane = document.getElementById('tab-' + tab.dataset.tab);
            if (pane) pane.classList.add('tab-pane--active');
        });
    });

    // ── SERIAL MONITOR ──
    const serialOutput = document.getElementById('serial-output');

    function appendSerial(text, type = 'info') {
        const cursor = document.querySelector('.serial-cursor');
        const line = document.createElement('span');

        if (type === 'success') line.style.color = 'var(--status-success)';
        else if (type === 'error') line.style.color = 'var(--status-error)';
        else if (type === 'warning') line.style.color = 'var(--status-warning)';
        else line.style.color = 'var(--cyan-glow)';

        line.innerHTML = '\n<span class="serial-prompt">&gt;</span> ' + text;

        if (cursor) cursor.before(line);
        else serialOutput.appendChild(line);

        const monitor = document.getElementById('serial-monitor');
        monitor.scrollTop = monitor.scrollHeight;
    }

    // ── WOKWI SIMULATION ──
    const btnStart    = document.getElementById('btn-start');
    const btnStop     = document.getElementById('btn-stop');
    const canvas      = document.getElementById('wokwi-canvas');
    const placeholder = document.getElementById('wokwi-placeholder');

    // Extract clean project ID in case a full URL was provided
    let rawProjectId = (LAB_DATA.wokwiProjectId || '').trim();
    let projectId = rawProjectId;
    if (projectId.includes('/projects/')) {
        projectId = projectId.split('/projects/')[1].split(/[?#]/)[0].replace(/\/+$/, '');
    } else if (projectId.startsWith('http')) {
        projectId = projectId.split('/').filter(Boolean).pop().split(/[?#]/)[0];
    }
    const embedUrl  = 'https://wokwi.com/projects/' + projectId + '?embed=1';

    btnStart.addEventListener('click', () => {
        if (projectId === 'YOUR_PROJECT_ID_HERE') {
            appendSerial('ERROR: No Wokwi project ID configured for this lab.', 'error');
            appendSerial('Set wokwi_project_id in apps/lab/views.py', 'warning');
            return;
        }

        if (placeholder) placeholder.style.display = 'none';

        let iframe = canvas.querySelector('iframe');
        if (!iframe) {
            iframe = document.createElement('iframe');
            iframe.src = embedUrl;
            iframe.allow = 'serial';
            iframe.style.width = '100%';
            iframe.style.height = '100%';
            iframe.style.border = 'none';
            canvas.appendChild(iframe);
        }

        btnStart.disabled = true;
        btnStop.disabled = false;
        appendSerial('Simulation started — loading virtual hardware...', 'success');
    });

    btnStop.addEventListener('click', () => {
        const iframe = canvas.querySelector('iframe');
        if (iframe) iframe.remove();
        if (placeholder) placeholder.style.display = 'flex';

        btnStart.disabled = false;
        btnStop.disabled = true;
        appendSerial('Simulation stopped.', 'warning');
    });

    // ── FLAG SUBMISSION ──
    const flagForm    = document.getElementById('flag-form');
    const flagInput   = document.getElementById('flag-input');
    const flagResult  = document.getElementById('flag-result');
    const flagWrapper = document.querySelector('.flag-input-wrapper');

    flagForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const payload = flagInput.value.trim();
        if (!payload) return;

        // Reset animations
        flagWrapper.classList.remove(
            'flag-input-wrapper--pulse',
            'flag-input-wrapper--shake',
            'flag-input-wrapper--success'
        );

        // Trigger pulse
        flagWrapper.classList.add('flag-input-wrapper--pulse');
        appendSerial('Injecting payload: FLAG{' + payload + '}...');

        setTimeout(() => {
            if (payload === LAB_DATA.flag) {
                // ✅ Correct
                flagWrapper.classList.add('flag-input-wrapper--success');
                flagResult.className = 'flag-result flag-result--success';
                flagResult.textContent = '✓ VALID PAYLOAD — +' + LAB_DATA.points + ' PTS';
                appendSerial('Checksum verified. Flag accepted! +' + LAB_DATA.points + ' PTS', 'success');
            } else {
                // ❌ Incorrect
                flagWrapper.classList.add('flag-input-wrapper--shake');
                flagResult.className = 'flag-result flag-result--error';
                flagResult.textContent = '✗ Checksum mismatch or invalid payload';
                appendSerial('ERROR: Checksum mismatch or invalid payload', 'error');
            }
        }, 500);

        setTimeout(() => {
            flagWrapper.classList.remove('flag-input-wrapper--pulse', 'flag-input-wrapper--shake');
        }, 1000);
    });

    // ── HINT REVEALS ──
    document.querySelectorAll('.hint-reveal-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const hintBox = btn.closest('.hint-box');
            const hintText = hintBox.querySelector('.hint-box__text');

            hintBox.classList.remove('hint-box--locked');
            hintBox.classList.add('hint-box--revealed');
            hintText.style.display = 'block';
            btn.style.display = 'none';
        });
    });

    // ── RESIZABLE SPLIT PANEL ──
    const handle    = document.getElementById('resize-handle');
    const leftPanel = document.querySelector('.panel--left');
    const workspace = document.querySelector('.workspace');

    let isResizing = false;

    handle.addEventListener('mousedown', (e) => {
        isResizing = true;
        handle.classList.add('active');
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';
        e.preventDefault();
    });

    document.addEventListener('mousemove', (e) => {
        if (!isResizing) return;
        const rect = workspace.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const pct = (x / rect.width) * 100;

        if (pct >= 30 && pct <= 75) {
            leftPanel.style.flex = 'none';
            leftPanel.style.width = pct + '%';
        }
    });

    document.addEventListener('mouseup', () => {
        if (isResizing) {
            isResizing = false;
            handle.classList.remove('active');
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
        }
    });
});
