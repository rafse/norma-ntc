"""Costruzioni di acciaio — NTC18 §4.2.

Proprieta' materiali, resistenza sezioni, instabilita',
collegamenti bullonati e saldati.

Unita':
- Tensioni/Resistenze: [N/mm^2] = [MPa]
- Forze: [N]
- Aree: [mm^2]
- Moduli di resistenza: [mm^3]
- Coefficienti: [-]
"""

from __future__ import annotations

import math

from pyntc.core.reference import ntc_ref


# ══════════════════════════════════════════════════════════════════════════════
# §4.2.1.1 — PROPRIETA' MATERIALI (Tab. 4.2.I)
# ══════════════════════════════════════════════════════════════════════════════

# Tab.4.2.I — Acciaio per costruzioni metalliche (EN 10025-2 / EN 10025-3)
# Formato: grade -> [(t_max, f_yk, f_tk), ...]
_STEEL_GRADES: dict[str, list[tuple[float, float, float]]] = {
    "S235": [(40.0, 235.0, 360.0), (80.0, 215.0, 360.0)],
    "S275": [(40.0, 275.0, 430.0), (80.0, 255.0, 410.0)],
    "S355": [(40.0, 355.0, 510.0), (80.0, 335.0, 470.0)],
    "S420": [(40.0, 420.0, 520.0), (80.0, 390.0, 520.0)],
    "S450": [(40.0, 450.0, 550.0), (80.0, 430.0, 550.0)],
    "S460": [(40.0, 460.0, 540.0), (80.0, 430.0, 540.0)],
}


@ntc_ref(article="4.2.1.1", table="Tab.4.2.I", latex=r"\text{Tab.\,4.2.I}")
def steel_grade_properties(
    grade: str, thickness: float
) -> tuple[float, float]:
    """Proprieta' acciaio da Tab. 4.2.I [N/mm^2].

    NTC18 §4.2.1.1, Tab. 4.2.I — Tensione di snervamento f_yk e
    tensione di rottura f_tk per laminati a caldo (EN 10025).

    Parameters
    ----------
    grade : str
        Grado dell'acciaio: "S235", "S275", "S355", "S420", "S450", "S460".
    thickness : float
        Spessore nominale dell'elemento [mm]. Deve essere 0 < t <= 80 mm.

    Returns
    -------
    tuple[float, float]
        (f_yk, f_tk): tensione di snervamento e di rottura [N/mm^2].
    """
    key = grade.upper()
    if key not in _STEEL_GRADES:
        raise ValueError(
            f"grade deve essere S235, S275, S355, S420, S450 o S460, "
            f"ricevuto: '{grade}'"
        )
    if thickness <= 0 or thickness > 80.0:
        raise ValueError(
            f"thickness deve essere 0 < t <= 80 mm, ricevuto: {thickness}"
        )
    for t_max, f_yk, f_tk in _STEEL_GRADES[key]:
        if thickness <= t_max:
            return f_yk, f_tk
    # Fallback (non raggiungibile per thickness <= 80)
    raise ValueError(f"thickness fuori range: {thickness}")  # pragma: no cover


# ══════════════════════════════════════════════════════════════════════════════
# §4.2.4.1.2 — RESISTENZA DELLE SEZIONI
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(article="4.2.4.1.2.1", formula="4.2.6", latex=r"N_{pl,Rd} = \frac{A \cdot f_{yk}}{\gamma_{M0}}")
def steel_tension_resistance(
    A: float,
    f_yk: float,
    gamma_M0: float,
    *,
    A_net: float | None = None,
    f_tk: float | None = None,
    gamma_M2: float | None = None,
) -> tuple[float, float | None]:
    """Resistenza a trazione della sezione [N].

    NTC18 §4.2.4.1.2.1 — Formule [4.2.6] e [4.2.7]:
        N_pl,Rd = A * f_yk / gamma_M0       (plasticizzazione lorda)
        N_u,Rd  = 0.9 * A_net * f_tk / gamma_M2  (rottura sezione netta)

    Parameters
    ----------
    A : float
        Area lorda della sezione [mm^2].
    f_yk : float
        Tensione di snervamento [N/mm^2].
    gamma_M0 : float
        Coefficiente parziale gamma_M0 [-].
    A_net : float or None
        Area netta della sezione (fori bulloni) [mm^2].
    f_tk : float or None
        Tensione di rottura [N/mm^2]. Richiesto se A_net fornito.
    gamma_M2 : float or None
        Coefficiente parziale gamma_M2 [-]. Richiesto se A_net fornito.

    Returns
    -------
    tuple[float, float | None]
        (N_pl_Rd, N_u_Rd): resistenza plastica e a rottura [N].
        N_u_Rd e' None se A_net non e' fornito.
    """
    if A <= 0:
        raise ValueError("A deve essere > 0")
    if f_yk <= 0:
        raise ValueError("f_yk deve essere > 0")
    if gamma_M0 <= 0:
        raise ValueError("gamma_M0 deve essere > 0")

    N_pl_Rd = A * f_yk / gamma_M0

    if A_net is not None:
        if f_tk is None or gamma_M2 is None:
            raise ValueError(
                "f_tk e gamma_M2 sono richiesti quando si fornisce A_net"
            )
        if A_net <= 0:
            raise ValueError("A_net deve essere > 0")
        N_u_Rd = 0.9 * A_net * f_tk / gamma_M2
        return N_pl_Rd, N_u_Rd

    return N_pl_Rd, None


@ntc_ref(article="4.2.4.1.2.2", formula="4.2.10", latex=r"N_{c,Rd} = \frac{A \cdot f_{yk}}{\gamma_{M0}}")
def steel_compression_resistance(
    A: float, f_yk: float, gamma_M0: float
) -> float:
    """Resistenza a compressione della sezione [N].

    NTC18 §4.2.4.1.2.2, Formula [4.2.10]:
        N_c,Rd = A * f_yk / gamma_M0

    Parameters
    ----------
    A : float
        Area della sezione [mm^2].
    f_yk : float
        Tensione di snervamento [N/mm^2].
    gamma_M0 : float
        Coefficiente parziale gamma_M0 [-].

    Returns
    -------
    float
        N_c,Rd: resistenza a compressione [N].
    """
    if A <= 0:
        raise ValueError("A deve essere > 0")
    if f_yk <= 0:
        raise ValueError("f_yk deve essere > 0")
    if gamma_M0 <= 0:
        raise ValueError("gamma_M0 deve essere > 0")
    return A * f_yk / gamma_M0


@ntc_ref(article="4.2.4.1.2.3", formula="4.2.12", latex=r"M_{c,Rd} = \frac{W \cdot f_{yk}}{\gamma_{M0}}")
def steel_bending_resistance(
    W: float, f_yk: float, gamma_M0: float
) -> float:
    """Resistenza a flessione della sezione [N*mm].

    NTC18 §4.2.4.1.2.3, Formula [4.2.12]:
        M_c,Rd = W * f_yk / gamma_M0

    Per sezioni di classe 1 e 2: W = W_pl (modulo plastico).
    Per sezioni di classe 3: W = W_el (modulo elastico).

    Parameters
    ----------
    W : float
        Modulo di resistenza (plastico o elastico) [mm^3].
    f_yk : float
        Tensione di snervamento [N/mm^2].
    gamma_M0 : float
        Coefficiente parziale gamma_M0 [-].

    Returns
    -------
    float
        M_c,Rd: resistenza a flessione [N*mm].
    """
    if W <= 0:
        raise ValueError("W deve essere > 0")
    if f_yk <= 0:
        raise ValueError("f_yk deve essere > 0")
    if gamma_M0 <= 0:
        raise ValueError("gamma_M0 deve essere > 0")
    return W * f_yk / gamma_M0


