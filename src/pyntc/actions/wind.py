"""Azione del vento — NTC18 §3.3.

Velocita' base di riferimento (§3.3.1), velocita' di riferimento (§3.3.2),
pressione cinetica (§3.3.6), coefficiente di esposizione (§3.3.7),
pressione del vento (§3.3.4), azione tangente (§3.3.5).
"""

from __future__ import annotations

import math

from pyntc.core.reference import ntc_ref


# ── Tab. 3.3.I — Parametri zone vento (v_b0 [m/s], a_0 [m], k_s [-]) ───────

_WIND_ZONES: dict[int, tuple[float, float, float]] = {
    1: (25.0, 1000.0, 0.40),
    2: (25.0,  750.0, 0.45),
    3: (27.0,  500.0, 0.37),
    4: (28.0,  500.0, 0.36),
    5: (28.0,  750.0, 0.40),
    6: (28.0,  500.0, 0.36),
    7: (28.0, 1000.0, 0.54),
    8: (30.0, 1500.0, 0.50),
    9: (31.0,  500.0, 0.32),
}


# ── Tab. 3.3.II — Parametri esposizione (k_r [-], z_0 [m], z_min [m]) ───────

_EXPOSURE_CATEGORIES: dict[int, tuple[float, float, float]] = {
    1: (0.17, 0.01,  2.0),
    2: (0.19, 0.05,  4.0),
    3: (0.20, 0.10,  5.0),
    4: (0.22, 0.30,  8.0),
    5: (0.23, 0.70, 12.0),
}


# Densita' dell'aria [kg/m^3] — NTC18 §3.3.6
_RHO_AIR = 1.25


@ntc_ref(article="3.3.1", table="Tab.3.3.I", formula="3.3.1",
         latex=r"v_b = v_{b,0} \cdot c_a \quad c_a = 1 + k_s \left(\frac{a_s}{a_0} - 1\right)")
def wind_base_velocity(zone: int, altitude: float = 0.0) -> float:
    """Velocita' base di riferimento del vento v_b [m/s].

    NTC18 §3.3.1, Tab. 3.3.I, Formula [3.3.1]:
        v_b = v_b,0 * c_a

    dove c_a e' il coefficiente di altitudine:
        c_a = 1                              per a_s <= a_0
        c_a = 1 + k_s * (a_s/a_0 - 1)      per a_0 < a_s <= 1500 m

    Parameters
    ----------
    zone : int
        Zona del vento (1-9), da Tab. 3.3.I / Fig. 3.3.1.
    altitude : float
        Altitudine del sito sul livello del mare [m]. Default 0.

    Returns
    -------
    float
        Velocita' base di riferimento v_b [m/s].

    Raises
    ------
    ValueError
        Se ``zone`` non e' in [1, 9], ``altitude`` < 0 o > 1500 m.
    """
    if zone not in _WIND_ZONES:
        raise ValueError(
            f"zona {zone} non valida. Valori ammessi: 1-9 (Tab. 3.3.I)."
        )
    if altitude < 0:
        raise ValueError("L'altitudine non puo' essere negativa.")
    if altitude > 1500:
        raise ValueError(
            "Per altitudini > 1500 m servono indagini statistiche specifiche "
            "(NTC18 §3.3.1)."
        )

    vb0, a0, ks = _WIND_ZONES[zone]

    if altitude <= a0:
        c_a = 1.0
    else:
        c_a = 1.0 + ks * (altitude / a0 - 1.0)

    return vb0 * c_a


@ntc_ref(article="3.3.2", formula="3.3.3",
         latex=r"c_r = 0{,}75 \sqrt{1 - 0{,}2 \ln\!\bigl[-\ln\!\bigl(1 - \tfrac{1}{T_R}\bigr)\bigr]}")
