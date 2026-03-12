"""Test per checks/composite.py — NTC18 §4.3 Costruzioni composte acciaio-calcestruzzo."""

import math

import pytest
from numpy.testing import assert_allclose

from pyntc.checks.composite import (
    composite_beam_shear_distribution,
    composite_bond_stress_limit,
    composite_column_bending_check,
    composite_column_biaxial_check,
    composite_column_buckling_curve,
    composite_column_buckling_resistance,
    composite_column_confinement_resistance,
    composite_column_effective_stiffness,
    composite_column_effective_stiffness_ii,
    composite_column_local_buckling_check,
    composite_column_plastic_resistance,
    composite_column_plastic_resistance_characteristic,
    composite_column_reduced_moment_resistance,
    composite_column_slenderness,
    composite_concrete_part_resistance,
    composite_confinement_coefficients,
    composite_effective_width,
    composite_load_dispersion_width,
    composite_minimum_connection_degree,
    composite_moment_amplification,
    composite_moment_redistribution_limits,
    composite_profiled_sheet_reduction,
    composite_steel_contribution_ratio,
    composite_stud_alpha,
    composite_stud_resistance,
)
from pyntc.core.reference import get_ntc_ref


# ---------------------------------------------------------------------------
# 1. composite_effective_width  [4.3.2]
# ---------------------------------------------------------------------------
class TestCompositeEffectiveWidth:
    """NTC18 §4.3.2.3 — Larghezza efficace della soletta."""

    def test_symmetric_slab(self):
        # b_0=100, L_0=8000, b_1=b_2=2000
        # b_e = min(8000/8, 2000) = 1000 each side
        # b_eff = 100 + 1000 + 1000 = 2100
        assert_allclose(composite_effective_width(100, 8000, 2000, 2000), 2100)

    def test_slab_limited_by_available_width(self):
        # b_0=100, L_0=8000, b_1=500, b_2=500
        # b_e = min(1000, 500) = 500 each side
        # b_eff = 100 + 500 + 500 = 1100
        assert_allclose(composite_effective_width(100, 8000, 500, 500), 1100)

    def test_asymmetric(self):
        # b_0=120, L_0=6000, b_1=3000, b_2=400
        # b_e1 = min(750, 3000) = 750
        # b_e2 = min(750, 400) = 400
        # b_eff = 120 + 750 + 400 = 1270
        assert_allclose(composite_effective_width(120, 6000, 3000, 400), 1270)

    def test_short_span(self):
        # b_0=80, L_0=1600, b_1=1000, b_2=1000
        # b_e = min(200, 1000) = 200
        # b_eff = 80 + 200 + 200 = 480
        assert_allclose(composite_effective_width(80, 1600, 1000, 1000), 480)

    def test_ntc_ref(self):
        ref = get_ntc_ref(composite_effective_width)
        assert ref is not None
        assert ref.article == "4.3.2.3"


# ---------------------------------------------------------------------------
# 2. composite_moment_redistribution_limits  [Tab.4.3.I]
# ---------------------------------------------------------------------------
class TestCompositeMomentRedistributionLimits:
    """NTC18 §4.3.2.2.1 Tab.4.3.I — Limiti di ridistribuzione."""

    def test_class1_uncracked(self):
        assert_allclose(composite_moment_redistribution_limits(1, "uncracked"), 40)

    def test_class2_cracked(self):
        assert_allclose(composite_moment_redistribution_limits(2, "cracked"), 15)

    def test_class3_uncracked(self):
        assert_allclose(composite_moment_redistribution_limits(3, "uncracked"), 20)

    def test_class4_cracked(self):
        assert_allclose(composite_moment_redistribution_limits(4, "cracked"), 0)

    def test_invalid_class(self):
        with pytest.raises(ValueError):
            composite_moment_redistribution_limits(5, "uncracked")

    def test_invalid_analysis_type(self):
        with pytest.raises(ValueError):
            composite_moment_redistribution_limits(1, "partial")

    def test_ntc_ref(self):
        ref = get_ntc_ref(composite_moment_redistribution_limits)
        assert ref is not None
        assert "4.3.2" in ref.article


# ---------------------------------------------------------------------------
# 3. composite_stud_alpha  [4.3.11]
# ---------------------------------------------------------------------------
class TestCompositeStudAlpha:
    """NTC18 §4.3.4.3.1.2 — Coefficiente alpha per connettori a piolo."""

    def test_ratio_above_4(self):
        # h_wc/d = 100/19 = 5.26 > 4 → alpha = 1.0
        assert_allclose(composite_stud_alpha(100, 19), 1.0)

    def test_ratio_between_3_and_4(self):
        # h_wc/d = 60/19 = 3.158 → alpha = 0.2*(3.158+1) = 0.8316
        assert_allclose(composite_stud_alpha(60, 19), 0.2 * (60 / 19 + 1), rtol=1e-6)

    def test_ratio_exactly_4(self):
        # h_wc/d = 4.0 → alpha = 0.2*(4+1) = 1.0
        assert_allclose(composite_stud_alpha(80, 20), 1.0)

    def test_ratio_exactly_3(self):
        # h_wc/d = 3.0 → alpha = 0.2*(3+1) = 0.8
        assert_allclose(composite_stud_alpha(57, 19), 0.2 * (57 / 19 + 1), rtol=1e-6)

    def test_ratio_below_3_raises(self):
        # h_wc/d = 2.0 < 3 → error
        with pytest.raises(ValueError):
            composite_stud_alpha(40, 20)

    def test_ntc_ref(self):
        ref = get_ntc_ref(composite_stud_alpha)
        assert ref is not None
        assert "4.3.11" in ref.formula


