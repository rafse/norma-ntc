"""Test per actions/loads — NTC18 §3.1.

Copre:
- Tab. 3.1.I  — pesi unita' di volume dei materiali
- §3.1.3      — carico equivalente partizioni interne
- Tab. 3.1.II — sovraccarichi per categoria d'uso
- [3.1.1]     — coefficiente riduttivo alpha_A (area d'influenza)
- [3.1.2]     — coefficiente riduttivo alpha_n (numero piani)
"""

import pytest
from numpy.testing import assert_allclose

from pyntc.actions.loads import (
    unit_weight,
    partition_equivalent_load,
    variable_load,
    area_reduction_factor,
    floor_reduction_factor,
)
from pyntc.core.reference import get_ntc_ref


# ── Tab. 3.1.I — Pesi unita' di volume ──────────────────────────────────────

class TestUnitWeight:
    """NTC18 §3.1.2, Tab. 3.1.I — Pesi unita' di volume dei materiali."""

    @pytest.mark.parametrize("material, expected", [
        ("calcestruzzo_ordinario", 24.0),
        ("calcestruzzo_armato", 25.0),
        ("malta_calce", 18.0),
        ("malta_cemento", 21.0),
        ("calce_polvere", 10.0),
        ("cemento_polvere", 14.0),
        ("sabbia", 17.0),
        ("acciaio", 78.5),
        ("ghisa", 72.5),
        ("alluminio", 27.0),
        ("tufo_vulcanico", 17.0),
        ("calcare_compatto", 26.0),
        ("calcare_tenero", 22.0),
        ("gesso", 13.0),
        ("granito", 27.0),
        ("laterizio_pieno", 18.0),
        ("acqua_dolce", 9.81),
        ("acqua_mare", 10.1),
        ("carta", 10.0),
        ("vetro", 25.0),
    ])
    def test_valori_tabellati(self, material, expected):
        """Verifica ogni valore di Tab. 3.1.I."""
        assert_allclose(unit_weight(material), expected, rtol=1e-3)

    def test_materiale_sconosciuto(self):
        """Materiale non in tabella deve sollevare ValueError."""
        with pytest.raises(ValueError, match="materiale"):
            unit_weight("unobtanium")

    def test_ntc_ref(self):
        """Verifica riferimento normativo."""
        ref = get_ntc_ref(unit_weight)
        assert ref is not None
        assert ref.article == "3.1.2"
        assert ref.table == "Tab.3.1.I"


# ── §3.1.3 — Carico equivalente partizioni ──────────────────────────────────

class TestPartitionEquivalentLoad:
    """NTC18 §3.1.3 — Carico equivalente distribuito delle partizioni."""

    @pytest.mark.parametrize("weight_per_m, expected_g2", [
        (0.50, 0.40),   # G2 <= 1.00 kN/m
        (1.00, 0.40),   # G2 <= 1.00 kN/m (limite)
        (1.50, 0.80),   # 1.00 < G2 <= 2.00 kN/m
        (2.00, 0.80),   # 1.00 < G2 <= 2.00 kN/m (limite)
        (2.50, 1.20),   # 2.00 < G2 <= 3.00 kN/m
        (3.00, 1.20),   # 2.00 < G2 <= 3.00 kN/m (limite)
        (3.50, 1.60),   # 3.00 < G2 <= 4.00 kN/m
        (4.00, 1.60),   # 3.00 < G2 <= 4.00 kN/m (limite)
        (4.50, 2.00),   # 4.00 < G2 <= 5.00 kN/m
        (5.00, 2.00),   # 4.00 < G2 <= 5.00 kN/m (limite)
    ])
    def test_scaglioni(self, weight_per_m, expected_g2):
        """Verifica i 5 scaglioni definiti al §3.1.3."""
        assert_allclose(
            partition_equivalent_load(weight_per_m), expected_g2, rtol=1e-3
        )

    def test_peso_superiore_a_5(self):
        """Partizione > 5.00 kN/m: deve essere valutata caso per caso."""
        with pytest.raises(ValueError, match="5"):
            partition_equivalent_load(5.50)

    def test_peso_negativo(self):
        """Peso negativo non ammesso."""
        with pytest.raises(ValueError):
            partition_equivalent_load(-1.0)

    def test_ntc_ref(self):
        """Verifica riferimento normativo."""
        ref = get_ntc_ref(partition_equivalent_load)
        assert ref is not None
        assert ref.article == "3.1.3"


# ── Tab. 3.1.II — Sovraccarichi per categoria d'uso ─────────────────────────

