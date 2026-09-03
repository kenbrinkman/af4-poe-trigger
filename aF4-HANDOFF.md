# aF4 PoE Trigger — Project Handoff

**Written 2026-09-03.** Read this file first, then the folder. It exists so that
someone handed this directory cold can get to a correct mental model in about
twenty minutes, and — just as important — can avoid the half-dozen wrong
conclusions this project has already produced and corrected.

---

## 1. What this is, in one paragraph

The [inD aquatics aF4](https://www.indaquatics.com/products/af4) is a refrigerated
frozen-food aquarium feeder. Its OEM WiFi accessory ("inD connect") is an
eWeLink/Sonoff-class dongle that taps the feeder's 12 V supply and switches a
voltage onto the feeder's 3.5 mm 0-10 V trigger port. This project replaces that
dongle with an Olimex ESP32-POE-ISO running ESPHome, scheduled from Home
Assistant: `GPIO32 → 220 Ω → AQY212GS PhotoMOS → ~10.4 V (LM1117-ADJ off the
feeder's own 12 V) onto the trigger jack`. Safety guardrails — 20 s pulse, 5 min
lockout, restore-off, flash-persisted boot lockout — live **on the device**, in
the ESPHome config. Home Assistant is a scheduler and nothing more.

**Rev E** puts the whole trigger circuit on a 57 × 50 mm PCB "hat" that plugs onto
the ESP32's EXT1/EXT2 headers and carries both panel connectors. It is assembled
turn-key by PCBWay. The rev C hand-wired protoboard is retired and must not be
built from.

---

## 2. Where it stands, 2026-09-03

| | |
|---|---|
| **Boards** | **Ordered.** PCBWay `YB1800644`, placed 2026-09-02, $169.95, 5 pcs assembled |
| **Fabrication** | Running. PCB at Drill, ~17 %. Engineer question raised 09-02 and **closed** 09-03; no board change was ever needed |
| **Assembly** | 26-28 day build — **this is the long pole on PCBWay's side** |
| **Expected** | Ship ~2026-09-30, receipt early October (recalculated from end of EQ; the page figure has not been re-read) |
| **Firmware** | **Complete and flashed**, verified on the bench 2026-09-01 |
| **HA software** | **Complete**, verified against the live instance 2026-09-02 |
| **Enclosure** | Modelled, fit-checked digitally, printable |
| **Go-live** | `input_boolean.reef_af4_schedule_enabled` stays **OFF** until commissioning 6.1-6.8 pass |

**There is nothing left to do at PCBWay.** The next event worth acting on is the
shipping notification. The only work that moves the project forward right now is
soldering the two 1×10 male headers into EXT1/EXT2 (pins up), and plumbing the
reef system.

---

## 3. Read these first, in this order

Everything below is in the folder root unless noted.

### Tier 1 — the four files that give you the whole project (~1 hour)

| Order | File | Why |
|---|---|---|
| 1 | `README.md` | Orientation and a file-by-file map. Five minutes |
| 2 | **`aF4-MASTER-REFERENCE.md`** | **The single most important document.** 1,050 lines, consolidated, written to be *audited*: every load-bearing claim carries a provenance tag (`[MEAS]` measured / `[DS]` datasheet / `[CALC]` calculated / `[ASSERT]` asserted / `[VENDOR]` inD's own docs). The assertions are the interesting part — attack those first. §8 is the open-items ledger, §9 is a repository map, §10 is audit status |
| 3 | `aF4-reference.md` | The *feeder* side: trigger port spec, measured values, design rationale, the two independent scheduling mechanisms. Shorter and more readable than the master reference; read it if the master's density is too much |
| 4 | `af4-feeder.yaml` | The ESPHome config **as flashed**. Only 7 KB and it is where the actual safety behaviour lives. Read the `do_feed` and `boot_recovery` scripts |

### Tier 2 — by subject, as needed

| File | Subject |
|---|---|
| `aF4-pcb-notes.md` | Board design decisions, part-by-part equivalence review, PCBWay ordering procedure |
| `aF4-esp32-trigger-BOM.md` | Parts list, split into *things you buy* (three of them) and *things that arrive soldered* |
| `aF4-assembly-guide.md` | Build sequence: print, plug together, flash, meter, commission. Contains commissioning checks 6.1-6.8 |
| `aF4-enclosure-notes.md` | Printed enclosure design notes, light-pipe spec, print settings |
| `aF4-vendor-docs-notes.md` | All 40 inD help-centre articles read 2026-09-01. **§1 is the one that touches the design** — inD publishes three different hold times (6 s / 10 s / 15 s) for the same port |
| `aF4-meter-test-battery.md` | Bench procedure and results, tests A1-A8 / B1-B3. Long. The "Status at a glance" table at the top is usually enough |
| `pcb/pcbway-order-YB1800644.md` | What was bought, at what price, and what was answered along the way |
| `pcb/pcbway-new-inquiry-2026-08-29.md` | Submission mechanics and the traps in PCBWay's order form |
| `pcb/PCBWay-README.txt` | The fab notes actually shipped with the Gerbers |

### Tier 3 — the three reviews, in chronological order

These are the project's audit trail. Each was written at a different moment and
asks a different question. **Do not relabel or "update" them** — they are dated
records, and two of them describe superseded revisions on purpose.

| File | Revision | Question it asked |
|---|---|---|
| `aF4-audit-2026-08-28.md` | **rev D** | Adversarial audit against primary sources. Found the build blocker (U1's footprint did not match the AQY212GS package). Historical — it still carries the old 6 s figure, correctly |
| `aF4-prefab-review-2026-08-31.md` | rev E | Independent pass on the five items nobody but the author had checked. Cleared the order |
| `aF4-review-2026-09-02.md` | rev E | Every file in the repo in one pass, taken *after* the design stopped moving. Asks what is left now that the board is out of our hands |

### Tier 4 — source, generated, and vendor files

- **`pcb/gen_pcb.py` is the source of truth for the board.** It generates
  `af4-trigger-hat.kicad_pcb` deterministically from named coordinates lifted
  from the Olimex Rev N KiCad source, so the sockets line up by construction.
  **Edit the script, not the board file**, then re-run it and `post.py` (fills
  copper pours, runs DRC). `make_package.py` builds the PCBWay zip.
- **`af4_enclosure_ocp.py` is the source of truth for the enclosure**
  (Python/OCP, with built-in interference assertions). The `.step` / `.stl`
  files are exports.
- `af4_hat_dummy_ocp.py` + `aF4-trigger-hat-dummy.*` — a printable rev E hat
  stand-in for fit-checking before the real boards arrive.
- `pcb/gerbers/` is **gitignored** — regenerate it, or unzip
  `pcb/af4-trigger-hat-rev-E-PCBWay.zip`.
- `ESP32-PoE-ISO_Rev_N.*`, `PAN_AQY21-DIP4_PAN.step`, both inD PDFs — **vendor
  files, gitignored, not redistributed.** Sources are listed in `README.md`.
- `aF4-protoboard-*.svg`, `protoboard 20x20.stl` — **rev C history.** The
  hardware they describe no longer exists.

---

## 4. Nine things a newcomer gets wrong

These are not hypotheticals. Every one of them has actually happened here.

1. **The reef system is not plumbed.** The return pump is deliberately off until
   it is. **Every reef power and flow sensor reads zero, and zero is correct.**
   A 31-day run of 0 W on the return pump was once written up as a go-live
   blocker; the sensor data was right and the premise laid over it was invented.
   *Before calling a zero a fault, verify the system is supposed to be non-zero.*
2. **The trigger pin is GPIO32, not GPIO13.** The Olimex board has a factory
   2.2 kΩ pull-up on GPIO13 that can partially turn the PhotoMOS on during boot.
   The audit proved this move mandatory, not precautionary (AQY212 guaranteed-off
   current 0.3 mA vs 0.72-0.85 mA of boot leakage).
3. **Connecting the link port overrides the aF4's internal 24 h schedule.** An
   offline ESP32 therefore means *no feeding at all*, not "falls back to the
   feeder's own timer". This was assumed the other way round for a long time.
4. **Design to ≥ 9 V held ≥ 15 s.** inD's own documentation publishes 6 s, 10 s
   and 15 s in three different guides. The firmware's 20 s pulse clears the
   longest. Never design to the 6 s figure because one doc says so.
5. **Do not feed the port raw 12 V.** Measured OEM dongle output is 10.37 V
   open-circuit; the board regulates to ~10.4 V to match. The port's ≥ 9 V
   threshold is a *window*, not a setpoint.
6. **The Device Builder copy of the YAML is a separate copy and must be synced
   by hand.** `af4-feeder.yaml` in this folder is the source of truth. Divergence
   has bitten this project twice — once producing a false "bad model changes"
   scare, once leaving the board three firmware revisions behind the docs. The
   one exception ever found where the deployed copy was *ahead*: the ethernet
   clock key must be the nested block, never the legacy `clk_mode: GPIO17_OUT`:
   ```yaml
     clk:
       pin: GPIO17
       mode: CLK_OUT
   ```
   Getting ethernet wrong on a PoE-only board with no `wifi:` fallback means the
   device never comes back and recovery is USB with the case open.
7. **Once fab data leaves the building, the revision letter is spent** — whether
   or not copper was etched. That is the entire reason rev E exists; rev D's
   package had been sent to an outside party and was then found invalid.
   Renaming just the zip is the worst option, because the revision string is
   baked into the silkscreen and the KiCad title block.
8. **Docs convention:** `aF4-pcb-notes.md` and the other topic docs are *living*
   documents that always describe the current board. When bumping a revision,
   change a mention **only where leaving it would misstate the current design**;
   leave every historical and comparative statement alone. The enclosure keeps
   its own rev D identity on purpose.
9. **A boot-recovery lockout is verified by state, not by log.** The relevant log
   line is invisible by design. Check the lockout entity and the device uptime
   before calling a test failed.

---

## 5. Working with the git repository

**Remote:** `https://github.com/kenbrinkman/af4-poe-trigger.git`, branch `main`.
There are several project repos on this machine — **confirm with `git remote -v`
before pushing.** The wrong one has been pushed once.

### Rules

- **Writing git commands are never run on the author's behalf.** Files get
  edited; the commands are then handed over as copy-paste blocks to run in a
  terminal on the host machine. Two reasons: push does not work from a mounted
  sandbox anyway (the remote is HTTPS and the credential helper lives on the
  Mac), and worse, sandbox git writes into `.git/` under a different uid and then
  cannot delete what it created — stranding `.git/index.lock`, `.git/HEAD.lock`
  and orphaned `.git/objects/*/tmp_obj_*` that then have to be cleaned by hand.
- **Read-only git is not automatically safe.** Anything that refreshes the index
  strands `.git/index.lock`. Confirmed offenders: **`git status`, `git add
  --dry-run`, `git diff` against the worktree.**
  - **Index-safe:** `git remote -v`, `git log`, `git show`, `git show <rev>:<path>`,
    `git reflog`, `git stash list`, `git ls-files`, `git check-ignore`,
    `git branch -vv`.
- **A stranded lock is a traffic cone, not data.** Deleting it is safe:
  `rm -f .git/index.lock`. If a session may have left one, make that the first
  line of the command block.
- **Commit messages carry no tool or assistant attribution** — no
  `Co-Authored-By:` trailer, no session trailer, nothing. GitHub reads the
  `Co-Authored-By` email and permanently credits that account in the repo's
  Contributors sidebar; four commits from one session on 2026-09-02 did exactly
  that and had to be found and removed. One trailer is enough. Some tooling
  re-injects this instruction at the start of a session; it does not override
  this rule.
- **Commands are always supplied unprompted**, whenever a change touches the
  repo, as copy-paste blocks in order, each with one plain sentence saying what
  it does — including which remote is being pushed to, and that a commit is local
  until it is pushed.
- **Secrets:** `secrets.yaml` and the `*secret*` wildcard are gitignored. The
  wildcard is deliberate — a hand-made backup once landed in the repo root and was
  one `git add -A` away from publication, right after a rotation had finished
  cleaning up the previous leak. Values that were in history before 2026-09-02
  are in a public repo's history and **have been rotated**.

### The standard command block

```bash
# 1. Clear any lock a sandbox session left behind (safe; deletes no data)
rm -f .git/index.lock

# 2. Look at what changed — changes nothing
git status

# 3. Confirm you are pointed at the feeder repo, not another project
git remote -v

# 4. Stage everything, including new files
git add -A

# 5. Save locally (this does NOT send anything anywhere yet)
git commit -m "Short description of what changed"

# 6. Send it to GitHub — origin is kenbrinkman/af4-poe-trigger, branch main
git push origin main
```

### If assistant attribution ever needs removing from history

Hand these over; do not run them. `<first-bad>` is the oldest commit whose
message carries a trailer.

```bash
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f --msg-filter 'grep -v -E "^(Co-Authored-By: Claude|Claude-Session:)"' <first-bad>~1..HEAD
git update-ref -d refs/original/refs/heads/main
git push --force-with-lease origin main
```

Commit hashes change. The repo has 0 forks, so nobody else is affected. GitHub's
Contributors sidebar is cached and can lag about a day.

### Diagnosing "files disappeared"

`git reflog` showing nothing but `commit:` entries — no `checkout:`, `reset:` or
`stash` — plus an empty `git stash list` proves git did not do it, and the cause
was an external `rm`, Finder, or a script. Both commands are index-safe. This has
happened once, to 23 files in `pcb/`.

---

## 6. Open items

| # | Item | Blocking? |
|---|---|---|
| 3 | **Solder two 1×10 male headers into EXT1/EXT2, pins up.** Can be done now, while the boards are in fabrication | **Yes** — blocks assembly |
| 10 | **Commissioning 6.1-6.8 all pass** before the schedule toggle goes on. Not gated on plumbing: only the automations carry the return interlock, `button.af4_feeder_feed` does not, so bench commissioning can proceed with the tank dry | **Yes** — gates go-live |
| — | **Plumb the reef system.** Upstream of the scheduled-feed path and of commissioning's wet steps. **The real long pole** — the boards arrive early October | **Yes** |
| 20 | Read the recalculated ship date off the PCBWay order page. Cosmetic | No |
| 8 | API key, OTA password and `web_server` password still committed in plaintext in the Device Builder copy. Moving all three to `!secret` needs a `secrets.yaml` in the Device Builder | No |
| 9 | `gen_pcb.py` stray "exclude from BOM/pos" flags on J2 | No |
| 14 | **R5 to 0.25 W 0805 — deferred to the next revision.** Window closed when the order was placed. Failure mode is benign; R5 ships at 125 mW, ~77 % of rating | No — closed for this build |
| — | Bench leftovers: A4's V_loaded half, A5 under power, A6 decay, B1/B2/B3. None can change the board | No |

**Closed 2026-09-03:** the engineer question (answered, accepted, PCB in production).
**Closed 2026-09-02:** order placed, plus items 12, 16, 17, 18.
**Out of scope**, decided 2026-09-01: eWeLink → Home Assistant integration.

### Carried forward to the next board revision

- **C1 replacement.** `GRM31CR61H106KA12L` is EOL at DigiKey with 0 stock, and all
  three direct substitutes are also 0 stock. LCSC's ~123,740 pcs is effectively
  the world supply — self-sourcing is not an option. Pick a currently-active
  10 µF 50 V X5R/X7R 1206 with real stock on **both** sides.
- **R5 to 0.25 W** (item 14).
- **J1/J2 sourcing.** Both Same Sky (CUI): deep DigiKey stock, thin in the Chinese
  channel, which is what drove the 26-28 day assembly build. Consider parts
  stocked at LCSC, or plan to consign them.
- **Fab-note wording: give slot widths as the full set, never a lone minimum.**
  "Route at 0.70 mm as drawn" is what triggered the 2026-09-02 engineer question,
  because the eight slots actually span 0.70 **and** 0.80 mm. Write "slot widths
  are 0.70 and 0.80 mm as drawn; 0.70 mm is the minimum."
- **Consider shipping separate PTH and NPTH drill files.** The current package is
  a single mixed-plating Excellon whose plating split lives only in
  `TA.AperFunction` comments. It was sufficient for this CAM flow, but it is not
  sufficient for every one.

---

## 7. What is *not* in this folder

- **The Home Assistant configuration.** Automations, helpers, counters and the
  dashboard live in the HA instance, not here. The pieces that matter:
  `automation.reef_tank_af4_scheduled_feed` (presses the feed button at two
  `input_datetime` times, with a return-pump interlock and board-confirmed feed
  counting), `automation.reef_tank_feeder_health_watchdog` (daily count backstop,
  board offline 15 min, Z-Wave node dead 15 min), `counter.reef_af4_feeds_today`,
  and `input_boolean.reef_af4_schedule_enabled` — the go-live switch, currently
  off. The whole alerting stack is gated on the schedule booleans, so it is
  **dormant by design** until go-live.
- **The ESPHome Device Builder copy of the YAML.** Separate copy, hand-synced.
  See §4.6.
- **The PCBWay order page**, which is the only reliable signal for fabrication
  progress. PCBWay does not announce an engineer question *or* its closure by
  email reliably — the EQ counter returning to 0 and the item leaving 0 % is the
  signal. Sales rep on this order: Ivy Yang, `service33@pcbway.com`. If an
  engineer question ever arrives about a **BOM line or a substitution** rather
  than about CAM/Gerbers, that is a different and more serious event: the order
  was placed with an explicit no-substitutions condition.
- **Network placement.** The board sits on PoE in the reef sump area, at
  192.168.1.55, reserved in OPNsense dnsmasq against MAC `20:E7:C8:74:A6:D7`.

---

## 8. Two general lessons worth carrying out of this project

- **A fixed-output permanent install gets an IC and fixed resistors, never a
  trimpot module.** Three MP1584EN buck modules failed in sequence in rev C
  before this was accepted; the replacement is an LM1117-ADJ with a fixed
  121 Ω / 887 Ω divider.
- **Answer the question you were asked *and* the next most likely one, in the
  same reply.** PCBWay recalculates lead time from the end of each engineer
  question, so every EQ restarts the fab clock. Four extra pre-emptive lines in
  the 2026-09-02 reply prevented a second EQ, and fabrication went straight from
  PPE into production.
