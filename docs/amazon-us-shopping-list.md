# Madkat Feedr — Amazon US shopping list (non-printed parts)

Pre-built Amazon **US** (amazon.com) search links for every off-the-shelf part in
`BOM/Madkat Feedr - BOM.csv`. Click each link to open Amazon already searching for
that part. Fitment criteria (verified against the STL geometry) are baked into each
search term so you buy parts that actually fit.

> **Tip:** open them all at once — most browsers let you middle-click (or Ctrl/Cmd-click)
> each link to open it in a new tab.

---

## Critical fitment criteria (measured from the models)

| Part | Hard constraint | Why |
|---|---|---|
| N20 motor | **3 mm shaft**, wire leads attached | Hub bore is ~3.1 mm; motor pocket is 12.9 × 10.8 mm (standard N20) |
| Switch | **12 mm threaded bushing** | Molded opening is ~11–13 mm round |
| Battery holder | **2×AA, ≤14 mm thick, with leads** | Battery cavity is ~13.5 mm thick |
| Magnets | **exactly 5 mm diameter** | Pockets are 5 mm Ø (8 mm length & grade non-critical) |
| Screws | M3 × 20 mm countersunk | per BOM |

---

## 🛒 Pinned products (direct Amazon links)

Amazon retired the old one-click "add all to cart" URL (it now throws "something
went wrong"), so open each product page directly and click **Add to Cart** — you'll
also see the live price/stock while you're there.

| # | Part | ASIN | Direct link |
|---|---|---|---|
| 1 | N20 gear motor (3-pack) | `B09DG3GCGK` | https://www.amazon.com/dp/B09DG3GCGK |
| 2 | M3×20 countersunk screws (100pk) | `B015A38FUS` | https://www.amazon.com/dp/B015A38FUS |
| 3 | M3 hex nuts (100pk) | `B01J35WBBI` | https://www.amazon.com/dp/B01J35WBBI |
| 4 | 12mm latching switch (12pk) | `B0927153HN` | https://www.amazon.com/dp/B0927153HN |
| 5 | 2×AA battery holder w/ leads | `B09V7Z4MT7` | https://www.amazon.com/dp/B09V7Z4MT7 |
| 6 | Wago 221-412 lever nuts | `B01AIC8LZU` | https://www.amazon.com/dp/B01AIC8LZU |
| 7 | 5mm neodymium magnets (20pk) | `B0D3F13DDX` | https://www.amazon.com/dp/B0D3F13DDX |

> Prices/stock were *not* machine-verified (Amazon blocks automated reads). If a page
> is dead or out of stock, use the matching search link below to find a replacement.
>
> **Fitment flags to double-check:** motor shaft = 3 mm & wires attached (#1);
> battery holder ≤14 mm thick (#5); magnets exactly 5 mm diameter (#7).

---

## Shopping links (Amazon US)

### 1. N20 gear motor with wires — qty 1
*Need: 3–6 V, 3 mm shaft, wire leads pre-attached. **Low RPM — aim for ~50–60 RPM (at 6 V).***

> The BOM motor (XIITIA B0DZNRRTB1) is rated **~52 RPM @ 3 V / ~104 RPM @ 6 V**. This is a
> fixed-speed, ON/OFF feeder run directly off 2×AA (~3 V) with **no speed controller** — the
> rotor sits straight on the motor hub, so motor RPM *is* feed-wheel RPM. If a generic N20
> listing offers an RPM menu, pick the **~50–60 RPM (≈200:1)** option; avoid the fast
> 100–300 RPM variants (you can't dial them back). Feed rate is fine-tuned via swappable rotors, not speed.

https://www.amazon.com/s?k=N20+gear+motor+3V-6V+with+wires+3mm+shaft

### 2. M3 × 20 mm countersunk screws — qty 3
https://www.amazon.com/s?k=M3+x+20mm+countersunk+flat+head+machine+screws

### 3. M3 nuts — qty 3
https://www.amazon.com/s?k=M3+hex+nuts+stainless

### 4. ON/OFF switch — qty 1
*Need: 12 mm threaded-bushing pushbutton (latching / self-locking ON-OFF).*

https://www.amazon.com/s?k=12mm+push+button+switch+latching+SPST+self-locking

### 5. Battery holder (2×AA) — qty 1
*Need: slim, ≤14 mm thick, with wire leads.*

https://www.amazon.com/s?k=2+AA+battery+holder+with+wire+leads+slim

### 6. Wire splice connector — qty 1
*No fitment constraint — any lever-nut works.*

https://www.amazon.com/s?k=Wago+221-412+lever+nut+connector

### 7. Magnets — qty 6
*Need: exactly 5 mm diameter neodymium cylinder.*

https://www.amazon.com/s?k=5mm+x+8mm+neodymium+cylinder+magnet

---

## Quantity / pack notes

Most of these sell only in multipacks, so one order covers many builds:

- Screws/nuts come in 50–100 packs.
- Magnets typically come in packs of 10–50 (buy 6+).
- N20 motors often come in 2–5 packs.
- Wago connectors come in packs of 10+.

Estimated single Amazon US order total: **~$57** (mostly leftover stock; true
per-feeder material cost is ~$15–20).

---

## Parts NOT on Amazon (genuine versions)

The BOM originally specs two manufacturer parts that Amazon doesn't carry. The
search links above substitute **dimension-matched generics**. If you want the exact
original parts instead, get them from Digikey (single-unit, verified):

- **Switch** — Judco 40-4526-00 → Digikey 545PB-ND (~$2.51)
  https://www.digikey.com/en/products/detail/judco-manufacturing-inc/40-4526-00/545PB-ND
- **Battery holder** — Keystone 2463 (~$1.36)
  https://www.digikey.com/en/products/detail/keystone-electronics/2463/303812
