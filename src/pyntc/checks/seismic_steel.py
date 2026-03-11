"""Verifiche acciaio in zona sismica — NTC18 §7.5.

Strutture a telaio (MRF), controventi concentrici (CBF),
controventi eccentrici (EBF), limitazioni di duttilita' locale.

Unita':
- Resistenze: [N/mm^2]
- Forze/momenti: [N], [N·mm]
- Lunghezze: [mm]
- Coefficienti: [-]
"""

from __future__ import annotations
import math
from pyntc.core.reference import ntc_ref


# ══════════════════════════════════════════════════════════════════════════════
# §7.5.3.1 — VERIFICHE DI RESISTENZA (RES) — REGOLE GENERALI
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(
    article="7.5.3.1",
    formula="7.5.1",
    latex=r"R_{j,d} \ge 1{,}1 \cdot \gamma_{ov} \cdot R_{p,LRd}",
)
def seismic_steel_connection_resistance(
    R_j_d: float,
    gamma_ov: float,
    R_p_LRd: float,
) -> tuple[bool, float]:
    """Verifica capacita' di collegamento in zona dissipativa (RES) [N o N·mm].

    NTC18 §7.5.3.1, Formula [7.5.1]:
        R_j,d >= 1.1 * gamma_ov * R_p,LRd  =>  R_U,Rd

    I collegamenti in zone dissipative devono consentire la plasticizzazione
    delle parti dissipative collegate.

    Parameters
    ----------
    R_j_d : float
        Capacita' di progetto del collegamento [N o N·mm].
    gamma_ov : float
        Coefficiente di sovraresistenza del materiale (§7.5.1) [-].
    R_p_LRd : float
        Capacita' al limite plastico della membratura dissipativa [N o N·mm].

    Returns
    -------
    tuple[bool, float]
        - satisfied: True se R_j,d >= R_U,Rd
        - ratio: R_j,d / R_U,Rd [-]
    """
    if R_j_d <= 0:
        raise ValueError("R_j_d deve essere > 0")
    if gamma_ov <= 0:
        raise ValueError("gamma_ov deve essere > 0")
    if R_p_LRd <= 0:
        raise ValueError("R_p_LRd deve essere > 0")

    R_U_Rd = 1.1 * gamma_ov * R_p_LRd
    ratio = R_j_d / R_U_Rd
    return ratio >= 1.0, ratio


@ntc_ref(
    article="7.5.3.1",
    formula="7.5.2",
    latex=r"\frac{A_{res}}{A} \ge 1{,}1 \cdot \frac{\gamma_{M2}}{\gamma_{M0}}",
)
def seismic_steel_net_section_check(
    A_res: float,
    A: float,
    gamma_M0: float,
    gamma_M2: float,
) -> tuple[bool, float]:
    """Verifica sezione netta per membrature tese con collegamenti bullonati [-].

    NTC18 §7.5.3.1, Formula [7.5.2]:
        A_res / A >= 1.1 * gamma_M2 / gamma_M0

    Garantisce che la plasticizzazione avvenga nella sezione lorda prima della
    rottura sulla sezione netta.

    Parameters
    ----------
    A_res : float
        Area resistente (area netta piu' eventuale rinforzo) [mm^2].
    A : float
        Area lorda della sezione [mm^2].
    gamma_M0 : float
        Coefficiente parziale gamma_M0 [-].
    gamma_M2 : float
        Coefficiente parziale gamma_M2 [-].

    Returns
    -------
    tuple[bool, float]
        - satisfied: True se il rapporto e' soddisfatto
        - ratio: (A_res / A) / (1.1 * gamma_M2 / gamma_M0) [-]
    """
    if A_res <= 0:
        raise ValueError("A_res deve essere > 0")
    if A <= 0:
        raise ValueError("A deve essere > 0")
    if A_res > A:
        raise ValueError("A_res non puo' essere maggiore di A")
    if gamma_M0 <= 0:
        raise ValueError("gamma_M0 deve essere > 0")
    if gamma_M2 <= 0:
        raise ValueError("gamma_M2 deve essere > 0")

    lhs = A_res / A
    rhs = 1.1 * gamma_M2 / gamma_M0
    ratio = lhs / rhs
    return lhs >= rhs, ratio


