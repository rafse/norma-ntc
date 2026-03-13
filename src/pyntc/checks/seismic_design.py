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


@ntc_ref(article="7.2.3", formula="7.2.1", latex=r"F_a = \frac{S_a \cdot W_a}{q_a}")
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


@ntc_ref(article="7.3.1", table="Tab.7.3.II", latex=r"\text{Tab.\,7.3.II}")
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


@ntc_ref(article="7.3.1", formula="7.3.1", latex=r"q = q_0 \cdot K_R")
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


@ntc_ref(article="7.3.1", formula="7.3.2", latex=r"1 \le q_{ND} = \frac{2}{3}\,q_{CD\text{B}} \le 1{,}5")
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


@ntc_ref(article="7.3.1", formula="7.3.3", latex=r"\theta = \frac{P \cdot d_r}{V \cdot h}")
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


@ntc_ref(article="7.3.3.1", formula="7.3.4", latex=r"E = \sqrt{\sum_i \sum_j \rho_{ij}\,E_i\,E_j}")
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


@ntc_ref(article="7.3.3.2", formula="7.3.6", latex=r"T_1 = 2\,\sqrt{d}")
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


@ntc_ref(article="7.3.3.2", formula="7.3.7", latex=r"F_i = F_h \,\frac{z_i \, W_i}{\sum_j z_j \, W_j}")
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


@ntc_ref(article="7.3.3.3", formula="7.3.8", latex=r"\mu_d = \begin{cases} q & T_1 \ge T_C \\ 1 + (q-1)\,\frac{T_C}{T_1} & T_1 < T_C \end{cases}")
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


@ntc_ref(article="7.3.5", formula="7.3.10", latex=r"1{,}00\,E_x + 0{,}30\,E_y + 0{,}30\,E_z")
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


@ntc_ref(article="7.4.4.1.2", formula="7.4.3", latex=r"\mu_{\varphi,0} = \begin{cases} 1{,}2\,(2\,q_0 - 1) & T_1 \ge T_C \\ 1 + 2\,(q_0 - 1)\,\frac{T_C}{T_1} & T_1 < T_C \end{cases}")
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


@ntc_ref(article="7.4.4.2.1", formula="7.4.4", latex=r"\sum M_{c,Rd} \ge \gamma_{Rd} \sum M_{b,Rd}")
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
# §7.4 — COSTRUZIONI IN CALCESTRUZZO ARMATO (DETTAGLI E GERARCHIA)
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(
    article="7.4.4.2.1",
    formula="7.4.5",
    latex=r"V_{Ed}\,l_p = \gamma_{Rd}\,(M_{i,d}^s + M_{i,d}^i)",
)
def column_capacity_shear(
    M_top: float,
    M_bot: float,
    l_p: float,
    gamma_Rd: float,
) -> float:
    """Taglio di progetto in capacita' per pilastri sismici [kN].

    NTC18 §7.4.4.2.1, Formula [7.4.5]:
        V_Ed * l_p = gamma_Rd * (M_top + M_bot)
        V_Ed = gamma_Rd * (M_top + M_bot) / l_p

    Parameters
    ----------
    M_top : float
        Capacita' a flessione nella sezione superiore del pilastro [kNm].
    M_bot : float
        Capacita' a flessione nella sezione inferiore del pilastro [kNm].
    l_p : float
        Lunghezza libera del pilastro [m].
    gamma_Rd : float
        Coefficiente di sovraresistenza (Tab. 7.2.1) [-].

    Returns
    -------
    float
        Taglio di progetto V_Ed [kN].
    """
    if l_p <= 0:
        raise ValueError(f"l_p deve essere > 0, ricevuto {l_p}")
    if gamma_Rd <= 0:
        raise ValueError(f"gamma_Rd deve essere > 0, ricevuto {gamma_Rd}")
    if M_top < 0 or M_bot < 0:
        raise ValueError("M_top e M_bot devono essere >= 0 (valori assoluti)")
    return gamma_Rd * (M_top + M_bot) / l_p


