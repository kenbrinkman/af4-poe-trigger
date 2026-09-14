# STATUS — aF4 PoE Trigger

**Rewritten 2026-09-14.** The only live-status document in this project. Rewrite it; never
append to it. If it passes ~120 lines, something in it belongs in `aF4-MASTER-REFERENCE.md`.

## Phase

**🟢 All five boards shipped 2026-09-14. Nothing is owed to PCBWay and nothing is waiting on
them. The next action is a bench session on the day the box lands.**

| | |
|---|---|
| Boards | PCBWay `YB1800644`, placed 2026-09-02, $169.95, 5 pcs assembled |
| Fabrication | **Done.** Bare PCB `W1125728AS3P5` hit 100 % on 2026-09-10 |
| Assembly | **Done.** Sample rejected 09-11, reworked and accepted 09-12, the other four built after |
| Shipped | **2026-09-14, DHL (DTP).** Tracking number not yet posted — deliberately not chased. → §A3.2 |
| Arrival | **No delivery date is published anywhere.** DHL Express out of China typically runs 3–6 business days, so *roughly* 09-18 to 09-23. A band, not a commitment |
| Firmware | **Complete and flashed**, bench-verified 2026-09-01 |
| HA software | **Complete**, verified against the live instance 2026-09-02 |
| Enclosure | Modelled, fit-checked digitally, printable |
| Go-live | `input_boolean.reef_af4_schedule_enabled` stays **OFF** until commissioning 6.1–6.8 pass |

**The immediate thread:** nothing at all until the box arrives — this is the first time since
2026-08-28 that no action is outstanding. When it lands, **one bench session covers items 26, 12
and 16**: inspect all five and pick the best board, reflow the two pin-10 joints and clean them
with IPA, loupe the ten ungraded J3 joints, solder the EXT1/EXT2 headers, then serial-flash and
rotate the OTA password in the same motion. Commissioning 6.1–6.8 follows on the same bench, dry.

## The 2026-09-14 shipment in one paragraph

The order page reads **"This order was Shipped (Awaiting delivery)"**, with the logistics table
showing DHL (DTP) and a shipping date of 2026-09-14 — **12 days after the order was placed,
against a quoted 26–28 day lead time and two engineer questions that each restarted the build
clock.** The page's "Estimated Finish Time 2026-09-29" reminder was never recalculated and is now
stale; **the status line and the logistics table are the live fields, the reminder is not.** The
tracking-number column is still blank, which is normal a day either side of a status flip.
Full record in **§A3.2**.

## What you may trust

- **The shipment itself**, read off the order page 2026-09-14: status, carrier, ship date. → §A3.2
- **The reworked board's mounting face, seating and pin 1**, checked 2026-09-12 against §6.1's
  stack table and the earlier pad-level geometry. The apparent J3 overhang past the board edge
  in the bottom-face photo is perspective on an 8.50 mm body, not offset. → §A3.1
- **Everything else in the original sample photos** — U1/U2 orientation, D1/D2 bands, C2 stripe,
  all seven resistor codes, all 21 designators populated — checked 2026-09-11 against the BOM and
  against geometry parsed from `pcb/af4-trigger-hat.kicad_pcb`. → §A3
- **§2 arithmetic, all `[CAD]` geometry, all 20 MPNs, DRC, BOM ≡ centroid ≡ board.**
  Independently re-derived 2026-08-28 and re-run 2026-08-31.
- **The firmware matches §5 exactly**, and the flashed device matches `firmware/af4-feeder.yaml`
  — diffed line by line 2026-09-03, content-identical, all four values on `!secret`.
- **The commissioning bands** (6.2 = 11.4–12.0 V, 6.3 = 10.0–10.9 V), widened 2026-09-01 on
  measured evidence — as originally written they would each have failed a good board.
- **Both reef automations as §5.7 now describes them** — read from the live HA config 2026-09-02.

## What you may not trust

- **No delivery date exists.** The 09-29 reminder on the order page is the pre-EQ finish estimate,
  not a delivery date, and it was never recalculated. **Do not quote it to anyone.** → §A3.2
- **The four boards other than the reworked sample were never photographed.** They are believed
  built to the corrected face because the rework was accepted as the pattern, but **only board 1
  has been seen.** Check the J3/J4 face on every board before choosing one. → item 26
- **The ten J3 joints are ungraded.** That row was photographed at too oblique an angle to tell
  a poorly wetted barrel from a camera artefact. Check under a loupe on arrival. → item 26
- **Every board ships with two known defects** — pin-10 excess solder with burnt flux on both
  rows, and uncleaned flux residue on the bottom face at that end. Accepted deliberately, not
  overlooked. → item 26
- **D3 and D5 polarity is unverified and will stay that way until commissioning.** → item 25
- **The enclosure's own 13+3 interference checks are script-reported, not independently re-run.**
- **Silkscreen on the five boards reads "10.4V 10s pulse"** — wrong, corrected in
  `pcb/gen_pcb.py` for any future rev, unfixable on this run.
