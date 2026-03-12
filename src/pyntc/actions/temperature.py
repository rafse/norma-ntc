"""Azioni della temperatura — NTC18 §3.5.

Temperatura aria esterna (§3.5.2), contributo irraggiamento solare (§3.5.4,
Tab. 3.5.I), variazione termica uniforme per edifici (§3.5.5, Tab. 3.5.II).
"""

from __future__ import annotations

from pyntc.core.reference import ntc_ref


# ── §3.5.2 — Parametri per zona: (T_min_base, slope_min, T_max_base, slope_max)
# T_min = T_min_base - slope_min * a_s / 1000
# T_max = T_max_base - slope_max * a_s / 1000

_TEMP_ZONES: dict[str, tuple[float, float, float, float]] = {
    #         T_min_base  slope_min  T_max_base  slope_max
    "I":   (-15.0,  4.0,  42.0,  6.0),   # [3.5.1], [3.5.2]
    "II":  ( -8.0,  6.0,  42.0,  2.0),   # [3.5.3], [3.5.4]
    "III": ( -8.0,  7.0,  42.0,  0.3),   # [3.5.5], [3.5.6]
    "IV":  ( -2.0,  9.0,  42.0,  2.0),   # [3.5.7], [3.5.8]
}


# ── Tab. 3.5.I — Incremento irraggiamento solare [°C] ───────────────────────
# Chiave: (surface, orientation) → valore estivo. Inverno = 0 per tutti.

_SOLAR_INCREMENT: dict[tuple[str, str], float] = {
    ("reflective", "NE"):  0.0,
    ("reflective", "SW"): 18.0,
    ("light", "NE"):       2.0,
    ("light", "SW"):      30.0,
    ("dark", "NE"):        4.0,
    ("dark", "SW"):       42.0,
}

_VALID_SURFACES = {"reflective", "light", "dark"}
_VALID_ORIENTATIONS = {"NE", "SW"}
_VALID_SEASONS = {"summer", "winter"}


# ── Tab. 3.5.II — Variazione termica uniforme ΔT_u [°C] ────────────────────

_UNIFORM_VARIATION: dict[str, float] = {
    "rc_exposed":      15.0,
    "rc_protected":    10.0,
    "steel_exposed":   25.0,
    "steel_protected": 15.0,
}


@ntc_ref(article="3.5.2", formula="3.5.1-3.5.8",
         latex=r"T_{\min} = T_{\min,0} - \Delta T_{\min} \cdot \frac{a_s}{1000};\;"
               r"T_{\max} = T_{\max,0} - \Delta T_{\max} \cdot \frac{a_s}{1000}")
def temperature_extremes(
    zone: str,
    altitude: float,
) -> tuple[float, float]:
    """Temperature estreme dell'aria esterna T_min e T_max [°C].

    NTC18 §3.5.2, Formule [3.5.1]-[3.5.8].
    Periodo di ritorno 50 anni.

    Parameters
    ----------
    zone : str
        Zona climatica: ``"I"``, ``"II"``, ``"III"``, ``"IV"``.
    altitude : float
        Altitudine del sito a_s [m s.l.m.]. Deve essere >= 0.

    Returns
    -------
    tuple[float, float]
        ``(T_min, T_max)`` temperature estreme [°C].

    Raises
    ------
    ValueError
        Se ``zone`` non e' valida o ``altitude`` < 0.
    """
    if zone not in _TEMP_ZONES:
        raise ValueError(
            f"zona '{zone}' non valida. "
            f"Valori ammessi: I, II, III, IV."
        )

    if altitude < 0:
        raise ValueError(
            f"L'altitudine deve essere >= 0, ricevuto {altitude}."
        )

    t_min_base, slope_min, t_max_base, slope_max = _TEMP_ZONES[zone]

    t_min = t_min_base - slope_min * altitude / 1000.0
    t_max = t_max_base - slope_max * altitude / 1000.0

    return t_min, t_max


@ntc_ref(article="3.5.4", table="Tab.3.5.I",
         latex=r"\text{Tab.\,3.5.I — Incremento irraggiamento solare}")