@ntc_ref(
    article="7.4.4.3.1",
    formula="7.4.6",
    latex=r"V_{jd} = \gamma_{Rd}\,(A_{s1}+A_{s2})\,f_{yd} - V_C",
)
def beam_column_joint_shear(
    A_s1: float,
    A_s2: float,
    f_yd: float,
    V_C: float,
    gamma_Rd: float,
    *,
    interior: bool = True,
) -> float:
    """Domanda di taglio orizzontale nel nodo trave-pilastro [kN].

    NTC18 §7.4.4.3.1:
        V_jd = gamma_Rd * (A_s1 + A_s2) * f_yd - V_C  [nodi interni, 7.4.6]
        V_jd = gamma_Rd * A_s1 * f_yd - V_C             [nodi esterni, 7.4.7]

    Parameters
    ----------
    A_s1 : float
        Area armatura superiore della trave confluente [m^2].
    A_s2 : float
        Area armatura inferiore della trave confluente [m^2].
    f_yd : float
        Resistenza di snervamento di progetto dell'acciaio [kN/m^2].
    V_C : float
        Forza di taglio nel pilastro al di sopra del nodo [kN].
    gamma_Rd : float
        Coefficiente di sovraresistenza (Tab. 7.2.1) [-].
    interior : bool
        True per nodo interno [7.4.6], False per nodo esterno [7.4.7].

    Returns
    -------
    float
        Domanda di taglio V_jd nel nodo [kN].
    """
    if gamma_Rd <= 0:
        raise ValueError(f"gamma_Rd deve essere > 0, ricevuto {gamma_Rd}")
    if A_s1 < 0 or A_s2 < 0:
        raise ValueError("A_s1 e A_s2 devono essere >= 0")
    if f_yd <= 0:
        raise ValueError(f"f_yd deve essere > 0, ricevuto {f_yd}")

    if interior:
        return gamma_Rd * (A_s1 + A_s2) * f_yd - V_C
    else:
        return gamma_Rd * A_s1 * f_yd - V_C


@ntc_ref(
    article="7.4.4.3.1",
    formula="7.4.8",
    latex=r"V_{jd} \le \eta\,f_{sd}\,b_j\,h_{js}\sqrt{1 - v_d/\eta}",
)
def joint_concrete_compression_check(
    V_jd: float,
    eta: float,
    f_sd: float,
    b_j: float,
    h_js: float,
    v_d: float,
) -> tuple[bool, float]:
    """Verifica compressione del puntone diagonale nel nodo trave-pilastro.

    NTC18 §7.4.4.3.1, Formula [7.4.8]:
        V_jd <= eta * f_sd * b_j * h_js * sqrt(1 - v_d / eta)

    Parameters
    ----------
    V_jd : float
        Domanda di taglio nel nodo [kN].
    eta : float
        Coefficiente riduttivo del calcestruzzo (da [7.4.9]) [-].
    f_sd : float
        Resistenza a compressione di progetto del calcestruzzo [kN/m^2].
    b_j : float
        Larghezza efficace del nodo [m].
    h_js : float
        Distanza tra le giaciture piu' esterne delle armature del pilastro [m].
    v_d : float
        Forza assiale normalizzata nel pilastro al di sopra del nodo [-].

    Returns
    -------
    tuple[bool, float]
        - satisfied: True se la verifica e' soddisfatta
        - ratio: V_jd / V_Rd [-]
    """
    if eta <= 0:
        raise ValueError(f"eta deve essere > 0, ricevuto {eta}")
    if f_sd <= 0:
        raise ValueError(f"f_sd deve essere > 0, ricevuto {f_sd}")
    if b_j <= 0 or h_js <= 0:
        raise ValueError("b_j e h_js devono essere > 0")
    if v_d < 0 or v_d >= eta:
        raise ValueError(
            f"v_d deve essere in [0, eta), ricevuto v_d={v_d}, eta={eta}"
        )

    V_Rd = eta * f_sd * b_j * h_js * math.sqrt(1.0 - v_d / eta)
    ratio = V_jd / V_Rd
    return ratio <= 1.0, ratio


@ntc_ref(
    article="7.4.4.3.1",
    formula="7.4.9",
    latex=r"\eta = a_j \cdot \left(1 - \frac{f_{sk}}{250}\right)",
)
def joint_eta_factor(a_j: float, f_ck: float) -> float:
    """Coefficiente eta per la resistenza a taglio del nodo trave-pilastro [-].

    NTC18 §7.4.4.3.1, Formula [7.4.9]:
        eta = a_j * (1 - f_sk / 250)

    con f_sk espresso in MPa.

    Parameters
    ----------
    a_j : float
        Coefficiente di nodo: 0.60 per nodi interni (CD'A'), 0.48 per esterni.
    f_ck : float
        Resistenza caratteristica del calcestruzzo [MPa].

    Returns
    -------
    float
        Coefficiente eta [-].
    """
    if a_j <= 0:
        raise ValueError(f"a_j deve essere > 0, ricevuto {a_j}")
    if f_ck <= 0:
        raise ValueError(f"f_ck deve essere > 0, ricevuto {f_ck}")
    return a_j * (1.0 - f_ck / 250.0)


