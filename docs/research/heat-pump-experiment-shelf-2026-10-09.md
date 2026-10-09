# Heat-pump modeling research shelf — October 9, 2026

## Status

PAUSED / PRESERVED FOR LATER RESEARCH

This document freezes the current heat-pump modeling investigation before
SRVX pivots to broader AHRI-backed supply fixtures.

This research is valuable and intentionally unfinished.

It must not be interpreted as a final SRVX heat-pump fallback, a completed
resolution of canmet-energy/h2k-hpxml issue #19, or a proposed upstream
default.

---

## 1. Original h2k-hpxml problem

canmet-energy/h2k-hpxml issue #19 concerns low-temperature air-source
heat-pump capacity when H2K does not provide enough information to directly
populate modern HPXML low-temperature performance inputs.

The pinned translator currently emits for relevant ASHP branches:

    extension/HeatingCapacityFraction17F
        Fraction = 0.563635566

The comment describes this as derived from the H2K heat-pump curve.

Research established that:

- a direct legacy H2K curve result;
- a capacity fraction normalized relative to 47°F;
- and a modern detailed performance map

are different concepts and must not be conflated.

---

## 2. Exact ENERGY STAR / AHRI fixture

The MURB fixture references:

    AHRI 210448841

The studied ENERGY STAR record reports approximately:

    47°F = 12,000 Btu/h
    17°F = 11,000 Btu/h
     5°F =  9,900 Btu/h

Therefore:

    Q17 / Q47 = 0.916667
    Q5  / Q47 = 0.825000

IMPORTANT:

0.916667 is an EQUIPMENT-SPECIFIC fixture observation.

It is not:

- the latest SRVX population result;
- a universal heat-pump fallback;
- an Addendum 82 coefficient;
- the SRVX reconstructed Addendum profile.

Its continuing value is as a matched real-equipment regression/control case.

---

## 3. MURB nominal capacity

The translated MURB model reports approximately:

    HeatingCapacity = 47,883.93 Btu/h

The research initially treated the difference between:

    47,883.93 Btu/h
    vs
    12,000 Btu/h

as a possible mismatch requiring reconciliation.

The closeout experiment established that the H2K capacity is a rated
47°F system/model capacity basis and should not simply be overwritten by the
12,000 Btu/h certification example.

The useful transferable quantity from the matched equipment record is its
performance SHAPE.

Conceptually:

    H2K nominal/system size
            +
    external normalized performance shape
            ↓
    HPXML low-temperature performance

This is analogous to the fenestration spine:

    preserve opening geometry
            +
    replace observed performance properties

rather than replacing the entire modeled object.

---

## 4. Mechanical projection proof

Astra closeout commit:

    3891a9c

proved a bounded equipment-specific projection.

For the Samsung fixture:

    Q17 / Q47 = 11,000 / 12,000
              = 0.916667

The experiment preserved:

    HeatingCapacity ≈ 47,883.93 Btu/h

and changed the low-temperature performance shape only.

Validated results reported by the closeout:

- exact diff: only intended 17°F performance changed;
- HPXML XSD: PASS;
- Schematron: zero new failures;
- 19 tests: PASS;
- real 17°F-only OpenStudio simulation smoke:
  - six warnings;
  - zero severe errors.

A separate synthetic nine-point fixture demonstrated that the pinned
OpenStudio-HPXML consumer accepts detailed heating performance data containing:

- outdoor temperature;
- normalized capacity;
- minimum / nominal / maximum operating levels;
- COP.

This validates the PROJECTION MECHANISM.

It does not validate 0.916667 as a population/default model.

---

## 5. Modern HPXML representation

Pinned OpenStudio-HPXML supports:

    HeatingDetailedPerformanceData
        PerformanceDataPoint
            OutdoorTemperature
            Capacity
            or CapacityFractionOfNominal
            CapacityDescription
            Efficiency / COP

