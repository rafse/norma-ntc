"""Verifiche fondazioni, muri di sostegno e isolamento sismico — NTC18 §7.10–§7.11.

Coefficienti sismici per muri di sostegno e paratie, verifiche fondazioni
superficiali e su pali in zona sismica, sistemi di vincolo sismico,
isolamento sismico (analisi lineare statica).

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

from pyntc.core.reference import ntc_ref


# ══════════════════════════════════════════════════════════════════════════════
# §7.11.6.2 — MURI DI SOSTEGNO: COEFFICIENTI SISMICI
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(
    article="7.11.6.2.1",
    formula="7.11.6",
    latex=r"k_h = \beta_m \,\frac{a_{\max}}{g}",
)
def seismic_wall_coeff_horizontal(
    a_max: float,
    beta_m: float,
    g: float = 9.81,
) -> float:
    """Coefficiente sismico orizzontale per muri di sostegno [-].

    NTC18 §7.11.6.2.1, Formula [7.11.6]:
        k_h = beta_m * a_max / g

    I valori di riferimento per beta_m sono:
        beta_m = 0.38  per verifiche allo SLV (muro libero di traslare)
        beta_m = 0.47  per verifiche allo SLD (muro libero di traslare)
        beta_m = 1.00  per muri non liberi di spostarsi

    Parameters
    ----------
    a_max : float
        Accelerazione orizzontale massima attesa al sito [m/s^2].
    beta_m : float
        Coefficiente di riduzione dell'accelerazione massima [-].
    g : float
        Accelerazione di gravita' [m/s^2], default 9.81.

    Returns
    -------
    float
        Coefficiente sismico orizzontale k_h [-].
    """
    if a_max < 0:
        raise ValueError(f"a_max deve essere >= 0, ricevuto {a_max}")
    if beta_m <= 0:
        raise ValueError(f"beta_m deve essere > 0, ricevuto {beta_m}")
    if g <= 0:
        raise ValueError(f"g deve essere > 0, ricevuto {g}")
    return beta_m * a_max / g


@ntc_ref(
    article="7.11.6.2.1",
    formula="7.11.7",
    latex=r"k_v = \pm 0{,}5\,k_h",
)
def seismic_wall_coeff_vertical(k_h: float) -> float:
    """Coefficiente sismico verticale per muri di sostegno [-].

    NTC18 §7.11.6.2.1, Formula [7.11.7]:
        k_v = +/- 0.5 * k_h

    Restituisce il valore assoluto; il segno (+/-) va scelto
    per la combinazione piu' sfavorevole.

    Parameters
    ----------
    k_h : float
        Coefficiente sismico orizzontale [-].

    Returns
    -------
    float
        Valore assoluto del coefficiente sismico verticale |k_v| [-].
    """
    if k_h < 0:
        raise ValueError(f"k_h deve essere >= 0, ricevuto {k_h}")
    return 0.5 * k_h


@ntc_ref(
    article="7.11.6.2.1",
    formula="7.11.8",
    latex=r"a_{\max} = S \cdot a_g = (S_g \cdot S_f) \cdot a_g",
)
def seismic_wall_site_acceleration(
    a_g: float,
    S_g: float,
    S_f: float = 1.0,
) -> float:
    """Accelerazione orizzontale massima attesa al sito per muri di sostegno [m/s^2].

    NTC18 §7.11.6.2.1, Formula [7.11.8]:
        a_max = S * a_g = (S_g * S_f) * a_g

    Parameters
    ----------
    a_g : float
        Accelerazione orizzontale massima su sito rigido [m/s^2].
    S_g : float
        Coefficiente di amplificazione stratigrafica [-].
    S_f : float
        Coefficiente di amplificazione topografica [-], default 1.0.

    Returns
    -------
    float
        Accelerazione massima attesa al sito a_max [m/s^2].
    """
    if a_g < 0:
        raise ValueError(f"a_g deve essere >= 0, ricevuto {a_g}")
    if S_g <= 0:
        raise ValueError(f"S_g deve essere > 0, ricevuto {S_g}")
    if S_f <= 0:
        raise ValueError(f"S_f deve essere > 0, ricevuto {S_f}")
    return S_g * S_f * a_g


# ══════════════════════════════════════════════════════════════════════════════
# §7.11.6.3 — PARATIE: METODI PSEUDO-STATICI
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(
    article="7.11.6.3.1",
    formula="7.11.9",
    latex=r"a_h = k_h \cdot g = \alpha \cdot \beta \cdot a_{\max}",
)
def seismic_sheet_pile_acceleration(
    a_max: float,
    alpha: float,
    beta: float,
    g: float = 9.81,
) -> tuple[float, float]:
    """Accelerazione equivalente orizzontale per paratie pseudo-statiche [m/s^2].

    NTC18 §7.11.6.3.1, Formula [7.11.9]:
        a_h = k_h * g = alpha * beta * a_max

    Se alpha * beta <= 0.2, la norma prescrive k_h = 0.2 * a_max / g.

    Parameters
    ----------
    a_max : float
        Accelerazione orizzontale massima al sito [m/s^2].
    alpha : float
        Coefficiente di deformabilita' dei terreni (<=1) [-].
    beta : float
        Coefficiente di capacita' di spostamento dell'opera (<=1) [-].
    g : float
        Accelerazione di gravita' [m/s^2], default 9.81.

    Returns
    -------
    tuple[float, float]
        - k_h: coefficiente sismico orizzontale applicato [-]
        - a_h: accelerazione equivalente orizzontale [m/s^2]
    """
    if a_max < 0:
        raise ValueError(f"a_max deve essere >= 0, ricevuto {a_max}")
    if not (0.0 <= alpha <= 1.0):
        raise ValueError(f"alpha deve essere in [0, 1], ricevuto {alpha}")
    if not (0.0 <= beta <= 1.0):
        raise ValueError(f"beta deve essere in [0, 1], ricevuto {beta}")
    if g <= 0:
        raise ValueError(f"g deve essere > 0, ricevuto {g}")

    alpha_beta = alpha * beta
    # Limite minimo normativo
    if alpha_beta <= 0.2:
        k_h = 0.2 * a_max / g
    else:
        k_h = alpha_beta * a_max / g

    a_h = k_h * g
    return k_h, a_h


@ntc_ref(
    article="7.11.6.3.1",
    formula="7.11.10",
    latex=r"a_{\max} = S \cdot a_g = (S_S \cdot S_T) \cdot a_g",
)
def seismic_sheet_pile_site_acceleration(
    a_g: float,
    S_S: float,
    S_T: float = 1.0,
) -> float:
    """Accelerazione massima al sito per paratie (formula §7.11.6.3.1) [m/s^2].

    NTC18 §7.11.6.3.1, Formula [7.11.10]:
        a_max = S * a_g = (S_S * S_T) * a_g

    Parameters
    ----------
    a_g : float
        Accelerazione orizzontale massima su sito rigido [m/s^2].
    S_S : float
        Coefficiente di amplificazione stratigrafica [-].
    S_T : float
        Coefficiente di amplificazione topografica [-], default 1.0.

    Returns
    -------
    float
        Accelerazione massima attesa al sito a_max [m/s^2].
    """
    if a_g < 0:
        raise ValueError(f"a_g deve essere >= 0, ricevuto {a_g}")
    if S_S <= 0:
        raise ValueError(f"S_S deve essere > 0, ricevuto {S_S}")
    if S_T <= 0:
        raise ValueError(f"S_T deve essere > 0, ricevuto {S_T}")
    return S_S * S_T * a_g


@ntc_ref(
    article="7.11.6.3.1",
    formula="7.11.11",
    latex=r"u_s \le 0{,}005 \cdot H",
)
def seismic_sheet_pile_displacement_limit(H: float) -> float:
    """Spostamento permanente massimo ammissibile per paratie [m].

    NTC18 §7.11.6.3.1, Formula [7.11.11]:
        u_s <= 0.005 * H

    Parameters
    ----------
    H : float
        Altezza complessiva della paratia [m].

    Returns
    -------
    float
        Spostamento permanente massimo ammissibile u_s,max [m].
    """
    if H <= 0:
        raise ValueError(f"H deve essere > 0, ricevuto {H}")
    return 0.005 * H


# ══════════════════════════════════════════════════════════════════════════════
# §7.11.6.4 — SISTEMI DI VINCOLO: LUNGHEZZA LIBERA SISMICA
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(
    article="7.11.6.4",
    formula="7.11.12",
    latex=r"L_{q,i} = L_s \left(1 + 1{,}5\,\frac{a_{\max}}{g}\right)",
)
def seismic_anchor_free_length(
    L_s: float,
    a_max: float,
    g: float = 9.81,
) -> float:
    """Lunghezza libera sismica dell'ancoraggio [m].

    NTC18 §7.11.6.4, Formula [7.11.12]:
        L_{q,i} = L_s * (1 + 1.5 * a_max / g)

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
        Lunghezza libera sismica L_{q,i} [m].
    """
    if L_s <= 0:
        raise ValueError(f"L_s deve essere > 0, ricevuto {L_s}")
    if a_max < 0:
        raise ValueError(f"a_max deve essere >= 0, ricevuto {a_max}")
    if g <= 0:
        raise ValueError(f"g deve essere > 0, ricevuto {g}")
    return L_s * (1.0 + 1.5 * a_max / g)


# ══════════════════════════════════════════════════════════════════════════════
# §7.11.5.3.1 — FONDAZIONI SUPERFICIALI: COEFFICIENTI PARZIALI Tab.7.11.II
# ══════════════════════════════════════════════════════════════════════════════

_SEISMIC_SHALLOW_FOUNDATION_FACTORS: dict[str, float] = {
    "bearing": 2.3,
    "sliding": 1.1,
    "lateral_resistance": 1.3,
}


@ntc_ref(
    article="7.11.5.3.1",
    table="Tab.7.11.II",
    latex=r"\text{Tab.\,7.11.II}",
)
def seismic_shallow_foundation_gamma_R(verification: str) -> float:
    """Coefficiente parziale gamma_R per fondazioni superficiali in zona sismica (SLV) [-].

    NTC18 §7.11.5.3.1 — Tab. 7.11.II.

    Parameters
    ----------
    verification : str
        Tipo di verifica:
        ``"bearing"`` (carico limite, gamma_R=2.3),
        ``"sliding"`` (scorrimento, gamma_R=1.1),
        ``"lateral_resistance"`` (resistenza superfici laterali, gamma_R=1.3).

    Returns
    -------
    float
        Coefficiente parziale gamma_R [-].
    """
    if verification not in _SEISMIC_SHALLOW_FOUNDATION_FACTORS:
        raise ValueError(
            f"Tipo di verifica non valido: {verification!r}. "
            f"Valori ammessi: {set(_SEISMIC_SHALLOW_FOUNDATION_FACTORS.keys())}"
        )
    return _SEISMIC_SHALLOW_FOUNDATION_FACTORS[verification]


# ══════════════════════════════════════════════════════════════════════════════
# §7.10.5.3.1 — ISOLAMENTO SISMICO: ANALISI LINEARE STATICA
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(
    article="7.10.5.3.1",
    formula="7.10.1",
    latex=r"F = M \cdot S_x(T_{in},\,\zeta_{out})",
)
def seismic_isolation_base_shear(
    M: float,
    S_x: float,
) -> float:
    """Forza orizzontale complessiva sul sistema di isolamento [kN].

    NTC18 §7.10.5.3.1, Formula [7.10.1]:
        F = M * S_x(T_in, zeta_out)

    Parameters
    ----------
    M : float
        Massa totale della struttura isolata [t] (o equivalente in kN·s^2/m).
    S_x : float
        Accelerazione spettrale S_x(T_in, zeta_out) [m/s^2].

    Returns
    -------
    float
        Forza orizzontale complessiva F [kN].
    """
    if M <= 0:
        raise ValueError(f"M deve essere > 0, ricevuto {M}")
    if S_x < 0:
        raise ValueError(f"S_x deve essere >= 0, ricevuto {S_x}")
    return M * S_x


@ntc_ref(
    article="7.10.5.3.1",
    formula="7.10.2",
    latex=r"d_{uc} = \frac{M \cdot S_x(T_{in},\,\zeta_{out})}{K_{est,\min}}",
)
def seismic_isolation_displacement(
    M: float,
    S_x: float,
    K_est_min: float,
) -> float:
    """Spostamento del centro di rigidezza del sistema di isolamento [m].

    NTC18 §7.10.5.3.1, Formula [7.10.2]:
        d_uc = M * S_x(T_in, zeta_out) / K_est_min

    Parameters
    ----------
    M : float
        Massa totale della struttura isolata [t].
    S_x : float
        Accelerazione spettrale S_x(T_in, zeta_out) [m/s^2].
    K_est_min : float
        Rigidezza equivalente minima del sistema di isolamento [kN/m].

    Returns
    -------
    float
        Spostamento del centro di rigidezza d_uc [m].
    """
    if M <= 0:
        raise ValueError(f"M deve essere > 0, ricevuto {M}")
    if S_x < 0:
        raise ValueError(f"S_x deve essere >= 0, ricevuto {S_x}")
    if K_est_min <= 0:
        raise ValueError(f"K_est_min deve essere > 0, ricevuto {K_est_min}")
    return M * S_x / K_est_min


@ntc_ref(
    article="7.10.5.3.1",
    formula="7.10.4",
    latex=r"\delta_{di} = 1 + \frac{e_{tot,x}}{r_j^2}\,y_i \quad \delta_{dy} = 1 + \frac{e_{tot,y}}{r_j^2}\,x_i",
)
def seismic_isolation_torsion_amplification(
    e_tot: float,
    r_j: float,
    coord: float,
) -> float:
    """Fattore di amplificazione torsionale del sistema di isolamento [-].

    NTC18 §7.10.5.3.1, Formula [7.10.4]:
        delta_di = 1 + (e_tot_x / r_j^2) * y_i
        delta_dy = 1 + (e_tot_y / r_j^2) * x_i

    Parameters
    ----------
    e_tot : float
        Eccentricita' totale nella direzione considerata [m].
    r_j : float
        Raggio torsionale del sistema di isolamento nella direzione
        trasversale [m].
    coord : float
        Coordinata del dispositivo rispetto al centro di rigidezza
        nella direzione trasversale [m].

    Returns
    -------
    float
        Fattore di amplificazione delta [-].
    """
    if r_j <= 0:
        raise ValueError(f"r_j deve essere > 0, ricevuto {r_j}")
    return 1.0 + (e_tot / r_j**2) * coord


@ntc_ref(
    article="7.10.5.3.1",
    formula="7.10.5",
    latex=r"r_x^2 = \frac{\sum(x_i^2 \cdot K_{yj} + y_i^2 \cdot K_{xi})}{\sum K_{yj}}",
)
def seismic_isolation_torsional_radius(
    x_coords: list[float],
    y_coords: list[float],
    K_x: list[float],
    K_y: list[float],
    direction: str = "x",
) -> float:
    """Raggio torsionale del sistema di isolamento [m].

    NTC18 §7.10.5.3.1, Formula [7.10.5]:
        r_x^2 = sum(x_i^2 * K_yj + y_i^2 * K_xi) / sum(K_yj)
        r_y^2 = sum(x_i^2 * K_yj + y_i^2 * K_xi) / sum(K_xi)

    Parameters
    ----------
    x_coords : list[float]
        Coordinate x dei dispositivi rispetto al centro di rigidezza [m].
    y_coords : list[float]
        Coordinate y dei dispositivi rispetto al centro di rigidezza [m].
    K_x : list[float]
        Rigidezze equivalenti dei dispositivi in direzione x [kN/m].
    K_y : list[float]
        Rigidezze equivalenti dei dispositivi in direzione y [kN/m].
    direction : str
        ``"x"`` per calcolare r_x (default) o ``"y"`` per calcolare r_y.

    Returns
    -------
    float
        Raggio torsionale r_x o r_y [m].
    """
    n = len(x_coords)
    if not (len(y_coords) == len(K_x) == len(K_y) == n):
        raise ValueError(
            "x_coords, y_coords, K_x, K_y devono avere la stessa lunghezza"
        )
    if n == 0:
        raise ValueError("Gli array non possono essere vuoti")
    if direction not in ("x", "y"):
        raise ValueError(f"direction deve essere 'x' o 'y', ricevuto {direction!r}")

    numerator = sum(
        x_coords[i] ** 2 * K_y[i] + y_coords[i] ** 2 * K_x[i]
        for i in range(n)
    )
    if direction == "x":
        denominator = sum(K_y)
    else:
        denominator = sum(K_x)

    if denominator <= 0:
        raise ValueError(
            f"Somma delle rigidezze in direzione {'y' if direction == 'x' else 'x'} "
            f"deve essere > 0"
        )

    return math.sqrt(numerator / denominator)


# ── Metodo di Mononobe-Okabe ──────────────────────────────────────────────────
# Metodo di Mononobe-Okabe per il calcolo della spinta sismica attiva e passiva
# e verifiche a scorrimento e ribaltamento di muri di sostegno in condizioni
# sismiche.


# ============================================================================
# Coefficienti di spinta sismica — Mononobe-Okabe
# ============================================================================


@ntc_ref(article="7.11.6", latex=r"K_{ae} = \text{Mononobe-Okabe}")
def seismic_active_pressure_coefficient(
    phi: float,
    delta: float,
    beta: float,
    theta: float,
    kh: float,
    kv: float = 0.0,
) -> float:
    """Coefficiente di spinta attiva sismica (Mononobe-Okabe) [-].

    NTC18 art.7.11.6 - Metodo di Mononobe-Okabe per la spinta attiva.

    Parameters
    ----------
    phi : float
        Angolo di resistenza al taglio interno del terreno [rad].
    delta : float
        Angolo di attrito muro-terreno [rad].
    beta : float
        Inclinazione della parete rispetto alla verticale [rad]
        (positivo se la parete si inclina verso il terrapieno).
    theta : float
        Inclinazione della superficie del terreno rispetto
        all'orizzontale [rad] (positivo verso l'alto).
    kh : float
        Coefficiente sismico orizzontale [-] (frazione di g).
    kv : float, optional
        Coefficiente sismico verticale [-] (frazione di g). Default 0.0.

    Returns
    -------
    float
        Coefficiente di spinta attiva sismica K_ae [-].

    Raises
    ------
    ValueError
        Se l'argomento della radice quadrata e' negativo (condizione
        geometrica non ammissibile).
    """
    if kv >= 1.0:
        raise ValueError(f"kv deve essere < 1.0: {kv}")
    psi = math.atan(kh / (1.0 - kv))

    arg = (
        math.sin(phi + delta) * math.sin(phi - psi - theta)
    ) / (
        math.cos(delta + beta + psi) * math.cos(beta - theta)
    )
    if arg < 0:
        raise ValueError(
            f"Argomento della radice quadrata negativo ({arg:.4f}): "
            "combinazione di parametri non ammissibile per Mononobe-Okabe attivo."
        )

    num = math.cos(phi - psi - beta) ** 2
    denom = (
        math.cos(psi)
        * math.cos(beta) ** 2
        * math.cos(delta + beta + psi)
        * (1.0 + math.sqrt(arg)) ** 2
    )
    return num / denom


@ntc_ref(
    article="7.11.6",
    latex=r"E_{ae} = 0.5\,\gamma_s H^2 K_{ae}(1-k_v)",
)
def seismic_active_earth_pressure(
    gamma_s: float,
    H: float,
    K_ae: float,
    kv: float = 0.0,
) -> float:
    """Spinta attiva sismica totale per unita' di lunghezza [kN/m].

    NTC18 §7.11.6 — E_ae = 0.5 * gamma_s * H^2 * K_ae * (1 - kv).

    Parameters
    ----------
    gamma_s : float
        Peso dell'unita' di volume del terreno [kN/m³].
    H : float
        Altezza del muro [m].
    K_ae : float
        Coefficiente di spinta attiva sismica [-].
    kv : float, optional
        Coefficiente sismico verticale [-] (frazione di g). Default 0.0.

    Returns
    -------
    float
        Spinta attiva sismica totale E_ae [kN/m].

    Raises
    ------
    ValueError
        Se gamma_s, H o K_ae sono non positivi.
    """
    if gamma_s <= 0:
        raise ValueError(f"gamma_s deve essere positivo: {gamma_s}")
    if H <= 0:
        raise ValueError(f"H deve essere positivo: {H}")
    if K_ae <= 0:
        raise ValueError(f"K_ae deve essere positivo: {K_ae}")
    return 0.5 * gamma_s * H ** 2 * K_ae * (1.0 - kv)


@ntc_ref(
    article="7.11.6",
    latex=r"K_{pe} = \text{Mononobe-Okabe passivo}",
)
def seismic_passive_pressure_coefficient(
    phi: float,
    delta: float,
    beta: float,
    theta: float,
    kh: float,
    kv: float = 0.0,
) -> float:
    """Coefficiente di spinta passiva sismica (Mononobe-Okabe) [-].

    NTC18 §7.11.6 — Metodo di Mononobe-Okabe per la spinta passiva.

    Parameters
    ----------
    phi : float
        Angolo di resistenza al taglio interno del terreno [rad].
    delta : float
        Angolo di attrito muro-terreno [rad].
    beta : float
        Inclinazione della parete rispetto alla verticale [rad].
    theta : float
        Inclinazione della superficie del terreno rispetto
        all'orizzontale [rad].
    kh : float
        Coefficiente sismico orizzontale [-] (frazione di g).
    kv : float, optional
        Coefficiente sismico verticale [-] (frazione di g). Default 0.0.

    Returns
    -------
    float
        Coefficiente di spinta passiva sismica K_pe [-].

    Raises
    ------
    ValueError
        Se l'argomento della radice quadrata e' negativo (condizione
        geometrica non ammissibile).
    """
    if kv >= 1.0:
        raise ValueError(f"kv deve essere < 1.0: {kv}")
    psi = math.atan(kh / (1.0 - kv))

    arg = (
        math.sin(phi + delta) * math.sin(phi + psi + theta)
    ) / (
        math.cos(delta - beta + psi) * math.cos(beta - theta)
    )
    if arg < 0:
        raise ValueError(
            f"Argomento della radice quadrata negativo ({arg:.4f}): "
            "combinazione di parametri non ammissibile per Mononobe-Okabe passivo."
        )
    if arg > 1.0:
        raise ValueError(
            f"Argomento della radice quadrata > 1 ({arg:.4f}): "
            "la formula passiva non e' applicabile per questa combinazione di parametri."
        )

    num = math.cos(phi + psi - beta) ** 2
    denom = (
        math.cos(psi)
        * math.cos(beta) ** 2
        * math.cos(delta - beta + psi)
        * (1.0 - math.sqrt(arg)) ** 2
    )
    if denom == 0:
        raise ValueError(
            "Denominatore nullo: argomento della radice pari a 1, "
            "K_pe non definito per questa combinazione di parametri."
        )
    return num / denom


# ============================================================================
# Verifiche muri di sostegno in condizioni sismiche
# ============================================================================


@ntc_ref(article="7.11.6", latex=r"E_{ae} \le R_d")
def seismic_wall_sliding_check(
    E_ae: float,
    W_wall: float,
    phi_base: float,
    c_base: float = 0.0,
    gamma_R: float = 1.1,
) -> tuple[bool, float]:
    """Verifica a scorrimento del muro di sostegno in condizioni sismiche.

    NTC18 §7.11.6 — La spinta orizzontale sismica deve essere inferiore
    alla resistenza a scorrimento alla base.

    Parameters
    ----------
    E_ae : float
        Spinta attiva sismica totale [kN/m].
    W_wall : float
        Peso totale del muro (struttura + terreno) per unita' di lunghezza
        [kN/m].
    phi_base : float
        Angolo di resistenza al taglio alla base del muro [rad].
    c_base : float, optional
        Coesione alla base del muro [kPa·m]. Default 0.0.
    gamma_R : float, optional
        Coefficiente parziale sulla resistenza [-]. Default 1.1.

    Returns
    -------
    tuple[bool, float]
        (verificato, rapporto E_ae / R_d).
        La verifica e' soddisfatta se il rapporto e' <= 1.0.

    Raises
    ------
    ValueError
        Se E_ae, W_wall sono negativi o gamma_R <= 0.
    """
    if E_ae < 0:
        raise ValueError(f"E_ae non puo' essere negativo: {E_ae}")
    if W_wall < 0:
        raise ValueError(f"W_wall non puo' essere negativo: {W_wall}")
    if gamma_R <= 0:
        raise ValueError(f"gamma_R deve essere positivo: {gamma_R}")

    R_d = (W_wall * math.tan(phi_base) + c_base) / gamma_R
    if R_d == 0:
        raise ValueError(
            "La resistenza a scorrimento R_d e' nulla: "
            "verificare phi_base e c_base."
        )
    ratio = E_ae / R_d
    return ratio <= 1.0, ratio


@ntc_ref(article="7.11.6", latex=r"M_{rib} \le M_{stab}")
def seismic_wall_overturning_check(
    E_ae: float,
    H: float,
    W_wall: float,
    b_base: float,
    kv: float = 0.0,
) -> tuple[bool, float]:
    """Verifica a ribaltamento del muro di sostegno in condizioni sismiche.

    NTC18 §7.11.6 — Il momento ribaltante sismico deve essere inferiore
    al momento stabilizzante.

    Il punto di applicazione della spinta e' assunto a H/3 dalla base
    (distribuzione triangolare della pressione).

    Parameters
    ----------
    E_ae : float
        Spinta attiva sismica totale [kN/m].
    H : float
        Altezza del muro [m].
    W_wall : float
        Peso totale del muro (struttura + terreno) per unita' di lunghezza
        [kN/m].
    b_base : float
        Larghezza della base del muro [m].
    kv : float, optional
        Coefficiente sismico verticale [-] (frazione di g). Default 0.0.

    Returns
    -------
    tuple[bool, float]
        (verificato, rapporto M_rib / M_stab).
        La verifica e' soddisfatta se il rapporto e' <= 1.0.

    Raises
    ------
    ValueError
        Se E_ae, H, W_wall o b_base sono non positivi.
    """
    if E_ae < 0:
        raise ValueError(f"E_ae non puo' essere negativo: {E_ae}")
    if H <= 0:
        raise ValueError(f"H deve essere positivo: {H}")
    if W_wall <= 0:
        raise ValueError(f"W_wall deve essere positivo: {W_wall}")
    if b_base <= 0:
        raise ValueError(f"b_base deve essere positivo: {b_base}")

    M_stab = W_wall * b_base / 2.0
    M_rib = E_ae * H / 3.0
    ratio = M_rib / M_stab
    return ratio <= 1.0, ratio
