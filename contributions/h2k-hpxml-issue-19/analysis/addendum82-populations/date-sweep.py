from __future__ import annotations

from datetime import date
import json
from pathlib import Path
from statistics import median

from run import (
    A82,
    PopulationSpec,
    base_population,
    evaluate,
    read_hp_rows,
    source_date,
)


HERE = Path(__file__).parent


ANCHORS = [
    # Exclusive cutoffs:
    # dataset must already have existed before the publication date.
    ("pre-PDS01", "2024-11-22"),
    ("pre-PDS02", "2025-04-21"),
    ("pre-PDS03", "2025-10-29"),
    ("pre-FINAL", "2025-12-17"),
    ("current", None),
]


def clean(value):
    if value is None:
        return None

    value = str(value).strip()
    return value or None


print("Reading NEEP rows...")

rows = base_population(read_hp_rows())

print("Live variable-capacity base:", len(rows))


# ------------------------------------------------------------
# Reuse the population definitions we already tested.
#
# Only take vintage=all definitions.
# The historical cutoff is controlled here instead.
# ------------------------------------------------------------

existing = json.loads(
    (HERE / "sweep-results.json").read_text()
)

cases = []
seen = set()

for result in existing["results"]:
    filters = dict(result["filters"])

    if filters.get("vintage") != "all":
        continue

    filters.pop("vintage", None)

    key = json.dumps(
        filters,
        sort_keys=True,
    )

    if key in seen:
        continue

    seen.add(key)

    cases.append({
        "originFamily": result.get("family"),
        "filters": filters,
    })


print("population definitions:", len(cases))


# ------------------------------------------------------------
# Materialize each historical proxy ONCE.
# ------------------------------------------------------------

pools = {}

for label, cutoff in ANCHORS:
    if cutoff is None:
        pool = rows

    else:
        stop = date.fromisoformat(cutoff)

        pool = [
            r
            for r in rows
            if (
                (d := source_date(
                    r["Date Added to List"]
                ))
                is not None
                and d < stop
            )
        ]

    pools[label] = pool

    print(
        f"{label:<12}",
        cutoff or "current",
        "rows:",
        len(pool),
    )


def apply_case(pool, filters):
    selected = pool

    ducting = filters.get("ducting")

    if ducting is not None:
        selected = [
            r
            for r in selected
            if clean(r["Ducting Configuration"])
            == ducting
        ]

    ahri_type = filters.get("ahriType")

    if ahri_type is not None:
        selected = [
            r
            for r in selected
            if clean(r["AHRI Type⁺"])
            == ahri_type
        ]

    energy_star = filters.get("energyStar")

    if energy_star is not None:
        selected = [
            r
            for r in selected
            if (
                r["ENERGY STAR Certified"]
                is energy_star
            )
        ]

    cold = filters.get("coldClimate")

    if cold is not None:
        selected = [
            r
            for r in selected
            if (
                r[
                    "ENERGY STAR Cold Climate Certified"
                ]
                is cold
            )
        ]

    return selected


results = []


