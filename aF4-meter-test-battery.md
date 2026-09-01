# aF4 meter test battery

Bench procedure for closing the measurement-dependent open items.
Started **2026-09-01**. **None of it requires opening the aF4**, so the warranty
stays intact.

## Status at a glance

| Test | What it settles | State |
|---|---|---|
| **A1** brick open-circuit | Open item 7, TVS standoff | ✅ **DONE — PASS**, headroom amber |
| **A2** loaded rail at splitter tap | LM1117 dropout headroom | ✅ **DONE — ACCEPT, no board change.** Forces the check-6.3 widening |
| **A3** port pinout | Port impedance | 🟨 ring question **closed by A7**; both-polarity check outstanding |
| **A4** dongle voltage open vs loaded | The 10.4 V target | 🟨 **V_open = 10.35→10.37 V**; V_loaded still to do |
| **A5** port input current | Open item 6 | 🟨 inferred (~0.95 mA), needs powered confirmation |
| **A6** port decay time | R3 bleed value | ⬜ not run |
| **A7** OEM plug pinout | J2 ring-to-sleeve tie | ✅ **DONE** — tip + sleeve, ring floats. **Keep the tie, no board change** |
| **A8** dongle pulse shape | Whether inD's 10 s is dongle logic | ✅ **DONE — pass-through, no fixed pulse.** B1's premise stands |
| **B1** hold-time sweep | 6 s vs 15 s | ⬜ confirmatory only |
| **B2** re-arm interval | R2 | ⬜ low value, confounded |
| **B3** held-high = one feed | Audit finding B5 | ⬜ high value |
| **C** commissioning | Go-live gate | ⬜ needs the built hat |

**Suggested run order:** ~~A7~~ → **A2** → A4 and A8 together → A5 confirm → A6 →
B3 → B1 → B2.

---

## Why the order matters

The rev E order is submitted to PCBWay but **not paid and not fabbed**. This is
the last cheap window to act on a measurement.

- **Group A can change the board.** Run before paying.
- **Group B only changes firmware.** Any time.
- **Group C needs the built hat.** It is the commissioning pass.

---

## What is already settled

**From measurement, 2026-09-01:**

- **Brick open-circuit 12.13 V, stable, centre-positive.** Well under the SMAJ13A's
  13 V standoff → no idle TVS conduction. **Open item 7 closed.**
- **~11 kΩ tip-to-sleeve** on the port (unpowered, through a TS plug) → about
  **0.95 mA at 10.4 V**. Against an 18.7 mA quiescent budget and F1's 100 mA hold
  that is negligible. **Open item 6 effectively answered**, pending A5.
- **The OEM dongle's plug is TRS but carries only two wires** — one conductor is
  unused. See the teardown section; this is board-affecting.

**From inD's own documentation** (full account in `aF4-vendor-docs-notes.md`):

- **5-minute minimum spacing** between feeds — vendor-stated, so our 300 s cycle
  is now sourced rather than derived.
- **A held-high line yields exactly one feed** — the Apex guide's worked example
  holds ON for 14 minutes and produces one feed. Independent corroboration of
  audit finding B5.
- **`R1 = >6 s` is unsourced.** inD documents 15 s (Hydros) and 10 s (inD Connect).
  The 10 s pulse's claimed "67 % margin" is actually zero or negative.
- **Connecting the link port overrides the aF4's internal 24-hour schedule**, so an
  offline ESP32 means the fish are silently never fed.
- 12 V / 12.5 A brick confirms `R6`. Driving the port is documented, supported use.

---

## Decisions pending before payment

Three things could still change the board. Two are answerable at the bench in
under an hour.

1. ~~**A2's result.**~~ **CLOSED 2026-09-01 — ACCEPT, no board change.** Loaded
   minimum 11.77 V. Sits on the dropout boundary, but the output lands at ~10.47 V
   either way and threshold margin is ~1.5 V. **Forces the check-6.3 widening.**
2. ~~**J2's ring — tie or float.**~~ **CLOSED 2026-09-01 by A7 — keep the tie, no
   board change.** See A7 for the reasoning.
3. **R5's power rating.** It sits at ~96 mW against an 0805's 125 mW — **77 %**.
   A 0.25 W part is a drop-in. Raising the divider impedance is **not** available:
   it is the minimum-load ballast. Window closes at assembly.

---

## Prerequisites

