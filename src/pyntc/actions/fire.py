"""Azioni eccezionali: incendio, esplosioni, urti — NTC18 §3.6.

Curve nominali di incendio (§3.6.1.5.1), carico d'incendio specifico
di progetto (§3.6.1.1), pressione equivalente esplosioni (§3.6.2.3),
forze statiche equivalenti urti veicoli (§3.6.3.3.1).
"""

from __future__ import annotations

import numpy as np

from pyntc.core.reference import ntc_ref


# ── Tab. 3.6.III — Forze statiche equivalenti urti veicoli [kN] ─────────────

_IMPACT_FORCES: dict[str, float] = {
    "highway":       1000.0,   # Autostrade, strade extraurbane
    "rural":          750.0,   # Strade locali
    "urban":          500.0,   # Strade urbane
    "parking_car":     50.0,   # Parcheggi — automobili
    "parking_truck":  150.0,   # Parcheggi — veicoli > 3.5 t
}


# ── [3.6.2] — Curva nominale standard ISO 834 ───────────────────────────────

@ntc_ref(article="3.6.1.5.1", formula="3.6.2",
         latex=r"\theta = 20 + 345 \log_{10}(8t + 1)")
def fire_standard_curve(t: float | np.ndarray) -> float | np.ndarray:
    """Curva nominale standard di incendio ISO 834 [°C].

    NTC18 §3.6.1.5.1, Formula [3.6.2]:
        theta = 20 + 345 * log10(8*t + 1)

    Parameters
    ----------
    t : float or np.ndarray
        Tempo di esposizione [min]. Deve essere >= 0.

    Returns
    -------
    float or np.ndarray
        Temperatura dei gas caldi [°C].

    Raises
    ------
    ValueError
        Se ``t`` < 0.
    """
    t_arr = np.asarray(t, dtype=float)
    scalar_input = t_arr.ndim == 0
    t_arr = np.atleast_1d(t_arr)

    if np.any(t_arr < 0):
        raise ValueError("Il tempo t non puo' essere negativo.")

    theta = 20.0 + 345.0 * np.log10(8.0 * t_arr + 1.0)

    if scalar_input:
        return float(theta[0])
    return theta


# ── [3.6.3] — Curva nominale idrocarburi ─────────────────────────────────────

@ntc_ref(article="3.6.1.5.1", formula="3.6.3",
         latex=r"\theta = 1080\,(1 - 0{,}325\,e^{-0{,}167\,t} - 0{,}675\,e^{-2{,}5\,t}) + 20")
def fire_hydrocarbon_curve(t: float | np.ndarray) -> float | np.ndarray:
    """Curva nominale di incendio per idrocarburi [°C].

    NTC18 §3.6.1.5.1, Formula [3.6.3]:
        theta = 1080 * (1 - 0.325*exp(-0.167*t) - 0.675*exp(-2.5*t)) + 20

    Parameters
    ----------
    t : float or np.ndarray
        Tempo di esposizione [min]. Deve essere >= 0.

    Returns
    -------
    float or np.ndarray
        Temperatura dei gas caldi [°C].

    Raises
    ------
    ValueError
        Se ``t`` < 0.
    """
    t_arr = np.asarray(t, dtype=float)
    scalar_input = t_arr.ndim == 0
    t_arr = np.atleast_1d(t_arr)

    if np.any(t_arr < 0):
        raise ValueError("Il tempo t non puo' essere negativo.")

    theta = 1080.0 * (1.0 - 0.325 * np.exp(-0.167 * t_arr)
                       - 0.675 * np.exp(-2.5 * t_arr)) + 20.0

    if scalar_input:
        return float(theta[0])
    return theta


# ── [3.6.4] — Curva nominale esterna ─────────────────────────────────────────

@ntc_ref(article="3.6.1.5.1", formula="3.6.4",
         latex=r"\theta = 660\,(1 - 0{,}687\,e^{-0{,}32\,t} - 0{,}313\,e^{-3{,}8\,t}) + 20")
def fire_external_curve(t: float | np.ndarray) -> float | np.ndarray:
    """Curva nominale di incendio esterna [°C].

    NTC18 §3.6.1.5.1, Formula [3.6.4]:
        theta = 660 * (1 - 0.687*exp(-0.32*t) - 0.313*exp(-3.8*t)) + 20

    Parameters
    ----------
    t : float or np.ndarray
        Tempo di esposizione [min]. Deve essere >= 0.

    Returns
    -------
    float or np.ndarray
        Temperatura dei gas caldi [°C].

    Raises
    ------
    ValueError
        Se ``t`` < 0.
    """
    t_arr = np.asarray(t, dtype=float)
    scalar_input = t_arr.ndim == 0
    t_arr = np.atleast_1d(t_arr)

    if np.any(t_arr < 0):
        raise ValueError("Il tempo t non puo' essere negativo.")

    theta = 660.0 * (1.0 - 0.687 * np.exp(-0.32 * t_arr)
                      - 0.313 * np.exp(-3.8 * t_arr)) + 20.0

    if scalar_input:
        return float(theta[0])
    return theta


# ── [3.6.1] — Carico d'incendio specifico di progetto ───────────────────────

@ntc_ref(article="3.6.1.1", formula="3.6.1",
         latex=r"q_{f,d} = q_f \cdot \delta_{q1} \cdot \delta_{q2} \cdot \delta_n")
