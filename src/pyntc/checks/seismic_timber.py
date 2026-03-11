"""Verifiche legno in zona sismica — NTC18 §7.7.

Fattori di comportamento, connessioni duttili, limitazioni dimensionali
e verifiche di sovraresistenza per strutture di legno in zona sismica
(CD"A", CD"B", strutture non dissipative).

Unita':
- Forze: [kN]
- Dimensioni: [mm]
- Diametri connettori: [mm]
- Coefficienti: [-]
"""

from __future__ import annotations

from pyntc.core.reference import ntc_ref


# ══════════════════════════════════════════════════════════════════════════════
# §7.7.3 — FATTORI DI COMPORTAMENTO PER COSTRUZIONI DI LEGNO
# ══════════════════════════════════════════════════════════════════════════════

# Tab. 7.3.II (estratto per legno) — valori massimi del fattore q_v
# Chiave: tipologia strutturale
# Valore: {classe_duttilita: q_v_max}
_Q_TIMBER: dict[str, dict[str, float]] = {
    # Strutture a telaio leggero con pannelli incollati
    "light_frame_glued": {
        "A": 3.0,
        "B": 2.0,
    },
    # Strutture a portale iperstatico
    "portal_hyperstat": {
        "A": 4.0,
        "B": 2.5,
    },
    # Strutture a telaio leggero con pannelli inchiodati
    "light_frame_nailed": {
        "A": 5.0,
        "B": 3.0,
    },
    # Strutture reticolari
    "truss": {
        "A": 2.5,
        "B": 2.5,
    },
    # Strutture isostatiche
    "isostatic": {
        "A": 1.5,
        "B": 1.5,
    },
}

_VALID_DUCTILITY_CLASSES = {"A", "B", "ND"}


@ntc_ref(
    article="7.7.3",
    table="Tab.7.3.II",
    latex=r"q_v \le q_{v,\max} \;\text{(Tab.\,7.3.II)}",
)
def seismic_timber_behavior_factor(
    structural_type: str,
    ductility_class: str = "B",
    *,
    regular_in_height: bool = True,
) -> float:
    """Fattore di comportamento q per costruzioni di legno [-].

    NTC18 §7.7.3, Tab. 7.3.II.
    q = q_v * K_R, con K_R = 1.0 se regolare in altezza, 0.8 altrimenti.

    Parameters
    ----------
    structural_type : str
        Tipologia strutturale:
        'light_frame_glued', 'portal_hyperstat', 'light_frame_nailed',
        'truss', 'isostatic'.
    ductility_class : str
        Classe di duttilita': 'A', 'B', o 'ND' (non dissipativa, q=1.5).
    regular_in_height : bool
        True se la struttura e' regolare in altezza (K_R=1.0),
        False altrimenti (K_R=0.8).

    Returns
    -------
    float
        Valore del fattore di comportamento q [-].
    """
    if ductility_class == "ND":
        # Struttura non dissipativa: q <= 1.5
        return 1.5

    if ductility_class not in ("A", "B"):
        raise ValueError(
            f"Classe di duttilita' deve essere 'A', 'B' o 'ND', "
            f"ricevuto '{ductility_class}'"
        )
    if structural_type not in _Q_TIMBER:
        raise ValueError(
            f"Tipologia strutturale '{structural_type}' non riconosciuta. "
            f"Valori ammessi: {sorted(_Q_TIMBER.keys())}"
        )

    q_v_max = _Q_TIMBER[structural_type][ductility_class]
    K_R = 1.0 if regular_in_height else 0.8
    return q_v_max * K_R