@ntc_ref(article="4.2.4.1.2.4", formula="4.2.17", latex=r"V_{c,Rd} = \frac{A_v \cdot f_{yk}}{\sqrt{3} \cdot \gamma_{M0}}")
def steel_shear_resistance(
    A_v: float, f_yk: float, gamma_M0: float
) -> float:
    """Resistenza a taglio della sezione [N].

    NTC18 §4.2.4.1.2.4, Formula [4.2.17]:
        V_c,Rd = A_v * f_yk / (sqrt(3) * gamma_M0)

    Parameters
    ----------
    A_v : float
        Area resistente a taglio [mm^2].
    f_yk : float
        Tensione di snervamento [N/mm^2].
    gamma_M0 : float
        Coefficiente parziale gamma_M0 [-].

    Returns
    -------
    float
        V_c,Rd: resistenza a taglio [N].
    """
    if A_v <= 0:
        raise ValueError("A_v deve essere > 0")
    if f_yk <= 0:
        raise ValueError("f_yk deve essere > 0")
    if gamma_M0 <= 0:
        raise ValueError("gamma_M0 deve essere > 0")
    return A_v * f_yk / (math.sqrt(3) * gamma_M0)


# ══════════════════════════════════════════════════════════════════════════════
# §4.2.4.1.2.6 — RIDUZIONE PER TAGLIO CONCOMITANTE
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(article="4.2.4.1.2.6", formula="4.2.31", latex=r"\rho = \left(\frac{2 V_{Ed}}{V_{c,Rd}} - 1\right)^2")
def steel_bending_shear_reduction(
    V_Ed: float, V_c_Rd: float
) -> float:
    """Fattore di riduzione rho per flessione in presenza di taglio [-].

    NTC18 §4.2.4.1.2.6, Formula [4.2.31]:
        Se V_Ed <= 0.5 * V_c,Rd: rho = 0 (nessuna riduzione)
        Se V_Ed > 0.5 * V_c,Rd:  rho = (2 * V_Ed / V_c,Rd - 1)^2

    Parameters
    ----------
    V_Ed : float
        Taglio di progetto [N].
    V_c_Rd : float
        Resistenza a taglio della sezione [N].

    Returns
    -------
    float
        Fattore di riduzione rho [-], 0 <= rho <= 1.
    """
    if V_c_Rd <= 0:
        raise ValueError("V_c_Rd deve essere > 0")
    if V_Ed < 0:
        raise ValueError("V_Ed deve essere >= 0")

    if V_Ed <= 0.5 * V_c_Rd:
        return 0.0

    return (2.0 * V_Ed / V_c_Rd - 1.0) ** 2


# ══════════════════════════════════════════════════════════════════════════════
# §4.2.4.1.2.7 — PRESSO/TENSO-FLESSIONE
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(article="4.2.4.1.2.7", formula="4.2.33", latex=r"M_{N,y,Rd} = M_{pl,y,Rd} \cdot \frac{1 - n}{1 - 0{,}5\,a}")
def steel_NM_resistance_y(
    n: float, a: float, M_pl_y_Rd: float
) -> float:
    """Resistenza a flessione ridotta per sforzo assiale — asse forte [N*mm].

    NTC18 §4.2.4.1.2.7, Formula [4.2.33]:
        M_N,y,Rd = M_pl,y,Rd * (1 - n) / (1 - 0.5 * a)
    con M_N,y,Rd <= M_pl,y,Rd.

    Parameters
    ----------
    n : float
        Rapporto N_Ed / N_pl,Rd [-].
    a : float
        Rapporto (A - 2*b*t_f) / A [-] (area anima / area totale).
    M_pl_y_Rd : float
        Resistenza plastica a flessione M_pl,y,Rd [N*mm].

    Returns
    -------
    float
        M_N,y,Rd: resistenza a flessione ridotta [N*mm].
    """
    if n < 0 or n > 1:
        raise ValueError("n deve essere 0 <= n <= 1")
    if a < 0 or a > 1:
        raise ValueError("a deve essere 0 <= a <= 1")
    if M_pl_y_Rd <= 0:
        raise ValueError("M_pl_y_Rd deve essere > 0")

    M_N_y_Rd = M_pl_y_Rd * (1.0 - n) / (1.0 - 0.5 * a)
    return min(M_N_y_Rd, M_pl_y_Rd)


@ntc_ref(article="4.2.4.1.2.7", formula="4.2.34", latex=r"M_{N,z,Rd} = M_{pl,z,Rd} \cdot \left[1 - \left(\frac{n - a}{1 - a}\right)^2\right]")
def steel_NM_resistance_z(
    n: float, a: float, M_pl_z_Rd: float
) -> float:
    """Resistenza a flessione ridotta per sforzo assiale — asse debole [N*mm].

    NTC18 §4.2.4.1.2.7, Formule [4.2.34-4.2.35]:
        Se n <= a: M_N,z,Rd = M_pl,z,Rd
        Se n > a:  M_N,z,Rd = M_pl,z,Rd * [1 - ((n - a) / (1 - a))^2]

    Parameters
    ----------
    n : float
        Rapporto N_Ed / N_pl,Rd [-].
    a : float
        Rapporto (A - 2*b*t_f) / A [-] (area anima / area totale).
    M_pl_z_Rd : float
        Resistenza plastica a flessione M_pl,z,Rd [N*mm].

    Returns
    -------
    float
        M_N,z,Rd: resistenza a flessione ridotta [N*mm].
    """
    if n < 0 or n > 1:
        raise ValueError("n deve essere 0 <= n <= 1")
    if a < 0 or a > 1:
        raise ValueError("a deve essere 0 <= a <= 1")
    if M_pl_z_Rd <= 0:
        raise ValueError("M_pl_z_Rd deve essere > 0")

    if n <= a:
        return M_pl_z_Rd

    return M_pl_z_Rd * (1.0 - ((n - a) / (1.0 - a)) ** 2)


