# aF4 PoE Trigger — session priming

**Durable facts only.** If a statement would stop being true next month, it belongs in
`STATUS.md`, not here.

## 0. How to read this project

Read **this file**, then **`STATUS.md`**. That is the whole default read path — about
6,000 tokens, and it is enough to answer most questions or to know where to look.

🚫 **Do not read the folder.** 🚫 **Do not read `aF4-MASTER-REFERENCE.md` whole** — it is
~63 KB and reading it costs ~16,000 tokens. Use its section index, then `grep -n` the
heading, then `sed -n` the line range:

```
grep -n "^### 2.4" aF4-MASTER-REFERENCE.md      → 402
sed -n '402,444p' aF4-MASTER-REFERENCE.md
```

🚫 **Do not read anything in `archive/`** on entry. `grep -rn` it only, and only to check
whether something was ever written down. See `archive/README.md`.

## 1. What this is

The [inD aquatics aF4](https://www.indaquatics.com/products/af4) is a refrigerated
frozen-food aquarium feeder. Its OEM WiFi accessory ("inD connect") taps the feeder's 12 V
supply and switches a voltage onto its 3.5 mm 0-10 V trigger port. This project replaces
that dongle with an Olimex ESP32-POE-ISO running ESPHome, scheduled from Home Assistant:

```
GPIO32 → 220 Ω → AQY212GS PhotoMOS → ~10.4 V (LM1117-ADJ off the feeder's own 12 V) → trigger jack
```

Safety guardrails — 20 s pulse, 5 min lockout, restore-off, flash-persisted boot lockout —
live **on the device**, in the ESPHome config. Home Assistant is a scheduler and nothing
more.

**Rev E** puts the trigger circuit on a 57 × 50 mm PCB "hat" that plugs onto the ESP32's
EXT1/EXT2 headers and carries both panel connectors, assembled turn-key by PCBWay. The rev C
hand-wired protoboard is retired and must not be built from.

## 2. Sources of truth

| Thing | Source of truth | Not the source |
|---|---|---|
| The board | `pcb/gen_pcb.py` — edit the script, re-run it and `pcb/post.py` | `pcb/af4-trigger-hat.kicad_pcb` (generated) |
| The enclosure | `hardware/enclosure/af4_enclosure_ocp.py`, with built-in interference assertions | the `.step` / `.stl` exports |
| The firmware | `firmware/af4-feeder.yaml` | the ESPHome Device Builder copy (see §4.3) |
| The deep record | `aF4-MASTER-REFERENCE.md`, grepped by `§N.N` | any review document |
| Current state | `STATUS.md` — the only live-status doc | everything else |

**Paths in every document are relative to the project root**, whatever folder the document
itself is in.

## 3. Where things live

```
README.md                     folder map, human entry point
STATUS.md                     the only live-status doc — rewritten, never appended
aF4-MASTER-REFERENCE.md       the record; §N.N numbered, grepped, never read whole
.claude/CLAUDE.md             this file
docs/                         subsystem references + git-rules.md
firmware/                     af4-feeder.yaml (source of truth) + secrets.yaml (gitignored)
hardware/enclosure/           OCP sources and their STEP/STL exports
pcb/                          KiCad project, generators, PCBWay package and order record
reference/diagrams/           wiring and system SVGs
reference/vendor/             vendor CAD and PDFs — gitignored, not redistributed
archive/                      🚫 not in the read path
```

## 4. The expensive lessons

Every one of these has actually cost time here.

1. **The trigger pin is GPIO32, not GPIO13.** The Olimex board has a factory 2.2 kΩ pull-up
   on GPIO13 that can partially turn the PhotoMOS on during boot. The audit proved the move
   mandatory, not precautionary: AQY212 guaranteed-off current is 0.3 mA against 0.72–0.85 mA
   of boot leakage. → §2.4
2. **Connecting the link port overrides the aF4's internal 24 h schedule.** An offline ESP32
   therefore means *no feeding at all*, not "falls back to the feeder's own timer". This was
   assumed the other way round for a long time. → §1.4
3. **The ESPHome Device Builder copy of the YAML is a separate copy, hand-synced.**
   Divergence has bitten this project twice. The Device Builder also has its **own** secrets
   store — a third copy that no diff of the YAML will ever catch. The one case where
   the deployed copy was *ahead*: the ethernet clock key must be the nested block, never the
   legacy `clk_mode: GPIO17_OUT`. Getting ethernet wrong on a PoE-only board with no `wifi:`
   fallback means the device never comes back and recovery is USB with the case open.
4. **Design to ≥ 9 V held ≥ 15 s.** inD's own documentation publishes 6 s, 10 s and 15 s in
   three different guides. The 20 s pulse clears the longest. Never design to the 6 s figure
   because one doc says so. → §1.3
5. **Do not feed the port raw 12 V.** Measured OEM dongle output is 10.37 V open-circuit; the
   board regulates to ~10.4 V. The ≥ 9 V threshold is a *window*, not a setpoint.
6. **Once fab data leaves the building, the revision letter is spent** — whether or not copper
   was etched. That is why rev E exists. Renaming just the zip is the worst option: the
   revision string is baked into the silkscreen and the KiCad title block.
7. **A boot-recovery lockout is verified by state, not by log.** The relevant log line is
   invisible by design. Check the lockout entity and the device uptime before calling a test
   failed.
8. **Verify an open item against reality before acting on it.** Item 17 was opened as the last
   safety gap and closed the same day: the work had existed in Home Assistant since 08-27 and
   had simply never been written back. Item 11 sat "open" for a day after the firmware was
   already flashed. **A ledger built by reading the repo invents open items as readily as it
   misses closed ones.** Check for the *function*, not the name. → §7.1
9. **The reef system is not plumbed.** Every reef power and flow sensor reads zero, and zero is
   correct. A 31-day run of 0 W on the return pump was once written up as a go-live blocker.
   *Before calling a zero a fault, verify the system is supposed to be non-zero.*
10. **A fixed-output permanent install gets an IC and fixed resistors, never a trimpot module.**
    Three MP1584EN buck modules failed in sequence in rev C before this was accepted.
11. **Answer the question you were asked *and* the next most likely one, in the same reply.**
    PCBWay recalculates lead time from the end of each engineer question, so every EQ restarts
    the fab clock. Four pre-emptive lines in the 2026-09-02 reply prevented a second EQ.
12. **Docs convention:** the topic docs in `docs/` are *living* — they describe the current
    board. When bumping a revision, change a mention **only where leaving it would misstate the
    current design**; leave historical and comparative statements alone. The enclosure keeps its
    own rev D identity on purpose.

## 5. What is not in this folder

- **The Home Assistant configuration.** Automations, helpers, counters and the dashboard live
  in the HA instance. The pieces that matter: `automation.reef_tank_af4_scheduled_feed`,
  `automation.reef_tank_feeder_health_watchdog`, `counter.reef_af4_feeds_today`, and
  `input_boolean.reef_af4_schedule_enabled` — the go-live switch. **Two feeds a day**, at times held in `input_datetime.reef_af4_feed_time_1` / `_2` so they stay dashboard-editable — the count and the times live only in HA, deliberately. → §5.7
- **The ESPHome Device Builder copy of the YAML**, and its own secrets store. See §4.3 above.
- **The PCBWay order page** — the only reliable signal for fabrication progress. PCBWay does
  not reliably announce an engineer question *or* its closure by email; the EQ counter
  returning to 0 is the signal. Rep on this order: Ivy Yang, `service33@pcbway.com`.
- **Network placement.** The board sits on PoE in the reef sump area, at `192.168.1.55`,
  reserved in OPNsense dnsmasq against MAC `20:E7:C8:74:A6:D7`.

## 6. Working rules

- **Git:** read `docs/git-rules.md` before any git work. The short version: ask for the folder
  delete grant, then commit directly. Kenny runs `git push`. Never write a `commit-*.sh`.
  Never put assistant attribution in a commit message.
- **Finishing work:** **rewrite `STATUS.md`, do not append to it.** The durable record goes to
  `aF4-MASTER-REFERENCE.md` as a new numbered section. Do not renumber existing sections, and
  re-run the section-index script (§3 of `docs/git-rules.md`) after any edit that changes the
  file's length.
- **Never renumber `§N.N`.** Docs, commits and conversations cite them. Add; do not renumber.

## 7. Routing table — where to look, without loading the world

| Question | Go to |
|---|---|
| What is left to do, and what can I trust | `STATUS.md` |
| Flash / deploy the firmware | `docs/aF4-assembly-guide.md` §4 · §5 |
| The safety architecture, lockouts, timing | §5.1 · §5.2 |
| Home Assistant automations, as they actually are | §5.7 |
| Why GPIO32 | §2.4 |
| Regulator maths, the 10.4 V rail, load budget | §2.1 · §2.2 |
| Trigger port spec and measured facts | §1.2 · §1.3 · `docs/aF4-reference.md` |
| Wiring | `reference/diagrams/` · §2 · §2.5 |
| Bill of materials, sourcing traps | §3 · §3.1 · `docs/aF4-esp32-trigger-BOM.md` |
| Board geometry, isolation, DRC | §4.1 · §4.2 · §4.3 |
| Commissioning checks 6.1–6.8 | §8.1 |
| Enclosure, the vertical stack | §6.1 · `docs/aF4-enclosure-notes.md` |
| The PCBWay order, the engineer question | `pcb/pcbway-order-YB1800644.md` |
| Bench tests, what is measured vs asserted | `docs/aF4-meter-test-battery.md` · §10.2 |
| What the audit did and did not confirm | §10 · §10.1 |
| Build blockers, and how U1 was fixed | §A1 · §A1.1 · §A1.2 |
| "Was this always true?" / "did we get this wrong once?" | §7 · §7.1, then `grep -rn archive/` |
| Toolchain limits (`pcbnew`, `kicad-cli`) | §9.1 |

Unqualified `§N.N` always means a section of `aF4-MASTER-REFERENCE.md`.
