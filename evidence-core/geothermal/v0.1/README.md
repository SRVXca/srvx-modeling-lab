# Geothermal / water-source heat-pump evidence v0.1

Status: LAB_REVIEWED_NOT_CANONICAL

## Purpose

This bundle is the first market-width geothermal fixture built using the
modeling-lab evidence discipline.

It deliberately separates:

    ENERGY STAR SourceRecord
        ↓
    GroundSourcePerformance Observation
        ↓
    market product fixture

from:

    AHRI matched configuration
    canonical SRVX Supply identity
    subsidy eligibility
    pricing / inventory
    modeling projection

Those later layers are not inferred when evidence is missing.

## Source records

The bundle preserves four exact ENERGY STAR geothermal records originally
pinned in nova-open.

They represent two model-level equipment identities:

### York Y5SZ036BD1

Three ENERGY STAR certification occurrences:

- Closed Loop Water-to-Air — COP 4.4 / EER 23.8
- Closed Loop Water-to-Air — COP 4.4 / EER 23.8
- Open Loop Water-to-Air — COP 5.1 / EER 29.5

The duplicate-looking closed-loop occurrences retain distinct source-native
ENERGY STAR identifiers and are not collapsed.

ENERGY STAR identifies the partner as:

    WaterFurnace International, Incorporated

while the product brand is:

    York

This relationship is preserved as source evidence only.

It is NOT interpreted here as proof of OEM/manufacturing direction.

### Hydro Solar Innovative Energy GEO040V1LM

One ENERGY STAR occurrence:

- Closed Loop Water-to-Water
- COP 3.4
- EER 17.9
- refrigerant R-32

## Manufacturer observations

The Hydro Solar manufacturer evidence additionally provides two conditional
performance-table variants for the same model identity.

### Titanium exchanger

- heating output: 40,600 Btu/h
- COP: 3.5
- source entering temperature: 0 C
- load entering temperature: 40 C

### Copper exchanger

- heating output: 41,456 Btu/h
- COP: 4.4
- source entering temperature: 0 C
- load entering temperature: 35 C

These are manufacturer performance-table observations under different
conditions.

They are NOT treated as:

- unconditional product capacities;
- AHRI certified ratings;
- separate model-level products;
- proven variants of ENERGY STAR occurrence 4710776.

## Observation model

The promoted observation contract is:

    GroundSourcePerformance

Current metrics represented:

- COP
- EER
- heating capacity

Conditions retain, where available:

- water-to-air vs water-to-water;
- open-loop vs closed-loop;
- exchanger material;
- source entering/leaving temperature;
- load entering/leaving temperature;
- source flow;
- load flow.

Missing test conditions remain null rather than being inferred.

## Market fixture

The market fixture contains two model-level products:

    York Y5SZ036BD1
    Hydro Solar Innovative Energy GEO040V1LM

For both products:

    AHRI reference          UNVERIFIED
    price                   UNKNOWN
    current availability    UNKNOWN

This does not prevent use as a reviewed lab market fixture.

It does prevent claiming a complete AHRI-certified matched configuration.

## AHRI next layer

The next geothermal research layer is AHRI WSHP configuration evidence.

That layer should resolve, where evidence permits:

    certification reference
    matched assembly identity
    water-to-air / water-to-water configuration
    source/loop rating class
    heating capacity
    cooling capacity
    COP
    EER
    part-load ratings where applicable

AHRI evidence must be added as another evidence layer.

It must not overwrite the existing ENERGY STAR or manufacturer SourceRecords.

## Relationship to nova-open

The source evidence was promoted from the existing committed geothermal work
in nova-open.

The modeling-lab fixture does not replace that implementation.

Future promotion should reuse nova-open's generic ENERGY STAR SourceRecord
adapter pattern:

    generic Socrata adapter
        ↓
    family-specific exact source schema
        ↓
    normalized Observation
        ↓
    reviewed product / system projection

