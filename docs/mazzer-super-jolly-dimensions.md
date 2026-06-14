# Mazzer Super Jolly adapter — dimension reference

This document records the measurements driving the Mazzer Super Jolly variant of the
Madkat Feedr grinder adapter. The adapter has two interfaces:

- **Body side** — the wide flange with the 3 screw holes that bolt the adapter to the
  feeder. **Reused unchanged** from the original EK43 adapter (`STL/Madkat Feedr_EK43_v5.step`).
- **Grinder side** — the narrow tube that drops into the grinder throat. **Re-modeled**
  for the Super Jolly.

Every value is tagged: **[MEASURED]** (from a physical part), **[REFERENCED]** (from a
published spec or another design), or **[ASSUMED]** (best estimate, verify before relying on it).

> **Update (v4):** the throat diameter (~59 mm) is corroborated by the **actual STL of
> the proven Thingiverse #4758610 funnel** (a part known to fit a real Super Jolly),
> measured directly — see [Measured from the reference model](#measured-from-the-reference-model).
> The adapter keeps the **clean connector shape of the EK43** and terminates in a smooth
> cylindrical plug sized to that collar. A physical caliper check of *your* grinder is
> still recommended; the plug fit is a single parameter (`PLUG_OD`) in
> `cad/mazzer_super_jolly_adapter.py`, so a re-print only needs one number changed.

---

## Coordinate system & orientation

> **Orientation correction (v4):** earlier versions (v1–v3) had the two ends swapped.
> The **wide flange with the 3 screw holes (Y = −48.5)** is the **BODY side** — it bolts
> the adapter to the rest of the feeder and is part of the whole feed process, so it must
> be preserved. The **narrow tube (Y = −78.5)** is the **GRINDER side** that inserts into
> the grinder. v4 preserves the flange/screw end verbatim and reshapes only the grinder
> tube into a Mazzer plug.

The original STEP solid is built around the **Y axis** (not Z):

- **Body face (flange + 3 screw holes):** Y = **−48.5** — PRESERVED
- **Grinder tube tip:** Y = **−78.5** — RESHAPED into the Mazzer plug
- **Cut / transition plane:** Y ≈ **−59.2** (all 3 screw holes sit at Y ≥ −58, safely
  above the cut). The script keeps everything at Y ≥ −59.2 verbatim and rebuilds the
  tube below it.

---

## Body-side interface (PRESERVED — do not change)

The flange end that bolts to the feeder body. Kept verbatim by the boolean-keep, so it
remains dimensionally identical to the EK43 adapter.

| Feature | Value | Y-range | Confidence |
|---|---|---|---|
| Flange face OD (with mounting ears) | ⌀~114 mm | face at Y=−48.5 | High |
| 3× mounting screw holes | at XZ (27.3, 20.2), (0, −34), (−33.9, 3.0) | open to Y≈−68 | High |
| Body bore at cut | ⌀46.9 mm | Y=−59.2 | High |
| Body OD at cut (becomes seating shoulder) | ⌀62 mm | Y=−59.2 | High |
| Transition plane (cut line) | **Y = −59.2** | — | High |

Because the script boolean-keeps the original solid above Y=−59.2, these dimensions are
reproduced exactly, not re-derived.

---

## Grinder-side interface — Mazzer Super Jolly (NEW)

The Super Jolly bean throat is a ~59 mm cylindrical collar/seat. The adapter (v4) keeps
the **clean connector shape of the original EK43 adapter** and reshapes only the grinder
tube into a **smooth cylindrical plug** that drops into that collar by friction —
**no screws, no bayonet**. The OD step at the cut (62 → 58.4 mm) forms a seating
shoulder that rests on top of the collar.

> **Design history:** v1 straight cylinder; v2 ribbed "bellows" taper (rejected — wrong
> look); v3 clean plug but **on the wrong end** (it rebuilt the flange and destroyed the
> 3 body-mount screw holes). **v4 fixes the orientation:** the flange + screw holes are
> preserved verbatim and only the grinder tube is reshaped.

### Measured from the reference model

Direct measurements of `mazzer_funnel_2.STL` from Thingiverse #4758610 (the funnel that
seats in a real Super Jolly throat; the other STL in that download is its plunger/lid):

| # | Dimension | Measured value | Notes |
|---|---|---|---|
| M1 | Rib-crown OD (the bits that grip the throat) | **~54 mm (bottom) → ~59–60 mm (top)** — a *taper* | self-centring; only crowns touch |
| M2 | Rib-valley OD (between ribs) | **~43 mm**, constant | bleeds trapped air/chaff |
| M3 | Spigot engagement length | **~40 mm** | ribbed zone before it blends to cone |
| M4 | Nose lead-in | **~8 mm** tapered, tip ~37 mm | eases insertion |
| M5 | Central bore | **~37 mm**, constant | bean drop |
| M6 | Retention | friction (ribs deform + grip) | README: "snug fit into the throat" + plunger |

**Verdict:** throat ≈ **59 mm confirmed**. The reference funnel proves a ~58 mm plug
seats by friction in this collar. v4 uses a clean **58.4 mm smooth plug** (matching the
EK43 connector style) into that 59 mm collar, with small retention beads for grip.

### As built (v4) — parameters in `cad/mazzer_super_jolly_adapter.py`

| Parameter | Value | Confidence | Basis |
|---|---|---|---|
| Throat collar diameter | **59.0 mm** | [REFERENCED + MEASURED] | 4+ vendor listings + reference model max OD |
| Plug OD | **58.4 mm** (= 59.0 − 0.6 clearance) | [REFERENCED]/[ASSUMED] | friction fit into the 59 mm collar |
| Plug engagement length | **~25 mm** | [ASSUMED] | compact, connector-like (EK43 grinder side is short) |
| Tip lead-in chamfer | **2 mm** | [ASSUMED] | eases insertion |
| Retention beads | 2× **0.4 mm** proud, 1.5 mm wide | [ASSUMED] | light grip without a "bellows"/thread look |
| Bore | **46.9 mm** | derived | matches the feeder seat bore exactly; ≥ 35 mm min |
| Base OD (weld to feeder) | **62 mm** | derived | continues the feeder tube OD cleanly |
| Retention | friction (no fastener) | [REFERENCED] | reference funnel + Mazzer OEM |

The plug is a **clean smooth cylinder** like the EK43 connector body. The fit is set by
`PLUG_OD`; if it's too tight/loose, change that one number and re-run. The retention
beads can be disabled with `BEAD_HEIGHT = 0` for a fully smooth plug.

---

## ⚠️ Verify on your physical grinder before a final print

The design now matches a proven part, but these are still worth a caliper check on *your* unit:

1. **Throat collar bore** — confirm ~59 mm (tune `PLUG_OD` / `THROAT_DIA` if different).
2. **Seat depth** available before the plug bottoms on the burr carrier (drives `PLUG_LENGTH`).
3. Whether a collar **set screw** is present (if so, a flat/relief can be added).

If the fit is too tight or too loose, change `PLUG_OD` (and re-run
`cad/mazzer_super_jolly_adapter.py`).
