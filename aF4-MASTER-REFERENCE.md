# aF4 PoE Trigger — Master Reference (rev E)

**Purpose of this document.** A single consolidated reference for the aF4 frozen-feeder
PoE trigger project, written to be *audited*. Every load-bearing claim carries a provenance
tag so a reviewer can tell what has been verified against a primary source and what is an
assertion that has not. The assertions are the interesting part — attack those first.

> 🔑 **Do not read this file whole** — it costs ~16,000 tokens. Use the section index
> below, then `grep -n "^### 2.4"` and read only that range.
>
> 🚫 **This file does not describe current state.** For phase, what may be trusted, and the
> open-items ledger, read **`STATUS.md`** — it is the only live-status document in this
> project. §8 below is the ledger of record for **item numbering**; `STATUS.md` is the
> ledger of record for **what is still open**.

Generated 2026-08-28, revised after independent audit the same day, after the 2026-09-01
bench and vendor-documentation passes, and after the 2026-09-02 order went to fabrication. Canonical source for this file is the repo; the other project docs
(`docs/aF4-reference.md`, `docs/aF4-pcb-notes.md`, `docs/aF4-esp32-trigger-BOM.md`,
`docs/aF4-enclosure-notes.md`, `docs/aF4-assembly-guide.md`) remain authoritative in their own areas
and go deeper. This document does not replace them; it makes the whole thing checkable in
one pass.

## Provenance tags used throughout

| Tag | Meaning |
|---|---|
| `[MEAS]` | Kenny measured it on the physical hardware, date given |
| `[DS]` | Read off the manufacturer datasheet, verified 2026-08-28 |
| `[DIST]` | Manufacturer part number confirmed as a real, stocked part at a distributor, 2026-08-28 |
| `[CAD]` | Taken from vendor CAD source (Olimex ESP32-POE-ISO Rev N KiCad files) |
| `[SPEC]` | From inD aquatics' published 0-10 V setup guide |
| `[CALC]` | Derived. Inputs and working shown so the arithmetic can be rechecked |
| `[ASSERT]` | **Stated but not independently verified.** Treat as unproven |

---

<!-- SECTION-INDEX -->
## Section index

> 🔑 **Do not read this file whole.** Find the section here, then read only its
> line range. Numbers drift — confirm with `grep -n "^### 2.4" <file>`.

  - §A1 U1 is on the wrong footprint — the board cannot be built `[AUDIT]` — L94
  - §A1.1 FIXED — a project-local footprint built from Panasonic's drawing — L112
  - §A1.2 Rejected: `SO-4_4.4x4.3mm_P2.54mm`, matched on dimensions but not on pad shape — L135
  - §A1.3 Isolation, re-derived `[AUDIT]` — L164
  - §A2 `pcb/gen_pcb.py` says `SMAJ15A` for D2; everything else says `SMAJ13A` `[AUDIT]` — L186
- **§1 What the system must do** — L197
  - §1.1 Requirements — L205
  - §1.2 Measured facts about the port — L216
  - §1.3 ⚠️ `[VENDOR] 2026-09-01` inD publishes THREE different hold times — L233
  - §1.4 ✅ `[VENDOR] 2026-09-01` RESOLVED — and the assumption was backwards — L273
- **§2 Circuit** — L302
  - §2.1 Regulator — the calculation that matters — L349
  - §2.2 Load on the 10.4 V rail — L382
  - §2.3 PhotoMOS drive — L433
  - §2.4 The GPIO13 problem — why the trigger is on GPIO32 — L458
  - §2.5 Protection — L500
  - §2.6 Indicator LEDs — L523
- **§3 Bill of materials — with verification status** — L557
  - §3.1 Sourcing traps recorded — L586
  - §3.2 Bought separately (not on the board) — L594
- **§4 Board** — L602
  - §4.1 Geometry from vendor CAD `[CAD]` — L619
  - §4.2 Verification status of the board — L629
  - §4.3 Isolation — L651
- **§5 Firmware** — L666
  - §5.1 The safety architecture — L672
  - §5.2 Timing check against the spec `[CALC]` — L689
  - §5.3 ✅ `[AUDIT]` The lockout did not survive a reboot — CLOSED 2026-09-01 — L709
  - §5.4 ✅ `[AUDIT]` The web server was a second, unauthenticated control path — CLOSED 2026-09-01 — L733
  - §5.5 ✅ The related hygiene problem — the worse one — CLOSED 2026-09-02 — L744
  - §5.6 `[AUDIT]` Held-high failure modes are bounded — the design's best safety property — L762
  - §5.7 Home Assistant integration — L773
- **§6 Enclosure** — L845
  - §6.1 The vertical stack — the governing dimension — L852
  - §6.2 Two details that are easy to lose — L873
- **§7 Errors already found and fixed** — L893
  - §7.1 The inverse failure mode, named 2026-09-02 — L927
- **§8 Open items** — L947
  - §8.1 Commissioning gate (from `docs/aF4-assembly-guide.md` §6) — L989
- **§9 Repository map** — L1020
  - §9.1 Toolchain constraints worth knowing — L1040
- **§10 Audit status** — L1051
  - §10.1 Still unverified after the audit — L1067
  - §10.2 Bench work still unrun (`docs/aF4-meter-test-battery.md`) — L1101

<!-- /SECTION-INDEX -->

---

## A. Build blockers

### A1. U1 is on the wrong footprint — the board cannot be built `[AUDIT]`

`pcb/gen_pcb.py` places U1 on KiCad's `Package_SO:SO-4_4.4x2.3mm_P1.27mm`. That footprint's
own description points at an **OPTEK OPIA403** optocoupler: pads at x = ±3.15 mm,
y = ±0.635 mm — a **1.27 mm terminal pitch**.

The Panasonic AQY212GS is not that package. From Panasonic's own GU SOP4 datasheet
(`semi_eng_gu_sop4_1a.pdf`) `[DS]`:

| Parameter | AQY212GS (Panasonic) | Footprint in use |
|---|---|---|
| **Terminal pitch** | **2.54 mm** | **1.27 mm** ❌ |
| Body | 4.4 × 4.3 mm | 4.4 × 2.3 mm ❌ |
| Lead span, tip to tip | 6.8 ± 0.4 mm | 6.30 mm pad centres |
| Recommended pad | 0.5 × 1.0 mm on 2.54 mm pitch | 0.64 × 2.0 mm on 1.27 mm |

Every pin missed its pad by ~0.635 mm along the pin row.

### A1.1 FIXED — a project-local footprint built from Panasonic's drawing

**Final answer: `pcb/footprints/aF4.pretty/AQY212GS_SOP4_Panasonic.kicad_mod`**, authored from the
"Recommended mounting pad (TOP VIEW)" drawing in `semi_eng_gu_sop4_1a.pdf`:

| Panasonic recommended pad | Value |
|---|---|
| Pad size | **0.8 mm** across the pitch axis × **1.2 mm** along the lead axis |
| Pad centres, pitch axis | 2.54 mm |
| Pad centres, span axis | **6.0 mm** (±3.0) |
| Tolerance | ±0.1 mm |

Pads therefore span 2.40–3.60 mm from the part centre, against a lead tip at 3.2–3.6 mm
(6.8 ± 0.4 span). Toe lands on the pad across the whole tolerance range.

> **An interim fix got this wrong in an instructive way.** Before the drawing was readable,
> KiCad's `SO-4_4.4x4.3mm_P2.54mm` was used — it has the correct pad **centres** (±3.0,
> ±1.27) and an exact body match, but **its pads are rotated 90°**: 0.8 mm along the lead
> axis where Panasonic asks for 1.2 mm, and 1.2 mm across the pitch axis where Panasonic
> asks for 0.8 mm. The part would have mounted, but with no toe fillet at the far end of the
> lead-span tolerance. A footprint can match on pitch, body and pad centres and still be the
> wrong land pattern. **Read the drawing.**

### A1.2 Rejected: `SO-4_4.4x4.3mm_P2.54mm`, matched on dimensions but not on pad shape

`SOP-4_3.8x4.1mm_P2.54mm` was rejected: right pitch, but pad centres only 5.50 mm apart,
too narrow for a 6.8 mm lead span. The footprint now used matches Panasonic on every
dimension that exists in both:

| | Panasonic AQY212GS | `SO-4_4.4x4.3mm_P2.54mm` |
|---|---|---|
| Body | 4.4 × 4.3 mm | F.Fab outline 4.4 × 4.3 mm — exact |
| Terminal pitch | 2.54 mm | pads at y = ±1.27 — exact |
| Lead span | 6.8 ± 0.4 mm → tips at 3.2–3.6 | pads span 2.6–3.4 from centre |
| Pad 1 quadrant | — | unchanged, so the netmap needed no edit |

**Regenerated in full:** `pcb/gen_pcb.py` → `pcb/post.py` → Gerber/drill export → `pcb/make_package.py`.
Three routing waypoints that had been hard-coded to the old pad rows now derive from the
pad positions. The "ISOLATION BARRIER" silk text moved from y 128.00 to 125.50, because the
taller footprint pushed U1's reference designator onto it.