# ══════════════════════════════════════════════════════════════════════════════
# §7.7.3 / §7.7.3.1 — REQUISITI DI DUTTILITA' DELLE ZONE DISSIPATIVE
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(
    article="7.7.3.1",
    latex=r"d \le 12\,\text{mm},\quad t \ge 10d \;\text{(caso a)}",
)
def seismic_timber_connector_ductility(
    connector_diameter: float,
    member_thickness: float,
    connection_type: str = "timber_timber",
) -> tuple[bool, str]:
    """Verifica dei requisiti di duttilita' del connettore in zona dissipativa.

    NTC18 §7.7.3.1 — Le zone dissipative con perni/chiodi devono rispettare:
    - caso a) legno-legno o legno-acciaio: d <= 12 mm, spessore >= 10d
    - caso b) pareti con telaio in legno: d <= 3.1 mm, spessore >= 4d

    Se lo spessore e' almeno 8d (caso a) o 3d (caso b) ma non raggiunge
    il limite pieno, la zona e' classificabile solo come CD"B".

    Parameters
    ----------
    connector_diameter : float
        Diametro del connettore (perno o chiodo) d [mm].
    member_thickness : float
        Spessore minimo della membratura lignea collegata t [mm].
    connection_type : str
        Tipo di collegamento: 'timber_timber' (o 'timber_steel') per caso a),
        'light_frame' per pareti con telaio leggero (caso b).

    Returns
    -------
    tuple[bool, str]
        - satisfied: True se i requisiti sono rispettati
        - ductility_class: 'A_B' (idoneo per CD"A" e CD"B"),
          'B_only' (solo CD"B"), o 'none' (non idoneo come zona dissipativa)
    """
    if connector_diameter <= 0:
        raise ValueError(
            f"Il diametro del connettore deve essere > 0, ricevuto {connector_diameter}"
        )
    if member_thickness <= 0:
        raise ValueError(
            f"Lo spessore della membratura deve essere > 0, ricevuto {member_thickness}"
        )

    valid_types = {"timber_timber", "timber_steel", "light_frame"}
    if connection_type not in valid_types:
        raise ValueError(
            f"Tipo di collegamento '{connection_type}' non riconosciuto. "
            f"Valori ammessi: {sorted(valid_types)}"
        )

    if connection_type in ("timber_timber", "timber_steel"):
        # Caso a): d <= 12 mm, spessore >= 10d per CD"A" e CD"B"
        d_limit = 12.0
        t_full = 10.0 * connector_diameter   # spessore per CD"A" e CD"B"
        t_partial = 8.0 * connector_diameter  # spessore min per CD"B" solo

        if connector_diameter > d_limit:
            return False, "none"
        if member_thickness >= t_full:
            return True, "A_B"
        if member_thickness >= t_partial:
            return True, "B_only"
        return False, "none"

    else:  # light_frame — caso b)
        # Caso b): d <= 3.1 mm, spessore >= 4d per CD"A" e CD"B"
        d_limit = 3.1
        t_full = 4.0 * connector_diameter    # spessore per CD"A" e CD"B"
        t_partial = 3.0 * connector_diameter  # spessore min per CD"B" solo

        if connector_diameter > d_limit:
            return False, "none"
        if member_thickness >= t_full:
            return True, "A_B"
        if member_thickness >= t_partial:
            return True, "B_only"
        return False, "none"


