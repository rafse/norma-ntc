"""Azione sismica — NTC18 §3.2.

Periodo di ritorno (§3.2.1), categorie di sottosuolo (§3.2.2),
spettro di risposta elastico orizzontale (§3.2.3.2.1).
"""

from __future__ import annotations

import math

import numpy as np

from pyntc.core.reference import ntc_ref


# ── Tab. 3.2.IV — Parametri amplificazione stratigrafica ─────────────────────
# Ogni categoria: (coeff_Ss, slope_Ss, min_Ss, max_Ss, coeff_Cc, exp_Cc)
# S_s = clamp(coeff_Ss - slope_Ss * F0 * ag, min_Ss, max_Ss)
# C_c = coeff_Cc * Tc_star^(exp_Cc)

_SOIL_PARAMS: dict[str, tuple[float, float, float, float, float, float]] = {
    #         coeff  slope  min   max   coeff_Cc  exp_Cc
    "A": (1.00,  0.00,  1.00, 1.00,  1.00,  0.00),
    "B": (1.40,  0.40,  1.00, 1.20,  1.10, -0.20),
    "C": (1.70,  0.60,  1.00, 1.50,  1.05, -0.33),
    "D": (2.40,  1.50,  0.90, 1.80,  1.25, -0.50),
    "E": (2.00,  1.10,  1.00, 1.60,  1.15, -0.40),
}


# ── Tab. 3.2.V — Amplificazione topografica ──────────────────────────────────

_TOPO_FACTORS: dict[str, float] = {
    "T1": 1.0,
    "T2": 1.2,
    "T3": 1.2,
    "T4": 1.4,
}


@ntc_ref(article="3.2.1", formula="3.2.0")
def seismic_return_period(v_r: float, p_vr: float) -> float:
    """Periodo di ritorno del sisma T_R [anni].

    NTC18 §3.2.1, Formula [3.2.0]:
        T_R = -V_R / ln(1 - P_VR)

    Parameters
    ----------
    v_r : float
        Periodo di riferimento della costruzione V_R [anni].
    p_vr : float
        Probabilita' di superamento nel periodo di riferimento [-].
        Deve essere in (0, 1). Valori tipici: 0.81 (SLO), 0.63 (SLD),
        0.10 (SLV), 0.05 (SLC).

    Returns
    -------
    float
        Periodo di ritorno T_R [anni].

    Raises
    ------
    ValueError
        Se ``p_vr`` non e' in (0, 1).
    """
    if p_vr <= 0.0 or p_vr >= 1.0:
        raise ValueError(
            f"La probabilita' di superamento deve essere in (0, 1), "
            f"ricevuto {p_vr}."
        )

    return -v_r / math.log(1.0 - p_vr)


@ntc_ref(article="3.2.3.2.1", formula="3.2.4")
def seismic_damping_factor(xi: float) -> float:
    """Fattore di smorzamento eta [-].

    NTC18 §3.2.3.2.1, Formula [3.2.4]:
        eta = sqrt(10 / (5 + xi)) >= 0.55

    Parameters
    ----------
    xi : float
        Coefficiente di smorzamento viscoso [%]. Tipicamente 5%.

    Returns
    -------
    float
        Fattore eta [-].

    Raises
    ------
    ValueError
        Se ``xi`` < 0.
    """
    if xi < 0:
        raise ValueError("Il coefficiente di smorzamento non puo' essere negativo.")

    return max(math.sqrt(10.0 / (5.0 + xi)), 0.55)


@ntc_ref(article="3.2.3.2.1", table="Tab.3.2.IV")
def seismic_soil_amplification(
    soil_category: str,
    ag: float,
    F0: float,
    Tc_star: float,
) -> tuple[float, float]:
    """Coefficienti di amplificazione stratigrafica S_s e C_c [-].

    NTC18 §3.2.3.2.1, Tab. 3.2.IV.

    Parameters
    ----------
    soil_category : str
        Categoria di sottosuolo: ``"A"``, ``"B"``, ``"C"``, ``"D"``, ``"E"``.
    ag : float
        Accelerazione massima al suolo su cat. A [g].
    F0 : float
        Fattore di amplificazione spettrale massima [-]. Minimo 2.2.
    Tc_star : float
        Periodo di inizio tratto a velocita' costante [s].

    Returns
    -------
    tuple[float, float]
        ``(S_s, C_c)`` coefficienti di amplificazione stratigrafica [-].

    Raises
    ------
    ValueError
        Se ``soil_category`` non e' valida.
    """
    if soil_category not in _SOIL_PARAMS:
        raise ValueError(
            f"categoria di sottosuolo '{soil_category}' non valida. "
            f"Valori ammessi: A, B, C, D, E."
        )

    coeff_ss, slope_ss, min_ss, max_ss, coeff_cc, exp_cc = _SOIL_PARAMS[
        soil_category
    ]

    # S_s con clamp
    ss_raw = coeff_ss - slope_ss * F0 * ag
    ss = max(min_ss, min(ss_raw, max_ss))

    # C_c
    if exp_cc == 0.0:
        cc = coeff_cc
    else:
        cc = coeff_cc * Tc_star**exp_cc

    return ss, cc


