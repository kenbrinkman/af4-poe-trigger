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

## 3. Prepare the buck module

1. Solder four wires to the MP1584EN corners: IN+ , IN−, OUT+, OUT−. Keep IN leads long enough to reach the input gland area (~120 mm), OUT leads ~80 mm.
2. Splice the 500 mA polyfuse inline into the IN+ lead, heatshrunk.
3. Power IN+ / IN− from 12 V (bench supply, or the feeder splitter later), clip a spare ~2.2 kΩ across OUT, and set the pot to **10.40 V** (clockwise = down). The preload matters — unloaded, these modules read high.
4. Drop the module into the wall pocket, flat back against the wall, **components/pot facing the room** — push down until the front post's nub snaps over the top. Wires can be soldered at all four corner pads before or after; every pad stays accessible in the pocket.

## 4. Cables through glands

Thread both PG7 glands into the walls, locknuts inside. Feed the bare ends through **before** terminating:

- **Input gland:** the 12 V splitter tap cable (5.5×2.5 mm center-positive Y-splitter). Inside: + → polyfuse → buck IN+; − → buck IN−.
- **Output gland:** the 3.5 mm cable. Inside: conductors to the protoboard TIP and SLEEVE pads. Outside: solder the MP3-3501 mono plug (tip = signal, sleeve = ground) and splice the SMAJ12A TVS ~1" behind the plug under heatshrink — cathode (stripe) → tip conductor, anode → sleeve.

Then: buck OUT+ → protoboard "10.4V in" pad, buck OUT− → protoboard "12V−" pad.

## 5. Flash the ESP32

Before it goes in the case (no USB cutout — OTA afterwards). Flash the ESPHome config from `aF4-esp32-trigger-BOM.md`: GPIO13 switch is `internal` with `restore_mode: ALWAYS_OFF`, the `do_feed` script enforces the 10 s pulse + 290 s lockout, and the only exposed control is the "aF4 Feed" button. Verify it comes up on Ethernet before assembly.

## 6. Final assembly

1. Mount the protoboard on its bosses (2 diagonal M2 screws is enough).
2. Drop the ESP32 onto its three standoffs, RJ45 nose into the wall opening; 3× M2 screws.
3. Dupont jumpers from the protoboard's GPIO13/GND wires to the EXT header pins (check the Olimex silkscreen for GPIO13 and GND).
4. Tighten both gland caps on the cables.

## 7. Commissioning checks

1. **Meter first, feeder later.** With the 3.5 mm plug NOT in the feeder: plug in the splitter, meter tip↔sleeve. Expect 0 V at rest.
2. Press "aF4 Feed" in HA (or the ESPHome web UI): expect **~10.4 V for 10 s, then 0 V**. Confirm the lockout binary_sensor holds for ~5 min.
3. Power-cycle the ESP32 mid-check once: tip must stay at 0 V through boot (R2 + `ALWAYS_OFF` doing their jobs).
4. Plug into the feeder's 0-10V port — the link icon should light (mechanical detect). Trigger a test feed at a sensible time.
5. Screw the lid (4× M3×12).

## 8. Home Assistant

Time-trigger automations press `button.af4_feed`. Never schedule feeds <5 min apart (the device blocks them anyway). Optional: counter for daily feeds, notification on trigger, and a power-monitoring plug on the feeder supply to infer motor activity — the 0-10V port gives no dispense feedback.

Reminder from the feeder docs: the aF4's internal 24 h timer keeps its own schedule from power-on time; note it or plan around it (open question in `aF4-reference.md`).

## Troubleshooting

- **No trigger:** meter the tip during a button press. 0 V → check SSR orientation (notch toward R1), R1 continuity, GPIO13 jumper on the right header pin. ~10.4 V but no feed → hold time or port re-arm: port needs >60 s at 0 V before it accepts the next trigger, and feeds must be ≥5 min apart.
- **Voltage above ~10.5 V at the tip:** buck drifting under light load — confirm R3 is populated; re-set the pot in place.
- **Voltage sags below 9 V during trigger:** cracked joint on the 10.4 V run, or the polyfuse tripped (check for shorts, let it cool).
- **Link icon dark:** plug not fully seated; the jack's detect switch is mechanical.
- **ESP32 unreachable:** it's PoE — check the switch port budget (802.3af) and that you're on the ISO board's LAN, then OTA via ESPHome dashboard.
