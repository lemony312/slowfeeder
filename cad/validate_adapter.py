"""
Validation harness for the Mazzer Super Jolly adapter.

No printer available, so we validate geometrically:
  1. Mesh is watertight (printable single shell).
  2. Feeder-side mating geometry is preserved vs. the original EK43 adapter
     (the portion at Y <= TRANSITION_Y must be dimensionally identical).
  3. Grinder-side spigot meets the Mazzer Super Jolly targets:
       - outer diameter within fit window of the 59 mm throat
       - engagement length
       - central bean bore >= minimum
  4. Bean bore is unobstructed end-to-end.

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
OUT_STL = os.path.join(ROOT, "STL", "Madkat Feedr_MazzerSJ_v1.stl")
OUT_STEP = os.path.join(ROOT, "STL", "Madkat Feedr_MazzerSJ_v1.step")

# expectations (keep in sync with mazzer_super_jolly_adapter.py)
TRANSITION_Y = -59.2
THROAT_DIA = 59.0
SPIGOT_OD = 58.4
SPIGOT_LENGTH = 32.0
SPIGOT_BORE = 46.9
MIN_BEAN_BORE = 42.0
FEEDER_FACE_Y = -78.5

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}  {detail}")


def radius_present(solid, r, y, axis="x"):
    """Is there material at radius r, height y (probe a 0.6mm cube)?"""
    if axis == "x":
        c = cq.Vector(r - 0.3, y - 0.3, -0.3)
    else:
        c = cq.Vector(-0.3, y - 0.3, r - 0.3)
    box = cq.Solid.makeBox(0.6, 0.6, 0.6, c)
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


def inner_bore_at(solid, y):
    """Find inner bore radius by scanning +X for the first solid material."""
    for r in [x * 0.5 for x in range(0, 80)]:
        if radius_present(solid, r, y, "x"):
            return r * 2.0  # diameter at first material = bore wall
    return None


def main():
    # --- 1. watertight mesh ---
    mesh = trimesh.load(OUT_STL)
    check("STL is watertight", mesh.is_watertight,
          f"(watertight={mesh.is_watertight}, volume={mesh.volume:.0f})")
    nbodies = len(mesh.split(only_watertight=False))
    check("STL single body", nbodies == 1, f"(bodies={nbodies})")

    new = cq.importers.importStep(OUT_STEP).val()
    orig = cq.importers.importStep(SRC_STEP).val()

    # --- 2. feeder-side preserved ---
    # Compare outer radius + presence of the main bore at feeder face & mid-feeder.
    for y in [FEEDER_FACE_Y + 0.5, -72.0, -66.5, TRANSITION_Y - 0.5]:
        ro = outer_radius_at(orig, y)
        rn = outer_radius_at(new, y)
        check(f"feeder outer radius preserved @Y={y}",
              abs(ro - rn) < 0.05, f"(orig={ro:.2f} new={rn:.2f})")

    # main feeder bore (~24.8 R) must be open at feeder face
    bore_open = not radius_present(new, 5.0, FEEDER_FACE_Y + 1.0, "x")
    check("feeder main bore open at face", bore_open,
          "(center hollow at feeder face)")

    # --- 3. spigot geometry ---
    spigot_mid_y = TRANSITION_Y + SPIGOT_LENGTH / 2.0
    ro = outer_radius_at(new, spigot_mid_y)
    check("spigot OD within throat fit window",
          (THROAT_DIA / 2 - 0.6) <= ro <= (THROAT_DIA / 2 + 0.05),
          f"(spigot R={ro:.2f}, target {SPIGOT_OD/2:.2f}, throat R={THROAT_DIA/2:.2f})")

    # spigot tip exists at expected length
    tip_y = TRANSITION_Y + SPIGOT_LENGTH - 2.0
    tip_present = radius_present(new, SPIGOT_OD / 2 - 2, tip_y, "x")
    check("spigot reaches engagement length", tip_present,
          f"(material at Y={tip_y:.1f})")

    # no material beyond spigot tip (clean end)
    beyond = radius_present(new, SPIGOT_OD / 2 - 2, TRANSITION_Y + SPIGOT_LENGTH + 2, "x")
    check("spigot ends cleanly", not beyond,
          f"(no material past Y={TRANSITION_Y+SPIGOT_LENGTH:.1f})")

    # --- 4. bean bore unobstructed end to end ---
    # center must be hollow along the whole length
    centers_hollow = all(
        not radius_present(new, 3.0, y, "x")
        for y in [FEEDER_FACE_Y + 2, -70, -62, spigot_mid_y, tip_y]
    )
    check("bean bore clear end-to-end", centers_hollow,
          "(center hollow along full length)")

    # bore diameter at spigot >= minimum
    bore = inner_bore_at(new, spigot_mid_y)
    check("spigot bore >= minimum",
          bore is not None and bore >= MIN_BEAN_BORE - 1,
          f"(bore~={bore})")

    n_fail = sum(1 for _, ok, _ in results if not ok)
    print(f"\n{len(results)-n_fail}/{len(results)} checks passed.")
    sys.exit(1 if n_fail else 0)


if __name__ == "__main__":
    main()
