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

Partial.

The modeling lab has a generic `HeatPumpPerformance` observation contract and
source-specific adapters, but a selected real heat-pump observation has not
yet been frozen as the equivalent of the fenestration NRCan observation.

### Projection layer

Experimental, not yet validated for the real fixture.

The current issue-19 adapter can replace the converter's fallback
17°F fraction with an absolute externally observed `HeatingCapacity17F`.

That operation works on the synthetic 12,000 Btu/h example.

It is not yet established as correct for the real MURB fixture.

### Model mutation

Incomplete.

A real MURB translation exists in audit evidence, but the external equipment
capacity basis has not been reconciled with the translated model.

### Validation blocker

The existing MURB audit reports approximately 47,883.93 Btu/h nominal
capacity.

The studied ENERGY STAR certification example reports 12,000 Btu/h at 47°F.

Until system count, equipment identity and capacity basis are reconciled, the
12,000/11,000 Btu/h example must not be applied as an absolute-capacity
replacement to the real MURB fixture.

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
