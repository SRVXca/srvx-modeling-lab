from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from statistics import mean, median
from zipfile import ZipFile
from xml.etree import ElementTree as ET
from posixpath import normpath
import math
import re


XLSX = Path("neep_air_source_heat_pump_2026-10-07.xlsx")

MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG = "http://schemas.openxmlformats.org/package/2006/relationships"


ADDENDUM82 = {
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


def q(ns, tag):
    return f"{{{ns}}}{tag}"


def colnum(ref):
    letters = re.match(r"[A-Z]+", ref).group(0)
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n


def resolve_target(target):
    if target.startswith("/"):
        return target.lstrip("/")
    if target.startswith("xl/"):
        return normpath(target)
    return normpath("xl/" + target)


def number(v):
    if v in (None, ""):
        return None

    if isinstance(v, bool):
        return None

    try:
        x = float(v)
    except (TypeError, ValueError):
        return None

    if not math.isfinite(x):
        return None

    return x


def safe_ratio(a, b):
    a = number(a)
    b = number(b)

    if a is None or b is None or b == 0:
        return None

    return a / b


def eir(power, capacity):
    return safe_ratio(power, capacity)


def percentile(values, p):
    xs = sorted(values)

    if not xs:
        return None

    k = (len(xs) - 1) * p
    lo = math.floor(k)
    hi = math.ceil(k)

    if lo == hi:
        return xs[lo]

    return xs[lo] * (hi - k) + xs[hi] * (k - lo)


def read_hp_rows():
    with ZipFile(XLSX) as z:
        shared = []

        if "xl/sharedStrings.xml" in z.namelist():
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))

            for si in root.findall(q(MAIN, "si")):
                shared.append("".join(
                    t.text or ""
                    for t in si.iter(q(MAIN, "t"))
                ))

        def cell_value(cell):
            typ = cell.attrib.get("t")

            if typ == "inlineStr":
                node = cell.find(q(MAIN, "is"))
                if node is None:
                    return None

                return "".join(
                    t.text or ""
                    for t in node.iter(q(MAIN, "t"))
                )

            v = cell.find(q(MAIN, "v"))

            if v is None:
                return None

            raw = v.text

            if raw is None:
                return None

            if typ == "s":
                return shared[int(raw)]

            if typ == "b":
                return raw == "1"

            return raw

        wb = ET.fromstring(z.read("xl/workbook.xml"))
        sheets = wb.find(q(MAIN, "sheets"))

        relroot = ET.fromstring(
            z.read("xl/_rels/workbook.xml.rels")
        )

        rels = {
            x.attrib["Id"]: x.attrib["Target"]
            for x in relroot.findall(q(PKG, "Relationship"))
        }

        sheet = next(
            s for s in sheets
            if s.attrib["name"] == "HP Report"
        )

        target = resolve_target(
            rels[sheet.attrib[q(REL, "id")]]
        )

        headers = None
        rownum = 0

        with z.open(target) as fh:
            for _, row in ET.iterparse(fh, events=("end",)):
                if row.tag != q(MAIN, "row"):
                    continue

                rownum += 1

                cells = {}

                for cell in row.findall(q(MAIN, "c")):
                    cells[colnum(cell.attrib["r"])] = cell_value(cell)

                if rownum == 2:
                    width = max(cells)
                    headers = [
                        cells.get(i)
                        for i in range(1, width + 1)
                    ]

                elif rownum >= 3:
                    if headers is None:
                        raise RuntimeError("missing header")

                    yield {
                        header: cells.get(i)
                        for i, header in enumerate(headers, 1)
                    }

                row.clear()


