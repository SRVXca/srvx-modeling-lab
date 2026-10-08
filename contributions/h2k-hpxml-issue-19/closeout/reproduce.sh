#!/usr/bin/env bash
set -euo pipefail
task_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
lab_root="$(cd -- "$task_root/../../.." && pwd)"
bundle_root="$lab_root/evidence-core/heat-pump/issue-19-v0.1"
mkdir -p "$task_root/work"
export PYTHONDONTWRITEBYTECODE=1
export XDG_CONFIG_HOME="$task_root/work/config" XDG_CACHE_HOME="$task_root/work/cache" TMPDIR="$task_root/work"
if [ ! -f "$task_root/h2k-hpxml-clean/src/h2k_hpxml/core/translator.py" ]; then
  python3 "$task_root/prepare_clean.py"
fi
cd "$task_root/work"
"$lab_root/repos/canmet-energy/h2k-hpxml/.venv/bin/python" -B "$task_root/translate_baseline.py" > baseline-command.log 2>&1
python3 "$task_root/freeze_source.py"
python3 "$task_root/build_models.py"
python3 "$task_root/validate_models.py"
openstudio "$task_root/consumer_probe.rb" "$bundle_root/model/MURB-synthetic-detailed-control.xml" "$bundle_root/validation/detailed-consumer-control.json"
consumer_workflow=/home/o/.local/share/OpenStudio-HPXML-v1.12.0/workflow/run_simulation.rb
openstudio "$consumer_workflow" --xml "$bundle_root/model/MURB-baseline.xml" --output-dir "$task_root/work/consumer-baseline" --skip-simulation --debug > consumer-baseline.log 2>&1
openstudio "$consumer_workflow" --xml "$bundle_root/model/MURB-samsung-17f.xml" --output-dir "$task_root/work/consumer-samsung-17f" --skip-simulation --debug > consumer-samsung-17f.log 2>&1
openstudio "$consumer_workflow" --xml "$bundle_root/model/MURB-current-downstream-defaults-COMPARISON.xml" --output-dir "$task_root/work/consumer-current-defaults" --skip-simulation --debug > consumer-current-defaults.log 2>&1
openstudio "$consumer_workflow" --xml "$bundle_root/model/MURB-synthetic-detailed-control.xml" --output-dir "$task_root/work/consumer-synthetic-detailed" --skip-simulation --debug > consumer-synthetic-detailed.log 2>&1
if [ "${1:-}" = "--simulate" ]; then
  openstudio "$consumer_workflow" --xml "$bundle_root/model/MURB-samsung-17f.xml" --output-dir "$task_root/work/simulation-samsung-17f" --debug > simulation-samsung-17f.log 2>&1
fi
python3 "$task_root/compare_profiles.py" > comparison.log 2>&1
python3 "$task_root/collect_consumer.py"
python3 "$task_root/render_comparison.py"
python3 "$task_root/test_performance.py" | tee "$task_root/test-results.txt"
python3 "$task_root/finalize.py"
