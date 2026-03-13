"""Ponti — NTC18 Cap. 5.

Azioni sui ponti stradali (§5.1) e ferroviari (§5.2):
corsie convenzionali, schemi di carico, forze di frenamento e centrifughe,
coefficienti dinamici, coefficienti di combinazione.

Unita':
- Forze: [kN]
- Carichi distribuiti lineari: [kN/m]
- Carichi distribuiti areali: [kN/m^2]
- Lunghezze: [m]
- Velocita': [km/h]
- Frequenze: [Hz]
"""

from __future__ import annotations

import math

from pyntc.core.reference import ntc_ref


# ══════════════════════════════════════════════════════════════════════════════
# §5.1 — PONTI STRADALI
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(
    article="5.1.3.3.2",
    table="Tab.5.1.I",
    latex=r"n = \lfloor w / 3 \rfloor, \quad w_r = w - 3n",
)
def bridge_conventional_lanes(w: float) -> tuple[int, float, float]:
    """Corsie convenzionali da larghezza superficie carrabile [m].

    NTC18 §5.1.3.3.2, Tab. 5.1.1.

    Parameters
    ----------
    w : float
        Larghezza della superficie carrabile [m].

    Returns
    -------
    tuple[int, float, float]
        (n_lanes, lane_width [m], remaining_width [m]).
    """
    if w <= 0:
        raise ValueError(f"w deve essere > 0, ricevuto {w}")
    if w < 5.40:
        return 1, 3.00, w - 3.00
    elif w < 6.00:
        return 2, w / 2.0, 0.00
    else:
        n = int(w / 3.0)
        return n, 3.00, w - 3.00 * n


@ntc_ref(
    article="5.1.3.3.3",
    table="Tab.5.1.II",
    latex=(
        r"\text{Corsia 1: } Q_{1k}=300\,\text{kN},\; q_{1k}=9{,}0\,\text{kN/m}^2 \\"
        r"\text{Corsia 2: } Q_{2k}=200\,\text{kN},\; q_{2k}=2{,}5\,\text{kN/m}^2 \\"
        r"\text{Corsia 3: } Q_{3k}=100\,\text{kN},\; q_{3k}=2{,}5\,\text{kN/m}^2"
    ),
)
def bridge_load_scheme_1(lane: int) -> tuple[float, float]:
    """Carichi dello Schema di Carico 1 per corsia [kN, kN/m^2].

    NTC18 §5.1.3.3.3, Tab. 5.1.II.

    Parameters
    ----------
    lane : int
        Numero della corsia convenzionale (1, 2, 3, 4+).

    Returns
    -------
    tuple[float, float]
        (Q_ik [kN] carico asse tandem, q_ik [kN/m^2] carico distribuito).
    """
    if lane < 1:
        raise ValueError(f"lane deve essere >= 1, ricevuto {lane}")
    if lane == 1:
        return 300.0, 9.0
    elif lane == 2:
        return 200.0, 2.5
    elif lane == 3:
        return 100.0, 2.5
    else:
        return 0.0, 2.5


@ntc_ref(
    article="5.1.3.3.3",
    formula="5.1.1",
    latex=(
        r"q_{L,t} = 128{,}95 \left(\frac{1}{L}\right)^{0{,}25} \quad "
        r"q_{L,b} = 88{,}71 \left(\frac{1}{L}\right)^{0{,}38} \quad "
        r"q_{L,c} = 77{,}12 \left(\frac{1}{L}\right)^{0{,}38}"
    ),
)
def bridge_long_span_load(L: float, load_type: str) -> float:
    """Carico distribuito per ponti di luce > 300 m [kN/m].

    NTC18 §5.1.3.3.3, Formule [5.1.1], [5.1.2], [5.1.3].

    Parameters
    ----------
    L : float
        Lunghezza della zona caricata [m].
    load_type : str
        Tipo di carico: "t" ([5.1.1] corsia 3), "b" ([5.1.2] corsia 2),
        "c" ([5.1.3] corsia 1).

    Returns
    -------
    float
        Carico distribuito q_L [kN/m].
    """
    if L <= 0:
        raise ValueError(f"L deve essere > 0, ricevuto {L}")
    if load_type == "t":
        # [5.1.1] q_L,t = 128.95 * (1/L)^0.25
        return 128.95 * (1.0 / L) ** 0.25
    elif load_type == "b":
        # [5.1.2] q_L,b = 88.71 * (1/L)^0.38
        return 88.71 * (1.0 / L) ** 0.38
    elif load_type == "c":
        # [5.1.3] q_L,c = 77.12 * (1/L)^0.38
        return 77.12 * (1.0 / L) ** 0.38
    else:
        raise ValueError(f"load_type deve essere 't', 'b' o 'c', ricevuto '{load_type}'")


@ntc_ref(
    article="5.1.3.5",
    formula="5.1.4",
    latex=r"180 \leq q_3 = 0{,}6 \cdot 2Q_{1k} + 0{,}10 \cdot q_{1k} \cdot w_1 \cdot L \leq 900 \; [\text{kN}]",
)
def bridge_braking_force_road(
    Q_1k: float, q_1k: float, w_1: float, L: float
) -> float:
    """Forza di frenamento o accelerazione per ponti stradali [kN].

    NTC18 §5.1.3.5, Formula [5.1.4].
    180 kN <= q_3 = 0.6*(2*Q_1k) + 0.10*q_1k*w_1*L <= 900 kN

    Parameters
    ----------
    Q_1k : float
        Carico asse tandem corsia 1 [kN].
    q_1k : float
        Carico distribuito corsia 1 [kN/m^2].
    w_1 : float
        Larghezza corsia convenzionale [m].
    L : float
        Lunghezza della zona caricata [m].

    Returns
    -------
    float
        Forza di frenamento q_3 [kN], clampata in [180, 900].
    """
    q_3 = 0.6 * (2.0 * Q_1k) + 0.10 * q_1k * w_1 * L
    return max(180.0, min(q_3, 900.0))


@ntc_ref(
    article="5.1.3.6",
    table="Tab.5.1.III",
    latex=(
        r"q_s = \begin{cases} 0{,}2\,Q_s & R < 200 \\ "
        r"\dfrac{40\,Q_s}{R} & 200 \leq R \leq 1500 \\ "
        r"0 & R > 1500 \end{cases}"
    ),
)
def bridge_centrifugal_force_road(R: float, Q_s: float) -> float:
    """Forza centrifuga per ponti stradali in curva [kN].

    NTC18 §5.1.3.6, Tab. 5.1.III.
    Q_s = somma carichi tandem agenti sul ponte.

    Parameters
    ----------
    R : float
        Raggio di curvatura dell'asse del ponte [m].
    Q_s : float
        Carico totale tandem Q_s = sum(2*Q_ik) [kN].

    Returns
    -------
    float
        Forza centrifuga q_s [kN].
    """
    if R <= 0:
        raise ValueError(f"R deve essere > 0, ricevuto {R}")
    if R < 200.0:
        return 0.2 * Q_s
    elif R <= 1500.0:
        return 40.0 * Q_s / R
    else:
        return 0.0


