# aF4 PoE Trigger — Master Reference (rev D)

**Purpose of this document.** A single consolidated reference for the aF4 frozen-feeder
PoE trigger project, written to be *audited*. Every load-bearing claim carries a provenance
tag so a reviewer can tell what has been verified against a primary source and what is an
assertion that has not. The assertions are the interesting part — attack those first.

> ## ✅ BUILD BLOCKER FIXED AND CLOSED — 2026-08-28
>
> U1 now sits on **Panasonic's own recommended mounting pad**, read off the dimension
> drawing rather than matched to a library part (§A1). The package is regenerated and
> re-verified, and no open item remains on the footprint. **PCBWay must be sent the new
> files** — the ones they hold are still the invalid set. Independent audit findings are
> folded in throughout and marked **[AUDIT]**.

Generated 2026-08-28, revised after independent audit the same day. Canonical source for this file is the repo; the other project docs
(`aF4-reference.md`, `aF4-rev-D-pcb-notes.md`, `aF4-esp32-trigger-BOM.md`,
`aF4-enclosure-notes.md`, `aF4-assembly-guide.md`) remain authoritative in their own areas
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

## A. Build blockers

### A1. U1 is on the wrong footprint — the board cannot be built `[AUDIT]`

`gen_pcb.py` places U1 on KiCad's `Package_SO:SO-4_4.4x2.3mm_P1.27mm`. That footprint's
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

### FIXED — a project-local footprint built from Panasonic's drawing

**Final answer: `footprints/aF4.pretty/AQY212GS_SOP4_Panasonic.kicad_mod`**, authored from the
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

### Rejected: `SO-4_4.4x4.3mm_P2.54mm`, matched on dimensions but not on pad shape

`SOP-4_3.8x4.1mm_P2.54mm` was rejected: right pitch, but pad centres only 5.50 mm apart,
too narrow for a 6.8 mm lead span. The footprint now used matches Panasonic on every
dimension that exists in both:

| | Panasonic AQY212GS | `SO-4_4.4x4.3mm_P2.54mm` |
|---|---|---|
| Body | 4.4 × 4.3 mm | F.Fab outline 4.4 × 4.3 mm — exact |
| Terminal pitch | 2.54 mm | pads at y = ±1.27 — exact |
| Lead span | 6.8 ± 0.4 mm → tips at 3.2–3.6 | pads span 2.6–3.4 from centre |
| Pad 1 quadrant | — | unchanged, so the netmap needed no edit |

**Regenerated in full:** `gen_pcb.py` → `post.py` → Gerber/drill export → `make_package.py`.
Three routing waypoints that had been hard-coded to the old pad rows now derive from the
pad positions. The "ISOLATION BARRIER" silk text moved from y 128.00 to 125.50, because the
taller footprint pushed U1's reference designator onto it.

**Verification:** DRC returns **61 items, identical in class and count to the pre-fix
board** — 0 clearance, 0 courtyard, 0 hole, 0 copper-to-edge, 0 unconnected, 0 mask
bridges; the remainder are the same silkscreen and library-footprint cosmetics as before.
Drill tools 0.450 / 0.700 / 0.800 / 1.000 / 1.200 / 2.130 / 3.200 mm, no plated slot under
0.70 mm. BOM ≡ PARTS ≡ board refs (21). Centroid 17 SMD. The board was also **rendered and
looked at**, not merely measured.

`gen_pcb.py`'s `load()` now checks a project-local `footprints/` directory before the stock
KiCad libraries, so `aF4.pretty` holds any part whose stock footprint is wrong for the part
actually being bought.

### Isolation, re-derived `[AUDIT]`

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

### A2. `gen_pcb.py` says `SMAJ15A` for D2; everything else says `SMAJ13A` `[AUDIT]`

The BOM, `make_package.py` and all prose specify SMAJ13A. Turn-key sources from the BOM,
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

### Requirements

