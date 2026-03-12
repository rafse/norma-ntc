"""Costruzioni composte acciaio-calcestruzzo — NTC18 §4.3.

Verifiche di resistenza, stabilita' e connessione per elementi composti
acciaio-calcestruzzo secondo NTC 2018 Cap.4.3.
"""

from __future__ import annotations

import math

from pyntc.core.reference import ntc_ref


# ============================================================================
# TRAVI — Larghezza efficace
# ============================================================================


@ntc_ref(article="4.3.2.3", formula="4.3.2", latex=r"b_{\mathrm{eff}} = b_0 + b_{e1} + b_{e2}, \quad b_{ei} = \min\!\left(\frac{L_0}{8},\, b_i\right)")
def composite_effective_width(
    b_0: float, L_0: float, b_1: float, b_2: float
) -> float:
    """Larghezza efficace della soletta in calcestruzzo [mm].

    NTC18 §4.3.2.3 — La larghezza collaborante e' determinata come
    b_eff = b_0 + b_e1 + b_e2.

    Parameters
    ----------
    b_0 : float
        Distanza tra gli assi dei connettori [mm].
    L_0 : float
        Luce equivalente (distanza tra punti di momento nullo) [mm].
    b_1 : float
        Larghezza di soletta disponibile lato 1 [mm].
    b_2 : float
        Larghezza di soletta disponibile lato 2 [mm].

    Returns
    -------
    float
        Larghezza efficace b_eff [mm].
    """
    b_e1 = min(L_0 / 8, b_1)
    b_e2 = min(L_0 / 8, b_2)
    return b_0 + b_e1 + b_e2


# ============================================================================
# TRAVI — Ridistribuzione dei momenti
# ============================================================================

# Tab.4.3.I — Limiti di ridistribuzione (%)
_REDISTRIBUTION_LIMITS: dict[tuple[int, str], float] = {
    (1, "uncracked"): 40,
    (1, "cracked"): 25,
    (2, "uncracked"): 30,
    (2, "cracked"): 15,
    (3, "uncracked"): 20,
    (3, "cracked"): 10,
    (4, "uncracked"): 10,
    (4, "cracked"): 0,
}


@ntc_ref(article="4.3.2.2.1", table="Tab.4.3.I", latex=r"\text{Tab.\,4.3.I}")
def composite_moment_redistribution_limits(
    section_class: int, analysis_type: str
) -> float:
    """Percentuale massima di ridistribuzione del momento negativo [%].

    NTC18 §4.3.2.2.1 Tab.4.3.I.

    Parameters
    ----------
    section_class : int
        Classe della sezione (1, 2, 3 o 4).
    analysis_type : str
        Tipo di analisi: ``"uncracked"`` o ``"cracked"``.

    Returns
    -------
    float
        Limite percentuale di ridistribuzione [%].
    """
    if section_class not in (1, 2, 3, 4):
        raise ValueError(f"Classe sezione non valida: {section_class}")
    if analysis_type not in ("uncracked", "cracked"):
        raise ValueError(f"Tipo analisi non valido: {analysis_type!r}")
    return _REDISTRIBUTION_LIMITS[(section_class, analysis_type)]


# ============================================================================
# CONNETTORI — Coefficiente alpha
# ============================================================================


@ntc_ref(article="4.3.4.3.1.2", formula="4.3.11", latex=r"\alpha = \begin{cases} 0{,}2\left(\dfrac{h_{wc}}{d}+1\right) & 3 \le \dfrac{h_{wc}}{d} \le 4 \\ 1{,}0 & \dfrac{h_{wc}}{d} > 4 \end{cases}")
def composite_stud_alpha(h_wc: float, d: float) -> float:
    """Coefficiente alpha per connettori a piolo [-].

    NTC18 §4.3.4.3.1.2 [4.3.11a/b].

    Parameters
    ----------
    h_wc : float
        Altezza del piolo dopo la saldatura [mm].
    d : float
        Diametro del gambo del piolo [mm].

    Returns
    -------
    float
        Coefficiente alpha [-].
    """
    ratio = h_wc / d
    if ratio < 3:
        raise ValueError(f"h_wc/d = {ratio:.2f} < 3: fuori dominio normativo")
    if ratio <= 4:
        return 0.2 * (ratio + 1)
    return 1.0


# ============================================================================
# CONNETTORI — Resistenza a taglio del piolo
# ============================================================================