def wind_return_coefficient(return_period: float) -> float:
    """Coefficiente di ritorno c_r [-].

    NTC18 §3.3.2, Formula [3.3.3]:
        c_r = 0.75 * sqrt(1 - 0.2 * ln(-ln(1 - 1/T_R)))

    Per T_R = 50 anni: c_r ≈ 1.0.

    Parameters
    ----------
    return_period : float
        Periodo di ritorno T_R [anni]. Deve essere >= 1.

    Returns
    -------
    float
        Coefficiente di ritorno c_r [-].

    Raises
    ------
    ValueError
        Se ``return_period`` < 1.
    """
    if return_period < 1.0:
        raise ValueError(
            f"Il periodo di ritorno deve essere >= 1 anno, ricevuto {return_period}."
        )

    return 0.75 * math.sqrt(
        1.0 - 0.2 * math.log(-math.log(1.0 - 1.0 / return_period))
    )


@ntc_ref(article="3.3.2", formula="3.3.2",
         latex=r"v_r = v_b \cdot c_r")
def wind_reference_velocity(
    zone: int,
    altitude: float = 0.0,
    return_period: float = 50.0,
) -> float:
    """Velocita' di riferimento del vento v_r [m/s].

    NTC18 §3.3.2, Formula [3.3.2]:
        v_r = v_b * c_r

    Parameters
    ----------
    zone : int
        Zona del vento (1-9).
    altitude : float
        Altitudine del sito [m]. Default 0.
    return_period : float
        Periodo di ritorno T_R [anni]. Default 50.

    Returns
    -------
    float
        Velocita' di riferimento v_r [m/s].
    """
    v_b = wind_base_velocity(zone, altitude)
    c_r = wind_return_coefficient(return_period)
    return v_b * c_r


@ntc_ref(article="3.3.6", formula="3.3.6",
         latex=r"q_b = \tfrac{1}{2}\,\rho\,v_r^2")
def wind_kinetic_pressure(v_r: float) -> float:
    """Pressione cinetica di riferimento q_b [kN/m^2].

    NTC18 §3.3.6, Formula [3.3.6]:
        q_b = 0.5 * rho * v_r^2

    con rho = 1.25 kg/m^3. Risultato convertito in kN/m^2.

    Parameters
    ----------
    v_r : float
        Velocita' di riferimento del vento [m/s]. Deve essere >= 0.

    Returns
    -------
    float
        Pressione cinetica di riferimento q_b [kN/m^2].

    Raises
    ------
    ValueError
        Se ``v_r`` < 0.
    """
    if v_r < 0:
        raise ValueError("La velocita' non puo' essere negativa.")

    # 0.5 * rho * v^2 -> N/m^2; diviso 1000 -> kN/m^2
    return 0.5 * _RHO_AIR * v_r**2 / 1000.0


@ntc_ref(article="3.3.7", table="Tab.3.3.II", formula="3.3.7",
         latex=r"c_e(z) = k_r^2 \, c_t \, \ln\!\tfrac{z}{z_0}\,\bigl[7 + c_t \, \ln\!\tfrac{z}{z_0}\bigr]")
def wind_exposure_coefficient(
    z: float,
    exposure_category: int,
    c_t: float = 1.0,
) -> float:
    """Coefficiente di esposizione c_e [-].

    NTC18 §3.3.7, Tab. 3.3.II, Formula [3.3.7]:
        c_e(z) = k_r^2 * c_t * ln(z/z_0) * [7 + c_t * ln(z/z_0)]   per z >= z_min
        c_e(z) = c_e(z_min)                                           per z < z_min

    Parameters
    ----------
    z : float
        Altezza sul suolo del punto considerato [m]. Deve essere > 0.
    exposure_category : int
        Categoria di esposizione (1-5), da Tab. 3.3.II / Fig. 3.3.2.
    c_t : float
        Coefficiente di topografia [-]. Default 1.0.

    Returns
    -------
    float
        Coefficiente di esposizione c_e [-].

    Raises
    ------
    ValueError
        Se ``z`` <= 0 o ``exposure_category`` non e' in [1, 5].
    """
    if z <= 0:
        raise ValueError("L'altezza sul suolo deve essere > 0.")
    if exposure_category not in _EXPOSURE_CATEGORIES:
        raise ValueError(
            f"categoria di esposizione {exposure_category} non valida. "
            "Valori ammessi: 1-5 (Tab. 3.3.II)."
        )

    kr, z0, z_min = _EXPOSURE_CATEGORIES[exposure_category]

    z_eff = max(z, z_min)
    ln_z = math.log(z_eff / z0)

    return kr**2 * c_t * ln_z * (7.0 + c_t * ln_z)


