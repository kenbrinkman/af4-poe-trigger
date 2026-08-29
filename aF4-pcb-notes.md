# aF4 PoE Trigger — rev E PCB (professional assembly)

Rev D replaced the hand-wired 25 × 25 mm protoboard with a real PCB designed for
PCBWay turn-key assembly. The mechanism is unchanged: PoE ESP32 → GPIO → PhotoMOS
→ 10.4 V from the feeder's own supply onto the 3.5 mm trigger jack. What changed
is everything that existed only because the board was being built by hand.

Files live in `pcb/`. `gen_pcb.py` is the source of truth — it generates
`af4-trigger-hat.kicad_pcb` deterministically from named coordinates. Edit the
script, not the board file.

## Form factor: a hat, not a separate board

The board is a 57 × 50 mm daughterboard that plugs onto the Olimex
ESP32-POE-ISO's EXT1 and EXT2 headers via two 1 × 10 sockets, and extends ~24 mm
sideways past the ESP32 to carry both panel connectors.

Socket positions are taken directly from the Olimex Rev N KiCad source, not
measured:

| Feature | Position (Olimex board frame) |
|---|---|
| ESP32-POE-ISO outline | x 90.15–118.15, y 90.00–188.15 (28.00 × 98.15 mm) |
| EXT1 pin 1 | (91.44, 123.22), 2.54 mm pitch |
| EXT2 pin 1 | (116.84, 123.22), 2.54 mm pitch |
| **GND** | EXT1 pin 3 → (91.44, 128.30) |
| **GPIO32** | EXT2 pin 6 → (116.84, 135.92) |

The hat's own coordinates are expressed in that same frame, so alignment is exact
by construction.

**Prerequisite:** EXT1 and EXT2 ship unpopulated. Two 1 × 10 male headers must be
soldered into them **pointing up** before the hat can be fitted (Olimex supplies
these loose; Sullins PRPC010SAAN-RC is equivalent).

**Stack height:** male header plastic 2.54 mm + socket body 8.5 mm ⇒ the hat's
underside sits ~11.0 mm above the ESP32's top face. The tallest thing underneath
is the UEXT box header; its vendor 3D model tops out at 4.40 mm, so clearance is
ample. Note the hat covers UEXT — that connector is unusable while it is fitted,
which is fine, nothing uses it.

## The GPIO13 problem, and why the trigger moved to GPIO32

**GPIO13 has a 2.2 kΩ pull-up to +3.3 V on the Olimex board** (R35 in the Rev N
schematic — the factory I²C SDA pull-up). It is not optional and not removable
without rework.

During reset and early boot, GPIO13 is high-impedance. The pull-up then feeds the
PhotoMOS LED through R1, with only the 10 kΩ pulldown opposing it. Solving the
node: it settles near 1.4 V, pushing roughly **0.6–0.7 mA into the LED**. The
AQY212's LED operate current is ~1.1 mA typical with no guaranteed non-operate
floor below it. That is not a safe margin for a circuit whose failure mode is
"10.4 V held on the trigger port for more than 6 seconds = unscheduled feed", and
`restore_mode: ALWAYS_OFF` cannot help, because the pin is high-Z before the
firmware runs.

**GPIO32 touches only the ESP32 module and EXT2 pin 6** — no pull-up, no strapping
function, not shared with UEXT. GPIO33 is nearly as clean (one unpopulated
resistor). Rev D onward uses GPIO32.

> **Action required in `af4-feeder.yaml`:** change the feed switch pin from
> `GPIO13` to `GPIO32`, then OTA. The board will not work until this is done.

## Circuit changes beyond the package swap

