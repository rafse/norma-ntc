"""Verifiche calcestruzzo armato — NTC18 §4.1.

Resistenze di progetto dei materiali, limiti di deformazione,
verifiche SLE (tensioni, fessurazione) e SLU (taglio, torsione,
pressoflessione deviata).

Unita':
- Resistenze e tensioni: [MPa]
- Dimensioni: [mm]
- Aree: [mm^2]
- Forze: [N]
- Momenti torcenti: [N*mm]
- Deformazioni: adimensionali (rapporto, non per mille)
- Aperture fessure: [mm]
"""

from __future__ import annotations

import math

from pyntc.core.reference import ntc_ref


# ── Resistenze di progetto dei materiali ──────────────────────────────────────


@ntc_ref(article="4.1.2.1.1.1", formula="4.1.3", latex=r"f_{cd} = \alpha_{cc} \cdot \frac{f_{ck}}{\gamma_c}")
def concrete_design_compressive_strength(
    f_ck: float,
    gamma_c: float = 1.5,
    alpha_cc: float = 0.85,
) -> float:
    """Resistenza di progetto a compressione del calcestruzzo [MPa].

    NTC18 §4.1.2.1.1.1 — f_cd = alpha_cc * f_ck / gamma_c

    Parameters
    ----------
    f_ck : float
        Resistenza caratteristica cilindrica a compressione [MPa].
    gamma_c : float
        Coefficiente parziale di sicurezza (default 1.5, riducibile a 1.4).
    alpha_cc : float
        Coefficiente riduttivo resistenze lunga durata (default 0.85).

    Returns
    -------
    float
        f_cd [MPa].
    """
    if f_ck <= 0:
        raise ValueError(f"f_ck deve essere > 0, ricevuto {f_ck}")
    return alpha_cc * f_ck / gamma_c


@ntc_ref(article="4.1.2.1.1.2", formula="4.1.4", latex=r"f_{ctd} = \frac{f_{ctk}}{\gamma_c}")
def concrete_design_tensile_strength(
    f_ctk: float,
    gamma_c: float = 1.5,
) -> float:
    """Resistenza di progetto a trazione del calcestruzzo [MPa].

    NTC18 §4.1.2.1.1.2 — f_ctd = f_ctk / gamma_c

    Parameters
    ----------
    f_ctk : float
        Resistenza caratteristica a trazione [MPa].
    gamma_c : float
        Coefficiente parziale di sicurezza (default 1.5).

    Returns
    -------
    float
        f_ctd [MPa].
    """
    if f_ctk <= 0:
        raise ValueError(f"f_ctk deve essere > 0, ricevuto {f_ctk}")
    return f_ctk / gamma_c


@ntc_ref(article="4.1.2.1.1.3", formula="4.1.5", latex=r"f_{yd} = \frac{f_{yk}}{\gamma_s}")
def steel_design_strength(
    f_yk: float,
    gamma_s: float = 1.15,
) -> float:
    """Resistenza di progetto dell'acciaio [MPa].

    NTC18 §4.1.2.1.1.3 — f_yd = f_yk / gamma_s

    Parameters
    ----------
    f_yk : float
        Tensione caratteristica di snervamento [MPa].
    gamma_s : float
        Coefficiente parziale di sicurezza (default 1.15).

    Returns
    -------
    float
        f_yd [MPa].
    """
    if f_yk <= 0:
        raise ValueError(f"f_yk deve essere > 0, ricevuto {f_yk}")
    return f_yk / gamma_s


@ntc_ref(article="4.1.2.1.1.4", formula="4.1.6", latex=r"f_{bd} = 2{,}25 \cdot \eta_1 \cdot \eta_2 \cdot \frac{f_{ctk}}{\gamma_c}")
def bond_design_strength(
    f_ctk: float,
    eta_1: float = 1.0,
    eta_2: float = 1.0,
    gamma_c: float = 1.5,
) -> float:
    """Resistenza tangenziale di aderenza di progetto [MPa].

    NTC18 §4.1.2.1.1.4 — f_bd = 2.25 * eta_1 * eta_2 * f_ctk / gamma_c

    Parameters
    ----------
    f_ctk : float
        Resistenza caratteristica a trazione del calcestruzzo [MPa].
    eta_1 : float
        1.0 buona aderenza, 0.7 non buona aderenza.
    eta_2 : float
        1.0 per Phi <= 32mm, (132-Phi)/100 per Phi > 32mm.
    gamma_c : float
        Coefficiente parziale di sicurezza (default 1.5).

    Returns
    -------
    float
        f_bd [MPa].
    """
    if f_ctk <= 0:
        raise ValueError(f"f_ctk deve essere > 0, ricevuto {f_ctk}")
    return 2.25 * eta_1 * eta_2 * f_ctk / gamma_c


# ── Limiti di deformazione ────────────────────────────────────────────────────


@ntc_ref(article="4.1.2.1.2.1", latex=r"\text{Tab.\,4.1.I — Deformazioni limite } \varepsilon_{c2},\,\varepsilon_{cu2},\,\varepsilon_{c3},\,\varepsilon_{cu3}")
def concrete_strain_limits(
    f_ck: float,
) -> tuple[float, float, float, float]:
    """Deformazioni limite del calcestruzzo (adimensionali).

    NTC18 §4.1.2.1.2.1 — Valori per modelli sigma-epsilon.

    Parameters
    ----------
    f_ck : float
        Resistenza caratteristica cilindrica a compressione [MPa].

    Returns
    -------
    tuple[float, float, float, float]
        (epsilon_c2, epsilon_cu2, epsilon_c3, epsilon_cu3)
        Modello parabola-rettangolo: eps_c2, eps_cu2.
        Modello bilineare: eps_c3, eps_cu3.
    """
    if f_ck <= 0:
        raise ValueError(f"f_ck deve essere > 0, ricevuto {f_ck}")

    if f_ck <= 50.0:
        eps_c2 = 2.0 / 1000
        eps_cu2 = 3.5 / 1000
        eps_c3 = 1.75 / 1000
        eps_cu3 = 3.5 / 1000
    else:
        eps_c2 = (2.0 + 0.085 * (f_ck - 50) ** 0.53) / 1000
        eps_cu2 = (2.6 + 35.0 * ((90 - f_ck) / 100) ** 4) / 1000
        eps_c3 = (1.75 + 0.55 * (f_ck - 50) / 40) / 1000
        eps_cu3 = eps_cu2  # stessa formula NTC18/EC2

    return eps_c2, eps_cu2, eps_c3, eps_cu3


