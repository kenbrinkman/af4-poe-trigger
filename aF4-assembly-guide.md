# aF4 PoE Trigger — Assembly Guide (rev E)

Build sequence for the ESP32-POE-ISO feeder trigger with the rev E PCB hat.
Companion docs: `aF4-esp32-trigger-BOM.md` (parts), `aF4-pcb-notes.md`
(board design and PCBWay ordering), `aF4-enclosure-notes.md` (print details),
`aF4-reference.md` (feeder specs and measured values).

Rev D is a much shorter build than rev C. There is no protoboard to cut, drill,
populate or wire; no resistors to stand on end; no splices to heatshrink; no
regulator pin to sleeve; and nothing to set at the bench. The circuit arrives
assembled and tested. What is left is: print, plug together, flash, meter, enable.

## 0. Parts and tools

Everything from the BOM, plus: a soldering iron (for exactly two headers), a
multimeter, M2 and M3 screwdrivers, and a 3.5 mm mono or stereo patch cable with
a plug on each end.

Not needed any more: 22 AWG wire, heatshrink, the 2.2 mm drill, a hacksaw, a bench
supply, a trimmer tool.

## 1. Print the enclosure

Print `aF4-trigger-case.stl` and `aF4-trigger-lid.stl` in PETG, orientations as
exported, no supports. 3 walls, 15–25 % infill, 0.2 mm layers.

Before going further, test-fit into the +X long wall:

- a 5.5 × 2.5 barrel plug into the counterbored hole,
- a 3.5 mm plug into the smaller hole.

A light chase with a round file is normal on a first print.

Chase the four lid sight holes with a 1/8" drill from the **inside** face only.
Do not open up the Ø2.6 apertures on the outer face — those are the seats the
light pipes land on.

### Light pipes

Four pipes, cut from **3 mm / ⅛" clear acrylic rod**. One 6" rod makes all four
with half of it left over; a 4" rod is also enough.

| Pipe | Over | Cut length | Should stand proud of the lid's INNER face by |
|---|---|---|---|
| ×2 | PWR1 (red), LNK1 (green) — Olimex | **22.7 mm** | 20.6 mm |
| ×2 | D3 (green), D5 (yellow) — hat | **10.1 mm** | 8.0 mm |

The rod occupies 2.10 mm inside the lid (seat at z 25.60 down to the lid
underside at 23.50), which is where that second column comes from. **That is the
check to trust** — seat a pipe dry in the lid and measure the protrusion with
calipers. It verifies the length against the part in your hand, with no board
involved.

**Tolerance is one-sided.** The lengths leave 0.6 mm of air over each LED. Short
is harmless — losing another half-millimetre of gap costs almost nothing in
brightness. Long is not: **a pipe that touches an LED is too long.** When in
doubt cut 0.3 mm short.

**Cutting.** Fine-tooth razor saw in a miter block, cut ~0.5 mm long, then face
to length. Do not use side cutters — acrylic chips and you will crack the rod.
A rotary cut-off disc works but melts a hazed rim you then have to face off
anyway.

**Facing and polishing.** Only the two **ends**. Hold the rod square against
wet-or-dry laid on glass or tile and draw circles: 400 → 800 → 1500 → 2000, then
a plastic polish (Novus 2, PlastX) on a cloth. **Leave the sides alone** — the
rod pipes light by total internal reflection off the acrylic/air sidewall, and
sanding or painting the side is exactly how you dim it. The LED-facing end
matters most; it is the coupling face.

Flame polishing gives a better end but is optional and easy to overdo: one fast
pass with butane, and check with calipers afterwards, because **a bulged end
over 3.5 mm will not pass the bore.**

**Fitting.** Deburr the bore, drop the pipe in from the lid's inside face until
it stops on the aperture step, then a small bead of **clear 5-minute epoxy**
around it on the inside face. Keep the epoxy inside; there is no need for it in
the Ø2.6 well.

- **Do not use cyanoacrylate.** CA crazes acrylic and its vapour will frost the
  polished ends — and anything else in the box.
- **Do not use acrylic solvent cement.** It does not bond PETG and will craze it.
- Neutral-cure silicone is a fine alternative if you would rather have something
  that stays flexible. Hot glue creeps and yellows; don't.