@ntc_ref(article="4.3.4.3.1.2", formula="4.3.9", latex=r"P_{Rd} = \min\!\left(\frac{0{,}8\,f_u\,\pi\,d^2/4}{\gamma_V},\;\frac{0{,}29\,\alpha\,d^2\sqrt{f_{ck}\,E_{cm}}}{\gamma_V}\right)")
def composite_stud_resistance(
    d: float,
    h_wc: float,
    f_u: float,
    f_ck: float,
    E_cm: float,
    gamma_V: float,
) -> float:
    """Resistenza di progetto a taglio di un piolo connettore [N].

    NTC18 §4.3.4.3.1.2 — Minore tra rottura del piolo [4.3.9]
    e schiacciamento del calcestruzzo [4.3.10].

    Parameters
    ----------
    d : float
        Diametro del piolo [mm] (16-25 mm).
    h_wc : float
        Altezza del piolo dopo saldatura [mm].
    f_u : float
        Resistenza a rottura dell'acciaio del piolo [N/mm²] (cap 500 MPa).
    f_ck : float
        Resistenza cilindrica caratteristica del calcestruzzo [N/mm²].
    E_cm : float
        Modulo elastico medio del calcestruzzo [N/mm²].
    gamma_V : float
        Fattore parziale di sicurezza [-] (tipicamente 1.25).

    Returns
    -------
    float
        Resistenza di progetto P_Rd [N].
    """
    # Cap f_u a 500 MPa come da norma
    f_u_eff = min(f_u, 500.0)

    # [4.3.9] — Rottura del piolo (acciaio)
    P_steel = 0.8 * f_u_eff * (math.pi * d**2 / 4) / gamma_V

    # [4.3.11] — Coefficiente alpha
    alpha = composite_stud_alpha.__wrapped__(h_wc, d)

    # [4.3.10] — Schiacciamento calcestruzzo
    P_concrete = 0.29 * alpha * d**2 * math.sqrt(f_ck * E_cm) / gamma_V

    return min(P_steel, P_concrete)


# ============================================================================
# CONNETTORI — Fattore riduttivo per lamiera grecata
# ============================================================================


@ntc_ref(article="4.3.4.3.1.2", formula="4.3.13", latex=r"k_1 = \min\!\left(0{,}6\,\frac{b_0\,(h_{wc}-h_p)}{h_p^2},\;1{,}0\right)")
def composite_profiled_sheet_reduction(
    b_0: float,
    h_wc: float,
    h_p: float,
    direction: str,
    *,
    n_studs: int = 1,
) -> float:
    """Fattore riduttivo k_1 per solette con lamiera grecata [-].

    NTC18 §4.3.4.3.1.2 [4.3.13] greche parallele, [4.3.14] greche trasversali.

    Parameters
    ----------
    b_0 : float
        Distanza tra gli assi dei connettori (o larghezza greca) [mm].
    h_wc : float
        Altezza del connettore [mm].
    h_p : float
        Altezza della lamiera grecata [mm].
    direction : str
        ``"parallel"`` o ``"transverse"`` rispetto al profilo.
    n_studs : int
        Numero di pioli per greca (solo per ``"transverse"``).

    Returns
    -------
    float
        Fattore riduttivo k_1 [-] (≤ 1.0).
    """
    if direction not in ("parallel", "transverse"):
        raise ValueError(f"Direzione non valida: {direction!r}")

    # L'altezza del connettore e' limitata a h_p + 75 mm
    h_wc_eff = min(h_wc, h_p + 75)

    if direction == "parallel":
        # [4.3.13]
        k1 = 0.6 * b_0 * (h_wc_eff - h_p) / h_p**2
    else:
        # [4.3.14]
        k1 = 0.7 * b_0 * (h_wc_eff - h_p) / (h_p**2 * math.sqrt(n_studs))

    return min(k1, 1.0)


# ============================================================================
# CONNETTORI — Grado minimo di connessione
# ============================================================================


@ntc_ref(article="4.3.4.3.1.1", formula="4.3.7", latex=r"\eta_{\min} = \max\!\left(1 - \frac{355}{f_{yk}}\left(1{,}0 - 0{,}04\,L_c\right),\;0{,}4\right)")
def composite_minimum_connection_degree(
    f_yk: float, L_c: float, *, stud_type: str = "standard"
) -> float:
    """Grado minimo di connessione eta_min [-].

    NTC18 §4.3.4.3.1.1 [4.3.7] per pioli standard, [4.3.8] per alternativi.

    Parameters
    ----------
    f_yk : float
        Resistenza caratteristica a snervamento dell'acciaio [N/mm²].
    L_c : float
        Distanza tra punti di momento nullo [m].
    stud_type : str
        ``"standard"`` (h>=76mm, d=19mm) o ``"alternative"`` (h>=4d, d=16-25mm).

    Returns
    -------
    float
        Grado minimo di connessione eta [-].
    """
    if L_c > 25:
        return 1.0

    ratio_355 = 355.0 / f_yk

    if stud_type == "standard":
        # [4.3.7]
        eta = 1 - ratio_355 * (1.0 - 0.04 * L_c)
    elif stud_type == "alternative":
        # [4.3.8]
        eta = 1 - ratio_355 * (0.75 - 0.03 * L_c)
    else:
        raise ValueError(f"Tipo piolo non valido: {stud_type!r}")

    return max(eta, 0.4)


# ============================================================================
# COLONNE — Resistenza plastica
# ============================================================================