**Verification:** DRC returns **61 items, identical in class and count to the pre-fix
board** — 0 clearance, 0 courtyard, 0 hole, 0 copper-to-edge, 0 unconnected, 0 mask
bridges; the remainder are the same silkscreen and library-footprint cosmetics as before.
Drill tools 0.450 / 0.700 / 0.800 / 1.000 / 1.200 / 2.130 / 3.200 mm, no plated slot under
0.70 mm. BOM ≡ PARTS ≡ board refs (21). Centroid 17 SMD. The board was also **rendered and
looked at**, not merely measured.

`pcb/gen_pcb.py`'s `load()` now checks a project-local `footprints/` directory before the stock
KiCad libraries, so `aF4.pretty` holds any part whose stock footprint is wrong for the part
actually being bought.

### A1.3 Isolation, re-derived `[AUDIT]`

The **"4.3 mm pad-to-pad across U1"** figure is **withdrawn** — it was the copper gap of the
OPIA403 pattern, not of the AQY212GS. The real numbers, measured off the regenerated board:

| | Value |
|---|---|
| U1 pad-to-pad copper gap | **4.80 mm** (was 4.30 on the wrong footprint) |
| Copper-free band, by design | 4.70 mm, x 121.65–126.35 |
| **True minimum logic-to-power creepage** | **4.425 mm** (was **4.225 mm** before the fix) |

The governing constraint is **not U1** — it is **R1 pad 2**, whose logic-side copper reaches
x 121.925 and intrudes 0.275 mm into the nominal band, against the GNDP pour edge at
126.350. That was true of the old board too; the footprint fix improved the real creepage by
0.2 mm. Both mounting holes inside the band are **NPTH — no copper**. Zone fills stop
exactly on the band edges. At 4.4 mm between two SELV domains, creepage is nowhere near the
weak link in the 1500 Vrms argument.

*How it got past DRC: the same mechanism as the slot widths — DRC checks pads against
tracks, not pads against the physical part. The footprint was well-formed and wrong,
which is this project's signature failure mode (§7).*

### A2. `pcb/gen_pcb.py` says `SMAJ15A` for D2; everything else says `SMAJ13A` `[AUDIT]`

