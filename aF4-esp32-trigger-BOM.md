# aF4 PoE Trigger — Parts List

Goal: PoE ESP32 running ESPHome pulses 10.4V (matching measured OEM level) onto the aF4's 3.5mm 0-10V port (≥9V for >6s = feed), scheduled via Home Assistant. Replaces inD connect dongle.

## Core

| Item | Pick | ~Price | Notes |
|---|---|---|---|
| PoE ESP32 board | **Olimex ESP32-POE-ISO** | $28–35 | 3000V galvanic isolation, IEEE 802.3af, first-class ESPHome support. Get the ISO version, not the plain POE. |
| Switching element | **Panasonic AQY212GH PhotoMOS SSR** (DIP-4) + 220Ω resistor | $3 | GPIO drives the internal LED directly — no coil, no flyback diode, no driver transistor. 60V/500mA output, galvanically isolated. Pinout: 1=LED+, 2=LED−, 3/4=output. |
| Protoboard | Generic pad-per-hole FR4 proto PCB, double-sided plated-through, 2.54mm grid, 1.6mm thick (2×8cm pack, cut to ~25×25mm) | $2 | Mounts SSR + LM1117 regulator + resistors/caps per `aF4-protoboard-layout.svg`. Drill out 4 grid holes to Ø2.2mm, 6 pitches (15.24mm) apart — they align with the case bosses; M2 self-tappers. Optional: DIP-4 socket so the SSR is replaceable. |
| 12V DC splitter | Barrel Y-splitter, **5.5×2.5mm, center-positive (confirmed)** | $6 | Taps feeder's 12V. Measured OEM trigger is **10.37V, not 12V** — regulate the tap down (regulator row). Note: many cheap Y-splitters are 5.5×2.1mm — 2.1 seats loosely in 2.5 jacks; buy 2.5mm specifically. Tap lead's male plug connects to the DC-099 panel jack (next row) — no cutting/splicing the splitter. |
| Panel-mount 12V jack | **DALQUIS DC-099 threaded panel-mount jack, 5.5×2.5mm, waterproof cap** (6-pack) | $9 | v6 enclosure: mounts in the input wall (12mm hole) beside the RJ45, replacing the input PG7 gland. Splitter's male tap plug clicks in from outside; pre-soldered 18AWG pigtails inside go to splice ① (polyfuse) → protoboard 12V-in pads. Red = center pin = +12V (center-positive — **verify with meter before wiring**). Rated 50V/5A, plenty for the mA-level tap. |
| 10.4V regulator | **LM1117T-ADJ** linear regulator, TO-220, + fixed divider R4 121Ω / R5 887Ω (both 1%) | $2 | DigiKey `LM1117T-ADJ/NOPB-ND` (TI). Lives **on the protoboard** — no module, no pot, no bench pre-set. Vout = 1.25 × (1 + 887/121) = **10.41V**, set by fixed 1% resistors; correct by construction, can't drift. Divider draws 10.3mA, which alone satisfies the part's worst-case 10mA minimum load — **no preload resistor needed** (old R3 deleted). Dissipation ~24mW at the ~15mW trigger load: no heatsink. Needs C1 10µF in / C2 10µF **tantalum or electrolytic** out (caps row). Replaces the MP1584EN buck module — see `aF4-reference.md` → "10.4V regulator selection" for why. |
| 3.5mm plug | **Same Sky (CUI) MP3-3501**, mono/TS, solder type | $2 | Tip = signal, sleeve = ground. (6VDC rating is nominal audio spec — 10.4V at µA is fine; OEM dongle and Apex cables do the same.) |
| TVS diode | **P6KE15CA** (bidirectional, DO-15) | $5.99/20 | Spliced across the trigger pair **~1" behind the plug**, under heatshrink — the slim MP3-3501 barrel is too cramped for internal mounting. Bidirectional: no orientation. Clamps ESD/inductive spikes after the cable run. Standoff 12.8 V sits properly **above** the 10.4 V line (zero standing leakage); breakdown from ~14.3 V clamps spikes well below anything the high-impedance port cares about. (History: SMAJ12A → P6KE12CA → P6KE15CA. The 12CA's 10.2 V standoff was *below* the working voltage — worked, but wrong side of the rule.) |
| Fuse | **100mA polyfuse** (MF-R010) | $1 | On the 12V tap, upstream of the regulator. Feeder supply can source 12.5A — a short in the enclosure shouldn't dump that into the wiring. Steady draw is only ~15mA, so 100mA hold gives real protection margin; the old 500mA spec (sized for the buck module) needed a dead short to trip. Self-resets. |
| Resistors | R1 220Ω (SSR LED), R2 10kΩ (GPIO13→GND pulldown), R4 121Ω 1% (LM1117 OUT→ADJ), R5 887Ω 1% (LM1117 ADJ→GND) | — | All on the protoboard per `aF4-protoboard-layout.svg`. R2 guarantees the PhotoMOS can't fire during boot/flash (software half: `restore_mode: ALWAYS_OFF`); R4/R5 set the regulator to 10.41V. **R3 (2.2kΩ buck preload) is deleted** — the divider is its own minimum load. R4/R5 are 1% parts with distinct color codes; the old 220Ω-vs-2.2kΩ brown/red trap is gone. |
| Capacitors | C1 10µF ≥25V (reg input), C2 10µF **tantalum or aluminum electrolytic** ≥16V (reg output) | $1 | On the protoboard at the LM1117 pins. C2 must have some ESR — a pure low-ESR ceramic on the output can make the LM1117 oscillate; tantalum or electrolytic is the datasheet-recommended stable choice. C2 is polarized: + to the 10.4V rail. **Ordered as a single part for both positions** — Panasonic ECA-1HM100I, 10µF 50V electrolytic (see DigiKey ordering below). |
| Enclosure | **3D-printed case** (`aF4-trigger-case.stl` + `aF4-trigger-lid.stl`, PETG) + 1× PG7 cable gland (output wall) + DC-099 jack (above) + 4× M3×12 self-tapping screws | ~$2 gland | 59.7 × 155 × 38.9 mm, flush RJ45, dry-location (no gasket). See `aF4-enclosure-notes.md` for print/assembly details. |
| Wire, heatshrink | 22 AWG | — | |

