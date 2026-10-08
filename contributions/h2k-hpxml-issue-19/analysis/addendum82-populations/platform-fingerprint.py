from collections import defaultdict
from statistics import median, mean

from run import (
    A82,
    base_population,
    metrics,
    number,
    read_hp_rows,
)

DUCT = "Multizone All Non-Ducted"

# These names are ONLY used after scoring to inspect whether
# the blind performance detector rediscovered known lineage.
MIDEA_ANCHORS = {
    "M2OA-18HFN1-M",
    "M3OJ-27HFN1-M",
    "M4OG-36HFN1-M",
    "M5OG-48HFN1-M",
}

EXPECTED_CALIBRATION = {
    "A2OA-18HFN1-M",
    "A3OJ-27HFN1-M",
    "A4OG-36HFN1-M",
    "A5OG-48HFN1-M",

    "ODUM2OA-18HFN1-M",
    "ODUM3OJ-27HFN1-M",
    "ODUM4OG-36HFN1-M",
    "ODUM5OG-48HFN1-M",
}


def txt(v):
    return str(v or "").strip()


def cap(r):
    return number(r["Rated Capacity 47°F⁺"])


def pct_distance(a, b):
    denom = max(abs(a), abs(b), 1e-9)
    return abs(a - b) / denom


# ---------------------------------------------------------
# Build a completely brand/model-blind performance signature
# for each outdoor model.
#
# Multiple AHRI/indoor combinations can exist for one outdoor
# unit. Median is deliberately used so one indoor combination
# does not dominate the platform signature.
# ---------------------------------------------------------

rows = [
    r
    for r in base_population(read_hp_rows())
    if r["Ducting Configuration"] == DUCT
    and r["ENERGY STAR Cold Climate Certified"] is False
    and cap(r) is not None
    and all(
        v is not None
        for v in metrics(r).values()
    )
]

groups = defaultdict(list)

for r in rows:
    brand = txt(r.get("Brand Name"))
    model = txt(r.get("Outdoor Unit Model Number⁺"))

    if not model:
        continue

    # Brand remains part of identity so two branded versions
    # with the same model text remain separately observable.
    groups[(brand, model)].append(r)


def signature(rs):
    caps = [cap(r) for r in rs]

    curve = {
        k: median(
            metrics(r)[k]
            for r in rs
        )
        for k in A82
    }

    return {
        "capacity": median(caps),
        "curve": curve,
    }


units = []

for (brand, model), rs in groups.items():
    units.append({
        "brand": brand,
        "model": model,
        "series": " | ".join(sorted({
            txt(r.get("Series Name"))
            for r in rs
            if txt(r.get("Series Name"))
        })),
        "rows": len(rs),
        "signature": signature(rs),
    })


# ---------------------------------------------------------
# Blind similarity:
#
# capacity_delta:
#   just prevents comparing an 18k machine with a 48k machine.
#
# curve_delta:
#   mean distance across all 15 Addendum-normalized dimensions.
#
# IMPORTANT:
# names do not participate in either calculation.
# ---------------------------------------------------------

def compare(a, b):
    sa = a["signature"]
    sb = b["signature"]

    capacity_delta = pct_distance(
        sa["capacity"],
        sb["capacity"],
    )

    deltas = {
        k: pct_distance(
            sa["curve"][k],
            sb["curve"][k],
        )
        for k in A82
    }

    curve_delta = mean(deltas.values())
    max_delta = max(deltas.values())

    return {
        "capacity_delta": capacity_delta,
        "curve_delta": curve_delta,
        "max_delta": max_delta,
        "deltas": deltas,
    }


print("rows:", len(rows))
print("unique branded outdoor models:", len(units))

print()
print("=" * 110)
print("BLIND CALIBRATION AGAINST KNOWN MIDEA OEM ANCHORS")
print("=" * 110)

anchors = [
    u for u in units
    if u["model"] in MIDEA_ANCHORS
]

print("anchors found:", len(anchors))


