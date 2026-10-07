from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class HeatPumpLowTempPerformance:
    """
    Small consumer contract for externally observed
    low-temperature heat-pump performance.

    This is intentionally independent of ENERGY STAR,
    SRVX Supply, H2K, and any other source ontology.
    """
    heating_capacity_17f_btu_h: float | None
    source_ref: str | None = None


def hpxml_low_temp_fields(
    performance: HeatPumpLowTempPerformance,
) -> dict[str, float]:
    capacity = performance.heating_capacity_17f_btu_h

    if capacity is None:
        return {}

    if capacity <= 0:
        raise ValueError(
            "17F heating capacity must be positive"
        )

    return {
        "HeatingCapacity17F": capacity,
    }


def apply_low_temp_performance(
    heat_pump: Mapping[str, Any],
    performance: HeatPumpLowTempPerformance | None,
) -> dict[str, Any]:
    """
    Enrich an already-built HPXML heat-pump projection.

    If no external performance is available, preserve
    the converter's existing fallback unchanged.

    If direct 17F capacity is available, prefer that
    source fact over the fallback retention/fraction.
    """
    result = deepcopy(dict(heat_pump))

    if performance is None:
        return result

    fields = hpxml_low_temp_fields(performance)

    if not fields:
        return result

    result.update(fields)

    extension = result.get("extension")

    if isinstance(extension, dict):
        extension.pop(
            "HeatingCapacityFraction17F",
            None,
        )
        extension.pop(
            "HeatingCapacityRetention",
            None,
        )

        if not extension:
            result.pop("extension")

    return result