# ---------------------------------------------------------------------------
# 4. composite_stud_resistance  [4.3.9] / [4.3.10]
# ---------------------------------------------------------------------------
class TestCompositeStudResistance:
    """NTC18 §4.3.4.3.1.2 — Resistenza a taglio del piolo connettore."""

    def test_concrete_governs(self):
        # d=19, h_wc=100, f_u=450, f_ck=25, E_cm=31000, gamma_V=1.25
        # alpha=1.0, P_steel = 0.8*450*pi*19^2/4/1.25 = 81656 N
        # P_concrete = 0.29*1.0*19^2*sqrt(25*31000)/1.25 = 73753 N
        P_Rd = composite_stud_resistance(19, 100, 450, 25, 31000, 1.25)
        P_steel = 0.8 * 450 * math.pi * 19**2 / 4 / 1.25
        P_concrete = 0.29 * 1.0 * 19**2 * math.sqrt(25 * 31000) / 1.25
        expected = min(P_steel, P_concrete)
        assert_allclose(P_Rd, expected, rtol=1e-6)
        assert P_Rd == pytest.approx(P_concrete, rel=1e-6)

    def test_steel_governs(self):
        # d=16, h_wc=70, f_u=400, f_ck=50, E_cm=37000, gamma_V=1.25
        P_Rd = composite_stud_resistance(16, 70, 400, 50, 37000, 1.25)
        P_steel = 0.8 * 400 * math.pi * 16**2 / 4 / 1.25
        P_concrete = 0.29 * 1.0 * 16**2 * math.sqrt(50 * 37000) / 1.25
        expected = min(P_steel, P_concrete)
        assert_allclose(P_Rd, expected, rtol=1e-6)
        assert P_Rd == pytest.approx(P_steel, rel=1e-6)

    def test_alpha_affects_concrete_mode(self):
        # h_wc/d = 60/19 = 3.16 → alpha = 0.832
        P_Rd = composite_stud_resistance(19, 60, 450, 25, 31000, 1.25)
        alpha = 0.2 * (60 / 19 + 1)
        P_concrete = 0.29 * alpha * 19**2 * math.sqrt(25 * 31000) / 1.25
        P_steel = 0.8 * 450 * math.pi * 19**2 / 4 / 1.25
        assert_allclose(P_Rd, min(P_steel, P_concrete), rtol=1e-6)

    def test_f_u_capped_at_500(self):
        # f_u=600 should be capped to 500 for steel mode
        P_Rd = composite_stud_resistance(19, 100, 600, 25, 31000, 1.25)
        P_steel_capped = 0.8 * 500 * math.pi * 19**2 / 4 / 1.25
        P_concrete = 0.29 * 1.0 * 19**2 * math.sqrt(25 * 31000) / 1.25
        assert_allclose(P_Rd, min(P_steel_capped, P_concrete), rtol=1e-6)

    def test_ntc_ref(self):
        ref = get_ntc_ref(composite_stud_resistance)
        assert ref is not None
        assert "4.3.9" in ref.formula


# ---------------------------------------------------------------------------
# 5. composite_profiled_sheet_reduction  [4.3.13] / [4.3.14]
# ---------------------------------------------------------------------------
class TestCompositeProfiledSheetReduction:
    """NTC18 §4.3.4.3.1.2 — Fattore riduttivo per lamiera grecata."""

    def test_parallel(self):
        # b_0=100, h_wc=100, h_p=60 (parallel)
        # k1 = 0.6 * 100 * (100-60) / 60^2 = 0.667
        k1 = composite_profiled_sheet_reduction(100, 100, 60, "parallel")
        assert_allclose(k1, 0.6 * 100 * 40 / 3600, rtol=1e-6)

    def test_parallel_capped_at_1(self):
        # very wide b_0, small h_p → k1 > 1.0, capped
        k1 = composite_profiled_sheet_reduction(300, 120, 40, "parallel")
        assert k1 <= 1.0

    def test_parallel_h_wc_capped(self):
        # h_wc=200, h_p=60 → h_wc_eff = min(200, 60+75) = 135
        # k1 = 0.6 * 100 * (135-60) / 60^2 = 0.6*100*75/3600 = 1.25 → capped to 1.0
        k1 = composite_profiled_sheet_reduction(100, 200, 60, "parallel")
        assert k1 <= 1.0

    def test_transverse_single_stud(self):
        # b_0=100, h_wc=100, h_p=60, n_studs=1
        # k1 = 0.7 * 100 * (100-60) / (60^2 * sqrt(1)) = 0.778
        k1 = composite_profiled_sheet_reduction(100, 100, 60, "transverse", n_studs=1)
        assert_allclose(k1, 0.7 * 100 * 40 / 3600, rtol=1e-6)

    def test_transverse_two_studs(self):
        # n_studs=2 → divide by sqrt(2)
        k1 = composite_profiled_sheet_reduction(100, 100, 60, "transverse", n_studs=2)
        expected = 0.7 * 100 * 40 / (3600 * math.sqrt(2))
        assert_allclose(k1, expected, rtol=1e-6)

    def test_invalid_direction(self):
        with pytest.raises(ValueError):
            composite_profiled_sheet_reduction(100, 100, 60, "diagonal")

    def test_ntc_ref(self):
        ref = get_ntc_ref(composite_profiled_sheet_reduction)
        assert ref is not None
        assert "4.3.13" in ref.formula


