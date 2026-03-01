"""Test per actions/combinations — NTC18 §2.5.3.

Copre:
- Tab. 2.5.1   — coefficienti di combinazione ψ_0, ψ_1, ψ_2
- Tab. 2.6.1   — coefficienti parziali γ_F per SLU
- [2.5.1]      — combinazione fondamentale SLU
- [2.5.2]      — combinazione caratteristica (rara) SLE
- [2.5.3]      — combinazione frequente SLE
- [2.5.4]      — combinazione quasi permanente SLE
- [2.5.5]      — combinazione sismica
- [2.5.6]      — combinazione eccezionale
- [2.5.7]      — masse sismiche
"""

import pytest
from numpy.testing import assert_allclose

from pyntc.actions.combinations import (
    combination_coefficients,
    partial_safety_factors,
    slu_combination,
    sle_characteristic_combination,
    sle_frequent_combination,
    sle_quasi_permanent_combination,
    seismic_combination,
    exceptional_combination,
    seismic_masses,
)
from pyntc.core.reference import get_ntc_ref


# ── Tab. 2.5.1 — Coefficienti di combinazione ψ ─────────────────────────────

class TestCombinationCoefficients:
    """NTC18 §2.5.2, Tab. 2.5.1 — ψ_0, ψ_1, ψ_2."""

    @pytest.mark.parametrize("category, expected", [
        ("A", (0.7, 0.5, 0.3)),
        ("B", (0.7, 0.5, 0.3)),
        ("C", (0.7, 0.7, 0.6)),
        ("D", (0.7, 0.7, 0.6)),
        ("E", (1.0, 0.9, 0.8)),
        ("F", (0.7, 0.7, 0.6)),
        ("G", (0.7, 0.5, 0.3)),
        ("H", (0.0, 0.0, 0.0)),
        ("K", (0.6, 0.2, 0.0)),
    ])
    def test_categorie_edifici(self, category, expected):
        """Verifica ψ per categorie edifici Tab. 2.5.1."""
        result = combination_coefficients(category)
        assert_allclose(result, expected, rtol=1e-3)

    def test_vento(self):
        """Vento: ψ_0=0.6, ψ_1=0.2, ψ_2=0.0."""
        assert_allclose(
            combination_coefficients("wind"), (0.6, 0.2, 0.0), rtol=1e-3
        )

    def test_neve_bassa_quota(self):
        """Neve quota ≤ 1000 m: ψ_0=0.5, ψ_1=0.2, ψ_2=0.0."""
        assert_allclose(
            combination_coefficients("snow_low"), (0.5, 0.2, 0.0), rtol=1e-3
        )

    def test_neve_alta_quota(self):
        """Neve quota > 1000 m: ψ_0=0.7, ψ_1=0.5, ψ_2=0.2."""
        assert_allclose(
            combination_coefficients("snow_high"), (0.7, 0.5, 0.2), rtol=1e-3
        )

    def test_temperatura(self):
        """Variazioni termiche: ψ_0=0.6, ψ_1=0.5, ψ_2=0.0."""
        assert_allclose(
            combination_coefficients("temperature"), (0.6, 0.5, 0.0),
            rtol=1e-3,
        )

    def test_categoria_I_caso_per_caso(self):
        """Categoria I solleva ValueError (da valutare caso per caso)."""
        with pytest.raises(ValueError, match="Categoria I"):
            combination_coefficients("I")

    def test_categoria_invalida(self):
        with pytest.raises(ValueError, match="non valida"):
            combination_coefficients("Z")

    def test_ntc_ref(self):
        ref = get_ntc_ref(combination_coefficients)
        assert ref is not None
        assert ref.table == "Tab.2.5.1"


# ── Tab. 2.6.1 — Coefficienti parziali γ_F per SLU ──────────────────────────

