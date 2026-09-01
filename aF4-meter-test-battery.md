# aF4 meter test battery

Written 2026-09-01. Bench procedure for closing the measurement-dependent open
items. **None of this requires opening the aF4**, so the warranty is untouched.

## Why the order matters

The rev E order is submitted to PCBWay but **not paid and not fabbed**. That
makes this the last cheap window to act on a measurement.

- **Group A tests can change the board.** Run them before paying.
- **Group B tests only change firmware.** They can wait for any time.
- **Group C needs the built hat.** It is the commissioning pass.

Group A is about two hours including cycle waits. If only one thing gets done,
make it **A2** — the design already knows the 10.4 V rail rides near the
LM1117's dropout, and nobody has ever measured the rail it actually rides on.

---

## Prerequisites

| Item | Note |
|---|---|
| DMM | **Min/Max record mode strongly preferred** — see A2 |
| 3.5 mm screw-terminal breakout | ~$4. Lets you probe tip and sleeve *while* the plug is seated. Alternative: sacrifice a patch cable and expose the conductors mid-run |
| 100 Ω and 1 kΩ resistors | Bin stock, ¼ W is fine |
| inD Connect dongle + eWeLink app | The known-good OEM signal source |
| Phone stopwatch | |
| Cup or container, ≥12 oz | |
| Sink or catch basin | |

**Do not measure port current by putting the DMM in series in amps mode.** The
burden voltage is unpredictable and a meter left in amps mode is the classic way
to blow a fuse or worse. A5 uses a series resistor instead — safer, and it gives
you input impedance for free.

### Record first

Write down the **aF4 serial number** from the underside sticker. It is needed for
any warranty claim, and it determines over-temperature behaviour: `100XXX` goes to
standby with continuous beeping, `20XXX`/`60XXX` shut down entirely.

---

## Setup S1 — the safe feed configuration

Used by every test that triggers an actual feed. This is inD's own pre-use-rinse
arrangement, so it is a documented-safe way to run the unit.

1. aF4 upright on a counter near a sink. **Never lay it on its side.**
2. Reservoir filled at least halfway with plain water. **No food** — food only
   makes the cycles messy and the results harder to read.
3. Black intake tube fully submerged in a cup holding ≥12 oz of water.
4. Grey output tube into the sink or a catch container. **Not the tank.**
5. Power on with a firm 3-second press. Solid green LED.
6. Set feed quantity to **1 LED (5 mL)** — shortest cycle, least water.

**Every triggered feed is followed automatically by a self-clean, so budget
5 minutes per trial.** A five-point sweep is a 25-minute test. Do not rush it by
re-triggering early; you will just be measuring the spacing lockout.

Never let the pump run dry — keep water in the reservoir and the cup throughout.

---

# Group A — board-affecting. Run before paying PCBWay.

## A1 — 12 V brick open-circuit voltage · closes open item 7

The input TVS is a **SMAJ13A, 13 V standoff**. If the brick idles above that, the
TVS conducts continuously, warms, and eventually fails short.

1. Unplug the brick from the aF4. Leave it plugged into mains.
2. DMM to DC volts.
3. Black probe on the barrel **outer sleeve**, red on the **centre pin**.
4. Record the reading.

| Result | Meaning |
|---|---|
| **12.2 – 12.9 V** | PASS — healthy, comfortable both ends |
| 13.0 – 14.4 V | **CONCERN** — D2 leaks at idle. Move to SMAJ15A or SMAJ16A. **Board change** |
| Below 12.2 V | See A2; the loaded rail will be worse |
| Reads negative | Polarity assumption is wrong — stop and re-check before anything else |

Confirm it reads **positive** with red on the centre pin. Centre-positive is
assumed throughout the design.

## A2 — loaded rail voltage at the splitter tap · the critical one

This is the actual input to the hat's LM1117, minus the SS14's ~0.3 V. The master
reference already establishes how tight this is:

| Brick | LDO input | Headroom to 10.47 V |
|---|---|---|
| 12.2 V | 11.90 V | 1.43 V ✓ |
| 12.0 V | 11.70 V | 1.23 V ✓ but worst-case divider is **in dropout** |
| 11.6 V | 11.30 V | **in dropout** |

The aF4 is a 12.5 A load running a TEC, pump, solenoid and fan off the same
brick. Sag is entirely plausible and has never been measured.

1. Brick → Y-splitter → aF4. Leave the hat tap free.
2. DMM on DC volts across the **free tap** (centre to sleeve).
3. **Turn on Min/Max record mode.** A plain DMM averages and will hide a sag.
4. Power the aF4 on and let the cooling system come up to temperature.
5. Record the **idle** reading with the TEC running.
6. Trigger a feed (Feed Now, or the dongle). Let the full cycle including
   auto-clean complete while recording.
7. Read the **minimum** captured.