@ntc_ref(
    article="7.4.4.3.1",
    formula="7.4.11",
    latex=r"A_{sh}\,f_{ywd} \ge \gamma_{Rd}\,(A_{s1}+A_{s2})\,f_{yd}\,(1-0{,}8v_d)",
)
def joint_horizontal_stirrups(
    A_s1: float,
    A_s2: float,
    f_yd: float,
    gamma_Rd: float,
    v_d: float,
    *,
    interior: bool = True,
) -> float:
    """Armatura orizzontale minima richiesta nel nodo trave-pilastro [m^2].

    NTC18 §7.4.4.3.1:
        A_sh * f_ywd >= gamma_Rd * (A_s1 + A_s2) * f_yd * (1 - 0.8*v_d)
            [nodi interni, 7.4.11]
        A_sh * f_ywd >= gamma_Rd * A_s2 * f_yd * (1 - 0.8*v_d)
            [nodi esterni, 7.4.12]

    Parameters
    ----------
    A_s1 : float
        Area armatura superiore della trave confluente [m^2].
    A_s2 : float
        Area armatura inferiore della trave confluente [m^2].
    f_yd : float
        Resistenza di snervamento di progetto armatura trave [kN/m^2].
    gamma_Rd : float
        Coefficiente di sovraresistenza (Tab. 7.2.1) [-].
    v_d : float
        Forza assiale normalizzata del pilastro [-].
    interior : bool
        True per nodo interno [7.4.11], False per nodo esterno [7.4.12].

    Returns
    -------
    float
        Prodotto minimo A_sh * f_ywd richiesto [kN].
    """
    if gamma_Rd <= 0:
        raise ValueError(f"gamma_Rd deve essere > 0, ricevuto {gamma_Rd}")
    if A_s1 < 0 or A_s2 < 0:
        raise ValueError("A_s1 e A_s2 devono essere >= 0")
    if f_yd <= 0:
        raise ValueError(f"f_yd deve essere > 0, ricevuto {f_yd}")
    if not 0.0 <= v_d <= 1.0:
        raise ValueError(f"v_d deve essere in [0, 1], ricevuto {v_d}")

    factor = 1.0 - 0.8 * v_d
    if interior:
        return gamma_Rd * (A_s1 + A_s2) * f_yd * factor
    else:
        return gamma_Rd * A_s2 * f_yd * factor


@ntc_ref(
    article="7.4.4.5.1",
    formula="7.4.13",
    latex=r"h_{cr} = \max(l_w,\,h_w/6)",
)
def wall_critical_height(
    l_w: float,
    h_w: float,
    n_floors: int,
) -> float:
    """Altezza della zona dissipativa di base delle pareti in c.a. [m].

    NTC18 §7.4.4.5.1, Formula [7.4.13]:
        h_cr = max(l_w, h_w/6)
        con limite: h_cr <= 2*l_w   (n <= 6 piani)
                    h_cr <= h_w     (n >= 7 piani)

    Parameters
    ----------
    l_w : float
        Dimensione maggiore della sezione trasversale della parete [m].
    h_w : float
        Altezza totale della parete [m].
    n_floors : int
        Numero di piani della costruzione.

    Returns
    -------
    float
        Altezza della zona dissipativa h_cr [m].
    """
    if l_w <= 0:
        raise ValueError(f"l_w deve essere > 0, ricevuto {l_w}")
    if h_w <= 0:
        raise ValueError(f"h_w deve essere > 0, ricevuto {h_w}")
    if n_floors < 1:
        raise ValueError(f"n_floors deve essere >= 1, ricevuto {n_floors}")

    h_cr = max(l_w, h_w / 6.0)

    if n_floors <= 6:
        h_cr = min(h_cr, 2.0 * l_w)
    else:
        h_cr = min(h_cr, h_w)

    return h_cr


@ntc_ref(
    article="7.4.6.2.1",
    formula="7.4.26",
    latex=r"\frac{1{,}4}{f_{yk}} < \rho < \rho_{\text{comp}} + \frac{3{,}5}{f_{yk}}",
)
def beam_reinforcement_ratio_limits(
    f_yk: float,
    rho_comp: float,
) -> tuple[float, float]:
    """Limiti del rapporto geometrico di armatura tesa nelle travi sismiche.

    NTC18 §7.4.6.2.1, Formula [7.4.26]:
        1.4 / f_yk < rho < rho_comp + 3.5 / f_yk

    con f_yk espresso in MPa.

    Parameters
    ----------
    f_yk : float
        Tensione caratteristica di snervamento dell'acciaio [MPa].
    rho_comp : float
        Rapporto geometrico dell'armatura compressa [-].

    Returns
    -------
    tuple[float, float]
        - rho_min: limite inferiore del rapporto di armatura tesa [-]
        - rho_max: limite superiore del rapporto di armatura tesa [-]
    """
    if f_yk <= 0:
        raise ValueError(f"f_yk deve essere > 0, ricevuto {f_yk}")
    if rho_comp < 0:
        raise ValueError(f"rho_comp deve essere >= 0, ricevuto {rho_comp}")

    rho_min = 1.4 / f_yk
    rho_max = rho_comp + 3.5 / f_yk
    return rho_min, rho_max