# ---------------------------------------------------------------------------
# 6. composite_minimum_connection_degree  [4.3.7] / [4.3.8]
# ---------------------------------------------------------------------------
class TestCompositeMinimumConnectionDegree:
    """NTC18 §4.3.4.3.1.1 — Grado minimo di connessione."""

    def test_standard_Lc_20_S355(self):
        # f_yk=355, L_c=20 → eta = max[1-(355/355)*(1-0.04*20); 0.4] = max[0.8; 0.4]
        eta = composite_minimum_connection_degree(355, 20, stud_type="standard")
        assert_allclose(eta, 0.8, rtol=1e-6)

    def test_standard_Lc_25_full(self):
        # f_yk=355, L_c=25 → eta = max[1-1*(1-1.0); 0.4] = 1.0
        eta = composite_minimum_connection_degree(355, 25, stud_type="standard")
        assert_allclose(eta, 1.0, rtol=1e-6)

    def test_standard_Lc_above_25(self):
        # L_c > 25 → eta >= 1.0
        eta = composite_minimum_connection_degree(355, 30, stud_type="standard")
        assert_allclose(eta, 1.0, rtol=1e-6)

    def test_standard_low_strength(self):
        # f_yk=235, L_c=10 → eta = max[1-(355/235)*(1-0.4); 0.4]
        # = max[1-1.5106*0.6; 0.4] = max[0.0936; 0.4] = 0.4
        eta = composite_minimum_connection_degree(235, 10, stud_type="standard")
        assert_allclose(eta, 0.4, rtol=1e-3)

    def test_alternative_Lc_10_S355(self):
        # f_yk=355, L_c=10, alternative studs
        # eta = max[1-(355/355)*(0.75-0.03*10); 0.4] = max[1-0.45; 0.4] = 0.55
        eta = composite_minimum_connection_degree(355, 10, stud_type="alternative")
        assert_allclose(eta, 0.55, rtol=1e-6)

    def test_alternative_Lc_above_25(self):
        eta = composite_minimum_connection_degree(355, 30, stud_type="alternative")
        assert_allclose(eta, 1.0, rtol=1e-6)

    def test_ntc_ref(self):
        ref = get_ntc_ref(composite_minimum_connection_degree)
        assert ref is not None
        assert "4.3.7" in ref.formula


# ---------------------------------------------------------------------------
# 7. composite_column_plastic_resistance  [4.3.21]
# ---------------------------------------------------------------------------
class TestCompositeColumnPlasticResistance:
    """NTC18 §4.3.5.3.1 — Resistenza plastica a compressione."""

    def test_standard_section(self):
        # A_a=10000, f_yk=355, gamma_A=1.05
        # A_c=90000, f_ck=25, gamma_C=1.5
        # A_s=2000, f_sk=450, gamma_S=1.15
        N_pl = composite_column_plastic_resistance(
            10000, 355, 1.05, 90000, 25, 1.5, 2000, 450, 1.15
        )
        expected = 10000 * 355 / 1.05 + 0.85 * 90000 * 25 / 1.5 + 2000 * 450 / 1.15
        assert_allclose(N_pl, expected, rtol=1e-6)

    def test_filled_section_coeff_1(self):
        # Filled sections: 0.85 replaced by 1.0
        N_pl = composite_column_plastic_resistance(
            10000, 355, 1.05, 90000, 25, 1.5, 2000, 450, 1.15, filled=True
        )
        expected = 10000 * 355 / 1.05 + 1.0 * 90000 * 25 / 1.5 + 2000 * 450 / 1.15
        assert_allclose(N_pl, expected, rtol=1e-6)

    def test_no_reinforcement(self):
        N_pl = composite_column_plastic_resistance(
            10000, 355, 1.05, 90000, 25, 1.5, 0, 450, 1.15
        )
        expected = 10000 * 355 / 1.05 + 0.85 * 90000 * 25 / 1.5
        assert_allclose(N_pl, expected, rtol=1e-6)

    def test_ntc_ref(self):
        ref = get_ntc_ref(composite_column_plastic_resistance)
        assert ref is not None
        assert ref.formula == "4.3.21"


# ---------------------------------------------------------------------------
# 8. composite_concrete_part_resistance  [4.3.25]
# ---------------------------------------------------------------------------
class TestCompositeConcretePartResistance:
    """NTC18 §4.3.5.3.1 — Sforzo normale resistente parte in calcestruzzo."""

    def test_standard(self):
        # A_c=90000, f_ck=25, gamma_C=1.5
        # N_pm = 0.85 * 25/1.5 * 90000 = 1275000 N
        N_pm = composite_concrete_part_resistance(90000, 25, 1.5)
        assert_allclose(N_pm, 0.85 * 25 / 1.5 * 90000, rtol=1e-6)

    def test_high_strength_concrete(self):
        N_pm = composite_concrete_part_resistance(50000, 50, 1.5)
        assert_allclose(N_pm, 0.85 * 50 / 1.5 * 50000, rtol=1e-6)

    def test_ntc_ref(self):
        ref = get_ntc_ref(composite_concrete_part_resistance)
        assert ref is not None
        assert ref.formula == "4.3.25"


# ---------------------------------------------------------------------------
# 9. composite_steel_contribution_ratio  [4.3.15]
# ---------------------------------------------------------------------------
class TestCompositeSteelContributionRatio:
    """NTC18 §4.3.5.2 — Contributo meccanico del profilato in acciaio."""

    def test_within_limits(self):
        # delta = A_a*f_yk / (gamma_A * N_pl_Rd)
        N_pl_Rd = 5_438_561.0
        delta = composite_steel_contribution_ratio(10000, 355, 1.05, N_pl_Rd)
        expected = 10000 * 355 / (1.05 * N_pl_Rd)
        assert_allclose(delta, expected, rtol=1e-6)

    def test_lower_limit(self):
        # delta < 0.2 → should raise
        with pytest.raises(ValueError):
            # Very small steel, large N_pl → delta < 0.2
            composite_steel_contribution_ratio(100, 235, 1.05, 1_000_000)

    def test_upper_limit(self):
        # delta > 0.9 → should raise
        with pytest.raises(ValueError):
            # Very large steel contribution
            composite_steel_contribution_ratio(10000, 355, 1.05, 3_500_000)

    def test_at_boundary_02(self):
        # Exactly 0.2 → should pass
        # Need N_pl_Rd such that 10000*355/(1.05*N_pl) = 0.2
        # N_pl = 10000*355/(1.05*0.2) = 16904762
        N_pl_Rd = 10000 * 355 / (1.05 * 0.2)
        delta = composite_steel_contribution_ratio(10000, 355, 1.05, N_pl_Rd)
        assert_allclose(delta, 0.2, rtol=1e-6)

    def test_ntc_ref(self):
        ref = get_ntc_ref(composite_steel_contribution_ratio)
        assert ref is not None
        assert ref.formula == "4.3.15"


