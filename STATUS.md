# STATUS — aF4 PoE Trigger

**Rewritten 2026-09-18 (evening).** The only live-status document in this project. Rewrite it;
never append to it. If it passes ~120 lines, something in it belongs in `aF4-MASTER-REFERENCE.md`.

## Phase

**🟢 The PoE board was swapped this evening and is live, commissioned and verified at
192.168.1.55.** The duplicate Olimex ESP32-POE-ISO is now the build board: flashed, adopted in
Home Assistant with all seven entity IDs intact, and — the part that matters — with the
**OTA path proven working**. Item 16 is closed. → §11

**🟠 Still standing from this morning: J1, the 12 V barrel jack, is rotated 180° on all five
hats.** The error is ours, in `pcb/gen_pcb.py`, not PCBWay's. Use all five as built, leave J1
fitted and dead, bring 12 V in through a panel-mount jack in the +X wall. → §A4

| | |
|---|---|
| Boards (hats) | **In hand, 5 pcs.** Electrically as designed; only the 12 V plug interface is unreachable. Not yet inspected → item 26 |
| ESP32 | **Replacement board flashed, on the network, adopted in HA** `[MEAS] 2026-09-18`. Ethernet MAC `00:70:07:7F:48:C3`, base MAC `00:70:07:7F:48:C0` |
| Firmware | **Complete**, matches §5. Running build `2026-09-18 18:07:52`, config hash `0xd4f82693` |
| Credentials | ✅ **All three rotated and verified.** OTA password rotated at the serial flash and proven by a live Device Builder OTA |
| HA software | **Complete**, re-verified against the live instance 2026-09-18. Unaffected by the swap |
| Enclosure | **Script changed and re-verified 2026-09-18** — old J1 hole removed, keyed D-hole added, cable tie post added. **The case must be reprinted** (item 29). ✅ **The lid does not** |
| 12 V wiring | **Soldered 2026-09-18** to J1's pad tails — red to pin 1, black to pin 2, pin 3 bare. ⚠️ **Polarity not yet confirmed with a meter** |
| Go-live | `input_boolean.reef_af4_schedule_enabled` stays **OFF** until commissioning 6.1–6.8 pass |

**Nothing is on order and nothing is waiting.**

1. **Confirm the 12 V polarity with a meter** — black tail to **TP4 is a dead short**. Ten seconds,
   and the only thing that settles it. ⚠️ Never the mirror test on red against TP1: F1 and D1 make
   a *correct* board read a diode drop.
2. **Print the case** (item 29) — the **lid is unchanged**. **Erase the retired ESP32** (item 30).
3. **At the bench:** items **26**, **12**, and the two PoE light pipes to 24.2 mm (item 27).

## The board swap in three lines

Only HA's config entry (keyed on MAC), the OPNsense reservation and the old board's own flash
ever knew which physical board this was. **Every board carries two MACs three apart** — HA
stores the base, DHCP reserves the Ethernet one, and both records were always right. HA's
*device conflict* repair → **"Migrate configuration to new device"** did the whole job. → §11

## What you may trust

- **The replacement board, end to end** `[MEAS] 2026-09-18`: lease `00:70:07:7f:48:c3 →
  192.168.1.55`, ping clean, API open on 6053, HA status `on`, lockout `off`, IP sensor reading
  `192.168.1.55`. All **four** consumers and the Reef Command dashboard resolve their entities.
- **The OTA path works.** A Device Builder install reached the board and rebooted it into build
  `18:07:52`. This is the check that had to pass *before the case closes* — there is no USB
  cutout, so after assembly OTA is the only way in. → §11.4
- **The Device Builder YAML is byte-identical to `firmware/af4-feeder.yaml`** — 196 lines, zero
  diff, verified 2026-09-18. The "Modified" badge was its secrets edit, not config drift.
- **The lid needs no reprint** — `aF4-trigger-lid.stl` checked byte-for-byte against `29f1682`.
- **The J1 diagnosis and the DC-099's calipered dimensions.** **Red is +12 V, black is −.**
- **The pad identification on the hat's underside** — the wider gap is the ground side. Confirm
  on the bench as **GND tail → TP4, a dead short**; ⚠️ never as red against TP1. → §A4
- **The enclosure at its new geometry**, re-run on the Mac 2026-09-18: every scalar check passes,
  all ten solid tests read 0 mm³, `verify_enclosure.py` passes independently. 65.2 × 117.0 × 39.9 mm.
- **Settled and re-checked:** heights under the hat and the 0.72 mm cap clearance (calipered
  09-16); §2 arithmetic, all `[CAD]` geometry, 20 MPNs, DRC, BOM ≡ centroid ≡ board; the ordered
  board on KiCad 9.0.7 (0 DRC errors, pixel-identical export); commissioning bands 6.2 =
  11.4–12.0 V and 6.3 = 10.0–10.9 V.

## What you may not trust

- ⚠️ **The 12 V polarity is soldered but unverified.** Photograph and datasheet agree; neither is
  a meter. Not dangerous either way — D1 blocks a reversal, so the symptom is D3 dark at 6.1.
