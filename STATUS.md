# STATUS — aF4 PoE Trigger

**Rewritten 2026-09-18.** The only live-status document in this project. Rewrite it; never
append to it. If it passes ~120 lines, something in it belongs in `aF4-MASTER-REFERENCE.md`.

## Phase

**🟠 Boards arrived 2026-09-18 — and J1, the 12 V barrel jack, is rotated 180° on all five.
The error is ours, in `pcb/gen_pcb.py`, not PCBWay's. Decision taken the same day: use all
five as built, leave J1 fitted and dead, and bring 12 V in through a panel-mount jack in the
+X wall wired to J1's pad tails on the hat's underside.** → §A4

| | |
|---|---|
| Boards | **In hand, 5 pcs.** Electrically as designed; only the 12 V plug interface is unreachable. Not yet inspected → item 26 |
| Firmware | **Complete and flashed**, bench-verified 2026-09-01. Unaffected |
| HA software | **Complete**, verified against the live instance 2026-09-02. Unaffected |
| Enclosure | **Script changed and re-verified 2026-09-18** — old J1 hole removed, keyed D-hole for the panel jack added, cable tie post added. **The case must be reprinted** (item 29). ✅ **The lid does not** — `aF4-trigger-lid.stl` is byte-identical to the commit the 09-17 lid was printed from, verified not assumed |
| 12 V wiring | **Soldered 2026-09-18** to J1's pad tails — red to pin 1, black to pin 2, pin 3 bare. ⚠️ **Polarity not yet confirmed with a meter** |
| Go-live | `input_boolean.reef_af4_schedule_enabled` stays **OFF** until commissioning 6.1–6.8 pass |

**Nothing is on order and nothing is waiting.** Item 28 opened and closed the same day: the
panel jack came out of the parts drawer — six **DALQUIS DC-099**, the part rev C already used —
was calipered, and the case geometry is set to the real part. **The case can be printed now.**

1. **Confirm the 12 V polarity with a meter** — black tail to **TP4 is a dead short**. Ten
   seconds, and it is the only thing that settles it. ⚠️ Never the mirror test on red against
   TP1: F1 and D1 make a *correct* board read a diode drop.
2. **Print the case** (item 29). The **lid is unchanged**; print the case only.
3. **At the bench, in parallel:** items **26**, **12** and **16** are the session already
   planned, plus cutting the two PoE light pipes to 24.2 mm (item 27 — pipe lengths unchanged).

## The 2026-09-18 finding in one paragraph

`pcb/gen_pcb.py` places J1 at rotation **270**, which aims CUI's bore at board **x 133.68** — the
middle of the hat. **J2 is correct at rot 90**; the two connectors needed the same handedness.
**The part cannot be re-seated:** its pins sit at local x = 0, −3.2, −8.5, and no rotation maps
gaps of 3.2 and 5.3 onto themselves. A second error surfaced on the same part — the enclosure's
`J1_Y` was the jack **body** centre, not its bore axis, so the hole was 1.25 mm off against
0.95 mm of slack. **Three checks appeared to cover this and all three were hollow.** → §A4

## What you may trust

- **The lid needs no reprint** — `aF4-trigger-lid.stl` checked byte-for-byte against commit
  `29f1682`, the state the 09-17 lid was printed from. Unchanged since `5cb4b7b`. → §A4
- **The J1 diagnosis and the DC-099's calipered dimensions** — the first read from the design
  sources and CUI's STEP model rather than the photograph, the second from the part. Both in §A4
  with their provenance. **Red is +12 V, black is −.**
- **The pad identification on the hat's underside** — corroborated by Same Sky's own PCB layout
  drawing, whose published gaps are exactly our footprint's. **The wider gap is the ground side**,
  in both the pin and the shield-tab column; **pin 1 is in the tight pair with pin 3**. Confirm on
  the bench as **GND tail → TP4, a dead short**; ⚠️ never as red against TP1. → §A4
