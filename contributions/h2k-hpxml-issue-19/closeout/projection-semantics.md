# Projection semantics

Task scope dated October 8, 2026; modeling-lab evidence, not canonical SRVX equipment truth.

## Capacity basis established for this fixture

The freshly translated pinned MURB input stores `AirHeatPump/Specifications/OutputCapacity/@value=14.0334`. The translator's `config_numeric.json` defines that stored field in **kW**, regardless of its UI display label `uiUnits="btu/hr"`, and converts it to `HeatingCapacity` in Btu/h. The fixture declares `Temperature/RatingType/@value=8.3333`, labelled **8.3°C / 47°F**, with `OutputCapacity/English=User-Specified`. The actual output is **47,883.93 Btu/h** for heating and cooling.

HPXML `HeatingCapacity` is the model's nominal heating output capacity. The installed v1.12.0 consumer uses it as the rated 47°F reference. Its `Defaults.expand_detailed_performance_data(:htg, ...)` converts each fraction to `(fraction * HeatingCapacity).round`. The Schematron separately checks that an explicit nominal 47°F point equals `HeatingCapacity`, or has `CapacityFractionOfNominal≈1`. This provides an executable reference-basis check rather than relying only on naming.

The ENERGY STAR reference is a distinct certificate: 12,000 Btu/h at 47°F, 11,000 at 17°F and 9,900 at 5°F. MURB declares AHRI 210448841 and the same outdoor/indoor model strings, with two heads. This supports source identity continuity; **it does not reconcile the physical installed size, quantity or multi-head configuration**. No head-count multiplication or nominal-capacity replacement is performed.

## What is projected

- Rated 17°F shape: **11,000 / 12,000 = 0.9166666667**, replacing only `HeatPump1/extension/HeatingCapacityFraction17F/Fraction` in the limited real-model scenario.
- The source 5°F fraction **0.825** and COP **2.0** remain observations. The saved data dictionary does not identify that point's compressor operating level. The record also lacks COPs at 47°F/17°F and minimum/maximum curves.
- Complete detailed performance therefore remains **blocked for the matched equipment**. Missing points, COPs and speed semantics are not supplied by the reconstruction or relabelled defaults.
- A separate nine-point **SYNTHETIC_TEST_FIXTURE** supplies minimum/nominal/maximum points at 47°F, 17°F and 5°F to prove parser, schema, rule and consumer behavior. It is not a Samsung/NEEP observation or a validated real installation.

`performance.py` guards reference temperature/level/units, finite positive values, duplicate points, nominal-basis conflicts, stage completeness, COP presence and ordered capacity/input-power relations. `project_detailed` emits fractions only, preserves explicit or autosized model size and identifies conflicting fields to remove. These are lab projection rules, not new production contracts.

## Version-pinned representation

The fresh document and installed validator use **HPXML 5.0**, namespace `http://hpxmlonline.com/2025/12`; OpenStudio-HPXML is **1.12.0**, OpenStudio is **3.11.0+241b8abb4d**. Installed code/schema/rule hashes are in `audit/tool-pins.json`. The clean translator copy is commit `0b77fcee8f1c717f0bfd02e4b5924c84244a9b6b`.

For valid complete details:

```xml
<HeatingDetailedPerformanceData>
  <PerformanceDataPoint>
    <OutdoorTemperature>47</OutdoorTemperature>
    <CapacityFractionOfNominal>1.0</CapacityFractionOfNominal>
    <CapacityDescription>nominal</CapacityDescription>
    <Efficiency><Units>COP</Units><Value>3.5</Value></Efficiency>
  </PerformanceDataPoint>
</HeatingDetailedPerformanceData>
```

The shown COP is **synthetic regression input**. The actual complete control includes all stage-required points. Its mutation removes the legacy fraction and the empty extension, adds only HeatingDetailedPerformanceData and preserves nominal size. Absolute Capacity is calculated by the consumer; it is not copied from the differently sized certificate.

Consumer precedence matters: `set_hvac_heating_performance` checks explicit HeatingCapacity17F, then the legacy fraction, then detailed points before using defaults. Conflicting fields are removed in the detailed control. The consumer subsequently expands fractions, preserves supplied COPs/descriptions, derives HeatingCapacity17F from the nominal detailed 17°F point, and clears the legacy fraction. Current modeled 5°F output after a 17°F-only scalar edit is still default-derived; it does **not** reproduce the certificate's 5°F point.

## Older lab adapter

The original `low_temp_performance_adapter.py` absolute-capacity toy example remains historical evidence; it is not invoked for MURB enrichment. Its synthetic 12,000-Btu/h example does not justify writing 11,000 Btu/h directly into a 47,883.93-Btu/h model. The new observation/projection explicitly separates certificate size and model size.
