# ChipsVsCrackerz — Wokwi Challenge Design & Category Guide

This guide establishes the architectural boundaries, viable CTF categories, and design patterns for authoring challenges using embedded **Wokwi** simulations where players have access to `sketch.ino` (source code) and `diagram.json` (circuit wiring).

---

## 1. The Threat Model & Architecture Constraints

Because Wokwi runs client-side in an `<iframe>` with public project visibility:
1. **Source Transparency (White-Box Model):** Players can view or extract `sketch.ino` and `diagram.json` via DevTools or Wokwi's public APIs.
2. **Functional Logic Simulation Only:** Wokwi emulates digital instruction execution and basic peripherals. It does **not** simulate silicon-level transistor physics, supply voltage sags, power rail noise, or electromagnetic radiation.
3. **No Hardware Security Enclaves:** Hardware security features like secure boot fuses, eFuses, flash encryption, and hardware crypto engines are not cryptographically isolated from the simulator's host environment.

Therefore, challenges must be designed as **White-Box Hardware Challenges**, where the puzzle is not *"find the hidden source code"*, but rather *"interact with the running circuit and protocol to reach the target exploit state"*.

---

## 2. Incompatible / Broken Categories

The following categories are **not viable** under a visible-source Wokwi setup:

| Category | Reason for Incompatibility |
| :--- | :--- |
| **Firmware Reverse Engineering** | Completely nullified. When players have the original C/C++ source code, there is no assembly or stripped binary to decompile in Ghidra/IDA Pro. |
| **Authentication Bypass / Secret Audits** | Trivially broken. Even if flags are XOR-masked, players can inspect the decryption algorithm, PIN check logic, or hash comparison directly in `sketch.ino` and solve it offline without running the lab. |
| **Memory Corruption & Binary Exploitation** | Broken and unrealistic. Buffer overflows and format string vulnerabilities are obvious in source, and Wokwi does not accurately reproduce real-world MPU (Memory Protection Unit) or ASLR/heap constraints. |
| **Hardware Glitching & Fault Injection** | Impossible. Wokwi cannot emulate voltage brownouts, clock glitching, or optical fault injection (skipping instructions via transient hardware disruptions). |
| **Physical Side-Channel Attacks (DPA/CPA)** | Impossible. Power consumption analysis and electromagnetic emissions cannot be measured in a browser JavaScript event loop. |

---

## 3. Recommended & Highly Viable Categories

When designing for visible source and schematic environments, the following categories thrive:

### A. Hardware Interfacing & Protocol Decoding (UART, I2C, SPI)
* **Mechanic:** The microcontroller communicates with simulated peripherals (EEPROMs, sensors, shift registers, or displays). The secret or key is transmitted across the digital bus rather than printed to the terminal.
* **Player Objective:** Use Wokwi's **built-in 8-channel Logic Analyzer** part (`wokwi-logic-analyzer`).
* **Workflow:**
  1. Players wire logic analyzer channels to the appropriate GPIO lines (SDA/SCL, MOSI/MISO/SCK, or TX/RX).
  2. Run the simulation to capture signal transitions.
  3. Download the generated `.vcd` (Value Change Dump) waveform file.
  4. Open the capture in **PulseView / Sigrok** to decode packets and recover the transmitted flag or crypto keys.

### B. Combinational Logic & Circuit Analysis
* **Mechanic:** Pure circuit design utilizing logic gates (74HC series ICs, AND/OR/XOR gates, flip-flops, resistors, and dip switches).
* **Player Objective:** Analyze the schematic in `diagram.json`, determine the truth table, and toggle inputs to produce the required output.
* **Flag Delivery:** The circuit illuminates a 7-segment display, enables an LCD screen, or pulls an enable line that signals the MCU to output the completion token.

### C. Industrial Control Systems (ICS / SCADA) & Physical State Exploitation
* **Mechanic:** The firmware represents a physical process controller (e.g., boiler heater, water tank pump, centrifuge motor).
* **Player Objective:** The source code acts as the "system operations manual". Players must identify logic flaws, race conditions, or unhandled sensor states.
* **Example:** Manipulating an analog potentiometer (pressure sensor) while pulsing a push button within a specific timing window to trigger an emergency maintenance dump that reveals the flag.

### D. Cryptographic Hardware Protocols & Weak PRNGs
* **Mechanic:** The MCU exposes an interactive challenge-response authentication service over UART.
* **Player Objective:** The source code reveals the algorithm, but the implementation contains cryptographic flaws (e.g., using `rand()` seeded with a predictable timer like `millis()`, weak XOR streams, or replayable tokens).
* **Workflow:** Players interact with the Serial Monitor or write an external script to compute the predictable response before the hardware watchdog timer resets.

---

## 4. Flag Security Best Practices for Lab Authors

1. **Never Hardcode Plaintext Flags:**
   Store keys as obfuscated byte arrays or compute them dynamically so that simple text search (`grep FLAG{`) yields nothing:
   ```cpp
   // Masked with XOR key 0x5A
   const uint8_t MASKED_PAYLOAD[] = { 0x3e, 0x69, 0x6e, 0x3e, ... };
   ```

2. **Trigger-Based Revelation:**
   Only decode or emit the flag when physical circuit conditions are satisfied (e.g., specific GPIO states held high, or valid packet received over I2C).

3. **Backend Flag Verification:**
   Never expose the flag in frontend templates (`workspace.html`) or JavaScript (`LAB_DATA.flag`). Always validate submitted flags via backend `POST` requests to the Django platform.
