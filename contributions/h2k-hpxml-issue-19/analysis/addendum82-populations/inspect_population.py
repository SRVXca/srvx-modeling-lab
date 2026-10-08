from collections import Counter, defaultdict
from datetime import date

import run


rows = run.read_hp_rows()
base = run.base_population(rows)

cutoff = date(2024, 11, 22)

historical = [
    r for r in base
    if (d := run.source_date(r["Date Added to List"])) is not None
    and d < cutoff
]


print("\n=== DATE DISTRIBUTION: LIVE VARIABLE-CAPACITY ===")

years = Counter()

for r in base:
    d = run.source_date(r["Date Added to List"])
    years[d.year if d else "unknown"] += 1

for year, n in sorted(years.items(), key=lambda x: str(x[0])):
    print(year, n)


print("\n=== PRE-PDS01 COHORT ===")
print("rows:", len(historical))


def show(label, field, limit=30):
    print(f"\n-- {label} --")
    counts = Counter(
        str(r[field] or "<empty>")
        for r in historical
    )

    for value, n in counts.most_common(limit):
        print(f"{n:>5}  {value}")


show("Brand", "Brand Name")
show("Ducting configuration", "Ducting Configuration")
show("Indoor type", "Indoor Type")
show("AHRI type", "AHRI Type⁺")
show(
    "Cold climate",
    "ENERGY STAR Cold Climate Certified",
)


print("\n=== OUTDOOR-UNIT DUPLICATION ===")

groups = defaultdict(list)

for r in historical:
    key = (
        r["Brand Name"],
        r["Outdoor Unit Model Number⁺"],
    )
    groups[key].append(r)

sizes = Counter(len(v) for v in groups.values())

print("unique outdoor units:", len(groups))
print("AHRI rows per outdoor-unit distribution:")

for size, n in sorted(sizes.items()):
    print(f"{size:>3} rows -> {n:>4} outdoor units")


PERF_FIELDS = [
    "Min Capacity 47°F",
    "Rated Capacity 47°F⁺",
    "Max Capacity 47°F",
    "Input Power Min 47°F",
    "Input Power Rated 47°F",
    "Input Power Max 47°F",

    "Min Capacity 17°F",
    "Rated Capacity 17°F⁺",
    "Max Capacity 17°F",
    "Input Power Min 17°F",
    "Input Power Rated 17°F",
    "Input Power Max 17°F",

    "Min Capacity 5°F",
    "Rated Capacity 5°F - Optional⁺",
    "Max Capacity 5°F",
    "Input Power Min 5°F",
    "Input Power Rated 5°F - Optional",
    "Input Power Max 5°F",
]


print("\n=== PERFORMANCE VARIATION WITHIN SAME OUTDOOR UNIT ===")

same_surface = 0
multiple_surfaces = 0

examples = []

for key, group in groups.items():
    signatures = {
        tuple(r[f] for f in PERF_FIELDS)
        for r in group
    }

    if len(signatures) == 1:
        same_surface += 1
    else:
        multiple_surfaces += 1

        if len(examples) < 10:
            examples.append(
                (key, len(group), len(signatures))
            )

print("same performance surface:", same_surface)
print("multiple performance surfaces:", multiple_surfaces)

if examples:
    print("\nExamples:")
    for key, rows_n, surfaces_n in examples:
        print(
            key,
            "AHRI rows:", rows_n,
            "performance surfaces:", surfaces_n,
        )


print("\n=== UNIQUE PERFORMANCE SURFACES ===")

signatures = {
    tuple(r[f] for f in PERF_FIELDS)
    for r in historical
}

print("AHRI rows:", len(historical))
print("outdoor units:", len(groups))
print("unique performance surfaces:", len(signatures))
