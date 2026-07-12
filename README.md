# aF4 Frozen Feeder — ESP32 PoE Trigger

Replaces the inD connect WiFi dongle on the [inD aquatics aF4](https://www.indaquatics.com/products/af4) refrigerated frozen-food feeder with an Olimex ESP32-POE-ISO running ESPHome, triggering feeds via the aF4's 0-10V port and scheduled from Home Assistant.

## How it works

ESP32-POE-ISO → GPIO13 → 220Ω → AQY212GH PhotoMOS → switches the feeder's own 12V supply (regulated to ~10.4V by an MP1584EN buck) onto the 3.5mm trigger jack. Safety guardrails (10s pulse, 5-min lockout, restore-off) are baked into the ESPHome config on-device; HA is scheduler only.

## Contents

| File | Purpose |
|---|---|
| `aF4-reference.md` | Technical reference: trigger port spec, measurements, design rationale |
| `aF4-esp32-trigger-BOM.md` | Parts list + full ESPHome YAML |
| `aF4-assembly-guide.md` | Build sequence: print, solder, wire, flash, commission |
| `aF4-enclosure-notes.md` | Printed enclosure design notes |
| `af4_enclosure_ocp.py` | Parametric enclosure source (build123d/OCP) |
| `aF4-trigger-case.stl/.step`, `aF4-trigger-lid.stl/.step` | Printable enclosure |
| `aF4-wiring-diagram.svg`, `aF4-system-diagram.svg` | Wiring and system diagrams |
| `aF4-protoboard-layout.svg`, `aF4-protoboard-solder-side.svg` | 25×25mm protoboard layout |
| `protoboard 20x20.stl` | Protoboard model |

## Vendor files (not in repo)

- ESP32-POE-ISO board CAD: [Olimex hardware files](https://github.com/OLIMEX/ESP32-POE-ISO)
- AQY212GH PhotoMOS STEP: Panasonic
- aF4 / inD connect product docs: [inD aquatics](https://www.indaquatics.com/products/af4)

## Key trigger rules (inD 0-10V spec)

Feed triggers on ≥9V held >6s; port must see ~0V for >60s to re-arm; feeds ≥5 min apart. Measured OEM dongle trigger voltage: 10.37V (don't feed raw 12V).
