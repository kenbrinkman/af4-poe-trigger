# PCBWay new order, rev E

> **✅ SUPERSEDED BY EVENTS 2026-09-02 — order placed, quoted, paid, in fabrication as
> YB1800644.** The full order record, the quote and the engineering question are in
> `pcbway-order-YB1800644.md`. This file stays for the submission mechanics and the traps
> in PCBWay's form, which are the part worth having next time.

## SUBMITTED 2026-08-31 - status and the form's traps

Submitted as a fresh inquiry. Both cart line items are **"Subject to audit"**,
review quoted 1-2 days, **nothing paid**.

| Item | Product No. | Price |
|---|---|---|
| PCB Production, 2 layers 57x50 1.6 mm, green/white, 24 h, qty 5 | W1125728AS3P5 | $5.00 |
| PCB Assembly, qty 5, $5.80/pc | T-3P6W1125728A | $29.00 |

Shipping $27.27 fully offset by the freight promo. **$34.00 shown, components
NOT yet priced** - expect roughly $110 all-in. Routed to Ivy Yang again.

**TRAP: the new assembly number differs from the deleted one by one character**
- T-3P**6**W1125728A now, T-3P**4**W1125728A before.

### BOTH note boxes cap at 600 characters, enforced SILENTLY

There is no `maxlength` attribute, so nothing truncates on entry and an
over-length field looks perfectly fine. Over the limit, **Calculate does
nothing at all**: no price, no page error, nothing in the console, and "Save to
Cart" stays hidden. The Part 1 text below is 2587 characters and does NOT fit.
What actually went in were two ~590-character versions.

**Rule for what earns space in the box: only what exists nowhere else.** The
three assembly constraints, the 28-joint breakdown and the polarity warnings
are all already in `PCBWay-README.txt` inside the zip, which has no length
limit - so the note points at the README instead of repeating it. The
substitution fence and the C1 alternate exist nowhere else, so they get the
room.

### Uploads: two line items, four slots

The cart splits into **PCB Production** and **PCB Assembly**, each with its own
file state - one all-in-one zip satisfies one and leaves the other empty, which
is what went wrong before. The dialog has four slots (Gerbers zip / BOM /
Centroid / assembly other) and **auto-commits on successful upload**. Its own
instruction: anything related to PCB *fabrication* goes INSIDE the Gerber zip,
not in the "other" slot.

What was uploaded:
- `af4-trigger-hat-rev-E-GERBERS.zip` - the 12 fab files flat at the zip root
  plus `PCBWay-README.txt`. Built 2026-08-31.
- `af4-trigger-hat-BOM.xlsx`
- `af4-trigger-hat-centroid.xlsx`

**`af4-trigger-hat-rev-E-PCBWay.zip` (the all-in-one) was NOT used** and should
not be - it sits beside the new file under a nearly identical name.

Build gotcha: the mounted folder blocks unlink, so `zip` fails with "Operation
not permitted" on its write-then-replace. Build outside the mount, then copy in.

### Still owed on the requote — ✅ ALL DELIVERED 2026-09-02

Components priced on all 20 lines including F1, R6 and R7; C1 priced against
GRM31CR61H106KA12L or the TDK alternate explicitly; 28 hand-soldered joints not
44; total lead time.

Every one of those came back on the 2026-09-02 sheet: 20 lines priced, F1 at
`1206L010/60WR`, C1 at the Murata MPN with **no substitution taken**, R6 and R7
as separate lines, and a 26-28 day lead time. Component $78.96 + assembly $29.00
+ PCB $5.00 = **$112.96**, paid at $169.95 with shipping and tax. See
`pcbway-order-YB1800644.md`.

---

## Historical: the original long-form notes

Everything below predates submission and is kept for its technical wording. The
Part 1 text is **too long for the 600-character box** - do not paste it as-is.

Updated 2026-08-31. This is a COMPLETELY NEW inquiry/order. The previous
quotation T-3P4W1125728A was deleted at PCBWay's end and nothing carries over
from it. Decision by Kenny 2026-08-31: no reply email to Ivy is being sent;
the old thread is closed. The former Part 2 letter below is retained for
history only and must not be sent.

Pre-fab review status (2026-08-31): independent review found nothing that
blocks the order. Full report in `archive/reviews/aF4-prefab-review-2026-08-31.md`. Both
residuals the review left explicitly open are now closed, with provenance:

- **U1 pad axis assignment - CONFIRMED BY KENNY, 2026-08-31, visually**,
  against Panasonic's own "Recommended mounting pad (TOP VIEW)" drawing in
  semi_eng_gu_sop4_1a.pdf. On that drawing the 6 mm span runs vertically and
  the 2.54 mm pitch horizontally; each pad measures 1.2 mm along the span
  (lead) axis and 0.8 mm across the pitch axis. That is what the footprint
  is built to, so the land pattern is correct.
  **This check is not re-derivable by tooling.** The drawing is unreachable
  from the automated environment - the egress proxy returns 403 for
  panasonic.com, mm.digikey.com and datasheet.octopart.com alike - and a
  list of numbers extracted from the PDF cannot settle which dimension sits
  on which axis, which is exactly how the previous wrong footprint survived
  a careful check. Only a human with the drawing open can close this. Do not
  let it be quietly re-opened or re-asserted.
