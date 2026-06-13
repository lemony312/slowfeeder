# Mazzer Super Jolly adapter — dimension reference

This document records the measurements driving the Mazzer Super Jolly variant of the
Madkat Feedr grinder adapter. The adapter has two interfaces:

- **Feeder side** — mates with the slow-feeder hub/insert. **Reused unchanged** from the
  original EK43 adapter (`STL/Madkat Feedr_EK43_v5.step`).
- **Grinder side** — drops into the grinder throat. **Re-modeled** for the Super Jolly.

Every value is tagged: **[MEASURED]** (from a physical part), **[REFERENCED]** (from a
published spec or another design), or **[ASSUMED]** (best estimate, verify before relying on it).

> ⚠️ **No calipers were used.** All grinder-side numbers are REFERENCED or ASSUMED.
> The first print should be treated as a **test fit**. Clearances are parameterised in
> `cad/mazzer_super_jolly_adapter.py` so a re-print only needs one number changed.

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

The Super Jolly bean throat is a straight ~59 mm cylindrical seat. Aftermarket hoppers and
the reference funnel (Thingiverse #4758610) use a plain friction-fit spigot — **no screws,
no bayonet**. We follow the same strategy.

| # | Dimension | Value | Confidence | Basis |
|---|---|---|---|---|
| 1 | Grinder throat seat diameter | **59.0 mm** | [REFERENCED] | 4+ vendor listings ("seat/collar/throat 59 mm") |
| 2 | Adapter male spigot OD | **58.4 mm** (= 59.0 − 0.6 clearance) | [REFERENCED]/[ASSUMED] | Etsy adapter "58 mm OD"; ~0.6 mm print clearance |
| 3 | Spigot engagement depth | **32 mm** | [REFERENCED]/[ASSUMED] | Etsy adapter "35 mm tall"; 30–35 mm typical |
| 4 | Center bean bore | **≥ 42 mm** | [ASSUMED] | Must feed beans freely; not published — verify |
| 5 | Lead-in chamfer (spigot base) | 1.5 mm × 45° | [ASSUMED] | Eases insertion |
| 6 | Retention | Friction fit (no fastener) | [REFERENCED] | Reference funnel + Mazzer OEM uses neck friction |
| 7 | Spigot wall thickness | ≈ 3 mm | [ASSUMED] | Print strength vs. bore (58.4 OD, ~42 bore would be thicker; bore set by feeder funnel) |

### Reference designs
- **Thingiverse #4758610** — "Mazzer Super Jolly Input Funnel" (portergieske, CC BY 4.0).
  Friction-fit, no published dimensions; confirms the *strategy*.
- Vendor hopper specs converging on **59 mm** seat (coffeeomega, coffeesparesdirect,
  espressoparts, etc.).

---

## ⚠️ Verify on your physical grinder before a final print

These [ASSUMED] / single-source items are the fit risks:

1. **Throat bore** — caliper the inside of the collar; confirm 59 mm on your unit.
2. **Seat depth** available before the spigot bottoms on the burr carrier (drives #3).
3. **Center outlet bore** the throat will accept (#4).
4. Whether a collar **set screw** is present (if so, a flat/relief can be added).

The single most reliable number is the **59 mm throat seat** (multiply referenced).
