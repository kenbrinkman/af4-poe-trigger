# PCBWay resubmission, rev E, 2026-08-29

Ivy replied 2026-08-29 (11:51) to the hold email. Two things came out of it:

1. **Nothing was fabricated and no components were purchased.** The order was
   never paid, so production never started. The hold is effectively in force
   regardless of whether the email was read.
2. **PCBWay asked for a new inquiry rather than an amendment** to
   T-3P4W1125728A. So the rev E package goes in through the SMT quote form,
   not as a reply attachment.

Note that Ivy said she did not receive the previous email while quoting it back
in full underneath her reply, so treat "we did not receive it" as boilerplate.
The operative sentence is the one about nothing being purchased.

Because this is a fresh inquiry, none of the sourcing decisions carry over
automatically. Everything settled in the last round has to be restated in the
files and the remark box, which is what the text below does.

---

## Part 1. Text for the inquiry remark / notes box

Upload `af4-trigger-hat-rev-E-PCBWay.zip` (15 files: Gerbers, drill, BOM,
centroid, PCBWay-README.txt) and paste this:

> aF4 PoE trigger hat, rev E. Qty 5, turn-key assembly, top side only.
>
> This replaces quotation T-3P4W1125728A (Ivy Yang), which was quoted against
> our rev D files. Rev D is withdrawn. Any rev D Gerbers or BOM still on file
> are void and must not be used. Rev E is the only valid data.
>
> Rev E differs from rev D in one respect on the board: the land pattern for U1
> (Panasonic AQY212GS PhotoMOS) was rebuilt to Panasonic's recommended mounting
> pad drawing. The rev D pattern was 1.27 mm pitch against a 2.54 mm part and
> would not have mounted. Outline 57.0 x 50.0 mm, 2 layers, 1.6 mm, 1 oz, ENIG
> preferred, drill tool list, and every other parameter are unchanged from the
> rev D board you quoted.
>
> BOM is 20 lines, 21 placements (17 SMD, 4 through-hole). Through-hole work is
> 28 hand-soldered joints, not the 44 our earlier README stated: J1 5, J2 3,
> J3 10, J4 10. Please quote hand soldering against 28.
>
> Three part numbers were corrected since the earlier quote and are already
> right in this BOM: F1 = 1206L010/60WR (not /60YR), C1 = GRM31CR61H106KA12L
> (not /71H, there is no 10 uF 50 V X7R in 1206), D5 = APT2012SYCK (not
> APT2012SYC). Two of these matched the "Actual Purchase Mfg Part #"
> substitutions your team had already proposed.
>
> Please quote: PCB fabrication, assembly cost, all 20 BOM lines including F1,
> R6 and R7, and total lead time.
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
> One availability question: Murata lists GRM31CR61H106KA12L as end of life, so
> distributor stock only. Please confirm you can source it. If you cannot, tell
> me and I will nominate the alternate myself rather than have one chosen at
> the bench.

---

## Part 2. Short reply to Ivy

**Subject:** Re: PCBWay: Question about SMT Inquiry_T-3P4W1125728A

Hi Ivy,

Understood, and thank you for confirming that nothing has been fabricated or
purchased. That is the important part.

I have submitted a new SMT inquiry with the corrected files. The board is now
labelled rev E. I changed the revision letter deliberately, because rev D files
had already gone out to you and were then found to be invalid, and I did not
want two different file sets both answering to the same name. Anything marked
rev D on your side is superseded and should be discarded.

The new inquiry references T-3P4W1125728A in the notes so your team can pull up
the parts review already done. That review still stands: fifteen of the twenty
BOM lines are untouched, three are the corrections your own sheet had already
flagged as substitutions, and the two new lines are ordinary 0805 resistors.
The only board change is the U1 land pattern.

Two items I would ask you to carry across to whoever picks up the new inquiry:
the hand-soldered joint count is 28, not the 44 our earlier documentation
stated, and C1 (GRM31CR61H106KA12L) is end of life at Murata, so please confirm
you can source it before quoting it.

Thanks for your patience through the revisions.

Best regards,
Kenny Brinkman

---

## Part 3. Checklist

- [ ] Submit new SMT inquiry at pcbway.com with `af4-trigger-hat-rev-E-PCBWay.zip`
- [ ] Paste the remark text from Part 1
- [ ] Send the Part 2 reply to Ivy on the existing thread
- [ ] On the requote, check: assembly cost present, F1 priced, C1 priced against
      the corrected MPN, R6 and R7 both present, 28 joints not 44, total lead time
- [ ] Confirm the new quote number and record it in project memory