def fire_design_load(
    q_f: float,
    delta_q1: float,
    delta_q2: float,
    delta_n: float,
) -> float:
    """Carico d'incendio specifico di progetto q_{f,d} [MJ/m²].

    NTC18 §3.6.1.1, Formula [3.6.1]:
        q_{f,d} = q_f * delta_q1 * delta_q2 * delta_n

    Parameters
    ----------
    q_f : float
        Valore nominale del carico d'incendio [MJ/m²]. Deve essere >= 0.
    delta_q1 : float
        Fattore rischio incendio per superficie compartimento [-]. >= 1.0.
    delta_q2 : float
        Fattore rischio incendio per tipo attivita' [-]. >= 0.8.
    delta_n : float
        Fattore misure di protezione antincendio [-]. >= 0.2.

    Returns
    -------
    float
        Carico d'incendio specifico di progetto [MJ/m²].

    Raises
    ------
    ValueError
        Se i parametri sono fuori dai limiti normativi.
    """
    if q_f < 0:
        raise ValueError(f"q_f deve essere >= 0, ricevuto {q_f}.")
    if delta_q1 < 1.0:
        raise ValueError(f"delta_q1 deve essere >= 1.0, ricevuto {delta_q1}.")
    if delta_q2 < 0.8:
        raise ValueError(f"delta_q2 deve essere >= 0.8, ricevuto {delta_q2}.")
    if delta_n < 0.2:
        raise ValueError(f"delta_n deve essere >= 0.2, ricevuto {delta_n}.")

    return q_f * delta_q1 * delta_q2 * delta_n


# ── [3.6.5] — Pressione statica equivalente esplosioni ──────────────────────

@ntc_ref(article="3.6.2.3", formula="3.6.5",
         latex=r"p = \max\!\bigl(3 + p_v,\; 3 + \tfrac{p_v}{2} + \tfrac{0{,}04}{(A_v/V)^2}\bigr)")
def explosion_equivalent_pressure(
    p_v: float,
    A_v: float,
    V: float,
) -> float:
    """Pressione statica equivalente per esplosioni Cat. 2 [kN/m²].

    NTC18 §3.6.2.3, Formule [3.6.5a]-[3.6.5b]:
        p_d = 3 + p_v
        p_s = 3 + p_v/2 + 0.04 / (A_v/V)²
        Risultato = max(p_d, p_s)

    Valida per compartimenti con V <= 1000 m³ e
    0.05 <= A_v/V <= 0.15 m⁻¹ [3.6.6].

    Parameters
    ----------
    p_v : float
        Pressione statica di cedimento aperture di sfogo [kN/m²].
    A_v : float
        Area delle aperture di sfogo [m²].
    V : float
        Volume dell'ambiente [m³]. Deve essere <= 1000.

    Returns
    -------
    float
        Pressione statica equivalente di progetto [kN/m²].

    Raises
    ------
    ValueError
        Se ``V`` > 1000 o rapporto ``A_v/V`` fuori range [0.05, 0.15].
    """
    if V > 1000.0:
        raise ValueError(
            f"Il volume deve essere <= 1000 m³, ricevuto {V}."
        )

    ratio = A_v / V
    if ratio < 0.05 or ratio > 0.15:
        raise ValueError(
            f"Il rapporto A_v/V deve essere in [0.05, 0.15] m⁻¹, "
            f"ricevuto {ratio:.4f}."
        )

    p_d = 3.0 + p_v                             # [3.6.5a]
    p_s = 3.0 + p_v / 2.0 + 0.04 / ratio**2    # [3.6.5b]

    return max(p_d, p_s)


# ── Tab. 3.6.III + [3.6.7] — Forze urti veicoli ────────────────────────────

@ntc_ref(article="3.6.3.3.1", table="Tab.3.6.III", formula="3.6.7",
         latex=r"F_{d,y} = 0{,}5\,F_{d,x} \quad (\text{Tab.\,3.6.III})")
def impact_vehicle_force(road_type: str) -> tuple[float, float]:
    """Forze statiche equivalenti per urti da traffico veicolare [kN].

    NTC18 §3.6.3.3.1, Tab. 3.6.III e Formula [3.6.7]:
        F_{d,y} = 0.5 * F_{d,x}

    Parameters
    ----------
    road_type : str
        Tipo di strada:
        - ``"highway"``: autostrade, strade extraurbane (1000 kN)
        - ``"rural"``: strade locali (750 kN)
        - ``"urban"``: strade urbane (500 kN)
        - ``"parking_car"``: parcheggi — automobili (50 kN)
        - ``"parking_truck"``: parcheggi — veicoli > 3.5 t (150 kN)

    Returns
    -------
    tuple[float, float]
        ``(F_dx, F_dy)`` forze in direzione parallela e ortogonale [kN].

    Raises
    ------
    ValueError
        Se ``road_type`` non e' valido.
    """
    if road_type not in _IMPACT_FORCES:
        raise ValueError(
            f"tipo di strada '{road_type}' non valido. "
            f"Valori ammessi: {', '.join(_IMPACT_FORCES.keys())}."
        )

    f_dx = _IMPACT_FORCES[road_type]
    f_dy = 0.5 * f_dx  # [3.6.7]

    return f_dx, f_dy


# ── [3.6.9] — Forza urto carrello elevatore ─────────────────────────────────

@ntc_ref(article="3.6.3.3.1", formula="3.6.9",
         latex=r"F = 5\,W")
def impact_forklift_force(W: float) -> float:
    """Forza statica equivalente per urto da carrello elevatore [kN].

    NTC18 §3.6.3.3.1, Formula [3.6.9]:
        F = 5 * W

    Parameters
    ----------
    W : float
        Peso complessivo del carrello elevatore e del massimo
        carico trasportabile [kN]. Deve essere >= 0.

    Returns
    -------
    float
        Forza orizzontale statica equivalente [kN].

    Raises
    ------
    ValueError
        Se ``W`` < 0.
    """
    if W < 0:
        raise ValueError(f"Il peso W deve essere >= 0, ricevuto {W}.")

    return 5.0 * W
