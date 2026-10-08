# NEEP ccASHP source study

Status: source study only  
Studied: 2026-10-07

## Purpose

Study the NEEP Cold Climate Air-Source Heat Pump Product List as an
independent source of heat-pump classification and low-temperature
performance evidence for the `canmet-energy/h2k-hpxml` issue #19
investigation.

This document records the source as published.

It does **not** define SRVX normalization, canonical classifications,
or mappings.

Current boundary:

```text
SOURCE STUDY
↓
SNAPSHOT
↓
ADAPTER
↓
NeepSourceRecord
↓
STOP

Publisher
NEEP — Northeast Energy Efficiency Partnerships
Public application:
https://ashp.neep.org/

The application exposes both:
- a public product-list UI;
- an anonymous REST/JSON API;
- an anonymous XLSX bulk export.
Access and usage restriction
The downloaded XLSX contains the notice:
The NEEP ccASHP Product List download is NOT for commercial use.
If you have an incentive program, and are looking to use this as a
source for a separate qualified products list, please confirm
permission at ccASHP@NEEP.org.

Therefore this snapshot is retained for the isolated upstream/research
contribution.
It must not be assumed to be reusable as SRVX commercial supply data
without resolving the applicable permission/license.
Acquisition
Bulk XLSX
Endpoint:
GET https://ashp.neep.org/api/products/bulk_export/

Observed anonymous response:
HTTP 200
Content-Type:
  application/vnd.openxmlformats-officedocument.spreadsheetml.sheet

Content-Disposition:
  attachment; filename="neep_air_source_heat_pump_2026-10-07.xlsx"

Snapshot:
neep_air_source_heat_pump_2026-10-07.xlsx

Size:
49,641,979 bytes

SHA-256:
bf2afe6e9570bb47a1354d43eda734e4a585895597dfadd9bc2703c8313e5b85

Product API
Collection:
GET /api/products/

Observed on 2026-10-07:
X-Total:           160848
X-Page:            1
X-Per-Page:        60
X-Max-Per-Page:    300
X-Total-Pages:     2681

The API accepts:
?page=1&page_size=300

which returned:
300 records/page
537 total pages

Product detail:
GET /api/products/{id}/

Source vocabulary:
GET /api/ahri_choices/

Other discovered endpoints
GET /api/productexport/

returned HTTP 500 during the study and is not used.
GET /api/products/bulk_export/

is the working XLSX export.
XLSX structure
Workbook sheets:
HP Report
VRF Report
PTHP Report
SPVHP Report
AHRI Rated Fields

Observed worksheet row counts include the notice/header rows.
Data-row counts:
HP Report       155,313
VRF Report            9
PTHP Report           19
SPVHP Report           7
------------------------
Total            155,348

The API collection reported:
160,848 records

Difference:
5,500 records

Therefore the XLSX export must not yet be treated as a byte-for-byte
or record-for-record representation of the complete API collection.
The reason for the 5,500-record difference remains an open source-study
question.
Record grain
The observed product representation describes one NEEP equipment/system
configuration.
Identity fields include source concepts such as:
NEEP product id
AHRI Certified Reference Number
old AHRI reference number
brand owner
brand
series
outdoor unit model
indoor unit model(s)
furnace model
module/system model
AHRI type
system type
ducting configuration

No SRVX identity interpretation is assigned here.
Product lifecycle fields
Observed API fields include:
id
created_date
modified_date
status
date_delisted
owner

Source status vocabulary:
1   Draft
2   Submit New Product
3   Submit for Renewal
4   Delisted
5   Live
6   Awaiting Payment
7   Awaiting Renewal
8   Not Eligible
9   Returned For Corrections
10  Archived

These remain NEEP source statuses.
Source classification vocabulary
System type
Observed system_type_choices:
1  Central Air Conditioning Heat Pump (HP)
2  Variable Refrigerant Flow (VRF) Multi-Split Heat Pump
3  Packaged Terminal Heat Pump (PTHP)
4  Single Package Vertical Heat Pump (SPVHP)
5  Room Heat Pump (RHP)

NEEP also publishes system_type_mapping, which relates source system
types to allowed/source-facing ducting configurations.
These relationships should be preserved as source evidence.
They are not SRVX taxonomy edges at this stage.
Ducting configuration
Observed values:
0   All Ducting Configurations
1   Multizone All Ducted
2   Singlezone Ducted, "Compact Ducted"
3   Singlezone Ducted, Centrally Ducted
4   Multizone All Non-ducted
5   Singlezone Non-Ducted, Ceiling Placement
6   Singlezone Non-Ducted, Wall Placement
7   Singlezone Non-Ducted, Floor Placement
8   Multizone Mix of Ducted and Non-Ducted
10  Packaged Terminal Heat Pump
11  Single Package Vertical Heat Pump
12  Single Package Heat Pump

Indoor type
Observed indoor_choices:
1  ""
2  Ducted Indoor Units
3  Mini-Splits
4  Mixed Ducted and Non-Ducted Indoor Units
5  Non-Ducted Indoor Units

AHRI type
Observed values:
1   HRCU-A-CB
2   HRCU-A-CB-O
3   HMSV-A-CB
4   N/A
5   HRCU-A-C
6   HMSV-A-CB-O
7   HMSR-A-CB
8   HSP-A
9   HMSR-A-CB-O
10  SCP-HSP-A

The source exposes both forward and reverse representations:
ahri_choices
ahri_choices_rev

No interpretation or expansion of these codes is performed yet.
Other classification/evidence fields
Observed source fields include:
variable_capacity
energy_star
energy_star_cold_climate
cee_tier_a
cee_tier_b
fed_tax_credit_n
fed_tax_credit_s
refrigerant
sold_in
indoor_unit_type

Again, these are source vocabulary, not canonical SRVX concepts.
Performance evidence
The HP export directly publishes capacity-maintenance fields:
Capacity Maintenance (Rated 17°F/Rated 47°F)
Capacity Maintenance (Rated 5°F/Rated 47°F)
Capacity Maintenance (Max 5°F/Rated 47°F)

It also publishes the underlying performance values.
Heating
Temperatures represented include:
47°F
17°F
5°F
Lowest Cataloged Temperature (LCT)

For relevant temperatures NEEP may publish:
Min Capacity
Rated Capacity
Max Capacity

Input Power Min
Input Power Rated
Input Power Max

COP Min
COP Rated
COP Max

Cooling
Observed temperatures include:
95°F
82°F

with corresponding min/rated/max performance fields.
Nested API rating model
The REST product representation contains:
ratings[]

Observed rating grain:
one product
× one heating/cooling mode
× one outdoor dry-bulb condition

Example source structure:
rating
  id
  heat_cool
  product
  created_date
  modified_date
  outdoor_dry_bulb
  indoor_dry_bulb

  capacity_min
  capacity_rated
  capacity_max

  power_min
  power_rated
  power_max

  cop_min
  cop_rated
  cop_max

A studied live product contained five ratings:
Heating @ 47°F
Heating @ 17°F
Heating @ 5°F
Cooling @ 95°F
Cooling @ 82°F

This nested representation appears structurally richer and more
source-native than treating every XLSX temperature column as an
independent domain field.
No adapter design is locked by that observation yet.
AHRI provenance
The XLSX AHRI Rated Fields sheet states:
⁺ AHRI certified and verified product information.

Rated capacity information is certified and verified by AHRI,
input power is manufacturer reported,
and COP is calculated.

Source: https://www.ahridirectory.org

This distinction must be preserved when later representing provenance.
In particular:
rated capacity
  → AHRI certified and verified

input power
  → manufacturer reported

COP
  → calculated

Relevance to h2k-hpxml issue #19
NEEP directly represents the quantities needed to evaluate the current
low-temperature ASHP assumption.
For equipment with rated values:
Q17 / Q47
Q5 / Q47

NEEP additionally publishes the corresponding capacity-maintenance
percentages directly.
This provides an independent source for comparison against:
legacy H2K/H3K curve
h2k-hpxml hardcoded 17°F fraction
OpenStudio-HPXML defaults
ENERGY STAR certified performance

Exact MURB fixture lookup
The current NEEP API was queried for:
AHRI 210448841

Result:
0 records

Therefore the exact Samsung MURB fixture used in the h2k-hpxml
repository cannot currently be used as a NEEP cross-source match.
NEEP remains suitable for population-level independent validation.
SourceRecord implications
A future NeepSourceRecord should preserve NEEP source vocabulary and
structure rather than prematurely mapping it to SRVX concepts.
Candidate source concepts that must be preserved include:
product identity
manufacturer/brand identity
model identifiers
AHRI identifiers/type
system_type + system_type_id
ducting_configuration + id
indoor type
status/lifecycle fields
variable-capacity flag
ENERGY STAR flags
refrigerant
market/sold_in
capacity-maintenance fields
nested ratings
source timestamps

The exact SourceRecord schema should be derived from the complete
observed API/export schema before implementation.
Explicit non-decisions
This source study does NOT decide:
NEEP system_type → SRVX classification
NEEP ducting configuration → SRVX classification
AHRI type → SRVX classification
NEEP product → canonical SupplySystem
NEEP product identity → ENERGY STAR identity
NEEP maintenance fields → canonical derived fields

Those belong to later normalization/canonicalization work.
Open questions

1. What exact internal rule causes the API and XLSX export populations
   to differ, particularly the 5,509 additional HP API records?

2. Is the REST ratings[] representation the authoritative/native
   performance representation from which XLSX columns are projected?

3. What update/deletion guarantees, if any, does NEEP publish for API
   records?

4. What permission would be required before any NEEP data could be
   reused outside this research/upstream-contribution context?

The API/XLSX population difference is unresolved but non-blocking for
the h2k-hpxml issue #19 investigation.

Observed population comparison:

API
  HP      160,822
  VRF           9
  PTHP         17
  SPVHP         0
  total    160,848

XLSX
  HP      155,313 Live
  VRF           9 Live
  PTHP         17 Live + 2 Draft
  SPVHP         7 Delisted
  total    155,348

Additional probes showed:
- subscriber=true does not change the API count;
- style=tile does not change the API count;
- style=list does not change the API count;
- widely spaced sampled HP API records were all present in the XLSX;
- therefore the difference is not explained by a simple record-order
  cutoff.

Snapshot decision

For this contribution:

Primary reproducible snapshot
  neep_air_source_heat_pump_2026-10-07.xlsx

Companion source vocabulary
  ahri-choices.json

Companion API evidence
  public /api/products/ representation
  including nested ratings[]

The XLSX is preferred for population analysis because it is an
official dated bulk artifact and avoids reconstructing a snapshot
through hundreds of live API requests.

The API remains useful for studying the richer source-native structure
and classification vocabulary.

Neither surface is treated as canonical SRVX truth.

Next gate
Before implementing an adapter:
1. inventory source fields represented by the chosen XLSX snapshot
2. preserve API/source vocabulary evidence
3. define NeepSourceRecord from the chosen source representation
4. implement deterministic adapter
5. verify representative records
6. STOP before normalization