The BOM, `pcb/make_package.py` and all prose specify SMAJ13A. Turn-key sources from the BOM,
so the boards would have received the 13 V part — but the "source of truth" script
contradicted the BOM. **Fixed 2026-08-28:** the script now says SMAJ13A. If a 15 V
standoff was ever the intent it was never propagated anywhere, and adopting it
deliberately would close the open-circuit-voltage question in §2.5 by fiat
(SMAJ15A breakdown 16.7–18.5 V still clamps far under the AQY212's 60 V rating).

---

## 1. What the system must do

Replace the inD connect WiFi dongle on an inD aquatics aF4 refrigerated frozen-food feeder
with an Olimex ESP32-POE-ISO running ESPHome, so feeds can be scheduled from Home Assistant.

The aF4 exposes a 3.5 mm "0-10 V" trigger port. It is a **threshold input, not an analog
level** — no DAC is required.

### 1.1 Requirements

| # | Requirement | Value | Source |
|---|---|---|---|
| R1 | Trigger threshold | ≥ 9 V held **≥ 15 s** | `[VENDOR] 2026-09-01` — see note |
| R2 | Re-arm | port must see ~0 V for > 60 s | `[SPEC]` — verbatim from inD's Neptune Systems page, audit-verified 2026-08-28 |
| R3 | Minimum feed spacing | ≥ 5 minutes | `[VENDOR] 2026-09-01` — Apex guide states it |
| R4 | Do not drive the port with raw 12 V | OEM dongle measured at **10.37 V** | `[MEAS] 2026-07-10` |
| R5 | Feeder must stay powered continuously | it is a refrigerator | `[SPEC]` |
| R6 | Supply | 12 V, 12.5 A external brick, barrel **5.5 × 2.5 mm centre-positive** | `[MEAS] 2026-07-10` |

### 1.2 Measured facts about the port

| Measurement | Result | Source |
|---|---|---|
| Tip↔sleeve at rest | 0 V | `[MEAS] 2026-07-10` |
| Tip↔sleeve during an OEM-triggered feed | 10.37 V | `[MEAS] 2026-07-10` |
| "Link" icon mechanism | **mechanical** — a bare plug with nothing attached lights it. Jack insertion switch, no electrical sensing | `[MEAS] 2026-07-10` |
| Consequence | no bleed resistor needed for link detect; rest voltage is genuinely 0 V | `[CALC]` |
| Tip↔sleeve resistance, unpowered | **~11 kΩ** → **~0.95 mA at 10.4 V** | `[MEAS] 2026-09-01` |
| OEM plug wiring | **TRS plug, only tip + sleeve wired. Ring floats** | `[MEAS] 2026-09-01` |
| OEM dongle output, open-circuit | 10.35 V settling to **10.37 V** — confirms R4 was an *open-circuit* figure | `[MEAS] 2026-09-01` |
| OEM dongle turn-on overshoot | **16.40 V**, brief, unloaded — boost startup overshoot | `[MEAS] 2026-09-01` |
| OEM dongle pulse behaviour | **pass-through, no fixed-width pulse** — holds until toggled off | `[MEAS] 2026-09-01` |
| 12 V brick, open-circuit | **12.13 V**, stable, centre-positive | `[MEAS] 2026-09-01` |
| 12 V rail loaded (TEC + feed) | idle **11.84–11.86 V**, minimum **11.77 V** across 3 feed cycles | `[MEAS] 2026-09-01` |
| aF4 unit under test | PN **10102101**, SN **130063** — outside every documented serial range | `[MEAS] 2026-09-01` |

### 1.3 ⚠️ `[VENDOR] 2026-09-01` inD publishes THREE different hold times

R1 previously read **`≥ 9 V held > 6 s`**. That figure is genuine: the 2026-08-28 audit
fetched inD's **Neptune Systems page** and quoted it verbatim — *"9v or higher signal for
greater than 6 seconds"*. R1–R3 were all verified against that page. **The 6 s was not
invented.**

The problem is that inD's own guides **disagree with each other**:

| inD source | Hold time |
|---|---|
| Neptune Systems 0-10 V page (fetched 2026-08-28) | **> 6 s** |
| inD Connect dongle guide (read 2026-09-01) | **≥ 10 s** |
| Coralvue Hydros guide (read 2026-09-01), `Run Time 00:00:15` | **≥ 15 s** |

The current Neptune **Apex** article no longer states a hold time at all, so the help
centre appears to have been reorganised since August.

**Design to the longest published figure.** R1 is therefore set to **≥ 15 s**. The old 10 s
firmware pulse satisfied the 6 s figure but **failed the 15 s one**, so the timing check's
"67 % margin" was margin against only the most permissive of three numbers.
✅ **Fixed in the repo 2026-09-01: 20 s pulse, tail left at 290 s** — a 310 s cycle, which
clears all three hold times *and* closes the separate zero-margin-at-300 s audit item. The
280 s tail first sketched here would have kept the cycle at exactly 300 s; keeping the
290 s was free. **Still needs flashing** — open item 11.

`[MEAS] 2026-09-01` closes the obvious escape route: the OEM dongle **passes the toggle
through** rather than emitting a fixed-width pulse, so inD's "10 seconds" describes the
**port**, not dongle logic.

**Key design insight:** R1 defines a *window*, not a setpoint. 10.37 V is merely what the
OEM dongle happens to produce. This is why a fixed resistor divider is the right answer and
a trimpot is not.

⚠️ `[AUDIT]` **The upper end of that window is an inference, not a spec.** inD's guide
states a 9 V floor and **no maximum voltage**; the "below 12 V" ceiling is this project's
own reading of the 10.37 V OEM measurement. The worst-case output of 10.88 V (§2.1) already
exceeds what the OEM dongle produces by half a volt. Almost certainly fine for a threshold
input — but that ceiling should carry an `[ASSERT]` tag, and until now it read as `[SPEC]`.

### 1.4 ✅ `[VENDOR] 2026-09-01` RESOLVED — and the assumption was backwards

This document previously asked whether the internal 24 h timer keeps running under
external triggering, and **assumed yes**. Both inD's Neptune Apex and Coralvue Hydros
guides state the built-in schedule is **completely overridden when the link port is
connected** — Hydros words it as *connection*, not signalling.

**So once J2's cable is plugged in the aF4 never feeds on its own.** An offline ESP32,
a mid-OTA reboot, or `input_boolean.reef_af4_schedule_enabled` left OFF means the fish
are **silently not fed**.

Every guardrail in this design prevents an *extra* feed. This is the opposite direction.

⚠️ **Corrected 2026-09-05.** This paragraph previously read "has **no detection at all**"
and proposed alerting when `counter.reef_af4_feeds_today` is still 0 past the scheduled
time, citing "open item 12". Both were wrong, and the wrongness is the point: **that alert
already existed** when this was written — `automation.reef_tank_feeder_health_watchdog` has
run a 23:45 counter-vs-elapsed-feed-times backstop and a board-offline branch since
2026-08-27 (§5.7). It was opened as **item 17** — not item 12, which is the headers — and
**withdrawn the same day**. See §7.1.

**What is actually detected:** an offline board (watchdog, 15 min), a missed scheduled feed
(watchdog, 23:45), and a skipped or unacknowledged press (the scheduled-feed automation).
**What is not:** whether food physically came out — §8 item 20, the one real remaining gap.
An over-temperature fault stops the feeder, never self-clears, and is invisible to every
mechanism above.

---

## 2. Circuit

```
 feeder 12 V brick
   │
   └─ barrel Y-splitter ──→ J1 (PJ-079BH, 5.5 × 2.5)
                             │
                             └─ F1 PPTC 0.10 A hold ──→ +12V_F
                                                          │
                                     D1 SS14 (reverse polarity, in series)
                                                          │
                            ┌───────────────┬─────────────┴──→ +12V
                            │               │
                     D2 SMAJ13A        C1 10 µF          U2 LM1117MPX-ADJ
                       (clamp)          ceramic          R4 121 Ω  OUT→ADJ
                            │               │            R5 887 Ω  ADJ→GND
                           GND             GND                    │
                                                                  │
   +10V4 rail ────┬──────────────┬─────────────────────────────────┘
                  │              │
            C2 10 µF        R6 1.0 k
            tantalum         D3 green      U1 AQY212GS PhotoMOS (pins 3/4)
                                                          │
   TIP ───┬───────────────┬──────────────┬────────────────┘
          │               │              │
     R3 100 k        R7 6.8 k        D4 SMBJ13CA      J2 (SJ1-3523N) tip
      bleed           D5 yellow       (bidir)
          │
         GND

 ESP32-POE-ISO ── GPIO32 ─┬─ R1 220 Ω ── U1 LED anode  (pin 1)
                          │
                          └─ R2 10 k ── GND
                             U1 LED cathode (pin 2) ── logic GND
```

The PhotoMOS is the **only** thing crossing between the logic domain and the feeder-power
domain. Separate ground pours, no copper bridging.

> `[AUDIT]` The chain is **series**: J1 → F1 → D1 → then D2, C1 and the LDO all
> *downstream* of the Schottky. An earlier draft of this diagram showed D2 clamping
> `+12V_RAW` upstream of D1, which is not what `pcb/gen_pcb.py` builds. The built topology is
> the better one — D2 never sees a reverse input, and F1 still protects a shorted D2 —
> but the diagram was wrong, and an auditor working from it would have signed off on a
> circuit that was never built. The pad-to-pad figure that used to appear here is
> withdrawn; see §A1.

### 2.1 Regulator — the calculation that matters

`[DS]` TI SNOS412Q, LM1117-ADJ:

| Parameter | Value |
|---|---|
| V_REF (OUT→ADJ) | 1.25 V typ; 1.238–1.262 V @ 25 °C; 1.225–1.27 V over 0–125 °C |
| I_ADJ | 60 µA typ, 120 µA max |
| Minimum load current | 1.7 mA @ 25 °C, **5 mA over full temperature range** |
| Output capacitor | ≥ 10 µF, **ESR 0.3 Ω to 22 Ω**, tantalum named explicitly |
| Dropout @ 800 mA | 1.2 V @ 25 °C, 1.3 V over temp |

`[CALC]` with R4 = 121 Ω (OUT→ADJ), R5 = 887 Ω (ADJ→GND):

```
V_OUT = V_REF × (1 + R5/R4) + I_ADJ × R5
      = 1.25 × (1 + 887/121)   + 60 µA × 887
      = 1.25 × 8.3306          + 0.0532
      = 10.413 + 0.053         = 10.47 V   (nominal)
```

Worst-case stack (V_REF at its 0–125 °C limits, both resistors at ±1 %, I_ADJ 60–120 µA):

```
  low   1.225 × (1 + 7.3306×0.9803) + 0.053  ≈  10.08 V
  high  1.270 × (1 + 7.3306×1.0202) + 0.107  ≈  10.88 V
```

**Both extremes satisfy R1 (≥ 9 V) with wide margin and stay well under 12 V.** The design is
robust precisely because the requirement is a window. ⚠️ Note the upper bound of 10.88 V
brushes the top of the "~9.5–11 V is correct" band stated in `docs/aF4-reference.md`; it is still
inside it, but there is less headroom above than the round number 10.4 V suggests.

### 2.2 Load on the 10.4 V rail

`[CALC]`, using V_OUT = 10.47 V and datasheet LED forward voltages:

| Branch | Expression | Current |
|---|---|---|
| R4 + R5 divider | 10.47 / 1008 Ω | **10.39 mA** |
| D3 green via R6 | (10.47 − 2.2) / 1000 Ω | **8.27 mA** |
| **Quiescent total** | | **18.7 mA** |
| R3 bleed (only while asserted) | 10.47 / 100 kΩ | 0.10 mA |
| D5 yellow via R7 (only while asserted) | (10.47 − 2.0) / 6800 Ω | 1.25 mA |
| **Total during a feed** | | **20.0 mA** |

Consequences:

- **Minimum load is satisfied by the divider alone** (10.39 mA vs the 5 mA requirement).
  D3's branch is a bonus, not load-bearing. Earlier project notes implied D3 carried this;
  it does not, and it must not be relied on. `[AUDIT]` Strictly the current *through R4* is
  V_REF/R4 = 10.33 mA (10.02 mA at worst-case tolerance) rather than V_OUT/1008 — same
  conclusion against the 5 mA floor, slightly different physics, and worth stating because
  this branch **is** the minimum-load guarantee.
- **`[AUDIT]` R5 is the hottest passive on the board.** It drops 9.22 V at 10.39 mA =
  **~96 mW against an 0805's 125 mW rating — 77 %**. Acceptable at enclosure temperatures,
  but it has no margin for a hot day and this document did not previously mention it. A
  0.25 W-rated 0805 is a drop-in if the margin is wanted. Note that **raising the divider
  impedance is not available** — the divider is the minimum-load ballast.
- **F1 margin:** 20 mA against a 0.10 A hold current — 5× margin `[DS]`.
- **U2 dissipation:** with the SS14 dropping ~0.35 V, U2 sees ~11.65 V in, so
  (11.65 − 10.47) × 18.7 mA ≈ **22 mW**. No thermal concern. ⚠️ The 0.35 V Schottky drop
  at ~20 mA is an estimate, not read off the SS14 forward-voltage curve. `[ASSERT]`
- **Headroom — `[AUDIT]` the earlier reasoning here was wrong.** This document previously
  argued "1.2 V dropout is specified at 800 mA, so at 20 mA it is far smaller." That is
  true of a PMOS LDO and **false of the LM1117**, which is a quasi-LDO with an NPN pass
  device: its dropout is a V_BE stack and the dropout-vs-current curve is nearly **flat at
  ~1 V**. Redone honestly, with the SS14 at ~0.3 V:

  | Brick | LDO input | Headroom to 10.47 V | Headroom to worst-case 10.88 V |
  |---|---|---|---|
  | 12.2 V | 11.90 V | 1.43 V ✓ | 1.02 V — at the edge |
  | 12.0 V | 11.70 V | 1.23 V ✓ | 0.82 V — **in dropout** |
  | 11.6 V | 11.30 V | 0.83 V — **in dropout** | 0.42 V — deep in dropout |

  **This is not a safety problem.** In dropout the LM1117 degrades gracefully to
  V_IN − ~1 V ≈ 10.3–10.7 V, still inside the 9–11 V window, so the feeder still triggers.
  What is lost is regulation and ripple rejection, not function. But two consequences
  follow: a board whose divider stacks toward the high end rides dropout on a nominal
  12 V brick; and **commissioning checks 6.2 and 6.3 are mutually inconsistent at their
  edges** — a brick legitimately passing 6.2 at 11.6 V cannot deliver 10.3 V at TP2 even
  with perfect parts. If 6.3 reads low after a low-but-passing 6.2, the divider is
  probably innocent.

### 2.3 PhotoMOS drive

`[DS]` Panasonic AQY212GS:

| Parameter | Value |
|---|---|
| LED forward voltage | 1.32 V typ, 1.5 V max |
| Recommended LED current | 5 mA min, 30 mA max |
| Load rating | 60 V, 1.0 A continuous |
| On-resistance | 0.34 Ω typ, 0.7 Ω max |
| Turn-on / turn-off | 1.3 ms typ (5 ms max) / 0.1 ms typ (0.5 ms max) |
| Isolation | 1500 Vrms |

`[CALC]` with R1 = 220 Ω from GPIO32:

```
  nominal    (3.3 − 1.32) / 220 = 9.0 mA
  worst case (3.0 − 1.5)  / 220 = 6.8 mA
```

Both inside the recommended 5–30 mA band, with 36 % margin at worst case. ESP32 GPIO source
current of 9 mA is well within its ~20 mA recommended / 40 mA absolute limit.

Switching time (1.3 ms typ) is irrelevant against a 20 s pulse.

### 2.4 The GPIO13 problem — why the trigger is on GPIO32

`[CAD]` The Olimex board has **R35, a factory 2.2 kΩ pull-up to +3.3 V on GPIO13** (the I²C
SDA pull-up), confirmed in the Rev N KiCad source. Not optional, not removable without rework.

During reset and early boot GPIO13 is high-impedance. `[CALC]` solving the node — 3.3 V through
2.2 kΩ, into R2 (10 kΩ to GND) in parallel with the R1 + LED branch:

```
  node settles ≈ 1.4 V
    in  via pull-up   (3.3 − 1.4)/2200  = 0.86 mA
    out via R2         1.4/10000        = 0.14 mA
    out via R1 + LED  (1.4 − ~1.25)/220 ≈ 0.68 mA   ← into the PhotoMOS LED
```

0.68 mA against an AQY212 operate current of ~1.1 mA typical is **62 % of the way to a
spurious feed**, before any firmware runs. `restore_mode: ALWAYS_OFF` cannot help — the pin
is high-Z before firmware exists. The failure mode is "10.4 V on the trigger port for more
than 6 seconds = an unscheduled feed into a reef tank."

> **`[AUDIT]` RESOLVED — and the truth is worse than the paragraph above.** Panasonic's
> published spec `[DS]`:
>
> | Parameter | Value |
> |---|---|
> | LED operate current | **1.1 mA typ, 3 mA max** |
> | LED **turn-off** current | **0.3 mA min**, 1.0 mA typ |
> | Recommended LED operating range | 5–30 mA |
>
> The ~1.1 mA figure was right. But the number that actually governs is the one this
> document never cited: **the guaranteed-off threshold is 0.3 mA**, and there is no
> minimum operate current — below 1.1 mA the datasheet simply stops promising the relay
> stays open. Re-solving the boot node with a realistic sub-milliamp LED V_F of
> 1.0–1.25 V gives **0.72–0.85 mA**, higher than the 0.68 mA above and **more than 2× the
> guaranteed-off current**.
>
> "62 % of the way to a spurious feed" understated it. On GPIO13, nothing guaranteed the
> feed *wouldn't* happen. Moving to GPIO32 was not cheap insurance — it was mandatory.

`[CAD]` **GPIO32** touches only the ESP32 module and EXT2 pin 6 — no pull-up, no strapping
function, not shared with UEXT. GPIO33 is nearly as clean (one unpopulated resistor).

### 2.5 Protection

| Ref | Part | Function | Notes |
|---|---|---|---|
| D1 | SS14 Schottky 40 V / 1 A | Reverse polarity, in series with +12 V | New in rev D; rev C had **none**. Costs ~0.35 V of headroom |
| D2 | SMAJ13A, 400 W unidirectional | Input transient clamp | 13 V standoff, 21.5 V clamping `[DIST]` |
| D4 | SMBJ13CA, 600 W bidirectional | Clamp across the trigger pair at J2 | 13 V standoff, breakdown 14.4–15.9 V `[DIST]`. No orientation |
| F1 | 1206L010/60WR PPTC | Overcurrent on the 12 V tap | 0.10 A hold / **0.25 A trip** / 60 Vdc, −40…+85 °C `[DS]` |
| R3 | 100 kΩ bleed | Guarantees the 0 V re-arm (R2 above) | 0.10 mA |

✅ **CLOSED `[MEAS] 2026-09-01`.** Both TVS parts have a 13 V standoff on a nominally
12 V rail. The brick measures **12.13 V open-circuit, stable** — comfortably below the
standoff, so D2 never conducts at idle and no part change is needed.

Loaded, the rail sits at **11.84–11.86 V** and dips to **11.77 V** during a feed, so the
standoff is even further away in service. Separately, the port itself tolerates the OEM
dongle's **16.40 V** turn-on overshoot on every feed, which makes the worst-case 10.88 V
output look tame.

**Deliberately absent:** a series resistor on the trigger tip. At 10.4 V into a short it
would sit right at the polyfuse hold current and cook rather than trip. The LDO's internal
current limit plus F1 handle a shorted tip properly. `[CALC]`

### 2.6 Indicator LEDs

`[DS]` Both are Kingbright 0805, both **water clear**:

| Ref | Part | Intensity @ 20 mA | V_F | λ | Angle |
|---|---|---|---|---|---|
| D3 green | APT2012SGC | 12 mcd typ, **5 mcd min** | 2.2 V typ, 2.5 max | 565 nm | 160° ⚠️ |
| D5 yellow | APT2012SYCK | 150 mcd typ, 80 mcd min | 2.0 V typ, 2.5 max | 590 nm | 140° ⚠️ |

⚠️ `[AUDIT]` **Unresolved conflict on viewing angle.** The figures above are read off the
Kingbright datasheet PDFs; the audit found 120° for both from two distributor-datasheet
sources. Neither resistor value depends on it — it changes only how wide the cone through
the lid sight holes is. Settle it against the current Kingbright drawing if it matters.

The two parts differ **~12× in efficiency**. `[CALC]` scaling intensity linearly with current:

| | Current | Intensity (typ) | Intensity (worst case) |
|---|---|---|---|
| D3 via R6 = 1.0 kΩ | 8.27 mA | ~5.0 mcd | ~2.1 mcd |
| D5 via R7 = 6.8 kΩ | 1.25 mA | ~9.3 mcd | ~5.0 mcd |

Reasonably matched to the eye. ⚠️ Linear intensity-vs-current scaling is an approximation
`[ASSERT]`; real LEDs are sub-linear at high current and roughly linear at low, so these
figures are fair-to-slightly-optimistic at the low end.

Both are viewed through **Ø3.5 mm sight holes in the lid**, which is why absolute brightness
matters here at all.

> **This was a defect, caught 2026-08-28.** R6 and R7 originally shared a single 10 kΩ value,
> giving 0.82 mA and putting D3 at ~0.5 mcd — effectively invisible. Root cause: 10 kΩ was
> chosen as a jellybean value without checking it against the LEDs' actual intensity specs.

---

## 3. Bill of materials — with verification status

Board BOM: **20 lines, 21 placements** (17 SMD + 4 THT / 28 joints). Every manufacturer part
number below was confirmed against a live distributor listing on 2026-08-28, and independently
re-confirmed by the audit the same day.

| # | Ref | MPN | Description | Status |
|---|---|---|---|---|
| 1 | U1 | Panasonic **AQY212GS** | PhotoMOS SSR, SOP-4, 60 V / 1 A, 1500 Vrms | `[DIST]` ✓ |
| 2 | U2 | TI **LM1117MPX-ADJ/NOPB** | LDO, SOT-223, adjustable, 800 mA | `[DIST]` ✓ |
| 3 | D1 | Vishay **SS14-E3/61T** | Schottky 40 V / 1 A, SMA | `[DIST]` ✓ |
| 4 | D2 | Littelfuse **SMAJ13A** | TVS 400 W unidirectional, SMA | `[DIST]` ✓ |
| 5 | D4 | Littelfuse **SMBJ13CA** | TVS 600 W bidirectional, SMB | `[DIST]` ✓ |
| 6 | D3 | Kingbright **APT2012SGC** | LED green 565 nm, 0805 | `[DIST]` ✓ |
| 7 | D5 | Kingbright **APT2012SYCK** | LED yellow 590 nm, 0805 | `[DIST]` ✓ **corrected** |
| 8 | F1 | Littelfuse **1206L010/60WR** | PPTC 0.10 A / 0.25 A / 60 V, 1206 | `[DIST]` ✓ **corrected** |
| 9 | C1 | Murata **GRM31CR61H106KA12L** | 10 µF 50 V **X5R** 1206 | ⚠️ `[AUDIT]` **EOL at Murata (2020)**, but DigiKey ships today and distributor float is ~1.6 M. Fine for 5 boards; expect PCBWay to flag it. Line up a current-production substitute from a **live parametric search**, never from memory |
| 10 | C2 | Kemet **T491B106K025AT** | 10 µF 25 V tantalum, EIA-3528 B, ESR ~2 Ω | `[DIST]` ✓ |
| 11 | R1 | Yageo **RC0805FR-07220RL** | 220 Ω 1 % | `[DIST]` ✓ |
| 12 | R2 | Yageo **RC0805FR-0710KL** | 10 kΩ 1 % | `[DIST]` ✓ |
| 13 | R3 | Yageo **RC0805FR-07100KL** | 100 kΩ 1 % | `[DIST]` ✓ |
| 14 | R4 | Yageo **RC0805FR-07121RL** | 121 Ω 1 % | `[DIST]` ✓ |
| 15 | R5 | Yageo **RC0805FR-07887RL** | 887 Ω 1 % | `[DIST]` ✓ |
| 16 | R6 | Yageo **RC0805FR-071KL** | 1.0 kΩ 1 % | `[DIST]` ✓ **new** |
| 17 | R7 | Yageo **RC0805FR-076K8L** | 6.8 kΩ 1 % | `[DIST]` ✓ **new** |
| 18 | J1 | Same Sky **PJ-079BH** | DC jack 5.5 × 2.5, 2.5 mm centre pin, 24 V / 5 A | `[DIST]` ✓ |
| 19 | J2 | Same Sky **SJ1-3523N** | 3.5 mm jack, 3-conductor, right angle | `[DIST]` ✓ |
| 20 | J3, J4 | Sullins **PPTC101LFBN-RC** ×2 | 1×10 socket, 2.54 mm | `[DIST]` ✓ |

### 3.1 Sourcing traps recorded

- **J1:** `PJ-002AH` / `PJ-102AH` look identical but are 2.0–2.1 mm centre pin. Only the
  **"B" suffix** parts are 2.5 mm. The same trap applies to the 12 V splitter cable.
- **C2 must stay tantalum.** The LM1117 requires output-cap ESR between 0.3 Ω and 22 Ω `[DS]`.
  A low-ESR ceramic substitution risks loop instability.
- **C1 is X5R, not X7R.** Murata makes no 10 µF 50 V X7R in 1206; that C/V needs a 1210.

### 3.2 Bought separately (not on the board)

Olimex ESP32-POE-ISO (~$28–35) · 2× 1×10 male headers for EXT1/EXT2 (ship unpopulated) ·
12 V barrel Y-splitter 5.5 × 2.5 centre-positive · 3.5 mm male–male patch cable ·
PETG for the enclosure · M2 / M3 self-tapping screws.

---

## 4. Board

| Property | Value |
|---|---|
| Size | 57.00 × 50.00 mm, rectangular |
| Layers / thickness / copper | 2 / 1.6 mm / 1 oz |
| Finish | ENIG preferred, HASL acceptable |
| Min track / space | 0.35 mm / 0.20 mm |
| Min drill | 0.45 mm (stitching vias) |
| Plated slots | **0.70 mm minimum**, deliberately widened |
| Placements | 17 SMD (top only) + 4 THT parts / **28** joints `[AUDIT]` |
| Mounting | 2 × M3 at (123.0, 118.0) and (123.5, 147.0), board frame |

`pcb/gen_pcb.py` is the source of truth — it generates the `.kicad_pcb` deterministically from
named coordinates taken from the Olimex Rev N source `[CAD]`, so socket alignment is exact by
construction. **Edit the script, not the board file.**

### 4.1 Geometry from vendor CAD `[CAD]`

| Feature | Position (Olimex board frame) |
|---|---|
| ESP32-POE-ISO outline | x 90.15–118.15, y 90.00–188.15 (28.00 × 98.15 mm) |
| EXT1 pin 1 | (91.44, 123.22), 2.54 mm pitch |
| EXT2 pin 1 | (116.84, 123.22), 2.54 mm pitch |
| GND | EXT1 pin 3 → (91.44, 128.30) |
| GPIO32 | EXT2 pin 6 → (116.84, 135.92) |

### 4.2 Verification status of the board

✅ **Independently re-run 2026-08-31** (`archive/reviews/aF4-prefab-review-2026-08-31.md`), on KiCad
7.0.11 with the zones filled from scratch — the counts below are confirmed, not reported.
DRC via `pcbnew.WriteDRCReport` (KiCad 7): clearance 0, courtyard
overlaps 0, hole clearance 0, hole-to-hole 0, copper-to-edge 0, unconnected 0, mask bridges 0.
That review also swept clearance at multiple rules on the filled board: **zero violations at
0.2032 mm (8 mil) and at 0.24 mm; first hits at 0.25 mm**, so the real minimum copper gap is
0.24–0.25 mm and the 0.20 mm carried in these docs is the KiCad netclass default, not the
geometry. The shipped Gerbers were re-exported and diffed against the board — identical.
Remaining flags are silkscreen cosmetics and "library footprint differs", both expected for
programmatically placed footprints.

**A defect DRC does not catch, found by inspecting the drill file:** KiCad's SJ1-3523N
footprint specifies 0.40 mm plated slots and PJ-079BH 0.60 mm — both below fab routing
minimum (~0.5 mm drilled / 1.0 mm milled). `pcb/gen_pcb.py` now enforces `MIN_SLOT = 0.70 mm` and
prints what it widened. Worst-case annular ring after widening is 0.25 mm.

> **Generalised lesson:** DRC checks what it was told to check. Slot widths, and any
> hand-written count in a generated document, are outside it. Inspect the drill tool list
> before any package leaves the building.

### 4.3 Isolation

Two separate ground pours with **no copper crossing**. The only connection is U1 itself,
straddling the boundary; its pad-to-pad gap is **4.80 mm**. The band is marked on both
silkscreens, and the two mounting holes sit inside it — both **NPTH, no copper**.

`[AUDIT]` The **true minimum logic-to-power creepage is 4.425 mm**, and it is not set by U1:
**R1 pad 2** reaches x 121.925, 0.275 mm inside the nominal band, against the GNDP pour edge
at 126.350. Measured off the regenerated board. The earlier "4.3 mm" figure was an artefact
of the wrong U1 footprint and is withdrawn (§A1).

⚠️ **Assembler instruction that must survive:** no copper, vias or stitching in that band.

---

## 5. Firmware

`firmware/af4-feeder.yaml` in the repo is the source of truth. The ESPHome Device Builder (Docker on
the Unraid server, port 6052) holds its own copy — changes must be pasted there manually,
then Install → Wirelessly.

### 5.1 The safety architecture

All feeder timing rules are enforced **on-device**. Home Assistant is scheduler only — it
presses one button and can do nothing else.

| Mechanism | Purpose |
|---|---|
| `switch.feed_ssr` is `internal: true` | HA cannot reach the raw GPIO line at all |
| `restore_mode: ALWAYS_OFF` | software half of the boot-safety pair |
| R2 10 kΩ pulldown on GPIO32 | hardware half — **unopposed** on GPIO32, which is the point |
| `script.do_feed` with `mode: single` | re-entrant presses are **dropped**, not queued |
| `button.af4_feed` template button | the sole exposed control |
| `binary_sensor.af4_lockout` | exposes lockout state for dashboards and automation conditions |
| `globals.feed_in_flight`, `restore_value: yes` | **flash-persisted**, so a reboot inside a cycle is detected on boot |
| `script.boot_recovery` off `on_boot` | serves a 300 s lockout when that flag comes back true |
| `web_server: auth:` | the local control page is no longer an anonymous second control path |

### 5.2 Timing check against the spec `[CALC]`

```
  20 s pulse    ≥ 15 s threshold hold      ✓  (33 % margin)   <-- live on the device
 290 s off tail ≥ 60 s re-arm              ✓  (383 % margin)
 20 + 290 = 310 s total cycle ≥ 5 min      ✓  (10 s of margin, was exactly 0)
```

✅ **RESOLVED AND FLASHED 2026-09-01.** Two separate problems were
closed in one edit. The old block read `≥ 6 s` and claimed a 67 % margin; against inD's
actual figures the 10 s pulse had none, so the pulse went to **20 s**. And the audit's
zero-margin complaint — R3 requires feeds ≥ 5 min apart and the cycle was exactly 300 s —
was closed by keeping the **290 s tail** rather than trimming it to 280 s, which buys the
310 s cycle for free.

Everything in this section describes the firmware **as actually running**: the device
reports its build as 2026-09-01 18:54:20, and the last YAML commit that evening was
18:51:33. It was installed three minutes after it was written. A second install on
2026-09-02 18:15:49 carried the rotated credentials and nothing else.

### 5.3 ✅ `[AUDIT]` The lockout did not survive a reboot — CLOSED 2026-09-01

`script.do_feed`'s state lives in RAM. Any reboot inside the 300 s cycle — OTA update,
crash, brownout, power blip — clears the lockout silently. The switch comes back
`ALWAYS_OFF`, so the pin is safe, but `binary_sensor.af4_lockout` reads `off` and the
device accepts a new press immediately.

A sequence that ends with two feeds ~2 minutes apart into the tank: scheduled feed fires →
OTA or crash at t+60 s → HA retry, second schedule slot, or a manual press → second feed.
Low probability, but it is exactly the class of unattended edge this document exists to
catch.

**Fix, implemented:** a `restore_value: yes` global, `feed_in_flight`, is set when the
pulse starts and cleared when the lockout ends. It lives in flash, so a reboot mid-cycle is
detected in `on_boot`, which runs `script.boot_recovery` — a 300 s lockout-only script. The
Feed button checks `boot_recovery.is_running()` and ignores presses while it is, and
`binary_sensor.af4_lockout` ORs both scripts so the state is visible. A clean boot leaves
the flag false and costs nothing.

⚠️ One practical wrinkle, verified 2026-09-01: the `on_boot` log line fires while ethernet
is still coming up, so **no log client ever sees it** and ESPHome does not replay it. Read
the *state* instead — Feed Lockout on at a low uptime with nobody having pressed Feed is
the recovery lockout. `docs/aF4-assembly-guide.md` §6 says so at the point of use.

### 5.4 ✅ `[AUDIT]` The web server was a second, unauthenticated control path — CLOSED 2026-09-01

`web_server: port: 80` exposes the Feed button to anything on the LAN, with no `auth:`
block. The safety story above — "HA is scheduler only, it presses one button and can do
nothing else" — is true of Home Assistant and **false of the network**. On a home LAN this
was a judgment call rather than a defect, but the document should have said so.

`web_server:` now carries an `auth:` block. Commissioning step 6.5 uses this page, so the
assembly guide records the credential at the point of use; Home Assistant is unaffected
because it talks over the API, not this page.

### 5.5 ✅ The related hygiene problem — the worse one — CLOSED 2026-09-02

The API encryption key, the OTA password **and the new web_server password** were all
committed in plaintext to a **public** GitHub repository. Adding web auth and publishing
its password in the same commit closed nothing; it moved the hole from the LAN to the
internet.

All three now resolve through `!secret` against a gitignored `firmware/secrets.yaml`, **and all
three were rotated** — which is the part that actually remediates it, because git history
keeps the old values whatever the working tree says. History was deliberately *not*
rewritten: rotation makes the exposed values worthless, and a filter-repo pass would
rewrite all 46 commit SHAs while GitHub can still serve cached objects. Decided 2026-09-02.

Two operational consequences, both recorded at the point of use in
`docs/aF4-assembly-guide.md` §4: the ESPHome Device Builder needs **its own copy** of
`firmware/secrets.yaml`, and the first install after the rotation authenticates with the **old**
OTA password while installing the new one.

### 5.6 `[AUDIT]` Held-high failure modes are bounded — the design's best safety property

Checked deliberately, since "unscheduled feed" is the nightmare. If the ESP32 crashes with
the SSR on, or the PhotoMOS fails shorted, the port sees a **continuously held** 10.4 V.
Per R2, re-arming requires ~0 V for more than 60 s — so a held-high line produces **at most
one feed and then never re-arms**.

Every stuck-at fault therefore costs one feed, not a feeding loop. This is the single best
safety property the design has, and it emerges from the feeder's own spec rather than from
anything on the board.

### 5.7 Home Assistant integration

Entities: `button.af4_feeder_feed` (sole control), `binary_sensor.af4_feeder_feed_lockout`,
`binary_sensor.af4_feeder_status`, `sensor.af4_feeder_ip_address`, `sensor.af4_feeder_uptime`,
`button.af4_feeder_restart`.

Helpers: `input_boolean.reef_af4_schedule_enabled` (master kill switch),
`input_datetime.reef_af4_feed_time_1` / `_2`, `counter.reef_af4_feeds_today`,
`sensor.reef_af4_next_feed`.

Automations: `automation.reef_tank_af4_scheduled_feed` (scheduler + per-feed confirmation),
`automation.reef_tank_feeder_health_watchdog` (backstop, shared with the Plank feeder),
`automation.reef_tank_reset_ato_counter_daily` (nightly counter reset).

#### `automation.reef_tank_af4_scheduled_feed` — read from HA 2026-09-02

Materially more than "presses a button", which is all this document used to say. Triggers
on the two `input_datetime` helpers so times stay dashboard-editable, gated by the master
kill switch, then:

1. **Two interlocks before pressing.** `binary_sensor.af4_feeder_feed_lockout` must be
   `off`, and `binary_sensor.reef_tank_sump_return_pump_..._running` must be `on`. The
   second is the one this document never knew about: the feeder discharges into the sump,
   so with no return pump the food never reaches the display. It reads `off` while the
   system is unplumbed and self-clears when the return comes up.
2. **Press, then wait up to 15 s for the lockout to go `on`.** On-device the lockout is
   `do_feed.is_running() || boot_recovery.is_running()`, and the press only happens while
   it is `off` — so **the lockout turning on is proof the pulse started**. That is as close
   to feed confirmation as an input-only port allows.
3. **The counter increments only on a confirmed pulse.** An unacknowledged press notifies
   and is deliberately *not* counted, so a press lost in transit cannot log a phantom feed
   and blind the watchdog below. This is load-bearing and must survive any rewrite.
4. **Both failure paths notify**, naming which interlock failed.

#### `automation.reef_tank_feeder_health_watchdog` — read from HA 2026-09-02

The backstop for silent failure, in three branches:

- **23:45 daily check.** Compares each feeder's counter against how many of its feed times
  have actually elapsed today, computed from the `input_datetime` helpers rather than
  hardcoded — so moving a feed time cannot false-alarm. 23:45 is late enough that any
  plausible feed time has passed and early enough to beat the midnight counter reset.
- **aF4 board offline 15+ minutes** while the schedule is enabled. Gated on the toggle, so
  bench and case work with the schedule off stays quiet.
- **Plank plug Z-Wave node dead** 15+ minutes.

Three deliberate choices worth preserving:

1. **Feed counting lives in HA, not on-device** — it survives ESP32 reboots and reuses the
   existing nightly reset automation.
2. **The lockout condition does double duty.** `off` means the device is reachable *and*
   outside its lockout, so an offline ESP32 skips the feed rather than firing a button
   press into the void. Offline reads `unavailable`, which fails the check correctly.
3. **The counter counts confirmed pulses, not presses.** See point 3 above.

Networking: IP 192.168.1.55 reserved in OPNsense dnsmasq against Ethernet MAC
`20:E7:C8:74:A6:D7` (host override `af4-feeder`, MAC match only, no client identifier). The
board pulled a new DHCP lease after flashing, which broke HA's cached discovery with
`Errno 113`; the reservation is the fix.

**No feedback channel exists, and this is now the only unmonitored failure direction.**
The 0-10 V port is input-only, so everything above confirms that *the pulse was sent* and
nothing confirms *that food came out*. The gap that matters is an over-temperature fault:
per inD's own documentation it stops the feeder and **never self-clears**, and it is
invisible to us — the ESP32 would pulse happily, the lockout would assert, the counter
would increment, and the 23:45 watchdog would stay silent while the tank went unfed.

A power-monitoring smart plug on the 12 V supply is the only way to close it without
opening the unit: feed-motor current is the sole dispense evidence available. Open item 20.

---

## 6. Enclosure

**External 65.2 × 117.0 × 38.4 mm**, PETG, printed with no supports.
`hardware/enclosure/af4_enclosure_ocp.py` is the parametric source and runs 13 dimensional checks plus 3
solid-interference tests (case vs hat, case vs ESP32, lid vs hat) before exporting — all pass
with zero intersection volume `[ASSERT]`, as reported by the script; not re-run in this pass.

### 6.1 The vertical stack — the governing dimension

```
  z = -11.90   case floor, outside
  z =  -9.50   case floor, inside
  z =   0.00   top of the three ESP32 standoffs
  z =   1.58   ESP32 top face
  z =   4.12   top of the male header plastic on EXT1/EXT2
  z =   5.98   top of the UEXT box header   ← tallest thing under the hat
  z =   9.22   lowest hat through-hole pin  → 3.24 mm clear
  z =  12.62   hat underside
  z =  14.22   hat top face
  z =  16.72   3.5 mm jack axis
  z =  17.82   barrel jack axis
  z =  21.42   barrel jack crown            → 2.08 mm clear of the lid
  z =  23.50   lid underside
```

**The 1×10 socket's body height sets everything.** Substitute a different socket → change
`HAT_Z` and re-run; the script reports what now collides.

### 6.2 Two details that are easy to lose

- The barrel-jack hole needs its **Ø13 × 1.8 mm counterbore on the outside**, thinning the
  wall to 1.2 mm locally. Without it, 3 mm of wall eats most of the jack's 9.5 mm insertion
  depth. As built the plug engages 6.9 mm.
- The **four Ø3.5 mm LED sight holes** in the lid, each fitted with a 3 mm clear acrylic
  **light pipe**, sit over D3 and D5 on the hat and PWR1 and LNK1 on the Olimex board. This
  is the entire reason LED brightness is a real requirement rather than a cosmetic
  preference (§2.6). The pipes exist because the Olimex LEDs are 21.2 mm below the lid — a
  plain hole gives them a 4.7° viewing half-angle, visible only dead-on. ACT1 and CHRG1
  deliberately have no hole: ACT1 sits 0.361 mm inside the hat footprint and is blindfolded
  by opaque FR4. Full spec in `docs/aF4-enclosure-notes.md`; cutting and fitting in
  `docs/aF4-assembly-guide.md` §1.

Hat mounting holes at (123.0, −118.0) and (123.5, −147.0) are **forced by geometry** — the
only X clearing the ESP32's right edge below (118.15) and the parts column above (from
126.45). Not free choices.

