#!/usr/bin/env python3
"""Validate the WizardHouse replacement against the local HPXML XSD."""
import json
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

try:
    from lxml import etree
except ImportError:
    sys.exit("Missing lxml. Install it in your lab Python environment.")

evidence = Path("evidence-core/fenestration/v0.1")
golden = Path(
    "repos/canmet-energy/h2k-hpxml/tests/fixtures/"
    "expected_outputs/golden_files/baseline/"
    "baseline_WizardHouse.xml"
)
replacement = evidence / "model/WizardHouse-NRCan-replacement.v0.4.xml"
projection = json.loads(
    (evidence / "projection/nrcan-window-projection.v0.3.json").read_text()
)

schema_path = Path(
    "repos/NatLabRockies/OpenStudio-HPXML/"
    "HPXMLtoOpenStudio/resources/hpxml_schema/HPXML.xsd"
)

def find_window(root, label):
    matches = [
        w for w in root.findall(".//{*}Window")
        if w.findtext("{*}extension/{*}H2kLabel") == label
    ]
    assert len(matches) == 1, (label, len(matches))
    return matches[0]

# Independently reconstruct the two permitted field changes.
original = ET.parse(golden).getroot()
actual = ET.parse(replacement).getroot()
label = projection["opening"]
window = find_window(original, label)

for field in ("UFactor", "SHGC"):
    value = projection["candidateWindow"][field]
    window.find("{*}" + field).text = str(value)

assert ET.tostring(original) == ET.tostring(actual), (
    "Replacement contains differences beyond the permitted fields"
)
print("PASS: exact two-field replacement")

if not schema_path.is_file():
    sys.exit(f"Full HPXML schema not found: {schema_path}")

schema_root = ET.parse(schema_path).getroot()
schema_ns = schema_root.attrib.get("targetNamespace")
schema_version = schema_root.attrib.get("version")

source_root = ET.parse(golden).getroot()
document_ns = source_root.tag.split("}")[0].lstrip("{")
document_version = source_root.attrib.get("schemaVersion")

print("Schema version:", schema_version)
print("Document version:", document_version)

if schema_ns != document_ns or schema_version != document_version:
    sys.exit(
        "SCHEMA VERSION MISMATCH: local OpenStudio-HPXML "
        "schema does not match the document. No files changed."
    )

schema = etree.XMLSchema(etree.parse(str(schema_path)))

results = {}
for name, path in (
    ("original", golden),
    ("replacement", replacement),
):
    doc = etree.parse(str(path))
    valid = schema.validate(doc)
    errors = [
        {"line": e.line, "message": e.message}
        for e in schema.error_log
    ]

    results[name] = {
        "valid": valid,
        "errors": errors,
    }

    print(f"\n{name.upper()}: {'PASS' if valid else 'FAIL'}")
    for e in errors[:8]:
        print(f"  line {e['line']}: {e['message']}")

status = (
    "XSD_PASS" if all(r["valid"] for r in results.values())
    else "BASELINE_XSD_INVALID" if not results["original"]["valid"]
    else "REPLACEMENT_XSD_INVALID"
)

report = {
    "status": status,
    "documentVersion": document_version,
    "schemaVersion": schema_version,
    "schemaPath": str(schema_path),
    "onlyTwoFieldsChanged": True,
    "results": results,
    "schematronValidated": False,
    "simulationExecuted": False,
}

dest = evidence / "validation/replacement-xsd-validation.v0.5.json"
dest.write_text(json.dumps(report, indent=2) + "\n")

print("\nSTATUS:", status)
print("REPORT:", dest)

if status != "XSD_PASS":
    sys.exit(1)