- **LM1117 V_REF sub-bands and the LED viewing angle** were never re-pulled from the primary PDFs.
- **`pcbnew` is not installed on the Mac**, so `pcb/make_package.py` cannot be re-run locally. → §9.1

## Standing corrections — settled, do not re-raise

- 🚫 **The EQ thread is closed and the order has shipped.** Do not re-open it, do not send a
  follow-up to Ivy or to Online Services, and do not ask about D3/D5. → §A3.2
- 🚫 **In `pcb/BOARD REVIEW EQ/`, the `rejected-sample-2026-09-11-*` pair is the board that was
  turned down** — both sockets standing on the top face. The accepted board is
  `rework-2026-09-12-*`. The folder's `README.md` says which is which. → §A3.1
- 🚫 **The J3/J4 error was not a PCBWay fault and not a substitution.** They built the package as
  supplied. Do not raise it as a quality complaint or ask for a credit. → §A3
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
| 26 | **Inspect all five on arrival and pick the best board** — check the J3/J4 face on each, do not assume board 1. Reflow the two pin-10 joints, clean with IPA, loupe the ten J3 joints | **The first thing that happens when the box lands** |
| 12 | **Solder two 1×10 male headers into EXT1/EXT2, pins up.** Same bench session as 26 and 16. Needs no parts you don't have | **Assembly** |
| 16 | **Rotate `af4_ota_password` during the item-12 serial flash.** The device still holds the value published in git history; ESPHome authenticates the upload with the password already on the board, so it cannot rotate over the air. Do both in one motion, then delete the old value from `firmware/secrets.yaml` **and** the Device Builder Secrets editor. **The last live remnant of the 2026-09-02 exposure** | No — but it is a live exposure |
| — | **Plumb the reef system.** Upstream of the scheduled-feed path and of commissioning's wet steps. **Now unambiguously the long pole** | **Go-live** |
| 15 | **Commissioning 6.1–6.8 all pass** before the schedule toggle goes on. Not gated on plumbing: only the automations carry the return interlock, `button.af4_feeder_feed` does not, so bench commissioning can proceed with the tank dry | **Go-live** |
| 24 | **Fix the cause of the J3/J4 error:** footprints to `B.Cu`, silkscreen to `B.SilkS`, name the face by designator in `PCBWay-README.txt`, add THT parts to the centroid with a side column | No — but nothing else stops it recurring |
| 25 | **D3/D5 polarity** resolves at commissioning 6.1 and 6.5 | No — a reversed indicator fails to light and does not touch the trigger path |
| 20 | **No dispense confirmation.** Everything in §5 confirms the pulse was *sent*; nothing confirms food came out. An over-temperature fault would be invisible and never self-clears. A power-monitoring smart plug on the 12 V supply is the only fix short of opening the unit | No — the last unmonitored failure direction |
| 22 | `pcb/gen_pcb.py` stray "exclude from BOM/pos" flags on J2. Fold into item 24 | No |
| 14 | LED viewing-angle conflict, 120° vs 160°/140° → §2.6 | No — cosmetic |
| 18 | R5 to 0.25 W 0805 — **deferred, window closed** when the order was placed. Ships at 125 mW, ~77 % of rating; failure mode is benign | No — closed for this build |
| — | Bench leftovers: A4's V_loaded half, A5 under power, A6 decay, B1/B2/B3. **None can change the board.** B3 has the real information value | No |

**Closed since the last rewrite:** item 21 — the recalculated ship date. The page never published
one; the shipment overtook the question. → §A3.2

**Out of scope**, decided 2026-09-01: eWeLink → Home Assistant integration.

### Carried to the next board revision

- **J3/J4 footprints onto `B.Cu`** (item 24). Still the first line of the list.
- **C1 replacement.** `GRM31CR61H106KA12L` is EOL at DigiKey with 0 stock and all three direct
  substitutes are also 0 stock. Pick a currently-active 10 µF 50 V X5R/X7R 1206 with real stock
  on **both** sides.
- **R5 to 0.25 W** (item 18).
- **J1/J2 sourcing.** Both Same Sky (CUI): deep DigiKey stock, thin in the Chinese channel —
  which is what drove the 26–28 day assembly quote. Consider LCSC-stocked parts, or consign.
- **Fab notes: give slot widths as the full set, never a lone minimum.** "Route at 0.70 mm as
  drawn" is what triggered the 2026-09-02 engineer question; the eight slots span 0.70 **and**
  0.80 mm.
- **Consider shipping separate PTH and NPTH drill files.**

## Last session — 2026-09-14

Read the shipment off the PCBWay order page: **Shipped (Awaiting delivery)**, DHL (DTP),
2026-09-14, tracking number still blank. Opened **§A3.2**, closing the A3 engineer-question
thread and recording the three things worth carrying: the order shipped **12 days after
placement against a 26–28 day quote**; the page's "Estimated Finish Time" reminder is never
recalculated and must not be read as a delivery date; only board 1 was ever photographed.
Closed item 21 as overtaken by events, decided not to chase the waybill, and rewrote the
open-item table so the arrival bench session — 26, 12 and 16 in one sitting — is the top line.