# ══════════════════════════════════════════════════════════════════════════════
# §7.5.3.2 — VERIFICHE DI DUTTILITA' (DUT) — REGOLE GENERALI
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(
    article="7.5.3.2",
    formula="7.5.3",
    latex=r"N_{Ed} / N_{p,LRd} \le 0{,}3",
)
def seismic_steel_column_axial_ductility(
    N_Ed: float,
    N_p_LRd: float,
) -> tuple[bool, float]:
    """Verifica di duttilita' per colonne primarie di strutture a telaio [-].

    NTC18 §7.5.3.2, Formula [7.5.3]:
        N_Ed / N_p,LRd <= 0.3

    Verifica che lo sforzo normale nella colonna non pregiudichi la
    duttilita' locale nelle zone dissipative.

    Parameters
    ----------
    N_Ed : float
        Domanda a sforzo normale [N].
    N_p_LRd : float
        Capacita' a sforzo normale della sezione (§4.2.4.1.2) [N].

    Returns
    -------
    tuple[bool, float]
        - satisfied: True se il rapporto <= 0.3
        - ratio: N_Ed / N_p,LRd [-]
    """
    if N_Ed < 0:
        raise ValueError("N_Ed deve essere >= 0")
    if N_p_LRd <= 0:
        raise ValueError("N_p_LRd deve essere > 0")

    ratio = N_Ed / N_p_LRd
    return ratio <= 0.3, ratio


@ntc_ref(
    article="7.5.3.2",
    table="Tab.7.5.1",
    latex=r"\text{Tab.\,7.5.1 — Classe sezione dissipativa}",
)
def seismic_steel_section_class_check(
    section_class: int,
    q_0: float,
    ductility_class: str,
) -> tuple[bool, str]:
    """Verifica classe di sezione trasversale per elementi dissipativi (DUT).

    NTC18 §7.5.3.2, Tab. 7.5.1:
        CD"B" con 2 < q_0 <= 4: classe 1 o 2
        CD"A" con q_0 > 4: solo classe 1

    Parameters
    ----------
    section_class : int
        Classe della sezione trasversale dell'elemento dissipativo (1, 2, 3 o 4).
    q_0 : float
        Valore di base del fattore di comportamento [-].
    ductility_class : str
        Classe di duttilita': "A" (CD"A") o "B" (CD"B").

    Returns
    -------
    tuple[bool, str]
        - satisfied: True se la classe e' ammessa
        - required: descrizione della classe richiesta ("1", "1 o 2", "nessuna")
    """
    if section_class not in (1, 2, 3, 4):
        raise ValueError("section_class deve essere 1, 2, 3 o 4")
    if q_0 <= 0:
        raise ValueError("q_0 deve essere > 0")
    dc = ductility_class.upper()
    if dc not in ("A", "B"):
        raise ValueError("ductility_class deve essere 'A' o 'B'")

    # Dalla Tab. 7.5.1
    if dc == "A" and q_0 > 4:
        required = "1"
        satisfied = section_class == 1
    elif dc == "B" and 2 < q_0 <= 4:
        required = "1 o 2"
        satisfied = section_class in (1, 2)
    else:
        # q_0 <= 2: nessuna prescrizione specifica dalla Tab. 7.5.1
        required = "nessuna"
        satisfied = True

    return satisfied, required


# ══════════════════════════════════════════════════════════════════════════════
# §7.5.4 — STRUTTURE A TELAIO (MRF)
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(
    article="7.5.4.2",
    formula="7.5.7",
    latex=r"N_{Ed} = N_{Ed,G} + 1{,}1 \cdot \gamma_{ov} \cdot \Omega \cdot N_{Ed,E}",
)
def seismic_steel_mrf_column_demand_N(
    N_Ed_G: float,
    gamma_ov: float,
    Omega: float,
    N_Ed_E: float,
) -> float:
    """Domanda a sforzo normale amplificata per colonne MRF [N].

    NTC18 §7.5.4.2, Formula [7.5.7]:
        N_Ed = N_Ed,G + 1.1 * gamma_ov * Omega * N_Ed,E

    Parameters
    ----------
    N_Ed_G : float
        Domanda a sforzo normale per azioni non sismiche [N].
    gamma_ov : float
        Coefficiente di sovraresistenza del materiale (§7.5.1) [-].
    Omega : float
        Fattore di sovraresistenza minimo Omega_i = M_pLRd,i / M_Ed,E,i [-].
    N_Ed_E : float
        Domanda a sforzo normale per azione sismica [N].

    Returns
    -------
    float
        N_Ed: sforzo normale di progetto amplificato [N].
    """
    if gamma_ov <= 0:
        raise ValueError("gamma_ov deve essere > 0")
    if Omega <= 0:
        raise ValueError("Omega deve essere > 0")

    return N_Ed_G + 1.1 * gamma_ov * Omega * N_Ed_E