- **The enclosure at its new geometry**, re-run on the Mac 2026-09-18: every scalar check passes,
  all ten solid tests read 0 mm³, and `verify_enclosure.py` passes independently — including the
  new check that the **old J1 hole is closed** in the printed mesh. External size unchanged at
  65.2 × 117.0 × 39.9 mm.
- **The measured heights under the hat and the 0.72 mm cap clearance** — calipered 2026-09-16. → §6.3
- **The EXT1/EXT2 pin assignments**, read 2026-09-16 from Olimex's `ESP32-PoE-ISO_Rev_N.kicad_pcb`.
- **§2 arithmetic, all `[CAD]` board geometry, all 20 MPNs, DRC, BOM ≡ centroid ≡ board.**
- **The ordered board under KiCad 9.0.7** (2026-09-17): 0 DRC errors, a KiCad 9 export
  pixel-identical to the shipped Gerbers. → §4.4
- **The firmware matches §5 exactly**, and the flashed device matches `firmware/af4-feeder.yaml`.
- **The commissioning bands** (6.2 = 11.4–12.0 V, 6.3 = 10.0–10.9 V).
- **Both reef automations as §5.7 describes them.**

## What you may not trust

- ⚠️ **The 12 V polarity is soldered but unverified.** Photograph and datasheet both agree it is
  right; neither is a meter. Not dangerous either way — D1 blocks a reversal, so the symptom
  would be D3 dark at 6.1, not damage. → §A4
- ⚠️ **Whichever board carries the wires is now the build board by default**, and item 26's
  inspection of all five has not happened yet. If that board fails inspection, the wires move.
- **Four `PJ_*` values are not calipered:** flange Ø and body Ø are assumed upper bounds, thread
  and overall length come from the vendor drawing. None shapes the printed hole and none gates a
  check; the script names them on every run. → §A4
- ⚠️ **The 2026-09-17 case print is retired** — it has the old J1 hole and no panel-jack hole. The
  **lid** from that print is still good.
- **The 0.72 mm cap clearance and the ~4.3 mm pin engagement are still calculated, not felt.**
  Both get their first physical check at the item-12 dry-fit.
- **The DCDC1 end of EXT2.** The vendor model shows ~0.65 mm to the header plastic; the real part
  needed force. Shave the plastic, don't force it.
- **Only board 1 of five was ever photographed**; the ten J3 joints are ungraded; every board ships
  with pin-10 excess solder and flux residue. → item 26
- **D3 and D5 polarity** is unverified until commissioning. → item 25
- **Silkscreen reads "10.4V 10s pulse"** — wrong, unfixable on this run.
- **The enclosure scripts run only on the Mac**, in `~/.venvs/cad`, and need the OCP 8
  compatibility block. → §9.2
- **`pcb/gen_pcb.py` and `pcb/make_package.py` have not been re-run under KiCad 9.** Diff a
  regenerated board against the committed `.kicad_pcb` before trusting it. → §9.2

## Standing corrections — settled, do not re-raise

- 🚫 **Never route the 12 V leads across the hat's right-hand edge.** 0.50 mm between the hat
  edge and the inner wall; a lead there is crushed by the lid, invisibly. Down into the void,
  then along the floor. → §A4
- 🚫 **Do not remove J1, and do not try to plug anything into it.** It stays fitted and dead on
  every board; D1 and C1 block its bore anyway. → §A4
- 🚫 **The J1 error is ours, not PCBWay's** — same family as J3/J4. No complaint, no credit
  request, no email. The EQ thread is closed and the order is delivered. → §A4, §A3.2
- 🚫 **A check whose result is fixed by its own inputs is not a check.** Before trusting one, ask
  what state of the world would make it fail. → §A4
- 🚫 **Do not mount the ESP32 bottom side up.** It mirrors the EXT pinout. → §6.3
- 🚫 **Do not press the hat fully home on the headers outside the case.** → §6.3
- 🚫 **In `pcb/BOARD REVIEW EQ/`, `rejected-sample-2026-09-11-*` is the board turned down.** → §A3.1
- 🚫 **Item 17 does not exist and never did.** → §7.1
- ⚠️ **Item numbers are `aF4-MASTER-REFERENCE.md` §8 numbers** — the only numbering.

