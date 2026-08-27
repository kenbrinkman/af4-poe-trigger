aF4 PoE Trigger Hat - rev D
Fabrication and assembly notes for PCBWay

BOARD
  Size              57.00 x 50.00 mm (rectangular)
  Layers            2
  Thickness         1.6 mm
  Copper            1 oz
  Surface finish    ENIG preferred (HASL acceptable)
  Soldermask        any colour
  Silkscreen        white
  Min trace/space   0.35 mm / 0.20 mm  (well inside standard capability)
  Min drill         0.45 mm (stitching vias)
  Slots             plated, min width 0.70 mm (connector blade terminals on
                    J1 and J2). Deliberately widened from the 0.40 mm the
                    library footprint specifies, which is below routing
                    minimum; annular ring is 0.25 mm at the worst pad.
  Castellations     none
  Panelisation      not required

ASSEMBLY
  Quantity          5
  Sides populated   top only
  SMD placements    20
  Through-hole      4 parts / 44 joints:
                      J1  DC jack        3 terminals + 2 shield tabs
                      J2  3.5 mm jack    3 terminals
                      J3  1x10 socket    10 pins
                      J4  1x10 socket    10 pins
  Sourcing          full turn-key, by manufacturer part number (see BOM)

COORDINATE SYSTEM
  The centroid file uses the board's lower-left corner as (0,0) with Y
  increasing upward. Rotations are counter-clockwise in degrees.

CRITICAL NOTES
  1. J1 must be the 2.5 mm centre-pin variant (PJ-079BH). The visually
     similar PJ-002AH / PJ-102AH are 2.0-2.1 mm and will not fit the
     supplied power plug.
  2. C2 is a POLARISED tantalum. The + terminal goes to the 10.4 V rail
     (pad 1, marked on silkscreen and fab layer).
  3. D1, D2, D3, D5 are polarised. D4 is bidirectional - orientation
     does not matter.
  4. U1 straddles a deliberate copper-free isolation band running the
     height of the board. Do not add copper, vias or stitching in that
     band; it is the barrier between the logic side and the feeder-power
     side of the circuit.
  5. J3 and J4 must be seated flush and square - they mate with a header
     on another board and any tilt will prevent assembly.
