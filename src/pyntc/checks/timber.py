"""Verifiche costruzioni di legno — NTC18 §4.4.

Proprieta' dei materiali, resistenze di calcolo, verifiche SLU
(trazione, compressione, flessione, taglio, instabilita'),
verifiche SLE (deformabilita').
"""

from __future__ import annotations

import numpy as np

from pyntc.core.reference import ntc_ref


# ---------------------------------------------------------------------------
# Tabelle interne
# ---------------------------------------------------------------------------

# Tab. 4.4.III — Coefficienti parziali gamma_M
# Formato: {material: (standard, controlled)}
_GAMMA_M: dict[str, tuple[float, float]] = {
    "solid": (1.50, 1.45),
    "glulam": (1.45, 1.35),
    "lvl": (1.40, 1.30),
    "panels": (1.50, 1.40),
    "connections": (1.50, 1.40),
    "exceptional": (1.00, 1.00),
}

# Tab. 4.4.IV — Coefficiente k_mod
# Chiave: (material_group, service_class, load_duration)
# Gruppi materiale: "solid_glulam_lvl", "plywood", "osb3", "particleboard",
#                   "fibreboard_hard"
_KMOD: dict[tuple[str, int, str], float] = {}

# Legno massiccio, lamellare, LVL
for _sc, _vals in [
    (1, {"permanent": 0.60, "long_term": 0.70, "medium_term": 0.80,
         "short_term": 0.90, "instantaneous": 1.10}),
    (2, {"permanent": 0.60, "long_term": 0.70, "medium_term": 0.80,
         "short_term": 0.90, "instantaneous": 1.10}),
    (3, {"permanent": 0.50, "long_term": 0.55, "medium_term": 0.65,
         "short_term": 0.70, "instantaneous": 0.90}),
]:
    for _dur, _v in _vals.items():
        _KMOD[("solid_glulam_lvl", _sc, _dur)] = _v

# Compensato (plywood)
for _sc, _vals in [
    (1, {"permanent": 0.60, "long_term": 0.70, "medium_term": 0.80,
         "short_term": 0.90, "instantaneous": 1.10}),
    (2, {"permanent": 0.60, "long_term": 0.70, "medium_term": 0.80,
         "short_term": 0.90, "instantaneous": 1.10}),
    (3, {"permanent": 0.50, "long_term": 0.55, "medium_term": 0.65,
         "short_term": 0.70, "instantaneous": 0.90}),
]:
    for _dur, _v in _vals.items():
        _KMOD[("plywood", _sc, _dur)] = _v

# OSB/3, OSB/4
for _sc, _vals in [
    (1, {"permanent": 0.40, "long_term": 0.50, "medium_term": 0.60,
         "short_term": 0.70, "instantaneous": 0.90}),
    (2, {"permanent": 0.30, "long_term": 0.40, "medium_term": 0.50,
         "short_term": 0.70, "instantaneous": 0.90}),
]:
    for _dur, _v in _vals.items():
        _KMOD[("osb3", _sc, _dur)] = _v

# Pannelli di particelle (particleboard) — tipo P5/P7
for _sc, _vals in [
    (1, {"permanent": 0.30, "long_term": 0.45, "medium_term": 0.65,
         "short_term": 0.85, "instantaneous": 1.10}),
    (2, {"permanent": 0.20, "long_term": 0.30, "medium_term": 0.45,
         "short_term": 0.65, "instantaneous": 0.90}),
]:
    for _dur, _v in _vals.items():
        _KMOD[("particleboard", _sc, _dur)] = _v

# Pannelli di fibra duro (fibreboard_hard) — tipo HB.HLA2
for _sc, _vals in [
    (1, {"permanent": 0.30, "long_term": 0.45, "medium_term": 0.65,
         "short_term": 0.85, "instantaneous": 1.10}),
    (2, {"permanent": 0.20, "long_term": 0.30, "medium_term": 0.45,
         "short_term": 0.65, "instantaneous": 0.90}),
]:
    for _dur, _v in _vals.items():
        _KMOD[("fibreboard_hard", _sc, _dur)] = _v


