"""Progettazione per azioni sismiche — NTC18 Cap. 7.

Regole generali, costruzioni in c.a., acciaio, composte,
legno, muratura. Criteri di gerarchia delle resistenze.

Unita':
- Forze: [kN]
- Momenti: [kNm]
- Accelerazioni: [m/s^2]
- Periodi: [s]
- Spostamenti: [m]
- Coefficienti: [-]
"""

from __future__ import annotations

import math

import numpy as np

from pyntc.core.reference import ntc_ref


# ══════════════════════════════════════════════════════════════════════════════
# §7.2 — CRITERI GENERALI DI PROGETTAZIONE
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(article="7.2.3", formula="7.2.1")
def seismic_force_nonstructural(
    S_a: float, W_a: float, q_a: float
) -> float:
    """Forza sismica orizzontale su elemento non strutturale [kN].

    NTC18 §7.2.3, Formula [7.2.1]:
        F_a = S_a * W_a / q_a

    Parameters
    ----------
    S_a : float
        Accelerazione massima adimensionalizzata [-].
    W_a : float
        Peso dell'elemento [kN].
    q_a : float
        Fattore di comportamento dell'elemento [-].

    Returns
    -------
    float
        Forza sismica orizzontale F_a [kN].
    """
    if q_a <= 0:
        raise ValueError(f"q_a deve essere > 0, ricevuto {q_a}")
    if W_a < 0:
        raise ValueError(f"W_a deve essere >= 0, ricevuto {W_a}")
    return S_a * W_a / q_a


# ══════════════════════════════════════════════════════════════════════════════
# §7.3.1 — FATTORE DI COMPORTAMENTO
# ══════════════════════════════════════════════════════════════════════════════


