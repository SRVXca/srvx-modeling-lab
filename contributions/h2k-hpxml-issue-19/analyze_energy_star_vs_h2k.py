#!/usr/bin/env python3

import csv
import gzip
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


SNAPSHOT = (
    Path.home()
    / "nova-open"
    / "data"
    / "supply"
    / "air-source-heat-pump-v0.1"
)

CSV_PATH = SNAPSHOT / "energy-star.csv.gz"
METADATA_PATH = SNAPSHOT / "metadata.json.gz"
MANIFEST_PATH = SNAPSHOT / "source.json"

REPORT_PATH = Path(__file__).with_name(
    "energy-star-vs-h2k.md"
)

CANMET_17F_FRACTION = 0.563635566

# OpenStudio-HPXML v1.12.0 defaults for
# HeatingCapacityFraction17F when no explicit
# low-temperature capacity information is provided.
OS_DEFAULT_SINGLE_TWO_STAGE_17F = 0.626
OS_DEFAULT_VARIABLE_SPEED_17F = 0.690


def h2k_capacity_multiplier(t_c: float) -> float:
    """
    Legacy NRCan/H3K ASHP capacity equation.

    ASHP_CAP from ESP-r CANMET source:
      Q(T) / Qrated =
          a + bT + cT^2 + dT^3 + eT^4
    """
    return (
        0.766836
        + 0.027487 * t_c
        + 0.00028936 * t_c**2
        - 1.4658e-5 * t_c**3
        - 5.65296e-7 * t_c**4
    )


# Use the same rounded Celsius temperatures implicated
# by the historical Canmet constant.
H2K_47F_DIRECT = h2k_capacity_multiplier(8.333)
H2K_17F_DIRECT = h2k_capacity_multiplier(-8.333)
H2K_5F_DIRECT = h2k_capacity_multiplier(-15.0)

H2K_17_OVER_47 = (
    H2K_17F_DIRECT / H2K_47F_DIRECT
)

H2K_5_OVER_47 = (
    H2K_5F_DIRECT / H2K_47F_DIRECT
)


def parse_number(value):
    if value is None:
        return None

    value = value.strip()

    if value == "":
        return None

    try:
        number = float(value)
    except ValueError:
        return None

    if not math.isfinite(number):
        return None

    return number


def percentile(sorted_values, p):
    if not sorted_values:
        return None

    if len(sorted_values) == 1:
        return sorted_values[0]

    position = (
        (len(sorted_values) - 1) * p
    )

    lower = math.floor(position)
    upper = math.ceil(position)

    if lower == upper:
        return sorted_values[lower]

    weight = position - lower

    return (
        sorted_values[lower] * (1 - weight)
        + sorted_values[upper] * weight
    )


def summarize(values):
    values = sorted(values)

    if not values:
        return None

    return {
        "n": len(values),
        "min": values[0],
        "p10": percentile(values, 0.10),
        "p25": percentile(values, 0.25),
        "median": percentile(values, 0.50),
        "p75": percentile(values, 0.75),
        "p90": percentile(values, 0.90),
        "max": values[-1],
        "mean": sum(values) / len(values),
    }


def ratio_comparison(values, baseline):
    if not values:
        return None

    above = sum(v > baseline for v in values)
    below = sum(v < baseline for v in values)
    equal = len(values) - above - below

    med = summarize(values)["median"]

    return {
        "baseline": baseline,
        "above": above,
        "below": below,
        "equal": equal,
        "above_pct": 100 * above / len(values),
        "below_pct": 100 * below / len(values),
        "median_delta": med - baseline,
        "median_relative_pct":
            100 * (med / baseline - 1),
        "mean_absolute_delta":
            sum(abs(v - baseline) for v in values)
            / len(values),
    }


def fmt(value, digits=4):
    if value is None:
        return "—"

    return f"{value:.{digits}f}"


def stats_row(label, values):
    s = summarize(values)

    if s is None:
        return (
            f"| {label} | 0 | — | — | — | "
            f"— | — | — | — | — |"
        )

    return (
        f"| {label} "
        f"| {s['n']:,} "
        f"| {fmt(s['mean'])} "
        f"| {fmt(s['p10'])} "
        f"| {fmt(s['p25'])} "
        f"| {fmt(s['median'])} "
        f"| {fmt(s['p75'])} "
        f"| {fmt(s['p90'])} "
        f"| {fmt(s['min'])} "
        f"| {fmt(s['max'])} |"
    )


