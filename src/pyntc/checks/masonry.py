"""Costruzioni di muratura — NTC18 §4.5.

Coefficienti parziali, resistenze di progetto, snellezza, fattori di
riduzione, verifiche semplificate per muratura ordinaria.

Unita':
- Tensioni/Resistenze: [N/mm^2] = [MPa]
- Forze: [N]
- Lunghezze: [mm]
- Coefficienti: [-]
"""

from __future__ import annotations

from pyntc.core.reference import ntc_ref


# ══════════════════════════════════════════════════════════════════════════════
# §4.5.6.1 — RESISTENZE DI PROGETTO (Tab. 4.5.II)
# ══════════════════════════════════════════════════════════════════════════════

# Tab.4.5.II — Valori gamma_M
# Formato: (element_category, mortar_type) -> {execution_class: gamma_M}
_GAMMA_M_TABLE: dict[tuple[int, str], dict[int, float]] = {
    (1, "guaranteed"): {1: 2.0, 2: 2.5},
    (1, "prescribed"): {1: 2.2, 2: 2.7},
    # Categoria II: mortar_type e' irrilevante, ma mappiamo entrambi
    (2, "guaranteed"): {1: 2.5, 2: 3.0},
    (2, "prescribed"): {1: 2.5, 2: 3.0},
}


@ntc_ref(article="4.5.6.1", table="Tab.4.5.II", latex=r"\text{Tab.\,4.5.II}")
def masonry_partial_safety_factor(
    element_category: int, mortar_type: str, execution_class: int
) -> float:
    """Coefficiente parziale di sicurezza gamma_M per muratura [-].

    NTC18 §4.5.6.1, Tab. 4.5.II:
        Cat.I + malta garantita:   classe 1 → 2.0, classe 2 → 2.5
        Cat.I + malta prescritta:  classe 1 → 2.2, classe 2 → 2.7
        Cat.II (qualsiasi malta):  classe 1 → 2.5, classe 2 → 3.0

    Parameters
    ----------
    element_category : int
        Categoria degli elementi resistenti: 1 o 2.
    mortar_type : str
        Tipo di malta: "guaranteed" (prestazione garantita) o
        "prescribed" (composizione prescritta).
    execution_class : int
        Classe di esecuzione: 1 o 2.

    Returns
    -------
    float
        Coefficiente parziale gamma_M [-].
    """
    if element_category not in (1, 2):
        raise ValueError(
            f"element_category deve essere 1 o 2, ricevuto: {element_category}"
        )
    if mortar_type not in ("guaranteed", "prescribed"):
        raise ValueError(
            f"mortar_type deve essere 'guaranteed' o 'prescribed', "
            f"ricevuto: '{mortar_type}'"
        )
    if execution_class not in (1, 2):
        raise ValueError(
            f"execution_class deve essere 1 o 2, ricevuto: {execution_class}"
        )

    return _GAMMA_M_TABLE[(element_category, mortar_type)][execution_class]


@ntc_ref(article="4.5.6.1", formula="4.5.2", latex=r"f_d = \frac{f_k}{\gamma_M}")
def masonry_design_compressive_strength(
    f_k: float, gamma_M: float
) -> float:
    """Resistenza di progetto a compressione della muratura [N/mm^2].

    NTC18 §4.5.6.1, Formula [4.5.2]:
        f_d = f_k / gamma_M

    Parameters
    ----------
    f_k : float
        Resistenza caratteristica a compressione della muratura [N/mm^2].
    gamma_M : float
        Coefficiente parziale di sicurezza [-].

    Returns
    -------
    float
        f_d: resistenza di progetto a compressione [N/mm^2].
    """
    if f_k <= 0:
        raise ValueError("f_k deve essere > 0")
    if gamma_M <= 0:
        raise ValueError("gamma_M deve essere > 0")
    return f_k / gamma_M


@ntc_ref(article="4.5.6.1", formula="4.5.3", latex=r"f_{vd} = \frac{f_{vk}}{\gamma_M}")
def masonry_design_shear_strength(
    f_vk: float, gamma_M: float
) -> float:
    """Resistenza di progetto a taglio della muratura [N/mm^2].

    NTC18 §4.5.6.1, Formula [4.5.3]:
        f_vd = f_vk / gamma_M

    Parameters
    ----------
    f_vk : float
        Resistenza caratteristica a taglio della muratura [N/mm^2].
    gamma_M : float
        Coefficiente parziale di sicurezza [-].

    Returns
    -------
    float
        f_vd: resistenza di progetto a taglio [N/mm^2].
    """
    if f_vk <= 0:
        raise ValueError("f_vk deve essere > 0")
    if gamma_M <= 0:
        raise ValueError("gamma_M deve essere > 0")
    return f_vk / gamma_M


