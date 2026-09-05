# STATUS — aF4 PoE Trigger

**Rewritten 2026-09-05.** The only live-status document in this project. Rewrite it; never
append to it. If it passes ~120 lines, something in it belongs in `aF4-MASTER-REFERENCE.md`.

## Phase

**Boards in fabrication. Firmware and HA software done. Nothing to do at PCBWay.**

| | |
|---|---|
| Boards | Ordered — PCBWay `YB1800644`, placed 2026-09-02, $169.95, 5 pcs assembled |
| Fabrication | Running. Engineer question raised 09-02, **closed 09-03**; no board change was needed |
| Assembly | 26–28 day build — the long pole on PCBWay's side |
| Expected | Ship ~2026-09-30, receipt early October |
| Firmware | **Complete and flashed**, bench-verified 2026-09-01 |
| HA software | **Complete**, verified against the live instance 2026-09-02 |
| Enclosure | Modelled, fit-checked digitally, printable |
| Go-live | `input_boolean.reef_af4_schedule_enabled` stays **OFF** until commissioning 6.1–6.8 pass |

The next external event worth acting on is the shipping notification.

## What you may trust

- **§2 arithmetic, all `[CAD]` geometry, all 20 MPNs, DRC, BOM ≡ centroid ≡ board.**
  Independently re-derived 2026-08-28 and re-run 2026-08-31.
- **The firmware matches §5 exactly**, and the flashed device matches `firmware/af4-feeder.yaml`.
  Diffed line by line 2026-09-03: content-identical, all four values on `!secret`.
- **The commissioning bands** (6.2 = 11.4–12.0 V, 6.3 = 10.0–10.9 V) — widened 2026-09-01 on
  measured evidence. As originally written they would each have failed a good board.
- **Both reef automations as §5.7 now describes them** — read from the live HA config 2026-09-02.

## What you may not trust

- **The enclosure's own 13+3 interference checks are script-reported, not independently re-run.**
- **Silkscreen on the five boards in fabrication reads "10.4V 10s pulse"** — wrong, corrected in
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
- ⚠️ **Item numbers are `aF4-MASTER-REFERENCE.md` §8 numbers.** The archived handoff used a
  second, conflicting numbering for the same items — its "item 3" is §8's item 12, its "item 8"
  is item 16, its "item 14" is item 18. **§8's numbering is the only one.** If you find a
  citation that does not match §8, it came from `archive/aF4-HANDOFF.md`.

## Open items — by consequence

| # | Item | Blocks |
|---|---|---|
| — | **Plumb the reef system.** Upstream of the scheduled-feed path and of commissioning's wet steps. **The real long pole** — boards arrive early October | **Go-live** |
| 12 | **Solder two 1×10 male headers into EXT1/EXT2, pins up.** Can be done now, while the boards are in fabrication. Needs no parts you don't have | **Assembly** |
| 15 | **Commissioning 6.1–6.8 all pass** before the schedule toggle goes on. Not gated on plumbing: only the automations carry the return interlock, `button.af4_feeder_feed` does not, so bench commissioning can proceed with the tank dry | **Go-live** |
| 16 | **Rotate `af4_ota_password` during the item-12 serial flash.** The device still holds the value published in git history; ESPHome authenticates the upload with the password already on the board, so it cannot rotate over the air. The board is on the bench for the headers anyway — do both in one motion, then delete the old value from `firmware/secrets.yaml` **and** the Device Builder Secrets editor. **The last live remnant of the 2026-09-02 exposure** | No — but it is a live exposure |
| 20 | **No dispense confirmation.** Everything in §5 confirms the pulse was *sent*; nothing confirms food came out. An over-temperature fault would be invisible and never self-clears. A power-monitoring smart plug on the 12 V supply is the only fix short of opening the unit | No — the last unmonitored failure direction |
| 21 | Read the recalculated ship date off the PCBWay order page | No — cosmetic |
| 22 | `pcb/gen_pcb.py` stray "exclude from BOM/pos" flags on J2 | No |
| 14 | LED viewing-angle conflict, 120° vs 160°/140° → §2.6 | No — cosmetic |
| 18 | R5 to 0.25 W 0805 — **deferred, window closed** when the order was placed. Ships at 125 mW, ~77 % of rating; failure mode is benign | No — closed for this build |
| — | Bench leftovers: A4's V_loaded half, A5 under power, A6 decay, B1/B2/B3. **None can change the board.** B3 has the real information value | No |

**Out of scope**, decided 2026-09-01: eWeLink → Home Assistant integration.

### Carried to the next board revision

- **C1 replacement.** `GRM31CR61H106KA12L` is EOL at DigiKey with 0 stock and all three direct
  substitutes are also 0 stock. Pick a currently-active 10 µF 50 V X5R/X7R 1206 with real stock
  on **both** sides.
- **R5 to 0.25 W** (item 18).
- **J1/J2 sourcing.** Both Same Sky (CUI): deep DigiKey stock, thin in the Chinese channel — which
  is what drove the 26–28 day assembly build. Consider LCSC-stocked parts, or plan to consign.
- **Fab notes: give slot widths as the full set, never a lone minimum.** "Route at 0.70 mm as
  drawn" is what triggered the 2026-09-02 engineer question; the eight slots span 0.70 **and**
  0.80 mm.
- **Consider shipping separate PTH and NPTH drill files.**

## Last session — 2026-09-05

Restructured the documentation layer so a new session costs ~6 K tokens on entry instead of
~27 K. Split durable priming into `.claude/CLAUDE.md` and live state into this file; numbered
every `###` subhead in `aF4-MASTER-REFERENCE.md` and gave it a section index; moved the three
dated reviews and the superseded handoff into `archive/`; filed the root into `docs/`,
`firmware/`, `hardware/`, `reference/`; rewrote and verified every path reference. Adopted the
delete-grant git practice (`docs/git-rules.md`), installed the `commit-msg` hook this repo did
not have, and cleared a `.git/index.lock` stranded since 09-03.