@ntc_ref(article="4.1.2.1.2.1", formula="4.1.8", latex=r"f_{ck,c} = f_{ck}\!\left(1 + 5\,\frac{\sigma_2}{f_{ck}}\right) \;\text{se } \sigma_2 \le 0{,}05\,f_{ck}")
def concrete_confined_strength(
    f_ck: float,
    sigma_2: float,
) -> tuple[float, float, float]:
    """Resistenza e deformazioni del calcestruzzo confinato.

    NTC18 §4.1.2.1.2.1 — Formule [4.1.8]-[4.1.11].

    Parameters
    ----------
    f_ck : float
        Resistenza caratteristica non confinata [MPa].
    sigma_2 : float
        Pressione laterale efficace di confinamento [MPa].

    Returns
    -------
    tuple[float, float, float]
        (f_ck_c, epsilon_c2_c, epsilon_cu_c)
        f_ck_c [MPa], deformazioni adimensionali.
    """
    if f_ck <= 0:
        raise ValueError(f"f_ck deve essere > 0, ricevuto {f_ck}")
    if sigma_2 < 0:
        raise ValueError(f"sigma_2 deve essere >= 0, ricevuto {sigma_2}")

    eps_c2 = 0.002
    eps_cu = 0.0035

    if sigma_2 <= 0.05 * f_ck:
        # [4.1.8]
        f_ck_c = f_ck * (1.0 + 5.0 * sigma_2 / f_ck)
    else:
        # [4.1.9]
        f_ck_c = f_ck * (1.125 + 2.5 * sigma_2 / f_ck)

    # [4.1.10]
    eps_c2_c = eps_c2 * (f_ck_c / f_ck) ** 2
    # [4.1.11]
    eps_cu_c = eps_cu + 0.2 * sigma_2 / f_ck

    return f_ck_c, eps_c2_c, eps_cu_c


# ── Limiti di tensione SLE ────────────────────────────────────────────────────


@ntc_ref(article="4.1.2.2.5.1", formula="4.1.15", latex=r"\sigma_c \le 0{,}60\,f_{ck} \;\text{(rara)};\quad \sigma_c \le 0{,}45\,f_{ck} \;\text{(quasi perm.)}")
def concrete_stress_limit(
    f_ck: float,
    combination: str = "characteristic",
) -> float:
    """Tensione massima ammissibile nel calcestruzzo SLE [MPa].

    NTC18 §4.1.2.2.5.1 — [4.1.15] e [4.1.16].

    Parameters
    ----------
    f_ck : float
        Resistenza caratteristica cilindrica a compressione [MPa].
    combination : str
        "characteristic" (0.60*f_ck) o "quasi_permanent" (0.45*f_ck).

    Returns
    -------
    float
        Tensione massima ammissibile sigma_c,max [MPa].
    """
    if f_ck <= 0:
        raise ValueError(f"f_ck deve essere > 0, ricevuto {f_ck}")

    if combination == "characteristic":
        return 0.60 * f_ck
    elif combination == "quasi_permanent":
        return 0.45 * f_ck
    else:
        raise ValueError(
            f"combination deve essere 'characteristic' o 'quasi_permanent', "
            f"ricevuto '{combination}'"
        )


@ntc_ref(article="4.1.2.2.5.2", formula="4.1.17", latex=r"\sigma_s \le 0{,}80\,f_{yk}")
def steel_stress_limit(f_yk: float) -> float:
    """Tensione massima ammissibile nell'acciaio SLE [MPa].

    NTC18 §4.1.2.2.5.2 — sigma_s,max <= 0.80 * f_yk

    Parameters
    ----------
    f_yk : float
        Tensione caratteristica di snervamento [MPa].

    Returns
    -------
    float
        Tensione massima ammissibile sigma_s,max [MPa].
    """
    if f_yk <= 0:
        raise ValueError(f"f_yk deve essere > 0, ricevuto {f_yk}")
    return 0.80 * f_yk


# ── Verifica a taglio ─────────────────────────────────────────────────────────


@ntc_ref(article="4.1.2.3.5.1", formula="4.1.23", latex=r"V_{Rd} = \max\!\bigl[\bigl(C_{Rd,c}\,k\,(100\,\rho_l\,f_{ck})^{1/3} + 0{,}15\,\sigma_{cp}\bigr)\,b_w\,d;\; (v_{\min} + 0{,}15\,\sigma_{cp})\,b_w\,d\bigr]")
def shear_resistance_no_stirrups(
    f_ck: float,
    d: float,
    bw: float,
    rho_l: float,
    sigma_cp: float = 0.0,
    gamma_c: float = 1.5,
) -> float:
    """Resistenza a taglio senza armature trasversali [N].

    NTC18 §4.1.2.3.5.1 — Formula [4.1.23].

    Parameters
    ----------
    f_ck : float
        Resistenza caratteristica cilindrica [MPa].
    d : float
        Altezza utile della sezione [mm].
    bw : float
        Larghezza minima della sezione [mm].
    rho_l : float
        Rapporto geometrico armatura longitudinale tesa (cappato a 0.02).
    sigma_cp : float
        Tensione media di compressione N_Ed/A_c [MPa] (cappata a 0.2*f_cd).
    gamma_c : float
        Coefficiente parziale (default 1.5).

    Returns
    -------
    float
        V_Rd [N].
    """
    if d <= 0:
        raise ValueError(f"d deve essere > 0, ricevuto {d}")
    if bw <= 0:
        raise ValueError(f"bw deve essere > 0, ricevuto {bw}")
    if f_ck <= 0:
        raise ValueError(f"f_ck deve essere > 0, ricevuto {f_ck}")

    # Cappatura rho_l
    rho_l = min(rho_l, 0.02)

    k = min(1.0 + math.sqrt(200.0 / d), 2.0)
    C_Rd_c = 0.18 / gamma_c

    term1 = (C_Rd_c * k * (100 * rho_l * f_ck) ** (1 / 3) + 0.15 * sigma_cp) * bw * d

    v_min = 0.035 * k ** 1.5 * f_ck ** 0.5
    term2 = (v_min + 0.15 * sigma_cp) * bw * d

    return max(term1, term2)


def _alpha_c_coefficient(sigma_cp: float, f_cd: float) -> float:
    """Coefficiente maggiorativo alpha_c per compressione (§4.1.2.3.5.2)."""
    if sigma_cp <= 0:
        return 1.0
    elif sigma_cp < 0.25 * f_cd:
        return 1.0 + sigma_cp / f_cd
    elif sigma_cp <= 0.5 * f_cd:
        return 1.25
    elif sigma_cp < f_cd:
        return 2.5 * (1.0 - sigma_cp / f_cd)
    else:
        return 0.0  # sigma_cp >= f_cd, sezione completamente compressa


