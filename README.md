# aF4 Frozen Feeder — ESP32 PoE Trigger

Replaces the inD connect WiFi dongle on the [inD aquatics aF4](https://www.indaquatics.com/products/af4) refrigerated frozen-food feeder with an Olimex ESP32-POE-ISO running ESPHome, triggering feeds via the aF4's 0-10V port and scheduled from Home Assistant.

## How it works

ESP32-POE-ISO → GPIO32 → 220Ω → AQY212GS PhotoMOS → switches the feeder's own 12V supply (regulated to ~10.4V by an on-board LM1117-ADJ) onto the 3.5mm trigger jack. Safety guardrails (20s pulse, 5-min lockout, restore-off, flash-persisted boot lockout) are baked into the ESPHome config on-device; HA is scheduler only.

**Rev E** puts all of that on a PCB "hat" that plugs onto the ESP32's EXT1/EXT2 headers and carries both panel connectors, assembled by PCBWay. The rev C hand-wired protoboard is retired.

> The trigger pin is **GPIO32**, not GPIO13. The Olimex board has a factory 2.2 kΩ pull-up on GPIO13 that can partially turn the PhotoMOS on during boot. See `aF4-pcb-notes.md`.

## Contents

| File | Purpose |
|---|---|
| `aF4-HANDOFF.md` | **Start here if you are new to this project.** Current status, what to read in what order, the conventions and the traps |
| `aF4-MASTER-REFERENCE.md` | **Consolidated audit-oriented reference.** Every load-bearing claim tagged with its provenance (measured / datasheet / calculated / asserted) |
| `af4-feeder.yaml` | ESPHome device config (as flashed) |
| `aF4-reference.md` | Technical reference: trigger port spec, measurements, design rationale |
| `aF4-pcb-notes.md` | Board design decisions, part equivalence review, PCBWay ordering |
| `aF4-esp32-trigger-BOM.md` | Parts list |
| `aF4-assembly-guide.md` | Build sequence: print, plug together, flash, commission |
| `aF4-enclosure-notes.md` | Printed enclosure design notes |
| `af4_enclosure_ocp.py` | Parametric enclosure source (Python/OCP), with built-in fit checks |
| `aF4-trigger-case.stl/.step`, `aF4-trigger-lid.stl/.step` | Printable enclosure (fits the rev E hat) |
| `aF4-wiring-diagram.svg`, `aF4-system-diagram.svg` | Wiring and system diagrams |
| `pcb/` | KiCad project, generator script, and the PCBWay upload package |
| `aF4-protoboard-layout.svg`, `aF4-protoboard-solder-side.svg` | **Rev C history** — the hand-wired protoboard these describe no longer exists |
| `protoboard 20x20.stl` | Rev C history |

## The board

`pcb/gen_pcb.py` is the source of truth: it generates `af4-trigger-hat.kicad_pcb`
deterministically from named coordinates, taken directly from the Olimex Rev N
KiCad source so the sockets line up by construction. Edit the script, not the
board file, then re-run it and `post.py` (fills the copper pours and runs DRC).

`pcb/af4-trigger-hat-rev-E-PCBWay.zip` is what you upload: Gerbers, drill, BOM,
centroid, fab notes.

## Vendor files (not in repo)

- ESP32-POE-ISO board CAD: [Olimex hardware files](https://github.com/OLIMEX/ESP32-POE-ISO)
- AQY212 PhotoMOS STEP: Panasonic
- aF4 / inD connect product docs: [inD aquatics](https://www.indaquatics.com/products/af4)

## Key trigger rules (inD 0-10V spec)

Feed triggers on ≥9V held ≥15s (inD publishes 6s/10s/15s across three guides — design to the longest); feeds ≥5 min apart; port must see ~0V for >60s to re-arm. Connecting the link port **overrides the aF4's internal 24h schedule** — an offline ESP32 means no feeding at all. Measured OEM dongle trigger voltage 10.37V open-circuit (don't feed raw 12V).
