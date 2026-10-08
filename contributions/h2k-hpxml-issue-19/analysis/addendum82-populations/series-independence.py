exec(open("series-capacity.py").read().split('results.sort(')[0])

from collections import defaultdict
from statistics import mean

# Rebuild the result set.
results = []

for name, rs in families.items():
    low = [r for r in rs if 18000 <= cap(r) < 36000]
    high = [r for r in rs if 36000 <= cap(r) < 65000]

    if len(low) < 2 or len(high) < 2:
        continue

    lm = metric_means(low)
    hm = metric_means(high)

    d = distance(lm, hm)

    # Conservative fingerprint:
    # same counts, capacities and normalized low/high curves
    # => treat as one independent performance pattern.
    fingerprint = (
        len(low),
        len(high),
        round(mean(cap(r) for r in low), 3),
        round(mean(cap(r) for r in high), 3),
        tuple(round(lm[k], 9) for k in A82),
        tuple(round(hm[k], 9) for k in A82),
    )

    results.append({
        "family": name,
        "lowN": len(low),
        "highN": len(high),
        "distance": d,
        "fingerprint": fingerprint,
    })


groups = defaultdict(list)

for r in results:
    groups[r["fingerprint"]].append(r)


print("qualified Brand+Series families:", len(results))
print("unique performance fingerprints:", len(groups))
print()

print("=" * 90)
print("DUPLICATE / REBADGE-LIKE CLUSTERS")
print("=" * 90)

duplicate_groups = [
    g for g in groups.values()
    if len(g) > 1
]

for g in sorted(
    duplicate_groups,
    key=lambda x: (-len(x), -x[0]["distance"]),
):
    print()
    print(
        f"{len(g)} families  "
        f"curveΔ={g[0]['distance']:.3%}  "
        f"lowN={g[0]['lowN']} "
        f"highN={g[0]['highN']}"
    )

    for r in g:
        print("   ", r["family"])


# One representative per independent fingerprint.
independent = [
    g[0]
    for g in groups.values()
]

ds = [
    r["distance"]
    for r in independent
]


print()
print("=" * 90)
print("CONSERVATIVE INDEPENDENT-PATTERN SUMMARY")
print("=" * 90)

print("independent patterns:", len(ds))
print(
    "mean curve distance:",
    f"{mean(ds):.3%}",
)
print(
    "patterns >= 3%:",
    sum(d >= .03 for d in ds),
)
print(
    "patterns >= 5%:",
    sum(d >= .05 for d in ds),
)
print(
    "patterns >= 8%:",
    sum(d >= .08 for d in ds),
)


print()
print("=" * 90)
print("STRICTER: >=3 LOW AND >=3 HIGH")
print("=" * 90)

strict = []

for g in groups.values():

    candidates = [
        r for r in g
        if r["lowN"] >= 3
        and r["highN"] >= 3
    ]

    if candidates:
        strict.append(candidates[0])


for r in sorted(
    strict,
    key=lambda x: -x["distance"],
):
    print(
        f"{r['distance']:>7.3%}  "
        f"low={r['lowN']:>2} "
        f"high={r['highN']:>2}  "
        f"{r['family']}"
    )

if strict:
    print()
    print(
        "strict independent patterns:",
        len(strict),
    )
    print(
        "strict mean distance:",
        f"{mean(r['distance'] for r in strict):.3%}",
    )
