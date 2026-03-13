"""Progettazione geotecnica — NTC18 Cap.6.

Coefficienti parziali, fattori di correlazione e verifiche per fondazioni
superficiali, fondazioni su pali, opere di sostegno, tiranti di ancoraggio
e opere di materiali sciolti.
"""

from __future__ import annotations

import numpy as np

from pyntc.core.reference import ntc_ref


# ============================================================================
# Tabelle coefficienti parziali per le azioni (Tab. 6.2.1)
# ============================================================================
_ACTION_FACTORS: dict[tuple[str, str, str], float] = {
    # (load_type, effect, combination) -> gamma
    # G1
    ("G1", "favorable", "EQU"): 0.9,
    ("G1", "unfavorable", "EQU"): 1.1,
    ("G1", "favorable", "A1"): 1.0,
    ("G1", "unfavorable", "A1"): 1.3,
    ("G1", "favorable", "A2"): 1.0,
    ("G1", "unfavorable", "A2"): 1.0,
    # G2
    ("G2", "favorable", "EQU"): 0.8,
    ("G2", "unfavorable", "EQU"): 1.5,
    ("G2", "favorable", "A1"): 0.8,
    ("G2", "unfavorable", "A1"): 1.5,
    ("G2", "favorable", "A2"): 0.8,
    ("G2", "unfavorable", "A2"): 1.3,
    # Q
    ("Q", "favorable", "EQU"): 0.0,
    ("Q", "unfavorable", "EQU"): 1.5,
    ("Q", "favorable", "A1"): 0.0,
    ("Q", "unfavorable", "A1"): 1.5,
    ("Q", "favorable", "A2"): 0.0,
    ("Q", "unfavorable", "A2"): 1.3,
}

# ============================================================================
# Tabella coefficienti parziali parametri geotecnici (Tab. 6.2.II)
# ============================================================================
_MATERIAL_FACTORS: dict[tuple[str, str], float] = {
    ("tan_phi", "M1"): 1.0,
    ("tan_phi", "M2"): 1.25,
    ("cohesion", "M1"): 1.0,
    ("cohesion", "M2"): 1.25,
    ("undrained", "M1"): 1.0,
    ("undrained", "M2"): 1.4,
    ("unit_weight", "M1"): 1.0,
    ("unit_weight", "M2"): 1.0,
}

# ============================================================================
# Tabella coefficienti parziali sollevamento UPL (Tab. 6.2.III)
# ============================================================================
_UPLIFT_FACTORS: dict[tuple[str, str], float] = {
    ("G1", "favorable"): 0.9,
    ("G1", "unfavorable"): 1.1,
    ("G2", "favorable"): 0.8,
    ("G2", "unfavorable"): 1.5,
    ("Q", "favorable"): 0.0,
    ("Q", "unfavorable"): 1.5,
}

# ============================================================================
# Tabella pali — R3 (Tab. 6.4.II)
# ============================================================================
_PILE_FACTORS: dict[tuple[str, str], float] = {
    # (resistance_type, pile_type) -> gamma_R
    ("base", "driven"): 1.15,
    ("base", "bored"): 1.35,
    ("base", "cfa"): 1.3,
    ("shaft", "driven"): 1.15,
    ("shaft", "bored"): 1.15,
    ("shaft", "cfa"): 1.15,
    ("total", "driven"): 1.15,
    ("total", "bored"): 1.30,
    ("total", "cfa"): 1.25,
    ("shaft_tension", "driven"): 1.25,
    ("shaft_tension", "bored"): 1.25,
    ("shaft_tension", "cfa"): 1.25,
}

# ============================================================================
# Tabella fattori correlazione prove statiche (Tab. 6.4.III)
# ============================================================================
_PILE_XI_STATIC: dict[int, tuple[float, float]] = {
    1: (1.40, 1.40),
    2: (1.30, 1.20),
    3: (1.20, 1.05),
    4: (1.10, 1.00),
}
# n >= 5 => (1.0, 1.0)

# ============================================================================
# Tabella fattori correlazione verticali indagine (Tab. 6.4.IV)
# ============================================================================
_PILE_XI_PROFILES: dict[int, tuple[float, float]] = {
    1: (1.70, 1.70),
    2: (1.65, 1.55),
    3: (1.60, 1.48),
    4: (1.55, 1.42),
    5: (1.50, 1.34),
    7: (1.45, 1.28),
    10: (1.40, 1.21),
}

# ============================================================================
# Tabella fattori correlazione prove dinamiche (Tab. 6.4.V)
# ============================================================================
_PILE_XI_DYNAMIC: list[tuple[int, float, float]] = [
    # (min_n, xi5, xi6) — in ordine decrescente di soglia
    (20, 1.40, 1.25),
    (15, 1.42, 1.25),
    (10, 1.45, 1.30),
    (5, 1.50, 1.35),
    (2, 1.60, 1.50),
]

# ============================================================================
# Tabella ancoraggi — correlazione prove (Tab. 6.6.II)
# ============================================================================
_ANCHOR_XI_TESTS: dict[int, tuple[float, float]] = {
    1: (1.5, 1.5),
    2: (1.4, 1.3),
}
# n > 2 => (1.3, 1.2)

# ============================================================================
# Tabella ancoraggi — correlazione profili (Tab. 6.6.III)
# ============================================================================
_ANCHOR_XI_PROFILES: dict[int, tuple[float, float]] = {
    1: (1.80, 1.80),
    2: (1.75, 1.70),
    3: (1.70, 1.65),
    4: (1.65, 1.60),
}
# n >= 5 => (1.60, 1.55)


# ============================================================================
# Funzioni
# ============================================================================