This permits a richer representation than one legacy 17°F fraction.

The long-term preferred heat-pump projection is therefore a performance
surface rather than one universal retention number.

---

## 6. Published RESNET Addendum 82

RESNET Addendum 82 provides 15 normalized coefficients describing
variable-capacity heat-pump performance relationships.

Published vector used in the research:

Capacity:

    Qr47full    0.908
    Qr47min     0.272
    Qr17full    0.817
    Qr17min     0.341
    Qm5max      0.866
    Qr5full     0.988
    Qr5min      0.321

Energy Input Ratio:

    EIRr47full  0.939
    EIRr47min   0.730
    EIRm17full  1.351
    EIRr17full  0.902
    EIRr17min   0.798
    EIRm5max    1.164
    EIRr5full   1.000
    EIRr5min    0.866

This vector is an external published reference and must remain distinct from
SRVX experimental reconstructions.

---

## 7. Current-data Addendum reconstruction

The exact historical NEEP population used by RESNET was not recovered.

Current NEEP can therefore provide a diagnostic reconstruction, not proof of
the historical population.

A strong current-data candidate population was found around:

    Status = Live
    Variable Capacity = true
    Ducting = Singlezone Non-Ducted, Ceiling Placement
    ENERGY STAR Cold Climate = false
    complete 15 metrics
    rated 47°F capacity >= approximately 18,000 Btu/h
    weighting = branded outdoor unit

Observed result:

    N = 159
    mean relative coefficient error ≈ 2.735%
    maximum coefficient error ≈ 7.98%

This is referred to as an SRVX current-data reconstruction.

It is NOT official Addendum 82.

---

## 8. Capacity dependence

The Addendum-style shape varied with equipment population and capacity.

Outdoor-weighted threshold observations included approximately:

    >=17k : 2.864%
    >=18k : 2.735%
    >=19k : 3.518%
    >=20k : 3.504%

Therefore the 18k→19k change became an investigation target.

Current interpretation:

    observed threshold effect
        =
    equipment/capacity structure
        +
    catalog/OEM composition effects

It is not a proven universal physical discontinuity.

---

## 9. Commercial/listing multiplicity

The selected 18k population was further collapsed using an exact numerical
fingerprint over 56 raw performance fields.

Result:

    branded outdoor units       159
    exact performance surfaces   79
    commercial votes removed     80

Overall Addendum fit:

    outdoor weighted              ≈ 2.735%
    exact-performance collapsed   ≈ 2.853%

The overall fit remained strong.

However individual coefficients moved materially.

Observed:

    mean absolute coefficient shift ≈ 2.465%
    maximum coefficient shift       ≈ 6.885%

Important example:

    EIRr17min
        outdoor weighted ≈ 0.758
        clone collapsed  ≈ 0.810
        published A82    = 0.798

Therefore population weighting and repeated commercial listings can influence
derived performance-map coefficients.

No manipulation or misconduct is inferred from this observation.

---

## 10. Threshold after clone collapse

At 18k:

    outdoor-weighted
        N = 159
        score ≈ 2.735%

    exact-performance collapse
        N = 79
        score ≈ 2.853%

At 19k:

    outdoor-weighted
        N = 130
        score ≈ 3.518%

    exact-performance collapse
        N = 65
        score ≈ 3.298%

The score discontinuity decreased approximately:

    +0.783 percentage points
        →
    +0.445 percentage points

Catalog multiplicity therefore amplifies the capacity signal but does not
fully explain it.

---

## 11. Three profiles must remain separate

Future work must distinguish:

### MATCHED_EQUIPMENT

Example:

    ENERGY STAR / AHRI 210448841

Specific equipment observations such as:

    47°F 12,000
    17°F 11,000
     5°F  9,900

### RESNET_ADDENDUM_82_PUBLISHED

Immutable external published coefficient vector.

### SRVX_A82_CURRENT_RECONSTRUCTION

