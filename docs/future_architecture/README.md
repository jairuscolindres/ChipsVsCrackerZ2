# ChipsVsCrackerz — Future Architecture Documentation Hub

This directory contains the technical design specifications and architectural roadmaps for evolving the **ChipsVsCrackerz** hardware CTF platform beyond basic web embeds toward a full, multi-layer hardware simulation engine.

---

## Architecture Documents

* **[Full Hardware & Chip Simulation Pipeline](hardware_simulation_pipeline.md):**  
  Detailed blueprint explaining how **compiled firmware (C/C++)**, **custom digital silicon (Verilog)**, the **coordinator/testbench engine**, and **interactive browser UI (`@wokwi/elements` + `xterm.js`)** integrate into a unified, secure simulation stack.

## Related References in `docs/`

* **[`docs/challenge_categories.md`](../challenge_categories.md):**  
  Guide to viable vs. incompatible CTF challenge categories when using client-side Wokwi embeds.
* **[`docs/advanced_hardware_simulation.md`](../advanced_hardware_simulation.md):**  
  Overview of ready-to-use open-source engines for advanced categories:
  * *QEMU / Unicorn* for Firmware Reverse Engineering.
  * *Rainbow (Ledger Donjon)* for Fault Injection & Glitching.
  * *ChipWhisperer Virtual Targets* for Side-Channel Power Analysis (DPA/CPA).
* **[`docs/security.md`](../security.md):**  
  Current threat model, moderation queue, and firmware sandboxing guidelines.
