"""Vita nominale, classe d'uso e periodo di riferimento — NTC18 Cap. 2.4.

Tabelle 2.4.I e 2.4.II, Formula 2.4.1.
"""

from __future__ import annotations

from pyntc.core.reference import ntc_ref


# ============================================================================
# Tabella 2.4.I — Vita nominale V_N
# ============================================================================
_NOMINAL_LIFE: dict[str, float] = {
    "temporanea": 10.0,
    "normale": 50.0,
    "strategica": 100.0,
}

# ============================================================================
# Tabella 2.4.II — Coefficiente d'uso C_U
# ============================================================================
_USAGE_COEFFICIENT: dict[str, float] = {
    "I": 0.7,
    "II": 1.0,
    "III": 1.5,
    "IV": 2.0,
}


# ============================================================================
# Funzioni
# ============================================================================


@ntc_ref(article="2.4.1", table="Tab.2.4.I", latex=r"V_N \in \{10,\,50,\,100\}\;\text{anni}")
def safety_nominal_life(building_type: str) -> float:
    """Vita nominale V_N di una costruzione [anni].

    NTC18 §2.4.1 — Tab. 2.4.I.

    Parameters
    ----------
    building_type : str
        Tipo di costruzione:

        - ``"temporanea"`` — strutture temporanee (V_N = 10 anni)
        - ``"normale"`` — strutture ordinarie e infrastrutture (V_N = 50 anni)
        - ``"strategica"`` — grandi infrastrutture e strutture strategiche
          (V_N = 100 anni)

    Returns
    -------
    float
        Vita nominale V_N [anni].

    Raises
    ------
    ValueError
        Se il tipo di costruzione non è riconosciuto.
    """
    if building_type not in _NOMINAL_LIFE:
        raise ValueError(
            f"Tipo di costruzione non valido: {building_type!r}. "
            f"Valori ammessi: {set(_NOMINAL_LIFE.keys())}"
        )
    return _NOMINAL_LIFE[building_type]


@ntc_ref(article="2.4.2", table="Tab.2.4.II", latex=r"C_U \in \{0.7,\,1.0,\,1.5,\,2.0\}")
def safety_usage_coefficient(usage_class: str) -> float:
    """Coefficiente d'uso C_U per classe d'uso [-].

    NTC18 §2.4.2 — Tab. 2.4.II.

    Parameters
    ----------
    usage_class : str
        Classe d'uso della costruzione:

        - ``"I"``  — strutture con presenza occasionale di persone (C_U = 0.7)
        - ``"II"`` — strutture a uso normale (C_U = 1.0)
        - ``"III"`` — strutture con affollamento significativo (C_U = 1.5)
        - ``"IV"`` — strutture strategiche o con funzioni pubbliche essenziali
          (C_U = 2.0)

    Returns
    -------
    float
        Coefficiente d'uso C_U [-].

    Raises
    ------
    ValueError
        Se la classe d'uso non è riconosciuta.
    """
    if usage_class not in _USAGE_COEFFICIENT:
        raise ValueError(
            f"Classe d'uso non valida: {usage_class!r}. "
            f"Valori ammessi: {set(_USAGE_COEFFICIENT.keys())}"
        )
    return _USAGE_COEFFICIENT[usage_class]


@ntc_ref(article="2.4.3", formula="2.4.1", latex=r"V_R = V_N \cdot C_U")
def reference_period(V_N: float, C_U: float) -> float:
    """Periodo di riferimento per l'azione sismica V_R [anni].

    NTC18 §2.4.3 — Formula [2.4.1]:

    .. math::
        V_R = V_N \\cdot C_U

    Parameters
    ----------
    V_N : float
        Vita nominale della costruzione [anni].
    C_U : float
        Coefficiente d'uso [-].

    Returns
    -------
    float
        Periodo di riferimento V_R [anni].

    Raises
    ------
    ValueError
        Se V_N o C_U non sono positivi.
    """
    if V_N <= 0:
        raise ValueError(f"V_N deve essere positivo: {V_N}")
    if C_U <= 0:
        raise ValueError(f"C_U deve essere positivo: {C_U}")
    return V_N * C_U
