# aF4 PoE Trigger — Parts List

Goal: PoE ESP32 running ESPHome pulses 10.4V (matching measured OEM level) onto the aF4's 3.5mm 0-10V port (≥9V for >6s = feed), scheduled via Home Assistant. Replaces inD connect dongle.

## Core

| Item | Pick | ~Price | Notes |
|---|---|---|---|
| PoE ESP32 board | **Olimex ESP32-POE-ISO** | $28–35 | 3000V galvanic isolation, IEEE 802.3af, first-class ESPHome support. Get the ISO version, not the plain POE. |
| Switching element | **Panasonic AQY212GH PhotoMOS SSR** (DIP-4) + 220Ω resistor | $3 | GPIO drives the internal LED directly — no coil, no flyback diode, no driver transistor. 60V/500mA output, galvanically isolated. Pinout: 1=LED+, 2=LED−, 3/4=output. |
| Protoboard | Generic pad-per-hole FR4 proto PCB, double-sided plated-through, 2.54mm grid, 1.6mm thick (2×8cm pack, cut to ~25×25mm) | $2 | Mounts SSR + resistor per `aF4-protoboard-layout.svg`. Drill out 4 grid holes to Ø2.2mm, 6 pitches (15.24mm) apart — they align with the case bosses; M2 self-tappers. Optional: DIP-4 socket so the SSR is replaceable. |
| 12V DC splitter | Barrel Y-splitter, **5.5×2.5mm, center-positive (confirmed)** | $6 | Taps feeder's 12V. Measured OEM trigger is **10.37V, not 12V** — regulate the tap down (buck row). Note: many cheap Y-splitters are 5.5×2.1mm — 2.1 seats loosely in 2.5 jacks; buy 2.5mm specifically. Tap lead's male plug connects to the DC-099 panel jack (next row) — no cutting/splicing the splitter. |
| Panel-mount 12V jack | **DALQUIS DC-099 threaded panel-mount jack, 5.5×2.5mm, waterproof cap** (6-pack) | $9 | v6 enclosure: mounts in the input wall (12mm hole) beside the RJ45, replacing the input PG7 gland. Splitter's male tap plug clicks in from outside; pre-soldered 18AWG pigtails inside go to splice ① (polyfuse) → buck IN. Red = center pin = +12V (center-positive — **verify with meter before wiring**). Rated 50V/5A, plenty for the mA-level tap. |
| 10.4V regulator | Mini adjustable buck module (**EBOOT MP1584EN 3-pack** or equivalent genuine adjustable MP1584EN), set to ~10.4V **before** install | $2–4 | 22×17×4 mm — drops into the case's wall pocket (snap post, no hardware, all pads accessible). Splitter + → polyfuse → buck IN; buck OUT feeds the protoboard. **R3 (2.2kΩ on the protoboard) preloads it ~5mA** so the light-load setpoint holds — set 10.4V on the bench with an equivalent load clipped on. Avoid fixed-5V boards and Mini-360 clones. See `aF4-reference.md` → "10.4V buck regulator selection". |
| 3.5mm plug | **Same Sky (CUI) MP3-3501**, mono/TS, solder type | $2 | Tip = signal, sleeve = ground. (6VDC rating is nominal audio spec — 10.4V at µA is fine; OEM dongle and Apex cables do the same.) |
| TVS diode | **P6KE12CA** (bidirectional, DO-15) | $5.99/20 | Spliced across the trigger pair **~1" behind the plug**, under heatshrink — the slim MP3-3501 barrel is too cramped for internal mounting. Bidirectional: no orientation. Clamps ESD/inductive spikes after the cable run. Standoff 10.2 V is nominally below the 10.4 V line — the µA of leakage is harmless into the high-impedance port, and the lower ~11.4 V breakdown clamps spikes closer to the line. (Originally spec'd SMAJ12A; swapped for leaded package + no polarity.) |
| Fuse | **500mA polyfuse** (MF-R050) or 250–500mA inline fuse | $1 | On the 12V tap, before the buck. Feeder supply can source 12.5A — a short in the enclosure shouldn't dump that into the wiring. Polyfuse self-resets. |
| Resistors | R1 220Ω (SSR LED), R2 10kΩ (GPIO13→GND pulldown), R3 2.2kΩ (buck preload) | — | All three live on the protoboard per `aF4-protoboard-layout.svg`. R2 guarantees the PhotoMOS can't fire during boot/flash (software half: `restore_mode: ALWAYS_OFF`); R3 holds the buck's light-load setpoint. |
| Enclosure | **3D-printed case** (`aF4-trigger-case.stl` + `aF4-trigger-lid.stl`, PETG) + 1× PG7 cable gland (output wall) + DC-099 jack (above) + 4× M3×12 self-tapping screws | ~$2 gland | 59.7 × 155 × 38.9 mm, flush RJ45, dry-location (no gasket). See `aF4-enclosure-notes.md` for print/assembly details. |
| Wire, heatshrink | 22 AWG | — | |