@ntc_ref(article="4.3.5.3.1", formula="4.3.21", latex=r"N_{pl,Rd} = \frac{A_a\,f_{yk}}{\gamma_A} + \alpha_{cc}\,\frac{A_c\,f_{ck}}{\gamma_C} + \frac{A_s\,f_{sk}}{\gamma_S}")
def composite_column_plastic_resistance(
    A_a: float,
    f_yk: float,
    gamma_A: float,
    A_c: float,
    f_ck: float,
    gamma_C: float,
    A_s: float,
    f_sk: float,
    gamma_S: float,
    *,
    filled: bool = False,
) -> float:
    """Resistenza plastica di progetto a sforzo normale [N].

    NTC18 §4.3.5.3.1 [4.3.21]. Per sezioni riempite (filled=True)
    il coefficiente 0.85 e' sostituito da 1.0.

    Parameters
    ----------
    A_a : float
        Area del profilo in acciaio [mm²].
    f_yk : float
        Resistenza caratteristica a snervamento acciaio [N/mm²].
    gamma_A : float
        Fattore parziale acciaio [-] (tipicamente 1.05).
    A_c : float
        Area della parte in calcestruzzo [mm²].
    f_ck : float
        Resistenza cilindrica caratteristica calcestruzzo [N/mm²].
    gamma_C : float
        Fattore parziale calcestruzzo [-] (tipicamente 1.5).
    A_s : float
        Area delle barre d'armatura [mm²].
    f_sk : float
        Resistenza caratteristica armatura [N/mm²].
    gamma_S : float
        Fattore parziale armatura [-] (tipicamente 1.15).
    filled : bool
        Se True, usa coefficiente 1.0 per il calcestruzzo (sezioni riempite).

    Returns
    -------
    float
        N_pl,Rd [N].
    """
    alpha_cc = 1.0 if filled else 0.85
    return A_a * f_yk / gamma_A + alpha_cc * A_c * f_ck / gamma_C + A_s * f_sk / gamma_S


# ============================================================================
# COLONNE — Resistenza parte calcestruzzo
# ============================================================================


@ntc_ref(article="4.3.5.3.1", formula="4.3.25", latex=r"N_{pm,Rd} = 0{,}85\,\frac{f_{ck}}{\gamma_C}\,A_c")
def composite_concrete_part_resistance(
    A_c: float, f_ck: float, gamma_C: float
) -> float:
    """Sforzo normale resistente di progetto della porzione in calcestruzzo [N].

    NTC18 §4.3.5.3.1 [4.3.25]: N_pm,Rd = 0.85 * f_ck/gamma_C * A_c.

    Parameters
    ----------
    A_c : float
        Area complessiva di calcestruzzo [mm²].
    f_ck : float
        Resistenza cilindrica caratteristica [N/mm²].
    gamma_C : float
        Fattore parziale [-].

    Returns
    -------
    float
        N_pm,Rd [N].
    """
    return 0.85 * f_ck / gamma_C * A_c


# ============================================================================
# COLONNE — Contributo meccanico dell'acciaio
# ============================================================================


@ntc_ref(article="4.3.5.2", formula="4.3.15", latex=r"\delta = \frac{A_a\,f_{yk}}{\gamma_A\,N_{pl,Rd}}, \quad 0{,}2 \le \delta \le 0{,}9")
def composite_steel_contribution_ratio(
    A_a: float, f_yk: float, gamma_A: float, N_pl_Rd: float
) -> float:
    """Contributo meccanico del profilato in acciaio delta [-].

    NTC18 §4.3.5.2 [4.3.15]: delta = A_a*f_yk / (gamma_A * N_pl,Rd).
    Deve risultare 0.2 <= delta <= 0.9.

    Parameters
    ----------
    A_a : float
        Area del profilo in acciaio [mm²].
    f_yk : float
        Resistenza caratteristica a snervamento [N/mm²].
    gamma_A : float
        Fattore parziale acciaio [-].
    N_pl_Rd : float
        Resistenza plastica di progetto della sezione composta [N].

    Returns
    -------
    float
        Contributo delta [-].
    """
    delta = A_a * f_yk / (gamma_A * N_pl_Rd)
    if delta < 0.2 - 1e-9:
        raise ValueError(
            f"delta = {delta:.4f} < 0.2: contributo acciaio insufficiente"
        )
    if delta > 0.9 + 1e-9:
        raise ValueError(
            f"delta = {delta:.4f} > 0.9: contributo acciaio eccessivo"
        )
    return delta


# ============================================================================
# COLONNE — Rigidezza flessionale efficace
# ============================================================================


