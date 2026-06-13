"""
Validation harness for the Mazzer Super Jolly adapter (v2, ribbed spigot).

No printer available, so we validate geometrically:
  1. Mesh is watertight + single body (printable shell).
  2. Feeder-side mating geometry is preserved vs. the original EK43 adapter
     (the portion at Y <= TRANSITION_Y must be dimensionally identical).
  3. Grinder-side ribbed spigot meets the Mazzer Super Jolly targets, derived
     from the proven Thingiverse #4758610 funnel:
       - max rib crown OD ~= throat dia (light interference, must not exceed it much)
       - valleys sit inside the throat (air bleed / rib room)
       - taper present (bottom crown < top crown -> self-centring)
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
OUT_STL = os.path.join(ROOT, "STL", "Madkat Feedr_MazzerSJ_v2.stl")
OUT_STEP = os.path.join(ROOT, "STL", "Madkat Feedr_MazzerSJ_v2.step")

# expectations (keep in sync with mazzer_super_jolly_adapter.py)
TRANSITION_Y = -59.2
THROAT_DIA = 59.0
CROWN_OD_TOP = 59.0
CROWN_OD_BOT = 54.5
MIN_BEAN_BORE = 35.0
FEEDER_FACE_Y = -78.5
ENGAGE_MIN, ENGAGE_MAX = 30.0, 45.0   # acceptable spigot engagement length band

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}  {detail}")


def radius_present(solid, r, y):
    """Is there material at radius r (+X), height y? Probe a 0.6mm cube."""
    box = cq.Solid.makeBox(0.6, 0.6, 0.6, cq.Vector(r - 0.3, y - 0.3, -0.3))
    try:
        return solid.intersect(box).Volume() > 1e-3
    except Exception:
        return False


def outer_radius_at(solid, y):
    """Approx outer radius via a thin slab section bbox."""
    slab = cq.Solid.makeBox(400, 0.4, 400, cq.Vector(-200, y - 0.2, -200))
    sec = solid.intersect(slab)
    bb = sec.BoundingBox()
    return max(abs(bb.xmin), abs(bb.xmax), abs(bb.zmin), abs(bb.zmax))


def inner_bore_dia_at(solid, y):
    """Scan +X for first solid material -> inner bore diameter."""
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

    # --- 3. ribbed spigot vs Mazzer throat ---
    # Scan the grinder side (Y > transition) for the max outer radius = top crown.
    bb = new.BoundingBox()
    spigot_ys = [TRANSITION_Y + 0.5 + i * 0.5 for i in range(0, 120)]
    spigot_ys = [y for y in spigot_ys if y < bb.ymax - 0.5]
    radii = [(y, outer_radius_at(new, y)) for y in spigot_ys]
    max_r = max(r for _, r in radii)
    check("max rib crown <= throat (seats, light interference)",
          max_r * 2 <= THROAT_DIA + 0.3,
          f"(max crown OD={max_r*2:.2f}, throat={THROAT_DIA})")
    check("max rib crown reaches throat (actually grips)",
          max_r * 2 >= THROAT_DIA - 1.5,
          f"(max crown OD={max_r*2:.2f})")

    # taper: top crown (near transition) larger than bottom crown (near tip)
    top_region = max(r for y, r in radii if y <= TRANSITION_Y + 12)
    bot_region = max(r for y, r in radii if y >= TRANSITION_Y + 20)
    check("spigot tapers (self-centring): top crown > bottom crown",
          top_region > bot_region + 0.5,
          f"(top={top_region*2:.2f} bottom={bot_region*2:.2f})")

    # ribs present: outer radius varies (crowns vs valleys), not a flat cylinder
    rr = [r for _, r in radii]
    check("ribs present (OD varies along spigot)",
          (max(rr) - min(rr)) > 1.5,
          f"(OD swing={2*(max(rr)-min(rr)):.2f} mm)")

    # engagement length: span of grinder-side material
    engage = bb.ymax - TRANSITION_Y
    check("engagement length in band",
          ENGAGE_MIN <= engage <= ENGAGE_MAX,
          f"(engage={engage:.1f} mm, band {ENGAGE_MIN}-{ENGAGE_MAX})")

    # --- 4. bean bore clear + adequate ---
    tip_y = bb.ymax - 3.0
    mid_y = (TRANSITION_Y + bb.ymax) / 2.0
    centers_hollow = all(
        not radius_present(new, 3.0, y)
        for y in [FEEDER_FACE_Y + 2, -70, -62, mid_y, tip_y]
    )
    check("bean bore clear end-to-end", centers_hollow,
          "(center hollow along full length)")
    bore = inner_bore_dia_at(new, mid_y)
    check("spigot bore >= minimum",
          bore is not None and bore >= MIN_BEAN_BORE - 1,
          f"(bore~={bore})")

    n_fail = sum(1 for _, ok, _ in results if not ok)
    print(f"\n{len(results)-n_fail}/{len(results)} checks passed.")
    sys.exit(1 if n_fail else 0)


if __name__ == "__main__":
    main()