@ntc_ref(article="6.2.4.1.1", table="Tab.6.2.1", latex=r"\text{Tab.\,6.2.I}")
def geo_action_partial_factors(
    load_type: str,
    effect: str,
    combination: str,
) -> float:
    """Coefficiente parziale per le azioni geotecniche [-].

    NTC18 §6.2.4.1.1 — Tab. 6.2.1.

    Parameters
    ----------
    load_type : str
        Tipo di carico: ``"G1"`` (permanenti strutturali),
        ``"G2"`` (permanenti non strutturali), ``"Q"`` (variabili).
    effect : str
        ``"favorable"`` o ``"unfavorable"``.
    combination : str
        Combinazione di coefficienti: ``"EQU"``, ``"A1"`` o ``"A2"``.

    Returns
    -------
    float
        Coefficiente parziale gamma_F [-].
    """
    key = (load_type, effect, combination)
    if key not in _ACTION_FACTORS:
        valid_loads = {"G1", "G2", "Q"}
        valid_effects = {"favorable", "unfavorable"}
        valid_combs = {"EQU", "A1", "A2"}
        if load_type not in valid_loads:
            raise ValueError(
                f"Tipo di carico non valido: {load_type!r}. "
                f"Valori ammessi: {valid_loads}"
            )
        if effect not in valid_effects:
            raise ValueError(
                f"Effetto non valido: {effect!r}. Valori ammessi: {valid_effects}"
            )
        if combination not in valid_combs:
            raise ValueError(
                f"Combinazione non valida: {combination!r}. "
                f"Valori ammessi: {valid_combs}"
            )
        raise ValueError(f"Combinazione non trovata: {key}")  # pragma: no cover
    return _ACTION_FACTORS[key]


@ntc_ref(article="6.2.4.1.2", table="Tab.6.2.II", latex=r"\text{Tab.\,6.2.II}")
def geo_material_partial_factors(parameter: str, group: str) -> float:
    """Coefficiente parziale per i parametri geotecnici del terreno [-].

    NTC18 §6.2.4.1.2 — Tab. 6.2.II.

    Parameters
    ----------
    parameter : str
        Parametro geotecnico: ``"tan_phi"`` (angolo di resistenza al taglio),
        ``"cohesion"`` (coesione efficace c'), ``"undrained"`` (resistenza
        non drenata c_u), ``"unit_weight"`` (peso dell'unita' di volume).
    group : str
        Gruppo di coefficienti: ``"M1"`` o ``"M2"``.

    Returns
    -------
    float
        Coefficiente parziale gamma_M [-].
    """
    key = (parameter, group)
    if key not in _MATERIAL_FACTORS:
        valid_params = {"tan_phi", "cohesion", "undrained", "unit_weight"}
        valid_groups = {"M1", "M2"}
        if parameter not in valid_params:
            raise ValueError(
                f"Parametro non valido: {parameter!r}. "
                f"Valori ammessi: {valid_params}"
            )
        if group not in valid_groups:
            raise ValueError(
                f"Gruppo non valido: {group!r}. Valori ammessi: {valid_groups}"
            )
        raise ValueError(f"Combinazione non trovata: {key}")  # pragma: no cover
    return _MATERIAL_FACTORS[key]


@ntc_ref(article="6.2.4.2", table="Tab.6.2.III", latex=r"\text{Tab.\,6.2.III}")
def geo_uplift_partial_factors(load_type: str, effect: str) -> float:
    """Coefficiente parziale per verifiche al sollevamento (UPL) [-].

    NTC18 §6.2.4.2 — Tab. 6.2.III.

    Parameters
    ----------
    load_type : str
        Tipo di carico: ``"G1"``, ``"G2"``, ``"Q"``.
    effect : str
        ``"favorable"`` o ``"unfavorable"``.

    Returns
    -------
    float
        Coefficiente parziale gamma_F [-].
    """
    key = (load_type, effect)
    if key not in _UPLIFT_FACTORS:
        valid_loads = {"G1", "G2", "Q"}
        valid_effects = {"favorable", "unfavorable"}
        if load_type not in valid_loads:
            raise ValueError(
                f"Tipo di carico non valido: {load_type!r}. "
                f"Valori ammessi: {valid_loads}"
            )
        if effect not in valid_effects:
            raise ValueError(
                f"Effetto non valido: {effect!r}. Valori ammessi: {valid_effects}"
            )
        raise ValueError(f"Combinazione non trovata: {key}")  # pragma: no cover
    return _UPLIFT_FACTORS[key]


@ntc_ref(article="6.2.4.2", formula="6.2.4", latex=r"V_{\mathrm{inst},d} \le G_{\mathrm{stb},d} + R_d")
def geo_uplift_check(
    V_inst_d: float,
    G_stb_d: float,
    R_d: float,
) -> tuple[bool, float]:
    """Verifica al sollevamento [6.2.4].

    NTC18 §6.2.4.2 — V_inst,d <= G_stb,d + R_d.

    Parameters
    ----------
    V_inst_d : float
        Valore di progetto dell'azione instabilizzante [kN].
    G_stb_d : float
        Valore di progetto dell'azione stabilizzante [kN].
    R_d : float
        Valore di progetto della resistenza [kN].

    Returns
    -------
    tuple[bool, float]
        (verificato, rapporto V_inst_d / (G_stb_d + R_d)).
    """
    if V_inst_d < 0 or G_stb_d < 0 or R_d < 0:
        raise ValueError("I valori non possono essere negativi.")
    stb = G_stb_d + R_d
    if stb == 0:
        raise ValueError("La somma G_stb_d + R_d non puo' essere zero.")
    ratio = V_inst_d / stb
    return ratio <= 1.0, ratio


