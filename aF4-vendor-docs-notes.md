# aF4 vendor documentation — notes

Source: the inD aquatics help centre, `indaquatics.gorgias.help/en-US`
(surfaced on the shop as `indaquatics.com/pages/support`). All 40 articles
across 10 categories read on **2026-09-01**. Tags follow the master
reference: `[VENDOR]` = stated in inD's own documentation.

This document exists because the trigger hat was designed against a small
set of port figures whose provenance was never a vendor page. Section 1 is
the part that touches the design; the rest is context for owning the unit.

---

## 1. The 0-10 V link port — what inD actually documents

Three integration guides describe the port from three directions. Read
together they are the closest thing to a published spec.

| Source | Trigger voltage | Minimum hold | Notes |
|---|---|---|---|
| GHL 0-10v guide | "9-10V signal" | not stated | video instructs setting 9 V or higher |
| Neptune Apex guide | "9–10V" | not stated | worked example holds ON for 10 and 14 minutes |
| Coralvue Hydros guide | ON 10.0 V / OFF 0.0 V | **"at least 15 seconds"** | app Run Time set to `00:00:15` |
| inD Connect (own dongle) | — | **"at least 10 seconds"** | and must go OFF before the next feed |

### 1.1 The hold time is longer than we assumed — action required

Our documents carry `R1 = ≥ 9 V held > 6 s`, tagged `[SPEC]` in
`aF4-MASTER-REFERENCE.md` §153. **No vendor page states 6 s.** The two
pages that do give a number say 10 s and 15 s.

`af4-feeder.yaml` fires a **10 s** pulse and the audit credits it with a
"67 % margin" over 6 s. Against the vendor figures that margin is gone:
10 s exactly equals inD's own dongle minimum and is **5 s short of the
15 s Hydros requires**. The margin is not 67 % — it is zero or negative
depending on which page you trust.

Read the two numbers charitably and they may be controller-side
conservatism rather than a hard threshold in the aF4 (Hydros run-time
granularity; the dongle figure describes what the *dongle* must see, not
the port). That is a reason to distrust 6 s, not a reason to keep it.

**Recommended change — cheap, and it costs nothing else:**

```yaml
- delay: 20s        # was 10s. >= 15s (Hydros), >= 10s (inD Connect)
- switch.turn_off: feed_ssr
- delay: 280s       # was 290s. 20 + 280 = 300 s, spacing unchanged
```

20 s clears the highest documented figure by 33 % and keeps the 300 s
cycle intact, so the 5-minute spacing rule and the lockout tail are
untouched. The Apex guide holding the line ON for 14 minutes shows long
assertions are ordinary, not risky.

**Retag `R1` from `[SPEC]` to `[VENDOR] ≥ 9 V held ≥ 15 s`** and drop the
6 s figure from `aF4-reference.md`, `aF4-esp32-trigger-BOM.md`, `README.md`
and `aF4-pcb-notes.md`, which all repeat it.

### 1.2 The 5-minute spacing rule is confirmed

The Apex guide states feed cycles need a 5-minute minimum separation.
Our 300 s cycle was derived, not sourced; it is now `[VENDOR]`.

### 1.3 Held-high bounding is confirmed — a positive result

Audit finding B5 argued that a stuck-on SSR yields at most one feed, not
a continuous one. The Apex worked example holds ON for a **14-minute
window and produces exactly one feed**. That is independent vendor
corroboration of the design's best safety property.

The related `R2` figure — "~0 V for > 60 s to re-arm" — is still
unsourced. The Apex OFF windows (~50 min) are far too long to bound it.
The 290 s tail covers any plausible value, so this is a provenance
problem, not a design one.

### 1.4 Connecting the port disables the aF4's own schedule — NEW, and it matters

Both the Apex and Hydros guides say the built-in 24-hour schedule is
**completely overridden when the link port is connected**. Hydros words it
as connection, not signalling.

Nothing in our documents records this. The consequence is operational:

> Once the J2 patch cable is plugged in, the aF4 will never feed on its
> own. If the ESP32 is offline, unadopted, mid-OTA, or
> `input_boolean.reef_af4_schedule_enabled` is OFF, **the fish are not fed
> at all** — silently.

Every guardrail in this project is built to prevent an *extra* feed. This
is the opposite failure and it has no detection at all. The existing
"unavailable ≠ off" lockout guard does not cover it.

**Suggested new open item:** an HA alert when
`counter.reef_af4_feeds_today` is still 0 some margin past the scheduled
feed time. That closes the only unmonitored failure direction.

### 1.5 The link LED is a free commissioning instrument — NEW

The indicator-lights guide: the link LED is **solid when a device is
connected** and **flashes green when a feed signal is received** (newer
units only). Assembly-guide step 6.6 currently ends by plugging J2 in with
nothing to observe. Two checks are now available with no meter:

- plug the patch cable into J2 → link LED goes solid = the port sees the
  connection
- press the HA feed button → link LED flashes green = the 10.4 V pulse was
  accepted, **without waiting to see food move**

