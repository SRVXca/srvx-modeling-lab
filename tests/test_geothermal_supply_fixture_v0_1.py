import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SOURCE = (
    ROOT
    / "evidence-core/geothermal/v0.1/source-record"
    / "energy-star-geothermal-source-records.v0.1.json"
)

OBSERVATIONS = (
    ROOT
    / "evidence-core/geothermal/v0.1/observation"
    / "ground-source-performance.v0.1.json"
)

MARKET = (
    ROOT
    / "fixtures/supply/geothermal-v0.1"
    / "market-products.v0.1.json"
)

REGISTRY = (
    ROOT
    / "registry/source-datasets.v0.1.json"
)


class GeothermalSupplyFixtureTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.source = json.loads(SOURCE.read_text())
        cls.observations = json.loads(
            OBSERVATIONS.read_text()
        )
        cls.market = json.loads(MARKET.read_text())
        cls.registry = json.loads(REGISTRY.read_text())

    def test_source_records_are_exact_and_registered(self):
        records = self.source["records"]

        self.assertEqual(len(records), 4)

        registry_ids = {
            source["id"]
            for source
            in self.registry["sourceDatasets"]
        }

        self.assertEqual(
            self.source["datasetId"],
            "EPA_ENERGY_STAR",
        )

        self.assertIn(
            self.source["datasetId"],
            registry_ids,
        )

        self.assertEqual(
            sorted(r["pd_id"] for r in records),
            [
                "4586690",
                "4586700",
                "4586731",
                "4710776",
            ],
        )

    def test_observation_count_and_contract(self):
        observations = self.observations["observations"]

        self.assertEqual(len(observations), 12)

        for observation in observations:
            self.assertEqual(
                observation["family"],
                "geothermal_water_source_heat_pump",
            )

            self.assertEqual(
                observation["contract"],
                "GroundSourcePerformance",
            )

            self.assertIn(
                observation["metric"],
                {
                    "cop",
                    "eer",
                    "heatingCapacity",
                },
            )

            self.assertIn(
                observation["evidenceKind"],
                {
                    "CERTIFICATION_REPORTED",
                    "MANUFACTURER_REPORTED",
                },
            )

    def test_york_occurrences_remain_distinct(self):
        york = next(
            product
            for product in self.market["products"]
            if product["model"] == "Y5SZ036BD1"
        )

        occurrences = (
            york["energyStarCertificationOccurrences"]
        )

        self.assertEqual(len(occurrences), 3)

        self.assertEqual(
            sorted(
                occurrence["loopType"]
                for occurrence in occurrences
            ),
            [
                "CLOSED_LOOP",
                "CLOSED_LOOP",
                "OPEN_LOOP",
            ],
        )

        self.assertIn(
            "WaterFurnace International, Incorporated",
            york["energyStarPartnerNames"],
        )

        # Source partner evidence must not silently replace
        # the marketed product brand.
        self.assertEqual(york["brand"], "York")

    def test_hydro_solar_variants_remain_conditional(self):
        hydro = next(
            product
            for product in self.market["products"]
            if product["model"] == "GEO040V1LM"
        )

        variants = hydro[
            "manufacturerPerformanceVariants"
        ]

        self.assertEqual(len(variants), 2)

        by_material = {
            v["exchangerMaterial"]: v
            for v in variants
        }

        self.assertEqual(
            by_material["TITANIUM"]["heatingCapacityBtuH"],
            40600,
        )

        self.assertEqual(
            by_material["COPPER"]["heatingCapacityBtuH"],
            41456,
        )

        self.assertNotEqual(
            by_material["TITANIUM"]["conditions"][
                "loadEnteringTemperatureC"
            ],
            by_material["COPPER"]["conditions"][
                "loadEnteringTemperatureC"
            ],
        )

    def test_no_ahri_reference_is_invented(self):
        for product in self.market["products"]:
            self.assertIsNone(
                product["ahri"]["reference"]
            )

            self.assertEqual(
                product["ahri"]["verificationStatus"],
                "UNVERIFIED",
            )

    def test_commercial_unknowns_remain_unknown(self):
        for product in self.market["products"]:
            self.assertIsNone(
                product["commercial"]["price"]
            )

            self.assertIsNone(
                product["commercial"][
                    "currentAvailability"
                ]
            )


if __name__ == "__main__":
    unittest.main()
