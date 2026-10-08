from __future__ import annotations

from typing import TypedDict

NeepHpSourceValue = str | bool | None


class NeepHpSourceRecord(TypedDict):
    date_added_to_list: NeepHpSourceValue
    status: NeepHpSourceValue
    brand_owner: NeepHpSourceValue
    brand_name: NeepHpSourceValue
    series_name: NeepHpSourceValue
    ducting_configuration: NeepHpSourceValue
    ahri_certified_reference_number: NeepHpSourceValue
    old_ahri_certified_reference_number: NeepHpSourceValue
    ahri_type: NeepHpSourceValue
    outdoor_unit_model_number: NeepHpSourceValue
    indoor_type: NeepHpSourceValue
    indoor_model_number_s: NeepHpSourceValue
    furnace_model_number_if_applicable: NeepHpSourceValue
    eer: NeepHpSourceValue
    seer: NeepHpSourceValue
    hspf_region_iv: NeepHpSourceValue
    eer2: NeepHpSourceValue
    seer2: NeepHpSourceValue
    hspf2_region_iv: NeepHpSourceValue
    hspf2_region_v: NeepHpSourceValue
    energy_star_certified: NeepHpSourceValue
    energy_star_cold_climate_certified: NeepHpSourceValue
    eligible_for_federal_tax_credit_north: NeepHpSourceValue
    eligible_for_federal_tax_credit_south: NeepHpSourceValue
    cee_tier_1_path_a_2025: NeepHpSourceValue
    cee_tier_1_path_b_2025: NeepHpSourceValue
    capacity_maintenance_rated_17_f_rated_47_f: NeepHpSourceValue
    capacity_maintenance_rated_5_f_rated_47_f: NeepHpSourceValue
    capacity_maintenance_max_5_f_rated_47_f: NeepHpSourceValue
    variable_capacity: NeepHpSourceValue
    pan_heater_integrated_or_accessory_provide_model: NeepHpSourceValue
    input_power_w: NeepHpSourceValue
    what_determines_when_heater_operates: NeepHpSourceValue
    integration_describe_any_capabilities_this_ashp_system_or_its_controller_s_have_related_to_integrating_other_heating_systems_third_party_thermostats_including_works_with_etc: NeepHpSourceValue
    connectivity_describe_any_capabilities_this_ashp_system_or_its_controller_s_have_related_to_communication_with_the_consumer_or_utility_e_g_meets_energy_star_connected_criteria_system_controller_have_an_interface_that_allows_for_remote_communication_with_the_consumer_or_utility_wi_fi_connected_etc: NeepHpSourceValue
    operational_diagnostics_describe_any_capabilities_of_this_ashp_system_to_self_report_or_self_diagnose_its_operation_or_the_quality_of_its_installation_including_whether_the_system_meets_any_all_of_energy_star_s_installation_capabilities_criteria: NeepHpSourceValue
    refrigerant: NeepHpSourceValue
    sold_in: NeepHpSourceValue
    min_capacity_95_f: NeepHpSourceValue
    input_power_min_95_f: NeepHpSourceValue
    cop_min_95_f: NeepHpSourceValue
    rated_capacity_95_f: NeepHpSourceValue
    input_power_rated_95_f: NeepHpSourceValue
    cop_rated_95_f: NeepHpSourceValue
    max_capacity_95_f: NeepHpSourceValue
    input_power_max_95_f: NeepHpSourceValue
    cop_max_95_f: NeepHpSourceValue
    min_capacity_82_f: NeepHpSourceValue
    input_power_min_82_f: NeepHpSourceValue
    cop_min_82_f: NeepHpSourceValue
    max_capacity_82_f: NeepHpSourceValue
    input_power_max_82_f: NeepHpSourceValue
    cop_max_82_f: NeepHpSourceValue
    min_capacity_47_f: NeepHpSourceValue
    input_power_min_47_f: NeepHpSourceValue
    cop_min_47_f: NeepHpSourceValue
    rated_capacity_47_f: NeepHpSourceValue
    input_power_rated_47_f: NeepHpSourceValue
    cop_rated_47_f: NeepHpSourceValue
    max_capacity_47_f: NeepHpSourceValue
    input_power_max_47_f: NeepHpSourceValue
    cop_max_47_f: NeepHpSourceValue
    min_capacity_17_f: NeepHpSourceValue
    input_power_min_17_f: NeepHpSourceValue
    cop_min_17_f: NeepHpSourceValue
    rated_capacity_17_f: NeepHpSourceValue
    input_power_rated_17_f: NeepHpSourceValue
    cop_rated_17_f: NeepHpSourceValue
    max_capacity_17_f: NeepHpSourceValue
    input_power_max_17_f: NeepHpSourceValue
    cop_max_17_f: NeepHpSourceValue
    min_capacity_5_f: NeepHpSourceValue
    input_power_min_5_f: NeepHpSourceValue
    cop_min_5_f: NeepHpSourceValue
    rated_capacity_5_f_optional: NeepHpSourceValue
    input_power_rated_5_f_optional: NeepHpSourceValue
    cop_rated_5_f_optional: NeepHpSourceValue
    max_capacity_5_f: NeepHpSourceValue
    input_power_max_5_f: NeepHpSourceValue
    cop_max_5_f: NeepHpSourceValue
    lowest_cataloged_temperature_outdoor_dry_bulb_f: NeepHpSourceValue
    min_capacity_lct_f: NeepHpSourceValue
    input_power_min_lct_f: NeepHpSourceValue
    cop_min_lct_f: NeepHpSourceValue
    max_capacity_lct_f: NeepHpSourceValue
    input_power_max_lct_f: NeepHpSourceValue
    cop_max_lct_f: NeepHpSourceValue