@ntc_ref(article="6.2.4.2", latex=r"i \le \frac{i_c}{\gamma_R}")
def geo_sifonamento_check(
    value: float,
    critical: float,
    check_type: str,
) -> tuple[bool, float]:
    """Verifica al sifonamento.

    NTC18 §6.2.4.2.

    Parameters
    ----------
    value : float
        Gradiente idraulico i (per ``"mean"`` e ``"outflow"``) oppure
        pressione interstiziale in eccesso delta_u [kPa] (per
        ``"excess_pressure"``).
    critical : float
        Gradiente idraulico critico i_c (per ``"mean"`` e ``"outflow"``)
        oppure tensione verticale efficace sigma'_v [kPa] (per
        ``"excess_pressure"``).
    check_type : str
        ``"mean"`` (gradiente medio, gamma_R=3),
        ``"outflow"`` (gradiente di efflusso, gamma_R=2),
        ``"excess_pressure"`` (pressione in eccesso, gamma_R=2).

    Returns
    -------
    tuple[bool, float]
        (verificato, rapporto value / limite).
    """
    if check_type == "mean":
        limit = critical / 3.0
    elif check_type == "outflow":
        limit = critical / 2.0
    elif check_type == "excess_pressure":
        limit = critical / 2.0
    else:
        raise ValueError(
            f"Tipo di verifica non valido: {check_type!r}. "
            f"Valori ammessi: 'mean', 'outflow', 'excess_pressure'"
        )
    ratio = value / limit
    return ratio <= 1.0, ratio


@ntc_ref(article="6.2.4.1.2", formula="6.2.3", latex=r"R_d = \frac{R_k}{\gamma_R}")
def geo_design_resistance(R_k: float, gamma_R: float) -> float:
    """Resistenza di progetto geotecnica [kN].

    NTC18 §6.2.4.1.2 — R_d = R_k / gamma_R [6.2.3].

    Parameters
    ----------
    R_k : float
        Resistenza caratteristica [kN].
    gamma_R : float
        Coefficiente parziale sulla resistenza [-].

    Returns
    -------
    float
        Resistenza di progetto R_d [kN].
    """
    if R_k < 0:
        raise ValueError(f"R_k non puo' essere negativa: {R_k}")
    if gamma_R <= 0:
        raise ValueError(f"gamma_R deve essere positivo: {gamma_R}")
    return R_k / gamma_R


@ntc_ref(article="6.2.4.1", formula="6.2.1", latex=r"E_d \le R_d")
def geo_design_check(E_d: float, R_d: float) -> tuple[bool, float]:
    """Verifica geotecnica E_d <= R_d [6.2.1].

    NTC18 §6.2.4.1.

    Parameters
    ----------
    E_d : float
        Valore di progetto dell'effetto delle azioni [kN].
    R_d : float
        Valore di progetto della resistenza [kN].

    Returns
    -------
    tuple[bool, float]
        (verificato, rapporto E_d / R_d).
    """
    if R_d <= 0:
        raise ValueError(f"R_d deve essere positivo: {R_d}")
    ratio = E_d / R_d
    return ratio <= 1.0, ratio


@ntc_ref(article="6.4.2.1", table="Tab.6.4.1", latex=r"\text{Tab.\,6.4.I}")
def geo_shallow_foundation_factors(verification: str) -> float:
    """Coefficiente parziale R3 per fondazioni superficiali [-].

    NTC18 §6.4.2.1 — Tab. 6.4.1.

    Parameters
    ----------
    verification : str
        Tipo di verifica: ``"bearing"`` (carico limite) o
        ``"sliding"`` (scorrimento).

    Returns
    -------
    float
        Coefficiente parziale gamma_R [-].
    """
    factors = {"bearing": 2.3, "sliding": 1.1}
    if verification not in factors:
        raise ValueError(
            f"Tipo di verifica non valido: {verification!r}. "
            f"Valori ammessi: {set(factors.keys())}"
        )
    return factors[verification]


@ntc_ref(article="6.4.3.1.1", table="Tab.6.4.II", latex=r"\text{Tab.\,6.4.II}")
def geo_pile_resistance_factors(resistance: str, pile_type: str) -> float:
    """Coefficiente parziale R3 per resistenza assiale dei pali [-].

    NTC18 §6.4.3.1.1 — Tab. 6.4.II.

    Parameters
    ----------
    resistance : str
        Tipo di resistenza: ``"base"``, ``"shaft"`` (laterale compressione),
        ``"total"``, ``"shaft_tension"`` (laterale trazione).
    pile_type : str
        Tipo di palo: ``"driven"`` (infissi), ``"bored"`` (trivellati),
        ``"cfa"`` (ad elica continua).

    Returns
    -------
    float
        Coefficiente parziale gamma_R [-].
    """
    key = (resistance, pile_type)
    if key not in _PILE_FACTORS:
        valid_res = {"base", "shaft", "total", "shaft_tension"}
        valid_types = {"driven", "bored", "cfa"}
        if resistance not in valid_res:
            raise ValueError(
                f"Tipo di resistenza non valido: {resistance!r}. "
                f"Valori ammessi: {valid_res}"
            )
        if pile_type not in valid_types:
            raise ValueError(
                f"Tipo di palo non valido: {pile_type!r}. "
                f"Valori ammessi: {valid_types}"
            )
        raise ValueError(f"Combinazione non trovata: {key}")  # pragma: no cover
    return _PILE_FACTORS[key]


@ntc_ref(article="6.4.3.1.1", table="Tab.6.4.III", latex=r"\text{Tab.\,6.4.III} \;\to\; (\xi_1,\,\xi_2)")
def geo_pile_correlation_static(n_tests: int) -> tuple[float, float]:
    """Fattori di correlazione xi per prove di carico statiche su pali.

    NTC18 §6.4.3.1.1 — Tab. 6.4.III.

    Parameters
    ----------
    n_tests : int
        Numero di prove di carico statiche su pali pilota.

    Returns
    -------
    tuple[float, float]
        (xi_1, xi_2).
    """
    if n_tests < 1:
        raise ValueError(f"Numero di prove deve essere >= 1: {n_tests}")
    if n_tests >= 5:
        return (1.0, 1.0)
    return _PILE_XI_STATIC[n_tests]


