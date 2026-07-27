# aF4 PoE Trigger — Assembly Guide

Build sequence for the ESP32-POE-ISO feeder trigger. Companion docs: `aF4-esp32-trigger-BOM.md` (parts), `aF4-protoboard-layout.svg` (protoboard wiring), `aF4-enclosure-notes.md` (print details), `aF4-reference.md` (feeder specs and measured values).

## 0. Parts and tools check

Everything from the BOM, plus: soldering iron, 22 AWG wire, heatshrink, multimeter, drill with 2.2 mm bit, M2/M3 screwdrivers, hacksaw or Dremel (protoboard cut). No bench supply or pot-setting step — the LM1117's output is fixed by R4/R5, so there is nothing to adjust.

## 1. Print the enclosure

Print `aF4-trigger-case.stl` and `aF4-trigger-lid.stl` in PETG, orientations as exported, no supports. 3 walls, 15–25% infill, 0.2 mm layers. Check that the PG7 gland passes the output-wall hole and the DC-099 jack threads into the input-wall hole (12.2 mm — a light chase with a round file if tight) before proceeding. (The wall pocket beside the channel was for the rev B buck module — now unused; ignore it.)

## 2. Build the protoboard

Cut the protoboard to size (one cut on a 3×7 cm Rindion board → ~30 × 33 mm, or 25 × 25 minimum) and drill the 4 mounting holes to Ø2.2 mm, 6 grid pitches (15.24 mm) apart — they land on existing grid holes matching the case bosses.

Populate per `aF4-protoboard-layout.svg` (component side view, bridges on solder side):

| Ref | Part | Between |
|---|---|---|
| U1 | AQY212GH (DIP-4 socket optional) | straddles the isolation boundary, notch/pin-1 dot toward R1 |
| U2 | LM1117T-ADJ (TO-220, tab up or flat — 24 mW, no heatsink) | 12 V+ column (IN) → 10.4 V rail (OUT); ADJ to the R4/R5 junction |
| R1 | 220 Ω | GPIO13 pad → SSR pin 1 (LED+) |
| R2 | 10 kΩ | GPIO13 net → ESP-GND net (pulldown) |
| R4 | 121 Ω 1% | U2 OUT → U2 ADJ |
| R5 | 887 Ω 1% | U2 ADJ → 12 V− column |
| C1 | 10 µF ≥25 V | U2 IN → 12 V− |
| C2 | 10 µF tantalum/electrolytic ≥16 V (**polarized**, + to rail) | U2 OUT (10.4 V rail) → 12 V− |

