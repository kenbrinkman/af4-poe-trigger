# STATUS — aF4 PoE Trigger

**Rewritten 2026-09-19.** The only live-status document in this project. Rewrite it;
never append to it. If it passes ~120 lines, something in it belongs in `aF4-MASTER-REFERENCE.md`.

## Phase

**🟢 Commissioning passed, end to end. 6.1 through 6.8, every check, against the real feeder.**
The trigger circuit has now been *measured* rather than argued, and it has driven an actual aF4.
Items 12, 15, 25 and 29 are closed. → §12

**🟢 The reef system is plumbed and running** — confirmed by Kenny, return pump at 142 W. That
retires the longest-standing item in this project and satisfies the scheduled-feed automation's
return-pump interlock. **Go-live is no longer gated on anything but closing the case.** → §12.3

**🟢 The retired ESP32 is erased** — full chip, verified by read-back. Item 30 and the LAN hazard
close together; the bare board is stock silicon now and all it still wants is a label. → §13

**🟠 The enclosure goes back to the bench to be finished** — light pipes, M3s, tie-post anchor,
lid. The link cable is pulled meanwhile so the feeder runs on its own internal schedule, and
**Kenny turns `input_boolean.reef_af4_schedule_enabled` on by hand once the case is closed.**

| | |
|---|---|
| Board + hat | **Assembled and commissioned** `[MEAS] 2026-09-18`. Hat on both headers, resting on its standoffs, both jack noses through the +X wall |
| ESP32 | **Online at 192.168.1.55**, adopted in HA, all seven entity IDs intact. Ethernet MAC `00:70:07:7F:48:C3` |
| Firmware | **Complete.** Build `2026-09-18 18:07:52`, config hash `0xd4f82693`. OTA path proven |
| Credentials | ✅ All three rotated and verified |
| 12 V wiring | ✅ **Polarity confirmed by meter** — black tail → TP4 a dead short, red → TP4 open. **Red is +12 V** |
| Enclosure | Case printed 09-18 and in use; **lid unchanged**. Light pipes uncut (item 27) |
| HA software | **Complete**, re-verified against the live instance 2026-09-18 |
| Go-live | `input_boolean.reef_af4_schedule_enabled` **OFF**. Kenny enables it manually after the case closes. Schedule stands at **2/day, 13:30 and 20:30** |

**Nothing is on order and nothing is waiting.**

1. **Pull the link cable and confirm the feeder shows a next feed time on its own display**
   (item 31). Nothing establishes that the internal schedule resumes on release — and while the
   cable is in with the schedule off, the feeder is silently dark.
2. **Finish the case:** cut the two PoE light pipes to 24.2 mm (item 27), the 2 × M3 into the
   tall standoffs, anchor the 12 V cable at the tie post, lid on.
3. **Then turn the schedule on.** Next scheduled feed would be 13:30.

## What 6.1–6.8 measured

**6.2 = 11.4 V · 6.3 = 10.37 V · 6.4 = 0 V, D5 dark · 6.5 = 10.37 V held 20 s, clean edge ·
6.6 = 310.007 s then 310.013 s · 6.7 link solid · 6.8 the unit fed.** Three of those carry more
than a pass — 6.2 landed on its *predicted* value and would have failed the pre-09-01 band, 6.3
proves R4/R5 by measurement because the LM1117 was not in dropout, and 6.4 is the first hardware
proof of the GPIO32 decision. **§12.2 says what each one settles**; 6.5's clean falling edge also
answers bench item **A6** for free.

## What you may trust

- **Every number above**, and the polarity behind them. This is the first evidence in the project
  that is measurement rather than inference.
- **The build board end to end**: online, adopted, entity IDs intact, OTA path proven, all four
  consumers resolving. Re-checked 09-19: seven entities, no `_2`, online at `192.168.1.55`.
- **That the retired board carries nothing** — erased, and verified at five offsets. → §13
- **D3 and D5 are the right way round** — on the build board. Item 25 closed at 6.1 and 6.5.
- **The reef is running.** Return pump 142.245 W against a 10 W threshold.
- **A manual feed leaves no trace in `counter.reef_af4_feeds_today`** — by design; it stayed at 0
  through both of tonight's feeds, and that is not a missing count. **Case work is also silent:**
  both watchdog branches are gated on the schedule toggle. → §12.4
- **The Device Builder YAML is byte-identical** to `firmware/af4-feeder.yaml`, and **the lid
  needs no reprint** — both verified byte-for-byte 2026-09-18.
- **The enclosure at its new geometry** — all checks re-run on the Mac 2026-09-18. 65.2 × 117.0 × 39.9 mm.

## What you may not trust

- ⚠️ **That the aF4's internal schedule resumes when the link cable comes out.** Both vendor
  guides describe only the *connected* state. This project assumed the override direction
  backwards once already — do not assume the reverse. **Verify on the unit.** → item 31
