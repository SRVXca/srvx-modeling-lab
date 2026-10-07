# h2k-hpxml issue #19 — Low-temperature ASHP capacity

This directory is independent of SRVX Supply normalization/canonicalization.

Purpose:
- investigate canmet-energy/h2k-hpxml issue #19;
- quantify low-temperature ASHP capacity behavior using public certification data;
- compare existing h2k-hpxml assumptions with available evidence;
- prepare a reproducible upstream report and, if appropriate, code/tests.

## Upstream issue

canmet-energy/h2k-hpxml#19:
H2K files do not provide the HPXML low-temperature ASHP capacity input.

Current translator behavior observed in `system_heat_pumps.py`:
- mini-split ASHP:
  `HeatingCapacityFraction17F = 0.563635566`
- air-to-air ASHP:
  `HeatingCapacityFraction17F = 0.563635566`

The comment describes this value as based on the H2K heat-pump curve.

## Initial ENERGY STAR evidence

Dataset:
EPA ENERGY STAR Air-Source Heat Pumps
Socrata dataset `83eb-xbyy`

Snapshot analyzed:
- 284,866 ENERGY STAR rows
- 284,430 distinct AHRI references
- 282,929 rows with usable 47°F + 17°F heating capacity
- 282,519 unambiguous AHRI references with usable 47°F + 17°F capacity
- 5 AHRI references with conflicting 47°F/17°F capacity pairs

Initial 17°F / 47°F capacity ratios by class:

- HP - Split System / continuously variable / cold climate:
  median 0.8265, n=121,092
- HP - Split System / two-stage / non-cold-climate:
  median 0.6384, n=63,452
- HP - Split System / single-stage / non-cold-climate:
  median 0.6500, n=50,461
- HP - Split System / continuously variable / non-cold-climate:
  median 0.8193, n=19,819
- HP - Mini or Multi Split / continuously variable / cold climate:
  median 0.8250, n=14,821
- HP - Split System / two-stage / cold climate:
  median 0.9573, n=9,436
- HP - Mini or Multi Split / continuously variable / non-cold-climate:
  median 0.7000, n=2,578

## Exact repository fixture example

MURB.h2k contains AHRI reference:

`210448841`

ENERGY STAR record:

- Samsung AR12CSFCMWKX / AR12CSFCMWKN
- mini/multi-split
- continuously variable
- non-cold-climate
- 47°F heating capacity: 12,000 Btu/h
- 17°F heating capacity: 11,000 Btu/h
- 5°F heating capacity: 9,900 Btu/h

Therefore:

17°F / 47°F certified capacity ratio:

`11000 / 12000 = 0.916667`

Current h2k-hpxml value:

`0.563635566`

This exact fixture therefore provides a useful validation case, but the
certified ENERGY STAR nominal capacity must not automatically replace the H2K
user-entered system capacity. The ratio/performance shape and the H2K capacity
input are separate questions.

## Before proposing a patch

Still verify:

- exact HPXML/OpenStudio semantics of `HeatingCapacityFraction17F`;
- why issue #19 discusses default retention at 5°F while the translator
  currently emits a 17°F fraction;
- whether the H2K heat-pump curve actually supports the current
  `0.563635566` value at 17°F;
- suitable grouping/fallback methodology;
- outliers and duplicate/certification-version behavior;
- whether exact AHRI enrichment belongs in this repository or whether the
  contribution should remain a better deterministic fallback;
- tests and backwards-compatibility implications.

No SRVX canonical or normalization assumptions belong in this analysis.