# ══════════════════════════════════════════════════════════════════════════════
# §4.5.4 — SNELLEZZA CONVENZIONALE
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(article="4.5.4", formula="4.5.1", latex=r"\lambda = \frac{h_0}{t}")
def masonry_slenderness(h_0: float, t: float) -> float:
    """Snellezza convenzionale della parete [-].

    NTC18 §4.5.4, Formula [4.5.1]:
        lambda = h_0 / t

    Il valore non deve risultare superiore a 20.

    Parameters
    ----------
    h_0 : float
        Lunghezza libera di inflessione della parete [mm].
    t : float
        Spessore della parete [mm].

    Returns
    -------
    float
        Snellezza convenzionale lambda [-].
    """
    if h_0 <= 0:
        raise ValueError("h_0 deve essere > 0")
    if t <= 0:
        raise ValueError("t deve essere > 0")

    lam = h_0 / t
    if lam > 20.0:
        raise ValueError(
            f"Snellezza lambda = {lam:.2f} supera il limite di 20 "
            f"previsto da NTC18 §4.5.4"
        )
    return lam


# ══════════════════════════════════════════════════════════════════════════════
# §4.5.6.2 — VERIFICHE SLU: FATTORI DI VINCOLO E RIDUZIONE
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(article="4.5.6.2", table="Tab.4.5.IV", latex=r"\rho = \begin{cases} 1 & h/a \le 0{,}5 \\ \frac{3}{2} - \frac{h}{a} & 0{,}5 < h/a \le 1 \\ \frac{1}{1+(h/a)^2} & h/a > 1 \end{cases}")
def masonry_lateral_restraint_factor(h: float, a: float) -> float:
    """Fattore laterale di vincolo rho (= q in [4.5.5]) [-].

    NTC18 §4.5.6.2, Tab. 4.5.IV:
        h/a <= 0.5:       rho = 1
        0.5 < h/a <= 1.0: rho = 3/2 - h/a
        h/a > 1.0:        rho = 1 / (1 + (h/a)^2)

    Parameters
    ----------
    h : float
        Altezza interna di piano [mm].
    a : float
        Interasse dei muri trasversali di irrigidimento [mm].

    Returns
    -------
    float
        Fattore laterale di vincolo rho [-].
    """
    if h <= 0:
        raise ValueError("h deve essere > 0")
    if a <= 0:
        raise ValueError("a deve essere > 0")

    ratio = h / a

    if ratio <= 0.5:
        return 1.0
    elif ratio <= 1.0:
        return 1.5 - ratio
    else:
        return 1.0 / (1.0 + ratio ** 2)


@ntc_ref(article="4.5.6.2", formula="4.5.5", latex=r"h_0 = \rho \cdot h")
def masonry_effective_height(rho: float, h: float) -> float:
    """Lunghezza libera d'inflessione della parete [mm].

    NTC18 §4.5.6.2, Formula [4.5.5]:
        h_0 = rho * h

    dove rho e' il fattore laterale di vincolo (Tab. 4.5.IV).

    Parameters
    ----------
    rho : float
        Fattore laterale di vincolo [-] (da Tab. 4.5.IV).
    h : float
        Altezza interna di piano [mm].

    Returns
    -------
    float
        h_0: lunghezza libera d'inflessione [mm].
    """
    if rho <= 0 or rho > 1:
        raise ValueError("rho deve essere 0 < rho <= 1")
    if h <= 0:
        raise ValueError("h deve essere > 0")
    return rho * h


@ntc_ref(article="4.5.6.2", formula="4.5.6", latex=r"m = \frac{6\,e}{t}")
def masonry_eccentricity_coefficient(e: float, t: float) -> float:
    """Coefficiente di eccentricita' m [-].

    NTC18 §4.5.6.2, Formula [4.5.6]:
        m = 6 * e / t

    Parameters
    ----------
    e : float
        Eccentricita' totale [mm]. Valore >= 0.
    t : float
        Spessore della parete [mm].

    Returns
    -------
    float
        Coefficiente di eccentricita' m [-].
    """
    if e < 0:
        raise ValueError("e deve essere >= 0")
    if t <= 0:
        raise ValueError("t deve essere > 0")
    return 6.0 * e / t