| Item | Note |
|---|---|
| DMM | Any DC voltmeter. **Min/Max is NOT needed** — the load that matters is sustained. Film the meter during a feed if you want fine detail |
| **TRS** 3.5 mm breakout | Three separate pigtails, or a TRS screw-terminal adapter (~$5). A **TS breakout cannot do A3** — see the trap below |
| 100 Ω and 1 kΩ resistors | Bin stock, ¼ W fine |
| inD Connect dongle + eWeLink app | The known-good OEM signal source |
| Phone stopwatch | |
| Cup or container, ≥12 oz | |
| Sink or catch basin | |

**Never measure port current with the DMM in series in amps mode.** Burden voltage
is unpredictable, and a meter left in amps mode is the classic way to blow a fuse
or worse. A5 uses a series resistor — safer, and it yields input impedance free.

### Unit identity — recorded 2026-09-01

| Field | Value |
|---|---|
| Part number | **10102101** |
| Serial number | **130063** |

**The serial falls outside every range inD documents.** Their fan guide covers
`20XXX` / `60XXX` (full shutdown on over-temperature) and `100XXX` (standby with
continuous beeping, cooling continues, manual restart). A **130XXX is newer than
all of them**, so it most likely behaves like `100XXX` or newer — inference, not
documentation. Neither behaviour self-clears, and neither signals Home Assistant,
which is part of the case for the item-12 missed-feed alert.

**Consequence worth having:** the link LED's flash-green-on-feed-signal is
documented as "newer units only". This unit is newer than any published range, so
**commissioning step 6.8 should be available.**

The 2024 solenoid manufacturing defect inD references should not apply to a unit
this recent.

---

## Setup S1 — the safe feed configuration

Used by every test that triggers a real feed. This is inD's own pre-use-rinse
arrangement, so it is a documented-safe way to run the unit.

1. aF4 upright on a counter near a sink. **Never on its side.**
2. Reservoir at least half full of plain water. **No food** — it only makes cycles
   messy and results harder to read.
3. Black intake tube fully submerged in a cup with ≥12 oz of water.
4. Grey output tube into the sink or a catch container. **Not the tank.**
5. Power on with a firm 3-second press. Solid green LED.
6. Feed quantity set to **1 LED (5 mL)** — shortest cycle, least water.

**Every triggered feed is auto-followed by a self-clean, so budget 5 minutes per
trial.** A five-point sweep is a 25-minute test. Do not rush it by re-triggering
early — you will only be measuring the spacing lockout. Never run the pump dry.

---

# Group A — board-affecting

## A1 — brick open-circuit voltage ✅ DONE

**Result: 12.13 V, stable, centre-positive. Open item 7 closed.**

TVS verdict **PASS** — well under the SMAJ13A's 13 V standoff, so no idle
conduction and no part change. Headroom verdict **AMBER** — this is the bottom of
the healthy band, and it is the *open-circuit* figure. Load only lowers it, which
is what makes A2 the priority.

*Method, for reference:* brick unplugged from the aF4, still on mains, DMM on DC
volts. **Black probe on the outer metal barrel, red probe INTO the centre hole.**

> On a male DC barrel plug the positive contact is a **hollow tube, not a
> protruding pin** — the pin lives in the female jack on the device. "5.5 × 2.5"
> means a 5.5 mm outer barrel and a **2.5 mm hole**, and that hole is the positive
> contact. A needle probe drops in. If it will not sit steady, push a short length
> of stripped solid-core wire or a male header pin into the hole and probe that.

> **The brick is rated 12.5 A.** Red probe slipping onto the outer barrel is a dead
> short across ~150 W. A 0 V reading almost always means lost contact, not a dead
> supply.

## A2 — loaded rail voltage at the splitter tap ⬜ THE PRIORITY

This is the actual input to the hat's LM1117, minus the SS14's ~0.3 V. The master
reference already establishes how tight it is:

| Brick | LDO input | Headroom to 10.47 V |
|---|---|---|
| 12.2 V | 11.90 V | 1.43 V ✓ |
| 12.0 V | 11.70 V | 1.23 V ✓, but a worst-case divider is **in dropout** |
| 11.6 V | 11.30 V | **in dropout** |

The aF4 is a 12.5 A load running a TEC, pump, solenoid and fan off this brick.
Sag is entirely plausible and has never been measured. **A1's 12.13 V starting
point means there is less headroom in hand than the design assumed.**

