import json
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from lxml import etree, isoschematron

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "var/modeling-audit/fenestration-v0.1"
REPO = ROOT / "repos/canmet-energy/h2k-hpxml"
OS = ROOT / "repos/NatLabRockies/OpenStudio-HPXML"

ORIGINAL = REPO / (
    "tests/fixtures/expected_outputs/golden_files/"
    "baseline/baseline_WizardHouse.xml"
)
REPLACEMENT = LAB / "WizardHouse-NRCan-replacement.v0.4.xml"
XSD = OS / "HPXMLtoOpenStudio/resources/hpxml_schema/HPXML.xsd"
SCH = OS / "HPXMLtoOpenStudio/resources/hpxml_schematron/EPvalidator.sch"


def load(name):
    return json.loads((LAB / name).read_text())


def window(root, label):
    matches = [
        w for w in root.findall(".//{*}Window")
        if w.findtext("{*}extension/{*}H2kLabel") == label
    ]
    assert len(matches) == 1
    return matches[0]


class FenestrationSpineV07(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = load("nrcan-window-source-record.v0.3.json")
        cls.observation = load("nrcan-window-observation.v0.3.json")
        cls.projection = load("nrcan-window-projection.v0.3.json")

    def test_source_identity(self):
        s, o, p = self.source, self.observation, self.projection
        self.assertEqual(s["sourceRecordId"], o["sourceRecordId"])
        self.assertEqual(s["sourceRecordId"], p["productEvidence"])
        self.assertEqual(s["sourceUrl"], o["sourceUrl"])
        self.assertEqual(s["captureMethod"], "MANUAL_REFERENCE_FIXTURE")

    def test_metric_provenance(self):
        raw = self.source["raw"]
        metrics = {m["name"]: m for m in self.observation["metrics"]}

        for metric in metrics.values():
            self.assertIn(metric["sourceField"], raw)
            self.assertEqual(
                metric["value"], raw[metric["sourceField"]]
            )

        u = metrics["wholeAssemblyUFactor"]
        shgc = metrics["solarHeatGainCoefficient"]

        self.assertEqual(u["unit"], "W/(m²·K)")
        self.assertAlmostEqual(
            self.projection["candidateWindow"]["UFactor"],
            round(u["value"] / 5.678263, 4),
        )
        self.assertEqual(
            self.projection["candidateWindow"]["SHGC"],
            shgc["value"],
        )
        self.assertEqual(
            self.observation["certification"]["subsidyEligibility"],
            "NOT_EVALUATED",
        )

    def test_exact_replacement(self):
        original = ET.parse(ORIGINAL).getroot()
        replacement = ET.parse(REPLACEMENT).getroot()

        label = self.projection["opening"]
        original_window = window(original, label)
        replacement_window = window(replacement, label)

        candidate = self.projection["candidateWindow"]

        for field in ("Area", "Azimuth"):
            self.assertEqual(
                original_window.findtext("{*}" + field),
                replacement_window.findtext("{*}" + field),
            )
            self.assertEqual(
                float(replacement_window.findtext("{*}" + field)),
                candidate[field],
            )

        self.assertEqual(
            original_window.find("{*}AttachedToWall").get("idref"),
            replacement_window.find("{*}AttachedToWall").get("idref"),
        )

        for field in ("UFactor", "SHGC"):
            original_window.find("{*}" + field).text = str(candidate[field])

        self.assertEqual(
            ET.tostring(original),
            ET.tostring(replacement),
        )

    def test_full_xsd(self):
        schema = etree.XMLSchema(etree.parse(str(XSD)))
        for path in (ORIGINAL, REPLACEMENT):
            with self.subTest(file=path.name):
                self.assertTrue(
                    schema.validate(etree.parse(str(path))),
                    str(schema.error_log),
                )

    def test_energyplus_schematron(self):
        validator = isoschematron.Schematron(
            etree.parse(str(SCH)),
            store_report=True,
        )
        ns = {"svrl": "http://purl.oclc.org/dsdl/svrl"}

        for path in (ORIGINAL, REPLACEMENT):
            with self.subTest(file=path.name):
                valid = validator.validate(etree.parse(str(path)))
                report = validator.validation_report
                self.assertIsNotNone(report)

                fired = report.xpath(
                    "count(//svrl:fired-rule)", namespaces=ns
                )
                errors = report.xpath(
                    "//svrl:failed-assert", namespaces=ns
                )
                self.assertGreater(fired, 0, "No rules activated")
                self.assertTrue(valid, f"{len(errors)} rule errors")
                self.assertEqual(len(errors), 0)


if __name__ == "__main__":
    unittest.main()
