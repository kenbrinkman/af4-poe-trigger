# STATUS — aF4 PoE Trigger

**Rewritten 2026-09-11.** The only live-status document in this project. Rewrite it; never
append to it. If it passes ~120 lines, something in it belongs in `aF4-MASTER-REFERENCE.md`.

## Phase

**🔴 Assembly sample REJECTED. J3 and J4 are built on the wrong face. Boards are in rework
at PCBWay and there IS something to do there — the EQ reply has to go out.**

| | |
|---|---|
| Boards | PCBWay `YB1800644`, placed 2026-09-02, $169.95, 5 pcs assembled |
| Fabrication | **Done.** Bare PCB `W1125728AS3P5` hit 100 % on 2026-09-10 |
| Assembly | **Built, then rejected 2026-09-11.** SMT is correct; J3/J4 are on the top face and belong on the bottom. Rework requested |
| Expected | **Unknown — do not quote a date.** PCBWay recalculates the build clock from the end of EQ, and the original 2026-09-30 was already stale on the optimistic side before this |
| Firmware | **Complete and flashed**, bench-verified 2026-09-01 |
| HA software | **Complete**, verified against the live instance 2026-09-02 |
| Enclosure | Modelled, fit-checked digitally, printable |
| Go-live | `input_boolean.reef_af4_schedule_enabled` stays **OFF** until commissioning 6.1–6.8 pass |

**The immediate thread:** send the reply in `pcb/pcbway-EQ-2026-09-11-reply.md` to Vivienne at
PCBWay Online Services, body starting with the word `EQ`, cc as received. Then wait for a
photo of one reworked board before they run the other four.

## The 2026-09-11 EQ in one paragraph

PCBWay photographed a finished board and asked us to check component orientation. Both 1 × 10
sockets are fitted on the **top** face, openings up; they belong on the **bottom**, body
hanging below the board, soldered on top. **§6.1's stack table is the proof** — the 8.50 mm
between the header plastic at z = 4.12 and the hat underside at z = 12.62 *is* the socket
body. As built, the Olimex pins never reach the board. **It is our error, not PCBWay's:**
`PCBWay-README.txt` said "sides populated: top only", the footprints are on `F.Cu`, and the
centroid carries SMD rows only, so the mounting side existed nowhere a factory could read it.
Rework needs no PCB change and no BOM change. Full analysis in **§A3**.

## What you may trust

- **Everything else in the sample photos is correct**, checked 2026-09-11 against the BOM and
  against pad-level geometry parsed out of `pcb/af4-trigger-hat.kicad_pcb`: U1 pin 1 top-left,
  U2 tab left, D1 cathode band bottom, D2 cathode band top, C2 positive stripe right, all
  seven resistor codes, J1 and J2 joint counts, all 21 designators populated. → §A3
- **§2 arithmetic, all `[CAD]` geometry, all 20 MPNs, DRC, BOM ≡ centroid ≡ board.**
  Independently re-derived 2026-08-28 and re-run 2026-08-31. The J3/J4 error is *not* a
  contradiction of this: mounting side is not a quantity any of those checks covers.
- **The firmware matches §5 exactly**, and the flashed device matches `firmware/af4-feeder.yaml`.
  Diffed line by line 2026-09-03: content-identical, all four values on `!secret`.
- **The commissioning bands** (6.2 = 11.4–12.0 V, 6.3 = 10.0–10.9 V) — widened 2026-09-01 on
  measured evidence. As originally written they would each have failed a good board.
- **Both reef automations as §5.7 now describes them** — read from the live HA config 2026-09-02.

## What you may not trust

- **D3 and D5 polarity on the built boards is unverified.** The 0805 water-clear packages show
  no cathode mark at the photos' resolution. Referred to PCBWay; otherwise it falls out at
  commissioning 6.1 and 6.5. → item 25
- **Through-hole workmanship on the sample was mediocre** — flux residue, loose solder balls, a
  solder splash near J2, excess on the last pin of each socket row, and blade slots that look
  low on fill. All raised in the same reply. Inspect the reworked boards on arrival.
- **The enclosure's own 13+3 interference checks are script-reported, not independently re-run.**
- **Silkscreen on the five boards reads "10.4V 10s pulse"** — wrong, corrected in
  `pcb/gen_pcb.py` for any future rev, unfixable on this run.
- **LM1117 V_REF sub-bands and the LED viewing angle** were never re-pulled from the primary PDFs.
- **`pcbnew` is not installed on the Mac**, so `pcb/make_package.py` cannot be re-run locally. → §9.1

## Standing corrections — settled, do not re-raise

- 🚫 **Item 17 (missed-feed alert) does not exist and never did.** It was opened 2026-09-02 and
  withdrawn the same day: `automation.reef_tank_feeder_health_watchdog` has done the job since
  2026-08-27. Work that exists in reality but not in the repo reads as an open item. → §7.1
- 🚫 **Item 11 (flash the firmware) is closed.** Done 2026-09-01; the row was stale for a day.
- 🚫 **Plaintext credentials in the Device Builder are gone**, verified 2026-09-03. The
  archived handoff called this "item 8"; in §8's registry item 8 is a closed measurement and
  this work is part of **item 16**. What remains is the OTA password, tracked below as 16.