---

## 7. Errors already found and fixed

Listed so an auditor does not spend effort re-discovering them, and because the pattern is
more useful than the individual items.

| Date | Error | Root cause |
|---|---|---|
| 2026-08-28 | **F1 `1206L010/60YR` did not exist** → `/60WR`. Trip current also wrong (0.30 → 0.25 A) | MPN generated from the naming convention (the 1206L suffix is a reel-quantity code) instead of looked up |
| 2026-08-28 | **C1 `GRM31CR71H106KA12L` did not exist** → `GRM31CR61H106KA12L`. X7R → X5R | Same. Murata makes no 10 µF 50 V X7R in 1206 |
| 2026-08-28 | **D5 `APT2012SYC` did not exist** → `APT2012SYCK` | Same |
| 2026-08-28 | **D3 under-driven ~10×** — R6/R7 shared 10 kΩ, putting the green at ~0.5 mcd | Resistor value chosen as a jellybean without checking it against the LEDs' intensity specs |
| 2026-08-28 | Docs claimed **"20 SMD placements"**; actual is 17 | A hard-coded count in a generated document, fixed in the script earlier but left standing in the prose |
| 2026-08-28 | Load and dissipation figures (~15 mA, 17 mW) predated the D3 branch | Derived numbers not revisited after a change to their inputs |
| 2026-08-28 | Claimed a lens mismatch between D3 and D5 | Asserted from naming convention; both are in fact water clear |
| 2026-08-28 `[AUDIT]` | **U1 on a 1.27 mm-pitch footprint; the AQY212GS is 2.54 mm** — board unbuildable | A KiCad footprint picked by name. Its description points at an OPTEK OPIA403 |
| 2026-08-28 `[AUDIT]` | `pcb/gen_pcb.py` said `SMAJ15A` for D2 while everything else said `SMAJ13A` | A value edited in one place and never propagated |
| 2026-08-28 `[AUDIT]` | **"44 joints" was fiction; the real count is 28** — and PCBWay prices hand-soldered joints | A hard-coded count in a generated document, with the correct itemisation printed directly beneath it |
| 2026-08-28 `[AUDIT]` | Circuit diagram showed D2 upstream of D1; the board wires it downstream | Diagram drawn from intent, not from the netlist |
| 2026-08-28 `[AUDIT]` | "Dropout is far smaller at 20 mA" — false for a quasi-LDO | A PMOS-LDO intuition applied to an NPN pass device |
| earlier | KiCad footprints specified 0.40 / 0.60 mm plated slots, below fab minimum | DRC does not check slot widths |
| earlier | Rev B: three buck modules failed in sequence | A trimpot existed only to hit a precision target the port does not require |

