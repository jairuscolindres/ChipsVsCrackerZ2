# ChipsVsCrackerz — Advanced Hardware Simulation Architecture Guide

This document outlines the architecture, open-source engines, and implementation patterns required to simulate advanced hardware security challenges—including **Firmware Reverse Engineering**, **Fault Injection (Glitching)**, and **Side-Channel Analysis (DPA/CPA)**—without building a custom simulation engine from scratch.

---

## 1. Executive Summary

Building a cycle-accurate, transistor-level physical hardware emulator from scratch is impractical for an application team. Instead, professional hardware CTFs and embedded security researchers rely on **mature, open-source emulation engines** that simulate hardware failure modes and physical leakages programmatically.

```
┌───────────────────────────────────────┬────────────────────────────────────────┐
│ Challenge Category                    │ Recommended Open-Source Engine         │
├───────────────────────────────────────┼────────────────────────────────────────┤
│ Firmware Reverse Engineering & Pwn    │ QEMU / Unicorn Engine                  │
│ Fault Injection & Glitching           │ Rainbow (Ledger Donjon) / Renode       │
│ Side-Channel Power Analysis (DPA/CPA) │ ChipWhisperer Virtual / Rainbow        │
└───────────────────────────────────────┴────────────────────────────────────────┘
```

---

## 2. Deep Dive: Category Implementation

### A. Firmware Reverse Engineering & Binary Exploitation

In this track, players are given a compiled binary (`.bin` or `.elf`) stripped of source code and symbols.

* **Underlying Engine:** **[QEMU System Mode](https://www.qemu.org/)** (`qemu-system-arm`, `qemu-system-riscv32`, `qemu-esp32`) or **[Unicorn Engine](https://www.unicorn-engine.org/)**.
* **Architecture:**
  1. **Author Upload:** The lab author uploads the source code or binary. The backend compiles it and stores the raw binary.
  2. **Player Download:** The platform provides a direct download link for `firmware.bin` / `firmware.elf`.
  3. **Live Instance:** When the player launches the challenge, a headless QEMU container boots the firmware and exposes the UART interface over a TCP socket (e.g., `nc <host> <port>`).
* **Player Workflow:**
  * Disassemble and decompile `firmware.bin` in **Ghidra**, **IDA Pro**, or **Binary Ninja**.
  * Locate vulnerable functions (e.g., stack buffer overflows in UART packet parsers, hardcoded decryption routines, or format string bugs).
  * Write an exploit using Python (`pwntools`) to send payloads to the TCP socket to hijack the program counter or trigger the flag printout.

---

### B. Fault Injection & Glitching (Clock & Voltage Glitches)

Physical fault injection uses voltage drops, clock pulses, or laser pulses to disrupt instruction execution. In software, this is achieved using **Fault Models**.

* **Underlying Engine:** **[Ledger-Donjon Rainbow](https://github.com/Ledger-Donjon/rainbow)** (built on top of Unicorn) or **[Renode](https://renode.io/)**.
* **Supported Fault Models:**
  * **`fault_skip`**: Forces the program counter to skip the target instruction completely (simulates a clock glitch or laser shot skipping a security check like `BNE verify_failed`).
  * **`fault_stuck_at`**: Forces an instruction's destination register to a fixed value (e.g., forcing Register `R0 = 0`, simulating a bit-reset attack on a PIN comparison).
* **Architecture & Workflow:**
  1. **Frontend UI:** The player interacts with a "Glitch Workbench" specifying:
     * *Trigger Offset:* Instruction address or clock cycle count (e.g., `0x0800043A`).
     * *Glitch Type:* `fault_skip` or `fault_stuck_at(reg='r0', val=0)`.
  2. **Backend Execution:** A Django/Celery worker runs a Python script wrapping Rainbow:
     ```python
     from rainbow import Rainbow
     from rainbow.generics import arm

     r = Rainbow(arm)
     r.load("secure_bootloader.bin")
     r.start(0x08000000)

     # Player injected glitch parameters
     target_addr = int(request.POST.get("target_addr"), 16)
     r.fault_skip(target_addr)

     # Step execution and check state
     r.step(max_steps=1000)
     if r.bypassed_authentication:
         return JsonResponse({"status": "GLITCH_SUCCESS", "flag": "FLAG{...}"})
     ```
  3. **Feedback:** The platform reports if the glitch caused a `SUCCESS`, `PANIC / CRASH`, or `RESET`.

---

### C. Side-Channel Power Analysis (DPA / CPA)

Power analysis exploits the fact that CMOS transistors consume varying amounts of current depending on the data bits being processed (Hamming Weight and Hamming Distance).

* **Underlying Engine:** **[ChipWhisperer Virtual Targets](https://github.com/newaetech/chipwhisperer)** or **Rainbow (Lascar)**.
* **How Simulated Power is Modeled:**
  During binary execution, the emulator computes the **Hamming Weight** of every value loaded into the ALU or data bus:
  $$\text{Power}(t) \propto \text{HammingWeight}(\text{Value}_t) + \text{Gaussian Noise}$$
* **Architecture & Workflow:**
  1. **Trace Generator:** The player sends plaintexts to the platform. The backend encrypts them with a secret key using simulated power logging and returns an array of power consumption curves (exported as a `.npy` or `.trc` file).
  2. **Player Tooling:** The player writes a Python script using Correlation Power Analysis (CPA) to correlate intermediate S-box outputs with power consumption spikes:
     ```python
     import numpy as np
     import chipwhisperer.analyzer as cwa

     # Load simulated traces from ChipsVsCrackerz
     traces = np.load("power_traces.npy")
     plaintexts = np.load("plaintexts.npy")

     # Perform Correlation Power Analysis (CPA) to recover AES Key
     leak_model = cwa.leakage_models.sbox_output
     attack = cwa.cpa(traces, plaintexts, leak_model)
     recovered_key = attack.run()
     ```

---

## 3. Platform Architecture: The Hybrid Model

ChipsVsCrackerz can support both accessible and advanced challenges by organizing challenges into two architectural tracks:

```text
ChipsVsCrackerz Platform
│
├── Track 1: Interactive Circuit & Protocol Labs (Wokwi Engine)
│   ├── Client-side Wokwi embed / @wokwi/elements
│   ├── I2C / SPI / UART protocol decoding (PulseView / Sigrok)
│   ├── Combinational logic gate puzzles
│   └── Industrial control (SCADA) process manipulation
│
└── Track 2: Advanced Hardware Security (Python / Microservice Engine)
    ├── Firmware Reverse Engineering (Dockerized QEMU + Ghidra binary downloads)
    ├── Fault Injection Simulator (Ledger's Rainbow library worker)
    └── Power Analysis / DPA (ChipWhisperer virtual target trace generator)
```

### Advantages of This Hybrid Setup:
1. **Zero Reinvention:** Leverages battle-tested tools used by professional security researchers.
2. **Cost-Effective:** Wokwi runs in the player's browser for visual challenges; advanced glitching and power trace generation run as quick, headless Python scripts on demand.
3. **Full Security Coverage:** Covers the complete hardware hacking lifecycle—from breadboard wiring up to silicon-level fault injection and side-channel cryptography.
