# STATUS — aF4 PoE Trigger

**Rewritten 2026-09-12.** The only live-status document in this project. Rewrite it; never
append to it. If it passes ~120 lines, something in it belongs in `aF4-MASTER-REFERENCE.md`.

## Phase

**🟡 Rework verified and accepted. The J3/J4 blocker is closed. One thing to do: send the
acceptance reply so the EQ closes and the build clock restarts.**

| | |
|---|---|
| Boards | PCBWay `YB1800644`, placed 2026-09-02, $169.95, 5 pcs assembled |
| Fabrication | **Done.** Bare PCB `W1125728AS3P5` hit 100 % on 2026-09-10 |
| Assembly | **Sample rejected 2026-09-11, reworked and verified 2026-09-12.** J3/J4 now on the bottom face, joints on top, seated flush and square. Other four still to be reworked |
| Expected | **Unknown — do not quote a date.** The clock restarts at the end of this EQ |
| Firmware | **Complete and flashed**, bench-verified 2026-09-01 |
| HA software | **Complete**, verified against the live instance 2026-09-02 |
| Enclosure | Modelled, fit-checked digitally, printable |
| Go-live | `input_boolean.reef_af4_schedule_enabled` stays **OFF** until commissioning 6.1–6.8 pass |

**The immediate thread:** send the reply in `pcb/pcbway-EQ-2026-09-12-rework-accepted.md` to
Vivienne at PCBWay Online Services, body starting with the word `EQ`, cc as received. It
approves the rework, releases them to build and ship the other four, and explicitly tells them
no further photo and no D3/D5 answer is needed — so nothing in it can hold the EQ open.

## The 2026-09-12 acceptance in one paragraph

PCBWay reworked one board and photographed both faces. **The defect is fixed:** socket bodies
on the bottom, pin tails and solder on the top, pin 1 unmoved, both flush and square, R1/R2
undamaged, isolation band clean. Two things from the 09-11 reply were **not** fixed — pin 10 of
each socket row is a dull blob with burnt flux, and the bottom face is uncleaned at that end —
and **Kenny's call on 2026-09-12 was to accept both rather than spend another rework round**.
Five boards are being built, one is needed, and both defects are five minutes with an iron and
IPA. Full inspection record in **§A3.1**.

## What you may trust

- **The reworked board's mounting face, seating and pin 1**, checked 2026-09-12 against §6.1's
  stack table and the earlier pad-level geometry. The apparent J3 overhang past the board edge
  in the bottom-face photo is perspective on an 8.50 mm body, not offset. → §A3.1
- **Everything else in the original sample photos**, checked 2026-09-11 against the BOM and
  against geometry parsed from `pcb/af4-trigger-hat.kicad_pcb`: U1 pin 1 top-left, U2 tab left,
  D1 cathode band bottom, D2 band top, C2 positive stripe right, all seven resistor codes, J1
  and J2 joint counts, all 21 designators populated. → §A3
- **§2 arithmetic, all `[CAD]` geometry, all 20 MPNs, DRC, BOM ≡ centroid ≡ board.**
  Independently re-derived 2026-08-28 and re-run 2026-08-31.
- **The firmware matches §5 exactly**, and the flashed device matches `firmware/af4-feeder.yaml`.
  Diffed line by line 2026-09-03: content-identical, all four values on `!secret`.
- **The commissioning bands** (6.2 = 11.4–12.0 V, 6.3 = 10.0–10.9 V) — widened 2026-09-01 on
  measured evidence. As originally written they would each have failed a good board.
- **Both reef automations as §5.7 now describes them** — read from the live HA config 2026-09-02.

## What you may not trust

- **The ten J3 joints are ungraded.** That row is photographed at too oblique an angle to tell
  a poorly wetted barrel from a camera artefact. Check it under a loupe on arrival. → item 26
- **Every board ships with two known defects** — pin-10 excess solder with burnt flux on both
  rows, and uncleaned flux residue on the bottom face at that end. Accepted deliberately, not
  overlooked. → item 26
- **D3 and D5 polarity is unverified and will stay that way until commissioning.** The 0805
  water-clear packages show no cathode mark at either photo set's resolution, and the question
  was released on 09-12 rather than left to hold the EQ open. → item 25
- **The enclosure's own 13+3 interference checks are script-reported, not independently re-run.**
- **Silkscreen on the five boards reads "10.4V 10s pulse"** — wrong, corrected in
  `pcb/gen_pcb.py` for any future rev, unfixable on this run.
- **LM1117 V_REF sub-bands and the LED viewing angle** were never re-pulled from the primary PDFs.
- **`pcbnew` is not installed on the Mac**, so `pcb/make_package.py` cannot be re-run locally. → §9.1

## Standing corrections — settled, do not re-raise

- 🚫 **In `pcb/BOARD REVIEW EQ/`, the `rejected-sample-2026-09-11-*` pair is the board that was
  turned down** — both sockets standing on the top face. The accepted board is
  `rework-2026-09-12-*`. They were one filename apart until 09-12; the folder's `README.md` now
  says which is which. → §A3.1
- 🚫 **The J3/J4 error was not a PCBWay fault and not a substitution.** They built the package as
  supplied. Do not raise it as a quality complaint or ask for a credit. → §A3
- 🚫 **Do not ask PCBWay for a second rework.** Decided 2026-09-12 and recorded with reasoning in
  §A3.1. Every remaining defect is bench-repairable.