| # | Requirement | Value | Source |
|---|---|---|---|
| R1 | Trigger threshold | ≥ 9 V held > 6 s | `[SPEC]` |
| R2 | Re-arm | port must see ~0 V for > 60 s | `[SPEC]` |
| R3 | Minimum feed spacing | ≥ 5 minutes | `[SPEC]` |
| R4 | Do not drive the port with raw 12 V | OEM dongle measured at **10.37 V** | `[MEAS] 2026-07-10` |
| R5 | Feeder must stay powered continuously | it is a refrigerator | `[SPEC]` |
| R6 | Supply | 12 V, 12.5 A external brick, barrel **5.5 × 2.5 mm centre-positive** | `[MEAS] 2026-07-10` |

### Measured facts about the port

| Measurement | Result | Source |
|---|---|---|
| Tip↔sleeve at rest | 0 V | `[MEAS] 2026-07-10` |
| Tip↔sleeve during an OEM-triggered feed | 10.37 V | `[MEAS] 2026-07-10` |
| "Link" icon mechanism | **mechanical** — a bare plug with nothing attached lights it. Jack insertion switch, no electrical sensing | `[MEAS] 2026-07-10` |
| Consequence | no bleed resistor needed for link detect; rest voltage is genuinely 0 V | `[CALC]` |

**Key design insight:** R1 defines a *window*, not a setpoint. 10.37 V is merely what the
OEM dongle happens to produce. This is why a fixed resistor divider is the right answer and
a trimpot is not.

⚠️ `[AUDIT]` **The upper end of that window is an inference, not a spec.** inD's guide
states a 9 V floor and **no maximum voltage**; the "below 12 V" ceiling is this project's
own reading of the 10.37 V OEM measurement. The worst-case output of 10.88 V (§2.1) already
exceeds what the OEM dongle produces by half a volt. Almost certainly fine for a threshold
input — but that ceiling should carry an `[ASSERT]` tag, and until now it read as `[SPEC]`.

**Open question, unresolved:** whether the feeder's internal 24 h timer keeps running while
external triggering is in use. Assumed yes; not confirmed. `[ASSERT]`

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
> `+12V_RAW` upstream of D1, which is not what `gen_pcb.py` builds. The built topology is
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
brushes the top of the "~9.5–11 V is correct" band stated in `aF4-reference.md`; it is still
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

Switching time (1.3 ms typ) is irrelevant against a 10 s pulse.

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

⚠️ **Open verification item:** both TVS parts have a **13 V standoff on a nominally 12 V
rail**. If the feeder's supply idles above 13 V at no load, D2 will begin to conduct and
heat. The supply's actual open-circuit voltage has not been measured. `[ASSERT]`

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

### Sourcing traps recorded

- **J1:** `PJ-002AH` / `PJ-102AH` look identical but are 2.0–2.1 mm centre pin. Only the
  **"B" suffix** parts are 2.5 mm. The same trap applies to the 12 V splitter cable.
- **C2 must stay tantalum.** The LM1117 requires output-cap ESR between 0.3 Ω and 22 Ω `[DS]`.
  A low-ESR ceramic substitution risks loop instability.
- **C1 is X5R, not X7R.** Murata makes no 10 µF 50 V X7R in 1206; that C/V needs a 1210.

### Bought separately (not on the board)

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

`gen_pcb.py` is the source of truth — it generates the `.kicad_pcb` deterministically from
named coordinates taken from the Olimex Rev N source `[CAD]`, so socket alignment is exact by
construction. **Edit the script, not the board file.**

### Geometry from vendor CAD `[CAD]`

| Feature | Position (Olimex board frame) |
|---|---|
| ESP32-POE-ISO outline | x 90.15–118.15, y 90.00–188.15 (28.00 × 98.15 mm) |
| EXT1 pin 1 | (91.44, 123.22), 2.54 mm pitch |
| EXT2 pin 1 | (116.84, 123.22), 2.54 mm pitch |
| GND | EXT1 pin 3 → (91.44, 128.30) |
| GPIO32 | EXT2 pin 6 → (116.84, 135.92) |

### Verification status of the board

`[ASSERT]` — the following is reported in `aF4-rev-D-pcb-notes.md` and was **not re-run**
during this audit pass. DRC via `pcbnew.WriteDRCReport` (KiCad 7): clearance 0, courtyard
overlaps 0, hole clearance 0, hole-to-hole 0, copper-to-edge 0, unconnected 0, mask bridges 0.
Remaining flags are silkscreen cosmetics and "library footprint differs", both expected for
programmatically placed footprints.