### Run it on the FIRST power-on — that is the worst case

The feeder has never been powered. **The first cool-down from room temperature is
the heaviest sustained load the brick will ever see**, because the TEC runs flat
out while it is far from setpoint. A2 taken now is genuinely worst case.

inD also requires a **pre-use rinse** before first use, so the two fold into one
session. This procedure is their rinse with the measurement layered on top.

#### Step 0 — before plugging anything in

- **The tank mount and cleaning tablet ship INSIDE the reservoir.** Remove both
  before adding water or the tablet dissolves.
- Uncoil the tubing (factory-fitted, no assembly). Check contents against the
  packing list; contact support rather than installing anything damaged.
- **Write down the serial number** from the underside sticker while the unit is
  still easy to tip.

#### Step 1 — meter hookup, using the dongle as a breakout

Better than holding probes in a barrel connector, and it frees your hands.

1. OEM splitter **female** end → power supply.
2. Splitter **short male** → inD Connect dongle.
3. Splitter **long male** → aF4.
4. **Leave the dongle's 3.5 mm plug OUT of the aF4** — it must not assert during
   the test. The dongle is only a powered breakout here.
5. **Alligator-clip the DMM across J1's two solder lugs on the dongle board** —
   the raw barrel input, ahead of any protection. Clips, not handheld probes: this
   needs to run unattended for half an hour.
6. DC volts. **Min/Max is not required** — the TEC is a *sustained* load, so a
   plain meter reads it correctly, and pump/solenoid events last seconds, not
   milliseconds. For fine detail during a feed, **prop a phone and film the meter**,
   then scrub back: ~30 readings/sec, better than most Min/Max modes.

7. **Sanity-check the rig before trusting it.** With mains connected and the aF4
   still switched off, the meter should read **≈ 12.1 V**, matching A1. Anything
   wildly different means the clips are wrong — stop and re-check. Record it as
   the **baseline**.

Cross-check once against **TP_12V**. Same reading → fine. TP_12V a few hundred mV
lower → D1 is in series and TP_12V is not the number you want; **trust the J1 lugs**.

#### Step 2 — fill, per inD's rinse procedure

- Reservoir at least half full of **warm** water.
- Long black intake tube **fully submerged** in a glass or bowl with ≥ 12 oz.
- Grey output tube into the sink or a catch container. Unit upright.
- **Temperature setting 3 or higher if convenient**, but do not fuss: nothing
  freezes in half an hour from room temperature. The freezing risk applies only to
  running for *hours* at setting 1 with plain freshwater. Load is unaffected either
  way — during pull-down from ambient the TEC draws full power whatever the setpoint.
- Power on with a firm **3-second** press. Wait for solid green.

#### Step 3 — cool-down, 20–30 min (sustained maximum load)

Leave it running with the meter recording. Note the reading a minute or two in,
then walk away and come back for the captured minimum.

> **Watch the temperature LEDs on this first run.** All five flashing together is
> an over-temperature fault, and *when* it starts is the diagnosis: **immediately**
> = fan failure; **within 3 h** = bad probe; **after 3 h** = genuinely hot. This
> unit's serial is outside every documented range, so **record whether it beeps and
> holds in standby or shuts down outright** — that is a new data point and it tells
> you which recovery to expect. It will not self-clear either way.

#### Step 4 — rinse feeds (transient load on top of the TEC)

Still recording, run inD's rinse: press **Feed Now**, let the full cycle *including
auto-clean* finish, and repeat **two more times** — about 5 minutes each.

If nothing dispenses, run one **Auto-Clean** and retry Feed Now before worrying.

#### Step 5 — shut down

Power off and drain the reservoir.

**Completed 2026-09-01.** inD's pre-use rinse requirement is satisfied; the unit
has been flushed three times and is ready for first real use.

#### Record

The idle reading, and the **minimum across the whole session**.

| Minimum | Verdict |
|---|---|
| **≥ 12.2 V** | PASS — the headroom assumption holds |
| 12.0 – 12.2 V | Marginal. A worst-case divider rides dropout. Functional, unregulated |
| 11.6 – 12.0 V | **CONCERN** — nominal parts enter dropout during feeds |
| **< 11.6 V** | **Board-affecting.** Shared-rail approach needs rethinking — separate supply for the hat, or a different regulator topology |

