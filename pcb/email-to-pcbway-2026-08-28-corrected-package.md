> **SUPERSEDED 2026-08-29.** PCBWay asked for a new inquiry rather than an
> amendment to T-3P4W1125728A. Use `pcbway-new-inquiry-2026-08-29.md` instead.
> Kept for the technical wording, which was reused there.

**Subject:** aF4 trigger hat rev E, corrected package attached (Quotation T-3P4W1125728A)

Hi Ivy,

Following up on the hold I sent earlier. The corrected package is finished and attached as `af4-trigger-hat-rev-E-PCBWay.zip`.

**Please note the revision letter has moved from D to E.** I did that deliberately so the new files cannot be confused with the rev D set you already have. Everything you hold marked rev D is superseded and should be discarded, Gerbers included. Rev E is the only valid data. The quotation number is unchanged.

The zip contains the Gerbers and drill file, the BOM, the centroid file, and an updated README with the fabrication and assembly notes.

**What changed since the rev D files you quoted**

1. **Board.** The land pattern for U1 (the Panasonic AQY212GS PhotoMOS) was rebuilt from Panasonic's own recommended mounting pad drawing. The rev D footprint was wrong and the part would not have mounted. This is the only change to the board. Outline, size (57.0 x 50.0 mm), layer count, thickness, copper weight and drill tool list are all unchanged, so I would not expect any movement on the bare PCB price.

2. **Three part numbers corrected.** F1 is `1206L010/60WR`, not `/60YR` (the 60 V rating only ships on the WR reel code, and the trip current is 0.25 A). C1 is `GRM31CR61H106KA12L`, which is X5R; there is no 10 uF 50 V X7R in 1206. D5 is `APT2012SYCK`, not `APT2012SYC`. Two of these came back on your sheet as "Actual Purchase" substitutions, so the BOM now states outright what you were going to buy anyway.

3. **Two new BOM lines.** R6 and R7 were previously one shared 10 k line. They are now split: R6 = 1.0 k and R7 = 6.8 k, because the green and yellow LEDs are about 12x apart in efficiency and the green was badly under-driven. The BOM goes from 18 lines to 20. Placement count is unchanged at 21.

4. **Hand-soldered joints are 28, not 44.** The rev D README had the wrong total. The breakdown is J1 5, J2 3, J3 10, J4 10.

**What I am asking for**

A revised quotation covering assembly cost, F1 priced, C1 repriced against the corrected part number, R6 and R7 added as new lines, 28 joints rather than 44, and a total lead time. Quantity is still 5, top side only, full turnkey.

To be clear, the revision letter change does not mean a redesign. It is the same board with one corrected land pattern, relabelled so the two file sets cannot be mixed up. If it is simpler on your side to open a fresh quotation instead of amending this one, please go ahead. Nothing in the sourcing work you have already done needs redoing. Fifteen of the twenty lines are untouched, three are corrections to what you had already identified, and the two new lines are ordinary 0805 resistors.

One question on availability: Murata lists `GRM31CR61H106KA12L` as end of life, so please confirm you can source it. If not, I would rather pick the substitute myself than have one chosen at the bench, so just let me know and I will send an alternate.

**Three things worth re-flagging for assembly**

- C2 must stay a tantalum. The LM1117 needs output capacitor ESR in the 0.3 to 22 ohm range, so a ceramic substitute will make the regulator unstable.
- J1 must be the 2.5 mm centre pin PJ-079BH. The PJ-002AH and PJ-102AH look identical but are 2.0 to 2.1 mm and will not fit our plug.
- The copper free band running the height of the board under U1 must stay clear. No copper, no vias, no stitching. It is the isolation barrier between the logic side and the feeder power side.

Thanks for your patience with the revisions. Better to catch it now than on five assembled boards.

Best regards,
Kenny Brinkman
