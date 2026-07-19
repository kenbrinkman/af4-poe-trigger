# aF4 PoE Trigger — Assembly Guide

Build sequence for the ESP32-POE-ISO feeder trigger. Companion docs: `aF4-esp32-trigger-BOM.md` (parts), `aF4-protoboard-layout.svg` (protoboard wiring), `aF4-enclosure-notes.md` (print details), `aF4-reference.md` (feeder specs and measured values).

## 0. Parts and tools check

Everything from the BOM, plus: soldering iron, 22 AWG wire, heatshrink, multimeter, small flat screwdriver (buck pot), drill with 2.2 mm bit, M2/M3 screwdrivers, hacksaw or Dremel (protoboard cut). A bench 12 V supply is handy for setting the buck but not required — the feeder's supply works via the splitter.

## 1. Print the enclosure

Print `aF4-trigger-case.stl` and `aF4-trigger-lid.stl` in PETG, orientations as exported, no supports. 3 walls, 15–25% infill, 0.2 mm layers. Check that a PG7 gland passes both wall holes and the buck module slides into the wall slot before proceeding (a light filing of the slot groove is fine).

## 2. Build the protoboard

Cut the protoboard to size (one cut on a 3×7 cm Rindion board → ~30 × 33 mm, or 25 × 25 minimum) and drill the 4 mounting holes to Ø2.2 mm, 6 grid pitches (15.24 mm) apart — they land on existing grid holes matching the case bosses.

Populate per `aF4-protoboard-layout.svg` (component side view, bridges on solder side):

| Ref | Part | Between |
|---|---|---|
| U1 | AQY212GH (DIP-4 socket optional) | straddles the isolation boundary, notch/pin-1 dot toward R1 |
| R1 | 220 Ω | GPIO13 pad → SSR pin 1 (LED+) |
| R2 | 10 kΩ | GPIO13 net → ESP-GND net (pulldown) |
| R3 | 2.2 kΩ | 10.4 V column → 12 V− column (buck preload) |

Wire pads: GPIO13 and ESP-GND on the 3.3 V side; 10.4 V-in and 12 V− on the power side; TIP and SLEEVE exit the edge that will face the output gland. **SLEEVE ties only to the 12 V− strip — never to ESP32 GND.** That gap through the middle of the SSR is the whole isolation design.

**Mounting the resistors.** The layout spaces R1/R2 on ideal pitch, but a ¼ W axial body plus bend radius wants 3–4 hole pitches (7.6–10 mm) — more room than the drawing allows on a 9×9 board. Stand them vertically instead: bend one lead 180° at the body shoulder (not at the glass seal — bending too close cracks the end cap) so the footprint drops to a single pitch. Sleeve the bent-back lead so it can't short to the adjacent row, and orient the bands so band 1 reads from the top.

R1 and R2 share the GPIO13 node, so their upper leads tie together. Land that junction **in a board hole**, not as a mid-air splice — the pad gives the joint mechanical support and becomes the landing point for the GPIO13 wire. A dab of hot glue at the resistor bases once the circuit tests good keeps the bends from fatiguing.

Meter each resistor before soldering. 220 Ω is red-red-**brown** and 2.2 kΩ is red-red-**red** — one band apart, and brown vs. red is the hardest pair to call under warm light. 2.2 k in the R1 slot starves the SSR LED; 220 Ω in the R3 slot pulls ~47 mA off the buck instead of ~5 mA.

Check that the tallest standing part clears the lid before committing — board height is fixed by the mounting bosses.

## 3. Prepare the buck module

1. Solder four wires to the MP1584EN corners: IN+ , IN−, OUT+, OUT−. Keep IN leads long enough to reach the input gland area (~120 mm), OUT leads ~80 mm.
2. Splice the 500 mA polyfuse inline into the IN+ lead, heatshrunk — see **detail ①** in `aF4-protoboard-layout.svg`. Cut IN+ only; the return lead runs straight through. The PTC has no polarity, but a radial disc has both legs on one edge, so bend one 180° to exit the far side before splicing. Slide the heatshrink onto the wire *before* soldering, shrink each joint, then run a larger sleeve over the whole body. The fuse sits upstream of the buck so it protects the entire chain.
3. Power IN+ / IN− from 12 V (bench supply, or the feeder splitter later), clip a spare ~2.2 kΩ across OUT, and set the pot to **10.40 V** (clockwise = down). The preload matters — unloaded, these modules read high. Multi-turn pots need many revolutions; go slow near target. Once set, lock the pot with a dab of nail polish or hot glue — vibration and thermal cycling walk them.
4. Drop the module into the wall pocket, flat back against the wall, **components/pot facing the room** — push down until the front post's nub snaps over the top. Wires can be soldered at all four corner pads before or after; every pad stays accessible in the pocket.