- 🚫 **The U1 land-pattern axis assignment was confirmed visually by Kenny on 2026-08-31.**
  It is not re-derivable by tooling and must not be quietly re-opened. → §A1.1
- 🚫 **The J3/J4 error is not a PCBWay fault and not a substitution.** The no-substitutions
  fence was never tripped; they built the package as supplied. Do not raise it as a quality
  complaint or ask for a credit. → §A3
- ⚠️ **Item numbers are `aF4-MASTER-REFERENCE.md` §8 numbers.** The archived handoff used a
  second, conflicting numbering for the same items — its "item 3" is §8's item 12, its "item 8"
  is item 16, its "item 14" is item 18. **§8's numbering is the only one.** If you find a
  citation that does not match §8, it came from `archive/aF4-HANDOFF.md`.

## Open items — by consequence

| # | Item | Blocks |
|---|---|---|
| 23 | **Send the EQ reply, then confirm a photo of one reworked board.** Text is written and ready in `pcb/pcbway-EQ-2026-09-11-reply.md`. Every day it sits unsent is a day of build clock | **Shipping — and it is the only thing on the critical path this week** |
| — | **Plumb the reef system.** Upstream of the scheduled-feed path and of commissioning's wet steps. **Still the real long pole**, and the rework has bought it time | **Go-live** |
| 12 | **Solder two 1×10 male headers into EXT1/EXT2, pins up.** Can be done now. Needs no parts you don't have. Pairs with item 16 in one bench session | **Assembly** |
| 15 | **Commissioning 6.1–6.8 all pass** before the schedule toggle goes on. Not gated on plumbing: only the automations carry the return interlock, `button.af4_feeder_feed` does not, so bench commissioning can proceed with the tank dry | **Go-live** |
| 16 | **Rotate `af4_ota_password` during the item-12 serial flash.** The device still holds the value published in git history; ESPHome authenticates the upload with the password already on the board, so it cannot rotate over the air. Do both in one motion, then delete the old value from `firmware/secrets.yaml` **and** the Device Builder Secrets editor. **The last live remnant of the 2026-09-02 exposure** | No — but it is a live exposure |
| 24 | **Fix the cause of item 23:** J3/J4 footprints to `B.Cu`, silkscreen to `B.SilkS`, name the face by designator in `PCBWay-README.txt`, add THT parts to the centroid with a side column | No — but nothing else stops item 23 recurring |
| 25 | **D3/D5 polarity unverified on the built boards.** Confirm with PCBWay during rework, or fall back to commissioning 6.1 and 6.5 | No — a reversed indicator fails to light and does not touch the trigger path |
| 20 | **No dispense confirmation.** Everything in §5 confirms the pulse was *sent*; nothing confirms food came out. An over-temperature fault would be invisible and never self-clears. A power-monitoring smart plug on the 12 V supply is the only fix short of opening the unit | No — the last unmonitored failure direction |
| 21 | Read the recalculated ship date off the PCBWay order page **after the EQ closes** | No — cosmetic |
| 22 | `pcb/gen_pcb.py` stray "exclude from BOM/pos" flags on J2. Fold into item 24 | No |
| 14 | LED viewing-angle conflict, 120° vs 160°/140° → §2.6 | No — cosmetic |
| 18 | R5 to 0.25 W 0805 — **deferred, window closed** when the order was placed. Ships at 125 mW, ~77 % of rating; failure mode is benign | No — closed for this build |
| — | Bench leftovers: A4's V_loaded half, A5 under power, A6 decay, B1/B2/B3. **None can change the board.** B3 has the real information value | No |

**Out of scope**, decided 2026-09-01: eWeLink → Home Assistant integration.

### Carried to the next board revision

- **J3/J4 footprints onto `B.Cu`** (item 24). This is now the first line of the list.
- **C1 replacement.** `GRM31CR61H106KA12L` is EOL at DigiKey with 0 stock and all three direct
  substitutes are also 0 stock. Pick a currently-active 10 µF 50 V X5R/X7R 1206 with real stock
  on **both** sides.
- **R5 to 0.25 W** (item 18).
- **J1/J2 sourcing.** Both Same Sky (CUI): deep DigiKey stock, thin in the Chinese channel — which
  is what drove the 26–28 day assembly build, though PCBWay had them in stock by 2026-09-10.
  Consider LCSC-stocked parts, or plan to consign.
- **Fab notes: give slot widths as the full set, never a lone minimum.** "Route at 0.70 mm as
  drawn" is what triggered the 2026-09-02 engineer question; the eight slots span 0.70 **and**
  0.80 mm.
- **Consider shipping separate PTH and NPTH drill files.**

## Last session — 2026-09-11

PCBWay sent assembly sample photos at 04:04 ET asking us to check orientation. Checked every
designator against the BOM and against pad-level geometry parsed out of the `.kicad_pcb`,
locating parts in the photographs by fitting a homography from the four board corners to the
KiCad frame. Found **J3 and J4 built on the top face when they mount from the bottom** — a
defect that is invisible to Gerbers, absent from an SMD-only centroid, and was contradicted by
our own "sides populated: top only" fab note. Wrote the reply and the analysis to
`pcb/pcbway-EQ-2026-09-11-reply.md`, opened §A3 as a third build blocker, and added items
23–25. Everything else in the photos verified correct.
