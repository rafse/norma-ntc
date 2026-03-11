"""Costruzioni esistenti — NTC18 Cap. 8.

Valutazione della sicurezza, livelli di conoscenza, fattori di confidenza,
classificazione degli interventi (miglioramento / adeguamento), resistenze
di progetto per meccanismi duttili e fragili.

Unita':
- Forze/Carichi: [kN] o [kN/m^2]
- Resistenze: [MPa]
- Coefficienti: [-]
"""

from __future__ import annotations

from pyntc.core.reference import ntc_ref


# ══════════════════════════════════════════════════════════════════════════════
# §8.5.4 — LIVELLI DI CONOSCENZA E FATTORI DI CONFIDENZA
# ══════════════════════════════════════════════════════════════════════════════

# Valori FC dalla Circolare C8.5.4.1 (Tab.C8.5.IV)
_FC_TABLE: dict[str, float] = {
    "LC1": 1.35,
    "LC2": 1.20,
    "LC3": 1.00,
}


@ntc_ref(article="8.5.4", latex=r"\text{Tab.\,C8.5.IV — }FC")
def confidence_factor(knowledge_level: str) -> float:
    """Fattore di confidenza FC per costruzioni esistenti [-].

    NTC18 §8.5.4 — Livelli di conoscenza e fattori di confidenza.
    Valori numerici da Circolare C8.5.4.1, Tab.C8.5.IV:
        LC1 (limitata)  → FC = 1.35
        LC2 (adeguata)  → FC = 1.20
        LC3 (accurata)  → FC = 1.00

    Parameters
    ----------
    knowledge_level : str
        Livello di conoscenza: "LC1", "LC2" o "LC3" (case-insensitive).

    Returns
    -------
    float
        Fattore di confidenza FC [-].
    """
    key = knowledge_level.upper()
    if key not in _FC_TABLE:
        raise ValueError(
            f"knowledge_level deve essere LC1, LC2 o LC3, ricevuto: "
            f"'{knowledge_level}'"
        )
    return _FC_TABLE[key]


# ══════════════════════════════════════════════════════════════════════════════
# §8.3 — VALUTAZIONE DELLA SICUREZZA
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(article="8.3", latex=r"\zeta_E = \frac{PGA_{C}}{PGA_{D}}")
def safety_ratio_seismic(
    capacity_action: float, demand_action: float
) -> float:
    """Rapporto di sicurezza sismico ζ_E [-].

    NTC18 §8.3 — Rapporto tra l'azione sismica massima sopportabile
    dalla struttura e l'azione sismica di progetto per nuova costruzione.

        ζ_E = capacity_action / demand_action

    Parameters
    ----------
    capacity_action : float
        Azione sismica massima sopportabile [kN] o [g].
    demand_action : float
        Azione sismica di progetto per nuova costruzione [kN] o [g].

    Returns
    -------
    float
        Rapporto di sicurezza sismico ζ_E [-].
    """
    if capacity_action < 0:
        raise ValueError("capacity_action deve essere >= 0")
    if demand_action <= 0:
        raise ValueError("demand_action deve essere > 0")
    return capacity_action / demand_action


@ntc_ref(article="8.3", latex=r"\zeta_v = \frac{Q_{C}}{Q_{D}}")
def safety_ratio_vertical(
    capacity_load: float, demand_load: float
) -> float:
    """Rapporto di sicurezza per carichi variabili verticali ζ_v [-].

    NTC18 §8.3 — Rapporto tra il valore massimo del sovraccarico
    variabile verticale sopportabile e il valore di progetto per
    nuova costruzione.

        ζ_v = capacity_load / demand_load

    Parameters
    ----------
    capacity_load : float
        Sovraccarico variabile massimo sopportabile [kN/m^2].
    demand_load : float
        Sovraccarico variabile di progetto [kN/m^2].

    Returns
    -------
    float
        Rapporto di sicurezza verticale ζ_v [-].
    """
    if capacity_load < 0:
        raise ValueError("capacity_load deve essere >= 0")
    if demand_load <= 0:
        raise ValueError("demand_load deve essere > 0")
    return capacity_load / demand_load