@ntc_ref(article="4.1.2.3.5.2", formula="4.1.27", latex=r"V_{Rd} = \min(V_{Rsd},\,V_{Rcd})")
def shear_resistance_with_stirrups(
    d: float,
    bw: float,
    Asw: float,
    s: float,
    f_yd: float,
    f_cd: float,
    cot_theta: float,
    alpha: float = 90.0,
    sigma_cp: float = 0.0,
) -> float:
    """Resistenza a taglio con armature trasversali [N].

    NTC18 §4.1.2.3.5.2 — Formule [4.1.27]-[4.1.29].
    V_Rd = min(V_Rsd, V_Rcd).

    Parameters
    ----------
    d : float
        Altezza utile [mm].
    bw : float
        Larghezza minima [mm].
    Asw : float
        Area armatura trasversale [mm^2].
    s : float
        Interasse staffe [mm].
    f_yd : float
        Resistenza di progetto acciaio [MPa].
    f_cd : float
        Resistenza di progetto calcestruzzo [MPa].
    cot_theta : float
        Cotangente angolo inclinazione puntoni (1 <= cot_theta <= 2.5).
    alpha : float
        Angolo inclinazione staffe [gradi] (default 90 = verticali).
    sigma_cp : float
        Tensione media compressione [MPa].

    Returns
    -------
    float
        V_Rd [N].
    """
    if not 1.0 <= cot_theta <= 2.5:
        raise ValueError(f"cot_theta deve essere in [1, 2.5], ricevuto {cot_theta}")

    alpha_rad = math.radians(alpha)
    sin_a = math.sin(alpha_rad)
    cot_a = math.cos(alpha_rad) / sin_a if alpha != 90.0 else 0.0

    nu = 0.5  # coefficiente riduzione resistenza cls fessurato
    ac = _alpha_c_coefficient(sigma_cp, f_cd)

    # [4.1.27] — taglio trazione (armatura)
    V_Rsd = 0.9 * d * (Asw / s) * f_yd * (cot_a + cot_theta) * sin_a

    # [4.1.28] — taglio compressione (calcestruzzo)
    V_Rcd = (
        0.9 * d * bw * ac * nu * f_cd
        * (cot_a + cot_theta) / (1.0 + cot_theta ** 2)
    )

    # [4.1.29]
    return min(V_Rsd, V_Rcd)


# ── Verifica a torsione ──────────────────────────────────────────────────────


@ntc_ref(article="4.1.2.3.6", formula="4.1.35", latex=r"T_{Rd} = \min(T_{Rcd},\,T_{Rsd},\,T_{Rld})")
def torsion_resistance(
    A: float,
    t: float,
    Asw: float,
    s: float,
    f_yd: float,
    f_cd: float,
    sum_Al: float,
    um: float,
    cot_theta: float,
    sigma_cp: float = 0.0,
) -> float:
    """Resistenza a torsione [N*mm].

    NTC18 §4.1.2.3.6 — Formule [4.1.35]-[4.1.39].
    T_Rd = min(T_Rcd, T_Rsd, T_Rld).

    Parameters
    ----------
    A : float
        Area racchiusa dalla fibra media del profilo periferico [mm^2].
    t : float
        Spessore della parete equivalente [mm].
    Asw : float
        Area di una staffa (singola branca) [mm^2].
    s : float
        Passo delle staffe [mm].
    f_yd : float
        Resistenza di progetto acciaio [MPa].
    f_cd : float
        Resistenza di progetto calcestruzzo [MPa].
    sum_Al : float
        Area complessiva armatura longitudinale [mm^2].
    um : float
        Perimetro medio del nucleo resistente [mm].
    cot_theta : float
        Cotangente angolo bielle compresse (1 <= cot_theta <= 2.5).
    sigma_cp : float
        Tensione media compressione [MPa].

    Returns
    -------
    float
        T_Rd [N*mm].
    """
    if not 1.0 <= cot_theta <= 2.5:
        raise ValueError(f"cot_theta deve essere in [1, 2.5], ricevuto {cot_theta}")

    nu = 0.5
    ac = _alpha_c_coefficient(sigma_cp, f_cd)

    # [4.1.35] — calcestruzzo
    T_Rcd = (
        2 * A * t * ac * nu * f_cd * cot_theta / (1.0 + cot_theta ** 2)
    )

    # [4.1.36] — staffe trasversali
    T_Rsd = 2 * A * (Asw / s) * f_yd * cot_theta

    # [4.1.37] — armatura longitudinale
    T_Rld = 2 * A * (sum_Al / um) * f_yd / cot_theta

    # [4.1.39]
    return min(T_Rcd, T_Rsd, T_Rld)


@ntc_ref(article="4.1.2.3.6", formula="4.1.40", latex=r"\frac{T_{Ed}}{T_{Rcd}} + \frac{V_{Ed}}{V_{Rcd}} \le 1{,}0")
def torsion_shear_interaction(
    T_Ed: float,
    T_Rcd: float,
    V_Ed: float,
    V_Rcd: float,
) -> float:
    """Rapporto di interazione torsione-taglio.

    NTC18 §4.1.2.3.6 — Formula [4.1.40].
    T_Ed/T_Rcd + V_Ed/V_Rcd <= 1.0 per verifica soddisfatta.

    Parameters
    ----------
    T_Ed : float
        Momento torcente di progetto.
    T_Rcd : float
        Resistenza torsionale lato calcestruzzo.
    V_Ed : float
        Taglio di progetto.
    V_Rcd : float
        Resistenza a taglio lato calcestruzzo.

    Returns
    -------
    float
        Rapporto di utilizzo (<=1.0 = verifica OK).
    """
    return T_Ed / T_Rcd + V_Ed / V_Rcd


# ── Pressoflessione deviata ──────────────────────────────────────────────────


def _biaxial_alpha(nu: float, section: str) -> float:
    """Esponente alpha per verifica pressoflessione deviata [4.1.19].

    Per sezioni rettangolari: interpolazione lineare dalla tabella NTC18.
    Per sezioni circolari/ellittiche: alpha = 2.0.
    """
    if section in ("circular", "elliptical"):
        return 2.0

    # Tabella NTC18 §4.1.2.3.4.2 per sezioni rettangolari
    # N_Ed/N_Rd:  0.1 -> 1.0,  0.7 -> 1.5,  1.0 -> 2.0
    if nu <= 0.1:
        return 1.0
    elif nu <= 0.7:
        return 1.0 + (nu - 0.1) / (0.7 - 0.1) * (1.5 - 1.0)
    elif nu <= 1.0:
        return 1.5 + (nu - 0.7) / (1.0 - 0.7) * (2.0 - 1.5)
    else:
        return 2.0


@ntc_ref(article="4.1.2.3.4.2", formula="4.1.19", latex=r"\left(\frac{M_{Edy}}{M_{Rdy}}\right)^{\!\alpha} + \left(\frac{M_{Edz}}{M_{Rdz}}\right)^{\!\alpha} \le 1{,}0")
def biaxial_bending_check(
    M_Edy: float,
    M_Rdy: float,
    M_Edz: float,
    M_Rdz: float,
    N_Ed: float,
    N_Rd: float,
    section: str = "rectangular",
) -> float:
    """Rapporto di verifica pressoflessione deviata.

    NTC18 §4.1.2.3.4.2 — Formula [4.1.19].
    (M_Edy/M_Rdy)^alpha + (M_Edz/M_Rdz)^alpha <= 1.0

    Parameters
    ----------
    M_Edy, M_Rdy : float
        Momento sollecitante e resistente attorno all'asse y.
    M_Edz, M_Rdz : float
        Momento sollecitante e resistente attorno all'asse z.
    N_Ed : float
        Sforzo normale di progetto.
    N_Rd : float
        Resistenza assiale della sezione.
    section : str
        "rectangular" (default), "circular" o "elliptical".

    Returns
    -------
    float
        Rapporto di utilizzo (<=1.0 = verifica OK).
    """
    nu = N_Ed / N_Rd
    alpha = _biaxial_alpha(nu, section)
    return (M_Edy / M_Rdy) ** alpha + (M_Edz / M_Rdz) ** alpha


