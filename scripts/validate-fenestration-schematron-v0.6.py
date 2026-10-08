#!/usr/bin/env python3
"""Independent Schematron comparison of original and modified HPXML."""
import hashlib
import json
from collections import Counter
from pathlib import Path
from lxml import etree, isoschematron

lab = Path("var/modeling-audit/fenestration-v0.1")
golden = Path(
    "repos/canmet-energy/h2k-hpxml/tests/fixtures/"
    "expected_outputs/golden_files/baseline/baseline_WizardHouse.xml"
)
candidate = lab / "WizardHouse-NRCan-replacement.v0.4.xml"
rules = Path(
    "repos/NatLabRockies/OpenStudio-HPXML/"
    "HPXMLtoOpenStudio/resources/hpxml_schematron/EPvalidator.sch"
)

svrl = {"svrl": "http://purl.oclc.org/dsdl/svrl"}

rule_ns = etree.parse(str(rules)).getroot().find(
    "{http://purl.oclc.org/dsdl/schematron}ns"
).get("uri")

for path in (golden, candidate):
    doc = etree.parse(str(path)).getroot()
    assert doc.tag == f"{{{rule_ns}}}HPXML", (
        "HPXML namespace and Schematron version mismatch"
    )

validator = isoschematron.Schematron(
    etree.parse(str(rules)),
    store_report=True,
)

def inspect(path):
    validator.validate(etree.parse(str(path)))
    report = validator.validation_report
    assert report is not None, "Missing Schematron validation report"

    result = {"errors": [], "warnings": []}

    for node_type, category in (
        ("failed-assert", "errors"),
        ("successful-report", "warnings"),
    ):
        for node in report.xpath(
            f"//svrl:{node_type}", namespaces=svrl
        ):
            message = " ".join(
                node.xpath("./svrl:text/text()", namespaces=svrl)
            ).strip()

            result[category].append({
                "test": node.get("test"),
                "location": node.get("location"),
                "message": message,
            })

    return result

original = inspect(golden)
replacement = inspect(candidate)

def signature(item):
    return (item["test"], item["location"], item["message"])

baseline_errors = Counter(map(signature, original["errors"]))
replacement_errors = Counter(map(signature, replacement["errors"]))
introduced = list((replacement_errors - baseline_errors).elements())

if not original["errors"] and not replacement["errors"]:
    status = "SCHEMATRON_PASS"
elif introduced:
    status = "NEW_RULE_FAILURES"
else:
    status = "BASELINE_RULE_FAILURES_UNCHANGED"

output = {
    "status": status,
    "validator": "lxml.isoschematron",
    "rulesSha256": hashlib.sha256(rules.read_bytes()).hexdigest(),
    "original": original,
    "replacement": replacement,
    "introducedErrors": introduced,
    "simulationExecuted": False,
}

dest = lab / "replacement-schematron-validation.v0.6.json"
dest.write_text(json.dumps(output, indent=2) + "\n")

print("=== SCHEMATRON VALIDATION ===")
for name, result in (("Original", original), ("Replacement", replacement)):
    print(
        f"{name}: {len(result['errors'])} errors, "
        f"{len(result['warnings'])} warnings"
    )

print("Introduced errors:", len(introduced))
for error in introduced[:10]:
    print("  NEW:", error[2])

print("STATUS:", status)
print("REPORT:", dest)

if status != "SCHEMATRON_PASS":
    raise SystemExit(1)