**A defect DRC does not catch, found by inspecting the drill file:** KiCad's SJ1-3523N
footprint specifies 0.40 mm plated slots and PJ-079BH 0.60 mm — both below fab routing
minimum (~0.5 mm drilled / 1.0 mm milled). `gen_pcb.py` now enforces `MIN_SLOT = 0.70 mm` and
prints what it widened. Worst-case annular ring after widening is 0.25 mm.

> **Generalised lesson:** DRC checks what it was told to check. Slot widths, and any
> hand-written count in a generated document, are outside it. Inspect the drill tool list
> before any package leaves the building.

### Isolation

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

`af4-feeder.yaml` in the repo is the source of truth. The ESPHome Device Builder (Docker on
the Unraid server, port 6052) holds its own copy — changes must be pasted there manually,
then Install → Wirelessly.

### The safety architecture

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

### Timing check against the spec `[CALC]`

```
  10 s pulse   ≥ 6 s threshold hold        ✓  (67 % margin)
 290 s off tail ≥ 60 s re-arm              ✓  (383 % margin)
 10 + 290 = 300 s total cycle ≥ 5 min      ⚠ EXACTLY at the limit, not above
```

⚠️ **Audit item.** R3 requires feeds ≥ 5 minutes apart and the script's cycle is exactly
300 s. There is zero margin. Any rounding in ESPHome's `delay` handling, or a press arriving
the instant the lockout clears, lands on the boundary rather than inside it. Widening the
tail to 300 s (giving a 310 s cycle) would cost nothing and remove the edge case. Not yet
changed — flagged for decision.

### `[AUDIT]` The lockout does not survive a reboot

`script.do_feed`'s state lives in RAM. Any reboot inside the 300 s cycle — OTA update,
crash, brownout, power blip — clears the lockout silently. The switch comes back
`ALWAYS_OFF`, so the pin is safe, but `binary_sensor.af4_lockout` reads `off` and the
device accepts a new press immediately.

A sequence that ends with two feeds ~2 minutes apart into the tank: scheduled feed fires →
OTA or crash at t+60 s → HA retry, second schedule slot, or a manual press → second feed.
Low probability, but it is exactly the class of unattended edge this document exists to
catch.

**Fix:** an `on_boot` hook that runs a lockout-only script, so every boot starts locked
out. That covers the power-blip case for free, and pairs naturally with widening the tail
to 300 s. Not yet implemented.

### `[AUDIT]` The web server is a second, unauthenticated control path

`web_server: port: 80` exposes the Feed button to anything on the LAN, with no `auth:`
block. The safety story above — "HA is scheduler only, it presses one button and can do
nothing else" — is true of Home Assistant and **false of the network**. On a home LAN this
is a judgment call rather than a defect, but the document should say so. Commissioning
step 6.5 uses this page, so add `auth:` after commissioning rather than before. Related
hygiene: the API encryption key and OTA password are committed in the repo in plaintext.

### `[AUDIT]` Held-high failure modes are bounded — the design's best safety property

Checked deliberately, since "unscheduled feed" is the nightmare. If the ESP32 crashes with
the SSR on, or the PhotoMOS fails shorted, the port sees a **continuously held** 10.4 V.
Per R2, re-arming requires ~0 V for more than 60 s — so a held-high line produces **at most
one feed and then never re-arms**.

Every stuck-at fault therefore costs one feed, not a feeding loop. This is the single best
safety property the design has, and it emerges from the feeder's own spec rather than from
anything on the board.

### Home Assistant integration

Entities: `button.af4_feeder_feed` (sole control), `binary_sensor.af4_feeder_feed_lockout`,
`binary_sensor.af4_feeder_status`, `sensor.af4_feeder_ip_address`, `sensor.af4_feeder_uptime`,
`button.af4_feeder_restart`.

Helpers: `input_boolean.reef_af4_schedule_enabled` (master kill switch),
`input_datetime.reef_af4_feed_time_1` / `_2`, `counter.reef_af4_feeds_today`,
`sensor.reef_af4_next_feed`, `automation.reef_tank_af4_scheduled_feed`.

Two deliberate choices worth preserving:

1. **Feed counting lives in HA, not on-device** — it survives ESP32 reboots and reuses the
   existing nightly reset automation.
