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
- [x] During eWeLink-triggered feed: **10.37V** (dongle regulates below 12V — replicate at ~10.4V; the real requirement is the ≥9V threshold, so anything in roughly 9.5–11V works)
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

ESPHome guardrails (all baked on-device — HA is scheduler only): `restore_mode: ALWAYS_OFF` + `internal: true` on the GPIO switch (HA cannot touch the raw line), `mode: single` feed script with 10s pulse + 290s lockout tail (enforces 5-min spacing and >60s 0V re-arm; re-entrant requests dropped), template button as the sole exposed control, lockout state exposed as a binary_sensor for dashboard/notify. As-flashed YAML: `af4-feeder.yaml` (source of truth); concept sketch in `aF4-esp32-trigger-BOM.md`.

## 10.4V regulator selection

Regulates the feeder's 12V tap down to ~10.4V (matching measured OEM trigger) for the PhotoMOS output.

**Design (rev C, 2026-07-26): LM1117T-ADJ linear regulator, on the protoboard.** DigiKey part, TO-220.

- Vout = 1.25 × (1 + R5/R4) with R4 121Ω 1% (OUT→ADJ) and R5 887Ω 1% (ADJ→GND) = **10.41V**. Fixed resistors — no pot, no bench pre-set, nothing to drift or seal.
- The divider draws 10.3mA, which alone satisfies the LM1117's worst-case 10mA minimum-load spec — the old R3 preload resistor is deleted.
- Dissipation: (12 − 10.4V) × ~15mA ≈ **24mW**. No heatsink. Dropout at 15mA is well under the 1.6V headroom.
- Caps: C1 10µF at IN, C2 10µF **tantalum or aluminum electrolytic** at OUT (the LM1117 wants some output-cap ESR for stability — don't substitute a lone low-ESR ceramic). Both positions are filled by one part in practice: a 10µF 50V aluminum electrolytic clears C1's voltage requirement and gives C2 the ESR it needs.
- Sourcing (2026-07-26): R4's usual Yageo 121Ω (`121XBK-ND`) is at zero stock / 18-week lead; the KOA MF1/4DCT52R1210F is the drop-in equal (121Ω ±1%, 0.25W, axial metal film, ±100ppm/°C, AEC-Q200). Exact DigiKey part numbers for the whole rev C delta are tabulated in `aF4-esp32-trigger-BOM.md` → "DigiKey ordering".
- Isolation: the regulator, divider, and caps all live on the **power side** of the protoboard's isolation gap. Nothing crosses the gap except the SSR.
- Bonus: removes a switching converter from the enclosure entirely (it sat centimeters from the LAN8720 PHY and magnetics).

Key insight: the requirement is a *window*, not a setpoint — the port triggers at **≥9V** and 10.37V is just what the OEM dongle happens to output. Anything ~9.5–11V is correct, which is exactly what a fixed divider delivers forever.

### History: why not a buck module (rev B, abandoned 2026-07-26)

Rev B spec'd an adjustable MP1584EN mini buck module (with Mini-360 clones and fixed-5V boards called out as traps, and an LM2596 board as the bigger alternative). Three Amazon-sourced modules failed in sequence: #1 buzzed (audible pulse-skipping at light load) and died after torque seal was applied to the pot — solvent wicked into the trimmer element; #2 shipped with no adjustment screw; #3's output collapsed to 3.5V as the pot approached 10V (open wiper → FB high → controller folds back).

The underlying problems were structural, not just QC: (a) the load is ~5mA/50mW, far below the "don't run under ~10% load" floor where cheap bucks regulate poorly and drift above setpoint — hence the R3 preload workaround; (b) a multi-turn trimmer is the dominant field-failure part, and it existed only to hit a precision target the port doesn't require. Lesson recorded: **for a fixed-output permanent install, buy the IC and set it with fixed resistors — don't buy a module with a trimpot.** Dropping 1.6V at 5–15mA is a linear regulator's job; a buck's efficiency advantage is irrelevant at 24mW.

(The rev B light-load bleed note remains true in general: any bleed/preload discussion was about the **regulator output**, not the trigger line — the trigger line needs no bleed; rest voltage confirmed 0V, link-detect mechanical.)

## CAD / 3D models (in this folder)

- `ESP32-PoE-ISO_Rev_N.step` / `.stl` — full Olimex ESP32-POE-ISO board model (Rev.N, latest), extracted from the [Olimex KiCad hardware files](https://github.com/OLIMEX/ESP32-POE-ISO): board solid + 124 component models, all through-holes. Board ~28 × 98 mm plus antenna and RJ45 overhang; overall envelope ~29.4 × 112.5 × 25.3 mm. Hole positions verified against factory drill files. Not included: RM1–RM3 resistor arrays (no STEP source). STEP for enclosure CAD, STL for printing/viewing.
- `PAN_AQY21-DIP4_PAN.step` — Panasonic AQY212GH PhotoMOS, DIP-4 package.
- `aF4-trigger-case.stl/.step` + `aF4-trigger-lid.stl/.step` — printed enclosure (PETG, 59.7 × 155 × 38.9 mm): flush RJ45 + DC-099 panel-mount 12V jack (5.5×2.5, takes the splitter's tap plug directly) on the input wall, centered PG7 gland on the output wall, drop-in wall pocket for the MP1584EN buck module (snap post, all pads exposed, pot faces the room), M3×12 self-tapped lid, M2 board/protoboard mounts. Details in `aF4-enclosure-notes.md`; parametric source `af4_enclosure_ocp.py`. (The wall pocket was sized for the rev B MP1584EN buck module — now unused/vestigial; no reprint needed.)
- `aF4-protoboard-layout.svg` — SSR + R1 (220Ω LED), R2 (10kΩ GPIO pulldown), and the rev C regulator block — LM1117T-ADJ (TO-220) + R4/R5 divider + C1/C2 — placement and wiring on the protoboard. Two detail panels below the board drawing show the splices: **①** the 100 mA polyfuse (MF-R010) inline on the +12 V lead, **②** the P6KE15CA TVS (bidirectional) across tip/sleeve ~1" behind the 3.5 mm plug. Step-by-step in `aF4-assembly-guide.md` §2–4.
- `aF4-assembly-guide.md` — full build sequence: print, protoboard build (incl. on-board regulator), wiring, flash, commissioning checks.

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