# ══════════════════════════════════════════════════════════════════════════════
# §8.4.2 — INTERVENTO DI MIGLIORAMENTO
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(article="8.4.2", latex=r"\zeta_E \ge \zeta_{E,\min}")
def improvement_check(
    zeta_E_post: float,
    use_class: int,
    *,
    is_school: bool = False,
    is_isolation: bool = False,
    zeta_E_pre: float | None = None,
) -> tuple[bool, float]:
    """Verifica soglie minime per interventi di miglioramento.

    NTC18 §8.4.2:
    - Classe III (scolastico) e IV: ζ_E >= 0.6
    - Classe II e III (non scolastico): incremento ζ_E >= 0.1
    - Con isolamento sismico: ζ_E >= 1.0

    Parameters
    ----------
    zeta_E_post : float
        Rapporto di sicurezza sismico post-intervento [-].
    use_class : int
        Classe d'uso (1, 2, 3 o 4).
    is_school : bool
        True se costruzione di classe III ad uso scolastico.
    is_isolation : bool
        True se l'intervento prevede sistemi di isolamento.
    zeta_E_pre : float or None
        Rapporto di sicurezza sismico pre-intervento [-].
        Obbligatorio per classi II e III (non scolastico).

    Returns
    -------
    tuple[bool, float]
        (verifica_superata, soglia_minima):
        - verifica_superata: True se ζ_E_post >= soglia
        - soglia_minima: valore minimo richiesto di ζ_E
    """
    if use_class not in (1, 2, 3, 4):
        raise ValueError(
            f"use_class deve essere 1, 2, 3 o 4, ricevuto: {use_class}"
        )

    # Isolamento: soglia assoluta ζ_E >= 1.0
    if is_isolation:
        return zeta_E_post >= 1.0, 1.0

    # Classe IV o Classe III scolastico: soglia assoluta ζ_E >= 0.6
    if use_class == 4 or (use_class == 3 and is_school):
        return zeta_E_post >= 0.6, 0.6

    # Classe II e III (non scolastico): incremento >= 0.1
    if use_class in (2, 3):
        if zeta_E_pre is None:
            raise ValueError(
                "zeta_E_pre obbligatorio per classe II e III "
                "(non scolastico): serve per calcolare l'incremento >= 0.1"
            )
        threshold = zeta_E_pre + 0.1
        return zeta_E_post >= threshold, threshold

    # Classe I: nessun vincolo specifico in §8.4.2
    # (la norma non definisce soglie per classe I)
    return True, 0.0


# ══════════════════════════════════════════════════════════════════════════════
# §8.4.3 — INTERVENTO DI ADEGUAMENTO
# ══════════════════════════════════════════════════════════════════════════════

# Soglie ζ_E per caso di intervento
_ADEQUACY_THRESHOLDS: dict[str, float] = {
    "a": 1.0,   # sopraelevazione
    "b": 1.0,   # ampliamento
    "c": 0.80,  # cambio destinazione d'uso (carichi > 10%)
    "d": 1.0,   # trasformazione strutturale
    "e": 0.80,  # cambio classe d'uso → III scol. o IV
}


@ntc_ref(article="8.4.3", latex=r"\zeta_E \ge \zeta_{E,\min}")
def adequacy_check(
    zeta_E: float, intervention_case: str
) -> tuple[bool, float]:
    """Verifica soglie minime per interventi di adeguamento.

    NTC18 §8.4.3:
    - Casi a), b), d): ζ_E >= 1.0
    - Casi c), e): ζ_E >= 0.80

    Parameters
    ----------
    zeta_E : float
        Rapporto di sicurezza sismico post-intervento [-].
    intervention_case : str
        Caso di intervento: "a", "b", "c", "d" o "e".

    Returns
    -------
    tuple[bool, float]
        (verifica_superata, soglia):
        - verifica_superata: True se ζ_E >= soglia
        - soglia: valore minimo richiesto di ζ_E
    """
    case = intervention_case.lower()
    if case not in _ADEQUACY_THRESHOLDS:
        raise ValueError(
            f"intervention_case deve essere 'a', 'b', 'c', 'd' o 'e', "
            f"ricevuto: '{intervention_case}'"
        )
    threshold = _ADEQUACY_THRESHOLDS[case]
    return zeta_E >= threshold, threshold