| Change | Reason |
|---|---|
| **D1 SS14 Schottky in series with the 12 V input** | Rev C has no reverse-polarity protection at all. A miswired supply reaches the regulator and both polarised caps directly. Costs 0.3 V of the 1.5 V headroom, and makes a barrel-jack polarity error non-destructive rather than fatal |
| **F1 polyfuse on-board** | Was a heatshrunk splice in a pigtail |
| **D4 TVS on-board at the jack** | Was the second heatshrunk splice, ~1" behind the plug |
| **D2 SMAJ13A on the 12 V input** | New. Clamps supply-side transients ahead of the regulator; 13 V standoff sits above the 12 V rail so there is no standing leakage |
| **C2 → 10 µF 25 V tantalum** | 16 V at a 10.4 V rail is only 65 % derating; tantalums want 50 %. Still tantalum, because the LM1117 needs output-cap ESR |
| **R3 100 kΩ bleed across the trigger output** | Guarantees the port sees 0 V for its 60 s re-arm instead of relying on stray discharge. 104 µA |
| **D3 / D5 indicator LEDs** | D3 green = 10.4 V rail live, D5 yellow = trigger asserted. Turns the assembly-guide meter checks into a glance. **Series resistors are deliberately unequal — R6 = 1.0 kΩ, R7 = 6.8 kΩ** — because the two LEDs differ ~12× in efficiency (APT2012SGC 12 mcd vs APT2012SYCK 150 mcd, both at 20 mA). The LM1117 minimum load is carried by the R4/R5 divider's 10.3 mA, not by D3 |
| **TP1–TP5 test pads** | 12 V, 10.4 V, trigger tip, power ground, logic ground. Probeable without clipping onto component legs |
| **No series resistor on the tip** | Considered and rejected: at 10.4 V into a short it would sit right at the polyfuse's hold current and cook rather than trip. The LDO's internal current limit plus the polyfuse handle a shorted tip properly |

## Part equivalence review

Every through-hole part was checked against its surface-mount replacement rather
than assumed equivalent.

| Ref | Rev C (THT) | Rev D (SMD) | Verdict |
|---|---|---|---|
| U1 | AQY212GH, DIP-4, 60 V / 1.1 A, 0.34 Ω, **5000 Vrms** isolation | AQY212GS, SOP-4, 60 V / 1.0 A, 0.34 Ω, **1500 Vrms** | Same family and die. **Isolation drops 5000 → 1500 Vrms.** Both sides are SELV (12 V vs 3.3 V), so 1500 V is still ~100× any credible fault. Accepted deliberately. Toshiba's SMD photorelays are worse, not better — TLP3475S is 500 Vrms |
| U2 | LM1117T-ADJ, TO-220 | LM1117MPX-ADJ/NOPB, SOT-223 | Same die, same datasheet. **The TO-220 pin-crossing problem disappears** — the SOT-223 footprint puts ADJ where ADJ goes, so the pin-1 sleeving step in the rev C assembly guide is deleted |
| R4 | KOA MF1/4DCT52R1210F, 121 Ω axial | 0805 1 % 121 Ω | **The rev C sourcing problem evaporates.** 121 Ω 1 % in 0805 is a stocked jellybean; no 18-week Yageo lead time to work around |
| C1/C2 | Panasonic ECA-1HM100I, one part for both | C1 10 µF 50 V X5R 1206; C2 10 µF 25 V tantalum | No longer one part. C1 is ceramic (fine at the input); C2 must stay tantalum for ESR |
| F1 | MF-R010, radial | 1206L010/60WR, 1206 | Same 0.10 A hold. 60 V rating |
| D4 | P6KE15CA, DO-15 | SMBJ13CA, SMB | Bidirectional either way. 13 V standoff still sits above the 10.4 V line — the rev C lesson holds |
| J1 | DALQUIS DC-099 panel jack + pigtails | PJ-079BH board jack, 5.5 × 2.5, 24 V / 5 A | **Watch the trap:** PJ-002AH and PJ-102AH are the 2.0–2.1 mm parts. Only the "B" suffix parts are 2.5 mm centre pin |
| J2 | MP3-3501 plug on a captive cable | SJ1-3523N board jack + a commercial 3.5 mm patch cable | Jack is 3-conductor; ring is tied to sleeve on the board, which is what a TS plug does anyway |

## Isolation

The logic domain (sockets, R1, R2, PhotoMOS LED side) and the feeder-power domain
are separate ground pours with **no copper crossing between them**. The only
connection is the PhotoMOS itself, which physically straddles the boundary — its
own 4.3 mm pad-to-pad gap forms the barrier, which comfortably exceeds the
creepage its 1500 Vrms rating implies. The band is marked on both silkscreens.
Two mounting holes sit in it, which is free real estate.

## Ordering from PCBWay

Upload `pcb/af4-trigger-hat-rev-E-PCBWay.zip`. It contains:

- `gerbers/` — RS-274X, all layers, plus Excellon drill and a drill map
- `af4-trigger-hat-BOM.csv` — PCBWay's turn-key column set, keyed by manufacturer
  part number