# ---------------------------------------------------------------------------
# 10. composite_column_effective_stiffness  [4.3.16] / [4.3.17]
# ---------------------------------------------------------------------------
class TestCompositeColumnEffectiveStiffness:
    """NTC18 §4.3.5.2 — Rigidezza flessionale efficace."""

    def test_standard(self):
        # E_a=210000, I_a=50e6, E_s=210000, I_s=5e6, E_cm=31000, I_c=200e6
        # phi_t=2.0, N_G=1000e3, N_Ed=1500e3
        # E_c_eff = 31000 / (1 + 2.0*1000e3/1500e3) = 31000/2.333 = 13285.7
        # EI_eff = 210000*50e6 + 210000*5e6 + 0.6*13285.7*200e6
        EI = composite_column_effective_stiffness(
            210000, 50e6, 210000, 5e6, 31000, 200e6, 2.0, 1000e3, 1500e3
        )
        E_c_eff = 31000 / (1 + 2.0 * 1000e3 / 1500e3)
        expected = 210000 * 50e6 + 210000 * 5e6 + 0.6 * E_c_eff * 200e6
        assert_allclose(EI, expected, rtol=1e-6)

    def test_no_creep(self):
        # phi_t=0 → E_c_eff = E_cm (no creep)
        EI = composite_column_effective_stiffness(
            210000, 50e6, 210000, 5e6, 31000, 200e6, 0, 0, 1500e3
        )
        expected = 210000 * 50e6 + 210000 * 5e6 + 0.6 * 31000 * 200e6
        assert_allclose(EI, expected, rtol=1e-6)

    def test_all_permanent(self):
        # N_G_Ed = N_Ed → ratio = 1.0
        EI = composite_column_effective_stiffness(
            210000, 50e6, 210000, 5e6, 31000, 200e6, 2.0, 1500e3, 1500e3
        )
        E_c_eff = 31000 / (1 + 2.0)
        expected = 210000 * 50e6 + 210000 * 5e6 + 0.6 * E_c_eff * 200e6
        assert_allclose(EI, expected, rtol=1e-6)

    def test_ntc_ref(self):
        ref = get_ntc_ref(composite_column_effective_stiffness)
        assert ref is not None
        assert "4.3.16" in ref.formula


# ---------------------------------------------------------------------------
# 11. composite_column_slenderness  [4.3.18]
# ---------------------------------------------------------------------------
class TestCompositeColumnSlenderness:
    """NTC18 §4.3.5.2 — Snellezza normalizzata."""

    def test_standard(self):
        # N_pl_Rk=6_362_500, N_cr=20_000_000
        lam = composite_column_slenderness(6_362_500, 20_000_000)
        assert_allclose(lam, math.sqrt(6_362_500 / 20_000_000), rtol=1e-6)

    def test_limit_2(self):
        # lambda_bar >= 2.0 should raise
        with pytest.raises(ValueError):
            composite_column_slenderness(10_000_000, 2_000_000)  # sqrt(5) = 2.24

    def test_low_slenderness(self):
        lam = composite_column_slenderness(1_000_000, 100_000_000)
        assert_allclose(lam, 0.1, rtol=1e-6)

    def test_ntc_ref(self):
        ref = get_ntc_ref(composite_column_slenderness)
        assert ref is not None
        assert ref.formula == "4.3.18"


# ---------------------------------------------------------------------------
# 12. composite_column_buckling_curve  [Tab.4.3.III]
# ---------------------------------------------------------------------------
class TestCompositeColumnBucklingCurve:
    """NTC18 §4.3.5.4.1 Tab.4.3.III — Curve di instabilita'."""

    def test_fully_encased_yy(self):
        curve, alpha = composite_column_buckling_curve("fully_encased", "y-y")
        assert curve == "b"
        assert_allclose(alpha, 0.34)

    def test_fully_encased_zz(self):
        curve, alpha = composite_column_buckling_curve("fully_encased", "z-z")
        assert curve == "c"
        assert_allclose(alpha, 0.49)

    def test_partially_encased_yy(self):
        curve, alpha = composite_column_buckling_curve("partially_encased", "y-y")
        assert curve == "b"
        assert_allclose(alpha, 0.34)

    def test_filled_low_reinforcement(self):
        # rho_s < 3% → curve a, alpha=0.21
        curve, alpha = composite_column_buckling_curve("filled", "any", rho_s=0.02)
        assert curve == "a"
        assert_allclose(alpha, 0.21)

    def test_filled_medium_reinforcement(self):
        # 3% <= rho_s < 6% → curve b, alpha=0.34
        curve, alpha = composite_column_buckling_curve("filled", "any", rho_s=0.04)
        assert curve == "b"
        assert_allclose(alpha, 0.34)

    def test_filled_high_reinforcement(self):
        # rho_s >= 6% → curve c, alpha=0.49
        curve, alpha = composite_column_buckling_curve("filled", "any", rho_s=0.06)
        assert curve == "c"
        assert_allclose(alpha, 0.49)

    def test_invalid_section_type(self):
        with pytest.raises(ValueError):
            composite_column_buckling_curve("timber", "y-y")

    def test_ntc_ref(self):
        ref = get_ntc_ref(composite_column_buckling_curve)
        assert ref is not None
        assert "Tab.4.3.III" in ref.table


