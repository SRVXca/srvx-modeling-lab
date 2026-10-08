# ASTRA TASK — Prepare the h2k-hpxml #19 contribution for upstream review

Task brief prepared October 8, 2026. Execute this as one bounded modeling-lab task.

## Objective

Consolidate the existing low-temperature heat-pump investigation into a small, reproducible, review-ready contribution for [canmet-energy/h2k-hpxml issue #19](https://github.com/canmet-energy/h2k-hpxml/issues/19).

The immediate result is an evidence-backed issue response and supporting reproduction package. A code change is included only when a specific correction is established by the source and tests; a research contribution can be useful without selecting a new population-wide fallback.

Prioritize: verified existing findings → repeatable fixture reproduction → concise upstream draft → clear remaining decisions. Finish this package before starting SRVX Docs design, equipment-data integration or further research sweeps.

## Workspace and boundaries

- Sole writable workspace: `/home/o/srvx-modeling-lab`.
- Primary existing work: `contributions/h2k-hpxml-issue-19/`.
- New closeout artifacts: `contributions/h2k-hpxml-issue-19/closeout/`. Inspect first; preserve any existing artifacts.
- Read-only dependencies: `repos/canmet-energy/h2k-hpxml`, `repos/NatLabRockies/OpenStudio-HPXML`, other cloned third-party repositories and `/home/o/nova-open`.
- Preserve all unrelated tracked/untracked work. In particular, the h2k-hpxml checkout currently has an unrelated modification to `src/h2k_hpxml/utils/weather_files.py`; do not reset, incorporate or claim that change as part of #19.
- If translator execution or a candidate correction requires writes inside a checkout, use a bounded scratch copy of the pinned committed source under `closeout/work/`. Save any proposed upstream changes as a focused patch artifact; keep the dependency checkout unchanged.
- No production repository edits, database writes/migrations, canonical SRVX classifications, publishing contracts, websites or deployments.
- Use existing local snapshots/tools. No bulk downloads, large installations, live catalog ingestion or new generalized equipment framework. Keep caches, temporary models and outputs inside the lab.
- Prepare local GitHub issue/PR text. Posting, contacting researchers/maintainers, opening a remote PR, and merging are separate actions outside this task.

## Inputs to inspect first

Read these existing files before changing logic:

1. `contributions/h2k-hpxml-issue-19/README.md` and `energy-star-vs-h2k.md`.
2. `analyze_h2k_curve.py`, `analyze_energy_star_vs_h2k.py`, `energy_star_adapter.py`, `low_temp_performance_adapter.py` and the three `test_*.py` scripts in that directory.
3. `source-study/neep/SOURCE-STUDY.md`, its source manifests/adapters/tests and the saved `neep_air_source_heat_pump_2026-10-07.xlsx`.
4. `analysis/addendum82-populations/README.md`, `run.py`, `results.json` and the existing relevant summary outputs. Later exploratory population/OEM scripts are context, not a requirement to rerun every sweep.
5. `docs/h2k-hpxml-field-audit-v0.1.md`, `docs/BOUNDARY.md` and `var/modeling-audit/h2k-hpxml-v0.1/paired-values-MURB.v0.4.json`.
6. `repos/canmet-energy/h2k-hpxml/src/h2k_hpxml/components/system_heat_pumps.py`, its unit tests and `src/h2k_hpxml/examples/MURB.h2k`.
7. The installed OpenStudio-HPXML `HPXMLtoOpenStudio/resources/hpxml.rb`, `defaults.rb`, `hvac.rb`, HPXML XSD and `hpxml_schematron/EPvalidator.sch`.
8. The actual issue #19 body and any accessible comments/linked changes. Read-only access is allowed; record retrieval date and limitations if the full thread cannot be read.

ENERGY STAR analysis currently reads the saved source under `/home/o/nova-open/data/supply/air-source-heat-pump-v0.1/` (`energy-star.csv.gz`, `metadata.json.gz`, `source.json`). Keep that source read only. Avoid copying the full snapshot into the closeout package.

Record exact repository commits, source-file/snapshot hashes, observation dates and tool versions. The inspected h2k-hpxml commit was `0b77fcee8f1c717f0bfd02e4b5924c84244a9b6b`; inspect and pin what actually exists when executing.

## Known issues to resolve through evidence

These are starting observations, not a predetermined fix:

- Issue #19 was opened May 13, 2025. Its body discusses absent H2K 17°F capacity and older OpenStudio defaults at 5°F. The public page was open on October 8, 2026. Separate the issue-era defaults from the pinned current software behavior.
- The local translator emits `HeatingCapacityFraction17F/Fraction = 0.563635566` for mini-split and air-to-air branches. Existing analysis relates this to the legacy H2K curve evaluated at 17°F; direct polynomial evaluation and a ratio normalized at 47°F are distinct quantities.
- The installed OpenStudio-HPXML source includes detailed performance at 5°F. Do not start from the assumption that HPXML/OpenStudio cannot hold 5°F data. Determine separately what H2K contains, what Canmet currently emits, what the HPXML schema permits and what the pinned OpenStudio consumer accepts/defaults.
- The exact ENERGY STAR example for AHRI `210448841` has reported capacities 12,000 / 11,000 / 9,900 Btu/h at 47°F / 17°F / 5°F. Reverify against the saved source and its equipment combination before treating it as matched evidence.
- The existing paired MURB audit records translated nominal capacity about **47,883.93 Btu/h**, not 12,000 Btu/h; it also says `converterRerun: false`. This discrepancy is central to the reproduction. Establish system count, capacity basis and equipment identity; an AHRI match alone does not settle installed capacity or aggregation.
- The current lab adapter writes an absolute `HeatingCapacity17F` and removes fallback fields. Its chain test uses a synthetic 12,000-Btu/h nominal capacity. Audit behavior when the actual H2K capacity differs before describing this as a safe real-fixture enrichment.
- NEEP's source study found no record for that exact AHRI query at its observation date. Do not invent an exact NEEP match or turn that dated observation into a permanent absence claim.
- Addendum 82 population similarity does not identify its original population or justify selecting filters/fallbacks by lowest error. Preserve exploratory OEM/rebranding/platform relationships as hypotheses unless independently verified.

## Work to perform

### 1. Reproduce the useful existing results

Run the relevant adapter tests, curve calculation and source analyses with logged commands. Before running scripts, inspect their output paths: some overwrite existing reports and include run timestamps. Parameterize outputs or run bounded scratch copies so existing evidence remains intact.

Recompute the principal ENERGY STAR 17°F/47°F and 5°F/47°F statistics from the saved snapshot. Record valid/missing/conflicting counts, deduplication basis and population definitions. Reconcile differences between summaries instead of choosing whichever count is convenient. Rerun only the NEEP baseline and the small number of existing comparisons necessary for an issue-relevant conclusion.

Separate scientific numeric repeatability from incidental timestamp/format differences. Do not claim reproduction solely because an old JSON/report file exists. If a primary derivation or reference is unavailable, disclose the missing provenance instead of treating a hardcoded number as independently verified.

### 2. Trace 17°F and 5°F semantics

Create a compact source-referenced table for:

- H2K observed fields and translator reads;
- Canmet HPXML fields actually emitted;
- HPXML schema representation, including version;
- OpenStudio-HPXML accepted fields, precedence and defaults in the pinned version;
- observed ENERGY STAR/NEEP performance versus inferred/fallback values.

Distinguish rated/nominal/minimum/maximum capacities, test temperatures, capacity fractions, absolute capacity, power and COP. Keep 17°F and 5°F conclusions separate. Identify deprecated inputs and relevant Schematron constraints. Do not create COP, compressor staging or missing performance points to complete a schema.

### 3. Reproduce one real translator fixture

Use MURB as the first fixture, with clean pinned translator source in the lab scratch directory. Produce and inspect a fresh baseline HPXML output, or report the exact execution dependency that prevents it. Record where capacities, AHRI identity, system count and autosizing inputs originate and how the baseline becomes the resulting HPXML.

For the existing enrichment example, explicitly test the mismatch between source-certified and H2K nominal capacity. Determine which absolute-capacity, shape-preserving ratio or no-enrichment behavior is supportable for that case. Do not silently pick a new universal rule. Any experimentally scaled value must be labeled calculated and its formula/basis disclosed.

Validate a proposed HPXML example against the pinned XSD and relevant consumer Schematron where available. SDK load, schema validation and successful energy simulation are separate checks; report only what ran. A full simulation or a new heat-pump installation in the CityGML example is not required.

### 4. Resolve mechanical defects and prepare the contribution

Fix narrowly scoped reproduction/test/provenance defects within the lab when necessary. Meaningful tests should cover missing, zero/negative and nonfinite values; conflicting identities/capacity records; differing nominal capacity; preservation of unrelated fields; and unchanged fallback when usable external evidence is absent. Do not add tests merely to mirror implementation details.

Prepare an upstream issue response that explains the verified problem, one real reproduction, version-specific semantics, relevant population evidence and the smallest justified recommendation. Lead with results; put longer methodology and unresolved questions in the supporting report. Keep SRVX promotion/marketing and broad OEM investigations out of the issue response.

If a concrete translator correction is established, provide a minimal patch and meaningful regression tests as local artifacts, plus a draft PR description. Preserve current fallback behavior when evidence is unavailable unless the correction itself establishes that behavior as invalid. Do not replace defaults with population medians or add an online AHRI/NEEP dependency without an agreed policy.

If the evidence does not establish a safe code change, deliver a complete research contribution with a precise maintainer question and an explicit statement that no implementation fix has been established. This can complete the review package; it does not mean the upstream issue is resolved.

### 5. Keep the sharing package bounded

Prepare the package using minimal permitted fixtures, aggregate findings, scripts and source links. Record source notices and known permission limits. The saved NEEP XLSX includes a non-commercial-use notice; local research access does not establish permission to republish raw exports, derived extracts or put them into SRVX commercial inventory. Mark uncertain sharing rights as unresolved and omit affected source payloads from the candidate sharing bundle.

Do not contact NEEP or others as part of this task. A short rights/provenance inventory is sufficient; a partnership plan, public dataset launch, bilingual publication pipeline and legal review are separate work.

## Deliverables

Keep the package under `contributions/h2k-hpxml-issue-19/closeout/`:

- `README.md`: scope, exact inputs/versions, reproduction commands and readiness status.
- `evidence-manifest.json`: selected source artifacts, hashes, observation dates, populations, claims and sharing-status notes. Keep this experiment-specific.
- `findings.md`: verified conclusions, 17°F/5°F semantics table, MURB capacity reconciliation, limitations and explicitly unresolved decisions.
- `upstream-issue-response.md`: concise English draft suitable for the maintainer thread, with source/method links and one clear next action.
- A runner/tests, small appropriate fixtures, fresh validation outputs and a command/results log. Existing test scripts may be reused; avoid needless restructuring.
- `proposed.patch` and `upstream-pr-description.md` only if a concrete, tested correction is supported. Otherwise state why a code proposal is not yet justified.
- `sharing-inventory.md`: what can be considered for sharing, what was omitted, and which permission questions remain. Do not assert unrestricted rights from public accessibility.

Adjust names if necessary, but deliver the complete review package rather than only another plan.

## Acceptance criteria

1. Every material claim in the draft is traceable to a dated source and an executed analysis or a clearly identified existing source observation.
2. Baseline translator output is freshly reproduced, or the exact missing execution dependency is disclosed; pre-existing output is not described as a new run.
3. The 47,883.93-versus-12,000 capacity mismatch is reconciled or remains a prominent blocker to absolute-capacity enrichment.
4. 17°F fields, 5°F data, issue-era defaults and current consumer behavior are not conflated.
5. Relevant tests and pinned schema/consumer checks have actual results, including meaningful failure cases.
6. Raw restricted data, unverified OEM identities and analysis-derived metrics are not promoted into public/canonical source observations.
7. No unrelated repository changes or remote publication are performed.
8. One documented command reproduces the selected checks using existing local inputs, with exact limitations and a small set of remaining maintainer decisions.

## Completion report

Return a compact report giving created paths, exact commands and test results, verified conclusions, any proposed patch, remaining scientific/maintainer/permission decisions, and whether the package is ready for upstream review.

Do not claim that issue #19 is fixed or closed because the draft/package is complete. Do not expand into SRVX Docs architecture or additional equipment/model integration during this task.
