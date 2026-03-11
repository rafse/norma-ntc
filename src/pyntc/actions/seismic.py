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


@ntc_ref(article="3.2.1", formula="3.2.0", latex=r"T_R = -\frac{V_R}{\ln(1 - P_{VR})}")
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


@ntc_ref(article="3.2.3.2.1", formula="3.2.4", latex=r"\eta = \sqrt{\frac{10}{5 + \xi}} \geq 0{,}55")
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


@ntc_ref(article="3.2.3.2.1", table="Tab.3.2.IV", latex=r"\text{Tab.\,3.2.IV — }S_s,\;C_c")
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


@ntc_ref(article="3.2.3.2.1", table="Tab.3.2.V", latex=r"\text{Tab.\,3.2.V — }S_T")
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


@ntc_ref(article="3.2.3.2.1", formula="3.2.2", latex=r"S_e(T) = a_g \cdot S \cdot \eta \cdot F_0 \cdot \begin{cases} \frac{T}{T_B} + \frac{1}{\eta F_0}\left(1 - \frac{T}{T_B}\right) & 0 \leq T < T_B \\ 1 & T_B \leq T < T_C \\ \frac{T_C}{T} & T_C \leq T < T_D \\ \frac{T_C T_D}{T^2} & T \geq T_D \end{cases}")
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


# ── §3.2.2 Velocità equivalente ───────────────────────────────────────────────

@ntc_ref(
    article="3.2.2",
    formula="3.2.1",
    latex=r"V_{s,eq} = \frac{H}{\sum_{i=1}^{N} \frac{h_i}{v_{s,i}}}",
)
def seismic_equivalent_shear_velocity(
    H: float,
    h_i: list[float],
    v_s_i: list[float],
) -> float:
    """Velocita' di taglio equivalente V_s,eq [m/s].

    NTC18 §3.2.2, Formula [3.2.1]:
        V_s,eq = H / sum(h_i / v_s,i)

    dove H = sum(h_i) e' la profondita' totale del profilo stratigrafico
    e la somma e' estesa agli N strati da 0 a 30 m di profondita'.

    Parameters
    ----------
    H : float
        Profondita' totale del profilo [m]. Deve essere > 0 e
        approssimativamente uguale a sum(h_i).
    h_i : list[float]
        Spessori dei singoli strati [m]. Tutti devono essere > 0.
    v_s_i : list[float]
        Velocita' di taglio dei singoli strati [m/s]. Tutti devono essere > 0.

    Returns
    -------
    float
        Velocita' di taglio equivalente V_s,eq [m/s].

    Raises
    ------
    ValueError
        Se le liste hanno lunghezze diverse, se H <= 0, se un valore e' <= 0,
        o se sum(h_i) non e' compatibile con H (tolleranza 1%).
    """
    if len(h_i) != len(v_s_i):
        raise ValueError(
            f"Le liste h_i e v_s_i devono avere la stessa lunghezza, "
            f"ricevuto {len(h_i)} e {len(v_s_i)}."
        )
    if H <= 0.0:
        raise ValueError(f"H deve essere positivo, ricevuto {H}.")
    for i, (h, v) in enumerate(zip(h_i, v_s_i)):
        if h <= 0.0:
            raise ValueError(f"h_i[{i}] = {h} deve essere positivo.")
        if v <= 0.0:
            raise ValueError(f"v_s_i[{i}] = {v} deve essere positivo.")

    sum_h = sum(h_i)
    if not math.isclose(sum_h, H, rel_tol=0.01):
        raise ValueError(
            f"sum(h_i) = {sum_h:.4f} non corrisponde a H = {H:.4f} "
            f"(tolleranza 1%)."
        )

    return H / sum(h / v for h, v in zip(h_i, v_s_i))


# ── §3.2.3.2.2 Spettro verticale ─────────────────────────────────────────────

