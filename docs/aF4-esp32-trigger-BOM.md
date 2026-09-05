# aF4 PoE Trigger — Parts List (rev E)

Goal: a PoE ESP32 running ESPHome pulses 10.4 V (matching the measured OEM level)
onto the aF4's 3.5 mm 0-10 V port (≥9 V for ≥15 s = feed), scheduled from Home
Assistant. Replaces the inD connect dongle.

Rev D moved the whole trigger circuit onto a PCB hat assembled by PCBWay. The
electronics BOM is therefore two lists: **things you buy** (three of them) and
**things that arrive already soldered to the board**.

## What you buy

| Item | Pick | ~Price | Notes |
|---|---|---|---|
| PoE ESP32 board | **Olimex ESP32-POE-ISO** | $28–35 | Get the ISO version. Ships with EXT1/EXT2 unpopulated |
| Trigger hat, assembled | **PCBWay, 5 pcs turn-key** | ~$100–160 for five | Upload `pcb/af4-trigger-hat-rev-E-PCBWay.zip`. See `aF4-pcb-notes.md` |
| 1 × 10 male headers | 2.54 mm, 2 off | pennies | Solder into EXT1/EXT2 **pins up**. Olimex ships these loose; Sullins PRPC010SAAN-RC is equivalent |
| 12 V DC splitter | Barrel Y-splitter, **5.5 × 2.5 mm, centre-positive (confirmed)** | $6 | Taps the feeder's 12 V. Many cheap splitters are 5.5 × 2.1 — buy 2.5 specifically |
| 3.5 mm patch cable | Male–male, mono or stereo, ~0.5 m | $5 | Hat jack → aF4 0-10 V port. Stereo is fine; the aF4's jack shorts ring to sleeve |
| Enclosure | `hardware/enclosure/aF4-trigger-case.stl` + `hardware/enclosure/aF4-trigger-lid.stl` (PETG) | filament | 65.2 × 117.0 × 38.4 mm. See `aF4-enclosure-notes.md` |
| Screws | 4× M3 × 12 self-tapping (lid), 3× M2 × 6–8 (ESP32), 2× M3 × 8–10 (hat) | — | |

**Total: roughly $60–70 for the one-off parts, plus the board order.**

No wire, no heatshrink, no glands, no panel-mount jacks, no polyfuse to splice,
no TVS to bury under heatshrink. All of that is on the board now.

## What's on the board

This is the manufacturing BOM. The machine-readable version PCBWay wants is
`pcb/af4-trigger-hat-BOM.csv`; this table is the human one, with the reasoning.

| Ref | Part | Package | Why this part |
|---|---|---|---|
| U1 | **Panasonic AQY212GS** PhotoMOS, 60 V / 1 A, 0.34 Ω, 1500 Vrms | SOP-4 | Same family and die as the rev C DIP part. Isolation drops 5000 → 1500 Vrms, accepted: both sides are SELV. Pins 3/4 are a symmetric MOSFET pair, no polarity |
| U2 | **TI LM1117MPX-ADJ/NOPB** | SOT-223 | Same die as the rev C TO-220. **The pin-crossing problem is gone** — the footprint puts ADJ where ADJ goes |
| R4 / R5 | 121 Ω / 887 Ω, 1 %, 0805 | 0805 | Vout = 1.25 × (1 + 887/121) = 10.41 V, +53 mV from I_ADJ ≈ **10.47 V**. Fixed by construction. **The rev C sourcing problem vanishes** — 121 Ω 1 % in 0805 is a stocked jellybean, no 18-week lead |
| C1 | 10 µF 50 V X5R | 1206 | Regulator input bulk. X5R, not X7R: Murata's 1206 10 µF 50 V part (GRM31CR61H106KA12L) is X5R; X7R at that C/V needs a 1210 |
| C2 | 10 µF 25 V **tantalum** | EIA-3528 (B) | Must stay tantalum — the LM1117 needs output-cap ESR. 25 V not 16 V: 16 V at a 10.4 V rail is only 65 % derating, and tantalums want 50 %. **Polarised** |
| D1 | **SS14** Schottky, 40 V / 1 A | SMA | **New in rev D.** Reverse-polarity protection in series with the 12 V input — rev C had none at all. Costs 0.3 V of the 1.5 V headroom and turns a polarity mistake into "nothing happens" |
| D2 | **SMAJ13A** TVS, unidirectional | SMA | **New.** Input clamp. 13 V standoff sits above the 12 V rail, so no standing leakage |
| D4 | **SMBJ13CA** TVS, bidirectional | SMB | Was the P6KE15CA spliced behind the plug. Now on-board at the jack. Bidirectional, so no orientation |
| F1 | **1206L010/60WR** PPTC, 0.10 A hold / 0.25 A trip, 60 V | 1206 | Was the MF-R010 spliced into a pigtail. The feeder supply can source 12.5 A; steady draw here is ~19 mA (divider 10.4 + D3 8.3), ~20 mA during a feed |
| R1 | 220 Ω 1 % | 0805 | PhotoMOS LED current, ~9 mA from GPIO32 (6.8 mA worst case at a 3.0 V GPIO and Vf max 1.5 V) — inside Panasonic's recommended 5–30 mA |
| R2 | 10 kΩ 1 % | 0805 | GPIO32 pulldown. **On GPIO32 this is unopposed** — see the GPIO13 note below |
| R3 | 100 kΩ 1 % | 0805 | **New.** Bleeds the trigger line so the port reliably sees 0 V for its 60 s re-arm. 104 µA |
| R6 / D3 | **1.0 kΩ** + green LED | 0805 | **New.** Rail-live indicator, visible through a lid hole. 1.0 kΩ gives 8.2 mA: the APT2012SGC is only 12 mcd typ / 5 mcd min at 20 mA, so at the 10 kΩ first drafted it sat near 0.5 mcd and was invisible |
| R7 / D5 | **6.8 kΩ** + yellow LED | 0805 | **New.** Lights while the trigger is asserted — turns the meter checks into a glance. Only 1.2 mA needed: the APT2012SYCK is 150 mcd at 20 mA, ~12× the green's efficiency, so an equal resistor would badly mismatch them |
| J1 | **Same Sky PJ-079BH**, 5.5 × 2.5 mm, 24 V / 5 A | THT right-angle | **Watch the trap:** PJ-002AH and PJ-102AH are the 2.0–2.1 mm parts. Only the "B" suffix is 2.5 mm centre pin. Same trap as the splitter |
| J2 | **Same Sky SJ1-3523N**, 3.5 mm, 3-conductor | THT right-angle | Tip = signal. Ring is tied to sleeve on the board, which is what a TS plug does anyway |
| J3 / J4 | **Sullins PPTC101LFBN-RC**, 1 × 10 socket, 2.54 mm | THT | Mate EXT1 and EXT2. Their 8.5 mm body height sets the whole vertical stack |
| TP1–TP5 | Test pads: 12 V, 10.4 V, tip, power GND, logic GND | — | Probeable without clipping onto component legs |