def _interpolate_pile_profiles(
    n: int,
    table: dict[int, tuple[float, float]],
) -> tuple[float, float]:
    """Interpola linearmente tra i valori tabellati per verticali indagine."""
    keys = sorted(table.keys())
    if n >= keys[-1]:
        return table[keys[-1]]
    if n <= keys[0]:
        return table[keys[0]]
    if n in table:
        return table[n]
    # Interpolazione lineare
    for i in range(len(keys) - 1):
        if keys[i] < n < keys[i + 1]:
            n_lo, n_hi = keys[i], keys[i + 1]
            xi_lo = table[n_lo]
            xi_hi = table[n_hi]
            t = (n - n_lo) / (n_hi - n_lo)
            return (
                xi_lo[0] + t * (xi_hi[0] - xi_lo[0]),
                xi_lo[1] + t * (xi_hi[1] - xi_lo[1]),
            )
    return table[keys[-1]]  # pragma: no cover


@ntc_ref(article="6.4.3.1.1", table="Tab.6.4.IV", latex=r"\text{Tab.\,6.4.IV} \;\to\; (\xi_3,\,\xi_4)")
def geo_pile_correlation_profiles(n_profiles: int) -> tuple[float, float]:
    """Fattori di correlazione xi per verticali di indagine su pali.

    NTC18 §6.4.3.1.1 — Tab. 6.4.IV.

    Parameters
    ----------
    n_profiles : int
        Numero di verticali di indagine.

    Returns
    -------
    tuple[float, float]
        (xi_3, xi_4).
    """
    if n_profiles < 1:
        raise ValueError(
            f"Numero di verticali di indagine deve essere >= 1: {n_profiles}"
        )
    return _interpolate_pile_profiles(n_profiles, _PILE_XI_PROFILES)


@ntc_ref(article="6.4.3.1.1", table="Tab.6.4.V", latex=r"\text{Tab.\,6.4.V} \;\to\; (\xi_5,\,\xi_6)")
def geo_pile_correlation_dynamic(n_tests: int) -> tuple[float, float]:
    """Fattori di correlazione xi per prove dinamiche su pali.

    NTC18 §6.4.3.1.1 — Tab. 6.4.V.

    Parameters
    ----------
    n_tests : int
        Numero di prove dinamiche ad alto livello di deformazione.

    Returns
    -------
    tuple[float, float]
        (xi_5, xi_6).
    """
    if n_tests < 2:
        raise ValueError(
            f"Numero di prove dinamiche deve essere >= 2: {n_tests}"
        )
    for min_n, xi5, xi6 in _PILE_XI_DYNAMIC:
        if n_tests >= min_n:
            return (xi5, xi6)
    return _PILE_XI_DYNAMIC[-1][1:]  # pragma: no cover


@ntc_ref(article="6.4.3.1.1", formula="6.4.1", latex=r"R_{c,k} = \min\!\left(\frac{R_{c,\mathrm{medio}}}{\xi_1},\;\frac{R_{c,\min}}{\xi_2}\right)")
def geo_pile_characteristic_resistance(
    R_values: list[float],
    method: str,
) -> float:
    """Resistenza caratteristica del palo singolo [kN].

    NTC18 §6.4.3.1.1 — [6.4.1]-[6.4.5].

    Parameters
    ----------
    R_values : list[float]
        Valori delle resistenze misurate o calcolate [kN].
    method : str
        Metodo di determinazione: ``"static"`` (prove statiche, [6.4.1]),
        ``"profiles"`` (verticali di indagine, [6.4.3]),
        ``"dynamic"`` (prove dinamiche, [6.4.5]).

    Returns
    -------
    float
        Resistenza caratteristica R_c,k [kN].
    """
    if not R_values:
        raise ValueError("La lista delle resistenze non puo' essere vuota.")

    arr = np.asarray(R_values, dtype=float)
    n = len(arr)
    mean_val = float(np.mean(arr))
    min_val = float(np.min(arr))

    if method == "static":
        xi1, xi2 = geo_pile_correlation_static.__wrapped__(n)
        return min(mean_val / xi1, min_val / xi2)
    elif method == "profiles":
        xi3, xi4 = geo_pile_correlation_profiles.__wrapped__(n)
        return min(mean_val / xi3, min_val / xi4)
    elif method == "dynamic":
        xi5, xi6 = geo_pile_correlation_dynamic.__wrapped__(n)
        return min(mean_val / xi5, min_val / xi6)
    else:
        raise ValueError(
            f"Metodo non valido: {method!r}. "
            f"Valori ammessi: 'static', 'profiles', 'dynamic'"
        )


@ntc_ref(article="6.4.3.1.2", table="Tab.6.4.VI", latex=r"\gamma_T = 1{,}3")
def geo_pile_transverse_factor() -> float:
    """Coefficiente parziale R3 per pali soggetti a carichi trasversali [-].

    NTC18 §6.4.3.1.2 — Tab. 6.4.VI.

    Returns
    -------
    float
        Coefficiente parziale gamma_T = 1.3 [-].
    """
    return 1.3


@ntc_ref(article="6.5.3.1.1", table="Tab.6.5.1", latex=r"\text{Tab.\,6.5.I}")
def geo_retaining_wall_factors(verification: str) -> float:
    """Coefficiente parziale R3 per muri di sostegno [-].

    NTC18 §6.5.3.1.1 — Tab. 6.5.1.

    Parameters
    ----------
    verification : str
        Tipo di verifica: ``"bearing"`` (capacita' portante),
        ``"sliding"`` (scorrimento), ``"overturning"`` (ribaltamento),
        ``"passive"`` (resistenza del terreno a valle).

    Returns
    -------
    float
        Coefficiente parziale gamma_R [-].
    """
    factors = {
        "bearing": 1.4,
        "sliding": 1.1,
        "overturning": 1.15,
        "passive": 1.4,
    }
    if verification not in factors:
        raise ValueError(
            f"Tipo di verifica non valido: {verification!r}. "
            f"Valori ammessi: {set(factors.keys())}"
        )
    return factors[verification]