# Tab. 7.3.II — Valori massimi di q_0
# Struttura: (q_0_base_CDA, usa_alpha_CDA, q_0_base_CDB, usa_alpha_CDB)
# usa_alpha: "alpha" -> moltiplica per alpha_u/alpha_1
#            "lambda" -> moltiplica per lambda (ponti)
#            None -> valore fisso
_Q0_TABLE: dict[str, dict[str, tuple[float, str | None]]] = {
    # ── Costruzioni di calcestruzzo (§7.4.3.2) ──
    "rc_frame": {
        "A": (4.5, "alpha"),
        "B": (3.0, "alpha"),
    },
    "rc_wall_uncoupled": {
        "A": (4.0, "alpha"),
        "B": (3.0, None),
    },
    "rc_torsional": {
        "A": (3.0, None),
        "B": (2.0, None),
    },
    "rc_inverted_pendulum": {
        "A": (2.0, None),
        "B": (1.5, None),
    },
    "rc_inverted_pendulum_framed": {
        "A": (3.5, None),
        "B": (2.5, None),
    },
    # ── Costruzioni con struttura prefabbricata (§7.4.5.1) ──
    "precast_panel": {
        "A": (4.0, "alpha"),
        "B": (3.0, None),
    },
    "precast_cell": {
        "A": (3.0, None),
        "B": (2.0, None),
    },
    "precast_column_hinge": {
        "A": (3.5, None),
        "B": (2.5, None),
    },
    # ── Costruzioni d'acciaio e composte (§7.5.2.2/7.6.2.2) ──
    "steel_frame": {
        "A": (5.0, "alpha"),
        "B": (4.0, None),
    },
    "steel_braced_eccentric": {
        "A": (4.0, None),
        "B": (4.0, None),
    },
    "steel_braced_concentric_tension": {
        "A": (2.5, None),
        "B": (2.0, None),
    },
    "steel_braced_concentric_v": {
        "A": (2.0, "alpha"),
        "B": (2.0, None),
    },
    "steel_cantilever": {
        "A": (4.0, "alpha"),
        "B": (4.0, None),
    },
    "steel_frame_concentric": {
        "A": (2.0, None),
        "B": (2.0, None),
    },
    "steel_frame_masonry_infill": {
        "A": (2.0, None),
        "B": (2.0, None),
    },
    # ── Costruzioni di legno (§7.7.3) ──
    "timber_light_frame_glued": {
        "A": (3.0, None),
        "B": (2.0, None),
    },
    "timber_portal_hyperstat": {
        "A": (4.0, None),
        "B": (2.5, None),
    },
    "timber_light_frame_nailed": {
        "A": (5.0, None),
        "B": (3.0, None),
    },
    "timber_truss": {
        "A": (2.5, None),
        "B": (2.5, None),
    },
    "timber_isostatic": {
        "A": (1.5, None),
        "B": (1.5, None),
    },
    # ── Costruzioni di muratura (§7.8.1.3) — no distinzione CD ──
    "masonry_ordinary": {
        "A": (1.75, "alpha"),
        "B": (1.75, "alpha"),
    },
    "masonry_reinforced": {
        "A": (2.5, "alpha"),
        "B": (2.5, "alpha"),
    },
    "masonry_reinforced_capacity": {
        "A": (3.0, "alpha"),
        "B": (3.0, "alpha"),
    },
    "masonry_confined": {
        "A": (2.0, "alpha"),
        "B": (2.0, "alpha"),
    },
    "masonry_confined_capacity": {
        "A": (3.0, "alpha"),
        "B": (3.0, "alpha"),
    },
    # ── Ponti (§7.9.2.1) ──
    "bridge_rc_vertical": {
        "A": (3.5, "lambda"),
        "B": (1.5, None),
    },
    "bridge_rc_inclined": {
        "A": (2.1, "lambda"),
        "B": (1.2, None),
    },
    "bridge_steel_vertical": {
        "A": (3.5, None),
        "B": (1.5, None),
    },
    "bridge_steel_inclined": {
        "A": (2.0, None),
        "B": (1.2, None),
    },
    "bridge_steel_concentric": {
        "A": (2.5, None),
        "B": (1.5, None),
    },
    "bridge_steel_eccentric": {
        "A": (3.5, None),
        "B": (1.0, None),  # "-" in tabella, assunto 1.0
    },
    "bridge_abutment": {
        "A": (1.5, None),
        "B": (1.5, None),
    },
    "bridge_abutment_soil": {
        "A": (1.0, None),
        "B": (1.0, None),
    },
}


@ntc_ref(article="7.3.1", table="Tab.7.3.II")
def behavior_factor_base(
    structural_type: str,
    ductility_class: str = "B",
    *,
    alpha_ratio: float = 1.0,
    lambda_factor: float = 1.0,
) -> float:
    """Valore base del fattore di comportamento q_0 [-].

    NTC18 §7.3.1, Tab. 7.3.II.

    Parameters
    ----------
    structural_type : str
        Tipologia strutturale (es. "rc_frame", "steel_frame", "masonry_ordinary").
    ductility_class : str
        Classe di duttilita': "A" o "B".
    alpha_ratio : float
        Rapporto alpha_u / alpha_1 [-], default 1.0.
    lambda_factor : float
        Fattore lambda per ponti (§7.9.2.1) [-], default 1.0.

    Returns
    -------
    float
        Valore base q_0 [-].
    """
    if structural_type not in _Q0_TABLE:
        raise ValueError(
            f"Tipologia strutturale '{structural_type}' non riconosciuta. "
            f"Valori ammessi: {sorted(_Q0_TABLE.keys())}"
        )
    if ductility_class not in ("A", "B"):
        raise ValueError(
            f"Classe di duttilita' deve essere 'A' o 'B', ricevuto '{ductility_class}'"
        )

    q0_base, multiplier_type = _Q0_TABLE[structural_type][ductility_class]

    if multiplier_type == "alpha":
        return q0_base * alpha_ratio
    elif multiplier_type == "lambda":
        return q0_base * lambda_factor
    else:
        return q0_base


