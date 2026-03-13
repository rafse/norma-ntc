"""Verifiche ponti in zona sismica — NTC18 §7.9.

Fattore di comportamento, analisi statica lineare, progettazione in
capacita' per pile e impalcato, armature di confinamento e dettagli
costruttivi per ponti stradali e ferroviari.

Unita':
- Forze: [kN]
- Momenti: [kNm]
- Accelerazioni: [m/s^2]
- Periodi: [s]
- Spostamenti: [m]
- Masse: [kN/g] = [t * g / g]  -- G_i in [kN], g in [m/s^2]
- Aree: [mm^2] per armature; [m^2] per sezioni strutturali
- Tensioni: [MPa]
- Coefficienti: [-]
"""

from __future__ import annotations

import math

import numpy as np

from pyntc.core.reference import ntc_ref


_G = 9.81  # accelerazione di gravita' [m/s^2]


# ══════════════════════════════════════════════════════════════════════════════
# §7.9.2.1 — FATTORE DI COMPORTAMENTO PER PONTI
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(
    article="7.9.2.1",
    formula="7.9.1",
    latex=r"q_i(v_k) = q_i - \left[\frac{v_k}{0{,}3} - 1\right](q_i - 1)",
)
def bridge_behavior_factor_vk(q_i: float, v_k: float) -> float:
    """Fattore di comportamento ridotto per compressione normalizzata elevata [-].

    NTC18 §7.9.2.1, Formula [7.9.1].
    Applicabile per 0,3 < v_k <= 0,6; per v_k <= 0,3 restituisce q_i invariato.

        q_i(v_k) = q_i - [v_k/0,3 - 1] * (q_i - 1)

    Parameters
    ----------
    q_i : float
        Fattore di comportamento applicabile per v_k <= 0,3 [-].
    v_k : float
        Sollecitazione di compressione normalizzata N_fd / A_k [-].
        Non puo' superare 0,6 (NTC18 §7.9.2.1).

    Returns
    -------
    float
        Fattore di comportamento ridotto q_i(v_k) [-].

    Raises
    ------
    ValueError
        Se q_i < 1, v_k < 0 oppure v_k > 0,6.
    """
    if q_i < 1.0:
        raise ValueError(f"q_i deve essere >= 1,0, ricevuto {q_i}")
    if v_k < 0.0:
        raise ValueError(f"v_k deve essere >= 0, ricevuto {v_k}")
    if v_k > 0.6:
        raise ValueError(
            f"v_k = {v_k} > 0,6: non ammesso dalla NTC18 §7.9.2.1"
        )
    if v_k <= 0.3:
        return q_i
    return q_i - (v_k / 0.3 - 1.0) * (q_i - 1.0)


@ntc_ref(
    article="7.9.2.1",
    formula="7.9.2",
    latex=r"K_R = \frac{2}{\bar{r}}, \quad q = q_i K_R \ge 1",
)
def bridge_regularity_factor(r_max: float, r_min: float) -> tuple[float, float]:
    """Fattore di regolarita' K_R e verifica di regolarita' del ponte.

    NTC18 §7.9.2.1, Formula [7.9.2].
    Il ponte e' regolare se r_bar = r_max / r_min < 2; altrimenti si riduce q
    tramite K_R = 2 / r_bar, con q = q_i * K_R >= 1.

    Parameters
    ----------
    r_max : float
        Massimo rapporto r_i = q_i * M_fd,i / M_Rd,i tra le pile [-].
    r_min : float
        Minimo rapporto r_i tra le pile [-].

    Returns
    -------
    tuple[float, float]
        - r_bar: rapporto r_max / r_min [-]
        - K_R: fattore di regolarita' (1.0 se regolare, 2/r_bar altrimenti) [-]

    Raises
    ------
    ValueError
        Se r_min <= 0 oppure r_max < r_min.
    """
    if r_min <= 0.0:
        raise ValueError(f"r_min deve essere > 0, ricevuto {r_min}")
    if r_max < r_min:
        raise ValueError(
            f"r_max ({r_max}) deve essere >= r_min ({r_min})"
        )
    r_bar = r_max / r_min
    if r_bar < 2.0:
        return r_bar, 1.0
    else:
        K_R = 2.0 / r_bar
        return r_bar, K_R