def _kmod_group(material: str) -> str:
    """Mappa il nome materiale al gruppo k_mod."""
    if material in ("solid", "glulam", "lvl"):
        return "solid_glulam_lvl"
    if material in ("plywood", "osb3", "particleboard", "fibreboard_hard"):
        return material
    raise ValueError(
        f"Materiale '{material}' non riconosciuto per k_mod. "
        "Valori ammessi: solid, glulam, lvl, plywood, osb3, "
        "particleboard, fibreboard_hard."
    )


# Tab. 4.4.V — Coefficiente di deformazione k_def
_KDEF: dict[tuple[str, int], float] = {
    # Legno massiccio, lamellare, LVL
    ("solid_glulam_lvl", 1): 0.60,
    ("solid_glulam_lvl", 2): 0.80,
    ("solid_glulam_lvl", 3): 2.00,
    # Compensato
    ("plywood", 1): 0.80,
    ("plywood", 2): 1.00,
    ("plywood", 3): 2.50,
    # OSB/3
    ("osb3", 1): 1.50,
    ("osb3", 2): 2.25,
    # Pannelli di particelle
    ("particleboard", 1): 2.25,
    ("particleboard", 2): 3.00,
    # Pannelli di fibra duro
    ("fibreboard_hard", 1): 2.25,
    ("fibreboard_hard", 2): 3.00,
}


# ---------------------------------------------------------------------------
# Durate di carico valide
# ---------------------------------------------------------------------------
_VALID_DURATIONS = {
    "permanent", "long_term", "medium_term", "short_term", "instantaneous"
}

_VALID_SERVICE_CLASSES = {1, 2, 3}


# ===========================================================================
# 1. timber_partial_safety_factor — Tab.4.4.III
# ===========================================================================

@ntc_ref(article="4.4.6", table="4.4.III")
def timber_partial_safety_factor(
    material: str, *, controlled: bool = False
) -> float:
    """Coefficiente parziale di sicurezza gamma_M per legno [-].

    NTC18 Tab.4.4.III.

    Parameters
    ----------
    material : str
        Tipo di materiale: 'solid', 'glulam', 'lvl', 'panels',
        'connections', 'exceptional'.
    controlled : bool
        Se True, si applicano i valori per produzione controllata.

    Returns
    -------
    float
        gamma_M [-].
    """
    if material not in _GAMMA_M:
        raise ValueError(
            f"Materiale '{material}' non riconosciuto. "
            f"Valori ammessi: {sorted(_GAMMA_M.keys())}."
        )
    std, ctrl = _GAMMA_M[material]
    return ctrl if controlled else std


# ===========================================================================
# 2. timber_kmod — Tab.4.4.IV
# ===========================================================================

@ntc_ref(article="4.4.6", table="4.4.IV")
def timber_kmod(material: str, service_class: int, load_duration: str) -> float:
    """Coefficiente di correzione k_mod [-].

    NTC18 Tab.4.4.IV — Tiene conto dell'effetto della durata del carico
    e dell'umidita' del legno.

    Parameters
    ----------
    material : str
        Tipo di materiale: 'solid', 'glulam', 'lvl', 'plywood', 'osb3',
        'particleboard', 'fibreboard_hard'.
    service_class : int
        Classe di servizio (1, 2 o 3).
    load_duration : str
        Classe di durata del carico: 'permanent', 'long_term',
        'medium_term', 'short_term', 'instantaneous'.

    Returns
    -------
    float
        k_mod [-].
    """
    if service_class not in _VALID_SERVICE_CLASSES:
        raise ValueError(
            f"Classe di servizio {service_class} non valida. "
            "Valori ammessi: 1, 2, 3."
        )
    if load_duration not in _VALID_DURATIONS:
        raise ValueError(
            f"Durata del carico '{load_duration}' non valida. "
            f"Valori ammessi: {sorted(_VALID_DURATIONS)}."
        )
    group = _kmod_group(material)
    key = (group, service_class, load_duration)
    if key not in _KMOD:
        raise ValueError(
            f"Combinazione materiale='{material}', classe_servizio={service_class}, "
            f"durata='{load_duration}' non prevista dalla norma."
        )
    return _KMOD[key]


