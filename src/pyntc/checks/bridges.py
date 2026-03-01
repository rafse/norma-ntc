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


@ntc_ref(article="5.1.3.3.2", table="Tab.5.1.I")
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


@ntc_ref(article="5.1.3.3.3", table="Tab.5.1.II")
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


@ntc_ref(article="5.1.3.3.3", formula="5.1.1")
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


@ntc_ref(article="5.1.3.5", formula="5.1.4")
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


@ntc_ref(article="5.1.3.6", table="Tab.5.1.III")
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


@ntc_ref(article="5.1.3.14", table="Tab.5.1.VI")
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


@ntc_ref(article="5.2.2.2.1.1", formula="5.2.1")
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


@ntc_ref(article="5.2.2.2.1.2", table="Tab.5.2.I")
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


@ntc_ref(article="5.2.2.2.3", formula="5.2.5")
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


@ntc_ref(article="5.2.2.2.3", formula="5.2.6")
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


@ntc_ref(article="5.2.2.2.3", formula="5.2.8")
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


@ntc_ref(article="5.2.2.2.3", formula="5.2.2")
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


@ntc_ref(article="5.2.2.3.1", formula="5.2.10")
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


@ntc_ref(article="5.2.2.3.1", formula="5.2.9")
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


@ntc_ref(article="5.2.2.3.3")
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


@ntc_ref(article="5.2.2.3.3")
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


@ntc_ref(article="5.2.3.2.2.1", formula="5.2.11")
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


@ntc_ref(article="5.2.3.2.2", table="Tab.5.2.VI")
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
