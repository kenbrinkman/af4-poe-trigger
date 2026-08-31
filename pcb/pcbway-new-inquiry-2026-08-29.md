# PCBWay new order, rev E

Updated 2026-08-31. This is a COMPLETELY NEW inquiry/order. The previous
quotation T-3P4W1125728A was deleted at PCBWay's end and nothing carries over
from it. Decision by Kenny 2026-08-31: no reply email to Ivy is being sent;
the old thread is closed. The former Part 2 letter below is retained for
history only and must not be sent.

Pre-fab review status (2026-08-31): all five review items verified. The two
residuals are closed: the U1 pad drawing axis assignment was confirmed
visually against Panasonic's recommended-mounting-pad drawing (1.2 mm along
the lead axis, 0.8 mm across, 2.54 pitch, 6 mm span), and C1's EOL status
was confirmed via Octopart lifecycle data (last-time-buy 2019-03-31,
last-time-delivery 2020-03-31). Nothing blocks the order.

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
> Board: 57.0 x 50.0 mm outline, 2 layers, 1.6 mm, 1 oz, ENIG preferred.
> Minimum track/space on the board is comfortably above 6/6 mil.
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

## Part 3. Checklist

- [ ] Submit new SMT quote at pcbway.com with `af4-trigger-hat-rev-E-PCBWay.zip`
- [ ] Paste the remark text from Part 1
- [ ] On the quote, check: assembly cost present, F1 priced, C1 priced against
      GRM31CR61H106KA12L (or the TDK alternate, explicitly), R6 and R7 both
      present, 28 joints not 44, total lead time
- [ ] Confirm the new quote number and record it in project memory
