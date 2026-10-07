# ENERGY STAR ASHP vs legacy H2K low-temperature capacity

Generated: 2026-10-07T16:39:01.368100+00:00

This analysis is an upstream contribution artifact for `canmet-energy/h2k-hpxml` issue #19. It is independent of SRVX normalization/canonicalization.

## Dataset

- ENERGY STAR snapshot rows: **284,866**
- Rows without AHRI reference: **12**
- Usable row-level 17°F/47°F ratios: **282,929**
- Usable row-level 5°F/47°F ratios: **282,145**
- Unambiguous AHRI 17°F/47°F ratios: **282,519**
- AHRI capacity-pair conflicts for 17°F/47°F: **5**
- AHRI classification conflicts excluded from 17°F grouped statistics: **0**
- Unambiguous AHRI 5°F/47°F ratios: **281,703**
- AHRI capacity-pair conflicts for 5°F/47°F: **20**
- AHRI classification conflicts excluded from 5°F grouped statistics: **0**

## Legacy H2K curve

| Quantity | Value |
|---|---:|
| H2K direct multiplier @ 47°F | 1.004770666 |
| H2K direct multiplier @ 17°F | 0.563635566 |
| Canmet hardcoded 17°F fraction | 0.563635566 |
| H2K direct multiplier @ 5°F | 0.440489640 |
| H2K normalized 17°F / 47°F | 0.560959416 |
| H2K normalized 5°F / 47°F | 0.438398189 |

The Canmet constant matches the legacy H2K curve evaluated directly at 17°F. It is not exactly the same as normalizing the legacy curve's 17°F value against its 47°F value because the old polynomial evaluates slightly above 1.0 at 47°F.

## OpenStudio-HPXML v1.12 defaults

| Compressor type | Default 17°F / 47°F |
|---|---:|
| Single-stage | 0.626 |
| Two-stage | 0.626 |
| Variable-speed | 0.690 |

These are OpenStudio-HPXML defaults used only when explicit 17°F capacity information, an explicit 17°F fraction, and suitable detailed performance data are absent.

## ENERGY STAR distributions

| Population | n | mean | p10 | p25 | median | p75 | p90 | min | max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 17°F / 47°F — raw rows | 282,929 | 0.7527 | 0.6080 | 0.6442 | 0.7402 | 0.8432 | 0.9300 | 0.0781 | 2.4848 |
| 17°F / 47°F — AHRI deduped | 282,519 | 0.7527 | 0.6080 | 0.6441 | 0.7388 | 0.8435 | 0.9300 | 0.0781 | 2.4848 |
| 5°F / 47°F — raw rows | 282,145 | 0.6732 | 0.4784 | 0.5181 | 0.7079 | 0.7966 | 0.8629 | 0.1684 | 3.8333 |
| 5°F / 47°F — AHRI deduped | 281,703 | 0.6729 | 0.4783 | 0.5180 | 0.7079 | 0.7965 | 0.8629 | 0.1684 | 3.8333 |

## Baseline comparison

| Comparison | baseline | median − baseline | median relative difference | below baseline | above baseline | mean absolute delta |
|---|---:|---:|---:|---:|---:|---:|
| Certified 17/47 vs Canmet translator | 0.563635566 | +0.1752 | +31.1% | 0.7% | 99.3% | 0.1891 |
| Certified 17/47 vs normalized H2K curve | 0.560959416 | +0.1778 | +31.7% | 0.3% | 99.7% | 0.1918 |
| Certified 5/47 vs normalized H2K curve | 0.438398189 | +0.2695 | +61.5% | 1.1% | 98.9% | 0.2348 |

Ratios greater than 1.0 are retained; the analysis does not assume they are errors.

## Largest ENERGY STAR groups — 17°F / 47°F, AHRI-deduped

