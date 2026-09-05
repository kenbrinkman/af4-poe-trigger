# PCBWay order YB1800644 — aF4 trigger hat rev E

**Status as of 2026-09-02: ordered, quoted, paid, in fabrication.** *Current progress lives
in `STATUS.md`, not here.* This file is the record of
what was bought, at what price, and what was answered along the way. The design-side story
lives in `docs/aF4-pcb-notes.md`; the submission mechanics and the traps in PCBWay's form live in
`pcbway-new-inquiry-2026-08-29.md`.

| | |
|---|---|
| Order ID | **YB1800644** |
| Placed | 2026-09-02 18:32:27 |
| Sales rep | Ivy Yang, `service33@pcbway.com` |
| Order amount paid | **$169.95** |
| Order status | **In fabrication** (PCB line item), Engineering Question raised and answered |

## The two line items

| Item | Product No. | Price | Notes |
|---|---|---|---|
| PCB production | **W1125728AS3P5** | $5.00 × 5 pcs | 57 × 50 mm, 2 layers, 1.6 mm, 1 oz finished copper, **lead-free HASL**, build time 24 h |
| PCB assembly | **T-3P6W1125728A** | $107.96 × 5 | Pads 17, thru-holes 4. Turn-key, top side only |

PCBWay's own page reports the board back to us as **17 pads / 4 thru-hole parts**, which
matches the 17 SMD placements and 4 THT parts (28 joints) the README declares. Their read of
the files agrees with ours.

Uploaded: `af4-trigger-hat-rev-E-GERBERS.zip` on the fabrication item;
`af4-trigger-hat-BOM.xlsx` and `af4-trigger-hat-centroid.xlsx` on the assembly item. The
all-in-one `af4-trigger-hat-rev-E-PCBWay.zip` was **not** used — its fab data is
byte-identical, but the cart splits into two line items with separate file state and the
all-in-one satisfies only one of them.

## The quote, received 2026-09-02

`Quotation T-3P6W1125728A - aF4 trigger hat rev E - quoted BOM 2026-09-02.xls` in this
folder. **All 20 lines priced**, which is what the requote was for.

| | |
|---|---|
| Component cost | $78.96 |
| Assembly cost | $29.00 |
| PCB cost | $5.00 |
| **Quoted total, 5 units** | **$112.96** ($22.59/board) |
| Quoted lead time | **26–28 days** |

The $169.95 paid is that $112.96 plus $56.99 of shipping, tax and handling at checkout.

### Everything the requote was asked for, and what came back

| Asked | Result |
|---|---|
| Assembly cost, which was blank on the rev D sheet | ✅ $29.00 |
| F1 priced — it came back unpriced with a bad MPN (`/60YR`) | ✅ `1206L010/60WR`, $0.409 |
| C1 requoted against the real MPN, not the non-existent X7R | ✅ `GRM31CR61H106KA12L`, $2.417 — **up from $1.459**, see below |
| R6 and R7 added as separate lines | ✅ both present at $0.074, no longer one shared 10 k line |
| 28 hand-soldered joints, not 44 | ✅ order note carries 28; their pad count agrees |
| Total lead time | ✅ 26–28 days |
| No substitutions without confirming | ✅ **none taken.** D5 is `APT2012SYCK` and C1 is the Murata part, both as specified — the TDK alternate was not needed |

### Line pricing, and where the money is

Six lines carry **84 %** of the $78.96:

| Ref | MPN | Unit | × 5 |
|---|---|---|---|
| J1 | PJ-079BH | $2.908 | $14.54 |
| C2 | T491B106K025AT | $2.473 | $12.36 |
| C1 | GRM31CR61H106KA12L | $2.417 | $12.09 |
| J2 | SJ1-3523N | $1.878 | $9.39 |
| U1 | AQY212GS | $1.823 | $9.12 |
| J3, J4 | PPTC101LFBN-RC ×2 | $0.886 | $8.86 |

Movement against the rev D sheet: D1 down ($0.242 → $0.192), J2 down ($2.10 → $1.878),
D5 down ($0.403 → $0.242 on the corrected `SYCK` part), and **C1 up 66 %** ($1.459 →
$2.417). The C1 rise is the one worth recording, because the requote was requested on the
grounds that the corrected part is a stocked commodity — LCSC lists it around $0.23
(`archive/reviews/aF4-prefab-review-2026-08-31.md`). Reviewed and accepted: at $22.59/board for a five-piece
prototype run the absolute number does not justify another round trip. **Noted, not
disputed.**

## Engineering question, 2026-09-02 — raised and answered same day

Flagged on the **PCB fabrication item only** (`W1125728AS3P5`), so it was a CAM question,
not a parts question, and the no-substitutions fence was never tripped.

**Their question:** the 8 plated slots on J1/J2 carry two widths, 0.70 mm and 0.80 mm, but
the fab note says "Route at 0.70 mm as drawn". Confirm they should be machined as drawn.

**Answered 14:05 ET by email to Ivy Yang** — confirm as drawn, no file change. The "0.70 mm"
in the note was the *minimum* across the set, not one value for all eight. Their reading of
the Gerbers was correct.

Verified against `gerbers/af4-trigger-hat.drl` before replying:

| Tool | Ø | Plating | Count | What it is |
|---|---|---|---|---|
| T1 | 0.450 | PTH | 11 | stitching vias |
| T2 | 0.700 | PTH slot (G85) | 5 | J1 shield ×2 (0.70 × 2.20), J2 pads R/S/T ×3 (0.70 × 1.40) |
| T3 | 0.800 | PTH slot (G85) | 3 | J1 pads 1/2/3 (0.80 × 2.00) |
| T4 | 1.000 | PTH | 20 | J3, J4 sockets |
| T5 | 1.200 | **NPTH** | 5 | J2 body pegs |
| T6 | 2.130 | **NPTH** | 1 | J1 locating post |
| T7 | 3.200 | **NPTH** | 2 | M3 mounting holes |

47 drilled features. The reply also **pre-answered the plating split**, because the Excellon
is a single mixed-plating file whose PTH/NPTH boundary lives only in `TA.AperFunction`
comments that CAM can legitimately ignore — the most likely second query. Worth the four
extra lines: PCBWay recalculates lead time from the end of each EQ, so a second one would
have cost another day.

Full text of both the question and the reply: `pcbway-EQ-2026-09-02-reply.md`, with the
wider prepared-answer sheet in `pcbway-EQ-2026-09-02-prepared-answers.md`.

## What is still owed, on either side

- **PCBWay:** deliver. Lead time restarts from the EQ answer, so 26–28 days from 2026-09-02.
- **Us:** nothing on the board. The remaining work is firmware (open item 11), two male
  headers into EXT1/EXT2 (item 12), and commissioning (item 15).

One thing that cannot now be fixed: the silkscreen on these five boards reads
**"10.4V 10s pulse"**. The firmware moved to a 20 s pulse on 2026-09-01, after the Gerbers
shipped. Cosmetic, not worth an EQ, and corrected in `gen_pcb.py` for any future revision.