@ntc_ref(article="4.3.5.2", formula="4.3.16", latex=r"(EI)_{\mathrm{eff}} = E_a I_a + E_s I_s + 0{,}6\,E_{c,\mathrm{eff}}\,I_c, \quad E_{c,\mathrm{eff}} = \frac{E_{cm}}{1 + \varphi_t\,N_{G,Ed}/N_{Ed}}")
def composite_column_effective_stiffness(
    E_a: float,
    I_a: float,
    E_s: float,
    I_s: float,
    E_cm: float,
    I_c: float,
    phi_t: float,
    N_G_Ed: float,
    N_Ed: float,
) -> float:
    """Rigidezza flessionale efficace della sezione composta [N·mm²].

    NTC18 §4.3.5.2 [4.3.16]/[4.3.17].
    (EI)_eff = E_a*I_a + E_s*I_s + 0.6*E_c,eff*I_c
    con E_c,eff = E_cm / (1 + phi_t * N_G,Ed / N_Ed).

    Parameters
    ----------
    E_a : float
        Modulo elastico acciaio strutturale [N/mm²].
    I_a : float
        Momento d'inerzia acciaio strutturale [mm⁴].
    E_s : float
        Modulo elastico armatura [N/mm²].
    I_s : float
        Momento d'inerzia armatura [mm⁴].
    E_cm : float
        Modulo elastico istantaneo calcestruzzo [N/mm²].
    I_c : float
        Momento d'inerzia calcestruzzo [mm⁴].
    phi_t : float
        Coefficiente di viscosita' [-].
    N_G_Ed : float
        Aliquota di azione assiale da carichi permanenti [N].
    N_Ed : float
        Azione assiale totale di progetto [N].

    Returns
    -------
    float
        (EI)_eff [N·mm²].
    """
    if N_Ed == 0 or phi_t == 0:
        E_c_eff = E_cm
    else:
        E_c_eff = E_cm / (1 + phi_t * N_G_Ed / N_Ed)
    k_a = 0.6
    return E_a * I_a + E_s * I_s + k_a * E_c_eff * I_c


# ============================================================================
# COLONNE — Snellezza normalizzata
# ============================================================================


@ntc_ref(article="4.3.5.2", formula="4.3.18", latex=r"\bar{\lambda} = \sqrt{\frac{N_{pl,Rk}}{N_{cr}}}")
def composite_column_slenderness(N_pl_Rk: float, N_cr: float) -> float:
    """Snellezza normalizzata della colonna composta [-].

    NTC18 §4.3.5.2 [4.3.18]: lambda_bar = sqrt(N_pl,Rk / N_cr).
    Deve risultare lambda_bar < 2.0.

    Parameters
    ----------
    N_pl_Rk : float
        Resistenza a compressione caratteristica [N].
    N_cr : float
        Carico critico euleriano [N].

    Returns
    -------
    float
        Snellezza normalizzata lambda_bar [-].
    """
    lam = math.sqrt(N_pl_Rk / N_cr)
    if lam >= 2.0:
        raise ValueError(
            f"lambda_bar = {lam:.3f} >= 2.0: fuori dominio normativo"
        )
    return lam


# ============================================================================
# COLONNE — Curva di instabilita'
# ============================================================================

# Tab.4.3.III
_BUCKLING_CURVES: dict[str, dict[str, tuple[str, float]]] = {
    "fully_encased": {
        "y-y": ("b", 0.34),
        "z-z": ("c", 0.49),
    },
    "partially_encased": {
        "y-y": ("b", 0.34),
        "z-z": ("c", 0.49),
    },
}


@ntc_ref(article="4.3.5.4.1", table="Tab.4.3.III", latex=r"\text{Tab.\,4.3.III}")
def composite_column_buckling_curve(
    section_type: str, axis: str, rho_s: float = 0.0
) -> tuple[str, float]:
    """Curva di instabilita' e fattore di imperfezione alpha [-].

    NTC18 §4.3.5.4.1 Tab.4.3.III.

    Parameters
    ----------
    section_type : str
        ``"fully_encased"``, ``"partially_encased"`` o ``"filled"``.
    axis : str
        Asse di inflessione: ``"y-y"`` o ``"z-z"``
        (per sezioni riempite, usare ``"any"``).
    rho_s : float
        Rapporto armatura/calcestruzzo p_s = A_s/A_c [-]
        (solo per sezioni ``"filled"``).

    Returns
    -------
    tuple[str, float]
        (nome curva, fattore di imperfezione alpha).
    """
    if section_type in ("fully_encased", "partially_encased"):
        if axis not in ("y-y", "z-z"):
            raise ValueError(f"Asse non valido per {section_type}: {axis!r}")
        return _BUCKLING_CURVES[section_type][axis]

    if section_type == "filled":
        if rho_s < 0.03:
            return ("a", 0.21)
        elif rho_s < 0.06:
            return ("b", 0.34)
        else:
            return ("c", 0.49)

    raise ValueError(f"Tipo di sezione non valido: {section_type!r}")


# ============================================================================
# COLONNE — Resistenza all'instabilita'
# ============================================================================


@ntc_ref(article="4.3.5.4.1", formula="4.3.29", latex=r"\chi = \frac{1}{\Phi + \sqrt{\Phi^2 - \bar{\lambda}^2}} \le 1{,}0, \quad N_{b,Rd} = \chi\,N_{pl,Rd}")
def composite_column_buckling_resistance(
    lambda_bar: float, alpha: float, N_pl_Rd: float
) -> tuple[float, float]:
    """Resistenza di progetto all'instabilita' della colonna composta.

    NTC18 §4.3.5.4.1 [4.3.29]/[4.3.30]:
    chi = 1 / (Phi + sqrt(Phi^2 - lambda_bar^2)) <= 1.0
    N_b,Rd = chi * N_pl,Rd

    Parameters
    ----------
    lambda_bar : float
        Snellezza normalizzata [-].
    alpha : float
        Fattore di imperfezione [-].
    N_pl_Rd : float
        Resistenza plastica di progetto [N].

    Returns
    -------
    tuple[float, float]
        (chi, N_b_Rd) dove chi [-] e N_b_Rd [N].
    """
    phi = 0.5 * (1 + alpha * (lambda_bar - 0.2) + lambda_bar**2)
    chi = 1 / (phi + math.sqrt(phi**2 - lambda_bar**2))
    chi = min(chi, 1.0)
    return chi, chi * N_pl_Rd


