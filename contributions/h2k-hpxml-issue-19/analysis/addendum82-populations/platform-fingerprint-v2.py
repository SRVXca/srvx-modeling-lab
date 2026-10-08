from collections import defaultdict
from statistics import mean, median

from run import (
    A82,
    base_population,
    metrics,
    number,
    read_hp_rows,
)

DUCT = "Multizone All Non-Ducted"

# Ground-truth calibration anchors.
# Brand/model are used ONLY to choose known Midea reference units.
ANCHORS = [
    "M2OA-18HFN1-M",
    "M3OJ-27HFN1-M",
    "M4OG-36HFN1-M",
    "M5OG-48HFN1-M",
]


def txt(v):
    return str(v or "").strip()


def cap(r):
    return number(r["Rated Capacity 47°F⁺"])


def rel(a, b):
    return abs(a - b) / max(abs(a), abs(b), 1e-9)


def percentile(xs, p):
    if not xs:
        return None

    xs = sorted(xs)
    i = round((len(xs) - 1) * p)
    return xs[i]


rows = [
    r
    for r in base_population(read_hp_rows())
    if r["Ducting Configuration"] == DUCT
    and r["ENERGY STAR Cold Climate Certified"] is False
    and cap(r) is not None
]


# ------------------------------------------------------------------
# Discover numeric PHYSICAL/PERFORMANCE fields automatically.
#
# Deliberately exclude:
# brand
# model
# AHRI reference
# series
#
# These fields never participate in similarity scoring.
# ------------------------------------------------------------------

def looks_like_performance_field(name):
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
    key
    for r in rows
    for key in r.keys()
})


RAW_FIELDS = []

for field in all_fields:

    if not looks_like_performance_field(field):
        continue

    n = sum(
        number(r.get(field)) is not None
        for r in rows
    )

    # Don't use extremely sparse fields.
    if n >= 30:
        RAW_FIELDS.append(field)


print("rows:", len(rows))
print("raw performance fields:", len(RAW_FIELDS))

for f in RAW_FIELDS:
    print("  ", f)


# ------------------------------------------------------------------
# Group identical marketed outdoor identities.
# ------------------------------------------------------------------

groups = defaultdict(list)

for r in rows:
    brand = txt(r.get("Brand Name"))
    model = txt(r.get("Outdoor Unit Model Number⁺"))

    if not brand or not model:
        continue

    groups[(brand, model)].append(r)


def med(values):
    values = [
        v
        for v in values
        if v is not None
    ]

    return median(values) if values else None


def signature(rs):

    raw = {}

    for field in RAW_FIELDS:
        value = med([
            number(r.get(field))
            for r in rs
        ])

        if value is not None:
            raw[field] = value

    curve = {}

    for key in A82:
        value = med([
            metrics(r).get(key)
            for r in rs
        ])

        if value is not None:
            curve[key] = value

    return {
        "capacity": med([
            cap(r)
            for r in rs
        ]),
        "raw": raw,
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
        "sig": signature(rs),
    })


# ------------------------------------------------------------------
# FUZZY PHYSICAL/PERFORMANCE COMPARISON
#
# No names participate.
# ------------------------------------------------------------------

def compare(a, b):

    sa = a["sig"]
    sb = b["sig"]

    cap_delta = rel(
        sa["capacity"],
        sb["capacity"],
    )

    common_raw = sorted(
        set(sa["raw"])
        & set(sb["raw"])
    )

    raw_deltas = [
        rel(
            sa["raw"][k],
            sb["raw"][k],
        )
        for k in common_raw
        if (
            sa["raw"][k] != 0
            or sb["raw"][k] != 0
        )
    ]

    common_curve = sorted(
        set(sa["curve"])
        & set(sb["curve"])
    )

    curve_deltas = [
        rel(
            sa["curve"][k],
            sb["curve"][k],
        )
        for k in common_curve
        if (
            sa["curve"][k] != 0
            or sb["curve"][k] != 0
        )
    ]

    if not raw_deltas:
        return None

    raw_med = median(raw_deltas)
    raw_p90 = percentile(
        raw_deltas,
        0.90,
    )

    curve_mean = (
        mean(curve_deltas)
        if curve_deltas
        else 0
    )

    # Ranking score only.
    #
    # We deliberately care more about the raw submitted
    # performance surface than our derived Addendum curve.
    score = (
        0.45 * raw_med
        + 0.30 * raw_p90
        + 0.15 * curve_mean
        + 0.10 * cap_delta
    )

    return {
        "score": score,
        "cap": cap_delta,
        "raw_med": raw_med,
        "raw_p90": raw_p90,
        "curve": curve_mean,
        "fields": len(raw_deltas),
    }


# ------------------------------------------------------------------
# Select ONE known MDV/Midea unit per calibration size.
# ------------------------------------------------------------------

anchors = []

for model in ANCHORS:

    found = next(
        (
            u
            for u in units
            if (
                u["brand"].casefold() == "mdv"
                and u["model"] == model
            )
        ),
        None,
    )

    if found:
        anchors.append(found)