def temperature_solar_increment(
    surface: str,
    orientation: str,
    season: str = "summer",
) -> float:
    """Incremento di temperatura da irraggiamento solare [°C].

    NTC18 §3.5.4, Tab. 3.5.I.

    Parameters
    ----------
    surface : str
        Natura della superficie: ``"reflective"``, ``"light"``, ``"dark"``.
    orientation : str
        Orientamento: ``"NE"`` (Nord-Est) o ``"SW"`` (Sud-Ovest/orizzontale).
    season : str
        Stagione: ``"summer"`` (estate) o ``"winter"`` (inverno).
        Default ``"summer"``.

    Returns
    -------
    float
        Incremento di temperatura [°C].

    Raises
    ------
    ValueError
        Se ``surface``, ``orientation`` o ``season`` non sono validi.
    """
    if surface not in _VALID_SURFACES:
        raise ValueError(
            f"superficie '{surface}' non valida. "
            f"Valori ammessi: reflective, light, dark."
        )

    if orientation not in _VALID_ORIENTATIONS:
        raise ValueError(
            f"orientamento '{orientation}' non valido. "
            f"Valori ammessi: NE, SW."
        )

    if season not in _VALID_SEASONS:
        raise ValueError(
            f"stagione '{season}' non valida. "
            f"Valori ammessi: summer, winter."
        )

    # In inverno l'incremento solare e' 0 per tutti
    if season == "winter":
        return 0.0

    return _SOLAR_INCREMENT[(surface, orientation)]


@ntc_ref(article="3.5.5", table="Tab.3.5.II",
         latex=r"\text{Tab.\,3.5.II — Variazione termica uniforme } \Delta T_u")
def temperature_uniform_variation(structure_type: str) -> float:
    """Variazione termica uniforme DeltaT_u per edifici [°C].

    NTC18 §3.5.5, Tab. 3.5.II.
    Il valore restituito e' positivo; applicare con segno ± nelle
    combinazioni di carico.

    Parameters
    ----------
    structure_type : str
        Tipo di struttura:
        - ``"rc_exposed"``: c.a./c.a.p. esposte (±15°C)
        - ``"rc_protected"``: c.a./c.a.p. protette (±10°C)
        - ``"steel_exposed"``: acciaio esposte (±25°C)
        - ``"steel_protected"``: acciaio protette (±15°C)

    Returns
    -------
    float
        DeltaT_u [°C] (valore assoluto).

    Raises
    ------
    ValueError
        Se ``structure_type`` non e' valido.
    """
    if structure_type not in _UNIFORM_VARIATION:
        raise ValueError(
            f"tipo di struttura '{structure_type}' non valido. "
            f"Valori ammessi: rc_exposed, rc_protected, "
            f"steel_exposed, steel_protected."
        )

    return _UNIFORM_VARIATION[structure_type]


# ── Tab. 3.5.III — Coefficienti di dilatazione termica ──────────────────────

_THERMAL_EXPANSION: dict[str, float | tuple[float, float]] = {
    "aluminum":              24.0,          # Alluminio [10⁻⁶/°C]
    "steel":                 12.0,          # Acciaio da carpenteria
    "concrete":              10.0,          # Calcestruzzo strutturale
    "composite":             12.0,          # Strutture miste acciaio-calcestruzzo
    "lightweight_concrete":   7.0,          # Calcestruzzo alleggerito
    "masonry":               (6.0, 10.0),   # Muratura (range)
    "timber_parallel":        5.0,          # Legno parallelo alle fibre
    "timber_perpendicular":  (30.0, 70.0),  # Legno ortogonale alle fibre (range)
}


@ntc_ref(article="3.5.7", table="Tab.3.5.III",
         latex=r"\alpha_T \;\text{[10^{-6}/°C]} — \text{Tab.\,3.5.III}")
def thermal_expansion_coefficient(
    material: str,
) -> float | tuple[float, float]:
    """Coefficiente di dilatazione termica alpha_T [10⁻⁶/°C].

    NTC18 §3.5.7, Tab. 3.5.III.
    Per materiali con valore a range (muratura, legno ortogonale),
    restituisce una tupla ``(min, max)``.

    Parameters
    ----------
    material : str
        Materiale:
        - ``"aluminum"``: alluminio (24)
        - ``"steel"``: acciaio da carpenteria (12)
        - ``"concrete"``: calcestruzzo strutturale (10)
        - ``"composite"``: strutture miste acciaio-calcestruzzo (12)
        - ``"lightweight_concrete"``: calcestruzzo alleggerito (7)
        - ``"masonry"``: muratura (6 ÷ 10) → tuple (6, 10)
        - ``"timber_parallel"``: legno parallelo alle fibre (5)
        - ``"timber_perpendicular"``: legno ortogonale alle fibre (30 ÷ 70) → tuple (30, 70)

    Returns
    -------
    float or tuple[float, float]
        Coefficiente alpha_T [10⁻⁶/°C].
        Tupla ``(min, max)`` per materiali con range normativo.

    Raises
    ------
    ValueError
        Se ``material`` non e' valido.
    """
    if material not in _THERMAL_EXPANSION:
        valid = ", ".join(_THERMAL_EXPANSION.keys())
        raise ValueError(
            f"materiale '{material}' non valido. "
            f"Valori ammessi: {valid}."
        )

    return _THERMAL_EXPANSION[material]