@ntc_ref(
    article="5.1.3.14",
    table="Tab.5.1.VI",
    latex=r"\psi_0,\;\psi_1,\;\psi_2 \text{ da Tab.\,5.1.VI}",
)
def bridge_road_psi_coefficients(action: str) -> tuple[float, float, float]:
    """Coefficienti psi per ponti stradali e pedonali.

    NTC18 §5.1.3.14, Tab. 5.1.VI.

    Parameters
    ----------
    action : str
        Tipo di azione. Valori ammessi:
        "tandem", "distributed", "concentrated", "schema2",
        "crowd", "wind_unloaded", "wind_construction",
        "wind_loaded", "snow", "snow_construction", "temperature".

    Returns
    -------
    tuple[float, float, float]
        (psi_0, psi_1, psi_2).
    """
    _table: dict[str, tuple[float, float, float]] = {
        # Schema 1 carichi tandem
        "tandem": (0.75, 0.75, 0.0),
        # Schemi 1, 5, 6 carichi distribuiti
        "distributed": (0.40, 0.40, 0.0),
        # Schemi 3, 4 carichi concentrati
        "concentrated": (0.40, 0.40, 0.0),
        # Schema 2
        "schema2": (0.0, 0.75, 0.0),
        # Folla (gruppo 4)
        "crowd": (0.0, 0.75, 0.0),
        # Vento a ponte scarico
        "wind_unloaded": (0.6, 0.2, 0.0),
        # Vento in esecuzione
        "wind_construction": (0.8, 0.0, 0.0),
        # Vento a ponte carico
        "wind_loaded": (0.6, 0.0, 0.0),
        # Neve (SLU e SLE)
        "snow": (0.0, 0.0, 0.0),
        # Neve in esecuzione
        "snow_construction": (0.8, 0.6, 0.5),
        # Temperatura
        "temperature": (0.6, 0.6, 0.5),
    }
    if action not in _table:
        valid = ", ".join(sorted(_table.keys()))
        raise ValueError(f"action '{action}' non valida. Valori ammessi: {valid}")
    return _table[action]


# ══════════════════════════════════════════════════════════════════════════════
# §5.2 — PONTI FERROVIARI
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(
    article="5.2.2.2.1.1",
    formula="5.2.1",
    latex=r"Q_{vk} = \alpha \cdot 250 \; [\text{kN}], \quad q_{vk} = \alpha \cdot 80 \; [\text{kN/m}]",
)
def bridge_lm71_axle_loads(alpha: float = 1.1) -> tuple[float, float]:
    """Carichi del modello LM71 per ferrovie ordinarie [kN, kN/m].

    NTC18 §5.2.2.2.1.1.
    4 assi da 250 kN (interasse 1.60 m) + carico distribuito 80 kN/m.
    Eccentricita' per rapporto Q_v2/Q_v1 = 1.25 → e = s/18 = 79.7 mm.

    Parameters
    ----------
    alpha : float
        Coefficiente di adattamento (default 1.1 per ferrovie ordinarie).

    Returns
    -------
    tuple[float, float]
        (Q_vk [kN] carico per asse, q_vk [kN/m] carico distribuito).
    """
    if alpha <= 0:
        raise ValueError(f"alpha deve essere > 0, ricevuto {alpha}")
    return alpha * 250.0, alpha * 80.0


@ntc_ref(
    article="5.2.2.2.1.2",
    table="Tab.5.2.I",
    latex=(
        r"\text{SW/0: } q_{ak}=\alpha \cdot 133\,\text{kN/m},\; a=15\,\text{m},\; c=5{,}3\,\text{m} \\"
        r"\text{SW/2: } q_{ak}=\alpha \cdot 150\,\text{kN/m},\; a=25\,\text{m},\; c=7{,}0\,\text{m}"
    ),
)
def bridge_sw_load(
    model: str, alpha: float | None = None
) -> tuple[float, float, float]:
    """Carichi dei modelli SW/0 e SW/2 [kN/m, m, m].

    NTC18 §5.2.2.2.1.2, Tab. 5.2.1.
    Alpha default: 1.1 per SW/0, 1.0 per SW/2 (ferrovie ordinarie).

    Parameters
    ----------
    model : str
        "SW/0" o "SW/2".
    alpha : float or None
        Coefficiente di adattamento. Se None, usa default normativo.

    Returns
    -------
    tuple[float, float, float]
        (q_ak [kN/m] carico distribuito, a [m] lunghezza caricata, c [m] distanza).
    """
    _sw_data: dict[str, tuple[float, float, float, float]] = {
        # (q_ak_base, a, c, alpha_default)
        "SW/0": (133.0, 15.0, 5.3, 1.1),
        "SW/2": (150.0, 25.0, 7.0, 1.0),
    }
    if model not in _sw_data:
        raise ValueError(f"model deve essere 'SW/0' o 'SW/2', ricevuto '{model}'")
    q_base, a, c, alpha_default = _sw_data[model]
    if alpha is None:
        alpha = alpha_default
    return alpha * q_base, a, c


@ntc_ref(
    article="5.2.2.2.3",
    formula="5.2.5",
    latex=r"n_0 = \frac{17{,}75}{\sqrt{\delta_0}}",
)
def bridge_natural_frequency(delta_0: float) -> float:
    """Frequenza propria flessionale di trave semplicemente appoggiata [Hz].

    NTC18 §5.2.2.2.3, Formula [5.2.5].
    n_0 = 17.75 / sqrt(delta_0)

    Parameters
    ----------
    delta_0 : float
        Freccia dovuta alle azioni permanenti [mm].

    Returns
    -------
    float
        Frequenza propria n_0 [Hz].
    """
    if delta_0 <= 0:
        raise ValueError(f"delta_0 deve essere > 0, ricevuto {delta_0}")
    return 17.75 / math.sqrt(delta_0)


@ntc_ref(
    article="5.2.2.2.3",
    formula="5.2.6",
    latex=(
        r"\Phi_2 = \frac{1{,}44}{\sqrt{L_\Phi - 0{,}2}} + 0{,}82 \quad "
        r"\Phi_3 = \frac{2{,}16}{\sqrt{L_\Phi - 0{,}2}} + 0{,}73"
    ),
)
def bridge_dynamic_coefficient(L_0: float, maintenance: str = "high") -> float:
    """Coefficiente di incremento dinamico Phi per ponti ferroviari.

    NTC18 §5.2.2.2.3, Formule [5.2.6] e [5.2.7].

    Parameters
    ----------
    L_0 : float
        Lunghezza caratteristica [m] (da Tab. 5.2.II).
    maintenance : str
        Livello di manutenzione: "high" → Phi_2, "low" → Phi_3.

    Returns
    -------
    float
        Coefficiente dinamico Phi (clampato nei limiti normativi).
    """
    if L_0 <= 0.2:
        raise ValueError(f"L_0 deve essere > 0.2, ricevuto {L_0}")
    if maintenance == "high":
        # [5.2.6] Phi_2 = 1.44/sqrt(L_0 - 0.2) + 0.82, 1.00 ≤ Phi_2 ≤ 1.67
        phi = 1.44 / math.sqrt(L_0 - 0.2) + 0.82
        return max(1.00, min(phi, 1.67))
    elif maintenance == "low":
        # [5.2.7] Phi_3 = 2.16/sqrt(L_0 - 0.2) + 0.73, 1.00 ≤ Phi_3 ≤ 2.00
        phi = 2.16 / math.sqrt(L_0 - 0.2) + 0.73
        return max(1.00, min(phi, 2.00))
    else:
        raise ValueError(
            f"maintenance deve essere 'high' o 'low', ricevuto '{maintenance}'"
        )