class TestVariableLoad:
    """NTC18 §3.1.4, Tab. 3.1.II — Sovraccarichi per categoria d'uso."""

    @pytest.mark.parametrize("category, expected_qk, expected_Qk, expected_Hk", [
        ("A",  2.00,  2.00, 1.00),
        ("B1", 2.00,  2.00, 1.00),
        ("B2", 3.00,  2.00, 1.00),
        ("C1", 3.00,  3.00, 1.00),
        ("C2", 4.00,  4.00, 2.00),
        ("C3", 5.00,  5.00, 3.00),
        ("C4", 5.00,  5.00, 3.00),
        ("C5", 5.00,  5.00, 3.00),
        ("D1", 4.00,  4.00, 2.00),
        ("D2", 5.00,  5.00, 2.00),
        ("F",  2.50, 10.00, 1.00),
        ("G",  5.00, 50.00, 1.00),
        ("H",  0.50,  1.20, 1.00),
    ])
    def test_valori_tabellati(self, category, expected_qk, expected_Qk, expected_Hk):
        """Verifica i valori di Tab. 3.1.II per ogni categoria."""
        qk, Qk, Hk = variable_load(category)
        assert_allclose(qk, expected_qk, rtol=1e-3)
        assert_allclose(Qk, expected_Qk, rtol=1e-3)
        assert_allclose(Hk, expected_Hk, rtol=1e-3)

    def test_categoria_sconosciuta(self):
        """Categoria non valida deve sollevare ValueError."""
        with pytest.raises(ValueError, match="categoria"):
            variable_load("Z")

    def test_ntc_ref(self):
        """Verifica riferimento normativo."""
        ref = get_ntc_ref(variable_load)
        assert ref is not None
        assert ref.article == "3.1.4"
        assert ref.table == "Tab.3.1.II"


# ── [3.1.1] — Coefficiente riduttivo alpha_A ────────────────────────────────

class TestAreaReductionFactor:
    """NTC18 §3.1.4.1, Formula [3.1.1] — Riduzione per area d'influenza."""

    def test_formula_base(self):
        """alpha_A = 5/7 * psi_0 + 10/A, con psi_0=0.7, A=50 m2."""
        # alpha_A = 5/7 * 0.7 + 10/50 = 0.5 + 0.2 = 0.7
        result = area_reduction_factor(area=50.0, psi_0=0.7)
        assert_allclose(result, 0.7, rtol=1e-3)

    def test_capped_at_1(self):
        """alpha_A non puo' superare 1.0."""
        # area piccola -> valore alto -> capped a 1.0
        result = area_reduction_factor(area=5.0, psi_0=0.7)
        assert_allclose(result, 1.0, rtol=1e-3)

    def test_minimum_06_for_C_D(self):
        """Per categorie C e D, alpha_A >= 0.6."""
        # Con area molto grande e psi_0 basso -> valore basso
        # alpha_A = 5/7 * 0.7 + 10/1000 = 0.5 + 0.01 = 0.51 -> 0.6 per cat C/D
        result = area_reduction_factor(area=1000.0, psi_0=0.7, category="C")
        assert_allclose(result, 0.6, rtol=1e-3)

    def test_no_minimum_for_A(self):
        """Per categoria A, alpha_A puo' scendere sotto 0.6."""
        result = area_reduction_factor(area=1000.0, psi_0=0.7, category="A")
        expected = 5 / 7 * 0.7 + 10 / 1000  # ~0.51
        assert_allclose(result, expected, rtol=1e-3)

    def test_area_zero_raises(self):
        """Area nulla o negativa non ammessa."""
        with pytest.raises(ValueError):
            area_reduction_factor(area=0.0, psi_0=0.7)

    def test_ntc_ref(self):
        """Verifica riferimento normativo."""
        ref = get_ntc_ref(area_reduction_factor)
        assert ref is not None
        assert ref.article == "3.1.4.1"
        assert ref.formula == "3.1.1"


# ── [3.1.2] — Coefficiente riduttivo alpha_n ────────────────────────────────

class TestFloorReductionFactor:
    """NTC18 §3.1.4.1, Formula [3.1.2] — Riduzione per numero piani."""

    def test_formula_base(self):
        """alpha_n = (2 + (n-2)*psi_0) / n, con n=5, psi_0=0.7."""
        # alpha_n = (2 + 3*0.7) / 5 = (2 + 2.1) / 5 = 4.1 / 5 = 0.82
        result = floor_reduction_factor(n_floors=5, psi_0=0.7)
        assert_allclose(result, 0.82, rtol=1e-3)

    def test_n_equals_2(self):
        """Con n=2, alpha_n = 2/2 = 1.0 (nessuna riduzione)."""
        result = floor_reduction_factor(n_floors=2, psi_0=0.7)
        assert_allclose(result, 1.0, rtol=1e-3)

    def test_n_less_than_3_raises(self):
        """Formula applicabile solo con n > 2."""
        with pytest.raises(ValueError, match="3"):
            floor_reduction_factor(n_floors=1, psi_0=0.7)

    def test_ntc_ref(self):
        """Verifica riferimento normativo."""
        ref = get_ntc_ref(floor_reduction_factor)
        assert ref is not None
        assert ref.article == "3.1.4.1"
        assert ref.formula == "3.1.2"
