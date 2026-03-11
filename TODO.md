# TODO — Funzioni mancanti pyntc vs NTC18 Vault

Copertura attuale: **~201 / 373 items** (~54%)

---

## Cap. 2 — Sicurezza e periodo di riferimento

- [ ] **Tab 2.4.1 + Tab 2.4.II + Formula 2.4.1** — Vita nominale V_N, coefficiente d'uso C_U, periodo di riferimento V_R = V_N · C_U

## Cap. 3 — Azioni sulle costruzioni

### §3.2 — Azione sismica

- [ ] **Formula 3.2.1** — Velocita' equivalente onde di taglio V_s,eq
- [ ] **Formula 3.2.9 + Tab 3.2.VI** — Spettro elastico componente verticale
- [ ] **Formule 3.2.10–3.2.11 + Tab 3.2.VII** — Spettro di spostamento (S_De)
- [ ] **Formule 3.2.12–3.2.16** — Spostamento e velocita' del terreno (d_g, v_g)

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
- [ ] Formule mancanti: flessione, punzonamento, instabilita' avanzata, fessurazione SLE
- [ ] Tab 4.1.I–IV (classi di resistenza, esposizione, fessurazione)

### §4.2 — Acciaio

- [x] `steel_shear_area` [4.2.18–4.2.23] — area resistente a taglio
- [x] `steel_von_mises_check` [4.2.4] — stato tensionale equivalente
- [x] `pin_shear_resistance` [4.2.75] — taglio perno
- [x] `pin_bearing_resistance` [4.2.76] — rifollamento perno
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

### Priorita' alta

- [ ] **Tab 5.1.V** — Coefficienti parziali gamma ponti stradali (EQU, A1, A2)
- [ ] **Tab 5.2.V** — Coefficienti parziali gamma ponti ferroviari

### Priorita' media

- [ ] **Tab 5.2.II** — Lunghezza caratteristica L_0 per coefficiente dinamico
- [ ] **Tab 5.2.III** — Riduzione carichi per binari multipli
- [ ] **Tab 5.2.VII** — Coefficienti psi aggiuntivi SLE ferroviario
- [ ] **Tab 5.2.VIII** — Limiti variazione angolare e raggio minimo per velocita'

### Priorita' bassa (fatica)

- [ ] **Tab 5.1.VII** — Modello di fatica 2 (veicoli frequenti)
- [ ] **Tab 5.1.VIII** — Modello di fatica 4 (veicoli equivalenti)
- [ ] **Tab 5.1.X** — Flusso annuo veicoli pesanti

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