@ntc_ref(article="7.3.1", formula="7.3.1")
def behavior_factor(
    q_0: float, regular_in_height: bool = True
) -> float:
    """Limite superiore del fattore di comportamento q_lim [-].

    NTC18 §7.3.1, Formula [7.3.1]:
        q_lim = q_0 * K_R

    Parameters
    ----------
    q_0 : float
        Valore base del fattore di comportamento [-].
    regular_in_height : bool
        True se la struttura e' regolare in altezza (K_R=1.0),
        False altrimenti (K_R=0.8).

    Returns
    -------
    float
        Fattore di comportamento limite q_lim [-].
    """
    if q_0 <= 0:
        raise ValueError(f"q_0 deve essere > 0, ricevuto {q_0}")
    K_R = 1.0 if regular_in_height else 0.8
    return q_0 * K_R


@ntc_ref(article="7.3.1", formula="7.3.2")
def behavior_factor_nondissipative(q_cdb: float) -> float:
    """Fattore di comportamento per strutture non dissipative [-].

    NTC18 §7.3.1, Formula [7.3.2]:
        1 <= q_ND = (2/3) * q_CD"B" <= 1.5

    Parameters
    ----------
    q_cdb : float
        Valore minimo relativo alla CD"B" (Tab. 7.3.II) [-].

    Returns
    -------
    float
        Fattore di comportamento q_ND [-].
    """
    if q_cdb <= 0:
        raise ValueError(f"q_cdb deve essere > 0, ricevuto {q_cdb}")
    q_nd = (2.0 / 3.0) * q_cdb
    return max(1.0, min(q_nd, 1.5))


# ══════════════════════════════════════════════════════════════════════════════
# §7.3.1 — EFFETTI P-DELTA
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(article="7.3.1", formula="7.3.3")
def pdelta_sensitivity(
    P: float, d_r: float, V: float, h: float
) -> tuple[float, str, float]:
    """Coefficiente di sensibilita' agli effetti del secondo ordine [-].

    NTC18 §7.3.1, Formula [7.3.3]:
        theta = P * d_r / (V * h)

    Parameters
    ----------
    P : float
        Carico verticale totale dell'orizzontamento [kN].
    d_r : float
        Spostamento di interpiano allo SLV [m].
    V : float
        Forza orizzontale totale all'orizzontamento [kN].
    h : float
        Altezza di interpiano [m].

    Returns
    -------
    tuple[float, str, float]
        - theta: coefficiente di sensibilita' [-]
        - action: "negligible" | "amplify" | "nonlinear_required"
        - factor: fattore di amplificazione (1.0 se negligible o nonlinear)
    """
    if V == 0:
        raise ValueError("V (forza orizzontale) non puo' essere zero")
    if h <= 0:
        raise ValueError(f"h deve essere > 0, ricevuto {h}")

    theta = P * d_r / (V * h)

    if theta > 0.3:
        raise ValueError(
            f"theta = {theta:.4f} > 0.3: il valore non e' ammesso (NTC18 §7.3.1)"
        )

    if theta < 0.1:
        return theta, "negligible", 1.0
    elif theta <= 0.2:
        return theta, "amplify", 1.0 / (1.0 - theta)
    else:
        # 0.2 < theta <= 0.3
        return theta, "nonlinear_required", 1.0 / (1.0 - theta)


# ══════════════════════════════════════════════════════════════════════════════
# §7.3.3.1 — ANALISI LINEARE DINAMICA: CQC
# ══════════════════════════════════════════════════════════════════════════════


def _cqc_correlation(beta: float, xi: float) -> float:
    """Coefficiente di correlazione CQC per smorzamento uguale [7.3.5b].

    rho_ij = 8*xi^2*(1+beta)*beta^(3/2) / [(1-beta^2)^2 + 4*xi^2*beta*(1+beta)^2]
    """
    num = 8.0 * xi**2 * (1.0 + beta) * beta**1.5
    den = (1.0 - beta**2) ** 2 + 4.0 * xi**2 * beta * (1.0 + beta) ** 2
    if den == 0:
        return 1.0
    return num / den