def comparison_row(label, values, baseline):
    c = ratio_comparison(
        values,
        baseline,
    )

    return (
        f"| {label} "
        f"| {baseline:.9f} "
        f"| {c['median_delta']:+.4f} "
        f"| {c['median_relative_pct']:+.1f}% "
        f"| {c['below_pct']:.1f}% "
        f"| {c['above_pct']:.1f}% "
        f"| {c['mean_absolute_delta']:.4f} |"
    )


manifest = json.loads(
    MANIFEST_PATH.read_text(
        encoding="utf-8",
    )
)

with gzip.open(
    METADATA_PATH,
    "rt",
    encoding="utf-8",
) as f:
    metadata = json.load(f)

field_to_display = {
    column["fieldName"]: column["name"]
    for column in metadata["columns"]
}

required_fields = [
    "pd_id",
    "ahri_reference_number",
    "product_type",
    "compressor_staging",
    "cold_climate",
    "heating_capacity_at_47_f_btu_h",
    "heating_capacity_at_17_f_btu_h",
    "heating_capacity_at_5_f_btu_h",
]

missing_fields = [
    field
    for field in required_fields
    if field not in field_to_display
]

if missing_fields:
    raise RuntimeError(
        "Missing ENERGY STAR fields: "
        + ", ".join(missing_fields)
    )


def source_value(row, field_name):
    return row.get(
        field_to_display[field_name],
        "",
    )


rows_seen = 0

raw_17 = []
raw_5 = []

groups_17 = defaultdict(list)
groups_5 = defaultdict(list)

# Preserve source strings when deciding whether
# multiple ENERGY STAR rows disagree about one AHRI.
ahri_pairs_17 = defaultdict(set)
ahri_pairs_5 = defaultdict(set)

# Preserve classification separately so the grouped
# statistics can also be AHRI-deduped.
ahri_groups_17 = defaultdict(set)
ahri_groups_5 = defaultdict(set)

rows_without_ahri = 0

samsung = None


with gzip.open(
    CSV_PATH,
    "rt",
    encoding="utf-8-sig",
    newline="",
) as f:
    reader = csv.DictReader(f)

    for row in reader:
        rows_seen += 1

        pd_id = source_value(
            row,
            "pd_id",
        ).strip()

        ahri = source_value(
            row,
            "ahri_reference_number",
        ).strip()

        product_type = source_value(
            row,
            "product_type",
        ).strip() or "(blank)"

        compressor = source_value(
            row,
            "compressor_staging",
        ).strip() or "(blank)"

        cold = source_value(
            row,
            "cold_climate",
        ).strip() or "(blank)"

        q47_raw = source_value(
            row,
            "heating_capacity_at_47_f_btu_h",
        ).strip()

        q17_raw = source_value(
            row,
            "heating_capacity_at_17_f_btu_h",
        ).strip()

        q5_raw = source_value(
            row,
            "heating_capacity_at_5_f_btu_h",
        ).strip()

        q47 = parse_number(q47_raw)
        q17 = parse_number(q17_raw)
        q5 = parse_number(q5_raw)

        group = (
            product_type,
            compressor,
            cold,
        )

        ratio17 = None
        ratio5 = None

        if (
            q47 is not None
            and q47 > 0
            and q17 is not None
            and q17 > 0
        ):
            ratio17 = q17 / q47

            # Deliberately do NOT clip ratios > 1.
            raw_17.append(ratio17)
            groups_17[group].append(
                ratio17
            )

            if ahri:
                ahri_pairs_17[ahri].add(
                    (q47_raw, q17_raw)
                )
                ahri_groups_17[ahri].add(
                    group
                )

        if (
            q47 is not None
            and q47 > 0
            and q5 is not None
            and q5 > 0
        ):
            ratio5 = q5 / q47

            raw_5.append(ratio5)
            groups_5[group].append(
                ratio5
            )

            if ahri:
                ahri_pairs_5[ahri].add(
                    (q47_raw, q5_raw)
                )
                ahri_groups_5[ahri].add(
                    group
                )

        if not ahri:
            rows_without_ahri += 1

        if ahri == "210448841":
            samsung = {
                "pd_id": pd_id,
                "q47": q47,
                "q17": q17,
                "q5": q5,
                "ratio17": ratio17,
                "ratio5": ratio5,
                "product_type": product_type,
                "compressor": compressor,
                "cold": cold,
            }


