# aF4 Frozen Feeder — ESP32 PoE Trigger

Replaces the inD connect WiFi dongle on the [inD aquatics aF4](https://www.indaquatics.com/products/af4) refrigerated frozen-food feeder with an Olimex ESP32-POE-ISO running ESPHome, triggering feeds via the aF4's 0-10V port and scheduled from Home Assistant.

## How it works

ESP32-POE-ISO → GPIO32 → 220Ω → AQY212GS PhotoMOS → switches the feeder's own 12V supply (regulated to ~10.4V by an on-board LM1117-ADJ) onto the 3.5mm trigger jack. Safety guardrails (20s pulse, 5-min lockout, restore-off, flash-persisted boot lockout) are baked into the ESPHome config on-device; HA is scheduler only.

**Rev E** puts all of that on a PCB "hat" that plugs onto the ESP32's EXT1/EXT2 headers and carries both panel connectors, assembled by PCBWay. The rev C hand-wired protoboard is retired.

> The trigger pin is **GPIO32**, not GPIO13. The Olimex board has a factory 2.2 kΩ pull-up on GPIO13 that can partially turn the PhotoMOS on during boot. See `docs/aF4-pcb-notes.md`.

## Where to start

| You are | Read |
|---|---|
| **A person, new to this project** | This file, then `STATUS.md` for where it stands, then `aF4-MASTER-REFERENCE.md` §1 and §2 |
| **An AI session** | `.claude/CLAUDE.md`, then `STATUS.md`. **Nothing else by default** — the routing table in `.claude/CLAUDE.md` §7 says where each answer lives |

Three documents are live. `STATUS.md` is the only one that describes current state; it is
rewritten, never appended to. `aF4-MASTER-REFERENCE.md` is the deep record — it carries a
section index and is meant to be grepped by `§N.N`, not read whole. `.claude/CLAUDE.md` holds
the durable facts and the routing table.

## Folder map

| Path | Contents |
|---|---|
| `STATUS.md` | **The only live-status doc.** Phase, what you may trust, open items |
| `aF4-MASTER-REFERENCE.md` | **The record.** Every load-bearing claim tagged with its provenance (measured / datasheet / calculated / asserted). Section-indexed |
| `.claude/CLAUDE.md` | Durable priming for AI sessions + the routing table |
| `docs/` | Subsystem references: feeder spec, PCB notes, BOM, assembly guide, enclosure notes, vendor-doc notes, meter test battery, and `docs/git-rules.md` |
| `firmware/` | `firmware/af4-feeder.yaml` — the ESPHome config as flashed, **source of truth**. `firmware/secrets.yaml` is gitignored |
| `hardware/enclosure/` | `hardware/enclosure/af4_enclosure_ocp.py` (parametric source, self-checking) and its STEP/STL exports; the printable rev E hat stand-in |
| `pcb/` | KiCad project, `pcb/gen_pcb.py` generator, the PCBWay upload package and the order record |
| `reference/diagrams/` | Wiring and system SVGs |
| `reference/vendor/` | Vendor CAD and PDFs — gitignored, not redistributed |
| `archive/` | 🚫 **Not authoritative and not in the read path.** Superseded handoff, the three dated reviews, rev C protoboard history. See `archive/README.md` |

## The board

`pcb/gen_pcb.py` is the source of truth: it generates `pcb/af4-trigger-hat.kicad_pcb`
deterministically from named coordinates, taken directly from the Olimex Rev N
KiCad source so the sockets line up by construction. Edit the script, not the
board file, then re-run it and `pcb/post.py` (fills the copper pours and runs DRC).

`pcb/af4-trigger-hat-rev-E-PCBWay.zip` is what you upload: Gerbers, drill, BOM,
centroid, fab notes.

## Vendor files (not in repo)

- ESP32-POE-ISO board CAD: [Olimex hardware files](https://github.com/OLIMEX/ESP32-POE-ISO)
- AQY212 PhotoMOS STEP: Panasonic
- aF4 / inD connect product docs: [inD aquatics](https://www.indaquatics.com/products/af4)

## Key trigger rules (inD 0-10V spec)

Feed triggers on ≥9V held ≥15s (inD publishes 6s/10s/15s across three guides — design to the longest); feeds ≥5 min apart; port must see ~0V for >60s to re-arm. Connecting the link port **overrides the aF4's internal 24h schedule** — an offline ESP32 means no feeding at all. Measured OEM dongle trigger voltage 10.37V open-circuit (don't feed raw 12V).
