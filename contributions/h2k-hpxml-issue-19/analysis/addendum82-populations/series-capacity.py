from collections import defaultdict
from statistics import mean

from run import (
    A82,
    base_population,
    metrics,
    number,
    read_hp_rows,
)

DUCT = "Multizone All Non-Ducted"


def cap(r):
    return number(r["Rated Capacity 47°F⁺"])


def family(r):
    brand = str(r.get("Brand Name") or "").strip()
    series = str(r.get("Series Name") or "").strip()

    if not brand or not series:
        return None

    if series.lower() in {"n/a", "none", "unknown"}:
        return None

    return f"{brand} :: {series}"


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
    values = {k: [] for k in A82}

    for r in rows:
        m = metrics(r)

        for k in A82:
            if m[k] is not None:
                values[k].append(m[k])

    return {
        k: mean(v) if v else None
        for k, v in values.items()
    }


def distance(a, b):
    values = []

    for k in A82:
        x = a[k]
        y = b[k]

        if x is None or y is None or x == 0:
            continue

        values.append(
            abs(y - x) / abs(x)
        )

    return mean(values) if values else None


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

families = defaultdict(list)

for r in rows:
    f = family(r)

    if f:
        families[f].append(r)


results = []

for name, rs in families.items():

    low = [
        r for r in rs
        if 18000 <= cap(r) < 36000
    ]

    high = [
        r for r in rs
        if 36000 <= cap(r) < 65000
    ]

    # Enough actual outdoor models on both sides
    # to avoid comparing one unit to one unit.
    if len(low) < 2 or len(high) < 2:
        continue

    lm = metric_means(low)
    hm = metric_means(high)

    d = distance(lm, hm)

    changes = []

    for k in A82:
        if lm[k] is None or hm[k] is None:
            continue

        delta = (
            (hm[k] - lm[k])
            / abs(lm[k])
        )

        changes.append(
            (
                abs(delta),
                delta,
                k,
                lm[k],
                hm[k],
            )
        )

    results.append({
        "family": name,
        "low": low,
        "high": high,
        "distance": d,
        "changes": sorted(
            changes,
            reverse=True,
        ),
    })


results.sort(
    key=lambda x: (
        -(len(x["low"]) + len(x["high"])),
        -x["distance"],
    )
)


print("hardware population:", len(rows))
print("families:", len(families))
print(
    "families with >=2 low and >=2 high:",
    len(results),
)

print()
print("=" * 100)
print("WITHIN-SERIES CAPACITY EFFECT")
print("=" * 100)

for x in results:
    low = x["low"]
    high = x["high"]

    print()
    print(x["family"])

    print(
        f"  low : N={len(low):2} "
        f"mean47={mean(cap(r) for r in low):8.0f}"
    )

    print(
        f"  high: N={len(high):2} "
        f"mean47={mean(cap(r) for r in high):8.0f}"
    )

    print(
        f"  15-metric curve distance: "
        f"{x['distance']:.3%}"
    )

    print("  largest changes:")

    for _, delta, key, lv, hv in x["changes"][:6]:
        print(
            f"    {key:<12} "
            f"{lv:7.3f} -> {hv:7.3f} "
            f"{delta:+7.1%}"
        )


if results:
    print()
    print("=" * 100)
    print("SUMMARY")
    print("=" * 100)

    ds = [
        x["distance"]
        for x in results
    ]

    print(
        "families:",
        len(ds),
    )
    print(
        "mean within-series curve distance:",
        f"{mean(ds):.3%}",
    )

    print(
        "families >= 3%:",
        sum(d >= .03 for d in ds),
    )

    print(
        "families >= 5%:",
        sum(d >= .05 for d in ds),
    )

    print(
        "families >= 8%:",
        sum(d >= .08 for d in ds),
    )