@ntc_ref(
    article="7.4.6.2.2",
    formula="7.4.28",
    latex=r"1\% \le \rho \le 4\%",
)
def column_reinforcement_ratio_check(
    rho: float,
) -> tuple[bool, float, float]:
    """Verifica del rapporto di armatura longitudinale nei pilastri sismici.

    NTC18 §7.4.6.2.2, Formula [7.4.28]:
        1% <= rho <= 4%

    Parameters
    ----------
    rho : float
        Rapporto geometrico di armatura longitudinale del pilastro [-]
        (area armatura / area sezione cls).

    Returns
    -------
    tuple[bool, float, float]
        - satisfied: True se il vincolo e' soddisfatto
        - rho_min: limite inferiore 0.01 [-]
        - rho_max: limite superiore 0.04 [-]
    """
    if rho < 0:
        raise ValueError(f"rho deve essere >= 0, ricevuto {rho}")

    rho_min = 0.01
    rho_max = 0.04
    satisfied = rho_min <= rho <= rho_max
    return satisfied, rho_min, rho_max


@ntc_ref(
    article="7.4.6.2.2",
    formula="7.4.29",
    latex=r"\alpha \cdot \omega_{sd} \ge 30\mu_e \cdot v_d \cdot \varepsilon_{\gamma d} \cdot \frac{b_s}{b_o} - 0{,}035",
)
def column_confinement_requirement(
    mu_e: float,
    v_d: float,
    eps_yd: float,
    b_s: float,
    b_o: float,
    alpha: float,
) -> float:
    """Rapporto meccanico minimo di armatura di confinamento nei pilastri.

    NTC18 §7.4.6.2.2, Formula [7.4.29]:
        alpha * omega_sd >= 30 * mu_e * v_d * eps_yd * (b_s/b_o) - 0.035

    Parameters
    ----------
    mu_e : float
        Domanda di duttilita' in curvatura allo SLC [-].
    v_d : float
        Forza assiale adimensionalizzata di progetto (N_Ed / A_c * f_cd) [-].
    eps_yd : float
        Deformazione di snervamento dell'acciaio [-].
    b_s : float
        Profondita' della sezione trasversale lorda [m].
    b_o : float
        Profondita' del nucleo confinato [m].
    alpha : float
        Coefficiente di efficacia del confinamento [-].

    Returns
    -------
    float
        Valore minimo richiesto di omega_sd [-].
    """
    if mu_e < 1.0:
        raise ValueError(f"mu_e deve essere >= 1.0, ricevuto {mu_e}")
    if not 0.0 < v_d <= 1.0:
        raise ValueError(f"v_d deve essere in (0, 1], ricevuto {v_d}")
    if eps_yd <= 0:
        raise ValueError(f"eps_yd deve essere > 0, ricevuto {eps_yd}")
    if b_o <= 0 or b_s <= 0:
        raise ValueError("b_s e b_o devono essere > 0")
    if alpha <= 0 or alpha > 1.0:
        raise ValueError(f"alpha deve essere in (0, 1], ricevuto {alpha}")

    demand = 30.0 * mu_e * v_d * eps_yd * (b_s / b_o) - 0.035
    omega_sd_min = max(demand, 0.0) / alpha
    return omega_sd_min


@ntc_ref(
    article="7.4.6.2.2",
    formula="7.4.31",
    latex=r"\alpha_n = 1 - \frac{\sum b_{si}^2}{n\,(2\,b_o\,h_o)} \qquad \alpha_s = \left(1-\frac{s}{2b_o}\right)\!\left(1-\frac{s}{2h_o}\right)",
)
def confinement_effectiveness_rectangular(
    b_si_list: list[float],
    b_o: float,
    h_o: float,
    s: float,
) -> tuple[float, float, float]:
    """Coefficiente di efficacia del confinamento per sezione rettangolare [-].

    NTC18 §7.4.6.2.2, Formule [7.4.31a] e [7.4.31b]:
        alpha_n = 1 - sum(b_si^2) / (n * 2 * b_o * h_o)
        alpha_s = (1 - s/(2*b_o)) * (1 - s/(2*h_o))
        alpha = alpha_n * alpha_s

    Parameters
    ----------
    b_si_list : list[float]
        Lista delle distanze tra barre consecutive contenute [m].
    b_o : float
        Larghezza del nucleo confinato (linea media staffe) [m].
    h_o : float
        Altezza del nucleo confinato (linea media staffe) [m].
    s : float
        Passo delle staffe di confinamento [m].

    Returns
    -------
    tuple[float, float, float]
        - alpha_n: coefficiente di efficacia in pianta [-]
        - alpha_s: coefficiente di efficacia in altezza [-]
        - alpha: prodotto alpha_n * alpha_s [-]
    """
    if b_o <= 0 or h_o <= 0:
        raise ValueError("b_o e h_o devono essere > 0")
    if s <= 0:
        raise ValueError(f"s deve essere > 0, ricevuto {s}")
    if len(b_si_list) == 0:
        raise ValueError("b_si_list non puo' essere vuota")

    n = len(b_si_list)
    sum_bsi2 = sum(b ** 2 for b in b_si_list)
    alpha_n = 1.0 - sum_bsi2 / (n * 2.0 * b_o * h_o)
    alpha_n = max(alpha_n, 0.0)

    alpha_s = (1.0 - s / (2.0 * b_o)) * (1.0 - s / (2.0 * h_o))
    alpha_s = max(alpha_s, 0.0)

    return alpha_n, alpha_s, alpha_n * alpha_s


