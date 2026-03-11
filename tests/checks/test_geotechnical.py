"""Test per geotechnical — NTC18 Cap.6 Progettazione geotecnica."""

import pytest
import numpy as np
from numpy.testing import assert_allclose

from pyntc.checks.geotechnical import (
    geo_action_partial_factors,
    geo_material_partial_factors,
    geo_uplift_partial_factors,
    geo_uplift_check,
    geo_sifonamento_check,
    geo_design_resistance,
    geo_design_check,
    geo_destabilising_force,
    geo_shallow_foundation_factors,
    geo_pile_resistance_factors,
    geo_pile_correlation_static,
    geo_pile_correlation_profiles,
    geo_pile_correlation_dynamic,
    geo_pile_characteristic_resistance,
    geo_pile_transverse_factor,
    geo_retaining_wall_factors,
    geo_anchor_resistance_factors,
    geo_anchor_correlation_tests,
    geo_anchor_correlation_profiles,
    geo_anchor_characteristic_resistance,
    geo_embankment_resistance_factor,
)
from pyntc.core.reference import get_ntc_ref


# ---------------------------------------------------------------------------
# 1. geo_action_partial_factors — Tab. 6.2.1
# ---------------------------------------------------------------------------
class TestGeoActionPartialFactors:
    """NTC18 §6.2.4.1.1 — Coefficienti parziali per le azioni."""

    def test_G1_unfavorable_EQU(self):
        """Tab.6.2.1: G1 sfavorevole in EQU = 1.1."""
        assert_allclose(geo_action_partial_factors("G1", "unfavorable", "EQU"), 1.1)

    def test_G1_favorable_EQU(self):
        """Tab.6.2.1: G1 favorevole in EQU = 0.9."""
        assert_allclose(geo_action_partial_factors("G1", "favorable", "EQU"), 0.9)

    def test_G1_unfavorable_A1(self):
        """Tab.6.2.1: G1 sfavorevole in A1 = 1.3."""
        assert_allclose(geo_action_partial_factors("G1", "unfavorable", "A1"), 1.3)

    def test_G1_favorable_A1(self):
        """Tab.6.2.1: G1 favorevole in A1 = 1.0."""
        assert_allclose(geo_action_partial_factors("G1", "favorable", "A1"), 1.0)

    def test_G1_unfavorable_A2(self):
        """Tab.6.2.1: G1 sfavorevole in A2 = 1.0."""
        assert_allclose(geo_action_partial_factors("G1", "unfavorable", "A2"), 1.0)

    def test_G2_unfavorable_A1(self):
        """Tab.6.2.1: G2 sfavorevole in A1 = 1.5."""
        assert_allclose(geo_action_partial_factors("G2", "unfavorable", "A1"), 1.5)

    def test_G2_favorable_A2(self):
        """Tab.6.2.1: G2 favorevole in A2 = 0.8."""
        assert_allclose(geo_action_partial_factors("G2", "favorable", "A2"), 0.8)

    def test_Q_unfavorable_A1(self):
        """Tab.6.2.1: Q sfavorevole in A1 = 1.5."""
        assert_allclose(geo_action_partial_factors("Q", "unfavorable", "A1"), 1.5)

    def test_Q_favorable_A1(self):
        """Tab.6.2.1: Q favorevole in A1 = 0.0."""
        assert_allclose(geo_action_partial_factors("Q", "favorable", "A1"), 0.0)

    def test_Q_unfavorable_A2(self):
        """Tab.6.2.1: Q sfavorevole in A2 = 1.3."""
        assert_allclose(geo_action_partial_factors("Q", "unfavorable", "A2"), 1.3)

    def test_invalid_load_type(self):
        """Tipo carico invalido."""
        with pytest.raises(ValueError):
            geo_action_partial_factors("G3", "unfavorable", "A1")

    def test_invalid_combination(self):
        """Combinazione invalida."""
        with pytest.raises(ValueError):
            geo_action_partial_factors("G1", "unfavorable", "X1")

    def test_ntc_ref(self):
        ref = get_ntc_ref(geo_action_partial_factors)
        assert ref is not None
        assert ref.article == "6.2.4.1.1"


