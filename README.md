# Madkat Feedr - A 3D printable and solder-free DIY slow feeder by Madkat Coffee

Free to download, 3d print and build, battery-powered slow feeder for coffee grinders

A simple, fast-to-build slow feeder to help you test and experience the impact of controlled bean feeding on grind consistency and extraction.

This project is intended as a learning and experimentation tool.
If you want a set-and-forget, variable-speed, daily-use version, see the metal upgrade at www.madkatcoffee.com.

## Why slow feeding?

Slow feeding:

Reduces fines generation

Reduces heat generation

Improves shot to shot consistency with a motorized feeder

## Many users report:

Improved clarity

Better flavour separation

Improved aroma

This DIY design exists so you can try it yourself.

## What this is (and isn’t)

### This is:

A simple ON/OFF slow feeder

Battery powered (2× AA)

Easy to print and assemble

Includes separate cassette wheels for feed speed reduction.

Designed to work with adapters that can be modified to suit your grinder. The included EK43 adapter has been included as a step file so you can modify/remix as you need to suit your grinder.

### This is not:

A variable speed feeder

A finished product


## Build overview

Build time: ~30–45 minutes

Print time: ~12 hours (depends on printer)

## Required tools

3D printer

Small screwdrivers

Wire strippers (to strip ends of wires)

## Files included

/STL/ – Printable parts (core assembly provided as STL)

/BOM/ – Bill of materials with sourcing notes

/Assembly/ – Step-by-step build instructions (PDF)

/cad/ – Parametric CadQuery scripts for grinder adapter variants

/docs/ – Dimension references for adapter variants

## Grinder adapter variants

The slow-feeder body is grinder-agnostic; only the **adapter** is grinder-specific.
The original `Madkat Feedr_EK43_v5` adapter fits an EK43. This fork adds a variant for
the **Mazzer Super Jolly**:

| Variant | Files | Notes |
|---|---|---|
| EK43 (original) | `STL/Madkat Feedr_EK43_v5.step`, `STL/Madkat Feedr_EK43 v5.stl` | Bolt-on flange |
| Mazzer Super Jolly | `STL/Madkat Feedr_MazzerSJ_v4.step`, `STL/Madkat Feedr_MazzerSJ_v4.stl` | Clean connector with a friction-fit plug into the ~59 mm throat collar |

### How the Mazzer variant was made

`cad/mazzer_super_jolly_adapter.py` imports the original EK43 STEP solid and keeps the
**body side verbatim** — the wide flange with the **3 screw holes that bolt the adapter
to the rest of the feeder** — so the part still mounts to the feeder exactly as the EK43
one does. It then reshapes **only the grinder tube** (the narrow end that inserts into the
grinder) into a friction-fit **plug** for the Super Jolly throat collar. Like the EK43,
it's a **clean cylindrical connector** — the grinder end is a smooth ⌀58.4 mm plug (into
the ~59 mm collar, confirmed against the proven Thingiverse #4758610 funnel) with a
seating shoulder, a tip lead-in chamfer, and two low-profile retention beads. The fit is
set by the single parameter `PLUG_OD`.

```sh
python3.12 -m venv .venv
.venv/bin/pip install cadquery trimesh scipy
.venv/bin/python cad/mazzer_super_jolly_adapter.py   # rebuild STEP + STL
.venv/bin/python cad/validate_adapter.py             # geometric checks
```

> ⚠️ **Test-fit recommended.** The Mazzer spigot is measured from the proven Thingiverse
> #4758610 funnel (a part known to fit a real Super Jolly), so it should fit — but it has
> not been verified against caliper measurements of *every* unit. Treat the first print as
> a test fit. To adjust the grip, change `PLUG_OD` in the
> script and re-run. See `docs/mazzer-super-jolly-dimensions.md`.

## You are free to:

Print

Build

Share

Remix

## Licensing

Core assembly: provided as-is for personal use

Funnels: open for remixing and sharing

## Known limitations

Fixed feed rate but can change with modified rotors.

Print quality matters (poor tolerances can cause fit issues)

Not designed for high-throughput or commercial use

For our variable speed product, you can find updates and availability at https://madkatcoffee.com


## Final note

This project exists because slow feeding has become a key part of our daily process for unlocking next level flavour and we want more people to experience it.

If you build one:

Post it on Instagram

Tag @madkatcoffee

We’ll feature the best builds and use community feedback to improve future designs.

Sign up to our newletter at www.madkatcoffee.com to be the first to hear about more community projects.

Remember, if you're making coffee at home you're already winning. So have fun with this build! Slow feeding is at the deeper end of the rabbit hole but the flavour improvement has been proven and confirmed by many leading coffee experts including Lance Hedrick, James Hoffman and Matt Perger at Barista Hustle.
 
Build it. Test it. Break it. Have fun with it!

—

Madkat Coffee
