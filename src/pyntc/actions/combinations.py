"""Combinazioni delle azioni — NTC18 §2.5.3.

Combinazione fondamentale SLU [2.5.1], combinazioni SLE [2.5.2]-[2.5.4],
combinazione sismica [2.5.5], combinazione eccezionale [2.5.6],
masse sismiche [2.5.7]. Tabelle coefficienti Tab. 2.5.1 e Tab. 2.6.1.
"""

from __future__ import annotations

from pyntc.core.reference import ntc_ref


# ── Tab. 2.5.1 — Coefficienti di combinazione ψ ─────────────────────────────
# (ψ_0, ψ_1, ψ_2)

_PSI_TABLE: dict[str, tuple[float, float, float]] = {
    "A":           (0.7, 0.5, 0.3),   # Residenziale
    "B":           (0.7, 0.5, 0.3),   # Uffici
    "C":           (0.7, 0.7, 0.6),   # Affollamento
    "D":           (0.7, 0.7, 0.6),   # Commerciale
    "E":           (1.0, 0.9, 0.8),   # Magazzini/industriale
    "F":           (0.7, 0.7, 0.6),   # Parcheggi ≤ 30 kN
    "G":           (0.7, 0.5, 0.3),   # Parcheggi > 30 kN
    "H":           (0.0, 0.0, 0.0),   # Coperture sola manutenzione
    "K":           (0.6, 0.2, 0.0),   # Coperture usi speciali
    "wind":        (0.6, 0.2, 0.0),   # Vento
    "snow_low":    (0.5, 0.2, 0.0),   # Neve quota ≤ 1000 m
    "snow_high":   (0.7, 0.5, 0.2),   # Neve quota > 1000 m
    "temperature": (0.6, 0.5, 0.0),   # Variazioni termiche
}


# ── Tab. 2.6.1 — Coefficienti parziali γ_F per SLU ──────────────────────────

_GAMMA_TABLE: dict[str, tuple[float, float, float, float, float, float]] = {
    #           G1_fav  G1_sfav  G2_fav  G2_sfav  Q_fav  Q_sfav
    "EQU": (    0.9,    1.1,     0.8,    1.5,     0.0,   1.5),
    "A1":  (    1.0,    1.3,     0.8,    1.5,     0.0,   1.5),
    "A2":  (    1.0,    1.0,     0.8,    1.3,     0.0,   1.3),
}

# Indici nella tupla _GAMMA_TABLE per ciascun load_type
_GAMMA_INDEX: dict[str, tuple[int, int]] = {
    "G1": (0, 1),  # (fav_idx, sfav_idx)
    "G2": (2, 3),
    "Q":  (4, 5),
}


# ── Tab. 2.5.1 — Lookup ψ ───────────────────────────────────────────────────

@ntc_ref(article="2.5.2", table="Tab.2.5.1")
def combination_coefficients(category: str) -> tuple[float, float, float]:
    """Coefficienti di combinazione ψ_0, ψ_1, ψ_2 [-].

    NTC18 §2.5.2, Tab. 2.5.1.

    Parameters
    ----------
    category : str
        Categoria o azione variabile. Valori ammessi:
        - ``"A"``..``"H"``, ``"K"``: categorie edifici (Tab. 3.1.II)
        - ``"wind"``: vento
        - ``"snow_low"``: neve quota ≤ 1000 m s.l.m.
        - ``"snow_high"``: neve quota > 1000 m s.l.m.
        - ``"temperature"``: variazioni termiche

    Returns
    -------
    tuple[float, float, float]
        ``(ψ_0, ψ_1, ψ_2)`` coefficienti di combinazione [-].

    Raises
    ------
    ValueError
        Se ``category`` non e' valida o e' ``"I"`` (da valutare caso per caso).
    """
    if category == "I":
        raise ValueError(
            "Categoria I (coperture praticabili): i coefficienti psi sono "
            "da valutarsi caso per caso (NTC18 Tab. 2.5.1)."
        )
    if category not in _PSI_TABLE:
        raise ValueError(
            f"Categoria '{category}' non valida. "
            f"Valori ammessi: {', '.join(sorted(_PSI_TABLE.keys()))}, I."
        )
    return _PSI_TABLE[category]


