from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
from statistics import mean
from zipfile import ZipFile
from xml.etree import ElementTree as ET
from posixpath import normpath
import json
import math
import re


ROOT = Path(__file__).resolve().parents[2]

XLSX = (
    ROOT
    / "source-study"
    / "neep"
    / "neep_air_source_heat_pump_2026-10-07.xlsx"
)

OUT = Path(__file__).resolve().parent / "results.json"

MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG = "http://schemas.openxmlformats.org/package/2006/relationships"


A82 = {
    "Qr47full":   0.908,
    "Qr47min":    0.272,
    "Qr17full":   0.817,
    "Qr17min":    0.341,
    "Qm5max":     0.866,
    "Qr5full":    0.988,
    "Qr5min":     0.321,

    "EIRr47full": 0.939,
    "EIRr47min":  0.730,
    "EIRm17full": 1.351,
    "EIRr17full": 0.902,
    "EIRr17min":  0.798,
    "EIRm5max":   1.164,
    "EIRr5full":  1.000,
    "EIRr5min":   0.866,
}


@dataclass(frozen=True)
class PopulationSpec:
    name: str

    cutoff_date: str | None = None

    complete_metrics: bool = False

    singlezone_only: bool = False
    central_ducted_only: bool = False

    cold_climate: bool | None = None
    ahri_type: str | None = None

    dedupe: str = "none"


def q(ns: str, tag: str) -> str:
    return f"{{{ns}}}{tag}"


def colnum(ref: str) -> int:
    m = re.match(r"[A-Z]+", ref)

    if m is None:
        raise ValueError(ref)

    n = 0

    for ch in m.group(0):
        n = n * 26 + ord(ch) - 64

    return n


def resolve_target(target: str) -> str:
    if target.startswith("/"):
        return target.lstrip("/")

    if target.startswith("xl/"):
        return normpath(target)

    return normpath("xl/" + target)


def number(value):
    if value in (None, "") or isinstance(value, bool):
        return None

    try:
        x = float(value)
    except (TypeError, ValueError):
        return None

    return x if math.isfinite(x) else None


def ratio(a, b):
    a = number(a)
    b = number(b)

    if a is None or b is None or b == 0:
        return None

    return a / b


def eir(power, capacity):
    return ratio(power, capacity)


def source_date(value) -> date | None:
    if not value:
        return None

    s = str(value).strip()

    for fmt in ("%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass

    return None


def read_hp_rows() -> list[dict]:
    rows = []

    with ZipFile(XLSX) as z:
        shared = []

        if "xl/sharedStrings.xml" in z.namelist():
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))

            for si in root.findall(q(MAIN, "si")):
                shared.append(
                    "".join(
                        t.text or ""
                        for t in si.iter(q(MAIN, "t"))
                    )
                )

        def value(cell):
            typ = cell.attrib.get("t")

            if typ == "inlineStr":
                node = cell.find(q(MAIN, "is"))

                if node is None:
                    return None

                return "".join(
                    t.text or ""
                    for t in node.iter(q(MAIN, "t"))
                )

            node = cell.find(q(MAIN, "v"))

            if node is None or node.text is None:
                return None

            raw = node.text

            if typ == "s":
                return shared[int(raw)]

            if typ == "b":
                return raw == "1"

            return raw

        workbook = ET.fromstring(
            z.read("xl/workbook.xml")
        )

        sheets = workbook.find(q(MAIN, "sheets"))

        relationships = ET.fromstring(
            z.read("xl/_rels/workbook.xml.rels")
        )

        rels = {
            r.attrib["Id"]: r.attrib["Target"]
            for r in relationships.findall(
                q(PKG, "Relationship")
            )
        }

        sheet = next(
            s
            for s in sheets
            if s.attrib["name"] == "HP Report"
        )

        target = resolve_target(
            rels[sheet.attrib[q(REL, "id")]]
        )

        headers = None
        row_number = 0

        with z.open(target) as fh:
            for _, row in ET.iterparse(
                fh,
                events=("end",),
            ):
                if row.tag != q(MAIN, "row"):
                    continue

                row_number += 1

                cells = {}

                for cell in row.findall(q(MAIN, "c")):
                    cells[
                        colnum(cell.attrib["r"])
                    ] = value(cell)

                if row_number == 2:
                    headers = [
                        cells.get(i)
                        for i in range(
                            1,
                            max(cells) + 1,
                        )
                    ]

                elif row_number >= 3:
                    if headers is None:
                        raise RuntimeError(
                            "NEEP header missing"
                        )

                    record = {
                        header: cells.get(i)
                        for i, header
                        in enumerate(headers, 1)
                    }

                    rows.append(record)

                row.clear()

    return rows