- ⚠️ **The retired ESP32 is still flashed** and still holds the node name, a valid API key and an
  OTA password. Until item 30 it must not be powered on the LAN. Two boards answering to
  `af4-feeder` is a feed hazard, not a theoretical one.
- ⚠️ **Whichever hat carries the 12 V wires is the build board by default**, and item 26's
  inspection of all five has not happened. If that board fails inspection, the wires move.
- **Four `PJ_*` values are not calipered.** None shapes the printed hole; none gates a check.
- ⚠️ **The 2026-09-17 case print is retired** — old J1 hole, no panel-jack hole. The **lid** is good.
- **The 0.72 mm cap clearance and the ~4.3 mm pin engagement are calculated, not felt.**
- **The DCDC1 end of EXT2.** Vendor model shows ~0.65 mm to the header plastic; the real part
  needed force. Shave the plastic, don't force it.
- **Only board 1 of five was ever photographed**; ten J3 joints ungraded; pin-10 excess solder
  on every board (item 26). **D3/D5 polarity** unverified until commissioning (item 25).
- **Silkscreen reads "10.4V 10s pulse"** — wrong, unfixable on this run. **The enclosure scripts
  run only on the Mac** (§9.2), and **`gen_pcb.py` / `make_package.py` are un-rerun under KiCad 9.**

## Standing corrections — settled, do not re-raise

- 🚫 **Never compute the Ethernet MAC for a DHCP reservation — read it from the lease.** → §11.1
- 🚫 **On a board swap take HA's "Migrate configuration to new device."** Never delete and re-add
  the ESPHome entry; the entity IDs are load-bearing and all four consumers key on them. → §11.2
- 🚫 **An OTA password must be punctuation-free.** Two YAML files that *look* identical can
  resolve differently — `#` truncates unquoted. Compare by hash. → §11.4
- 🚫 **Never route the 12 V leads across the hat's right-hand edge.** 0.50 mm clearance; a lead
  there is crushed by the lid, invisibly. Down into the void, then along the floor. → §A4
- 🚫 **J1: leave it fitted and dead, plug nothing into it, and raise nothing with PCBWay** — the
  error is ours. No complaint, no credit request, no email. → §A4
- 🚫 **A check whose result is fixed by its own inputs is not a check.** → §A4
- 🚫 **Never mount the ESP32 bottom side up** (it mirrors the EXT pinout), and **never press the
  hat fully home on the headers outside the case.** → §6.3
- 🚫 **Item 17 does not exist and never did.** → §7.1
- ⚠️ **Item numbers are `aF4-MASTER-REFERENCE.md` §8 numbers** — the only numbering.

## Open items — by consequence

| # | Item | Blocks |
|---|---|---|
| 29 | **Print the case** from the 09-18 exports — **not the lid**. Fit the DC-099 flat up, tighten its 14 mm nut **while the box is empty**, solder to J1's pad tails (**red +12 V, black −**), anchor at the tie post | **Assembly** |
| 26 | **Inspect all five hats and pick the best** — check the J3/J4 face on each. Reflow the two pin-10 joints, clean with IPA, loupe the ten J3 joints | **The bench session** |
| 12 | **Solder two 1×10 male headers into EXT1/EXT2, pins up, plastic on the top face.** Shave the pin-10 end of EXT2's plastic if it binds on DCDC1 | **Assembly** |
| 27 | **Cut the two PoE light pipes to 24.2 mm** (hat pipes unchanged, 10.1); move the hat up 1.5 mm in Tinkercad | **Assembly** |
| 30 | **Erase the retired ESP32** and label it. Safe now — the replacement is proven | No — standing hazard |
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
**Closed 2026-09-18:** items 16 (OTA password rotated and proven) and 28 (panel jack in stock).

### Carried to the next board revision

**§A4 holds the full list**, headed by J1 to rotation 90 with its corner re-laid out, and both
jack datums taken from the vendor STEP rather than by hand. Unchanged: J3/J4 footprints onto
`B.Cu` (item 24), the hat's underside kept clear over the Olimex cap, C1's EOL replacement,
R5 to 0.25 W (item 18), J1/J2 sourcing, and the fab-note fixes.

## Last session — 2026-09-18

Two pieces of work. **Morning:** boards delivered; diagnosed J1 from the design sources and CUI's
STEP model, proved no re-seat is possible, found the enclosure's J1 hole was 1.25 mm off axis and
that all three checks covering the jack were hollow; took the panel-jack repair route into the
scripts and recorded it as §A4 with items 28 and 29. Item 28 closed the same day — the jack was
in stock and had a flat on its barrel, which replaced the anti-rotation scheme with a D-hole.
Kenny soldered the 12 V pair to J1's pad tails. **Evening:** swapped the PoE board. Flashed the
duplicate from the Mac, moved the OPNsense reservation, took HA's migrate path, rotated the OTA
password, hit `authentication is invalid` from a password containing YAML-significant characters,
fixed it with hex and proved the Device Builder OTA path end to end. Recorded as §11; item 16
closed and item 30 opened.
