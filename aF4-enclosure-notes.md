# aF4 Trigger Enclosure — Print & Assembly Notes

Case for the ESP32-POE-ISO + AQY212 protoboard. Designed against the measured `ESP32-PoE-ISO_Rev_N.step` model; fit verified digitally (zero interference).

## Files

- `aF4-trigger-case.stl` / `.step` — case body, 59.7 × 155 × 38.9 mm. Lengthened 14 mm at the output end (9 mm clear between the output gland's locknut and the protoboard, plus cable slack to the tip/sleeve pads). **v5:** RJ45 back flush in the outer wall (v1 style — v3/v4's lengthened input end left the jack recessed). Gland-nut clearance now comes from *width* instead: the left wall sits 12 mm out from the original design and the input gland moved left (x-center 21 mm from the inner left wall) so its locknut + thread stub (5 mm protrusion past the inner face) land entirely beside the board — 2.1 mm clear of the board edge — instead of under it. The board seats flush on its standoffs regardless of how far the gland protrudes.
- `aF4-trigger-lid.stl` / `.step` — lid, exported print-side down (flat top on bed)
- `af4_enclosure_ocp.py` — parametric source (Python/OpenCascade); every dimension is a named constant

## Layout

- **Input wall:** RJ45 flush cutout (jack face sits in the outer wall plane, tight 0.5 mm reveal) + PG7 gland for the 12V splitter cable, left of the jack and fully clear of the board footprint. Inner-face relief pockets clear the jack's latch wings and top shield bump; the springy wing tips compress slightly against the pocket floor (same as the proven v1 fit).
- **Output wall:** PG7 gland centered, for the 3.5mm cable. A 13.5 mm deep clearance zone sits between this wall and the protoboard — the locknut/thread stub use ~4.5 mm of it, leaving 9 mm for the cable to drop to the protoboard's tip/sleeve pads. Solder those wires on the board edge facing this gland (as drawn in `aF4-protoboard-layout.svg`).
- **Board:** three Ø6 standoffs matching the board's 2.2 mm holes, board bottom sits 9.5 mm above floor (header pins protrude 8.6 mm below board). **M2 self-tapping screws**, 1.7 mm pilot holes, ≥8 mm thread.
- **Protoboard bay:** past the antenna end, four Ø6 × 6 mm bosses spaced 6 perfboard grid pitches apart (15.24 × 15.24 mm) so the mounting holes land on existing grid holes — just drill 4 grid holes out to Ø2.2 mm. M2 self-tappers (two diagonal bosses is enough). See `aF4-protoboard-layout.svg` for component placement and wiring.
- **Buck pocket:** drop-in pocket on the left wall, mid-channel — designed against the actual MP1584EN module STEP (22.4 × 17.1, components verified). Nothing touches any edge or pad: the module's **flat back** sits 0.3 mm off the wall, its bottom PCB edge rests on a shelf that stops before the component zone, side fences stand 0.4 mm beyond the board ends, and a flexible front post with a stepped nub snaps over the top-front as it drops in. All four corner pads, the mid-edge caps, and the pot stay in open air; pot faces the room for adjustment. Solder wires first, then drop in. Optional: a small foam pad on the lid underside above the module stops any rattle (15 mm gap).
- **Lid:** 4× **M3 × 12 coarse self-tapping** screws into Ø9 corner bosses (2.5 mm pilots, open-bottomed so screws can't bottom out). Countersunk holes in lid. Registration lips on all four sides (30 mm on the long sides, 26 mm on the short sides to clear the corner bosses).
- Headroom above board: 26 mm — clears Dupont jumpers on the EXT headers.

## Print settings (PETG, P1S)

- Case upright (as exported), lid as exported (top face down). No supports needed — gland holes have truncated-teardrop roofs (45° sides, ~4 mm flat bridge at the crown, sized to hide completely under the PG7 hex body and locknut), RJ45 opening bridges 16.9 mm at z 16.5 (fine in PETG).
- 3 walls / 4 top-bottom layers, 15–25% infill, 0.2 mm layers.
- If self-tapping feels tight in PETG, run the M3s in slowly (low friction heat) or pre-thread with a screw before final assembly.

## Hardware

| Item | Qty | Spec |
|---|---|---|
| Lid screws | 4 | M3 × 12 coarse self-tapping (or plastite) |
| Board screws | 3 | M2 × 6–8 self-tapping |
| Protoboard screws | 2–4 | M2 × 8 self-tapping |
| Glands | 2 | PG7 (12.5 mm hole), feed bare cable before terminating |

## Assembly order

1. Thread glands into walls (12.5 mm holes; locknuts inside).
2. Feed 12V splitter cable through input gland, 3.5 mm cable through output gland, **before** soldering plugs/protoboard.
3. Solder the buck module's four corner wires (12V+/− in via polyfuse; 10.4V/− out) and **set it to 10.4 V on the bench with the R3 preload equivalent (~2.2 kΩ) loaded** — then slide it into the wall slot, pot facing inward.
4. Mount protoboard (SSR + R1/R2/R3), wire per `aF4-protoboard-layout.svg`.
5. Flash the ESP32 over USB first — there's no USB cutout (OTA afterwards).
6. Drop board onto standoffs, RJ45 into wall opening, 3× M2.
7. Dupont jumpers to GPIO13/GND, tighten glands, screw lid.
8. Before first live feed: meter tip↔sleeve, press the ESPHome button, confirm ~10.4 V for 10 s then 0 V.