@ntc_ref(
    article="7.4.6.2.4",
    formula="7.4.32",
    latex=r"\alpha \cdot \omega_{wd} \ge 30\mu_k \cdot (v_g+\omega_v) \cdot \varepsilon_{y,d} \cdot \frac{b_x}{b_0} - 0{,}035",
)
def wall_confinement_requirement(
    mu_k: float,
    v_g: float,
    omega_v: float,
    eps_yd: float,
    b_x: float,
    b_0: float,
    alpha: float,
) -> float:
    """Rapporto meccanico minimo di armatura di confinamento negli elementi di bordo delle pareti.

    NTC18 §7.4.6.2.4, Formula [7.4.32]:
        alpha * omega_wd >= 30 * mu_k * (v_g + omega_v) * eps_yd * (b_x/b_0) - 0.035

    Parameters
    ----------
    mu_k : float
        Domanda di duttilita' in curvatura per la parete [-].
    v_g : float
        Forza assiale normalizzata per i carichi gravitazionali [-].
    omega_v : float
        Rapporto meccanico dell'armatura verticale fuori dagli elementi di bordo
        (rho_v * f_yd_v / f_ed) [-].
    eps_yd : float
        Deformazione di snervamento dell'acciaio [-].
    b_x : float
        Larghezza della sezione trasversale lorda [m].
    b_0 : float
        Larghezza del nucleo confinato degli elementi di bordo [m].
    alpha : float
        Coefficiente di efficacia del confinamento [-].

    Returns
    -------
    float
        Valore minimo richiesto di omega_wd [-].
    """
    if mu_k < 1.0:
        raise ValueError(f"mu_k deve essere >= 1.0, ricevuto {mu_k}")
    if v_g < 0:
        raise ValueError(f"v_g deve essere >= 0, ricevuto {v_g}")
    if omega_v < 0:
        raise ValueError(f"omega_v deve essere >= 0, ricevuto {omega_v}")
    if eps_yd <= 0:
        raise ValueError(f"eps_yd deve essere > 0, ricevuto {eps_yd}")
    if b_0 <= 0 or b_x <= 0:
        raise ValueError("b_x e b_0 devono essere > 0")
    if alpha <= 0 or alpha > 1.0:
        raise ValueError(f"alpha deve essere in (0, 1], ricevuto {alpha}")

    demand = 30.0 * mu_k * (v_g + omega_v) * eps_yd * (b_x / b_0) - 0.035
    omega_wd_min = max(demand, 0.0) / alpha
    return omega_wd_min


# ══════════════════════════════════════════════════════════════════════════════
# §7.4.4.5.1 — PARETI ACCOPPIATE — SCORRIMENTO
# ══════════════════════════════════════════════════════════════════════════════




# ══════════════════════════════════════════════════════════════════════════════
# §7.4.4.5.1 — PARETI ACCOPPIATE — SCORRIMENTO
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(
    article="7.4.4.5.1",
    formula="7.4.20",
    latex=r"V_{dd} = \min\{1{,}3 \cdot \sum A_{id}\sqrt{f_{cd}f_{yd}},\;0{,}25\,f_{yd}\sum A_{id}\}",
)
def wall_sliding_shear_diagonal(sum_A_id: float, f_cd: float, f_yd: float) -> float:
    """Contributo delle armature diagonali alla resistenza a scorrimento.

    NTC18 §7.4.4.5.1, Formula [7.4.20]:
        V_dd = min(1.3 * sum_A_id * sqrt(f_cd * f_yd), 0.25 * f_yd * sum_A_id)

    Parameters
    ----------
    sum_A_id : float
        Somma delle aree delle armature diagonali [mm^2].
    f_cd : float
        Resistenza di progetto a compressione del calcestruzzo [MPa].
    f_yd : float
        Resistenza di progetto dell'acciaio [MPa].

    Returns
    -------
    float
        Contributo V_dd alla resistenza a scorrimento [N].
    """
    if sum_A_id <= 0:
        raise ValueError(f"sum_A_id deve essere > 0, ricevuto {sum_A_id}")
    if f_cd <= 0:
        raise ValueError(f"f_cd deve essere > 0, ricevuto {f_cd}")
    if f_yd <= 0:
        raise ValueError(f"f_yd deve essere > 0, ricevuto {f_yd}")

    opt1 = 1.3 * sum_A_id * math.sqrt(f_cd * f_yd)
    opt2 = 0.25 * f_yd * sum_A_id
    return min(opt1, opt2)


