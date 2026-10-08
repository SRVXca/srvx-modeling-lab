from __future__ import annotations

from collections import Counter
from datetime import date
import json
from pathlib import Path

from run import (
    A82,
    PopulationSpec,
    base_population,
    evaluate,
    read_hp_rows,
    source_date,
)


OUT = Path(__file__).parent
PDS01 = date.fromisoformat("2024-11-22")


def clean(value):
    if value is None:
        return None
    value = str(value).strip()
    return value or None


print("Reading NEEP HP population...")
all_rows = read_hp_rows()
base = base_population(all_rows)

print("all HP rows:", len(all_rows))
print("Live variable-capacity:", len(base))


ductings = sorted({
    clean(r["Ducting Configuration"])
    for r in base
    if clean(r["Ducting Configuration"])
})

ahri_types = sorted({
    clean(r["AHRI Type⁺"])
    for r in base
    if clean(r["AHRI Type⁺"])
})

pair_counts = Counter(
    (
        clean(r["Ducting Configuration"]),
        clean(r["AHRI Type⁺"]),
    )
    for r in base
)

# Don't optimize against tiny accidental populations.
useful_pairs = sorted(
    pair
    for pair, n in pair_counts.items()
    if pair[0] is not None
    and pair[1] is not None
    and n >= 30
)


print("\nDucting configurations:")
for x in ductings:
    n = sum(
        clean(r["Ducting Configuration"]) == x
        for r in base
    )
    print(f"{n:8}  {x}")

print("\nAHRI types:")
for x in ahri_types:
    n = sum(
        clean(r["AHRI Type⁺"]) == x
        for r in base
    )
    print(f"{n:8}  {x}")


cases = []
seen = set()


def add_case(
    family,
    *,
    vintage="all",
    ducting=None,
    ahri_type=None,
    energy_star=None,
    cold_climate=None,
    complete=True,
    dedupe="none",
):
    key = (
        vintage,
        ducting,
        ahri_type,
        energy_star,
        cold_climate,
        complete,
        dedupe,
    )

    if key in seen:
        return

    seen.add(key)

    cases.append({
        "family": family,
        "vintage": vintage,
        "ducting": ducting,
        "ahriType": ahri_type,
        "energyStar": energy_star,
        "coldClimate": cold_climate,
        "completeMetrics": complete,
        "dedupe": dedupe,
    })


# ------------------------------------------------------------
# 1. Global controls
# ------------------------------------------------------------

for vintage in ("all", "pre-PDS01"):
    for energy_star in (None, True, False):
        for cold in (None, True, False):
            for dedupe in (
                "none",
                "outdoor",
                "outdoor_indoor",
            ):
                for complete in (False, True):
                    add_case(
                        "control",
                        vintage=vintage,
                        energy_star=energy_star,
                        cold_climate=cold,
                        complete=complete,
                        dedupe=dedupe,
                    )


# ------------------------------------------------------------
# 2. Exact NEEP ducting configuration
# ------------------------------------------------------------

for ducting in ductings:
    for vintage in ("all", "pre-PDS01"):
        for cold in (None, True, False):
            for dedupe in ("none", "outdoor"):
                add_case(
                    "ducting",
                    vintage=vintage,
                    ducting=ducting,
                    cold_climate=cold,
                    complete=True,
                    dedupe=dedupe,
                )


# ------------------------------------------------------------
# 3. AHRI type
# ------------------------------------------------------------

for ahri_type in ahri_types:
    for vintage in ("all", "pre-PDS01"):
        for cold in (None, True, False):
            for dedupe in ("none", "outdoor"):
                add_case(
                    "ahri-type",
                    vintage=vintage,
                    ahri_type=ahri_type,
                    cold_climate=cold,
                    complete=True,
                    dedupe=dedupe,
                )


# ------------------------------------------------------------
# 4. Actual observed Ducting × AHRI combinations
#    Only populations with >=30 current base rows.
# ------------------------------------------------------------

for ducting, ahri_type in useful_pairs:
    for vintage in ("all", "pre-PDS01"):
        for cold in (None, True, False):
            for dedupe in ("none", "outdoor"):
                add_case(
                    "ducting-x-ahri",
                    vintage=vintage,
                    ducting=ducting,
                    ahri_type=ahri_type,
                    cold_climate=cold,
                    complete=True,
                    dedupe=dedupe,
                )