**The dominant failure mode in this project is a plausible value asserted rather than
checked** — a part number that parses correctly under its manufacturer's scheme, a resistor
value that looks like a jellybean, a count copied from an earlier revision, **a footprint
chosen because its name contained the right characters**. Every one was well-formed and
wrong.

`[AUDIT]` The first version of this document was written to expose exactly that pattern and
still shipped four fresh instances of it, including a build blocker. The lesson is not
"tag your claims" — it is that **naming a thing is not verifying it**, and the tags are only
worth what the checking behind them was worth. Where this document now says `[DS]`, a
datasheet was actually opened.

### 7.1 The inverse failure mode, named 2026-09-02

Once the design stopped moving, the dominant error flipped direction. **The docs now lag
execution rather than overstating it**, and a review that reads only the repo will invent
work that is already done. Three instances surfaced in a single day:

| What the repo said | What was true |
|---|---|
| "Missed-feed alert in HA" was the last unattended-safety gap (item 17) | `automation.reef_tank_feeder_health_watchdog` had been running it since 2026-08-27 |
| `automation.reef_tank_af4_scheduled_feed` "presses the button at each feed time" | It also holds a return-pump interlock, a 15 s pulse confirmation, and a confirmation-gated counter — all load-bearing |
| Firmware "has never been flashed", device "still on GPIO13" (item 11) | Flashed 2026-09-01 18:54, three minutes after the commit that wrote it |