# ══════════════════════════════════════════════════════════════════════════════
# §7.7.1 — GERARCHIA DELLE RESISTENZE (CAPACITY DESIGN)
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(
    article="7.7.1",
    latex=r"R_{\text{non-diss}} \ge \gamma_{Rd} \cdot R_{\text{diss}}",
)
def seismic_timber_capacity_design(
    R_nondissipative: float,
    R_dissipative: float,
    ductility_class: str = "B",
    *,
    gamma_Rd: float | None = None,
) -> tuple[bool, float]:
    """Verifica di gerarchia delle resistenze (capacity design) per legno.

    NTC18 §7.7.1 — Le componenti non dissipative adiacenti alle zone dissipative
    devono avere una capacita' pari alla capacita' della zona dissipativa
    amplificata del fattore di sovraresistenza gamma_Rd (Tab. 7.2.1):
        R_nondiss >= gamma_Rd * R_diss

    I valori minimi di gamma_Rd sono:
    - CD"A": 1.3
    - CD"B": 1.1

    Parameters
    ----------
    R_nondissipative : float
        Resistenza della componente non dissipativa [kN o kNm].
    R_dissipative : float
        Resistenza della zona dissipativa [kN o kNm].
    ductility_class : str
        Classe di duttilita': 'A' o 'B'.
    gamma_Rd : float, optional
        Fattore di sovraresistenza. Se None, usa il valore minimo normativo
        (1.3 per CD"A", 1.1 per CD"B").

    Returns
    -------
    tuple[bool, float]
        - satisfied: True se la verifica e' soddisfatta
        - ratio: R_nondiss / (gamma_Rd * R_diss) [-]
    """
    if R_dissipative <= 0:
        raise ValueError(
            f"La resistenza dissipativa deve essere > 0, ricevuto {R_dissipative}"
        )
    if R_nondissipative < 0:
        raise ValueError(
            f"La resistenza non dissipativa deve essere >= 0, ricevuto {R_nondissipative}"
        )
    if ductility_class not in ("A", "B"):
        raise ValueError(
            f"Classe di duttilita' deve essere 'A' o 'B', ricevuto '{ductility_class}'"
        )

    # Valori minimi normativi di gamma_Rd
    gamma_Rd_min = 1.3 if ductility_class == "A" else 1.1

    if gamma_Rd is None:
        gamma_Rd_used = gamma_Rd_min
    else:
        if gamma_Rd < gamma_Rd_min:
            raise ValueError(
                f"gamma_Rd = {gamma_Rd} < {gamma_Rd_min} (minimo normativo per CD'{ductility_class}'). "
                "Valori inferiori devono essere giustificati con evidenze teorico-sperimentali."
            )
        gamma_Rd_used = gamma_Rd

    demand = gamma_Rd_used * R_dissipative
    ratio = R_nondissipative / demand
    return ratio >= 1.0, ratio


# ══════════════════════════════════════════════════════════════════════════════
# §7.7.6 — RESISTENZA DI CALCOLO CICLICA (degrado per deformazioni cicliche)
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(
    article="7.7.6",
    latex=r"X_{d,\text{sism}} = 0{,}80 \cdot X_d",
)
def seismic_timber_cyclic_design_strength(X_d: float) -> float:
    """Resistenza di calcolo ridotta per degrado ciclico [N/mm^2].

    NTC18 §7.7.6 — Per strutture dissipative (CD"A" o CD"B"), la resistenza
    del materiale deve essere ridotta del 20% per tenere conto del degrado
    dovuto alle deformazioni cicliche:
        X_d,sism = 0.80 * X_d

    Parameters
    ----------
    X_d : float
        Resistenza di calcolo statica [N/mm^2].

    Returns
    -------
    float
        Resistenza di calcolo ridotta per azioni cicliche [N/mm^2].
    """
    if X_d < 0:
        raise ValueError(
            f"La resistenza di calcolo X_d deve essere >= 0, ricevuto {X_d}"
        )
    return 0.80 * X_d


# ══════════════════════════════════════════════════════════════════════════════
# §7.7.6 — VERIFICA DI RESISTENZA TRAVE DISSIPATIVA (sovraresistenza taglio)
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(
    article="7.7.6",
    latex=r"\tau_d \le \frac{f_{v,d}}{1{,}3}",
)
def seismic_timber_carpentry_joint_shear(
    tau_d: float, f_v_d: float
) -> tuple[bool, float]:
    """Verifica a taglio dei giunti di carpenteria in zona sismica.

    NTC18 §7.7.6 — I giunti di carpenteria non presentano rischi di rottura
    fragile se la verifica per tensioni tangenziali (§4.4) e' soddisfatta con
    un ulteriore coefficiente parziale di sicurezza pari a 1.3:
        tau_d <= f_v,d / 1.3

    Parameters
    ----------
    tau_d : float
        Tensione tangenziale di progetto [N/mm^2].
    f_v_d : float
        Resistenza di progetto a taglio [N/mm^2].

    Returns
    -------
    tuple[bool, float]
        - satisfied: True se la verifica e' soddisfatta
        - ratio: tau_d / (f_v,d / 1.3) [-]
    """
    if f_v_d <= 0:
        raise ValueError(
            f"La resistenza a taglio f_v_d deve essere > 0, ricevuto {f_v_d}"
        )
    if tau_d < 0:
        raise ValueError(
            f"La tensione tangenziale tau_d deve essere >= 0, ricevuto {tau_d}"
        )
    f_v_d_reduced = f_v_d / 1.3
    ratio = tau_d / f_v_d_reduced
    return ratio <= 1.0, ratio