print()
print("=" * 110)
print("MIDEA CALIBRATION ANCHORS")
print("=" * 110)

for a in anchors:
    print(
        a["brand"],
        a["model"],
        a["sig"]["capacity"],
    )


# ------------------------------------------------------------------
# Rank neighbors per anchor.
# ------------------------------------------------------------------

print()
print("=" * 110)
print("FUZZY NEIGHBORS PER MIDEA ANCHOR")
print("=" * 110)

for anchor in anchors:

    candidates = []

    for u in units:

        if u is anchor:
            continue

        result = compare(
            anchor,
            u,
        )

        if result is None:
            continue

        # Broad enough to tolerate nominal/reporting differences.
        if result["cap"] > 0.10:
            continue

        candidates.append(
            (
                result["score"],
                result,
                u,
            )
        )

    candidates.sort(
        key=lambda x: x[0]
    )

    print()
    print(
        "ANCHOR",
        anchor["model"],
        f"{anchor['sig']['capacity']:.0f} Btu/h"
    )

    print(
        f"{'rank':>4} "
        f"{'score':>8} "
        f"{'raw50':>8} "
        f"{'raw90':>8} "
        f"{'curve':>8} "
        f"{'cap':>7} "
        f"{'nf':>4} "
        f"{'brand':<22} "
        f"model"
    )

    for rank, (
        score,
        result,
        u,
    ) in enumerate(
        candidates[:30],
        1,
    ):

        print(
            f"{rank:4} "
            f"{score:8.3%} "
            f"{result['raw_med']:8.3%} "
            f"{result['raw_p90']:8.3%} "
            f"{result['curve']:8.3%} "
            f"{result['cap']:7.2%} "
            f"{result['fields']:4} "
            f"{u['brand']:<22} "
            f"{u['model']}"
        )


# ------------------------------------------------------------------
# PLATFORM-LADDER TEST
#
# This is the important new part.
#
# For every commercial brand:
# find its best match to EACH Midea capacity anchor.
#
# A hidden rebrand should not merely resemble one 28k unit.
# It should reproduce the 18/27/36/48k PLATFORM SHAPE.
# ------------------------------------------------------------------

brands = sorted({
    u["brand"]
    for u in units
})


ladder = []

for brand in brands:

    if brand.casefold() == "mdv":
        continue

    matches = []

    for anchor in anchors:

        best = None

        for u in units:

            if u["brand"] != brand:
                continue

            result = compare(
                anchor,
                u,
            )

            if result is None:
                continue

            if result["cap"] > 0.10:
                continue

            candidate = (
                result["score"],
                result,
                u,
            )

            if (
                best is None
                or candidate[0] < best[0]
            ):
                best = candidate

        if best is not None:
            matches.append(
                (
                    anchor,
                    best,
                )
            )

    # Require >= 3 different capacities.
    if len(matches) < 3:
        continue

    scores = [
        match[1][0]
        for match in matches
    ]

    raw_meds = [
        match[1][1]["raw_med"]
        for match in matches
    ]

    raw_p90s = [
        match[1][1]["raw_p90"]
        for match in matches
    ]

    ladder.append({
        "brand": brand,
        "coverage": len(matches),
        "score": mean(scores),
        "raw_med": mean(raw_meds),
        "raw_p90": mean(raw_p90s),
        "matches": matches,
    })


ladder.sort(
    key=lambda x: (
        -x["coverage"],
        x["score"],
    )
)


print()
print("=" * 110)
print("BLIND MIDEA PLATFORM-LADDER CANDIDATES")
print("=" * 110)

print(
    f"{'brand':<25} "
    f"{'coverage':>8} "
    f"{'score':>9} "
    f"{'raw50':>9} "
    f"{'raw90':>9}"
)

for x in ladder[:50]:

    print(
        f"{x['brand']:<25} "
        f"{x['coverage']:>4}/{len(anchors):<3} "
        f"{x['score']:>8.3%} "
        f"{x['raw_med']:>8.3%} "
        f"{x['raw_p90']:>8.3%}"
    )

    for anchor, (
        score,
        result,
        u,
    ) in x["matches"]:

        print(
            f"    "
            f"{anchor['model']:<18} "
            f"→ {u['model']:<28} "
            f"score={score:.3%}"
        )


# ------------------------------------------------------------------
# Useful evidence labels.
#
# These are CANDIDATE levels, not OEM assertions.
# ------------------------------------------------------------------

print()
print("=" * 110)
print("HIGH-CONFIDENCE CANDIDATE LADDERS")
print("=" * 110)

for x in ladder:

    if x["coverage"] < 3:
        continue

    if (
        x["raw_med"] <= 0.015
        and x["raw_p90"] <= 0.05
    ):
        print(
            f"{x['brand']:<25} "
            f"coverage={x['coverage']}/{len(anchors)} "
            f"raw50={x['raw_med']:.3%} "
            f"raw90={x['raw_p90']:.3%}"
        )