| Minimum captured | Meaning |
|---|---|
| **≥ 12.2 V** | PASS — the design's headroom assumption holds |
| 12.0 – 12.2 V | Marginal. A worst-case divider rides dropout. Still functional, but regulation is lost |
| 11.6 – 12.0 V | **CONCERN** — nominal parts enter dropout during feeds |
| **< 11.6 V** | **Board-affecting.** The shared-rail approach needs rethinking — a separate supply for the hat, or a different regulator topology |

Dropout is **not a safety failure** — the LM1117 degrades to roughly V_IN − 1 V,
which is still inside the 9–11 V trigger window, so feeds still work. What is lost
is regulation and ripple rejection. But if this test lands below 12.0 V, say so
before paying, because it is much cheaper to change now than after assembly.

If your meter has no Min/Max, the sustained TEC-running reading is still the most
important number and a plain DMM catches that fine. Short transients would need a
scope; do not chase them.

## A3 — port pinout and the ring-to-sleeve assumption

The board ties J2's ring to sleeve on the assumption that the aF4's jack already
shorts them. If that is wrong, the hat could load or short part of the port.

1. **aF4 powered off and unplugged from mains.**
2. Insert the 3.5 mm breakout into the 0-10 V port.
3. DMM on continuity / lowest ohms range.

| Measure | Expected | If different |
|---|---|---|
| Ring – Sleeve | **Short, < 1 Ω** | If open or a defined resistance, tying them on the board is **not** safe → **board change** to leave J2's ring floating |
| Tip – Sleeve | High: kΩ to MΩ, or open | Record the value; it feeds A5 |
| Tip – Ring | Same as tip–sleeve if ring is shorted | Consistency check |

An ohmmeter injects its own small test voltage, so if the port input has
protection diodes the tip–sleeve reading may be nonlinear and polarity-dependent.
Take it in **both probe orientations** and record both.

## A4 — dongle output voltage, open-circuit vs loaded

The project carries a measured 10.37 V from the OEM dongle, but not whether that
was open-circuit or loaded. The distinction sets what the hat should target.

1. Dongle powered through its splitter. 3.5 mm plug **not** in the aF4.
2. Assert the dongle: eWeLink toggle ON, hold it on.
3. Measure tip–sleeve at the free plug. Record as **V_open**.
4. Now seat the plug into the aF4 through the breakout, so you can probe with it
   connected. Assert again.
5. Measure tip–sleeve. Record as **V_loaded**.

| Result | Meaning |
|---|---|
| V_open ≈ V_loaded | The port draws almost nothing. Confirms the load-budget assumption |
| V_loaded materially lower | The port draws real current and the dongle has output impedance. **Not a problem for the hat** — the LM1117 has far lower output impedance and will hold 10.4 V. Note it and continue |
| V_loaded < 9 V | Something is wrong with the dongle or the breakout. Stop and re-check wiring |

Both readings should sit comfortably inside the 9–11 V window.

## A5 — port input current and impedance · closes open item 6

The entire load budget assumes the port draws approximately nothing. It has never
been checked.

1. Wire inline through the breakout: **dongle tip → 100 Ω → aF4 port tip.**
   Sleeves common to both.
2. Assert the dongle and hold.
3. Measure the voltage **across the 100 Ω resistor**.
4. Current = V / 100.

| Drop across 100 Ω | Current | Verdict |
|---|---|---|
| Unreadable, < 1 mV | < 10 µA | Port is high-Z. Assumption confirmed, **done** |
| 1 – 100 mV | 10 µA – 1 mA | Negligible. Fine |
| 0.1 – 2 V | 1 – 20 mA | Acceptable, but recheck the AQY212GS load-current rating against it |
| > 2 V | > 20 mA | **Board-affecting.** Recheck LM1117 dissipation, F1's 0.10 A hold, and the AQY212GS on-resistance |

If you get a readable value, swap the 100 Ω for **1 kΩ** and repeat. A plain
resistive input gives a proportional result; a comparator or opto input will
behave nonlinearly. Either way, compute apparent input impedance as
**Z ≈ V_loaded / I**.

For reference, quiescent load on the 10.4 V rail is 18.7 mA and rises to 20.0 mA
during a feed, against F1's 0.10 A hold current. Anything the port adds stacks on
top of that.

## A6 — port decay time · bears on R3 and the unsourced 60 s re-arm

R3 is a 100 kΩ bleed whose job is to return the port to 0 V after a feed. Its time
constant depends on capacitance inside the port, which nobody has measured.

1. Dongle connected through the breakout. DMM on DC volts, tip–sleeve.
2. Assert for 20 s, then release the toggle.
3. Time how long the voltage takes to fall below **1 V**. Stopwatch is fine.

| Decay to < 1 V | Meaning |
|---|---|
| **Under 1 s** | Port self-discharges. R3's exact value is irrelevant. No change |
| 1 – 10 s | Some capacitance present. R3 100 kΩ still works; note the constant |
| **Over 10 s** | Consider dropping R3 to 10 kΩ so the hat re-arms briskly. **Board change** — decide now |