All three were caught by reading the live system — Home Assistant's config and the device's
own reported build timestamp — rather than the documents describing it. **Check reality
before opening an item, and record work at the moment it is done, not at the moment someone
next reads the file.** The provenance tags do not help here: an `[ASSERT]` that has quietly
become true looks identical to one that has not.

---

## 8. Open items

> 🚫 **This table is not current state.** It is the **numbering registry** — item 12 means
> the headers, item 16 means the OTA password, permanently — plus the dated record of what
> closed each item and why. **For what is actually still open, read `STATUS.md`.**
> When an item closes, record *how* it closed here; change the open/closed picture in
> `STATUS.md`. Never renumber a row.

Revised after the 2026-08-28 audit, the 2026-08-31 pre-fabrication review, the 2026-09-01
bench and vendor-documentation passes, the 2026-09-02 order going to fabrication, and the
2026-09-02 read of the live Home Assistant config.

⚠️ Item 17 is a caution about this table itself: it was opened by the 2026-09-02 review and
closed the same day on discovering the work had existed in Home Assistant since 08-27 and
had simply never been written back here. **A ledger built by reading the repo will invent
open items as readily as it misses closed ones.** Check reality before adding a row.

| # | Item | Blocking? |
|---|---|---|
| 1 | ~~U1 footprint~~ — **CLOSED 2026-08-28.** Rebuilt from Panasonic's recommended mounting pad, regenerated and re-verified (§A1); independently re-checked 2026-08-31 | — |
| 2 | ~~Tell PCBWay to hold~~ — **CLOSED.** The rev D quotation was deleted at the vendor; rev E went in as a fresh inquiry 2026-08-31 with the corrected files and the 28-joint count | — |
| 3 | ~~`on_boot` lockout~~ — **CLOSED 2026-09-01.** Flash-persisted `feed_in_flight` + `script.boot_recovery`, 300 s (§5) | — |
| 4 | ~~Verify AQY212 operate current~~ — **CLOSED.** 1.1 mA typ / 3 mA max, turn-off 0.3 mA min. The GPIO32 move was mandatory, not optional | — |
| 5 | ~~Measure the 12 V supply's open-circuit voltage~~ — **CLOSED `[MEAS] 2026-09-01`: 12.13 V**, stable, comfortably under the 13 V standoff. Loaded it sits at 11.84–11.86 V and dips to 11.77 V | — |
| 6 | ~~Widen the 300 s feed cycle~~ — **CLOSED 2026-09-01.** 20 s + 290 s = 310 s; the tail was kept rather than trimmed, which buys the margin for free | — |
| 7 | ~~Widen commissioning check 6.3~~ — **CLOSED 2026-09-01.** 6.3 is now 10.0–10.9 V and 6.2 is 11.4–12.0 V; A2 made this mandatory, not optional | — |
| 8 | ~~Measure the trigger port's input current~~ — **CLOSED `[MEAS] 2026-09-01`: ~11 kΩ, about 0.95 mA at 10.4 V.** Negligible against the 18.7 mA budget; the load-budget assumption was right | — |
| 9 | ~~`web_server: auth:`~~ — **CLOSED 2026-09-01**, and it created item 16 | — |
| 10 | ~~C1 substitute~~ — **CLOSED 2026-08-31.** LCSC holds ~123 k of `GRM31CR61H106KA12L`; pre-approved alternate `C3216X5R1H106K160AB` (TDK) is in the order notes. PCBWay quoted the correct MPN 2026-09-02 and did not substitute | — |
| 11 | ~~`firmware/af4-feeder.yaml` needs pasting into the ESPHome Device Builder + OTA~~ — **CLOSED 2026-09-01**, and this row was stale for a day before anyone noticed. The device reports its firmware as built 18:54:20 that evening, three minutes after the commit that wrote it. GPIO32, the 20 s pulse, the boot lockout and web auth have been live since | — |
| 12 | Solder two 1×10 male headers into EXT1/EXT2, pins up | **YES** — blocks assembly |
| 13 | ~~Confirm the internal 24 h timer under external triggering~~ — **CLOSED `[VENDOR]`: the built-in schedule is completely overridden while the link port is connected.** The old assumption was backwards; this is what item 17 exists to cover | — |
| 14 | Resolve the LED viewing-angle conflict, 120° vs 160°/140° (§2.6) | No — cosmetic |
| 15 | Commissioning steps 6.1–6.8 must all pass before the schedule toggle is enabled | **YES** — gates go-live |
| 16 | **Secrets: two of three fully remediated 2026-09-02.** All three moved out of the repo to a gitignored `firmware/secrets.yaml` via `!secret`, and history deliberately not rewritten because rotation is what remediates. **API key and web_server password are rotated and verified live** on the device. ⚠️ **The OTA password on the device is still the value published in git history** — ESPHome uses one value for both compiling and authenticating the upload, so it cannot rotate over OTA (see `docs/aF4-assembly-guide.md` §4). It rotates at the next **serial** flash, which item 12 puts the board on the bench for anyway | No — but it is a live exposure until the serial flash |
| 17 | ~~Missed-feed alert in HA~~ — **ALREADY CLOSED, and this item should never have been opened.** `automation.reef_tank_feeder_health_watchdog` has done it since 2026-08-27: a 23:45 counter-vs-elapsed-feed-times backstop, plus a board-offline branch. The scheduled-feed automation independently notifies on skip and on unacknowledged press. Read from HA 2026-09-02; the work existed and was simply never written back to this repo | — |
| 18 | **R5 runs at 77 % of an 0805's 125 mW rating.** A 0.25 W part is a drop-in; raising the divider impedance is NOT available, it is the minimum-load ballast. **Window has now closed for this run** — boards are in fabrication | No — note for a future rev |
| 19 | Silkscreen on the fabbed rev E boards reads **"10.4V 10s pulse"**. Corrected in `pcb/gen_pcb.py` for any future rev; the five boards in fabrication will carry the old string | No — cosmetic, and unfixable now |
| 20 | **No dispense confirmation.** Everything in §5 confirms the pulse was *sent*; nothing confirms food came out. An over-temperature fault would be invisible and never self-clears. A power-monitoring smart plug on the 12 V supply is the only fix short of opening the unit | No — the last unmonitored failure direction |
| 21 | Read the recalculated ship date off the PCBWay order page. Added to the registry 2026-09-05; it had been carried only in the handoff, which numbered it 20 — a number already spent on dispense confirmation | No — cosmetic |
| 22 | `pcb/gen_pcb.py` stray "exclude from BOM/pos" flags on J2. Added to the registry 2026-09-05; the handoff numbered it 9, a number already spent on the closed `web_server: auth:` item | No |