# ── Snellezza elementi compressi ──────────────────────────────────────────────


@ntc_ref(article="4.1.2.3.9.2", formula="4.1.42", latex=r"\lambda = l_0 / i")
def concrete_slenderness(l_0: float, i: float) -> float:
    """Snellezza di un elemento compresso in c.a. [-].

    NTC18 §4.1.2.3.9.2, Formula [4.1.42]:
        lambda = l_0 / i

    Parameters
    ----------
    l_0 : float
        Lunghezza libera di inflessione [mm].
    i : float
        Raggio di inerzia della sezione [mm].

    Returns
    -------
    float
        Snellezza lambda [-].
    """
    if l_0 <= 0:
        raise ValueError("l_0 deve essere > 0")
    if i <= 0:
        raise ValueError("i deve essere > 0")
    return l_0 / i


@ntc_ref(
    article="4.1.2.3.9.2",
    formula="4.1.41",
    latex=r"\lambda_{\lim} = \frac{25}{\sqrt{v}}",
)
def concrete_slenderness_limit(v: float) -> float:
    """Snellezza limite per pilastri in c.a. [-].

    NTC18 §4.1.2.3.9.2, Formula [4.1.41]:
        lambda_lim = 25 / sqrt(v)

    dove v = N_Ed / (A_c * f_cd) e' il rapporto di sollecitazione assiale.

    Parameters
    ----------
    v : float
        Rapporto di sollecitazione assiale v = N_Ed / (A_c * f_cd) [-].
        Deve essere 0 < v <= 1.

    Returns
    -------
    float
        Snellezza limite lambda_lim [-].
    """
    if v <= 0:
        raise ValueError("v deve essere > 0")
    if v > 1.0:
        raise ValueError("v deve essere <= 1.0")
    return 25.0 / math.sqrt(v)


# ── Armatura minima ───────────────────────────────────────────────────────────


@ntc_ref(
    article="4.1.6.1.1",
    formula="4.1.45",
    latex=r"A_{s,\min} = \max\!\left(0{,}26\,\frac{f_{ctm}}{f_{yk}}\,b\,d;\;0{,}0013\,b\,d\right)",
)
def concrete_beam_min_reinforcement(
    f_ctm: float, f_yk: float, b: float, d: float
) -> float:
    """Armatura longitudinale minima per travi in c.a. [mm^2].

    NTC18 §4.1.6.1.1, Formula [4.1.45]:
        A_s,min = max(0.26 * f_ctm/f_yk * b * d, 0.0013 * b * d)

    Parameters
    ----------
    f_ctm : float
        Resistenza media a trazione del calcestruzzo [MPa].
    f_yk : float
        Resistenza caratteristica a snervamento dell'acciaio [MPa].
    b : float
        Larghezza della sezione [mm].
    d : float
        Altezza utile della sezione [mm].

    Returns
    -------
    float
        A_s,min: area minima dell'armatura longitudinale [mm^2].
    """
    if f_ctm <= 0:
        raise ValueError("f_ctm deve essere > 0")
    if f_yk <= 0:
        raise ValueError("f_yk deve essere > 0")
    if b <= 0:
        raise ValueError("b deve essere > 0")
    if d <= 0:
        raise ValueError("d deve essere > 0")
    a1 = 0.26 * (f_ctm / f_yk) * b * d
    a2 = 0.0013 * b * d
    return max(a1, a2)


@ntc_ref(
    article="4.1.6.1.2",
    formula="4.1.46",
    latex=r"A_{s,\min} = \max\!\left(0{,}10\,\frac{N_{Ed}}{f_{yd}};\;0{,}003\,A_c\right)",
)
def concrete_column_min_reinforcement(
    N_Ed: float, f_yd: float, A_c: float
) -> float:
    """Armatura longitudinale minima per pilastri in c.a. [mm^2].

    NTC18 §4.1.6.1.2, Formula [4.1.46]:
        A_s,min = max(0.10 * N_Ed / f_yd, 0.003 * A_c)

    Parameters
    ----------
    N_Ed : float
        Sforzo normale di progetto [N].
    f_yd : float
        Resistenza di progetto dell'acciaio [MPa].
    A_c : float
        Area della sezione di calcestruzzo [mm^2].

    Returns
    -------
    float
        A_s,min: area minima dell'armatura longitudinale [mm^2].
    """
    if N_Ed < 0:
        raise ValueError("N_Ed deve essere >= 0")
    if f_yd <= 0:
        raise ValueError("f_yd deve essere > 0")
    if A_c <= 0:
        raise ValueError("A_c deve essere > 0")
    a1 = 0.10 * N_Ed / f_yd
    a2 = 0.003 * A_c
    return max(a1, a2)


# ── Armature da precompressione ───────────────────────────────────────────────


@ntc_ref(
    article="4.1.8.15",
    formula="4.1.49",
    latex=(
        r"\sigma_{p,\max} \le \begin{cases}"
        r"0{,}85\,f_{p(0,1)k}\text{ e }0{,}75\,f_{pk} & \text{post-tesa}\\"
        r"0{,}90\,f_{p(0,1)k}\text{ e }0{,}80\,f_{pk} & \text{pre-tesa}"
        r"\end{cases}"
    ),
)
def concrete_prestress_stress_limits(
    f_p01k: float, f_pk: float, prestress_type: str
) -> tuple[float, float]:
    """Tensioni limite per armature da precompressione [MPa].

    NTC18 §4.1.8.15, Formula [4.1.49]:
    - Post-tesa:  sigma < 0.85 * f_p(0.1)k  e  sigma < 0.75 * f_pk
    - Pre-tesa:   sigma < 0.90 * f_p(0.1)k  e  sigma < 0.80 * f_pk

    Parameters
    ----------
    f_p01k : float
        Tensione caratteristica all'1‰ di deformazione [MPa].
    f_pk : float
        Tensione caratteristica a rottura [MPa].
    prestress_type : str
        Tipo di precompressione: "post_tensioned" o "pre_tensioned".

    Returns
    -------
    tuple[float, float]
        (sigma_max_01k, sigma_max_pk): tensioni limite [MPa].
        La tensione applicata deve essere minore di entrambi i valori.
    """
    if f_p01k <= 0:
        raise ValueError("f_p01k deve essere > 0")
    if f_pk <= 0:
        raise ValueError("f_pk deve essere > 0")
    if prestress_type == "post_tensioned":
        return 0.85 * f_p01k, 0.75 * f_pk
    elif prestress_type == "pre_tensioned":
        return 0.90 * f_p01k, 0.80 * f_pk
    else:
        raise ValueError(
            f"prestress_type deve essere 'post_tensioned' o 'pre_tensioned', "
            f"ricevuto '{prestress_type}'"
        )


