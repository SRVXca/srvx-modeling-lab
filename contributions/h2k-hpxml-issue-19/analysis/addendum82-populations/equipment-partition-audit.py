from collections import Counter

from run import (
    base_population,
    number,
    read_hp_rows,
)


rows = list(base_population(read_hp_rows()))


def text(v):
    return str(v or "").strip()


fields = sorted({
    field
    for r in rows
    for field in r
})


print("rows:", len(rows))
print("fields:", len(fields))


# ------------------------------------------------------------
# Discover categorical fields automatically.
# ------------------------------------------------------------

candidates = []

for field in fields:

    values = [
        text(r.get(field))
        for r in rows
        if text(r.get(field))
    ]

    if len(values) < 100:
        continue

    unique = set(values)

    numeric = sum(
        number(v) is not None
        for v in values
    )

    numeric_ratio = (
        numeric / len(values)
    )

    # Useful categorical vocabulary:
    # not mostly numeric and not essentially an ID/model field.
    if (
        2 <= len(unique) <= 100
        and numeric_ratio < 0.25
    ):
        candidates.append(
            (
                field,
                len(values),
                len(unique),
                numeric_ratio,
            )
        )


print()
print("=" * 110)
print("CANDIDATE PARTITION FIELDS")
print("=" * 110)

print(
    f"{'field':<60}"
    f"{'present':>12}"
    f"{'unique':>10}"
    f"{'numeric':>10}"
)

for field, present, unique, numeric_ratio in candidates:

    print(
        f"{field:<60}"
        f"{present:>12}"
        f"{unique:>10}"
        f"{numeric_ratio:>9.1%}"
    )


# ------------------------------------------------------------
# Fields whose names are especially relevant to equipment
# architecture / component identity.
# ------------------------------------------------------------

keywords = (
    "duct",
    "zone",
    "type",
    "configuration",
    "indoor",
    "outdoor",
    "refriger",
    "compressor",
    "equipment",
    "application",
    "ahri",
    "furnace",
    "air handler",
    "handler",
    "capacity",
    "variable",
    "climate",
)


interesting = [
    field
    for field in fields
    if any(
        keyword in field.casefold()
        for keyword in keywords
    )
]


print()
print("=" * 110)
print("ARCHITECTURE / COMPONENT FIELD INVENTORY")
print("=" * 110)

for field in interesting:

    values = [
        text(r.get(field))
        for r in rows
        if text(r.get(field))
    ]

    if not values:
        continue

    counts = Counter(values)

    print()
    print(field)

    print(
        "  present:",
        len(values),
        f"({len(values) / len(rows):.1%})",
    )

    print(
        "  unique:",
        len(counts),
    )

    # Don't dump thousands of model numbers.
    for value, count in counts.most_common(20):

        print(
            f"    {count:>8}  {value}"
        )


# ------------------------------------------------------------
# Exact source field list for us to inspect.
# ------------------------------------------------------------

print()
print("=" * 110)
print("ALL SOURCE FIELDS")
print("=" * 110)

for field in fields:
    print(field)