@ntc_ref(
    article="7.5.4.2",
    formula="7.5.8",
    latex=r"M_{Ed} = M_{Ed,G} + 1{,}1 \cdot \gamma_{ov} \cdot \Omega \cdot M_{Ed,E}",
)
def seismic_steel_mrf_column_demand_M(
    M_Ed_G: float,
    gamma_ov: float,
    Omega: float,
    M_Ed_E: float,
) -> float:
    """Domanda a flessione amplificata per colonne MRF [N·mm].

    NTC18 §7.5.4.2, Formula [7.5.8]:
        M_Ed = M_Ed,G + 1.1 * gamma_ov * Omega * M_Ed,E

    Parameters
    ----------
    M_Ed_G : float
        Domanda a flessione per azioni non sismiche [N·mm].
    gamma_ov : float
        Coefficiente di sovraresistenza del materiale (§7.5.1) [-].
    Omega : float
        Fattore di sovraresistenza minimo [-].
    M_Ed_E : float
        Domanda a flessione per azione sismica [N·mm].

    Returns
    -------
    float
        M_Ed: momento flettente di progetto amplificato [N·mm].
    """
    if gamma_ov <= 0:
        raise ValueError("gamma_ov deve essere > 0")
    if Omega <= 0:
        raise ValueError("Omega deve essere > 0")

    return M_Ed_G + 1.1 * gamma_ov * Omega * M_Ed_E


@ntc_ref(
    article="7.5.4.2",
    formula="7.5.9",
    latex=r"V_{Ed} = V_{Ed,G} + 1{,}1 \cdot \gamma_{ov} \cdot \Omega \cdot V_{Ed,E}",
)
def seismic_steel_mrf_column_demand_V(
    V_Ed_G: float,
    gamma_ov: float,
    Omega: float,
    V_Ed_E: float,
) -> float:
    """Domanda a taglio amplificata per colonne MRF [N].

    NTC18 §7.5.4.2, Formula [7.5.9]:
        V_Ed = V_Ed,G + 1.1 * gamma_ov * Omega * V_Ed,E

    Parameters
    ----------
    V_Ed_G : float
        Domanda a taglio per azioni non sismiche [N].
    gamma_ov : float
        Coefficiente di sovraresistenza del materiale (§7.5.1) [-].
    Omega : float
        Fattore di sovraresistenza minimo [-].
    V_Ed_E : float
        Domanda a taglio per azione sismica [N].

    Returns
    -------
    float
        V_Ed: taglio di progetto amplificato [N].
    """
    if gamma_ov <= 0:
        raise ValueError("gamma_ov deve essere > 0")
    if Omega <= 0:
        raise ValueError("Omega deve essere > 0")

    return V_Ed_G + 1.1 * gamma_ov * Omega * V_Ed_E


@ntc_ref(
    article="7.5.4.2",
    formula="7.5.11",
    latex=r"\sum M_{C,pl,Rd} \ge \gamma_{Rd} \cdot \sum M_{b,pl,Rd}",
)
def seismic_steel_mrf_beam_column_hierarchy(
    M_c_pl_Rd: list[float] | tuple[float, ...],
    M_b_pl_Rd: list[float] | tuple[float, ...],
    gamma_Rd: float,
) -> tuple[bool, float]:
    """Verifica gerarchia delle resistenze ai nodi trave-colonna (MRF) [-].

    NTC18 §7.5.4.2, Formula [7.5.11]:
        sum(M_C,pl,Rd) >= gamma_Rd * sum(M_b,pl,Rd)

    Assicura lo sviluppo del meccanismo globale dissipativo (strong column /
    weak beam).

    Parameters
    ----------
    M_c_pl_Rd : list[float]
        Capacita' a flessione plastica delle colonne convergenti nel nodo [N·mm].
    M_b_pl_Rd : list[float]
        Capacita' a flessione plastica delle travi convergenti nel nodo [N·mm].
    gamma_Rd : float
        Coefficiente di amplificazione (Tab. 7.2.1) [-].

    Returns
    -------
    tuple[bool, float]
        - satisfied: True se la verifica e' soddisfatta
        - ratio: sum(M_c) / (gamma_Rd * sum(M_b)) [-]
    """
    if gamma_Rd <= 0:
        raise ValueError("gamma_Rd deve essere > 0")
    if not M_c_pl_Rd:
        raise ValueError("M_c_pl_Rd non puo' essere vuoto")
    if not M_b_pl_Rd:
        raise ValueError("M_b_pl_Rd non puo' essere vuoto")

    sum_Mc = sum(M_c_pl_Rd)
    sum_Mb = sum(M_b_pl_Rd)
    demand = gamma_Rd * sum_Mb
    ratio = sum_Mc / demand
    return ratio >= 1.0, ratio