# ── Tab. 2.6.1 — Lookup γ ───────────────────────────────────────────────────

@ntc_ref(article="2.6.1", table="Tab.2.6.1")
def partial_safety_factors(
    load_type: str,
    favorable: bool,
    approach: str = "A1",
) -> float:
    """Coefficiente parziale di sicurezza γ_F per SLU [-].

    NTC18 §2.6.1, Tab. 2.6.1.

    Parameters
    ----------
    load_type : str
        Tipo di carico: ``"G1"`` (permanenti strutturali),
        ``"G2"`` (permanenti non strutturali), ``"Q"`` (variabili).
    favorable : bool
        ``True`` se l'azione ha effetto favorevole.
    approach : str
        Approccio di verifica: ``"EQU"``, ``"A1"`` (STR), ``"A2"`` (GEO).

    Returns
    -------
    float
        Coefficiente parziale γ_F [-].

    Raises
    ------
    ValueError
        Se ``load_type`` o ``approach`` non sono validi.
    """
    if load_type not in _GAMMA_INDEX:
        raise ValueError(
            f"load_type '{load_type}' non valido. "
            f"Valori ammessi: {', '.join(_GAMMA_INDEX.keys())}."
        )
    if approach not in _GAMMA_TABLE:
        raise ValueError(
            f"approach '{approach}' non valido. "
            f"Valori ammessi: {', '.join(_GAMMA_TABLE.keys())}."
        )
    fav_idx, sfav_idx = _GAMMA_INDEX[load_type]
    idx = fav_idx if favorable else sfav_idx
    return _GAMMA_TABLE[approach][idx]


# ── Funzione helper per validare Q/categories ────────────────────────────────

def _validate_Q_categories(
    Q: list[float], categories: list[str],
) -> list[tuple[float, float, float]]:
    """Valida e restituisce i coefficienti ψ per ogni azione variabile."""
    if len(Q) != len(categories):
        raise ValueError(
            f"Q e categories devono avere la stessa lunghezza, "
            f"ricevuto {len(Q)} e {len(categories)}."
        )
    return [combination_coefficients(cat) for cat in categories]


# ── [2.5.1] — Combinazione fondamentale SLU ─────────────────────────────────

@ntc_ref(article="2.5.3", formula="2.5.1")
def slu_combination(
    G1: float,
    G2: float,
    Q: list[float],
    categories: list[str],
    P: float = 0.0,
    approach: str = "A1",
) -> float:
    """Combinazione fondamentale per stati limite ultimi.

    NTC18 §2.5.3, Formula [2.5.1]:
        γ_G1·G_1 + γ_G2·G_2 + γ_P·P + γ_Q·Q_k1 + Σ(γ_Q·ψ_0i·Q_ki)

    La funzione prova ogni azione variabile come dominante e
    restituisce il valore massimo della combinazione.

    Parameters
    ----------
    G1 : float
        Carichi permanenti strutturali (sfavorevoli) [kN o kN/m²].
    G2 : float
        Carichi permanenti non strutturali (sfavorevoli) [kN o kN/m²].
    Q : list[float]
        Valori caratteristici delle azioni variabili [kN o kN/m²].
    categories : list[str]
        Categorie corrispondenti a ciascuna Q (per lookup ψ).
    P : float
        Precompressione [kN o kN/m²]. Default 0.
    approach : str
        Approccio di verifica: ``"EQU"``, ``"A1"``, ``"A2"``.

    Returns
    -------
    float
        Valore della combinazione piu' gravosa.

    Raises
    ------
    ValueError
        Se ``Q`` e ``categories`` hanno lunghezze diverse.
    """
    psi_list = _validate_Q_categories(Q, categories)

    gamma_G1 = partial_safety_factors("G1", favorable=False, approach=approach)
    gamma_G2 = partial_safety_factors("G2", favorable=False, approach=approach)
    gamma_Q = partial_safety_factors("Q", favorable=False, approach=approach)
    gamma_P = 1.0  # §2.6.1: γ_P = 1.0

    base = gamma_G1 * G1 + gamma_G2 * G2 + gamma_P * P

    if not Q:
        return base

    # Prova ogni Q[j] come azione dominante
    max_val = float("-inf")
    for j in range(len(Q)):
        val = base + gamma_Q * Q[j]
        for i in range(len(Q)):
            if i != j:
                psi_0 = psi_list[i][0]
                val += gamma_Q * psi_0 * Q[i]
        if val > max_val:
            max_val = val

    return max_val