Dropout is **not a safety failure**: the LM1117 degrades to roughly V_IN − 1 V,
still inside the 9–11 V window, so feeds still trigger. What is lost is regulation
and ripple rejection. But if this lands under 12.0 V, say so **before paying** —
far cheaper to change now than after assembly.

Short sub-100 ms transients would need a scope; do not chase them — the hat's
10 µF input cap rides through those anyway. Sustained sag is the whole question.

**Report four numbers:** baseline (aF4 off), idle with the TEC running, lowest
during cool-down, lowest during a feed.

**Given A1's 12.13 V unloaded, anything but a small sag lands in the marginal band
immediately.** That is precisely what is worth knowing before paying.

> **Two cautions.** The dongle is an open board carrying 12 V — keep it off
> anything conductive and never bridge J1's lugs, which is a dead short across a
> 12.5 A supply. And do not short the boost output; live 10 V rail with an
> inductor behind it.

### A2 VERDICT, 2026-09-01 — ACCEPT. No board change.

| Reading | Value |
|---|---|
| Baseline, aF4 off | 12.13 V |
| Idle, TEC running | 11.84 → 11.86 V (sag 0.29 V, stable) |
| **Minimum during feed** | **11.77 V**, recovering immediately |
| Repeatability | **Floor held at 11.77 V across all three rinse cycles** |

The feed adds only **0.09 V** over the TEC load — pump and solenoid are minor
next to the TEC, so there is no transient risk hiding behind the steady figure.
**Confirmed over three complete feed + auto-clean cycles**: same floor each time,
immediate recovery, no drift or droop as the run went on — which is where a
genuinely marginal supply would have shown itself.
Total sag from baseline 0.36 V. Measured under the heaviest conditions the unit
will ever see: first pull-down from ambient, TEC flat out, feed stacked on top.

**Worst case:** 11.77 V − 0.3 V (SS14) = **11.47 V at the LDO**, giving exactly
**1.00 V** headroom against ~1 V of dropout — precisely on the boundary.

**Why that is a non-event:**

1. **In dropout the output lands where regulation would have put it.**
   11.47 − 1.0 ≈ **10.47 V**, versus a 10.47 V regulated target. The two answers
   converge at this input voltage.
2. **Threshold margin is ~1.5 V.** For the output to fall under 9 V the brick
   would have to sag to ~10.3 V. Nothing in a feed cycle approaches that.
3. **Dropout makes the divider tolerance BETTER, not worse.** With the pass device
   saturated, V_OUT follows V_IN regardless of what R4/R5 ask for — so the
   worst-case-high stack the audit flagged simply sits at ~10.47 V instead of
   10.88 V. Real spread becomes ~10.08–10.5 V, **tighter than designed**.
4. **~1 V dropout is the audit's conservative figure.** At 20 mA the true value is
   likely lower, in which case it regulates normally and none of this applies.
5. **What is lost — regulation and PSRR — is not needed.** The port is a threshold
   input with a ≥10 s hold, not an analog input. It cannot tell the difference.

**Considered and rejected:** retargeting the divider lower to guarantee regulation.
That trades a known-good 10.5 V for a lower voltage with less threshold margin, to
fix something that is not causing harm.

### ⚠️ This makes the check-6.3 widening MANDATORY

Check 6.3 currently demands **10.3–10.5 V at TP2**. A low-tolerance board
legitimately regulating at **10.08 V** would **fail commissioning while working
perfectly**. Open item 5's widening to **~10.0–10.9 V** is no longer optional —
leaving it will send someone chasing a fault that does not exist.

---

## A3 — port pinout ⚠️ BLOCKED, superseded by A7

**Partial result: ~11 kΩ tip-to-sleeve, unpowered, one polarity.** Still to do:
the same measurement in **both probe polarities** — if they differ there are
protection diodes and the plain resistance model does not hold.

> **A 2-conductor TS plug CANNOT measure ring-to-sleeve.** Its sleeve spans both
> the ring and sleeve contacts inside the jack, tying them together before the aF4
> gets a say. Through a TS plug the reading is always a short, whatever the aF4
> does internally.

The ring question is now better attacked from the OEM side — see **A7**.

*Full method if a TRS breakout is on hand:* aF4 powered off and unplugged, TRS
breakout inserted, DMM on lowest ohms. Ring–sleeve expected short (< 1 Ω);
tip–sleeve high, both polarities.

## A4 — dongle output voltage, open-circuit vs loaded ⬜