@ntc_ref(
    article="7.5.4.3",
    formula="7.5.12",
    latex=r"M_{J,Rd} \ge 1{,}1 \cdot \gamma_{ov} \cdot M_{b,pl,Rd}",
)
def seismic_steel_mrf_connection_moment(
    M_J_Rd: float,
    gamma_ov: float,
    M_b_pl_Rd: float,
) -> tuple[bool, float]:
    """Verifica capacita' a flessione del collegamento trave-colonna (MRF) [-].

    NTC18 §7.5.4.3, Formula [7.5.12]:
        M_J,Rd >= 1.1 * gamma_ov * M_b,pl,Rd

    Il collegamento deve essere in grado di trasferire la sovraresistenza
    della trave in condizioni sismiche.

    Parameters
    ----------
    M_J_Rd : float
        Capacita' a flessione del collegamento [N·mm].
    gamma_ov : float
        Coefficiente di sovraresistenza del materiale (§7.5.1) [-].
    M_b_pl_Rd : float
        Capacita' a flessione plastica della trave [N·mm].

    Returns
    -------
    tuple[bool, float]
        - satisfied: True se M_J,Rd >= 1.1 * gamma_ov * M_b,pl,Rd
        - ratio: M_J,Rd / (1.1 * gamma_ov * M_b,pl,Rd) [-]
    """
    if M_J_Rd <= 0:
        raise ValueError("M_J_Rd deve essere > 0")
    if gamma_ov <= 0:
        raise ValueError("gamma_ov deve essere > 0")
    if M_b_pl_Rd <= 0:
        raise ValueError("M_b_pl_Rd deve essere > 0")

    demand = 1.1 * gamma_ov * M_b_pl_Rd
    ratio = M_J_Rd / demand
    return ratio >= 1.0, ratio


# ══════════════════════════════════════════════════════════════════════════════
# §7.5.5 — STRUTTURE CON CONTROVENTI CONCENTRICI (CBF)
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(
    article="7.5.5",
    formula="7.5.15",
    latex=r"1{,}3 \le \bar{\lambda} \le 2{,}0 \text{ (CBF a X)}; \quad \bar{\lambda} \le 2{,}0 \text{ (CBF a V)}",
)
def seismic_steel_cbf_diagonal_slenderness(
    lambda_bar: float,
    brace_type: str,
) -> tuple[bool, str]:
    """Verifica snellezza adimensionale della diagonale di controvento (CBF).

    NTC18 §7.5.5:
        CBF a X:  1.3 <= lambda_bar <= 2.0
        CBF a V:  lambda_bar <= 2.0

    Valida per edifici con piu' di due piani.

    Parameters
    ----------
    lambda_bar : float
        Snellezza adimensionale della diagonale [-].
    brace_type : str
        Tipo di controvento: "X" (a croce di Sant'Andrea) o "V" (a V o a
        V rovesciata).

    Returns
    -------
    tuple[bool, str]
        - satisfied: True se la snellezza rispetta i limiti
        - message: descrizione dell'esito
    """
    if lambda_bar <= 0:
        raise ValueError("lambda_bar deve essere > 0")
    bt = brace_type.upper()
    if bt not in ("X", "V"):
        raise ValueError("brace_type deve essere 'X' o 'V'")

    if bt == "X":
        satisfied = 1.3 <= lambda_bar <= 2.0
        if satisfied:
            msg = f"OK: 1.3 <= {lambda_bar:.3f} <= 2.0"
        elif lambda_bar < 1.3:
            msg = f"NOK: {lambda_bar:.3f} < 1.3 (snellezza troppo bassa)"
        else:
            msg = f"NOK: {lambda_bar:.3f} > 2.0 (snellezza troppo alta)"
    else:  # V
        satisfied = lambda_bar <= 2.0
        if satisfied:
            msg = f"OK: {lambda_bar:.3f} <= 2.0"
        else:
            msg = f"NOK: {lambda_bar:.3f} > 2.0 (snellezza troppo alta)"

    return satisfied, msg