Deliberately **not** on the board: a series resistor on the tip. At 10.4 V into a
short it would sit right at the polyfuse's hold current and cook instead of
tripping. The LDO's own current limit plus the polyfuse handle a shorted tip.

## The GPIO13 trap

`firmware/af4-feeder.yaml` drives **GPIO32**, not GPIO13. The Olimex board carries a
factory 2.2 kΩ pull-up to 3.3 V on GPIO13 (R35, the I²C SDA pull-up, confirmed in
the Rev N KiCad source). While the ESP32 is in reset, that pull-up feeds the
PhotoMOS LED through R1 with only R2 opposing it — about 0.6–0.7 mA into a part
whose operate current is ~1.1 mA typical, with no guaranteed non-operate floor
below that. `restore_mode: ALWAYS_OFF` cannot help, because the pin is high-Z
before any firmware runs.

GPIO32 touches only the ESP32 module and EXT2 pin 6. No pull-up, no strapping
role, not shared with UEXT. Do not move it back.

## Ordering the board

Upload `pcb/af4-trigger-hat-rev-E-PCBWay.zip`. Order shape: 5 pieces, 2 layers,
1.6 mm, top side populated, full turn-key. 17 SMD placements plus 4 through-hole
parts (28 joints) that they hand-solder. 20 unique part numbers. Full procedure and the fab notes are in
`aF4-pcb-notes.md`.

Distributor part numbers are deliberately blank in the CSV — PCBWay sources by
manufacturer part number. Fill them in only if you want to buy any of it yourself.

## Rev C parts you already own

From the two DigiKey orders (2026-07-11 web ID 373961064 and 2026-07-26 web ID
374640854): the ESP32-POE-ISO carries straight over, and the AQY212GH, MP3-3501,
LM1117T-ADJ, axial resistors, electrolytics, MF-R010 and P6KE15CA become spares.
None of them are used in rev D — the through-hole build they belonged to no
longer exists. Keep the AQY212GH ×2 and the ESP32; the rest is bin stock.

## Is PoE ESP32 right for a 0-10 V application?

Yes, with the same nuance as always: no ESP32 outputs 9–12 V natively. The board
is brains and network; the trigger voltage comes from the feeder's own supply via
the splitter, regulated to 10.4 V on the hat and switched onto the tip by the
PhotoMOS. You do **not** need a 0-10 V DAC — the aF4 treats the port as a
threshold trigger (≥9 V, ≥15 s `[VENDOR] 2026-09-01`), not an analog level.

## Verification before wiring (voltmeter, OEM dongle installed)

Already done and recorded in `aF4-reference.md`: rest voltage 0 V, trigger voltage
10.37 V, link detect mechanical, splitter 5.5 × 2.5 centre-positive.