# ── Tab. 3.3.III — Classi di rugosità del terreno ────────────────────────────

_TERRAIN_ROUGHNESS: dict[str, tuple[float, float, float]] = {
    #       z_0 [m]  z_min [m]  alpha [-]
    "0":   (0.003,   1.0,       0.12),
    "I":   (0.01,    1.0,       0.14),
    "II":  (0.05,    2.0,       0.16),
    "III": (0.30,    5.0,       0.22),
    "IV":  (1.00,   10.0,       0.28),
}


@ntc_ref(article="3.3.7", table="Tab.3.3.III",
         latex=r"k_r = 0.19\!\left(\frac{z_0}{0.05}\right)^{0.07}")
def wind_terrain_roughness(category: str) -> dict[str, float]:
    """Parametri della classe di rugosita' del terreno (Tab. 3.3.III).

    NTC18 §3.3.7, Tab. 3.3.III.

    Coefficiente di rugosita' k_r calcolato come:
        k_r = 0.19 * (z_0 / 0.05)^0.07

    Parameters
    ----------
    category : str
        Classe di rugosita' del terreno: "0", "I", "II", "III", "IV".

    Returns
    -------
    dict[str, float]
        Dizionario con le chiavi:
        - ``"z_0"``   : lunghezza di rugosita' [m]
        - ``"z_min"`` : altezza minima [m]
        - ``"kr"``    : coefficiente di rugosita' k_r [-]
        - ``"alpha"`` : esponente del profilo di velocita' [-]

    Raises
    ------
    ValueError
        Se ``category`` non e' in {"0", "I", "II", "III", "IV"}.
    """
    if category not in _TERRAIN_ROUGHNESS:
        raise ValueError(
            f"categoria di rugosita' '{category}' non valida. "
            f"Valori ammessi: {', '.join(_TERRAIN_ROUGHNESS.keys())} "
            "(Tab. 3.3.III)."
        )

    z_0, z_min, alpha = _TERRAIN_ROUGHNESS[category]
    kr = 0.19 * (z_0 / 0.05) ** 0.07

    return {"z_0": z_0, "z_min": z_min, "kr": kr, "alpha": alpha}


@ntc_ref(article="3.3.4", formula="3.3.4",
         latex=r"p = q_b \, c_e \, c_p \, c_d")
def wind_pressure(
    q_b: float,
    c_e: float,
    c_p: float,
    c_d: float = 1.0,
) -> float:
    """Pressione del vento p [kN/m^2].

    NTC18 §3.3.4, Formula [3.3.4]:
        p = q_b * c_e * c_p * c_d

    Parameters
    ----------
    q_b : float
        Pressione cinetica di riferimento [kN/m^2].
    c_e : float
        Coefficiente di esposizione [-].
    c_p : float
        Coefficiente di pressione (aerodinamico) [-].
    c_d : float
        Coefficiente dinamico [-]. Default 1.0.

    Returns
    -------
    float
        Pressione del vento p [kN/m^2].
    """
    return q_b * c_e * c_p * c_d


@ntc_ref(article="3.3.5", formula="3.3.5",
         latex=r"p_f = q_b \, c_e \, c_f")
def wind_friction_action(
    q_b: float,
    c_e: float,
    c_f: float,
) -> float:
    """Azione tangente del vento p_f [kN/m^2].

    NTC18 §3.3.5, Formula [3.3.5]:
        p_f = q_b * c_e * c_f

    Parameters
    ----------
    q_b : float
        Pressione cinetica di riferimento [kN/m^2].
    c_e : float
        Coefficiente di esposizione [-].
    c_f : float
        Coefficiente d'attrito [-].

    Returns
    -------
    float
        Azione tangente del vento p_f [kN/m^2].
    """
    return q_b * c_e * c_f