class TestPartialSafetyFactors:
    """NTC18 §2.6.1, Tab. 2.6.1 — γ_F."""

    # ── G1 ────────────────────────────────────────────────────────────────
    @pytest.mark.parametrize("approach, fav, sfav", [
        ("EQU", 0.9, 1.1),
        ("A1",  1.0, 1.3),
        ("A2",  1.0, 1.0),
    ])
    def test_G1(self, approach, fav, sfav):
        assert_allclose(
            partial_safety_factors("G1", favorable=True, approach=approach),
            fav, rtol=1e-3,
        )
        assert_allclose(
            partial_safety_factors("G1", favorable=False, approach=approach),
            sfav, rtol=1e-3,
        )

    # ── G2 ────────────────────────────────────────────────────────────────
    @pytest.mark.parametrize("approach, fav, sfav", [
        ("EQU", 0.8, 1.5),
        ("A1",  0.8, 1.5),
        ("A2",  0.8, 1.3),
    ])
    def test_G2(self, approach, fav, sfav):
        assert_allclose(
            partial_safety_factors("G2", favorable=True, approach=approach),
            fav, rtol=1e-3,
        )
        assert_allclose(
            partial_safety_factors("G2", favorable=False, approach=approach),
            sfav, rtol=1e-3,
        )

    # ── Q ─────────────────────────────────────────────────────────────────
    @pytest.mark.parametrize("approach, sfav", [
        ("EQU", 1.5),
        ("A1",  1.5),
        ("A2",  1.3),
    ])
    def test_Q(self, approach, sfav):
        assert_allclose(
            partial_safety_factors("Q", favorable=True, approach=approach),
            0.0, atol=1e-3,
        )
        assert_allclose(
            partial_safety_factors("Q", favorable=False, approach=approach),
            sfav, rtol=1e-3,
        )

    def test_load_type_invalido(self):
        with pytest.raises(ValueError, match="load_type"):
            partial_safety_factors("X", favorable=True)

    def test_approach_invalido(self):
        with pytest.raises(ValueError, match="approach"):
            partial_safety_factors("G1", favorable=True, approach="B1")

    def test_ntc_ref(self):
        ref = get_ntc_ref(partial_safety_factors)
        assert ref is not None
        assert ref.table == "Tab.2.6.1"


# ── [2.5.1] — Combinazione fondamentale SLU ──────────────────────────────────

class TestSluCombination:
    """NTC18 §2.5.3, Formula [2.5.1]."""

    def test_singola_azione_variabile(self):
        """G1=10, G2=5, Q=[8] cat A, approccio A1.
        F = 1.3*10 + 1.5*5 + 1.5*8 = 13+7.5+12 = 32.5.
        """
        result = slu_combination(
            G1=10.0, G2=5.0, Q=[8.0], categories=["A"], approach="A1",
        )
        assert_allclose(result, 32.5, rtol=1e-3)

    def test_due_azioni_variabili_scelta_dominante(self):
        """G1=10, G2=5, Q=[8, 6] cat [A, C], approccio A1.
        Caso 1 (Q[0] dominante): 1.3*10 + 1.5*5 + 1.5*8 + 1.5*0.7*6
            = 13 + 7.5 + 12 + 6.3 = 38.8
        Caso 2 (Q[1] dominante): 1.3*10 + 1.5*5 + 1.5*0.7*8 + 1.5*6
            = 13 + 7.5 + 8.4 + 9.0 = 37.9
        Max = 38.8.
        """
        result = slu_combination(
            G1=10.0, G2=5.0, Q=[8.0, 6.0], categories=["A", "C"],
            approach="A1",
        )
        assert_allclose(result, 38.8, rtol=1e-3)

    def test_con_precompressione(self):
        """G1=10, G2=5, Q=[8] cat A, P=3, approccio A1.
        F = 1.3*10 + 1.5*5 + 1.0*3 + 1.5*8 = 13+7.5+3+12 = 35.5.
        """
        result = slu_combination(
            G1=10.0, G2=5.0, Q=[8.0], categories=["A"],
            P=3.0, approach="A1",
        )
        assert_allclose(result, 35.5, rtol=1e-3)

    def test_approccio_EQU(self):
        """G1=10, G2=5, Q=[8] cat A, EQU.
        F = 1.1*10 + 1.5*5 + 1.5*8 = 11+7.5+12 = 30.5.
        """
        result = slu_combination(
            G1=10.0, G2=5.0, Q=[8.0], categories=["A"], approach="EQU",
        )
        assert_allclose(result, 30.5, rtol=1e-3)

    def test_approccio_A2(self):
        """G1=10, G2=5, Q=[8] cat A, A2.
        F = 1.0*10 + 1.3*5 + 1.3*8 = 10+6.5+10.4 = 26.9.
        """
        result = slu_combination(
            G1=10.0, G2=5.0, Q=[8.0], categories=["A"], approach="A2",
        )
        assert_allclose(result, 26.9, rtol=1e-3)

    def test_senza_variabili(self):
        """Solo permanenti: G1=10, G2=5, Q=[], A1.
        F = 1.3*10 + 1.5*5 = 13+7.5 = 20.5.
        """
        result = slu_combination(
            G1=10.0, G2=5.0, Q=[], categories=[], approach="A1",
        )
        assert_allclose(result, 20.5, rtol=1e-3)

    def test_tre_azioni_variabili(self):
        """G1=10, G2=5, Q=[8, 6, 4] cat [A, C, wind], A1.
        Caso 0 dominante: 13+7.5+1.5*8+1.5*0.7*6+1.5*0.6*4 = 13+7.5+12+6.3+3.6 = 42.4
        Caso 1 dominante: 13+7.5+1.5*0.7*8+1.5*6+1.5*0.6*4 = 13+7.5+8.4+9+3.6 = 41.5
        Caso 2 dominante: 13+7.5+1.5*0.7*8+1.5*0.7*6+1.5*4 = 13+7.5+8.4+6.3+6 = 41.2
        Max = 42.4.
        """
        result = slu_combination(
            G1=10.0, G2=5.0, Q=[8.0, 6.0, 4.0],
            categories=["A", "C", "wind"], approach="A1",
        )
        assert_allclose(result, 42.4, rtol=1e-3)

    def test_mismatch_Q_categories(self):
        """Q e categories devono avere la stessa lunghezza."""
        with pytest.raises(ValueError, match="lunghezza"):
            slu_combination(G1=10.0, G2=5.0, Q=[8.0], categories=["A", "B"])

    def test_ntc_ref(self):
        ref = get_ntc_ref(slu_combination)
        assert ref is not None
        assert ref.formula == "2.5.1"