@ntc_ref(
    article="7.5.5",
    formula="7.5.7",
    latex=r"N_{Ed} = N_{Ed,G} + 1{,}1 \cdot \gamma_{ov} \cdot \Omega \cdot N_{Ed,E}",
)
def seismic_steel_cbf_member_demand(
    N_Ed_G: float,
    gamma_ov: float,
    Omega: float,
    N_Ed_E: float,
) -> float:
    """Domanda a sforzo normale amplificata per travi/colonne di CBF [N].

    NTC18 §7.5.5, applicazione delle formule [7.5.7]-[7.5.9] ai CBF:
        N_Ed = N_Ed,G + 1.1 * gamma_ov * Omega * N_Ed,E

    Omega e' il minimo valore tra Omega_i = N_p(RAD),i / N_Ed,i valutati
    per tutte le diagonali dissipative.

    Parameters
    ----------
    N_Ed_G : float
        Domanda a sforzo normale per azioni non sismiche [N].
    gamma_ov : float
        Coefficiente di sovraresistenza del materiale (§7.5.1) [-].
    Omega : float
        Minimo fattore Omega_i = N_p(RAD),i / N_Ed,i tra le diagonali [-].
    N_Ed_E : float
        Domanda a sforzo normale per azione sismica [N].

    Returns
    -------
    float
        N_Ed: sforzo normale di progetto amplificato per trave/colonna [N].
    """
    if gamma_ov <= 0:
        raise ValueError("gamma_ov deve essere > 0")
    if Omega <= 0:
        raise ValueError("Omega deve essere > 0")

    return N_Ed_G + 1.1 * gamma_ov * Omega * N_Ed_E


@ntc_ref(
    article="7.5.5",
    formula="7.5.15",
    latex=r"N_{Ed} / N_{hRdp}(M_{Ed}) \le 1",
)
def seismic_steel_cbf_column_buckling_check(
    N_Ed: float,
    N_hRdp: float,
) -> tuple[bool, float]:
    """Verifica instabilita' di travi e colonne in CBF (RES) [-].

    NTC18 §7.5.5, Formula [7.5.15]:
        N_Ed / N_hRdp(M_Ed) <= 1

    N_hRdp e' la capacita' all'instabilita' (§4.2.4.1.3.1) tenendo conto
    dell'interazione con il momento flettente M_Ed.

    Parameters
    ----------
    N_Ed : float
        Domanda a sforzo normale amplificata [N].
    N_hRdp : float
        Capacita' all'instabilita' della sezione con interazione con M_Ed [N].

    Returns
    -------
    tuple[bool, float]
        - satisfied: True se il rapporto <= 1.0
        - ratio: N_Ed / N_hRdp [-]
    """
    if N_Ed < 0:
        raise ValueError("N_Ed deve essere >= 0")
    if N_hRdp <= 0:
        raise ValueError("N_hRdp deve essere > 0")

    ratio = N_Ed / N_hRdp
    return ratio <= 1.0, ratio


@ntc_ref(
    article="7.5.5",
    formula="7.5.15",
    latex=r"\left| \Omega_{max} - \Omega_{min} \right| / \Omega_{min} \le 0{,}25",
)
def seismic_steel_cbf_omega_homogeneity(
    Omega_values: list[float] | tuple[float, ...],
) -> tuple[bool, float]:
    """Verifica omogeneita' dei coefficienti Omega delle diagonali CBF [-].

    NTC18 §7.5.5:
        (Omega_max - Omega_min) / Omega_min <= 0.25

    Garantisce un comportamento dissipativo omogeneo delle diagonali.

    Parameters
    ----------
    Omega_values : list[float]
        Valori Omega_i = N_p(RAD),i / N_Ed,i per le diagonali dissipative [-].

    Returns
    -------
    tuple[bool, float]
        - satisfied: True se la dispersione e' <= 25%
        - dispersion: (Omega_max - Omega_min) / Omega_min [-]
    """
    if not Omega_values:
        raise ValueError("Omega_values non puo' essere vuoto")
    if any(o <= 0 for o in Omega_values):
        raise ValueError("Tutti i valori Omega devono essere > 0")

    Omega_max = max(Omega_values)
    Omega_min = min(Omega_values)
    dispersion = (Omega_max - Omega_min) / Omega_min
    return dispersion <= 0.25, dispersion


# ══════════════════════════════════════════════════════════════════════════════
# §7.5.6 — STRUTTURE CON CONTROVENTI ECCENTRICI (EBF)
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(
    article="7.5.6",
    formula="7.5.17",
    latex=r"M_{I,Rd} = f_y \cdot b \cdot t_f \cdot (h - t_f)",
)
def seismic_steel_ebf_link_bending_resistance(
    f_y: float,
    b: float,
    t_f: float,
    h: float,
) -> float:
    """Capacita' a flessione dell'elemento di connessione EBF (sezione I) [N·mm].

    NTC18 §7.5.6, Formula [7.5.17]:
        M_I,Rd = f_y * b * t_f * (h - t_f)

    Valida in assenza di domanda a sforzo normale.

    Parameters
    ----------
    f_y : float
        Tensione di snervamento del materiale [N/mm^2].
    b : float
        Larghezza della flangia [mm].
    t_f : float
        Spessore della flangia [mm].
    h : float
        Altezza totale della sezione [mm].

    Returns
    -------
    float
        M_I,Rd: capacita' a flessione dell'elemento di connessione [N·mm].
    """
    if f_y <= 0:
        raise ValueError("f_y deve essere > 0")
    if b <= 0:
        raise ValueError("b deve essere > 0")
    if t_f <= 0:
        raise ValueError("t_f deve essere > 0")
    if h <= t_f:
        raise ValueError("h deve essere > t_f")

    return f_y * b * t_f * (h - t_f)