@ntc_ref(article="3.2.3.2.1", table="Tab.3.2.V")
def seismic_topographic_amplification(topo_category: str) -> float:
    """Coefficiente di amplificazione topografica S_T [-].

    NTC18 §3.2.3.2.1, Tab. 3.2.V.

    Parameters
    ----------
    topo_category : str
        Categoria topografica: ``"T1"``, ``"T2"``, ``"T3"``, ``"T4"``.

    Returns
    -------
    float
        Coefficiente S_T [-].

    Raises
    ------
    ValueError
        Se ``topo_category`` non e' valida.
    """
    try:
        return _TOPO_FACTORS[topo_category]
    except KeyError:
        raise ValueError(
            f"categoria topografica '{topo_category}' non valida. "
            f"Valori ammessi: T1, T2, T3, T4."
        )


@ntc_ref(article="3.2.3.2.1", formula="3.2.2")
def elastic_response_spectrum(
    T: float | np.ndarray,
    ag: float,
    F0: float,
    Tc_star: float,
    soil_category: str = "A",
    topo_category: str = "T1",
    xi: float = 5.0,
) -> float | np.ndarray:
    """Spettro di risposta elastico orizzontale Se(T) [g].

    NTC18 §3.2.3.2.1, Formula [3.2.2].

    Calcola le ordinate spettrali per i quattro tratti:
    - 0 <= T < T_B:  rampa ascendente
    - T_B <= T < T_C: plateau (accelerazione costante)
    - T_C <= T < T_D: tratto a velocita' costante (1/T)
    - T_D <= T:       tratto a spostamento costante (1/T^2)

    Parameters
    ----------
    T : float or np.ndarray
        Periodo/i di vibrazione [s]. Deve essere >= 0.
    ag : float
        Accelerazione massima al suolo su cat. A [g].
    F0 : float
        Fattore di amplificazione spettrale massima [-].
    Tc_star : float
        Periodo di inizio tratto a velocita' costante [s].
    soil_category : str
        Categoria di sottosuolo (default ``"A"``).
    topo_category : str
        Categoria topografica (default ``"T1"``).
    xi : float
        Smorzamento viscoso [%]. Default 5%.

    Returns
    -------
    float or np.ndarray
        Ordinata/e spettrale/i Se(T) [g].

    Raises
    ------
    ValueError
        Se ``T`` < 0.
    """
    T_arr = np.asarray(T, dtype=float)
    scalar_input = T_arr.ndim == 0
    T_arr = np.atleast_1d(T_arr)

    if np.any(T_arr < 0):
        raise ValueError("Il periodo T non puo' essere negativo.")

    # Parametri di sito
    Ss, Cc = seismic_soil_amplification(soil_category, ag, F0, Tc_star)
    St = seismic_topographic_amplification(topo_category)
    S = Ss * St                                # [3.2.3]
    eta = seismic_damping_factor(xi)           # [3.2.4]

    # Periodi caratteristici
    Tc = Cc * Tc_star                           # [3.2.5]
    Tb = Tc / 3.0                               # [3.2.6]
    Td = 4.0 * ag + 1.6                         # [3.2.7]

    # Plateau
    plateau = ag * S * eta * F0

    # Calcolo spettro per ogni periodo
    Se = np.empty_like(T_arr)

    # Tratto 1: 0 <= T < T_B
    mask1 = T_arr < Tb
    if np.any(mask1):
        ratio = T_arr[mask1] / Tb
        Se[mask1] = plateau * (ratio + (1.0 / (eta * F0)) * (1.0 - ratio))

    # Tratto 2: T_B <= T < T_C
    mask2 = (T_arr >= Tb) & (T_arr < Tc)
    Se[mask2] = plateau

    # Tratto 3: T_C <= T < T_D
    mask3 = (T_arr >= Tc) & (T_arr < Td)
    if np.any(mask3):
        Se[mask3] = plateau * (Tc / T_arr[mask3])

    # Tratto 4: T >= T_D
    mask4 = T_arr >= Td
    if np.any(mask4):
        Se[mask4] = plateau * (Tc * Td / T_arr[mask4] ** 2)

    if scalar_input:
        return float(Se[0])
    return Se
