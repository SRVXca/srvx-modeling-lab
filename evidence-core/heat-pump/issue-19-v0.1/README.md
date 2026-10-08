# Heat-pump issue #19 evidence spine v0.1

Status: **REAL 17°F-ONLY SPINE VALIDATED; MATCHED DETAILED 47°F/17°F/5°F PROFILE BLOCKED**.

The task dated October 8, 2026 has produced a reproducible, bounded closeout. It does not claim issue #19 is fixed or that the full matched-equipment spine has reached fenestration parity.

```text
ENERGY STAR SourceRecord (AHRI 210448841 / pd_id 2469692)
→ four provenance-preserving HeatPumpPerformance observations
→ normalized 17°F/47°F shape projection
→ freshly translated real MURB HPXML (nominal size preserved)
→ exact one-field diff
→ HPXML 5.0 XSD + pinned consumer Schematron
→ actual OpenStudio-HPXML processing + simulation execution smoke
→ limited scenario finding; installed-system fidelity unresolved
```

The clean pinned MURB input declares **14.0334 kW**, user-specified, with a **47°F** rating condition. Its output **47,883.93 Btu/h** is preserved. The external certificate's **12,000 Btu/h** is used only as the denominator of **11,000/12,000 = 0.9166667**. UI display units do not change the translator's kW field mapping. Physical system count/configuration remains unresolved; two declared heads do not establish an aggregation conversion.

The real candidate `model/MURB-samsung-17f.xml` changes only the 17°F fraction. It validates against XSD/Schematron with zero new failures. Its **5°F behavior remains a consumer default**, not the certificate's 5°F point. The source 5°F value and COP are retained without guessing their operating level. COPs at 47°F/17°F and minimum/maximum curves are unavailable.

A separate **synthetic** nine-point consumer control demonstrates that 47°F/17°F/5°F detailed fractions, minimum/nominal/maximum descriptions and COPs are parsed and consumed by the installed software while nominal size stays unchanged. It is not Samsung/NEEP equipment evidence. A deliberately incomplete detail-map negative test is XSD-valid but has eight new Schematron failures.

## Reproduction

From `/home/o/srvx-modeling-lab`:

```bash
bash contributions/h2k-hpxml-issue-19/closeout/reproduce.sh
# Include the already demonstrated full simulation smoke:
bash contributions/h2k-hpxml-issue-19/closeout/reproduce.sh --simulate
```

The runner uses existing local datasets, Python environments, weather and installed consumer code; it does not download packages/data. It creates a clean git-archive copy if absent and directs logs/config/cache into `closeout/work/`. The original dirty translator working tree is unchanged. Runtime paths are local prerequisites, not redistributed datasets. A normal rerun uses roughly four consumer measure runs plus one streamed NEEP aggregate pass; `--simulate` adds one annual execution smoke. No savings conclusion is made.

## Artifacts and versions

| Directory | Selected evidence |
|---|---|
| `source-record/` | One public, source-shaped ENERGY STAR record and its snapshot manifest/hash. No raw NEEP bulk payload. |
| `observation/` | Real performance points/flat contract-validated observations, rating basis, source fields and explicit missing values. |
| `projection/` | Validated limited 17°F projection, blocked complete-equipment projection and separately labelled synthetic control/negative input. |
| `model/` | Fresh baseline, real 17°F-only candidate, complete synthetic control, current-fallback comparison and deliberately invalid negative test. |
| `validation/` | Exact diffs, XSD/Schematron/SVRL results, actual consumer parsing/workflows, unit tests and simulation smoke status. |
| `comparison/` | Immutable published Addendum 82 coefficients, separately labelled current-data reconstruction, NEEP population aggregates and figure. |
| `audit/` | Existing historical audits plus fresh translator basis/identity and pinned tool/source hashes. |
| `ARTIFACTS.sha256` | Hash manifest for all selected bundle artifacts, excluding the manifest itself. |

Pinned translator: `0b77fcee8f1c717f0bfd02e4b5924c84244a9b6b`; OpenStudio **3.11.0+241b8abb4d**; OpenStudio-HPXML **1.12.0**; HPXML **5.0**, namespace `http://hpxmlonline.com/2025/12`. The installed consumer files, schema/rules and local weather are hashed in audit/validation artifacts.

**19 lab regression tests pass.** Both valid model cases and the baseline pass XSD/Schematron. The full 17°F-only scenario simulation reported six warnings and zero severe errors. These are distinct checks; no complete matched equipment map or installed-performance validity is claimed.

## Finding and upstream outcome

Normalized equipment shape and modeled nominal size are representable independently when rating basis agrees. For this fixture the 47°F basis is explicit. Full detailed projection additionally requires complete, appropriately labelled capacity/COP points; source identity alone does not supply them.

The NEEP reconstruction reproduces **N=159**, mean relative error **2.734516%**, maximum metric error **7.982842%**; exact clone collapse gives **N=79**, mean relative error **2.852760%**. These remain calculated experimental references, not official Addendum 82, recovered historical populations or upstream defaults.

No safe upstream behavior change was established. See [closeout README](../../../contributions/h2k-hpxml-issue-19/closeout/README.md), `projection-semantics.md`, `mechanical-findings.md`, `performance-profile-comparison.md` and `upstream.patch.NOT_JUSTIFIED.md` in that folder. Population/OEM analyses remain separate from source observations; no SRVX production contract was changed.