# ══════════════════════════════════════════════════════════════════════════════
# §7.7.2 — REQUISITI DI SPESSORE PER PANNELLI STRUTTURALI DI RIVESTIMENTO
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(
    article="7.7.2",
    latex=r"t \ge t_{\min} \;\text{(Tab.\,§7.7.2)}",
)
def seismic_timber_panel_thickness(
    panel_type: str,
    thickness: float,
    *,
    osb_paired: bool = False,
) -> tuple[bool, float]:
    """Verifica dello spessore minimo dei pannelli strutturali di rivestimento.

    NTC18 §7.7.2 — Per l'utilizzo nelle pareti di taglio e nei diaframmi
    orizzontali, i pannelli strutturali devono rispettare:
    - Pannelli di particelle (UNI EN 312): t_min = 13 mm
    - Compensato (UNI EN 636): t_min = 9 mm
    - OSB (UNI EN 300): t_min = 12 mm (a coppia) / 15 mm (singolo)

    Parameters
    ----------
    panel_type : str
        Tipo di pannello: 'particleboard', 'plywood', 'osb'.
    thickness : float
        Spessore del pannello [mm].
    osb_paired : bool
        Solo per OSB: True se disposti a coppia (t_min = 12 mm),
        False se singoli (t_min = 15 mm).

    Returns
    -------
    tuple[bool, float]
        - satisfied: True se lo spessore e' sufficiente
        - ratio: thickness / t_min [-]
    """
    _panel_min: dict[str, float] = {
        "particleboard": 13.0,
        "plywood": 9.0,
    }

    if panel_type not in ("particleboard", "plywood", "osb"):
        raise ValueError(
            f"Tipo di pannello '{panel_type}' non riconosciuto. "
            "Valori ammessi: 'particleboard', 'plywood', 'osb'."
        )
    if thickness <= 0:
        raise ValueError(
            f"Lo spessore deve essere > 0, ricevuto {thickness}"
        )

    if panel_type == "osb":
        t_min = 12.0 if osb_paired else 15.0
    else:
        t_min = _panel_min[panel_type]

    ratio = thickness / t_min
    return ratio >= 1.0, ratio


# ══════════════════════════════════════════════════════════════════════════════
# §7.7.7.1 — LIMITAZIONE DIAMETRO BULLONI IN ZONA DISSIPATIVA
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(
    article="7.7.7.1",
    latex=r"d_{\text{bolt}} \le 16\,\text{mm} \;\text{(collegamento legno-legno/acciaio)}",
)
def seismic_timber_bolt_diameter_check(
    bolt_diameter: float,
    *,
    is_closure_element: bool = False,
) -> tuple[bool, float]:
    """Verifica della limitazione del diametro dei bulloni in zona dissipativa.

    NTC18 §7.7.7.1 — Perni e bulloni di diametro d > 16 mm non devono essere
    utilizzati nei collegamenti legno-legno e legno-acciaio in zona dissipativa,
    tranne quando utilizzati come elementi di chiusura che non influenzano
    la resistenza a taglio.

    Parameters
    ----------
    bolt_diameter : float
        Diametro del bullone o del perno d [mm].
    is_closure_element : bool
        True se il bullone e' un elemento di chiusura (non influisce
        sulla resistenza a taglio); in tal caso la limitazione non si applica.

    Returns
    -------
    tuple[bool, float]
        - satisfied: True se la verifica e' soddisfatta
        - ratio: bolt_diameter / 16.0 [-]
    """
    if bolt_diameter <= 0:
        raise ValueError(
            f"Il diametro del bullone deve essere > 0, ricevuto {bolt_diameter}"
        )

    d_limit = 16.0
    ratio = bolt_diameter / d_limit

    if is_closure_element:
        # Elementi di chiusura: nessuna limitazione
        return True, ratio

    return bolt_diameter <= d_limit, ratio