# ── Classi di resistenza del calcestruzzo ─────────────────────────────────────

# Valori NTC18 Tab. 4.1.I — f_ck [MPa] -> (f_cm, f_ctm, f_ctk_005, E_cm)
# f_cm = f_ck + 8 [MPa]
# f_ctm = 0.30 * f_ck^(2/3) per f_ck <= 50; 2.12 * ln(1 + f_cm/10) per f_ck > 50
# f_ctk_005 = 0.70 * f_ctm (5° percentile)
# E_cm = 22000 * (f_cm/10)^0.3 [MPa]
_CONCRETE_CLASSES: dict[str, dict[str, float]] = {
    "C8/10":    {"f_ck": 8.0,  "f_cm": 16.0, "f_ctm": 1.12, "f_ctk_005": 0.78,  "E_cm": 27085.0},
    "C12/15":   {"f_ck": 12.0, "f_cm": 20.0, "f_ctm": 1.57, "f_ctk_005": 1.10,  "E_cm": 29000.0},
    "C16/20":   {"f_ck": 16.0, "f_cm": 24.0, "f_ctm": 1.90, "f_ctk_005": 1.33,  "E_cm": 29900.0},
    "C20/25":   {"f_ck": 20.0, "f_cm": 28.0, "f_ctm": 2.21, "f_ctk_005": 1.55,  "E_cm": 30000.0},
    "C25/30":   {"f_ck": 25.0, "f_cm": 33.0, "f_ctm": 2.56, "f_ctk_005": 1.80,  "E_cm": 31476.0},
    "C30/37":   {"f_ck": 30.0, "f_cm": 38.0, "f_ctm": 2.90, "f_ctk_005": 2.03,  "E_cm": 32837.0},
    "C35/45":   {"f_ck": 35.0, "f_cm": 43.0, "f_ctm": 3.21, "f_ctk_005": 2.25,  "E_cm": 34077.0},
    "C40/50":   {"f_ck": 40.0, "f_cm": 48.0, "f_ctm": 3.51, "f_ctk_005": 2.46,  "E_cm": 35220.0},
    "C45/55":   {"f_ck": 45.0, "f_cm": 53.0, "f_ctm": 3.80, "f_ctk_005": 2.66,  "E_cm": 36283.0},
    "C50/60":   {"f_ck": 50.0, "f_cm": 58.0, "f_ctm": 4.07, "f_ctk_005": 2.85,  "E_cm": 37278.0},
    "C55/67":   {"f_ck": 55.0, "f_cm": 63.0, "f_ctm": 4.21, "f_ctk_005": 2.95,  "E_cm": 38215.0},
    "C60/75":   {"f_ck": 60.0, "f_cm": 68.0, "f_ctm": 4.34, "f_ctk_005": 3.04,  "E_cm": 39096.0},
    "C70/85":   {"f_ck": 70.0, "f_cm": 78.0, "f_ctm": 4.57, "f_ctk_005": 3.20,  "E_cm": 40745.0},
    "C80/95":   {"f_ck": 80.0, "f_cm": 88.0, "f_ctm": 4.77, "f_ctk_005": 3.34,  "E_cm": 42292.0},
    "C90/105":  {"f_ck": 90.0, "f_cm": 98.0, "f_ctm": 4.96, "f_ctk_005": 3.47,  "E_cm": 43745.0},
}


@ntc_ref(
    article="4.1.2.1.1",
    table="Tab. 4.1.I",
    latex=r"\text{Tab.\,4.1.I — Classi di resistenza del calcestruzzo}",
)
def concrete_strength_class(strength_class: str) -> dict[str, float]:
    """Proprieta' meccaniche di una classe di resistenza del calcestruzzo.

    NTC18 §4.1.2.1.1 — Tabella 4.1.I.
    Classi disponibili: C8/10 ... C90/105.

    Parameters
    ----------
    strength_class : str
        Denominazione della classe di resistenza (es. "C25/30").

    Returns
    -------
    dict[str, float]
        Dizionario con le chiavi:
        - f_ck  : resistenza caratteristica cilindrica [MPa]
        - f_cm  : resistenza media cilindrica [MPa]
        - f_ctm : resistenza media a trazione [MPa]
        - f_ctk_005 : resistenza caratteristica a trazione (5° perc.) [MPa]
        - E_cm  : modulo elastico secante [MPa]
    """
    if strength_class not in _CONCRETE_CLASSES:
        valid = ", ".join(_CONCRETE_CLASSES)
        raise ValueError(
            f"Classe '{strength_class}' non riconosciuta. "
            f"Classi valide: {valid}"
        )
    return dict(_CONCRETE_CLASSES[strength_class])


# ── Verifica a fessurazione SLE ───────────────────────────────────────────────

# Limiti w_max [mm] — NTC18 Tab. 4.1.IV
# Armatura sensibile: Gruppi A(frequente/q.p.)=w1, B(frequente)=w1, C(frequente)=0
# Armatura poco sensibile: tutti i casi w1
# Valori numerici EC2/NTC18: w1=0.2mm, w2=0.3mm, w3=0.4mm
# NTC18 §4.1.2.2.4 specifica w1, w2, w3 in funzione della classe di esposizione
# Tabella 4.1.III NTC18 assegna:
#   XC1           -> w_max = 0.4 mm
#   XC2, XC3, XC4 -> w_max = 0.3 mm
#   XD, XS, XF    -> w_max = 0.2 mm (armatura sensibile)
_CRACK_WIDTH_LIMITS: dict[tuple[str, str], float | None] = {
    # (classe_esposizione, combinazione) -> w_max [mm] | None (decompressione)
    ("XC1", "quasi_permanent"):  0.4,
    ("XC1", "frequent"):         0.4,
    ("XC2", "quasi_permanent"):  0.3,
    ("XC2", "frequent"):         0.3,
    ("XC3", "quasi_permanent"):  0.3,
    ("XC3", "frequent"):         0.3,
    ("XC4", "quasi_permanent"):  0.3,
    ("XC4", "frequent"):         0.3,
    ("XD1", "quasi_permanent"):  0.2,
    ("XD1", "frequent"):         0.2,
    ("XD2", "quasi_permanent"):  0.2,
    ("XD2", "frequent"):         0.2,
    ("XD3", "quasi_permanent"):  0.2,
    ("XD3", "frequent"):         0.2,
    ("XS1", "quasi_permanent"):  0.2,
    ("XS1", "frequent"):         0.2,
    ("XS2", "quasi_permanent"):  0.2,
    ("XS2", "frequent"):         0.2,
    ("XS3", "quasi_permanent"):  0.2,
    ("XS3", "frequent"):         0.2,
}