The project carries a measured 10.37 V from the OEM dongle but not whether that
was open or loaded. The distinction sets what the hat should target.

1. Dongle powered through its splitter, 3.5 mm plug **not** in the aF4.
2. Assert the dongle (eWeLink toggle ON) and hold.
3. Measure tip–sleeve at the free plug → **V_open**.
4. Seat the plug into the aF4 through the breakout so you can probe connected.
   Assert again → **V_loaded**.

| Result | Meaning |
|---|---|
| V_open ≈ V_loaded | Port draws almost nothing; load-budget assumption confirmed |
| V_loaded materially lower | Port draws real current and the dongle has output impedance. **Not a problem for the hat** — the LM1117's output impedance is far lower and will hold 10.4 V |
| V_loaded < 9 V | Something is wrong with the dongle or breakout. Stop and re-check |

Both should sit comfortably inside the 9–11 V window. **Do this together with A8** —
same setup, same trigger.

## A5 — port input current and impedance 🟨 inferred, confirm under power

**Inferred: ~0.95 mA** from A3's 11 kΩ at 10.4 V. Negligible against an 18.7 mA
quiescent budget (20.0 mA during a feed) and F1's 0.10 A hold. Confirm powered:

1. Inline through the breakout: **dongle tip → 100 Ω → aF4 port tip.** Sleeves common.
2. Assert the dongle and hold.
3. Measure the voltage **across the 100 Ω**. Current = V / 100.

| Drop across 100 Ω | Current | Verdict |
|---|---|---|
| < 1 mV | < 10 µA | High-Z. Assumption confirmed, done |
| 1 – 100 mV | 10 µA – 1 mA | Negligible. **Expected — matches the 11 kΩ inference** |
| 0.1 – 2 V | 1 – 20 mA | Acceptable; recheck the AQY212GS load-current rating |
| > 2 V | > 20 mA | **Board-affecting.** Recheck LM1117 dissipation, F1's hold, AQY212GS on-resistance |

If readable, repeat with **1 kΩ** to test linearity — a resistive input scales
proportionally, a comparator or opto input will not. Compute **Z ≈ V_loaded / I**.

## A6 — port decay time ⬜

R3 is a 100 kΩ bleed returning the port to 0 V after a feed. Its time constant
depends on capacitance inside the port.

1. Dongle connected through the breakout, DMM on DC volts tip–sleeve.
2. Assert 20 s, then release.
3. Time the fall below **1 V**. Stopwatch is fine.

| Decay to < 1 V | Meaning |
|---|---|
| **Under 1 s** | Port self-discharges; R3's value irrelevant. No change |
| 1 – 10 s | Some capacitance. R3 100 kΩ still works; note the constant |
| **Over 10 s** | Consider dropping R3 to 10 kΩ. **Board change — decide now** |

**Expectation given A3:** the port's own ~11 kΩ is nine times stiffer than R3's
100 kΩ, so it should self-discharge quickly and R3 should prove harmless but
largely redundant. This test confirms or refutes that.

## A7 — OEM plug pinout ✅ DONE · ring question CLOSED

**Result: TIP + SLEEVE. Ring floating.** Black wire = sleeve (0 Ω), ring = O/L,
tip = the red wire. **Our pinout is correct — no J2 redesign.**

> **Reading note.** Tip-to-black measured 17–18 MΩ *and climbing*. That is not a
> resistance, it is the dongle's 10 V rail capacitance charging off the DMM's ohms
> source. It matched red-to-black on the board, which is what identifies tip and
> the red wire as the same node. The clean confirmation is **tip to the red
> terminal ≈ 0 Ω**.

### Decision: KEEP the ring-to-sleeve tie. No board change.

`aF4-MASTER-REFERENCE.md` already carries the fact that settles it, `[MEAS]
2026-07-10`: the link icon is **mechanical** — *"a bare plug with nothing attached
lights it. Jack insertion switch, no electrical sensing."*

A bare plug means all three contacts floating and the aF4 is happy. So the ring is
not a detect line, not a sense input, not anything. inD leaving it unwired agrees.

Both states are therefore demonstrated safe: **floating** (bare plug, OEM cable)
and **tied to sleeve** (what any TS plug does at the jack).

**The tie is also the more robust choice**, which earlier notes in this document had
backwards. Floating the ring on the board only genuinely floats it if a **TRS**
cable is used — a mono cable grounds it at the jack regardless, silently. Tying it
on the board makes behaviour cable-independent, which is what a design rebuilt
years later from the BOM needs. The BOM's "mono or stereo, either is fine" stands.

