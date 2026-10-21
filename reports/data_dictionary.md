# Data dictionary

| column | meaning | role | notes |
|---|---|---|---|
| poi_id | Open Charge Map location ID | split key | Rows from the same location always land in the same split |
| power_kw | Rated connector power in kW | TARGET (log scale) | Median 3.7 kW, long right tail up to 400 kW |
| connection_type | Connector standard (J1772, CCS, CHAdeMO, NACS...) | feature | Rare types grouped as __other__ using training counts only |
| current_type | AC single-phase, AC three-phase, DC | feature | Missing -> Unknown |
| operator | Charging network | feature | Rare operators grouped as __other__; missing -> Unknown |
| usage_type | Access policy (public, membership, restricted...) | feature |  |
| city | City as entered by contributors | feature | Title-cased; rare cities grouped as __other__ |
| latitude, longitude | Location | feature | Standardised with training statistics |
| connector_quantity | Number of identical connectors in the group | feature | log1p, clipped at 50 |
| charge_level | Level 1/2/3 bucket | EXCLUDED | Derived from the target (leakage) |
| amps, voltage | Electrical rating | EXCLUDED | amps x volts = power (leakage), 26% missing |
| connector_status, number_of_points | Status and point count | EXCLUDED | >85% missing |
| date_created, date_last_verified | Record timestamps | EXCLUDED | Reflect bulk imports, not install dates |
| flag_missing_target, flag_level_kw_mismatch | Quality flags added in v2 | metadata | Used to build the model-ready set |