- **C1 EOL - confirmed via Octopart lifecycle data**: last-time-buy
  2019-03-31, last-time-delivery 2020-03-31, manufacturer status "to be
  discontinued". Independently re-checked 2026-08-31. Murata's own page 403s,
  so Octopart is the best available source. Moot in practice: LCSC, which is
  PCBWay's natural supplier, holds the part in volume.

---

## Part 1. Text for the inquiry remark / notes box

Upload `af4-trigger-hat-rev-E-PCBWay.zip` (15 files: Gerbers, drill, BOM,
centroid, PCBWay-README.txt) and paste this:

> aF4 PoE trigger hat, rev E. Qty 5, turn-key assembly, top side only.
>
> This is a fresh inquiry. If any earlier files for this board (marked rev D,
> from a since-deleted quotation) remain on file, they are void. Rev E is the
> only valid data.
>
> Board: 57.0 x 50.0 mm outline, 2 layers, 1.6 mm, 1 oz, lead-free HASL.
> If you are able to substitute ENIG, please do - it is preferred for this
> board, and the shipped README says so - but lead-free HASL is acceptable
> and is what we are ordering against.
> Minimum track 0.35 mm, minimum copper gap 0.24 mm, smallest drill 0.45 mm.
> All standard process - no fine-line capability is required.
>
> Three fabrication notes:
> 1. There are 8 PLATED SLOTS on J1 and J2 at 0.70 mm minimum width (drill
>    tools T2 0.70 mm and T3 0.80 mm). These were deliberately widened from
>    the 0.40 and 0.60 mm the footprint library specifies, both of which are
>    below routing minimum. Please route them at 0.70 mm as drawn and do not
>    narrow them back.
> 2. Drill tools T5 1.20 mm, T6 2.13 mm and T7 3.20 mm are NON-PLATED
>    (mounting and clearance holes) and must stay unplated. The .drl is a
>    single merged file and carries plated/non-plated attributes per tool.
> 3. The copper-free isolation band under U1 must stay clear - see assembly
>    constraint 3 below. It applies to fabrication as much as assembly.
>
> BOM is 20 lines, 21 placements (17 SMD, 4 through-hole). Through-hole work
> is 28 hand-soldered joints: J1 5, J2 3, J3 10, J4 10. Please quote hand
> soldering against 28 joints.
>
> Please quote: PCB fabrication, assembly cost, all 20 BOM lines including
> F1, R6 and R7, and total lead time.
>
> Three assembly constraints, all of them non-negotiable:
> 1. C2 must remain a tantalum. The LM1117 requires output capacitor ESR
>    between 0.3 and 22 ohms and a ceramic substitute makes it unstable.
> 2. J1 must be the 2.5 mm centre-pin PJ-079BH. PJ-002AH and PJ-102AH look
>    identical but are 2.0 to 2.1 mm and will not fit our plug.
> 3. The copper-free band running the height of the board under U1 must stay
>    clear. No copper, no vias, no stitching. It is the isolation barrier
>    between the logic side and the feeder power side.
>
> Sourcing notes:
> - C1 (GRM31CR61H106KA12L) is end of life at Murata; distributor stock only,
>   LCSC holds it in volume. If you cannot source it, the pre-approved
>   substitute is TDK C3216X5R1H106K160AB (10 uF, 50 V, X5R, 1206, 10%).
>   Please do not substitute C1 with anything else without confirming first.
> - F1 = Littelfuse 1206L010/60WR. The 1206L010/60WR-A packaging variant is
>   the same device and is acceptable.
> - No other substitutions on any line without confirmation.

---

## Part 2. Reply to Ivy - NOT TO BE SENT (historical only)

Superseded 2026-08-31: this is a completely new order, the old quotation was
deleted at the vendor, and no email to Ivy is being sent. Text removed to
prevent accidental sending; see git history for the original draft if ever
needed.

---

## Part 3. Checklist — closed 2026-09-02

- [x] Submit new SMT quote at pcbway.com — submitted 2026-08-31 with
      `af4-trigger-hat-rev-E-GERBERS.zip` on the fab item and the BOM/centroid
      xlsx on the assembly item, **not** the all-in-one zip named in the original
      line of this checklist
- [x] Paste the remark text from Part 1 — in two ~590-character halves, per the
      600-character limit recorded above
- [x] On the quote, check: assembly cost present, F1 priced, C1 priced against
      GRM31CR61H106KA12L (or the TDK alternate, explicitly), R6 and R7 both
      present, 28 joints not 44, total lead time — **all confirmed**
- [x] Confirm the new quote number and record it — order **YB1800644**, PCB item
      W1125728AS3P5, assembly item T-3P6W1125728A, recorded in
      `pcbway-order-YB1800644.md`
- [x] Answer the engineering question on the slot widths — sent 2026-09-02 14:05
- [x] Pay — $169.95, 2026-09-02