### 8.1 Commissioning gate (from `docs/aF4-assembly-guide.md` §6)

All voltages referenced to **TP4 (power ground)**, not the ESP32's ground.

| # | Check | Expect |
|---|---|---|
| 6.1 | Splitter tap into J1 | D3 green lit |
| 6.2 | TP1 (12 V) → TP4 | **11.4–12.0 V** (12 V less the Schottky drop) |
| 6.3 | TP2 (10.4 V) → TP4 | **10.0–10.9 V** — the check that matters |
| 6.4 | TP3 (tip) → TP4 at rest | 0 V, D5 dark |
| 6.5 | Press Feed on the ESPHome web page (login `af4`) | D5 lights, TP3 ≈ 10.4 V for **20 s**, returns to 0 V |
| 6.6 | Feed Lockout binary sensor | On with the pulse, clears **310 s** later |
| 6.7 | Plug the patch cable into J2 | aF4's **link LED goes solid** — the port sees the connection |
| 6.8 | Press Feed again | aF4's **link LED flashes green** — the pulse was accepted (newer units; SN 130063 qualifies) |

If 6.3 reads ~1.4 V, R4 and R5 are swapped. If it reads near 12 V, the divider is not
connected. Either way **stop — do not connect the feeder.**

✅ **Both bands widened 2026-09-01 on measured evidence, and this was mandatory rather than
cosmetic: as originally written, 6.2 and 6.3 would each have failed a perfectly good board.**
A2 measured the feeder's 12 V rail at 11.77 V under load, putting TP1 near 11.47 V, and a
low-tolerance divider legitimately regulates at 10.08 V against a stated floor of 10.3 V.
The two checks were also mutually inconsistent at their edges. **If 6.3 reads low, check 6.2
first** — a low-but-passing 6.2 means the LM1117 is simply in dropout and following its
input, where the output lands at ~10.5 V regardless of R4/R5, and the divider is innocent.

