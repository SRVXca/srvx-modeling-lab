# Upstream patch not established by this evidence

No change was made to the original translator working tree, its weather modification or the clean pinned copy. There is no placeholder patch.

The lab now demonstrates a safe-to-execute **17°F-only shape-transfer scenario**, retaining modeled nominal capacity, and consumer support for complete **synthetic** detailed inputs. This does not establish a source-complete 47°F/17°F/5°F performance map for the matched Samsung equipment.

Reasons to defer an upstream implementation:

1. The matched certificate supplies nominal 47°F/17°F capacity but no COP at those temperatures, no minimum/maximum surface, and no documented operating level for its 5°F field in the saved dictionary. Three capacity points alone introduce **eight** consumer rule failures in the negative test.
2. MURB retains a user-entered 14.0334 kW setting at a 47°F rating condition, two heads, and an equipment identity whose certified nominal capacity is 12,000 Btu/h. The 47°F reference basis is compatible for a scenario calculation; the physical installed combination/aggregation is not verified.
3. Removing the legacy constant (Option A) is an intentional modeling policy change. It produces the pinned consumer's 0.69 variable-speed default rather than 0.563635566. The example does not establish that this is generally correct for all legacy H2K inputs.
4. Published Addendum 82 (Option B) and reconstructed NEEP statistics are different references. The published scope excludes multi-splits; applicability to MURB's two-head input is unresolved. The reconstructed N=159/N=79 profiles must not become upstream defaults.
5. Optional externally supplied detailed profiles (Option C) are technically representable and covered by lab completeness/basis guards, but a verified real source-complete integration and a maintainer-approved input/interface are still missing. Synthetic consumer acceptance is not enough to call the matched equipment spine complete.

The smallest defensible next contribution is the issue report and reproducible evidence, plus a maintainer question: should external rated-shape enrichment be an explicit optional scenario boundary preserving H2K nominal size, and which verified complete source profile/input interface should that boundary accept? A future patch can keep existing fallback when no eligible evidence is supplied. No upstream default or 5°F COP is invented here.