if rows_seen != manifest["rows"]:
    raise RuntimeError(
        f"Expected {manifest['rows']} rows, "
        f"read {rows_seen}"
    )


def dedupe_pairs(mapping):
    values = []
    conflicts = {}

    for ahri, pairs in mapping.items():
        if len(pairs) == 1:
            numerator_base, numerator_low = (
                next(iter(pairs))
            )

            q_base = parse_number(
                numerator_base
            )
            q_low = parse_number(
                numerator_low
            )

            if (
                q_base is not None
                and q_base > 0
                and q_low is not None
                and q_low > 0
            ):
                values.append(
                    q_low / q_base
                )

        else:
            conflicts[ahri] = sorted(pairs)

    return values, conflicts


dedup_17, conflicts_17 = dedupe_pairs(
    ahri_pairs_17
)

dedup_5, conflicts_5 = dedupe_pairs(
    ahri_pairs_5
)


def dedupe_grouped_pairs(
    pair_mapping,
    group_mapping,
):
    grouped = defaultdict(list)
    ambiguous_group_ahri = 0

    for ahri, pairs in pair_mapping.items():
        # Pair conflicts are already counted separately.
        if len(pairs) != 1:
            continue

        groups = group_mapping.get(
            ahri,
            set(),
        )

        # Do not arbitrarily assign one AHRI to a class
        # if ENERGY STAR rows disagree on classification.
        if len(groups) != 1:
            if len(groups) > 1:
                ambiguous_group_ahri += 1
            continue

        q47_raw, qlow_raw = next(
            iter(pairs)
        )

        q47 = parse_number(q47_raw)
        qlow = parse_number(qlow_raw)

        if (
            q47 is None
            or q47 <= 0
            or qlow is None
            or qlow <= 0
        ):
            continue

        group = next(iter(groups))

        grouped[group].append(
            qlow / q47
        )

    return grouped, ambiguous_group_ahri


dedup_groups_17, ambiguous_groups_17 = (
    dedupe_grouped_pairs(
        ahri_pairs_17,
        ahri_groups_17,
    )
)

dedup_groups_5, ambiguous_groups_5 = (
    dedupe_grouped_pairs(
        ahri_pairs_5,
        ahri_groups_5,
    )
)


def os_default_17f(compressor):
    value = compressor.lower()

    if (
        "single" in value
        or "two-stage" in value
        or "two stage" in value
    ):
        return OS_DEFAULT_SINGLE_TWO_STAGE_17F

    if (
        "continuous" in value
        or "variable" in value
    ):
        return OS_DEFAULT_VARIABLE_SPEED_17F

    return None


def group_rows(groups, limit=15):
    rows = []

    ordered = sorted(
        groups.items(),
        key=lambda item: len(item[1]),
        reverse=True,
    )

    for (
        product_type,
        compressor,
        cold,
    ), values in ordered:
        if len(values) < 100:
            continue

        stats = summarize(values)
        os_default = os_default_17f(
            compressor
        )

        rows.append(
            "| "
            + " | ".join(
                [
                    product_type,
                    compressor,
                    cold,
                    f"{stats['n']:,}",
                    fmt(
                        CANMET_17F_FRACTION,
                        3,
                    ),
                    (
                        fmt(os_default, 3)
                        if os_default is not None
                        else "—"
                    ),
                    fmt(stats["p10"]),
                    fmt(stats["median"]),
                    fmt(stats["p90"]),
                ]
            )
            + " |"
        )

        if len(rows) >= limit:
            break

    return rows


report = []

report.append(
    "# ENERGY STAR ASHP vs legacy H2K "
    "low-temperature capacity"
)

report.append("")
report.append(
    "Generated: "
    + datetime.now(
        timezone.utc
    ).isoformat()
)

report.append("")
report.append(
    "This analysis is an upstream contribution "
    "artifact for `canmet-energy/h2k-hpxml` "
    "issue #19. It is independent of SRVX "
    "normalization/canonicalization."
)

report.append("")
report.append("## Dataset")

report.append("")
report.append(
    f"- ENERGY STAR snapshot rows: "
    f"**{rows_seen:,}**"
)

report.append(
    f"- Rows without AHRI reference: "
    f"**{rows_without_ahri:,}**"
)

report.append(
    f"- Usable row-level 17°F/47°F ratios: "
    f"**{len(raw_17):,}**"
)

