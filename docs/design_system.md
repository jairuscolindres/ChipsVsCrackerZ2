# ChipsvsCrackerZ — UI/UX Design System Specification

A unified, hardware-inspired design system tailored for **ChipsvsCrackerZ**, built around a **"Cyber-Diner / Industrial Circuit"** aesthetic (*"Byte-sized firmware, deep-fried electronics"*).

---

## 1. Visual & Thematic Foundations

### Design Metaphor

* **The Breadboard & Workbench:** Pages act as mounting surfaces.
* **Component Cards:** Content blocks framed like Integrated Circuit (IC) packages with corner pins and silk-screen markings.
* **LED Feedback:** Action statuses, connectivity, and validation rely on glowing diode indicators rather than standard flat badges.
* **Serial Telemetry:** Text outputs, terminals, and logs mimic real-time UART / RS-232 serial streams.

### Grid & Spacing

* **Base Unit:** $8\text{px}$ spatial grid ($8\text{px}$, $16\text{px}$, $24\text{px}$, $32\text{px}$, $48\text{px}$, $64\text{px}$).
* **Background Layer:** Dark PCB texture overlaid with a subtle $16\text{px} \times 16\text{px}$ dot-matrix grid to emulate schematic layout paper.

---

## 2. Color System

### Base / Board Tokens

| Token | Hex Code | Usage |
| --- | --- | --- |
| `bg-primary` | `#0D1117` | Main platform canvas / chassis background |
| `bg-secondary` | `#161B22` | Cards, sidebars, dock panels, editor containers |
| `bg-tertiary` | `#21262D` | Form inputs, inactive tabs, disabled surfaces |
| `border-subtle` | `#30363D` | Trace lines, panel dividers, card boundaries |
| `border-active` | `#FFB800` | Focused fields, selected lab cards, active pins |

### Brand & Accent Tokens

| Token | Hex Code | Usage |
| --- | --- | --- |
| `brand-gold` | `#FFB800` | Deep-Fried Gold: Primary CTAs, key badges, gold header accents |
| `accent-copper` | `#E56B10` | Crisp Copper: Hover states, interactive highlights, secondary links |
| `cyan-glow` | `#00E5FF` | Logic Probe Cyan: Active signals, terminal outputs, code selections |

### Functional LED Tokens

| Token | Hex Code | Usage |
| --- | --- | --- |
| `status-success` | `#23D18B` | Valid Flag, compile success, active device connected |
| `status-error` | `#FF453A` | Invalid Flag, short circuit, runtime error |
| `status-warning` | `#FF9F0A` | Hints unlocked, thermal alerts, medium difficulty |
| `status-info` | `#0A84FF` | Documentation notes, easy difficulty, system logs |

---

## 3. Typography Hierarchy

### Typefaces

* **Interface & Headings:** `JetBrains Mono` or `Inter` (Clean, modern geometry with industrial feel).
* **Code, Terminals & Flags:** `Fira Code` or `Source Code Pro` (Monospace with developer ligatures enabled).

### Type Scale

* **Hero / Title Display:** $32\text{px}$ / Bold / Line-height $1.2$ — Workbench headers, page titles.
* **H1 / Section Header:** $24\text{px}$ / SemiBold / Line-height $1.3$ — Lab titles, primary modal headers.
* **H2 / Card Header:** $20\text{px}$ / SemiBold / Line-height $1.4$ — Panel titles, category section headers.
* **Body Standard:** $14\text{px}$ / Regular / Line-height $1.5$ — Challenge descriptions, user bio, instructions.
* **Caption / Metadata:** $12\text{px}$ / Regular / Line-height $1.4$ — Timestamps, chip architectures, tag labels.
* **Terminal & Code Input:** $15\text{px}$ / Monospace / Line-height $1.6$ — Flag inputs, serial logs, raw source code.

---

## 4. UI Components Specification

### Action Buttons

1. **Primary CTA (Gold Crisp):**
* Solid `#FFB800` background with dark `#0D1117` bold typography.
* Subtle $2\text{px}$ drop-glow on hover (`#FFB800` at $30\%$ opacity).
* Micro-movement: Shifts $-1\text{px}$ on Y-axis when pressed.


