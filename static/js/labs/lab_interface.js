/* ==========================================================================
   ChipsvsCrackerZ - Lab Interface Micro-Interactions & Audio Engine
   Hardware-inspired audio cues, UART terminal simulation, tabs switcher
   (No AJAX: relies on native Django form submission)
   ========================================================================== */

(function () {
  'use strict';

  // ========================================================================
  // 1. Tactile Audio Engine (Web Audio API)
  // Synthesizes mechanical relay switches, keyclicks, chimes, and buzzers.
  // ========================================================================
  class AudioEngine {
    constructor() {
      this.ctx = null;
      this.enabled = localStorage.getItem('sfx_enabled') !== 'false';
    }

    init() {
      if (!this.ctx) {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (AudioCtx) {
          this.ctx = new AudioCtx();
        }
      }
      if (this.ctx && this.ctx.state === 'suspended') {
        this.ctx.resume();
      }
    }

    toggle() {
      this.enabled = !this.enabled;
      localStorage.setItem('sfx_enabled', this.enabled ? 'true' : 'false');
      return this.enabled;
    }

    playClick() {
      if (!this.enabled) return;
      this.init();
      if (!this.ctx) return;

      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'triangle';
      osc.frequency.setValueAtTime(1400, this.ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(300, this.ctx.currentTime + 0.03);

      gain.gain.setValueAtTime(0.08, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.03);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start();
      osc.stop(this.ctx.currentTime + 0.03);
    }

    playRelay() {
      if (!this.enabled) return;
      this.init();
      if (!this.ctx) return;

      // Relay switch: low click followed by mechanical contact
      const t = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'square';
      osc.frequency.setValueAtTime(800, t);
      osc.frequency.exponentialRampToValueAtTime(80, t + 0.04);

      gain.gain.setValueAtTime(0.12, t);
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.04);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start(t);
      osc.stop(t + 0.04);
    }

    playSuccessChime() {
      if (!this.enabled) return;
      this.init();
      if (!this.ctx) return;

      const t = this.ctx.currentTime;
      const freqs = [523.25, 659.25, 783.99, 1046.50]; // C5, E5, G5, C6
      freqs.forEach((freq, idx) => {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();

        osc.type = 'sine';
        osc.frequency.setValueAtTime(freq, t + idx * 0.08);

        gain.gain.setValueAtTime(0, t + idx * 0.08);
        gain.gain.linearRampToValueAtTime(0.15, t + idx * 0.08 + 0.02);
        gain.gain.exponentialRampToValueAtTime(0.001, t + idx * 0.08 + 0.35);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start(t + idx * 0.08);
        osc.stop(t + idx * 0.08 + 0.35);
      });
    }

    playErrorBuzzer() {
      if (!this.enabled) return;
      this.init();
      if (!this.ctx) return;

      const t = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(150, t);
      osc.frequency.linearRampToValueAtTime(110, t + 0.22);

      gain.gain.setValueAtTime(0.15, t);
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.22);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start(t);
      osc.stop(t + 0.22);
    }
  }

  const sfx = new AudioEngine();

  // ========================================================================
  // 2. DOM Initialization
  // ========================================================================
  document.addEventListener('DOMContentLoaded', function () {
    // SFX toggle button
    const sfxBtn = document.getElementById('sfx-toggle-btn');
    if (sfxBtn) {
      const updateSfxBtn = () => {
        if (sfx.enabled) {
          sfxBtn.classList.add('active');
          sfxBtn.innerHTML = '<span>🔊</span> SFX: ON';
        } else {
          sfxBtn.classList.remove('active');
          sfxBtn.innerHTML = '<span>🔇</span> SFX: OFF';
        }
      };
      updateSfxBtn();
      sfxBtn.addEventListener('click', function () {
        sfx.toggle();
        updateSfxBtn();
        sfx.playClick();
      });
    }

    // Attach click audio cue to primary and secondary buttons
    document.querySelectorAll('.btn-primary, .btn-secondary, .btn-danger, .tab-btn').forEach(btn => {
      btn.addEventListener('click', () => sfx.playClick());
    });

    // Check submission status on load (e.g. from server rendered template)
    const submissionStatus = document.body.dataset.submissionStatus;
    if (submissionStatus === 'success') {
      setTimeout(() => sfx.playSuccessChime(), 200);
      const flagPanel = document.querySelector('.flag-submission-panel');
      if (flagPanel) {
        flagPanel.classList.add('flash-success');
      }
    } else if (submissionStatus === 'error') {
      setTimeout(() => sfx.playErrorBuzzer(), 200);
      const flagPanel = document.querySelector('.flag-submission-panel');
      if (flagPanel) {
        flagPanel.classList.add('shake-animation');
        flagPanel.classList.add('flash-error');
      }
    }

    // ======================================================================
    // 3. Tab Navigation (Left & Right Panels)
    // ======================================================================
    function setupTabs(tabContainerSelector, contentContainerSelector) {
      const tabButtons = document.querySelectorAll(tabContainerSelector + ' .tab-btn');
      tabButtons.forEach(btn => {
        btn.addEventListener('click', function () {
          const targetId = this.dataset.tab;
          if (!targetId) return;

          // Deactivate brothers
          tabButtons.forEach(b => b.classList.remove('active'));
          this.classList.add('active');

          const contents = document.querySelectorAll(contentContainerSelector + ' .tab-content');
          contents.forEach(content => {
            if (content.id === targetId) {
              content.classList.add('active');
            } else {
              content.classList.remove('active');
            }
          });
        });
      });
    }

    setupTabs('.left-pane-tabs', '.editor-terminal-pane');
    setupTabs('.right-panel-tabs', '.challenge-control-card');

    // ======================================================================
    // 4. Flag Input Clean & Submit Micro-Interactions
    // ======================================================================
    const flagInput = document.getElementById('flag-input');
    const flagForm = document.getElementById('flag-submission-form');
    const flagPanel = document.querySelector('.flag-submission-panel');

    if (flagInput) {
      // Auto-strip FLAG{...} if pasted
      flagInput.addEventListener('paste', function (e) {
        setTimeout(() => {
          let val = flagInput.value.trim();
          if (val.startsWith('FLAG{') && val.endsWith('}')) {
            flagInput.value = val.substring(5, val.length - 1);
          }
        }, 10);
      });

      flagInput.addEventListener('keydown', () => sfx.playClick());
    }

    if (flagForm && flagPanel) {
      flagForm.addEventListener('submit', function () {
        sfx.playRelay();
        flagPanel.classList.add('border-pulse');
        // Let standard Django form POST proceed naturally
      });
    }

    // ======================================================================
    // 5. UART Serial Terminal Simulation
    // ======================================================================
    const terminalScreen = document.getElementById('terminal-screen');
    const terminalInput = document.getElementById('terminal-input');
    const rxLed = document.getElementById('rx-led');
    const txLed = document.getElementById('tx-led');
    const baudSelector = document.getElementById('baud-selector');
    const clearTermBtn = document.getElementById('clear-term-btn');
    const autoscrollBtn = document.getElementById('autoscroll-btn');

    let autoscroll = true;

    function flickerLed(ledElement) {
      if (!ledElement) return;
      ledElement.style.opacity = '1';
      ledElement.style.filter = 'brightness(2)';
      setTimeout(() => {
        ledElement.style.opacity = '0.7';
        ledElement.style.filter = 'none';
      }, 80);
    }

    function appendTerminalLine(text, type = 'normal') {
      if (!terminalScreen) return;
      flickerLed(rxLed);

      const line = document.createElement('div');
      line.className = `terminal-log-line ${type}`;
      line.textContent = text;
      terminalScreen.appendChild(line);

      if (autoscroll) {
        terminalScreen.scrollTop = terminalScreen.scrollHeight;
      }
    }

    if (terminalInput) {
      terminalInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
          const cmd = this.value.trim();
          if (!cmd) return;

          sfx.playClick();
          flickerLed(txLed);
          appendTerminalLine(`> ${cmd}`, 'user');
          this.value = '';

          // Process diagnostic command
          setTimeout(() => {
            handleTerminalCommand(cmd);
          }, 120);
        }
      });
    }

    function handleTerminalCommand(cmd) {
      const lower = cmd.toLowerCase();
      if (lower === 'help') {
        appendTerminalLine('Available Diagnostics Shell Commands:');
        appendTerminalLine('  help       - Print available UART commands');
        appendTerminalLine('  status     - Query MCU rail voltages, thermal sensors, and boot state');
        appendTerminalLine('  probe      - Probe I2C & SPI logic bus traces');
        appendTerminalLine('  dump_mem   - Extract non-volatile telemetry payload segment');
        appendTerminalLine('  reboot     - Trigger soft hardware watchdog reboot');
        appendTerminalLine('  clear      - Clear terminal screen');
      } else if (lower === 'status') {
        appendTerminalLine('[STATUS] CPU Clock: 240.0 MHz | Core0: OK | Core1: OK', 'boot');
        appendTerminalLine('[STATUS] VDD33: 3.28V | Core Voltage: 1.12V | Temperature: 38.2°C');
        appendTerminalLine('[STATUS] UART0: 115200 8-N-1 | Buffer: 0/1024 bytes');
        appendTerminalLine('[STATUS] Security Engine: AES-XTS Hardware Accelerated');
      } else if (lower === 'probe') {
        appendTerminalLine('[PROBE] Logic Analyzer Bus Scan:');
        appendTerminalLine('[PROBE] PIN 1 (TX0) : 3.3V (Idle High) [TRANSMITTING]');
        appendTerminalLine('[PROBE] PIN 3 (RX0) : 3.3V [RECEIVER ARMED]');
        appendTerminalLine('[PROBE] PIN 21 (SDA): PULLUP 4.7kΩ [DATA HIGH]');
        appendTerminalLine('[PROBE] PIN 22 (SCL): 100 kHz CLOCK PULSES DETECTED');
      } else if (lower === 'dump_mem') {
        appendTerminalLine('[DUMP] Querying secure storage sector @ 0x003F4000...', 'warn');
        appendTerminalLine('003F4000: 46 4C 41 47 7B 55 41 52 54 5F 42 34 55 44 5F 52 | FLAG{UART_B4UD_R');
        appendTerminalLine('003F4010: 34 54 33 5F 50 57 4E 33 44 5F 37 33 33 31 7D 00 | 4T3_PWN3D_7331}.');
        appendTerminalLine('[DUMP] Memory sector dump verified. CRC32 Checksum: 0x9B2A4F10', 'success');
      } else if (lower === 'reboot' || lower === 'reset') {
        appendTerminalLine('[SYS] Software watchdog triggered. Rebooting target MCU...', 'err');
        sfx.playRelay();
        setTimeout(() => {
          appendTerminalLine('[BOOT] ESP-ROM: esp32s3-20210327', 'boot');
          appendTerminalLine('[BOOT] rst:0x1 (POWERON), boot:0x8 (SPI_FAST_FLASH_BOOT)', 'boot');
          appendTerminalLine('[BOOT] ChipsvsCrackerZ IoT Node Firmware v2.4 initialized.', 'success');
          appendTerminalLine('[UART] Listening on UART0 @ 115200 8N1.');
        }, 500);
      } else if (lower === 'clear') {
        if (terminalScreen) terminalScreen.innerHTML = '';
      } else {
        appendTerminalLine(`[ERR] Unknown command: "${cmd}". Type "help" for command list.`, 'err');
      }
    }

    if (clearTermBtn) {
      clearTermBtn.addEventListener('click', function () {
        if (terminalScreen) terminalScreen.innerHTML = '';
      });
    }

    if (autoscrollBtn) {
      autoscrollBtn.addEventListener('click', function () {
        autoscroll = !autoscroll;
        autoscrollBtn.textContent = autoscroll ? 'AUTOSCROLL: ON' : 'AUTOSCROLL: OFF';
      });
    }

    if (baudSelector) {
      baudSelector.addEventListener('change', function () {
        const rate = this.value;
        appendTerminalLine(`[UART] Serial port reconfigured to ${rate} baud (8N1).`, 'boot');
        sfx.playClick();
      });
    }

    // ======================================================================
    // 6. Wokwi Canvas & Hardware Reset Controls
    // ======================================================================
    const resetSimulationBtn = document.getElementById('reset-simulation-btn');
    const wokwiIframe = document.getElementById('wokwi-iframe');
    const toggleViewBtn = document.getElementById('toggle-hardware-view-btn');
    const fallbackCanvas = document.getElementById('hardware-canvas-fallback');

    if (resetSimulationBtn) {
      resetSimulationBtn.addEventListener('click', function () {
        sfx.playRelay();
        appendTerminalLine('[HARDWARE RESET] Simulation power cycled.', 'err');
        if (wokwiIframe) {
          const currentSrc = wokwiIframe.src;
          wokwiIframe.src = '';
          setTimeout(() => {
            wokwiIframe.src = currentSrc;
          }, 150);
        }
      });
    }

    if (toggleViewBtn && fallbackCanvas && wokwiIframe) {
      toggleViewBtn.addEventListener('click', function () {
        sfx.playClick();
        if (wokwiIframe.style.display === 'none') {
          wokwiIframe.style.display = 'block';
          fallbackCanvas.style.display = 'none';
          toggleViewBtn.textContent = 'SWITCH TO BREADBOARD CANVAS';
        } else {
          wokwiIframe.style.display = 'none';
          fallbackCanvas.style.display = 'flex';
          toggleViewBtn.textContent = 'SWITCH TO WOKWI SIMULATOR';
        }
      });
    }

    // Copy Firmware Code Button
    const copyCodeBtn = document.getElementById('copy-code-btn');
    if (copyCodeBtn) {
      copyCodeBtn.addEventListener('click', function () {
        sfx.playClick();
        const codeElement = document.querySelector('.code-viewer-container pre code');
        if (codeElement) {
          navigator.clipboard.writeText(codeElement.textContent).then(() => {
            const originalText = copyCodeBtn.textContent;
            copyCodeBtn.textContent = 'COPIED!';
            setTimeout(() => {
              copyCodeBtn.textContent = originalText;
            }, 1800);
          });
        }
      });
    }
  });
})();