for label, cutoff in ANCHORS:
    pool = pools[label]

    print()
    print(
        f"=== {label} "
        f"({cutoff or 'current'}) ==="
    )

    for i, case in enumerate(cases, 1):
        filters = case["filters"]

        selected = apply_case(
            pool,
            filters,
        )

        result = evaluate(
            selected,
            PopulationSpec(
                name=f"{label}-{i:04d}",
                complete_metrics=filters.get(
                    "completeMetrics",
                    False,
                ),
                dedupe=filters.get(
                    "dedupe",
                    "none",
                ),
            ),
        )

        metric_rows = [
            m
            for m in result["metrics"].values()
            if m["mean"] is not None
        ]

        errors = [
            m["relativeError"]
            for m in metric_rows
        ]

        ns = [
            m["n"]
            for m in metric_rows
            if m["n"] > 0
        ]

        coverage = len(metric_rows)
        min_n = min(ns) if ns else 0

        max_error = (
            max(errors)
            if errors
            else None
        )

        median_error = (
            median(errors)
            if errors
            else None
        )

        numeric_strong = (
            result["score"] is not None
            and coverage == len(A82)
            and min_n >= 100
            and result["score"] <= 0.04
            and max_error is not None
            and max_error <= 0.10
        )

        results.append({
            "anchor": label,
            "cutoffExclusive": cutoff,
            "originFamily":
                case["originFamily"],
            "filters": filters,

            "rowsBeforeDedupe":
                result["rowsBeforeDedupe"],
            "rows": result["rows"],

            "metricCoverage": coverage,
            "minimumMetricN": min_n,

            "score": result["score"],
            "medianRelativeError":
                median_error,
            "maxRelativeError":
                max_error,

            "numericStrong":
                numeric_strong,

            "metrics":
                result["metrics"],
        })

        if i % 100 == 0:
            print(
                f"  {i}/{len(cases)}"
            )


eligible = [
    r
    for r in results
    if r["score"] is not None
    and r["metricCoverage"] == len(A82)
    and r["minimumMetricN"] >= 30
]


eligible.sort(
    key=lambda r: r["score"]
)


(HERE / "date-sweep-results.json").write_text(
    json.dumps(
        {
            "anchors": ANCHORS,
            "populationDefinitions":
                len(cases),
            "resultCount":
                len(results),
            "results":
                results,
        },
        indent=2,
    )
)


with (
    HERE / "date-sweep-top.tsv"
).open("w") as f:

    f.write(
        "rank\tanchor\tcutoff_exclusive\t"
        "score\tmax_error\tmedian_error\t"
        "rows\tmin_metric_n\tstrong\t"
        "family\tducting\tahri_type\t"
        "energy_star\tcold_climate\t"
        "complete\tdedupe\n"
    )

    for rank, r in enumerate(
        eligible,
        1,
    ):
        c = r["filters"]

        f.write(
            f"{rank}\t"
            f"{r['anchor']}\t"
            f"{r['cutoffExclusive'] or 'current'}\t"
            f"{r['score']:.8f}\t"
            f"{r['maxRelativeError']:.8f}\t"
            f"{r['medianRelativeError']:.8f}\t"
            f"{r['rows']}\t"
            f"{r['minimumMetricN']}\t"
            f"{r['numericStrong']}\t"
            f"{r['originFamily']}\t"
            f"{c.get('ducting') or '*'}\t"
            f"{c.get('ahriType') or '*'}\t"
            f"{c.get('energyStar')}\t"
            f"{c.get('coldClimate')}\t"
            f"{c.get('completeMetrics')}\t"
            f"{c.get('dedupe')}\n"
        )


print()
print("=" * 110)
print("BEST BY HISTORICAL ANCHOR")
print("=" * 110)

for label, cutoff in ANCHORS:

    group = [
        r
        for r in eligible
        if r["anchor"] == label
    ]

    group.sort(
        key=lambda r: r["score"]
    )

    print()
    print(
        label,
        cutoff or "current",
    )

    for rank, r in enumerate(
        group[:10],
        1,
    ):
        c = r["filters"]

        print(
            f"{rank:>2} "
            f"score={r['score']:>7.3%} "
            f"max={r['maxRelativeError']:>7.3%} "
            f"med={r['medianRelativeError']:>7.3%} "
            f"n={r['minimumMetricN']:<6} "
            f"rows={r['rows']:<6} "
            f"strong={str(r['numericStrong']):<5} "
            f"duct={c.get('ducting') or '*'} | "
            f"ahri={c.get('ahriType') or '*'} | "
            f"ES={c.get('energyStar')} | "
            f"cold={c.get('coldClimate')} | "
            f"dedupe={c.get('dedupe')}"
        )


print()
print(
    "wrote:",
    HERE / "date-sweep-results.json",
)
print(
    "wrote:",
    HERE / "date-sweep-top.tsv",
)