Worth adding as steps 6.7 and 6.8.

### 1.6 Cable caution — probably does not apply to us, worth knowing

The Apex guide warns against a standard 3.5 mm audio cable and insists on
inD's own 0-10v splitter. That warning is about a *splitter* — one Apex
variable port feeding several devices — not about the plain male–male
patch cable in our BOM, which drives the port from a single source. Our
J2 (SJ1-3523N, tip = signal, ring tied to sleeve) is consistent with the
TS plug the port expects. **No change indicated**, but if the port ever
fails to acknowledge, borrowing a genuine inD cable to compare is the
cheap test.

### 1.7 Quantity is never remotely controllable

Both guides state feed **quantity is set on the aF4 itself** and cannot be
driven over the link. The port carries "feed now", nothing else. HA can
own *when* and never *how much*. Worth recording so no future session
tries to build a quantity entity.

---

## 2. Operating the unit

**Feed quantity LEDs:** 1 = 5 mL, 2 = 10 mL, 3 = 20 mL, 4 = 30 mL,
5 = 50 mL. 5 mL ≈ one frozen cube; 50 mL ≈ ten.

**Every feed is followed automatically by a self-clean** flushing intake,
output tubing, solenoid and pump. This is very likely *why* the 5-minute
spacing exists — the 300 s window is a clean cycle, not an arbitrary
guard.

**Reservoir:** 200 mL, roughly 50 cubes with 20 mL dilution.

**Temperature settings** (the two pages disagree slightly; the
programming guide is the fuller one):

| Setting | Programming guide | FAQ page |
|---|---|---|
| 1 ❆ | −1 to 0 °C | −1 to 0.5 °C |
| 2 | 0 to 2 °C | 0 to 1 °C |
| 3 | 2 to 3 °C | 1 to 2 °C |
| 4 | 3 to 4 °C | 3 to 4 °C |
| 5 | 4 to 5 °C | 4 to 5 °C |

Setting 2 is the recommended default. Setting 1 reaches the 21-day
freshness claim but demands high-salinity dilution (1.026–1.030 SG) or the
slurry freezes solid. Realistic freshness is 10–14 days; inD's own FAQ
suggests reloading every 7–10 days.

**Feed-time offset LEDs:** −4 h, −2 h, 0, +2 h, +4 h. The unit's daily
feed time is simply *when it was powered on*; changing it permanently
means power-cycling at the desired time. Irrelevant while the link port is
connected (§1.4).

**Power:** 12 V DC brick rated **12.5 A**, ~2 kWh/day at 70 °F ambient.
Confirms `R6`. The docs still give **no figure for the link port's own
input current**, so open item 6 stays open.

**Power button needs a firm 3-second press.** Red LED above it = powered
but off; solid green = running.

---

## 3. Faults, and why they are invisible to us

All five temperature LEDs flashing together is an over-temperature fault,
and **when** the flashing starts is the diagnosis: immediately = fan
failed; within 3 h = bad probe; after 3 h = genuinely hot.

Behaviour splits by serial number — **worth recording ours**:

| Serial prefix | Behaviour on fault |
|---|---|
| 100XXX | standby, continuous beeping, cooling continues, manual restart |
| 20XXX / 60XXX | full shutdown, manual power cycle |

**The fault never clears itself**, even after cooling. Combined with §1.4,
a fault means feeding stops with no signal reaching HA — the same
unmonitored direction, reinforcing the case for the missed-feed alert.

Placement rules that bear on a sump-cabinet install: **6 inches clearance
around all vents**, fan intake kept out of salt spray, active cabinet
ventilation, drip loop on the power cable.

**Condensation drawer:** empty every 14 days, or every 7 in a humid room
or on colder settings. A full drawer is the usual cause of apparent
leaking. Water at the base with an *empty* drawer means solenoid or pump.

---

## 4. Consumables and warranty

Tubing is the wear part: inspect 12–18 months, replace 18 months–2 years
at one feed/day. Deep clean with an inD tablet every 2–4 weeks; auto-clean
between refills, held 10–15 s, ~3 min, beeps when done — never with the
output tube in the tank. Fan: clean monthly, replace every 2–3 years.

Warranty is 12 months plus a 30-day grace period; claims need the serial
(underside sticker) and proof of purchase. Exclusions are physical damage,
installation error and consumables. **Driving the 0-10 V port is a
documented, supported use**, so the trigger hat does not put the warranty
at risk — the port exists for exactly this.

Returns: 14 days on the aF4, 10 % restocking, unused and complete only.

---

## 5. What the vendor docs still do not answer

1. The port's input current — open item 6 is unchanged.
2. The re-arm time (`R2`, our 60 s) — no vendor figure found.
3. The port's actual input impedance or whether it is opto-isolated.
4. Whether a *held* line re-triggers after some very long interval; the
   longest documented assertion is 14 minutes.
5. Confirmation that 6 s is wrong rather than merely unsourced — only a
   measurement on the real unit settles it.

Items 1–4 need a meter and the physical feeder, not more reading.
