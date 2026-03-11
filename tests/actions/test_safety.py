"""Test per safety — NTC18 Cap. 2.4 (vita nominale, classe d'uso, periodo di riferimento)."""

import pytest
from numpy.testing import assert_allclose

from pyntc.actions.safety import (
    safety_nominal_life,
    safety_usage_coefficient,
    reference_period,
)
from pyntc.core.reference import get_ntc_ref


# ---------------------------------------------------------------------------
# 1. safety_nominal_life — Tab. 2.4.I
# ---------------------------------------------------------------------------
class TestSafetyNominalLife:
    """NTC18 §2.4.1 — Vita nominale V_N."""

    def test_temporanea(self):
        """Tab.2.4.I: strutture temporanee V_N = 10 anni."""
        assert_allclose(safety_nominal_life("temporanea"), 10.0)

    def test_normale(self):
        """Tab.2.4.I: strutture ordinarie V_N = 50 anni."""
        assert_allclose(safety_nominal_life("normale"), 50.0)

    def test_strategica(self):
        """Tab.2.4.I: strutture strategiche V_N = 100 anni."""
        assert_allclose(safety_nominal_life("strategica"), 100.0)

    def test_invalid_type(self):
        """Tipo non riconosciuto solleva ValueError."""
        with pytest.raises(ValueError, match="Tipo di costruzione non valido"):
            safety_nominal_life("industriale")

    def test_ntc_ref(self):
        ref = get_ntc_ref(safety_nominal_life)
        assert ref is not None
        assert ref.article == "2.4.1"
        assert ref.table == "Tab.2.4.I"


# ---------------------------------------------------------------------------
# 2. safety_usage_coefficient — Tab. 2.4.II
# ---------------------------------------------------------------------------
class TestSafetyUsageCoefficient:
    """NTC18 §2.4.2 — Coefficiente d'uso C_U."""

    def test_class_I(self):
        """Tab.2.4.II: Classe I C_U = 0.7."""
        assert_allclose(safety_usage_coefficient("I"), 0.7)

    def test_class_II(self):
        """Tab.2.4.II: Classe II C_U = 1.0."""
        assert_allclose(safety_usage_coefficient("II"), 1.0)

    def test_class_III(self):
        """Tab.2.4.II: Classe III C_U = 1.5."""
        assert_allclose(safety_usage_coefficient("III"), 1.5)

    def test_class_IV(self):
        """Tab.2.4.II: Classe IV C_U = 2.0."""
        assert_allclose(safety_usage_coefficient("IV"), 2.0)

    def test_invalid_class(self):
        """Classe non riconosciuta solleva ValueError."""
        with pytest.raises(ValueError, match="Classe d'uso non valida"):
            safety_usage_coefficient("V")

    def test_ntc_ref(self):
        ref = get_ntc_ref(safety_usage_coefficient)
        assert ref is not None
        assert ref.article == "2.4.2"
        assert ref.table == "Tab.2.4.II"


# ---------------------------------------------------------------------------
# 3. reference_period — Formula 2.4.1
# ---------------------------------------------------------------------------
class TestReferencePeriod:
    """NTC18 §2.4.3 — Periodo di riferimento V_R [2.4.1]."""

    def test_classe_II_normale(self):
        """V_R = 50 * 1.0 = 50 anni (caso comune)."""
        assert_allclose(reference_period(50.0, 1.0), 50.0)

    def test_classe_IV_normale(self):
        """V_R = 50 * 2.0 = 100 anni."""
        assert_allclose(reference_period(50.0, 2.0), 100.0)

    def test_classe_I_normale(self):
        """V_R = 50 * 0.7 = 35 anni."""
        assert_allclose(reference_period(50.0, 0.7), 35.0)

    def test_strategica_classe_IV(self):
        """V_R = 100 * 2.0 = 200 anni."""
        assert_allclose(reference_period(100.0, 2.0), 200.0)

    def test_temporanea_classe_I(self):
        """V_R = 10 * 0.7 = 7 anni."""
        assert_allclose(reference_period(10.0, 0.7), 7.0)

    def test_combined_with_table_functions(self):
        """Integrazione: lookup tabelle + formula."""
        V_N = safety_nominal_life("normale")
        C_U = safety_usage_coefficient("III")
        assert_allclose(reference_period(V_N, C_U), 75.0)

    def test_zero_VN_raises(self):
        """V_N = 0 non ammesso."""
        with pytest.raises(ValueError, match="V_N"):
            reference_period(0.0, 1.0)

    def test_negative_VN_raises(self):
        """V_N negativa non ammessa."""
        with pytest.raises(ValueError, match="V_N"):
            reference_period(-10.0, 1.0)

    def test_zero_CU_raises(self):
        """C_U = 0 non ammesso."""
        with pytest.raises(ValueError, match="C_U"):
            reference_period(50.0, 0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(reference_period)
        assert ref is not None
        assert ref.article == "2.4.3"
        assert ref.formula == "2.4.1"
        assert r"V_R = V_N \cdot C_U" in ref.latex
