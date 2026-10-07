from low_temp_performance_adapter import (
    HeatPumpLowTempPerformance,
    apply_low_temp_performance,
)


fallback = {
    "HeatPumpType": "air-to-air",
    "HeatingCapacity": 12000,
    "extension": {
        "HeatingCapacityFraction17F": {
            "Fraction": 0.563635566,
        },
        "HeatingAutosizingFactor": 1,
    },
}


# No external evidence: existing behavior survives.
unchanged = apply_low_temp_performance(
    fallback,
    None,
)

assert unchanged == fallback


# ENERGY STAR Samsung example from our issue-19 study.
performance = HeatPumpLowTempPerformance(
    heating_capacity_17f_btu_h=11000,
    source_ref="ENERGY_STAR:AHRI:210448841",
)

adapted = apply_low_temp_performance(
    fallback,
    performance,
)

assert adapted["HeatingCapacity17F"] == 11000

assert (
    "HeatingCapacityFraction17F"
    not in adapted["extension"]
)

assert (
    adapted["extension"]["HeatingAutosizingFactor"]
    == 1
)

# Adapter must not mutate the converter's original object.
assert (
    fallback["extension"]
    ["HeatingCapacityFraction17F"]
    ["Fraction"]
    == 0.563635566
)


try:
    apply_low_temp_performance(
        fallback,
        HeatPumpLowTempPerformance(
            heating_capacity_17f_btu_h=-1,
        ),
    )
except ValueError:
    pass
else:
    raise AssertionError(
        "Negative capacity should fail"
    )


print("low-temp performance adapter OK")
print(adapted)
