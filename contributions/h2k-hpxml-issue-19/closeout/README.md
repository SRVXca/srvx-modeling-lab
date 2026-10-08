# Heat-pump issue #19 projection closeout

Outcome: **validated real 17°F-only shape scenario; full matched 47°F/17°F/5°F detailed profile blocked; no upstream patch justified**. Task dated October 8, 2026. All implementation and generated files stay in `/home/o/srvx-modeling-lab`.

Read [projection-semantics.md](projection-semantics.md), [mechanical-findings.md](mechanical-findings.md), [performance-profile-comparison.md](performance-profile-comparison.md) and [upstream.patch.NOT_JUSTIFIED.md](upstream.patch.NOT_JUSTIFIED.md). The durable evidence bundle is `/home/o/srvx-modeling-lab/evidence-core/heat-pump/issue-19-v0.1/` with `ARTIFACTS.sha256`.

## Reproduce

```bash
cd /home/o/srvx-modeling-lab
bash contributions/h2k-hpxml-issue-19/closeout/reproduce.sh
# Executes the full simulation smoke as well:
bash contributions/h2k-hpxml-issue-19/closeout/reproduce.sh --simulate
```

Required existing local assets:

- Translator commit `0b77fcee8f1c717f0bfd02e4b5924c84244a9b6b` in `repos/canmet-energy/h2k-hpxml`. `prepare_clean.py` makes a **clean git-archive copy**, not a worktree that changes the original repository's metadata. The unrelated original `weather_files.py` modification is hashed before/after and preserved.
- Existing `repos/canmet-energy/h2k-hpxml/.venv/bin/python` for the fresh translator run. This environment has its runtime dependencies but no pytest/lxml. Lab tests use the existing system Python's stdlib unittest, lxml and jsonschema; no package installation was needed.
- Public ENERGY STAR snapshot: `/home/o/nova-open/data/supply/air-source-heat-pump-v0.1/{energy-star.csv.gz,metadata.json.gz,source.json}`. Read only; exactly one source record is frozen.
- Local NEEP XLSX `contributions/h2k-hpxml-issue-19/source-study/neep/neep_air_source_heat_pump_2026-10-07.xlsx`. Read only and ignored; no raw NEEP records are committed. Existing 87-field adapter and metric functions are reused to produce only aggregate research results. Source usage notice remains relevant; access is not permission for commercial inventory or public raw extracts.
- `/home/o/.local/bin/openstudio` and installed `/home/o/.local/share/OpenStudio-HPXML-v1.12.0/`, including its existing Moncton CWEC2020 EPW. Installed dependencies/source remain unchanged.

The runner directs configuration, cache and logging into ignored `work/`. It performs a fresh baseline translation, source freeze, model mutations, independent exact diffs, pinned XSD/Schematron checks, direct consumer expansion, four actual measure workflows, aggregate comparison, 19 regression tests and hash finalization. `--simulate` runs one actual annual EnergyPlus smoke (about 22 seconds in the executed run). Schema/Schematron validation is never skipped. No energy-savings interpretation is produced.

## Exact executed consumer commands

The workflow uses the installed script's **`--xml`** option:

```bash
openstudio /home/o/.local/share/OpenStudio-HPXML-v1.12.0/workflow/run_simulation.rb \
  --xml /home/o/srvx-modeling-lab/evidence-core/heat-pump/issue-19-v0.1/model/MURB-samsung-17f.xml \
  --output-dir /home/o/srvx-modeling-lab/contributions/h2k-hpxml-issue-19/closeout/work/consumer-samsung-17f \
  --skip-simulation --debug
```

Equivalent runs cover `MURB-baseline.xml`, `MURB-current-downstream-defaults-COMPARISON.xml` and `MURB-synthetic-detailed-control.xml`. Full smoke omits `--skip-simulation` and writes to `work/simulation-samsung-17f`. `consumer_probe.rb` independently checks the installed parser/default expansion for nine synthetic points, COP preservation, scaled capacities and absence of conflicting fallback fields.

## Completion questions answered

| Question | Result |
|---|---|
| H2K capacity meaning | Explicit user/model output-capacity setting, internally kW, with 47°F rating condition in MURB; not a verified installed-size survey. |
| HPXML HeatingCapacity | Nominal model heating output at the consumer's 47°F reference. |
| Shape independent of size | Supported and executed as a scenario: 11,000/12,000 ratio with 47,883.93 model size unchanged. Physical correctness remains unresolved. |
| Detailed 47°F/17°F/5°F representation | Parsed, schema/rule checked and consumed with a separately marked complete synthetic control. Matched source lacks the required complete map. |
| Real candidate XSD/Schematron | The real 17°F-only candidate passes both. Incomplete full-map negative test has eight new rule failures despite passing XSD. |
| Consumer actually consumes points | Direct pinned parser/default expansion and full measure workflow both succeed for the synthetic control; actual real 17°F-only consumer and simulation also succeed. |
| Exact model fields changed | Real scenario: one 17°F Fraction text value. Synthetic control: remove stale fraction/empty extension, add detailed subtree. All unrelated model fields and nominal capacities preserved. |
| Performance comparisons | Distinct polynomial, executed legacy-input/current-default outputs, immutable published coefficients, experimental reconstruction, source equipment points and NEEP aggregate roles retained. |
| Upstream change justified? | No safe general behavior/input-interface change established; patch-not-justified artifact records Options A/B/C. |
| Smallest next upstream action | Share the precise issue evidence and agree on source completeness/interface/default policy; then test a verified real full-profile input. |

The old absolute-17°F toy adapter is retained as historical code and is not used for the real model. New guards refuse missing reference/COP/operating-level evidence rather than silently padding it. No default is replaced by the SRVX reconstruction. The source records, observations, projection calculations, model controls and findings remain distinct.

## Files and scope

`performance.py`, `freeze_source.py`, `translate_baseline.py`, `build_models.py`, `validate_models.py`, `consumer_probe.rb`, `collect_consumer.py`, `compare_profiles.py`, `render_comparison.py`, `test_performance.py`, `prepare_clean.py`, `finalize.py` and `reproduce.sh` implement the lab proof. `test-results.txt` records the regression run; `upstream-diff-stat.txt` explicitly records the absence of an upstream patch.

No OEM/component/AHRI-wide research, CityGML, fenestration upgrade or production integration was added. No remote issue/PR was posted, and the task does not claim issue #19 is fixed.