The pipe seats 0.9 mm below the outer face, looking up a shallow Ø2.6 well. That
is deliberate — it protects the end and the well is too shallow to narrow the
view. Cutting the pipes longer to sit flush does not work: a 3 mm rod will not
pass a 2.6 mm aperture.

**Cross-talk** between PWR1 and LNK1 (centres 5.715 mm apart) is not worth
engineering around. Both are steady-state indicators — red on means the 3V3 rail
is up, green on means the link is up — so a little bleed does not change what
either one tells you.

**Check before you close up.** With the splitter tap live and the patch cable in,
you should read red PWR1 and green LNK1 from a metre away, square on.

## 2. Receive and inspect the board

The hat arrives populated. Give it thirty seconds:

- **C2 polarity** — the tantalum's stripe/+ end must face the 10.4 V rail (pad 1,
  marked on the silkscreen).
- **J1 is the 2.5 mm centre-pin jack.** Plug the feeder splitter's tap lead into
  it and confirm it seats with a click, not a wobble. A 2.1 mm part will feel
  loose; if it does, stop — see the note in the BOM.
- **U1 pin 1** dot toward the ESP32 side of the board.
- Nothing bridging the copper-free isolation band running down the middle.

Meter, board unpowered: **J1 centre pin to J2 sleeve should read open** (the
PhotoMOS is off and the LM1117 is unpowered). Between the 12 V test pad and GND
you will read the reverse-polarity diode, not a short.

## 3. Fit the male headers to the ESP32

The Olimex board ships with EXT1 and EXT2 as bare plated holes. Solder a
**1 × 10 male header into each, pins pointing up**, plastic sitting flat on the
board's top face.

Get these square. The hat mates over both at once, and a header leaning even a
couple of degrees will fight the sockets. Tack one end pin, check the header is
flat and perpendicular, then do the remaining nine.

## 4. Flash the ESP32

There is no USB cutout in the case, so flash **before** final assembly if this is
a fresh board. `af4-feeder.yaml` in this folder is the source of truth; paste it
into the ESPHome Device Builder on the Unraid server (port 6052) and install.

> **Do this once before that first install.** The YAML no longer carries its
> credentials inline — it reads them with `!secret`, and `!secret` resolves against
> the `secrets.yaml` sitting beside the file being compiled, **not** against this
> repo. Open the Device Builder's Secrets editor and create the four keys listed in
> this folder's `secrets.yaml` (`af4_api_key`, `af4_ota_password`,
> `af4_web_username`, `af4_web_password`). Without them the build fails at
> compile time with an unresolved-secret error, which is the safe way to fail.
>
> **Then mind the OTA ordering.** All three credentials were rotated 2026-09-02.
> The Device Builder authenticates the *upload* with the password already on the
> device and installs firmware carrying the new one, so the first install after
> the rotation still needs the **old** OTA password. It is recorded in the header
> of `secrets.yaml`; delete that line once the install succeeds.
>
> **And expect Home Assistant to ask.** The API encryption key changed, so the
> ESPHome integration will prompt for the new one after the device comes back.
> Entity IDs and history survive — the device name is unchanged.

> **If you are re-using the already-flashed board:** the trigger pin changed.
> Rev E drives **GPIO32**, not GPIO13, because of the factory 2.2 kΩ pull-up on
> GPIO13 — see `aF4-pcb-notes.md`. Push the updated YAML over OTA before
> you plug the hat on. The board will do nothing at all until you do.

## 5. Assemble

Order matters — the hat covers two of the ESP32's mounting screws.

1. ESP32-POE-ISO onto its three standoffs, RJ45 into the wall opening, 3 × M2.
2. Hat down onto the two headers. Both jack noses should drop into their wall
   holes as the sockets seat; if they do not line up, the sockets are not fully
   home. Press evenly along the socket rows, not on the jacks.
3. 2 × M3 self-tappers through the hat's mounting holes into the two tall
   standoffs. Snug, not tight — the sockets locate the board, the screws just
   stop it lifting.
4. Leave the lid off for §6.

## 6. Commissioning checks

Ethernet first, feeder power second. All voltages are referenced to the **GND**
test pad on the power side of the board (TP4), not to the ESP32's ground.