# ══════════════════════════════════════════════════════════════════════════════
# §4.2.4.1.28 — PRESSO/TENSO-FLESSIONE BIASSIALE
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(article="4.2.4.1.28", formula="4.2.38", latex=r"\left(\frac{M_{y,Ed}}{M_{N,y,Rd}}\right)^2 + \left(\frac{M_{z,Ed}}{M_{N,z,Rd}}\right)^{5n} \le 1")
def steel_biaxial_check(
    M_y_Ed: float,
    M_z_Ed: float,
    M_N_y_Rd: float,
    M_N_z_Rd: float,
    n: float,
) -> tuple[bool, float]:
    """Verifica presso/tenso-flessione biassiale [-].

    NTC18 §4.2.4.1.28, Formule [4.2.38-4.2.39]:
        Se n >= 0.2: (M_y_Ed / M_N,y,Rd)^2 + (M_z_Ed / M_N,z,Rd)^(5n) <= 1
        Se n < 0.2:  M_y_Ed / M_N,y,Rd + M_z_Ed / M_N,z,Rd <= 1

    Parameters
    ----------
    M_y_Ed : float
        Momento flettente di progetto asse forte [N*mm].
    M_z_Ed : float
        Momento flettente di progetto asse debole [N*mm].
    M_N_y_Rd : float
        Resistenza ridotta a flessione asse forte [N*mm].
    M_N_z_Rd : float
        Resistenza ridotta a flessione asse debole [N*mm].
    n : float
        Rapporto N_Ed / N_pl,Rd [-].

    Returns
    -------
    tuple[bool, float]
        (verifica_superata, utilization):
        - verifica_superata: True se il rapporto <= 1
        - utilization: valore del rapporto di interazione [-]
    """
    if M_N_y_Rd <= 0:
        raise ValueError("M_N_y_Rd deve essere > 0")
    if M_N_z_Rd <= 0:
        raise ValueError("M_N_z_Rd deve essere > 0")
    if n < 0:
        raise ValueError("n deve essere >= 0")

    ratio_y = abs(M_y_Ed) / M_N_y_Rd
    ratio_z = abs(M_z_Ed) / M_N_z_Rd

    if n >= 0.2:
        # [4.2.38]: esponente alpha=2 per y, beta=5*n per z
        utilization = ratio_y ** 2 + ratio_z ** (5.0 * n)
    else:
        # [4.2.39]: interazione lineare
        utilization = ratio_y + ratio_z

    return utilization <= 1.0, utilization


# ══════════════════════════════════════════════════════════════════════════════
# §4.2.4.1.3.1 — INSTABILITA' ASTE COMPRESSE
# ══════════════════════════════════════════════════════════════════════════════

# Tab.4.2.VIII — Fattori di imperfezione per curve di instabilita'
_IMPERFECTION_FACTORS: dict[str, float] = {
    "a0": 0.13,
    "a": 0.21,
    "b": 0.34,
    "c": 0.49,
    "d": 0.76,
}


@ntc_ref(article="4.2.4.1.3.1", table="Tab.4.2.VIII", latex=r"\text{Tab.\,4.2.VIII}")
def steel_buckling_imperfection(curve: str) -> float:
    """Fattore di imperfezione alpha da Tab. 4.2.VIII [-].

    NTC18 §4.2.4.1.3.1, Tab. 4.2.VIII:
        a0 → 0.13, a → 0.21, b → 0.34, c → 0.49, d → 0.76

    Parameters
    ----------
    curve : str
        Curva di instabilita': "a0", "a", "b", "c" o "d".

    Returns
    -------
    float
        Fattore di imperfezione alpha [-].
    """
    key = curve.lower()
    if key not in _IMPERFECTION_FACTORS:
        raise ValueError(
            f"curve deve essere 'a0', 'a', 'b', 'c' o 'd', "
            f"ricevuto: '{curve}'"
        )
    return _IMPERFECTION_FACTORS[key]


@ntc_ref(article="4.2.4.1.3.1", formula="4.2.44", latex=r"\chi = \frac{1}{\Phi + \sqrt{\Phi^2 - \bar{\lambda}^2}}")
def steel_buckling_reduction(
    lambda_bar: float, alpha: float
) -> float:
    """Coefficiente di riduzione per instabilita' chi [-].

    NTC18 §4.2.4.1.3.1, Formula [4.2.44]:
        Phi = 0.5 * [1 + alpha * (lambda_bar - 0.2) + lambda_bar^2]
        chi = 1 / (Phi + sqrt(Phi^2 - lambda_bar^2))
    con chi <= 1.0.

    Per lambda_bar <= 0.2 si assume chi = 1.0 (instabilita' trascurabile).

    Parameters
    ----------
    lambda_bar : float
        Snellezza adimensionale [-].
    alpha : float
        Fattore di imperfezione [-] (da Tab. 4.2.VIII).

    Returns
    -------
    float
        Coefficiente di riduzione chi [-], 0 < chi <= 1.
    """
    if lambda_bar < 0:
        raise ValueError("lambda_bar deve essere >= 0")
    if alpha < 0:
        raise ValueError("alpha deve essere >= 0")

    if lambda_bar <= 0.2:
        return 1.0

    Phi = 0.5 * (1.0 + alpha * (lambda_bar - 0.2) + lambda_bar ** 2)
    chi = 1.0 / (Phi + math.sqrt(Phi ** 2 - lambda_bar ** 2))
    return min(chi, 1.0)


@ntc_ref(article="4.2.4.1.3.1", formula="4.2.42", latex=r"N_{b,Rd} = \frac{\chi \cdot A \cdot f_{yk}}{\gamma_{M1}}")
def steel_buckling_resistance(
    chi: float, A: float, f_yk: float, gamma_M1: float
) -> float:
    """Resistenza ad instabilita' per aste compresse [N].

    NTC18 §4.2.4.1.3.1, Formula [4.2.42]:
        N_b,Rd = chi * A * f_yk / gamma_M1

    Parameters
    ----------
    chi : float
        Coefficiente di riduzione per instabilita' [-].
    A : float
        Area della sezione [mm^2].
    f_yk : float
        Tensione di snervamento [N/mm^2].
    gamma_M1 : float
        Coefficiente parziale gamma_M1 [-].

    Returns
    -------
    float
        N_b,Rd: resistenza ad instabilita' [N].
    """
    if chi <= 0 or chi > 1:
        raise ValueError("chi deve essere 0 < chi <= 1")
    if A <= 0:
        raise ValueError("A deve essere > 0")
    if f_yk <= 0:
        raise ValueError("f_yk deve essere > 0")
    if gamma_M1 <= 0:
        raise ValueError("gamma_M1 deve essere > 0")
    return chi * A * f_yk / gamma_M1


# ══════════════════════════════════════════════════════════════════════════════
# §4.2.4.1.3.2 — INSTABILITA' FLESSO-TORSIONALE
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(article="4.2.4.1.3.2", formula="4.2.50", latex=r"\chi_{LT} = \frac{1}{\Phi_{LT} + \sqrt{\Phi_{LT}^2 - \bar{\lambda}_{LT}^2}}")
def steel_lt_buckling_reduction(
    lambda_LT_bar: float, alpha_LT: float
) -> float:
    """Coefficiente di riduzione per instabilita' flesso-torsionale chi_LT [-].

    NTC18 §4.2.4.1.3.2, Formula [4.2.50] (metodo generale):
        Phi_LT = 0.5 * [1 + alpha_LT * (lambda_LT_bar - 0.2) + lambda_LT_bar^2]
        chi_LT = 1 / (Phi_LT + sqrt(Phi_LT^2 - lambda_LT_bar^2))
    con chi_LT <= 1.0.

    Per lambda_LT_bar <= 0.2 si assume chi_LT = 1.0.

    Parameters
    ----------
    lambda_LT_bar : float
        Snellezza adimensionale flesso-torsionale [-].
    alpha_LT : float
        Fattore di imperfezione flesso-torsionale [-].

    Returns
    -------
    float
        Coefficiente di riduzione chi_LT [-], 0 < chi_LT <= 1.
    """
    if lambda_LT_bar < 0:
        raise ValueError("lambda_LT_bar deve essere >= 0")
    if alpha_LT < 0:
        raise ValueError("alpha_LT deve essere >= 0")

    if lambda_LT_bar <= 0.2:
        return 1.0

    Phi_LT = 0.5 * (1.0 + alpha_LT * (lambda_LT_bar - 0.2) + lambda_LT_bar ** 2)
    chi_LT = 1.0 / (Phi_LT + math.sqrt(Phi_LT ** 2 - lambda_LT_bar ** 2))
    return min(chi_LT, 1.0)