# ===========================================================================
# 3. timber_kdef — Tab.4.4.V
# ===========================================================================

@ntc_ref(article="4.4.7", table="4.4.V")
def timber_kdef(material: str, service_class: int) -> float:
    """Coefficiente di deformazione k_def [-].

    NTC18 Tab.4.4.V — Per il calcolo della deformazione finale.

    Parameters
    ----------
    material : str
        Tipo di materiale.
    service_class : int
        Classe di servizio (1, 2 o 3).

    Returns
    -------
    float
        k_def [-].
    """
    if service_class not in _VALID_SERVICE_CLASSES:
        raise ValueError(
            f"Classe di servizio {service_class} non valida. "
            "Valori ammessi: 1, 2, 3."
        )
    group = _kmod_group(material)
    key = (group, service_class)
    if key not in _KDEF:
        raise ValueError(
            f"Combinazione materiale='{material}', classe_servizio={service_class} "
            "non prevista dalla norma."
        )
    return _KDEF[key]


# ===========================================================================
# 4. timber_design_strength — [4.4.1]
# ===========================================================================

@ntc_ref(article="4.4.6", formula="4.4.1")
def timber_design_strength(X_k: float, k_mod: float, gamma_M: float) -> float:
    """Resistenza di progetto X_d = k_mod * X_k / gamma_M [N/mm^2].

    NTC18 [4.4.1].

    Parameters
    ----------
    X_k : float
        Resistenza caratteristica [N/mm^2].
    k_mod : float
        Coefficiente di correzione [-].
    gamma_M : float
        Coefficiente parziale di sicurezza [-].

    Returns
    -------
    float
        Resistenza di progetto X_d [N/mm^2].
    """
    if X_k < 0.0:
        raise ValueError("La resistenza caratteristica X_k non puo' essere negativa.")
    if gamma_M <= 0.0:
        raise ValueError("Il coefficiente gamma_M deve essere positivo.")
    return k_mod * X_k / gamma_M


# ===========================================================================
# 5. timber_long_term_modulus — §4.4.7
# ===========================================================================

@ntc_ref(article="4.4.7")
def timber_long_term_modulus(E_mean: float, k_def: float) -> float:
    """Modulo elastico a lungo termine E_fin = E_mean / (1 + k_def) [N/mm^2].

    NTC18 §4.4.7 — Per il calcolo delle deformazioni finali.

    Parameters
    ----------
    E_mean : float
        Modulo elastico medio [N/mm^2].
    k_def : float
        Coefficiente di deformazione [-].

    Returns
    -------
    float
        Modulo elastico a lungo termine [N/mm^2].
    """
    return E_mean / (1.0 + k_def)


# ===========================================================================
# 6. timber_km_factor — §4.4.8.1.6
# ===========================================================================

@ntc_ref(article="4.4.8.1.6")
def timber_km_factor(section: str) -> float:
    """Coefficiente k_m per flessione deviata [-].

    NTC18 §4.4.8.1.6 — Ridistribuzione tensioni nella sezione.

    Parameters
    ----------
    section : str
        Tipo di sezione: 'rectangular', 'circular', 'other'.

    Returns
    -------
    float
        k_m [-].
    """
    _valid = {"rectangular", "circular", "other"}
    if section not in _valid:
        raise ValueError(
            f"Sezione '{section}' non riconosciuta. Valori ammessi: {sorted(_valid)}."
        )
    if section == "rectangular":
        return 0.7
    return 1.0


# ===========================================================================
# 7. timber_biaxial_bending_check — [4.4.5a/b]
# ===========================================================================

