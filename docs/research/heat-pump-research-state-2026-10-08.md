# Heat-pump research state — October 8, 2026

## Purpose

Persistent research state for the work performed in `srvx-modeling-lab`
around heat-pump modeling, low-temperature performance, certification
data, equipment identity and OEM/platform investigation.

This document records validated findings, useful experimental results,
limitations and unresolved hypotheses. It is not a canonical SRVX
equipment model and must not be treated as one.

## Source foundation

Work performed against locally preserved or inspected sources includes:

- ENERGY STAR air-source heat-pump certification data
- NEEP cold-climate heat-pump performance data
- AHRI certified reference identities
- Hydro-Québec LogisVert observations
- Canmet `h2k-hpxml`
- OpenStudio-HPXML
- H2K/HOT2000 inputs and translated HPXML
- RESNET Addendum 82

Experimental work currently lives primarily under:

`contributions/h2k-hpxml-issue-19/`

## Canmet h2k-hpxml issue #19

Issue #19 concerns low-temperature ASHP capacity when H2K does not
provide the desired HPXML low-temperature performance inputs.

Important current observations:

- The local Canmet translator emits a 17°F heating-capacity fraction
  around `0.563635566` for relevant heat-pump branches.
- The legacy H2K curve evaluated at 17°F and a quantity normalized
  relative to 47°F are different calculations and must not be conflated.
- Current OpenStudio-HPXML supports detailed low-temperature performance,
  including 5°F data; issue-era defaults must therefore be distinguished
  from current consumer behavior.
- ENERGY STAR example AHRI `210448841` reports approximately:
  - 47°F: 12,000 Btu/h
  - 17°F: 11,000 Btu/h
  - 5°F: 9,900 Btu/h
- The existing MURB audit records translated nominal capacity around
  `47,883.93 Btu/h`.
- The 47,883.93-versus-12,000 discrepancy remains important and must be
  resolved before absolute-capacity enrichment can be described as safe.
- An AHRI identity match alone does not establish the installed-system
  capacity basis or aggregation semantics.

The next closeout step is a mechanical reproduction/audit before making
a final scientific or upstream implementation recommendation.

## RESNET Addendum 82 population investigation

Addendum 82 defines 15 normalized coefficients for variable-capacity
heat-pump performance-map reconstruction.

The exact historical NEEP snapshot used to derive the published
coefficients has not been recovered.

Therefore:

- current NEEP data can be used for diagnostic reconstruction;
- `Date Added` filtering is not equivalent to the historical dataset;
- the original Addendum 82 population must not be claimed as recovered.

A strong current-data reconstruction was found around:

- Live
- Variable Capacity
- Singlezone Non-Ducted, Ceiling Placement
- non-cold-climate population
- complete 15-metric observations
- rated 47°F capacity near or above 18,000 Btu/h
- outdoor-unit weighting

Best observed outdoor-weighted reconstruction around the 18k threshold:

- N = 159
- mean relative error ≈ 2.735%
- maximum metric error ≈ 7.98%

This is a strong diagnostic similarity, not proof of the original
population-selection method.

## Capacity dependence

Performance-map shape was found to vary materially with equipment
architecture and capacity.

The 18k threshold remained visible under multiple weighting methods.

Outdoor-weighted threshold results included:

- 17k: score ≈ 2.864%
- 18k: score ≈ 2.735%
- 19k: score ≈ 3.518%
- 20k: score ≈ 3.504%

The 18→19k discontinuity therefore warranted further investigation.

The current interpretation is:

`observed threshold signal = equipment/capacity structure + catalog/OEM composition effects`

It must not be interpreted as a universal physical discontinuity.

## Exact performance-clone collapse

To test commercial/listing multiplicity, branded outdoor models in the
best Addendum population were collapsed using an exact fingerprint over
56 available raw performance fields.

Result:

- branded outdoor units: 159
- exact performance fingerprints: 79
- extra commercial votes removed: 80

Addendum fit:

- outdoor weighted: ≈ 2.735%
- exact-performance collapsed: ≈ 2.853%

The overall reconstruction remained strong.

However, individual published-coefficient estimates moved materially:

- mean absolute coefficient shift ≈ 2.465%
- maximum shift ≈ 6.885%
- `EIRr17min` moved approximately 0.758 → 0.810

Conclusion:

Commercial/listing multiplicity can materially affect population-derived
statistics even when the overall Addendum reconstruction remains robust.

This does not establish intentional manipulation.

## Threshold test after clone collapse

Exact clone collapse reduced but did not eliminate the 18→19k break.

At 18k:

- outdoor population: N=159, score≈2.735%
- collapsed population: N=79, score≈2.853%

At 19k:

- outdoor population: N=130, score≈3.518%
- collapsed population: N=65, score≈3.298%

The observed score break decreased from approximately `+0.783` to
`+0.445`.

Therefore catalog multiplicity amplifies the threshold signal but does
not fully explain it.

## OEM / rebranding investigation

A numerical platform-fingerprint experiment was performed against the
current NEEP population.

Current source scale observed:

- Live variable-capacity rows: 152,301
- source fields: 87
- unique outdoor-unit model strings: 8,187
- performance fields used by one experimental fingerprint: 56

Repeated exact performance surfaces occur across many commercial brands.