@ntc_ref(
    article="5.2.2.2.3",
    formula="5.2.8",
    latex=r"\Phi_{\text{rid}} = \Phi - \frac{h - 1{,}00}{10} \geq 1{,}0",
)
def bridge_reduced_dynamic_coefficient(Phi: float, h: float) -> float:
    """Coefficiente dinamico ridotto per ponti ad arco/scatolari con copertura.

    NTC18 §5.2.2.2.3, Formula [5.2.8].
    Phi_rid = Phi - (h - 1.00) / 10 >= 1.0
    Per h <= 1.0 m nessuna riduzione.

    Parameters
    ----------
    Phi : float
        Coefficiente dinamico base (Phi_2 o Phi_3).
    h : float
        Altezza della copertura dall'estradosso della struttura
        alla faccia superiore delle traverse [m].

    Returns
    -------
    float
        Coefficiente dinamico ridotto Phi_rid.
    """
    if h <= 1.0:
        return Phi
    phi_rid = Phi - (h - 1.0) / 10.0
    return max(phi_rid, 1.0)


@ntc_ref(
    article="5.2.2.2.3",
    formula="5.2.2",
    latex=(
        r"n_{\max} = 94{,}76 \, L^{-0{,}748} \quad "
        r"n_{\min} = \begin{cases} 80/L & L \leq 20 \\ "
        r"23{,}58 \, L^{-0{,}902} & L > 20 \end{cases}"
    ),
)
def bridge_frequency_limits(L: float) -> tuple[float, float]:
    """Limiti del fuso di frequenza per ponti ferroviari [Hz].

    NTC18 §5.2.2.2.3, Formule [5.2.2], [5.2.3], [5.2.4].

    Parameters
    ----------
    L : float
        Luce della campata [m], 4 m <= L <= 100 m per il limite inferiore.

    Returns
    -------
    tuple[float, float]
        (n_upper [Hz], n_lower [Hz]).
    """
    if L <= 0:
        raise ValueError(f"L deve essere > 0, ricevuto {L}")
    # [5.2.2] Limite superiore
    n_upper = 94.76 * L ** (-0.748)
    # Limite inferiore
    if L <= 20.0:
        # [5.2.3]
        n_lower = 80.0 / L
    else:
        # [5.2.4]
        n_lower = 23.58 * L ** (-0.902)
    return n_upper, n_lower


@ntc_ref(
    article="5.2.2.3.1",
    formula="5.2.10",
    latex=(
        r"f = 1 - \frac{V - 120}{1000} "
        r"\left(\frac{814}{V} + 1{,}75\right) "
        r"\left(1 - \sqrt{\frac{2{,}88}{L_t}}\right)"
    ),
)
def bridge_centrifugal_reduction_factor(V: float, L_t: float) -> float:
    """Fattore di riduzione f per forza centrifuga ferroviaria.

    NTC18 §5.2.2.3.1, Formula [5.2.10].
    f = 1 per V <= 120 km/h o L_t <= 2.88 m.
    f(V) = f(300) per V > 300 km/h.

    Parameters
    ----------
    V : float
        Velocita' di progetto [km/h].
    L_t : float
        Lunghezza di influenza del tratto curvo caricato [m].

    Returns
    -------
    float
        Fattore di riduzione f.
    """
    if V <= 120.0 or L_t <= 2.88:
        return 1.0
    # Per V > 300, usa V = 300
    V_calc = min(V, 300.0)
    f = 1.0 - (V_calc - 120.0) / 1000.0 * (814.0 / V_calc + 1.75) * (
        1.0 - math.sqrt(2.88 / L_t)
    )
    return f


@ntc_ref(
    article="5.2.2.3.1",
    formula="5.2.9",
    latex=r"Q_a = \frac{V^2}{127 \, r} \cdot f \cdot \alpha \cdot Q_{ik}",
)
def bridge_centrifugal_force_rail(
    V: float,
    r: float,
    Q_ik: float,
    alpha: float = 1.1,
    f: float = 1.0,
) -> float:
    """Forza centrifuga su ponte ferroviario in curva [kN o kN/m].

    NTC18 §5.2.2.3.1, Formula [5.2.9].
    Q_a = V^2 / (127 * r) * (f * alpha * Q_ik)

    Parameters
    ----------
    V : float
        Velocita' di progetto [km/h].
    r : float
        Raggio di curvatura [m].
    Q_ik : float
        Carico verticale caratteristico [kN o kN/m].
    alpha : float
        Coefficiente di adattamento (default 1.1).
    f : float
        Fattore di riduzione (default 1.0, calcolare con
        bridge_centrifugal_reduction_factor).

    Returns
    -------
    float
        Forza centrifuga [kN o kN/m].
    """
    if r <= 0:
        raise ValueError(f"r deve essere > 0, ricevuto {r}")
    return V**2 / (127.0 * r) * (f * alpha * Q_ik)


@ntc_ref(
    article="5.2.2.3.3",
    latex=(
        r"Q_{hk} = \begin{cases} "
        r"20 \, \alpha \, L \leq 6000 & \text{LM71, SW/0} \\ "
        r"35 \, \alpha \, L & \text{SW/2} \end{cases} \; [\text{kN}]"
    ),
)
def bridge_braking_force_rail(
    L: float, model: str = "LM71", alpha: float = 1.1
) -> float:
    """Forza di frenamento per ponti ferroviari [kN].

    NTC18 §5.2.2.3.3.
    LM71/SW0: Q_hk = 20 * L * alpha <= 6000 kN
    SW/2:     Q_hk = 35 * L * alpha (senza limite superiore esplicito)

    Parameters
    ----------
    L : float
        Lunghezza di binario caricato [m].
    model : str
        Modello di carico: "LM71", "SW/0" o "SW/2".
    alpha : float
        Coefficiente di adattamento (default 1.1).

    Returns
    -------
    float
        Forza di frenamento Q_hk [kN].
    """
    if model in ("LM71", "SW/0"):
        return min(20.0 * L * alpha, 6000.0)
    elif model == "SW/2":
        return 35.0 * L * alpha
    else:
        raise ValueError(
            f"model deve essere 'LM71', 'SW/0' o 'SW/2', ricevuto '{model}'"
        )