# ============================================================================
# COLONNE — Coefficienti di confinamento (sezioni circolari)
# ============================================================================


@ntc_ref(article="4.3.5.3.1", formula="4.3.23", latex=r"\eta_a = 0{,}25\,(3 + 2\,\bar{\lambda}), \quad \eta_c = 4{,}9 - 18{,}5\,\bar{\lambda} + 17\,\bar{\lambda}^2")
def composite_confinement_coefficients(
    lambda_bar: float, e_d: float
) -> tuple[float, float]:
    """Coefficienti di confinamento eta_a ed eta_c per sezioni circolari [-].

    NTC18 §4.3.5.3.1 [4.3.23]/[4.3.24].
    Validi per lambda_bar <= 0.5 e e/d <= 0.1 (eta_c > 0).

    Parameters
    ----------
    lambda_bar : float
        Snellezza normalizzata [-] (deve essere <= 0.5).
    e_d : float
        Eccentricita' relativa e/d [-].

    Returns
    -------
    tuple[float, float]
        (eta_a, eta_c).
    """
    if lambda_bar > 0.5 + 1e-9:
        raise ValueError(
            f"lambda_bar = {lambda_bar:.3f} > 0.5: confinamento non applicabile"
        )

    if e_d > 0.1:
        return 1.0, 0.0

    # Valore base per e=0
    eta_a_0 = min(0.25 * (3 + 2 * lambda_bar), 1.0)
    eta_c_0 = max(4.9 - 18.5 * lambda_bar + 17 * lambda_bar**2, 0.0)

    if e_d == 0:
        return eta_a_0, eta_c_0

    # Interpolazione per 0 < e/d <= 0.1
    eta_a = eta_a_0 + 10 * (0.25 - 0.5 * lambda_bar) * e_d
    eta_c = eta_c_0 * (1 - 10 * e_d)
    return eta_a, max(eta_c, 0.0)


# ============================================================================
# COLONNE — Instabilita' locale
# ============================================================================


@ntc_ref(article="4.3.5.4.2", formula="4.3.31", latex=r"\frac{d}{t} \le 90\,\frac{235}{f_y} \;\text{(circ.)}, \quad \frac{d}{t} \le 52\sqrt{\frac{235}{f_y}} \;\text{(rett.)}")
def composite_column_local_buckling_check(
    section_type: str, d_or_b: float, t: float, f_y: float
) -> tuple[bool, float]:
    """Verifica di instabilita' locale per colonne composte.

    NTC18 §4.3.5.4.2 [4.3.31]-[4.3.33].

    Parameters
    ----------
    section_type : str
        ``"circular"`` (cave riempite), ``"rectangular"`` (cave riempite)
        o ``"partially_encased"`` (parzialmente rivestite).
    d_or_b : float
        Diametro d (circular/rectangular) o larghezza b (partially_encased) [mm].
    t : float
        Spessore [mm].
    f_y : float
        Resistenza a snervamento [N/mm²].

    Returns
    -------
    tuple[bool, float]
        (verifica_ok, rapporto d/t / limite).
    """
    ratio = d_or_b / t

    if section_type == "circular":
        # [4.3.31]: d/t <= 90 * (235/f_y)
        limit = 90 * (235 / f_y)
    elif section_type == "rectangular":
        # [4.3.32]: d/t <= 52 * sqrt(235/f_y)
        limit = 52 * math.sqrt(235 / f_y)
    elif section_type == "partially_encased":
        # [4.3.33]: b/t <= 44 * sqrt(235/f_y)
        limit = 44 * math.sqrt(235 / f_y)
    else:
        raise ValueError(f"Tipo sezione non valido: {section_type!r}")

    return ratio <= limit, ratio / limit


# ============================================================================
# COLONNE — Verifica a pressoflessione
# ============================================================================


@ntc_ref(article="4.3.5.4.3", formula="4.3.35", latex=r"M_{Ed} \le \alpha_M\,\mu_d\,M_{pl,Rd}")
def composite_column_bending_check(
    M_Ed: float, mu_d: float, M_pl_Rd: float, alpha_M: float
) -> tuple[bool, float]:
    """Verifica a pressoflessione della colonna composta.

    NTC18 §4.3.5.4.3 [4.3.35]: M_Ed <= alpha_M * mu_d * M_pl,Rd.

    Parameters
    ----------
    M_Ed : float
        Momento flettente di progetto [N·mm].
    mu_d : float
        Coefficiente da dominio di interazione N-M [-].
    M_pl_Rd : float
        Momento resistente plastico di progetto [N·mm].
    alpha_M : float
        Coefficiente: 0.9 per S235-S355, 0.8 per S420-S460 [-].

    Returns
    -------
    tuple[bool, float]
        (verifica_ok, rapporto M_Ed / (alpha_M * mu_d * M_pl,Rd)).
    """
    M_Rd = alpha_M * mu_d * M_pl_Rd
    ratio = M_Ed / M_Rd
    return ratio <= 1.0, ratio


