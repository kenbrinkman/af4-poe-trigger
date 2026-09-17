# STATUS — aF4 PoE Trigger

**Rewritten 2026-09-17.** The only live-status document in this project. Rewrite it; never
append to it. If it passes ~120 lines, something in it belongs in `aF4-MASTER-REFERENCE.md`.

## Phase

**🟡 Boards in transit since 2026-09-14. The case and lid are reprinted (2026-09-17) with the
1.5 mm hat lift that clears the Olimex capacitor and the portrait lid label. Left before the boards
land: cut the two PoE light pipes to 24.2 mm.** → item 27, §6.3, §6.4

| | |
|---|---|
| Boards | PCBWay `YB1800644`, 5 pcs assembled, **shipped 2026-09-14, DHL (DTP)**. No delivery date is published; DHL Express out of China typically runs 3–6 business days, so *roughly* 09-18 to 09-23 — a band, not a commitment. Tracking number deliberately not chased → §A3.2 |
| Firmware | **Complete and flashed**, bench-verified 2026-09-01 |
| HA software | **Complete**, verified against the live instance 2026-09-02 |
| Enclosure | **Reprinted 2026-09-17** — case at the 1.5 mm hat lift (39.9 mm tall), lid with the portrait label. Both from the exports verified 2026-09-16: every script check, all six solid tests, `verify_enclosure.py` ALL CHECKS PASSED (label rot 180, IoU 0.72). PoE light pipes still to cut → item 27 |
| Go-live | `input_boolean.reef_af4_schedule_enabled` stays **OFF** until commissioning 6.1–6.8 pass |

**The immediate thread:** cut the two PoE light pipes to 24.2 mm — before the boards land. When the box arrives, **one bench session still covers items 26, 12 and 16**.

## The 2026-09-16 finding in one paragraph

Dry-fitting headers to a spare ESP32-POE-ISO, Kenny found the header plastic had to be forced in
beside the black DCDC1 module and questioned the hat's clearance there. Calipers from the
ESP32's bottom face (= z 0 in the stack) put the **cap beside DCDC1 at 13.4 mm, DCDC1 at 11.5,
UEXT1 at 11.2** — against a hat underside at 12.62. The enclosure script had checked the hat
against a hand-typed **4.40 mm** UEXT height, so no tall Olimex part had ever been tested. **The
hat now sits 1.50 mm higher** (`HAT_LIFT`; underside 14.12, lid underside 25.00), clearing the cap
by 0.72 mm at the cost of pin engagement ~5.8 → ~4.3 mm. Mounting the ESP32 upside down was
considered first and rejected: it mirrors the EXT pinout and the hat's ground lands on no ground
pin in any orientation. Full record in **§6.3**.

## What you may trust

- **The three measured heights and the clearances derived from them** — calipered 2026-09-16, and
  within ~0.5 mm of Olimex's own mesh. → §6.3
- **The scalar checks in `hardware/enclosure/af4_enclosure_ocp.py` at the new height** — all pass,
  re-run 2026-09-16 by executing the parameter and check sections without OCP.
- **The regenerated enclosure exports** — Mac, OCP 8.0.1, 2026-09-16: all script checks and six
  solid tests pass, and `verify_enclosure.py` passes them independently. (The lid export has since
  been superseded by the label rotation, §6.4.)
- **`hardware/enclosure/verify_enclosure.py`** — numpy only, runs in any shell. Validated against
  the old exports first: it passed them at the old parameters and independently found the cap
  collision from the vendor mesh (13.15 vs 12.62).
- **The EXT1/EXT2 pin assignments** — read 2026-09-16 from Olimex's `ESP32-PoE-ISO_Rev_N.kicad_pcb`.
- **The shipment itself**, read off the order page 2026-09-14. → §A3.2
- **The reworked sample's mounting face, seating and pin 1** (2026-09-12), and everything else in
  the original sample photos (2026-09-11). → §A3, §A3.1
- **§2 arithmetic, all `[CAD]` board geometry, all 20 MPNs, DRC, BOM ≡ centroid ≡ board.**
- **The firmware matches §5 exactly**, and the flashed device matches `firmware/af4-feeder.yaml`.
- **The commissioning bands** (6.2 = 11.4–12.0 V, 6.3 = 10.0–10.9 V).
- **Both reef automations as §5.7 describes them.**

## What you may not trust

- ⚠️ **The old pre-lift case**, if it is still around. Do not assemble into it. The reprint is
  the one to use. → item 27
- **The reprinted case has not been dry-fitted.** It is printed from verified exports, but the
  0.72 mm cap clearance is first physically checked at the item-12 dry-fit.
- **The enclosure scripts run only on the Mac**, in `~/.venvs/cad`, and need the OCP 8
  compatibility block now in both. Claude Code sessions run there too. → §9.2
- **Pin engagement of ~4.3 mm is calculated, not felt.** Check the hat's grip on the headers at
  the first dry-fit. A longer-pin header restores depth if it is loose.
- **The DCDC1 end of EXT2.** The vendor model shows ~0.65 mm to the header plastic; the real part
  needed force. The hat's J4 socket meets the same face. Shave the plastic, don't force it.