# ══════════════════════════════════════════════════════════════════════════════
# §7.9.4.1 — ANALISI STATICA LINEARE
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(
    article="7.9.4.1",
    formula="7.9.4",
    latex=r"T_1 = 2\pi\sqrt{M/K}",
)
def bridge_period_single_mass(M: float, K: float) -> float:
    """Periodo fondamentale del ponte — modello a massa singola [s].

    NTC18 §7.9.4.1, Formula [7.9.4].
    Applicabile per:
    - direzione longitudinale/trasversale, ponti a travata semplicemente appoggiata (caso a);
    - direzione longitudinale, ponti a travata continua (caso b).

        T_1 = 2*pi * sqrt(M / K)

    Parameters
    ----------
    M : float
        Massa concentrata in corrispondenza dell'impalcato [kN*s^2/m].
        Tipicamente M = G / g dove G e' il peso [kN] e g = 9,81 m/s^2.
    K : float
        Rigidezza laterale del modello [kN/m]:
        - pila singola nel caso (a);
        - rigidezza complessiva delle pile nel caso (b).

    Returns
    -------
    float
        Periodo fondamentale T_1 [s].

    Raises
    ------
    ValueError
        Se M <= 0 oppure K <= 0.
    """
    if M <= 0.0:
        raise ValueError(f"M deve essere > 0, ricevuto {M}")
    if K <= 0.0:
        raise ValueError(f"K deve essere > 0, ricevuto {K}")
    return 2.0 * math.pi * math.sqrt(M / K)


@ntc_ref(
    article="7.9.4.1",
    formula="7.9.6",
    latex=r"T_1 = 2\pi\sqrt{\frac{\sum G_i\,d_i^2}{g\,\sum G_i\,d_i}}",
)
def bridge_period_multispan(
    weights: np.ndarray,
    displacements: np.ndarray,
    g: float = _G,
) -> float:
    """Periodo fondamentale del ponte in direzione trasversale — formula approssimata [s].

    NTC18 §7.9.4.1, Formula [7.9.6].
    Applicabile per la direzione trasversale (caso c):

        T_1 = 2*pi * sqrt( sum(G_i * d_i^2) / (g * sum(G_i * d_i)) )

    Parameters
    ----------
    weights : np.ndarray
        Pesi delle masse concentrate G_i [kN].
    displacements : np.ndarray
        Spostamenti dei gradi di liberta' d_i [m] sotto sistema di forze
        statiche trasversali f_i = G_i (analisi di forze statiche unitarie).
    g : float
        Accelerazione di gravita' [m/s^2], default 9,81.

    Returns
    -------
    float
        Periodo fondamentale T_1 [s].

    Raises
    ------
    ValueError
        Se weights e displacements hanno dimensioni diverse, o se la somma
        dei contributi e' nulla.
    """
    weights = np.asarray(weights, dtype=float)
    displacements = np.asarray(displacements, dtype=float)
    if weights.shape != displacements.shape:
        raise ValueError(
            f"weights e displacements devono avere la stessa dimensione: "
            f"{weights.shape} != {displacements.shape}"
        )
    num = float(np.sum(weights * displacements**2))
    den = g * float(np.sum(weights * displacements))
    if den == 0.0:
        raise ValueError(
            "sum(G_i * d_i) = 0: impossibile calcolare il periodo"
        )
    return 2.0 * math.pi * math.sqrt(num / den)


