# Reply to PCBWay EQ, order YB1800644 / PCB item W1125728AS3P5

EQ received 2026-09-02 13:58 ET from PCBWay Online Services Team (Ivy Yang).
Subject: "Urgent! PCBWay: EQ of Your PCB Order#W1125728AS3P5_af4-trigger-hat-rev-E-GERBERS.zip"

**Their question:** the 8 plated slots on J1/J2 have two different widths, 0.70 mm and
0.80 mm, but the fab note says "Route at 0.70 mm as drawn". Confirm the slots should be
machined exactly as drawn at 0.70 and 0.80 mm without narrowing.

**Answer: confirm as drawn. No file change required.** The note's "0.70 mm" was the
*minimum* width across the set, not a single value for all eight. Their reading of the
Gerbers is correct.

**They warn: "The lead time will be recalculated starting from the end of EQ."** The 24 h
fab clock restarts when this is answered, so reply same day.

---

## Send this, replying directly to that email

**Subject:** Re: Urgent! PCBWay: EQ of Your PCB Order#W1125728AS3P5_af4-trigger-hat-rev-E-GERBERS.zip

Hi Ivy,

Confirmed. Please machine all 8 slots exactly as drawn, with no modification and no
narrowing.

Both widths are intentional and are set by the connector terminals:

- Tool T2, 0.700 mm: 5 slots. J1 shield x2 (0.70 x 2.20 mm), J2 pads R/S/T x3 (0.70 x 1.40 mm)
- Tool T3, 0.800 mm: 3 slots. J1 pads 1/2/3 (0.80 x 2.00 mm)

All 8 are plated. The "0.70 mm" in my note was the minimum slot width across the set, not a
single value for all of them, so 0.70 mm and 0.80 mm as drawn are both correct.

To save a second query, the rest of the drill file: T1 0.450, T2 0.700, T3 0.800 and T4
1.000 are plated. T5 1.200, T6 2.130 and T7 3.200 are non-plated and must stay unplated.
They are connector body pegs and M3 mounting holes, with no pad and no net.

No file changes are needed. Please proceed as drawn.

Best regards,
Kenneth Brinkman
Order YB1800644

---

## Why the extra paragraph is there

The single mixed-plating Excellon carries its PTH/NPTH split only in `TA.AperFunction`
comments, which CAM can ignore. That was the most likely *second* EQ. Since lead time
restarts at the end of each EQ, pre-answering it is worth the four extra lines.