# ============================================================================
# COLONNE — Amplificazione del momento (II ordine)
# ============================================================================


@ntc_ref(article="4.3.5.4.3", formula="4.3.36", latex=r"k = \frac{\beta}{1 - N_{Ed}/N_{cr,\mathrm{eff}}} \ge 1{,}0")
def composite_moment_amplification(
    N_Ed: float,
    N_cr_eff: float,
    *,
    M_min: float | None = None,
    M_max: float | None = None,
) -> float:
    """Coefficiente amplificativo del momento per effetti del II ordine [-].

    NTC18 §4.3.5.4.3 [4.3.36]/[4.3.37]:
    k = beta / (1 - N_Ed/N_cr) >= 1.0

    Parameters
    ----------
    N_Ed : float
        Azione assiale di progetto [N].
    N_cr_eff : float
        Carico critico euleriano efficace [N].
    M_min : float, optional
        Momento minimo alle estremita' [N·mm]. Se fornito con M_max,
        si usa beta = 0.66 + 0.44*(M_min/M_max) (distribuzione lineare).
    M_max : float, optional
        Momento massimo alle estremita' [N·mm].

    Returns
    -------
    float
        Coefficiente amplificativo k [-] (>= 1.0).

    Notes
    -----
    Se M_min e M_max non sono forniti, beta = 1.0
    (momento parabolico o triangolare con valori nulli alle estremita').
    Se M_min == M_max (momento costante), beta = 1.1.
    """
    if M_min is not None and M_max is not None:
        beta = max(0.66 + 0.44 * M_min / M_max, 0.44)
    else:
        beta = 1.0

    k = beta / (1 - N_Ed / N_cr_eff)
    return max(k, 1.0)


# ============================================================================
# COLONNE — Verifica a pressoflessione deviata
# ============================================================================


@ntc_ref(article="4.3.5.3.1", formula="4.3.27", latex=r"\frac{M_{y,Ed}}{\mu_{dy}\,M_{pl,y,Rd}} + \frac{M_{z,Ed}}{\mu_{dz}\,M_{pl,z,Rd}} \le 1{,}0")
def composite_column_biaxial_check(
    M_y_Ed: float,
    M_z_Ed: float,
    mu_dy: float,
    mu_dz: float,
    M_pl_y_Rd: float,
    M_pl_z_Rd: float,
    alpha_M_y: float,
    alpha_M_z: float,
) -> tuple[bool, float]:
    """Verifica a pressoflessione deviata della colonna composta.

    NTC18 §4.3.5.3.1 [4.3.27]:
    - M_y,Ed / (mu_dy * M_pl,y,Rd) <= alpha_M,y
    - M_z,Ed / (mu_dz * M_pl,z,Rd) <= alpha_M,z
    - r_y + r_z <= 1.0

    Parameters
    ----------
    M_y_Ed : float
        Momento di progetto asse y [N·mm].
    M_z_Ed : float
        Momento di progetto asse z [N·mm].
    mu_dy : float
        Coefficiente interazione asse y [-].
    mu_dz : float
        Coefficiente interazione asse z [-].
    M_pl_y_Rd : float
        Momento resistente plastico asse y [N·mm].
    M_pl_z_Rd : float
        Momento resistente plastico asse z [N·mm].
    alpha_M_y : float
        Coefficiente alpha_M asse y [-].
    alpha_M_z : float
        Coefficiente alpha_M asse z [-].

    Returns
    -------
    tuple[bool, float]
        (verifica_ok, max(r_y/alpha_M_y, r_z/alpha_M_z, r_y+r_z)).
    """
    r_y = M_y_Ed / (mu_dy * M_pl_y_Rd)
    r_z = M_z_Ed / (mu_dz * M_pl_z_Rd)

    check_y = r_y <= alpha_M_y
    check_z = r_z <= alpha_M_z
    check_sum = (r_y + r_z) <= 1.0

    passes = check_y and check_z and check_sum
    max_ratio = max(r_y / alpha_M_y, r_z / alpha_M_z, r_y + r_z)
    return passes, max_ratio


# ============================================================================
# TRAVI — Distribuzione del taglio
# ============================================================================


@ntc_ref(article="4.3.5.3.2", formula="4.3.28", latex=r"V_{a,Ed} = V_{Ed}\,\frac{M_{pl,a,Rd}}{M_{pl,Rd}}")
def composite_beam_shear_distribution(
    V_Ed: float, M_pl_a_Rd: float, M_pl_Rd: float
) -> tuple[float, float]:
    """Distribuzione del taglio tra parte in acciaio e calcestruzzo.

    NTC18 §4.3.5.3.2 [4.3.28]: V_a,Ed = V_Ed * M_pl,a,Rd / M_pl,Rd.

    Parameters
    ----------
    V_Ed : float
        Taglio totale di progetto [N].
    M_pl_a_Rd : float
        Momento resistente plastico della sola sezione in acciaio [N·mm].
    M_pl_Rd : float
        Momento resistente plastico della sezione composta [N·mm].

    Returns
    -------
    tuple[float, float]
        (V_a_Ed, V_c_Ed) [N].
    """
    V_a = V_Ed * M_pl_a_Rd / M_pl_Rd
    V_c = V_Ed - V_a
    return V_a, V_c