@ntc_ref(
    article="7.9.4.1",
    formula="7.9.5",
    latex=r"F_i = \frac{4\pi^2\,S_d(T_i)}{T_i^2\,g^2}\,d_i\,G_i",
)
def bridge_seismic_forces_multispan(
    S_d_T1: float,
    T_1: float,
    weights: np.ndarray,
    displacements: np.ndarray,
    g: float = _G,
) -> np.ndarray:
    """Forze sismiche equivalenti su ponti a travata continua — direzione trasversale [kN].

    NTC18 §7.9.4.1, Formula [7.9.5].
    Applicabile per il caso (c) — analisi statica lineare in direzione trasversale:

        F_i = 4*pi^2 * S_d(T_i) / (T_i^2 * g^2) * d_i * G_i

    Parameters
    ----------
    S_d_T1 : float
        Ordinata dello spettro di progetto al periodo T_1 [m/s^2].
    T_1 : float
        Periodo fondamentale del ponte in direzione trasversale [s].
    weights : np.ndarray
        Pesi G_i delle masse concentrate [kN].
    displacements : np.ndarray
        Spostamenti d_i [m] sotto sistema di forze statiche f_i = G_i.
    g : float
        Accelerazione di gravita' [m/s^2], default 9,81.

    Returns
    -------
    np.ndarray
        Forze sismiche F_i [kN].

    Raises
    ------
    ValueError
        Se weights e displacements hanno dimensioni diverse o T_1 <= 0.
    """
    weights = np.asarray(weights, dtype=float)
    displacements = np.asarray(displacements, dtype=float)
    if weights.shape != displacements.shape:
        raise ValueError(
            f"weights e displacements devono avere la stessa dimensione: "
            f"{weights.shape} != {displacements.shape}"
        )
    if T_1 <= 0.0:
        raise ValueError(f"T_1 deve essere > 0, ricevuto {T_1}")
    coeff = 4.0 * math.pi**2 * S_d_T1 / (T_1**2 * g**2)
    return coeff * displacements * weights


# ══════════════════════════════════════════════════════════════════════════════
# §7.9.5 — FATTORE DI SOVRARESISTENZA (CAPACITY DESIGN)
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(
    article="7.9.5",
    formula="7.9.7",
    latex=r"\gamma_{id} = 0{,}7 + 0{,}2\,q \ge 1",
)
def bridge_overstrength_factor(q: float, v_k: float = 0.0) -> float:
    """Fattore di sovraresistenza gamma_id per progettazione in capacita' [-].

    NTC18 §7.9.5, Formula [7.9.7]:
        gamma_id = 0,7 + 0,2*q >= 1

    Per sezioni in c.a. con v_k > 0,1, il fattore e' moltiplicato per
    [1 + 2*(v_k - 0,1)^2].

    Parameters
    ----------
    q : float
        Fattore di comportamento utilizzato nel calcolo [-].
    v_k : float
        Sollecitazione di compressione normalizzata N_fd / A_k [-], default 0.
        Se v_k > 0,1 per sezioni in c.a. si applica il moltiplicatore.

    Returns
    -------
    float
        Fattore di sovraresistenza gamma_id [-].

    Raises
    ------
    ValueError
        Se q < 1.
    """
    if q < 1.0:
        raise ValueError(f"q deve essere >= 1, ricevuto {q}")
    gamma = 0.7 + 0.2 * q
    gamma = max(gamma, 1.0)
    if v_k > 0.1:
        gamma *= 1.0 + 2.0 * (v_k - 0.1) ** 2
    return gamma


# ══════════════════════════════════════════════════════════════════════════════
# §7.9.5.1.1 — VERIFICHE DI RESISTENZA PILE: TAGLIO IN CAPACITA'
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(
    article="7.9.5.1.1",
    formula="7.9.11",
    latex=r"1 \le \gamma_{bd} = 2{,}25 - q\,(V_E/V_{prc}) \le 1{,}25",
)
def bridge_pier_shear_overstrength(
    q: float, V_E: float, V_prc: float
) -> float:
    """Fattore di amplificazione gamma_bd per taglio pila in progettazione capacita' [-].

    NTC18 §7.9.5.1.1, Formula [7.9.11]:
        1,00 <= gamma_bd = 2,25 - q*(V_E/V_prc) <= 1,25

    Parameters
    ----------
    q : float
        Fattore di comportamento utilizzato nel calcolo [-].
    V_E : float
        Taglio derivante dall'analisi globale [kN].
    V_prc : float
        Taglio di equilibrio con le capacita' flessionali di estremita'
        (= (M_lpec + M_lprc) / I_p) [kN].

    Returns
    -------
    float
        Fattore di amplificazione gamma_bd [-], clampato in [1,00; 1,25].

    Raises
    ------
    ValueError
        Se q < 1 o V_prc <= 0.
    """
    if q < 1.0:
        raise ValueError(f"q deve essere >= 1, ricevuto {q}")
    if V_prc <= 0.0:
        raise ValueError(f"V_prc deve essere > 0, ricevuto {V_prc}")
    gamma_bd = 2.25 - q * (V_E / V_prc)
    return max(1.0, min(gamma_bd, 1.25))


