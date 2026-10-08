# H2K / HPXML equipment interoperability audit — v0.1

Status: **research candidate mappings; not an implemented converter**. Date: 2026-10-08. Scope: all six AHRI equipment families. This is additive to the previously validated equipment evidence registry. No SRVX canonical identity, seeding, direct AHRI ingestion, and no changes to source contracts.

## Primary references

- [OpenStudio-HPXML current Workflow Inputs](https://openstudio-hpxml.readthedocs.io/en/latest/workflow_inputs.html). This is a **software input profile**, not all of generic HPXML. Pin installed versions before implementation; `latest` may drift.
- [NRCan/Canmet H2K-HPXML translator](https://github.com/canmet-energy/h2k-hpxml). The translator is H2K **to** HPXML; not the inverse and not an equipment catalog ingestion engine.
- Existing translator components: `src/h2k_hpxml/components/system_air_conditioning.py`, `system_heat_pumps.py`, `system_heating_primary.py`, `system_hot_water.py`, `system_hvac_distribution.py`.
- [H2K-HPXML implementation status](https://github.com/canmet-energy/h2k-hpxml/blob/main/docs/status/status.md). Claims systems support generally; does not prove exact mappings for all Supply ratings.
- [HPXML schema API](https://github.com/canmet-energy/hpxml-schema-api): `GET /fields`, `/tree`, `/search`, `/validate`. Use it in later *schema-version-pinned* validation.

## Findings by family

| Family | HPXML model | Confirmed equipment fields | Still scenario-only / unresolved |
|---|---|---|---|
| Air conditioning | `CoolingSystem` | `CoolingCapacity`, `AnnualCoolingEfficiency` SEER2/EER2 | compressor type; distribution; fraction of cool load; subtype differences |
| ASHP | `HeatPump` | 47F nominal `HeatingCapacity`, nominal `HeatingCapacity17F`, HSPF2, SEER2, optional detailed heating/cooling points | heat/cool load shares; backup/lockout; compressor stage; distribution |
| Furnace | `HeatingSystem/Furnace` | `AnnualHeatingEfficiency` AFUE, fuel, `HeatingCapacity` **output** | distribution system; fan; pilot; heat load share; source burner input cannot go into output-capacity field |
| Boiler | `HeatingSystem/Boiler` | AFUE, fuel, `HeatingCapacity` **output**, optional electric auxiliary energy | hydronic distribution; heat load share; input vs output semantics |
| Water heater | `WaterHeatingSystem` | `UniformEnergyFactor` or `EnergyFactor`, tank volume, first-hour, usage bin, recovery efficiency | water-heater subtype, DHW share, installed location; *here* `HeatingCapacity` refers to input |
| Ground/water source | `HeatPump` with `ground-to-air` or `water-loop-to-air` | COP, EER, heating/cooling capacity | geothermal loop and flow / connected shared system; certified test conditions differ from installed loop |

Machine-readable inventory: `registry/h2k-hpxml-field-matrix.v0.1.csv` (66 rows: equipment-evidence candidates and scenario-only requirements). **Every H2K path is deliberately marked unverified** until actual local XML/parser source audit. A column being documented in OpenStudio-HPXML is not proof that a specific manufacturer dataset supplies it.

## Critical engineering traps discovered

1. **Capacity signification differs by system.** For furnace/boiler, `HeatingCapacity` is delivered heating output; for the documented conventional storage water-heater workflow, `HeatingCapacity` refers to heating **input**. Mapping all `heatingInputCapacity` to `HeatingCapacity` universally would be wrong.
2. **47F/17F nominal ≠ 17F maximum.** ASHP detailed points carry `OutdoorTemperature`, `CapacityDescription` (`minimum`, `nominal`, `maximum`), capacity and COP. OpenStudio-HPXML constrains heating outdoor temperatures (47F, 17F, 5F and at most one below 5F) and completeness by compressor stage. Do not manufacture missing nominal points from maximum tests.
3. **Seasonal labels vs detailed performance:** the simulation can ignore HSPF/SEER for systems whose detailed points are supplied. The labeling facts remain in source observations.
4. **Subtypes need distinct schemas.** `WaterHeatingSystem` includes storage, tankless, heat-pump and combi applications; do not assume a single UEF range or required field set for all.
5. **Geothermal manufacturer rating ≠ installed loop.** A test flow, EWT, EER or COP is not a building's borehole/loop configuration. Do not copy AHRI rating-test flow into `GeothermalLoop/LoopFlow` without an installed system basis.
6. **Software defaults are not source evidence.** Autosizing, compressor lockout, water heater recovery, and HVAC airflow may be defaulted by the simulation. Report each as a projection fallback if relied on.

## What can be claimed today

- **Verified against published OpenStudio-HPXML workflow documentation:** system choices and candidate field names, including differences in semantics.
- **Not yet verified:** H2K native XML paths, actual translator reads and writes on installed branch, compatibility with a pinned local HPXML XSD + Schematron, a round-trip (unsupported), or simulation fidelity.

## Run the *local* H2K audit next

From `~/srvx-modeling-lab` (only read repo source and example fixtures):

```bash
python3 scripts/audit-h2k-hpxml-local.py
python3 tests/test-h2k-hpxml-field-audit.py
```

Results are written to `var/modeling-audit/h2k-hpxml-v0.1/`:

- `h2k-xml-candidate-paths.csv` — observed XML element paths and attribute **names** from bounded local sample H2K files; no values.
- `h2k-translator-keyword-evidence.csv` — source file/line matches as **candidates only**, not verified mapping rules.
- `audit-summary.json` — how many translator sources and XML fixtures were available; empty outputs mean missing local inputs rather than confirmed unsupported equipment.

This script intentionally **does not** guess an H2K field based on an HPXML name. The next review must select one representative H2K input for each equipment family, compare the translator output and pin exact H2K schema + translator commit before changing candidate statuses.

## Gate for adapter work

Required before beginning the furnace/water-heater vertical slice: (1) read actual H2K schema and parser path, (2) pin HPXML/OpenStudio-HPXML versions, (3) confirm unit and test conditions, (4) separate product facts from installed-system configuration, (5) add positive/negative target projection tests. Keep original source observations even where neither simulation target supports them.
