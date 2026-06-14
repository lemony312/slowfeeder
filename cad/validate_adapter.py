"""
Validation harness for the Mazzer Super Jolly adapter (v3, clean plug connector).

No printer available, so we validate geometrically:
  1. Mesh is watertight + single body + winding-consistent (printable shell).
  2. Feeder-side mating geometry is preserved vs. the original EK43 adapter
     (the portion at Y <= TRANSITION_Y must be dimensionally identical).
  3. Grinder-side plug fits the Mazzer Super Jolly throat collar:
       - plug OD within the friction-fit window of the ~59 mm collar
       - plug is a clean cylinder (not a long ribbed bellows): OD ~constant along
         the body apart from small retention beads
       - engagement length in the expected band
  4. Bean bore is unobstructed end-to-end and >= minimum.

Exit code 0 = all pass.
Run: ../.venv/bin/python cad/validate_adapter.py
"""

import sys
import os
import cadquery as cq
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC_STEP = os.path.join(ROOT, "STL", "Madkat Feedr_EK43_v5.step")
OUT_STL = os.path.join(ROOT, "STL", "Madkat Feedr_MazzerSJ_v3.stl")
OUT_STEP = os.path.join(ROOT, "STL", "Madkat Feedr_MazzerSJ_v3.step")

# expectations (keep in sync with mazzer_super_jolly_adapter.py)
TRANSITION_Y = -59.2
THROAT_DIA = 59.0
PLUG_OD = 58.4
BEAD_HEIGHT = 0.4
MIN_BEAN_BORE = 35.0
FEEDER_FACE_Y = -78.5
ENGAGE_MIN, ENGAGE_MAX = 20.0, 32.0   # acceptable plug engagement length band

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}  {detail}")


def radius_present(solid, r, y):
    box = cq.Solid.makeBox(0.6, 0.6, 0.6, cq.Vector(r - 0.3, y - 0.3, -0.3))
    try:
        return solid.intersect(box).Volume() > 1e-3
    except Exception:
        return False


def outer_radius_at(solid, y):
    slab = cq.Solid.makeBox(400, 0.4, 400, cq.Vector(-200, y - 0.2, -200))
    sec = solid.intersect(slab)
    bb = sec.BoundingBox()
    return max(abs(bb.xmin), abs(bb.xmax), abs(bb.zmin), abs(bb.zmax))


def inner_bore_dia_at(solid, y):
    for i in range(0, 80):
        r = i * 0.5
        if radius_present(solid, r, y):
            return r * 2.0
    return None


def main():
    # --- 1. mesh sanity ---
    mesh = trimesh.load(OUT_STL)
    check("STL is watertight", mesh.is_watertight,
          f"(watertight={mesh.is_watertight}, volume={mesh.volume:.0f})")
    nbodies = len(mesh.split(only_watertight=False))
    check("STL single body", nbodies == 1, f"(bodies={nbodies})")
    check("STL winding consistent", mesh.is_winding_consistent, "")

    new = cq.importers.importStep(OUT_STEP).val()
    orig = cq.importers.importStep(SRC_STEP).val()

    # --- 2. feeder-side preserved (the whole point of the boolean-keep) ---
    for y in [FEEDER_FACE_Y + 0.5, -72.0, -66.5, TRANSITION_Y - 0.5]:
        ro = outer_radius_at(orig, y)
        rn = outer_radius_at(new, y)
        check(f"feeder outer radius preserved @Y={y}",
              abs(ro - rn) < 0.05, f"(orig={ro:.2f} new={rn:.2f})")
    check("feeder main bore open at face",
          not radius_present(new, 5.0, FEEDER_FACE_Y + 1.0),
          "(center hollow at feeder face)")

    # --- 3. plug fits the Mazzer collar and is a CLEAN cylinder ---
    bb = new.BoundingBox()
    # sample the plug body (skip the shoulder near the transition and the very tip)
    ys = [y for y in [TRANSITION_Y + 5 + 0.5 * i for i in range(0, 80)]
          if y < bb.ymax - 3.0]
    radii = [outer_radius_at(new, y) for y in ys]
    max_od = max(radii) * 2
    # body OD excluding beads: the median is the plain wall
    radii_sorted = sorted(radii)
    body_od = radii_sorted[len(radii_sorted) // 2] * 2

    check("plug fits collar (OD within friction window)",
          (THROAT_DIA - 1.2) <= body_od <= THROAT_DIA,
          f"(body OD={body_od:.2f}, collar={THROAT_DIA})")
    check("beads do not exceed collar",
          max_od <= THROAT_DIA + 0.2,
          f"(max OD inc. beads={max_od:.2f})")
    # clean cylinder: body OD nearly constant (swing small — beads are <=0.4mm proud)
    od_swing = (max(radii) - min(radii)) * 2
    check("plug is a clean cylinder (not a bellows)",
          od_swing <= 2.0,
          f"(OD swing along body={od_swing:.2f} mm, beads ~{2*BEAD_HEIGHT})")

    engage = bb.ymax - TRANSITION_Y
    check("engagement length in band",
          ENGAGE_MIN <= engage <= ENGAGE_MAX,
          f"(engage={engage:.1f} mm, band {ENGAGE_MIN}-{ENGAGE_MAX})")

    # --- 4. bean bore clear + adequate ---
    tip_y = bb.ymax - 2.0
    mid_y = (TRANSITION_Y + bb.ymax) / 2.0
    centers_hollow = all(
        not radius_present(new, 3.0, y)
        for y in [FEEDER_FACE_Y + 2, -70, -62, mid_y, tip_y]
    )
    check("bean bore clear end-to-end", centers_hollow,
          "(center hollow along full length)")
    bore = inner_bore_dia_at(new, mid_y)
    check("plug bore >= minimum",
          bore is not None and bore >= MIN_BEAN_BORE - 1,
          f"(bore~={bore})")

    n_fail = sum(1 for _, ok, _ in results if not ok)
    print(f"\n{len(results)-n_fail}/{len(results)} checks passed.")
    sys.exit(1 if n_fail else 0)


if __name__ == "__main__":
    main()