@ntc_ref(article="4.2.4.1.3.2", formula="4.2.49", latex=r"M_{b,Rd} = \frac{\chi_{LT} \cdot W_y \cdot f_{yk}}{\gamma_{M1}}")
def steel_lt_buckling_resistance(
    chi_LT: float, W_y: float, f_yk: float, gamma_M1: float
) -> float:
    """Resistenza ad instabilita' flesso-torsionale [N*mm].

    NTC18 §4.2.4.1.3.2, Formula [4.2.49]:
        M_b,Rd = chi_LT * W_y * f_yk / gamma_M1

    Parameters
    ----------
    chi_LT : float
        Coefficiente di riduzione flesso-torsionale [-].
    W_y : float
        Modulo di resistenza rispetto all'asse forte [mm^3].
    f_yk : float
        Tensione di snervamento [N/mm^2].
    gamma_M1 : float
        Coefficiente parziale gamma_M1 [-].

    Returns
    -------
    float
        M_b,Rd: resistenza ad instabilita' flesso-torsionale [N*mm].
    """
    if chi_LT <= 0 or chi_LT > 1:
        raise ValueError("chi_LT deve essere 0 < chi_LT <= 1")
    if W_y <= 0:
        raise ValueError("W_y deve essere > 0")
    if f_yk <= 0:
        raise ValueError("f_yk deve essere > 0")
    if gamma_M1 <= 0:
        raise ValueError("gamma_M1 deve essere > 0")
    return chi_LT * W_y * f_yk / gamma_M1


# ══════════════════════════════════════════════════════════════════════════════
# §4.2.8.1.1 — COLLEGAMENTI BULLONATI
# ══════════════════════════════════════════════════════════════════════════════

# Coefficienti alfa_v per classi bulloni (Tab. 4.2.XII / §4.2.8.1.1)
_BOLT_SHEAR_COEFFICIENTS: dict[str, float] = {
    "4.6": 0.6,
    "5.6": 0.6,
    "5.8": 0.5,
    "6.8": 0.5,
    "8.8": 0.6,
    "10.9": 0.5,
}


@ntc_ref(article="4.2.8.1.1", formula="4.2.63", latex=r"F_{v,Rd} = \frac{\alpha_v \cdot f_{ub} \cdot A_s}{\gamma_{M2}}")
def bolt_shear_resistance(
    f_ub: float, A_s: float, bolt_class: str, gamma_M2: float
) -> float:
    """Resistenza a taglio di un bullone [N].

    NTC18 §4.2.8.1.1, Formula [4.2.63]:
        F_v,Rd = alpha_v * f_ub * A_s / gamma_M2

    dove alpha_v = 0.6 per classi 4.6, 5.6, 8.8
                 = 0.5 per classi 5.8, 6.8, 10.9

    Parameters
    ----------
    f_ub : float
        Tensione di rottura del bullone [N/mm^2].
    A_s : float
        Area resistente a trazione del bullone [mm^2].
    bolt_class : str
        Classe del bullone: "4.6", "5.6", "5.8", "6.8", "8.8", "10.9".
    gamma_M2 : float
        Coefficiente parziale gamma_M2 [-].

    Returns
    -------
    float
        F_v,Rd: resistenza a taglio [N].
    """
    if bolt_class not in _BOLT_SHEAR_COEFFICIENTS:
        raise ValueError(
            f"bolt_class deve essere 4.6, 5.6, 5.8, 6.8, 8.8 o 10.9, "
            f"ricevuto: '{bolt_class}'"
        )
    if f_ub <= 0:
        raise ValueError("f_ub deve essere > 0")
    if A_s <= 0:
        raise ValueError("A_s deve essere > 0")
    if gamma_M2 <= 0:
        raise ValueError("gamma_M2 deve essere > 0")

    alpha_v = _BOLT_SHEAR_COEFFICIENTS[bolt_class]
    return alpha_v * f_ub * A_s / gamma_M2


@ntc_ref(article="4.2.8.1.1", formula="4.2.68", latex=r"F_{t,Rd} = \frac{0{,}9 \cdot f_{ub} \cdot A_s}{\gamma_{M2}}")
def bolt_tension_resistance(
    f_ub: float, A_s: float, gamma_M2: float
) -> float:
    """Resistenza a trazione di un bullone [N].

    NTC18 §4.2.8.1.1, Formula [4.2.68]:
        F_t,Rd = 0.9 * f_ub * A_s / gamma_M2

    Parameters
    ----------
    f_ub : float
        Tensione di rottura del bullone [N/mm^2].
    A_s : float
        Area resistente a trazione del bullone [mm^2].
    gamma_M2 : float
        Coefficiente parziale gamma_M2 [-].

    Returns
    -------
    float
        F_t,Rd: resistenza a trazione [N].
    """
    if f_ub <= 0:
        raise ValueError("f_ub deve essere > 0")
    if A_s <= 0:
        raise ValueError("A_s deve essere > 0")
    if gamma_M2 <= 0:
        raise ValueError("gamma_M2 deve essere > 0")
    return 0.9 * f_ub * A_s / gamma_M2


@ntc_ref(article="4.2.8.1.1", formula="4.2.71", latex=r"\frac{F_{v,Ed}}{F_{v,Rd}} + \frac{F_{t,Ed}}{F_{t,Rd}} \le 1{,}0")
def bolt_shear_tension_interaction(
    F_v_Ed: float, F_t_Ed: float, F_v_Rd: float, F_t_Rd: float
) -> tuple[bool, float]:
    """Verifica interazione taglio + trazione bullone [-].

    NTC18 §4.2.8.1.1, Formula [4.2.71]:
        F_v,Ed / F_v,Rd + F_t,Ed / F_t,Rd <= 1.0

    Parameters
    ----------
    F_v_Ed : float
        Taglio di progetto sul bullone [N].
    F_t_Ed : float
        Trazione di progetto sul bullone [N].
    F_v_Rd : float
        Resistenza a taglio del bullone [N].
    F_t_Rd : float
        Resistenza a trazione del bullone [N].

    Returns
    -------
    tuple[bool, float]
        (verifica_superata, utilization):
        - verifica_superata: True se rapporto <= 1
        - utilization: valore del rapporto di interazione [-]
    """
    if F_v_Rd <= 0:
        raise ValueError("F_v_Rd deve essere > 0")
    if F_t_Rd <= 0:
        raise ValueError("F_t_Rd deve essere > 0")
    if F_v_Ed < 0:
        raise ValueError("F_v_Ed deve essere >= 0")
    if F_t_Ed < 0:
        raise ValueError("F_t_Ed deve essere >= 0")

    utilization = F_v_Ed / F_v_Rd + F_t_Ed / F_t_Rd
    return utilization <= 1.0, utilization


