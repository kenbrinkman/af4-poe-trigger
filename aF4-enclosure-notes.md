# aF4 Trigger Enclosure — rev D print & assembly notes

Case for the ESP32-POE-ISO plus the rev E trigger hat. Modelled against the
measured `ESP32-PoE-ISO_Rev_N.step` and against the hat's own KiCad geometry;
fit verified digitally (zero interference — the build script asserts it).

**External: 65.2 × 117.0 × 38.4 mm** (rev C was 59.7 × 155 × 38.9). 38 mm shorter,
5.5 mm wider, same height. Interior volume drops about 18 %, and everything that
used to be hand-wired inside it is gone.

## Files

- `aF4-trigger-case.stl` / `.step` — case body
- `aF4-trigger-lid.stl` / `.step` — lid, exported print-side down (flat top on bed)
- `af4_enclosure_ocp.py` — parametric source (Python/OpenCascade); every dimension
  is a named constant and the script runs a geometry + solid-interference check
  before it exports

## What changed from rev C

| Rev C feature | Rev D |
|---|---|
| Protoboard bay + 4 bosses past the antenna end | **Gone.** The case now stops 1.7 mm past the antenna tip |
| MP1584EN buck pocket on the left wall | **Gone** (it was already vestigial) |
| DC-099 barrel jack in the input wall | **Gone.** The barrel jack is on the hat |
| PG7 gland in the output wall | **Gone.** The 3.5 mm jack is on the hat |
| Both user connectors on opposite short walls | Both on **one long wall**, side by side |
| — | **New:** two tall standoffs carrying the hat |
| — | **New:** two LED sight holes in the lid |

## Layout

- **Input wall (−Y):** RJ45 flush cutout only, jack face in the outer wall plane
  with a 0.5 mm reveal. Inner-face relief pockets clear the latch wings and the
  top shield bump, exactly as in rev C — that fit is proven, so it was left alone.
- **Long wall (+X):** the hat's two jacks. Barrel jack at y = −116.56, axis 17.82 mm
  above the case floor datum; 3.5 mm jack at y = −148.50, axis 16.72 mm. Both holes
  are truncated-teardrop so they bridge without support.
  - The barrel hole is Ø7.4 with a **Ø13 × 1.8 mm counterbore on the outside**.
    That thins the wall to 1.2 mm locally, which is what makes the plug seat: full
    3 mm of wall would have eaten most of the jack's 9.5 mm insertion depth. As
    built the plug engages **6.9 mm**.
  - The 3.5 mm hole is Ø6.6 for the jack's 6.0 mm nose. The nose ends 1.2 mm inside
    the outer face, so it is protected rather than proud.
- **Output wall (+Y):** blank. Nothing exits that end any more.
- **ESP32 board:** three Ø6 standoffs, tops at z = 0, M2 self-tappers into 1.7 mm
  pilots — unchanged from rev C.