# Tab.4.5.III — Valori del coefficiente Phi
# Righe: lambda = [0, 5, 10, 15, 20]
# Colonne: m = [0, 0.5, 1.0, 1.5, 2.0]
# None indica combinazione non ammessa
_PHI_LAMBDA = [0, 5, 10, 15, 20]
_PHI_M = [0.0, 0.5, 1.0, 1.5, 2.0]
_PHI_TABLE: list[list[float | None]] = [
    [1.00, 0.74, 0.59, 0.44, 0.33],       # lambda = 0
    [0.97, 0.71, 0.55, 0.39, 0.27],       # lambda = 5
    [0.86, 0.61, 0.45, 0.27, 0.16],       # lambda = 10
    [0.69, 0.48, 0.32, 0.17, None],       # lambda = 15
    [0.53, 0.36, 0.23, None, None],        # lambda = 20
]


def _phi_value(i_lam: int, j_m: int) -> float | None:
    """Accede al valore Phi nella tabella, None se non ammesso."""
    if 0 <= i_lam < len(_PHI_LAMBDA) and 0 <= j_m < len(_PHI_M):
        return _PHI_TABLE[i_lam][j_m]
    return None


@ntc_ref(article="4.5.6.2", table="Tab.4.5.III", latex=r"\Phi = f(\lambda,\,m) \quad \text{Tab.\,4.5.III}")
def masonry_reduction_factor(lambda_: float, m: float) -> float:
    """Coefficiente di riduzione Phi della resistenza [-].

    NTC18 §4.5.6.2, Tab. 4.5.III — Interpolazione bilineare sui valori
    tabulati in funzione della snellezza lambda e del coefficiente di
    eccentricita' m.

    Parameters
    ----------
    lambda_ : float
        Snellezza convenzionale [-], 0 <= lambda <= 20.
    m : float
        Coefficiente di eccentricita' m = 6*e/t [-], m >= 0.

    Returns
    -------
    float
        Coefficiente di riduzione Phi [-].
    """
    if lambda_ < 0:
        raise ValueError("lambda_ deve essere >= 0")
    if lambda_ > 20:
        raise ValueError("lambda_ deve essere <= 20")
    if m < 0:
        raise ValueError("m deve essere >= 0")
    if m > 2.0:
        raise ValueError("m deve essere <= 2.0 (limite Tab.4.5.III)")

    # Trova gli indici di interpolazione per lambda
    i_lo = 0
    for i in range(len(_PHI_LAMBDA) - 1):
        if _PHI_LAMBDA[i + 1] > lambda_:
            break
        i_lo = i + 1
    # Se valore esatto sulla griglia, non serve interpolare oltre
    if _PHI_LAMBDA[i_lo] == lambda_:
        i_hi = i_lo
    else:
        i_hi = min(i_lo + 1, len(_PHI_LAMBDA) - 1)

    # Trova gli indici di interpolazione per m
    j_lo = 0
    for j in range(len(_PHI_M) - 1):
        if _PHI_M[j + 1] > m:
            break
        j_lo = j + 1
    if _PHI_M[j_lo] == m:
        j_hi = j_lo
    else:
        j_hi = min(j_lo + 1, len(_PHI_M) - 1)

    # Verifica che tutti e 4 gli angoli siano validi
    corners = [
        _phi_value(i_lo, j_lo),
        _phi_value(i_lo, j_hi),
        _phi_value(i_hi, j_lo),
        _phi_value(i_hi, j_hi),
    ]
    if any(c is None for c in corners):
        raise ValueError(
            f"Combinazione (lambda={lambda_}, m={m}) fuori dal dominio "
            f"ammesso dalla Tab.4.5.III"
        )

    # Interpolazione bilineare
    if i_lo == i_hi and j_lo == j_hi:
        # Punto esatto sulla griglia
        return corners[0]  # type: ignore[return-value]

    if i_lo == i_hi:
        # Solo interpolazione su m
        t_m = (m - _PHI_M[j_lo]) / (_PHI_M[j_hi] - _PHI_M[j_lo])
        return corners[0] * (1.0 - t_m) + corners[1] * t_m  # type: ignore[operator]

    if j_lo == j_hi:
        # Solo interpolazione su lambda
        t_lam = (lambda_ - _PHI_LAMBDA[i_lo]) / (
            _PHI_LAMBDA[i_hi] - _PHI_LAMBDA[i_lo]
        )
        return corners[0] * (1.0 - t_lam) + corners[2] * t_lam  # type: ignore[operator]

    # Interpolazione bilineare completa
    t_lam = (lambda_ - _PHI_LAMBDA[i_lo]) / (
        _PHI_LAMBDA[i_hi] - _PHI_LAMBDA[i_lo]
    )
    t_m = (m - _PHI_M[j_lo]) / (_PHI_M[j_hi] - _PHI_M[j_lo])

    phi = (
        corners[0] * (1.0 - t_lam) * (1.0 - t_m)
        + corners[2] * t_lam * (1.0 - t_m)
        + corners[1] * (1.0 - t_lam) * t_m
        + corners[3] * t_lam * t_m
    )
    return phi  # type: ignore[return-value]