@ntc_ref(article="4.2.8.1.1", formula="4.2.67", latex=r"F_{b,Rd} = \frac{k_1 \cdot \alpha_b \cdot f_u \cdot d \cdot t}{\gamma_{M2}}")
def bolt_bearing_resistance(
    k1: float, alpha_b: float, f_u: float, d: float, t: float, gamma_M2: float
) -> float:
    """Resistenza a rifollamento del piatto dell'unione [N].

    NTC18 §4.2.8.1.1, Formula [4.2.67]:
        F_b,Rd = k1 * alpha_b * f_u * d * t / gamma_M2

    I coefficienti k1 e alpha_b dipendono dalla posizione del bullone:

    alpha_b (direzione del carico):
        bordo:   min(e1 / (3*d0),  f_ub/f_u,  1.0)
        interno: min(p1 / (3*d0) - 1/4,  f_ub/f_u,  1.0)

    k1 (direzione perpendicolare al carico):
        bordo:   min(2.8 * e2/d0 - 1.7,  2.5)
        interno: min(1.4 * p2/d0 - 1.7,  2.5)

    Parameters
    ----------
    k1 : float
        Coefficiente k1 [-].
    alpha_b : float
        Coefficiente alpha_b [-].
    f_u : float
        Tensione di rottura dell'acciaio del piatto [N/mm^2].
    d : float
        Diametro nominale del bullone [mm].
    t : float
        Spessore del piatto collegato [mm].
    gamma_M2 : float
        Coefficiente parziale gamma_M2 [-].

    Returns
    -------
    float
        F_b,Rd: resistenza a rifollamento [N].
    """
    if k1 <= 0:
        raise ValueError("k1 deve essere > 0")
    if alpha_b <= 0:
        raise ValueError("alpha_b deve essere > 0")
    if f_u <= 0:
        raise ValueError("f_u deve essere > 0")
    if d <= 0:
        raise ValueError("d deve essere > 0")
    if t <= 0:
        raise ValueError("t deve essere > 0")
    if gamma_M2 <= 0:
        raise ValueError("gamma_M2 deve essere > 0")
    return k1 * alpha_b * f_u * d * t / gamma_M2


@ntc_ref(article="4.2.8.1.1", formula="4.2.70", latex=r"F_{p,Rd} = \frac{0{,}6 \cdot \pi \cdot d_m \cdot t_p \cdot f_u}{\gamma_{M2}}")
def bolt_punching_resistance(
    d_m: float, t_p: float, f_u: float, gamma_M2: float
) -> float:
    """Resistenza a punzonamento del piatto collegato [N].

    NTC18 §4.2.8.1.1, Formula [4.2.70]:
        F_p,Rd = 0.6 * pi * d_m * t_p * f_u / gamma_M2

    Parameters
    ----------
    d_m : float
        Minimo tra diametro del dado e diametro medio della testa
        del bullone [mm].
    t_p : float
        Spessore del piatto [mm].
    f_u : float
        Tensione di rottura dell'acciaio del piatto [N/mm^2].
    gamma_M2 : float
        Coefficiente parziale gamma_M2 [-].

    Returns
    -------
    float
        F_p,Rd: resistenza a punzonamento [N].
    """
    if d_m <= 0:
        raise ValueError("d_m deve essere > 0")
    if t_p <= 0:
        raise ValueError("t_p deve essere > 0")
    if f_u <= 0:
        raise ValueError("f_u deve essere > 0")
    if gamma_M2 <= 0:
        raise ValueError("gamma_M2 deve essere > 0")
    return 0.6 * math.pi * d_m * t_p * f_u / gamma_M2


@ntc_ref(article="4.2.8.1.1", formula="4.2.72", latex=r"F_{s,Rd} = \frac{n \cdot \mu \cdot F_{p,Cd}}{\gamma_{M3}}")
def bolt_friction_resistance(
    n: int, mu: float, F_p_Cd: float, gamma_M3: float
) -> float:
    """Resistenza allo scorrimento di un bullone precaricato [N].

    NTC18 §4.2.8.1.1, Formula [4.2.72]:
        F_s,Rd = n * mu * F_p,Cd / gamma_M3

    Valori tipici di mu:
        0.5 — superfici sabbiate, esenti da ruggine
        0.4 — superfici sabbiate e verniciate (Al o Zn)
        0.3 — superfici spazzolate o alla fiamma
        0.2 — superfici non trattate

    Parameters
    ----------
    n : int
        Numero di superfici di attrito [-].
    mu : float
        Coefficiente di attrito [-].
    F_p_Cd : float
        Forza di precarico del bullone [N].
    gamma_M3 : float
        Coefficiente parziale gamma_M3 [-].

    Returns
    -------
    float
        F_s,Rd: resistenza allo scorrimento [N].
    """
    if n <= 0:
        raise ValueError("n deve essere > 0")
    if mu <= 0:
        raise ValueError("mu deve essere > 0")
    if F_p_Cd <= 0:
        raise ValueError("F_p_Cd deve essere > 0")
    if gamma_M3 <= 0:
        raise ValueError("gamma_M3 deve essere > 0")
    return n * mu * F_p_Cd / gamma_M3


@ntc_ref(article="4.2.8.1.1", formula="4.2.73", latex=r"F_{s,Rd} = \frac{n \cdot \mu \cdot (F_{p,Cd} - 0{,}8 \cdot F_{t,Ed})}{\gamma_{M3}}")
def bolt_friction_tension_resistance(
    n: int, mu: float, F_p_Cd: float, F_t_Ed: float, gamma_M3: float
) -> float:
    """Resistenza allo scorrimento con trazione concomitante [N].

    NTC18 §4.2.8.1.1, Formula [4.2.73]:
        F_s,Rd = n * mu * (F_p,Cd - 0.8 * F_t,Ed) / gamma_M3

    Parameters
    ----------
    n : int
        Numero di superfici di attrito [-].
    mu : float
        Coefficiente di attrito [-].
    F_p_Cd : float
        Forza di precarico del bullone [N].
    F_t_Ed : float
        Trazione di progetto sul bullone [N].
    gamma_M3 : float
        Coefficiente parziale gamma_M3 [-].

    Returns
    -------
    float
        F_s,Rd: resistenza allo scorrimento ridotta [N].
    """
    if n <= 0:
        raise ValueError("n deve essere > 0")
    if mu <= 0:
        raise ValueError("mu deve essere > 0")
    if F_p_Cd <= 0:
        raise ValueError("F_p_Cd deve essere > 0")
    if F_t_Ed < 0:
        raise ValueError("F_t_Ed deve essere >= 0")
    if gamma_M3 <= 0:
        raise ValueError("gamma_M3 deve essere > 0")
    return n * mu * (F_p_Cd - 0.8 * F_t_Ed) / gamma_M3


