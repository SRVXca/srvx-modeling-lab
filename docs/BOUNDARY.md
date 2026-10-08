# SRVX Modeling Lab — Boundary

## Purpose

This repository is a non-authoritative integration, study, fixture, adapter,
and upstream-contribution workspace.

It exists to answer:

> What mature external model, schema, engine, or dataset can SRVX integrate
> instead of rebuilding itself?

## Authority

This repository MUST NOT define canonical SRVX semantics.

Canonical SRVX authority remains in the appropriate SRVX repositories:

- srvx-core — canonical identity, semantics, relationships, publishing rules
- nova-open — normalized domain truth, observations, evidence, provenance
- srvx-studio — page/block/design contracts and fixtures
- srvx-web — public renderer
- nova-app — authenticated operational truth

The Modeling Lab may:

- inspect external schemas and models
- build adapters
- build projections
- create fixtures
- create compatibility tests
- compare external models
- reproduce upstream bugs
- prototype integrations
- contribute fixes/tests/fixtures upstream

The Modeling Lab MUST NOT silently promote an external schema into canonical
SRVX truth.

## Working rule

Prefer:

SRVX canonical truth
→ thin adapter/projection
→ external schema/model/engine

over:

external schema
→ becoming SRVX canonical semantics

## Current product slice

Initial proving ground:

Québec residential heat pumps.

Primary question:

> Can one normalized SRVX building + supply scenario be projected through
> mature external modeling tools and return useful decision metrics?
