# TODO — Funzioni mancanti pyntc vs NTC18 Vault

Copertura attuale: **~325 / 373 items** (~87%)

---

## Cap. 2 — Sicurezza e periodo di riferimento

- [x] `safety_nominal_life` [Tab 2.4.I] — vita nominale V_N
- [x] `safety_usage_coefficient` [Tab 2.4.II] — coefficiente d'uso C_U
- [x] `reference_period` [2.4.1] — V_R = V_N · C_U

## Cap. 3 — Azioni sulle costruzioni

### §3.2 — Azione sismica

- [x] `seismic_equivalent_shear_velocity` [3.2.1] — V_s,eq
- [x] `seismic_vertical_spectrum_amplification` [3.2.9] — spettro verticale
- [x] `seismic_displacement_spectrum` [3.2.10–3.2.11] — S_De(T)
- [x] `seismic_peak_ground_displacement` [3.2.12] — d_g, v_g
- [x] `seismic_max_ground_displacement` [3.2.13] — d_g,max

### §3.3 — Azione del vento

- [x] `wind_terrain_roughness` [Tab 3.3.III] — classi di rugosita' del terreno (0, I, II, III, IV)

### §3.5 — Azione della temperatura

- [x] `thermal_expansion_coefficient` [Tab 3.5.III] — coefficienti di dilatazione termica per materiale

### §3.6 — Azioni eccezionali

- [x] **Formula 3.6.1** — `fire_design_load` gia' in `fire.py`
- [x] **Formula 3.6.4** — `fire_external_curve` gia' in `fire.py`

## Cap. 4 — Verifiche materiali

### §4.1 — Calcestruzzo

- [x] `concrete_slenderness` [4.1.42] — snellezza λ = l₀/i
- [x] `concrete_slenderness_limit` [4.1.41] — snellezza limite λ_lim = 25/√v
- [x] `concrete_beam_min_reinforcement` [4.1.45] — armatura min. travi
- [x] `concrete_column_min_reinforcement` [4.1.46] — armatura min. pilastri
- [x] `concrete_prestress_stress_limits` [4.1.49] — limiti tensione precompressione
- [x] `concrete_strength_class` [Tab 4.1.I] — classi C8/10–C90/105
- [x] `concrete_crack_mean_strain` [4.1.15] — epsilon_am - epsilon_cm
- [x] `concrete_crack_spacing` [4.1.17] — s_r,max
- [x] `concrete_crack_width` [4.1.14] — w_1 = 1.7 * epsilon * s_r
- [x] `concrete_crack_width_limit` [Tab 4.1.IV] — w_max per classe esposizione
- [x] `concrete_bending_resistance` [4.1.19] — momento resistente sezione rettangolare
- [x] `concrete_bending_check` [4.1.19] — verifica flessione M_Ed ≤ M_Rd
- [x] `concrete_punching_shear_resistance` [4.1.30] — resistenza punzonamento
- [x] `concrete_punching_shear_check` [4.1.30] — verifica punzonamento
- [x] `concrete_punching_shear_resistance_reinforced` [4.1.32] — punzonamento con armatura
- [x] `concrete_column_effective_length` [4.1.2.3.9.1] — lunghezza efficace pilastro
- [x] `concrete_column_interaction_check` [4.1.19] — interazione N-M
- [x] `concrete_min_stirrup_spacing` [4.1.29] — passo massimo staffe

### §4.2 — Acciaio