Candidate ecosystems visibly include relationships around manufacturers
or manufacturer-branded families such as:

- Midea / MDV
- Gree / TOSOT / KINGHOME
- Hisense-linked product families
- AUX-linked product families

These are discovery signals, not sufficient OEM attribution by
themselves.

### Important failed approach

An experimental census using transitive graph connected-components
produced a largest component containing:

- 117 brands
- 741 commercial series/model nodes
- 23,114 graph edges

That component includes clearly distinct large manufacturers.

Therefore:

`connected numerical similarity != one OEM family`

A distributor, multi-source commercial series, generation transition or
other bridge can incorrectly merge otherwise distinct engineering
lineages.

Future OEM analysis must use direct evidence and avoid unrestricted
transitive closure.

## Evidence hierarchy for OEM/platform work

Do not infer manufacturing direction from model-number similarity or
performance similarity.

Preferred hierarchy:

1. documented OEM / PBM relationship
2. exact outdoor hardware identity
3. exact component/BOM evidence
4. platform-level component architecture
5. numerical performance lineage
6. model-name similarity

Numerical fingerprints are useful for finding candidates. They are not
physical-manufacturing proof.

## Outdoor-unit focus

Current research should prioritize the outdoor engineering platform
before attempting a complete indoor-unit ontology.

Relevant conceptual layers:

`component → subsystem → outdoor engineering platform → finished outdoor unit → marketed product`

Primary component investigation order:

1. compressor
2. inverter / compressor drive
3. main control PCB / controller
4. refrigerant circuit / expansion devices
5. outdoor heat exchanger
6. fan and fan motor
7. valves, sensors, heaters and secondary components
8. chassis / dimensions / weight
9. cosmetic enclosure / labels

The first three components are expected to provide particularly useful
platform-lineage evidence.

## Compressor evidence

The current NEEP source does not provide:

- compressor manufacturer
- compressor model number
- compressor mechanism
- compressor displacement
- compressor speed range
- inverter model
- vapor-injection/EVI identity

It does provide behavioral observations related to the complete matched
system, including:

- min/rated/max capacities
- COP values
- input power
- low-temperature performance
- SEER2/HSPF2/EER2
- refrigerant
- outdoor model identity
- AHRI reference

Therefore current performance data provide a behavioral fingerprint,
not compressor identity.

Future compressor work should establish:

`outdoor model → compressor manufacturer → exact compressor model`

using service manuals, parts catalogs, exploded diagrams and component
manufacturer documentation.

Same compressor model alone does not establish the same outdoor OEM.

## Single-zone / multi-zone clarification

A compressor itself is not inherently a complete single-zone or
multi-zone system.

The same compressor family may be engineered into multiple outdoor
architectures.

A finished outdoor unit, however, includes refrigerant distribution,
valves, controls, firmware, sensors and connection topology. A completed
single-zone condenser therefore cannot generally be treated as a
multi-zone condenser merely by branching piping.

For OEM/platform analysis, zone capability should be retained as an
outdoor-platform attribute but should not be an absolute barrier to
detecting shared component/platform ancestry.

Indoor delivery classifications such as wall-mounted, cassette or
central air handler should not define the outdoor platform.

## Repairability / reuse opportunity

The emerging equipment/component graph may later support a separate
repairability projection:

`OutdoorPlatform → Component → OEM part number → supersession → compatible models`

This could identify legitimate cross-brand replacement components and
improve reuse/recycling.

Do not infer component interchangeability merely from shared platform or
performance lineage. Exact part identity, revision, electrical
specification, firmware and refrigerant compatibility must be checked.

## Evidence/provenance rule

Keep these categories distinct:

### Source identity/catalog evidence
Brand, model, series, certification identifiers.

### Manufacturer-reported observations
Extended performance observations supplied through listing programs.

### Certified ratings
Values participating in formal certification programs.

### Independent verification/test evidence
Laboratory or enforcement results where provenance is available.

### Hardware evidence
Compressor, inverter, PCB, fan, valves, heat exchanger, service parts.

### Calculated analysis
Ratios, Addendum reconstruction metrics, deduplication scores and
population comparisons.

### Inference/hypothesis
OEM lineage, platform sharing, probable rebranding or anomalous
performance relationships not independently established.

Do not promote analysis-derived values or hypotheses into canonical
source observations.

## Repository boundary

For now:

- `srvx-modeling-lab`: experiments, hypotheses, research and validation
- `nova-open`: later normalized source/domain evidence
- `srvx-core`: later stable shared semantics and identities
- `srvx-studio`: later publication/page contracts
- `nova-frontend`: later public rendering

Promotion should happen only after the research semantics stabilize.

## Publication / licensing caution

Public accessibility does not establish redistribution rights.

In particular, preserve source notices and verify permissions before
publishing raw or derived third-party datasets.

Aggregate findings, reproducible methods, source links and independently
created analysis may have different sharing constraints from source
payloads.

## Immediate next work

1. Finish the mechanical closeout of Canmet `h2k-hpxml` issue #19.
2. Keep the broader Addendum/OEM research separate from that upstream
   contribution.
3. Resume outdoor-component investigation later, starting with exact
   compressor identity.
4. After verified research artifacts exist, define the first SRVX Docs
   publication collection.