@ntc_ref(
    article="5.2.2.3.3",
    latex=r"Q_{ak} = 33 \, \alpha \, L \leq 1000 \; [\text{kN}]",
)
def bridge_starting_force_rail(L: float, alpha: float = 1.1) -> float:
    """Forza di avviamento per ponti ferroviari [kN].

    NTC18 §5.2.2.3.3.
    Q_ak = 33 * L * alpha <= 1000 kN (per tutti i modelli LM71, SW/0, SW/2).

    Parameters
    ----------
    L : float
        Lunghezza di binario caricato [m].
    alpha : float
        Coefficiente di adattamento (default 1.1).

    Returns
    -------
    float
        Forza di avviamento Q_ak [kN].
    """
    return min(33.0 * L * alpha, 1000.0)


@ntc_ref(
    article="5.2.3.2.2.1",
    formula="5.2.11",
    latex=r"R = \frac{L^2}{8 \, \delta_i}",
)
def bridge_curvature_radius(L: float, delta_i: float) -> float:
    """Raggio di curvatura orizzontale da freccia per impalcato appoggiato [m].

    NTC18 §5.2.3.2.2.1, Formula [5.2.11].
    R = L^2 / (8 * delta_i)

    Parameters
    ----------
    L : float
        Luce dell'impalcato [m].
    delta_i : float
        Freccia orizzontale [m].

    Returns
    -------
    float
        Raggio di curvatura R [m].
    """
    if delta_i <= 0:
        raise ValueError(f"delta_i deve essere > 0, ricevuto {delta_i}")
    return L**2 / (8.0 * delta_i)




# ══════════════════════════════════════════════════════════════════════════════
# §5.2.2.4.2 — TEMPERATURA NEI PONTI
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(
    article="5.2.2.4.2",
    latex=(
        r"\Delta T_{\text{deck}} = 5\,°\text{C} \quad "
        r"\Delta T_{\text{box}} = 5\,°\text{C} \quad "
        r"\Delta T_{\text{composite}} = 5\,°\text{C} \quad "
        r"\Delta T_{\text{deform}} = 10\,°\text{C}"
    ),
)
def bridge_deck_thermal_gradient(
    deck_type: str, check: str = "strength"
) -> float:
    """Gradiente termico non uniforme nell'impalcato [°C].

    NTC18 §5.2.2.4.2.

    Parameters
    ----------
    deck_type : str
        Tipo di impalcato:
        - ``"slab"``: impalcato generico (gradiente estradosso-intradosso)
        - ``"box"``: impalcato a cassone in c.a. (gradiente nello spessore pareti)
        - ``"composite"``: struttura mista acciaio-calcestruzzo
          (differenza soletta c.a. - trave acciaio)
    check : str
        Tipo di verifica: ``"strength"`` (resistenza, default) o
        ``"deformation"`` (verifica deformazioni orizzontali/verticali,
        esclude comfort).

    Returns
    -------
    float
        Differenza di temperatura DeltaT [°C].
        Il valore e' positivo; applicare con segno ± (entrambi i versi).

    Raises
    ------
    ValueError
        Se ``deck_type`` o ``check`` non sono validi.
    """
    _valid_types = {"slab", "box", "composite"}
    _valid_checks = {"strength", "deformation"}

    if deck_type not in _valid_types:
        valid = ", ".join(sorted(_valid_types))
        raise ValueError(
            f"deck_type '{deck_type}' non valido. Valori ammessi: {valid}"
        )
    if check not in _valid_checks:
        valid = ", ".join(sorted(_valid_checks))
        raise ValueError(
            f"check '{check}' non valido. Valori ammessi: {valid}"
        )

    if check == "deformation":
        return 10.0

    # check == "strength"
    return 5.0


@ntc_ref(
    article="5.2.2.4.2",
    latex=(
        r"\Delta T_{\text{int-ext}} = 10\,°\text{C}, \quad "
        r"\Delta T_{\text{fusto-zattera}} = 5\,°\text{C}, \quad "
        r"h_{\text{var}} = 5 \, t_w"
    ),
)
def bridge_hollow_pier_thermal(t_w: float) -> tuple[float, float, float]:
    """Gradienti termici per pile cave [°C, °C, m].

    NTC18 §5.2.2.4.2.
    - DeltaT interno-esterno = 10 °C (con E non ridotto)
    - DeltaT fusto-zattera = 5 °C con variazione lineare su altezza 5*t_w

    Parameters
    ----------
    t_w : float
        Spessore della parete della pila [m].

    Returns
    -------
    tuple[float, float, float]
        (DeltaT_int_ext [°C], DeltaT_shaft_raft [°C],
         h_variation [m] altezza di variazione lineare).

    Raises
    ------
    ValueError
        Se ``t_w`` <= 0.
    """
    if t_w <= 0:
        raise ValueError(f"t_w deve essere > 0, ricevuto {t_w}")

    delta_t_int_ext = 10.0
    delta_t_shaft_raft = 5.0
    h_variation = 5.0 * t_w

    return delta_t_int_ext, delta_t_shaft_raft, h_variation


@ntc_ref(
    article="5.2.2.4.2",
    latex=(
        r"\Delta T_{\text{rotaia}} = \begin{cases} "
        r"0 & \text{senza giunti di dilatazione} \\ "
        r"+30\,°\text{C},\; -40\,°\text{C} & \text{con giunti di dilatazione}"
        r"\end{cases}"
    ),
)
def bridge_rail_thermal_variation(
    has_expansion_device: bool,
) -> tuple[float, float]:
    """Variazioni termiche del binario per interazione statica [°C].

    NTC18 §5.2.2.4.2.
    Senza apparecchi di dilatazione: variazione nulla.
    Con apparecchi di dilatazione: +30 °C e -40 °C rispetto alla
    temperatura di regolazione.

    Parameters
    ----------
    has_expansion_device : bool
        ``True`` se il binario ha apparecchi di dilatazione.

    Returns
    -------
    tuple[float, float]
        (DeltaT_positive [°C], DeltaT_negative [°C]).
    """
    if has_expansion_device:
        return 30.0, -40.0
    return 0.0, 0.0


# ══════════════════════════════════════════════════════════════════════════════
# §5.1.3.14 — COEFFICIENTI PARZIALI SLU PONTI STRADALI (Tab. 5.1.V)
# ══════════════════════════════════════════════════════════════════════════════