def metrics(r):
    # Capacity
    q47min  = r["Min Capacity 47°F"]
    q47full = r["Rated Capacity 47°F⁺"]
    q47max  = r["Max Capacity 47°F"]

    q17min  = r["Min Capacity 17°F"]
    q17full = r["Rated Capacity 17°F⁺"]
    q17max  = r["Max Capacity 17°F"]

    q5min   = r["Min Capacity 5°F"]
    q5full  = r["Rated Capacity 5°F - Optional⁺"]
    q5max   = r["Max Capacity 5°F"]

    # Power
    p47min  = r["Input Power Min 47°F"]
    p47full = r["Input Power Rated 47°F"]
    p47max  = r["Input Power Max 47°F"]

    p17min  = r["Input Power Min 17°F"]
    p17full = r["Input Power Rated 17°F"]
    p17max  = r["Input Power Max 17°F"]

    p5min   = r["Input Power Min 5°F"]
    p5full  = r["Input Power Rated 5°F - Optional"]
    p5max   = r["Input Power Max 5°F"]

    e47min  = eir(p47min, q47min)
    e47full = eir(p47full, q47full)
    e47max  = eir(p47max, q47max)

    e17min  = eir(p17min, q17min)
    e17full = eir(p17full, q17full)
    e17max  = eir(p17max, q17max)

    e5min   = eir(p5min, q5min)
    e5full  = eir(p5full, q5full)
    e5max   = eir(p5max, q5max)

    return {
        "Qr47full": safe_ratio(q47full, q47max),
        "Qr47min":  safe_ratio(q47min, q47max),

        "Qr17full": safe_ratio(q17full, q17max),
        "Qr17min":  safe_ratio(q17min, q17max),

        "Qm5max":   safe_ratio(q5max, q17max),
        "Qr5full":  safe_ratio(q5full, q5max),
        "Qr5min":   safe_ratio(q5min, q5max),

        "EIRr47full": safe_ratio(e47full, e47max),
        "EIRr47min":  safe_ratio(e47min, e47max),

        "EIRm17full": safe_ratio(e17full, e47full),
        "EIRr17full": safe_ratio(e17full, e17max),
        "EIRr17min":  safe_ratio(e17min, e17max),

        "EIRm5max":   safe_ratio(e5max, e17max),
        "EIRr5full":  safe_ratio(e5full, e5max),
        "EIRr5min":   safe_ratio(e5min, e5max),
    }


def analyze(name, rows):
    values = defaultdict(list)

    count = 0

    for r in rows:
        count += 1

        for key, value in metrics(r).items():
            if value is not None:
                values[key].append(value)

    print()
    print("=" * 100)
    print(name)
    print("products:", count)
    print("=" * 100)

    print(
        f"{'metric':<14}"
        f"{'n':>10}"
        f"{'A82':>10}"
        f"{'mean':>12}"
        f"{'delta':>12}"
        f"{'median':>12}"
        f"{'p10':>12}"
        f"{'p90':>12}"
    )

    for key, target in ADDENDUM82.items():
        xs = values[key]

        if not xs:
            print(f"{key:<14}{0:>10}")
            continue

        avg = mean(xs)
        med = median(xs)

        print(
            f"{key:<14}"
            f"{len(xs):>10,d}"
            f"{target:>10.3f}"
            f"{avg:>12.6f}"
            f"{(avg-target):>+12.6f}"
            f"{med:>12.6f}"
            f"{percentile(xs, .10):>12.6f}"
            f"{percentile(xs, .90):>12.6f}"
        )


rows = list(read_hp_rows())

# Population 1:
# broad NEEP Live + Variable Capacity HP population.
broad = [
    r for r in rows
    if r["Status"] == "Live"
    and r["Variable Capacity?"] is True
]

# Population 2:
# scope-like approximation for Addendum 82.
#
# Current Addendum scope excludes multi-splits.
# We therefore exclude NEEP multizone ducting configurations.
# This is explicitly an approximation until RESNET's exact
# historical NEEP selection methodology is recovered.
scope_like = [
    r for r in broad
    if not str(r["Ducting Configuration"] or "").startswith("Multizone")
]

analyze(
    "NEEP 2026 — Live variable-capacity HPs",
    broad,
)

analyze(
    "NEEP 2026 — scope-like, excluding Multizone",
    scope_like,
)