@ntc_ref(article="6.6.2", table="Tab.6.6.1", latex=r"\text{Tab.\,6.6.I}")
def geo_anchor_resistance_factors(anchor_type: str) -> float:
    """Coefficiente parziale per la resistenza degli ancoraggi [-].

    NTC18 §6.6.2 — Tab. 6.6.1.

    Parameters
    ----------
    anchor_type : str
        Tipo di ancoraggio: ``"temporary"`` o ``"permanent"``.

    Returns
    -------
    float
        Coefficiente parziale gamma_R [-].
    """
    factors = {"temporary": 1.1, "permanent": 1.2}
    if anchor_type not in factors:
        raise ValueError(
            f"Tipo di ancoraggio non valido: {anchor_type!r}. "
            f"Valori ammessi: {set(factors.keys())}"
        )
    return factors[anchor_type]


@ntc_ref(article="6.6.2", table="Tab.6.6.II", latex=r"\text{Tab.\,6.6.II} \;\to\; (\xi_{a1},\,\xi_{a2})")
def geo_anchor_correlation_tests(n_tests: int) -> tuple[float, float]:
    """Fattori di correlazione xi per prove di progetto su ancoraggi.

    NTC18 §6.6.2 — Tab. 6.6.II.

    Parameters
    ----------
    n_tests : int
        Numero di ancoraggi di prova.

    Returns
    -------
    tuple[float, float]
        (xi_a1, xi_a2).
    """
    if n_tests < 1:
        raise ValueError(f"Numero di prove deve essere >= 1: {n_tests}")
    if n_tests > 2:
        return (1.3, 1.2)
    return _ANCHOR_XI_TESTS[n_tests]


@ntc_ref(article="6.6.2", table="Tab.6.6.III", latex=r"\text{Tab.\,6.6.III} \;\to\; (\xi_{a3},\,\xi_{a4})")
def geo_anchor_correlation_profiles(n_profiles: int) -> tuple[float, float]:
    """Fattori di correlazione xi per profili di indagine per ancoraggi.

    NTC18 §6.6.2 — Tab. 6.6.III.

    Parameters
    ----------
    n_profiles : int
        Numero di profili di indagine.

    Returns
    -------
    tuple[float, float]
        (xi_a3, xi_a4).
    """
    if n_profiles < 1:
        raise ValueError(
            f"Numero di profili deve essere >= 1: {n_profiles}"
        )
    if n_profiles >= 5:
        return (1.60, 1.55)
    return _ANCHOR_XI_PROFILES[n_profiles]


@ntc_ref(article="6.6.2", formula="6.6.1", latex=r"R_{a,k} = \min\!\left(\frac{R_{a,\mathrm{medio}}}{\xi_{a1}},\;\frac{R_{a,\min}}{\xi_{a2}}\right)")
def geo_anchor_characteristic_resistance(
    R_values: list[float],
    method: str,
) -> float:
    """Resistenza caratteristica di un ancoraggio [kN].

    NTC18 §6.6.2 — [6.6.1]/[6.6.2].

    Parameters
    ----------
    R_values : list[float]
        Valori delle resistenze misurate o calcolate [kN].
    method : str
        Metodo: ``"tests"`` (prove di progetto, [6.6.1]) o
        ``"profiles"`` (profili di indagine, [6.6.2]).

    Returns
    -------
    float
        Resistenza caratteristica R_a,k [kN].
    """
    if not R_values:
        raise ValueError("La lista delle resistenze non puo' essere vuota.")

    arr = np.asarray(R_values, dtype=float)
    n = len(arr)
    mean_val = float(np.mean(arr))
    min_val = float(np.min(arr))

    if method == "tests":
        xi1, xi2 = geo_anchor_correlation_tests.__wrapped__(n)
        return min(mean_val / xi1, min_val / xi2)
    elif method == "profiles":
        xi3, xi4 = geo_anchor_correlation_profiles.__wrapped__(n)
        return min(mean_val / xi3, min_val / xi4)
    else:
        raise ValueError(
            f"Metodo non valido: {method!r}. "
            f"Valori ammessi: 'tests', 'profiles'"
        )


@ntc_ref(
    article="6.2.4.2",
    formula="6.2.5",
    latex=r"V_{\mathrm{inst},d} = C_{\mathrm{inst},d} + Q_{\mathrm{inst},d}",
)
def geo_destabilising_force(C_inst_d: float, Q_inst_d: float) -> float:
    """Forza instabilizzante di progetto per verifiche idrauliche [kN].

    NTC18 §6.2.4.2 — Formula [6.2.5]:

    .. math::
        V_{\\mathrm{inst},d} = C_{\\mathrm{inst},d} + Q_{\\mathrm{inst},d}

    Parameters
    ----------
    C_inst_d : float
        Componente permanente instabilizzante di progetto [kN].
    Q_inst_d : float
        Componente variabile instabilizzante di progetto [kN].

    Returns
    -------
    float
        Forza instabilizzante totale V_inst,d [kN].

    Raises
    ------
    ValueError
        Se uno dei parametri è negativo.
    """
    if C_inst_d < 0:
        raise ValueError(f"C_inst_d non puo' essere negativa: {C_inst_d}")
    if Q_inst_d < 0:
        raise ValueError(f"Q_inst_d non puo' essere negativa: {Q_inst_d}")
    return C_inst_d + Q_inst_d


