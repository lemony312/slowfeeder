# Mazzer Super Jolly adapter — dimension reference

This document records the measurements driving the Mazzer Super Jolly variant of the
Madkat Feedr grinder adapter. The adapter has two interfaces:

- **Feeder side** — mates with the slow-feeder hub/insert. **Reused unchanged** from the
  original EK43 adapter (`STL/Madkat Feedr_EK43_v5.step`).
- **Grinder side** — drops into the grinder throat. **Re-modeled** for the Super Jolly.

Every value is tagged: **[MEASURED]** (from a physical part), **[REFERENCED]** (from a
published spec or another design), or **[ASSUMED]** (best estimate, verify before relying on it).

> **Update (v2):** the grinder-side geometry is now derived from the **actual STL of
> the proven Thingiverse #4758610 funnel** (a part known to fit a real Super Jolly),
> measured directly — see [Measured from the reference model](#measured-from-the-reference-model).
> These numbers are tagged **[MEASURED-from-reference-model]**, a stronger basis than the
> original REFERENCED/ASSUMED estimates. A physical caliper check of *your* grinder is
> still recommended, but the design now matches a part proven to work. Clearances/ribs
> are parameterised in `cad/mazzer_super_jolly_adapter.py` so a re-print only needs a
> number changed.

---

## Coordinate system

The original STEP solid is built around the **Y axis** (not Z). The feeder mating face
sits at **Y = −78.5**; the EK43 grinder flange face at **Y = −48.5**. The grinder→feeder
transition plane is **Y ≈ −59.2**. The CadQuery script cuts the original solid at this
plane, keeps the feeder portion verbatim, and unions a new Super Jolly spigot below it.

---

## Feeder-side interface (PRESERVED — do not change)

Extracted from `Madkat Feedr_EK43_v5.step` (`MANIFOLD_SOLID_BREP 'BaseModelForAdapters'`).

| Feature | Value | Y-range | Confidence |
|---|---|---|---|
| Mating end face OD | ⌀51.5 mm | face at Y=−78.5 | High |
| Outer step / register | ⌀53.0 mm | Y=−78.5 → −77.5 | High |
| Central through-bore (main) | **⌀49.6 mm** | Y=−78.5 → ≈−66.5 | High |
| Internal funnel cone | 21.8° half-angle, narrows toward seat | apex ≈ Y=−74.1 | High |
| Inner seat at transition | ⌀46.9 mm | Y≈−58.25 / −59.2 | High |
| Locating holes | 4× ⌀1.2 mm | at Y=−66.5 | High |
| Transition plane (cut line) | **Y = −59.2** | — | High |

Because the script boolean-keeps the original solid above Y=−59.2, these dimensions are
reproduced exactly, not re-derived.

---

## Grinder-side interface — Mazzer Super Jolly (NEW)

The Super Jolly bean throat is a ~59 mm cylindrical seat. The proven reference funnel
(Thingiverse #4758610) does **not** use a plain cylinder — it uses a **ribbed/barbed
tapered spigot** with **no screws, no bayonet**. v2 of our adapter follows that design.

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

**Verdict:** throat ≈ **59 mm confirmed**. The earlier straight-58.4 mm cylinder was in the
right ballpark (it matches the *top* crown) but the proven part is a ribbed taper — more
forgiving and self-centring. v2 adopts the ribbed taper.

### As built (v2) — parameters in `cad/mazzer_super_jolly_adapter.py`

| Parameter | Value | Confidence | Basis |
|---|---|---|---|
| Throat seat diameter | **59.0 mm** | [REFERENCED] | 4+ vendor listings + reference model max OD |
| Top rib crown OD | **59.0 mm** | [MEASURED-from-reference-model] | light interference against throat |
| Bottom rib crown OD | **54.5 mm** | [MEASURED-from-reference-model] | lead-in / self-centring |
| Valley OD | **49.0 mm** | [MEASURED-from-reference-model]* | *raised from the ref's 43 mm so it clears our 46.9 mm feeder bore |
| Rib count / pitch | **5 / 6 mm** | [MEASURED-from-reference-model] | ~5–6 ribs, ~7 mm pitch on ref |
| Engagement length | **~38 mm** | [MEASURED-from-reference-model] | ref ~40 mm |
| Nose lead-in | **10 mm**, tip OD 37 mm | [MEASURED-from-reference-model] | ref ~8 mm, tip ~37 mm |
| Bore (body) | **40 mm**, base 46.9 mm | derived | base matches feeder seat; ≥ 35 mm min |
| Retention | friction (no fastener) | [REFERENCED] | reference funnel + Mazzer OEM |

*Note on the valley:* the reference uses a 43 mm valley with a 37 mm bore. Our adapter
inherits a **46.9 mm feeder bore**, so a 43 mm valley would fall *inside* the bore (zero
wall). We therefore widen the valley to **49 mm** (≥ 2 mm wall) and taper the bore down to
40 mm through the spigot body — narrowing in the bean-flow direction, so no ledge/trap.

---

## ⚠️ Verify on your physical grinder before a final print

The design now matches a proven part, but these are still worth a caliper check on *your* unit:

1. **Throat bore** — confirm ~59 mm (tune `CROWN_OD_TOP` / `THROAT_DIA` if different).
2. **Seat depth** available before the spigot bottoms on the burr carrier (drives engagement).
3. Whether a collar **set screw** is present (if so, a flat/relief can be added).

If the fit is too tight or too loose, change `CROWN_OD_TOP` (and/or `CROWN_OD_BOT`) and
re-run `cad/mazzer_super_jolly_adapter.py`.