Experimental current-data population reconstruction.

At present it has at least two useful statistical views:

    outdoor-unit weighted
    exact-performance-clone collapsed

SRVX has NOT decided that either view is a canonical fallback.

---

## 12. OEM / platform investigation

The NEEP research expanded into equipment lineage and rebranding discovery.

Observed current scale:

    Live variable-capacity rows      152,301
    source fields                         87
    unique outdoor model strings       8,187
    fingerprint performance fields        56

Repeated exact and near-exact performance surfaces occur across multiple
brands.

Useful candidate ecosystems were observed around families including:

- Midea / MDV
- Gree / TOSOT / KINGHOME
- Hisense-related candidates
- AUX-related candidates

These remain candidate lineage signals, not manufacturing proof.

Evidence hierarchy retained for later research:

    documented OEM/PBM relationship
        >
    exact outdoor hardware identity
        >
    component/BOM evidence
        >
    platform component architecture
        >
    performance lineage
        >
    model-name similarity

A failed unrestricted connected-components experiment produced a giant
117-brand component.

Conclusion:

    connected numerical similarity != one OEM

That failed method must not be reused as an OEM classifier.

---

## 13. Component investigation direction

Outdoor-unit research should proceed roughly through:

    compressor
    inverter / compressor drive
    control PCB
    refrigerant topology / expansion devices
    outdoor heat exchanger
    fan / motor
    secondary parts
    chassis
    cosmetics

NEEP provides complete-system behavioral evidence.

It does not directly provide compressor, inverter or PCB identity.

Future component work should bridge:

    outdoor model
        →
    service / parts documentation
        →
    exact component model
        →
    component manufacturer evidence

---

## 14. What is actually validated today

Validated:

    Source studies                    YES
    NEEP source adapter               YES
    equipment-specific 17°F shape     YES
    preserve H2K nominal size         YES
    detailed-performance capability   YES, synthetic control
    XSD validation                    YES
    Schematron validation             YES
    bounded simulation smoke          YES
    Addendum population experiments   YES
    clone sensitivity experiment      YES

Not validated/finalized:

    universal 17°F fallback           NO
    canonical SRVX A82 profile        NO
    full real matched 47/17/5 map     NO
    canonical population weighting    NO
    upstream h2k-hpxml patch          NO
    issue #19 resolution              NO
    OEM attribution                   NO

---

## 15. Why the experiment is being paused

The modeling/research work has reached a useful reproducible milestone.

SRVX now needs broader equipment-family coverage for the commercial product.

Near-term priority moves to source-backed supply fixtures for:

    air conditioning
    air-source heat pumps
    residential furnaces
    residential water heaters
    residential boilers
    geothermal / water-source heat pumps

The heat-pump experiment is intentionally shelved rather than closed.

---

## 16. Recommended continuation

When resumed, continue from the performance-map abstraction, not from a search
for one replacement 17°F number.

Primary next experiment:

    H2K nominal system size
        +
    one selected performance profile
        ↓
    HeatingDetailedPerformanceData

Run the same MURB model through:

    published Addendum 82
    SRVX outdoor-weighted reconstruction
    SRVX clone-collapsed reconstruction
    matched equipment profile where sufficiently complete

Then compare model behavior.

Only after that work should an upstream h2k-hpxml fallback change be proposed.

---

## 17. Reproduction

Latest closeout mechanics:

    bash contributions/h2k-hpxml-issue-19/closeout/reproduce.sh --simulate

Primary persistent locations:

    docs/research/heat-pump-research-state-2026-10-08.md
    evidence-core/heat-pump/issue-19-v0.1/
    contributions/h2k-hpxml-issue-19/
    contributions/h2k-hpxml-issue-19/analysis/addendum82-populations/
    contributions/h2k-hpxml-issue-19/closeout/

This research remains modeling-lab evidence and does not define canonical
SRVX production semantics.