**Total: ~$55–70**

## Alternates for the board

- **wESP32 (Silicognition)** — ~$45, most robust option, 13W isolated PoE output, popular in HA community. Pick if you want extra 5V/12V budget for future sensors.
- **LILYGO T-ETH-Lite + PoE shield** — cheaper, ESP32-S3, but flakier QC and less-proven ESPHome ethernet configs. Budget option.
- **Olimex ESP32-POE2** — newer Olimex, higher power output. Fine, but the ISO is the proven default.

## Is PoE ESP32 right for a 0-10V application?

Yes, with one nuance: no ESP32 board outputs 9–12V natively (GPIO is 3.3V). The board is just brains + network + power. The trigger voltage comes from elsewhere — two clean options:

1. **Recommended — copy the OEM design:** splitter taps the feeder's 12V → polyfuse → buck regulated to 10.4V (matching measured OEM trigger) → PhotoMOS (driven by ESP32 GPIO) switches it onto the 3.5mm tip. Grounds shared via feeder supply only; ESP32 fully isolated behind the PhotoMOS.
2. Boost converter (5V→10V) from the board's 5V rail → MOSFET onto tip. Only needed if you don't want the splitter; more parts, no real benefit.

You do NOT need a true 0-10V DAC — the aF4 treats it as a threshold trigger (≥9V, >6s), not an analog level.

## Verification before wiring (voltmeter, OEM dongle installed)

1. 3.5mm tip↔sleeve at rest: expect ~0V
2. During app-triggered feed: expect ~10–12V; note exact voltage and pulse length
3. Confirm aF4 input doesn't source voltage itself (rules out contact-closure design)
4. Splitter pinout: center-positive 12V

## ESPHome sketch (concept)

```yaml
ethernet:
  type: LAN8720   # ESP32-POE-ISO
  mdc_pin: GPIO23
  mdio_pin: GPIO18
  clk_mode: GPIO17_OUT
  phy_addr: 0
  power_pin: GPIO12

switch:
  - platform: gpio
    pin: GPIO13
    id: feed_ssr
    restore_mode: ALWAYS_OFF
    internal: true          # HA never sees the raw switch

script:
  - id: do_feed
    mode: single            # re-entry ignored while running = hardware lockout
    then:
      - switch.turn_on: feed_ssr
      - delay: 10s          # spec: ≥9V for >6s
      - switch.turn_off: feed_ssr
      - delay: 290s         # lockout tail → 5 min between feeds; also covers >60s 0V re-arm

button:
  - platform: template
    name: "aF4 Feed"
    on_press:
      - script.execute: do_feed

binary_sensor:
  - platform: template
    name: "aF4 Feed Lockout"
    lambda: 'return id(do_feed).is_running();'
```

Feeder timing rules (10s pulse, 5-min spacing, 0V re-arm) are enforced on-device — HA is scheduler only. Schedule with time-trigger automations pressing `button.af4_feed`; no HA bug, double-click, or API call can violate the feeder spec.
