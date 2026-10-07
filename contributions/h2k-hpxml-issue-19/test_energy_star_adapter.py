from energy_star_adapter import (
    from_energy_star_ashp_record,
)


samsung = {
    "pd_id": "2469692",
    "ahri_reference_number": "210448841",
    "model_number": "AR12CSFCMWKX",
    "heating_capacity_at_47_f_btu_h": "12000",
    "heating_capacity_at_17_f_btu_h": "11000",
    "heating_capacity_at_5_f_btu_h": "9900",
}


performance = from_energy_star_ashp_record(
    samsung
)

assert (
    performance.heating_capacity_17f_btu_h
    == 11000
)

assert (
    performance.source_ref
    == "ENERGY_STAR:AHRI:210448841"
)


missing = from_energy_star_ashp_record(
    {
        "ahri_reference_number": "123",
        "heating_capacity_at_17_f_btu_h": None,
    }
)

assert (
    missing.heating_capacity_17f_btu_h
    is None
)


print("ENERGY STAR adapter OK")
print(performance)