# ---------------------------------------------------------------------------
# 13. composite_column_buckling_resistance  [4.3.29] / [4.3.30]
# ---------------------------------------------------------------------------
class TestCompositeColumnBucklingResistance:
    """NTC18 §4.3.5.4.1 — Resistenza all'instabilita'."""

    def test_standard(self):
        # lambda_bar=0.564, alpha=0.34, N_pl_Rd=5438561
        lam = 0.564
        alpha = 0.34
        N_pl = 5_438_561
        phi = 0.5 * (1 + alpha * (lam - 0.2) + lam**2)
        chi_exp = 1 / (phi + math.sqrt(phi**2 - lam**2))
        chi, N_b = composite_column_buckling_resistance(lam, alpha, N_pl)
        assert_allclose(chi, chi_exp, rtol=1e-6)
        assert_allclose(N_b, chi_exp * N_pl, rtol=1e-6)

    def test_low_slenderness(self):
        # lambda_bar very small → chi close to 1.0
        chi, N_b = composite_column_buckling_resistance(0.1, 0.21, 5_000_000)
        assert chi > 0.95
        assert_allclose(N_b, chi * 5_000_000, rtol=1e-6)

    def test_chi_capped_at_1(self):
        # Very low slenderness → chi must not exceed 1.0
        chi, _ = composite_column_buckling_resistance(0.01, 0.21, 5_000_000)
        assert chi <= 1.0

    def test_high_slenderness(self):
        # lambda_bar close to 2.0 → chi much less than 1.0
        chi, N_b = composite_column_buckling_resistance(1.8, 0.49, 5_000_000)
        assert chi < 0.3

    def test_ntc_ref(self):
        ref = get_ntc_ref(composite_column_buckling_resistance)
        assert ref is not None
        assert "4.3.29" in ref.formula