**Total: ~$55–70**

## DigiKey ordering

Two orders. Everything below is the electronics side only — the splitter, DC-099 jack, PG7 gland, screws, and filament come from elsewhere.

**Order 1 (placed 2026-07-11, web ID 373961064)** — the rev A/B core:

| DK part number | Part | Qty | Status |
|---|---|---|---|
| 255-2680-ND | AQY212GH PhotoMOS | 2 | ✅ still current |
| 1188-ESP32-POE-ISO-ND | Olimex ESP32-POE-ISO | 1 | ✅ still current |
| CF14JT220RCT-ND | 220Ω 5% 1/4W (R1) | 10 | ✅ still current |
| CF14JT10K0CT-ND | 10kΩ 5% 1/4W (R2) | 10 | ✅ still current |
| CP3-1005-ND | Same Sky MP3-3501 3.5mm plug | 2 | ✅ still current |
| SMAJ12ALFCT-ND | SMAJ12A TVS | 2 | ⚠️ superseded → P6KE15CA |
| MF-R050-ND | MF-R050 500mA polyfuse | 2 | ⚠️ superseded → MF-R010 |

**Order 2 (cart built 2026-07-26, web ID 374640854)** — rev C delta:

| DK part number | Mfr part | Part | Qty |
|---|---|---|---|
| LM1117T-ADJ/NOPB-ND | TI LM1117T-ADJ/NOPB | LDO regulator, TO-220 (U2) | 2 |
| 2019-MF1/4DCT52R1210FCT-ND | KOA MF1/4DCT52R1210F | 121Ω 1% 1/4W metal film (R4) | 10 |
| 13-MFR-25FBF52-887R-ND | Yageo MFR-25FBF52-887R | 887Ω 1% 1/4W metal film (R5) | 10 |
| P10425CT-ND | Panasonic ECA-1HM100I | 10µF 50V aluminum electrolytic (C1 **and** C2) | 10 |
| MF-R010-ND | Bourns MF-R010 | 100mA polyfuse | 2 |
| P6KE15CALFCT-ND | Littelfuse P6KE15CA | TVS, bidirectional, DO-204AC/DO-15 | 2 |

Sourcing notes:

- **R4 (121Ω):** the obvious Yageo MFR-25FBF52-121R (`121XBK-ND`) is at zero stock with an 18-week factory lead, and its listed substitutes are mostly also dry. The KOA MF1/4DCT52R1210F is the same 121Ω ±1% 0.25W axial metal film, ±100ppm/°C, and is AEC-Q200 rated on top. Same blue 5-band body as R5 — the meter check in `aF4-assembly-guide.md` §2 is unchanged.
- **C1 and C2 are one part.** The Panasonic ECA-1HM100I (10µF, 50V, radial, 2.5mm lead spacing) satisfies both: 50V clears C1's ≥25V input requirement, and being aluminum electrolytic it has the ESR the LM1117 needs on its output, so it's a legal C2 as well. One line item, one bin, no chance of mixing them up. Both are polarized — **+ to the positive rail** in each position.
- **TVS package:** DigiKey lists the Littelfuse P6KE15CA as DO-204AC, which is the same body as DO-15. Correct part for the inline splice behind the 3.5mm plug.

## Alternates for the board

- **wESP32 (Silicognition)** — ~$45, most robust option, 13W isolated PoE output, popular in HA community. Pick if you want extra 5V/12V budget for future sensors.
- **LILYGO T-ETH-Lite + PoE shield** — cheaper, ESP32-S3, but flakier QC and less-proven ESPHome ethernet configs. Budget option.
- **Olimex ESP32-POE2** — newer Olimex, higher power output. Fine, but the ISO is the proven default.

## Is PoE ESP32 right for a 0-10V application?

Yes, with one nuance: no ESP32 board outputs 9–12V natively (GPIO is 3.3V). The board is just brains + network + power. The trigger voltage comes from elsewhere — two clean options:

1. **Recommended — copy the OEM design:** splitter taps the feeder's 12V → polyfuse → LM1117 linear-regulated to 10.4V (matching measured OEM trigger; ~24mW dissipation at this µA-scale load, so a buck buys nothing) → PhotoMOS (driven by ESP32 GPIO) switches it onto the 3.5mm tip. Grounds shared via feeder supply only; ESP32 fully isolated behind the PhotoMOS.
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

Feeder timing rules (10s pulse, 5-min spacing, 0V re-arm) are enforced on-device — HA is scheduler only. Schedule with time-trigger automations pressing `button.af4_feeder_feed`; no HA bug, double-click, or API call can violate the feeder spec. (Concept sketch above — the as-flashed config is `af4-feeder.yaml`, the source of truth.)
