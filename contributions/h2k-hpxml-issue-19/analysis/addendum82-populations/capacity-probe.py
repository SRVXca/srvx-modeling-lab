from run import (
    PopulationSpec,
    base_population,
    evaluate,
    metrics,
    number,
    read_hp_rows,
)

DUCT = "Singlezone Non-Ducted, Ceiling Placement"

base = [
    r for r in base_population(read_hp_rows())
    if r["Ducting Configuration"] == DUCT
    and r["ENERGY STAR Cold Climate Certified"] is False
    and all(v is not None for v in metrics(r).values())
]

print("winning base population:", len(base))

# Rated heating capacity @47F.
def cap(r):
    return number(r["Rated Capacity 47°F⁺"])

caps = sorted(
    x for r in base
    if (x := cap(r)) is not None
)

print(
    "capacity range:",
    min(caps),
    "to",
    max(caps),
)

# Common nominal equipment boundaries.
edges = [
    0,
    12000,
    18000,
    24000,
    30000,
    36000,
    48000,
    60000,
    1000000,
]

cases = []

# Full baseline.
cases.append(("ALL", 0, 1000000))

# Individual normal capacity bands.
for lo, hi in zip(edges[:-1], edges[1:]):
    cases.append((f"{lo/1000:g}-{hi/1000:g}k", lo, hi))

# Contiguous broader ranges.
for i in range(len(edges) - 2):
    for j in range(i + 2, len(edges)):
        lo = edges[i]
        hi = edges[j]

        cases.append(
            (f"{lo/1000:g}-{hi/1000:g}k", lo, hi)
        )


results = []

for name, lo, hi in cases:
    selected = [
        r for r in base
        if (x := cap(r)) is not None
        and lo <= x < hi
    ]

    if len(selected) < 30:
        continue

    for dedupe in ("none", "outdoor"):
        result = evaluate(
            selected,
            PopulationSpec(
                name=name,
                complete_metrics=True,
                dedupe=dedupe,
            ),
        )

        if result["score"] is None:
            continue

        errors = [
            m["relativeError"]
            for m in result["metrics"].values()
            if m["relativeError"] is not None
        ]

        ns = [
            m["n"]
            for m in result["metrics"].values()
            if m["n"] > 0
        ]

        results.append({
            "band": name,
            "lo": lo,
            "hi": hi,
            "dedupe": dedupe,
            "rows": result["rows"],
            "minN": min(ns),
            "score": result["score"],
            "max": max(errors),
        })


results.sort(key=lambda x: x["score"])

print()
print(
    f"{'score':>8} "
    f"{'max':>8} "
    f"{'N':>5} "
    f"{'band':>14} "
    f"{'dedupe':>8}"
)

for r in results[:40]:
    print(
        f"{r['score']:>7.3%} "
        f"{r['max']:>7.2%} "
        f"{r['minN']:>5} "
        f"{r['band']:>14} "
        f"{r['dedupe']:>8}"
    )