@ntc_ref(article="6.4.2", latex=r"s = q B (1-\nu^2) I_s / E_s")
def geo_settlement_elastic(
    q: float,
    B: float,
    E_s: float,
    nu: float = 0.3,
    I_s: float = 0.8,
) -> float:
    """Cedimento elastico di fondazione superficiale [m].

    NTC18 §6.4.2 — Formula di Janbu/Schmertmann semplificata.

    Parameters
    ----------
    q : float
        Pressione di contatto [kPa].
    B : float
        Dimensione caratteristica della fondazione [m].
    E_s : float
        Modulo elastico del terreno [kPa].
    nu : float
        Coefficiente di Poisson (default 0.3).
    I_s : float
        Fattore di forma (default 0.8 per fondazione flessibile quadrata).

    Returns
    -------
    float
        Cedimento elastico s [m].
    """
    if q < 0:
        raise ValueError(f"q deve essere >= 0, ricevuto {q}")
    if B <= 0:
        raise ValueError(f"B deve essere > 0, ricevuto {B}")
    if E_s <= 0:
        raise ValueError(f"E_s deve essere > 0, ricevuto {E_s}")
    if not (0.0 <= nu < 0.5):
        raise ValueError(f"nu deve essere in [0, 0.5), ricevuto {nu}")
    return q * B * (1.0 - nu**2) / E_s * I_s


@ntc_ref(article="6.4.2", latex=r"s_c = m_v \Delta\sigma_v H")
def geo_consolidation_settlement(mv: float, sigma_v_inc: float, H: float) -> float:
    """Cedimento di consolidazione primaria [m].

    NTC18 §6.4.2 — s_c = mv * sigma_v_inc * H.

    Parameters
    ----------
    mv : float
        Coefficiente di compressibilita' volumetrica [1/kPa].
    sigma_v_inc : float
        Incremento di tensione verticale efficace [kPa].
    H : float
        Spessore dello strato compressibile [m].

    Returns
    -------
    float
        Cedimento di consolidazione s_c [m].
    """
    if mv <= 0:
        raise ValueError(f"mv deve essere > 0, ricevuto {mv}")
    if sigma_v_inc < 0:
        raise ValueError(f"sigma_v_inc deve essere >= 0, ricevuto {sigma_v_inc}")
    if H <= 0:
        raise ValueError(f"H deve essere > 0, ricevuto {H}")
    return mv * sigma_v_inc * H


@ntc_ref(article="6.4.2", latex=r"s \le s_{lim}")
def geo_settlement_check(s_calc: float, s_lim: float) -> tuple[bool, float]:
    """Verifica del cedimento calcolato rispetto al limite ammissibile.

    NTC18 §6.4.2 — s_calc <= s_lim.

    Parameters
    ----------
    s_calc : float
        Cedimento calcolato [m o mm].
    s_lim : float
        Cedimento limite ammissibile [m o mm].

    Returns
    -------
    tuple[bool, float]
        (verificato, ratio = s_calc / s_lim).
    """
    if s_calc < 0:
        raise ValueError(f"s_calc deve essere >= 0, ricevuto {s_calc}")
    if s_lim <= 0:
        raise ValueError(f"s_lim deve essere > 0, ricevuto {s_lim}")
    ratio = s_calc / s_lim
    return ratio <= 1.0, ratio


@ntc_ref(article="6.8.2", table="Tab.6.8.1", latex=r"\gamma_R = 1{,}1")
def geo_embankment_resistance_factor() -> float:
    """Coefficiente parziale R2 per opere di materiali sciolti e fronti di scavo [-].

    NTC18 §6.8.2 — Tab. 6.8.1.

    Returns
    -------
    float
        Coefficiente parziale gamma_R = 1.1 [-].
    """
    return 1.1


# ============================================================================
# Fondazioni superficiali — capacità portante (§6.4.1)
# ============================================================================


@ntc_ref(article="6.4.1", latex=r"N_q = e^{\pi\tan\phi}\tan^2(45+\phi/2)")
def geo_bearing_capacity_factors(phi_k: float) -> dict[str, float]:
    """Fattori di portanza N_c, N_q, N_γ secondo Brinch-Hansen.

    NTC18 §6.4.1.

    Parameters
    ----------
    phi_k : float
        Angolo di attrito caratteristico [gradi].

    Returns
    -------
    dict[str, float]
        Dizionario con chiavi ``"N_c"``, ``"N_q"``, ``"N_gamma"``.
    """
    if phi_k < 0:
        raise ValueError(f"phi_k deve essere >= 0: {phi_k}")
    if phi_k >= 90:
        raise ValueError(f"phi_k deve essere < 90: {phi_k}")

    phi_rad = np.radians(phi_k)

    if phi_k == 0.0:
        N_q = 1.0
        N_c = np.pi + 2.0  # = 5.14159...
        N_gamma = 0.0
    else:
        N_q = np.exp(np.pi * np.tan(phi_rad)) * np.tan(np.pi / 4.0 + phi_rad / 2.0) ** 2
        N_c = (N_q - 1.0) / np.tan(phi_rad)
        N_gamma = 2.0 * (N_q + 1.0) * np.tan(phi_rad)

    return {"N_c": float(N_c), "N_q": float(N_q), "N_gamma": float(N_gamma)}