@ntc_ref(
    article="7.9.5.1.1",
    formula="7.9.10b",
    latex=r"V_{prc} = \frac{M_{lpec} + M_{lprc}}{l_p}",
)
def bridge_pier_capacity_shear(
    M_lpec: float, M_lprc: float, l_p: float
) -> float:
    """Taglio di equilibrio con le capacita' flessionali di estremita' pila [kN].

    NTC18 §7.9.5.1.1, Formula [7.9.10b]:
        V_prc = (M_lpec + M_lprc) / l_p

    Parameters
    ----------
    M_lpec : float
        Momento resistente della sezione di estremita' superiore (testa) [kNm].
    M_lprc : float
        Momento resistente della sezione di estremita' inferiore (base) [kNm].
    l_p : float
        Lunghezza della pila tra le due sezioni di estremita' [m].
        Per pila incastrata solo alla base, e' la distanza tra la sezione
        di incastro e la sezione di momento nullo.

    Returns
    -------
    float
        Taglio V_prc [kN].

    Raises
    ------
    ValueError
        Se l_p <= 0.
    """
    if l_p <= 0.0:
        raise ValueError(f"l_p deve essere > 0, ricevuto {l_p}")
    return (M_lpec + M_lprc) / l_p


@ntc_ref(
    article="7.9.5.1.1",
    formula="7.9.10a",
    latex=r"V_{Ed} = \gamma_{bd}\,V_{prc}",
)
def bridge_pier_design_shear(gamma_bd: float, V_prc: float) -> float:
    """Domanda di taglio amplificata per progettazione in capacita' della pila [kN].

    NTC18 §7.9.5.1.1, Formula [7.9.10a]:
        V_Ed = gamma_bd * V_prc

    Parameters
    ----------
    gamma_bd : float
        Fattore di amplificazione (da bridge_pier_shear_overstrength) [-].
    V_prc : float
        Taglio di equilibrio con le capacita' flessionali (da
        bridge_pier_capacity_shear) [kN].

    Returns
    -------
    float
        Domanda di taglio V_Ed [kN].

    Raises
    ------
    ValueError
        Se gamma_bd < 1 o V_prc <= 0.
    """
    if gamma_bd < 1.0:
        raise ValueError(f"gamma_bd deve essere >= 1, ricevuto {gamma_bd}")
    if V_prc <= 0.0:
        raise ValueError(f"V_prc deve essere > 0, ricevuto {V_prc}")
    return gamma_bd * V_prc


# ══════════════════════════════════════════════════════════════════════════════
# §7.9.5.2.1 — VERIFICHE DI RESISTENZA IMPALCATO IN DIREZIONE TRASVERSALE
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(
    article="7.9.5.2.1",
    formula="7.9.12",
    latex=r"V_{Ed} = V_{E,i}\,\frac{\gamma_{bd}\,M_{lprc,i}}{M_{lprc,i}} \le V_{E,i}\,q",
)
def bridge_deck_capacity_shear(
    V_E_i: float,
    gamma_bd: float,
    M_lprc_i: float,
    M_Rd_base: float,
    q: float,
) -> tuple[float, float]:
    """Taglio di progetto per l'impalcato in direzione trasversale [kN].

    NTC18 §7.9.5.2.1, Formula [7.9.12]:
        V_Ed = V_E,i * (gamma_bd * M_lprc,i / M_lprc,i) <= V_E,i * q

    Nota: nella formula normativa il termine M_lprc,i al numeratore e
    denominatore e' il momento flettente analisi vs momento resistente —
    nella pratica si usa gamma_bd come amplificatore diretto moltiplicato
    per V_E,i, con il limite superiore V_E,i * q.

    Parameters
    ----------
    V_E_i : float
        Taglio in sommita' pila i dall'analisi [kN].
    gamma_bd : float
        Fattore di amplificazione da Formula 7.9.11 (adimensionale).
    M_lprc_i : float
        Momento resistente effettivo alla base della pila i [kNm].
    M_Rd_base : float
        Momento resistente di riferimento (denominatore) alla base [kNm].
        In generale coincide con M_lprc_i; puo' differire se si usa il
        momento di prima plasticizzazione.
    q : float
        Fattore di comportamento (adimensionale).

    Returns
    -------
    tuple[float, float]
        (V_Ed, V_Ed_max): taglio di progetto e limite superiore [kN].

    Raises
    ------
    ValueError
        Se V_E_i < 0, M_Rd_base <= 0 o q < 1.
    """
    if V_E_i < 0.0:
        raise ValueError(f"V_E_i deve essere >= 0, ricevuto {V_E_i}")
    if M_Rd_base <= 0.0:
        raise ValueError(f"M_Rd_base deve essere > 0, ricevuto {M_Rd_base}")
    if q < 1.0:
        raise ValueError(f"q deve essere >= 1, ricevuto {q}")
    V_Ed_raw = V_E_i * gamma_bd * M_lprc_i / M_Rd_base
    V_Ed_max = V_E_i * q
    V_Ed = min(V_Ed_raw, V_Ed_max)
    return V_Ed, V_Ed_max


