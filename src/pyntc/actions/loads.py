"""Carichi permanenti e variabili — NTC18 §3.1.

Pesi propri dei materiali strutturali (§3.1.2), carichi permanenti
non strutturali (§3.1.3), sovraccarichi (§3.1.4).
"""

from __future__ import annotations

from pyntc.core.reference import ntc_ref


# ── Tab. 3.1.I — Pesi unita' di volume [kN/m^3] ────────────────────────────

_UNIT_WEIGHTS: dict[str, float] = {
    # Calcestruzzi cementizi e malte
    "calcestruzzo_ordinario": 24.0,
    "calcestruzzo_armato": 25.0,
    "malta_calce": 18.0,
    "malta_cemento": 21.0,
    "calce_polvere": 10.0,
    "cemento_polvere": 14.0,
    "sabbia": 17.0,
    # Metalli e leghe
    "acciaio": 78.5,
    "ghisa": 72.5,
    "alluminio": 27.0,
    # Materiale lapideo
    "tufo_vulcanico": 17.0,
    "calcare_compatto": 26.0,
    "calcare_tenero": 22.0,
    "gesso": 13.0,
    "granito": 27.0,
    "laterizio_pieno": 18.0,
    # Sostanze varie
    "acqua_dolce": 9.81,
    "acqua_mare": 10.1,
    "carta": 10.0,
    "vetro": 25.0,
}


# ── Tab. 3.1.II — Sovraccarichi per categoria d'uso ─────────────────────────
# (qk [kN/m^2], Qk [kN], Hk [kN/m])

_VARIABLE_LOADS: dict[str, tuple[float, float, float]] = {
    "A":  (2.00,  2.00, 1.00),
    "B1": (2.00,  2.00, 1.00),
    "B2": (3.00,  2.00, 1.00),
    "C1": (3.00,  3.00, 1.00),
    "C2": (4.00,  4.00, 2.00),
    "C3": (5.00,  5.00, 3.00),
    "C4": (5.00,  5.00, 3.00),
    "C5": (5.00,  5.00, 3.00),
    "D1": (4.00,  4.00, 2.00),
    "D2": (5.00,  5.00, 2.00),
    "F":  (2.50, 10.00, 1.00),
    "G":  (5.00, 50.00, 1.00),
    "H":  (0.50,  1.20, 1.00),
}


@ntc_ref(article="3.1.2", table="Tab.3.1.I", latex=r"\text{Tab.\,3.1.I}")
def unit_weight(material: str) -> float:
    """Peso unita' di volume di un materiale strutturale [kN/m^3].

    NTC18 §3.1.2, Tab. 3.1.I.

    Parameters
    ----------
    material : str
        Identificativo del materiale (snake_case, es. ``"calcestruzzo_armato"``).
        Valori ammessi: chiavi di ``_UNIT_WEIGHTS``.

    Returns
    -------
    float
        Peso per unita' di volume [kN/m^3].

    Raises
    ------
    ValueError
        Se il materiale non e' presente in Tab. 3.1.I.
    """
    try:
        return _UNIT_WEIGHTS[material]
    except KeyError:
        raise ValueError(
            f"materiale '{material}' non presente in Tab. 3.1.I. "
            f"Valori ammessi: {', '.join(sorted(_UNIT_WEIGHTS))}"
        )


@ntc_ref(article="3.1.3", latex=r"G_2 = \begin{cases} 0{,}40 & g \le 1{,}00 \\ 0{,}80 & g \le 2{,}00 \\ 1{,}20 & g \le 3{,}00 \\ 1{,}60 & g \le 4{,}00 \\ 2{,}00 & g \le 5{,}00 \end{cases}")
def partition_equivalent_load(weight_per_meter: float) -> float:
    """Carico equivalente distribuito delle partizioni interne [kN/m^2].

    NTC18 §3.1.3 — Il peso proprio per unita' di lunghezza delle
    partizioni viene convertito in carico uniformemente distribuito G2.

    Parameters
    ----------
    weight_per_meter : float
        Peso proprio per unita' di lunghezza della partizione [kN/m].

    Returns
    -------
    float
        Carico equivalente distribuito G2 [kN/m^2].

    Raises
    ------
    ValueError
        Se ``weight_per_meter`` e' negativo o superiore a 5.00 kN/m.
    """
    if weight_per_meter < 0:
        raise ValueError("Il peso per unita' di lunghezza non puo' essere negativo.")

    if weight_per_meter > 5.00:
        raise ValueError(
            "Partizioni con peso > 5.00 kN/m devono essere considerate "
            "con il loro effettivo posizionamento (NTC18 §3.1.3)."
        )

    # Scaglioni definiti al §3.1.3
    if weight_per_meter <= 1.00:
        return 0.40
    if weight_per_meter <= 2.00:
        return 0.80
    if weight_per_meter <= 3.00:
        return 1.20
    if weight_per_meter <= 4.00:
        return 1.60
    return 2.00