Residual risk is small enough to accept. To eliminate rather than reason it away:
a $5 TRS breakout and one ring-to-sleeve measurement on the aF4, unit off. **Not
worth holding the order for.**

---

*Original method, for reference:*

The teardown showed a **TRS plug with only two wires** at J2. Which two decides a
board question.

1. Dongle unplugged from power.
2. DMM on continuity.
3. Ring out **each** of the two J2 wires against the plug's **tip**, **ring**, and
   **sleeve** in turn.

| Result | Meaning |
|---|---|
| **Tip + sleeve** | Expected. Ring floats in the OEM cable → see the two routes below |
| **Tip + ring** | **Our pinout is wrong.** Stop and redesign J2 before anything else |

**If tip + sleeve, pick one before paying:**

| Route | What it means |
|---|---|
| **Match the OEM** | Leave J2's ring **unconnected** and **specify a TRS patch cable**. Ring floats end to end exactly as inD does it. Promotes the cable from "mono or stereo, either is fine" (as `aF4-esp32-trigger-BOM.md` says today) to a **design requirement** — a TS plug shorts ring to sleeve at the jack no matter what the board does |
| **Prove and keep** | Buy a TRS breakout, measure the aF4's ring to sleeve with the unit off, and keep the tie if it is already grounded |

Grounding a contact the OEM leaves floating is very likely harmless — but
"likely" is doing the work, and this is the last moment it is free to change.

## A8 — dongle pulse shape at TP_10V0 ⬜ NEW · high information

The dongle has a microcontroller, so inD's "ON for at least 10 seconds" may
describe the *dongle's* logic rather than the aF4's threshold. This separates them.

1. Dongle open, powered. Meter on **TP_10V0 / TP_GND**.
2. Trigger from the eWeLink app. Hold the toggle ON for ~30 s, then release.
3. Watch when the 10 V rail rises and — the point of the test — **when it falls**.

| Behaviour | Meaning |
|---|---|
| Rail follows the toggle | Pass-through. The 10 s figure really is about the port, and **B1's premise stands** |
| Rail drops after a **fixed** interval regardless of the toggle | The dongle generates its own pulse. inD's "10 seconds" is dongle logic, not an aF4 threshold — **B1 is reframed**, and the fixed width is the number to copy |

Record the fixed width if there is one; that is the OEM's own answer to "how long
should a pulse be," which is exactly what item 11 is guessing at.

> **Do not short the boost output.** That is a live 10 V rail with an inductor
> behind it.

### A4 / A8 findings, 2026-09-01

Measured on the OEM plug, clips on tip and sleeve, dongle **not** in the aF4.

| Time | Reading |
|---|---|
| 0:00 | 0.001 V (rest) |
| 0:02 | **16.40 V** — spike, immediately gone |
| 0:21 | 10.35 V |
| 0:40 | 10.36 V, creeping to 10.37 |
| 1:00 | 0.002 V, only after the app toggle was tapped OFF |

**A8 — the dongle passes the toggle through; it does NOT emit a fixed-width
pulse.** It held for the full minute. So inD's "ON for at least 10 seconds"
describes the **port**, not dongle logic. **B1's premise stands and the 15 s
Hydros figure remains the number to beat — the 20 s pulse decision is confirmed.**

This also explains inD's otherwise-arbitrary "every ON needs a paired OFF one
minute later": the dongle simply holds the line, a held line yields exactly one
feed (audit B5), and every later ON is a no-op against an already-asserted port.
Our firmware already pulses and releases correctly.

**A4 — V_open 10.35 → 10.37 V.** Confirms the project's long-standing 10.37 V and
pins down that it was an **open-circuit** figure. Rest voltage 0.001–0.002 V
confirms `[MEAS]` "rest voltage is genuinely 0 V".

**The 16.40 V spike is boost-converter startup overshoot. Benign. No board change.**

- The dongle makes 10 V with a boost converter (L1, U1, D1). Boost topologies
  overshoot before the feedback loop closes, and **worst when unloaded** — exactly
  how this was measured, plug hanging free with nothing to sink the charge.
- **The hat cannot reproduce it and does not need to.** It switches a
  *pre-regulated* 10.4 V rail through the PhotoMOS: no boost stage, no mechanism to
  exceed the rail. The spike is incidental to the dongle's topology, not part of
  the signalling — Hydros and Apex drive the port from analog outputs with no
  overshoot and work fine.