# ── [2.5.2] — Combinazione caratteristica (rara) SLE ────────────────────────

@ntc_ref(article="2.5.3", formula="2.5.2")
def sle_characteristic_combination(
    G1: float,
    G2: float,
    Q: list[float],
    categories: list[str],
    P: float = 0.0,
) -> float:
    """Combinazione caratteristica (rara) per SLE irreversibili.

    NTC18 §2.5.3, Formula [2.5.2]:
        G_1 + G_2 + P + Q_k1 + Σ(ψ_0i·Q_ki)

    Parameters
    ----------
    G1 : float
        Carichi permanenti strutturali [kN o kN/m²].
    G2 : float
        Carichi permanenti non strutturali [kN o kN/m²].
    Q : list[float]
        Valori caratteristici delle azioni variabili [kN o kN/m²].
    categories : list[str]
        Categorie corrispondenti a ciascuna Q.
    P : float
        Precompressione [kN o kN/m²]. Default 0.

    Returns
    -------
    float
        Valore della combinazione piu' gravosa.
    """
    psi_list = _validate_Q_categories(Q, categories)

    base = G1 + G2 + P

    if not Q:
        return base

    max_val = float("-inf")
    for j in range(len(Q)):
        val = base + Q[j]
        for i in range(len(Q)):
            if i != j:
                val += psi_list[i][0] * Q[i]
        if val > max_val:
            max_val = val

    return max_val


# ── [2.5.3] — Combinazione frequente SLE ────────────────────────────────────

@ntc_ref(article="2.5.3", formula="2.5.3")
def sle_frequent_combination(
    G1: float,
    G2: float,
    Q: list[float],
    categories: list[str],
    P: float = 0.0,
) -> float:
    """Combinazione frequente per SLE reversibili.

    NTC18 §2.5.3, Formula [2.5.3]:
        G_1 + G_2 + P + ψ_11·Q_k1 + Σ(ψ_2i·Q_ki)

    Parameters
    ----------
    G1 : float
        Carichi permanenti strutturali [kN o kN/m²].
    G2 : float
        Carichi permanenti non strutturali [kN o kN/m²].
    Q : list[float]
        Valori caratteristici delle azioni variabili [kN o kN/m²].
    categories : list[str]
        Categorie corrispondenti a ciascuna Q.
    P : float
        Precompressione [kN o kN/m²]. Default 0.

    Returns
    -------
    float
        Valore della combinazione piu' gravosa.
    """
    psi_list = _validate_Q_categories(Q, categories)

    base = G1 + G2 + P

    if not Q:
        return base

    max_val = float("-inf")
    for j in range(len(Q)):
        psi_1j = psi_list[j][1]  # ψ_1 dell'azione dominante
        val = base + psi_1j * Q[j]
        for i in range(len(Q)):
            if i != j:
                psi_2i = psi_list[i][2]  # ψ_2 delle accompagnanti
                val += psi_2i * Q[i]
        if val > max_val:
            max_val = val

    return max_val


# ── [2.5.4] — Combinazione quasi permanente SLE ─────────────────────────────

@ntc_ref(article="2.5.3", formula="2.5.4")
def sle_quasi_permanent_combination(
    G1: float,
    G2: float,
    Q: list[float],
    categories: list[str],
    P: float = 0.0,
) -> float:
    """Combinazione quasi permanente per effetti a lungo termine.

    NTC18 §2.5.3, Formula [2.5.4]:
        G_1 + G_2 + P + Σ(ψ_2i·Q_ki)

    Parameters
    ----------
    G1 : float
        Carichi permanenti strutturali [kN o kN/m²].
    G2 : float
        Carichi permanenti non strutturali [kN o kN/m²].
    Q : list[float]
        Valori caratteristici delle azioni variabili [kN o kN/m²].
    categories : list[str]
        Categorie corrispondenti a ciascuna Q.
    P : float
        Precompressione [kN o kN/m²]. Default 0.

    Returns
    -------
    float
        Valore della combinazione.
    """
    psi_list = _validate_Q_categories(Q, categories)

    result = G1 + G2 + P
    for i in range(len(Q)):
        psi_2i = psi_list[i][2]
        result += psi_2i * Q[i]

    return result