for anchor in sorted(
    anchors,
    key=lambda u: u["signature"]["capacity"],
):
    print()
    print(
        f"ANCHOR: {anchor['brand']} :: {anchor['model']} "
        f"cap={anchor['signature']['capacity']:.0f} "
        f"N={anchor['rows']}"
    )

    candidates = []

    for candidate in units:

        if candidate is anchor:
            continue

        c = compare(anchor, candidate)

        # Only compare plausibly equivalent capacity classes.
        if c["capacity_delta"] > 0.08:
            continue

        candidates.append(
            (
                c["curve_delta"],
                c["max_delta"],
                c["capacity_delta"],
                candidate,
            )
        )

    candidates.sort(
        key=lambda x: (
            x[0],
            x[1],
            x[2],
        )
    )

    print(
        f"{'rank':>4} "
        f"{'curveΔ':>8} "
        f"{'maxΔ':>8} "
        f"{'capΔ':>7} "
        f"{'cap47':>8} "
        f"{'N':>3}  "
        f"{'brand':<24} "
        f"model"
    )

    for rank, (
        curve_d,
        max_d,
        cap_d,
        u,
    ) in enumerate(candidates[:15], 1):

        expected = (
            "  <-- EXPECTED"
            if u["model"] in EXPECTED_CALIBRATION
            else ""
        )

        print(
            f"{rank:4} "
            f"{curve_d:8.3%} "
            f"{max_d:8.3%} "
            f"{cap_d:7.2%} "
            f"{u['signature']['capacity']:8.0f} "
            f"{u['rows']:3}  "
            f"{u['brand']:<24} "
            f"{u['model']}"
            f"{expected}"
        )


# ---------------------------------------------------------
# Global discovery:
#
# Cross-brand only.
#
# STRICT candidates:
#   <= 1% mean difference over the entire 15-D curve
#   <= 3% capacity difference
#
# VERY STRICT:
#   <= .25% curve difference
#
# These are candidate shared platforms, NOT automatically
# asserted OEM identity.
# ---------------------------------------------------------

print()
print("=" * 110)
print("GLOBAL CROSS-BRAND PLATFORM CANDIDATES")
print("=" * 110)

pairs = []

for i, a in enumerate(units):
    for b in units[i + 1:]:

        if a["brand"].casefold() == b["brand"].casefold():
            continue

        c = compare(a, b)

        if c["capacity_delta"] > 0.03:
            continue

        if c["curve_delta"] > 0.01:
            continue

        pairs.append(
            (
                c["curve_delta"],
                c["max_delta"],
                c["capacity_delta"],
                a,
                b,
            )
        )


pairs.sort(
    key=lambda x: (
        x[0],
        x[1],
        x[2],
    )
)

print("candidate pairs:", len(pairs))
print()

for (
    curve_d,
    max_d,
    cap_d,
    a,
    b,
) in pairs[:100]:

    strength = (
        "VERY_STRONG"
        if curve_d <= 0.0025
        else "STRONG"
    )

    print(
        f"{strength:<11} "
        f"curve={curve_d:7.3%} "
        f"max={max_d:7.3%} "
        f"cap={cap_d:6.2%}"
    )

    print(
        f"   A  "
        f"{a['brand']} :: {a['model']} "
        f"[{a['signature']['capacity']:.0f} Btu/h, "
        f"N={a['rows']}]"
    )

    print(
        f"   B  "
        f"{b['brand']} :: {b['model']} "
        f"[{b['signature']['capacity']:.0f} Btu/h, "
        f"N={b['rows']}]"
    )

    print()


# ---------------------------------------------------------
# Calibration score:
# how many known AC Pro / Kepler candidates are found among
# the top-15 neighbors of the appropriate Midea anchors?
# ---------------------------------------------------------

print()
print("=" * 110)
print("CALIBRATION SUMMARY")
print("=" * 110)

hits = []
misses = []

for expected_model in sorted(EXPECTED_CALIBRATION):

    expected = next(
        (
            u for u in units
            if u["model"] == expected_model
        ),
        None,
    )

    if expected is None:
        misses.append(
            (expected_model, "not present")
        )
        continue

    best_anchor = None
    best_cmp = None

    for anchor in anchors:

        c = compare(anchor, expected)

        if c["capacity_delta"] > 0.08:
            continue

        if (
            best_cmp is None
            or c["curve_delta"]
            < best_cmp["curve_delta"]
        ):
            best_anchor = anchor
            best_cmp = c

    if best_cmp is None:
        misses.append(
            (expected_model, "no compatible anchor")
        )
        continue

    hits.append(
        (
            expected_model,
            best_anchor["model"],
            best_cmp,
        )
    )


for model, anchor, c in hits:
    print(
        f"{model:<24} "
        f"vs {anchor:<18} "
        f"curve={c['curve_delta']:.3%} "
        f"max={c['max_delta']:.3%} "
        f"cap={c['capacity_delta']:.2%}"
    )

for model, reason in misses:
    print(
        f"{model:<24} "
        f"MISS: {reason}"
    )