- **Hat:** two Ø7 standoffs rising from the floor to z = 12.62 (the hat's underside),
  M3 self-tappers into 2.5 mm pilots, each with a conical foot so a 22 mm post is
  not a cantilever. They sit at (123.0, −118.0) and (123.5, −147.0) — the only X
  that clears the ESP32's right edge below **and** the hat's parts column above.
  Those two, plus twenty socket pins on the left and two jack noses captured in the
  wall on the right, is what holds the hat.
- **Lid:** 4 × M3 × 12 coarse self-tapping into Ø9 corner bosses (2.5 mm pilots,
  open-bottomed). Registration lips on all four sides. **Four LED sight holes**
  fitted with 3 mm light pipes, and the label `aF4 PoE / TRIGGER` engraved 0.8 mm
  into the outer face — both detailed in their own section below.
- **Wall-mount tabs:** one per long side, mid-length, flush with the case bottom,
  4.5 mm hole for #8 / M4.

## Lid LED sight holes and light pipes

Four Ø3.5 bores from the lid underside, each stepping down to a **Ø2.6 aperture**
through the last 0.9 mm of the outer face. A 3 mm clear acrylic rod drops in from
the inside, seats on that step — so it cannot migrate down onto the LED — and is
held and sealed with a bead of clear epoxy at the inner face. That also **seals**
four holes that were previously open to a sump room.

| Hole | x, y | Over | Rod |
|---|---|---|---|
| hat D3 | 139.50, −139.00 | rail live, green | 10.1 mm |
| hat D5 | 128.20, −150.80 | feed pulsing, yellow | 10.1 mm |
| PWR1 | 91.567, −171.069 | Olimex 3V3 rail, red | 22.7 mm |
| LNK1 | 91.567, −165.354 | Olimex ethernet link, green | 22.7 mm |

Rods seat at z = 25.60 and stop 0.6 mm short of each LED. **They must never touch
the LED.**

**Why pipes and not plain holes.** The hat's LEDs sit on `HAT_TOP`, 8.5 mm under
the lid, so a plain Ø3.5 hole gave an 11.6° viewing half-angle and worked fine.
The Olimex LEDs are **21.2 mm** down and the same hole gives **4.7°** — visible
only dead-on. Widening does not rescue it (Ø4.5 only reaches 6.1°). The air gap
is the limiter, not the aperture.

**Where the Olimex LED positions came from.** `ESP32-PoE-ISO_Rev_N.step` is
authored in this same frame, so its component placements are enclosure
coordinates directly — no mapping, and the Rev N Eagle files were not needed.
All four of its LEDs sit in one column at x = 91.567 on a 5.715 mm pitch:
CHRG1 −176.784, PWR1 −171.069, LNK1 −165.354, ACT1 −159.639.

**Two of them deliberately have no hole.**

- **ACT1** sits **0.361 mm inside the hat footprint** (`HAT_Y0` = −160.0) and is
  blindfolded by 1.6 mm of opaque FR4. Nothing in the lid can see it, and no
  amount of hole moving fixes it. The `light pipes intersect hat PCB` solid test
  in `af4_enclosure_ocp.py` is what enforces this — it will fail the build if a
  future hole is placed over anything the hat covers.
- **CHRG1** is the LiPo charge LED and there is no battery in this build. U3
  (SOT-23-5) is also only 2.9 mm away, which a 3 mm pipe would foul.

**Engraved label.** `aF4 PoE` / `TRIGGER`, DejaVu Sans Bold at 8 mm, 0.8 mm deep,
block centred at (117.0, −108.0) and reading along +Y — upright when the box is
held landscape with the cable end on the left. Nearest obstruction is 14.4 mm
away. The lid exports top-face-down, so the recess lands on the bed and comes out
crisp. Glyph outlines come from `matplotlib`'s TextPath, the same idiom as the
Temp Junction Box scripts, so the build now needs `matplotlib` installed.

## The vertical stack

This is the dimension that governs everything, so it is worth stating plainly:

```
  z = -11.90   case floor, outside
  z =  -9.50   case floor, inside
  z =   0.00   top of the three ESP32 standoffs
  z =   1.58   ESP32 top face
  z =   4.12   top of the male header plastic on EXT1/EXT2
  z =   5.98   top of the UEXT box header  (the tallest thing under the hat)
  z =   9.22   lowest point of the hat's through-hole pins   -> 3.24 mm clear
  z =  12.62   hat underside  (= socket body height above the header plastic)
  z =  14.22   hat top face
  z =  16.72   3.5 mm jack axis
  z =  17.82   barrel jack axis
  z =  21.42   barrel jack crown  -> 2.08 mm clear of the lid
  z =  23.50   lid underside
```

If you substitute a different 1 × 10 socket, its **body height is the parameter
that moves the whole hat** — change `HAT_Z` in `af4_enclosure_ocp.py` and re-run;
the script will tell you if anything now collides.

## Print settings (PETG, P1S)

- Case upright (as exported), lid as exported (top face down). **No supports.**
  Both jack holes have truncated-teardrop roofs, and the RJ45 opening bridges
  16.9 mm at z 16.5 — fine in PETG, proven on the rev C prints.
- 3 walls / 4 top-bottom layers, 15–25 % infill, 0.2 mm layers.
- The two hat standoffs are the tallest unsupported features. They print fine
  upright with their conical feet, but do not drop infill below 15 %.
- If self-tapping feels tight in PETG, run the screws in slowly or pre-thread.

## Hardware

| Item | Qty | Spec |
|---|---|---|
| Lid screws | 4 | M3 × 12 coarse self-tapping (or plastite) |
| ESP32 board screws | 3 | M2 × 6–8 self-tapping |
| Hat screws | 2 | M3 × 8–10 self-tapping |
| Wall-mount screws | 2 | #8 or M4, into the tabs |

No glands, no locknuts, no panel-mount jacks, no cable feed-throughs. The only
things that pass through a wall are the RJ45 and the two jacks, and all three are
soldered to a board.

## Assembly order

1. Print both parts. Test-fit a barrel plug and a 3.5 mm plug into the two
   +X wall holes **before** going further — a light chase with a round file is
   normal.
2. Fit the ESP32-POE-ISO onto its three standoffs, RJ45 into the wall opening,
   3 × M2. **This has to happen first** — the hat covers two of its screws.
3. Solder two 1 × 10 male headers into EXT1/EXT2, pins up, if not already done.
4. Drop the hat on: sockets onto the headers, both jack noses into their wall
   holes, then 2 × M3 into the standoffs. Seat the sockets before the screws.
5. Lid on, 4 × M3 × 12.

## The fitment dummy (2026-08-31)

`aF4-trigger-hat-dummy.stl` is a printable stand-in for the rev E hat, so the
enclosure can be proven before the real board comes back from PCBWay. Generated
by `af4_hat_dummy_ocp.py`, which — like the enclosure script — asserts its own
fit before it exports, and does it against the exported case and lid solids
rather than against a bounding box:

```
  board outline 57.0 x 50.0 x 1.6, both M3 holes at 3.30 (real board is 3.20)
  J1 PJ-079BH body 11.5 x 10.1 x 7.2, bored 6.0 x 9.5 from the front face
  J2 SJ1-3523N body 11.0 x 12.0 x 5.0, 9.0 mm shoulder, 6.0 mm nose to x=147.95
  U1, D3 and D5 bumps under the two lid sight holes
  two detachable 8.5 mm socket bars (J3/J4) that peg into the underside
```

Checks, all passing: zero intersection with the case solid and with the lid
solid; an M3 shank passes both mounting holes; a 5.5 mm plug pushed through the
wall bore reaches the J1 bore; and each socket bar clears the tallest ESP32
feature under it by 1.17 mm, taken from the vertices of
`ESP32-PoE-ISO_Rev_N.stl` rather than assumed.

Bodies come from the **F.Fab outlines actually placed in the .kicad_pcb**,
transformed into the board frame — not from the datasheets a second time. One
discrepancy surfaced doing that: F.Fab puts the J2 nose tip at x = 147.95, while
`af4_enclosure_ocp.py` carries `J2_NOSE_X = 148.45`. The enclosure constant is
the conservative one (recess 1.20 vs 1.70 mm inside the outer face), so nothing
needs changing — but they should not be allowed to drift further apart.

**What the dummy cannot prove.** The J2 barrel axis at hat top + 2.50 is an
assumed number in `af4_enclosure_ocp.py`, and the dummy is built from the same
assumption, so it cannot catch an error in it. The Ø6.6 wall hole leaves only
0.3 mm per side around a Ø6.0 nose, so a 0.5 mm error in that axis height is an
interference. **Measure the real jack's barrel axis above its seating plane when
the parts arrive.** The same applies, less tightly, to the barrel jack: Ø7.4
hole, axis assumed at hat top + 3.60.

Print: as exported, no supports, 0.2 mm layers, 3 walls, 15 % infill. **Use a
brim** — the board is a thin 57 x 50 plate and the two socket bars are thin
standing walls. Plate is 58.8 x 87.4 x 10.1 mm. The socket bars are optional;
print them only if the ESP32 is going in the case for the same test, and press
their 1.6 mm pegs into the four holes on the board's underside.
