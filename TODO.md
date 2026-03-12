# TODO — Funzioni mancanti pyntc vs NTC18 Vault

Copertura attuale: **~240 / 373 items** (~64%)

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

- [ ] **Tab 3.3.III** — Classi di rugosita' del terreno (A-D)

### §3.5 — Azione della temperatura

- [ ] **Tab 3.5.III** — Coefficienti di dilatazione termica per materiale

### §3.6 — Azioni eccezionali

- [ ] **Formula 3.6.1** — Carico d'incendio di progetto q_f,d
- [ ] **Formula 3.6.4** — Curva di incendio esterno (smoldering)

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
- [ ] Formule mancanti: flessione, punzonamento, instabilita' avanzata

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
- [ ] Formule mancanti: stabilita' avanzata (aste composte, piastre, connessioni a T)
- [ ] Tab 4.2.II–XIV rimanenti

### §4.3 — Strutture composte acciaio-cls

- [ ] ~9 formule mancanti (connessione, momento resistente, taglio)

### §4.4 — Legno

- [x] `timber_tension_check` [4.4.2] — trazione parallela
- [x] `timber_compression_check` [4.4.3] — compressione parallela
- [x] `timber_compression_perp_check` [4.4.4] — compressione perpendicolare
- [ ] Formule residue (instabilita' avanzata, fatica)
- [ ] Tab 4.4.I–IV (classi di servizio, k_mod, k_def, proprieta')

### §4.5 — Muratura

- [x] `masonry_vertical_load_eccentricity` [4.5.7] — eccentricita' carichi verticali
- [x] `masonry_horizontal_eccentricity` [4.5.9] — eccentricita' azioni orizzontali
- [x] `masonry_combined_eccentricity` [4.5.10] — combinazione eccentricita'
- [x] `masonry_eccentricity_check` [4.5.11] — verifica limiti eccentricita'
- [ ] Muratura armata §4.5.7, muratura confinata §4.5.8

## Cap. 5 — Ponti

- [x] `bridge_road_partial_factors` [Tab 5.1.V] — gamma SLU ponti stradali
- [x] `bridge_rail_partial_factors` [Tab 5.2.V] — gamma SLU ponti ferroviari
- [x] `bridge_rail_multitrack_factor` [Tab 5.2.III] — riduzione binari multipli
- [x] `bridge_rail_deformation_limits` [Tab 5.2.VIII] — limiti SLE ferroviario
- [x] `bridge_fatigue_traffic_flow` [Tab 5.1.X] — flusso veicoli pesanti (fatica)
- [ ] Tab 5.2.II — L_0 per coefficiente dinamico (tabella qualitativa, non numerica)
- [ ] Tab 5.2.VII — Coefficienti psi SLE ferroviario
- [ ] Tab 5.1.VII/VIII — Modelli di fatica 2/4 (veicoli frequenti/equivalenti)

## Cap. 6 — Geotecnica (~7 formule mancanti)

- [ ] Formule fondazioni superficiali (capacita' portante, cedimenti)
- [ ] Formule pali di fondazione (portata laterale, portata di base)
- [ ] Formule micropali

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
- [ ] Pareti accoppiate, analisi pushover

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
- [ ] Verifica a scorrimento e ribaltamento muri
- [ ] Spinta sismica (Mononobe-Okabe)