@ntc_ref(article="6.4.1", latex=r"q_{lim} = c N_c + q N_q + 0.5\,\gamma B N_\gamma")
def geo_shallow_bearing_capacity(
    c_k: float,
    phi_k: float,
    gamma: float,
    B: float,
    L: float,
    D: float,
    q_surcharge: float = 0.0,
) -> float:
    """Resistenza caratteristica di una fondazione superficiale [kPa].

    NTC18 §6.4.1 — Formula di Brinch-Hansen semplificata (senza fattori di
    inclinazione/forma).

    Parameters
    ----------
    c_k : float
        Coesione caratteristica del terreno [kPa].
    phi_k : float
        Angolo di attrito caratteristico [gradi].
    gamma : float
        Peso specifico del terreno [kN/m³].
    B : float
        Larghezza della fondazione [m].
    L : float
        Lunghezza della fondazione [m] (riservato per estensioni future).
    D : float
        Profondità del piano di posa [m].
    q_surcharge : float, optional
        Sovraccarico aggiuntivo in superficie [kPa], default 0.0.

    Returns
    -------
    float
        Carico limite unitario q_lim [kPa].
    """
    if c_k < 0:
        raise ValueError(f"c_k deve essere >= 0: {c_k}")
    if gamma <= 0:
        raise ValueError(f"gamma deve essere > 0: {gamma}")
    if B <= 0:
        raise ValueError(f"B deve essere > 0: {B}")
    if D < 0:
        raise ValueError(f"D deve essere >= 0: {D}")

    factors = geo_bearing_capacity_factors.__wrapped__(phi_k)
    N_c = factors["N_c"]
    N_q = factors["N_q"]
    N_gamma = factors["N_gamma"]

    q = gamma * D + q_surcharge
    q_lim = c_k * N_c + q * N_q + 0.5 * gamma * B * N_gamma
    return float(q_lim)


@ntc_ref(article="6.4.1", formula="6.2.1", latex=r"q_{Ed} \le q_{lim}/\gamma_R")
def geo_shallow_foundation_check(
    N_Ed: float,
    A: float,
    q_lim: float,
    gamma_R: float = 1.0,
) -> tuple[bool, float]:
    """Verifica portanza fondazione superficiale — NTC18 §6.4.1.

    Parameters
    ----------
    N_Ed : float
        Carico verticale di progetto [kN].
    A : float
        Area della fondazione [m²].
    q_lim : float
        Carico limite unitario caratteristico [kPa].
    gamma_R : float, optional
        Coefficiente parziale sulla resistenza [-], default 1.0.

    Returns
    -------
    tuple[bool, float]
        (verificato, rapporto q_Ed / R_d).
    """
    if A <= 0:
        raise ValueError(f"A deve essere > 0: {A}")
    if q_lim <= 0:
        raise ValueError(f"q_lim deve essere > 0: {q_lim}")
    if gamma_R <= 0:
        raise ValueError(f"gamma_R deve essere > 0: {gamma_R}")

    q_Ed = N_Ed / A
    R_d = q_lim / gamma_R
    ratio = q_Ed / R_d
    return ratio <= 1.0, float(ratio)


# ============================================================================
# Pali — resistenza laterale, di punta e totale (§6.4.3)
# ============================================================================


@ntc_ref(article="6.4.3.1", latex=r"R_{s,k} = \alpha\,c_u\,U\,L")
def geo_pile_skin_friction(
    c_u: float,
    alpha: float,
    perimeter: float,
    length: float,
) -> float:
    """Resistenza laterale caratteristica di un palo in argilla — metodo α.

    NTC18 §6.4.3.1.

    Parameters
    ----------
    c_u : float
        Resistenza al taglio non drenata [kPa].
    alpha : float
        Fattore di adesione [-] (tipico 0.5–1.0).
    perimeter : float
        Perimetro della sezione del palo [m].
    length : float
        Lunghezza del palo [m].

    Returns
    -------
    float
        Resistenza laterale caratteristica R_s,k [kN].
    """
    if c_u < 0:
        raise ValueError(f"c_u deve essere >= 0: {c_u}")
    if alpha <= 0:
        raise ValueError(f"alpha deve essere > 0: {alpha}")
    if perimeter <= 0:
        raise ValueError(f"perimeter deve essere > 0: {perimeter}")
    if length <= 0:
        raise ValueError(f"length deve essere > 0: {length}")

    return float(alpha * c_u * perimeter * length)


@ntc_ref(article="6.4.3.1", latex=r"R_{b,k} = q_b \cdot A_b")
def geo_pile_base_resistance(q_b: float, A_b: float) -> float:
    """Resistenza di punta caratteristica di un palo.

    NTC18 §6.4.3.1.

    Parameters
    ----------
    q_b : float
        Resistenza unitaria di punta [kPa].
    A_b : float
        Area della sezione di punta del palo [m²].

    Returns
    -------
    float
        Resistenza di punta caratteristica R_b,k [kN].
    """
    if q_b < 0:
        raise ValueError(f"q_b deve essere >= 0: {q_b}")
    if A_b <= 0:
        raise ValueError(f"A_b deve essere > 0: {A_b}")

    return float(q_b * A_b)


@ntc_ref(article="6.4.3.1.1", formula="6.4.2", latex=r"R_{c,d} = R_{c,k} / \gamma_t")
def geo_pile_total_resistance(
    R_s_k: float,
    R_b_k: float,
    xi: float,
    gamma_t: float = 1.15,
) -> float:
    """Resistenza totale di progetto di un palo [kN].

    NTC18 §6.4.3.1.1 — R_c,d = (R_s,k + R_b,k) / (xi * gamma_t).

    Parameters
    ----------
    R_s_k : float
        Resistenza laterale caratteristica [kN].
    R_b_k : float
        Resistenza di punta caratteristica [kN].
    xi : float
        Fattore di correlazione xi [-].
    gamma_t : float, optional
        Coefficiente parziale gamma_t [-], default 1.15.

    Returns
    -------
    float
        Resistenza totale di progetto R_c,d [kN].
    """
    if R_s_k < 0:
        raise ValueError(f"R_s_k deve essere >= 0: {R_s_k}")
    if R_b_k < 0:
        raise ValueError(f"R_b_k deve essere >= 0: {R_b_k}")
    if xi <= 0:
        raise ValueError(f"xi deve essere > 0: {xi}")
    if gamma_t <= 0:
        raise ValueError(f"gamma_t deve essere > 0: {gamma_t}")

    R_c_k = R_s_k + R_b_k
    return float(R_c_k / (xi * gamma_t))