2. **The automation's lockout condition does double duty.** `off` means the device is
   reachable *and* outside its lockout, so an offline ESP32 skips the feed rather than firing
   a button press into the void.

Networking: IP 192.168.1.55 reserved in OPNsense dnsmasq against Ethernet MAC
`20:E7:C8:74:A6:D7` (host override `af4-feeder`, MAC match only, no client identifier). The
board pulled a new DHCP lease after flashing, which broke HA's cached discovery with
`Errno 113`; the reservation is the fix.

**No feedback channel exists.** The 0-10 V port is input-only; there is no electrical
confirmation that a dispense actually occurred. A power-monitoring smart plug on the 12 V
supply could infer feed-motor activity if that is ever wanted.

---

## 6. Enclosure

**External 65.2 × 117.0 × 38.4 mm**, PETG, printed with no supports.
`af4_enclosure_ocp.py` is the parametric source and runs 13 dimensional checks plus 3
solid-interference tests (case vs hat, case vs ESP32, lid vs hat) before exporting — all pass
with zero intersection volume `[ASSERT]`, as reported by the script; not re-run in this pass.

### The vertical stack — the governing dimension

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

### Two details that are easy to lose

- The barrel-jack hole needs its **Ø13 × 1.8 mm counterbore on the outside**, thinning the
  wall to 1.2 mm locally. Without it, 3 mm of wall eats most of the jack's 9.5 mm insertion
  depth. As built the plug engages 6.9 mm.
- The **two Ø3.5 mm LED sight holes** in the lid sit over D3 and D5. This is the entire
  reason LED brightness is a real requirement rather than a cosmetic preference (§2.6).

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
| 2026-08-28 `[AUDIT]` | `gen_pcb.py` said `SMAJ15A` for D2 while everything else said `SMAJ13A` | A value edited in one place and never propagated |
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

---

## 8. Open items

Revised after the 2026-08-28 audit. Items 1–3 are new; item 4 (AQY212 operate current) is
**closed** — see §2.4.

| # | Item | Blocking? |
|---|---|---|
| 1 | ~~U1 footprint~~ — **CLOSED.** Rebuilt from Panasonic's recommended mounting pad, regenerated and re-verified (§A1) | — |
| 2 | **Tell PCBWay to hold.** They have invalid Gerbers and a README claiming 44 hand-soldered joints against a real count of 28 | **YES — do this first** |
| 3 | `on_boot` lockout so the 290 s tail survives a reboot (§5) | No, but it is the only unattended-safety gap left |
| 4 | ~~Verify AQY212 operate current~~ — **CLOSED.** 1.1 mA typ / 3 mA max, turn-off 0.3 mA min. The GPIO32 move was mandatory, not optional | — |
| 5 | **Measure the 12 V supply's open-circuit voltage** against the 13 V TVS standoff. Narrowed: a ±5 % 12 V brick idles ≤ 12.6 V, and D2 sits downstream of D1, so it takes a >13.3 V-idling brick to make D2 warm | No |
| 6 | **Widen the 300 s feed cycle** — confirmed at exactly the 5-minute minimum with zero margin. A 300 s tail costs nothing; do it with item 3 | No — cheap |
| 7 | **Widen commissioning check 6.3** from 10.3–10.5 V to ~10.0–10.9 V, and note that 6.2 and 6.3 are inconsistent at their edges (§2.2) | No — but before commissioning |
| 8 | **Measure the feeder trigger port's input current.** Never measured; the whole load budget silently assumes it draws ~nothing | No |
| 9 | Decide whether to add `web_server: auth:` after commissioning (§5) | No |
| 10 | Line up a current-production substitute for C1 — EOL at Murata, distributor stock only | No |
| 11 | `af4-feeder.yaml` GPIO13 → GPIO32 still needs pasting into the ESPHome Device Builder + OTA | **YES** — the board does nothing until then |
| 12 | Solder two 1×10 male headers into EXT1/EXT2, pins up | **YES** — blocks assembly |
| 13 | Confirm whether the feeder's internal 24 h timer runs while externally triggered | No |
| 14 | Resolve the LED viewing-angle conflict, 120° vs 160°/140° (§2.6) | No — cosmetic |
| 15 | Commissioning steps 6.1–6.6 must all pass before the schedule toggle is enabled | **YES** — gates go-live |