report.append(
    f"- Usable row-level 5°F/47°F ratios: "
    f"**{len(raw_5):,}**"
)

report.append(
    f"- Unambiguous AHRI 17°F/47°F ratios: "
    f"**{len(dedup_17):,}**"
)

report.append(
    f"- AHRI capacity-pair conflicts for "
    f"17°F/47°F: "
    f"**{len(conflicts_17):,}**"
)

report.append(
    f"- AHRI classification conflicts excluded "
    f"from 17°F grouped statistics: "
    f"**{ambiguous_groups_17:,}**"
)

report.append(
    f"- Unambiguous AHRI 5°F/47°F ratios: "
    f"**{len(dedup_5):,}**"
)

report.append(
    f"- AHRI capacity-pair conflicts for "
    f"5°F/47°F: "
    f"**{len(conflicts_5):,}**"
)

report.append(
    f"- AHRI classification conflicts excluded "
    f"from 5°F grouped statistics: "
    f"**{ambiguous_groups_5:,}**"
)

report.append("")
report.append("## Legacy H2K curve")

report.append("")
report.append(
    "| Quantity | Value |"
)
report.append(
    "|---|---:|"
)
report.append(
    f"| H2K direct multiplier @ 47°F "
    f"| {H2K_47F_DIRECT:.9f} |"
)
report.append(
    f"| H2K direct multiplier @ 17°F "
    f"| {H2K_17F_DIRECT:.9f} |"
)
report.append(
    f"| Canmet hardcoded 17°F fraction "
    f"| {CANMET_17F_FRACTION:.9f} |"
)
report.append(
    f"| H2K direct multiplier @ 5°F "
    f"| {H2K_5F_DIRECT:.9f} |"
)
report.append(
    f"| H2K normalized 17°F / 47°F "
    f"| {H2K_17_OVER_47:.9f} |"
)
report.append(
    f"| H2K normalized 5°F / 47°F "
    f"| {H2K_5_OVER_47:.9f} |"
)

report.append("")
report.append(
    "The Canmet constant matches the legacy "
    "H2K curve evaluated directly at 17°F. "
    "It is not exactly the same as normalizing "
    "the legacy curve's 17°F value against its "
    "47°F value because the old polynomial "
    "evaluates slightly above 1.0 at 47°F."
)

report.append("")
report.append(
    "## OpenStudio-HPXML v1.12 defaults"
)

report.append("")
report.append(
    "| Compressor type | Default 17°F / 47°F |"
)
report.append(
    "|---|---:|"
)
report.append(
    f"| Single-stage | "
    f"{OS_DEFAULT_SINGLE_TWO_STAGE_17F:.3f} |"
)
report.append(
    f"| Two-stage | "
    f"{OS_DEFAULT_SINGLE_TWO_STAGE_17F:.3f} |"
)
report.append(
    f"| Variable-speed | "
    f"{OS_DEFAULT_VARIABLE_SPEED_17F:.3f} |"
)

report.append("")
report.append(
    "These are OpenStudio-HPXML defaults used only "
    "when explicit 17°F capacity information, an "
    "explicit 17°F fraction, and suitable detailed "
    "performance data are absent."
)

report.append("")
report.append(
    "## ENERGY STAR distributions"
)

report.append("")
report.append(
    "| Population | n | mean | p10 | p25 | "
    "median | p75 | p90 | min | max |"
)
report.append(
    "|---|---:|---:|---:|---:|---:|---:|"
    "---:|---:|---:|"
)

report.append(
    stats_row(
        "17°F / 47°F — raw rows",
        raw_17,
    )
)

report.append(
    stats_row(
        "17°F / 47°F — AHRI deduped",
        dedup_17,
    )
)

report.append(
    stats_row(
        "5°F / 47°F — raw rows",
        raw_5,
    )
)

report.append(
    stats_row(
        "5°F / 47°F — AHRI deduped",
        dedup_5,
    )
)

report.append("")
report.append(
    "## Baseline comparison"
)

report.append("")
report.append(
    "| Comparison | baseline | median − baseline "
    "| median relative difference | below baseline "
    "| above baseline | mean absolute delta |"
)
report.append(
    "|---|---:|---:|---:|---:|---:|---:|"
)

report.append(
    comparison_row(
        "Certified 17/47 vs Canmet translator",
        dedup_17,
        CANMET_17F_FRACTION,
    )
)