def metrics(r: dict) -> dict[str, float | None]:
    q47min = r["Min Capacity 47°F"]
    q47full = r["Rated Capacity 47°F⁺"]
    q47max = r["Max Capacity 47°F"]

    q17min = r["Min Capacity 17°F"]
    q17full = r["Rated Capacity 17°F⁺"]
    q17max = r["Max Capacity 17°F"]

    q5min = r["Min Capacity 5°F"]
    q5full = r["Rated Capacity 5°F - Optional⁺"]
    q5max = r["Max Capacity 5°F"]

    p47min = r["Input Power Min 47°F"]
    p47full = r["Input Power Rated 47°F"]
    p47max = r["Input Power Max 47°F"]

    p17min = r["Input Power Min 17°F"]
    p17full = r["Input Power Rated 17°F"]
    p17max = r["Input Power Max 17°F"]

    p5min = r["Input Power Min 5°F"]
    p5full = r["Input Power Rated 5°F - Optional"]
    p5max = r["Input Power Max 5°F"]

    e47min = eir(p47min, q47min)
    e47full = eir(p47full, q47full)
    e47max = eir(p47max, q47max)

    e17min = eir(p17min, q17min)
    e17full = eir(p17full, q17full)
    e17max = eir(p17max, q17max)

    e5min = eir(p5min, q5min)
    e5full = eir(p5full, q5full)
    e5max = eir(p5max, q5max)

    return {
        "Qr47full": ratio(q47full, q47max),
        "Qr47min": ratio(q47min, q47max),

        "Qr17full": ratio(q17full, q17max),
        "Qr17min": ratio(q17min, q17max),

        "Qm5max": ratio(q5max, q17max),
        "Qr5full": ratio(q5full, q5max),
        "Qr5min": ratio(q5min, q5max),

        "EIRr47full": ratio(e47full, e47max),
        "EIRr47min": ratio(e47min, e47max),

        "EIRm17full": ratio(e17full, e47full),
        "EIRr17full": ratio(e17full, e17max),
        "EIRr17min": ratio(e17min, e17max),

        "EIRm5max": ratio(e5max, e17max),
        "EIRr5full": ratio(e5full, e5max),
        "EIRr5min": ratio(e5min, e5max),
    }


def base_population(rows: list[dict]) -> list[dict]:
    return [
        r
        for r in rows
        if r["Status"] == "Live"
        and r["Variable Capacity?"] is True
    ]


def matches(r: dict, spec: PopulationSpec) -> bool:
    if spec.cutoff_date is not None:
        d = source_date(r["Date Added to List"])

        if d is None:
            return False

        if d >= date.fromisoformat(spec.cutoff_date):
            return False

    ducting = str(
        r["Ducting Configuration"] or ""
    )

    if spec.singlezone_only:
        if not ducting.startswith("Singlezone"):
            return False

    if spec.central_ducted_only:
        if ducting != "Singlezone Ducted, Centrally Ducted":
            return False

    if spec.cold_climate is not None:
        if (
            r["ENERGY STAR Cold Climate Certified"]
            is not spec.cold_climate
        ):
            return False

    if spec.ahri_type is not None:
        if r["AHRI Type⁺"] != spec.ahri_type:
            return False

    if spec.complete_metrics:
        m = metrics(r)

        if any(v is None for v in m.values()):
            return False

    return True


def identity_key(
    r: dict,
    mode: str,
    row_index: int,
):
    if mode == "none":
        return ("row", row_index)

    if mode == "ahri":
        value = r["AHRI Certified Reference Number⁺"]

        if value:
            return ("ahri", str(value))

    elif mode == "outdoor":
        value = r["Outdoor Unit Model Number⁺"]

        if value:
            return (
                "outdoor",
                r["Brand Name"],
                str(value),
            )

    elif mode == "outdoor_indoor":
        outdoor = r["Outdoor Unit Model Number⁺"]
        indoor = r["Indoor Model Number(s)⁺"]

        if outdoor or indoor:
            return (
                "pair",
                r["Brand Name"],
                str(outdoor or ""),
                str(indoor or ""),
            )

    else:
        raise ValueError(
            f"unknown dedupe mode {mode!r}"
        )

    # Missing identity should never collapse unrelated rows.
    return ("row", row_index)


def dedupe(
    rows: list[dict],
    mode: str,
) -> list[dict]:
    if mode == "none":
        return rows

    seen = set()
    result = []

    for i, r in enumerate(rows):
        key = identity_key(r, mode, i)

        if key in seen:
            continue

        seen.add(key)
        result.append(r)

    return result