## 4. Cables through glands

Thread both PG7 glands into the walls, locknuts inside. Feed the bare ends through **before** terminating:

- **Input gland:** the 12 V splitter tap cable (5.5×2.5 mm center-positive Y-splitter). Inside: + → polyfuse → buck IN+; − → buck IN−.
- **Output gland:** the 3.5 mm cable. Inside: conductors to the protoboard TIP and SLEEVE pads. Outside: solder the MP3-3501 mono plug (tip = signal, sleeve = ground) and splice the P6KE12CA TVS ~1" behind the plug under heatshrink — one leg to each conductor, either way round (bidirectional, no polarity). See **detail ②** in `aF4-protoboard-layout.svg`.

  Strip a window in each conductor rather than cutting through, wrap a leg around each, solder, then heatshrink each junction separately before sleeving both together. Its 10.2 V standoff sits nominally under the 10.4 V line — the resulting µA-scale leakage is harmless into the high-impedance trigger port, and breakdown from ~11.4 V clamps spikes close to the line.

Then: buck OUT+ → protoboard "10.4V in" pad, buck OUT− → protoboard "12V−" pad.

## 5. Flash the ESP32

Before it goes in the case (no USB cutout — OTA afterwards). Flash the ESPHome config from `aF4-esp32-trigger-BOM.md`: GPIO13 switch is `internal` with `restore_mode: ALWAYS_OFF`, the `do_feed` script enforces the 10 s pulse + 290 s lockout, and the only exposed control is the "aF4 Feed" button. Verify it comes up on Ethernet before assembly.

## 6. Final assembly

1. Mount the protoboard on its bosses (2 diagonal M2 screws is enough).
2. Drop the ESP32 onto its three standoffs, RJ45 nose into the wall opening; 3× M2 screws.
3. Dupont jumpers from the protoboard's GPIO13/GND wires to the EXT header pins (check the Olimex silkscreen for GPIO13 and GND).
4. Tighten both gland caps on the cables.

## 7. Commissioning checks

1. **Continuity before power.** With nothing energised, meter tip↔sleeve with the SSR off: expect open (or ~2.2 kΩ if you're reading across the buck side). A short here means a damaged TVS or a solder bridge at the splice — find it now, not at power-up.
2. **Meter first, feeder later.** With the 3.5 mm plug NOT in the feeder: plug in the splitter, meter tip↔sleeve. Expect 0 V at rest.
3. Press "aF4 Feed" in HA (or the ESPHome web UI): expect **~10.4 V for 10 s, then 0 V**. Confirm the lockout binary_sensor holds for ~5 min.
4. Power-cycle the ESP32 mid-check once: tip must stay at 0 V through boot (R2 + `ALWAYS_OFF` doing their jobs).
5. Plug into the feeder's 0-10V port — the link icon should light (mechanical detect). Trigger a test feed at a sensible time.
6. Screw the lid (4× M3×12).

## 8. Home Assistant

Time-trigger automations press `button.af4_feed`. Never schedule feeds <5 min apart (the device blocks them anyway). Optional: counter for daily feeds, notification on trigger, and a power-monitoring plug on the feeder supply to infer motor activity — the 0-10V port gives no dispense feedback.

Reminder from the feeder docs: the aF4's internal 24 h timer keeps its own schedule from power-on time; note it or plan around it (open question in `aF4-reference.md`).

## Troubleshooting

- **No trigger:** meter the tip during a button press. 0 V → check SSR orientation (notch toward R1), R1 continuity, GPIO13 jumper on the right header pin. ~10.4 V but no feed → hold time or port re-arm: port needs >60 s at 0 V before it accepts the next trigger, and feeds must be ≥5 min apart.
- **Voltage above ~10.5 V at the tip:** buck drifting under light load — confirm R3 is populated; re-set the pot in place.
- **Voltage sags below 9 V during trigger:** cracked joint on the 10.4 V run, or the polyfuse tripped (check for shorts, let it cool).
- **Link icon dark:** plug not fully seated; the jack's detect switch is mechanical.
- **ESP32 unreachable:** it's PoE — check the switch port budget (802.3af) and that you're on the ISO board's LAN, then OTA via ESPHome dashboard.