# ── [2.5.2] — Combinazione caratteristica (rara) SLE ─────────────────────────

class TestSleCharacteristicCombination:
    """NTC18 §2.5.3, Formula [2.5.2]."""

    def test_singola_azione(self):
        """G1=10, G2=5, Q=[8] cat A.
        F = 10 + 5 + 8 = 23.
        """
        result = sle_characteristic_combination(
            G1=10.0, G2=5.0, Q=[8.0], categories=["A"],
        )
        assert_allclose(result, 23.0, rtol=1e-3)

    def test_due_azioni(self):
        """G1=10, G2=5, Q=[8, 6] cat [A, C].
        Caso 0 dom: 10+5+8+0.7*6 = 27.2
        Caso 1 dom: 10+5+0.7*8+6 = 26.6
        Max = 27.2.
        """
        result = sle_characteristic_combination(
            G1=10.0, G2=5.0, Q=[8.0, 6.0], categories=["A", "C"],
        )
        assert_allclose(result, 27.2, rtol=1e-3)

    def test_con_precompressione(self):
        """G1=10, G2=5, Q=[8] cat A, P=3.
        F = 10+5+3+8 = 26.
        """
        result = sle_characteristic_combination(
            G1=10.0, G2=5.0, Q=[8.0], categories=["A"], P=3.0,
        )
        assert_allclose(result, 26.0, rtol=1e-3)

    def test_senza_variabili(self):
        result = sle_characteristic_combination(
            G1=10.0, G2=5.0, Q=[], categories=[],
        )
        assert_allclose(result, 15.0, rtol=1e-3)

    def test_ntc_ref(self):
        ref = get_ntc_ref(sle_characteristic_combination)
        assert ref is not None
        assert ref.formula == "2.5.2"


# ── [2.5.3] — Combinazione frequente SLE ─────────────────────────────────────

class TestSleFrequentCombination:
    """NTC18 §2.5.3, Formula [2.5.3]."""

    def test_singola_azione(self):
        """G1=10, G2=5, Q=[8] cat A.
        F = 10+5+0.5*8 = 19.
        """
        result = sle_frequent_combination(
            G1=10.0, G2=5.0, Q=[8.0], categories=["A"],
        )
        assert_allclose(result, 19.0, rtol=1e-3)

    def test_due_azioni(self):
        """G1=10, G2=5, Q=[8, 6] cat [A, C].
        Caso 0 dom: 10+5+0.5*8+0.6*6 = 22.6
        Caso 1 dom: 10+5+0.3*8+0.7*6 = 21.6
        Max = 22.6.
        """
        result = sle_frequent_combination(
            G1=10.0, G2=5.0, Q=[8.0, 6.0], categories=["A", "C"],
        )
        assert_allclose(result, 22.6, rtol=1e-3)

    def test_ntc_ref(self):
        ref = get_ntc_ref(sle_frequent_combination)
        assert ref is not None
        assert ref.formula == "2.5.3"


# ── [2.5.4] — Combinazione quasi permanente SLE ──────────────────────────────

