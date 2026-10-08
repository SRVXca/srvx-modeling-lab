# Performance-profile comparison

Reference and model roles remain separate. Detailed numerical outputs are retained under `evidence-core/heat-pump/issue-19-v0.1/comparison/` and `validation/executed-consumer-workflows.json`; the figure is `comparison/performance-profiles.png`.

| Profile / evidence kind | 47°F nominal fraction | 17°F nominal fraction | 5°F nominal fraction | COP basis |
|---|---:|---:|---:|---|
| Legacy H2K polynomial, calculated and normalized at 47°F | 1.0 | 0.560959 | 0.438398 | Not derived as a measured COP surface here |
| Existing Canmet 17°F constant consumed by current OpenStudio-HPXML | 1.000001 | 0.563634 | 0.590261 | Modeled COPs 3.2205 / 2.3838 / 1.8473 |
| Current variable-speed downstream fallback (comparison only) | 1.000001 | 0.690002 | 0.722602 | Modeled COPs 2.9804 / 2.2061 / 1.7095 |
| Matched ENERGY STAR certificate, reported capacities | 1.0 | 0.916667 | **0.825, operating level unspecified** | Only reported 5°F COP=2.0; 47°F/17°F COP absent |
| 17°F source-ratio model scenario, remaining performance default-derived | 1.000001 | 0.916675 | 0.959988 | Modeled COPs 2.7912 / 2.0660 / 1.6010; not reported equipment COPs |
| NEEP Live variable-capacity population, raw-row-weighted means | reference 1.0 | 0.797836, N=152301 | 0.766587, N=152251 | Population capacities; no exact Samsung match in this snapshot |

Tiny executed-model deviations from exact ratios arise from the consumer's capacity rounding. The Canmet constant is a direct polynomial evaluation, not exactly the old curve's ratio normalized at 47°F. Supplying only the 17°F fraction does not supply a 5°F curve: the resulting 5°F value comes from the current consumer's model defaults.

## Published reference versus experimental reconstruction

**`RESNET_ADDENDUM_82_PUBLISHED`** retains the published 15 coefficients unchanged. **`SRVX_A82_RESEARCH_2026_10_08`** records a calculated current-data reconstruction, expressly not the official addendum or a recovered historical population. The exact raw performance fingerprint uses 56 fields; N=159 branded outdoor identities collapse to N=79 exact reported-performance fingerprints. This does not establish OEM identity or justify a default.

Published `Qr17full=0.817` means **Q17full/Q17max**, not Q17full/Q47full. Those different denominators must not be plotted or projected interchangeably. To compare coefficient-derived shapes, the retained comparison applies an explicit common illustrative **Q17full/Q47full=11/12** anchor:

```text
Q47max = 1 / Qr47full
Q47min = Q47max * Qr47min
Q17max = (11/12) / Qr17full
Q17min = Q17max * Qr17min
Q5max  = Q17max * Qm5max
Q5full = Q5max * Qr5full
Q5min  = Q5max * Qr5min
```

This produces full minimum/nominal/maximum capacity-fraction comparisons at 47°F/17°F/5°F without calling the anchor a universal or official retention. Published/reconstructed EIR ratios likewise have specific denominators and are not absolute COP values. All 15 means/errors and denominator definitions are retained separately; neither reconstruction becomes a source observation or upstream fallback.

The official [Addendum 82](https://www.resnet.us/wp-content/uploads/Addendum-82-HPAC-Modeling.pdf), approved December 17, 2025, supplies the reference coefficients. Its scope excludes multi-splits; applicability to MURB's two-head input has not been established. The benchmark is useful research context and current consumer behavior, not proof that this model is within a rating standard's scope.