# ══════════════════════════════════════════════════════════════════════════════
# §7.9.5.3.3 — DISPOSITIVI DI FINE CORSA
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(
    article="7.9.5.3.3",
    latex=r"F_{fc} = \alpha \cdot Q, \quad \alpha = 1{,}5\,S\,a_0/g",
)
def bridge_end_stop_force(S: float, a_0: float, Q: float, g: float = _G) -> float:
    """Forza di dimensionamento dei dispositivi di fine corsa [kN].

    NTC18 §7.9.5.3.3:
        alpha = 1,5 * S * a_0 / g
        F_fc = alpha * Q

    In mancanza di verifica analitica dinamica, i dispositivi di fine corsa
    vengono dimensionati per una forza F_fc = alpha * Q, dove alpha e'
    l'accelerazione normalizzata di progetto valutata allo SLC.

    Parameters
    ----------
    S : float
        Coefficiente di amplificazione del sito (S = S_s * S_t) [-].
    a_0 : float
        Accelerazione orizzontale massima su sito rigido allo SLC [m/s^2].
    Q : float
        Peso della parte di impalcato collegata al dispositivo [kN].
        Nel caso di due parti di impalcato collegate tra loro, si usa il
        minore dei due pesi.
    g : float
        Accelerazione di gravita' [m/s^2], default 9,81.

    Returns
    -------
    float
        Forza di dimensionamento F_fc [kN].

    Raises
    ------
    ValueError
        Se Q < 0, a_0 < 0 o g <= 0.
    """
    if Q < 0.0:
        raise ValueError(f"Q deve essere >= 0, ricevuto {Q}")
    if a_0 < 0.0:
        raise ValueError(f"a_0 deve essere >= 0, ricevuto {a_0}")
    if g <= 0.0:
        raise ValueError(f"g deve essere > 0, ricevuto {g}")
    alpha = 1.5 * S * a_0 / g
    return alpha * Q


# ══════════════════════════════════════════════════════════════════════════════
# §7.9.5.3.4 — ZONE DI SOVRAPPOSIZIONE
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(
    article="7.9.5.3.4",
    latex=r"l_{ov} = d_{rel} + 400\,\text{mm}",
)
def bridge_overlap_length(d_rel: float) -> float:
    """Lunghezza minima della zona di sovrapposizione (appoggio) [m].

    NTC18 §7.9.5.3.4:
        l_ov = d_rel + 0,400 m

    La lunghezza minima e' ottenuta aggiungendo allo spostamento relativo
    tra le parti lo spazio minimo di 400 mm per l'apparecchio di appoggio.

    Parameters
    ----------
    d_rel : float
        Spostamento relativo tra le parti (valutato secondo §7.2.2) [m].

    Returns
    -------
    float
        Lunghezza minima di sovrapposizione l_ov [m].

    Raises
    ------
    ValueError
        Se d_rel < 0.
    """
    if d_rel < 0.0:
        raise ValueError(f"d_rel deve essere >= 0, ricevuto {d_rel}")
    return d_rel + 0.400