# (load_type, effect) → (EQU, A1, A2)
_TABLE_5_1_V: dict[tuple[str, str], tuple[float, float, float]] = {
    # Azioni permanenti g1, g3
    ("G1", "favorable"):   (0.90, 1.00, 1.00),
    ("G1", "unfavorable"): (1.10, 1.35, 1.00),
    # Azioni permanenti non strutturali g2
    ("G2", "favorable"):   (0.00, 0.00, 0.00),
    ("G2", "unfavorable"): (1.50, 1.50, 1.30),
    # Azioni variabili da traffico
    ("Q_traffic", "favorable"):   (0.00, 0.00, 0.00),
    ("Q_traffic", "unfavorable"): (1.35, 1.35, 1.15),
    # Azioni variabili
    ("Q", "favorable"):   (0.00, 0.00, 0.00),
    ("Q", "unfavorable"): (1.50, 1.50, 1.30),
    # Distorsioni e presollecitazioni di progetto
    ("prestress", "favorable"):   (0.90, 1.00, 1.00),
    ("prestress", "unfavorable"): (1.00, 1.00, 1.00),
    # Ritiro, viscosita', cedimenti vincolari
    ("creep", "favorable"):   (0.00, 0.00, 0.00),
    ("creep", "unfavorable"): (1.20, 1.20, 1.00),
}

_VALID_COMBINATIONS_ROAD = {"EQU", "A1", "A2"}
_COMBINATION_INDEX: dict[str, int] = {"EQU": 0, "A1": 1, "A2": 2}


@ntc_ref(
    article="5.1.3.14",
    table="Tab. 5.1.V",
    latex=r"\gamma_{G1},\;\gamma_{G2},\;\gamma_Q,\;\gamma_{Q1},\;\gamma_{C2} \text{ da Tab.\,5.1.V}",
)
def bridge_road_partial_factors(
    load_type: str, effect: str, combination: str
) -> float:
    """Coefficienti parziali di sicurezza agli SLU per ponti stradali.

    NTC18 §5.1.3.14, Tab. 5.1.V.

    Tabella valori:
    +-----------+------------+------+------+------+
    | load_type | effect     |  EQU |   A1 |   A2 |
    +===========+============+======+======+======+
    | G1        | favorable  | 0.90 | 1.00 | 1.00 |
    |           | unfavorable| 1.10 | 1.35 | 1.00 |
    | G2        | favorable  | 0.00 | 0.00 | 0.00 |
    |           | unfavorable| 1.50 | 1.50 | 1.30 |
    | Q_traffic | favorable  | 0.00 | 0.00 | 0.00 |
    |           | unfavorable| 1.35 | 1.35 | 1.15 |
    | Q         | favorable  | 0.00 | 0.00 | 0.00 |
    |           | unfavorable| 1.50 | 1.50 | 1.30 |
    | prestress | favorable  | 0.90 | 1.00 | 1.00 |
    |           | unfavorable| 1.00 | 1.00 | 1.00 |
    | creep     | favorable  | 0.00 | 0.00 | 0.00 |
    |           | unfavorable| 1.20 | 1.20 | 1.00 |
    +-----------+------------+------+------+------+

    Parameters
    ----------
    load_type : str
        Tipo di azione: "G1" (perm. strutturali), "G2" (perm. non-strutt.),
        "Q_traffic" (var. traffico), "Q" (var. altre), "prestress"
        (distorsioni/presollecitazioni), "creep" (ritiro/viscosita').
    effect : str
        Effetto dell'azione: "favorable" o "unfavorable".
    combination : str
        Combinazione SLU: "EQU", "A1" o "A2".

    Returns
    -------
    float
        Coefficiente parziale gamma.
    """
    valid_load_types = {k for k, _ in _TABLE_5_1_V}
    if load_type not in valid_load_types:
        raise ValueError(
            f"load_type '{load_type}' non valido. "
            f"Valori ammessi: {', '.join(sorted(valid_load_types))}"
        )
    if effect not in ("favorable", "unfavorable"):
        raise ValueError(
            f"effect '{effect}' non valido. Valori ammessi: 'favorable', 'unfavorable'"
        )
    if combination not in _VALID_COMBINATIONS_ROAD:
        raise ValueError(
            f"combination '{combination}' non valida. "
            f"Valori ammessi: {', '.join(sorted(_VALID_COMBINATIONS_ROAD))}"
        )
    row = _TABLE_5_1_V[(load_type, effect)]
    return row[_COMBINATION_INDEX[combination]]


# ══════════════════════════════════════════════════════════════════════════════
# §5.2.3.2.1 — COEFFICIENTI PARZIALI SLU PONTI FERROVIARI (Tab. 5.2.V)
# ══════════════════════════════════════════════════════════════════════════════

# (load_type, effect) → (EQU, A1, A2)
_TABLE_5_2_V: dict[tuple[str, str], tuple[float, float, float]] = {
    # Azioni permanenti
    ("G1", "favorable"):   (0.90, 1.00, 1.00),
    ("G1", "unfavorable"): (1.10, 1.35, 1.00),
    # Azioni permanenti non strutturali
    ("G2", "favorable"):   (0.00, 0.00, 0.00),
    ("G2", "unfavorable"): (1.50, 1.50, 1.30),
    # Ballast
    ("ballast", "favorable"):   (0.90, 1.00, 1.00),
    ("ballast", "unfavorable"): (1.50, 1.50, 1.30),
    # Azioni variabili da traffico
    ("Q_traffic", "favorable"):   (0.00, 0.00, 0.00),
    ("Q_traffic", "unfavorable"): (1.45, 1.45, 1.25),
    # Azioni variabili
    ("Q", "favorable"):   (0.00, 0.00, 0.00),
    ("Q", "unfavorable"): (1.50, 1.50, 1.30),
    # Precompressione
    ("prestress", "favorable"):   (0.90, 1.00, 1.00),
    ("prestress", "unfavorable"): (1.00, 1.00, 1.00),
    # Ritiro, viscosita', cedimenti
    ("creep", "favorable"):   (0.00, 0.00, 0.00),
    ("creep", "unfavorable"): (1.20, 1.20, 1.00),
}