- `af4-trigger-hat-centroid.csv` — SMD parts only, per PCBWay's rule; origin at
  the board's lower-left corner, Y up
- `PCBWay-README.txt` — stack-up, finish, and the five things an assembler could
  get wrong

Order shape: 5 pieces, 2 layers, 1.6 mm, top side only, full turn-key.
17 SMD placements plus 4 through-hole parts (28 joints) that they hand-solder.
20 unique part numbers.
Expect a parts-availability review email before they quote firm.

## Verification status

`gen_pcb.py` → KiCad 7 → DRC via `pcbnew.WriteDRCReport`:

- clearance: 0
- courtyard overlaps: 0
- hole clearance / hole-to-hole: 0
- copper-to-edge: 0
- unconnected items: 0
- solder-mask bridges: 0

Remaining flags are silkscreen cosmetics (text near footprint outlines) and
"library footprint differs from library", which is expected — the footprints are
placed programmatically with nets attached.

**One thing DRC does not catch, found by inspecting the drill file:** KiCad's
SJ1-3523N footprint specifies **0.40 mm-wide plated slots** for the jack's blade
terminals, and the PJ-079BH's shield tabs ask for 0.60 mm. Both are below what a
fab will route — PCBWay's minimum is around 1.0 mm milled / 0.5 mm drilled — so
the order would have come back as an engineering query at best. `gen_pcb.py` now
enforces `MIN_SLOT = 0.70 mm` on every plated slot and prints what it widened:

```
  widened slot J1 pad SH: 0.60x2.20 -> 0.70x2.20 mm
  widened slot J1 pad SH: 0.60x2.20 -> 0.70x2.20 mm
  widened slot J2 pad R:  0.40x1.40 -> 0.70x1.40 mm
  widened slot J2 pad S:  1.40x0.40 -> 1.40x0.70 mm
  widened slot J2 pad T:  0.40x1.40 -> 0.70x1.40 mm
```

Worst-case annular ring after widening is 0.25 mm, comfortably inside standard
capability, and the smallest tool in the drill file is now 0.45 mm — the stitching
vias, which is an ordinary drill rather than a slot.

## Mounting

Two M3 holes, at (123.0, 118.0) and (123.5, 147.0) in the board frame. Both sit in
the isolation band, which is the only X where a standoff rising from the enclosure
floor clears the **ESP32's right edge below** (118.15) and the **parts column above**
(from 126.45). That constraint is what fixes them; they are not free choices.

Everything else holding the hat is structural rather than threaded: twenty socket
pins along the left, and the two jack noses captured in their wall holes on the
right, which is where plug insertion force actually lands.

## The enclosure

Regenerated in `af4_enclosure_ocp.py`, which now asserts its own fit before it
exports — thirteen dimensional checks plus three solid-interference tests (case
against the hat envelope, case against the ESP32 envelope, lid against the hat).
All pass with zero intersection volume.

**External: 65.2 × 117.0 × 38.4 mm**, against rev C's 59.7 × 155 × 38.9. Same
height, 5.5 mm wider, 38 mm shorter. Gone: the protoboard bay, the buck pocket,
the DC-099 hole, the PG7 gland, and every wire that used to run between them.

The vertical stack is the governing dimension and is tabulated in
`aF4-enclosure-notes.md`. The short version: the socket body height sets where the
hat sits, the hat sits 12.62 mm above the ESP32, and the barrel jack's crown ends
up 2.08 mm below the lid. If you ever substitute a different 1 × 10 socket, change
`HAT_Z` and re-run — the script will tell you what now collides.

One detail worth knowing: the barrel-jack hole has a **Ø13 × 1.8 mm counterbore on
the outside**, thinning the wall to 1.2 mm locally. Without it, 3 mm of wall would
have eaten most of the jack's 9.5 mm insertion depth. As built the plug engages
6.9 mm.

## Open items

1. **`af4-feeder.yaml` moves GPIO13 → GPIO32.** The file in this repo is already
   updated; it still needs pasting into the ESPHome Device Builder and an OTA.
   Until that happens the board does nothing.
2. Solder two 1 × 10 male headers into EXT1/EXT2, pointing up.
3. Distributor part numbers are intentionally blank in the BOM — PCBWay sources by
   MPN. Fill them in only if you want to buy any of it yourself.
4. The two protoboard SVGs and `protoboard 20x20.stl` describe hardware that no
   longer exists. Kept as rev C history; don't build from them.