### Commissioning gate (from `aF4-assembly-guide.md` §6)

All voltages referenced to **TP4 (power ground)**, not the ESP32's ground.

| # | Check | Expect |
|---|---|---|
| 6.1 | Splitter tap into J1 | D3 green lit |
| 6.2 | TP1 (12 V) → TP4 | 11.6–12.2 V |
| 6.3 | TP2 (10.4 V) → TP4 | **10.3–10.5 V** — the check that matters |
| 6.4 | TP3 (tip) → TP4 at rest | 0 V, D5 dark |
| 6.5 | Press Feed on the ESPHome web page | D5 lights, TP3 ≈ 10.4 V for 10 s, returns to 0 V |
| 6.6 | Feed Lockout binary sensor | On with the pulse, clears ~5 min later |

If 6.3 reads ~1.4 V, R4 and R5 are swapped. If it reads near 12 V, the divider is not
connected. Either way **stop — do not connect the feeder.**

⚠️ Note 6.3's stated band of 10.3–10.5 V is narrower than the calculated worst-case spread of
10.08–10.88 V (§2.1). A board reading 10.7 V is within design tolerance but would fail this
check as written. Consider widening the acceptance band to 10.0–10.9 V.

---

## 9. Repository map

| File | Role |
|---|---|
| `aF4-MASTER-REFERENCE.md` | This document — consolidated, audit-oriented |
| `af4-feeder.yaml` | ESPHome config, **source of truth** |
| `aF4-reference.md` | Feeder specs, measurements, regulator rationale |
| `aF4-rev-D-pcb-notes.md` | Board design decisions, part equivalence, PCBWay procedure |
| `aF4-esp32-trigger-BOM.md` | Human-readable parts list with reasoning |
| `aF4-assembly-guide.md` | Build sequence and commissioning |
| `aF4-enclosure-notes.md` | Print and fit notes |
| `af4_enclosure_ocp.py` | Parametric enclosure source, self-checking |
| `pcb/gen_pcb.py` | **Source of truth for the board.** Edit this, not the `.kicad_pcb` |
| `pcb/post.py` | Fills copper pours, runs DRC |
| `pcb/make_package.py` | Generates BOM, centroid, fab notes, zip |
| `pcb/af4-trigger-hat-rev-D-PCBWay.zip` | The upload package |
| `aF4-protoboard-*.svg`, `protoboard 20x20.stl` | **Rev C history — do not build from these** |

### Toolchain constraints worth knowing

- **`pcbnew` is not installed on the Mac.** `make_package.py` cannot be re-run locally;
  artifact-only fixes must patch the generated file and repack the zip directly. The BOM half
  of the script needs no `pcbnew`, though — its `PARTS` list can be sliced out of the source
  and exec'd to regenerate the CSV, then cross-checked against the centroid.
- `kicad-cli` 7.x has **no `pcb drc` subcommand**; DRC runs through the `pcbnew` Python module.
- Zones must be filled with `ZONE_FILLER` before exporting Gerbers, or the pours come out empty.

---

## 10. Audit status

This document was independently audited on 2026-08-28 (`aF4-audit-2026-08-28.md`). The audit
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

### Still unverified after the audit

1. Supply open-circuit voltage vs the 13 V standoff — needs a DMM.
2. **Feeder trigger-port input impedance / current draw — never measured.** The whole load
   budget assumes it draws ~nothing. One measurement during an OEM feed closes it.
3. Feeder's internal 24 h timer behaviour under external triggering.
4. DRC and the enclosure's 13+3 checks — reported, not re-run (no `pcbnew` available).
5. **Panasonic's recommended SOP4 land pattern** — pitch (2.54 mm), pad size (0.5 × 1.0 mm)
   and lead span (6.8 ± 0.4 mm) are confirmed; the pad-centre spacing in X still has to come
   off the drawing before U1 can be rebuilt.
6. LM1117 V_REF sub-bands — consistent with SNOS412 and every secondary source, but the
   exact table was not re-pulled from TI's PDF.
7. LED viewing angle, 120° vs 160°/140°.
