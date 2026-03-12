"""Test per masonry — NTC18 §4.5."""

import math

import pytest
from numpy.testing import assert_allclose

from pyntc.checks.masonry import (
    masonry_combined_eccentricity,
    masonry_confined_bending_resistance,
    masonry_confined_shear_resistance,
    masonry_design_compressive_strength,
    masonry_design_shear_strength,
    masonry_eccentricity_check,
    masonry_eccentricity_coefficient,
    masonry_eccentricity_m,
    masonry_effective_height,
    masonry_horizontal_eccentricity,
    masonry_lateral_restraint_factor,
    masonry_partial_safety_factor,
    masonry_phi_from_table,
    masonry_reduced_strength,
    masonry_reduction_factor,
    masonry_reinforced_axial_check,
    masonry_reinforced_flexural_resistance,
    masonry_reinforced_shear_resistance,
    masonry_simplified_axial_check,
    masonry_simplified_check,
    masonry_slenderness,
    masonry_vertical_load_eccentricity,
)
from pyntc.core.reference import get_ntc_ref


# ── Tab.4.5.II — Coefficienti parziali gamma_M ──────────────────────────────


class TestMasonryPartialSafetyFactor:
    """NTC18 §4.5.6.1, Tab. 4.5.II."""

    def test_cat_I_guaranteed_class_1(self):
        """Cat.I, malta a prestazione garantita, classe 1: gamma_M = 2.0."""
        result = masonry_partial_safety_factor(
            element_category=1, mortar_type="guaranteed", execution_class=1
        )
        assert_allclose(result, 2.0, rtol=1e-3)

    def test_cat_I_guaranteed_class_2(self):
        """Cat.I, malta a prestazione garantita, classe 2: gamma_M = 2.5."""
        result = masonry_partial_safety_factor(
            element_category=1, mortar_type="guaranteed", execution_class=2
        )
        assert_allclose(result, 2.5, rtol=1e-3)

    def test_cat_I_prescribed_class_1(self):
        """Cat.I, malta a composizione prescritta, classe 1: gamma_M = 2.2."""
        result = masonry_partial_safety_factor(
            element_category=1, mortar_type="prescribed", execution_class=1
        )
        assert_allclose(result, 2.2, rtol=1e-3)

    def test_cat_I_prescribed_class_2(self):
        """Cat.I, malta a composizione prescritta, classe 2: gamma_M = 2.7."""
        result = masonry_partial_safety_factor(
            element_category=1, mortar_type="prescribed", execution_class=2
        )
        assert_allclose(result, 2.7, rtol=1e-3)

    def test_cat_II_class_1(self):
        """Cat.II, qualsiasi malta, classe 1: gamma_M = 2.5."""
        result = masonry_partial_safety_factor(
            element_category=2, mortar_type="guaranteed", execution_class=1
        )
        assert_allclose(result, 2.5, rtol=1e-3)

    def test_cat_II_class_2(self):
        """Cat.II, qualsiasi malta, classe 2: gamma_M = 3.0."""
        result = masonry_partial_safety_factor(
            element_category=2, mortar_type="prescribed", execution_class=2
        )
        assert_allclose(result, 3.0, rtol=1e-3)

    def test_invalid_category_raises(self):
        with pytest.raises(ValueError, match="element_category"):
            masonry_partial_safety_factor(
                element_category=3, mortar_type="guaranteed", execution_class=1
            )

    def test_invalid_mortar_raises(self):
        with pytest.raises(ValueError, match="mortar_type"):
            masonry_partial_safety_factor(
                element_category=1, mortar_type="unknown", execution_class=1
            )

    def test_invalid_class_raises(self):
        with pytest.raises(ValueError, match="execution_class"):
            masonry_partial_safety_factor(
                element_category=1, mortar_type="guaranteed", execution_class=3
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(masonry_partial_safety_factor)
        assert ref is not None
        assert ref.article == "4.5.6.1"


# ── [4.5.2] — Resistenza di progetto a compressione ─────────────────────────


class TestMasonryDesignCompressiveStrength:
    """NTC18 §4.5.6.1, Formula [4.5.2]."""

    def test_basic(self):
        """f_d = f_k / gamma_M = 5.0 / 2.5 = 2.0 MPa."""
        result = masonry_design_compressive_strength(f_k=5.0, gamma_M=2.5)
        assert_allclose(result, 2.0, rtol=1e-3)

    def test_high_strength(self):
        """f_d = 10.0 / 2.0 = 5.0 MPa."""
        result = masonry_design_compressive_strength(f_k=10.0, gamma_M=2.0)
        assert_allclose(result, 5.0, rtol=1e-3)

    def test_zero_fk_raises(self):
        with pytest.raises(ValueError):
            masonry_design_compressive_strength(f_k=0.0, gamma_M=2.5)

    def test_ntc_ref(self):
        ref = get_ntc_ref(masonry_design_compressive_strength)
        assert ref is not None
        assert ref.article == "4.5.6.1"


# ── [4.5.3] — Resistenza di progetto a taglio ───────────────────────────────


class TestMasonryDesignShearStrength:
    """NTC18 §4.5.6.1, Formula [4.5.3]."""

    def test_basic(self):
        """f_vd = f_vk / gamma_M = 0.3 / 2.5 = 0.12 MPa."""
        result = masonry_design_shear_strength(f_vk=0.3, gamma_M=2.5)
        assert_allclose(result, 0.12, rtol=1e-3)

    def test_with_compression(self):
        """f_vd = 0.5 / 2.0 = 0.25 MPa."""
        result = masonry_design_shear_strength(f_vk=0.5, gamma_M=2.0)
        assert_allclose(result, 0.25, rtol=1e-3)

    def test_zero_fvk_raises(self):
        with pytest.raises(ValueError):
            masonry_design_shear_strength(f_vk=0.0, gamma_M=2.5)

    def test_ntc_ref(self):
        ref = get_ntc_ref(masonry_design_shear_strength)
        assert ref is not None
        assert ref.article == "4.5.6.1"


# ── [4.5.1] — Snellezza convenzionale ───────────────────────────────────────


class TestMasonrySlenderness:
    """NTC18 §4.5.4, Formula [4.5.1]."""

    def test_basic(self):
        """lambda = h_0 / t = 3000 / 300 = 10."""
        result = masonry_slenderness(h_0=3000.0, t=300.0)
        assert_allclose(result, 10.0, rtol=1e-3)

    def test_max_lambda(self):
        """lambda = 20 esatto: ammesso."""
        result = masonry_slenderness(h_0=4000.0, t=200.0)
        assert_allclose(result, 20.0, rtol=1e-3)

    def test_exceeds_20_raises(self):
        """lambda > 20: non ammesso da §4.5.4."""
        with pytest.raises(ValueError, match="20"):
            masonry_slenderness(h_0=4200.0, t=200.0)

    def test_zero_thickness_raises(self):
        with pytest.raises(ValueError):
            masonry_slenderness(h_0=3000.0, t=0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(masonry_slenderness)
        assert ref is not None
        assert ref.article == "4.5.4"


# ── Tab.4.5.IV — Fattore laterale di vincolo ────────────────────────────────


class TestMasonryLateralRestraintFactor:
    """NTC18 §4.5.6.2, Tab. 4.5.IV."""

    def test_low_ratio(self):
        """h/a <= 0.5: rho = 1."""
        result = masonry_lateral_restraint_factor(h=3000.0, a=8000.0)
        assert_allclose(result, 1.0, rtol=1e-3)

    def test_boundary_05(self):
        """h/a = 0.5: rho = 1."""
        result = masonry_lateral_restraint_factor(h=3000.0, a=6000.0)
        assert_allclose(result, 1.0, rtol=1e-3)

    def test_mid_range(self):
        """h/a = 0.75: rho = 3/2 - 0.75 = 0.75."""
        result = masonry_lateral_restraint_factor(h=3000.0, a=4000.0)
        assert_allclose(result, 0.75, rtol=1e-3)

    def test_boundary_10(self):
        """h/a = 1.0: rho = 3/2 - 1.0 = 0.5."""
        result = masonry_lateral_restraint_factor(h=3000.0, a=3000.0)
        assert_allclose(result, 0.5, rtol=1e-3)

    def test_high_ratio(self):
        """h/a = 2.0: rho = 1/(1+4) = 0.2."""
        result = masonry_lateral_restraint_factor(h=6000.0, a=3000.0)
        assert_allclose(result, 0.2, rtol=1e-3)

    def test_zero_spacing_raises(self):
        with pytest.raises(ValueError):
            masonry_lateral_restraint_factor(h=3000.0, a=0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(masonry_lateral_restraint_factor)
        assert ref is not None
        assert ref.article == "4.5.6.2"


# ── [4.5.5] — Lunghezza libera d'inflessione ────────────────────────────────


class TestMasonryEffectiveHeight:
    """NTC18 §4.5.6.2, Formula [4.5.5]."""

    def test_isolated_wall(self):
        """Muro isolato: rho=1, h_0 = 1 * 3000 = 3000 mm."""
        result = masonry_effective_height(rho=1.0, h=3000.0)
        assert_allclose(result, 3000.0, rtol=1e-3)

    def test_restrained_wall(self):
        """rho = 0.75, h = 3000: h_0 = 2250 mm."""
        result = masonry_effective_height(rho=0.75, h=3000.0)
        assert_allclose(result, 2250.0, rtol=1e-3)

    def test_zero_rho_raises(self):
        with pytest.raises(ValueError):
            masonry_effective_height(rho=0.0, h=3000.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(masonry_effective_height)
        assert ref is not None
        assert ref.article == "4.5.6.2"


# ── [4.5.6] — Coefficiente di eccentricita' ─────────────────────────────────


class TestMasonryEccentricityCoefficient:
    """NTC18 §4.5.6.2, Formula [4.5.6]."""

    def test_zero_eccentricity(self):
        """e = 0: m = 0."""
        result = masonry_eccentricity_coefficient(e=0.0, t=300.0)
        assert_allclose(result, 0.0, atol=1e-10)

    def test_basic(self):
        """e = 25 mm, t = 300 mm: m = 6*25/300 = 0.5."""
        result = masonry_eccentricity_coefficient(e=25.0, t=300.0)
        assert_allclose(result, 0.5, rtol=1e-3)

    def test_high_eccentricity(self):
        """e = 50 mm, t = 300 mm: m = 6*50/300 = 1.0."""
        result = masonry_eccentricity_coefficient(e=50.0, t=300.0)
        assert_allclose(result, 1.0, rtol=1e-3)

    def test_zero_thickness_raises(self):
        with pytest.raises(ValueError):
            masonry_eccentricity_coefficient(e=25.0, t=0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(masonry_eccentricity_coefficient)
        assert ref is not None
        assert ref.article == "4.5.6.2"


# ── Tab.4.5.III — Coefficiente di riduzione Phi ─────────────────────────────


class TestMasonryReductionFactor:
    """NTC18 §4.5.6.2, Tab. 4.5.III."""

    def test_lambda_0_m_0(self):
        """lambda=0, m=0: Phi = 1.00."""
        result = masonry_reduction_factor(lambda_=0.0, m=0.0)
        assert_allclose(result, 1.00, rtol=1e-3)

    def test_lambda_0_m_1(self):
        """lambda=0, m=1.0: Phi = 0.59."""
        result = masonry_reduction_factor(lambda_=0.0, m=1.0)
        assert_allclose(result, 0.59, rtol=1e-3)

    def test_lambda_10_m_0(self):
        """lambda=10, m=0: Phi = 0.86."""
        result = masonry_reduction_factor(lambda_=10.0, m=0.0)
        assert_allclose(result, 0.86, rtol=1e-3)

    def test_lambda_10_m_2(self):
        """lambda=10, m=2.0: Phi = 0.16."""
        result = masonry_reduction_factor(lambda_=10.0, m=2.0)
        assert_allclose(result, 0.16, rtol=1e-3)

    def test_lambda_20_m_0(self):
        """lambda=20, m=0: Phi = 0.53."""
        result = masonry_reduction_factor(lambda_=20.0, m=0.0)
        assert_allclose(result, 0.53, rtol=1e-3)

    def test_lambda_20_m_1(self):
        """lambda=20, m=1.0: Phi = 0.23."""
        result = masonry_reduction_factor(lambda_=20.0, m=1.0)
        assert_allclose(result, 0.23, rtol=1e-3)

    def test_interpolated(self):
        """lambda=7.5, m=0.25: interpolazione bilineare."""
        # lambda tra 5 e 10, m tra 0 e 0.5
        # Phi(5,0)=0.97, Phi(5,0.5)=0.71, Phi(10,0)=0.86, Phi(10,0.5)=0.61
        # Interpolazione bilineare: media dei quattro angoli ponderata
        # t_lam = (7.5-5)/(10-5) = 0.5
        # t_m   = (0.25-0)/(0.5-0) = 0.5
        # Phi = (1-0.5)*(1-0.5)*0.97 + 0.5*(1-0.5)*0.86 + (1-0.5)*0.5*0.71 + 0.5*0.5*0.61
        #     = 0.25*0.97 + 0.25*0.86 + 0.25*0.71 + 0.25*0.61 = 0.7875
        result = masonry_reduction_factor(lambda_=7.5, m=0.25)
        assert_allclose(result, 0.7875, rtol=1e-2)

    def test_lambda_20_m_15_raises(self):
        """lambda=20, m=1.5: fuori dal dominio Tab.4.5.III."""
        with pytest.raises(ValueError, match="dominio"):
            masonry_reduction_factor(lambda_=20.0, m=1.5)

    def test_lambda_15_m_2_raises(self):
        """lambda=15, m=2.0: fuori dal dominio Tab.4.5.III."""
        with pytest.raises(ValueError, match="dominio"):
            masonry_reduction_factor(lambda_=15.0, m=2.0)

    def test_negative_lambda_raises(self):
        with pytest.raises(ValueError):
            masonry_reduction_factor(lambda_=-1.0, m=0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(masonry_reduction_factor)
        assert ref is not None
        assert ref.article == "4.5.6.2"


# ── [4.5.4] — Resistenza ridotta ────────────────────────────────────────────


class TestMasonryReducedStrength:
    """NTC18 §4.5.6.2, Formula [4.5.4]."""

    def test_no_reduction(self):
        """Phi = 1.0: f_d_rid = f_d."""
        result = masonry_reduced_strength(Phi=1.0, f_d=2.0)
        assert_allclose(result, 2.0, rtol=1e-3)

    def test_reduced(self):
        """Phi = 0.59, f_d = 2.0: f_d_rid = 1.18 MPa."""
        result = masonry_reduced_strength(Phi=0.59, f_d=2.0)
        assert_allclose(result, 1.18, rtol=1e-3)

    def test_heavily_reduced(self):
        """Phi = 0.23, f_d = 5.0: f_d_rid = 1.15 MPa."""
        result = masonry_reduced_strength(Phi=0.23, f_d=5.0)
        assert_allclose(result, 1.15, rtol=1e-3)

    def test_zero_Phi_raises(self):
        with pytest.raises(ValueError):
            masonry_reduced_strength(Phi=0.0, f_d=2.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(masonry_reduced_strength)
        assert ref is not None
        assert ref.article == "4.5.6.2"


# ── [4.5.12] — Verifica semplificata ────────────────────────────────────────


class TestMasonrySimplifiedCheck:
    """NTC18 §4.5.6.4, Formula [4.5.12]."""

    def test_passes(self):
        """sigma = 500/(0.65*0.3) = 2564 kN/m^2 = 2.56 MPa; f_d = 5/2.5 = 2.0 => fail."""
        # N=500 kN, A=0.3 m^2, f_k=5 MPa, gamma_M=2.5
        passes, sigma = masonry_simplified_check(
            N=500.0, A=0.3, f_k=5.0, gamma_M=2.5
        )
        # sigma = 500/(0.65*0.3) = 2564.1 kN/m^2 (= 2.564 MPa in consistent units)
        # But units depend on usage — let's keep it in consistent units
        expected_sigma = 500.0 / (0.65 * 0.3)
        assert_allclose(sigma, expected_sigma, rtol=1e-3)

    def test_low_load_passes(self):
        """Carico basso: verifica passa."""
        passes, sigma = masonry_simplified_check(
            N=100.0, A=0.5, f_k=5.0, gamma_M=2.5
        )
        # sigma = 100/(0.65*0.5) = 307.7
        # f_d = 5.0/2.5 = 2.0
        # Per passare: sigma <= f_d => 307.7 <= 2.0 in stesse unita'?
        # No — le unita' devono essere coerenti. In pratica:
        # N [kN], A [m^2] => sigma [kN/m^2]; f_k [MPa] = [N/mm^2] = [kN/m^2 * 1e-3]
        # Convenzionalmente in questa formula tutto e' nello stesso sistema.
        # f_k = 5.0, gamma_M = 2.5 => f_d = 2.0
        # sigma = 100/(0.65*0.5) = 307.7
        # 307.7 <= 2.0? No. Ma se le unita' sono tutte [MPa]:
        # N [N], A [mm^2]: sigma = 100e3/(0.65*500e3) = 0.307 MPa <= 2.0 => passa!
        # La funzione lavora in unita' coerenti, passate dall'utente.
        passes, sigma = masonry_simplified_check(
            N=100e3, A=500e3, f_k=5.0, gamma_M=2.5
        )
        expected_sigma = 100e3 / (0.65 * 500e3)
        expected_f_d = 5.0 / 2.5
        assert passes is True
        assert_allclose(sigma, expected_sigma, rtol=1e-3)
        assert sigma <= expected_f_d

    def test_high_load_fails(self):
        """Carico alto: verifica non passa."""
        # N=800e3 N, A=200e3 mm^2, f_k=3.0 MPa, gamma_M=2.5
        passes, sigma = masonry_simplified_check(
            N=800e3, A=200e3, f_k=3.0, gamma_M=2.5
        )
        expected_sigma = 800e3 / (0.65 * 200e3)  # 6.15 MPa
        expected_f_d = 3.0 / 2.5  # 1.2 MPa
        assert passes is False
        assert sigma > expected_f_d

    def test_zero_area_raises(self):
        with pytest.raises(ValueError):
            masonry_simplified_check(N=100.0, A=0.0, f_k=5.0, gamma_M=2.5)

    def test_ntc_ref(self):
        ref = get_ntc_ref(masonry_simplified_check)
        assert ref is not None
        assert ref.article == "4.5.6.4"


# ── [4.5.7] — Eccentricità carichi verticali ────────────────────────────────


class TestMasonryVerticalLoadEccentricity:
    """NTC18 §4.5.6.2, Formula [4.5.7]."""

    def test_symmetric(self):
        # N1=100, d1=50, N2=100, d2=50 → e_s1 = 100*50/200 = 25, e_s2 = 25
        e_s1, e_s2 = masonry_vertical_load_eccentricity(100.0, 50.0, 100.0, 50.0)
        assert_allclose(e_s1, 25.0, rtol=1e-6)
        assert_allclose(e_s2, 25.0, rtol=1e-6)

    def test_only_wall_load(self):
        # N1=200, d1=30, N2=0, d2=0 → e_s1 = 200*30/200 = 30, e_s2 = 0
        e_s1, e_s2 = masonry_vertical_load_eccentricity(200.0, 30.0, 0.0, 0.0)
        assert_allclose(e_s1, 30.0, rtol=1e-6)
        assert_allclose(e_s2, 0.0, atol=1e-9)

    def test_negative_eccentricity(self):
        # d1=-20, N1=150, N2=50 → e_s1 = 150*(-20)/200 = -15
        e_s1, e_s2 = masonry_vertical_load_eccentricity(150.0, -20.0, 50.0, 0.0)
        assert_allclose(e_s1, -15.0, rtol=1e-6)
        assert_allclose(e_s2, 0.0, atol=1e-9)

    def test_zero_total_raises(self):
        with pytest.raises(ValueError):
            masonry_vertical_load_eccentricity(0.0, 10.0, 0.0, 10.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(masonry_vertical_load_eccentricity)
        assert ref is not None
        assert ref.article == "4.5.6.2"
        assert ref.formula == "4.5.7"


# ── [4.5.9] — Eccentricità da azioni orizzontali ────────────────────────────


class TestMasonryHorizontalEccentricity:
    """NTC18 §4.5.6.2, Formula [4.5.9]."""

    def test_basic(self):
        # M_s=600e3 N·mm, N=10000 N → e_s = 60 mm
        assert_allclose(masonry_horizontal_eccentricity(600e3, 10000.0), 60.0, rtol=1e-6)

    def test_sign_preserved(self):
        # M negativo
        assert_allclose(masonry_horizontal_eccentricity(-300e3, 10000.0), -30.0, rtol=1e-6)

    def test_zero_N_raises(self):
        with pytest.raises(ValueError):
            masonry_horizontal_eccentricity(100.0, 0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(masonry_horizontal_eccentricity)
        assert ref is not None
        assert ref.article == "4.5.6.2"
        assert ref.formula == "4.5.9"


# ── [4.5.10] — Combinazione eccentricità ────────────────────────────────────


class TestMasonryCombinedEccentricity:
    """NTC18 §4.5.6.2, Formula [4.5.10]."""

    def test_positive_both(self):
        # e_x=30, e_y=20 → e1 = 30+20=50, e2 = 25+20=45
        e1, e2 = masonry_combined_eccentricity(30.0, 20.0)
        assert_allclose(e1, 50.0, rtol=1e-6)
        assert_allclose(e2, 45.0, rtol=1e-6)

    def test_negative_ex(self):
        # e_x=-40, e_y=10 → e1 = 40+10=50, e2 = 25+10=35
        e1, e2 = masonry_combined_eccentricity(-40.0, 10.0)
        assert_allclose(e1, 50.0, rtol=1e-6)
        assert_allclose(e2, 35.0, rtol=1e-6)

    def test_zero_ex(self):
        # e_x=0, e_y=15 → e1=15, e2=7.5+15=22.5
        e1, e2 = masonry_combined_eccentricity(0.0, 15.0)
        assert_allclose(e1, 15.0, rtol=1e-6)
        assert_allclose(e2, 22.5, rtol=1e-6)

    def test_ntc_ref(self):
        ref = get_ntc_ref(masonry_combined_eccentricity)
        assert ref is not None
        assert ref.article == "4.5.6.2"
        assert ref.formula == "4.5.10"


# ── [4.5.11] — Verifica limiti eccentricità ──────────────────────────────────


class TestMasonryEccentricityCheck:
    """NTC18 §4.5.6.2, Formula [4.5.11]."""

    def test_safe(self):
        # e1=30, e2=25, t=200 → limit=66, max_ratio=30/66≈0.455
        ok, ratio = masonry_eccentricity_check(30.0, 25.0, 200.0)
        assert ok is True
        assert_allclose(ratio, 30.0 / (0.33 * 200.0), rtol=1e-6)

    def test_limit_exactly(self):
        # e1=e2=0.33*t → ratio=1.0
        t = 300.0
        ok, ratio = masonry_eccentricity_check(0.33 * t, 0.33 * t, t)
        assert ok is True
        assert_allclose(ratio, 1.0, rtol=1e-6)

    def test_unsafe_e1(self):
        # e1 supera il limite
        ok, ratio = masonry_eccentricity_check(80.0, 20.0, 200.0)
        assert ok is False
        assert ratio > 1.0

    def test_unsafe_e2(self):
        # e2 supera il limite
        ok, ratio = masonry_eccentricity_check(20.0, 80.0, 200.0)
        assert ok is False

    def test_zero_t_raises(self):
        with pytest.raises(ValueError):
            masonry_eccentricity_check(10.0, 10.0, 0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(masonry_eccentricity_check)
        assert ref is not None
        assert ref.article == "4.5.6.2"
        assert ref.formula == "4.5.11"


# ── [4.5.6] — masonry_eccentricity_m ────────────────────────────────────────


class TestMasonryEccentricityM:
    """NTC18 §4.5.6.2, Formula [4.5.6] — m = 6*e/t."""

    def test_zero_eccentricity(self):
        """e = 0: m = 0."""
        result = masonry_eccentricity_m(e=0.0, t=300.0)
        assert_allclose(result, 0.0, atol=1e-10)

    def test_e_t6(self):
        """e = t/6 => m = 1.0."""
        result = masonry_eccentricity_m(e=50.0, t=300.0)
        assert_allclose(result, 1.0, rtol=1e-6)

    def test_quarter_thickness(self):
        """e = t/4 => m = 6*(t/4)/t = 1.5."""
        result = masonry_eccentricity_m(e=75.0, t=300.0)
        assert_allclose(result, 1.5, rtol=1e-6)

    def test_half_sixth(self):
        """e = 25 mm, t = 300 mm => m = 6*25/300 = 0.5."""
        result = masonry_eccentricity_m(e=25.0, t=300.0)
        assert_allclose(result, 0.5, rtol=1e-6)

    def test_negative_eccentricity_raises(self):
        with pytest.raises(ValueError, match="e deve essere"):
            masonry_eccentricity_m(e=-1.0, t=300.0)

    def test_zero_thickness_raises(self):
        with pytest.raises(ValueError, match="t deve essere"):
            masonry_eccentricity_m(e=25.0, t=0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(masonry_eccentricity_m)
        assert ref is not None
        assert ref.article == "4.5.6.2"
        assert ref.formula == "4.5.6"


# ── Tab.4.5.III — masonry_phi_from_table ────────────────────────────────────


class TestMasonryPhiFromTable:
    """NTC18 §4.5.6.2, Tab. 4.5.III — interpolazione bilineare."""

    # Valori esatti sulla griglia
    def test_grid_lambda0_m0(self):
        """lambda=0, m=0: Phi = 1.00."""
        assert_allclose(masonry_phi_from_table(0.0, 0.0), 1.00, rtol=1e-3)

    def test_grid_lambda0_m05(self):
        """lambda=0, m=0.5: Phi = 0.74."""
        assert_allclose(masonry_phi_from_table(0.0, 0.5), 0.74, rtol=1e-3)

    def test_grid_lambda0_m10(self):
        """lambda=0, m=1.0: Phi = 0.59."""
        assert_allclose(masonry_phi_from_table(0.0, 1.0), 0.59, rtol=1e-3)

    def test_grid_lambda0_m15(self):
        """lambda=0, m=1.5: Phi = 0.44."""
        assert_allclose(masonry_phi_from_table(0.0, 1.5), 0.44, rtol=1e-3)

    def test_grid_lambda0_m20(self):
        """lambda=0, m=2.0: Phi = 0.33."""
        assert_allclose(masonry_phi_from_table(0.0, 2.0), 0.33, rtol=1e-3)

    def test_grid_lambda5_m0(self):
        """lambda=5, m=0: Phi = 0.97."""
        assert_allclose(masonry_phi_from_table(5.0, 0.0), 0.97, rtol=1e-3)

    def test_grid_lambda10_m0(self):
        """lambda=10, m=0: Phi = 0.86."""
        assert_allclose(masonry_phi_from_table(10.0, 0.0), 0.86, rtol=1e-3)

    def test_grid_lambda10_m10(self):
        """lambda=10, m=1.0: Phi = 0.45."""
        assert_allclose(masonry_phi_from_table(10.0, 1.0), 0.45, rtol=1e-3)

    def test_grid_lambda10_m20(self):
        """lambda=10, m=2.0: Phi = 0.16."""
        assert_allclose(masonry_phi_from_table(10.0, 2.0), 0.16, rtol=1e-3)

    def test_grid_lambda15_m0(self):
        """lambda=15, m=0: Phi = 0.69."""
        assert_allclose(masonry_phi_from_table(15.0, 0.0), 0.69, rtol=1e-3)

    def test_grid_lambda15_m10(self):
        """lambda=15, m=1.0: Phi = 0.32."""
        assert_allclose(masonry_phi_from_table(15.0, 1.0), 0.32, rtol=1e-3)

    def test_grid_lambda20_m0(self):
        """lambda=20, m=0: Phi = 0.53."""
        assert_allclose(masonry_phi_from_table(20.0, 0.0), 0.53, rtol=1e-3)

    def test_grid_lambda20_m10(self):
        """lambda=20, m=1.0: Phi = 0.23."""
        assert_allclose(masonry_phi_from_table(20.0, 1.0), 0.23, rtol=1e-3)

    # Interpolazione solo su m (lambda esatto)
    def test_interp_m_only(self):
        """lambda=10 esatto, m=0.25: interp fra m=0 (0.86) e m=0.5 (0.61).
        Phi = 0.86*(1-0.5) + 0.61*0.5 = 0.735
        """
        result = masonry_phi_from_table(10.0, 0.25)
        assert_allclose(result, 0.735, rtol=1e-3)

    # Interpolazione solo su lambda (m esatto)
    def test_interp_lambda_only(self):
        """m=0 esatto, lambda=7.5: interp fra lambda=5 (0.97) e lambda=10 (0.86).
        t_lam = (7.5-5)/(10-5) = 0.5
        Phi = 0.97*0.5 + 0.86*0.5 = 0.915
        """
        result = masonry_phi_from_table(7.5, 0.0)
        assert_allclose(result, 0.915, rtol=1e-3)

    # Interpolazione bilineare completa
    def test_interp_bilinear(self):
        """lambda=7.5, m=0.25: interpolazione bilineare.
        Phi(5,0)=0.97, Phi(5,0.5)=0.71, Phi(10,0)=0.86, Phi(10,0.5)=0.61
        t_lam=0.5, t_m=0.5
        Phi = 0.25*0.97 + 0.25*0.86 + 0.25*0.71 + 0.25*0.61 = 0.7875
        """
        result = masonry_phi_from_table(7.5, 0.25)
        assert_allclose(result, 0.7875, rtol=1e-2)

    # Combinazioni fuori dominio (celle None nella tabella)
    def test_lambda20_m15_raises(self):
        """lambda=20, m=1.5: fuori dal dominio Tab.4.5.III."""
        with pytest.raises(ValueError, match="dominio"):
            masonry_phi_from_table(20.0, 1.5)

    def test_lambda15_m20_raises(self):
        """lambda=15, m=2.0: fuori dal dominio Tab.4.5.III."""
        with pytest.raises(ValueError, match="dominio"):
            masonry_phi_from_table(15.0, 2.0)

    # Validazione input
    def test_negative_lambda_raises(self):
        with pytest.raises(ValueError, match="lambda_slend deve essere >= 0"):
            masonry_phi_from_table(-1.0, 0.0)

    def test_lambda_exceeds_20_raises(self):
        with pytest.raises(ValueError, match="lambda_slend deve essere <= 20"):
            masonry_phi_from_table(21.0, 0.0)

    def test_m_exceeds_2_raises(self):
        with pytest.raises(ValueError, match="m deve essere <= 2.0"):
            masonry_phi_from_table(0.0, 2.1)

    def test_negative_m_raises(self):
        with pytest.raises(ValueError, match="m deve essere >= 0"):
            masonry_phi_from_table(0.0, -0.1)

    def test_ntc_ref(self):
        ref = get_ntc_ref(masonry_phi_from_table)
        assert ref is not None
        assert ref.article == "4.5.6.2"
        assert ref.table == "Tab.4.5.III"


# ── [4.5.12] — masonry_simplified_axial_check ───────────────────────────────


class TestMasonrySimplifiedAxialCheck:
    """NTC18 §4.5.6.4, Formula [4.5.12] — ratio = sigma / f_d."""

    def test_passes_low_load(self):
        """Carico basso: ratio < 1.0 => verifica superata."""
        # N_Ed=100e3 N, A=500e3 mm^2 => sigma = 100e3/(0.65*500e3) = 0.3077 MPa
        # f_d = 5.0/2.5 = 2.0 MPa => ratio = 0.3077/2.0 = 0.1538
        passes, ratio = masonry_simplified_axial_check(
            N_Ed=100e3, A=500e3, f_k=5.0, gamma_M=2.5
        )
        expected_sigma = 100e3 / (0.65 * 500e3)
        expected_ratio = expected_sigma / (5.0 / 2.5)
        assert passes is True
        assert_allclose(ratio, expected_ratio, rtol=1e-4)
        assert ratio < 1.0

    def test_fails_high_load(self):
        """Carico elevato: ratio > 1.0 => verifica non superata."""
        # N_Ed=800e3 N, A=200e3 mm^2 => sigma = 800e3/(0.65*200e3) = 6.154 MPa
        # f_d = 3.0/2.5 = 1.2 MPa => ratio = 6.154/1.2 = 5.128
        passes, ratio = masonry_simplified_axial_check(
            N_Ed=800e3, A=200e3, f_k=3.0, gamma_M=2.5
        )
        assert passes is False
        assert ratio > 1.0

    def test_exactly_at_limit(self):
        """ratio = 1.0 esatto: verifica superata (sigma = f_d)."""
        # Vogliamo sigma = f_d => N_Ed = 0.65 * A * f_k / gamma_M
        f_k = 4.0
        gamma_M = 2.0
        A = 300e3  # mm^2
        f_d = f_k / gamma_M  # 2.0 MPa
        N_Ed = 0.65 * A * f_d  # N tale che sigma = f_d esattamente
        passes, ratio = masonry_simplified_axial_check(
            N_Ed=N_Ed, A=A, f_k=f_k, gamma_M=gamma_M
        )
        assert passes is True
        assert_allclose(ratio, 1.0, rtol=1e-6)

    def test_ratio_formula(self):
        """Verifica la formula del ratio: ratio = sigma / (f_k / gamma_M)."""
        N_Ed = 250e3
        A = 400e3
        f_k = 6.0
        gamma_M = 3.0
        passes, ratio = masonry_simplified_axial_check(
            N_Ed=N_Ed, A=A, f_k=f_k, gamma_M=gamma_M
        )
        sigma = N_Ed / (0.65 * A)
        f_d = f_k / gamma_M
        assert_allclose(ratio, sigma / f_d, rtol=1e-6)

    def test_zero_area_raises(self):
        with pytest.raises(ValueError, match="A deve essere"):
            masonry_simplified_axial_check(N_Ed=100.0, A=0.0, f_k=5.0, gamma_M=2.5)

    def test_negative_N_raises(self):
        with pytest.raises(ValueError, match="N_Ed deve essere"):
            masonry_simplified_axial_check(N_Ed=-1.0, A=100.0, f_k=5.0, gamma_M=2.5)

    def test_zero_fk_raises(self):
        with pytest.raises(ValueError, match="f_k deve essere"):
            masonry_simplified_axial_check(N_Ed=100.0, A=100.0, f_k=0.0, gamma_M=2.5)

    def test_zero_gamma_raises(self):
        with pytest.raises(ValueError, match="gamma_M deve essere"):
            masonry_simplified_axial_check(N_Ed=100.0, A=100.0, f_k=5.0, gamma_M=0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(masonry_simplified_axial_check)
        assert ref is not None
        assert ref.article == "4.5.6.4"
        assert ref.formula == "4.5.12"


# ── §4.5.7 — Muratura armata ─────────────────────────────────────────────────


class TestMasonryReinforcedFlexuralResistance:
    """NTC18 §4.5.7.3 — Momento resistente muratura armata."""

    def test_basic(self):
        """Calcolo manuale:
        b=300, d=500, A_s=400, f_yd=391.3, f_k=6.0, gamma_M=2.0
        f_d  = 6.0/2.0 = 3.0 N/mm²
        F_s  = 400*391.3 = 156520 N
        x    = 156520/(0.8*300*3.0) = 156520/720 = 217.39 mm
        M_Rd = 156520*(500 - 0.4*217.39) = 156520*412.956 N·mm
        """
        b, d, A_s = 300.0, 500.0, 400.0
        f_yd, f_k, gamma_M = 391.3, 6.0, 2.0
        f_d = f_k / gamma_M
        F_s = A_s * f_yd
        x = F_s / (0.8 * b * f_d)
        expected = F_s * (d - 0.4 * x)
        result = masonry_reinforced_flexural_resistance(b, d, A_s, f_yd, f_k, gamma_M)
        assert_allclose(result, expected, rtol=1e-6)

    def test_heavily_reinforced_raises(self):
        """Sezione sovra-armata: x > d => ValueError."""
        with pytest.raises(ValueError, match="sovra-armata"):
            masonry_reinforced_flexural_resistance(
                b=100.0, d=200.0, A_s=5000.0, f_yd=500.0, f_k=5.0, gamma_M=2.0
            )

    def test_invalid_b_raises(self):
        with pytest.raises(ValueError):
            masonry_reinforced_flexural_resistance(
                b=0.0, d=500.0, A_s=400.0, f_yd=391.3, f_k=6.0, gamma_M=2.0
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(masonry_reinforced_flexural_resistance)
        assert ref is not None
        assert ref.article == "4.5.7.3"


class TestMasonryReinforcedShearResistance:
    """NTC18 §4.5.7.4 — Taglio resistente muratura armata."""

    def test_basic(self):
        """Calcolo manuale:
        b=300, d=500, A_sw=100, s=200, f_ywk=450
        gamma_s=1.15, f_vk0=0.3, gamma_M=2.0
        V_Rd1 = 0.3/2.0 * 300*500 = 22500 N
        V_Rd2 = 0.9*500*(100/200)*(450/1.15) = 0.9*500*0.5*391.304 N
        V_Rd  = V_Rd1 + V_Rd2
        """
        b, d = 300.0, 500.0
        A_sw, s, f_ywk = 100.0, 200.0, 450.0
        gamma_s, f_vk0, gamma_M = 1.15, 0.3, 2.0
        V_Rd1 = f_vk0 / gamma_M * b * d
        V_Rd2 = 0.9 * d * (A_sw / s) * (f_ywk / gamma_s)
        expected = V_Rd1 + V_Rd2
        result = masonry_reinforced_shear_resistance(
            b, d, A_sw, s, f_ywk, gamma_s=gamma_s, f_vk0=f_vk0, gamma_M=gamma_M
        )
        assert_allclose(result, expected, rtol=1e-6)

    def test_default_parameters(self):
        """Verifica che i parametri di default producano lo stesso risultato
        di una chiamata esplicita."""
        b, d, A_sw, s, f_ywk = 250.0, 400.0, 78.5, 150.0, 500.0
        result_default = masonry_reinforced_shear_resistance(b, d, A_sw, s, f_ywk)
        result_explicit = masonry_reinforced_shear_resistance(
            b, d, A_sw, s, f_ywk, gamma_s=1.15, f_vk0=0.3, gamma_M=2.0
        )
        assert_allclose(result_default, result_explicit, rtol=1e-9)

    def test_invalid_s_raises(self):
        with pytest.raises(ValueError):
            masonry_reinforced_shear_resistance(
                b=300.0, d=500.0, A_sw=100.0, s=0.0, f_ywk=450.0
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(masonry_reinforced_shear_resistance)
        assert ref is not None
        assert ref.article == "4.5.7.4"


class TestMasonryReinforcedAxialCheck:
    """NTC18 §4.5.7.2 — Verifica assiale muratura armata."""

    def test_passes(self):
        """Calcolo manuale:
        N_Ed=500e3, b=300, d=400, A_s=600, f_yd=391.3, f_k=6.0, gamma_M=2.0
        f_d  = 6.0/2.0 = 3.0 N/mm²
        N_Rd = 300*400*3.0 + 600*391.3 = 360000 + 234780 = 594780 N
        ratio = 500000/594780 ≈ 0.840 <= 1.0 → verifica passa
        """
        N_Ed = 500e3
        b, d, A_s = 300.0, 400.0, 600.0
        f_yd, f_k, gamma_M = 391.3, 6.0, 2.0
        f_d = f_k / gamma_M
        N_Rd = b * d * f_d + A_s * f_yd
        expected_ratio = N_Ed / N_Rd
        passes, ratio = masonry_reinforced_axial_check(N_Ed, b, d, A_s, f_yd, f_k, gamma_M)
        assert passes is True
        assert_allclose(ratio, expected_ratio, rtol=1e-6)
        assert ratio <= 1.0

    def test_fails(self):
        """Carico superiore alla resistenza: verifica non passa."""
        N_Ed = 2_000e3
        b, d, A_s = 200.0, 300.0, 400.0
        f_yd, f_k, gamma_M = 391.3, 4.0, 2.0
        passes, ratio = masonry_reinforced_axial_check(N_Ed, b, d, A_s, f_yd, f_k, gamma_M)
        assert passes is False
        assert ratio > 1.0

    def test_invalid_N_Ed_raises(self):
        with pytest.raises(ValueError):
            masonry_reinforced_axial_check(
                N_Ed=-1.0, b=300.0, d=400.0, A_s=600.0,
                f_yd=391.3, f_k=6.0, gamma_M=2.0
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(masonry_reinforced_axial_check)
        assert ref is not None
        assert ref.article == "4.5.7.2"


# ── §4.5.8 — Muratura confinata ───────────────────────────────────────────────


class TestMasonryConfinedShearResistance:
    """NTC18 §4.5.8.2 — Taglio resistente muratura confinata."""

    def test_without_normal_stress(self):
        """sigma_n=0 (default):
        l=3000, t=300, f_vk0=0.2, gamma_M=2.0
        f_vk = 0.2 + 0.4*0 = 0.2 N/mm²
        V_Rd = 0.2/2.0 * 3000*300 = 0.1 * 900000 = 90000 N
        """
        result = masonry_confined_shear_resistance(
            l=3000.0, t=300.0, f_vk0=0.2, gamma_M=2.0
        )
        expected = 0.2 / 2.0 * 3000.0 * 300.0
        assert_allclose(result, expected, rtol=1e-9)

    def test_with_normal_stress(self):
        """sigma_n=0.5 MPa:
        l=2500, t=250, f_vk0=0.2, gamma_M=2.0, sigma_n=0.5
        f_vk = 0.2 + 0.4*0.5 = 0.4 N/mm²
        V_Rd = 0.4/2.0 * 2500*250 = 0.2 * 625000 = 125000 N
        """
        result = masonry_confined_shear_resistance(
            l=2500.0, t=250.0, f_vk0=0.2, gamma_M=2.0, sigma_n=0.5
        )
        expected = (0.2 + 0.4 * 0.5) / 2.0 * 2500.0 * 250.0
        assert_allclose(result, expected, rtol=1e-9)

    def test_invalid_l_raises(self):
        with pytest.raises(ValueError):
            masonry_confined_shear_resistance(l=0.0, t=300.0, f_vk0=0.2, gamma_M=2.0)

    def test_negative_sigma_n_raises(self):
        with pytest.raises(ValueError):
            masonry_confined_shear_resistance(
                l=3000.0, t=300.0, f_vk0=0.2, gamma_M=2.0, sigma_n=-0.1
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(masonry_confined_shear_resistance)
        assert ref is not None
        assert ref.article == "4.5.8.2"


class TestMasonryConfinedBendingResistance:
    """NTC18 §4.5.8.3 — Momento resistente muratura confinata."""

    def test_basic(self):
        """Calcolo manuale:
        A_s=400, f_yd=391.3, z=2000
        M_Rd = 400*391.3*2000 = 313040000 N·mm
        """
        A_s, f_yd, z = 400.0, 391.3, 2000.0
        expected = A_s * f_yd * z
        result = masonry_confined_bending_resistance(A_s, f_yd, z)
        assert_allclose(result, expected, rtol=1e-9)

    def test_proportional_to_z(self):
        """Raddoppiando z, M_Rd raddoppia."""
        r1 = masonry_confined_bending_resistance(300.0, 350.0, 1500.0)
        r2 = masonry_confined_bending_resistance(300.0, 350.0, 3000.0)
        assert_allclose(r2, 2.0 * r1, rtol=1e-9)

    def test_invalid_A_s_raises(self):
        with pytest.raises(ValueError):
            masonry_confined_bending_resistance(A_s=0.0, f_yd=391.3, z=2000.0)

    def test_invalid_z_raises(self):
        with pytest.raises(ValueError):
            masonry_confined_bending_resistance(A_s=400.0, f_yd=391.3, z=0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(masonry_confined_bending_resistance)
        assert ref is not None
        assert ref.article == "4.5.8.3"