@ntc_ref(
    article="5.2.3.2.1",
    table="Tab. 5.2.V",
    latex=r"\gamma_{G1},\;\gamma_{G2},\;\gamma_B,\;\gamma_Q,\;\gamma_P,\;\gamma_{Ce} \text{ da Tab.\,5.2.V}",
)
def bridge_rail_partial_factors(
    load_type: str, effect: str, combination: str
) -> float:
    """Coefficienti parziali di sicurezza agli SLU per ponti ferroviari.

    NTC18 §5.2.3.2.1, Tab. 5.2.V.

    Tabella valori:
    +-----------+------------+------+------+------+
    | load_type | effect     |  EQU |   A1 |   A2 |
    +===========+============+======+======+======+
    | G1        | favorable  | 0.90 | 1.00 | 1.00 |
    |           | unfavorable| 1.10 | 1.35 | 1.00 |
    | G2        | favorable  | 0.00 | 0.00 | 0.00 |
    |           | unfavorable| 1.50 | 1.50 | 1.30 |
    | ballast   | favorable  | 0.90 | 1.00 | 1.00 |
    |           | unfavorable| 1.50 | 1.50 | 1.30 |
    | Q_traffic | favorable  | 0.00 | 0.00 | 0.00 |
    |           | unfavorable| 1.45 | 1.45 | 1.25 |
    | Q         | favorable  | 0.00 | 0.00 | 0.00 |
    |           | unfavorable| 1.50 | 1.50 | 1.30 |
    | prestress | favorable  | 0.90 | 1.00 | 1.00 |
    |           | unfavorable| 1.00 | 1.00 | 1.00 |
    | creep     | favorable  | 0.00 | 0.00 | 0.00 |
    |           | unfavorable| 1.20 | 1.20 | 1.00 |
    +-----------+------------+------+------+------+

    Parameters
    ----------
    load_type : str
        Tipo di azione: "G1" (perm.), "G2" (non-strutt.), "ballast",
        "Q_traffic" (var. traffico), "Q" (var. altre), "prestress"
        (precompressione), "creep" (ritiro/viscosita').
    effect : str
        Effetto dell'azione: "favorable" o "unfavorable".
    combination : str
        Combinazione SLU: "EQU", "A1" o "A2".

    Returns
    -------
    float
        Coefficiente parziale gamma.
    """
    valid_load_types = {k for k, _ in _TABLE_5_2_V}
    if load_type not in valid_load_types:
        raise ValueError(
            f"load_type '{load_type}' non valido. "
            f"Valori ammessi: {', '.join(sorted(valid_load_types))}"
        )
    if effect not in ("favorable", "unfavorable"):
        raise ValueError(
            f"effect '{effect}' non valido. Valori ammessi: 'favorable', 'unfavorable'"
        )
    if combination not in _VALID_COMBINATIONS_ROAD:
        raise ValueError(
            f"combination '{combination}' non valida. "
            f"Valori ammessi: {', '.join(sorted(_VALID_COMBINATIONS_ROAD))}"
        )
    row = _TABLE_5_2_V[(load_type, effect)]
    return row[_COMBINATION_INDEX[combination]]


# ══════════════════════════════════════════════════════════════════════════════
# §5.2.3.1.2 — FATTORI MULTITRACK PONTI FERROVIARI (Tab. 5.2.III)
# ══════════════════════════════════════════════════════════════════════════════

# (n_tracks_bucket, track_index, traffic_type) → factor
# n_tracks_bucket: 1, 2, or 3 (meaning >=3)
_TABLE_5_2_III: dict[tuple[int, int, str], float] = {
    # 1 binario
    (1, 1, "normal"): 1.0,
    (1, 1, "heavy"):  1.0,
    # 2 binari: primo binario
    (2, 1, "normal"): 1.0,
    (2, 1, "heavy"):  1.0,
    # 2 binari: secondo binario
    (2, 2, "normal"): 1.0,
    (2, 2, "heavy"):  0.75,
    # >=3 binari: primo binario
    (3, 1, "normal"): 1.0,
    (3, 1, "heavy"):  1.0,
    # >=3 binari: secondo binario
    (3, 2, "normal"): 0.75,
    (3, 2, "heavy"):  0.75,
    # >=3 binari: altri binari (3+) — solo traffico normale 0.75, heavy non caricato
    (3, 3, "normal"): 0.75,
    (3, 3, "heavy"):  0.0,
}


@ntc_ref(
    article="5.2.3.1.2",
    table="Tab. 5.2.III",
    latex=r"\alpha_{\text{track}} \in \{1{,}0;\; 0{,}75;\; 0{,}0\}",
)
def bridge_rail_multitrack_factor(
    n_tracks: int, track_index: int, traffic_type: str = "normal"
) -> float:
    """Fattore di riduzione carichi per piu' binari su ponte ferroviario.

    NTC18 §5.2.3.1.2, Tab. 5.2.III.

    Tabella valori:
    +----------+-------------+---------+-------+
    | n_tracks | track_index | normal  | heavy |
    +==========+=============+=========+=======+
    | 1        | 1           | 1.0     | 1.0   |
    | 2        | 1           | 1.0     | 1.0   |
    | 2        | 2           | 1.0     | 0.75  |
    | >=3      | 1           | 1.0     | 1.0   |
    | >=3      | 2           | 0.75    | 0.75  |
    | >=3      | 3+          | 0.75    | 0.0   |
    +----------+-------------+---------+-------+

    Per traffico pesante (heavy, SW/2): il secondo binario e oltre non
    sono considerati caricati contemporaneamente → fattore 0.0 per 3+.

    Parameters
    ----------
    n_tracks : int
        Numero totale di binari presenti sul ponte.
    track_index : int
        Indice del binario considerato (1=primo, 2=secondo, 3+=altri).
    traffic_type : str
        Tipo di traffico: "normal" (LM71+SW/0) o "heavy" (SW/2).

    Returns
    -------
    float
        Fattore di riduzione (1.0, 0.75 o 0.0).
    """
    if n_tracks < 1:
        raise ValueError(f"n_tracks deve essere >= 1, ricevuto {n_tracks}")
    if track_index < 1:
        raise ValueError(f"track_index deve essere >= 1, ricevuto {track_index}")
    if traffic_type not in ("normal", "heavy"):
        raise ValueError(
            f"traffic_type '{traffic_type}' non valido. "
            "Valori ammessi: 'normal', 'heavy'"
        )

    # Bucket per n_tracks: cap a 3 per >=3 binari
    bucket = min(n_tracks, 3)
    # Bucket per track_index: cap a 3 per terzo binario e oltre
    idx = min(track_index, 3)

    key = (bucket, idx, traffic_type)
    if key not in _TABLE_5_2_III:
        # track_index > n_tracks: binario non esiste
        raise ValueError(
            f"track_index {track_index} non valido per n_tracks={n_tracks}"
        )
    return _TABLE_5_2_III[key]


# ══════════════════════════════════════════════════════════════════════════════
# §5.2.3 — LIMITI SLE DEFORMAZIONE PONTI FERROVIARI (Tab. 5.2.VIII)
# ══════════════════════════════════════════════════════════════════════════════

# (angular_variation [rad], radius_single [m], radius_multiple [m])
_TABLE_5_2_VIII: list[tuple[float, float, float, float, float]] = [
    # (v_min, v_max, angular_variation, radius_single, radius_multiple)
    (0.0,   120.0, 0.0035, 1700.0,  3500.0),
    (120.0, 200.0, 0.0020, 6000.0,  9500.0),
    (200.0, math.inf, 0.0015, 14000.0, 17500.0),
]