@ntc_ref(
    article="7.4.4.5.1",
    formula="7.4.21",
    latex=r"V_{id} = f_{yd} \sum A_{id} \cos\varphi_i",
)
def wall_sliding_shear_inclined(sum_A_id: float, f_yd: float, phi: float) -> float:
    """Contributo delle armature inclinate alla resistenza a scorrimento.

    NTC18 §7.4.4.5.1, Formula [7.4.21]:
        V_id = f_yd * sum_A_id * cos(phi)

    Parameters
    ----------
    sum_A_id : float
        Somma delle aree delle armature inclinate [mm^2].
    f_yd : float
        Resistenza di progetto dell'acciaio [MPa].
    phi : float
        Angolo di inclinazione delle armature rispetto all'asse orizzontale [rad].

    Returns
    -------
    float
        Contributo V_id alla resistenza a scorrimento [N].
    """
    if sum_A_id <= 0:
        raise ValueError(f"sum_A_id deve essere > 0, ricevuto {sum_A_id}")
    if f_yd <= 0:
        raise ValueError(f"f_yd deve essere > 0, ricevuto {f_yd}")

    return f_yd * sum_A_id * math.cos(phi)


@ntc_ref(
    article="7.4.4.5.1",
    formula="7.4.22",
    latex=r"V_{fd} = \min\{\mu_f\bigl(\sum A_{ij}f_{yd}+N_{fd}\bigr)\xi + \frac{M_{fd}}{2\xi l_w},\;0{,}5\,\eta_{fc}\,f_{cd}\,\xi\,l_w\,b_{w0}\}",
)
def wall_sliding_shear_friction(
    sum_A_ij: float,
    f_yd: float,
    N_fd: float,
    xi: float,
    M_fd: float,
    l_w: float,
    b_w0: float,
    f_ck: float,
    f_cd: float,
    mu_f: float = 0.6,
) -> float:
    """Contributo dell'attrito alla resistenza a scorrimento.

    NTC18 §7.4.4.5.1, Formula [7.4.22]:
        eta_fc = 0.6 * (1 - f_ck / 250)
        V_fd = min(
            mu_f * (sum_A_ij * f_yd + N_fd) * xi + M_fd / (2 * xi * l_w),
            0.5 * eta_fc * f_cd * xi * l_w * b_w0
        )

    Parameters
    ----------
    sum_A_ij : float
        Somma delle aree delle armature trasversali [mm^2].
    f_yd : float
        Resistenza di progetto dell'acciaio [MPa].
    N_fd : float
        Forza normale di progetto [N].
    xi : float
        Rapporto profondita' zona compressa / altezza parete [-].
    M_fd : float
        Momento flettente di progetto [N*mm].
    l_w : float
        Lunghezza della parete [mm].
    b_w0 : float
        Spessore dell'anima della parete [mm].
    f_ck : float
        Resistenza caratteristica a compressione del calcestruzzo [MPa].
    f_cd : float
        Resistenza di progetto a compressione del calcestruzzo [MPa].
    mu_f : float
        Coefficiente di attrito, default 0.6 (NTC18).

    Returns
    -------
    float
        Contributo V_fd alla resistenza a scorrimento [N].
    """
    if f_ck <= 0:
        raise ValueError(f"f_ck deve essere > 0, ricevuto {f_ck}")
    if f_cd <= 0:
        raise ValueError(f"f_cd deve essere > 0, ricevuto {f_cd}")
    if l_w <= 0:
        raise ValueError(f"l_w deve essere > 0, ricevuto {l_w}")
    if b_w0 <= 0:
        raise ValueError(f"b_w0 deve essere > 0, ricevuto {b_w0}")

    eta_fc = 0.6 * (1.0 - f_ck / 250.0)
    term1 = mu_f * (sum_A_ij * f_yd + N_fd) * xi + M_fd / (2.0 * xi * l_w)
    term2 = 0.5 * eta_fc * f_cd * xi * l_w * b_w0
    return min(term1, term2)


@ntc_ref(
    article="7.4.4.5.1",
    formula="7.4.19",
    latex=r"V_{Rd,S} = V_{dd} + V_{id} + V_{fd}",
)
def wall_sliding_shear_resistance(V_dd: float, V_id: float, V_fd: float) -> float:
    """Resistenza totale a scorrimento della parete.

    NTC18 §7.4.4.5.1, Formula [7.4.19]:
        V_Rd_S = V_dd + V_id + V_fd

    Parameters
    ----------
    V_dd : float
        Contributo delle armature diagonali [N].
    V_id : float
        Contributo delle armature inclinate [N].
    V_fd : float
        Contributo dell'attrito [N].

    Returns
    -------
    float
        Resistenza totale a scorrimento V_Rd_S [N].
    """
    return V_dd + V_id + V_fd