@ntc_ref(
    article="3.2.3.2.2",
    formula="3.2.9",
    latex=r"F_v = 1{,}35 \cdot F_0 \cdot \left(\frac{a_g}{g}\right)^{0{,}5}",
)
def seismic_vertical_spectrum_amplification(
    a_g: float,
    F_0: float,
) -> float:
    """Fattore di amplificazione spettrale massima verticale F_v [-].

    NTC18 §3.2.3.2.2, Formula [3.2.9]:
        F_v = 1.35 * F_0 * (a_g / g)^0.5

    dove g = 9.81 m/s^2.

    Parameters
    ----------
    a_g : float
        Accelerazione massima al suolo su cat. A [g]. Deve essere > 0.
    F_0 : float
        Fattore di amplificazione spettrale massima orizzontale [-].
        Deve essere >= 2.2.

    Returns
    -------
    float
        Fattore di amplificazione spettrale massima verticale F_v [-].

    Raises
    ------
    ValueError
        Se ``a_g`` <= 0 o ``F_0`` < 2.2.
    """
    if a_g <= 0.0:
        raise ValueError(f"a_g deve essere positivo, ricevuto {a_g}.")
    if F_0 < 2.2:
        raise ValueError(f"F_0 deve essere >= 2.2, ricevuto {F_0}.")

    return 1.35 * F_0 * math.sqrt(a_g)


# ── §3.2.3.2.3 Spettro di spostamento ────────────────────────────────────────

@ntc_ref(
    article="3.2.3.2.3",
    formula="3.2.10",
    latex=(
        r"S_{De}(T) = S_e(T) \cdot \left(\frac{T}{2\pi}\right)^2 \;"
        r"\text{per } T \leq T_D, \quad "
        r"S_{De}(T) = S_{De}(T_D) \; \text{per } T > T_D"
    ),
)
def seismic_displacement_spectrum(
    S_e: float,
    T: float,
    T_D: float,
    S_e_TD: float | None = None,
) -> float:
    """Ordinata dello spettro elastico di spostamento S_De(T) [m].

    NTC18 §3.2.3.2.3, Formule [3.2.10]–[3.2.11]:
        S_De(T) = S_e(T) * (T / (2*pi))^2    per T <= T_D
        S_De(T) = S_De(T_D)                   per T >  T_D  (plateau spostamenti)

    dove S_e e' espressa in [g] (come restituito da elastic_response_spectrum),
    e il risultato e' convertito in [m] con g = 9.81 m/s^2.

    Parameters
    ----------
    S_e : float
        Ordinata spettrale elastica S_e(T) [g].
    T : float
        Periodo di vibrazione [s]. Deve essere >= 0.
    T_D : float
        Periodo di inizio tratto a spostamento costante [s]. Deve essere > 0.
    S_e_TD : float or None
        Ordinata spettrale al periodo T_D [g], necessaria solo quando T > T_D.
        Se None e T > T_D viene sollevato ValueError.

    Returns
    -------
    float
        Ordinata spettrale di spostamento S_De(T) [m].

    Raises
    ------
    ValueError
        Se ``T`` < 0, ``T_D`` <= 0, o ``S_e_TD`` non fornito per T > T_D.
    """
    _G = 9.81  # m/s^2

    if T < 0.0:
        raise ValueError(f"Il periodo T non puo' essere negativo, ricevuto {T}.")
    if T_D <= 0.0:
        raise ValueError(f"T_D deve essere positivo, ricevuto {T_D}.")

    if T <= T_D:
        return S_e * _G * (T / (2.0 * math.pi)) ** 2
    else:
        if S_e_TD is None:
            raise ValueError(
                "Per T > T_D e' necessario fornire S_e_TD (ordinata spettrale "
                "in accelerazione a T_D) per calcolare il plateau di spostamento."
            )
        return S_e_TD * _G * (T_D / (2.0 * math.pi)) ** 2


# ── §3.2.3.3 Spostamento e velocità di picco del terreno ─────────────────────