@ntc_ref(
    article="5.2.3",
    table="Tab. 5.2.VIII",
    latex=(
        r"\theta_{\max},\; R_{\min,\text{single}},\; R_{\min,\text{multiple}} "
        r"\text{ da Tab.\,5.2.VIII}"
    ),
)
def bridge_rail_deformation_limits(speed: float) -> tuple[float, float, float]:
    """Limiti SLE di deformazione per la sicurezza del traffico ferroviario.

    NTC18 §5.2.3, Tab. 5.2.VIII.

    Tabella valori:
    +---------------+-------------------+-----------+-----------+
    | Velocita'     | Var. ang. max     | R_min     | R_min     |
    | [km/h]        | [rad]             | singola   | piu' camp.|
    +===============+===================+===========+===========+
    | V <= 120      | 0.0035            | 1700 m    | 3500 m    |
    | 120 < V <= 200| 0.0020            | 6000 m    | 9500 m    |
    | V > 200       | 0.0015            | 14000 m   | 17500 m   |
    +---------------+-------------------+-----------+-----------+

    Parameters
    ----------
    speed : float
        Velocita' di progetto [km/h].

    Returns
    -------
    tuple[float, float, float]
        (max_angular_variation [rad], min_radius_single [m],
         min_radius_multiple [m]).
    """
    if speed <= 0:
        raise ValueError(f"speed deve essere > 0, ricevuto {speed}")
    for v_min, v_max, theta, r_single, r_multi in _TABLE_5_2_VIII:
        if v_min < speed <= v_max:
            return theta, r_single, r_multi
    # speed <= 120 (first row, v_min=0)
    _, _, theta, r_single, r_multi = _TABLE_5_2_VIII[0]  # fallback first row
    return theta, r_single, r_multi


# ══════════════════════════════════════════════════════════════════════════════
# §5.1.4.3 — FLUSSO ANNUO VEICOLI PESANTI PER FATICA (Tab. 5.1.X)
# ══════════════════════════════════════════════════════════════════════════════

_TABLE_5_1_X: dict[int, float] = {
    1: 2.0e6,
    2: 0.5e6,
    3: 0.125e6,
    4: 0.05e6,
}


@ntc_ref(
    article="5.1.4.3",
    table="Tab. 5.1.X",
    latex=r"N_{\text{obs}} \text{ da Tab.\,5.1.X}",
)
def bridge_fatigue_traffic_flow(traffic_category: int) -> float:
    """Flusso annuo di veicoli pesanti per categoria di traffico (fatica).

    NTC18 §5.1.4.3, Tab. 5.1.X.

    Tabella valori:
    +----------+--------------------------------------------------+------------------+
    | Cat.     | Descrizione                                      | Flusso [veh/anno]|
    +==========+==================================================+==================+
    | 1        | Autostrade/strade >=2 corsie, intenso traffico   | 2.0 x 10^6       |
    | 2        | Autostrade/strade, traffico medio                | 0.5 x 10^6       |
    | 3        | Strade principali, traffico medio                | 0.125 x 10^6     |
    | 4        | Strade locali, traffico molto ridotto            | 0.05 x 10^6      |
    +----------+--------------------------------------------------+------------------+

    Parameters
    ----------
    traffic_category : int
        Categoria di traffico (1, 2, 3 o 4).

    Returns
    -------
    float
        Flusso annuo di veicoli di peso > 100 kN [veicoli/anno].
    """
    if traffic_category not in _TABLE_5_1_X:
        raise ValueError(
            f"traffic_category {traffic_category} non valida. "
            "Valori ammessi: 1, 2, 3, 4"
        )
    return _TABLE_5_1_X[traffic_category]


@ntc_ref(
    article="5.2.3.2.2",
    table="Tab.5.2.VI",
    latex=r"\psi_0,\;\psi_1,\;\psi_2 \text{ da Tab.\,5.2.VI}",
)
def bridge_rail_psi_coefficients(
    action: str, n_tracks: int = 1
) -> tuple[float, float, float]:
    """Coefficienti psi per ponti ferroviari.

    NTC18 §5.2.3.2.2, Tab. 5.2.VI.
    Per gruppi di carico (gr1-gr4), psi_0 dipende dal numero di binari caricati.

    Parameters
    ----------
    action : str
        Tipo di azione: "gr1", "gr2", "gr3", "gr4", "wind",
        "snow_construction", "snow", "temperature".
    n_tracks : int
        Numero di binari caricati (1, 2, 3+). Rilevante solo per gr1-gr3.

    Returns
    -------
    tuple[float, float, float]
        (psi_0, psi_1, psi_2).
    """
    # Coefficienti base (1 binario)
    _table: dict[str, tuple[float, float, float]] = {
        "gr1": (0.80, 0.80, 0.0),
        "gr2": (0.80, 0.80, 0.0),
        "gr3": (0.80, 0.80, 0.0),
        "gr4": (1.00, 1.00, 0.0),
        "wind": (0.60, 0.50, 0.0),
        "snow_construction": (0.80, 0.0, 0.0),
        "snow": (0.0, 0.0, 0.0),
        "temperature": (0.60, 0.60, 0.50),
    }
    if action not in _table:
        valid = ", ".join(sorted(_table.keys()))
        raise ValueError(f"action '{action}' non valida. Valori ammessi: {valid}")

    psi_0, psi_1, psi_2 = _table[action]

    # Riduzione psi_0 per numero di binari (Tab. 5.2.VI nota 1)
    if action in ("gr1", "gr2", "gr3"):
        if n_tracks == 2:
            psi_0 = 0.60
        elif n_tracks >= 3:
            psi_0 = 0.40

    return psi_0, psi_1, psi_2

@ntc_ref(
    article="5.2.4",
    table="Tab.5.2.VII",
    latex=r"\text{Tab.\,5.2.VII}",
)
def bridge_rail_sle_combination_factors(load_type: str) -> dict[str, float]:
    """Coefficienti psi per combinazioni SLE ferroviario [Tab. 5.2.VII].

    NTC18 §5.2.4, Tab. 5.2.VII — Ulteriori coefficienti di combinazione psi
    delle azioni per ponti ferroviari (SLE).

    Parameters
    ----------
    load_type : str
        Tipo di carico. Valori ammessi:
        "LM71", "SW/0", "SW/2", "traction_braking", "centrifugal",
        "nosing", "wind", "thermal".

    Returns
    -------
    dict[str, float]
        Dizionario con chiavi "psi_0", "psi_1", "psi_2".
    """
    _table: dict[str, dict[str, float]] = {
        "LM71":             {"psi_0": 0.80, "psi_1": 0.50, "psi_2": 0.0},
        "SW/0":             {"psi_0": 0.80, "psi_1": 0.80, "psi_2": 0.0},
        "SW/2":             {"psi_0": 0.00, "psi_1": 0.80, "psi_2": 0.0},
        "traction_braking": {"psi_0": 0.80, "psi_1": 0.50, "psi_2": 0.2},
        "centrifugal":      {"psi_0": 0.80, "psi_1": 0.50, "psi_2": 0.2},
        "nosing":           {"psi_0": 1.00, "psi_1": 0.80, "psi_2": 0.0},
        "wind":             {"psi_0": 0.60, "psi_1": 0.50, "psi_2": 0.0},
        "thermal":          {"psi_0": 0.60, "psi_1": 0.60, "psi_2": 0.5},
    }
    if load_type not in _table:
        valid = ", ".join(sorted(_table.keys()))
        raise ValueError(
            f"load_type '{load_type}' non valido. Valori ammessi: {valid}"
        )
    return dict(_table[load_type])