@ntc_ref(article="4.4.8.1.6", formula="4.4.5")
def timber_biaxial_bending_check(
    sigma_m_y_d: float,
    f_m_y_d: float,
    sigma_m_z_d: float,
    f_m_z_d: float,
    k_m: float,
) -> tuple[bool, float]:
    """Verifica a flessione deviata [-].

    NTC18 [4.4.5a/b]:
    eq_a: sigma_y/f_y + k_m * sigma_z/f_z <= 1
    eq_b: k_m * sigma_y/f_y + sigma_z/f_z <= 1

    Parameters
    ----------
    sigma_m_y_d, sigma_m_z_d : float
        Tensioni di progetto per flessione nei piani xz e xy [N/mm^2].
    f_m_y_d, f_m_z_d : float
        Resistenze di progetto a flessione [N/mm^2].
    k_m : float
        Coefficiente k_m [-].

    Returns
    -------
    tuple[bool, float]
        (verificata, max_ratio).
    """
    eq_a = sigma_m_y_d / f_m_y_d + k_m * sigma_m_z_d / f_m_z_d
    eq_b = k_m * sigma_m_y_d / f_m_y_d + sigma_m_z_d / f_m_z_d
    ratio = max(eq_a, eq_b)
    return ratio <= 1.0, ratio


# ===========================================================================
# 8. timber_tension_bending_check — [4.4.6a/b]
# ===========================================================================

@ntc_ref(article="4.4.8.1.7", formula="4.4.6")
def timber_tension_bending_check(
    sigma_t_0_d: float,
    f_t_0_d: float,
    sigma_m_y_d: float,
    f_m_y_d: float,
    sigma_m_z_d: float,
    f_m_z_d: float,
    k_m: float,
) -> tuple[bool, float]:
    """Verifica a tensoflessione [-].

    NTC18 [4.4.6a/b]:
    eq_a: sigma_t/f_t + sigma_y/f_y + k_m * sigma_z/f_z <= 1
    eq_b: sigma_t/f_t + k_m * sigma_y/f_y + sigma_z/f_z <= 1

    Parameters
    ----------
    sigma_t_0_d : float
        Tensione di trazione parallela alla fibratura [N/mm^2].
    f_t_0_d : float
        Resistenza di progetto a trazione [N/mm^2].
    sigma_m_y_d, sigma_m_z_d : float
        Tensioni di flessione [N/mm^2].
    f_m_y_d, f_m_z_d : float
        Resistenze di progetto a flessione [N/mm^2].
    k_m : float
        Coefficiente k_m [-].

    Returns
    -------
    tuple[bool, float]
        (verificata, max_ratio).
    """
    t_ratio = sigma_t_0_d / f_t_0_d
    eq_a = t_ratio + sigma_m_y_d / f_m_y_d + k_m * sigma_m_z_d / f_m_z_d
    eq_b = t_ratio + k_m * sigma_m_y_d / f_m_y_d + sigma_m_z_d / f_m_z_d
    ratio = max(eq_a, eq_b)
    return ratio <= 1.0, ratio


# ===========================================================================
# 9. timber_compression_bending_check — [4.4.7a/b]
# ===========================================================================

@ntc_ref(article="4.4.8.1.8", formula="4.4.7")
def timber_compression_bending_check(
    sigma_c_0_d: float,
    f_c_0_d: float,
    sigma_m_y_d: float,
    f_m_y_d: float,
    sigma_m_z_d: float,
    f_m_z_d: float,
    k_m: float,
) -> tuple[bool, float]:
    """Verifica a pressoflessione [-].

    NTC18 [4.4.7a/b] — Il termine di compressione e' al quadrato:
    eq_a: (sigma_c/f_c)^2 + sigma_y/f_y + k_m * sigma_z/f_z <= 1
    eq_b: (sigma_c/f_c)^2 + k_m * sigma_y/f_y + sigma_z/f_z <= 1

    Parameters
    ----------
    sigma_c_0_d : float
        Tensione di compressione parallela [N/mm^2].
    f_c_0_d : float
        Resistenza di progetto a compressione [N/mm^2].
    sigma_m_y_d, sigma_m_z_d : float
        Tensioni di flessione [N/mm^2].
    f_m_y_d, f_m_z_d : float
        Resistenze di progetto a flessione [N/mm^2].
    k_m : float
        Coefficiente k_m [-].

    Returns
    -------
    tuple[bool, float]
        (verificata, max_ratio).
    """
    c_ratio_sq = (sigma_c_0_d / f_c_0_d) ** 2
    eq_a = c_ratio_sq + sigma_m_y_d / f_m_y_d + k_m * sigma_m_z_d / f_m_z_d
    eq_b = c_ratio_sq + k_m * sigma_m_y_d / f_m_y_d + sigma_m_z_d / f_m_z_d
    ratio = max(eq_a, eq_b)
    return ratio <= 1.0, ratio


