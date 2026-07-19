# aF4 Frozen Feeder — Technical Reference

Project: replace the inD connect WiFi dongle with a PoE ESP32 (ESPHome) triggering feeds via the aF4's 0-10V port, scheduled in Home Assistant. See `aF4-esp32-trigger-BOM.md` for parts.

## System components

**aF4 feeder** ($549.99) — refrigerated frozen-food feeder. 200mL / ~50 cube capacity, operating temp -1C to 5C, max ambient 29C/85F. Rinses feed tubes between feeds. Powered by **12V 12.5A** external supply. Stays powered continuously (it's a fridge — do not power cycle for scheduling).

**inD connect** ($69.99) — OEM WiFi accessory. Contents: power supply splitter cable + WiFi relay module (eWeLink-based, almost certainly ESP8266/Sonoff-class) + setup card. Uses the eWeLink app. It does **not** power cycle the feeder — the splitter taps the 12V supply and the relay switches voltage onto the 0-10V trigger port.

## Feed scheduling — two independent mechanisms

1. **Internal 24h timer** — feeds every 24h at the power-on time. First automatic feed occurs 24h after initial power-up. Adjustable only via front-panel Feed Time Offset buttons: -4/-2/0/+2/+4 (hours).
2. **0-10V trigger port** — external trigger, unlimited feeds (subject to rules below). This is what the connect dongle, Apex/Hydros/Profilux, and our ESP32 use.

Open question: whether the internal 24h schedule keeps running while using external triggering (assume yes — plan schedules accordingly or note the power-on time).

## 0-10V trigger port spec (3.5mm jack)

Official rules (inD Neptune guide):

- Feed triggers on **≥9V held for >6 seconds**
- Port must see **~0V for >60 seconds** before it will re-arm for the next trigger
- Feed cycles must be **≥5 minutes apart**
- The "link" icon (top-right of aF4) illuminates when a controller is connected to the port

Implications for ESPHome: pulse ON for ~10s, then ensure OFF ≥60s (trivially satisfied by any sane schedule); never schedule feeds <5 min apart.

Assumed pinout (verify): tip = signal (+9-12V), sleeve = ground. Mono/TS sufficient.

## Verification checklist (voltmeter, OEM dongle)

- [x] 3.5mm tip↔sleeve at rest: **0V confirmed**
- [x] During eWeLink-triggered feed: **10.37V** (dongle regulates below 12V — replicate with buck at ~10.4V)
- [x] Link-detect mechanism: **CONFIRMED mechanical (2026-07-10)** — bare plug with nothing attached lights the link icon. Jack insertion switch; no electrical sensing. No bleed resistor needed on the PhotoMOS output (rest voltage confirmed 0V).
- [x] Splitter cable: **5.5×2.5mm barrel, center-positive, confirmed 2026-07-10**
- [ ] Confirm internal 24h schedule behavior while dongle connected

Record results here:

| Measurement | Value (measured 2026-07-10) |
|---|---|
| Rest voltage | 0V |
| Trigger voltage | **10.37V** — NOT raw 12V; dongle regulates/drops. Replicate ~10.4V, don't feed 12V direct. |
| Pulse duration | n/a — eWeLink has no pulse mode, just on/off (scheduled on time + off time). Our ESPHome will pulse 10s per Neptune rules. |
| aF4 self-sourced voltage | n/a — link detect is mechanical (jack insertion switch) |
| Barrel size / polarity | 5.5×2.5mm, center-positive |

## Replacement design (summary)

Olimex ESP32-POE-ISO → GPIO13 → 220Ω → **AQY212GH PhotoMOS** (pin 1 LED+, pin 2 LED− to GND) → output pins 3/4 switch the feeder's own 12V (via barrel splitter) onto the 3.5mm tip; sleeve to supply GND. ESP32 fully isolated behind the PhotoMOS; PoE isolated from Ethernet (3000V). HA automations press an ESPHome template button (ON 10s → OFF). See `aF4-wiring-diagram.svg`.

ESPHome guardrails (all baked on-device — HA is scheduler only): `restore_mode: ALWAYS_OFF` + `internal: true` on the GPIO switch (HA cannot touch the raw line), `mode: single` feed script with 10s pulse + 290s lockout tail (enforces 5-min spacing and >60s 0V re-arm; re-entrant requests dropped), template button as the sole exposed control, lockout state exposed as a binary_sensor for dashboard/notify. Full YAML in `aF4-esp32-trigger-BOM.md`.

## 10.4V buck regulator selection

Regulates the feeder's 12V tap down to ~10.4V (matching measured OEM trigger) for the PhotoMOS output. Not a DigiKey part — source from Amazon/AliExpress.

- **Pick: genuine adjustable MP1584EN mini module** (e.g. EBOOT MP1584EN, 4.4★/1.3K reviews). Continuously adjustable, spec **0.8–20V out** — 10.4V is mid-range. The listing titles ("24V to 12V 9V 5V 3V") just list example outputs; it is NOT stepped. ~22×17mm, fits the case better than an LM2596 board (~43×21mm).
- **Avoid** the fixed-output MP1584EN "5V" boards (can't be set to 10.4V), and no-name **Mini-360** clones (heavily counterfeited MP2307, poor/ drifting regulation).
- LM2596-with-voltmeter-display is a valid alternative — lets you dial 10.4V by eye without a meter — but is physically bigger.

**Light-load caveat (matters here).** The aF4 0-10V input is high-impedance (trigger draws well under 1mA), so the module runs at a few mW — far below the "don't run under ~10% load / no load" warning on these buck boards. At near-zero load, cheap bucks regulate poorly and the output can creep above setpoint. Two fixes (either works):
1. Set 10.4V **with the real load (or a stand-in) connected**, not on an unloaded bench — measure what it actually outputs in service.
2. Add a small permanent **bleed/preload resistor across the buck output** (~2.2kΩ, ≈5mA / ~50mW) so the setpoint holds and it can't overshoot.

Note: this bleed is on the **buck output (regulation)**, a different point from the trigger line — the trigger line needs no bleed (rest voltage confirmed 0V, link-detect is mechanical; see verification checklist). For a threshold trigger a little upward drift is harmless (needs only ≥9V), so this is about setpoint repeatability, not a dealbreaker.

## CAD / 3D models (in this folder)

- `ESP32-PoE-ISO_Rev_N.step` / `.stl` — full Olimex ESP32-POE-ISO board model (Rev.N, latest), extracted from the [Olimex KiCad hardware files](https://github.com/OLIMEX/ESP32-POE-ISO): board solid + 124 component models, all through-holes. Board ~28 × 98 mm plus antenna and RJ45 overhang; overall envelope ~29.4 × 112.5 × 25.3 mm. Hole positions verified against factory drill files. Not included: RM1–RM3 resistor arrays (no STEP source). STEP for enclosure CAD, STL for printing/viewing.
- `PAN_AQY21-DIP4_PAN.step` — Panasonic AQY212GH PhotoMOS, DIP-4 package.
- `aF4-trigger-case.stl/.step` + `aF4-trigger-lid.stl/.step` — printed enclosure (PETG, 51.7 × 155 × 38.9 mm): flush RJ45 + PG7 gland on the input wall, centered PG7 on the output wall, drop-in wall pocket for the MP1584EN buck module (snap post, all pads exposed, pot faces the room), M3×12 self-tapped lid, M2 board/protoboard mounts. Details in `aF4-enclosure-notes.md`; parametric source `af4_enclosure_ocp.py`.
- `aF4-protoboard-layout.svg` — SSR + R1 (220Ω LED), R2 (10kΩ GPIO pulldown), R3 (2.2kΩ buck preload) placement and wiring on the 25×25 mm protoboard; off-board polyfuse/buck/TVS chain noted in the rev B panel. Two detail panels below the board drawing show the splices: **①** the 500 mA polyfuse inline on the +12 V lead, **②** the P6KE12CA TVS (bidirectional) across tip/sleeve ~1" behind the 3.5 mm plug. Step-by-step in `aF4-assembly-guide.md` §3–4.
- `aF4-assembly-guide.md` — full build sequence: print, protoboard build, buck setup, wiring, flash, commissioning checks.

## Home Assistant notes

Device adopted 2026-07-18. Config in `af4-feeder.yaml`; built on the ESPHome
container on the Unraid server (port 6052), not an HA add-on.

**Entities (ESPHome):** `button.af4_feeder_feed` (sole control),
`binary_sensor.af4_feeder_feed_lockout`, `binary_sensor.af4_feeder_status`
(connectivity, for the Reef Command dashboard), `sensor.af4_feeder_ip_address`,
`sensor.af4_feeder_uptime`, `button.af4_feeder_restart`.

Build/flash workflow: `af4-feeder.yaml` in this folder is the **source of
truth**. The ESPHome Device Builder (Docker on the Unraid server, port 6052)
holds its own copy — paste changes there manually, then Install → Wirelessly.
First flash was USB via web.esphome.io (factory .bin); everything since is OTA
(enclosure has no USB cutout). IP 192.168.1.55 reserved in OPNsense dnsmasq
against Ethernet MAC `20:E7:C8:74:A6:D7`.

**Helpers + automation (HA):**

| Entity | Role |
|---|---|
| `input_boolean.reef_af4_schedule_enabled` | Master kill switch for scheduled feeds |
| `input_datetime.reef_af4_feed_time_1` / `_2` | Feed times (default 09:00 / 17:00) |
| `counter.reef_af4_feeds_today` | Daily count; reset by `automation.reef_tank_reset_ato_counter_daily` |
| `sensor.reef_af4_next_feed` | Template; reads `unknown` while the schedule toggle is off (expected) |
| `automation.reef_tank_af4_scheduled_feed` | Presses the button at each feed time |

Feed counting is deliberately in HA, not on-device: the counter survives ESP32
reboots and reuses the existing nightly reset. The automation's lockout
condition does double duty — `off` means the device is reachable *and* outside
its 5-minute lockout, so an offline ESP32 skips the feed instead of firing a
press into the void.

Networking: the board pulled a new DHCP lease after flashing (.230 → .55),
which broke HA's cached discovery with `Errno 113`. Fixed 2026-07-18: Ethernet
MAC `20:E7:C8:74:A6:D7` reserved at 192.168.1.55 in OPNsense dnsmasq (host
override `af4-feeder`, no client identifier — MAC match only).

- Feeder has no feedback channel — the 0-10V port is input-only. Confirmation of an actual dispense isn't available electrically; a power-monitoring smart plug on the 12V supply could infer feed motor activity if desired

## Sources

- [aF4 product page](https://www.indaquatics.com/products/af4)
- [0-10V Setup Guide: Neptune Systems](https://www.indaquatics.com/pages/0-10v-setup-guide-neptune-systems) — trigger rules
- [0-10V Setup Guide: Hydros](https://www.indaquatics.com/pages/0-10v-setup-guide-coralvue-hydros)
- [inD connect product page](https://www.indaquatics.com/collections/af4-accessories) — see `inD connect.pdf` in this folder
- Manual page photo (feed time offset) — conversation, 2026-07-10