- **Useful positive result:** the aF4's port takes a ~16 V transient on every
  OEM-triggered feed and is fine, so the worst-case 10.88 V rail is nowhere near
  stressing it.
- Even the odd case of the dongle and the hat split onto one port is covered —
  D4's 14.4–15.9 V breakdown clamps it, which is D4 doing its job.

⚠️ For a handheld DMM to latch and display 16.40 V the event probably lasted tens
of milliseconds, not microseconds. A scope would settle it; not needed.

**Still to do:** repeat **plugged into the aF4** for V_loaded, and see whether the
overshoot survives a real ~11 kΩ load. Two minutes, completes A4.

---

# Group B — firmware only, any time

The move from a 10 s to a 20 s pulse is **already safe under every documented
figure**, so B1 is confirmatory. Do not delay the firmware change waiting for it.

## B1 — hold-time sweep ⬜

Setup S1. Assert the dongle for a measured duration, release, wait a full
5 minutes, repeat. Sweep **5 s, 8 s, 12 s, 16 s, 20 s**.

Record per trial: did water dispense? did the link LED flash green?

eWeLink round-trips over WiFi, so treat each duration as **±1–2 s**. Once you find
the boundary, run it twice more to confirm it is repeatable and not latency.
Expect an answer between 6 s and 15 s; 20 s clears whatever it is.

**Run A8 first** — if the dongle emits a fixed-width pulse, this sweep is measuring
the dongle, not the aF4, and the result would be meaningless.

## B2 — re-arm interval ⬜ low value, confounded

Assert 20 s, release, wait N, assert 20 s again. N = 30 s, 60 s, 120 s, 300 s.

**The confound:** the documented 5-minute spacing blocks any second feed under
300 s regardless of the true re-arm time, so this can only confirm the *combined*
constraint, never isolate R2. The practical answer is already known — 300 s works,
and that is what the firmware does. Completeness only.

## B3 — held-high yields exactly one feed ⬜ high value

Validates the design's best safety property on your own unit. Audit finding B5 and
the whole held-high failure analysis rest on it, and it is currently only
vendor-documented.

1. Setup S1.
2. Assert the dongle and **leave it on for 20 minutes.**
3. Count dispense events. Expect **exactly 1**.
4. Release, wait 5 minutes, assert 20 s, confirm it feeds again — proving the port
   re-arms after a long hold.

More than one feed would mean the held-high analysis is wrong and the failure
bounding in the master reference needs revisiting. That would be significant.

---

# Group C — after the hat is built

Existing commissioning steps 6.1 – 6.6 from `aF4-assembly-guide.md`, plus two the
vendor documentation made available:

- **6.7** — plug the patch cable into J2. **Link LED goes solid** = the port sees
  the connection.
- **6.8** — press the HA feed button. **Link LED flashes green** = the 10.4 V pulse
  was accepted, confirmed without waiting to watch food move.

**Known inconsistency:** checks 6.2 and 6.3 are mutually inconsistent at their
edges. A brick legitimately passing 6.2 at 11.6 V cannot deliver 10.3 V at TP2
even with perfect parts. If 6.3 reads low after a low-but-passing 6.2, the divider
is probably innocent — look at the brick. A2 should predict whether this will bite.

---

# OEM teardown reference, 2026-09-01

The inD Connect dongle, opened:

- Board **inD connect_V0.0**. WiFi is an **SM-028_V1.3** daughterboard carrying a
  **Bouffalo Lab BL602C20**. A 5-pin header (likely UART) is populated.
- On-board boost converter (L1, U1, D1) makes the 10 V rail. Test points **TP_12V,
  TP_10VI, TP_10V0, TP_GND, TP_L, TP_W1, TP_W2, TP_C, TP_B, TP_3V3** all labelled
  and exposed.
- **The 3.5 mm plug is TRS but only TWO wires land at J2.** One conductor unused.

### On repurposing it

**Reflashing the BL602 is not recommended.** ESPHome does not target it,
LibreTiny's BL602 support is uncertain (verify before believing it), and the result
would be a 2.4 GHz WiFi device with none of the hat's protection or on-device
guardrails — strictly worse than the board already designed.

