from energy_star_adapter import (
    from_energy_star_ashp_record,
)
from low_temp_performance_adapter import (
    apply_low_temp_performance,
)


energy_star_record = {
    "pd_id": "2469692",
    "ahri_reference_number": "210448841",
    "model_number": "AR12CSFCMWKX",
    "heating_capacity_at_47_f_btu_h": "12000",
    "heating_capacity_at_17_f_btu_h": "11000",
    "heating_capacity_at_5_f_btu_h": "9900",
}


hpxml_heat_pump = {
    "HeatPumpType": "air-to-air",
    "HeatingCapacity": 12000,
    "extension": {
        "HeatingCapacityFraction17F": {
            "Fraction": 0.563635566,
        }
    },
}


performance = from_energy_star_ashp_record(
    energy_star_record
)

result = apply_low_temp_performance(
    hpxml_heat_pump,
    performance,
)


assert result["HeatingCapacity17F"] == 11000.0

assert (
    "HeatingCapacityFraction17F"
    not in result.get("extension", {})
)

assert (
    hpxml_heat_pump["extension"]
    ["HeatingCapacityFraction17F"]
    ["Fraction"]
    == 0.563635566
)


print("ENERGY STAR -> HPXML adapter chain OK")
print(result)
