# aF4 Frozen Feeder — Technical Reference

Project: replace the inD connect WiFi dongle with a PoE ESP32 (ESPHome) triggering feeds via the aF4's 0-10V port, scheduled in Home Assistant. See `aF4-esp32-trigger-BOM.md` for parts.

> **Rev D (2026-08-27), relabelled rev E (2026-08-31).** The hand-wired protoboard is retired. The trigger circuit is now a 57 x 50 mm PCB "hat" that plugs onto the ESP32's EXT1/EXT2 headers and carries both panel connectors, assembled by PCBWay. Two things changed that matter beyond packaging: the trigger moved from **GPIO13 to GPIO32** (the Olimex board has a factory 2.2 k pull-up on GPIO13 that can partially turn the PhotoMOS on during boot), and the input gained **reverse-polarity protection**, which rev C did not have. Design decisions, the part-by-part equivalence review and the PCBWay procedure live in `aF4-pcb-notes.md`. Everything below about the *feeder* — port spec, measured values, the regulator maths — is unchanged and still governs.

## System components

**aF4 feeder** ($549.99) — refrigerated frozen-food feeder. 200mL / ~50 cube capacity, operating temp -1C to 5C, max ambient 29C/85F. Rinses feed tubes between feeds. Powered by **12V 12.5A** external supply. Stays powered continuously (it's a fridge — do not power cycle for scheduling).

**inD connect** ($69.99) — OEM WiFi accessory. Contents: power supply splitter cable + WiFi relay module (eWeLink-based, almost certainly ESP8266/Sonoff-class) + setup card. Uses the eWeLink app. It does **not** power cycle the feeder — the splitter taps the 12V supply and the relay switches voltage onto the 0-10V trigger port.

## Feed scheduling — two independent mechanisms

1. **Internal 24h timer** — feeds every 24h at the power-on time. First automatic feed occurs 24h after initial power-up. Adjustable only via front-panel Feed Time Offset buttons: -4/-2/0/+2/+4 (hours).
2. **0-10V trigger port** — external trigger, unlimited feeds (subject to rules below). This is what the connect dongle, Apex/Hydros/Profilux, and our ESP32 use.

Open question: whether the internal 24h schedule keeps running while using external triggering (assume yes — plan schedules accordingly or note the power-on time).

## 0-10V trigger port spec (3.5mm jack)

Official rules, re-derived from inD's help centre 2026-09-01:

- Feed triggers on **≥9V held for ≥15 seconds** `[VENDOR]` — design figure; see the conflict note below
- Feed cycles must be **≥5 minutes apart** `[VENDOR]`
- Port must see **~0V for >60 seconds** before it re-arms `[SPEC]`
- **Connecting the link port completely overrides the aF4's internal 24h schedule** `[VENDOR]` — so an offline ESP32 means the fish are silently never fed
- The "link" icon illuminates when a controller is connected, and **flashes green when a feed signal is accepted** (newer units)
- Feed **quantity is set on the aF4 only** and cannot be driven over the link

⚠️ **inD publishes three different hold times.** The ">6 seconds" here was quoted verbatim
from inD's Neptune Systems page and audit-verified 2026-08-28 — it is genuine. But the inD
Connect guide says **10 s** and the Coralvue Hydros guide says **15 s**, and the current
Neptune Apex article states none at all. **Design to the longest: 15 s.**

Implications for ESPHome: pulse ON for **20s** (not 10s — 10s has no margin against 15s),
then ensure OFF ≥60s; never schedule feeds <5 min apart.

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
| Pulse duration | n/a — eWeLink has no pulse mode, just on/off (scheduled on time + off time). Our ESPHome pulses 20s (see the three-way hold-time conflict above). |
| aF4 self-sourced voltage | n/a — link detect is mechanical (jack insertion switch) |
| Barrel size / polarity | 5.5×2.5mm, center-positive |

## Replacement design (summary)

Olimex ESP32-POE-ISO → GPIO32 → 220Ω → **AQY212GS PhotoMOS** (pin 1 LED+, pin 2 LED− to GND) → output pins 3/4 switch the feeder's own 12V (via barrel splitter) onto the 3.5mm tip; sleeve to supply GND. (Rev C used GPIO13 and the DIP AQY212GH; see the rev D note above.) ESP32 fully isolated behind the PhotoMOS; PoE isolated from Ethernet (3000V). HA automations press an ESPHome template button (ON 20s → OFF). See `aF4-wiring-diagram.svg`.

ESPHome guardrails (all baked on-device — HA is scheduler only): `restore_mode: ALWAYS_OFF` + `internal: true` on the GPIO switch (HA cannot touch the raw line), `mode: single` feed script with 20s pulse + 290s lockout tail (a 310s cycle — enforces 5-min spacing and >60s 0V re-arm with margin; re-entrant requests dropped), a **flash-persisted `feed_in_flight` flag** so a reboot mid-cycle serves a 300s recovery lockout instead of silently clearing it, template button as the sole exposed control, lockout state exposed as a binary_sensor for dashboard/notify, and `web_server: auth:` on the local control page. As-committed YAML: `af4-feeder.yaml` (source of truth). ⚠️ **Not yet flashed** — the running device is still the GPIO13 / 10s build; concept sketch in `aF4-esp32-trigger-BOM.md`.

## 10.4V regulator selection

Regulates the feeder's 12V tap down to ~10.4V (matching measured OEM trigger) for the PhotoMOS output.

**Design: LM1117-ADJ linear regulator, on the trigger board.** Rev C used the TO-220 `LM1117T-ADJ`; rev D uses the SOT-223 `LM1117MPX-ADJ/NOPB` — same die, same datasheet, and the pin-crossing problem below disappears because the SMD footprint puts ADJ where ADJ goes. The divider maths is identical.

- Vout = 1.25 × (1 + R5/R4) with R4 121Ω 1% (OUT→ADJ) and R5 887Ω 1% (ADJ→GND) = 10.41V, plus I_ADJ × R5 (60µA × 887Ω ≈ 53mV) = **~10.46V measured**. Fixed resistors — no pot, no bench pre-set, nothing to drift or seal.
- The divider draws 10.4mA on its own, comfortably above the LM1117-ADJ's **5mA worst-case minimum load** (TI SNOS412Q: 1.7mA typ at 25°C, 5mA over 0–125°C) — the old R3 preload resistor is deleted. Rev D adds the D3 indicator branch (R6 1.0kΩ, 8.3mA), so total quiescent load on the 10.4V rail is **~18.6mA**, rising to ~19.9mA during a feed (R3 bleed 0.1mA + D5 1.2mA). The divider alone still carries the minimum-load requirement; D3 is not relied on for it.
- Dissipation: with the SS14 dropping ~0.35V at this current, U2 sees ~11.65V in, so (11.65 − 10.46V) × 18.6mA ≈ **22mW** (~24mW during a feed). No heatsink. Note the -ADJ part has no ground pin, so there is no separate quiescent-current loss term — the only current leaving besides the load is I_ADJ. (DigiKey's parametric "Iq 5mA" is the *fixed*-output versions' ground-pin current and does not apply here.) Dropout at ~10mA is well under the 1.6V headroom.
- Pinout (TO-220, TI SNOS412Q Table 6-1): **1 = ADJ, 2 = VOUT and TAB, 3 = VIN.** The protoboard pads run top→bottom IN, ADJ, OUT, so the leads fan out of line and **pin 1 crosses pin 2** — sleeve pin 1. A bare crossing shorts ADJ to OUT and pushes the rail to ~12V. See `aF4-assembly-guide.md` §2.
- Caps: C1 10µF at IN, C2 10µF **tantalum** at OUT. TI SNOS412Q requires ≥10µF with **ESR between 0.3Ω and 22Ω** on the output and names a tantalum explicitly — don't substitute a lone low-ESR ceramic. The Kemet T491B106K025AT is ~2Ω, inside that window. (Rev C filled both positions with a single 10µF 50V aluminum electrolytic; rev D splits them — C1 is a 1206 ceramic, which is fine at the input, and C2 stays tantalum.)
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
- `aF4-trigger-case.stl/.step` + `aF4-trigger-lid.stl/.step` — printed enclosure, **rev D** (PETG, 65.2 x 117.0 x 38.4 mm): flush RJ45 on the input wall; the trigger hat's barrel jack and 3.5 mm jack exit one long wall; two tall standoffs carry the hat; four light-pipe LED sight holes in the lid (D3, D5 on the hat; PWR1, LNK1 on the Olimex board). The rev C protoboard bay, buck pocket, DC-099 hole and PG7 gland are all gone. Details in `aF4-enclosure-notes.md`; parametric source `af4_enclosure_ocp.py`, which asserts its own fit checks before exporting.
- `aF4-protoboard-layout.svg`, `aF4-protoboard-solder-side.svg` — **rev C history.** They describe the hand-wired protoboard, which rev D replaces with a PCB. Kept for the record; do not build from them.
- `pcb/` — rev E KiCad project, the generator script that produces it, and the PCBWay upload package. See `aF4-pcb-notes.md`.
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
| `automation.reef_tank_af4_scheduled_feed` | Scheduler **and** per-feed confirmation — see below |
| `automation.reef_tank_feeder_health_watchdog` | Silent-failure backstop, shared with the Plank feeder |

**The scheduled-feed automation is more than a button press** (read from HA
2026-09-02; this table used to claim otherwise). It checks two interlocks before
pressing — the feeder lockout must be `off`, **and the sump return pump must be
running**, because the feeder discharges into the sump and without the return the
food never reaches the display. After pressing it waits up to 15 s for the lockout
to go `on`; since the press only happens while the lockout is `off`, that
transition is proof the pulse started. **The counter increments only on that
confirmation**, so a press lost in transit cannot log a phantom feed and blind the
watchdog. Both failure paths send a phone notification naming the interlock.

**`automation.reef_tank_feeder_health_watchdog`** is the backstop: a 23:45 check
comparing the counter against how many feed times have actually elapsed today
(computed from the `input_datetime` helpers, so editing a feed time cannot
false-alarm), plus an alert when the board is offline 15+ minutes with the
schedule enabled. 23:45 is late enough for any plausible feed time and early
enough to beat the midnight counter reset.

Feed counting is deliberately in HA, not on-device: the counter survives ESP32
reboots and reuses the existing nightly reset. The lockout condition does double
duty — `off` means the device is reachable *and* outside its 5-minute lockout, so
an offline ESP32 skips the feed instead of firing a press into the void; offline
reads `unavailable`, which fails the check correctly.

Networking: the board pulled a new DHCP lease after flashing (.230 → .55),
which broke HA's cached discovery with `Errno 113`. Fixed 2026-07-18: Ethernet
MAC `20:E7:C8:74:A6:D7` reserved at 192.168.1.55 in OPNsense dnsmasq (host
override `af4-feeder`, no client identifier — MAC match only).

- Feeder has no feedback channel — the 0-10V port is input-only. Everything above confirms the pulse was *sent*, never that food came out. The case that matters is an over-temperature fault: it stops the feeder, **never self-clears**, and is invisible to HA — the ESP32 would pulse, the lockout would assert, the counter would increment and the watchdog would stay quiet. A power-monitoring smart plug on the 12V supply is the only way to infer real feed-motor activity short of opening the unit

## Sources

- [aF4 product page](https://www.indaquatics.com/products/af4)
- [0-10V Setup Guide: Neptune Systems](https://www.indaquatics.com/pages/0-10v-setup-guide-neptune-systems) — trigger rules
- [0-10V Setup Guide: Hydros](https://www.indaquatics.com/pages/0-10v-setup-guide-coralvue-hydros)
- [inD connect product page](https://www.indaquatics.com/collections/af4-accessories) — see `inD connect.pdf` in this folder
- Manual page photo (feed time offset) — conversation, 2026-07-10