# ══════════════════════════════════════════════════════════════════════════════
# §4.2.8.2.4 — SALDATURE A CORDONI D'ANGOLO
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(article="4.2.8.2.4", formula="4.2.83", latex=r"F_{w,Rd} = \frac{a \cdot f_{tk}}{\sqrt{3} \cdot \beta_w \cdot \gamma_{M2}}")
def weld_fillet_resistance(
    a: float, f_tk: float, beta_w: float, gamma_M2: float
) -> float:
    """Resistenza per unita' di lunghezza di cordone d'angolo [N/mm].

    NTC18 §4.2.8.2.4, Formula [4.2.83]:
        F_w,Rd = a * f_tk / (sqrt(3) * beta_w * gamma_M2)

    Fattore di correlazione beta_w (Tab. 4.2.XIII):
        S235 → 0.80, S275 → 0.85, S355 → 0.90, S420/S460 → 1.00

    Parameters
    ----------
    a : float
        Altezza di gola del cordone [mm].
    f_tk : float
        Tensione di rottura dell'acciaio base [N/mm^2].
    beta_w : float
        Fattore di correlazione [-] (da Tab. 4.2.XIII).
    gamma_M2 : float
        Coefficiente parziale gamma_M2 [-].

    Returns
    -------
    float
        F_w,Rd: resistenza per unita' di lunghezza [N/mm].
    """
    if a <= 0:
        raise ValueError("a deve essere > 0")
    if f_tk <= 0:
        raise ValueError("f_tk deve essere > 0")
    if beta_w <= 0:
        raise ValueError("beta_w deve essere > 0")
    if gamma_M2 <= 0:
        raise ValueError("gamma_M2 deve essere > 0")
    return a * f_tk / (math.sqrt(3) * beta_w * gamma_M2)


# ══════════════════════════════════════════════════════════════════════════════
# §4.2.4.1.2.3 — FLESSIONE SEZIONI CLASSE 3 E CLASSE 4
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(
    article="4.2.4.1.2.3",
    formula="4.2.13",
    latex=r"M_{el,Rd} = \frac{W_{el,min} \cdot f_{yk}}{\gamma_{M0}}",
)
def steel_bending_resistance_class3(
    W_el_min: float, f_yk: float, gamma_M0: float = 1.0
) -> float:
    """Resistenza a flessione elastica per sezioni di classe 3 [N*mm].

    NTC18 §4.2.4.1.2.3, Formula [4.2.13]:
        M_c,Rd = M_el,Rd = W_el,min * f_yk / gamma_M0

    Parameters
    ----------
    W_el_min : float
        Modulo di resistenza elastico minimo della sezione [mm^3].
    f_yk : float
        Tensione di snervamento caratteristica [N/mm^2].
    gamma_M0 : float
        Coefficiente parziale gamma_M0 [-]. Default NTC18: 1.0.

    Returns
    -------
    float
        M_el,Rd: resistenza a flessione elastica [N*mm].
    """
    if W_el_min <= 0:
        raise ValueError("W_el_min deve essere > 0")
    if f_yk <= 0:
        raise ValueError("f_yk deve essere > 0")
    if gamma_M0 <= 0:
        raise ValueError("gamma_M0 deve essere > 0")
    return W_el_min * f_yk / gamma_M0


@ntc_ref(
    article="4.2.4.1.2.3",
    formula="4.2.14",
    latex=r"M_{eff,Rd} = \frac{W_{eff,min} \cdot f_{yk}}{\gamma_{M0}}",
)
def steel_bending_resistance_class4(
    W_eff_min: float, f_yk: float, gamma_M0: float = 1.0
) -> float:
    """Resistenza a flessione per sezioni di classe 4 (sezione efficace) [N*mm].

    NTC18 §4.2.4.1.2.3, Formula [4.2.14]:
        M_c,Rd = M_eff,Rd = W_eff,min * f_yk / gamma_M0

    Parameters
    ----------
    W_eff_min : float
        Modulo di resistenza della sezione efficace minimo [mm^3].
    f_yk : float
        Tensione di snervamento caratteristica [N/mm^2].
    gamma_M0 : float
        Coefficiente parziale gamma_M0 [-]. Default NTC18: 1.0.

    Returns
    -------
    float
        M_eff,Rd: resistenza a flessione sezione efficace [N*mm].
    """
    if W_eff_min <= 0:
        raise ValueError("W_eff_min deve essere > 0")
    if f_yk <= 0:
        raise ValueError("f_yk deve essere > 0")
    if gamma_M0 <= 0:
        raise ValueError("gamma_M0 deve essere > 0")
    return W_eff_min * f_yk / gamma_M0


# ── §4.2.4.1.2.5 — Torsione ────────────────────────────────────────────────


@ntc_ref(
    article="4.2.4.1.2.5",
    formula="4.2.28",
    latex=r"T_{Rd} = \frac{W_t \cdot f_{yk}}{\sqrt{3} \cdot \gamma_{M0}}",
)
def steel_torsion_resistance(
    W_t: float, f_yk: float, gamma_M0: float = 1.0
) -> float:
    """Resistenza a torsione della sezione [N*mm].

    NTC18 §4.2.4.1.2.5 — Resistenza a torsione (formula standard EN):
        T_Rd = W_t * f_yk / (sqrt(3) * gamma_M0)

    dove W_t e' il modulo resistente a torsione (W_t,el per torsione
    uniforme, W_t = 2*A_m*t per sezioni tubolari).

    Parameters
    ----------
    W_t : float
        Modulo resistente a torsione della sezione [mm^3].
    f_yk : float
        Tensione di snervamento caratteristica [N/mm^2].
    gamma_M0 : float
        Coefficiente parziale gamma_M0 [-]. Default NTC18: 1.0.

    Returns
    -------
    float
        T_Rd: resistenza a torsione [N*mm].
    """
    if W_t <= 0:
        raise ValueError("W_t deve essere > 0")
    if f_yk <= 0:
        raise ValueError("f_yk deve essere > 0")
    if gamma_M0 <= 0:
        raise ValueError("gamma_M0 deve essere > 0")
    return W_t * f_yk / (math.sqrt(3) * gamma_M0)


@ntc_ref(
    article="4.2.4.1.2.5",
    formula="4.2.28",
    latex=r"\frac{T_{Ed}}{T_{Rd}} \le 1{,}0",
)
def steel_torsion_check(T_Ed: float, T_Rd: float) -> tuple[bool, float]:
    """Verifica a torsione della sezione [-].

    NTC18 §4.2.4.1.2.5, Formula [4.2.28]:
        T_Ed / T_Rd <= 1.0

    Parameters
    ----------
    T_Ed : float
        Momento torcente di progetto [N*mm].
    T_Rd : float
        Resistenza a torsione della sezione [N*mm].

    Returns
    -------
    tuple[bool, float]
        (verifica_superata, utilization):
        - verifica_superata: True se T_Ed / T_Rd <= 1.0
        - utilization: rapporto T_Ed / T_Rd [-]
    """
    if T_Rd <= 0:
        raise ValueError("T_Rd deve essere > 0")
    if T_Ed < 0:
        raise ValueError("T_Ed deve essere >= 0")
    utilization = T_Ed / T_Rd
    return utilization <= 1.0, utilization


# ── §4.2.4.1.3.1 — Snellezza adimensionale (classi 1-3 e classe 4) ──────────


