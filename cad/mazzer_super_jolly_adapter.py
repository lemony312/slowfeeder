"""
Madkat Feedr — Mazzer Super Jolly grinder adapter (parametric).

Orientation (IMPORTANT — corrected in v4)
-----------------------------------------
The original EK43 adapter (`STL/Madkat Feedr_EK43_v5.step`) spans Y = -78.5 .. -48.5:

  * BODY side   (Y >= TRANSITION_Y, up to the -48.5 face) — the WIDE flange with the
                3 screw holes that bolt the adapter to the rest of the feeder body.
                This MUST be preserved verbatim — it is part of the whole feed process.
  * GRINDER tube (Y <= TRANSITION_Y, down to the -78.5 tip) — the narrow tube that
                inserts INTO the grinder. On the EK43 this fits the EK43 throat; we
                reshape ONLY this end into a plug for the Mazzer Super Jolly collar.

(v1-v3 had this backwards — they preserved the narrow tube and rebuilt the flange,
which destroyed the 3 body-mount screw holes. v4 fixes it: keep the flange+screws,
change only the grinder tube.)

Plug geometry (v4): a CLEAN CYLINDRICAL PLUG, matching the EK43 connector look.
  - Mazzer throat collar ~59 mm (MEASURED from the proven Thingiverse #4758610 funnel
    + corroborated by published specs)
  - plug OD 58.4 mm (light clearance), ~25 mm insertion into the collar
  - the OD step at the cut (62 -> 58.4) forms a SEATING SHOULDER that rests on top of
    the collar so the plug can't fall in
  - a tip lead-in chamfer eases insertion; two low-profile beads add grip

Run:  ../.venv/bin/python cad/mazzer_super_jolly_adapter.py
Out:  STL/Madkat Feedr_MazzerSJ_v4.step
      STL/Madkat Feedr_MazzerSJ_v4.stl
"""

import os
import cadquery as cq

# --------------------------------------------------------------------------- #
# PARAMETERS (mm)                                                             #
# --------------------------------------------------------------------------- #
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC_STEP = os.path.join(ROOT, "STL", "Madkat Feedr_EK43_v5.step")
OUT_STEP = os.path.join(ROOT, "STL", "Madkat Feedr_MazzerSJ_v4.step")
OUT_STL = os.path.join(ROOT, "STL", "Madkat Feedr_MazzerSJ_v4.stl")

# Plane (in the original solid's Y axis) splitting the BODY side (Y >= cut, the
# flange + 3 screw holes, PRESERVED) from the GRINDER tube (Y <= cut, REPLACED).
# All 3 screw holes lie at Y >= -58, so a -59.2 cut keeps them fully intact.
TRANSITION_Y = -59.2

# --- Mazzer Super Jolly throat collar (the part the plug drops into) --------
THROAT_DIA = 59.0          # [REFERENCED + MEASURED] grinder throat collar diameter
PLUG_CLEARANCE = 0.6       # [ASSUMED] diametral fit allowance
PLUG_OD = THROAT_DIA - PLUG_CLEARANCE   # = 58.4 mm friction-fit plug OD

PLUG_LENGTH = 25.0         # insertion depth into the collar (below the shoulder)
TIP_CHAMFER = 2.0          # lead-in chamfer at the plug tip (eases insertion)

# Optional low-profile retention beads (NOT bellows ribs). Set BEAD_HEIGHT = 0 for a
# fully smooth plug. Beads stand 0.4 mm proud of the plug OD and grip the collar.
BEAD_HEIGHT = 0.4
BEAD_WIDTH = 1.5
BEAD_OFFSETS = [9.0, 17.0]     # axial distance BELOW the shoulder (into the collar)

BORE = 46.9                # central bean bore — MATCHES the preserved bore at the cut
SHOULDER_OD = 62.0         # body OD at the cut; the 62->58.4 step seats on the collar
BASE_OVERLAP = 1.0         # how far the plug base reaches up into the preserved solid

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

    # 1) PRESERVE the body side verbatim: keep everything at Y >= TRANSITION_Y.
    #    (flange + 3 screw holes + upper body that bolts to the feeder)
    big = 400.0
    keep_box = cq.Solid.makeBox(
        big, big, big, cq.Vector(-big / 2, TRANSITION_Y, -big / 2)
    )
    body = src.intersect(keep_box)

    # 2) New Mazzer plug, grown DOWNWARD (-Y) from the cut plane. Solid of
    #    revolution about Y. Profile coords are (x = radius, y = absolute Y).
    tip_y = TRANSITION_Y - PLUG_LENGTH
    profile = [
        # --- outside, from the weld (just inside the body) down to the tip ---
        (SHOULDER_OD / 2.0, TRANSITION_Y + BASE_OVERLAP),  # base outer (welds up)
        (SHOULDER_OD / 2.0, TRANSITION_Y),                 # shoulder (rests on collar)
        (PLUG_OD / 2.0, TRANSITION_Y),                     # step in to plug OD
        (PLUG_OD / 2.0, tip_y + TIP_CHAMFER),              # straight plug body
        (PLUG_OD / 2.0 - TIP_CHAMFER, tip_y),              # tip lead-in chamfer (outer)
        # --- inside (bore), tip back up to the weld ---
        (BORE / 2.0, tip_y),                               # tip inner (bore)
        (BORE / 2.0, TRANSITION_Y + BASE_OVERLAP),         # base inner == preserved bore
    ]
    plug = (
        cq.Workplane("XY")
        .polyline(profile)
        .close()
        .revolve(360, (0, 0, 0), (0, 1, 0))
    )

    # Low-profile retention beads: thin coaxial rings standing proud of the plug,
    # below the shoulder (inside the collar). Grip without the "bellows" look.
    if BEAD_HEIGHT > 0:
        ro = PLUG_OD / 2.0 + BEAD_HEIGHT
        ri = BORE / 2.0
        for off in BEAD_OFFSETS:
            y0 = TRANSITION_Y - off
            bead = (
                cq.Workplane("XY")
                .polyline([(ro, y0), (ro, y0 - BEAD_WIDTH),
                           (ri, y0 - BEAD_WIDTH), (ri, y0)])
                .close()
                .revolve(360, (0, 0, 0), (0, 1, 0))
            )
            plug = plug.union(bead)

    # 3) Union the plug onto the preserved body.
    result = body.fuse(plug.val()).clean()
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
