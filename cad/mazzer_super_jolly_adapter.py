"""
Madkat Feedr — Mazzer Super Jolly grinder adapter (parametric).

Strategy
--------
The original EK43 adapter (`STL/Madkat Feedr_EK43_v5.step`) has two interfaces:

  * FEEDER side  (Y <= TRANSITION_Y) — mates with the slow-feeder hub/insert.
                 We keep this portion of the original solid VERBATIM via a boolean
                 cut, so the critical mating geometry is preserved exactly.
  * GRINDER side (Y >= TRANSITION_Y) — the EK43 throat flange + M5 bolt pattern.
                 We discard this and union a new friction-fit spigot sized for the
                 Mazzer Super Jolly bean throat.

Spigot geometry (v2): a RIBBED / BARBED TAPER, reverse-engineered from the proven
Thingiverse #4758610 "Mazzer Super Jolly Input Funnel" STL (mazzer_funnel_2.STL),
which is a part known to fit a real Super Jolly. Measured key facts:
  - throat seat ~59 mm (corroborates published specs)
  - NOT a straight cylinder: rib crowns taper ~54 -> ~59-60 mm, valleys ~43 mm
  - ~40 mm engagement, ~8 mm tapered nose lead-in, ~37 mm bore
The ribs are slightly oversized barbs that deform/grip; the taper self-centres; the
valleys bleed trapped air. See docs/mazzer-super-jolly-dimensions.md.

Run:  ../.venv/bin/python cad/mazzer_super_jolly_adapter.py
Out:  STL/Madkat Feedr_MazzerSJ_v2.step
      STL/Madkat Feedr_MazzerSJ_v2.stl
"""

import os
import cadquery as cq

# --------------------------------------------------------------------------- #
# PARAMETERS (mm)                                                             #
# --------------------------------------------------------------------------- #
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC_STEP = os.path.join(ROOT, "STL", "Madkat Feedr_EK43_v5.step")
OUT_STEP = os.path.join(ROOT, "STL", "Madkat Feedr_MazzerSJ_v2.step")
OUT_STL = os.path.join(ROOT, "STL", "Madkat Feedr_MazzerSJ_v2.stl")

# Plane (in the original solid's Y axis) where the grinder side meets the feeder
# side. Everything at Y <= TRANSITION_Y is the preserved feeder portion.
TRANSITION_Y = -59.2

# --- Mazzer Super Jolly throat fit (the part the spigot drops into) ---------
# All [MEASURED-from-reference-model] unless noted, from mazzer_funnel_2.STL.
THROAT_DIA = 59.0          # [REFERENCED] grinder throat seat diameter (multi-source)

CROWN_OD_TOP = 59.0        # top rib OD (light interference against the throat)
CROWN_OD_BOT = 54.5        # lowest rib OD near the nose (clearance, self-centring)
VALLEY_OD = 49.0           # OD between ribs (air/chaff bleed; proven part ~43-49)
N_RIBS = 5                 # number of barb ribs
RIB_START_S = 2.0          # axial start of first rib (from spigot base)
RIB_PITCH = 6.0            # axial spacing crown-to-crown

NOSE_LEN = 10.0            # tapered nose lead-in length
NOSE_TIP_OD = 37.0         # OD at the very tip (matches proven ~37 mm)
TIP_FLAT_OD = 34.0         # small flat tip face (avoids a zero-wall knife edge)

BORE_BASE = 46.9           # bore at the base — MATCHES the feeder seat bore exactly
BORE_BODY = 40.0           # bore through the spigot body (narrows toward grinder)

# Geometry derived from the rib layout.
BASE_OD = 59.0             # spigot base OD == feeder outer at the weld (~59)
LAST_VALLEY_S = RIB_START_S + (N_RIBS - 1) * RIB_PITCH + RIB_PITCH / 2.0
SPIGOT_TOP_S = LAST_VALLEY_S + NOSE_LEN          # tip, measured from base
BASE_OVERLAP = 0.8         # how far the base sits inside the feeder solid (weld)