⚠️ If 6.5 does nothing, suspect the boot-recovery lockout before the hardware — and read the
*state*, not the log (§5).

---

## 9. Repository map

| File | Role |
|---|---|
| `aF4-MASTER-REFERENCE.md` | This document — consolidated, audit-oriented |
| `firmware/af4-feeder.yaml` | ESPHome config, **source of truth** |
| `docs/aF4-reference.md` | Feeder specs, measurements, regulator rationale |
| `docs/aF4-pcb-notes.md` | Board design decisions, part equivalence, PCBWay procedure |
| `docs/aF4-esp32-trigger-BOM.md` | Human-readable parts list with reasoning |
| `docs/aF4-assembly-guide.md` | Build sequence and commissioning |
| `docs/aF4-enclosure-notes.md` | Print and fit notes |
| `hardware/enclosure/af4_enclosure_ocp.py` | Parametric enclosure source, self-checking |
| `pcb/gen_pcb.py` | **Source of truth for the board.** Edit this, not the `.kicad_pcb` |
| `pcb/post.py` | Fills copper pours, runs DRC |
| `pcb/make_package.py` | Generates BOM, centroid, fab notes, zip |
| `pcb/af4-trigger-hat-rev-E-GERBERS.zip` | **What was actually uploaded** to the PCB-fabrication line item |
| `pcb/af4-trigger-hat-rev-E-PCBWay.zip` | The all-in-one package. Byte-identical fab data, but **not** the file that was uploaded |
| `pcb/pcbway-order-YB1800644.md` | Order, quote, EQ and payment record |
| `aF4-protoboard-*.svg`, `archive/rev-c-protoboard/protoboard 20x20.stl` | **Rev C history — do not build from these** |

### 9.1 Toolchain constraints worth knowing

- **`pcbnew` is not installed on the Mac.** `pcb/make_package.py` cannot be re-run locally;
  artifact-only fixes must patch the generated file and repack the zip directly. The BOM half
  of the script needs no `pcbnew`, though — its `PARTS` list can be sliced out of the source
  and exec'd to regenerate the CSV, then cross-checked against the centroid.
- `kicad-cli` 7.x has **no `pcb drc` subcommand**; DRC runs through the `pcbnew` Python module.
- Zones must be filled with `ZONE_FILLER` before exporting Gerbers, or the pours come out empty.

---

## 10. Audit status

This document was independently audited on 2026-08-28 (`archive/reviews/aF4-audit-2026-08-28.md`). The audit
re-derived all §2 arithmetic, re-verified all 20 MPNs against live listings, cloned the
Olimex Rev N source to check every `[CAD]` claim, and read the repo's own generated files.

**What held:** every arithmetic result in §2 (V_OUT 10.466 V, worst-case 10.080–10.875 V,
loads 18.6 / 19.95 mA, dissipation 22.1 mW, PhotoMOS drive 9.00 / 6.75 mA); every `[CAD]`
geometry claim; the firmware matching §5 exactly; all 20 part numbers; the drill file
carrying no slot under 0.70 mm; BOM ≡ PARTS ≡ board refs; centroid = 17 SMD; no vias in the
isolation band; every diode and regulator orientation checked pad-by-pad.

**What did not:** §A1 (U1 footprint), §A2 (SMAJ15A), the circuit diagram's topology, the
44-joint count, the dropout reasoning in §2.2, the unstated reboot gap in §5, and the
`[SPEC]`-tagged 12 V ceiling in §1 that was really an inference.

### 10.1 Still unverified after the audit

*(Items 1–3 were closed by the bench session and vendor-documentation pass of
2026-09-01. Struck through rather than deleted, so the audit's original scope stays
readable.)*

1. ~~Supply open-circuit voltage vs the 13 V standoff~~ — **CLOSED `[MEAS]`: 12.13 V.**
2. ~~Feeder trigger-port input impedance / current draw~~ — **CLOSED `[MEAS]`: ~11 kΩ,
   about 0.95 mA at 10.4 V. Negligible against the 18.7 mA quiescent budget and F1's
   0.10 A hold. The load-budget assumption was correct.**
3. ~~Feeder's internal 24 h timer behaviour under external triggering~~ — **CLOSED
   `[VENDOR]`: the schedule is completely overridden while the link port is connected.
   The previous assumption was backwards. See §1.**
4. ~~DRC and the enclosure's 13+3 checks — reported, not re-run~~ — **DRC CLOSED
   2026-08-31**: independently re-run on KiCad 7.0.11 with zones refilled, 61 items, counts
   identical, every class read rather than assumed cosmetic; the shipped Gerbers were also
   re-exported and diffed against the board. The **enclosure's own checks remain
   script-reported**, not independently re-run.
5. ~~Panasonic's recommended SOP4 land pattern~~ — **CLOSED 2026-08-31.** Two independent
   extractions of Panasonic's drawing put every footprint number on the printed
   callout list (0.4, 1.2, 0.8, 2.54 ±0.1) against a package run ending 6.8 ±0.4, and only
   the orientation actually used — 1.2 mm along the lead axis — keeps the toe on the pad
   across the whole span tolerance. **Kenny confirmed the axis assignment visually against
   the drawing on 2026-08-31.** That check is not re-derivable by tooling and must not be
   quietly re-opened.
6. LM1117 V_REF sub-bands — consistent with SNOS412 and every secondary source, but the
   exact table was not re-pulled from TI's PDF.
7. LED viewing angle, 120° vs 160°/140°.
8. **Murata's official EOL notice for C1** — corroborated only by the zero-stock pattern at
   three authorised distributors and Octopart's lifecycle data. Moot in practice: PCBWay
   quoted and sourced the correct MPN.
9. **Stock depth on 18 of the 20 BOM lines** — existence was verified for all 20, but only
   F1 and C1 had stock actually counted. Also moot now: all 20 are priced and on order.

### 10.2 Bench work still unrun (`docs/aF4-meter-test-battery.md`)

None of it blocks anything, and none of it can change the board any more.
**A4** V_loaded and **A5**'s powered current confirmation are two minutes each with the rig
already understood; **A6** (port decay time) would confirm R3 is harmless-but-redundant;
**B1** (hold-time sweep) is confirmatory only, since 20 s clears all three of inD's
published figures; **B2** is confounded by the 5-minute spacing rule; **B3** (held-high
yields exactly one feed) is the one with real information value, because the design's best
safety property currently rests on vendor documentation rather than on this unit.