# ---------------------------------------------------------------------------
# 14. composite_confinement_coefficients  [4.3.23] / [4.3.24]
# ---------------------------------------------------------------------------
class TestCompositeConfinementCoefficients:
    """NTC18 §4.3.5.3.1 — Coefficienti di confinamento sezioni circolari."""

    def test_zero_eccentricity(self):
        # lambda_bar=0.3, e/d=0
        # eta_a = min(0.25*(3+2*0.3), 1.0) = min(0.9, 1.0) = 0.9
        # eta_c = max(4.9 - 18.5*0.3 + 17*0.3^2, 0) = max(0.88, 0) = 0.88
        eta_a, eta_c = composite_confinement_coefficients(0.3, 0)
        assert_allclose(eta_a, 0.9, rtol=1e-6)
        assert_allclose(eta_c, 4.9 - 18.5 * 0.3 + 17 * 0.09, rtol=1e-6)

    def test_small_eccentricity(self):
        # lambda_bar=0.3, e/d=0.05
        # eta_a = 0.25*(3+2*0.3) + 10*(0.25-0.5*0.3)*0.05 = 0.9 + 10*0.1*0.05 = 0.95
        # eta_c = (4.9-18.5*0.3+17*0.09) * (1-10*0.05) = 0.88*0.5 = 0.44
        eta_a, eta_c = composite_confinement_coefficients(0.3, 0.05)
        assert_allclose(eta_a, 0.95, rtol=1e-6)
        assert_allclose(eta_c, 0.88 * 0.5, rtol=1e-3)

    def test_eccentricity_above_01(self):
        # e/d > 0.1 → eta_a=1.0, eta_c=0.0
        eta_a, eta_c = composite_confinement_coefficients(0.3, 0.2)
        assert_allclose(eta_a, 1.0)
        assert_allclose(eta_c, 0.0)

    def test_eta_a_capped_at_1(self):
        # lambda_bar=0.5 → 0.25*(3+1) = 1.0 exactly
        eta_a, _ = composite_confinement_coefficients(0.5, 0)
        assert eta_a <= 1.0

    def test_eta_c_non_negative(self):
        # High lambda → 4.9 - 18.5*lam + 17*lam^2 could be negative
        # At lam=0.7: 4.9 - 12.95 + 8.33 = 0.28 (still positive)
        # At lam=0.5: 4.9 - 9.25 + 4.25 = -0.1 (negative) → clamp to 0
        _, eta_c = composite_confinement_coefficients(0.5, 0)
        assert eta_c >= 0

    def test_lambda_at_limit(self):
        # lambda_bar must be <= 0.5 for confinement
        with pytest.raises(ValueError):
            composite_confinement_coefficients(0.6, 0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(composite_confinement_coefficients)
        assert ref is not None
        assert "4.3.23" in ref.formula


# ---------------------------------------------------------------------------
# 15. composite_column_local_buckling_check  [4.3.31-4.3.33]
# ---------------------------------------------------------------------------
class TestCompositeColumnLocalBucklingCheck:
    """NTC18 §4.3.5.4.2 — Instabilita' locale."""

    def test_circular_ok(self):
        # d=500, t=10, f_y=355 → d/t=50, limit=90*(235/355)=59.58 → OK
        passes, ratio = composite_column_local_buckling_check("circular", 500, 10, 355)
        assert passes is True
        assert ratio < 1.0

    def test_circular_fail(self):
        # d=600, t=8, f_y=355 → d/t=75 > 59.58 → FAIL
        passes, ratio = composite_column_local_buckling_check("circular", 600, 8, 355)
        assert passes is False
        assert ratio > 1.0

    def test_rectangular_ok(self):
        # d=300, t=10, f_y=355 → d/t=30, limit=52*sqrt(235/355)=42.31 → OK
        passes, ratio = composite_column_local_buckling_check("rectangular", 300, 10, 355)
        assert passes is True

    def test_rectangular_fail(self):
        # d=400, t=8, f_y=355 → d/t=50 > 42.31 → FAIL
        passes, ratio = composite_column_local_buckling_check("rectangular", 400, 8, 355)
        assert passes is False

    def test_partially_encased_ok(self):
        # b=300, t=15, f_y=355 → b/t=20, limit=44*sqrt(235/355)=35.80 → OK
        passes, ratio = composite_column_local_buckling_check(
            "partially_encased", 300, 15, 355
        )
        assert passes is True

    def test_invalid_section_type(self):
        with pytest.raises(ValueError):
            composite_column_local_buckling_check("wooden", 300, 10, 355)

    def test_ntc_ref(self):
        ref = get_ntc_ref(composite_column_local_buckling_check)
        assert ref is not None
        assert "4.3.31" in ref.formula


# ---------------------------------------------------------------------------
# 16. composite_column_bending_check  [4.3.35]
# ---------------------------------------------------------------------------
class TestCompositeColumnBendingCheck:
    """NTC18 §4.3.5.4.3 — Verifica a pressoflessione."""

    def test_passes(self):
        # M_Ed=200e6, mu_d=0.8, M_pl_Rd=400e6, alpha_M=0.9
        # ratio = 200e6 / (0.9*0.8*400e6) = 0.694
        passes, ratio = composite_column_bending_check(200e6, 0.8, 400e6, 0.9)
        assert passes is True
        assert_allclose(ratio, 200e6 / (0.9 * 0.8 * 400e6), rtol=1e-6)

    def test_fails(self):
        # M_Ed=350e6, mu_d=0.8, M_pl_Rd=400e6, alpha_M=0.9
        passes, ratio = composite_column_bending_check(350e6, 0.8, 400e6, 0.9)
        assert passes is False
        assert ratio > 1.0

    def test_alpha_M_08_for_S460(self):
        # alpha_M=0.8 for S420/S460
        passes, ratio = composite_column_bending_check(250e6, 0.8, 400e6, 0.8)
        expected_ratio = 250e6 / (0.8 * 0.8 * 400e6)
        assert_allclose(ratio, expected_ratio, rtol=1e-6)

    def test_ntc_ref(self):
        ref = get_ntc_ref(composite_column_bending_check)
        assert ref is not None
        assert ref.formula == "4.3.35"


# ---------------------------------------------------------------------------
# 17. composite_moment_amplification  [4.3.36] / [4.3.37]
# ---------------------------------------------------------------------------
class TestCompositeMomentAmplification:
    """NTC18 §4.3.5.4.3 — Amplificazione del momento per effetti del II ordine."""

    def test_linear_distribution(self):
        # M_min/M_max = 0.5 → beta = 0.66+0.44*0.5 = 0.88
        # k = 0.88 / (1-3000e3/15000e3) = 0.88/0.8 = 1.1
        k = composite_moment_amplification(3000e3, 15000e3, M_min=100, M_max=200)
        beta = 0.66 + 0.44 * 0.5
        expected = beta / (1 - 3000e3 / 15000e3)
        assert_allclose(k, expected, rtol=1e-6)

    def test_constant_moment(self):
        # M_min = M_max → beta = 0.66+0.44*1 = 1.1
        k = composite_moment_amplification(3000e3, 15000e3, M_min=200, M_max=200)
        expected = 1.1 / (1 - 3000e3 / 15000e3)
        assert_allclose(k, expected, rtol=1e-6)

    def test_parabolic(self):
        # No M_min/M_max → beta = 1.0
        k = composite_moment_amplification(3000e3, 15000e3)
        expected = 1.0 / (1 - 3000e3 / 15000e3)
        assert_allclose(k, expected, rtol=1e-6)

    def test_k_minimum_1(self):
        # When N_Ed is very small → k approaches beta < 1 → capped to 1.0
        k = composite_moment_amplification(100, 15000e3, M_min=-100, M_max=200)
        assert k >= 1.0

    def test_beta_minimum_044(self):
        # M_min/M_max very negative → beta capped to 0.44
        k = composite_moment_amplification(3000e3, 15000e3, M_min=-200, M_max=200)
        beta = max(0.66 + 0.44 * (-1.0), 0.44)
        expected = max(beta / (1 - 3000e3 / 15000e3), 1.0)
        assert_allclose(k, expected, rtol=1e-6)

    def test_ntc_ref(self):
        ref = get_ntc_ref(composite_moment_amplification)
        assert ref is not None
        assert "4.3.36" in ref.formula


# ---------------------------------------------------------------------------
# 18. composite_column_biaxial_check  [4.3.27]
# ---------------------------------------------------------------------------
class TestCompositeColumnBiaxialCheck:
    """NTC18 §4.3.5.3.1 — Verifica a pressoflessione deviata."""

    def test_passes(self):
        # M_y=150e6, M_z=80e6, mu_dy=0.8, mu_dz=0.7
        # M_pl_y=400e6, M_pl_z=300e6, alpha=0.9
        passes, ratio = composite_column_biaxial_check(
            150e6, 80e6, 0.8, 0.7, 400e6, 300e6, 0.9, 0.9
        )
        r_y = 150e6 / (0.8 * 400e6)
        r_z = 80e6 / (0.7 * 300e6)
        assert passes is True
        assert_allclose(ratio, r_y + r_z, rtol=1e-6)

    def test_fails_interaction(self):
        # Sum of ratios > 1.0
        passes, ratio = composite_column_biaxial_check(
            300e6, 200e6, 0.8, 0.7, 400e6, 300e6, 0.9, 0.9
        )
        assert passes is False

    def test_fails_single_axis_y(self):
        # M_y exceeds alpha_M_y limit
        passes, _ = composite_column_biaxial_check(
            400e6, 10e6, 0.8, 0.7, 400e6, 300e6, 0.9, 0.9
        )
        assert passes is False

    def test_fails_single_axis_z(self):
        # M_z exceeds alpha_M_z limit
        passes, _ = composite_column_biaxial_check(
            10e6, 250e6, 0.8, 0.7, 400e6, 300e6, 0.9, 0.9
        )
        assert passes is False

    def test_ntc_ref(self):
        ref = get_ntc_ref(composite_column_biaxial_check)
        assert ref is not None
        assert ref.formula == "4.3.27"


# ---------------------------------------------------------------------------
# 19. composite_beam_shear_distribution  [4.3.28]
# ---------------------------------------------------------------------------
class TestCompositeBeamShearDistribution:
    """NTC18 §4.3.5.3.2 — Distribuzione del taglio."""

    def test_equal_moments(self):
        # M_pl_a = M_pl → all shear to steel
        V_a, V_c = composite_beam_shear_distribution(500e3, 300e6, 300e6)
        assert_allclose(V_a, 500e3)
        assert_allclose(V_c, 0, atol=1e-6)

    def test_standard(self):
        # V=500e3, M_pl_a=300e6, M_pl=600e6 → V_a=250e3, V_c=250e3
        V_a, V_c = composite_beam_shear_distribution(500e3, 300e6, 600e6)
        assert_allclose(V_a, 250e3)
        assert_allclose(V_c, 250e3)

    def test_sum_equals_total(self):
        V_Ed = 800e3
        V_a, V_c = composite_beam_shear_distribution(V_Ed, 200e6, 500e6)
        assert_allclose(V_a + V_c, V_Ed)

    def test_ntc_ref(self):
        ref = get_ntc_ref(composite_beam_shear_distribution)
        assert ref is not None
        assert ref.formula == "4.3.28"


# ---------------------------------------------------------------------------
# 20. composite_bond_stress_limit  [§4.3.5.5.1]
# ---------------------------------------------------------------------------
class TestCompositeBondStressLimit:
    """NTC18 §4.3.5.5.1 — Tensione tangenziale limite di aderenza."""

    def test_fully_encased(self):
        assert_allclose(composite_bond_stress_limit("fully_encased"), 0.30)

    def test_filled_circular(self):
        assert_allclose(composite_bond_stress_limit("filled_circular"), 0.55)

    def test_filled_rectangular(self):
        assert_allclose(composite_bond_stress_limit("filled_rectangular"), 0.40)

    def test_partially_encased_flange(self):
        assert_allclose(composite_bond_stress_limit("partially_encased_flange"), 0.20)

    def test_partially_encased_web(self):
        assert_allclose(composite_bond_stress_limit("partially_encased_web"), 0.0)

    def test_invalid_type(self):
        with pytest.raises(ValueError):
            composite_bond_stress_limit("unknown")

    def test_ntc_ref(self):
        ref = get_ntc_ref(composite_bond_stress_limit)
        assert ref is not None
        assert "4.3.5.5" in ref.article


# ---------------------------------------------------------------------------
# 21. composite_column_plastic_resistance_characteristic  [4.3.19]
# ---------------------------------------------------------------------------
class TestCompositeColumnPlasticResistanceCharacteristic:
    """NTC18 §4.3.5.2 — Resistenza plastica caratteristica N_pl,Rk."""

    def test_standard_section(self):
        # A_a=10000, f_yk=355, A_c=90000, f_ck=25, A_s=2000, f_sk=450
        # N_pl,Rk = 10000*355 + 0.85*90000*25 + 2000*450
        N_plRk = composite_column_plastic_resistance_characteristic(
            10000, 355, 90000, 25, 2000, 450
        )
        expected = 10000 * 355 + 0.85 * 90000 * 25 + 2000 * 450
        assert_allclose(N_plRk, expected, rtol=1e-6)

    def test_filled_section_coeff_1(self):
        # Filled: coefficient = 1.0 instead of 0.85
        N_plRk = composite_column_plastic_resistance_characteristic(
            10000, 355, 90000, 25, 2000, 450, filled=True
        )
        expected = 10000 * 355 + 1.0 * 90000 * 25 + 2000 * 450
        assert_allclose(N_plRk, expected, rtol=1e-6)

    def test_no_reinforcement(self):
        N_plRk = composite_column_plastic_resistance_characteristic(
            10000, 355, 90000, 25, 0, 450
        )
        expected = 10000 * 355 + 0.85 * 90000 * 25
        assert_allclose(N_plRk, expected, rtol=1e-6)

    def test_larger_than_N_pl_Rd(self):
        # N_pl,Rk (no gamma) must be larger than N_pl,Rd (with gamma > 1)
        N_plRk = composite_column_plastic_resistance_characteristic(
            10000, 355, 90000, 25, 2000, 450
        )
        from pyntc.checks.composite import composite_column_plastic_resistance
        N_plRd = composite_column_plastic_resistance(
            10000, 355, 1.05, 90000, 25, 1.5, 2000, 450, 1.15
        )
        assert N_plRk > N_plRd

    def test_ntc_ref(self):
        ref = get_ntc_ref(composite_column_plastic_resistance_characteristic)
        assert ref is not None
        assert ref.formula == "4.3.19"


# ---------------------------------------------------------------------------
# 22. composite_column_effective_stiffness_ii  [4.3.20]
# ---------------------------------------------------------------------------
class TestCompositeColumnEffectiveStiffnessII:
    """NTC18 §4.3.5.2 — Rigidezza flessionale efficace di II ordine."""

    def test_default_coefficients(self):
        # Default: k_0=0.9, k_c_ii=0.5
        # (EI)_eff,II = 0.9*(210000*50e6 + 210000*5e6 + 0.5*31000*200e6)
        EI = composite_column_effective_stiffness_ii(
            210000, 50e6, 210000, 5e6, 31000, 200e6
        )
        expected = 0.9 * (210000 * 50e6 + 210000 * 5e6 + 0.5 * 31000 * 200e6)
        assert_allclose(EI, expected, rtol=1e-6)

    def test_custom_coefficients(self):
        EI = composite_column_effective_stiffness_ii(
            210000, 50e6, 210000, 5e6, 31000, 200e6, k_0=0.85, k_c_ii=0.45
        )
        expected = 0.85 * (210000 * 50e6 + 210000 * 5e6 + 0.45 * 31000 * 200e6)
        assert_allclose(EI, expected, rtol=1e-6)

    def test_no_concrete(self):
        # I_c=0 → concrete term vanishes
        EI = composite_column_effective_stiffness_ii(
            210000, 50e6, 210000, 5e6, 31000, 0.0
        )
        expected = 0.9 * (210000 * 50e6 + 210000 * 5e6)
        assert_allclose(EI, expected, rtol=1e-6)

    def test_stiffness_ii_less_than_stiffness_i(self):
        # (EI)_eff,II (k_0=0.9, k_c=0.5) < (EI)_eff (k_a=0.6, no k_0)
        from pyntc.checks.composite import composite_column_effective_stiffness
        EI_ii = composite_column_effective_stiffness_ii(
            210000, 50e6, 210000, 5e6, 31000, 200e6
        )
        EI_i = composite_column_effective_stiffness(
            210000, 50e6, 210000, 5e6, 31000, 200e6, 0, 0, 1
        )
        # With default k_0=0.9 and k_c_ii=0.5 vs k_a=0.6, EI_II is smaller
        assert EI_ii < EI_i

    def test_ntc_ref(self):
        ref = get_ntc_ref(composite_column_effective_stiffness_ii)
        assert ref is not None
        assert ref.formula == "4.3.20"


# ---------------------------------------------------------------------------
# 23. composite_column_confinement_resistance  [4.3.22]
# ---------------------------------------------------------------------------
class TestCompositeColumnConfinementResistance:
    """NTC18 §4.3.5.3.1 — Resistenza plastica con confinamento (sezioni circolari)."""

    def test_no_confinement(self):
        # eta_a=1.0, eta_c=0.0: degenerates to standard formula without confinement
        # (but concrete term still gets the (1 + 0*t/d*...) factor = 1.0)
        N = composite_column_confinement_resistance(
            10000, 355, 1.05, 90000, 25, 1.5, 2000, 450, 1.15,
            t=10, d=250, eta_a=1.0, eta_c=0.0
        )
        expected = (
            1.0 * 10000 * 355 / 1.05
            + (90000 * 25 / 1.5) * (1 + 0.0 * 10 / 250 * 355 / 25)
            + 2000 * 450 / 1.15
        )
        assert_allclose(N, expected, rtol=1e-6)

    def test_with_confinement_increases_resistance(self):
        # Confinement should increase N relative to no-confinement base case
        N_base = composite_column_confinement_resistance(
            10000, 355, 1.05, 90000, 25, 1.5, 2000, 450, 1.15,
            t=10, d=250, eta_a=1.0, eta_c=0.0
        )
        N_confined = composite_column_confinement_resistance(
            10000, 355, 1.05, 90000, 25, 1.5, 2000, 450, 1.15,
            t=10, d=250, eta_a=0.9, eta_c=4.5
        )
        # eta_c > 0: concrete term increased, eta_a < 1: steel term reduced
        # net effect with eta_c=4.5 dominates → N_confined > N_base
        assert N_confined > N_base

    def test_manual_calculation(self):
        # d=250, t=10, eta_a=0.75, eta_c=3.5
        # A_a=7363, f_yk=355, gamma_A=1.05
        # A_c=41230, f_ck=30, gamma_C=1.5
        # A_s=800, f_sk=450, gamma_S=1.15
        N = composite_column_confinement_resistance(
            7363, 355, 1.05, 41230, 30, 1.5, 800, 450, 1.15,
            t=10, d=250, eta_a=0.75, eta_c=3.5
        )
        N_steel = 0.75 * 7363 * 355 / 1.05
        N_concrete = (41230 * 30 / 1.5) * (1 + 3.5 * (10 / 250) * (355 / 30))
        N_rebar = 800 * 450 / 1.15
        expected = N_steel + N_concrete + N_rebar
        assert_allclose(N, expected, rtol=1e-6)

    def test_ntc_ref(self):
        ref = get_ntc_ref(composite_column_confinement_resistance)
        assert ref is not None
        assert ref.formula == "4.3.22"


# ---------------------------------------------------------------------------
# 24. composite_column_reduced_moment_resistance  [4.3.26]
# ---------------------------------------------------------------------------
class TestCompositeColumnReducedMomentResistance:
    """NTC18 §4.3.5.3.1 — Momento resistente ridotto da interazione N-M."""

    def test_standard(self):
        # mu_d=0.8, M_pl_Rd=500e6 → M=400e6
        M = composite_column_reduced_moment_resistance(0.8, 500e6)
        assert_allclose(M, 400e6, rtol=1e-6)

    def test_full_moment(self):
        # mu_d=1.0 → M = M_pl_Rd
        M = composite_column_reduced_moment_resistance(1.0, 500e6)
        assert_allclose(M, 500e6, rtol=1e-6)

    def test_zero_moment(self):
        # mu_d=0.0 → M = 0
        M = composite_column_reduced_moment_resistance(0.0, 500e6)
        assert_allclose(M, 0.0, atol=1e-6)

    def test_invalid_mu_d_negative(self):
        with pytest.raises(ValueError):
            composite_column_reduced_moment_resistance(-0.1, 500e6)

    def test_invalid_mu_d_above_1(self):
        with pytest.raises(ValueError):
            composite_column_reduced_moment_resistance(1.1, 500e6)

    def test_ntc_ref(self):
        ref = get_ntc_ref(composite_column_reduced_moment_resistance)
        assert ref is not None
        assert ref.formula == "4.3.26"


# ---------------------------------------------------------------------------
# 25. composite_load_dispersion_width  [4.3.38]
# ---------------------------------------------------------------------------
class TestCompositeLoadDispersionWidth:
    """NTC18 §4.3.6.1.1 — Larghezza efficace di dispersione per carichi concentrati."""

    def test_standard(self):
        # b_p=200, h_c=100, h_t=50 → b_m = 200 + 2*(100+50) = 500
        b_m = composite_load_dispersion_width(200, 100, 50)
        assert_allclose(b_m, 500.0, rtol=1e-6)

    def test_no_overlay(self):
        # h_t=0 → b_m = b_p + 2*h_c
        b_m = composite_load_dispersion_width(300, 120, 0)
        assert_allclose(b_m, 300 + 2 * 120, rtol=1e-6)

    def test_wheel_load_typical(self):
        # Typical wheel patch: b_p=400, h_c=150, h_t=80
        b_m = composite_load_dispersion_width(400, 150, 80)
        assert_allclose(b_m, 400 + 2 * (150 + 80), rtol=1e-6)

    def test_ntc_ref(self):
        ref = get_ntc_ref(composite_load_dispersion_width)
        assert ref is not None
        assert ref.formula == "4.3.38"
