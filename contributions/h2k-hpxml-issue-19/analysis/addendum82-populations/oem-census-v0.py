from collections import defaultdict, Counter
from itertools import combinations

from run import (
    base_population,
    number,
    read_hp_rows,
)


def txt(v):
    return str(v or "").strip()


def norm(v):
    return txt(v).casefold()


def cap(r):
    return number(r.get("Rated Capacity 47°F⁺"))


# ------------------------------------------------------------
# Performance field vocabulary
# ------------------------------------------------------------

rows = list(base_population(read_hp_rows()))


def performance_field(name):
    s = name.casefold()

    wanted = (
        "capacity",
        "power",
        "cop",
        "seer2",
        "hspf2",
        "eer2",
    )

    forbidden = (
        "model",
        "brand",
        "manufacturer",
        "ahri",
        "series",
        "date",
    )

    return (
        any(x in s for x in wanted)
        and not any(x in s for x in forbidden)
    )


all_fields = sorted({
    field
    for r in rows
    for field in r.keys()
})


RAW_FIELDS = [
    field
    for field in all_fields
    if performance_field(field)
    and sum(
        number(r.get(field)) is not None
        for r in rows
    ) >= 100
]


print("live variable-capacity rows:", len(rows))
print("performance fields:", len(RAW_FIELDS))


# ------------------------------------------------------------
# Commercial family node
#
# Prefer Brand + Series.
# If series is missing, fall back to Brand + Outdoor Model
# so we don't merge a whole brand into one node.
# ------------------------------------------------------------

def node_key(r):
    brand = txt(r.get("Brand Name"))
    series = txt(r.get("Series Name"))
    model = txt(r.get("Outdoor Unit Model Number⁺"))

    if series:
        return (
            norm(brand),
            norm(series),
        )

    return (
        norm(brand),
        f"model:{norm(model)}",
    )


def node_label(r):
    brand = txt(r.get("Brand Name"))
    series = txt(r.get("Series Name"))
    model = txt(r.get("Outdoor Unit Model Number⁺"))

    if series:
        return f"{brand} :: {series}"

    return f"{brand} :: [model] {model}"


# ------------------------------------------------------------
# Exact raw-performance fingerprint
#
# Include architecture/context so identical-looking numbers
# from structurally different equipment don't merge blindly.
# ------------------------------------------------------------

def fingerprint(r):
    values = []

    for field in RAW_FIELDS:
        value = number(r.get(field))

        if value is not None:
            values.append(
                (
                    field,
                    float(value),
                )
            )

    # Require meaningful evidence density.
    if len(values) < 20:
        return None

    return (
        txt(r.get("Ducting Configuration")),
        bool(
            r.get(
                "ENERGY STAR Cold Climate Certified"
            )
        ),
        tuple(values),
    )


# ------------------------------------------------------------
# Build fingerprint → commercial families
# ------------------------------------------------------------

by_fp = defaultdict(dict)
node_labels = {}
node_owners = defaultdict(set)

for r in rows:
    fp = fingerprint(r)

    if fp is None:
        continue

    node = node_key(r)

    if not node[0]:
        continue

    node_labels[node] = node_label(r)

    owner = txt(r.get("Brand Owner"))

    if owner:
        node_owners[node].add(owner)

    # One representative per commercial family per fingerprint.
    by_fp[fp][node] = r


shared_fps = {
    fp: members
    for fp, members in by_fp.items()
    if len(members) >= 2
}


print("exact fingerprints:", len(by_fp))
print(
    "cross-family fingerprints:",
    len(shared_fps),
)


# ------------------------------------------------------------
# Pair evidence:
# two Brand+Series families are linked only if they repeatedly
# share exact fingerprints at multiple capacities.
# ------------------------------------------------------------

pair_fps = defaultdict(set)
pair_caps = defaultdict(set)