@ntc_ref(article="7.3.3.1", formula="7.3.4")
def cqc_modal_combination(
    effects: np.ndarray,
    periods: np.ndarray,
    damping: float = 0.05,
) -> float:
    """Combinazione quadratica completa (CQC) degli effetti modali.

    NTC18 §7.3.3.1, Formula [7.3.4]:
        E = sqrt(sum_i sum_j rho_ij * E_i * E_j)

    con rho_ij da [7.3.5b] (smorzamento uguale per tutti i modi).

    Parameters
    ----------
    effects : np.ndarray
        Effetti modali E_i (uno per modo).
    periods : np.ndarray
        Periodi modali T_i [s] (uno per modo).
    damping : float
        Rapporto di smorzamento viscoso xi [-], default 0.05 (5%).

    Returns
    -------
    float
        Effetto combinato CQC.
    """
    effects = np.asarray(effects, dtype=float)
    periods = np.asarray(periods, dtype=float)

    if effects.size == 0:
        raise ValueError("effects non puo' essere vuoto")
    if effects.shape != periods.shape:
        raise ValueError(
            f"effects e periods devono avere la stessa dimensione: "
            f"{effects.shape} != {periods.shape}"
        )

    n = effects.size
    if n == 1:
        return float(abs(effects[0]))

    # Matrice di correlazione
    result = 0.0
    for i in range(n):
        for j in range(n):
            if i == j:
                rho = 1.0
            else:
                # beta = T_j / T_i (oppure T_i / T_j: il risultato e' simmetrico)
                beta = periods[j] / periods[i]
                rho = _cqc_correlation(beta, damping)
            result += rho * effects[i] * effects[j]

    return math.sqrt(result)


# ══════════════════════════════════════════════════════════════════════════════
# §7.3.3.2 — ANALISI LINEARE STATICA
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(article="7.3.3.2", formula="7.3.6")
def approximate_period(d: float) -> float:
    """Periodo fondamentale approssimato [s].

    NTC18 §7.3.3.2, Formula [7.3.6]:
        T_1 = 2 * sqrt(d)

    Parameters
    ----------
    d : float
        Spostamento laterale elastico del punto piu' alto [m].

    Returns
    -------
    float
        Periodo approssimato T_1 [s].
    """
    if d < 0:
        raise ValueError(f"d deve essere >= 0, ricevuto {d}")
    return 2.0 * math.sqrt(d)


_G = 9.81  # accelerazione di gravita' [m/s^2]


@ntc_ref(article="7.3.3.2", formula="7.3.7")
def equivalent_static_forces(
    S_d_T1: float,
    weights: np.ndarray,
    heights: np.ndarray,
    T_1: float,
    T_c: float,
    n_floors: int,
) -> np.ndarray:
    """Forze statiche equivalenti per analisi lineare statica [kN].

    NTC18 §7.3.3.2, Formula [7.3.7]:
        F_i = F_h * z_i * W_i / sum(z_j * W_j)
    con F_h = S_d(T_1) * W * lambda / g

    Parameters
    ----------
    S_d_T1 : float
        Ordinata dello spettro di progetto al periodo T_1 [m/s^2].
    weights : np.ndarray
        Pesi delle masse W_i [kN].
    heights : np.ndarray
        Quote delle masse z_i rispetto al piano di fondazione [m].
    T_1 : float
        Periodo fondamentale nella direzione in esame [s].
    T_c : float
        Periodo di inizio del tratto a velocita' costante dello spettro [s].
    n_floors : int
        Numero di orizzontamenti della costruzione.

    Returns
    -------
    np.ndarray
        Forze statiche equivalenti F_i [kN].
    """
    weights = np.asarray(weights, dtype=float)
    heights = np.asarray(heights, dtype=float)

    if weights.shape != heights.shape:
        raise ValueError(
            f"weights e heights devono avere la stessa dimensione: "
            f"{weights.shape} != {heights.shape}"
        )

    # lambda = 0.85 se T_1 < 2*T_c e almeno 3 orizzontamenti
    lam = 0.85 if (T_1 < 2.0 * T_c and n_floors >= 3) else 1.0

    W_total = float(np.sum(weights))
    F_h = S_d_T1 * W_total * lam / _G

    z_W = heights * weights
    z_W_sum = float(np.sum(z_W))

    return F_h * z_W / z_W_sum