@ntc_ref(
    article="5.2.2",
    formula="5.2.3",
    latex=r"\phi_2 = \frac{1.44}{\sqrt{L_\phi}-0.2}+0.82",
)
def bridge_dynamic_factor(L_phi: float, track_type: str = "standard") -> float:
    """Coefficiente dinamico phi per ponti ferroviari.

    NTC18 §5.2.2 — phi_2 (binario ben mantenuto) e phi_3 (binario normale).

    Parameters
    ----------
    L_phi : float
        Lunghezza di riferimento [m] (da Tab. 5.2.II), 2 <= L_phi <= 20.
    track_type : str
        Tipo di binario: ``"maintained"`` (ben mantenuto, phi_2) o
        ``"standard"`` (normale, phi_3).

    Returns
    -------
    float
        Coefficiente dinamico phi (clampato in [1.0, 2.0]).
    """
    if L_phi < 2.0 or L_phi > 20.0:
        raise ValueError(
            f"L_phi deve essere in [2, 20] m, ricevuto {L_phi}"
        )
    if track_type == "maintained":
        phi = 1.44 / (math.sqrt(L_phi) - 0.2) + 0.82
    elif track_type == "standard":
        phi = 2.16 / (math.sqrt(L_phi) - 0.2) + 0.73
    else:
        raise ValueError(
            f"track_type deve essere 'maintained' o 'standard', "
            f"ricevuto '{track_type}'"
        )
    return max(1.0, min(phi, 2.0))



# ══════════════════════════════════════════════════════════════════════════
# §5.1.4.3 — MODELLI DI CARICO DI FATICA
# ══════════════════════════════════════════════════════════════════════════

# Dati geometrici condivisi (interassi e tipo ruota) per i 5 veicoli
_FATIGUE_VEHICLES: dict[int, dict] = {
    1: {
        "axle_spacing_m": [4.50],
        "wheel_type": ["A", "B"],
    },
    2: {
        "axle_spacing_m": [4.20, 1.30],
        "wheel_type": ["A", "B", "B"],
    },
    3: {
        "axle_spacing_m": [3.20, 5.20, 1.30, 1.30],
        "wheel_type": ["A", "B", "C", "C", "C"],
    },
    4: {
        "axle_spacing_m": [3.40, 6.00, 1.80],
        "wheel_type": ["A", "B", "B", "B"],
    },
    5: {
        "axle_spacing_m": [4.80, 3.60, 4.40, 1.30],
        "wheel_type": ["A", "B", "C", "C", "C"],
    },
}

# Carichi modello 2 (Tab. 5.1.VII)
_FATIGUE_MODEL2_LOADS: dict[int, list[float]] = {
    1: [90, 190],
    2: [80, 140, 140],
    3: [90, 180, 120, 120, 120],
    4: [90, 190, 140, 140],
    5: [90, 180, 120, 110, 110],
}

# Carichi modello 4 (Tab. 5.1.VIII) e composizione traffico
_FATIGUE_MODEL4_LOADS: dict[int, list[float]] = {
    1: [70, 130],
    2: [70, 120, 120],
    3: [70, 150, 90, 90, 90],
    4: [70, 140, 90, 90],
    5: [70, 130, 90, 80, 80],
}

# Percentuali traffico: {vehicle: {traffic_type: percentage}}
_FATIGUE_MODEL4_TRAFFIC: dict[int, dict[str, float]] = {
    1: {"long_distance": 20.0, "medium_distance": 40.0, "local": 80.0},
    2: {"long_distance": 5.0,  "medium_distance": 10.0, "local": 5.0},
    3: {"long_distance": 50.0, "medium_distance": 30.0, "local": 5.0},
    4: {"long_distance": 15.0, "medium_distance": 15.0, "local": 5.0},
    5: {"long_distance": 10.0, "medium_distance": 5.0,  "local": 5.0},
}

_VALID_TRAFFIC_TYPES = ("long_distance", "medium_distance", "local")


@ntc_ref(
    article="5.1.4.3",
    table="Tab.5.1.VII",
    latex=r"\text{Tab.\,5.1.VII}",
)
def bridge_fatigue_vehicle_model2(vehicle: int) -> dict:
    """Veicolo frequente modello 2 per fatica ponti stradali [Tab. 5.1.VII].

    NTC18 §5.1.4.3, Tab. 5.1.VII.

    Parameters
    ----------
    vehicle : int
        Numero del veicolo (1-5).

    Returns
    -------
    dict
        {"vehicle": int, "axle_spacing_m": list[float],
         "axle_loads_kN": list[float], "wheel_type": list[str]}
    """
    if vehicle not in _FATIGUE_VEHICLES:
        raise ValueError(
            f"vehicle {vehicle!r} non valido. Valori ammessi: 1-5."
        )
    return {
        "vehicle": vehicle,
        "axle_spacing_m": _FATIGUE_VEHICLES[vehicle]["axle_spacing_m"],
        "axle_loads_kN": _FATIGUE_MODEL2_LOADS[vehicle],
        "wheel_type": _FATIGUE_VEHICLES[vehicle]["wheel_type"],
    }


@ntc_ref(
    article="5.1.4.3",
    table="Tab.5.1.VIII",
    latex=r"\text{Tab.\,5.1.VIII}",
)
def bridge_fatigue_vehicle_model4(
    vehicle: int, traffic_type: str = "long_distance"
) -> dict:
    """Veicolo equivalente modello 4 per fatica ponti stradali [Tab. 5.1.VIII].

    NTC18 §5.1.4.3, Tab. 5.1.VIII.

    Parameters
    ----------
    vehicle : int
        Numero del veicolo (1-5).
    traffic_type : str
        Tipo di traffico: "long_distance", "medium_distance", "local".

    Returns
    -------
    dict
        {"vehicle": int, "axle_spacing_m": list[float],
         "axle_loads_kN": list[float], "wheel_type": list[str],
         "traffic_percentage": float}
    """
    if vehicle not in _FATIGUE_VEHICLES:
        raise ValueError(
            f"vehicle {vehicle!r} non valido. Valori ammessi: 1-5."
        )
    if traffic_type not in _VALID_TRAFFIC_TYPES:
        valid = ", ".join(f'"{t}"' for t in _VALID_TRAFFIC_TYPES)
        raise ValueError(
            f"traffic_type {traffic_type!r} non valido. Valori ammessi: {valid}."
        )
    return {
        "vehicle": vehicle,
        "axle_spacing_m": _FATIGUE_VEHICLES[vehicle]["axle_spacing_m"],
        "axle_loads_kN": _FATIGUE_MODEL4_LOADS[vehicle],
        "wheel_type": _FATIGUE_VEHICLES[vehicle]["wheel_type"],
        "traffic_percentage": _FATIGUE_MODEL4_TRAFFIC[vehicle][traffic_type],
    }