(R3, the old 2.2 kΩ buck preload, is deleted — the R4/R5 divider is the regulator's minimum load.)

Wire pads: GPIO13 and ESP-GND on the 3.3 V side; **12 V+ and 12 V− in** on the power side (the regulator now lives on-board, so raw fused 12 V arrives here and 10.4 V is made in place); TIP and SLEEVE exit the edge that will face the output gland. **SLEEVE ties only to the 12 V− strip — never to ESP32 GND.** That gap through the middle of the SSR is the whole isolation design — U2, R4/R5, and C1/C2 all stay on the power side of it.

**Mounting the resistors.** The layout spaces R1/R2 on ideal pitch, but a ¼ W axial body plus bend radius wants 3–4 hole pitches (7.6–10 mm) — more room than the drawing allows on a 9×9 board. Stand them vertically instead: bend one lead 180° at the body shoulder (not at the glass seal — bending too close cracks the end cap) so the footprint drops to a single pitch. Sleeve the bent-back lead so it can't short to the adjacent row, and orient the bands so band 1 reads from the top.

R1 and R2 share the GPIO13 node, so their upper leads tie together. Land that junction **in a board hole**, not as a mid-air splice — the pad gives the joint mechanical support and becomes the landing point for the GPIO13 wire. A dab of hot glue at the resistor bases once the circuit tests good keeps the bends from fatiguing.

Meter each resistor before soldering anyway — but note the old brown/red trap is gone with R3: 220 Ω, 10 kΩ, 121 Ω, and 887 Ω are all comfortably distinct on a meter, and R4/R5 are 1% parts (blue body, 5-band). Swapping R4 and R5 gives ~1.42 V out (feed never triggers) — worth the 10-second meter check.

Check that the tallest standing part clears the lid before committing — board height is fixed by the mounting bosses.

## 3. Prepare the fused input lead

Splice the 100 mA polyfuse (MF-R010) inline into the DC-099 jack's **red (+) pigtail**, heatshrunk — see **detail ①** in `aF4-protoboard-layout.svg`. Cut the + lead only; the black return runs straight through. The PTC has no polarity, but a radial disc has both legs on one edge, so bend one 180° to exit the far side before splicing. Slide the heatshrink onto the wire *before* soldering, shrink each joint, then run a larger sleeve over the whole body. The fuse sits upstream of everything, so it protects the whole chain. Leave the pigtails long enough to reach the protoboard's 12 V+ / 12 V− pads (~120 mm).

(Rev B had a buck-module preparation step here — four fly wires, bench pre-set to 10.40 V under preload, pot lock, wall-pocket install. All deleted: the LM1117 + fixed divider went onto the protoboard in §2 and needs no setup.)

## 4. Wall penetrations & cables

Mount the DC-099 jack in the input wall and the PG7 gland in the output wall, locknuts inside. Feed the 3.5 mm cable's bare end through the gland **before** terminating:

- **Input jack (DC-099):** no feed-through — the splitter's 5.5×2.5 male tap plug connects from outside. Inside, the jack's pre-soldered 18AWG pigtails: red (+, center pin) → polyfuse splice (§3) → protoboard **12 V+** pad; black (−) → protoboard **12 V−** pad. **Meter once before wiring:** plug the splitter in and confirm red = +12 V (center-positive).
- **Output gland:** the 3.5 mm cable. Inside: conductors to the protoboard TIP and SLEEVE pads. Outside: solder the MP3-3501 mono plug (tip = signal, sleeve = ground) and splice the P6KE15CA TVS ~1" behind the plug under heatshrink — one leg to each conductor, either way round (bidirectional, no polarity). See **detail ②** in `aF4-protoboard-layout.svg`.

  Strip a window in each conductor rather than cutting through, wrap a leg around each, solder, then heatshrink each junction separately before sleeving both together. Its 12.8 V standoff sits properly above the 10.4 V line — zero standing leakage — and breakdown from ~14.3 V clamps spikes well below anything the high-impedance port minds.

## 5. Flash the ESP32

**Done 2026-07-18** — flashed via web.esphome.io (USB), then adopted into the ESPHome Device Builder on the Unraid server; updates are OTA (no USB cutout). Config is `af4-feeder.yaml` (source of truth): GPIO13 switch is `internal` with `restore_mode: ALWAYS_OFF`, the `do_feed` script enforces the 10 s pulse + 290 s lockout, and the only exposed control is the "aF4 Feed" button. Verify it comes up on Ethernet before assembly.

## 6. Final assembly

1. Mount the protoboard on its bosses (2 diagonal M2 screws is enough).
2. Drop the ESP32 onto its three standoffs, RJ45 nose into the wall opening; 3× M2 screws.
3. Dupont jumpers from the protoboard's GPIO13/GND wires to the EXT header pins (check the Olimex silkscreen for GPIO13 and GND).
4. Tighten the output gland cap on the 3.5 mm cable.

## 7. Commissioning checks

1. **Continuity before power.** With nothing energised, meter tip↔sleeve with the SSR off: expect open (if you probe the 10.4 V rail to 12 V− instead, ~1.0 kΩ — that's R4+R5, correct). A short at tip↔sleeve means a damaged TVS or a solder bridge at the splice — find it now, not at power-up.
2. **Meter first, feeder later.** With the 3.5 mm plug NOT in the feeder: plug in the splitter, meter tip↔sleeve. Expect 0 V at rest. Then meter the 10.4 V rail (C2 legs): expect **10.3–10.5 V** — this is the regulator check, no adjustment possible or needed; if it's wrong, it's a wiring/orientation error, not drift.
3. Press "aF4 Feed" in HA (or the ESPHome web UI): expect **~10.4 V for 10 s, then 0 V**. Confirm the lockout binary_sensor holds for ~5 min.
4. Power-cycle the ESP32 mid-check once: tip must stay at 0 V through boot (R2 + `ALWAYS_OFF` doing their jobs).
5. Plug into the feeder's 0-10V port — the link icon should light (mechanical detect). Trigger a test feed at a sensible time.
6. Screw the lid (4× M3×12).

## 8. Home Assistant

Already set up (see `aF4-reference.md` → Home Assistant notes): `automation.reef_tank_af4_scheduled_feed` presses `button.af4_feeder_feed` at the helper-set feed times, gated by `input_boolean.reef_af4_schedule_enabled` (leave **off** until step 7 passes) and the lockout sensor. `counter.reef_af4_feeds_today` tracks daily feeds. Never schedule feeds <5 min apart (the device blocks them anyway). Optional: a power-monitoring plug on the feeder supply to infer motor activity — the 0-10V port gives no dispense feedback.

Reminder from the feeder docs: the aF4's internal 24 h timer keeps its own schedule from power-on time; note it or plan around it (open question in `aF4-reference.md`).

## Troubleshooting

- **No trigger:** meter the tip during a button press. 0 V → check SSR orientation (notch toward R1), R1 continuity, GPIO13 jumper on the right header pin. ~10.4 V but no feed → hold time or port re-arm: port needs >60 s at 0 V before it accepts the next trigger, and feeds must be ≥5 min apart.
- **Tip voltage wrong (not ~10.4 V):** the LM1117 can't drift — a wrong reading is a build error. ~1.4 V → R4/R5 swapped. ~12 V → ADJ open (cold joint at the divider junction). 0 V on the rail → polyfuse tripped or C2 reversed/shorted. Oscillation/instability → C2 is a low-ESR ceramic; use tantalum/electrolytic.
- **Voltage sags below 9 V during trigger:** cracked joint on the 10.4 V run, or the polyfuse tripped (check for shorts, let it cool).
- **Link icon dark:** plug not fully seated; the jack's detect switch is mechanical.
- **ESP32 unreachable:** it's PoE — check the switch port budget (802.3af) and that you're on the ISO board's LAN, then OTA via ESPHome dashboard.