# ══════════════════════════════════════════════════════════════════════════════
# §4.5.6.2 — RESISTENZA RIDOTTA
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(article="4.5.6.2", formula="4.5.4", latex=r"f_{d,\text{rid}} = \Phi \cdot f_d")
def masonry_reduced_strength(Phi: float, f_d: float) -> float:
    """Resistenza unitaria di progetto ridotta [N/mm^2].

    NTC18 §4.5.6.2, Formula [4.5.4]:
        f_d,rid = Phi * f_d

    Parameters
    ----------
    Phi : float
        Coefficiente di riduzione [-] (da Tab. 4.5.III).
    f_d : float
        Resistenza di progetto a compressione [N/mm^2].

    Returns
    -------
    float
        f_d,rid: resistenza ridotta [N/mm^2].
    """
    if Phi <= 0 or Phi > 1:
        raise ValueError("Phi deve essere 0 < Phi <= 1")
    if f_d <= 0:
        raise ValueError("f_d deve essere > 0")
    return Phi * f_d


# ══════════════════════════════════════════════════════════════════════════════
# §4.5.6.2 — ECCENTRICITÀ DEI CARICHI VERTICALI  [4.5.7]
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(
    article="4.5.6.2",
    formula="4.5.7",
    latex=(
        r"e_{s1} = \frac{N_1 d_1}{N_1 + \sum N_2};\quad"
        r"e_{s2} = \frac{\sum N_2 d_2}{N_1 + \sum N_2}"
    ),
)
def masonry_vertical_load_eccentricity(
    N1: float, d1: float, N2_sum: float, d2: float
) -> tuple[float, float]:
    """Eccentricità totali dei carichi verticali sulla parete [mm].

    NTC18 §4.5.6.2, Formula [4.5.7]:
        e_s1 = N1 * d1 / (N1 + ΣN2)
        e_s2 = ΣN2 * d2 / (N1 + ΣN2)

    Parameters
    ----------
    N1 : float
        Carico trasmesso dal muro sovrastante [N].
    d1 : float
        Eccentricità di N1 rispetto al piano medio del muro [mm].
    N2_sum : float
        Somma delle reazioni di appoggio dei solai soprastanti [N].
    d2 : float
        Eccentricità di N2 rispetto al piano medio del muro [mm].

    Returns
    -------
    tuple[float, float]
        (e_s1, e_s2): eccentricità [mm], possono essere positive o negative.
    """
    N_tot = N1 + N2_sum
    if N_tot == 0:
        raise ValueError("N1 + ΣN2 deve essere != 0")
    e_s1 = N1 * d1 / N_tot
    e_s2 = N2_sum * d2 / N_tot
    return e_s1, e_s2


# ══════════════════════════════════════════════════════════════════════════════
# §4.5.6.2 — ECCENTRICITÀ DA AZIONI ORIZZONTALI  [4.5.9]
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(article="4.5.6.2", formula="4.5.9", latex=r"e_s = M_s / N")
def masonry_horizontal_eccentricity(M_s: float, N: float) -> float:
    """Eccentricità da azioni orizzontali [mm].

    NTC18 §4.5.6.2, Formula [4.5.9]:
        e_s = M_s / N

    Parameters
    ----------
    M_s : float
        Massimo momento flettente dovuto alle azioni orizzontali [N·mm].
    N : float
        Sforzo normale nella sezione di verifica [N]. Deve essere != 0.

    Returns
    -------
    float
        e_s: eccentricità [mm].
    """
    if N == 0:
        raise ValueError("N deve essere != 0")
    return M_s / N


