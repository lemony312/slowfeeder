"""
Validation harness for the Mazzer Super Jolly adapter (v4, correct orientation).

Orientation: the BODY side (flange + 3 screw holes, Y >= TRANSITION_Y) is preserved
verbatim from the EK43 adapter; only the GRINDER tube (Y <= TRANSITION_Y) is reshaped
into a plug for the Mazzer collar.

No printer available, so we validate geometrically:
  1. Mesh is watertight + single body + winding-consistent (printable shell).
  2. BODY side preserved vs. original EK43:
       - outer profile identical at several Y planes
       - all 3 mounting screw holes still present
  3. GRINDER plug fits the Mazzer collar:
       - plug OD within the friction-fit window of the ~59 mm collar
       - a seating shoulder (OD step) exists at the cut
       - clean cylinder (not a bellows): OD ~constant apart from small beads
       - insertion length in the expected band
  4. Bean bore unobstructed end-to-end and >= minimum.

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
OUT_STL = os.path.join(ROOT, "STL", "Madkat Feedr_MazzerSJ_v4.stl")
OUT_STEP = os.path.join(ROOT, "STL", "Madkat Feedr_MazzerSJ_v4.step")

# expectations (keep in sync with mazzer_super_jolly_adapter.py)
TRANSITION_Y = -59.2
THROAT_DIA = 59.0
PLUG_OD = 58.4
SHOULDER_OD = 62.0
BEAD_HEIGHT = 0.4
MIN_BEAN_BORE = 35.0
FLANGE_FACE_Y = -48.5
SCREW_HOLES = [(27.331, 20.224), (0.0, -34.0), (-33.871, 2.963)]
ENGAGE_MIN, ENGAGE_MAX = 20.0, 30.0

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}  {detail}")


def solid_at(solid, x, y, z, sz=1.0):
    box = cq.Solid.makeBox(sz, sz, sz, cq.Vector(x - sz / 2, y - sz / 2, z - sz / 2))
    try:
        return solid.intersect(box).Volume() > 1e-3
    except Exception:
        return False


def radius_present(solid, r, y):
    return solid_at(solid, r, y, 0.0, sz=0.6)


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

    # --- 2. BODY side preserved (flange + screws) ---
    for y in [FLANGE_FACE_Y - 0.5, -52.0, -55.0, TRANSITION_Y + 0.5]:
        ro = outer_radius_at(orig, y)
        rn = outer_radius_at(new, y)
        check(f"body outer profile preserved @Y={y}",
              abs(ro - rn) < 0.05, f"(orig={ro:.2f} new={rn:.2f})")
    for (x, z) in SCREW_HOLES:
        present = (not solid_at(new, x, -50.0, z)) and (not solid_at(new, x, -55.0, z))
        check(f"screw hole preserved @XZ=({x:.1f},{z:.1f})", present, "")

    # --- 3. GRINDER plug fits the Mazzer collar ---
    bb = new.BoundingBox()
    tip_y = bb.ymin
    # sample plug body between the shoulder and the tip (skip shoulder + chamfer)
    ys = [TRANSITION_Y - 4 - 0.5 * i for i in range(0, 60)]
    ys = [y for y in ys if y > tip_y + 3.0]
    radii = [outer_radius_at(new, y) for y in ys]
    max_od = max(radii) * 2
    body_od = sorted(radii)[len(radii) // 2] * 2

    check("plug fits collar (OD within friction window)",
          (THROAT_DIA - 1.2) <= body_od <= THROAT_DIA,
          f"(body OD={body_od:.2f}, collar={THROAT_DIA})")
    check("beads do not exceed collar",
          max_od <= THROAT_DIA + 0.2,
          f"(max OD inc. beads={max_od:.2f})")
    od_swing = (max(radii) - min(radii)) * 2
    check("plug is a clean cylinder (not a bellows)",
          od_swing <= 2.0,
          f"(OD swing along body={od_swing:.2f} mm, beads ~{2*BEAD_HEIGHT})")

    # seating shoulder: OD right at the cut should exceed the collar (rests on it),
    # then step down to the plug OD just below. Probe at the cut plane itself.
    shoulder_od = outer_radius_at(new, TRANSITION_Y + 0.1) * 2
    check("seating shoulder present at cut",
          shoulder_od >= THROAT_DIA + 1.0,
          f"(shoulder OD={shoulder_od:.2f} > collar {THROAT_DIA})")

    engage = TRANSITION_Y - tip_y
    check("insertion length in band",
          ENGAGE_MIN <= engage <= ENGAGE_MAX,
          f"(insert={engage:.1f} mm, band {ENGAGE_MIN}-{ENGAGE_MAX})")

    # --- 4. bean bore clear + adequate ---
    mid_y = (TRANSITION_Y + tip_y) / 2.0
    centers_hollow = all(
        not radius_present(new, 3.0, y)
        for y in [FLANGE_FACE_Y - 1, -55, -62, mid_y, tip_y + 2]
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
