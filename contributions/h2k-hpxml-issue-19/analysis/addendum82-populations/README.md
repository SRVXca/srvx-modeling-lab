# Addendum 82 NEEP population experiments

Reproducible investigation supporting canmet-energy/h2k-hpxml issue #19.

## Question

RESNET Addendum 82 publishes mean normalized heat-pump performance
relationships derived from the NEEP database.

This experiment asks:

> Which defensible NEEP population definitions reproduce those published
> population statistics, and how sensitive are the results to population
> definition?

This is an investigation, not a reverse-fit of filters to target values.

## Baseline

NEEP HP Report:

- Status = Live
- Variable Capacity = true

## Population dimensions

Initial experiments vary:

- source vintage / Date Added to List
- data completeness
- ducting configuration
- ENERGY STAR cold-climate flag
- AHRI type
- row weighting / deduplication:
  - raw NEEP rows
  - AHRI certificate
  - outdoor unit
  - outdoor + indoor unit combination

Dimensions are first tested independently.

Only a small set of explicit, interpretable combinations is then tested.

## Metrics

Capacity:

- Qr47full
- Qr47min
- Qr17full
- Qr17min
- Qm5max
- Qr5full
- Qr5min

Energy Input Ratio:

- EIRr47full
- EIRr47min
- EIRm17full
- EIRr17full
- EIRr17min
- EIRm5max
- EIRr5full
- EIRr5min

Each population is compared against the published Addendum 82 vector.

The summary score is the mean absolute relative difference across the
available metrics. It is a diagnostic ranking only, not evidence that
the lowest-scoring population was RESNET's original population.

## Source

Primary source snapshot:

`source-study/neep/neep_air_source_heat_pump_2026-10-07.xlsx`

The NEEP source study and usage restriction are documented under:

`source-study/neep/SOURCE-STUDY.md`