# ══════════════════════════════════════════════════════════════════════════════
# §7.3.3.3 — SPOSTAMENTI E DUTTILITA'
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(article="7.3.3.3", formula="7.3.8")
def displacement_ductility(
    q: float, T_1: float, T_c: float
) -> float:
    """Fattore di duttilita' in spostamento mu_d [-].

    NTC18 §7.3.3.3, Formule [7.3.8]-[7.3.9]:
        d_e = +/- mu_d * d_te
        mu_d = q                         se T_1 >= T_c
        mu_d = 1 + (q-1) * T_c / T_1    se T_1 < T_c
        mu_d <= 5*q - 4

    Parameters
    ----------
    q : float
        Fattore di comportamento [-].
    T_1 : float
        Periodo fondamentale della struttura [s].
    T_c : float
        Periodo di inizio del tratto a velocita' costante [s].

    Returns
    -------
    float
        Fattore di duttilita' mu_d [-].
    """
    if q < 1.0:
        raise ValueError(f"q deve essere >= 1.0, ricevuto {q}")
    if T_1 <= 0:
        raise ValueError(f"T_1 deve essere > 0, ricevuto {T_1}")

    if T_1 >= T_c:
        mu_d = q
    else:
        mu_d = 1.0 + (q - 1.0) * T_c / T_1

    cap = 5.0 * q - 4.0
    return min(mu_d, cap)


# ══════════════════════════════════════════════════════════════════════════════
# §7.3.5 — COMBINAZIONE DIREZIONALE
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(article="7.3.5", formula="7.3.10")
def seismic_directional_combination(
    E_x: float, E_y: float, E_z: float = 0.0
) -> tuple[float, float, float]:
    """Combinazione direzionale delle componenti sismiche.

    NTC18 §7.3.5, Formula [7.3.10]:
        1.00*E_x + 0.30*E_y + 0.30*E_z
    con permutazione circolare dei coefficienti.

    Parameters
    ----------
    E_x : float
        Effetto della componente sismica X (>=0).
    E_y : float
        Effetto della componente sismica Y (>=0).
    E_z : float
        Effetto della componente sismica Z (>=0), default 0.

    Returns
    -------
    tuple[float, float, float]
        Le tre combinazioni direzionali.
    """
    if E_x < 0 or E_y < 0 or E_z < 0:
        raise ValueError("Gli effetti sismici devono essere >= 0")

    c1 = 1.00 * E_x + 0.30 * E_y + 0.30 * E_z
    c2 = 0.30 * E_x + 1.00 * E_y + 0.30 * E_z
    c3 = 0.30 * E_x + 0.30 * E_y + 1.00 * E_z
    return c1, c2, c3