report.append(
    comparison_row(
        "Certified 17/47 vs normalized H2K curve",
        dedup_17,
        H2K_17_OVER_47,
    )
)

report.append(
    comparison_row(
        "Certified 5/47 vs normalized H2K curve",
        dedup_5,
        H2K_5_OVER_47,
    )
)

report.append("")
report.append(
    "Ratios greater than 1.0 are retained; "
    "the analysis does not assume they are errors."
)

report.append("")
report.append(
    "## Largest ENERGY STAR groups — "
    "17°F / 47°F, AHRI-deduped"
)

report.append("")
report.append(
    "| Product type | Compressor staging "
    "| Cold climate | n | Canmet | OS v1.12 default "
    "| p10 | median | p90 |"
)
report.append(
    "|---|---|---|---:|---:|---:|---:|---:|---:|"
)

report.extend(
    group_rows(dedup_groups_17)
)

report.append("")
report.append(
    "## Largest ENERGY STAR groups — "
    "5°F / 47°F, AHRI-deduped"
)

report.append("")
report.append(
    "| Product type | Compressor staging "
    "| Cold climate | n | Canmet 17°F* "
    "| OS v1.12 17°F default* | p10 | median | p90 |"
)
report.append(
    "|---|---|---|---:|---:|---:|---:|---:|---:|"
)

report.extend(
    group_rows(dedup_groups_5)
)

report.append("")
report.append(
    "\\* Canmet and OpenStudio columns are 17°F "
    "references shown only for context; neither is "
    "a 5°F translator input. The 5°F ENERGY STAR "
    "distribution is compared to the legacy H2K "
    "curve separately above."
)

if samsung is not None:
    report.append("")
    report.append(
        "## Exact h2k-hpxml MURB fixture match"
    )

    report.append("")
    report.append(
        "- AHRI: `210448841`"
    )
    report.append(
        f"- ENERGY STAR pd_id: "
        f"`{samsung['pd_id']}`"
    )
    report.append(
        f"- Product type: "
        f"`{samsung['product_type']}`"
    )
    report.append(
        f"- Compressor: "
        f"`{samsung['compressor']}`"
    )
    report.append(
        f"- Cold climate: "
        f"`{samsung['cold']}`"
    )
    report.append(
        f"- Q47: **{samsung['q47']:.0f} Btu/h**"
    )
    report.append(
        f"- Q17: **{samsung['q17']:.0f} Btu/h**"
    )
    report.append(
        f"- Q5: **{samsung['q5']:.0f} Btu/h**"
    )
    report.append(
        f"- Q17/Q47: "
        f"**{samsung['ratio17']:.9f}**"
    )
    report.append(
        f"- Q5/Q47: "
        f"**{samsung['ratio5']:.9f}**"
    )

report.append("")
report.append(
    "## Interpretation guardrail"
)

report.append("")
report.append(
    "This analysis compares certified equipment "
    "capacity *shape* with the low-temperature "
    "capacity fraction consumed by "
    "OpenStudio-HPXML. It does not replace the "
    "H2K user-entered nominal capacity with the "
    "ENERGY STAR nameplate capacity."
)

REPORT_PATH.write_text(
    "\n".join(report) + "\n",
    encoding="utf-8",
)

print("ENERGY STAR vs H2K analysis OK")
print("rows:", rows_seen)
print(
    "17/47 raw:",
    len(raw_17),
)
print(
    "17/47 AHRI deduped:",
    len(dedup_17),
)
print(
    "17/47 conflicts:",
    len(conflicts_17),
)
print(
    "5/47 raw:",
    len(raw_5),
)
print(
    "5/47 AHRI deduped:",
    len(dedup_5),
)
print(
    "5/47 conflicts:",
    len(conflicts_5),
)
print()
print(
    "H2K direct 17F:",
    f"{H2K_17F_DIRECT:.12f}",
)
print(
    "Canmet constant:",
    f"{CANMET_17F_FRACTION:.12f}",
)
print(
    "H2K normalized 17/47:",
    f"{H2K_17_OVER_47:.12f}",
)
print(
    "H2K normalized 5/47:",
    f"{H2K_5_OVER_47:.12f}",
)
print()
print(
    "ENERGY STAR AHRI-deduped 17/47:",
    summarize(dedup_17),
)
print()
print(
    "ENERGY STAR AHRI-deduped 5/47:",
    summarize(dedup_5),
)
print()
print("report:", REPORT_PATH)