def evaluate(
    base: list[dict],
    spec: PopulationSpec,
) -> dict:
    rows = [
        r
        for r in base
        if matches(r, spec)
    ]

    before_dedupe = len(rows)

    rows = dedupe(
        rows,
        spec.dedupe,
    )

    values = defaultdict(list)

    for r in rows:
        for key, value in metrics(r).items():
            if value is not None:
                values[key].append(value)

    metric_results = {}
    relative_errors = []

    for key, target in A82.items():
        xs = values[key]

        if not xs:
            metric_results[key] = {
                "n": 0,
                "target": target,
                "mean": None,
                "delta": None,
                "relativeError": None,
            }
            continue

        avg = mean(xs)
        delta = avg - target
        error = abs(delta) / abs(target)

        relative_errors.append(error)

        metric_results[key] = {
            "n": len(xs),
            "target": target,
            "mean": avg,
            "delta": delta,
            "relativeError": error,
        }

    score = (
        mean(relative_errors)
        if relative_errors
        else None
    )

    return {
        "population": asdict(spec),
        "rowsBeforeDedupe": before_dedupe,
        "rows": len(rows),
        "score": score,
        "metrics": metric_results,
    }




def main():
    rows = read_hp_rows()
    base = base_population(rows)

    print("NEEP HP rows:", len(rows))
    print("Baseline Live variable-capacity:", len(base))
    print()


    EXPERIMENTS = [
        # Baseline
        PopulationSpec(
            name="baseline",
        ),

        # One dimension at a time
        PopulationSpec(
            name="pre-PDS01",
            cutoff_date="2024-11-22",
        ),

        PopulationSpec(
            name="complete-metrics",
            complete_metrics=True,
        ),

        PopulationSpec(
            name="singlezone",
            singlezone_only=True,
        ),

        PopulationSpec(
            name="central-ducted",
            central_ducted_only=True,
        ),

        PopulationSpec(
            name="cold-climate",
            cold_climate=True,
        ),

        PopulationSpec(
            name="non-cold-climate",
            cold_climate=False,
        ),

        PopulationSpec(
            name="dedupe-AHRI",
            dedupe="ahri",
        ),

        PopulationSpec(
            name="dedupe-outdoor",
            dedupe="outdoor",
        ),

        PopulationSpec(
            name="dedupe-outdoor-indoor",
            dedupe="outdoor_indoor",
        ),

        # Controlled combinations
        PopulationSpec(
            name="pre-PDS01-complete",
            cutoff_date="2024-11-22",
            complete_metrics=True,
        ),

        PopulationSpec(
            name="pre-PDS01-dedupe-outdoor",
            cutoff_date="2024-11-22",
            dedupe="outdoor",
        ),

        PopulationSpec(
            name="pre-PDS01-singlezone",
            cutoff_date="2024-11-22",
            singlezone_only=True,
        ),

        PopulationSpec(
            name="pre-PDS01-central-ducted",
            cutoff_date="2024-11-22",
            central_ducted_only=True,
        ),

        PopulationSpec(
            name="pre-PDS01-central-dedupe-outdoor",
            cutoff_date="2024-11-22",
            central_ducted_only=True,
            dedupe="outdoor",
        ),
    ]


    # Add one-factor AHRI-type populations automatically.
    ahri_types = sorted({
        str(r["AHRI Type⁺"])
        for r in base
        if r["AHRI Type⁺"]
    })

    for value in ahri_types:
        EXPERIMENTS.append(
            PopulationSpec(
                name=f"AHRI-{value}",
                ahri_type=value,
            )
        )


    results = [
        evaluate(base, spec)
        for spec in EXPERIMENTS
    ]

    results.sort(
        key=lambda r: (
            float("inf")
            if r["score"] is None
            else r["score"]
        )
    )

    OUT.write_text(
        json.dumps(
            {
                "sourceRows": len(rows),
                "baselineRows": len(base),
                "scoreDefinition": (
                    "mean absolute relative difference "
                    "from Addendum 82 across available metrics"
                ),
                "results": results,
            },
            indent=2,
        )
        + "\n"
    )


    print(
        f"{'population':<40}"
        f"{'rows':>10}"
        f"{'pre-dedupe':>14}"
        f"{'score':>12}"
    )

    print("-" * 76)

    for result in results:
        score = result["score"]

        print(
            f"{result['population']['name']:<40}"
            f"{result['rows']:>10,d}"
            f"{result['rowsBeforeDedupe']:>14,d}"
            f"{score:>12.4%}"
        )

    print()
    print("wrote:", OUT)


if __name__ == "__main__":
    main()