# ── [2.5.5] — Combinazione sismica ──────────────────────────────────────────

@ntc_ref(article="2.5.3", formula="2.5.5")
def seismic_combination(
    E: float,
    G1: float,
    G2: float,
    Q: list[float],
    categories: list[str],
    P: float = 0.0,
) -> float:
    """Combinazione sismica per SLU e SLE connessi all'azione sismica.

    NTC18 §2.5.3, Formula [2.5.5]:
        E + G_1 + G_2 + P + Σ(ψ_2i·Q_ki)

    Parameters
    ----------
    E : float
        Azione sismica [kN o kN/m²].
    G1 : float
        Carichi permanenti strutturali [kN o kN/m²].
    G2 : float
        Carichi permanenti non strutturali [kN o kN/m²].
    Q : list[float]
        Valori caratteristici delle azioni variabili [kN o kN/m²].
    categories : list[str]
        Categorie corrispondenti a ciascuna Q.
    P : float
        Precompressione [kN o kN/m²]. Default 0.

    Returns
    -------
    float
        Valore della combinazione sismica.
    """
    psi_list = _validate_Q_categories(Q, categories)

    result = E + G1 + G2 + P
    for i in range(len(Q)):
        psi_2i = psi_list[i][2]
        result += psi_2i * Q[i]

    return result


# ── [2.5.6] — Combinazione eccezionale ──────────────────────────────────────

@ntc_ref(article="2.5.3", formula="2.5.6")
def exceptional_combination(
    G1: float,
    G2: float,
    A_d: float,
    Q: list[float],
    categories: list[str],
    P: float = 0.0,
) -> float:
    """Combinazione eccezionale per SLU connessi alle azioni eccezionali.

    NTC18 §2.5.3, Formula [2.5.6]:
        G_1 + G_2 + P + A_d + Σ(ψ_2i·Q_ki)

    Parameters
    ----------
    G1 : float
        Carichi permanenti strutturali [kN o kN/m²].
    G2 : float
        Carichi permanenti non strutturali [kN o kN/m²].
    A_d : float
        Valore di progetto dell'azione eccezionale [kN o kN/m²].
    Q : list[float]
        Valori caratteristici delle azioni variabili [kN o kN/m²].
    categories : list[str]
        Categorie corrispondenti a ciascuna Q.
    P : float
        Precompressione [kN o kN/m²]. Default 0.

    Returns
    -------
    float
        Valore della combinazione eccezionale.
    """
    psi_list = _validate_Q_categories(Q, categories)

    result = G1 + G2 + P + A_d
    for i in range(len(Q)):
        psi_2i = psi_list[i][2]
        result += psi_2i * Q[i]

    return result


# ── [2.5.7] — Masse sismiche ────────────────────────────────────────────────

@ntc_ref(article="2.5.3", formula="2.5.7")
def seismic_masses(
    G1: float,
    G2: float,
    Q: list[float],
    categories: list[str],
) -> float:
    """Masse associate ai carichi gravitazionali per azione sismica.

    NTC18 §2.5.3, Formula [2.5.7]:
        G_1 + G_2 + Σ(ψ_2i·Q_ki)

    Parameters
    ----------
    G1 : float
        Carichi permanenti strutturali [kN o kN/m²].
    G2 : float
        Carichi permanenti non strutturali [kN o kN/m²].
    Q : list[float]
        Valori caratteristici delle azioni variabili [kN o kN/m²].
    categories : list[str]
        Categorie corrispondenti a ciascuna Q.

    Returns
    -------
    float
        Massa associata ai carichi gravitazionali [kN o kN/m²].
    """
    psi_list = _validate_Q_categories(Q, categories)

    result = G1 + G2
    for i in range(len(Q)):
        psi_2i = psi_list[i][2]
        result += psi_2i * Q[i]

    return result