@ntc_ref(
    article="4.2.4.1.3.1",
    formula="4.2.45",
    latex=(
        r"\bar{\lambda} = \sqrt{\frac{A \cdot f_{yk}}{N_{cr}}}"
        r"\quad \text{(cl.\,1\text{-}3)} \;"
        r";\quad \bar{\lambda} = \sqrt{\frac{A_{\text{eff}} \cdot f_{yk}}{N_{cr}}}"
        r"\quad \text{(cl.\,4)}"
    ),
)
def steel_relative_slenderness(
    A_or_A_eff: float,
    f_yk: float,
    N_cr: float,
    section_class: int = 1,
) -> float:
    """Snellezza adimensionale per aste compresse [-].

    NTC18 §4.2.4.1.3.1:
        Classi 1, 2, 3 — Formula [4.2.45]:
            lambda_bar = sqrt(A * f_yk / N_cr)
        Classe 4 — Formula [4.2.46]:
            lambda_bar = sqrt(A_eff * f_yk / N_cr)

    Parameters
    ----------
    A_or_A_eff : float
        Area lorda A (classi 1-3) o area efficace A_eff (classe 4) [mm^2].
    f_yk : float
        Tensione di snervamento caratteristica [N/mm^2].
    N_cr : float
        Carico critico euleriano [N].
    section_class : int
        Classe della sezione: 1, 2, 3 → Formula [4.2.45];
        4 → Formula [4.2.46]. Default: 1.

    Returns
    -------
    float
        lambda_bar: snellezza adimensionale [-].
    """
    if A_or_A_eff <= 0:
        raise ValueError("A_or_A_eff deve essere > 0")
    if f_yk <= 0:
        raise ValueError("f_yk deve essere > 0")
    if N_cr <= 0:
        raise ValueError("N_cr deve essere > 0")
    if section_class not in (1, 2, 3, 4):
        raise ValueError("section_class deve essere 1, 2, 3 o 4")
    return math.sqrt(A_or_A_eff * f_yk / N_cr)


@ntc_ref(
    article="4.2.4.1.3.1",
    formula="4.2.43",
    latex=r"N_{b,Rd} = \frac{\chi \cdot A_{\text{eff}} \cdot f_{yk}}{\gamma_{M1}}",
)
def steel_buckling_resistance_class4(
    chi: float, A_eff: float, f_yk: float, gamma_M1: float = 1.0
) -> float:
    """Resistenza ad instabilita' per sezioni di classe 4 [N].

    NTC18 §4.2.4.1.3.1, Formula [4.2.43]:
        N_b,Rd = chi * A_eff * f_yk / gamma_M1

    Parameters
    ----------
    chi : float
        Coefficiente di riduzione per instabilita' [-].
    A_eff : float
        Area efficace della sezione di classe 4 [mm^2].
    f_yk : float
        Tensione di snervamento caratteristica [N/mm^2].
    gamma_M1 : float
        Coefficiente parziale gamma_M1 [-]. Default NTC18: 1.0.

    Returns
    -------
    float
        N_b,Rd: resistenza ad instabilita' [N].
    """
    if chi <= 0 or chi > 1:
        raise ValueError("chi deve essere 0 < chi <= 1")
    if A_eff <= 0:
        raise ValueError("A_eff deve essere > 0")
    if f_yk <= 0:
        raise ValueError("f_yk deve essere > 0")
    if gamma_M1 <= 0:
        raise ValueError("gamma_M1 deve essere > 0")
    return chi * A_eff * f_yk / gamma_M1


# ── §4.2.8.2.4 — Verifica combinata saldatura ────────────────────────────────


@ntc_ref(
    article="4.2.8.2.4",
    formula="4.2.81",
    latex=(
        r"\sqrt{\sigma_{\perp}^2 + 3(\tau_{\perp}^2 + \tau_{\parallel}^2)}"
        r"\le \frac{f_u}{\beta_w \cdot \gamma_{M2}}"
    ),
)
def weld_combined_stress_check(
    sigma_perp: float,
    tau_perp: float,
    tau_par: float,
    f_u: float,
    beta_w: float,
    gamma_M2: float = 1.25,
) -> tuple[bool, float]:
    """Verifica tensionale combinata di cordone d'angolo [-].

    NTC18 §4.2.8.2.4, Formula [4.2.81]:
        sqrt(sigma_perp^2 + 3*(tau_perp^2 + tau_par^2)) <= f_u / (beta_w * gamma_M2)

    dove:
        sigma_perp: tensione normale perpendicolare al piano della gola
        tau_perp:   tensione tangenziale perp. all'asse del cordone
        tau_par:    tensione tangenziale parallela all'asse del cordone

    Fattore di correlazione beta_w (Tab. 4.2.XIII):
        S235 → 0.80, S275 → 0.85, S355 → 0.90, S420/S460 → 1.00

    Parameters
    ----------
    sigma_perp : float
        Tensione normale perpendicolare al piano della gola [N/mm^2].
    tau_perp : float
        Tensione tangenziale perpendicolare all'asse del cordone [N/mm^2].
    tau_par : float
        Tensione tangenziale parallela all'asse del cordone [N/mm^2].
    f_u : float
        Tensione di rottura dell'acciaio base [N/mm^2].
    beta_w : float
        Fattore di correlazione [-] (da Tab. 4.2.XIII).
    gamma_M2 : float
        Coefficiente parziale gamma_M2 [-]. Default NTC18: 1.25.

    Returns
    -------
    tuple[bool, float]
        (verifica_superata, ratio):
        - verifica_superata: True se ratio <= 1.0
        - ratio = sqrt(...) / (f_u / (beta_w * gamma_M2)) [-]
    """
    if f_u <= 0:
        raise ValueError("f_u deve essere > 0")
    if beta_w <= 0:
        raise ValueError("beta_w deve essere > 0")
    if gamma_M2 <= 0:
        raise ValueError("gamma_M2 deve essere > 0")

    sigma_eq = math.sqrt(sigma_perp**2 + 3.0 * (tau_perp**2 + tau_par**2))
    f_limit = f_u / (beta_w * gamma_M2)
    ratio = sigma_eq / f_limit
    return ratio <= 1.0, ratio