class TestSleQuasiPermanentCombination:
    """NTC18 §2.5.3, Formula [2.5.4]."""

    def test_singola_azione(self):
        """G1=10, G2=5, Q=[8] cat A.
        F = 10+5+0.3*8 = 17.4.
        """
        result = sle_quasi_permanent_combination(
            G1=10.0, G2=5.0, Q=[8.0], categories=["A"],
        )
        assert_allclose(result, 17.4, rtol=1e-3)

    def test_due_azioni(self):
        """G1=10, G2=5, Q=[8, 6] cat [A, E].
        F = 10+5+0.3*8+0.8*6 = 22.2.
        """
        result = sle_quasi_permanent_combination(
            G1=10.0, G2=5.0, Q=[8.0, 6.0], categories=["A", "E"],
        )
        assert_allclose(result, 22.2, rtol=1e-3)

    def test_senza_variabili(self):
        result = sle_quasi_permanent_combination(
            G1=10.0, G2=5.0, Q=[], categories=[],
        )
        assert_allclose(result, 15.0, rtol=1e-3)

    def test_ntc_ref(self):
        ref = get_ntc_ref(sle_quasi_permanent_combination)
        assert ref is not None
        assert ref.formula == "2.5.4"


# ── [2.5.5] — Combinazione sismica ───────────────────────────────────────────

class TestSeismicCombination:
    """NTC18 §2.5.3, Formula [2.5.5]."""

    def test_base(self):
        """E=20, G1=10, G2=5, Q=[8, 6] cat [A, C].
        F = 20+10+5+0.3*8+0.6*6 = 41.0.
        """
        result = seismic_combination(
            E=20.0, G1=10.0, G2=5.0, Q=[8.0, 6.0], categories=["A", "C"],
        )
        assert_allclose(result, 41.0, rtol=1e-3)

    def test_senza_variabili(self):
        """E=20, G1=10, G2=5, Q=[].
        F = 20+10+5 = 35.
        """
        result = seismic_combination(
            E=20.0, G1=10.0, G2=5.0, Q=[], categories=[],
        )
        assert_allclose(result, 35.0, rtol=1e-3)

    def test_con_precompressione(self):
        """E=20, G1=10, G2=5, Q=[8] cat A, P=3.
        F = 20+10+5+3+0.3*8 = 40.4.
        """
        result = seismic_combination(
            E=20.0, G1=10.0, G2=5.0, Q=[8.0], categories=["A"], P=3.0,
        )
        assert_allclose(result, 40.4, rtol=1e-3)

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_combination)
        assert ref is not None
        assert ref.formula == "2.5.5"


# ── [2.5.6] — Combinazione eccezionale ───────────────────────────────────────

class TestExceptionalCombination:
    """NTC18 §2.5.3, Formula [2.5.6]."""

    def test_base(self):
        """G1=10, G2=5, A_d=15, Q=[8, 6] cat [A, C].
        F = 10+5+15+0.3*8+0.6*6 = 36.0.
        """
        result = exceptional_combination(
            G1=10.0, G2=5.0, A_d=15.0, Q=[8.0, 6.0], categories=["A", "C"],
        )
        assert_allclose(result, 36.0, rtol=1e-3)

    def test_senza_variabili(self):
        """G1=10, G2=5, A_d=15.
        F = 10+5+15 = 30.
        """
        result = exceptional_combination(
            G1=10.0, G2=5.0, A_d=15.0, Q=[], categories=[],
        )
        assert_allclose(result, 30.0, rtol=1e-3)

    def test_ntc_ref(self):
        ref = get_ntc_ref(exceptional_combination)
        assert ref is not None
        assert ref.formula == "2.5.6"


# ── [2.5.7] — Masse sismiche ─────────────────────────────────────────────────

class TestSeismicMasses:
    """NTC18 §2.5.3, Formula [2.5.7]."""

    def test_base(self):
        """G1=10, G2=5, Q=[8, 6] cat [A, C].
        W = 10+5+0.3*8+0.6*6 = 21.0.
        """
        result = seismic_masses(
            G1=10.0, G2=5.0, Q=[8.0, 6.0], categories=["A", "C"],
        )
        assert_allclose(result, 21.0, rtol=1e-3)

    def test_senza_variabili(self):
        """G1=10, G2=5, Q=[].
        W = 10+5 = 15.
        """
        result = seismic_masses(G1=10.0, G2=5.0, Q=[], categories=[])
        assert_allclose(result, 15.0, rtol=1e-3)

    def test_cat_E(self):
        """G1=10, G2=5, Q=[8] cat E.
        W = 10+5+0.8*8 = 21.4.
        """
        result = seismic_masses(G1=10.0, G2=5.0, Q=[8.0], categories=["E"])
        assert_allclose(result, 21.4, rtol=1e-3)

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_masses)
        assert ref is not None
        assert ref.formula == "2.5.7"