# ══════════════════════════════════════════════════════════════════════════════
# §7.9.6.1.2 — ARMATURE DI CONFINAMENTO NUCLEO IN C.A.
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(
    article="7.9.6.1.2",
    formula="7.9.16",
    latex=(
        r"\omega_{w,req} = \frac{A_{wc}}{A_{ec}}\,\lambda\,v_k "
        r"+ 0{,}13\,\frac{f_{sd}}{f_{od}}\,(\rho_{L1} - 0{,}01)"
    ),
)
def bridge_confinement_omega_req(
    A_wc: float,
    A_ec: float,
    v_k: float,
    lambda_cd: float,
    f_sd: float,
    f_od: float,
    rho_L1: float,
) -> float:
    """Percentuale meccanica richiesta di armatura di confinamento omega_w,req [-].

    NTC18 §7.9.6.1.2, Formula [7.9.16]:
        omega_w,req = (A_wc/A_ec)*lambda*v_k + 0,13*(f_sd/f_od)*(rho_L1 - 0,01)

    Parameters
    ----------
    A_wc : float
        Area totale di calcestruzzo della sezione [m^2].
    A_ec : float
        Area del nucleo confinato della sezione [m^2].
    v_k : float
        Sollecitazione di compressione normalizzata [-].
    lambda_cd : float
        Coefficiente lambda: 0,37 per CD"A", 0,28 per CD"B".
    f_sd : float
        Tensione di snervamento di progetto dell'acciaio delle staffe [MPa].
    f_od : float
        Resistenza di progetto a compressione del calcestruzzo [MPa].
    rho_L1 : float
        Percentuale geometrica di armatura longitudinale [-].

    Returns
    -------
    float
        Percentuale meccanica richiesta omega_w,req [-].

    Raises
    ------
    ValueError
        Se A_ec <= 0, f_od <= 0 o lambda_cd non e' 0.28 o 0.37.
    """
    if A_ec <= 0.0:
        raise ValueError(f"A_ec deve essere > 0, ricevuto {A_ec}")
    if f_od <= 0.0:
        raise ValueError(f"f_od deve essere > 0, ricevuto {f_od}")
    if lambda_cd not in (0.28, 0.37):
        raise ValueError(
            f"lambda_cd deve essere 0.37 (CD'A') o 0.28 (CD'B'), ricevuto {lambda_cd}"
        )
    return (A_wc / A_ec) * lambda_cd * v_k + 0.13 * (f_sd / f_od) * (rho_L1 - 0.01)


@ntc_ref(
    article="7.9.6.1.2",
    formula="7.9.15",
    latex=r"\omega_{wd,t} \ge \max(\omega_{w,req};\;0{,}67\,\omega_{w,min})",
)
def bridge_confinement_check_rectangular(
    omega_wd_t: float,
    omega_w_req: float,
    ductility_class: str = "B",
) -> tuple[bool, float]:
    """Verifica percentuale meccanica confinamento — staffe rettangolari.

    NTC18 §7.9.6.1.2, Formula [7.9.15]:
        omega_wd,t >= max(omega_w,req;  0,67 * omega_w,min)

    omega_w,min = 0,18 per CD"A"; 0,12 per CD"B".

    Parameters
    ----------
    omega_wd_t : float
        Percentuale meccanica di armatura trasversale effettivamente
        prevista (da Formula [7.9.18]) [-].
    omega_w_req : float
        Percentuale meccanica richiesta (da Formula [7.9.16]) [-].
    ductility_class : str
        Classe di duttilita': "A" o "B" (default "B").

    Returns
    -------
    tuple[bool, float]
        - satisfied: True se la verifica e' soddisfatta.
        - omega_min_demand: valore minimo richiesto max(omega_w_req, 0,67*omega_w,min) [-].

    Raises
    ------
    ValueError
        Se ductility_class non e' "A" o "B".
    """
    _omega_min = {"A": 0.18, "B": 0.12}
    if ductility_class not in _omega_min:
        raise ValueError(
            f"ductility_class deve essere 'A' o 'B', ricevuto '{ductility_class}'"
        )
    omega_w_min = _omega_min[ductility_class]
    demand = max(omega_w_req, 0.67 * omega_w_min)
    return omega_wd_t >= demand, demand