# ══════════════════════════════════════════════════════════════════════════════
# §4.2.4.1.2 — AREA RESISTENTE A TAGLIO
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(
    article="4.2.4.1.2.4",
    formula="4.2.18",
    latex=(
        r"A_v = \begin{cases}"
        r"A - 2bt_f + (t_w + 2r)t_f & \text{I/H laminati}\\"
        r"A - 2bt_f + (t_w + r)t_f & \text{I/H saldati}\\"
        r"A - \sum h_w t_w & \text{scatolare}\\"
        r"0{,}9(A - b t_f) & \text{T}\\"
        r"2A/\pi & \text{circolare piena}"
        r"\end{cases}"
    ),
)
def steel_shear_area(
    section: str,
    A: float,
    *,
    b: float | None = None,
    t_f: float | None = None,
    t_w: float | None = None,
    r: float = 0.0,
    h: float | None = None,
    hw_tw_sum: float | None = None,
    load_direction: str = "height",
) -> float:
    """Area resistente a taglio A_v per diversi profili [mm^2].

    NTC18 §4.2.4.1.2.4, Formule [4.2.18]–[4.2.23]:
    - "I_H_rolled": A_v = A - 2*b*t_f + (t_w + 2*r)*t_f  [4.2.18]
    - "I_H_weld":   A_v = A - 2*b*t_f + (t_w + r)*t_f    [4.2.19]
    - "box":        A_v = A - hw_tw_sum                    [4.2.20]
    - "T":          A_v = 0.9*(A - b*t_f)                 [4.2.21]
    - "rectangular": A_v = A*h/(b+h) o A*b/(b+h)          [4.2.22]
    - "circular":   A_v = 2*A/pi                           [4.2.23]

    Parameters
    ----------
    section : str
        Tipo di sezione: "I_H_rolled", "I_H_weld", "box", "T",
        "rectangular", "circular".
    A : float
        Area totale della sezione [mm^2].
    b : float, optional
        Larghezza delle ali [mm].
    t_f : float, optional
        Spessore delle ali [mm].
    t_w : float, optional
        Spessore dell'anima [mm].
    r : float, optional
        Raccordo d'angolo o gola della saldatura [mm]. Default 0.
    h : float, optional
        Altezza del profilo [mm] (per sezione rettangolare).
    hw_tw_sum : float, optional
        Somma (h_w * t_w) delle anime [mm^2] (per sezione scatolare).
    load_direction : str, optional
        Direzione del carico per sezione rettangolare:
        "height" (carico parallelo all'altezza) o "width". Default "height".

    Returns
    -------
    float
        A_v: area resistente a taglio [mm^2].
    """
    if A <= 0:
        raise ValueError("A deve essere > 0")

    if section in ("I_H_rolled", "I_H_weld"):
        if b is None or t_f is None or t_w is None:
            raise ValueError(
                f"Per section='{section}' sono richiesti b, t_f, t_w"
            )
        factor = 2.0 if section == "I_H_rolled" else 1.0
        return A - 2.0 * b * t_f + (t_w + factor * r) * t_f

    elif section == "box":
        if hw_tw_sum is None:
            raise ValueError("Per section='box' è richiesto hw_tw_sum")
        return A - hw_tw_sum

    elif section == "T":
        if b is None or t_f is None:
            raise ValueError("Per section='T' sono richiesti b e t_f")
        return 0.9 * (A - b * t_f)

    elif section == "rectangular":
        if b is None or h is None:
            raise ValueError("Per section='rectangular' sono richiesti b e h")
        if load_direction == "height":
            return A * h / (b + h)
        elif load_direction == "width":
            return A * b / (b + h)
        else:
            raise ValueError(
                "load_direction deve essere 'height' o 'width'"
            )

    elif section == "circular":
        return 2.0 * A / math.pi

    else:
        raise ValueError(
            f"section '{section}' non riconosciuto. "
            "Valori ammessi: 'I_H_rolled', 'I_H_weld', 'box', 'T', "
            "'rectangular', 'circular'."
        )


# ══════════════════════════════════════════════════════════════════════════════
# §4.2.4.1.2 — VERIFICA VON MISES
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(
    article="4.2.4.1.2",
    formula="4.2.4",
    latex=(
        r"\sqrt{\sigma_x^2 + \sigma_y^2 - \sigma_x\sigma_y + 3\tau^2}"
        r"\le f_{yk}/\gamma_{M0}"
    ),
)
def steel_von_mises_check(
    sigma_x: float,
    sigma_y: float,
    tau: float,
    f_yk: float,
    gamma_M0: float,
) -> tuple[bool, float]:
    """Verifica dello stato tensionale equivalente (Von Mises) [-].

    NTC18 §4.2.4.1.2, Formula [4.2.4]:
        sqrt(σ_x² + σ_y² - σ_x*σ_y + 3*τ²) ≤ f_yk / γ_M0

    Parameters
    ----------
    sigma_x : float
        Tensione normale nella direzione x [N/mm^2].
    sigma_y : float
        Tensione normale nella direzione y [N/mm^2].
    tau : float
        Tensione tangenziale [N/mm^2].
    f_yk : float
        Tensione di snervamento caratteristica [N/mm^2].
    gamma_M0 : float
        Coefficiente parziale gamma_M0 [-].

    Returns
    -------
    tuple[bool, float]
        (verificata, ratio): verificata = True se ratio <= 1.0;
        ratio = sigma_eq / (f_yk / gamma_M0).
    """
    if f_yk <= 0:
        raise ValueError("f_yk deve essere > 0")
    if gamma_M0 <= 0:
        raise ValueError("gamma_M0 deve essere > 0")
    sigma_eq = math.sqrt(sigma_x**2 + sigma_y**2 - sigma_x * sigma_y + 3.0 * tau**2)
    f_limit = f_yk / gamma_M0
    ratio = sigma_eq / f_limit
    return ratio <= 1.0, ratio


# ══════════════════════════════════════════════════════════════════════════════
# §4.2.8.1.2 — COLLEGAMENTI CON PERNI
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(
    article="4.2.8.1.2",
    formula="4.2.75",
    latex=r"F_{v,Rd} = \frac{0{,}6 \cdot f_{upk} \cdot A}{\gamma_{M2}}",
)
def pin_shear_resistance(
    f_upk: float, A: float, gamma_M2: float
) -> float:
    """Resistenza a taglio del perno [N].

    NTC18 §4.2.8.1.2, Formula [4.2.75]:
        F_v,Rd = 0.6 * f_upk * A / gamma_M2

    Parameters
    ----------
    f_upk : float
        Tensione di rottura caratteristica del perno [N/mm^2].
    A : float
        Area della sezione trasversale del perno [mm^2].
    gamma_M2 : float
        Coefficiente parziale gamma_M2 [-].

    Returns
    -------
    float
        F_v,Rd: resistenza a taglio del perno [N].
    """
    if f_upk <= 0:
        raise ValueError("f_upk deve essere > 0")
    if A <= 0:
        raise ValueError("A deve essere > 0")
    if gamma_M2 <= 0:
        raise ValueError("gamma_M2 deve essere > 0")
    return 0.6 * f_upk * A / gamma_M2


@ntc_ref(
    article="4.2.8.1.2",
    formula="4.2.76",
    latex=r"F_{b,Rd} = \frac{1{,}5 \cdot t \cdot d \cdot f_y}{\gamma_{M3}}",
)
def pin_bearing_resistance(
    t: float, d: float, f_y: float, gamma_M3: float
) -> float:
    """Resistenza a rifollamento del foro del perno [N].

    NTC18 §4.2.8.1.2, Formula [4.2.76]:
        F_b,Rd = 1.5 * t * d * f_y / gamma_M3

    Parameters
    ----------
    t : float
        Spessore della piastra [mm].
    d : float
        Diametro del perno [mm].
    f_y : float
        Tensione di snervamento della piastra [N/mm^2].
    gamma_M3 : float
        Coefficiente parziale gamma_M3 [-].

    Returns
    -------
    float
        F_b,Rd: resistenza a rifollamento [N].
    """
    if t <= 0:
        raise ValueError("t deve essere > 0")
    if d <= 0:
        raise ValueError("d deve essere > 0")
    if f_y <= 0:
        raise ValueError("f_y deve essere > 0")
    if gamma_M3 <= 0:
        raise ValueError("gamma_M3 deve essere > 0")
    return 1.5 * t * d * f_y / gamma_M3
