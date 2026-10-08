#!/usr/bin/env python3
"""Dependency-free lab registry/fixture structural checks; not a complete HPXML validator."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def load(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))
families=load("registry/equipment-families.v0.1.json")["families"]
contracts=load("registry/technical-contracts.v0.1.json")["contracts"]
sources=load("registry/source-datasets.v0.1.json")["sourceDatasets"]
fixture=load("fixtures/equipment/synthetic-ashp-observation.v0.1.json")
schema=load("contracts/equipment-observation.v0.1.schema.json")
family_ids=[f["id"] for f in families]
source_ids=[s["id"] for s in sources]
assert len(family_ids)==6 and len(set(family_ids))==6
assert len(source_ids)==len(set(source_ids))
for family in families:
    assert family["technicalContracts"], family["id"]
    assert all(name in contracts for name in family["technicalContracts"])
for source in sources:
    assert set(source["families"]) <= set(family_ids), source["id"]
for key in schema["required"]:
    assert key in fixture, key
assert fixture["family"] in family_ids
assert fixture["contract"] in [f for obj in families if obj["id"]==fixture["family"] for f in obj["technicalContracts"]]
assert fixture["metric"] in contracts[fixture["contract"]]["fields"]
assert fixture["unit"] in contracts[fixture["contract"]]["fields"][fixture["metric"]]["allowedUnits"]
assert fixture["source"]["datasetId"] in source_ids
assert fixture["synthetic"] is True and fixture["publicationAllowed"] is False
assert fixture["evidenceKind"]=="SYNTHETIC_TEST_FIXTURE"
assert all(fixture["source"].get(k) for k in schema["properties"]["source"]["required"])
print(f"PASS: {len(family_ids)} families; {len(sources)} source registries; {len(contracts)} technical contracts; synthetic fixture gates")
try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError:
    print("INFO: jsonschema not installed; semantic/structural checks only")
else:
    Draft202012Validator(schema,format_checker=FormatChecker()).validate(fixture)
    print("PASS: JSON Schema Draft 2020-12 fixture validation")
