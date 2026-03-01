# pyntc — Istruzioni per Claude Code

## Cosa e' pyntc
Libreria Python open source (MIT) per verifiche strutturali secondo NTC 2018 (D.M. 17/01/2018).
Architettura definita in ADR-001.

## Struttura
- `src/pyntc/actions/` — Azioni a monte del solutore (carichi, combinazioni, sismica, vento, neve, temperatura, incendio)
- `src/pyntc/checks/` — Verifiche a valle del solutore (c.a., acciaio, muratura, geotecnica)
- `src/pyntc/core/` — Decoratore `@ntc_ref()` e costanti SI
- `tests/` — Test pytest (TDD: test PRIMA dell'implementazione)
- `ntc18_data/` — JSON strutturati del testo NTC18 parsato con dots.ocr

## Regole di sviluppo
1. Ogni funzione pubblica DEVE avere `@ntc_ref(article=..., table=..., formula=...)`
2. TDD: scrivi il test prima, poi l'implementazione
3. Unita' SI ovunque, documentate in docstring tra `[kN/m^2]`
4. Nomi funzioni in inglese, snake_case
5. Solo `numpy` come dipendenza core, `scipy` opzionale
6. Il solutore FEM e' ESTERNO — pyntc non dipende da OpenSees
7. Use AskUserQuestion if you need to clarify the approach
8. In caso di dubbi su valori OCR o interpretazione della norma, puoi procedere con la tua interpretazione ma DEVI documentare il dubbio in `DUBBI_NTC18.md` (sezione, valore dubbio, motivazione, stato)

## Comandi
- `pytest -v` — esegui tutti i test
- `pytest --cov=pyntc` — coverage
- `/pyntc <sezione>` — skill per scaffolding TDD di un modulo NTC18

## Stato implementazione

| Modulo | Sezione | Funzioni | Test | Stato |
|--------|---------|----------|------|-------|
| `actions/loads.py` | §3.1 | `unit_weight`, `partition_equivalent_load`, `variable_load`, `area_reduction_factor`, `floor_reduction_factor` | 60 | Fatto |
| `actions/wind.py` | §3.3 | `wind_base_velocity`, `wind_return_coefficient`, `wind_reference_velocity`, `wind_kinetic_pressure`, `wind_exposure_coefficient`, `wind_pressure`, `wind_friction_action` | 41 | Fatto |
| `actions/snow.py` | §3.4 | `snow_ground_load`, `snow_shape_coefficient`, `snow_exposure_coefficient`, `snow_roof_load` | 30 | Fatto |
| `actions/seismic.py` | §3.2 | `seismic_return_period`, `seismic_damping_factor`, `seismic_soil_amplification`, `seismic_topographic_amplification`, `elastic_response_spectrum` | 33 | Fatto |
| `actions/temperature.py` | §3.5 | `temperature_extremes`, `temperature_solar_increment`, `temperature_uniform_variation` | 29 | Fatto |
| `actions/fire.py` | §3.6 | `fire_standard_curve`, `fire_hydrocarbon_curve`, `fire_external_curve`, `fire_design_load`, `explosion_equivalent_pressure`, `impact_vehicle_force`, `impact_forklift_force` | 43 | Fatto |
| `actions/combinations.py` | §2.5.3 | `combination_coefficients`, `partial_safety_factors`, `slu_combination`, `sle_characteristic_combination`, `sle_frequent_combination`, `sle_quasi_permanent_combination`, `seismic_combination`, `exceptional_combination`, `seismic_masses` | 60 | Fatto |
| `checks/concrete.py` | §4.1 | `concrete_design_compressive_strength`, `concrete_design_tensile_strength`, `steel_design_strength`, `bond_design_strength`, `concrete_strain_limits`, `concrete_confined_strength`, `concrete_stress_limit`, `steel_stress_limit`, `shear_resistance_no_stirrups`, `shear_resistance_with_stirrups`, `torsion_resistance`, `torsion_shear_interaction`, `biaxial_bending_check` | 63 | Fatto |
| `checks/bridges.py` | Cap.5 | `bridge_conventional_lanes`, `bridge_load_scheme_1`, `bridge_long_span_load`, `bridge_braking_force_road`, `bridge_centrifugal_force_road`, `bridge_road_psi_coefficients`, `bridge_lm71_axle_loads`, `bridge_sw_load`, `bridge_natural_frequency`, `bridge_dynamic_coefficient`, `bridge_reduced_dynamic_coefficient`, `bridge_frequency_limits`, `bridge_centrifugal_reduction_factor`, `bridge_centrifugal_force_rail`, `bridge_braking_force_rail`, `bridge_starting_force_rail`, `bridge_curvature_radius`, `bridge_rail_psi_coefficients` | 96 | Fatto |

| `checks/seismic_design.py` | Cap.7 | `seismic_force_nonstructural`, `behavior_factor_base`, `behavior_factor`, `behavior_factor_nondissipative`, `pdelta_sensitivity`, `cqc_modal_combination`, `approximate_period`, `equivalent_static_forces`, `displacement_ductility`, `seismic_directional_combination`, `curvature_ductility_demand`, `capacity_design_columns`, `pseudostatic_coefficients` | 99 | Fatto |

| `checks/existing_buildings.py` | Cap.8 | `confidence_factor`, `safety_ratio_seismic`, `safety_ratio_vertical`, `improvement_check`, `adequacy_check`, `adequacy_required_load_increase`, `existing_design_strength_ductile`, `existing_design_strength_brittle` | 63 | Fatto |

| `checks/steel.py` | §4.2 | `steel_grade_properties`, `steel_tension_resistance`, `steel_compression_resistance`, `steel_bending_resistance`, `steel_shear_resistance`, `steel_bending_shear_reduction`, `steel_NM_resistance_y`, `steel_NM_resistance_z`, `steel_biaxial_check`, `steel_buckling_imperfection`, `steel_buckling_reduction`, `steel_buckling_resistance`, `steel_lt_buckling_reduction`, `steel_lt_buckling_resistance`, `bolt_shear_resistance`, `bolt_tension_resistance`, `bolt_shear_tension_interaction`, `weld_fillet_resistance` | 85 | Fatto |

| `checks/masonry.py` | §4.5 | `masonry_partial_safety_factor`, `masonry_design_compressive_strength`, `masonry_design_shear_strength`, `masonry_slenderness`, `masonry_lateral_restraint_factor`, `masonry_effective_height`, `masonry_eccentricity_coefficient`, `masonry_reduction_factor`, `masonry_reduced_strength`, `masonry_simplified_check` | 60 | Fatto |

| `checks/composite.py` | §4.3 | `composite_effective_width`, `composite_moment_redistribution_limits`, `composite_stud_alpha`, `composite_stud_resistance`, `composite_profiled_sheet_reduction`, `composite_minimum_connection_degree`, `composite_column_plastic_resistance`, `composite_concrete_part_resistance`, `composite_steel_contribution_ratio`, `composite_column_effective_stiffness`, `composite_column_slenderness`, `composite_column_buckling_curve`, `composite_column_buckling_resistance`, `composite_confinement_coefficients`, `composite_column_local_buckling_check`, `composite_column_bending_check`, `composite_moment_amplification`, `composite_column_biaxial_check`, `composite_beam_shear_distribution`, `composite_bond_stress_limit` | 110 | Fatto |

| `checks/geotechnical.py` | Cap.6 | `geo_action_partial_factors`, `geo_material_partial_factors`, `geo_uplift_partial_factors`, `geo_uplift_check`, `geo_sifonamento_check`, `geo_design_resistance`, `geo_design_check`, `geo_shallow_foundation_factors`, `geo_pile_resistance_factors`, `geo_pile_correlation_static`, `geo_pile_correlation_profiles`, `geo_pile_correlation_dynamic`, `geo_pile_characteristic_resistance`, `geo_pile_transverse_factor`, `geo_retaining_wall_factors`, `geo_anchor_resistance_factors`, `geo_anchor_correlation_tests`, `geo_anchor_correlation_profiles`, `geo_anchor_characteristic_resistance`, `geo_embankment_resistance_factor` | 127 | Fatto |

| `checks/timber.py` | §4.4 | `timber_partial_safety_factor`, `timber_kmod`, `timber_kdef`, `timber_design_strength`, `timber_long_term_modulus`, `timber_km_factor`, `timber_biaxial_bending_check`, `timber_tension_bending_check`, `timber_compression_bending_check`, `timber_shear_check`, `timber_torsion_shape_factor`, `timber_torsion_check`, `timber_shear_torsion_interaction`, `timber_beam_critical_factor`, `timber_beam_stability_check`, `timber_column_relative_slenderness`, `timber_column_critical_factor`, `timber_column_stability_check`, `timber_deflection_limits`, `timber_straightness_limit` | 140 | Fatto |

| `checks/glass.py` | §4.6 | — | — | Todo |

**Suite totale: 1142 test passed**

## Convenzioni commit
- `feat(actions): add wind_base_velocity §3.3.1`
- `test(actions): add tests for snow_ground_load §3.4.2`
- `fix(core): correct @ntc_ref decorator wrapping`
