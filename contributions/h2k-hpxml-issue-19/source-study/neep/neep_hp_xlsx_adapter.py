from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from posixpath import normpath
import re
from typing import Iterator, cast
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from neep_hp_source_record import (
    NeepHpSourceRecord,
    NeepHpSourceValue,
)

MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG = "http://schemas.openxmlformats.org/package/2006/relationships"

HERE = Path(__file__).resolve().parent

DEFAULT_SNAPSHOT = (
    HERE / "neep_air_source_heat_pump_2026-10-07.xlsx"
)

FIELD_CONTRACT = HERE / "hp-source-fields.json"

SHEET_NAME = "HP Report"
NOTICE_ROW = 1
HEADER_ROW = 2
FIRST_DATA_ROW = 3


def q(ns: str, tag: str) -> str:
    return f"{{{ns}}}{tag}"


def column_number(ref: str) -> int:
    match = re.match(r"[A-Z]+", ref)
    if match is None:
        raise ValueError(f"invalid XLSX cell reference: {ref!r}")

    n = 0
    for ch in match.group(0):
        n = n * 26 + ord(ch) - ord("A") + 1

    return n


def resolve_target(target: str) -> str:
    if target.startswith("/"):
        return target.lstrip("/")

    if target.startswith("xl/"):
        return normpath(target)

    return normpath("xl/" + target)


@dataclass(frozen=True)
class NeepHpSourceRow:
    source_row: int
    record: NeepHpSourceRecord


def _load_contract() -> tuple[list[str], list[str]]:
    data = json.loads(FIELD_CONTRACT.read_text())

    if data["fieldCount"] != 87:
        raise ValueError(
            f"expected 87 NEEP HP fields, "
            f"got {data['fieldCount']}"
        )

    fields = data["fields"]

    headers = [
        field["sourceHeader"]
        for field in fields
    ]

    keys = [
        field["sourceKey"]
        for field in fields
    ]

    if len(set(headers)) != len(headers):
        raise ValueError("duplicate NEEP HP source headers")

    if len(set(keys)) != len(keys):
        raise ValueError("duplicate NEEP HP source keys")

    return headers, keys


def iter_neep_hp_source_rows(
    snapshot: Path = DEFAULT_SNAPSHOT,
) -> Iterator[NeepHpSourceRow]:
    """
    Stream the NEEP HP Report into NeepHpSourceRecord objects.

    Adapter-layer behavior only:
    - asserts the exact 87-column source header;
    - maps source columns to mechanical code-safe keys;
    - preserves XLSX scalar representation;
    - empty cells become None.

    No semantic normalization is performed.
    """

    expected_headers, source_keys = _load_contract()

    with ZipFile(snapshot) as z:
        shared: list[str] = []

        if "xl/sharedStrings.xml" in z.namelist():
            root = ET.fromstring(
                z.read("xl/sharedStrings.xml")
            )

            for si in root.findall(q(MAIN, "si")):
                shared.append(
                    "".join(
                        t.text or ""
                        for t in si.iter(q(MAIN, "t"))
                    )
                )

        def cell_value(
            cell: ET.Element,
        ) -> NeepHpSourceValue:
            cell_type = cell.attrib.get("t")

            if cell_type == "inlineStr":
                node = cell.find(q(MAIN, "is"))

                if node is None:
                    return None

                return "".join(
                    t.text or ""
                    for t in node.iter(q(MAIN, "t"))
                )

            value = cell.find(q(MAIN, "v"))

            if value is None:
                return None

            raw = value.text

            if raw is None:
                return None

            if cell_type == "s":
                return shared[int(raw)]

            if cell_type == "b":
                return raw == "1"

            # Deliberately preserve numeric/date source cells
            # as their XLSX textual scalar representation.
            return raw

        workbook = ET.fromstring(
            z.read("xl/workbook.xml")
        )

        sheets = workbook.find(q(MAIN, "sheets"))

        if sheets is None:
            raise ValueError("XLSX workbook has no sheets")

        relations_root = ET.fromstring(
            z.read("xl/_rels/workbook.xml.rels")
        )

        relations = {
            relation.attrib["Id"]:
                relation.attrib["Target"]
            for relation in relations_root.findall(
                q(PKG, "Relationship")
            )
        }

        sheet = next(
            (
                item
                for item in sheets
                if item.attrib["name"] == SHEET_NAME
            ),
            None,
        )

        if sheet is None:
            raise ValueError(
                f"missing XLSX sheet {SHEET_NAME!r}"
            )

        relationship_id = sheet.attrib[q(REL, "id")]

        target = resolve_target(
            relations[relationship_id]
        )

        header_checked = False

        with z.open(target) as fh:
            for _, row in ET.iterparse(
                fh,
                events=("end",),
            ):
                if row.tag != q(MAIN, "row"):
                    continue

                source_row = int(
                    row.attrib.get("r", "0")
                )

                cells: dict[int, NeepHpSourceValue] = {}

                for cell in row.findall(q(MAIN, "c")):
                    ref = cell.attrib.get("r")

                    if ref is None:
                        raise ValueError(
                            "XLSX cell without reference"
                        )

                    cells[column_number(ref)] = (
                        cell_value(cell)
                    )

                if source_row == HEADER_ROW:
                    actual_headers = [
                        cells.get(column)
                        for column in range(
                            1,
                            len(expected_headers) + 1,
                        )
                    ]

                    if actual_headers != expected_headers:
                        raise ValueError(
                            "NEEP HP source header drift detected"
                        )

                    header_checked = True

                elif source_row >= FIRST_DATA_ROW:
                    if not header_checked:
                        raise ValueError(
                            "data encountered before validated "
                            "NEEP HP header"
                        )

                    record = {
                        key: cells.get(column)
                        for column, key in enumerate(
                            source_keys,
                            start=1,
                        )
                    }

                    yield NeepHpSourceRow(
                        source_row=source_row,
                        record=cast(
                            NeepHpSourceRecord,
                            record,
                        ),
                    )

                row.clear()

        if not header_checked:
            raise ValueError(
                "NEEP HP header row was not found"
            )
