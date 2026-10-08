from collections import defaultdict
from statistics import mean

from run import (
    A82,
    PopulationSpec,
    base_population,
    evaluate,
    identity_key,
    metrics,
    number,
    read_hp_rows,
)

DUCT = "Singlezone Non-Ducted, Ceiling Placement"


def txt(v):
    return str(v or "").strip()


def cap(r):
    return number(r["Rated Capacity 47°F⁺"])


# ---------------------------------------------------------
# Original best-population semantics
# ---------------------------------------------------------

rows = [
    r for r in base_population(read_hp_rows())
    if r["Ducting Configuration"] == DUCT
    and r["ENERGY STAR Cold Climate Certified"] is False
    and cap(r) is not None
    and cap(r) >= 18000
    and all(
        v is not None
        for v in metrics(r).values()
    )
]


# ---------------------------------------------------------
# First collapse ordinary duplicate listings:
# one Brand + Outdoor Unit identity.
# This reproduces our previous "outdoor" weighting.
# ---------------------------------------------------------

seen = set()
outdoors = []

for i, r in enumerate(rows):
    key = identity_key(r, "outdoor", i)

    if key in seen:
        continue

    seen.add(key)
    outdoors.append(r)


# ---------------------------------------------------------
# Identify raw performance fields.
#
# No brand/model/series/AHRI identity participates.
# ---------------------------------------------------------

def performance_field(name):
    s = name.casefold()

    wanted = (
        "capacity",
        "power",
        "cop",
        "seer2",
        "hspf2",
        "eer2",
    )

    forbidden = (
        "model",
        "brand",
        "manufacturer",
        "ahri",
        "series",
        "date",
    )

    return (
        any(x in s for x in wanted)
        and not any(x in s for x in forbidden)
    )


all_fields = sorted({
    field
    for r in outdoors
    for field in r.keys()
})

RAW_FIELDS = [
    field
    for field in all_fields
    if performance_field(field)
    and sum(
        number(r.get(field)) is not None
        for r in outdoors
    ) >= 30
]


# ---------------------------------------------------------
# EXACT submitted-performance fingerprint.
#
# This does NOT mean "proven same OEM".
#
# It means:
# after brand/outdoor dedupe, these marketed outdoor units
# still report exactly the same numerical performance surface.
# ---------------------------------------------------------

def fingerprint(r):
    values = []

    for field in RAW_FIELDS:
        value = number(r.get(field))

        values.append(
            None
            if value is None
            else float(value)
        )

    return tuple(values)


by_fp = defaultdict(list)

for r in outdoors:
    by_fp[fingerprint(r)].append(r)


# One representative per exact numerical fingerprint.
collapsed = [
    group[0]
    for group in by_fp.values()
]


# ---------------------------------------------------------
# Evaluate Addendum fit.
# ---------------------------------------------------------

def run_eval(name, population):
    result = evaluate(
        population,
        PopulationSpec(
            name=name,
            complete_metrics=True,
            dedupe="none",
        ),
    )

    errors = [
        m["relativeError"]
        for m in result["metrics"].values()
        if m["relativeError"] is not None
    ]

    return {
        "name": name,
        "rows": len(population),
        "score": result["score"],
        "max": max(errors),
        "result": result,
    }


baseline = run_eval(
    "outdoor-weighted",
    outdoors,
)

exact = run_eval(
    "exact-performance-collapse",
    collapsed,
)


print("=" * 100)
print("POPULATION")
print("=" * 100)

print("raw selected rows:               ", len(rows))
print("unique branded outdoor units:    ", len(outdoors))
print("exact performance fingerprints:  ", len(collapsed))
print("raw performance fields compared: ", len(RAW_FIELDS))


duplicate_groups = [
    group
    for group in by_fp.values()
    if len(group) > 1
]

duplicate_units = sum(
    len(group) - 1
    for group in duplicate_groups
)

print("multi-unit clone groups:         ", len(duplicate_groups))
print("extra votes removed:             ", duplicate_units)


print()
print("=" * 100)
print("ADDENDUM 82 FIT")
print("=" * 100)

for x in (baseline, exact):
    print(
        f"{x['name']:<30} "
        f"N={x['rows']:>4} "
        f"score={x['score']:.3%} "
        f"max={x['max']:.2%}"
    )


print()
print("=" * 100)
print("COEFFICIENT CHANGE AFTER EXACT-CLONE COLLAPSE")
print("=" * 100)

print(
    f"{'metric':<13} "
    f"{'A82':>8} "
    f"{'outdoor':>10} "
    f"{'collapsed':>10} "
    f"{'shift':>9}"
)

shifts = []

for key, target in A82.items():

    a = baseline["result"]["metrics"][key]["mean"]
    b = exact["result"]["metrics"][key]["mean"]

    shift = (
        (b - a) / abs(a)
        if a
        else 0
    )

    shifts.append(
        abs(shift)
    )

    print(
        f"{key:<13} "
        f"{target:>8.3f} "
        f"{a:>10.3f} "
        f"{b:>10.3f} "
        f"{shift:>+8.2%}"
    )


print()
print(
    "mean absolute coefficient shift:",
    f"{mean(shifts):.3%}",
)

print(
    "max coefficient shift:",
    f"{max(shifts):.3%}",
)


# ---------------------------------------------------------
# Show biggest clone groups so we can inspect what
# actually received duplicate statistical weight.
# ---------------------------------------------------------

print()
print("=" * 100)
print("LARGEST EXACT PERFORMANCE-CLONE GROUPS")
print("=" * 100)

for group in sorted(
    duplicate_groups,
    key=len,
    reverse=True,
)[:25]:

    brands = sorted({
        txt(r.get("Brand Name"))
        for r in group
    })

    print()
    print(
        f"size={len(group):>3} "
        f"capacity={cap(group[0]):.0f} "
        f"brands={len(brands)}"
    )

    for r in group[:30]:
        print(
            "   "
            f"{txt(r.get('Brand Name')):<24} "
            f"{txt(r.get('Outdoor Unit Model Number⁺'))}"
        )