| Product type | Compressor staging | Cold climate | n | Canmet | OS v1.12 default | p10 | median | p90 |
|---|---|---|---:|---:|---:|---:|---:|---:|
| HP - Split System | Continuously variable | Yes | 121,092 | 0.564 | 0.690 | 0.7065 | 0.8265 | 0.9357 |
| HP - Split System | Two-stage | No | 63,452 | 0.564 | 0.626 | 0.5894 | 0.6384 | 0.6923 |
| HP - Split System | Single stage | No | 50,461 | 0.564 | 0.626 | 0.5989 | 0.6500 | 0.6826 |
| HP - Split System | Continuously variable | No | 19,819 | 0.564 | 0.690 | 0.6298 | 0.8193 | 1.0054 |
| HP - Mini or Multi Split | Continuously variable | Yes | 14,830 | 0.564 | 0.690 | 0.6458 | 0.8250 | 1.0000 |
| HP - Split System | Two-stage | Yes | 9,436 | 0.564 | 0.626 | 0.6564 | 0.9573 | 1.0185 |
| HP - Mini or Multi Split | Continuously variable | No | 2,578 | 0.564 | 0.690 | 0.5888 | 0.7000 | 0.8333 |
| HP - Single Package | Continuously variable | Yes | 495 | 0.564 | 0.690 | 0.6944 | 0.8444 | 1.0854 |
| HP - Single Package | Two-stage | No | 346 | 0.564 | 0.626 | 0.5441 | 0.5778 | 0.6696 |

## Largest ENERGY STAR groups — 5°F / 47°F, AHRI-deduped

| Product type | Compressor staging | Cold climate | n | Canmet 17°F* | OS v1.12 17°F default* | p10 | median | p90 |
|---|---|---|---:|---:|---:|---:|---:|---:|
| HP - Split System | Continuously variable | Yes | 121,092 | 0.564 | 0.690 | 0.7083 | 0.7698 | 0.8743 |
| HP - Split System | Two-stage | No | 62,933 | 0.564 | 0.626 | 0.4476 | 0.5155 | 0.5696 |
| HP - Split System | Single stage | No | 50,415 | 0.564 | 0.626 | 0.4575 | 0.5051 | 0.5427 |
| HP - Split System | Continuously variable | No | 19,734 | 0.564 | 0.690 | 0.5600 | 0.6697 | 0.8087 |
| HP - Mini or Multi Split | Continuously variable | Yes | 14,815 | 0.564 | 0.690 | 0.7068 | 0.8833 | 1.0278 |
| HP - Split System | Two-stage | Yes | 9,436 | 0.564 | 0.626 | 0.4800 | 0.7906 | 0.8438 |
| HP - Mini or Multi Split | Continuously variable | No | 2,457 | 0.564 | 0.690 | 0.5200 | 0.6611 | 0.7667 |
| HP - Single Package | Continuously variable | Yes | 495 | 0.564 | 0.690 | 0.5775 | 0.7195 | 0.7895 |
| HP - Single Package | Two-stage | No | 316 | 0.564 | 0.626 | 0.3692 | 0.4318 | 0.5474 |

\* Canmet and OpenStudio columns are 17°F references shown only for context; neither is a 5°F translator input. The 5°F ENERGY STAR distribution is compared to the legacy H2K curve separately above.

## Exact h2k-hpxml MURB fixture match

- AHRI: `210448841`
- ENERGY STAR pd_id: `2469692`
- Product type: `HP - Mini or Multi Split`
- Compressor: `Continuously variable`
- Cold climate: `No`
- Q47: **12000 Btu/h**
- Q17: **11000 Btu/h**
- Q5: **9900 Btu/h**
- Q17/Q47: **0.916666667**
- Q5/Q47: **0.825000000**

## Interpretation guardrail

This analysis compares certified equipment capacity *shape* with the low-temperature capacity fraction consumed by OpenStudio-HPXML. It does not replace the H2K user-entered nominal capacity with the ENERGY STAR nameplate capacity.