- [x] `steel_shear_area` [4.2.18–4.2.23] — area resistente a taglio
- [x] `steel_von_mises_check` [4.2.4] — stato tensionale equivalente
- [x] `pin_shear_resistance` [4.2.75] — taglio perno
- [x] `pin_bearing_resistance` [4.2.76] — rifollamento perno
- [x] `steel_bending_resistance_class3` [4.2.13] — M_el,Rd sezione classe 3
- [x] `steel_bending_resistance_class4` [4.2.14] — M_eff,Rd sezione classe 4
- [x] `steel_torsion_resistance` — T_Rd = W_t * f_yk / (sqrt(3) * gamma_M0)
- [x] `steel_torsion_check` [4.2.28] — T_Ed / T_Rd ≤ 1
- [x] `steel_relative_slenderness` [4.2.45–4.2.46] — lambda_bar
- [x] `steel_buckling_resistance_class4` [4.2.43] — N_b,Rd classe 4
- [x] `weld_combined_stress_check` [4.2.81] — verifica combinata saldatura
- [x] `bolt_grade_properties` [Tab 4.2.IX] — proprieta' meccaniche bulloni (gradi 4.6–10.9)
- [x] `pin_bending_resistance` [4.2.77] — resistenza perno a flessione M_Rd
- [x] `steel_ltb_slenderness` [4.251] — snellezza relativa LTB
- [x] `steel_ltb_correction_factor` [4.252] — fattore correttivo f
- [x] `steel_ltb_reduction_factor` [4.250] — fattore riduzione chi_LT
- [x] `steel_ltb_resistance` [4.249] — M_b,Rd = chi_LT * W_y * f_yk / gamma_M1
- [x] `steel_ltb_check` [4.248] — verifica M_Ed / M_b,Rd ≤ 1
- [x] `steel_fatigue_check` [4.254] — verifica a fatica Δs ≤ ΔR/γMf
- [x] `steel_fatigue_normal_stress_check` [4.255] — fatica tensioni normali
- [x] `steel_fatigue_shear_stress_check` [4.256] — fatica tensioni tangenziali
- [x] `steel_fatigue_damage` [4.257] — danno cumulato Miner D = Σ(ni/Ni)
- [x] `steel_vertical_deflection` [4.260] — freccia totale SLE δtot = δ1 + δ2
- [x] `steel_drift_limit` [Tab 4.2.XIII] — spostamento interpiano SLE
- [x] `pin_bearing_resistance_sle` [4.278] — rifollamento perno SLE
- [x] `pin_bending_resistance_sle` [4.279] — flessione perno SLE
- [x] `weld_fillet_directional_resistance` [4.283-4.284] — cordone d'angolo direzionale
- [x] `weld_simplified_stress_check` [4.285] — verifica semplificata cordone
- [ ] Stabilita' avanzata: aste composte, piastre

### §4.3 — Strutture composte acciaio-cls

- [x] `composite_column_plastic_resistance_characteristic` [4.3.19] — resistenza plastica
- [x] `composite_column_effective_stiffness_ii` [4.3.20] — rigidezza effettiva
- [x] `composite_column_confinement_resistance` [4.3.22] — aumento resistenza per confinamento
- [x] `composite_column_reduced_moment_resistance` [4.3.26] — momento resistente ridotto
- [x] `composite_load_dispersion_width` [4.3.38] — larghezza di dispersione del carico
- [x] `composite_shear_connector_resistance` [4.3.8] — resistenza piolo shear stud
- [x] `composite_degree_of_connection` [4.3.2.3.3] — grado di connessione eta
- [x] `composite_beam_plastic_moment` [4.3.1] — momento plastico trave composta
- [x] `composite_beam_minimum_connection_degree` [4.3.2.3.3] — grado minimo connessione

### §4.4 — Legno