**The eWeLink HA integration is worth doing**, as a stopgap and a test rig. No
soldering, gives HA-scheduled feeding before the PCB arrives, and lets the
`counter.reef_af4_feeds_today` logic, the lockout condition and the item-12
missed-feed alert be proven against real hardware ahead of commissioning.

---

# Results

| Test | Reading | Date | Verdict |
|---|---|---|---|
| Part / serial number | **10102101 / 130063** | 2026-09-01 | Outside all documented serial ranges — newer than `100XXX` |
| A1 brick open-circuit | **12.13 V, stable** | 2026-09-01 | TVS **PASS**, open item 7 closed. Headroom **AMBER** — bottom of band, open-circuit; makes A2 critical |
| A2 baseline (aF4 off) | **12.13 V** | 2026-09-01 | Matches A1 — rig verified |
| A2 idle, TEC running | **11.84 V @ 1 min, 11.86 @ 3 min** | 2026-09-01 | Sag **0.29 V**, stable. LDO input ≈ 11.54 V → **1.07 V headroom vs ~1 V dropout — at the boundary**; worst-case divider in dropout |
| A2 minimum during feed | **11.77 V** — held across **all 3 rinse cycles** | 2026-09-01 | Feed adds only **0.09 V**, immediate recovery, no drift cycle to cycle. **PASS — no board change** |
| A3 tip–sleeve, polarity 1 | **11 kΩ** (unpowered, TS plug) | 2026-09-01 | ~0.95 mA at 10.4 V — negligible |
| A3 tip–sleeve, polarity 2 | | | Differing values ⇒ protection diodes present |
| A3 ring–sleeve | blocked by TS plug | 2026-09-01 | Superseded by A7 |
| A4 V_open | **10.35 V settling to 10.37 V** | 2026-09-01 | Confirms the historic 10.37 V and identifies it as **open-circuit**. Rest = 0.001–0.002 V |
| A4 V_loaded | | | Still to do |
| **A4 turn-on overshoot** | **16.40 V**, unloaded, brief | 2026-09-01 | Boost startup overshoot. **Benign — no board change** |
| A5 drop / current / Z | | | Expect ~1 mA, matching A3 |
| A6 decay to < 1 V | | | Expect fast, given the port's own 11 kΩ |
| **A7 OEM plug: which 2 wires** | **TIP + SLEEVE, ring floats** | 2026-09-01 | Pinout correct. **Ring tie KEPT** — link detect is mechanical, so the ring is unused |
| **A8 dongle pulse width** | **none — pass-through** | 2026-09-01 | Held ~60 s until toggled off. inD's "10 s" is about the port, not the dongle |
| B1 shortest reliable hold | | | |
| B3 feeds during 20 min hold | | | |

---

# Carry-forward to-dos — not meter work

Tracked in project memory as open items 1–14.

| # | Item |
|---|---|
| 1 | **PCBWay requote** — components on all 20 lines, C1 MPN or TDK alternate, F1, R6/R7, 28 joints, lead time. Then decide on payment |
| 2 | Paste `af4-feeder.yaml` into the ESPHome Device Builder + OTA — carries **both** GPIO13 → GPIO32 **and** the 10 s → 20 s / 290 s → 280 s change |
| 4 | `on_boot` lockout — `script.do_feed` state is RAM-only, so a reboot inside the 300 s cycle silently clears it |
| 5 | Widen the feed cycle past exactly 300 s, and widen check 6.3 from 10.3–10.5 V to ~10.0–10.9 V. If widening the cycle, widen the **tail**, not the pulse |
| 8 | `web_server: port: 80` has no `auth:`; API key and OTA password committed in plaintext |
| 9 | `gen_pcb.py` stray "exclude from BOM/pos" flags on J2 |
| 11 | Retag `R1` `[VENDOR] ≥ 9 V held ≥ 15 s` and purge the unsourced 6 s from `aF4-reference.md`, `aF4-esp32-trigger-BOM.md`, `README.md`, `aF4-pcb-notes.md` |
| 12 | **Missed-feed alert in HA** — `counter.reef_af4_feeds_today` still 0 past the scheduled time. The only wholly unmonitored failure direction; also covers over-temperature faults, which never self-clear |
| 13 | Add link-LED checks as commissioning steps 6.7 / 6.8 |
| 14 | **R5 at 77 % of an 0805's rating.** 0.25 W part is a drop-in. Decide before assembly — raising the divider impedance is NOT available, it is the minimum-load ballast |
