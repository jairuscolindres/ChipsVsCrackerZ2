# ChipsVsCrackerz — Future Architecture: Full Hardware & Chip Simulation Pipeline

This document defines the architectural blueprint for a complete, end-to-end hardware simulation system in ChipsVsCrackerz. It details how **compiled firmware (C/C++)**, **custom digital silicon (Verilog)**, **physical electronic components (breadboard circuits)**, and a **software coordinator** interact to create an authentic hardware CTF playground with zero source-code leakage.

---

## 1. High-Level Architecture Overview

A complete hardware simulation requires four distinct layers working in lockstep:

```text
 ┌────────────────────────────────────────────────────────────────────────┐
 │ 1. FIRMWARE LAYER (The Software)                                       │
 │    • Written in: C / C++                                               │
 │    • Compiled with: riscv32-unknown-elf-gcc (or target toolchain)       │
 │    • Output: firmware.hex (Raw machine-code binary)                    │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │ Loaded into simulated RAM ($readmemh)
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │ 2. CHIP & SILICON LAYER (Digital Logic)                                │
 │    • Written in: Verilog (CPU Core e.g. PicoRV32 + RAM + UART + GPIO)  │
 │    • Simulated by: Verilator (Compiles Verilog to C++ or WebAssembly)  │
 │    • Role: Naturally executes machine code and drives physical pins    │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │ Exposes Pin Signals (clk, tx, rx, gpios)
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │ 3. THE COORDINATOR / TESTBENCH (The "Glue" Engine)                     │
 │    • Written in: Python or C++                                         │
 │    • Clock Generator: Pulses the CPU clock pin (clk: 0 -> 1 -> 0)      │
 │    • Signal Router: Passes voltages/logic levels to circuit parts      │
 │    • Communication Bridge: Routes UART and GPIO to WebSockets          │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │ Pin Transitions (HIGH/LOW) & Serial bytes
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │ 4. PHYSICAL CIRCUIT & USER INTERFACE (The Frontend)                    │
 │    • Components: LEDs, buttons, resistors, sensors, displays           │
 │    • Rendered with: @wokwi/elements (Web Components) + xterm.js (CLI)  │
 │    • User Action: Toggles switches, views terminal, monitors LEDs      │
 └────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Layer-by-Layer Breakdown

### Layer 1: Firmware Layer (The Machine Code)
* **What it is:** The program designed by the challenge author to run on the virtual microcontroller or custom processor.
* **Format:** Written in bare-metal C.
* **Compilation:** Cross-compiled into an ELF file, then stripped to a raw hexadecimal format:
  ```bash
  riscv32-unknown-elf-gcc -O2 -nostdlib -T linker.ld -o firmware.elf firmware.c
  riscv32-unknown-elf-objcopy -O verilog firmware.elf firmware.hex
  ```
* **Memory Mapping:** Memory-Mapped I/O (MMIO) pointers allow standard C code to manipulate hardware pins directly:
  ```c
  #define UART_TX_REG  (*(volatile unsigned int*)0x40000000)
  #define GPIO_OUT_REG (*(volatile unsigned int*)0x40000004)

  void main() {
      GPIO_OUT_REG = 0x01; // Turn on Status LED
      UART_TX_REG  = 'A';  // Transmit byte over UART
  }
  ```

---

### Layer 2: Chip & Silicon Layer (Verilog Hardware)
* **What it is:** The digital circuitry of the microcontroller, implemented in standard Verilog.
* **Instruction Set Execution:** Rather than using a separate instruction emulator, the Verilog design **is** the instruction set engine. It contains an open-source CPU core (e.g., [PicoRV32](https://github.com/YosysHQ/picorv32), [FemtoRV](https://github.com/BrunoLevy/learn-fpga), or custom logic) paired with a block of memory and peripheral controllers.
* **Verilog Skeleton (`top.v`):**
  ```verilog
  module top (
      input clk,
      input resetn,
      input uart_rx,
      output uart_tx,
      output [7:0] gpio_out
  );
      // Internal RAM
      reg [31:0] memory [0:4095];
      initial $readmemh("firmware.hex", memory);

      // CPU Core instantiation
      picorv32 cpu (
          .clk(clk),
          .resetn(resetn),
          // Bus and Memory lines
      );
  endmodule
  ```
* **Simulation Engine:** Compiled via **[Verilator](https://www.veripool.org/verilator/)** into high-speed C++ code that can run headlessly on a Linux server or compiled to WebAssembly (WASM) to run directly inside the player's web browser.

---

### Layer 3: The Coordinator / Testbench (The "Glue Engine")

The Coordinator connects the digital chip to the rest of the world and manages two vital synchronization tasks:

#### 1. Clock Generation (Time Stepper)
A physical quartz crystal oscillator is simulated via a cycle loop:
```python
# Coordinator execution loop (Python / C++)
while simulation_active:
    # 1. Drive clock high
    chip.clk = 1
    chip.eval()

    # 2. Drive clock low
    chip.clk = 0
    chip.eval()

    # 3. Read pin states
    if chip.uart_tx != previous_tx_state:
        broadcast_uart_bit(chip.uart_tx)
```

#### 2. WebSocket & Protocol Bridge
* **Chip $\rightarrow$ Browser:** When the Verilog chip asserts a GPIO pin `HIGH`, the coordinator transmits a JSON packet over WebSockets:
  ```json
  { "type": "PIN_CHANGE", "pin": 2, "state": 1 }
  ```
* **Browser $\rightarrow$ Chip:** When a player presses a button on the UI canvas, the coordinator pulls the corresponding input pin `HIGH` on the next clock cycle:
  ```json
  { "type": "USER_INPUT", "pin": 5, "state": 1 }
  ```

---

### Layer 4: Physical Circuit & User Interface (The Frontend)

* **Circuit Rendering:** Built with **[`@wokwi/elements`](https://github.com/wokwi/wokwi-elements)**, rendering interactive, responsive hardware components:
  * `<wokwi-led>` (State bound to GPIO output)
  * `<wokwi-pushbutton>` (Bound to GPIO input)
  * `<wokwi-7segment>` / `<wokwi-lcd1602>` (Bound to bus registers)
* **Terminal Interface:** Built with **`xterm.js`**, connected to the virtual UART serial stream.

---

## 3. Technology Stack Summary

| Role | Tool / Technology | License |
| :--- | :--- | :--- |
| **Firmware Toolchain** | `riscv32-unknown-elf-gcc` / `llvm` | GPL / Apache 2.0 |
| **CPU Core (Hardware)** | `PicoRV32` or `FemtoRV` (Verilog) | ISC / MIT |
| **HDL Compiler/Runner** | `Verilator` (C++ / WebAssembly) | LGPL / Artistic |
| **Coordinator / Bus** | Python (`asyncio` / `websockets`) or C++ | Custom Platform Code |
| **Frontend UI Canvas** | `@wokwi/elements` | MIT |
| **Interactive Terminal** | `xterm.js` | MIT |

---

## 4. CTF Platform Security Guarantees

1. **Complete Source Concealment:**
   * Players never receive `firmware.c` or `top.v`.
   * Only the compiled simulator binary runs in the sandbox.
2. **Support for Hardware Trojans:**
   * Authors can inject deliberate hardware vulnerabilities into the Verilog silicon (e.g., shadow registers, privilege-escalation state-machine bugs, or glitchable comparator circuits).
3. **Pluggable & Extensible:**
   * Authors can upload either standard C firmware or upload custom Verilog modules to test novel cryptographic accelerators and custom instruction sets.