Note this measures decay under the *dongle's* output stage, not the hat's. It
tells you about the port's own capacitance, from which R3's behaviour follows.

---

# Group B — firmware only. Any time.

The decision to move the pulse from 10 s to 20 s is **already safe under every
documented figure**, so B1 is confirmatory rather than decision-critical. Do not
delay the firmware change waiting for it.

## B1 — hold-time sweep · settles the 6 s vs 15 s question

Setup S1. Assert the dongle for a measured duration, release, wait a full
5 minutes, repeat.

Sweep: **5 s, 8 s, 12 s, 16 s, 20 s.**

For each trial record: did water dispense? Did the link LED flash green?

eWeLink round-trips over WiFi, so treat every duration as **±1–2 s**. Once you
find the boundary, run it twice more to confirm it is repeatable and not a
latency artefact. Expect the answer to land somewhere between 6 s and 15 s;
whatever it is, 20 s clears it.

## B2 — re-arm interval · low value, and confounded

Assert 20 s, release, wait N, assert 20 s again. Try N = 30 s, 60 s, 120 s, 300 s.

**Caveat that limits this test:** the documented 5-minute spacing rule blocks any
second feed under 300 s regardless of what the re-arm time actually is. So this
can only ever confirm the *combined* constraint, not isolate R2. The practical
answer is already known — 300 s works, and that is what the firmware does. Run it
only for completeness.

## B3 — held-high yields exactly one feed · high value

This validates the design's single best safety property on your own unit. Audit
finding B5 and the entire held-high failure analysis rest on it, and it is
currently only vendor-documented.

1. Setup S1.
2. Assert the dongle and **leave it on for 20 minutes.**
3. Count dispense events.
4. Expect **exactly 1.**
5. Release, wait 5 minutes, assert 20 s, and confirm it feeds again — proving the
   port re-arms after a long hold.

If this ever produces more than one feed, the held-high analysis is wrong and the
failure bounding in the master reference needs revisiting. That would be a
significant finding.

---

# Group C — after the hat is built

Existing commissioning steps 6.1 – 6.6 from `aF4-assembly-guide.md`, plus two new
ones that the vendor documentation made available:

- **6.7** — plug the patch cable into J2. **Link LED goes solid** = the port sees
  the connection.
- **6.8** — press the HA feed button. **Link LED flashes green** = the 10.4 V
  pulse was accepted, confirmed without waiting to watch food move.

Note the known inconsistency: **checks 6.2 and 6.3 are mutually inconsistent at
their edges.** A brick legitimately passing 6.2 at 11.6 V cannot deliver 10.3 V at
TP2 even with perfect parts. If 6.3 reads low after a low-but-passing 6.2, the
divider is probably innocent — look at the brick. A2 should tell you in advance
whether this will bite.

---

# Results

| Test | Reading | Date | Verdict |
|---|---|---|---|
| Serial number | | | |
| A1 brick open-circuit | | | |
| A2 rail idle / **minimum** | | | |
| A3 ring–sleeve | | | |
| A3 tip–sleeve (both polarities) | | | |
| A4 V_open / V_loaded | | | |
| A5 drop / current / Z | | | |
| A6 decay to < 1 V | | | |
| B1 shortest reliable hold | | | |
| B3 feeds during 20 min hold | | | |

---

# Carry-forward to-dos — not meter work

Tracked in project memory as open items 1–13. These need no bench time:

| # | Item |
|---|---|
| 1 | **PCBWay requote** — check components on all 20 lines, C1 MPN or TDK alternate, F1, R6/R7, 28 joints, lead time. Then decide on payment |
| 2 | Paste `af4-feeder.yaml` into the ESPHome Device Builder + OTA — carries **both** GPIO13 → GPIO32 **and** the 10 s → 20 s / 290 s → 280 s change |
| 4 | `on_boot` lockout — `script.do_feed` state is RAM-only, so a reboot inside the 300 s cycle silently clears it |
| 5 | Widen the feed cycle past exactly 300 s, and widen check 6.3 from 10.3–10.5 V to ~10.0–10.9 V. If widening the cycle, widen the **tail**, not the pulse |
| 8 | `web_server: port: 80` has no `auth:`; API key and OTA password are committed in plaintext |
| 9 | `gen_pcb.py` stray "exclude from BOM/pos" flags on J2 |
| 11 | Retag `R1` `[VENDOR] ≥ 9 V held ≥ 15 s` and purge the unsourced 6 s from `aF4-reference.md`, `aF4-esp32-trigger-BOM.md`, `README.md`, `aF4-pcb-notes.md` |
| 12 | **Missed-feed alert in HA** — `counter.reef_af4_feeds_today` still 0 past the scheduled time. The only wholly unmonitored failure direction; also covers over-temperature faults, which never self-clear |
| 13 | Add link-LED checks as commissioning steps 6.7 / 6.8 |
| — | R5 is at 77 % of an 0805's rating at ~96 mW. A 0.25 W part is a drop-in if the margin is wanted — **decide before assembly** |