- [x] `timber_tension_check` [4.4.2] — trazione parallela
- [x] `timber_compression_check` [4.4.3] — compressione parallela
- [x] `timber_compression_perp_check` [4.4.4] — compressione perpendicolare
- [x] `timber_service_class_description` [Tab 4.4.II] — classi di servizio 1/2/3
- [x] `timber_load_duration_class` [Tab 4.4.I] — classi di durata del carico
- [x] Formule residue (instabilita' avanzata, fatica) — completate

### §4.5 — Muratura

- [x] `masonry_vertical_load_eccentricity` [4.5.7] — eccentricita' carichi verticali
- [x] `masonry_horizontal_eccentricity` [4.5.9] — eccentricita' azioni orizzontali
- [x] `masonry_combined_eccentricity` [4.5.10] — combinazione eccentricita'
- [x] `masonry_eccentricity_check` [4.5.11] — verifica limiti eccentricita'
- [x] `masonry_eccentricity_m` [4.5.6] — eccentricita' accidentale
- [x] `masonry_phi_from_table` [Tab 4.5.III] — coefficiente Φ per interpolazione bilineare
- [x] `masonry_simplified_axial_check` [4.5.12] — verifica semplificata snellezza
- [x] `masonry_reinforced_flexural_resistance` [4.5.7.3] — flessione muratura armata
- [x] `masonry_reinforced_shear_resistance` [4.5.7.4] — taglio muratura armata
- [x] `masonry_reinforced_axial_check` [4.5.7.2] — verifica assiale muratura armata
- [x] `masonry_confined_shear_resistance` [4.5.8.2] — taglio muratura confinata
- [x] `masonry_confined_bending_resistance` [4.5.8.3] — momento muratura confinata

## Cap. 5 — Ponti

- [x] `bridge_road_partial_factors` [Tab 5.1.V] — gamma SLU ponti stradali
- [x] `bridge_rail_partial_factors` [Tab 5.2.V] — gamma SLU ponti ferroviari
- [x] `bridge_rail_multitrack_factor` [Tab 5.2.III] — riduzione binari multipli
- [x] `bridge_rail_deformation_limits` [Tab 5.2.VIII] — limiti SLE ferroviario
- [x] `bridge_fatigue_traffic_flow` [Tab 5.1.X] — flusso veicoli pesanti (fatica)
- [ ] Tab 5.2.II — L_0 per coefficiente dinamico (tabella qualitativa, non numerica)
- [x] `bridge_rail_sle_combination_factors` [Tab 5.2.VII] — coefficienti psi SLE ferroviario
- [x] `bridge_dynamic_factor` [5.2.3] — coefficiente dinamico φ ponti ferroviari
- [x] `bridge_fatigue_vehicle_model2` [Tab 5.1.VII] — veicoli frequenti modello 2
- [x] `bridge_fatigue_vehicle_model4` [Tab 5.1.VIII] — veicoli equivalenti modello 4

## Cap. 6 — Geotecnica

- [x] `geo_bearing_capacity_factors` [6.4.1] — fattori N_c, N_q, N_γ (Brinch-Hansen)
- [x] `geo_shallow_bearing_capacity` [6.4.1] — capacita' portante fondazione superficiale
- [x] `geo_shallow_foundation_check` [6.4.1] — verifica q_Ed ≤ q_lim/γ_R
- [x] `geo_pile_skin_friction` [6.4.3.1] — resistenza laterale palo
- [x] `geo_pile_base_resistance` [6.4.3.1] — resistenza di punta palo
- [x] `geo_pile_total_resistance` [6.4.3.1.1] — resistenza totale palo di progetto
- [x] `geo_pile_check` [6.4.3.1] — verifica N_Ed ≤ R_c,d
- [x] `geo_settlement_elastic` [6.4.2] — cedimento elastico (Schmertmann)
- [x] `geo_consolidation_settlement` [6.4.2] — cedimento consolidazione
- [x] `geo_settlement_check` [6.4.2] — verifica s ≤ s_lim
- [x] `geo_anchor_correlation_factors` [Tab 6.6.III] — fattori ζ_as, ζ_at per ancoraggi
- [x] `geo_anchor_partial_factor` [Tab 6.6.1] — coefficiente parziale γ_g ancoraggi
- [x] `geo_anchor_check` [6.6.1] — verifica R_Ed ≤ R_ak/γ_g
- [x] `geo_retaining_wall_resistance_factor` [Tab 6.5.1] — γ_n muri di sostegno R3
- [ ] Micropali (6.6.1–6.6.2 formule complete)

## Cap. 7 — Progettazione sismica

### §7.4 — C.A. in zona sismica

- [x] `column_capacity_shear` [7.4.5] — taglio di progetto pilastri in capacita'
- [x] `beam_column_joint_shear` [7.4.6–7.4.7] — taglio nodo trave-pilastro
- [x] `joint_concrete_compression_check` [7.4.8] — compressione puntone diagonale
- [x] `joint_eta_factor` [7.4.9] — coefficiente η resistenza nodo
- [x] `joint_horizontal_stirrups` [7.4.11–7.4.12] — armatura orizzontale nodo
- [x] `wall_critical_height` [7.4.13] — altezza zona dissipativa pareti
- [x] `beam_reinforcement_ratio_limits` [7.4.26] — limiti armatura travi
- [x] `column_reinforcement_ratio_check` [7.4.28] — verifica armatura pilastri
- [x] `column_confinement_requirement` [7.4.29–7.4.30] — confinamento pilastri
- [x] `confinement_effectiveness_rectangular` [7.4.31] — efficacia confinamento
- [x] `wall_confinement_requirement` [7.4.32–7.4.33] — confinamento pareti
- [x] `wall_sliding_shear_diagonal` [7.4.20] — contributo diagonali scorrimento parete
- [x] `wall_sliding_shear_inclined` [7.4.21] — contributo armature inclinate
- [x] `wall_sliding_shear_friction` [7.4.22] — contributo attrito
- [x] `wall_sliding_shear_resistance` [7.4.19] — V_Rd,S totale
- [x] `wall_sliding_check` [7.4.18] — verifica V_Ed ≤ V_Rd,S
- [x] `coupling_beam_shear_capacity` [7.4.23] — taglio trave di accoppiamento
- [x] `coupling_beam_shear_check` [7.4.23] — verifica taglio trave accoppiamento
- [x] `coupling_beam_inclined_bars_shear` [7.4.24] — taglio con armature inclinate
- [ ] Analisi pushover

### §7.5 — Acciaio in zona sismica

- [x] `seismic_steel_connection_resistance` [7.5.1] — resistenza connessioni
- [x] `seismic_steel_net_section_check` [7.5.2] — sezione netta membrature tese
- [x] `seismic_steel_column_axial_ductility` [7.5.3] — duttilita' assiale pilastri
- [x] `seismic_steel_section_class_check` [Tab 7.5.1] — classe sezione dissipativa
- [x] `seismic_steel_mrf_column_demand_N/M/V` [7.5.7–7.5.9] — domanda pilastri MRF
- [x] `seismic_steel_mrf_beam_column_hierarchy` [7.5.11] — strong column/weak beam
- [x] `seismic_steel_mrf_connection_moment` [7.5.12] — momento connessione MRF
- [x] `seismic_steel_cbf_diagonal_slenderness` — snellezza diagonali CBF
- [x] `seismic_steel_cbf_member_demand` — domanda membrature CBF
- [x] `seismic_steel_cbf_column_buckling_check` [7.5.15] — instabilita' colonne CBF
- [x] `seismic_steel_cbf_omega_homogeneity` — omogeneita' Omega CBF
- [x] `seismic_steel_ebf_link_bending/shear_resistance` [7.5.17–7.5.18] — link EBF
- [x] `seismic_steel_ebf_link_classification` [7.5.16] — classificazione link EBF
- [x] `seismic_steel_ebf_member/connection_demand` [7.5.25–7.5.26] — domanda EBF
- [x] `seismic_steel_ebf_omega_homogeneity` — omogeneita' Omega EBF

### §7.7 — Legno in zona sismica

- [x] `seismic_timber_behavior_factor` — fattore q per tipologia strutturale
- [x] `seismic_timber_connector_ductility` — requisiti duttilita' connettori
- [x] `seismic_timber_capacity_design` — gerarchia delle resistenze
- [x] `seismic_timber_cyclic_design_strength` — riduzione resistenza ciclica
- [x] `seismic_timber_carpentry_joint_shear` — taglio giunti carpenteria
- [x] `seismic_timber_panel_thickness` — spessori minimi pannelli
- [x] `seismic_timber_bolt_diameter_check` — diametro max bulloni
- [x] `seismic_timber_beam_hb_ratio` — rapporto h/b travi
- [x] `seismic_timber_static_ductility_check` — duttilita' statica minima

### §7.8 — Ponti in zona sismica (§7.9 NTC18)

- [x] `bridge_behavior_factor_vk` [7.9.1] — fattore di comportamento ponti
- [x] `bridge_regularity_factor` [7.9.2] — fattore di regolarita'
- [x] `bridge_period_single_mass` [7.9.4] — periodo metodo massa singola
- [x] `bridge_period_multispan` [7.9.6] — periodo multi-campata
- [x] `bridge_seismic_forces_multispan` [7.9.5] — forze sismiche multi-campata
- [x] `bridge_overstrength_factor` [7.9.7] — fattore di sovraresistenza
- [x] `bridge_pier_capacity_shear` [7.9.10] — taglio in capacita' pila
- [x] `bridge_pier_shear_overstrength` [7.9.11] — sovraresistenza pila
- [x] `bridge_deck_capacity_shear` [7.9.12] — taglio in capacita' impalcato
- [x] `bridge_end_stop_force` / `bridge_overlap_length` — vincoli appoggi
- [x] `bridge_confinement_*` [7.9.15–7.9.22] — 8 funzioni confinamento pile

### §7.9–§7.10 — Fondazioni e isolamento sismico

- [x] `seismic_wall_coeff_horizontal/vertical` [7.11.6–7.11.8] — coeff. muri sostegno
- [x] `seismic_wall_site_acceleration` — accelerazione sito muri
- [x] `seismic_sheet_pile_acceleration` [7.11.9–7.11.10] — accelerazione paratie
- [x] `seismic_sheet_pile_displacement_limit` [7.11.11] — limite spostamento paratia
- [x] `seismic_anchor_free_length` [7.11.12] — lunghezza libera ancoraggio
- [x] `seismic_shallow_foundation_gamma_R` — coefficiente gamma_R fondazioni
- [x] `seismic_isolation_base_shear` — taglio alla base isolamento
- [x] `seismic_isolation_displacement` — spostamento sistema isolato
- [x] `seismic_isolation_torsion_amplification` — amplificazione torsionale
- [x] `seismic_isolation_torsional_radius` — raggio torsionale
- [x] `seismic_active_pressure_coefficient` [7.11.6] — Mononobe-Okabe attivo K_ae
- [x] `seismic_active_earth_pressure` [7.11.6] — spinta attiva sismica E_ae
- [x] `seismic_passive_pressure_coefficient` [7.11.6] — Mononobe-Okabe passivo K_pe
- [x] `seismic_wall_sliding_check` [7.11.6] — verifica a scorrimento muro
- [x] `seismic_wall_overturning_check` [7.11.6] — verifica a ribaltamento muro
