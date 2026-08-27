# aF4 PoE Trigger — Assembly Guide (rev D)

Build sequence for the ESP32-POE-ISO feeder trigger with the rev D PCB hat.
Companion docs: `aF4-esp32-trigger-BOM.md` (parts), `aF4-rev-D-pcb-notes.md`
(board design and PCBWay ordering), `aF4-enclosure-notes.md` (print details),
`aF4-reference.md` (feeder specs and measured values).

Rev D is a much shorter build than rev C. There is no protoboard to cut, drill,
populate or wire; no resistors to stand on end; no splices to heatshrink; no
regulator pin to sleeve; and nothing to set at the bench. The circuit arrives
assembled and tested. What is left is: print, plug together, flash, meter, enable.

## 0. Parts and tools

Everything from the BOM, plus: a soldering iron (for exactly two headers), a
multimeter, M2 and M3 screwdrivers, and a 3.5 mm mono or stereo patch cable with
a plug on each end.

Not needed any more: 22 AWG wire, heatshrink, the 2.2 mm drill, a hacksaw, a bench
supply, a trimmer tool.

## 1. Print the enclosure

Print `aF4-trigger-case.stl` and `aF4-trigger-lid.stl` in PETG, orientations as
exported, no supports. 3 walls, 15–25 % infill, 0.2 mm layers.

Before going further, test-fit into the +X long wall:

- a 5.5 × 2.5 barrel plug into the counterbored hole,
- a 3.5 mm plug into the smaller hole.

A light chase with a round file is normal on a first print.

## 2. Receive and inspect the board

The hat arrives populated. Give it thirty seconds:

- **C2 polarity** — the tantalum's stripe/+ end must face the 10.4 V rail (pad 1,
  marked on the silkscreen).
- **J1 is the 2.5 mm centre-pin jack.** Plug the feeder splitter's tap lead into
  it and confirm it seats with a click, not a wobble. A 2.1 mm part will feel
  loose; if it does, stop — see the note in the BOM.
- **U1 pin 1** dot toward the ESP32 side of the board.
- Nothing bridging the copper-free isolation band running down the middle.

Meter, board unpowered: **J1 centre pin to J2 sleeve should read open** (the
PhotoMOS is off and the LM1117 is unpowered). Between the 12 V test pad and GND
you will read the reverse-polarity diode, not a short.

## 3. Fit the male headers to the ESP32

The Olimex board ships with EXT1 and EXT2 as bare plated holes. Solder a
**1 × 10 male header into each, pins pointing up**, plastic sitting flat on the
board's top face.

Get these square. The hat mates over both at once, and a header leaning even a
couple of degrees will fight the sockets. Tack one end pin, check the header is
flat and perpendicular, then do the remaining nine.

## 4. Flash the ESP32

There is no USB cutout in the case, so flash **before** final assembly if this is
a fresh board. `af4-feeder.yaml` in this folder is the source of truth; paste it
into the ESPHome Device Builder on the Unraid server (port 6052) and install.

> **If you are re-using the already-flashed board:** the trigger pin changed.
> Rev D drives **GPIO32**, not GPIO13, because of the factory 2.2 kΩ pull-up on
> GPIO13 — see `aF4-rev-D-pcb-notes.md`. Push the updated YAML over OTA before
> you plug the hat on. The board will do nothing at all until you do.

## 5. Assemble

Order matters — the hat covers two of the ESP32's mounting screws.

1. ESP32-POE-ISO onto its three standoffs, RJ45 into the wall opening, 3 × M2.
2. Hat down onto the two headers. Both jack noses should drop into their wall
   holes as the sockets seat; if they do not line up, the sockets are not fully
   home. Press evenly along the socket rows, not on the jacks.
3. 2 × M3 self-tappers through the hat's mounting holes into the two tall
   standoffs. Snug, not tight — the sockets locate the board, the screws just
   stop it lifting.
4. Leave the lid off for §6.

## 6. Commissioning checks

Ethernet first, feeder power second. All voltages are referenced to the **GND**
test pad on the power side of the board (TP4), not to the ESP32's ground.

| # | Check | Expect |
|---|---|---|
| 6.1 | Splitter tap plugged into J1 | Green LED (D3) lit |
| 6.2 | TP1 (12 V) to TP4 | 11.6–12.2 V (12 V less the Schottky drop) |
| 6.3 | TP2 (10.4 V) to TP4 | **10.3–10.5 V.** This is the check that matters — it confirms the R4/R5 divider |
| 6.4 | TP3 (tip) to TP4, at rest | 0 V, and the yellow LED (D5) dark |
| 6.5 | Press the Feed button on the ESPHome web page | Yellow LED lights, TP3 reads ~10.4 V for 10 s, then returns to 0 V |
| 6.6 | Feed Lockout binary sensor | Turns on with the pulse, clears about 5 minutes later |

If 6.3 reads ~1.4 V, R4 and R5 are swapped. If it reads near 12 V, the divider is
not connected. Either way, stop — do not connect the feeder.

Only once 6.1–6.6 all pass, connect the 3.5 mm patch cable from J2 to the aF4's
0-10 V port and confirm the link icon lights on the feeder.

## 7. Close up and enable

1. Lid on, 4 × M3 × 12. The two LED sight holes should land over D3 and D5 — you
   should be able to see the green rail LED through the lid.
2. In Home Assistant, run one manual feed via `button.af4_feeder_feed` and watch
   the feeder actually cycle.
3. Only then turn on `input_boolean.reef_af4_schedule_enabled`.

## Rev C history

The rev C protoboard build sequence — cutting and drilling the board, standing
the resistors vertically, sleeving the LM1117's crossed pin 1, splicing the
polyfuse into the jack pigtail and the TVS behind the 3.5 mm plug — is preserved
in git history along with `aF4-protoboard-layout.svg` and
`aF4-protoboard-solder-side.svg`. None of it applies to rev D, and the two
protoboard SVGs describe hardware that no longer exists.
