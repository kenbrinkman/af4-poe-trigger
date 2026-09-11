# PCBWay EQ reply, assembly sample photos, 09/11/26

Order `YB1800644`, assembly item `T-3P6W1125728A`, rev E.
Photos received 09/11/26 04:04 ET from PCBWay Online Services Team / Vivienne,
cc `service33@pcbway.com` (Ivy Yang) and `feedback03@pcbway.com`.

**Verdict: NOT OK. J3 and J4 are on the wrong face of the board.**
Everything else in the photos checks out.

Reply by email to the sender, starting the body with the word `EQ`, per their
instruction. Note their warning: the build clock is recalculated from the end of
EQ, so answer promptly.

---

## The reply text

Subject: EQ  T-3P6W1125728A  af4-trigger-hat-rev-E  order YB1800644

Hi Vivienne,

EQ. Thank you for the sample photos. The SMT placement is all correct, but the
two socket headers are fitted on the wrong face of the board and need rework
before the boards ship.

### NOT OK: J3 and J4 (PPTC101LFBN-RC, 1 x 10 sockets)

Both are fitted on the TOP side with the socket openings facing up. They must be
fitted on the BOTTOM side, with the socket body hanging below the board and the
solder joints on the top side.

This board is a hat that plugs downward onto a male header on another board, so
the socket openings have to face down. Our assembly note said "sides populated:
top only", and that note was wrong for these two parts. Apologies for the
ambiguity.

Please rework all 5 boards:

1. Remove J3 and J4.
2. Refit both from the opposite face: plastic body against the bottom side of the
   PCB, pins through the same holes, soldered on the top side.
3. Pin 1 goes in the same hole it is in now, the one with the square pad. Do not
   mirror or renumber the pins. It is an in-line 1 x 10 connector, so the hole
   positions do not change.
4. Seat both sockets flush and square to the board. Any tilt will stop the board
   mating with the other board.

No PCB change and no BOM change is needed. The holes are plated through with pads
on both faces, so the same holes and the same parts are used. The J3 and J4
silkscreen legend stays on the top face. That is cosmetic only, please ignore it.

### Also, while the boards are being reworked

- Please clean the flux residue from the bottom side and remove the loose solder
  balls. There is a solder splash near the J2 area and residue around the last pin
  of each socket row.
- Two joints have excess solder: the last pin of each socket row, and one of the
  J1 blade slots. Please reflow them to a normal fillet.
- The J1 and J2 blade slots look low on solder fill in several places. Please
  confirm the slots are filled to your normal standard.
- Please keep the copper-free isolation band down the middle of the board free of
  solder balls and residue. That band is the safety barrier between the two
  halves of the circuit.
- D3 and D5 are the two small LEDs. They are too small to check in the photos, so
  please confirm their cathodes match the centroid file.

### OK: everything else in the photos

I checked the rest against our BOM and centroid file and it is all correct:

- U1 pin 1 dot at the top left, matching the silkscreen pin 1 marker.
- U2 SOT-223 with the tab pad on the left, three pins on the right.
- D1 cathode band at the bottom. D2 cathode band at the top. Correct and opposite,
  as intended.
- D4 fitted. It is bidirectional, so orientation does not matter.
- C2 tantalum with the positive stripe facing right, toward the regulator output.
  Marking 106 25V is correct.
- All resistor codes correct: R1 2200, R2 1002, R3 1003, R4 1210, R5 8870,
  R6 1001, R7 6801.
- C1 and F1 fitted, both non-polarised.
- J1 is the correct barrel jack with 5 soldered terminals and the plastic locating
  post in the unplated hole.
- J2 is the correct 3.5 mm jack with 3 soldered terminals and 5 unplated pegs.
- All 21 designators are populated. Nothing is missing.

Please send a photo of one reworked board when it is done and I will confirm.

Thanks,
Kenneth Brinkman

---

## How the J3/J4 error was found

The hat's own documentation fixes the stack, and it puts the socket body below the
board:

- `docs/aF4-pcb-notes.md`: "male header plastic 2.54 mm + socket body 8.5 mm => the
  hat's underside sits ~11.0 mm above the ESP32's top face." 2.54 + 8.5 = 11.04.
- `docs/aF4-enclosure-notes.md`: "z = 12.62 hat underside (= socket body height
  above the header plastic)", and the two enclosure standoffs rise to z = 12.62.
- `docs/aF4-assembly-guide.md` section 5: "Hat down onto the two headers", after the
  ESP32 is already on its standoffs. The male pins point up, so the socket
  openings must point down.
- The printable fitment dummy carries "two detachable 8.5 mm socket bars (J3/J4)
  that peg into the underside" of the plate.

With the sockets on top, the Olimex male pins reach only about 8.5 mm above the
ESP32's top face while the hat's underside sits at 11.04 mm. They would not reach
the board at all, and even if they did they cannot enter a socket from below.

## Why it was not caught earlier

Three things lined up:

1. `gen_pcb.py` places J3 and J4 with `place(...)` on the front layer, like every
   other part. The footprints sit on `F.Cu` with their silkscreen on `F.SilkS`.
   Nothing in the fab data says "fit from the other side".
2. The centroid file contains SMD parts only. It has no J1, J2, J3 or J4 rows, so
   through-hole side information was never in the machine-readable data at all.
3. `PCBWay-README.txt` says "Sides populated: top only" under ASSEMBLY. PCBWay
   followed it exactly.

Critical note 5 in that README already says J3 and J4 "must be seated flush and
square, they mate with a header on another board". It stopped one sentence short
of saying which face.

## For the next revision

- Put the J3 and J4 footprints on `B.Cu` in `gen_pcb.py` so the fab data matches
  the intent, and move their silkscreen to `B.SilkS`.
- Change the README line to "Sides populated: SMD top only. J3 and J4 are
  through-hole parts fitted from the BOTTOM face, body below the board, soldered
  on top."
- Add the through-hole parts to the centroid file with a side column, so the side
  is carried in machine-readable data rather than in prose.

**The generalisable lesson: a through-hole part's mounting side is invisible in
Gerbers and absent from an SMD-only centroid file, so it exists only in prose. Any
part fitted from the non-standard face has to be called out by designator in the
fab note, and the footprint has to live on that face in the CAD.**