@ntc_ref(
    article="7.5.6",
    formula="7.5.18",
    latex=r"V_{I,Rd} = \frac{f_y}{\sqrt{3}} \cdot t_w \cdot (h - t_f)",
)
def seismic_steel_ebf_link_shear_resistance(
    f_y: float,
    t_w: float,
    h: float,
    t_f: float,
) -> float:
    """Capacita' a taglio dell'elemento di connessione EBF (sezione I) [N].

    NTC18 §7.5.6, Formula [7.5.18]:
        V_I,Rd = f_y / sqrt(3) * t_w * (h - t_f)

    Valida in assenza di domanda a sforzo normale.

    Parameters
    ----------
    f_y : float
        Tensione di snervamento del materiale [N/mm^2].
    t_w : float
        Spessore dell'anima [mm].
    h : float
        Altezza totale della sezione [mm].
    t_f : float
        Spessore della flangia [mm].

    Returns
    -------
    float
        V_I,Rd: capacita' a taglio dell'elemento di connessione [N].
    """
    if f_y <= 0:
        raise ValueError("f_y deve essere > 0")
    if t_w <= 0:
        raise ValueError("t_w deve essere > 0")
    if h <= t_f:
        raise ValueError("h deve essere > t_f")
    if t_f <= 0:
        raise ValueError("t_f deve essere > 0")

    return (f_y / math.sqrt(3.0)) * t_w * (h - t_f)


@ntc_ref(
    article="7.5.6",
    formula="7.5.21",
    latex=r"V_{I,Rd,r} = V_{I,Rd} \left[1 - \left(\frac{N_{Ed}}{N_{p,Rd}}\right)^2\right]^{0{,}5}",
)
def seismic_steel_ebf_link_shear_resistance_reduced(
    V_I_Rd: float,
    N_Ed: float,
    N_p_Rd: float,
) -> float:
    """Capacita' a taglio ridotta per sforzo normale del link EBF [N].

    NTC18 §7.5.6, Formula [7.5.21]:
        V_I,Rd,r = V_I,Rd * sqrt(1 - (N_Ed / N_p,Rd)^2)

    Da applicare quando N_Ed / N_p,Rd > 0.15.

    Parameters
    ----------
    V_I_Rd : float
        Capacita' a taglio del link in assenza di sforzo normale [N].
    N_Ed : float
        Domanda a sforzo normale nel link [N].
    N_p_Rd : float
        Capacita' a sforzo normale della sezione [N].

    Returns
    -------
    float
        V_I,Rd,r: capacita' a taglio ridotta [N].
    """
    if V_I_Rd <= 0:
        raise ValueError("V_I_Rd deve essere > 0")
    if N_Ed < 0:
        raise ValueError("N_Ed deve essere >= 0")
    if N_p_Rd <= 0:
        raise ValueError("N_p_Rd deve essere > 0")

    n = N_Ed / N_p_Rd
    if n >= 1.0:
        raise ValueError(f"N_Ed / N_p_Rd = {n:.4f} >= 1.0: la sezione e' esaurita")

    return V_I_Rd * math.sqrt(1.0 - n**2)


@ntc_ref(
    article="7.5.6",
    formula="7.5.22",
    latex=r"M_{I,Rd,r} = M_{I,Rd} \left[1 - \frac{N_{Ed}}{N_{p,Rd}}\right]",
)
def seismic_steel_ebf_link_bending_resistance_reduced(
    M_I_Rd: float,
    N_Ed: float,
    N_p_Rd: float,
) -> float:
    """Capacita' a flessione ridotta per sforzo normale del link EBF [N·mm].

    NTC18 §7.5.6, Formula [7.5.22]:
        M_I,Rd,r = M_I,Rd * (1 - N_Ed / N_p,Rd)

    Da applicare quando N_Ed / N_p,Rd > 0.15.

    Parameters
    ----------
    M_I_Rd : float
        Capacita' a flessione del link in assenza di sforzo normale [N·mm].
    N_Ed : float
        Domanda a sforzo normale nel link [N].
    N_p_Rd : float
        Capacita' a sforzo normale della sezione [N].

    Returns
    -------
    float
        M_I,Rd,r: capacita' a flessione ridotta [N·mm].
    """
    if M_I_Rd <= 0:
        raise ValueError("M_I_Rd deve essere > 0")
    if N_Ed < 0:
        raise ValueError("N_Ed deve essere >= 0")
    if N_p_Rd <= 0:
        raise ValueError("N_p_Rd deve essere > 0")

    n = N_Ed / N_p_Rd
    if n >= 1.0:
        raise ValueError(f"N_Ed / N_p_Rd = {n:.4f} >= 1.0: la sezione e' esaurita")

    return M_I_Rd * (1.0 - n)