# ---------------------------------------------------------------------------
# 2. geo_material_partial_factors — Tab. 6.2.II
# ---------------------------------------------------------------------------
class TestGeoMaterialPartialFactors:
    """NTC18 §6.2.4.1.2 — Coefficienti parziali per parametri geotecnici."""

    def test_tan_phi_M1(self):
        """Tab.6.2.II: tan(phi') in M1 = 1.0."""
        assert_allclose(geo_material_partial_factors("tan_phi", "M1"), 1.0)

    def test_tan_phi_M2(self):
        """Tab.6.2.II: tan(phi') in M2 = 1.25."""
        assert_allclose(geo_material_partial_factors("tan_phi", "M2"), 1.25)

    def test_cohesion_M2(self):
        """Tab.6.2.II: c' in M2 = 1.25."""
        assert_allclose(geo_material_partial_factors("cohesion", "M2"), 1.25)

    def test_undrained_M2(self):
        """Tab.6.2.II: c_u in M2 = 1.4."""
        assert_allclose(geo_material_partial_factors("undrained", "M2"), 1.4)

    def test_unit_weight_M2(self):
        """Tab.6.2.II: gamma in M2 = 1.0."""
        assert_allclose(geo_material_partial_factors("unit_weight", "M2"), 1.0)

    def test_all_M1_are_unity(self):
        """Tab.6.2.II: tutti M1 = 1.0."""
        for param in ("tan_phi", "cohesion", "undrained", "unit_weight"):
            assert_allclose(geo_material_partial_factors(param, "M1"), 1.0)

    def test_invalid_parameter(self):
        with pytest.raises(ValueError):
            geo_material_partial_factors("friction", "M1")

    def test_ntc_ref(self):
        ref = get_ntc_ref(geo_material_partial_factors)
        assert ref is not None
        assert ref.article == "6.2.4.1.2"


# ---------------------------------------------------------------------------
# 3. geo_uplift_partial_factors — Tab. 6.2.III
# ---------------------------------------------------------------------------
class TestGeoUpliftPartialFactors:
    """NTC18 §6.2.4.2 — Coefficienti parziali per sollevamento (UPL)."""

    def test_G1_favorable(self):
        """Tab.6.2.III: G1 favorevole UPL = 0.9."""
        assert_allclose(geo_uplift_partial_factors("G1", "favorable"), 0.9)

    def test_G1_unfavorable(self):
        """Tab.6.2.III: G1 sfavorevole UPL = 1.1."""
        assert_allclose(geo_uplift_partial_factors("G1", "unfavorable"), 1.1)

    def test_G2_favorable(self):
        """Tab.6.2.III: G2 favorevole UPL = 0.8."""
        assert_allclose(geo_uplift_partial_factors("G2", "favorable"), 0.8)

    def test_G2_unfavorable(self):
        """Tab.6.2.III: G2 sfavorevole UPL = 1.5."""
        assert_allclose(geo_uplift_partial_factors("G2", "unfavorable"), 1.5)

    def test_Q_favorable(self):
        """Tab.6.2.III: Q favorevole UPL = 0.0."""
        assert_allclose(geo_uplift_partial_factors("Q", "favorable"), 0.0)

    def test_Q_unfavorable(self):
        """Tab.6.2.III: Q sfavorevole UPL = 1.5."""
        assert_allclose(geo_uplift_partial_factors("Q", "unfavorable"), 1.5)

    def test_ntc_ref(self):
        ref = get_ntc_ref(geo_uplift_partial_factors)
        assert ref is not None
        assert ref.article == "6.2.4.2"