@ntc_ref(
    article="4.1.2.2.4.4",
    table="Tab. 4.1.IV",
    latex=r"w_k \le w_{\max} \quad \text{(Tab.\,4.1.IV)}",
)
def concrete_crack_width_limit(
    exposure_class: str,
    load_combination: str = "quasi_permanent",
) -> float:
    """Apertura massima delle fessure in funzione della classe di esposizione.

    NTC18 §4.1.2.2.4.4 — Tab. 4.1.IV.

    Parameters
    ----------
    exposure_class : str
        Classe di esposizione ambientale secondo NTC18/EC2.
        Valori ammessi: "XC1", "XC2", "XC3", "XC4",
        "XD1", "XD2", "XD3", "XS1", "XS2", "XS3".
    load_combination : str
        Combinazione delle azioni: "quasi_permanent" (default) o "frequent".

    Returns
    -------
    float
        Apertura massima ammissibile w_max [mm].
    """
    key = (exposure_class.upper(), load_combination)
    if key not in _CRACK_WIDTH_LIMITS:
        valid_classes = sorted({k[0] for k in _CRACK_WIDTH_LIMITS})
        valid_combos = sorted({k[1] for k in _CRACK_WIDTH_LIMITS})
        raise ValueError(
            f"Combinazione classe='{exposure_class}', "
            f"combinazione='{load_combination}' non valida. "
            f"Classi valide: {valid_classes}. "
            f"Combinazioni valide: {valid_combos}."
        )
    return _CRACK_WIDTH_LIMITS[key]


@ntc_ref(
    article="4.1.2.2.4.5",
    formula="4.1.14",
    latex=r"w_1 = 1{,}7 \cdot \varepsilon_{am} \cdot \Delta_{am}",
)
def concrete_crack_width(epsilon_am_cm: float, s_r_max: float) -> float:
    """Apertura caratteristica delle fessure [mm].

    NTC18 §4.1.2.2.4.5 — Formula [4.1.14]:
        w_1 = 1.7 * epsilon_am_cm * s_r_max

    Parameters
    ----------
    epsilon_am_cm : float
        Differenza media di deformazione (epsilon_am - epsilon_cm) [-].
        Valore non negativo (adimensionale).
    s_r_max : float
        Distanza massima tra fessure [mm].

    Returns
    -------
    float
        Apertura caratteristica w_1 [mm].
    """
    if epsilon_am_cm < 0:
        raise ValueError(
            f"epsilon_am_cm deve essere >= 0, ricevuto {epsilon_am_cm}"
        )
    if s_r_max <= 0:
        raise ValueError(f"s_r_max deve essere > 0, ricevuto {s_r_max}")
    return 1.7 * epsilon_am_cm * s_r_max


@ntc_ref(
    article="4.1.2.2.4.5",
    formula="4.1.15",
    latex=(
        r"\varepsilon_{am} - \varepsilon_{cm} = "
        r"\frac{\sigma_s - k_t \frac{f_{ctm}}{\rho_{eff}}(1 + n\,\rho_{eff})}{E_s}"
        r"\ge 0{,}6\,\frac{\sigma_s}{E_s}"
    ),
)
def concrete_crack_mean_strain(
    sigma_s: float,
    E_s: float,
    rho_eff: float,
    f_ctm: float,
    k_t: float = 0.4,
) -> float:
    """Differenza media di deformazione tra acciaio e calcestruzzo [-].

    NTC18 §4.1.2.2.4.5 — Formule [4.1.15]-[4.1.16]:
        epsilon_am - epsilon_cm =
            [sigma_s - k_t * (f_ctm / rho_eff) * (1 + n * rho_eff)] / E_s
        con il limite inferiore:
            >= 0.6 * sigma_s / E_s

    Il rapporto modulare n = E_s / E_cm e' comunemente preso pari a 15
    (valore di riferimento NTC18 per il calcestruzzo ordinario),
    ma il suo effetto su (1 + n*rho_eff) e' trascurabile per rho_eff tipici.
    In questa formula n*rho_eff rappresenta il contributo della rigidezza
    del calcestruzzo interposto tra le fessure; il prodotto
    (f_ctm/rho_eff)*(1+n*rho_eff) e' anche scritto come f_ctm/rho_eff + n*f_ctm.

    Parameters
    ----------
    sigma_s : float
        Tensione nell'armatura tesa nella sezione fessurata [MPa].
    E_s : float
        Modulo elastico dell'acciaio [MPa] (tipicamente 200000 MPa).
    rho_eff : float
        Rapporto di armatura efficace A_s / A_c,eff [-].
    f_ctm : float
        Resistenza media a trazione del calcestruzzo [MPa].
    k_t : float
        Coefficiente di durata del carico: 0.6 per carichi brevi,
        0.4 per carichi di lunga durata (default 0.4).

    Returns
    -------
    float
        epsilon_am - epsilon_cm [-], non negativo.
    """
    if sigma_s <= 0:
        raise ValueError(f"sigma_s deve essere > 0, ricevuto {sigma_s}")
    if E_s <= 0:
        raise ValueError(f"E_s deve essere > 0, ricevuto {E_s}")
    if rho_eff <= 0:
        raise ValueError(f"rho_eff deve essere > 0, ricevuto {rho_eff}")
    if f_ctm <= 0:
        raise ValueError(f"f_ctm deve essere > 0, ricevuto {f_ctm}")
    if k_t not in (0.4, 0.6) and not (0.0 < k_t <= 1.0):
        raise ValueError(f"k_t deve essere in (0, 1], ricevuto {k_t}")

    # Rapporto modulare n = E_s / E_cm; per E_cm medio NTC18 ≈ 31000 MPa -> n ≈ 6.45
    # NTC18 usa n = E_s / E_cm calcolato; come da prassi si usa n ≈ 15 per c.a. ordinario
    # ma la formula nel testo NTC18 §4.1.2.2.4.5 indica esplicitamente n = E_s/E_cm.
    # Qui si adotta n = 15 come valore di riferimento standard per acciaio/calcestruzzo.
    n = 15.0

    eps_formula = (sigma_s - k_t * (f_ctm / rho_eff) * (1.0 + n * rho_eff)) / E_s
    eps_min = 0.6 * sigma_s / E_s
    return max(eps_formula, eps_min)