@ntc_ref(
    article="7.4.4.5.1",
    formula="7.4.18",
    latex=r"V_{Ed} \le V_{Rd,S}",
)
def wall_sliding_check(V_Ed: float, V_Rd_S: float) -> tuple[bool, float]:
    """Verifica a scorrimento della parete accoppiata.

    NTC18 §7.4.4.5.1, Formula [7.4.18]:
        V_Ed <= V_Rd_S

    Parameters
    ----------
    V_Ed : float
        Taglio di progetto [N].
    V_Rd_S : float
        Resistenza totale a scorrimento [N].

    Returns
    -------
    tuple[bool, float]
        - satisfied: True se la verifica e' soddisfatta
        - ratio: V_Ed / V_Rd_S [-]
    """
    ratio = V_Ed / V_Rd_S
    return ratio <= 1.0, ratio


# ══════════════════════════════════════════════════════════════════════════════
# §7.4.4.6 — TRAVI DI ACCOPPIAMENTO
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(
    article="7.4.4.6",
    formula="7.4.23",
    latex=r"V_{Ed} \le f_{cut} \cdot b \cdot d, \quad f_{cut} = 0{,}5\,\eta\,f_{cd}",
)
def coupling_beam_shear_capacity(f_ck: float, f_cd: float, b: float, d: float) -> float:
    """Resistenza a taglio della trave di accoppiamento (contributo calcestruzzo).

    NTC18 §7.4.4.6, Formula [7.4.23]:
        eta = 0.6 * (1 - f_ck / 250)
        f_cut = 0.5 * eta * f_cd
        V_Rd = f_cut * b * d

    Parameters
    ----------
    f_ck : float
        Resistenza caratteristica a compressione del calcestruzzo [MPa].
    f_cd : float
        Resistenza di progetto a compressione del calcestruzzo [MPa].
    b : float
        Larghezza della trave [mm].
    d : float
        Altezza utile della trave [mm].

    Returns
    -------
    float
        Resistenza a taglio V_Rd [N].
    """
    eta = 0.6 * (1.0 - f_ck / 250.0)
    f_cut = 0.5 * eta * f_cd
    return f_cut * b * d


@ntc_ref(
    article="7.4.4.6",
    formula="7.4.23",
    latex=r"V_{Ed} \le f_{cut} \cdot b \cdot d",
)
def coupling_beam_shear_check(
    V_Ed: float, f_ck: float, f_cd: float, b: float, d: float
) -> tuple[bool, float]:
    """Verifica a taglio della trave di accoppiamento (cls).

    NTC18 §7.4.4.6, Formula [7.4.23]:
        V_Rd = coupling_beam_shear_capacity(f_ck, f_cd, b, d)
        V_Ed <= V_Rd

    Parameters
    ----------
    V_Ed : float
        Taglio di progetto [N].
    f_ck : float
        Resistenza caratteristica a compressione del calcestruzzo [MPa].
    f_cd : float
        Resistenza di progetto a compressione del calcestruzzo [MPa].
    b : float
        Larghezza della trave [mm].
    d : float
        Altezza utile della trave [mm].

    Returns
    -------
    tuple[bool, float]
        - satisfied: True se la verifica e' soddisfatta
        - ratio: V_Ed / V_Rd [-]
    """
    V_Rd = coupling_beam_shear_capacity(f_ck, f_cd, b, d)
    ratio = V_Ed / V_Rd
    return ratio <= 1.0, ratio


@ntc_ref(
    article="7.4.4.6",
    formula="7.4.24",
    latex=r"V_{il} = 2\,A_s\,f_{yd}\,\sin\varphi",
)
def coupling_beam_inclined_bars_shear(A_s: float, f_yd: float, phi: float) -> float:
    """Resistenza a taglio della trave di accoppiamento con armatura inclinata.

    NTC18 §7.4.4.6, Formula [7.4.24]:
        V_il = 2 * A_s * f_yd * sin(phi)

    Parameters
    ----------
    A_s : float
        Area delle armature inclinate (per lato) [mm^2].
    f_yd : float
        Resistenza di progetto dell'acciaio [MPa].
    phi : float
        Angolo di inclinazione delle armature rispetto all'asse orizzontale [rad].

    Returns
    -------
    float
        Resistenza a taglio V_il [N].
    """
    return 2.0 * A_s * f_yd * math.sin(phi)

# ══════════════════════════════════════════════════════════════════════════════
# §7.11 — OPERE E SISTEMI GEOTECNICI
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(article="7.11.3.5.2", formula="7.11.3", latex=r"k_h = \beta_s \,\frac{a_{max}}{g}, \quad k_v = 0{,}5\,k_h, \quad a_{max} = S_S \, S_T \, a_g")
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