# ===========================================================================
# 10. timber_shear_check — [4.4.8]
# ===========================================================================

@ntc_ref(article="4.4.8.1.9", formula="4.4.8")
def timber_shear_check(tau_d: float, f_v_d: float) -> tuple[bool, float]:
    """Verifica a taglio [-].

    NTC18 [4.4.8]: tau_d <= f_v,d.

    Parameters
    ----------
    tau_d : float
        Tensione tangenziale di progetto [N/mm^2].
    f_v_d : float
        Resistenza di progetto a taglio [N/mm^2].

    Returns
    -------
    tuple[bool, float]
        (verificata, ratio tau_d/f_v_d).
    """
    ratio = tau_d / f_v_d
    return ratio <= 1.0, ratio


# ===========================================================================
# 11. timber_torsion_shape_factor — §4.4.8.1.10
# ===========================================================================

@ntc_ref(article="4.4.8.1.10")
def timber_torsion_shape_factor(
    section: str, *, h: float | None = None, b: float | None = None
) -> float:
    """Coefficiente di forma k_sh per torsione [-].

    NTC18 §4.4.8.1.10:
    - Sezione circolare piena: k_sh = 1.2
    - Sezione rettangolare piena: k_sh = min(1 + 0.15*h/b, 2.0), con b <= h
    - Altro: k_sh = 1.0

    Parameters
    ----------
    section : str
        'circular', 'rectangular', 'other'.
    h, b : float, optional
        Dimensioni della sezione rettangolare [mm]. h >= b.

    Returns
    -------
    float
        k_sh [-].
    """
    if section == "circular":
        return 1.2
    if section == "rectangular":
        if h is None or b is None:
            raise ValueError(
                "Per sezione rettangolare servono h e b."
            )
        # Assicura h >= b
        h_val, b_val = max(h, b), min(h, b)
        return min(1.0 + 0.15 * h_val / b_val, 2.0)
    if section == "other":
        return 1.0
    raise ValueError(
        f"Sezione '{section}' non riconosciuta. "
        "Valori ammessi: 'circular', 'rectangular', 'other'."
    )


# ===========================================================================
# 12. timber_torsion_check — [4.4.9]
# ===========================================================================

@ntc_ref(article="4.4.8.1.10", formula="4.4.9")
def timber_torsion_check(
    tau_tor_d: float, f_v_d: float, k_sh: float
) -> tuple[bool, float]:
    """Verifica a torsione [-].

    NTC18 [4.4.9]: tau_tor,d <= k_sh * f_v,d.

    Parameters
    ----------
    tau_tor_d : float
        Tensione tangenziale di torsione [N/mm^2].
    f_v_d : float
        Resistenza di progetto a taglio [N/mm^2].
    k_sh : float
        Coefficiente di forma [-].

    Returns
    -------
    tuple[bool, float]
        (verificata, ratio tau_tor_d / (k_sh * f_v_d)).
    """
    ratio = tau_tor_d / (k_sh * f_v_d)
    return ratio <= 1.0, ratio


# ===========================================================================
# 13. timber_shear_torsion_interaction — [4.4.10]
# ===========================================================================

@ntc_ref(article="4.4.8.1.11", formula="4.4.10")
def timber_shear_torsion_interaction(
    tau_d: float, f_v_d: float, tau_tor_d: float, k_sh: float
) -> tuple[bool, float]:
    """Verifica interazione taglio-torsione [-].

    NTC18 [4.4.10] (corretto da OCR, coerente con EC5):
    (tau_tor,d / (k_sh * f_v,d))^2 + (tau_d / f_v,d)^2 <= 1

    Parameters
    ----------
    tau_d : float
        Tensione tangenziale di taglio [N/mm^2].
    f_v_d : float
        Resistenza di progetto a taglio [N/mm^2].
    tau_tor_d : float
        Tensione tangenziale di torsione [N/mm^2].
    k_sh : float
        Coefficiente di forma [-].

    Returns
    -------
    tuple[bool, float]
        (verificata, ratio = somma dei termini quadratici).
    """
    ratio = (tau_tor_d / (k_sh * f_v_d)) ** 2 + (tau_d / f_v_d) ** 2
    return ratio <= 1.0, ratio