# ══════════════════════════════════════════════════════════════════════════════
# §7.4 — COSTRUZIONI IN CALCESTRUZZO ARMATO
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(article="7.4.4.1.2", formula="7.4.3")
def curvature_ductility_demand(
    q_0: float, T_1: float, T_c: float
) -> float:
    """Domanda di duttilita' in curvatura mu_phi0 [-].

    NTC18 §7.4.4.1.2, Formula [7.4.3]:
        mu_phi0 = 1.2*(2*q_0 - 1)          se T_1 >= T_c
        mu_phi0 = 1 + 2*(q_0-1)*T_c/T_1    se T_1 < T_c

    Parameters
    ----------
    q_0 : float
        Valore base del fattore di comportamento [-].
    T_1 : float
        Periodo fondamentale della struttura [s].
    T_c : float
        Periodo di inizio del tratto a velocita' costante [s].

    Returns
    -------
    float
        Domanda di duttilita' in curvatura mu_phi0 [-].
    """
    if q_0 < 1.0:
        raise ValueError(f"q_0 deve essere >= 1.0, ricevuto {q_0}")
    if T_1 <= 0:
        raise ValueError(f"T_1 deve essere > 0, ricevuto {T_1}")

    if T_1 >= T_c:
        return 1.2 * (2.0 * q_0 - 1.0)
    else:
        return 1.0 + 2.0 * (q_0 - 1.0) * T_c / T_1


@ntc_ref(article="7.4.4.2.1", formula="7.4.4")
def capacity_design_columns(
    M_c: np.ndarray,
    M_b: np.ndarray,
    gamma_Rd: float,
) -> tuple[bool, float]:
    """Verifica di gerarchia delle resistenze ai nodi trave-pilastro.

    NTC18 §7.4.4.2.1, Formula [7.4.4]:
        sum(M_c,Rd) >= gamma_Rd * sum(M_b,Rd)

    Parameters
    ----------
    M_c : np.ndarray
        Capacita' a flessione dei pilastri convergenti nel nodo [kNm].
    M_b : np.ndarray
        Capacita' a flessione delle travi convergenti nel nodo [kNm].
    gamma_Rd : float
        Coefficiente di sovraresistenza (Tab. 7.2.1) [-].

    Returns
    -------
    tuple[bool, float]
        - satisfied: True se la verifica e' soddisfatta
        - ratio: sum(M_c) / (gamma_Rd * sum(M_b)) [-]
    """
    if gamma_Rd <= 0:
        raise ValueError(f"gamma_Rd deve essere > 0, ricevuto {gamma_Rd}")

    sum_Mc = float(np.sum(M_c))
    sum_Mb = float(np.sum(M_b))
    demand = gamma_Rd * sum_Mb
    ratio = sum_Mc / demand
    return ratio >= 1.0, ratio


# ══════════════════════════════════════════════════════════════════════════════
# §7.11 — OPERE E SISTEMI GEOTECNICI
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(article="7.11.3.5.2", formula="7.11.3")
def pseudostatic_coefficients(
    a_g: float,
    S_s: float,
    S_t: float,
    beta_s: float,
    g: float = 9.81,
) -> tuple[float, float, float]:
    """Coefficienti sismici pseudostatici per stabilita' dei pendii.

    NTC18 §7.11.3.5.2, Formule [7.11.3]-[7.11.5]:
        a_max = S_s * S_t * a_g        [7.11.5]
        k_h   = beta_s * a_max / g      [7.11.3]
        k_v   = 0.5 * k_h               [7.11.4]

    Parameters
    ----------
    a_g : float
        Accelerazione orizzontale massima su sito rigido [m/s^2].
    S_s : float
        Coefficiente di amplificazione stratigrafica [-].
    S_t : float
        Coefficiente di amplificazione topografica [-].
    beta_s : float
        Coefficiente di riduzione dell'accelerazione massima [-].
    g : float
        Accelerazione di gravita' [m/s^2], default 9.81.

    Returns
    -------
    tuple[float, float, float]
        - k_h: coefficiente sismico orizzontale [-]
        - k_v: coefficiente sismico verticale [-]
        - a_max: accelerazione massima attesa al sito [m/s^2]
    """
    if a_g < 0:
        raise ValueError(f"a_g deve essere >= 0, ricevuto {a_g}")

    a_max = S_s * S_t * a_g
    k_h = beta_s * a_max / g
    k_v = 0.5 * k_h
    return k_h, k_v, a_max