@ntc_ref(
    article="7.11.6.2.1",
    formula="7.11.6",
    latex=r"k_h = \beta_m \frac{a_{max}}{g},\quad k_v = \pm 0{,}5\,k_h,\quad a_{max} = (S_g \cdot S_f)\,a_g",
)
def retaining_wall_seismic_coefficients(
    a_g: float,
    S_g: float,
    S_f: float,
    beta_m: float,
    g: float = 9.81,
) -> tuple[float, float, float]:
    """Coefficienti sismici per muri di sostegno (analisi pseudostatica).

    NTC18 §7.11.6.2.1, Formule [7.11.6]-[7.11.8]:
        a_max = S_g * S_f * a_g        [7.11.8]
        k_h   = beta_m * a_max / g      [7.11.6]
        k_v   = 0.5 * k_h               [7.11.7]

    Per SLV: beta_m = 0.38; per SLD: beta_m = 0.47.
    Per muri non liberi di spostarsi rispetto al terreno: beta_m = 1.0.

    Parameters
    ----------
    a_g : float
        Accelerazione orizzontale massima su sito rigido [m/s^2].
    S_g : float
        Coefficiente di amplificazione stratigrafica [-].
    S_f : float
        Coefficiente di amplificazione topografica [-].
    beta_m : float
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
    if beta_m < 0:
        raise ValueError(f"beta_m deve essere >= 0, ricevuto {beta_m}")

    a_max = S_g * S_f * a_g
    k_h = beta_m * a_max / g
    k_v = 0.5 * k_h
    return k_h, k_v, a_max


@ntc_ref(
    article="7.11.6.3.1",
    formula="7.11.9",
    latex=r"a_h = k_h \cdot g = \alpha \cdot \beta \cdot a_{max}",
)
def sheet_pile_pseudostatic_acceleration(
    alpha: float,
    beta: float,
    a_max: float,
    g: float = 9.81,
) -> tuple[float, float]:
    """Accelerazione pseudostatica equivalente per paratie [m/s^2].

    NTC18 §7.11.6.3.1, Formula [7.11.9]:
        a_h = k_h * g = alpha * beta * a_max

    Per le paratie si puo' porre a_h = 0 (§7.11.6.3.1).

    Parameters
    ----------
    alpha : float
        Coefficiente di deformabilita' del terreno (alpha <= 1) [-].
    beta : float
        Coefficiente di capacita' di spostamento dell'opera (beta <= 1) [-].
    a_max : float
        Accelerazione di picco attesa nel terreno significativo [m/s^2].
    g : float
        Accelerazione di gravita' [m/s^2], default 9.81.

    Returns
    -------
    tuple[float, float]
        - a_h: accelerazione orizzontale equivalente [m/s^2]
        - k_h: coefficiente sismico orizzontale [-]
    """
    if not 0.0 <= alpha <= 1.0:
        raise ValueError(f"alpha deve essere in [0, 1], ricevuto {alpha}")
    if not 0.0 <= beta <= 1.0:
        raise ValueError(f"beta deve essere in [0, 1], ricevuto {beta}")
    if a_max < 0:
        raise ValueError(f"a_max deve essere >= 0, ricevuto {a_max}")

    alpha_beta = alpha * beta
    # NTC18: se alpha*beta <= 0.2, assumere k_h = 0.2 * a_max / g
    if alpha_beta <= 0.2 and a_max > 0:
        k_h = max(alpha_beta * a_max / g, 0.2 * a_max / g)
    else:
        k_h = alpha_beta * a_max / g

    a_h = k_h * g
    return a_h, k_h


@ntc_ref(
    article="7.11.6.3.1",
    formula="7.11.11",
    latex=r"u_s \le 0{,}005 \cdot H",
)
def sheet_pile_displacement_limit(
    H: float,
) -> float:
    """Spostamento permanente massimo ammissibile per una paratia [m].

    NTC18 §7.11.6.3.1, Formula [7.11.11]:
        u_s <= 0.005 * H

    Parameters
    ----------
    H : float
        Altezza complessiva della paratia [m].

    Returns
    -------
    float
        Spostamento permanente massimo u_s,max = 0.005 * H [m].
    """
    if H <= 0:
        raise ValueError(f"H deve essere > 0, ricevuto {H}")
    return 0.005 * H


@ntc_ref(
    article="7.11.6.4",
    formula="7.11.12",
    latex=r"L_{q,i} = L_s \left(1 + 1{,}5\,\frac{a_{max}}{g}\right)",
)
def anchor_free_length_seismic(
    L_s: float,
    a_max: float,
    g: float = 9.81,
) -> float:
    """Lunghezza libera di ancoraggio in condizioni sismiche [m].

    NTC18 §7.11.6.4, Formula [7.11.12]:
        L_q,i = L_s * (1 + 1.5 * a_max / g)

    Parameters
    ----------
    L_s : float
        Lunghezza libera dell'ancoraggio in condizioni statiche [m].
    a_max : float
        Accelerazione orizzontale massima attesa al sito [m/s^2].
    g : float
        Accelerazione di gravita' [m/s^2], default 9.81.

    Returns
    -------
    float
        Lunghezza libera in condizioni sismiche L_q,i [m].
    """
    if L_s <= 0:
        raise ValueError(f"L_s deve essere > 0, ricevuto {L_s}")
    if a_max < 0:
        raise ValueError(f"a_max deve essere >= 0, ricevuto {a_max}")

    return L_s * (1.0 + 1.5 * a_max / g)