@ntc_ref(
    article="7.5.6",
    formula="7.5.23",
    latex=r"e \le 1{,}6 \cdot \frac{M_{I,Rd}}{V_{I,Rd}} \quad (R < 0{,}3)",
)
def seismic_steel_ebf_link_length_limit(
    e: float,
    M_I_Rd: float,
    V_I_Rd: float,
    R: float,
) -> tuple[bool, float, str]:
    """Verifica lunghezza massima del link EBF per garantire taglio prevalente [-].

    NTC18 §7.5.6, Formule [7.5.23]-[7.5.24]:
        Se R < 0.3:  e <= 1.6 * M_I,Rd / V_I,Rd
        Se R >= 0.3: e <= (1.15 - 0.5 * R) * 1.6 * M_I,Rd / V_I,Rd

    dove R = N_Ed * t_w * (d - 2*t_f) / (V_Ed * A)

    Parameters
    ----------
    e : float
        Lunghezza dell'elemento di connessione [mm].
    M_I_Rd : float
        Capacita' a flessione del link [N·mm].
    V_I_Rd : float
        Capacita' a taglio del link [N].
    R : float
        Parametro di interazione R = N_Ed*t_w*(d-2t_f)/(V_Ed*A) [-].

    Returns
    -------
    tuple[bool, float, str]
        - satisfied: True se il limite e' rispettato
        - e_lim: lunghezza limite [mm]
        - formula_used: "7.5.23" o "7.5.24"
    """
    if e <= 0:
        raise ValueError("e deve essere > 0")
    if M_I_Rd <= 0:
        raise ValueError("M_I_Rd deve essere > 0")
    if V_I_Rd <= 0:
        raise ValueError("V_I_Rd deve essere > 0")
    if R < 0:
        raise ValueError("R deve essere >= 0")

    base = 1.6 * M_I_Rd / V_I_Rd

    if R < 0.3:
        e_lim = base
        formula_used = "7.5.23"
    else:
        e_lim = (1.15 - 0.5 * R) * base
        formula_used = "7.5.24"

    return e <= e_lim, e_lim, formula_used


@ntc_ref(
    article="7.5.6",
    formula="7.5.16a",
    latex=r"e \le 0{,}8(1+a)\,\frac{M_{I,Rd}}{V_{I,Rd}} \; \text{corto}",
)
def seismic_steel_ebf_link_classification(
    e: float,
    M_I_Rd: float,
    V_I_Rd: float,
    alpha: float = 1.0,
) -> str:
    """Classificazione dell'elemento di connessione EBF (corto/intermedio/lungo).

    NTC18 §7.5.6, Formule [7.5.16a]-[7.5.16c]:
        "corto":      e <= 0.8*(1+a)*M_I,Rd/V_I,Rd
        "intermedio": 0.8*(1+a)*M_I,Rd/V_I,Rd < e < 1.5*(1+a)*M_I,Rd/V_I,Rd
        "lungo":      e >= 1.5*(1+a)*M_I,Rd/V_I,Rd

    Parameters
    ----------
    e : float
        Lunghezza dell'elemento di connessione [mm].
    M_I_Rd : float
        Capacita' a flessione del link [N·mm].
    V_I_Rd : float
        Capacita' a taglio del link [N].
    alpha : float
        Rapporto tra il momento minore e il maggiore alle estremita' del link
        [-], default 1.0.

    Returns
    -------
    str
        Tipo di link: "corto", "intermedio" o "lungo".
    """
    if e <= 0:
        raise ValueError("e deve essere > 0")
    if M_I_Rd <= 0:
        raise ValueError("M_I_Rd deve essere > 0")
    if V_I_Rd <= 0:
        raise ValueError("V_I_Rd deve essere > 0")
    if alpha < 0 or alpha > 1:
        raise ValueError("alpha deve essere 0 <= alpha <= 1")

    ratio = M_I_Rd / V_I_Rd
    e_short = 0.8 * (1.0 + alpha) * ratio
    e_long = 1.5 * (1.0 + alpha) * ratio

    if e <= e_short:
        return "corto"
    elif e < e_long:
        return "intermedio"
    else:
        return "lungo"