@ntc_ref(
    article="7.9.6.1.2",
    formula="7.9.17",
    latex=r"\omega_{wd,c} \ge \max(1{,}4\,\omega_{w,req};\;\omega_{w,min})",
)
def bridge_confinement_check_circular(
    omega_wd_c: float,
    omega_w_req: float,
    ductility_class: str = "B",
) -> tuple[bool, float]:
    """Verifica percentuale meccanica confinamento — staffe circolari.

    NTC18 §7.9.6.1.2, Formula [7.9.17]:
        omega_wd,c >= max(1,4 * omega_w,req;  omega_w,min)

    omega_w,min = 0,18 per CD"A"; 0,12 per CD"B".

    Parameters
    ----------
    omega_wd_c : float
        Percentuale meccanica di armatura circolare effettiva
        (da Formula [7.9.19]) [-].
    omega_w_req : float
        Percentuale meccanica richiesta (da Formula [7.9.16]) [-].
    ductility_class : str
        Classe di duttilita': "A" o "B" (default "B").

    Returns
    -------
    tuple[bool, float]
        - satisfied: True se la verifica e' soddisfatta.
        - omega_min_demand: valore minimo richiesto max(1,4*omega_w_req, omega_w_min) [-].

    Raises
    ------
    ValueError
        Se ductility_class non e' "A" o "B".
    """
    _omega_min = {"A": 0.18, "B": 0.12}
    if ductility_class not in _omega_min:
        raise ValueError(
            f"ductility_class deve essere 'A' o 'B', ricevuto '{ductility_class}'"
        )
    omega_w_min = _omega_min[ductility_class]
    demand = max(1.4 * omega_w_req, omega_w_min)
    return omega_wd_c >= demand, demand


@ntc_ref(
    article="7.9.6.1.2",
    formula="7.9.18",
    latex=r"\omega_{wd,t} = \frac{A_{wc}}{s\,b}\,\frac{f_{sd}}{f_{od}}",
)
def bridge_confinement_omega_rectangular(
    A_wc: float,
    s: float,
    b: float,
    f_sd: float,
    f_od: float,
) -> float:
    """Percentuale meccanica di confinamento per staffe rettangolari omega_wd,t [-].

    NTC18 §7.9.6.1.2, Formula [7.9.18]:
        omega_wd,t = (A_wc / (s * b)) * (f_sd / f_od)

    Parameters
    ----------
    A_wc : float
        Area complessiva dei bracci delle staffe chiuse e dei tiranti
        in una direzione [mm^2].
    s : float
        Interasse verticale delle armature di confinamento S_t [mm].
    b : float
        Dimensione del nucleo confinato di calcestruzzo nel piano orizzontale
        in direzione ortogonale a quella dei bracci delle staffe [mm].
    f_sd : float
        Tensione di snervamento di progetto dell'acciaio delle staffe [MPa].
    f_od : float
        Resistenza di progetto a compressione del calcestruzzo [MPa].

    Returns
    -------
    float
        Percentuale meccanica omega_wd,t [-].

    Raises
    ------
    ValueError
        Se s <= 0, b <= 0 o f_od <= 0.
    """
    if s <= 0.0:
        raise ValueError(f"s deve essere > 0, ricevuto {s}")
    if b <= 0.0:
        raise ValueError(f"b deve essere > 0, ricevuto {b}")
    if f_od <= 0.0:
        raise ValueError(f"f_od deve essere > 0, ricevuto {f_od}")
    return (A_wc / (s * b)) * (f_sd / f_od)


