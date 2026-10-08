from datetime import date
from statistics import mean, median

import run


CANMET = 0.563635566
OS_SINGLE_TWO = 0.626
OS_VARIABLE = 0.690


def ratio(a, b):
    a = run.number(a)
    b = run.number(b)

    if a is None or b is None or b == 0:
        return None

    return a / b


def percentile(values, p):
    xs = sorted(values)

    if not xs:
        return None

    k = (len(xs) - 1) * p
    lo = int(k)
    hi = min(lo + 1, len(xs) - 1)
    f = k - lo

    return xs[lo] * (1 - f) + xs[hi] * f


def analyze(name, rows):
    q17q47 = []
    q5q47 = []

    for r in rows:
        r17 = ratio(
            r["Rated Capacity 17°F⁺"],
            r["Rated Capacity 47°F⁺"],
        )

        r5 = ratio(
            r["Rated Capacity 5°F - Optional⁺"],
            r["Rated Capacity 47°F⁺"],
        )

        if r17 is not None:
            q17q47.append(r17)

        if r5 is not None:
            q5q47.append(r5)

    print()
    print("=" * 90)
    print(name)
    print("rows:", len(rows))
    print("=" * 90)

    print("Q17full / Q47full")
    print("n:      ", len(q17q47))
    print("mean:   ", f"{mean(q17q47):.6f}")
    print("median: ", f"{median(q17q47):.6f}")
    print("p10:    ", f"{percentile(q17q47, .10):.6f}")
    print("p90:    ", f"{percentile(q17q47, .90):.6f}")

    for label, threshold in [
        ("Canmet 0.563636", CANMET),
        ("OS single/two 0.626", OS_SINGLE_TWO),
        ("OS variable 0.690", OS_VARIABLE),
    ]:
        above = sum(x > threshold for x in q17q47)

        print(
            f"above {label:<20}",
            f"{above / len(q17q47):.2%}",
        )

    if q5q47:
        print()
        print("Q5full / Q47full")
        print("n:      ", len(q5q47))
        print("mean:   ", f"{mean(q5q47):.6f}")
        print("median: ", f"{median(q5q47):.6f}")
        print("p10:    ", f"{percentile(q5q47, .10):.6f}")
        print("p90:    ", f"{percentile(q5q47, .90):.6f}")


rows = run.read_hp_rows()
base = run.base_population(rows)

historical = [
    r for r in base
    if (
        (d := run.source_date(r["Date Added to List"]))
        is not None
        and d < date(2024, 11, 22)
    )
]

analyze(
    "NEEP 2026 Live variable-capacity",
    base,
)

analyze(
    "NEEP 2026 Live variable-capacity, unique outdoor",
    run.dedupe(base, "outdoor"),
)

analyze(
    "Pre-PDS01 survivors",
    historical,
)

analyze(
    "Pre-PDS01 survivors, unique outdoor",
    run.dedupe(historical, "outdoor"),
)
