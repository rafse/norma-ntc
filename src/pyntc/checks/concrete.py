"""Verifiche calcestruzzo armato — NTC18 §4.1.

Resistenze di progetto dei materiali, limiti di deformazione,
verifiche SLE (tensioni) e SLU (taglio, torsione, pressoflessione deviata).

Unita':
- Resistenze e tensioni: [MPa]
- Dimensioni: [mm]
- Aree: [mm^2]
- Forze: [N]
- Momenti torcenti: [N*mm]
- Deformazioni: adimensionali (rapporto, non per mille)
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