# ---------------------------------------------------------------------------
# 4. geo_uplift_check — [6.2.4]
# ---------------------------------------------------------------------------
class TestGeoUpliftCheck:
    """NTC18 §6.2.4.2 — Verifica al sollevamento [6.2.4]."""

    def test_safe(self):
        """V_inst,d < G_stb,d + R_d => verificato."""
        ok, ratio = geo_uplift_check(100.0, 80.0, 30.0)
        assert ok is True
        assert_allclose(ratio, 100.0 / 110.0, rtol=1e-10)

    def test_unsafe(self):
        """V_inst,d > G_stb,d + R_d => non verificato."""
        ok, ratio = geo_uplift_check(200.0, 80.0, 30.0)
        assert ok is False
        assert_allclose(ratio, 200.0 / 110.0, rtol=1e-10)

    def test_exact_limit(self):
        """V_inst,d == G_stb,d + R_d => verificato (<=)."""
        ok, ratio = geo_uplift_check(110.0, 80.0, 30.0)
        assert ok is True
        assert_allclose(ratio, 1.0)

    def test_negative_raises(self):
        """Valori negativi non ammessi."""
        with pytest.raises(ValueError):
            geo_uplift_check(-10.0, 80.0, 30.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(geo_uplift_check)
        assert ref is not None
        assert "6.2.4" in ref.formula


# ---------------------------------------------------------------------------
# 5. geo_sifonamento_check — §6.2.4.2
# ---------------------------------------------------------------------------
class TestGeoSifonamentoCheck:
    """NTC18 §6.2.4.2 — Verifica al sifonamento."""

    def test_mean_gradient_safe(self):
        """Gradiente medio: i <= i_c/3 => verificato."""
        ok, ratio = geo_sifonamento_check(0.3, 1.0, "mean")
        assert ok is True
        assert_allclose(ratio, 0.3 / (1.0 / 3.0), rtol=1e-10)

    def test_mean_gradient_unsafe(self):
        """Gradiente medio: i > i_c/3 => non verificato."""
        ok, ratio = geo_sifonamento_check(0.5, 1.0, "mean")
        assert ok is False

    def test_outflow_gradient_safe(self):
        """Gradiente efflusso: i <= i_c/2 => verificato."""
        ok, ratio = geo_sifonamento_check(0.4, 1.0, "outflow")
        assert ok is True
        assert_allclose(ratio, 0.4 / 0.5, rtol=1e-10)

    def test_outflow_gradient_unsafe(self):
        """Gradiente efflusso: i > i_c/2 => non verificato."""
        ok, ratio = geo_sifonamento_check(0.6, 1.0, "outflow")
        assert ok is False

    def test_excess_pressure_safe(self):
        """Pressione in eccesso: delta_u <= sigma'_v/2 => verificato."""
        ok, ratio = geo_sifonamento_check(40.0, 100.0, "excess_pressure")
        assert ok is True
        assert_allclose(ratio, 40.0 / 50.0, rtol=1e-10)

    def test_invalid_type(self):
        with pytest.raises(ValueError):
            geo_sifonamento_check(0.3, 1.0, "invalid")

    def test_ntc_ref(self):
        ref = get_ntc_ref(geo_sifonamento_check)
        assert ref is not None
        assert ref.article == "6.2.4.2"


# ---------------------------------------------------------------------------
# 6. geo_design_resistance — [6.2.3]
# ---------------------------------------------------------------------------
class TestGeoDesignResistance:
    """NTC18 §6.2.4.1.2 — Resistenza di progetto [6.2.3]."""

    def test_basic(self):
        """R_d = R_k / gamma_R."""
        assert_allclose(geo_design_resistance(230.0, 2.3), 100.0, rtol=1e-10)

    def test_unity_factor(self):
        """gamma_R = 1.0 => R_d = R_k."""
        assert_allclose(geo_design_resistance(100.0, 1.0), 100.0)

    def test_pile_factor(self):
        """R_d = 1000 / 1.35 per palo trivellato base."""
        assert_allclose(geo_design_resistance(1000.0, 1.35), 1000.0 / 1.35, rtol=1e-10)

    def test_zero_resistance_raises(self):
        """R_k negativa non ammessa."""
        with pytest.raises(ValueError):
            geo_design_resistance(-100.0, 1.3)

    def test_ntc_ref(self):
        ref = get_ntc_ref(geo_design_resistance)
        assert ref is not None
        assert ref.formula == "6.2.3"


# ---------------------------------------------------------------------------
# 7. geo_design_check — [6.2.1]
# ---------------------------------------------------------------------------
class TestGeoDesignCheck:
    """NTC18 §6.2.4.1 — Verifica E_d <= R_d [6.2.1]."""

    def test_safe(self):
        """E_d < R_d => verificato."""
        ok, ratio = geo_design_check(80.0, 100.0)
        assert ok is True
        assert_allclose(ratio, 0.8)

    def test_unsafe(self):
        """E_d > R_d => non verificato."""
        ok, ratio = geo_design_check(120.0, 100.0)
        assert ok is False
        assert_allclose(ratio, 1.2)

    def test_exact_limit(self):
        """E_d == R_d => verificato."""
        ok, _ = geo_design_check(100.0, 100.0)
        assert ok is True

    def test_zero_resistance_raises(self):
        with pytest.raises(ValueError):
            geo_design_check(100.0, 0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(geo_design_check)
        assert ref is not None
        assert ref.formula == "6.2.1"


# ---------------------------------------------------------------------------
# 8. geo_shallow_foundation_factors — Tab. 6.4.1
# ---------------------------------------------------------------------------
class TestGeoShallowFoundationFactors:
    """NTC18 §6.4.2.1 — Coefficienti R3 per fondazioni superficiali."""

    def test_bearing_capacity(self):
        """Tab.6.4.1: carico limite R3 = 2.3."""
        assert_allclose(geo_shallow_foundation_factors("bearing"), 2.3)

    def test_sliding(self):
        """Tab.6.4.1: scorrimento R3 = 1.1."""
        assert_allclose(geo_shallow_foundation_factors("sliding"), 1.1)

    def test_invalid(self):
        with pytest.raises(ValueError):
            geo_shallow_foundation_factors("overturning")

    def test_ntc_ref(self):
        ref = get_ntc_ref(geo_shallow_foundation_factors)
        assert ref is not None
        assert ref.article == "6.4.2.1"


# ---------------------------------------------------------------------------
# 9. geo_pile_resistance_factors — Tab. 6.4.II
# ---------------------------------------------------------------------------
class TestGeoPileResistanceFactors:
    """NTC18 §6.4.3.1.1 — Coefficienti R3 per pali."""

    def test_base_driven(self):
        """Tab.6.4.II: base pali infissi R3 = 1.15."""
        assert_allclose(geo_pile_resistance_factors("base", "driven"), 1.15)

    def test_base_bored(self):
        """Tab.6.4.II: base pali trivellati R3 = 1.35."""
        assert_allclose(geo_pile_resistance_factors("base", "bored"), 1.35)

    def test_base_cfa(self):
        """Tab.6.4.II: base pali CFA R3 = 1.3."""
        assert_allclose(geo_pile_resistance_factors("base", "cfa"), 1.3)

    def test_shaft_bored(self):
        """Tab.6.4.II: laterale compressione trivellati R3 = 1.15."""
        assert_allclose(geo_pile_resistance_factors("shaft", "bored"), 1.15)

    def test_total_bored(self):
        """Tab.6.4.II: totale trivellati R3 = 1.30."""
        assert_allclose(geo_pile_resistance_factors("total", "bored"), 1.30)

    def test_total_cfa(self):
        """Tab.6.4.II: totale CFA R3 = 1.25."""
        assert_allclose(geo_pile_resistance_factors("total", "cfa"), 1.25)

    def test_shaft_tension(self):
        """Tab.6.4.II: laterale trazione R3 = 1.25 per tutti."""
        for ptype in ("driven", "bored", "cfa"):
            assert_allclose(geo_pile_resistance_factors("shaft_tension", ptype), 1.25)

    def test_invalid_resistance(self):
        with pytest.raises(ValueError):
            geo_pile_resistance_factors("tip", "driven")

    def test_ntc_ref(self):
        ref = get_ntc_ref(geo_pile_resistance_factors)
        assert ref is not None
        assert ref.article == "6.4.3.1.1"


# ---------------------------------------------------------------------------
# 10. geo_pile_correlation_static — Tab. 6.4.III
# ---------------------------------------------------------------------------
class TestGeoPileCorrelationStatic:
    """NTC18 §6.4.3.1.1 — Fattori xi da prove di carico statiche."""

    def test_1_test(self):
        """Tab.6.4.III: n=1 => xi1=1.40, xi2=1.40."""
        xi1, xi2 = geo_pile_correlation_static(1)
        assert_allclose(xi1, 1.40)
        assert_allclose(xi2, 1.40)

    def test_2_tests(self):
        """Tab.6.4.III: n=2 => xi1=1.30, xi2=1.20."""
        xi1, xi2 = geo_pile_correlation_static(2)
        assert_allclose(xi1, 1.30)
        assert_allclose(xi2, 1.20)

    def test_3_tests(self):
        """Tab.6.4.III: n=3 => xi1=1.20, xi2=1.05."""
        xi1, xi2 = geo_pile_correlation_static(3)
        assert_allclose(xi1, 1.20)
        assert_allclose(xi2, 1.05)

    def test_4_tests(self):
        """Tab.6.4.III: n=4 => xi1=1.10, xi2=1.00."""
        xi1, xi2 = geo_pile_correlation_static(4)
        assert_allclose(xi1, 1.10)
        assert_allclose(xi2, 1.00)

    def test_5_or_more(self):
        """Tab.6.4.III: n>=5 => xi1=1.00, xi2=1.00."""
        xi1, xi2 = geo_pile_correlation_static(5)
        assert_allclose(xi1, 1.00)
        assert_allclose(xi2, 1.00)
        xi1, xi2 = geo_pile_correlation_static(10)
        assert_allclose(xi1, 1.00)

    def test_zero_raises(self):
        with pytest.raises(ValueError):
            geo_pile_correlation_static(0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(geo_pile_correlation_static)
        assert ref is not None
        assert "6.4.III" in (ref.table or "")


# ---------------------------------------------------------------------------
# 11. geo_pile_correlation_profiles — Tab. 6.4.IV
# ---------------------------------------------------------------------------
class TestGeoPileCorrelationProfiles:
    """NTC18 §6.4.3.1.1 — Fattori xi da verticali di indagine."""

    def test_1_profile(self):
        """Tab.6.4.IV: n=1 => xi3=1.70, xi4=1.70."""
        xi3, xi4 = geo_pile_correlation_profiles(1)
        assert_allclose(xi3, 1.70)
        assert_allclose(xi4, 1.70)

    def test_3_profiles(self):
        """Tab.6.4.IV: n=3 => xi3=1.60, xi4=1.48."""
        xi3, xi4 = geo_pile_correlation_profiles(3)
        assert_allclose(xi3, 1.60)
        assert_allclose(xi4, 1.48)

    def test_5_profiles(self):
        """Tab.6.4.IV: n=5 => xi3=1.50, xi4=1.34."""
        xi3, xi4 = geo_pile_correlation_profiles(5)
        assert_allclose(xi3, 1.50)
        assert_allclose(xi4, 1.34)

    def test_7_profiles(self):
        """Tab.6.4.IV: n=7 => xi3=1.45, xi4=1.28."""
        xi3, xi4 = geo_pile_correlation_profiles(7)
        assert_allclose(xi3, 1.45)
        assert_allclose(xi4, 1.28)

    def test_10_or_more(self):
        """Tab.6.4.IV: n>=10 => xi3=1.40, xi4=1.21."""
        xi3, xi4 = geo_pile_correlation_profiles(10)
        assert_allclose(xi3, 1.40)
        assert_allclose(xi4, 1.21)

    def test_interpolation_6(self):
        """Tab.6.4.IV: n=6 => interpolazione lineare tra n=5 e n=7."""
        xi3, xi4 = geo_pile_correlation_profiles(6)
        # xi3: lerp(1.50, 1.45, 0.5) = 1.475
        assert_allclose(xi3, 1.475, rtol=1e-3)
        # xi4: lerp(1.34, 1.28, 0.5) = 1.31
        assert_allclose(xi4, 1.31, rtol=1e-3)

    def test_zero_raises(self):
        with pytest.raises(ValueError):
            geo_pile_correlation_profiles(0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(geo_pile_correlation_profiles)
        assert ref is not None
        assert "6.4.IV" in (ref.table or "")


# ---------------------------------------------------------------------------
# 12. geo_pile_correlation_dynamic — Tab. 6.4.V
# ---------------------------------------------------------------------------
class TestGeoPileCorrelationDynamic:
    """NTC18 §6.4.3.1.1 — Fattori xi da prove dinamiche."""

    def test_2_tests(self):
        """Tab.6.4.V: n>=2 => xi5=1.60, xi6=1.50."""
        xi5, xi6 = geo_pile_correlation_dynamic(2)
        assert_allclose(xi5, 1.60)
        assert_allclose(xi6, 1.50)

    def test_5_tests(self):
        """Tab.6.4.V: n>=5 => xi5=1.50, xi6=1.35."""
        xi5, xi6 = geo_pile_correlation_dynamic(5)
        assert_allclose(xi5, 1.50)
        assert_allclose(xi6, 1.35)

    def test_10_tests(self):
        """Tab.6.4.V: n>=10 => xi5=1.45, xi6=1.30."""
        xi5, xi6 = geo_pile_correlation_dynamic(10)
        assert_allclose(xi5, 1.45)
        assert_allclose(xi6, 1.30)

    def test_15_tests(self):
        """Tab.6.4.V: n>=15 => xi5=1.42, xi6=1.25."""
        xi5, xi6 = geo_pile_correlation_dynamic(15)
        assert_allclose(xi5, 1.42)
        assert_allclose(xi6, 1.25)

    def test_20_tests(self):
        """Tab.6.4.V: n>=20 => xi5=1.40, xi6=1.25."""
        xi5, xi6 = geo_pile_correlation_dynamic(20)
        assert_allclose(xi5, 1.40)
        assert_allclose(xi6, 1.25)

    def test_large_n(self):
        """n=50 => stessi valori di n>=20."""
        xi5, xi6 = geo_pile_correlation_dynamic(50)
        assert_allclose(xi5, 1.40)
        assert_allclose(xi6, 1.25)

    def test_1_test_raises(self):
        """Minimo 2 prove."""
        with pytest.raises(ValueError):
            geo_pile_correlation_dynamic(1)

    def test_ntc_ref(self):
        ref = get_ntc_ref(geo_pile_correlation_dynamic)
        assert ref is not None
        assert "6.4.V" in (ref.table or "")


# ---------------------------------------------------------------------------
# 13. geo_pile_characteristic_resistance — [6.4.1]-[6.4.5]
# ---------------------------------------------------------------------------
class TestGeoPileCharacteristicResistance:
    """NTC18 §6.4.3.1.1 — Resistenza caratteristica pali."""

    def test_static_single_test(self):
        """[6.4.1]: una prova R=1000 => R_ck = 1000/1.40."""
        R_ck = geo_pile_characteristic_resistance([1000.0], "static")
        assert_allclose(R_ck, 1000.0 / 1.40, rtol=1e-3)

    def test_static_two_tests(self):
        """[6.4.1]: due prove R=[1000, 900] => min(media/xi1, min/xi2)."""
        R_ck = geo_pile_characteristic_resistance([1000.0, 900.0], "static")
        mean_val = 950.0
        min_val = 900.0
        expected = min(mean_val / 1.30, min_val / 1.20)
        assert_allclose(R_ck, expected, rtol=1e-3)

    def test_profiles_single(self):
        """[6.4.3]: un profilo R=500 => R_ck = 500/1.70."""
        R_ck = geo_pile_characteristic_resistance([500.0], "profiles")
        assert_allclose(R_ck, 500.0 / 1.70, rtol=1e-3)

    def test_profiles_three(self):
        """[6.4.3]: tre profili R=[600, 500, 550]."""
        R_ck = geo_pile_characteristic_resistance([600.0, 500.0, 550.0], "profiles")
        mean_val = 550.0
        min_val = 500.0
        expected = min(mean_val / 1.60, min_val / 1.48)
        assert_allclose(R_ck, expected, rtol=1e-3)

    def test_dynamic_two_tests(self):
        """[6.4.5]: due prove R=[800, 700]."""
        R_ck = geo_pile_characteristic_resistance([800.0, 700.0], "dynamic")
        mean_val = 750.0
        min_val = 700.0
        expected = min(mean_val / 1.60, min_val / 1.50)
        assert_allclose(R_ck, expected, rtol=1e-3)

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            geo_pile_characteristic_resistance([], "static")

    def test_invalid_method(self):
        with pytest.raises(ValueError):
            geo_pile_characteristic_resistance([100.0], "unknown")

    def test_ntc_ref(self):
        ref = get_ntc_ref(geo_pile_characteristic_resistance)
        assert ref is not None
        assert ref.article == "6.4.3.1.1"


# ---------------------------------------------------------------------------
# 14. geo_pile_transverse_factor — Tab. 6.4.VI
# ---------------------------------------------------------------------------
class TestGeoPileTransverseFactor:
    """NTC18 §6.4.3.1.2 — Coefficiente per carichi trasversali."""

    def test_value(self):
        """Tab.6.4.VI: gamma_T R3 = 1.3."""
        assert_allclose(geo_pile_transverse_factor(), 1.3)

    def test_ntc_ref(self):
        ref = get_ntc_ref(geo_pile_transverse_factor)
        assert ref is not None
        assert ref.article == "6.4.3.1.2"


# ---------------------------------------------------------------------------
# 15. geo_retaining_wall_factors — Tab. 6.5.1
# ---------------------------------------------------------------------------
class TestGeoRetainingWallFactors:
    """NTC18 §6.5.3.1.1 — Coefficienti R3 per muri di sostegno."""

    def test_bearing(self):
        """Tab.6.5.1: capacita' portante R3 = 1.4."""
        assert_allclose(geo_retaining_wall_factors("bearing"), 1.4)

    def test_sliding(self):
        """Tab.6.5.1: scorrimento R3 = 1.1."""
        assert_allclose(geo_retaining_wall_factors("sliding"), 1.1)

    def test_overturning(self):
        """Tab.6.5.1: ribaltamento R3 = 1.15."""
        assert_allclose(geo_retaining_wall_factors("overturning"), 1.15)

    def test_passive_resistance(self):
        """Tab.6.5.1: resistenza terreno a valle R3 = 1.4."""
        assert_allclose(geo_retaining_wall_factors("passive"), 1.4)

    def test_invalid(self):
        with pytest.raises(ValueError):
            geo_retaining_wall_factors("uplift")

    def test_ntc_ref(self):
        ref = get_ntc_ref(geo_retaining_wall_factors)
        assert ref is not None
        assert ref.article == "6.5.3.1.1"


# ---------------------------------------------------------------------------
# 16. geo_anchor_resistance_factors — Tab. 6.6.1
# ---------------------------------------------------------------------------
class TestGeoAnchorResistanceFactors:
    """NTC18 §6.6.2 — Coefficienti parziali per ancoraggi."""

    def test_temporary(self):
        """Tab.6.6.1: temporanei gamma_R = 1.1."""
        assert_allclose(geo_anchor_resistance_factors("temporary"), 1.1)

    def test_permanent(self):
        """Tab.6.6.1: permanenti gamma_R = 1.2."""
        assert_allclose(geo_anchor_resistance_factors("permanent"), 1.2)

    def test_invalid(self):
        with pytest.raises(ValueError):
            geo_anchor_resistance_factors("provisional")

    def test_ntc_ref(self):
        ref = get_ntc_ref(geo_anchor_resistance_factors)
        assert ref is not None
        assert ref.article == "6.6.2"


# ---------------------------------------------------------------------------
# 17. geo_anchor_correlation_tests — Tab. 6.6.II
# ---------------------------------------------------------------------------
class TestGeoAnchorCorrelationTests:
    """NTC18 §6.6.2 — Fattori xi da prove su ancoraggi."""

    def test_1_test(self):
        """Tab.6.6.II: n=1 => xi_a1=1.5, xi_a2=1.5."""
        xi1, xi2 = geo_anchor_correlation_tests(1)
        assert_allclose(xi1, 1.5)
        assert_allclose(xi2, 1.5)

    def test_2_tests(self):
        """Tab.6.6.II: n=2 => xi_a1=1.4, xi_a2=1.3."""
        xi1, xi2 = geo_anchor_correlation_tests(2)
        assert_allclose(xi1, 1.4)
        assert_allclose(xi2, 1.3)

    def test_3_or_more(self):
        """Tab.6.6.II: n>2 => xi_a1=1.3, xi_a2=1.2."""
        xi1, xi2 = geo_anchor_correlation_tests(3)
        assert_allclose(xi1, 1.3)
        assert_allclose(xi2, 1.2)
        xi1, xi2 = geo_anchor_correlation_tests(10)
        assert_allclose(xi1, 1.3)

    def test_zero_raises(self):
        with pytest.raises(ValueError):
            geo_anchor_correlation_tests(0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(geo_anchor_correlation_tests)
        assert ref is not None
        assert "6.6.II" in (ref.table or "")


# ---------------------------------------------------------------------------
# 18. geo_anchor_correlation_profiles — Tab. 6.6.III
# ---------------------------------------------------------------------------
class TestGeoAnchorCorrelationProfiles:
    """NTC18 §6.6.2 — Fattori xi da profili di indagine per ancoraggi."""

    def test_1_profile(self):
        """Tab.6.6.III: n=1 => xi_a3=1.80, xi_a4=1.80."""
        xi3, xi4 = geo_anchor_correlation_profiles(1)
        assert_allclose(xi3, 1.80)
        assert_allclose(xi4, 1.80)

    def test_2_profiles(self):
        """Tab.6.6.III: n=2 => xi_a3=1.75, xi_a4=1.70."""
        xi3, xi4 = geo_anchor_correlation_profiles(2)
        assert_allclose(xi3, 1.75)
        assert_allclose(xi4, 1.70)

    def test_3_profiles(self):
        """Tab.6.6.III: n=3 => xi_a3=1.70, xi_a4=1.65."""
        xi3, xi4 = geo_anchor_correlation_profiles(3)
        assert_allclose(xi3, 1.70)
        assert_allclose(xi4, 1.65)

    def test_4_profiles(self):
        """Tab.6.6.III: n=4 => xi_a3=1.65, xi_a4=1.60."""
        xi3, xi4 = geo_anchor_correlation_profiles(4)
        assert_allclose(xi3, 1.65)
        assert_allclose(xi4, 1.60)

    def test_5_or_more(self):
        """Tab.6.6.III: n>=5 => xi_a3=1.60, xi_a4=1.55."""
        xi3, xi4 = geo_anchor_correlation_profiles(5)
        assert_allclose(xi3, 1.60)
        assert_allclose(xi4, 1.55)

    def test_zero_raises(self):
        with pytest.raises(ValueError):
            geo_anchor_correlation_profiles(0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(geo_anchor_correlation_profiles)
        assert ref is not None
        assert "6.6.III" in (ref.table or "")


# ---------------------------------------------------------------------------
# 19. geo_anchor_characteristic_resistance — [6.6.1]/[6.6.2]
# ---------------------------------------------------------------------------
class TestGeoAnchorCharacteristicResistance:
    """NTC18 §6.6.2 — Resistenza caratteristica ancoraggi."""

    def test_single_test(self):
        """[6.6.1]: una prova R=500 => R_ak = 500/1.5."""
        R_ak = geo_anchor_characteristic_resistance([500.0], "tests")
        assert_allclose(R_ak, 500.0 / 1.5, rtol=1e-3)

    def test_two_tests(self):
        """[6.6.1]: due prove R=[500, 400]."""
        R_ak = geo_anchor_characteristic_resistance([500.0, 400.0], "tests")
        mean_val = 450.0
        min_val = 400.0
        expected = min(mean_val / 1.4, min_val / 1.3)
        assert_allclose(R_ak, expected, rtol=1e-3)

    def test_profiles_single(self):
        """[6.6.2]: un profilo R=300 => R_ak = 300/1.80."""
        R_ak = geo_anchor_characteristic_resistance([300.0], "profiles")
        assert_allclose(R_ak, 300.0 / 1.80, rtol=1e-3)

    def test_profiles_three(self):
        """[6.6.2]: tre profili R=[300, 250, 280]."""
        R_ak = geo_anchor_characteristic_resistance([300.0, 250.0, 280.0], "profiles")
        mean_val = 276.6666666
        min_val = 250.0
        expected = min(mean_val / 1.70, min_val / 1.65)
        assert_allclose(R_ak, expected, rtol=1e-3)

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            geo_anchor_characteristic_resistance([], "tests")

    def test_invalid_method(self):
        with pytest.raises(ValueError):
            geo_anchor_characteristic_resistance([100.0], "unknown")

    def test_ntc_ref(self):
        ref = get_ntc_ref(geo_anchor_characteristic_resistance)
        assert ref is not None
        assert ref.article == "6.6.2"


# ---------------------------------------------------------------------------
# 20. geo_destabilising_force — [6.2.5]
# ---------------------------------------------------------------------------
class TestGeoDestabilisingForce:
    """NTC18 §6.2.4.2 — Forza instabilizzante [6.2.5]."""

    def test_basic(self):
        """V_inst,d = C_inst,d + Q_inst,d."""
        from numpy.testing import assert_allclose
        assert_allclose(geo_destabilising_force(80.0, 40.0), 120.0)

    def test_zero_variable(self):
        """Solo componente permanente."""
        from numpy.testing import assert_allclose
        assert_allclose(geo_destabilising_force(100.0, 0.0), 100.0)

    def test_zero_permanent(self):
        """Solo componente variabile."""
        from numpy.testing import assert_allclose
        assert_allclose(geo_destabilising_force(0.0, 50.0), 50.0)

    def test_negative_C_raises(self):
        """C_inst_d negativa non ammessa."""
        with pytest.raises(ValueError, match="C_inst_d"):
            geo_destabilising_force(-10.0, 20.0)

    def test_negative_Q_raises(self):
        """Q_inst_d negativa non ammessa."""
        with pytest.raises(ValueError, match="Q_inst_d"):
            geo_destabilising_force(10.0, -5.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(geo_destabilising_force)
        assert ref is not None
        assert ref.article == "6.2.4.2"
        assert ref.formula == "6.2.5"


# ---------------------------------------------------------------------------
# 21. geo_embankment_resistance_factor — Tab. 6.8.1
# ---------------------------------------------------------------------------
class TestGeoEmbankmentResistanceFactor:
    """NTC18 §6.8.2 — Coefficiente R2 per opere di materiali sciolti."""

    def test_value(self):
        """Tab.6.8.1: gamma_R R2 = 1.1."""
        assert_allclose(geo_embankment_resistance_factor(), 1.1)

    def test_ntc_ref(self):
        ref = get_ntc_ref(geo_embankment_resistance_factor)
        assert ref is not None
        assert ref.article == "6.8.2"