# ===========================================================================
# 14. timber_beam_critical_factor — [4.4.12]
# ===========================================================================

@ntc_ref(article="4.4.8.2.1", formula="4.4.12")
def timber_beam_critical_factor(lambda_rel_m: float) -> float:
    """Coefficiente riduttivo k_crit,m per instabilita' di trave [-].

    NTC18 [4.4.12]:
    - lambda_rel <= 0.75: k_crit = 1.0
    - 0.75 < lambda_rel <= 1.4: k_crit = 1.56 - 0.75 * lambda_rel
    - lambda_rel > 1.4: k_crit = 1 / lambda_rel^2

    Parameters
    ----------
    lambda_rel_m : float
        Snellezza relativa di trave [-].

    Returns
    -------
    float
        k_crit,m [-].
    """
    if lambda_rel_m < 0.0:
        raise ValueError("La snellezza relativa non puo' essere negativa.")
    if lambda_rel_m <= 0.75:
        return 1.0
    if lambda_rel_m <= 1.4:
        return 1.56 - 0.75 * lambda_rel_m
    return 1.0 / lambda_rel_m**2


# ===========================================================================
# 15. timber_beam_stability_check — [4.4.11]
# ===========================================================================

@ntc_ref(article="4.4.8.2.1", formula="4.4.11")
def timber_beam_stability_check(
    sigma_m_d: float, f_m_d: float, lambda_rel_m: float
) -> tuple[bool, float]:
    """Verifica stabilita' trave (svergolamento) [-].

    NTC18 [4.4.11]: sigma_m,d / (k_crit,m * f_m,d) <= 1.

    Parameters
    ----------
    sigma_m_d : float
        Tensione di flessione di progetto [N/mm^2].
    f_m_d : float
        Resistenza di progetto a flessione [N/mm^2].
    lambda_rel_m : float
        Snellezza relativa di trave [-].

    Returns
    -------
    tuple[bool, float]
        (verificata, ratio).
    """
    k_crit = timber_beam_critical_factor.__wrapped__(lambda_rel_m)
    ratio = sigma_m_d / (k_crit * f_m_d)
    return ratio <= 1.0, ratio


# ===========================================================================
# 16. timber_column_relative_slenderness — [4.4.14]
# ===========================================================================

@ntc_ref(article="4.4.8.2.2", formula="4.4.14")
def timber_column_relative_slenderness(
    lambda_val: float, f_c_0_k: float, E_005: float
) -> float:
    """Snellezza relativa di colonna lambda_rel,c [-].

    NTC18 [4.4.14]: lambda_rel,c = (lambda/pi) * sqrt(f_c,0,k / E_0,05).

    Parameters
    ----------
    lambda_val : float
        Snellezza dell'elemento [-].
    f_c_0_k : float
        Resistenza caratteristica a compressione parallela [N/mm^2].
    E_005 : float
        Modulo elastico caratteristico al 5° frattile [N/mm^2].

    Returns
    -------
    float
        lambda_rel,c [-].
    """
    if lambda_val < 0.0:
        raise ValueError("La snellezza non puo' essere negativa.")
    return (lambda_val / np.pi) * np.sqrt(f_c_0_k / E_005)


# ===========================================================================
# 17. timber_column_critical_factor — [4.4.15]/[4.4.16]
# ===========================================================================

