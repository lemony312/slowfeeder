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

Spigot geometry (v3): a CLEAN CYLINDRICAL CONNECTOR, matching the look of the
original EK43 adapter (a compact connector, NOT a long ribbed bellows). The grinder
side is a smooth cylindrical plug that drops into the Mazzer Super Jolly throat
collar, sized for a friction fit:
  - throat seat ~59 mm (MEASURED from the proven Thingiverse #4758610 funnel +
    corroborated by published specs)
  - plug OD 58.4 mm (light clearance), ~26 mm engagement into the collar
  - a lead-in chamfer at the tip eases insertion
  - two shallow, low-profile retention beads provide grip without the "bellows" look
The feeder side is still boolean-kept verbatim from the original EK43 solid.
See docs/mazzer-super-jolly-dimensions.md.

Run:  ../.venv/bin/python cad/mazzer_super_jolly_adapter.py
Out:  STL/Madkat Feedr_MazzerSJ_v3.step
      STL/Madkat Feedr_MazzerSJ_v3.stl
"""

import os
import cadquery as cq

# --------------------------------------------------------------------------- #
# PARAMETERS (mm)                                                             #
# --------------------------------------------------------------------------- #
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC_STEP = os.path.join(ROOT, "STL", "Madkat Feedr_EK43_v5.step")
OUT_STEP = os.path.join(ROOT, "STL", "Madkat Feedr_MazzerSJ_v3.step")
OUT_STL = os.path.join(ROOT, "STL", "Madkat Feedr_MazzerSJ_v3.stl")

# Plane (in the original solid's Y axis) where the grinder side meets the feeder
# side. Everything at Y <= TRANSITION_Y is the preserved feeder portion.
TRANSITION_Y = -59.2

# --- Mazzer Super Jolly throat fit (the part the plug drops into) -----------
THROAT_DIA = 59.0          # [REFERENCED + MEASURED] grinder throat collar diameter
PLUG_CLEARANCE = 0.6       # [ASSUMED] diametral fit allowance
PLUG_OD = THROAT_DIA - PLUG_CLEARANCE   # = 58.4 mm friction-fit plug OD

PLUG_LENGTH = 26.0         # engagement depth into the collar (compact, connector-like)
TIP_CHAMFER = 2.0          # lead-in chamfer at the plug tip (eases insertion)

# Optional low-profile retention beads (NOT bellows ribs). Set BEAD_HEIGHT = 0 for a
# fully smooth plug. Beads stand 0.4 mm proud of the plug OD and grip the collar.
BEAD_HEIGHT = 0.4
BEAD_WIDTH = 1.5
BEAD_POSITIONS = [9.0, 18.0]   # axial distance from plug base

BORE = 46.9                # central bean bore — MATCHES the feeder seat bore exactly
BASE_OD = 62.0             # base OD == feeder tube OD at the weld (clean continuation)
BASE_OVERLAP = 1.0         # how far the base sits inside the feeder solid (weld)

# Sanity floor: beans must feed freely (beans ~6-10 mm; proven funnel uses 37 mm).
MIN_BEAN_BORE = 35.0

# Mesh export tolerances
STL_LINEAR_TOL = 0.05
STL_ANGULAR_TOL = 0.2


def build():
    assert BORE >= MIN_BEAN_BORE, f"bore {BORE} < min {MIN_BEAN_BORE}"
    assert PLUG_OD > BORE + 4, "plug wall too thin (<2 mm)"
    assert PLUG_OD <= THROAT_DIA, "plug bigger than throat collar — won't seat"

    src = cq.importers.importStep(SRC_STEP).val()

    # 1) Keep the feeder portion verbatim: intersect with a half-space Y <= cut.
    big = 400.0
    keep_box = cq.Solid.makeBox(
        big, big, big, cq.Vector(-big / 2, TRANSITION_Y - big, -big / 2)
    )
    feeder = src.intersect(keep_box)

    # 2) New clean cylindrical plug as a solid of revolution about the Y axis.
    #    Profile coordinates are (x = radius, y = axial distance from base).
    #    A short tapered shoulder blends the BASE_OD (feeder tube) down to PLUG_OD.
    SHOULDER = 3.0
    profile = [
        (BASE_OD / 2.0, 0.0),                       # base outer (welds to feeder)
        (PLUG_OD / 2.0, SHOULDER),                  # taper shoulder down to plug OD
        (PLUG_OD / 2.0, PLUG_LENGTH - TIP_CHAMFER), # straight plug body
        (PLUG_OD / 2.0 - TIP_CHAMFER, PLUG_LENGTH), # tip lead-in chamfer (outer)
        (BORE / 2.0, PLUG_LENGTH),                  # tip inner (bore)
        (BORE / 2.0, 0.0),                          # base inner (bore == feeder bore)
    ]
    plug = (
        cq.Workplane("XY")
        .polyline(profile)
        .close()
        .revolve(360, (0, 0, 0), (0, 1, 0))
    )

    # Low-profile retention beads: thin rings standing proud of the plug body,
    # coaxial with the plug (Y axis). These grip the collar without the "bellows"
    # look. Each bead is a short tube of OD (PLUG_OD + 2*BEAD_HEIGHT).
    if BEAD_HEIGHT > 0:
        for pos in BEAD_POSITIONS:
            ro = PLUG_OD / 2.0 + BEAD_HEIGHT
            ri = BORE / 2.0
            bead = (
                cq.Workplane("XY")
                .polyline([(ro, pos), (ro, pos + BEAD_WIDTH),
                           (ri, pos + BEAD_WIDTH), (ri, pos)])
                .close()
                .revolve(360, (0, 0, 0), (0, 1, 0))
            )
            plug = plug.union(bead)

    plug_solid = plug.val()
    # Place the plug base just inside the preserved feeder for a clean weld.
    plug_solid = plug_solid.translate(cq.Vector(0, TRANSITION_Y - BASE_OVERLAP, 0))

    # 3) Union onto the preserved feeder solid.
    result = feeder.fuse(plug_solid)
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