@ntc_ref(
    article="7.5.6",
    formula="7.5.25",
    latex=r"N_{Rd}(M_{Ed}, V_{Ed}) \le N_{Ed,G} + 1{,}1 \cdot \gamma_{ov} \cdot \Omega \cdot N_{Ed,E}",
)
def seismic_steel_ebf_member_demand(
    N_Ed_G: float,
    gamma_ov: float,
    Omega: float,
    N_Ed_E: float,
) -> float:
    """Domanda a sforzo normale amplificata per colonne/diagonali EBF [N].

    NTC18 §7.5.6, Formula [7.5.25]:
        N_Rd(M_Ed, V_Ed) <= N_Ed,G + 1.1 * gamma_ov * Omega * N_Ed,E

    Restituisce il limite superiore della domanda (membro destro).
    Omega e' il minimo di Omega_i = 1.5*V_I,Rd,i/V_Ed,i (link corti) oppure
    Omega = 1.5*M_I,Rd,i/M_Ed,i (link lunghi/intermedi).

    Parameters
    ----------
    N_Ed_G : float
        Domanda a sforzo normale per azioni non sismiche [N].
    gamma_ov : float
        Coefficiente di sovraresistenza del materiale (§7.5.1) [-].
    Omega : float
        Minimo fattore Omega_i tra i link dissipativi [-].
    N_Ed_E : float
        Domanda a sforzo normale per azione sismica [N].

    Returns
    -------
    float
        Limite superiore della domanda N_Ed amplificata [N].
    """
    if gamma_ov <= 0:
        raise ValueError("gamma_ov deve essere > 0")
    if Omega <= 0:
        raise ValueError("Omega deve essere > 0")

    return N_Ed_G + 1.1 * gamma_ov * Omega * N_Ed_E


@ntc_ref(
    article="7.5.6",
    formula="7.5.26",
    latex=r"E_d = E_{d,G} + 1{,}1 \cdot \gamma_{ov} \cdot \Omega_i \cdot E_{d,E}",
)
def seismic_steel_ebf_connection_demand(
    E_d_G: float,
    gamma_ov: float,
    Omega_i: float,
    E_d_E: float,
) -> float:
    """Domanda amplificata per i collegamenti degli elementi di connessione EBF [N o N·mm].

    NTC18 §7.5.6, Formula [7.5.26]:
        E_d = E_d,G + 1.1 * gamma_ov * Omega_i * E_d,E

    I collegamenti devono avere capacita' sufficiente a soddisfare questa
    domanda amplificata.

    Parameters
    ----------
    E_d_G : float
        Domanda per azioni non sismiche [N o N·mm].
    gamma_ov : float
        Coefficiente di sovraresistenza del materiale (§7.5.1) [-].
    Omega_i : float
        Fattore di sovraresistenza relativo all'elemento di connessione i [-].
    E_d_E : float
        Domanda per azione sismica [N o N·mm].

    Returns
    -------
    float
        E_d: domanda amplificata per il collegamento [N o N·mm].
    """
    if gamma_ov <= 0:
        raise ValueError("gamma_ov deve essere > 0")
    if Omega_i <= 0:
        raise ValueError("Omega_i deve essere > 0")

    return E_d_G + 1.1 * gamma_ov * Omega_i * E_d_E


@ntc_ref(
    article="7.5.6",
    formula="7.5.26",
    latex=r"\left| \Omega_{max} - \Omega_{min} \right| / \Omega_{min} \le 0{,}25",
)
def seismic_steel_ebf_omega_homogeneity(
    Omega_values: list[float] | tuple[float, ...],
) -> tuple[bool, float]:
    """Verifica omogeneita' dei coefficienti Omega dei link EBF [-].

    NTC18 §7.5.6:
        (Omega_max - Omega_min) / Omega_min <= 0.25

    Garantisce un comportamento dissipativo omogeneo degli elementi di
    connessione.

    Parameters
    ----------
    Omega_values : list[float]
        Valori Omega_i per i link dissipativi. Per link corti:
        Omega_i = 1.5 * V_I,Rd,i / V_Ed,i. Per link lunghi/intermedi:
        Omega_i = 1.5 * M_I,Rd,i / M_Ed,i [-].

    Returns
    -------
    tuple[bool, float]
        - satisfied: True se la dispersione e' <= 25%
        - dispersion: (Omega_max - Omega_min) / Omega_min [-]
    """
    if not Omega_values:
        raise ValueError("Omega_values non puo' essere vuoto")
    if any(o <= 0 for o in Omega_values):
        raise ValueError("Tutti i valori Omega devono essere > 0")

    Omega_max = max(Omega_values)
    Omega_min = min(Omega_values)
    dispersion = (Omega_max - Omega_min) / Omega_min
    return dispersion <= 0.25, dispersion