@ntc_ref(article="4.4.8.2.2", formula="4.4.15")
def timber_column_critical_factor(
    lambda_rel_c: float, *, material: str = "solid"
) -> float:
    """Coefficiente riduttivo k_crit,c per instabilita' di colonna [-].

    NTC18 [4.4.15]/[4.4.16]:
    - lambda_rel <= 0.3: k_crit = 1.0
    - altrimenti: k_crit = 1 / (k + sqrt(k^2 - lambda_rel^2))
      con k = 0.5*(1 + beta_c*(lambda_rel - 0.3) + lambda_rel^2)
      beta_c = 0.2 (massiccio), 0.1 (lamellare)

    Parameters
    ----------
    lambda_rel_c : float
        Snellezza relativa di colonna [-].
    material : str
        'solid' (beta_c=0.2) o 'glulam' (beta_c=0.1).

    Returns
    -------
    float
        k_crit,c [-].
    """
    if lambda_rel_c <= 0.3:
        return 1.0

    if material == "solid":
        beta_c = 0.2
    elif material == "glulam":
        beta_c = 0.1
    else:
        raise ValueError(
            f"Materiale '{material}' non riconosciuto. "
            "Valori ammessi: 'solid', 'glulam'."
        )

    k = 0.5 * (1.0 + beta_c * (lambda_rel_c - 0.3) + lambda_rel_c**2)
    return 1.0 / (k + np.sqrt(k**2 - lambda_rel_c**2))


# ===========================================================================
# 18. timber_column_stability_check — [4.4.13]
# ===========================================================================

@ntc_ref(article="4.4.8.2.2", formula="4.4.13")
def timber_column_stability_check(
    sigma_c_0_d: float, f_c_0_d: float, k_crit_c: float
) -> tuple[bool, float]:
    """Verifica stabilita' colonna (instabilita' di colonna) [-].

    NTC18 [4.4.13]: sigma_c,0,d / (k_crit,c * f_c,0,d) <= 1.

    Parameters
    ----------
    sigma_c_0_d : float
        Tensione di compressione di progetto [N/mm^2].
    f_c_0_d : float
        Resistenza di progetto a compressione [N/mm^2].
    k_crit_c : float
        Coefficiente riduttivo per instabilita' [-].

    Returns
    -------
    tuple[bool, float]
        (verificata, ratio).
    """
    ratio = sigma_c_0_d / (k_crit_c * f_c_0_d)
    return ratio <= 1.0, ratio


# ===========================================================================
# 19. timber_deflection_limits — §4.4.7
# ===========================================================================

@ntc_ref(article="4.4.7")
def timber_deflection_limits(
    L: float, check_type: str, *, cantilever: bool = False
) -> float:
    """Limite di freccia ammissibile [mm].

    NTC18 §4.4.7:
    - Trave: L/300 (istantanea), L/200 (finale)
    - Mensola: L/150 (istantanea), L/100 (finale)

    Parameters
    ----------
    L : float
        Luce dell'elemento [mm].
    check_type : str
        'instantaneous' o 'final'.
    cantilever : bool
        True per mensola.

    Returns
    -------
    float
        Freccia limite ammissibile [mm].
    """
    _limits = {
        (False, "instantaneous"): 300.0,
        (False, "final"): 200.0,
        (True, "instantaneous"): 150.0,
        (True, "final"): 100.0,
    }
    key = (cantilever, check_type)
    if key not in _limits:
        raise ValueError(
            f"Tipo di verifica '{check_type}' non valido. "
            "Valori ammessi: 'instantaneous', 'final'."
        )
    return L / _limits[key]


# ===========================================================================
# 20. timber_straightness_limit — §4.4.15
# ===========================================================================

@ntc_ref(article="4.4.15")
def timber_straightness_limit(L: float, material: str) -> float:
    """Limite di rettilineita' per membrature compresse [mm].

    NTC18 §4.4.15:
    - Legno lamellare incollato: L/500
    - Legno massiccio: L/300

    Parameters
    ----------
    L : float
        Distanza tra due vincoli successivi [mm].
    material : str
        'glulam' o 'solid'.

    Returns
    -------
    float
        Scostamento massimo dalla rettilineita' [mm].
    """
    if material == "glulam":
        return L / 500.0
    if material == "solid":
        return L / 300.0
    raise ValueError(
        f"Materiale '{material}' non riconosciuto. "
        "Valori ammessi: 'solid', 'glulam'."
    )