## Open items — by consequence

| # | Item | Blocks |
|---|---|---|
| 29 | **Print the case** from the 09-18 exports — **not the lid**. Then fit the DC-099 flat up and tighten its 14 mm nut **while the box is empty**, solder the pair to J1's pad tails (**red +12 V, black −**), anchor at the tie post | **Assembly** |
| 26 | **Inspect all five and pick the best board** — check the J3/J4 face on each. Reflow the two pin-10 joints, clean with IPA, loupe the ten J3 joints | **The bench session, now** |
| 12 | **Solder two 1×10 male headers into EXT1/EXT2, pins up, plastic on the top face.** Shave the pin-10 end of EXT2's plastic if it binds on DCDC1 | **Assembly** |
| 16 | **Rotate `af4_ota_password` during the item-12 serial flash**, then delete the old value from `firmware/secrets.yaml` **and** the Device Builder Secrets editor | No — but a live exposure |
| 27 | **Cut the two PoE light pipes to 24.2 mm** (hat pipes unchanged, 10.1); move the hat up 1.5 mm in Tinkercad. Unaffected by the reprint | **Assembly** |
| — | **Plumb the reef system.** The long pole | **Go-live** |
| 15 | **Commissioning 6.1–6.8 all pass** before the schedule toggle goes on. 6.1 now means the panel jack, not J1 | **Go-live** |
| 24 | **Fix the cause of the J3/J4 error:** footprints to `B.Cu`, silkscreen to `B.SilkS`, face named in `PCBWay-README.txt`, THT parts in the centroid with a side column | No |
| 25 | **D3/D5 polarity** resolves at commissioning 6.1 and 6.5 | No |
| 20 | **No dispense confirmation.** A power-monitoring smart plug on the 12 V supply is the only fix short of opening the unit | No — the last unmonitored failure direction |
| 22 | `pcb/gen_pcb.py` stray "exclude from BOM/pos" flags on J2. Fold into item 24 | No |
| 14 | LED viewing-angle conflict → §2.6 | No — cosmetic |
| 18 | R5 to 0.25 W — deferred, window closed | No |
| — | Bench leftovers: A4's V_loaded half, A5 under power, A6 decay, B1/B2/B3 | No |

**Out of scope**, decided 2026-09-01: eWeLink → Home Assistant integration.

### Carried to the next board revision

**§A4 holds the full list**, headed by J1 to rotation 90 with its corner re-laid out, and both
jack datums taken from the vendor STEP rather than by hand. Unchanged from before: J3/J4
footprints onto `B.Cu` (item 24), the hat's underside kept clear over the Olimex cap, C1's EOL
replacement, R5 to 0.25 W (item 18), J1/J2 sourcing, and the fab-note fixes.

## Last session — 2026-09-18

Boards delivered. Diagnosed J1 from the design sources and CUI's STEP model, confirmed J2 is
correct, and proved no re-seat is possible. Found the enclosure's J1 hole was 1.25 mm off axis
independently, and that all three checks covering the jack were hollow. Took Kenny's repair
route — hat used as built, panel jack in the +X wall — into `af4_enclosure_ocp.py` and
`verify_enclosure.py`, corrected `af4_hat_dummy_ocp.py`, and recorded it as §A4 with items 28
and 29. Then item 28 closed the same day: the jack was already in stock, and calipering it
revealed a **flat on the barrel**, which replaced the printed anti-rotation scheme with a keyed
D-hole and deleted the `hex_x` helper. Exports regenerated. Kenny then soldered the 12 V pair to
J1's pad tails, re-running them inboard once the 0.50 mm edge clearance was pointed out, and the
lid was confirmed byte-identical to the 09-17 print rather than taken on trust.