for fp, members in shared_fps.items():

    nodes = sorted(members)

    capacities = {
        round(cap(r) / 1000)
        for r in members.values()
        if cap(r) is not None
    }

    for a, b in combinations(nodes, 2):
        pair = (a, b)

        pair_fps[pair].add(fp)
        pair_caps[pair].update(capacities)


# Conservative edge:
# >=2 exact fingerprints
# AND >=2 nominal capacity points.

edges = {}

for pair, fps in pair_fps.items():

    caps = pair_caps[pair]

    if (
        len(fps) >= 2
        and len(caps) >= 2
    ):
        edges[pair] = {
            "fingerprints": len(fps),
            "capacities": caps,
        }


print("multi-capacity lineage edges:", len(edges))


# ------------------------------------------------------------
# Connected components
# ------------------------------------------------------------

adj = defaultdict(set)

for a, b in edges:
    adj[a].add(b)
    adj[b].add(a)


visited = set()
components = []

for start in adj:

    if start in visited:
        continue

    stack = [start]
    members = set()

    while stack:
        node = stack.pop()

        if node in visited:
            continue

        visited.add(node)
        members.add(node)

        stack.extend(
            adj[node] - visited
        )

    components.append(members)


def component_stats(component):

    brands = {
        node[0]
        for node in component
    }

    owners = set()

    for node in component:
        owners.update(
            node_owners[node]
        )

    internal_edges = []

    for (a, b), evidence in edges.items():

        if (
            a in component
            and b in component
        ):
            internal_edges.append(
                (
                    a,
                    b,
                    evidence,
                )
            )

    capacities = set()

    for _, _, e in internal_edges:
        capacities.update(
            e["capacities"]
        )

    return {
        "members": component,
        "brands": brands,
        "owners": owners,
        "edges": internal_edges,
        "capacities": capacities,
    }


stats = [
    component_stats(c)
    for c in components
]


stats.sort(
    key=lambda x: (
        len(x["brands"]),
        len(x["members"]),
        len(x["edges"]),
    ),
    reverse=True,
)


print()
print("=" * 110)
print("LARGEST MULTI-CAPACITY PLATFORM-DATA FAMILIES")
print("=" * 110)

for i, c in enumerate(
    stats[:30],
    1,
):

    print()
    print(
        f"FAMILY {i:02d} "
        f"brands={len(c['brands'])} "
        f"series={len(c['members'])} "
        f"edges={len(c['edges'])} "
        f"capacities={sorted(c['capacities'])}"
    )

    if c["owners"]:
        print(
            "  Brand Owners:",
            " | ".join(
                sorted(c["owners"])
            )
        )

    print("  Members:")

    for node in sorted(
        c["members"],
        key=lambda n: node_labels[n].casefold(),
    ):
        print(
            "   ",
            node_labels[node],
        )

    strongest = sorted(
        c["edges"],
        key=lambda x: (
            len(x[2]["capacities"]),
            x[2]["fingerprints"],
        ),
        reverse=True,
    )[:10]

    print("  Strongest links:")

    for a, b, e in strongest:
        print(
            "    "
            f"{node_labels[a]}"
            "  <->  "
            f"{node_labels[b]}"
            f" | fingerprints={e['fingerprints']}"
            f" capacities={sorted(e['capacities'])}"
        )


# ------------------------------------------------------------
# Global summary
# ------------------------------------------------------------

all_linked_nodes = set()

for c in stats:
    all_linked_nodes.update(
        c["members"]
    )


all_nodes = {
    node_key(r)
    for r in rows
    if node_key(r)[0]
}


print()
print("=" * 110)
print("CENSUS SUMMARY")
print("=" * 110)

print(
    "commercial Brand+Series/model families:",
    len(all_nodes),
)

print(
    "families participating in repeated "
    "multi-capacity exact lineage:",
    len(all_linked_nodes),
)

print(
    "candidate platform-data components:",
    len(stats),
)

print(
    "largest component brands:",
    (
        len(stats[0]["brands"])
        if stats
        else 0
    ),
)