# ============================================================================
# COLONNE — Resistenza caratteristica (N_pl,Rk)
# ============================================================================


@ntc_ref(article="4.3.5.2", formula="4.3.19", latex=r"N_{pl,Rk} = A_a\,f_{yk} + 0{,}85\,A_c\,f_{ck} + A_s\,f_{sk}")
def composite_column_plastic_resistance_characteristic(
    A_a: float,
    f_yk: float,
    A_c: float,
    f_ck: float,
    A_s: float,
    f_sk: float,
    *,
    filled: bool = False,
) -> float:
    """Resistenza plastica caratteristica a sforzo normale N_pl,Rk [N].

    NTC18 §4.3.5.2 [4.3.19]: usata per il calcolo della snellezza normalizzata.
    Differisce da N_pl,Rd perche' non divide per i fattori parziali.

    Parameters
    ----------
    A_a : float
        Area del profilo in acciaio strutturale [mm²].
    f_yk : float
        Resistenza caratteristica a snervamento acciaio [N/mm²].
    A_c : float
        Area della parte in calcestruzzo [mm²].
    f_ck : float
        Resistenza cilindrica caratteristica calcestruzzo [N/mm²].
    A_s : float
        Area delle barre d'armatura [mm²].
    f_sk : float
        Resistenza caratteristica armatura [N/mm²].
    filled : bool
        Se True, usa coefficiente 1.0 per il calcestruzzo (sezioni riempite).

    Returns
    -------
    float
        N_pl,Rk [N].
    """
    alpha_cc = 1.0 if filled else 0.85
    return A_a * f_yk + alpha_cc * A_c * f_ck + A_s * f_sk


# ============================================================================
# COLONNE — Rigidezza flessionale efficace per analisi del II ordine
# ============================================================================


@ntc_ref(article="4.3.5.2", formula="4.3.20", latex=r"(EI)_{\mathrm{eff,II}} = k_0\!\left(E_a I_a + E_s I_s + k_{c,II}\,E_{cm}\,I_c\right)")
def composite_column_effective_stiffness_ii(
    E_a: float,
    I_a: float,
    E_s: float,
    I_s: float,
    E_cm: float,
    I_c: float,
    *,
    k_0: float = 0.9,
    k_c_ii: float = 0.5,
) -> float:
    """Rigidezza flessionale efficace di II ordine per colonne composte [N·mm²].

    NTC18 §4.3.5.2 [4.3.20]:
    (EI)_eff,II = k_0 * (E_a*I_a + E_s*I_s + k_c,II * E_cm * I_c)

    Utilizzata per la verifica del carico critico N_cr nel metodo semplificato.

    Parameters
    ----------
    E_a : float
        Modulo elastico acciaio strutturale [N/mm²].
    I_a : float
        Momento d'inerzia acciaio strutturale [mm⁴].
    E_s : float
        Modulo elastico armatura [N/mm²].
    I_s : float
        Momento d'inerzia armatura [mm⁴].
    E_cm : float
        Modulo elastico istantaneo calcestruzzo [N/mm²].
    I_c : float
        Momento d'inerzia calcestruzzo [mm⁴].
    k_0 : float
        Coefficiente calibrazione (default 0.9 per NTC18).
    k_c_ii : float
        Coefficiente riduttivo per il calcestruzzo (default 0.5 per NTC18).

    Returns
    -------
    float
        (EI)_eff,II [N·mm²].
    """
    return k_0 * (E_a * I_a + E_s * I_s + k_c_ii * E_cm * I_c)


# ============================================================================
# COLONNE — Resistenza plastica con confinamento (sezioni circolari riempite)
# ============================================================================