- **No delivery date exists.** The 09-29 reminder on the order page is stale. Do not quote it.
- **Only board 1 of five was ever photographed**; the ten J3 joints are ungraded; every board ships
  with pin-10 excess solder and flux residue. → item 26
- **D3 and D5 polarity** is unverified until commissioning. → item 25
- **Silkscreen reads "10.4V 10s pulse"** — wrong, unfixable on this run.
- **LM1117 V_REF sub-bands and the LED viewing angle** were never re-pulled from primary PDFs.
- **`pcbnew` via KiCad 9.0.7 is available but unexercised** on this board, which KiCad 7-era
  tooling produced. Diff the first regenerated `.kicad_pcb` and `drc.rpt` before trusting it. → §9.2

## Standing corrections — settled, do not re-raise

- 🚫 **Do not mount the ESP32 bottom side up.** It mirrors the EXT pinout; no orientation connects
  the hat's ground. → §6.3
- 🚫 **Do not press the hat fully home on the headers outside the case.** The standoffs set its
  height now; without them it bottoms on the header plastic and lands on the cap. → §6.3
- 🚫 **The EQ thread is closed and the order has shipped.** No follow-ups to Ivy or Online
  Services, no D3/D5 question. → §A3.2
- 🚫 **In `pcb/BOARD REVIEW EQ/`, `rejected-sample-2026-09-11-*` is the board turned down**;
  `rework-2026-09-12-*` is the accepted one. → §A3.1
- 🚫 **The J3/J4 error was ours, not PCBWay's.** No complaint, no credit request. → §A3
- 🚫 **Item 17 does not exist and never did.** → §7.1
- 🚫 **The U1 land-pattern axis assignment was confirmed visually by Kenny on 2026-08-31.** → §A1.1
- ⚠️ **Item numbers are `aF4-MASTER-REFERENCE.md` §8 numbers** — the only numbering.

## Open items — by consequence

| # | Item | Blocks |
|---|---|---|
| 27 | **Case and lid reprinted 2026-09-17.** Still open: cut the PoE light pipes at 24.2 mm (hat pipes unchanged, 10.1); move the hat up 1.5 mm in Tinkercad | **Assembly** — light pipes only |
| 26 | **Inspect all five on arrival and pick the best board** — check the J3/J4 face on each. Reflow the two pin-10 joints, clean with IPA, loupe the ten J3 joints | **The first thing when the box lands** |
| 12 | **Solder two 1×10 male headers into EXT1/EXT2, pins up, plastic on the top face.** Shave the pin-10 end of the EXT2 plastic if it binds on DCDC1. Same bench session as 26 and 16 | **Assembly** |
| 16 | **Rotate `af4_ota_password` during the item-12 serial flash**, then delete the old value from `firmware/secrets.yaml` **and** the Device Builder Secrets editor | No — but a live exposure |
| — | **Plumb the reef system.** The long pole | **Go-live** |
| 15 | **Commissioning 6.1–6.8 all pass** before the schedule toggle goes on. Can run dry on the bench | **Go-live** |
| 24 | **Fix the cause of the J3/J4 error:** footprints to `B.Cu`, silkscreen to `B.SilkS`, face named in `PCBWay-README.txt`, THT parts in the centroid with a side column | No |
| 25 | **D3/D5 polarity** resolves at commissioning 6.1 and 6.5 | No |
| 20 | **No dispense confirmation.** A power-monitoring smart plug on the 12 V supply is the only fix short of opening the unit | No — the last unmonitored failure direction |
| 22 | `pcb/gen_pcb.py` stray "exclude from BOM/pos" flags on J2. Fold into item 24 | No |
| 14 | LED viewing-angle conflict → §2.6 | No — cosmetic |
| 18 | R5 to 0.25 W — deferred, window closed | No |
| — | Bench leftovers: A4's V_loaded half, A5 under power, A6 decay, B1/B2/B3 | No |

**Out of scope**, decided 2026-09-01: eWeLink → Home Assistant integration.

### Carried to the next board revision

- **J3/J4 footprints onto `B.Cu`** (item 24).
- **Keep the hat's bottom face clear over enclosure x 111.5–118.5, y −161.5 to −155** — the
  Olimex cap sits there. A notch in the outline would let a future rev drop the 1.5 mm lift.
- **C1 replacement** — `GRM31CR61H106KA12L` is EOL with no stock on the substitutes.
- **R5 to 0.25 W** (item 18). **J1/J2 sourcing** — consider LCSC-stocked parts.
- **Fab notes: give slot widths as the full set**, and consider separate PTH/NPTH drill files.

## Last session — 2026-09-17

Kenny reported the case and lid reprinted; recorded against item 27 in `STATUS.md` and the §8
registry, with a line in §6.4. No hardware verification in-session. Earlier the same day: first
session in **Claude Code on the Mac** (toolchain checked and recorded in **§9.2**; settings, hooks
and `tools/section_index.py` added; `docs/git-rules.md` §1, §2, §6 rewritten).
