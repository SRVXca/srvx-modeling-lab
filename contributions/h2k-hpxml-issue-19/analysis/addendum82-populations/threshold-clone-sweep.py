from collections import defaultdict

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


def cap(r):
    return number(r["Rated Capacity 47°F⁺"])


# ------------------------------------------------------------
# Same performance-field definition as our exact-clone test.
# ------------------------------------------------------------

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


all_rows = [
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


all_fields = sorted({
    field
    for r in all_rows
    for field in r.keys()
})


RAW_FIELDS = [
    field
    for field in all_fields
    if performance_field(field)
    and sum(
        number(r.get(field)) is not None
        for r in all_rows
    ) >= 30
]


def fingerprint(r):
    out = []

    for field in RAW_FIELDS:
        v = number(r.get(field))

        out.append(
            None
            if v is None
            else float(v)
        )

    return tuple(out)


def outdoor_dedupe(rows):
    seen = set()
    out = []

    for i, r in enumerate(rows):
        key = identity_key(
            r,
            "outdoor",
            i,
        )

        if key in seen:
            continue

        seen.add(key)
        out.append(r)

    return out


def exact_clone_collapse(rows):
    by_fp = defaultdict(list)

    for r in rows:
        by_fp[fingerprint(r)].append(r)

    collapsed = [
        group[0]
        for group in by_fp.values()
    ]

    clone_groups = [
        group
        for group in by_fp.values()
        if len(group) > 1
    ]

    removed = sum(
        len(group) - 1
        for group in clone_groups
    )

    return (
        collapsed,
        len(clone_groups),
        removed,
    )


def evaluate_population(rows):
    result = evaluate(
        rows,
        PopulationSpec(
            name="threshold-test",
            complete_metrics=True,
            dedupe="none",
        ),
    )

    errors = [
        m["relativeError"]
        for m in result["metrics"].values()
        if m["relativeError"] is not None
    ]

    return (
        result["score"],
        max(errors),
    )


print(
    "complete ceiling/non-cold rows:",
    len(all_rows),
)

print(
    "raw performance fields:",
    len(RAW_FIELDS),
)

print()

print(
    f"{'cut':>5} "
    f"{'Nout':>5} "
    f"{'outScore':>9} "
    f"{'outMax':>8} "
    f"{'Nplat':>6} "
    f"{'platScore':>10} "
    f"{'platMax':>8} "
    f"{'removed':>7} "
    f"{'Δscore':>9}"
)

results = []

for threshold in range(
    12000,
    25000,
    1000,
):

    selected = [
        r
        for r in all_rows
        if cap(r) >= threshold
    ]

    outdoor = outdoor_dedupe(
        selected
    )

    (
        platform,
        clone_groups,
        removed,
    ) = exact_clone_collapse(
        outdoor
    )

    out_score, out_max = (
        evaluate_population(
            outdoor
        )
    )

    plat_score, plat_max = (
        evaluate_population(
            platform
        )
    )

    delta = (
        plat_score
        - out_score
    )

    results.append({
        "threshold": threshold,
        "out_n": len(outdoor),
        "out_score": out_score,
        "out_max": out_max,
        "plat_n": len(platform),
        "plat_score": plat_score,
        "plat_max": plat_max,
        "removed": removed,
        "groups": clone_groups,
        "delta": delta,
    })

    print(
        f"{threshold//1000:>4}k "
        f"{len(outdoor):>5} "
        f"{out_score:>8.3%} "
        f"{out_max:>7.2%} "
        f"{len(platform):>6} "
        f"{plat_score:>9.3%} "
        f"{plat_max:>7.2%} "
        f"{removed:>7} "
        f"{delta:>+8.3%}"
    )


print()
print("=" * 100)
print("BEST THRESHOLD — OUTDOOR WEIGHTED")
print("=" * 100)

best_out = min(
    results,
    key=lambda x: x["out_score"],
)

print(
    f"{best_out['threshold']//1000}k "
    f"N={best_out['out_n']} "
    f"score={best_out['out_score']:.3%} "
    f"max={best_out['out_max']:.2%}"
)


print()
print("=" * 100)
print("BEST THRESHOLD — EXACT PLATFORM-DATA COLLAPSE")
print("=" * 100)

best_plat = min(
    results,
    key=lambda x: x["plat_score"],
)

print(
    f"{best_plat['threshold']//1000}k "
    f"N={best_plat['plat_n']} "
    f"score={best_plat['plat_score']:.3%} "
    f"max={best_plat['plat_max']:.2%}"
)


print()
print("=" * 100)
print("18k → 19k DISCONTINUITY")
print("=" * 100)

r18 = next(
    x
    for x in results
    if x["threshold"] == 18000
)

r19 = next(
    x
    for x in results
    if x["threshold"] == 19000
)


def change(a, b):
    return b - a


print("OUTDOOR WEIGHTED")

print(
    "  score:",
    f"{r18['out_score']:.3%}",
    "→",
    f"{r19['out_score']:.3%}",
    "change",
    f"{change(r18['out_score'], r19['out_score']):+.3%}",
)

print(
    "  N:",
    r18["out_n"],
    "→",
    r19["out_n"],
    "removed:",
    r18["out_n"] - r19["out_n"],
)


print()
print("EXACT PLATFORM-DATA COLLAPSE")

print(
    "  score:",
    f"{r18['plat_score']:.3%}",
    "→",
    f"{r19['plat_score']:.3%}",
    "change",
    f"{change(r18['plat_score'], r19['plat_score']):+.3%}",
)

print(
    "  N:",
    r18["plat_n"],
    "→",
    r19["plat_n"],
    "removed:",
    r18["plat_n"] - r19["plat_n"],
)


print()
print("=" * 100)
print("INTERPRETATION SIGNAL")
print("=" * 100)

out_jump = change(
    r18["out_score"],
    r19["out_score"],
)

plat_jump = change(
    r18["plat_score"],
    r19["plat_score"],
)

if abs(plat_jump) < abs(out_jump) * 0.5:
    print(
        "Clone collapse removes more than half "
        "of the 18k→19k discontinuity."
    )
    print(
        "Strong evidence that catalog/platform "
        "multiplicity contributed materially."
    )

elif abs(plat_jump) < abs(out_jump):
    print(
        "Clone collapse reduces the 18k→19k discontinuity."
    )
    print(
        "Catalog composition contributed, but does not "
        "fully explain the capacity effect."
    )

else:
    print(
        "Clone collapse does NOT reduce the 18k→19k discontinuity."
    )
    print(
        "The threshold effect survives conservative "
        "platform-data deduplication."
    )