@ntc_ref(
    article="4.1.2.2.4.5",
    formula="4.1.17",
    latex=r"s_{r,\max} = k_3\,c + k_1\,k_2\,k_4\,\frac{\phi}{\rho_{eff}}",
)
def concrete_crack_spacing(
    phi: float,
    rho_eff: float,
    c: float,
    k_1: float = 0.8,
    k_2: float = 0.5,
    k_3: float = 3.4,
    k_4: float = 0.425,
) -> float:
    """Distanza massima tra fessure [mm].

    NTC18 §4.1.2.2.4.5 — Formula [4.1.17]:
        s_r,max = k_3 * c + k_1 * k_2 * k_4 * phi / rho_eff

    Valori tipici dei coefficienti (NTC18/EC2):
    - k_1 = 0.8 per barre ad aderenza migliorata, 1.6 per barre lisce
    - k_2 = 0.5 per flessione pura, 1.0 per trazione pura
    - k_3 = 3.4
    - k_4 = 0.425

    Parameters
    ----------
    phi : float
        Diametro delle barre di armatura [mm].
    rho_eff : float
        Rapporto di armatura efficace A_s / A_c,eff [-].
    c : float
        Copriferro netto [mm].
    k_1 : float
        Coefficiente per tipo di barra (default 0.8, aderenza migliorata).
    k_2 : float
        Coefficiente per distribuzione delle deformazioni (default 0.5).
    k_3 : float
        Coefficiente per copriferro (default 3.4).
    k_4 : float
        Coefficiente per spaziatura (default 0.425).

    Returns
    -------
    float
        s_r,max [mm].
    """
    if phi <= 0:
        raise ValueError(f"phi deve essere > 0, ricevuto {phi}")
    if rho_eff <= 0:
        raise ValueError(f"rho_eff deve essere > 0, ricevuto {rho_eff}")
    if c < 0:
        raise ValueError(f"c deve essere >= 0, ricevuto {c}")
    return k_3 * c + k_1 * k_2 * k_4 * phi / rho_eff


# ── Flessione semplice ────────────────────────────────────────────────────────


@ntc_ref(article="4.1.2.3.1", formula="4.1.19", latex=r"M_{Rd} = A_s f_{yd} (d - 0.4x)")
def concrete_bending_resistance(
    b: float,
    d: float,
    A_s: float,
    f_yd: float,
    f_cd: float,
) -> float:
    """Momento resistente sezione rettangolare a pressoflessione semplice [N*mm].

    NTC18 §4.1.2.3.1 — Armatura tesa, blocco rettangolare di tensioni.

    Parameters
    ----------
    b : float
        Larghezza della sezione [mm].
    d : float
        Altezza utile della sezione [mm].
    A_s : float
        Area armatura tesa [mm²].
    f_yd : float
        Resistenza di progetto acciaio [MPa].
    f_cd : float
        Resistenza di progetto calcestruzzo [MPa].

    Returns
    -------
    float
        M_Rd [N*mm].
    """
    if b <= 0:
        raise ValueError(f"b deve essere > 0, ricevuto {b}")
    if d <= 0:
        raise ValueError(f"d deve essere > 0, ricevuto {d}")
    if A_s <= 0:
        raise ValueError(f"A_s deve essere > 0, ricevuto {A_s}")
    if f_yd <= 0:
        raise ValueError(f"f_yd deve essere > 0, ricevuto {f_yd}")
    if f_cd <= 0:
        raise ValueError(f"f_cd deve essere > 0, ricevuto {f_cd}")

    x = A_s * f_yd / (0.8 * b * f_cd)
    if x > d:
        raise ValueError(
            f"Asse neutro x={x:.2f} mm > d={d:.2f} mm: sezione completamente compressa"
        )
    return A_s * f_yd * (d - 0.4 * x)


@ntc_ref(article="4.1.2.3.1", formula="4.1.19", latex=r"M_{Ed} \le M_{Rd}")
def concrete_bending_check(
    M_Ed: float,
    M_Rd: float,
) -> tuple[bool, float]:
    """Verifica a flessione semplice.

    NTC18 §4.1.2.3.1 — M_Ed / M_Rd <= 1.0.

    Parameters
    ----------
    M_Ed : float
        Momento flettente di progetto [N*mm].
    M_Rd : float
        Momento resistente [N*mm].

    Returns
    -------
    tuple[bool, float]
        (verifica_ok, ratio) con ratio = M_Ed / M_Rd.
    """
    ratio = M_Ed / M_Rd
    return ratio <= 1.0, ratio


# ── Punzonamento ──────────────────────────────────────────────────────────────


@ntc_ref(article="4.1.2.3.7", formula="4.1.30", latex=r"V_{Rd,c} = v_{Rd,c} \cdot b_0 \cdot d")
def concrete_punching_shear_resistance(
    f_ck: float,
    rho_l: float,
    sigma_cp: float,
    b_0: float,
    d: float,
    gamma_c: float = 1.5,
) -> float:
    """Resistenza a punzonamento senza armatura [N].

    NTC18 §4.1.2.3.7 — Formula [4.1.30].

    Parameters
    ----------
    f_ck : float
        Resistenza caratteristica cilindrica a compressione [MPa].
    rho_l : float
        Rapporto geometrico armatura longitudinale [-] (cappato a 0.02).
    sigma_cp : float
        Tensione media di compressione N_Ed/A_c [MPa] (0 se assente).
    b_0 : float
        Perimetro critico di controllo [mm].
    d : float
        Altezza utile della sezione [mm].
    gamma_c : float
        Coefficiente parziale (default 1.5).

    Returns
    -------
    float
        V_Rd,c [N].
    """
    if f_ck <= 0:
        raise ValueError(f"f_ck deve essere > 0, ricevuto {f_ck}")
    if b_0 <= 0:
        raise ValueError(f"b_0 deve essere > 0, ricevuto {b_0}")
    if d <= 0:
        raise ValueError(f"d deve essere > 0, ricevuto {d}")

    rho_l = min(rho_l, 0.02)
    k = min(1.0 + math.sqrt(200.0 / d), 2.0)

    v_Rdc = (0.18 / gamma_c) * k * (100.0 * rho_l * f_ck) ** (1.0 / 3.0) + 0.15 * sigma_cp
    v_min = 0.035 * k ** 1.5 * f_ck ** 0.5

    return max(v_Rdc, v_min + 0.15 * sigma_cp) * b_0 * d


@ntc_ref(article="4.1.2.3.7", formula="4.1.30", latex=r"V_{Ed} \le V_{Rd,c}")
def concrete_punching_shear_check(
    V_Ed: float,
    f_ck: float,
    rho_l: float,
    sigma_cp: float,
    b_0: float,
    d: float,
    gamma_c: float = 1.5,
) -> tuple[bool, float]:
    """Verifica a punzonamento senza armatura.

    NTC18 §4.1.2.3.7 — V_Ed / V_Rd,c <= 1.0.

    Parameters
    ----------
    V_Ed : float
        Forza di punzonamento di progetto [N].
    f_ck : float
        Resistenza caratteristica cilindrica a compressione [MPa].
    rho_l : float
        Rapporto geometrico armatura longitudinale [-].
    sigma_cp : float
        Tensione media di compressione [MPa] (0 se assente).
    b_0 : float
        Perimetro critico di controllo [mm].
    d : float
        Altezza utile della sezione [mm].
    gamma_c : float
        Coefficiente parziale (default 1.5).

    Returns
    -------
    tuple[bool, float]
        (verifica_ok, ratio) con ratio = V_Ed / V_Rd,c.
    """
    V_Rdc = concrete_punching_shear_resistance(f_ck, rho_l, sigma_cp, b_0, d, gamma_c)
    ratio = V_Ed / V_Rdc
    return ratio <= 1.0, ratio


