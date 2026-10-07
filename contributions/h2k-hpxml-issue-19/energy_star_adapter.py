from typing import Any, Mapping

from low_temp_performance_adapter import (
    HeatPumpLowTempPerformance,
)


def _positive_float(
    value: object,
    field: str,
) -> float | None:
    if value is None or value == "":
        return None

    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Invalid ENERGY STAR {field}: {value!r}"
        ) from exc

    if number <= 0:
        raise ValueError(
            f"Invalid ENERGY STAR {field}: {value!r}"
        )

    return number


def from_energy_star_ashp_record(
    record: Mapping[str, Any],
) -> HeatPumpLowTempPerformance:
    capacity_17f = _positive_float(
        record.get(
            "heating_capacity_at_17_f_btu_h"
        ),
        "heating_capacity_at_17_f_btu_h",
    )

    ahri = record.get(
        "ahri_reference_number"
    )

    source_ref = (
        f"ENERGY_STAR:AHRI:{ahri}"
        if ahri not in (None, "")
        else None
    )

    return HeatPumpLowTempPerformance(
        heating_capacity_17f_btu_h=capacity_17f,
        source_ref=source_ref,
    )
