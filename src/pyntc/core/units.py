"""Costanti fisiche e coefficienti parziali di sicurezza NTC18.

Tutte le grandezze sono in unita' SI:
- forze in kN
- lunghezze in m
- tensioni in kN/m^2 (= kPa)
- pesi per unita' di volume in kN/m^3
"""

# --- Costanti fisiche ---
g = 9.81  # accelerazione di gravita' [m/s^2]

# --- Coefficienti parziali di sicurezza (NTC18 Cap. 2, Cap. 4) ---
gamma_c = 1.5    # calcestruzzo
gamma_s = 1.15   # acciaio da armatura
gamma_M0 = 1.05  # acciaio strutturale - resistenza sezioni
gamma_M1 = 1.05  # acciaio strutturale - instabilita'
gamma_M2 = 1.25  # acciaio strutturale - resistenza netta

# --- Pesi unita' di volume dei materiali principali [kN/m^3] (NTC18 Tab. 3.1.1) ---
GAMMA_CLS_ORDINARIO = 24.0
GAMMA_CLS_ARMATO = 25.0
GAMMA_ACCIAIO = 78.5
GAMMA_GHISA = 72.5
GAMMA_ALLUMINIO = 27.0
GAMMA_ACQUA_DOLCE = 9.81
GAMMA_ACQUA_MARE = 10.1