# Sanity floor: beans must feed freely. The proven funnel uses a 37 mm bore, so a
# 35 mm floor is conservative-but-realistic (coffee beans are ~6-10 mm).
MIN_BEAN_BORE = 35.0

# Mesh export tolerances
STL_LINEAR_TOL = 0.05
STL_ANGULAR_TOL = 0.2


def _spigot_profile():
    """Closed (radius, axial) cross-section of the ribbed spigot, for revolving
    about the axial axis. Axial coordinate s runs from 0 at the base to
    SPIGOT_TOP_S at the tip. Returns a list of (r, s) points forming a hollow
    annular section: up the outside, across the tip, down the bore, close at base.
    """
    out = []
    # --- outside, base -> tip ---
    out.append((BASE_OD / 2.0, 0.0))                  # base outer (welds to feeder)
    for i in range(N_RIBS):
        cod = CROWN_OD_TOP - i * (CROWN_OD_TOP - CROWN_OD_BOT) / (N_RIBS - 1)
        cs = RIB_START_S + i * RIB_PITCH
        out.append((cod / 2.0, cs))                   # rib crown (grips throat)
        out.append((VALLEY_OD / 2.0, cs + RIB_PITCH / 2.0))  # valley (air bleed)
    out.append((NOSE_TIP_OD / 2.0, SPIGOT_TOP_S - 0.0))      # nose outer at tip
    out.append((TIP_FLAT_OD / 2.0, SPIGOT_TOP_S))            # small flat tip (outer)
    # --- inside (bore), tip -> base ---
    inn = [
        (BORE_BODY / 2.0 - 1.0, SPIGOT_TOP_S),               # tip inner (flat face)
        (BORE_BODY / 2.0, SPIGOT_TOP_S - NOSE_LEN),          # bore opens up the nose
        (BORE_BODY / 2.0, 8.0),                              # hold body bore
        (BORE_BASE / 2.0, 0.0),                              # base bore == feeder bore
    ]
    return out + inn


def build():
    assert BORE_BODY >= MIN_BEAN_BORE, f"body bore {BORE_BODY} < min {MIN_BEAN_BORE}"
    assert NOSE_TIP_OD >= MIN_BEAN_BORE, f"tip bore {NOSE_TIP_OD} < min {MIN_BEAN_BORE}"
    assert VALLEY_OD > BORE_BODY + 4, "valley wall too thin (<2 mm)"
    assert CROWN_OD_TOP <= THROAT_DIA + 0.2, "top rib bigger than throat — won't seat"

    src = cq.importers.importStep(SRC_STEP).val()

    # 1) Keep the feeder portion verbatim: intersect with a half-space Y <= cut.
    big = 400.0
    keep_box = cq.Solid.makeBox(
        big, big, big, cq.Vector(-big / 2, TRANSITION_Y - big, -big / 2)
    )
    feeder = src.intersect(keep_box)

    # 2) New ribbed Mazzer spigot as a solid of revolution about the Y axis.
    pts = _spigot_profile()
    spigot = (
        cq.Workplane("XY")
        .polyline(pts)
        .close()
        .revolve(360, (0, 0, 0), (0, 1, 0))
    )
    spigot_solid = spigot.val()

    # Place the spigot base just inside the preserved feeder for a clean weld.
    spigot_solid = spigot_solid.translate(
        cq.Vector(0, TRANSITION_Y - BASE_OVERLAP, 0)
    )

    # 3) Union onto the preserved feeder solid.
    result = feeder.fuse(spigot_solid)
    result = result.clean()
    return result


def main():
    solid = build()
    bb = solid.BoundingBox()
    print(
        "result bbox  X %.2f..%.2f  Y %.2f..%.2f  Z %.2f..%.2f  vol %.1f"
        % (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax, solid.Volume())
    )
    cq.exporters.export(solid, OUT_STEP)
    cq.exporters.export(
        solid, OUT_STL, tolerance=STL_LINEAR_TOL, angularTolerance=STL_ANGULAR_TOL
    )
    print("wrote", OUT_STEP)
    print("wrote", OUT_STL)


if __name__ == "__main__":
    main()