@ntc_ref(
    article="3.2.3.3",
    formula="3.2.12",
    latex=(
        r"d_g = 0{,}025 \cdot a_g \cdot S \cdot T_C \cdot T_D, \quad "
        r"v_g = 0{,}16 \cdot a_g \cdot S \cdot T_C"
    ),
)
def seismic_peak_ground_displacement(
    a_g: float,
    S: float,
    T_C: float,
    T_D: float,
) -> tuple[float, float]:
    """Spostamento e velocita' di picco del terreno d_g [m] e v_g [m/s].

    NTC18 §3.2.3.3, Formula [3.2.12]:
        d_g = 0.025 * a_g * g * S * T_C * T_D   [m]
        v_g = 0.16  * a_g * g * S * T_C          [m/s]

    dove g = 9.81 m/s^2 e a_g e' espresso in [g].

    Parameters
    ----------
    a_g : float
        Accelerazione massima al suolo su cat. A [g]. Deve essere > 0.
    S : float
        Coefficiente di amplificazione complessivo S = S_s * S_T [-].
        Deve essere > 0.
    T_C : float
        Periodo di inizio tratto a velocita' costante [s]. Deve essere > 0.
    T_D : float
        Periodo di inizio tratto a spostamento costante [s]. Deve essere > 0.

    Returns
    -------
    tuple[float, float]
        ``(d_g, v_g)`` spostamento [m] e velocita' [m/s] di picco del terreno.

    Raises
    ------
    ValueError
        Se uno qualsiasi dei parametri e' <= 0.
    """
    _G = 9.81  # m/s^2

    if a_g <= 0.0:
        raise ValueError(f"a_g deve essere positivo, ricevuto {a_g}.")
    if S <= 0.0:
        raise ValueError(f"S deve essere positivo, ricevuto {S}.")
    if T_C <= 0.0:
        raise ValueError(f"T_C deve essere positivo, ricevuto {T_C}.")
    if T_D <= 0.0:
        raise ValueError(f"T_D deve essere positivo, ricevuto {T_D}.")

    ag_ms2 = a_g * _G  # [m/s^2]
    d_g = 0.025 * ag_ms2 * S * T_C * T_D
    v_g = 0.16 * ag_ms2 * S * T_C
    return d_g, v_g


# ── §3.2.4.2 Spostamento assoluto massimo del terreno ────────────────────────

@ntc_ref(
    article="3.2.4.2",
    formula="3.2.13",
    latex=r"d_{g,\max} = 1{,}25\,\sqrt{d_{g,x}^2 + d_{g,y}^2}",
)
def seismic_max_ground_displacement(d_g_x: float, d_g_y: float) -> float:
    """Spostamento assoluto massimo del terreno d_g,max [m].

    NTC18 §3.2.4.2, Formula [3.2.13]:
        d_g,max = 1.25 * sqrt(d_g_x^2 + d_g_y^2)

    dove d_g_x e d_g_y sono gli spostamenti di picco del terreno nelle due
    direzioni orizzontali principali (tipicamente coincidenti se si usa
    lo stesso spettro nelle due direzioni).

    Parameters
    ----------
    d_g_x : float
        Spostamento di picco del terreno in direzione X [m]. Deve essere >= 0.
    d_g_y : float
        Spostamento di picco del terreno in direzione Y [m]. Deve essere >= 0.

    Returns
    -------
    float
        Spostamento assoluto massimo d_g,max [m].

    Raises
    ------
    ValueError
        Se uno dei valori e' negativo.
    """
    if d_g_x < 0.0:
        raise ValueError(f"d_g_x deve essere >= 0, ricevuto {d_g_x}.")
    if d_g_y < 0.0:
        raise ValueError(f"d_g_y deve essere >= 0, ricevuto {d_g_y}.")

    return 1.25 * math.sqrt(d_g_x**2 + d_g_y**2)