| # | Check | Expect |
|---|---|---|
| 6.1 | Splitter tap plugged into J1 | Green LED (D3) lit |
| 6.2 | TP1 (12 V) to TP4 | **11.4–12.0 V** (12 V less the Schottky drop) |
| 6.3 | TP2 (10.4 V) to TP4 | **10.0–10.9 V.** This is the check that matters — it confirms the R4/R5 divider |
| 6.4 | TP3 (tip) to TP4, at rest | 0 V, and the yellow LED (D5) dark |
| 6.5 | Press the Feed button on the ESPHome web page | Yellow LED lights, TP3 reads ~10.4 V for **20 s**, then returns to 0 V |
| 6.6 | Feed Lockout binary sensor | Turns on with the pulse, clears **310 s** later |
| 6.7 | Plug the 3.5 mm patch cable into J2 | **Link LED on the aF4 goes solid** — the port sees the connection |
| 6.8 | Press Feed again | **Link LED flashes green** — the pulse was accepted. Confirms the trigger without waiting to watch food move (newer units; our SN 130063 qualifies) |

If 6.3 reads ~1.4 V, R4 and R5 are swapped. If it reads near 12 V, the divider is
not connected. Either way, stop — do not connect the feeder.

⚠️ **Ranges widened 2026-09-01 on measured evidence.** 6.2 was 11.6–12.2 V and 6.3 was
10.3–10.5 V; **both would have failed a perfectly good board.** The feeder's 12 V rail
measures 11.77 V at its worst under load (`aF4-meter-test-battery.md`, A2), putting TP1
near 11.47 V, and a low-tolerance divider legitimately regulates at 10.08 V.

**If 6.3 reads low, check 6.2 first.** A low-but-passing 6.2 means the LM1117 is simply
in dropout and following its input — the divider is innocent. In dropout the output
lands at ~10.5 V regardless of R4/R5, which is why the widened range is the correct
test rather than a loosened one.

**The ESPHome web page requires a login** — username and password are in `secrets.yaml`,
which is gitignored and not in the repo. Added 2026-09-01 to close an unauthenticated LAN
control path; the credentials were rotated 2026-09-02. Home Assistant is unaffected — it
uses the API, not this page.

**After any reboot inside a feed cycle the device serves a 300 s recovery lockout** and
ignores Feed presses until it clears. If 6.5 does nothing, suspect this before the
hardware — but **do not go looking for it in the log.** The `on_boot` message fires
seconds after boot, while ethernet is still coming up and no log client is attached
yet, and ESPHome does not replay it. Verified 2026-09-01: the line is never observable.

**Read the state instead.** Feed Lockout ON at a low uptime, with nobody having pressed
Feed since the reboot, IS the recovery lockout — `do_feed` state is RAM-only and the
reboot wipes it, so nothing else can hold that sensor on. And check **uptime** first:
a Restart click that silently failed to register looks exactly like a broken lockout.

Only once 6.1–6.6 all pass, connect the 3.5 mm patch cable from J2 to the aF4's
0-10 V port and confirm the link icon lights on the feeder.

## 7. Close up and enable

1. Lid on, 4 × M3 × 12. All four sight holes should land over their LEDs: **D3**
   (green, rail live) and **D5** (yellow, feed) on the hat, **PWR1** (red, 3V3
   rail) and **LNK1** (green, ethernet link) on the Olimex board. With the
   splitter tap live and the patch cable in, all three of D3, PWR1 and LNK1
   should read through the lid without opening anything.
2. In Home Assistant, run one manual feed via `button.af4_feeder_feed` and watch
   the feeder actually cycle.
3. Only then turn on `input_boolean.reef_af4_schedule_enabled`.

## Rev C history

The rev C protoboard build sequence — cutting and drilling the board, standing
the resistors vertically, sleeving the LM1117's crossed pin 1, splicing the
polyfuse into the jack pigtail and the TVS behind the 3.5 mm plug — is preserved
in git history along with `aF4-protoboard-layout.svg` and
`aF4-protoboard-solder-side.svg`. None of it applies to rev D, and the two
protoboard SVGs describe hardware that no longer exists.
