import csv
import gzip
import re
from collections import defaultdict
from pathlib import Path

from run import read_hp_rows

CLUSTER = {
    ("mdv", "msep seris"),
    ("senville", "sen series"),
    ("comfortstar", "c series"),
    ("c&h", "ch series"),
    ("elios", "de-series"),
    ("moovair", "dm-series"),
    ("direct air", "dirm series"),
    ("bosch", "bms500"),
    ("breeze33", "bz33 series"),
    ("trust air conditioners", "m-series"),
    ("mrcool", "multi"),
    ("multi mfg", "mpc series"),
    ("ac pro", "a series"),
    ("kepler", "odu series"),
}

ES = (
    Path.home()
    / "nova-open/data/supply/air-source-heat-pump-v0.1/"
      "energy-star.csv.gz"
)


def txt(v):
    return str(v or "").strip()


def norm(v):
    return re.sub(r"[^a-z0-9]+", "", txt(v).lower())


def ahri(v):
    s = txt(v)

    if re.fullmatch(r"\d+(?:\.0+)?", s):
        return str(int(float(s)))

    digits = re.sub(r"\D", "", s)
    return digits or None


def get_col(headers, *parts):
    wanted = [norm(x) for x in parts]

    for h in headers:
        nh = norm(h)

        if all(x in nh for x in wanted):
            return h

    return None


# --------------------------------------------------
# NEEP side
# --------------------------------------------------

neep = defaultdict(lambda: {
    "owners": set(),
    "refs": set(),
    "outdoors": set(),
})

for r in read_hp_rows():
    key = (
        txt(r.get("Brand Name")).casefold(),
        txt(r.get("Series Name")).casefold(),
    )

    if key not in CLUSTER:
        continue

    label = (
        f"{txt(r.get('Brand Name'))} :: "
        f"{txt(r.get('Series Name'))}"
    )

    neep[label]["owners"].add(
        txt(r.get("Brand Owner"))
    )

    ref = ahri(
        r.get("AHRI Certified Reference Number⁺")
    )

    if ref:
        neep[label]["refs"].add(ref)

    outdoor = txt(
        r.get("Outdoor Unit Model Number⁺")
    )

    if outdoor:
        neep[label]["outdoors"].add(outdoor)


all_refs = {
    ref
    for data in neep.values()
    for ref in data["refs"]
}


print("NEEP cluster families:", len(neep))
print("unique AHRI refs:", len(all_refs))
print("ENERGY STAR:", ES)

if not ES.exists():
    raise SystemExit(
        f"\nMissing ENERGY STAR source:\n{ES}"
    )


# --------------------------------------------------
# ENERGY STAR side
# --------------------------------------------------

with gzip.open(
    ES,
    "rt",
    encoding="utf-8-sig",
    newline="",
) as f:

    reader = csv.DictReader(f)
    headers = reader.fieldnames or []

    cols = {
        "ahri": get_col(
            headers,
            "ahri",
            "reference",
        ),
        "partner": get_col(
            headers,
            "partner",
            "name",
        ),
        "manufacturer_type": get_col(
            headers,
            "manufacturer",
            "type",
        ),
        "series": get_col(
            headers,
            "series",
            "name",
        ),
        "outdoor_brand": get_col(
            headers,
            "outdoor",
            "brand",
        ),
        "outdoor_model": get_col(
            headers,
            "outdoor",
            "model",
        ),
        "indoor_brand": get_col(
            headers,
            "indoor",
            "brand",
        ),
        "indoor_model": get_col(
            headers,
            "indoor",
            "model",
        ),
    }

    print()
    print("=== ENERGY STAR COLUMN MAP ===")

    for k, v in cols.items():
        print(f"{k:20} {v}")

    if not cols["ahri"]:
        raise SystemExit(
            "\nCould not identify AHRI reference column."
        )

    es_by_ref = defaultdict(list)

    for row in reader:
        ref = ahri(row.get(cols["ahri"]))

        if ref in all_refs:
            es_by_ref[ref].append(row)


# --------------------------------------------------
# Report lineage per marketed family
# --------------------------------------------------

print()
print("=" * 100)
print("NEEP → AHRI → ENERGY STAR LINEAGE")
print("=" * 100)

for family in sorted(neep):
    data = neep[family]

    partners = set()
    mtypes = set()
    es_brands = set()
    es_models = set()

    matched_refs = 0

    for ref in data["refs"]:
        matches = es_by_ref.get(ref, [])

        if matches:
            matched_refs += 1

        for row in matches:
            if cols["partner"]:
                v = txt(row.get(cols["partner"]))
                if v:
                    partners.add(v)

            if cols["manufacturer_type"]:
                v = txt(
                    row.get(
                        cols["manufacturer_type"]
                    )
                )
                if v:
                    mtypes.add(v)

            if cols["outdoor_brand"]:
                v = txt(
                    row.get(cols["outdoor_brand"])
                )
                if v:
                    es_brands.add(v)

            if cols["outdoor_model"]:
                v = txt(
                    row.get(cols["outdoor_model"])
                )
                if v:
                    es_models.add(v)

    print()
    print(family)

    print(
        "  NEEP Brand Owner:",
        " | ".join(sorted(data["owners"]))
        or "-"
    )

    print(
        "  AHRI refs:",
        len(data["refs"]),
        "matched ENERGY STAR:",
        matched_refs,
    )

    print(
        "  ENERGY STAR Partner:",
        " | ".join(sorted(partners))
        or "-"
    )

    print(
        "  Manufacturer Type:",
        " | ".join(sorted(mtypes))
        or "-"
    )

    print(
        "  ENERGY STAR brands:",
        " | ".join(sorted(es_brands))
        or "-"
    )

    print("  NEEP outdoor models:")

    for model in sorted(data["outdoors"]):
        print("    ", model)

    if es_models:
        print("  ENERGY STAR outdoor models:")

        for model in sorted(es_models):
            print("    ", model)


# --------------------------------------------------
# Cross-family AHRI collisions
# --------------------------------------------------

ref_to_families = defaultdict(set)

for family, data in neep.items():
    for ref in data["refs"]:
        ref_to_families[ref].add(family)


print()
print("=" * 100)
print("AHRI REFERENCES SHARED ACROSS MARKETED FAMILIES")
print("=" * 100)

shared = {
    ref: fams
    for ref, fams in ref_to_families.items()
    if len(fams) > 1
}

if not shared:
    print("none")
else:
    for ref, fams in sorted(shared.items()):
        print()
        print("AHRI", ref)

        for family in sorted(fams):
            print("   ", family)
