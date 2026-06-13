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
                 Mazzer Super Jolly ~59 mm bean throat.

All grinder-side numbers live in the PARAMETERS block below. Without calipers these
are REFERENCED/ASSUMED (see docs/mazzer-super-jolly-dimensions.md) — treat the first
print as a test fit. To re-tune the fit, change SPIGOT_OD (or SPIGOT_CLEARANCE) and
re-run; nothing else needs to move.

Run:  ../.venv/bin/python cad/mazzer_super_jolly_adapter.py
Out:  STL/Madkat Feedr_MazzerSJ_v1.step
      STL/Madkat Feedr_MazzerSJ_v1.stl
"""

import os
import cadquery as cq

# --------------------------------------------------------------------------- #
# PARAMETERS (mm)                                                             #
# --------------------------------------------------------------------------- #
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC_STEP = os.path.join(ROOT, "STL", "Madkat Feedr_EK43_v5.step")
OUT_STEP = os.path.join(ROOT, "STL", "Madkat Feedr_MazzerSJ_v1.step")
OUT_STL = os.path.join(ROOT, "STL", "Madkat Feedr_MazzerSJ_v1.stl")

# Plane (in the original solid's Y axis) where the grinder side meets the feeder
# side. Everything at Y <= TRANSITION_Y is the preserved feeder portion.
TRANSITION_Y = -59.2

# --- Mazzer Super Jolly throat (the part the spigot drops into) -------------
THROAT_DIA = 59.0          # [REFERENCED] grinder throat seat diameter
SPIGOT_CLEARANCE = 0.6     # [ASSUMED]    radial-fit allowance (diametral)
SPIGOT_OD = THROAT_DIA - SPIGOT_CLEARANCE   # = 58.4 mm friction-fit spigot OD

SPIGOT_LENGTH = 32.0       # [REFERENCED/ASSUMED] engagement depth into throat
SPIGOT_BORE = 46.9         # central bean bore; matches feeder seat bore (>= 42 min)
TIP_CHAMFER = 1.5          # [ASSUMED] lead-in chamfer at spigot tip (45 deg)

# Sanity floor: beans must feed freely.
MIN_BEAN_BORE = 42.0

# Mesh export tolerances
STL_LINEAR_TOL = 0.05
STL_ANGULAR_TOL = 0.2


def build():
    assert SPIGOT_BORE >= MIN_BEAN_BORE, (
        f"bean bore {SPIGOT_BORE} < min {MIN_BEAN_BORE}"
    )
    assert SPIGOT_OD > SPIGOT_BORE + 4, "spigot wall too thin (<2 mm)"

    src = cq.importers.importStep(SRC_STEP).val()

    # 1) Keep the feeder portion verbatim: intersect with a half-space Y <= cut.
    big = 400.0
    keep_box = cq.Solid.makeBox(
        big, big, big, cq.Vector(-big / 2, TRANSITION_Y - big, -big / 2)
    )
    feeder = src.intersect(keep_box)

    # 2) New Mazzer spigot, grown in +Y from the transition plane.
    #    Build as a Z-axis cylinder then rotate so its axis is +Y.
    outer = (
        cq.Workplane("XY")
        .circle(SPIGOT_OD / 2.0)
        .extrude(SPIGOT_LENGTH)
    )
    spigot = (
        outer.faces(">Z")
        .workplane()
        .hole(SPIGOT_BORE)            # through bore for beans
    )
    # Lead-in chamfer on the tip: the outer edge of the +Z (free) face. This is
    # the end that enters the grinder throat, so a chamfer eases insertion.
    spigot = (
        spigot.faces(">Z")
        .edges(cq.selectors.RadiusNthSelector(-1))   # outer (largest) circle
        .chamfer(TIP_CHAMFER)
    )

    spigot_solid = spigot.val()
    # Rotate +Z axis -> +Y axis, then place base at the transition plane.
    spigot_solid = spigot_solid.rotate(
        cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), -90
    )  # +Z -> +Y
    spigot_solid = spigot_solid.translate(cq.Vector(0, TRANSITION_Y, 0))

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
        solid,
        OUT_STL,
        tolerance=STL_LINEAR_TOL,
        angularTolerance=STL_ANGULAR_TOL,
    )
    print("wrote", OUT_STEP)
    print("wrote", OUT_STL)


if __name__ == "__main__":
    main()
