from neep_hp_xlsx_adapter import (
    iter_neep_hp_source_rows,
)

rows = iter_neep_hp_source_rows()

first = next(rows)

assert first.source_row == 3

r = first.record

assert r["status"] == "Live"
assert r["brand_name"] == "TRANE"
assert r["ahri_certified_reference_number"] == "216765123"

assert r["rated_capacity_47_f"] == "51000"
assert r["rated_capacity_17_f"] == "34000"
assert r["rated_capacity_5_f_optional"] == "38500"

assert (
    r["capacity_maintenance_rated_17_f_rated_47_f"]
    == "66"
)

assert r["energy_star_certified"] is False
assert r["energy_star_cold_climate_certified"] is True
assert r["variable_capacity"] is True

count = 1

for _ in rows:
    count += 1

assert count == 155313, count

print("NEEP HP SourceRecord adapter OK")
print("records:", count)
print("first source row:", first.source_row)
print(
    "first AHRI:",
    r["ahri_certified_reference_number"],
)
print(
    "Q47:",
    r["rated_capacity_47_f"],
)
print(
    "Q17:",
    r["rated_capacity_17_f"],
)
print(
    "Q5:",
    r["rated_capacity_5_f_optional"],
)
