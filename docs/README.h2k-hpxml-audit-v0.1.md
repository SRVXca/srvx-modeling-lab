# Additive H2K / HPXML field audit v0.1

This bundle contains **only new, namespaced files** intended for `~/srvx-modeling-lab`. It does not modify the existing seven equipment-spine v0.1 files, submodules, commits, other SRVX repos, or remotes. All H2K fields remain `PENDING_LOCAL_XML_TRANSLATOR_AUDIT`.

1. Extract at the lab root with `tar --keep-old-files -xzf <bundle.tar.gz> -C ~/srvx-modeling-lab` (refuses to replace existing files).
2. `cd ~/srvx-modeling-lab && python3 tests/test-h2k-hpxml-field-audit.py`
3. `python3 scripts/audit-h2k-hpxml-local.py`
4. Inspect `docs/h2k-hpxml-field-audit-v0.1.md`, the CSV matrix and the generated candidate evidence in `var/modeling-audit/h2k-hpxml-v0.1/`.

The test requires Python 3 only; source scanner does not access network, modify .H2K files, use Git, or run EnergyPlus/HOT2000.
