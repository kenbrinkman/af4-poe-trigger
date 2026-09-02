# PCBWay Engineer Question — order YB1800644, PCB item W1125728AS3P5
Prepared 2026-09-02. Status at time of writing: EQ flag raised, **question not yet
released**. PCBWay LiveChat (Assistant 05/US): *"The question just generated, we need to
check it first before sends to you… you should be able to receive it within 12 hours."*
Message Center shows 0 unread; both line items still read "has been approved".

**The flag is on the PCB FABRICATION item only (W1125728AS3P5), not the assembly item
(T-3P6W1125728A).** So this is a CAM/Gerber question, not a parts-sourcing question — the
no-substitutions fence has *not* been tripped. PCB progress shows 0%; the 24 h fab clock is
held until the reply goes back.

Reply by email to Ivy Yang, service33@pcbway.com, subject line carrying **YB1800644**.

---

## 1. The drill table — verified against `af4-trigger-hat.drl`

The Excellon is a single **mixed-plating** file (`TF.FileFunction,MixedPlating,1,2`) with
per-tool `TA.AperFunction` attributes. Those attributes are Excellon comments (`; #@!`), so
CAM that ignores them sees no PTH/NPTH split — **this is the single most likely question.**

| Tool | Ø | Plating | Count | What it is |
|---|---|---|---|---|
| T1 | 0.450 mm | **PTH** via | 11 | stitching vias |
| T2 | 0.700 mm | **PTH slot** (G85) | 5 | J1 shield ×2 (0.7 × 2.2), J2 pads R/S/T ×3 (0.7 × 1.4) |
| T3 | 0.800 mm | **PTH slot** (G85) | 3 | J1 pads 1/2/3 (0.8 × 2.0) |
| T4 | 1.000 mm | **PTH** | 20 | J3 and J4, 1×10 pin sockets (10 + 10) |
| T5 | 1.200 mm | **NPTH** | 5 | J2 SJ1-3523N plastic body pegs |
| T6 | 2.130 mm | **NPTH** | 1 | J1 PJ-079BH plastic locating post |
| T7 | 3.200 mm | **NPTH** | 2 | M3 mounting holes (ISO 7380) |

Totals: **8 plated slots, 8 NPTH round holes, 31 PTH round holes, 47 drilled features.**
T5/T6/T7 have **no pad, no annular ring and no net** — they are mechanical only.

## 2. Answers, ready to paste

**Q: "Please split / confirm plated vs non-plated holes."**
> The drill file is intentionally mixed-plating with per-tool attributes. Plated: T1 0.45,
> T2 0.70, T3 0.80, T4 1.00. Non-plated: T5 1.20, T6 2.13, T7 3.20. T5/T6/T7 carry no pad
> and no net — they are mechanical holes for the two connector bodies and the two M3
> mounting holes, and must stay unplated. If you need separate PTH and NPTH drill files I
> can send them within the hour; otherwise please follow the tool list above.

**Q: "Slot width 0.70 mm — confirm, or can we reduce it?"**
> Confirmed at 0.70 mm, and please do not narrow it. The KiCad library footprints specify
> 0.40 / 0.60 mm, which is below routing minimum; the slots were deliberately widened to
> 0.70 / 0.80 mm for manufacturability. Route as drawn.

**Q: "Annular ring on J2 is 0.25 mm — confirm."**
> Confirmed and acceptable. Worst case is J2 pad R: 0.70 × 1.40 mm slot in a 1.20 × 2.20 mm
> pad = 0.25 mm ring. Standard-process minimum, accepted as drawn.

**Q: "Silkscreen overlaps / will be clipped."**
> Accepted as-is, cosmetic only. Clip silkscreen where it lands on pads or mask openings —
> do not move or delete reference designators. The one placement that matters: keep the
> PCBWay order number in silkscreen and **clear of the copper-free isolation band running
> the height of the board under U1.**

**Q: "Board outline / dimensions."**
> Edge_Cuts is a single closed 8-vertex outline, exactly 57.000 × 50.000 mm. No
> panelisation, no castellations, no edge connector.

**Q: "The copper-free band under U1 looks like a pour error / shall we fill it?"**
> No. It is a deliberate isolation barrier between the logic side and the feeder-power side.
> No copper, no vias, no stitching in that band. Do not fill or bridge it.

**Q: Anything touching the BOM, a substitution, or a part being unavailable.**
> Do not answer from this sheet — that would mean the EQ landed on the wrong line item.
> The standing rule holds: no substitutions on any line without confirming first. The only
> pre-approved alternate is C1 → TDK C3216X5R1H106K160AB.

## 3. What the design data actually says (checked, not assumed)

- Board: 57.000 × 50.000 mm from Edge_Cuts extents, 8 vertices, closed.
- DRC: **0 copper/clearance violations, 0 unconnected pads, 0 footprint errors.** The 61
  reported items are 24 silk-on-silk overlaps, 2 silk text-height, and local overrides —
  all cosmetic warnings.
- Zip: 12 fab files flat at root + `PCBWay-README.txt`. One drill file, one drill map.
- Min track 0.35 mm, min gap 0.20 mm (order note says 0.24), min drill 0.45 mm. All well
  inside the ordered 6/6 mil, 0.3 mm capability.

## 4. Housekeeping

- Reply **by email to the sales rep**, per PCBWay's own EQ dialog. LiveChat is not the
  channel and the Message Center thread is not either.
- Keep the reply short and numbered against their question numbers. Do not restate the
  whole fab note — it is already on the order page, untruncated.
- If they ask for corrected files, send **only** the file they asked for. Do not re-upload
  `af4-trigger-hat-rev-E-PCBWay.zip` — that is the unused all-in-one archive sitting under a
  nearly identical name.
- Once the reply is sent, watch for the Production Status item to move off 0%.