@ntc_ref(article="3.1.4", table="Tab.3.1.II", latex=r"\text{Tab.\,3.1.II}")
def variable_load(category: str) -> tuple[float, float, float]:
    """Sovraccarichi per categoria d'uso [kN/m^2, kN, kN/m].

    NTC18 §3.1.4, Tab. 3.1.II.

    Parameters
    ----------
    category : str
        Categoria d'uso (es. ``"A"``, ``"B1"``, ``"C3"``, ``"H"``).

    Returns
    -------
    tuple[float, float, float]
        ``(qk, Qk, Hk)`` dove:
        - ``qk`` carico verticale distribuito [kN/m^2]
        - ``Qk`` carico verticale concentrato [kN]
        - ``Hk`` carico orizzontale lineare [kN/m]

    Raises
    ------
    ValueError
        Se la categoria non e' presente in Tab. 3.1.II.
    """
    try:
        return _VARIABLE_LOADS[category]
    except KeyError:
        raise ValueError(
            f"categoria '{category}' non presente in Tab. 3.1.II. "
            f"Valori ammessi: {', '.join(sorted(_VARIABLE_LOADS))}"
        )


@ntc_ref(article="3.1.4.1", formula="3.1.1", latex=r"\alpha_A = \frac{5}{7}\,\psi_0 + \frac{10}{A} \le 1{,}0")
def area_reduction_factor(
    area: float,
    psi_0: float,
    category: str = "A",
) -> float:
    """Coefficiente riduttivo per area d'influenza alpha_A [-].

    NTC18 §3.1.4.1, Formula [3.1.1]:
        alpha_A = (5/7) * psi_0 + 10 / A  <= 1.0

    Per categorie C e D: alpha_A >= 0.6.

    Parameters
    ----------
    area : float
        Area d'influenza dell'elemento [m^2]. Deve essere > 0.
    psi_0 : float
        Coefficiente di combinazione (Tab. 2.5.I) [-].
    category : str
        Categoria d'uso (default ``"A"``). Influenza il minimo ammissibile.

    Returns
    -------
    float
        Coefficiente riduttivo alpha_A [-].

    Raises
    ------
    ValueError
        Se ``area`` <= 0.
    """
    if area <= 0:
        raise ValueError("L'area d'influenza deve essere > 0.")

    alpha_a = (5.0 / 7.0) * psi_0 + 10.0 / area

    # Cap superiore
    alpha_a = min(alpha_a, 1.0)

    # Cap inferiore per categorie C e D (§3.1.4.1)
    if category.startswith(("C", "D")):
        alpha_a = max(alpha_a, 0.6)

    return alpha_a


@ntc_ref(article="3.1.4.1", formula="3.1.2", latex=r"\alpha_n = \frac{2 + (n - 2)\,\psi_0}{n}")
def floor_reduction_factor(n_floors: int, psi_0: float) -> float:
    """Coefficiente riduttivo per numero di piani alpha_n [-].

    NTC18 §3.1.4.1, Formula [3.1.2]:
        alpha_n = (2 + (n - 2) * psi_0) / n

    Applicabile solo a categorie A-D, edifici con n > 2 piani.

    Parameters
    ----------
    n_floors : int
        Numero di piani caricati. Deve essere >= 2.
        La formula ha effetto solo per n >= 3.
    psi_0 : float
        Coefficiente di combinazione (Tab. 2.5.I) [-].

    Returns
    -------
    float
        Coefficiente riduttivo alpha_n [-].

    Raises
    ------
    ValueError
        Se ``n_floors`` < 2 (formula non applicabile con meno di 3 piani).
    """
    if n_floors < 2:
        raise ValueError(
            "La formula [3.1.2] e' applicabile a edifici con almeno 3 piani "
            f"(n >= 2), ricevuto n={n_floors}."
        )

    return (2.0 + (n_floors - 2) * psi_0) / n_floors
