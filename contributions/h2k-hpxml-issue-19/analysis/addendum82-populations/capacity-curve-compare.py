from statistics import mean

from run import (
    A82,
    base_population,
    metrics,
    number,
    read_hp_rows,
)

GROUPS = [
    (
        "single-zone ceiling",
        "Singlezone Non-Ducted, Ceiling Placement",
    ),
    (
        "multisplit non-ducted",
        "Multizone All Non-Ducted",
    ),
]

BINS = [
    ("<12k",        0, 12000),
    ("12-18k",  12000, 18000),
    ("18-24k",  18000, 24000),
    ("24-36k",  24000, 36000),
    ("36-48k",  36000, 48000),
    ("48-65k",  48000, 65000),
    ("65k+",    65000, 10**9),
]


def cap(r):
    return number(r["Rated Capacity 47°F⁺"])


def hardware_dedupe(rows):
    seen = set()
    out = []

    for r in rows:
        model = str(
            r["Outdoor Unit Model Number⁺"] or ""
        ).strip()

        # Missing identity: retain the row.
        if not model:
            out.append(r)
            continue

        if model in seen:
            continue

        seen.add(model)
        out.append(r)

    return out


def metric_means(rows):
    values = {
        key: []
        for key in A82
    }

    for r in rows:
        m = metrics(r)

        for key in A82:
            if m[key] is not None:
                values[key].append(m[key])

    return {
        key: (
            mean(xs)
            if xs
            else None
        )
        for key, xs in values.items()
    }


def relative_distance(a, b):
    errors = []

    for key in A82:
        x = a[key]
        y = b[key]

        if x is None or y is None or y == 0:
            continue

        errors.append(
            abs(x - y) / abs(y)
        )

    return (
        mean(errors)
        if errors
        else None
    )


def a82_distance(m):
    errors = []

    for key, target in A82.items():
        value = m[key]

        if value is None:
            continue

        errors.append(
            abs(value - target)
            / abs(target)
        )

    return mean(errors)


base = base_population(
    read_hp_rows()
)


for group_name, ducting in GROUPS:

    population = [
        r
        for r in base
        if r["Ducting Configuration"] == ducting
        and (
            r[
                "ENERGY STAR Cold Climate Certified"
            ]
            is False
        )
        and cap(r) is not None
        and all(
            v is not None
            for v in metrics(r).values()
        )
    ]

    print()
    print("=" * 100)
    print(group_name.upper())
    print(ducting)
    print("=" * 100)

    if not population:
        print("NO ROWS")
        continue

    print(
        "complete non-cold rows:",
        len(population),
    )
    print(
        "capacity range:",
        min(cap(r) for r in population),
        "to",
        max(cap(r) for r in population),
    )

    for weighting in (
        "rows",
        "hardware",
    ):

        source = (
            population
            if weighting == "rows"
            else hardware_dedupe(population)
        )

        print()
        print(
            f"--- weighting: {weighting} "
            f"(N={len(source)}) ---"
        )

        results = []

        for label, lo, hi in BINS:
            subset = [
                r
                for r in source
                if lo <= cap(r) < hi
            ]

            if not subset:
                continue

            m = metric_means(subset)

            results.append({
                "label": label,
                "rows": subset,
                "metrics": m,
                "a82": a82_distance(m),
            })

        reference = next(
            (
                x
                for x in results
                if x["label"] == "18-24k"
            ),
            None,
        )

        if reference is None:
            print(
                "No 18-24k reference population."
            )
            continue

        ref = reference["metrics"]

        print()
        print(
            f"{'band':>9} "
            f"{'N':>5} "
            f"{'mean47':>9} "
            f"{'vs18-24':>10} "
            f"{'vsA82':>9}"
        )

        for x in results:
            distance = relative_distance(
                x["metrics"],
                ref,
            )

            print(
                f"{x['label']:>9} "
                f"{len(x['rows']):>5} "
                f"{mean(cap(r) for r in x['rows']):>9.0f} "
                f"{distance:>9.3%} "
                f"{x['a82']:>8.3%}"
            )

        print()
        print(
            "NORMALIZED CURVE BY CAPACITY"
        )

        labels = [
            x["label"]
            for x in results
        ]

        print(
            f"{'metric':<13}"
            + "".join(
                f"{label:>11}"
                for label in labels
            )
        )

        for key in A82:
            print(
                f"{key:<13}",
                end="",
            )

            for x in results:
                value = x["metrics"][key]

                print(
                    f"{value:>11.3f}",
                    end="",
                )

            print()

        print()
        print(
            "DELTA VS 18-24k CURVE"
        )

        print(
            f"{'metric':<13}"
            + "".join(
                f"{label:>11}"
                for label in labels
            )
        )

        for key in A82:
            print(
                f"{key:<13}",
                end="",
            )

            rv = ref[key]

            for x in results:
                value = x["metrics"][key]

                delta = (
                    (value - rv)
                    / abs(rv)
                )

                print(
                    f"{delta:>10.1%} ",
                    end="",
                )

            print()