# ══════════════════════════════════════════════════════════════════════════════
# §4.5.6.2 — COMBINAZIONE ECCENTRICITÀ  [4.5.10]
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(
    article="4.5.6.2",
    formula="4.5.10",
    latex=r"e_1 = |e_x| + e_y;\quad e_2 = \frac{e_1}{2} + |e_y|",
)
def masonry_combined_eccentricity(e_x: float, e_y: float) -> tuple[float, float]:
    """Combinazione convenzionale delle eccentricità [mm].

    NTC18 §4.5.6.2, Formula [4.5.10]:
        e1 = |e_x| + e_y
        e2 = e1/2 + |e_y|

    e1 è adottato per le sezioni di estremità;
    e2 per la sezione a massimo momento.

    Parameters
    ----------
    e_x : float
        Eccentricità totale dei carichi verticali [mm].
    e_y : float
        Eccentricità da tolleranze e azioni orizzontali [mm].

    Returns
    -------
    tuple[float, float]
        (e1, e2): eccentricità di calcolo [mm].
    """
    e1 = abs(e_x) + e_y
    e2 = e1 / 2.0 + abs(e_y)
    return e1, e2


# ══════════════════════════════════════════════════════════════════════════════
# §4.5.6.2 — VERIFICA LIMITI ECCENTRICITÀ  [4.5.11]
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(
    article="4.5.6.2",
    formula="4.5.11",
    latex=r"e_1 \le 0{,}33\,t;\quad e_2 \le 0{,}33\,t",
)
def masonry_eccentricity_check(e1: float, e2: float, t: float) -> tuple[bool, float]:
    """Verifica dei limiti di eccentricità [-].

    NTC18 §4.5.6.2, Formula [4.5.11]:
        e1 <= 0.33 * t  e  e2 <= 0.33 * t

    Parameters
    ----------
    e1 : float
        Eccentricità alla sezione di estremità [mm].
    e2 : float
        Eccentricità alla sezione a massimo momento [mm].
    t : float
        Spessore della parete [mm].

    Returns
    -------
    tuple[bool, float]
        (verificata, ratio): verificata = True se entrambe le eccentricità
        rispettano il limite; ratio = max(e1, e2) / (0.33 * t).
    """
    if t <= 0:
        raise ValueError("t deve essere > 0")
    limit = 0.33 * t
    ratio = max(e1, e2) / limit
    return ratio <= 1.0, ratio


# ══════════════════════════════════════════════════════════════════════════════
# §4.5.6.4 — VERIFICA SEMPLIFICATA
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(article="4.5.6.4", formula="4.5.12", latex=r"\sigma = \frac{N}{0{,}65\,A} \le \frac{f_k}{\gamma_M}")
def masonry_simplified_check(
    N: float, A: float, f_k: float, gamma_M: float
) -> tuple[bool, float]:
    """Verifica semplificata per edifici semplici [-].

    NTC18 §4.5.6.4, Formula [4.5.12]:
        sigma = N / (0.65 * A) <= f_k / gamma_M

    Le unita' di N, A, f_k devono essere coerenti tra loro
    (es. N [N], A [mm^2], f_k [N/mm^2]).

    Parameters
    ----------
    N : float
        Carico verticale totale alla base del piano.
    A : float
        Area totale dei muri portanti allo stesso piano.
    f_k : float
        Resistenza caratteristica a compressione della muratura.
    gamma_M : float
        Coefficiente parziale di sicurezza [-].

    Returns
    -------
    tuple[bool, float]
        (verifica_superata, sigma):
        - verifica_superata: True se sigma <= f_k / gamma_M
        - sigma: tensione di compressione ridotta
    """
    if N < 0:
        raise ValueError("N deve essere >= 0")
    if A <= 0:
        raise ValueError("A deve essere > 0")
    if f_k <= 0:
        raise ValueError("f_k deve essere > 0")
    if gamma_M <= 0:
        raise ValueError("gamma_M deve essere > 0")

    sigma = N / (0.65 * A)
    f_d = f_k / gamma_M
    return sigma <= f_d, sigma