@ntc_ref(
    article="7.9.6.1.2",
    formula="7.9.19",
    latex=r"\omega_{wd,c} = \frac{4\,A_{ep}\,f_{yd}}{D_{sp}\,s\,f_{el}}",
)
def bridge_confinement_omega_circular(
    A_ep: float,
    D_sp: float,
    s: float,
    f_yd: float,
    f_el: float,
) -> float:
    """Percentuale meccanica di confinamento per staffe circolari omega_wd,c [-].

    NTC18 §7.9.6.1.2, Formula [7.9.19]:
        omega_wd,c = 4 * A_ep * f_yd / (D_sp * s * f_el)

    Parameters
    ----------
    A_ep : float
        Area della sezione delle barre circonferenziali [mm^2].
    D_sp : float
        Diametro della circonferenza delle staffe [mm].
    s : float
        Interasse verticale delle armature di confinamento S_L [mm].
    f_yd : float
        Tensione di snervamento di progetto delle staffe [MPa].
    f_el : float
        Resistenza di progetto a compressione del calcestruzzo [MPa].

    Returns
    -------
    float
        Percentuale meccanica omega_wd,c [-].

    Raises
    ------
    ValueError
        Se D_sp <= 0, s <= 0 o f_el <= 0.
    """
    if D_sp <= 0.0:
        raise ValueError(f"D_sp deve essere > 0, ricevuto {D_sp}")
    if s <= 0.0:
        raise ValueError(f"s deve essere > 0, ricevuto {s}")
    if f_el <= 0.0:
        raise ValueError(f"f_el deve essere > 0, ricevuto {f_el}")
    return 4.0 * A_ep * f_yd / (D_sp * s * f_el)


# ══════════════════════════════════════════════════════════════════════════════
# §7.9.6.1.2 — PASSO ARMATURE CONFINAMENTO
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(
    article="7.9.6.1.2",
    formula="7.9.20",
    latex=r"S_L \le \min(6\,d_{SL};\;1{,}5\,b^*)",
)
def bridge_confinement_spacing_vertical(
    d_SL: float, b_star: float
) -> float:
    """Passo massimo armature di confinamento in direzione verticale [mm].

    NTC18 §7.9.6.1.2, Formula [7.9.20]:
        S_L <= min(6 * d_SL; 1,5 * b*)

    Parameters
    ----------
    d_SL : float
        Diametro delle armature longitudinali [mm].
    b_star : float
        Dimensione minore del nucleo confinato di calcestruzzo [mm].

    Returns
    -------
    float
        Passo massimo S_L [mm].

    Raises
    ------
    ValueError
        Se d_SL <= 0 o b_star <= 0.
    """
    if d_SL <= 0.0:
        raise ValueError(f"d_SL deve essere > 0, ricevuto {d_SL}")
    if b_star <= 0.0:
        raise ValueError(f"b_star deve essere > 0, ricevuto {b_star}")
    return min(6.0 * d_SL, 1.5 * b_star)


@ntc_ref(
    article="7.9.6.1.2",
    formula="7.9.21",
    latex=r"S_L \le \min\!\left(\tfrac{1}{3}\,b^*;\;200\,\text{mm}\right)",
)
def bridge_confinement_spacing_transverse(b_star: float) -> float:
    """Passo massimo armature di confinamento in direzione trasversale [mm].

    NTC18 §7.9.6.1.2, Formula [7.9.21]:
        S_L <= min(b*/3; 200 mm)

    Parameters
    ----------
    b_star : float
        Dimensione minore del nucleo confinato di calcestruzzo [mm].

    Returns
    -------
    float
        Passo massimo trasversale S_L [mm].

    Raises
    ------
    ValueError
        Se b_star <= 0.
    """
    if b_star <= 0.0:
        raise ValueError(f"b_star deve essere > 0, ricevuto {b_star}")
    return min(b_star / 3.0, 200.0)


@ntc_ref(
    article="7.9.6.1.2",
    formula="7.9.22",
    latex=r"S_L \le 6\,d_{BL}",
)
def bridge_tie_spacing_longitudinal(d_BL: float) -> float:
    """Passo massimo barre longitudinali per contrastare instabilita' [mm].

    NTC18 §7.9.6.1.2, Formula [7.9.22]:
        S_L <= 6 * d_BL

    Parameters
    ----------
    d_BL : float
        Diametro delle barre longitudinali compresse [mm].

    Returns
    -------
    float
        Passo massimo S_L [mm].

    Raises
    ------
    ValueError
        Se d_BL <= 0.
    """
    if d_BL <= 0.0:
        raise ValueError(f"d_BL deve essere > 0, ricevuto {d_BL}")
    return 6.0 * d_BL