def filter_rows(case):
    rows = base

    if case["vintage"] == "pre-PDS01":
        rows = [
            r for r in rows
            if (
                (d := source_date(r["Date Added to List"]))
                is not None
                and d < PDS01
            )
        ]

    if case["ducting"] is not None:
        rows = [
            r for r in rows
            if clean(r["Ducting Configuration"])
            == case["ducting"]
        ]

    if case["ahriType"] is not None:
        rows = [
            r for r in rows
            if clean(r["AHRI Type⁺"])
            == case["ahriType"]
        ]

    if case["energyStar"] is not None:
        rows = [
            r for r in rows
            if r["ENERGY STAR Certified"]
            is case["energyStar"]
        ]

    if case["coldClimate"] is not None:
        rows = [
            r for r in rows
            if r["ENERGY STAR Cold Climate Certified"]
            is case["coldClimate"]
        ]

    return rows


results = []

print()
print("Running", len(cases), "population definitions...")


for i, case in enumerate(cases, 1):
    filtered = filter_rows(case)

    name = f"sweep-{i:04d}"

    result = evaluate(
        filtered,
        PopulationSpec(
            name=name,
            complete_metrics=case["completeMetrics"],
            dedupe=case["dedupe"],
        ),
    )

    covered = sum(
        1
        for m in result["metrics"].values()
        if m["mean"] is not None
    )

    ns = [
        m["n"]
        for m in result["metrics"].values()
        if m["n"] > 0
    ]

    result["family"] = case["family"]
    result["filters"] = case
    result["metricCoverage"] = covered
    result["minimumMetricN"] = min(ns) if ns else 0

    results.append(result)

    if i % 50 == 0:
        print(f"  {i}/{len(cases)}")


# ------------------------------------------------------------
# Ranking
#
# Serious ranking:
# - all 15 Addendum metrics represented
# - at least 30 observations in every metric
# ------------------------------------------------------------

eligible = [
    r
    for r in results
    if r["score"] is not None
    and r["metricCoverage"] == len(A82)
    and r["minimumMetricN"] >= 30
]

eligible.sort(key=lambda r: r["score"])


(OUT / "sweep-results.json").write_text(
    json.dumps(
        {
            "caseCount": len(cases),
            "eligibleCount": len(eligible),
            "targetMetricCount": len(A82),
            "results": results,
        },
        indent=2,
    )
)


with (OUT / "sweep-top.tsv").open("w") as f:
    f.write(
        "rank\tscore\trows\tpre_dedupe\tmin_metric_n\t"
        "family\tvintage\tducting\tahri_type\t"
        "energy_star\tcold_climate\tcomplete\tdedupe\n"
    )

    for rank, r in enumerate(eligible, 1):
        c = r["filters"]

        f.write(
            f"{rank}\t"
            f"{r['score']:.8f}\t"
            f"{r['rows']}\t"
            f"{r['rowsBeforeDedupe']}\t"
            f"{r['minimumMetricN']}\t"
            f"{r['family']}\t"
            f"{c['vintage']}\t"
            f"{c['ducting'] or '*'}\t"
            f"{c['ahriType'] or '*'}\t"
            f"{c['energyStar']}\t"
            f"{c['coldClimate']}\t"
            f"{c['completeMetrics']}\t"
            f"{c['dedupe']}\n"
        )


print()
print("=== TOP 40 ===")
print(
    f"{'#':>3} "
    f"{'score':>9} "
    f"{'rows':>8} "
    f"{'minN':>7} "
    f"{'family':<16} "
    f"{'vintage':<10} "
    f"{'dedupe':<14} "
    "filters"
)

for i, r in enumerate(eligible[:40], 1):
    c = r["filters"]

    details = []

    if c["ducting"]:
        details.append(f"duct={c['ducting']}")

    if c["ahriType"]:
        details.append(f"ahri={c['ahriType']}")

    if c["energyStar"] is not None:
        details.append(f"ES={c['energyStar']}")

    if c["coldClimate"] is not None:
        details.append(f"cold={c['coldClimate']}")

    print(
        f"{i:>3} "
        f"{r['score']:>8.3%} "
        f"{r['rows']:>8} "
        f"{r['minimumMetricN']:>7} "
        f"{r['family']:<16} "
        f"{c['vintage']:<10} "
        f"{c['dedupe']:<14} "
        + ", ".join(details)
    )


print()
print("wrote:", OUT / "sweep-results.json")
print("wrote:", OUT / "sweep-top.tsv")
