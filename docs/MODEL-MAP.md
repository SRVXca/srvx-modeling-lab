# SRVX Modeling Lab — Model Map

This document records discovered external model ownership and data flow.

It does not establish canonical SRVX semantics.

Current working map:

REAL BUILDING
  -> geometry / physical representation
     CityJSON / IFC / IfcOpenShell

  -> residential energy representation
     H2K / HPXML

  -> equipment performance representation
     HPXML / ASHRAE 205

  -> simulation
     OpenStudio-HPXML / EnergyPlus

  -> calculated model results

  -> SRVX
     normalized observations
     evidence / provenance
     Supply identity
     Québec subsidies
     seller offers
     installation economics
     contractor execution
     customer decision

This map must be refined from inspected upstream source code rather than
assumptions.