@ntc_ref(article="8.4.3", latex=r"\frac{Q_{post}}{Q_{pre}} > 1{,}10")
def adequacy_required_load_increase(
    load_pre: float, load_post: float
) -> bool:
    """Verifica se l'incremento di carichi richiede adeguamento (caso c).

    NTC18 §8.4.3.c — L'adeguamento e' obbligatorio quando le variazioni
    di destinazione d'uso comportano incrementi dei carichi globali
    verticali in fondazione superiore al 10%.

    Parameters
    ----------
    load_pre : float
        Carico verticale globale pre-intervento [kN].
    load_post : float
        Carico verticale globale post-intervento [kN].

    Returns
    -------
    bool
        True se l'incremento e' superiore al 10% (adeguamento richiesto).
    """
    if load_pre <= 0:
        raise ValueError("load_pre deve essere > 0")
    if load_post < 0:
        raise ValueError("load_post deve essere >= 0")
    ratio = load_post / load_pre
    # "superiore al 10%" → strettamente maggiore di 1.10
    return ratio > 1.10


# ══════════════════════════════════════════════════════════════════════════════
# §8.7.2 — RESISTENZE DI PROGETTO PER COSTRUZIONI ESISTENTI
# ══════════════════════════════════════════════════════════════════════════════


@ntc_ref(article="8.7.2", latex=r"f_d = \frac{f_{mean}}{FC}")
def existing_design_strength_ductile(
    f_mean: float, FC: float
) -> float:
    """Resistenza di progetto per meccanismi duttili [MPa].

    NTC18 §8.7.2 — Per il calcolo della capacita' di meccanismi duttili
    si impiegano le proprieta' medie dei materiali divise per il fattore
    di confidenza.

        f_d = f_mean / FC

    Parameters
    ----------
    f_mean : float
        Resistenza media del materiale da indagini in situ [MPa].
    FC : float
        Fattore di confidenza [-] (1.00, 1.20 o 1.35).

    Returns
    -------
    float
        Resistenza di progetto per meccanismi duttili [MPa].
    """
    if f_mean < 0:
        raise ValueError("f_mean deve essere >= 0")
    if FC <= 0:
        raise ValueError("FC deve essere > 0")
    return f_mean / FC


@ntc_ref(article="8.7.2", latex=r"f_d = \frac{f_{mean}}{\gamma_m \cdot FC}")
def existing_design_strength_brittle(
    f_mean: float, gamma_m: float, FC: float
) -> float:
    """Resistenza di progetto per meccanismi fragili [MPa].

    NTC18 §8.7.2 — Per il calcolo della capacita' di meccanismi fragili
    le resistenze si dividono per i coefficienti parziali E per il fattore
    di confidenza.

        f_d = f_mean / (gamma_m * FC)

    Parameters
    ----------
    f_mean : float
        Resistenza media del materiale da indagini in situ [MPa].
    gamma_m : float
        Coefficiente parziale di sicurezza del materiale [-].
    FC : float
        Fattore di confidenza [-] (1.00, 1.20 o 1.35).

    Returns
    -------
    float
        Resistenza di progetto per meccanismi fragili [MPa].
    """
    if f_mean < 0:
        raise ValueError("f_mean deve essere >= 0")
    if gamma_m <= 0:
        raise ValueError("gamma_m deve essere > 0")
    if FC <= 0:
        raise ValueError("FC deve essere > 0")
    return f_mean / (gamma_m * FC)
