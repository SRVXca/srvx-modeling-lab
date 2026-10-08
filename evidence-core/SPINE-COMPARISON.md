# Evidence spine comparison — fenestration vs heat pump

Status: modeling-lab architecture note, October 8, 2026.

## Shared evidence spine

The reusable experimental path is:

    SourceRecord
        ↓
    Observation
        ↓
    Projection
        ↓
    Model Mutation / Scenario
        ↓
    Validation
        ↓
    Finding

Population analysis is a separate research layer. It may inform findings but
does not become source evidence or canonical equipment truth.

## Fenestration

Fenestration currently demonstrates the most complete vertical evidence spine.

### SourceRecord

A selected NRCan window reference is preserved as a source-shaped record.

### Observation

Source metrics are carried into an explicit observation with provenance.

### Projection

The observed whole-assembly U-factor and SHGC are explicitly projected into
the corresponding HPXML window fields while preserving opening geometry.

### Model mutation

A real WizardHouse HPXML fixture is modified.

### Validation

The current bundle verifies:

- source identity continuity;
- field-level metric provenance;
- exact permitted replacement;
- HPXML XSD validity;
- OpenStudio-HPXML Schematron validity.

Manufacturer size applicability remains explicitly unverified.

## Heat pump

Heat-pump research is substantially richer at the source-study and research
layers but does not yet have the same completed real-fixture spine.

### SourceRecord layer

Strong.

Existing work preserves the 87-field NEEP HP source vocabulary and XLSX
structure without silently normalizing it.

ENERGY STAR evidence is also used in the issue-19 investigation.

### Observation layer

One real ENERGY STAR SourceRecord and four provenance-preserving HeatPumpPerformance observations are now frozen under the issue-19 bundle. The source capacities at 47°F/17°F/5°F and only available 5°F COP remain distinct from model-default or synthetic control values. Missing min/max curves, COPs and 5°F speed semantics are explicit.

### Projection layer

The real MURB 17°F-only scenario now validates a normalized source shape while preserving model size. Its declared 47°F rating condition establishes the compatible reference basis; 11,000/12,000 replaces only the 17°F fraction. The historical absolute-capacity toy adapter is not used for this case. Full matched detailed-performance projection remains blocked by incomplete source data.

### Model mutation

A fresh clean pinned MURB baseline, exact one-field real scenario and separate synthetic detailed consumer control have been created. The real limited scenario passes XSD/Schematron, consumer processing and a simulation execution smoke. The complete synthetic control proves 47°F/17°F/5°F consumer mechanics without supplying missing equipment facts.

### Validation blocker

The existing MURB audit reports approximately 47,883.93 Btu/h nominal
capacity.

The studied ENERGY STAR certification example reports 12,000 Btu/h at 47°F.

The MURB input explicitly rates its user/model capacity at 47°F, so normalized shape transfer is representable without changing size. Physical installed-system count/configuration remains unresolved; the 12,000/11,000 Btu/h certificate must not be applied as an absolute-capacity replacement. Missing COP/min/max and unspecified 5°F speed prevent a complete matched detailed profile. Synthetic acceptance does not complete that evidence gap.

### Research layer

Very strong and deliberately separate from the evidence spine.

Current heat-pump research includes:

- ENERGY STAR low-temperature comparisons;
- NEEP 17°F/5°F performance evidence;
- RESNET Addendum 82 population reconstruction;
- capacity/population sensitivity;
- listing/clone weighting effects;
- OEM/platform fingerprint experiments;
- component/OEM lineage hypotheses.

These analyses do not become SourceRecord or Observation fields.

## Integration target

Heat-pump issue #19 should reach parity with fenestration by producing, in
order:

1. one selected real external SourceRecord;
2. one provenance-preserving HeatPumpPerformance Observation;
3. one explicit projection whose capacity basis is documented;
4. one freshly translated real H2K fixture;
5. one minimally mutated HPXML artifact, if justified;
6. XSD validation;
7. relevant OpenStudio-HPXML Schematron/consumer validation;
8. an exact diff identifying only intended changes.

If the capacity-basis discrepancy cannot be resolved, the correct result is a
blocked projection rather than an invented transformation.

## Architectural lesson

Fenestration demonstrates how a narrow vertical proof should look.

Heat-pump research supplies much richer upstream evidence, but must now adopt
the same explicit stage boundaries before any low-temperature enrichment is
treated as a validated modeling input.