@ntc_ref(article="6.4.3.1", latex=r"N_{Ed} \le R_{c,d}")
def geo_pile_check(N_Ed: float, R_c_d: float) -> tuple[bool, float]:
    """Verifica portanza assiale di un palo — NTC18 §6.4.3.1.

    Parameters
    ----------
    N_Ed : float
        Carico assiale di progetto [kN].
    R_c_d : float
        Resistenza totale di progetto del palo [kN].

    Returns
    -------
    tuple[bool, float]
        (verificato, rapporto N_Ed / R_c,d).
    """
    if R_c_d <= 0:
        raise ValueError(f"R_c_d deve essere > 0: {R_c_d}")

    ratio = N_Ed / R_c_d
    return ratio <= 1.0, float(ratio)
# §6.5.3.1.1 / §6.6 — MURI DI SOSTEGNO E ANCORAGGI
# ══════════════════════════════════════════════════════════════════════════

# ============================================================================
# Tabella Tab. 6.6.III — fattori di correlazione ancoraggi (ζ_as, ζ_at)
# ============================================================================
_ANCHOR_ZETA_PROFILES: dict[int, tuple[float, float]] = {
    1: (1.80, 1.80),
    2: (1.75, 1.70),
    3: (1.70, 1.65),
    4: (1.65, 1.60),
}
# n >= 5 => (1.60, 1.55)

# ============================================================================
# Tabella Tab. 6.5.1 — coefficienti R3 muri di sostegno
# ============================================================================
_RETAINING_WALL_FACTORS: dict[str, float] = {
    "bearing": 1.4,
    "sliding": 1.1,
    "overturning": 1.15,
    "passive": 1.4,
}


@ntc_ref(
    article="6.6.2",
    table="Tab.6.6.III",
    latex=r"\zeta_{as},\;\zeta_{at}",
)
def geo_anchor_correlation_factors(n_profiles: int) -> tuple[float, float]:
    """Fattori di correlazione ζ_as e ζ_at per ancoraggi (Tab. 6.6.III).

    NTC18 §6.6.2 — Tab. 6.6.III.

    Parameters
    ----------
    n_profiles : int
        Numero di profili di indagine. Per n_profiles >= 5 si usano i valori
        di n = 5.

    Returns
    -------
    tuple[float, float]
        (ζ_as, ζ_at).
    """
    if n_profiles < 1:
        raise ValueError(
            f"Il numero di profili deve essere >= 1: {n_profiles}"
        )
    if n_profiles >= 5:
        return (1.60, 1.55)
    return _ANCHOR_ZETA_PROFILES[n_profiles]




@ntc_ref(
    article="6.6.2",
    table="Tab.6.6.1",
    latex=r"\gamma_g",
)
def geo_anchor_partial_factor(anchor_type: str) -> float:
    """Coefficiente parziale γ_g per la resistenza degli ancoraggi [-].

    NTC18 §6.6.2 — Tab. 6.6.1.

    Parameters
    ----------
    anchor_type : str
        Tipo di ancoraggio: ``"temporary"`` (temporanei, γ_g = 1.1) o
        ``"permanent"`` (permanenti, γ_g = 1.2).

    Returns
    -------
    float
        Coefficiente parziale γ_g [-].
    """
    factors = {"temporary": 1.1, "permanent": 1.2}
    if anchor_type not in factors:
        raise ValueError(
            f"Tipo di ancoraggio non valido: {anchor_type!r}. "
            f"Valori ammessi: {set(factors.keys())}"
        )
    return factors[anchor_type]


@ntc_ref(
    article="6.6.2",
    formula="6.6.1",
    latex=r"R_{Ed} \le R_d = \frac{R_{a,k}}{\gamma_g}",
)
def geo_anchor_check(
    R_Ed: float,
    R_ak: float,
    gamma_g: float,
) -> tuple[bool, float]:
    """Verifica di un ancoraggio: R_Ed <= R_d = R_ak / γ_g.

    NTC18 §6.6.2.

    Parameters
    ----------
    R_Ed : float
        Valore di progetto dell'azione sull'ancoraggio [kN].
    R_ak : float
        Resistenza caratteristica dell'ancoraggio [kN].
    gamma_g : float
        Coefficiente parziale sulla resistenza [-].

    Returns
    -------
    tuple[bool, float]
        (verificato, rapporto R_Ed / R_d).
    """
    if R_ak <= 0:
        raise ValueError(f"R_ak deve essere positivo: {R_ak}")
    if gamma_g <= 0:
        raise ValueError(f"gamma_g deve essere positivo: {gamma_g}")
    R_d = R_ak / gamma_g
    ratio = R_Ed / R_d
    return ratio <= 1.0, ratio


@ntc_ref(
    article="6.5.3.1.1",
    table="Tab.6.5.1",
    latex=r"\gamma_n \;\text{(R3)}",
)
def geo_retaining_wall_resistance_factor(verification: str) -> float:
    """Coefficiente parziale R3 per muri di sostegno [-].

    NTC18 §6.5.3.1.1 — Tab. 6.5.1.

    Parameters
    ----------
    verification : str
        Tipo di verifica: ``"bearing"`` (capacita' portante della fondazione,
        1.4), ``"sliding"`` (scorrimento, 1.1), ``"overturning"``
        (ribaltamento, 1.15), ``"passive"`` (resistenza del terreno a valle,
        1.4).

    Returns
    -------
    float
        Coefficiente parziale γ_n [-].
    """
    if verification not in _RETAINING_WALL_FACTORS:
        raise ValueError(
            f"Tipo di verifica non valido: {verification!r}. "
            f"Valori ammessi: {set(_RETAINING_WALL_FACTORS.keys())}"
        )
    return _RETAINING_WALL_FACTORS[verification]