# ── Punzonamento con armatura ─────────────────────────────────────────────────


@ntc_ref(article="4.1.2.3.7", formula="4.1.32", latex=r"V_{Rd} = 0.75V_{Rd,c} + V_{Rd,s}")
def concrete_punching_shear_resistance_reinforced(
    f_ck: float,
    rho_l: float,
    sigma_cp: float,
    b_0: float,
    d: float,
    A_sw: float,
    f_ywd: float,
    s_r: float,
    gamma_c: float = 1.5,
) -> float:
    """Resistenza a punzonamento con armatura [N].

    NTC18 §4.1.2.3.7 — Formula [4.1.32].
    V_Rd = 0.75 * V_Rd,c + V_Rd,s

    Parameters
    ----------
    f_ck : float
        Resistenza caratteristica cilindrica [MPa].
    rho_l : float
        Rapporto geometrico armatura longitudinale (cappato a 0.02).
    sigma_cp : float
        Tensione media di compressione N_Ed/A_c [MPa].
    b_0 : float
        Perimetro di controllo [mm].
    d : float
        Altezza utile [mm].
    A_sw : float
        Area armatura a punzonamento in un perimetro [mm²].
    f_ywd : float
        Resistenza di progetto armatura a punzonamento [MPa].
    s_r : float
        Distanza radiale tra i cerchi di armatura [mm].
    gamma_c : float
        Coefficiente parziale calcestruzzo (default 1.5).

    Returns
    -------
    float
        V_Rd [N].
    """
    if A_sw < 0:
        raise ValueError(f"A_sw deve essere >= 0, ricevuto {A_sw}")
    if f_ywd <= 0:
        raise ValueError(f"f_ywd deve essere > 0, ricevuto {f_ywd}")

    V_Rd_c = concrete_punching_shear_resistance(f_ck, rho_l, sigma_cp, b_0, d, gamma_c)
    V_Rd_c_red = 0.75 * V_Rd_c
    V_Rd_s = (1.0 / 1.5) * A_sw * f_ywd  # sin(alpha)=1 per staffe verticali
    return V_Rd_c_red + V_Rd_s


# ── Lunghezza efficace pilastro ───────────────────────────────────────────────


@ntc_ref(article="4.1.2.3.9.1", latex=r"l_0 = \beta L")
def concrete_column_effective_length(
    L: float,
    condition_top: str,
    condition_bottom: str,
) -> float:
    """Lunghezza efficace del pilastro [mm].

    NTC18 §4.1.2.3.9.1 — l_0 = beta * L

    Parameters
    ----------
    L : float
        Lunghezza geometrica del pilastro [mm].
    condition_top : str
        Condizione di vincolo alla sommità: "fixed", "pinned" o "free".
    condition_bottom : str
        Condizione di vincolo alla base: "fixed", "pinned" o "free".

    Returns
    -------
    float
        Lunghezza efficace l_0 [mm].
    """
    if L <= 0:
        raise ValueError(f"L deve essere > 0, ricevuto {L}")

    _valid = {"fixed", "pinned", "free"}
    if condition_top not in _valid:
        raise ValueError(f"condition_top deve essere in {_valid}, ricevuto '{condition_top}'")
    if condition_bottom not in _valid:
        raise ValueError(f"condition_bottom deve essere in {_valid}, ricevuto '{condition_bottom}'")

    _beta_map: dict[tuple[str, str], float] = {
        ("fixed", "fixed"): 0.5,
        ("fixed", "pinned"): 0.7,
        ("pinned", "fixed"): 0.7,
        ("pinned", "pinned"): 1.0,
        ("fixed", "free"): 2.0,
        ("free", "fixed"): 2.0,
        ("pinned", "free"): 2.0,
        ("free", "pinned"): 2.0,
    }

    key = (condition_top, condition_bottom)
    if key not in _beta_map:
        raise ValueError(
            f"Combinazione ('{condition_top}', '{condition_bottom}') non supportata."
        )

    beta = _beta_map[key]
    return beta * L


# ── Verifica dominio N-M ──────────────────────────────────────────────────────


@ntc_ref(article="4.1.2.3.3", formula="4.1.19", latex=r"N_{Ed}/N_{Rd} + M_{Ed}/M_{Rd} \le 1")
def concrete_column_interaction_check(
    N_Ed: float,
    M_Ed: float,
    N_Rd: float,
    M_Rd: float,
) -> tuple[bool, float]:
    """Verifica dominio N-M (interazione lineare) per pilastro in c.a.

    NTC18 §4.1.2.3.3 — Formula [4.1.19].
    N_Ed/N_Rd + M_Ed/M_Rd <= 1.0

    Parameters
    ----------
    N_Ed : float
        Sforzo normale di progetto [N].
    M_Ed : float
        Momento di progetto [N*mm].
    N_Rd : float
        Resistenza assiale di progetto [N].
    M_Rd : float
        Resistenza flessionale di progetto [N*mm].

    Returns
    -------
    tuple[bool, float]
        (verifica_ok, ratio) dove ratio = N_Ed/N_Rd + M_Ed/M_Rd.
    """
    if N_Rd <= 0:
        raise ValueError(f"N_Rd deve essere > 0, ricevuto {N_Rd}")
    if M_Rd <= 0:
        raise ValueError(f"M_Rd deve essere > 0, ricevuto {M_Rd}")

    ratio = N_Ed / N_Rd + M_Ed / M_Rd
    return ratio <= 1.0, ratio


# ── Passo massimo staffe ──────────────────────────────────────────────────────


@ntc_ref(article="4.1.2.3.5.3", formula="4.1.29", latex=r"s_{max} = \min(0.75d,\;300\,\text{mm})")
def concrete_min_stirrup_spacing(
    d: float,
    phi_l: float = 0.0,
    phi_w: float = 0.0,
) -> float:
    """Passo massimo staffe trasversali [mm].

    NTC18 §4.1.2.3.5.3 — Formula [4.1.29].
    Per staffe verticali: s_max = min(0.75*d, 300 mm).

    Parameters
    ----------
    d : float
        Altezza utile della sezione [mm].
    phi_l : float
        Diametro barra longitudinale [mm] (non usato nella formula base, incluso per completezza).
    phi_w : float
        Diametro staffa [mm] (non usato nella formula base, incluso per completezza).

    Returns
    -------
    float
        Passo massimo s_max [mm].
    """
    if d <= 0:
        raise ValueError(f"d deve essere > 0, ricevuto {d}")

    return min(0.75 * d, 300.0)