# ══════════════════════════════════════════════════════════════════════════════
# §7.7.7.2 — LIMITAZIONE h/b TRAVI IMPALCATO (zona sismica)
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(
    article="7.7.7.2",
    latex=r"\frac{h}{b} \le 4 \;\text{(trave senza controventi trasversali)}",
)
def seismic_timber_beam_hb_ratio(
    h: float,
    b: float,
) -> tuple[bool, float]:
    """Verifica del rapporto altezza/spessore delle travi di impalcato.

    NTC18 §7.7.7.2 — In assenza di elementi di controvento trasversali intermedi
    lungo la trave, il rapporto altezza/spessore per una trave a sezione
    rettangolare deve rispettare:
        h/b <= 4

    Parameters
    ----------
    h : float
        Altezza della sezione trasversale della trave [mm].
    b : float
        Larghezza (spessore) della sezione trasversale della trave [mm].

    Returns
    -------
    tuple[bool, float]
        - satisfied: True se la verifica e' soddisfatta
        - ratio: h/b [-]
    """
    if b <= 0:
        raise ValueError(f"La larghezza b deve essere > 0, ricevuta {b}")
    if h <= 0:
        raise ValueError(f"L'altezza h deve essere > 0, ricevuta {h}")

    ratio = h / b
    return ratio <= 4.0, ratio


# ══════════════════════════════════════════════════════════════════════════════
# §7.7.3.1 — DUTTILITA' CICLICA DELLE ZONE DISSIPATIVE
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(
    article="7.7.3.1",
    latex=r"\mu_s \ge \begin{cases} 6 & \text{CD''A''} \\ 4 & \text{CD''B''} \end{cases}",
)
def seismic_timber_static_ductility_check(
    mu_s: float,
    ductility_class: str,
) -> tuple[bool, float]:
    """Verifica della duttilita' statica minima della zona dissipativa.

    NTC18 §7.7.3.1 — Le zone dissipative devono essere in grado di deformarsi
    plasticamente per almeno 3 cicli a inversione completa con un rapporto di
    duttilita' statica pari a:
    - mu_s >= 6  per strutture in CD"A"
    - mu_s >= 4  per strutture in CD"B"
    senza riduzione di resistenza superiore al 20%.

    Parameters
    ----------
    mu_s : float
        Duttilita' statica della zona dissipativa (rapporto spostamento ultimo /
        spostamento al limite elastico, da prove quasi-statiche) [-].
    ductility_class : str
        Classe di duttilita': 'A' o 'B'.

    Returns
    -------
    tuple[bool, float]
        - satisfied: True se la duttilita' e' sufficiente
        - ratio: mu_s / mu_s_min [-]
    """
    if ductility_class not in ("A", "B"):
        raise ValueError(
            f"Classe di duttilita' deve essere 'A' o 'B', ricevuto '{ductility_class}'"
        )
    if mu_s <= 0:
        raise ValueError(
            f"La duttilita' statica mu_s deve essere > 0, ricevuto {mu_s}"
        )

    mu_s_min = 6.0 if ductility_class == "A" else 4.0
    ratio = mu_s / mu_s_min
    return ratio >= 1.0, ratio