@ntc_ref(article="4.3.5.3.1", formula="4.3.22", latex=r"N_{pl,Rd} = \eta_a\,\frac{A_a\,f_{yk}}{\gamma_A} + \frac{A_c\,f_{ck}}{\gamma_C}\!\left(1 + \eta_c\,\frac{t}{d}\,\frac{f_{yk}}{f_{ck}}\right) + \frac{A_s\,f_{sk}}{\gamma_S}")
def composite_column_confinement_resistance(
    A_a: float,
    f_yk: float,
    gamma_A: float,
    A_c: float,
    f_ck: float,
    gamma_C: float,
    A_s: float,
    f_sk: float,
    gamma_S: float,
    t: float,
    d: float,
    eta_a: float,
    eta_c: float,
) -> float:
    """Resistenza plastica di progetto con effetto di confinamento [N].

    NTC18 §4.3.5.3.1 [4.3.22] — per colonne circolari cave riempite.
    Tiene conto del confinamento del calcestruzzo da parte del tubo in acciaio.

    Parameters
    ----------
    A_a : float
        Area del profilo in acciaio (tubo circolare) [mm²].
    f_yk : float
        Resistenza caratteristica a snervamento acciaio [N/mm²].
    gamma_A : float
        Fattore parziale acciaio [-].
    A_c : float
        Area della parte in calcestruzzo [mm²].
    f_ck : float
        Resistenza cilindrica caratteristica calcestruzzo [N/mm²].
    gamma_C : float
        Fattore parziale calcestruzzo [-].
    A_s : float
        Area delle barre d'armatura [mm²].
    f_sk : float
        Resistenza caratteristica armatura [N/mm²].
    gamma_S : float
        Fattore parziale armatura [-].
    t : float
        Spessore della parete del tubo [mm].
    d : float
        Diametro esterno del tubo [mm].
    eta_a : float
        Coefficiente di confinamento per acciaio [-] (da [4.3.23]).
    eta_c : float
        Coefficiente di confinamento per calcestruzzo [-] (da [4.3.24]).

    Returns
    -------
    float
        N_pl,Rd con confinamento [N].
    """
    N_steel = eta_a * A_a * f_yk / gamma_A
    N_concrete = (A_c * f_ck / gamma_C) * (1 + eta_c * (t / d) * (f_yk / f_ck))
    N_rebar = A_s * f_sk / gamma_S
    return N_steel + N_concrete + N_rebar


# ============================================================================
# COLONNE — Momento resistente ridotto da interazione N-M
# ============================================================================


@ntc_ref(article="4.3.5.3.1", formula="4.3.26", latex=r"M_{pl,Rd}(N_{Ed}) = \mu_d\,M_{pl,Rd}")
def composite_column_reduced_moment_resistance(
    mu_d: float, M_pl_Rd: float
) -> float:
    """Momento resistente di progetto ridotto per effetto dello sforzo normale [N·mm].

    NTC18 §4.3.5.3.1 [4.3.26]:
    M_pl,Rd(N_Ed) = mu_d * M_pl,Rd

    Il coefficiente mu_d e' ottenuto dal dominio di interazione N-M
    in corrispondenza del valore di N_Ed agente.

    Parameters
    ----------
    mu_d : float
        Coefficiente dal dominio di interazione N-M [-] (0 <= mu_d <= 1.0).
    M_pl_Rd : float
        Momento resistente plastico puro della sezione composta [N·mm].

    Returns
    -------
    float
        Momento resistente ridotto M_pl,Rd(N_Ed) [N·mm].
    """
    if mu_d < 0 or mu_d > 1.0 + 1e-9:
        raise ValueError(f"mu_d = {mu_d:.4f}: deve essere compreso tra 0 e 1")
    return mu_d * M_pl_Rd


# ============================================================================
# TRAVI — Larghezza efficace di dispersione per carichi concentrati
# ============================================================================


@ntc_ref(article="4.3.6.1.1", formula="4.3.38", latex=r"b_m = b_p + 2\,(h_c + h_t)")
def composite_load_dispersion_width(
    b_p: float, h_c: float, h_t: float
) -> float:
    """Larghezza efficace di dispersione per carichi concentrati o lineari [mm].

    NTC18 §4.3.6.1.1 [4.3.38]:
    b_m = b_p + 2*(h_c + h_t)

    Larghezza su cui ripartire il carico concentrato/lineare agente sulla
    soletta composita (es. carico da ruota).

    Parameters
    ----------
    b_p : float
        Larghezza della zona di applicazione del carico (contatto) [mm].
    h_c : float
        Altezza dello strato di calcestruzzo sopra la lamiera [mm].
    h_t : float
        Spessore del rivestimento impermeabile/pavimento sovrapposto [mm].

    Returns
    -------
    float
        Larghezza di dispersione b_m [mm].
    """
    return b_p + 2 * (h_c + h_t)


# ============================================================================
# COLONNE — Tensione tangenziale limite di aderenza
# ============================================================================

_BOND_STRESS_LIMITS: dict[str, float] = {
    "fully_encased": 0.30,
    "filled_circular": 0.55,
    "filled_rectangular": 0.40,
    "partially_encased_flange": 0.20,
    "partially_encased_web": 0.0,
}


@ntc_ref(article="4.3.5.5.1", latex=r"\tau_{Rd} \;\text{(§4.3.5.5.1)}")
def composite_bond_stress_limit(section_type: str) -> float:
    """Tensione tangenziale limite di aderenza all'interfaccia [N/mm²].

    NTC18 §4.3.5.5.1.

    Parameters
    ----------
    section_type : str
        ``"fully_encased"``, ``"filled_circular"``, ``"filled_rectangular"``,
        ``"partially_encased_flange"`` o ``"partially_encased_web"``.

    Returns
    -------
    float
        Tensione tangenziale limite tau_Rd [N/mm²] (= MPa).
    """
    if section_type not in _BOND_STRESS_LIMITS:
        raise ValueError(f"Tipo sezione non valido: {section_type!r}")
    return _BOND_STRESS_LIMITS[section_type]
