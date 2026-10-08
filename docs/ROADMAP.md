# SRVX Modeling Lab — Roadmap

## Phase 1 — Understand the ecosystem

Study each upstream independently.

For every repository record:

1. what it owns
2. what model/schema it defines
3. what data it expects
4. what it calculates
5. what it outputs
6. where SRVX overlaps
7. what SRVX should NOT rebuild
8. one useful contribution candidate

Initial upstreams:

- canmet-energy/h2k-hpxml
- canmet-energy/community-energy-orchestrator
- canmet-energy/hpxml-schema-api
- canmet-energy/housing-archetypes
- NatLabRockies/OpenStudio-HPXML
- NatLabRockies/EnergyPlus
- open205/schema-205
- open205/toolkit-205
- IfcOpenShell/IfcOpenShell
- cityjson/cjio
- canmet-energy/tandm

## Phase 2 — Model map

Map the external modeling loop:

Building facts
→ geometry
→ HPXML
→ equipment performance
→ simulation
→ results

Identify which portions are:

- external authority
- SRVX normalized observation
- SRVX adapter
- SRVX decision logic

## Phase 3 — First executable scenario

Build one Québec heat-pump scenario:

SRVX building observations
+ SRVX SupplySystem
+ cold-climate performance observations
→ HPXML projection
→ OpenStudio-HPXML / EnergyPlus
→ calculated results

## Phase 4 — Economics

Combine simulation results with:

- supply price observations
- subsidy results
- contractor payout
- installation scope
- customer package price

## Phase 5 — Upstream contribution

For each integration, contribute upstream only when SRVX produces something
generally useful:

- regression fixture
- bug reproduction
- adapter
- schema compatibility test
- documentation
- validated real-world example