- 🚫 **Item 17 (missed-feed alert) does not exist and never did.** Opened 2026-09-02 and withdrawn
  the same day: `automation.reef_tank_feeder_health_watchdog` has done the job since 2026-08-27.
  Work that exists in reality but not in the repo reads as an open item. → §7.1
- 🚫 **Plaintext credentials in the Device Builder are gone**, verified 2026-09-03. What remains
  is the OTA password, tracked below as 16.
- 🚫 **The U1 land-pattern axis assignment was confirmed visually by Kenny on 2026-08-31.** Not
  re-derivable by tooling; must not be quietly re-opened. → §A1.1
- ⚠️ **Item numbers are `aF4-MASTER-REFERENCE.md` §8 numbers.** The archived handoff used a
  second, conflicting numbering: its "item 3" is §8's item 12, its "item 8" is item 16, its
  "item 14" is item 18. **§8's numbering is the only one.**

## Open items — by consequence

| # | Item | Blocks |
|---|---|---|
| — | **Send the acceptance reply.** Text ready in `pcb/pcbway-EQ-2026-09-12-rework-accepted.md`. Every day it sits unsent is a day of build clock | **Shipping — the only thing on the critical path this week** |
| — | **Plumb the reef system.** Upstream of the scheduled-feed path and of commissioning's wet steps. **Still the real long pole** | **Go-live** |
| 26 | **Inspect all five on arrival and pick the best board** — do not assume board 1. Reflow the two pin-10 joints, clean with IPA, loupe the ten J3 joints. Same bench session as items 12 and 16 | **Assembly quality** |
| 12 | **Solder two 1×10 male headers into EXT1/EXT2, pins up.** Can be done now. Needs no parts you don't have | **Assembly** |
| 15 | **Commissioning 6.1–6.8 all pass** before the schedule toggle goes on. Not gated on plumbing: only the automations carry the return interlock, `button.af4_feeder_feed` does not, so bench commissioning can proceed with the tank dry | **Go-live** |
| 16 | **Rotate `af4_ota_password` during the item-12 serial flash.** The device still holds the value published in git history; ESPHome authenticates the upload with the password already on the board, so it cannot rotate over the air. Do both in one motion, then delete the old value from `firmware/secrets.yaml` **and** the Device Builder Secrets editor. **The last live remnant of the 2026-09-02 exposure** | No — but it is a live exposure |
| 24 | **Fix the cause of the J3/J4 error:** footprints to `B.Cu`, silkscreen to `B.SilkS`, name the face by designator in `PCBWay-README.txt`, add THT parts to the centroid with a side column | No — but nothing else stops it recurring |
| 25 | **D3/D5 polarity** now resolves at commissioning 6.1 and 6.5 | No — a reversed indicator fails to light and does not touch the trigger path |
| 20 | **No dispense confirmation.** Everything in §5 confirms the pulse was *sent*; nothing confirms food came out. An over-temperature fault would be invisible and never self-clears. A power-monitoring smart plug on the 12 V supply is the only fix short of opening the unit | No — the last unmonitored failure direction |
| 21 | Read the recalculated ship date off the PCBWay order page **after the EQ closes** | No — cosmetic |
| 22 | `pcb/gen_pcb.py` stray "exclude from BOM/pos" flags on J2. Fold into item 24 | No |
| 14 | LED viewing-angle conflict, 120° vs 160°/140° → §2.6 | No — cosmetic |
| 18 | R5 to 0.25 W 0805 — **deferred, window closed** when the order was placed. Ships at 125 mW, ~77 % of rating; failure mode is benign | No — closed for this build |
| — | Bench leftovers: A4's V_loaded half, A5 under power, A6 decay, B1/B2/B3. **None can change the board.** B3 has the real information value | No |

**Out of scope**, decided 2026-09-01: eWeLink → Home Assistant integration.

### Carried to the next board revision

- **J3/J4 footprints onto `B.Cu`** (item 24). Still the first line of the list.
- **C1 replacement.** `GRM31CR61H106KA12L` is EOL at DigiKey with 0 stock and all three direct
  substitutes are also 0 stock. Pick a currently-active 10 µF 50 V X5R/X7R 1206 with real stock
  on **both** sides.
- **R5 to 0.25 W** (item 18).
- **J1/J2 sourcing.** Both Same Sky (CUI): deep DigiKey stock, thin in the Chinese channel —
  which is what drove the 26–28 day assembly build. Consider LCSC-stocked parts, or consign.
- **Fab notes: give slot widths as the full set, never a lone minimum.** "Route at 0.70 mm as
  drawn" is what triggered the 2026-09-02 engineer question; the eight slots span 0.70 **and**
  0.80 mm.
- **Consider shipping separate PTH and NPTH drill files.**

## Last session — 2026-09-12

Verified PCBWay's rework photographs: sockets on the bottom face, joints on top, pin 1 unmoved,
both flush and square, isolation band clean, R1/R2 undamaged. Established that the two files in
`pcb/BOARD REVIEW EQ/` were the *rejected* sample and not the reworked board, then renamed both
pairs and added a folder README so the trap cannot be walked into again. The pin-10 joints and the bottom-face flux were still unfixed and now look worse.
**Kenny accepted the board as-is rather than spend a second rework round**, on the reasoning
that five are being built, one is needed, and both defects are bench-repairable. Wrote the
acceptance reply, opened §A3.1, closed item 23, released item 25 to commissioning, and added
item 26 so the arrival inspection is an explicit step rather than an assumption.
