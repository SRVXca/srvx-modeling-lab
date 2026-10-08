# SRVX Modeling Lab — Evidence Core

## Purpose

`evidence-core/` contains deliberately promoted, versioned research evidence
that is important enough to persist in Git.

It is NOT `srvx-core` and does not define canonical SRVX truth.

The distinction is:

    var/
        generated/local/ephemeral audit state

    evidence-core/
        selected evidence intentionally promoted from experiments/audits

    docs/research/
        interpreted research conclusions

    nova-open / srvx-core
        later production promotion, only after semantics are stable

## Evidence spine

A complete modeling-evidence chain is:

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

Not every investigation needs to reach every stage.

Missing or blocked stages must remain explicit. They must not be filled with
invented assumptions merely to make the chain complete.

## Stage meanings

### SourceRecord

Typed or structured representation of a foreign source while preserving its
source vocabulary and identity.

No SRVX normalization or inferred values belong here.

### Observation

Evidence expressed with shared modeling semantics while retaining source
provenance, conditions, rating basis and uncertainty.

An observation is evidence, not canonical equipment truth.

### Projection

An explicit transformation from observations/scenario data into the input
required by a downstream model or schema.

Calculated values must disclose their formula and basis.

### Model Mutation / Scenario

The concrete external-model artifact created or modified by the projection.

Examples include an HPXML replacement fixture or an OpenStudio scenario.

### Validation

Evidence that the resulting artifact satisfies the checks actually performed,
such as:

- exact replacement comparison
- XSD validation
- Schematron validation
- SDK load
- translator reproduction
- simulation

These checks are distinct and must not be conflated.

### Finding

An interpreted conclusion supported by the preceding evidence.

Population analyses and exploratory research may support findings but remain
separate from source observations.

## Promotion rule

Files under `var/` remain disposable generated state by default.

An artifact is copied into `evidence-core/` only when:

1. it supports a meaningful research claim or regression test;
2. its provenance is known;
3. its role in the evidence spine is understood;
4. persisting it improves reproducibility;
5. redistribution is permitted or the artifact is independently created.

Raw restricted third-party datasets are not promoted merely because they were
used during research.
