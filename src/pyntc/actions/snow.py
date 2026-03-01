"""Azione della neve — NTC18 §3.4.

Carico neve sulle coperture (§3.4.1), carico di riferimento al suolo (§3.4.2),
coefficienti di forma (§3.4.3), coefficiente di esposizione (§3.4.4),
coefficiente termico (§3.4.5).
"""

from __future__ import annotations

from pyntc.core.reference import ntc_ref


# ── Zone neve — parametri per q_sk (§3.4.2) ─────────────────────────────────
# Ogni zona e' definita da: (q_base [kN/m^2], coeff, divisore, esponente)
# Formula: q_sk = coeff * [1 + (a_s / divisore)^esponente]  per a_s > 200 m
#           q_sk = q_base                                    per a_s <= 200 m

_SNOW_ZONES: dict[str, tuple[float, float, float, float]] = {
    #        q_base  coeff  divisore  esponente
    "IA":  (1.50,   1.39,  728.0,    2.0),   # Zona I - Alpina     [3.4.2]
    "IM":  (1.50,   1.35,  602.0,    2.0),   # Zona I - Medit.     [3.4.3]
    "II":  (1.00,   0.85,  481.0,    2.0),   # Zona II             [3.4.4]
    "III": (0.60,   0.51,  481.0,    2.0),   # Zona III            [3.4.5]
}


# ── Tab. 3.4.I — Coefficiente di esposizione C_E ────────────────────────────

_EXPOSURE_COEFFICIENTS: dict[str, float] = {
    "windswept": 0.9,   # battuta dai venti
    "normal":    1.0,   # normale
    "sheltered": 1.1,   # riparata
}


@ntc_ref(article="3.4.2")
def snow_ground_load(zone: str, altitude: float) -> float:
    """Carico di riferimento della neve al suolo q_sk [kN/m^2].

    NTC18 §3.4.2, Formule [3.4.2]-[3.4.5].

    Per a_s <= 200 m: q_sk = valore base della zona.
    Per a_s > 200 m:  q_sk = coeff * [1 + (a_s / divisore)^2].

    Parameters
    ----------
    zone : str
        Zona neve: ``"IA"`` (I-Alpina), ``"IM"`` (I-Mediterranea),
        ``"II"``, ``"III"``. Vedi Fig. 3.4.1.
    altitude : float
        Altitudine del sito sul livello del mare [m].

    Returns
    -------
    float
        Carico neve al suolo q_sk [kN/m^2].

    Raises
    ------
    ValueError
        Se ``zone`` non e' valida, ``altitude`` < 0 o > 1500 m.
    """
    if zone not in _SNOW_ZONES:
        raise ValueError(
            f"zona neve '{zone}' non valida. "
            f"Valori ammessi: {', '.join(sorted(_SNOW_ZONES))}."
        )
    if altitude < 0:
        raise ValueError("L'altitudine non puo' essere negativa.")
    if altitude > 1500:
        raise ValueError(
            "Per altitudini > 1500 m servono indagini statistiche specifiche "
            "(NTC18 §3.4.2)."
        )

    q_base, coeff, divisore, esponente = _SNOW_ZONES[zone]

    if altitude <= 200.0:
        return q_base

    return coeff * (1.0 + (altitude / divisore) ** esponente)


@ntc_ref(article="3.4.3", table="Tab.3.4.II")
def snow_shape_coefficient(alpha: float) -> float:
    """Coefficiente di forma della copertura mu_1 [-].

    NTC18 §3.4.3, Tab. 3.4.II.

    - 0 <= alpha <= 30:  mu_1 = 0.8
    - 30 < alpha < 60:   mu_1 = 0.8 * (60 - alpha) / 30
    - alpha >= 60:        mu_1 = 0.0

    Parameters
    ----------
    alpha : float
        Angolo di inclinazione della falda rispetto all'orizzontale [gradi].

    Returns
    -------
    float
        Coefficiente di forma mu_1 [-].

    Raises
    ------
    ValueError
        Se ``alpha`` < 0.
    """
    if alpha < 0:
        raise ValueError("L'angolo di inclinazione non puo' essere negativo.")

    if alpha <= 30.0:
        return 0.8
    if alpha < 60.0:
        return 0.8 * (60.0 - alpha) / 30.0
    return 0.0


@ntc_ref(article="3.4.4", table="Tab.3.4.I")
def snow_exposure_coefficient(topography: str) -> float:
    """Coefficiente di esposizione C_E [-].

    NTC18 §3.4.4, Tab. 3.4.I.

    Parameters
    ----------
    topography : str
        Classe di esposizione: ``"windswept"`` (battuta dai venti),
        ``"normal"`` (normale), ``"sheltered"`` (riparata).

    Returns
    -------
    float
        Coefficiente di esposizione C_E [-].

    Raises
    ------
    ValueError
        Se ``topography`` non e' valida.
    """
    try:
        return _EXPOSURE_COEFFICIENTS[topography]
    except KeyError:
        raise ValueError(
            f"topografia '{topography}' non valida. "
            f"Valori ammessi: {', '.join(sorted(_EXPOSURE_COEFFICIENTS))}."
        )


@ntc_ref(article="3.4.1", formula="3.4.1")
def snow_roof_load(
    q_sk: float,
    mu_i: float,
    c_e: float = 1.0,
    c_t: float = 1.0,
) -> float:
    """Carico neve sulle coperture q_s [kN/m^2].

    NTC18 §3.4.1, Formula [3.4.1]:
        q_s = q_sk * mu_i * C_E * C_t

    Parameters
    ----------
    q_sk : float
        Carico di riferimento neve al suolo [kN/m^2].
    mu_i : float
        Coefficiente di forma della copertura [-].
    c_e : float
        Coefficiente di esposizione [-]. Default 1.0.
    c_t : float
        Coefficiente termico [-]. Default 1.0 (§3.4.5).

    Returns
    -------
    float
        Carico neve sulla copertura q_s [kN/m^2].
    """
    return q_sk * mu_i * c_e * c_t
