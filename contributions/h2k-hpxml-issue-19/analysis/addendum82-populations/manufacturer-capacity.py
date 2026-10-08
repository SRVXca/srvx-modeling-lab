from collections import Counter, defaultdict
from statistics import mean

from run import (
    A82,
    base_population,
    metrics,
    number,
    read_hp_rows,
)

DUCT = "Multizone All Non-Ducted"

BINS = [
    ("18-24k", 18000, 24000),
    ("24-36k", 24000, 36000),
    ("36-48k", 36000, 48000),
    ("48-65k", 48000, 65000),
]


def cap(r):
    return number(r["Rated Capacity 47°F⁺"])


def manufacturer(r):
    owner = str(r.get("Brand Owner") or "").strip()
    brand = str(r.get("Brand Name") or "").strip()

    return owner or brand or "UNKNOWN"


def hardware_dedupe(rows):
    seen = set()
    out = []

    for r in rows:
        model = str(
            r["Outdoor Unit Model Number⁺"] or ""
        ).strip()

        if not model:
            out.append(r)
            continue

        if model in seen:
            continue

        seen.add(model)
        out.append(r)

    return out


def metric_means(rows):
    vals = {k: [] for k in A82}

    for r in rows:
        m = metrics(r)

        for k in A82:
            if m[k] is not None:
                vals[k].append(m[k])

    return {
        k: mean(xs) if xs else None
        for k, xs in vals.items()
    }


def distance(a, b):
    errs = []

    for k in A82:
        if (
            a[k] is None
            or b[k] is None
            or b[k] == 0
        ):
            continue

        errs.append(
            abs(a[k] - b[k]) / abs(b[k])
        )

    return mean(errs) if errs else None


rows = [
    r for r in base_population(read_hp_rows())
    if r["Ducting Configuration"] == DUCT
    and r["ENERGY STAR Cold Climate Certified"] is False
    and cap(r) is not None
    and all(
        v is not None
        for v in metrics(r).values()
    )
]

rows = hardware_dedupe(rows)

print("hardware rows:", len(rows))


# --------------------------------------------------
# 1. Manufacturer mix by capacity bin
# --------------------------------------------------

print()
print("=" * 90)
print("MANUFACTURER MIX BY CAPACITY")
print("=" * 90)

for label, lo, hi in BINS:
    subset = [
        r for r in rows
        if lo <= cap(r) < hi
    ]

    counts = Counter(
        manufacturer(r)
        for r in subset
    )

    print()
    print(
        f"{label}  N={len(subset)}"
    )

    for name, n in counts.most_common(15):
        pct = (
            n / len(subset) * 100
            if subset
            else 0
        )

        print(
            f"{n:4}  "
            f"{pct:6.1f}%  "
            f"{name}"
        )


# --------------------------------------------------
# 2. Find manufacturers represented across bins
# --------------------------------------------------

by_manufacturer = defaultdict(list)

for r in rows:
    by_manufacturer[
        manufacturer(r)
    ].append(r)


print()
print("=" * 90)
print("CAPACITY COVERAGE BY MANUFACTURER")
print("=" * 90)

qualified = []

for name, mrows in by_manufacturer.items():

    counts = {}

    for label, lo, hi in BINS:
        counts[label] = sum(
            1
            for r in mrows
            if lo <= cap(r) < hi
        )

    good_bins = sum(
        n >= 5
        for n in counts.values()
    )

    if good_bins >= 2:
        qualified.append(
            (
                sum(counts.values()),
                name,
                counts,
            )
        )


for total, name, counts in sorted(
    qualified,
    reverse=True,
):
    print(
        f"{name:<30} "
        + " ".join(
            f"{label}={counts[label]:3}"
            for label, _, _ in BINS
        )
    )


# --------------------------------------------------
# 3. Within-manufacturer capacity curves
# --------------------------------------------------

print()
print("=" * 90)
print("WITHIN-MANUFACTURER CAPACITY EFFECT")
print("=" * 90)

for total, name, counts in sorted(
    qualified,
    reverse=True,
):

    mrows = by_manufacturer[name]

    populated = []

    for label, lo, hi in BINS:
        subset = [
            r for r in mrows
            if lo <= cap(r) < hi
        ]

        if len(subset) < 5:
            continue

        populated.append(
            (
                label,
                subset,
                metric_means(subset),
            )
        )

    if len(populated) < 2:
        continue

    ref_label, ref_rows, ref_metrics = populated[0]

    print()
    print(
        f"--- {name} ---"
    )
    print(
        f"reference: {ref_label}"
    )

    print(
        f"{'band':>9} "
        f"{'N':>5} "
        f"{'mean47':>9} "
        f"{'curveΔ':>9}"
    )

    for label, subset, m in populated:
        d = distance(
            m,
            ref_metrics,
        )

        print(
            f"{label:>9} "
            f"{len(subset):>5} "
            f"{mean(cap(r) for r in subset):>9.0f} "
            f"{d:>8.3%}"
        )


# --------------------------------------------------
# 4. Big movers within manufacturers
# --------------------------------------------------

print()
print("=" * 90)
print("LARGEST WITHIN-MANUFACTURER METRIC CHANGES")
print("=" * 90)

for total, name, counts in sorted(
    qualified,
    reverse=True,
):

    mrows = by_manufacturer[name]

    low = [
        r for r in mrows
        if 18000 <= cap(r) < 36000
    ]

    high = [
        r for r in mrows
        if 36000 <= cap(r) < 65000
    ]

    if len(low) < 10 or len(high) < 10:
        continue

    a = metric_means(low)
    b = metric_means(high)

    changes = []

    for k in A82:
        if a[k] is None or b[k] is None:
            continue

        delta = (
            (b[k] - a[k])
            / abs(a[k])
        )

        changes.append(
            (
                abs(delta),
                delta,
                k,
                a[k],
                b[k],
            )
        )

    print()
    print(
        f"--- {name} "
        f"lowN={len(low)} "
        f"highN={len(high)} ---"
    )

    for _, delta, k, lv, hv in sorted(
        changes,
        reverse=True,
    )[:8]:
        print(
            f"{k:<12} "
            f"{lv:7.3f} -> "
            f"{hv:7.3f}  "
            f"{delta:+7.1%}"
        )