- ⚠️ **Only the build board is proven.** The other four are uninspected (item 26): D3/D5 untested,
  ten J3 joints ungraded, pin-10 excess solder on every board.
- **The 0.72 mm cap clearance is still calculated**, not measured — the stack assembles and the fit
  is good, but no feeler gauge has been on that gap. **Four `PJ_*` values remain uncalipered**, and
  none of them shapes the printed hole or gates a check.
- **Silkscreen reads "10.4V 10s pulse"** — wrong, unfixable on this run. The enclosure scripts run
  only on the Mac (§9.2), and **`gen_pcb.py` / `make_package.py` are un-rerun under KiCad 9.**

## Standing corrections — settled, do not re-raise

- 🚫 **Do not tighten the commissioning bands.** 6.2 measured 11.4 V — the floor. The 09-01
  widening is now validated by a passing board, not just by argument. → §8.1 · §12.6
- 🚫 **A reef sensor reading zero is now suspect, not expected.** The plumbing rule inverted
  2026-09-18. The underlying lesson is unchanged: check what the system is *supposed* to read. → §12.3
- 🚫 **Never compute the Ethernet MAC for a DHCP reservation — read it from the lease.** → §11.1
- 🚫 **On a board swap take HA's "Migrate configuration to new device"** (§11.2), and **an OTA
  password must be punctuation-free** — compare by hash, not by eye (§11.4).
- 🚫 **Never route the 12 V leads across the hat's right-hand edge.** 0.50 mm; a lead there is
  crushed by the lid, invisibly. Down into the void, then along the floor. → §A4
- 🚫 **J1: leave it fitted and dead, plug nothing into it, raise nothing with PCBWay.** → §A4
- 🚫 **A check whose result is fixed by its own inputs is not a check.** → §A4
- 🚫 **Never mount the ESP32 bottom side up**, and **never press the hat fully home on the headers
  outside the case** (§6.3). 🚫 **Item 17 does not exist and never did** (§7.1).
- 🚫 **Wiping an ESP32 is `erase-flash`, not a re-flash** — credentials live in NVS — and the
  verification is a read-back, never the tool's own success line. `read-mac` resets the board it
  is pointed at: identify bench boards with it, never a running one. → §13.1
- ⚠️ **Item numbers are `aF4-MASTER-REFERENCE.md` §8 numbers** — the only numbering.

## Open items — by consequence

| # | Item | Blocks |
|---|---|---|
| 31 | **Confirm the feeder's internal schedule resumes** once the link cable is pulled. Free to check; the cost of not checking is a silently dark feeder | **The fish, tonight** |
| 27 | **Cut the two PoE light pipes to 24.2 mm** (hat pipes unchanged, 10.1); move the hat up 1.5 mm in Tinkercad. Then M3s, tie-post anchor, lid | **Closing the case** |
| — | **Turn on `input_boolean.reef_af4_schedule_enabled`** — Kenny, by hand, once the case is closed. Every engineering gate has passed | **Go-live** |
| 26 | **Inspect the other four hats** — the build board is chosen, so this is no longer a selection question, but their J3/J4 faces and joints are ungraded if one is ever needed | No |
| 24 | **Fix the cause of the J3/J4 error:** footprints to `B.Cu`, silkscreen to `B.SilkS`, face named in `PCBWay-README.txt`, THT parts in the centroid with a side column | No |
| 20 | **No dispense confirmation.** A power-monitoring smart plug on the 12 V supply is the only fix short of opening the unit | No — the last unmonitored failure direction |
| 22 | `pcb/gen_pcb.py` stray "exclude from BOM/pos" flags on J2. Fold into item 24 | No |
| 14 | LED viewing-angle conflict → §2.6 | No — cosmetic |
| 18 | R5 to 0.25 W — deferred, window closed | No |
| — | Bench leftovers: A4's V_loaded half, A5 under power, B1/B2, and **B3** — held-high yields exactly one feed, the one with real information value. **A6 is answered** by 6.5's clean edge | No |

**Out of scope**, decided 2026-09-01: eWeLink → Home Assistant integration.
**Closed 2026-09-18:** items 16, 28, 12, 15, 25, 29, and the reef-plumbing long pole.
**Closed 2026-09-19:** item 30.

### Carried to the next board revision

**§A4 holds the full list**, headed by J1 to rotation 90 and both jack datums taken from the
vendor STEP rather than by hand.

## Last session — 2026-09-19

The retired board identified by `read-mac`, full-chip erased over USB with the Ethernet lead out,
and the erase verified by read-back at five offsets. Item 30 closed; HA holds no orphan. → §13

## 2026-09-18

J1 found rotated 180° on all five boards and the panel-jack repair taken into the scripts (§A4,
items 28–29); the PoE board swapped, OTA password rotated, OTA path proven (§11); the hat
assembled into the reprinted case, 12 V polarity settled with a meter, and **commissioning
6.1–6.8 passed against the real feeder** (§12). The reef proved plumbed; item 31 opened.