2. **Secondary Button (Trace Outline):**
* Transparent background with $1\text{px}$ `#30363D` border and white text.
* Hover state transforms border color to `#FFB800` with light copper text tint.


3. **Danger / Hard Reset:**
* `#FF453A` background or border for destructive actions (e.g., Reset Wokwi Simulation, Wipe Code).



### Component Cards (Lab & Stats Cards)

* Background: `#161B22` with a $1\text{px}$ `#30363D` border outline.
* Header Bar: Includes difficulty status LED badge + Point Value tag.
* Footer Bar: Chip architecture tags (e.g., `ESP32`, `AVR`, `UART`, `Logic Analyzer`).
* Solved State: Displays a glowing green LED dot and a faint `$1\text{px}$` green border border-line.

### Flag Submission Bar

* Styled as an interactive hardware payload injector panel.
* Input container uses a permanent prefix (`FLAG{`) and suffix (`}`).
* **Submit Action:** Triggers a pulse animation along the border line.
* **Correct Submission:** Green flashing border, success notification sound, "+500 PTS" animated overlay.
* **Failed Submission:** Red horizontal shake, terminal log error output (*"Checksum mismatch or invalid payload"*).

---

## 5. Screen Layout Architecture

```
+-----------------------------------------------------------------------------------+
|  [LOGO] ChipsvsCrackerZ    Dashboard  Labs  Leaderboard  Editor      [USER PROFILE] |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  +---------------------------------------+  +----------------------------------+  |
|  | LEFT PANEL: INTERACTIVE WORKBENCH     |  | RIGHT PANEL: CHALLENGE CONTROL   |  |
|  |                                       |  |                                  |  |
|  | +-----------------------------------+ |  | [Brief] [Datasheet] [Hints]      |  |
|  | | Wokwi Canvas (Virtual Hardware)   | |  | -------------------------------- |  |
|  | | - Breadboard / ESP32 / LEDs       | |  | Scenario description, signal     |  |
|  | +-----------------------------------+ |  | timing diagrams, download links. |  |
|  |                                       |  |                                  |  |
|  | +-----------------------------------+ |  | -------------------------------- |  |
|  | | Firmware Code Editor / Serial Log | |  | FLAG SUBMISSION PANEL            |  |
|  | | > Serial initialized... 115200    | |  | [ FLAG{                     } ]  |  |
|  | +-----------------------------------+ |  | [ INJECT PAYLOAD / SUBMIT     ]  |  |
|  +---------------------------------------+  +----------------------------------+  |
+-----------------------------------------------------------------------------------+

```

### Core Page Views

1. **Authentication (Register / Login):**
* Minimalist dark surface centered over a glowing circuit schematic grid.
* Text inputs feature terminal-style prompt prefixes (`user@crackerz:~$`).


2. **Dashboard:**
* Player statistics overview (Global Rank, Points, Architecture Badges).
* Activity Grid: PCB-style daily solve heatmap (dark grey to gold/green squares).
* Recommended target challenges tailored to current skill rank.


3. **Labs Library:**
* Component Inventory layout with search bar supporting architecture queries (e.g., `arch:esp32 tag:uart`).
* Filter tags by difficulty (`Easy`, `Medium`, `Hard`, `Deep-Fried`), completion status, and payload type.


4. **Lab Interface (Split Workbench):**
* **Left Side:** Top pane hosts the live Wokwi Virtual Hardware canvas; bottom pane hosts the firmware source code editor and live UART serial monitor.
* **Right Side:** Tabbed panel containing the challenge narrative, schematic pinouts, logic waveforms, and the Flag Submission engine.


5. **Lab Editor (Authoring Tool):**
* Node-based or JSON diagram editor for mounting components onto virtual breadboards.
* Trigger setup interface for defining flag emission conditions (e.g., "Emit flag on UART when Pin 4 receives high frequency clock signal").



---

## 6. Micro-Interactions & Feedback Loops

* **LED Status Lights:** Circular status indicators utilize radial gradients to imitate physical LED bulb diffusion and lens reflections.
* **Terminal Scrolling:** Auto-scrolling serial outputs maintain active focus at the bottom line, complete with a blinking block cursor (`▋`).
* **Tactile Audio Cues (Optional Toggle):** Soft mechanical key clicks and relay switch toggles when pressing main buttons or submitting payloads.