NEEP_HP_SOURCE_HEADERS: dict[str, str] = {
    'date_added_to_list': 'Date Added to List',
    'status': 'Status',
    'brand_owner': 'Brand Owner',
    'brand_name': 'Brand Name',
    'series_name': 'Series Name',
    'ducting_configuration': 'Ducting Configuration',
    'ahri_certified_reference_number': 'AHRI Certified Reference Number⁺',
    'old_ahri_certified_reference_number': 'Old AHRI Certified Reference Number⁺',
    'ahri_type': 'AHRI Type⁺',
    'outdoor_unit_model_number': 'Outdoor Unit Model Number⁺',
    'indoor_type': 'Indoor Type',
    'indoor_model_number_s': 'Indoor Model Number(s)⁺',
    'furnace_model_number_if_applicable': 'Furnace Model Number (if applicable)⁺',
    'eer': 'EER⁺',
    'seer': 'SEER⁺',
    'hspf_region_iv': 'HSPF (Region IV)⁺',
    'eer2': 'EER2⁺',
    'seer2': 'SEER2⁺',
    'hspf2_region_iv': 'HSPF2 (Region IV)⁺',
    'hspf2_region_v': 'HSPF2 (Region V)',
    'energy_star_certified': 'ENERGY STAR Certified',
    'energy_star_cold_climate_certified': 'ENERGY STAR Cold Climate Certified',
    'eligible_for_federal_tax_credit_north': 'Eligible for Federal Tax Credit - North',
    'eligible_for_federal_tax_credit_south': 'Eligible for Federal Tax Credit - South',
    'cee_tier_1_path_a_2025': 'CEE Tier 1 Path A (2025)',
    'cee_tier_1_path_b_2025': 'CEE Tier 1 Path B (2025)',
    'capacity_maintenance_rated_17_f_rated_47_f': 'Capacity Maintenance (Rated 17°F/Rated 47°F)',
    'capacity_maintenance_rated_5_f_rated_47_f': 'Capacity Maintenance (Rated 5°F/Rated 47°F)',
    'capacity_maintenance_max_5_f_rated_47_f': 'Capacity Maintenance (Max 5°F/Rated 47°F)',
    'variable_capacity': 'Variable Capacity?',
    'pan_heater_integrated_or_accessory_provide_model': 'Pan Heater: Integrated or Accessory (provide model #)',
    'input_power_w': 'Input Power (W)',
    'what_determines_when_heater_operates': 'What determines when heater operates?',
    'integration_describe_any_capabilities_this_ashp_system_or_its_controller_s_have_related_to_integrating_other_heating_systems_third_party_thermostats_including_works_with_etc': 'Integration: Describe any capabilities this ASHP system or its controller(s) have related to integrating other heating systems/third-party thermostats, including “works with,” etc.',
    'connectivity_describe_any_capabilities_this_ashp_system_or_its_controller_s_have_related_to_communication_with_the_consumer_or_utility_e_g_meets_energy_star_connected_criteria_system_controller_have_an_interface_that_allows_for_remote_communication_with_the_consumer_or_utility_wi_fi_connected_etc': 'Connectivity: Describe any capabilities this ASHP system or its controller(s) have related to communication with the consumer or utility (e.g. meets ENERGY STAR “Connected” criteria, system/controller have an interface that allows for remote communication with the consumer or utility, wi-fi connected, etc.)',
    'operational_diagnostics_describe_any_capabilities_of_this_ashp_system_to_self_report_or_self_diagnose_its_operation_or_the_quality_of_its_installation_including_whether_the_system_meets_any_all_of_energy_star_s_installation_capabilities_criteria': 'Operational diagnostics: Describe any capabilities of this ASHP system to self-report or self-diagnose its operation or the quality of its installation, including whether the system meets any/all of ENERGY STAR’s Installation Capabilities criteria.',
    'refrigerant': 'Refrigerant',
    'sold_in': 'Sold In?',
    'min_capacity_95_f': 'Min Capacity 95°F',
    'input_power_min_95_f': 'Input Power Min 95°F',
    'cop_min_95_f': 'COP Min 95°F',
    'rated_capacity_95_f': 'Rated Capacity 95°F⁺',
    'input_power_rated_95_f': 'Input Power Rated 95°F',
    'cop_rated_95_f': 'COP Rated 95°F',
    'max_capacity_95_f': 'Max Capacity 95°F',
    'input_power_max_95_f': 'Input Power Max 95°F',
    'cop_max_95_f': 'COP Max 95°F',
    'min_capacity_82_f': 'Min Capacity 82°F',
    'input_power_min_82_f': 'Input Power Min 82°F',
    'cop_min_82_f': 'COP Min 82°F',
    'max_capacity_82_f': 'Max Capacity 82°F',
    'input_power_max_82_f': 'Input Power Max 82°F',
    'cop_max_82_f': 'COP Max 82°F',
    'min_capacity_47_f': 'Min Capacity 47°F',
    'input_power_min_47_f': 'Input Power Min 47°F',
    'cop_min_47_f': 'COP Min 47°F',
    'rated_capacity_47_f': 'Rated Capacity 47°F⁺',
    'input_power_rated_47_f': 'Input Power Rated 47°F',
    'cop_rated_47_f': 'COP Rated 47°F',
    'max_capacity_47_f': 'Max Capacity 47°F',
    'input_power_max_47_f': 'Input Power Max 47°F',
    'cop_max_47_f': 'COP Max 47°F',
    'min_capacity_17_f': 'Min Capacity 17°F',
    'input_power_min_17_f': 'Input Power Min 17°F',
    'cop_min_17_f': 'COP Min 17°F',
    'rated_capacity_17_f': 'Rated Capacity 17°F⁺',
    'input_power_rated_17_f': 'Input Power Rated 17°F',
    'cop_rated_17_f': 'COP Rated 17°F',
    'max_capacity_17_f': 'Max Capacity 17°F',
    'input_power_max_17_f': 'Input Power Max 17°F',
    'cop_max_17_f': 'COP Max 17°F',
    'min_capacity_5_f': 'Min Capacity 5°F',
    'input_power_min_5_f': 'Input Power Min 5°F',
    'cop_min_5_f': 'COP Min 5°F',
    'rated_capacity_5_f_optional': 'Rated Capacity 5°F - Optional⁺',
    'input_power_rated_5_f_optional': 'Input Power Rated 5°F - Optional',
    'cop_rated_5_f_optional': 'COP Rated 5°F - Optional',
    'max_capacity_5_f': 'Max Capacity 5°F',
    'input_power_max_5_f': 'Input Power Max 5°F',
    'cop_max_5_f': 'COP Max 5°F',
    'lowest_cataloged_temperature_outdoor_dry_bulb_f': 'Lowest Cataloged Temperature (Outdoor Dry Bulb °F)',
    'min_capacity_lct_f': 'Min Capacity LCT°F',
    'input_power_min_lct_f': 'Input Power Min LCT°F',
    'cop_min_lct_f': 'COP Min LCT°F',
    'max_capacity_lct_f': 'Max Capacity LCT°F',
    'input_power_max_lct_f': 'Input Power Max LCT°F',
    'cop_max_lct_f': 'COP Max LCT°F',
}
