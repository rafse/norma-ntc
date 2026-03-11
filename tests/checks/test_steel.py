"""Test per steel — NTC18 §4.2."""

import math

import pytest
from numpy.testing import assert_allclose

from pyntc.checks.steel import (
    bolt_bearing_resistance,
    bolt_friction_resistance,
    bolt_friction_tension_resistance,
    bolt_punching_resistance,
    bolt_shear_resistance,
    bolt_shear_tension_interaction,
    bolt_tension_resistance,
    pin_bearing_resistance,
    pin_shear_resistance,
    steel_bending_resistance,
    steel_bending_resistance_class3,
    steel_bending_resistance_class4,
    steel_bending_shear_reduction,
    steel_biaxial_check,
    steel_buckling_imperfection,
    steel_buckling_reduction,
    steel_buckling_resistance,
    steel_buckling_resistance_class4,
    steel_compression_resistance,
    steel_grade_properties,
    steel_lt_buckling_reduction,
    steel_lt_buckling_resistance,
    steel_NM_resistance_y,
    steel_NM_resistance_z,
    steel_relative_slenderness,
    steel_shear_area,
    steel_shear_resistance,
    steel_tension_resistance,
    steel_torsion_check,
    steel_torsion_resistance,
    steel_von_mises_check,
    weld_combined_stress_check,
    weld_fillet_resistance,
)
from pyntc.core.reference import get_ntc_ref


# ── Tab.4.2.I — Proprieta' acciaio laminato ─────────────────────────────────


class TestSteelGradeProperties:
    """NTC18 §4.2.1.1, Tab. 4.2.I — Acciaio laminato."""

    def test_s235_thin(self):
        """S235, t <= 40 mm: f_yk=235, f_tk=360 N/mm^2."""
        f_yk, f_tk = steel_grade_properties("S235", thickness=20.0)
        assert_allclose(f_yk, 235.0, rtol=1e-3)
        assert_allclose(f_tk, 360.0, rtol=1e-3)

    def test_s275_thin(self):
        """S275, t <= 40 mm: f_yk=275, f_tk=430 N/mm^2."""
        f_yk, f_tk = steel_grade_properties("S275", thickness=10.0)
        assert_allclose(f_yk, 275.0, rtol=1e-3)
        assert_allclose(f_tk, 430.0, rtol=1e-3)

    def test_s355_thin(self):
        """S355, t <= 40 mm: f_yk=355, f_tk=510 N/mm^2."""
        f_yk, f_tk = steel_grade_properties("S355", thickness=30.0)
        assert_allclose(f_yk, 355.0, rtol=1e-3)
        assert_allclose(f_tk, 510.0, rtol=1e-3)

    def test_s355_thick(self):
        """S355, 40 < t <= 80 mm: f_yk=335, f_tk=470 N/mm^2."""
        f_yk, f_tk = steel_grade_properties("S355", thickness=60.0)
        assert_allclose(f_yk, 335.0, rtol=1e-3)
        assert_allclose(f_tk, 470.0, rtol=1e-3)

    def test_s460_thin(self):
        """S460, t <= 40 mm: f_yk=460, f_tk=540 N/mm^2."""
        f_yk, f_tk = steel_grade_properties("S460", thickness=25.0)
        assert_allclose(f_yk, 460.0, rtol=1e-3)
        assert_allclose(f_tk, 540.0, rtol=1e-3)

    def test_s460_thick(self):
        """S460, 40 < t <= 80 mm: f_yk=430, f_tk=540 N/mm^2."""
        f_yk, f_tk = steel_grade_properties("S460", thickness=50.0)
        assert_allclose(f_yk, 430.0, rtol=1e-3)
        assert_allclose(f_tk, 540.0, rtol=1e-3)

    def test_invalid_grade_raises(self):
        with pytest.raises(ValueError, match="grade"):
            steel_grade_properties("S500", thickness=20.0)

    def test_thickness_over_80_raises(self):
        with pytest.raises(ValueError, match="thickness"):
            steel_grade_properties("S235", thickness=100.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(steel_grade_properties)
        assert ref is not None
        assert ref.article == "4.2.1.1"


# ── [4.2.6-4.2.7] — Resistenza a trazione ───────────────────────────────────


class TestSteelTensionResistance:
    """NTC18 §4.2.4.1.2.1, Formule [4.2.6-4.2.7]."""

    def test_plastic_only(self):
        """N_pl,Rd = A * f_yk / gamma_M0 = 5000 * 235 / 1.05 = 1119048 N."""
        N_pl, N_u = steel_tension_resistance(
            A=5000.0, f_yk=235.0, gamma_M0=1.05
        )
        assert_allclose(N_pl, 5000.0 * 235.0 / 1.05, rtol=1e-3)
        assert N_u is None

    def test_with_net_section(self):
        """N_u,Rd = 0.9 * A_net * f_tk / gamma_M2."""
        N_pl, N_u = steel_tension_resistance(
            A=5000.0, f_yk=235.0, gamma_M0=1.05,
            A_net=4200.0, f_tk=360.0, gamma_M2=1.25,
        )
        expected_N_pl = 5000.0 * 235.0 / 1.05
        expected_N_u = 0.9 * 4200.0 * 360.0 / 1.25
        assert_allclose(N_pl, expected_N_pl, rtol=1e-3)
        assert_allclose(N_u, expected_N_u, rtol=1e-3)

    def test_hierarchy_check(self):
        """Verifica che N_pl,Rd e N_u,Rd siano confrontabili per gerarchia [4.2.8]."""
        N_pl, N_u = steel_tension_resistance(
            A=5000.0, f_yk=235.0, gamma_M0=1.05,
            A_net=4500.0, f_tk=360.0, gamma_M2=1.25,
        )
        # Gerarchia: N_pl,Rd <= N_u,Rd per duttilita'
        assert N_pl <= N_u

    def test_negative_area_raises(self):
        with pytest.raises(ValueError):
            steel_tension_resistance(A=-1.0, f_yk=235.0, gamma_M0=1.05)

    def test_ntc_ref(self):
        ref = get_ntc_ref(steel_tension_resistance)
        assert ref is not None
        assert ref.article == "4.2.4.1.2.1"


# ── [4.2.10] — Resistenza a compressione ────────────────────────────────────


class TestSteelCompressionResistance:
    """NTC18 §4.2.4.1.2.2, Formula [4.2.10]."""

    def test_basic(self):
        """N_c,Rd = A * f_yk / gamma_M0 = 5000 * 355 / 1.05."""
        result = steel_compression_resistance(A=5000.0, f_yk=355.0, gamma_M0=1.05)
        assert_allclose(result, 5000.0 * 355.0 / 1.05, rtol=1e-3)

    def test_s235(self):
        """N_c,Rd con S235."""
        result = steel_compression_resistance(A=3000.0, f_yk=235.0, gamma_M0=1.05)
        assert_allclose(result, 3000.0 * 235.0 / 1.05, rtol=1e-3)

    def test_zero_area_raises(self):
        with pytest.raises(ValueError):
            steel_compression_resistance(A=0.0, f_yk=235.0, gamma_M0=1.05)

    def test_ntc_ref(self):
        ref = get_ntc_ref(steel_compression_resistance)
        assert ref is not None
        assert ref.article == "4.2.4.1.2.2"


# ── [4.2.12-4.2.14] — Resistenza a flessione ───────────────────────────────


class TestSteelBendingResistance:
    """NTC18 §4.2.4.1.2.3, Formule [4.2.12-4.2.14]."""

    def test_class_1_2(self):
        """M_c,Rd = W_pl * f_yk / gamma_M0."""
        result = steel_bending_resistance(W=500e3, f_yk=355.0, gamma_M0=1.05)
        assert_allclose(result, 500e3 * 355.0 / 1.05, rtol=1e-3)

    def test_class_3_elastic(self):
        """W_el < W_pl: ancora M = W * f_yk / gamma_M0."""
        result = steel_bending_resistance(W=400e3, f_yk=275.0, gamma_M0=1.05)
        assert_allclose(result, 400e3 * 275.0 / 1.05, rtol=1e-3)

    def test_s460(self):
        """Grado S460."""
        result = steel_bending_resistance(W=600e3, f_yk=460.0, gamma_M0=1.05)
        assert_allclose(result, 600e3 * 460.0 / 1.05, rtol=1e-3)

    def test_zero_W_raises(self):
        with pytest.raises(ValueError):
            steel_bending_resistance(W=0.0, f_yk=355.0, gamma_M0=1.05)

    def test_ntc_ref(self):
        ref = get_ntc_ref(steel_bending_resistance)
        assert ref is not None
        assert ref.article == "4.2.4.1.2.3"


# ── [4.2.17] — Resistenza a taglio ──────────────────────────────────────────


class TestSteelShearResistance:
    """NTC18 §4.2.4.1.2.4, Formula [4.2.17]."""

    def test_basic(self):
        """V_c,Rd = A_v * f_yk / (sqrt(3) * gamma_M0)."""
        result = steel_shear_resistance(A_v=3000.0, f_yk=355.0, gamma_M0=1.05)
        expected = 3000.0 * 355.0 / (math.sqrt(3) * 1.05)
        assert_allclose(result, expected, rtol=1e-3)

    def test_s235(self):
        """S235: V_c,Rd = 2000 * 235 / (sqrt(3) * 1.05)."""
        result = steel_shear_resistance(A_v=2000.0, f_yk=235.0, gamma_M0=1.05)
        expected = 2000.0 * 235.0 / (math.sqrt(3) * 1.05)
        assert_allclose(result, expected, rtol=1e-3)

    def test_zero_Av_raises(self):
        with pytest.raises(ValueError):
            steel_shear_resistance(A_v=0.0, f_yk=355.0, gamma_M0=1.05)

    def test_ntc_ref(self):
        ref = get_ntc_ref(steel_shear_resistance)
        assert ref is not None
        assert ref.article == "4.2.4.1.2.4"


# ── [4.2.30-4.2.31] — Riduzione flessione per taglio ────────────────────────


class TestSteelBendingShearReduction:
    """NTC18 §4.2.4.1.2.6, Formule [4.2.30-4.2.31]."""

    def test_low_shear_no_reduction(self):
        """V_Ed <= 0.5 * V_c,Rd: rho = 0."""
        rho = steel_bending_shear_reduction(V_Ed=100.0, V_c_Rd=400.0)
        assert_allclose(rho, 0.0, atol=1e-10)

    def test_exactly_half(self):
        """V_Ed = 0.5 * V_c,Rd: rho = 0 (boundary)."""
        rho = steel_bending_shear_reduction(V_Ed=200.0, V_c_Rd=400.0)
        assert_allclose(rho, 0.0, atol=1e-10)

    def test_high_shear(self):
        """V_Ed = 300, V_c,Rd = 400: rho = (2*300/400 - 1)^2 = 0.25."""
        rho = steel_bending_shear_reduction(V_Ed=300.0, V_c_Rd=400.0)
        expected = (2.0 * 300.0 / 400.0 - 1.0) ** 2
        assert_allclose(rho, expected, rtol=1e-3)

    def test_full_shear(self):
        """V_Ed = V_c,Rd: rho = (2 - 1)^2 = 1.0."""
        rho = steel_bending_shear_reduction(V_Ed=400.0, V_c_Rd=400.0)
        assert_allclose(rho, 1.0, rtol=1e-3)

    def test_zero_Vcrd_raises(self):
        with pytest.raises(ValueError):
            steel_bending_shear_reduction(V_Ed=100.0, V_c_Rd=0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(steel_bending_shear_reduction)
        assert ref is not None
        assert ref.article == "4.2.4.1.2.6"


# ── [4.2.33] — Presso/tenso-flessione nel piano dell'anima ──────────────────


class TestSteelNMResistanceY:
    """NTC18 §4.2.4.1.2.7, Formula [4.2.33]."""

    def test_basic(self):
        """M_N,y,Rd = M_pl,y,Rd * (1-n)/(1-0.5*a)."""
        # n=0.3, a=0.4, M_pl=500 kNm
        result = steel_NM_resistance_y(n=0.3, a=0.4, M_pl_y_Rd=500.0)
        expected = 500.0 * (1.0 - 0.3) / (1.0 - 0.5 * 0.4)
        assert_allclose(result, expected, rtol=1e-3)

    def test_no_axial(self):
        """n=0: M_N,y,Rd = M_pl,y,Rd."""
        result = steel_NM_resistance_y(n=0.0, a=0.4, M_pl_y_Rd=500.0)
        assert_allclose(result, 500.0, rtol=1e-3)

    def test_capped_at_Mpl(self):
        """Risultato limitato a M_pl,y,Rd."""
        # Per n piccolo e a grande il risultato potrebbe superare M_pl
        result = steel_NM_resistance_y(n=0.05, a=0.5, M_pl_y_Rd=500.0)
        assert result <= 500.0 + 1e-6  # ≤ M_pl,y,Rd

    def test_negative_n_raises(self):
        with pytest.raises(ValueError):
            steel_NM_resistance_y(n=-0.1, a=0.4, M_pl_y_Rd=500.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(steel_NM_resistance_y)
        assert ref is not None
        assert ref.article == "4.2.4.1.2.7"


# ── [4.2.34-4.2.35] — Presso/tenso-flessione nel piano delle ali ────────────


class TestSteelNMResistanceZ:
    """NTC18 §4.2.4.1.2.7, Formule [4.2.34-4.2.35]."""

    def test_n_le_a(self):
        """n <= a: M_N,z,Rd = M_pl,z,Rd."""
        result = steel_NM_resistance_z(n=0.3, a=0.4, M_pl_z_Rd=200.0)
        assert_allclose(result, 200.0, rtol=1e-3)

    def test_n_gt_a(self):
        """n > a: M_N,z,Rd = M_pl,z,Rd * [1 - ((n-a)/(1-a))^2]."""
        result = steel_NM_resistance_z(n=0.6, a=0.4, M_pl_z_Rd=200.0)
        expected = 200.0 * (1.0 - ((0.6 - 0.4) / (1.0 - 0.4)) ** 2)
        assert_allclose(result, expected, rtol=1e-3)

    def test_n_equals_a(self):
        """n = a: boundary, M_N,z,Rd = M_pl,z,Rd."""
        result = steel_NM_resistance_z(n=0.4, a=0.4, M_pl_z_Rd=200.0)
        assert_allclose(result, 200.0, rtol=1e-3)

    def test_ntc_ref(self):
        ref = get_ntc_ref(steel_NM_resistance_z)
        assert ref is not None
        assert ref.article == "4.2.4.1.2.7"


# ── [4.2.38-4.2.39] — Presso/tenso-flessione biassiale ──────────────────────


class TestSteelBiaxialCheck:
    """NTC18 §4.2.4.1.28, Formule [4.2.38-4.2.39]."""

    def test_n_ge_02_passes(self):
        """n >= 0.2: (My/MNy)^2 + (Mz/MNz)^(5n) <= 1."""
        # n=0.3: (100/400)^2 + (50/200)^(1.5) = 0.0625 + 0.3536 = 0.416
        passes, utilization = steel_biaxial_check(
            M_y_Ed=100.0, M_z_Ed=50.0,
            M_N_y_Rd=400.0, M_N_z_Rd=200.0, n=0.3,
        )
        assert passes is True
        assert utilization < 1.0

    def test_n_ge_02_fails(self):
        """n >= 0.2: rapporto > 1 => non passa."""
        passes, utilization = steel_biaxial_check(
            M_y_Ed=350.0, M_z_Ed=180.0,
            M_N_y_Rd=400.0, M_N_z_Rd=200.0, n=0.3,
        )
        assert passes is False
        assert utilization > 1.0

    def test_n_lt_02_linear(self):
        """n < 0.2: My/MNy + Mz/MNz <= 1 (interazione lineare)."""
        passes, utilization = steel_biaxial_check(
            M_y_Ed=100.0, M_z_Ed=50.0,
            M_N_y_Rd=400.0, M_N_z_Rd=200.0, n=0.1,
        )
        expected = 100.0 / 400.0 + 50.0 / 200.0  # 0.5
        assert passes is True
        assert_allclose(utilization, expected, rtol=1e-3)

    def test_n_lt_02_fails(self):
        """n < 0.2: interazione lineare > 1."""
        passes, utilization = steel_biaxial_check(
            M_y_Ed=300.0, M_z_Ed=150.0,
            M_N_y_Rd=400.0, M_N_z_Rd=200.0, n=0.1,
        )
        assert passes is False

    def test_ntc_ref(self):
        ref = get_ntc_ref(steel_biaxial_check)
        assert ref is not None
        assert ref.article == "4.2.4.1.28"


# ── Tab.4.2.VIII — Fattori di imperfezione ───────────────────────────────────


class TestSteelBucklingImperfection:
    """NTC18 §4.2.4.1.3.1, Tab. 4.2.VIII."""

    def test_curve_a0(self):
        assert_allclose(steel_buckling_imperfection("a0"), 0.13, rtol=1e-3)

    def test_curve_a(self):
        assert_allclose(steel_buckling_imperfection("a"), 0.21, rtol=1e-3)

    def test_curve_b(self):
        assert_allclose(steel_buckling_imperfection("b"), 0.34, rtol=1e-3)

    def test_curve_c(self):
        assert_allclose(steel_buckling_imperfection("c"), 0.49, rtol=1e-3)

    def test_curve_d(self):
        assert_allclose(steel_buckling_imperfection("d"), 0.76, rtol=1e-3)

    def test_invalid_curve_raises(self):
        with pytest.raises(ValueError, match="curve"):
            steel_buckling_imperfection("e")

    def test_ntc_ref(self):
        ref = get_ntc_ref(steel_buckling_imperfection)
        assert ref is not None
        assert ref.article == "4.2.4.1.3.1"


# ── [4.2.44] — Coefficiente di riduzione instabilita' ───────────────────────


class TestSteelBucklingReduction:
    """NTC18 §4.2.4.1.3.1, Formula [4.2.44]."""

    def test_low_lambda_no_buckling(self):
        """lambda_bar <= 0.2: chi = 1.0 (instabilita' trascurabile)."""
        chi = steel_buckling_reduction(lambda_bar=0.15, alpha=0.21)
        assert_allclose(chi, 1.0, rtol=1e-3)

    def test_lambda_1_curve_a(self):
        """lambda_bar = 1.0, curva a (alpha=0.21)."""
        alpha = 0.21
        lam = 1.0
        Phi = 0.5 * (1 + alpha * (lam - 0.2) + lam ** 2)
        expected = 1.0 / (Phi + math.sqrt(Phi ** 2 - lam ** 2))
        chi = steel_buckling_reduction(lambda_bar=1.0, alpha=0.21)
        assert_allclose(chi, expected, rtol=1e-3)

    def test_lambda_2_curve_c(self):
        """lambda_bar = 2.0, curva c (alpha=0.49): chi << 1."""
        chi = steel_buckling_reduction(lambda_bar=2.0, alpha=0.49)
        assert chi < 0.3

    def test_chi_le_1(self):
        """chi non supera mai 1.0."""
        chi = steel_buckling_reduction(lambda_bar=0.1, alpha=0.13)
        assert chi <= 1.0 + 1e-10

    def test_ntc_ref(self):
        ref = get_ntc_ref(steel_buckling_reduction)
        assert ref is not None
        assert ref.article == "4.2.4.1.3.1"


# ── [4.2.42] — Resistenza instabilita' aste compresse ───────────────────────


class TestSteelBucklingResistance:
    """NTC18 §4.2.4.1.3.1, Formula [4.2.42]."""

    def test_basic(self):
        """N_b,Rd = chi * A * f_yk / gamma_M1."""
        result = steel_buckling_resistance(
            chi=0.8, A=5000.0, f_yk=355.0, gamma_M1=1.05
        )
        assert_allclose(result, 0.8 * 5000.0 * 355.0 / 1.05, rtol=1e-3)

    def test_chi_one(self):
        """chi = 1 (nessuna riduzione)."""
        result = steel_buckling_resistance(
            chi=1.0, A=3000.0, f_yk=235.0, gamma_M1=1.05
        )
        expected = 3000.0 * 235.0 / 1.05
        assert_allclose(result, expected, rtol=1e-3)

    def test_ntc_ref(self):
        ref = get_ntc_ref(steel_buckling_resistance)
        assert ref is not None
        assert ref.article == "4.2.4.1.3.1"


# ── [4.2.50] — Coefficiente riduzione instabilita' flesso-torsionale ────────


class TestSteelLTBucklingReduction:
    """NTC18 §4.2.4.1.3.2, Formula [4.2.50]."""

    def test_low_lambda(self):
        """lambda_LT_bar <= 0.2: chi_LT = 1.0."""
        chi_LT = steel_lt_buckling_reduction(lambda_LT_bar=0.15, alpha_LT=0.34)
        assert_allclose(chi_LT, 1.0, rtol=1e-3)

    def test_lambda_1_curve_b(self):
        """lambda_LT_bar = 1.0, curva b (alpha=0.34)."""
        alpha = 0.34
        lam = 1.0
        Phi = 0.5 * (1 + alpha * (lam - 0.2) + lam ** 2)
        expected = 1.0 / (Phi + math.sqrt(Phi ** 2 - lam ** 2))
        chi_LT = steel_lt_buckling_reduction(lambda_LT_bar=1.0, alpha_LT=0.34)
        assert_allclose(chi_LT, expected, rtol=1e-3)

    def test_high_lambda(self):
        """lambda_LT elevato: chi_LT molto basso."""
        chi_LT = steel_lt_buckling_reduction(lambda_LT_bar=2.5, alpha_LT=0.49)
        assert chi_LT < 0.2

    def test_ntc_ref(self):
        ref = get_ntc_ref(steel_lt_buckling_reduction)
        assert ref is not None
        assert ref.article == "4.2.4.1.3.2"


# ── [4.2.49] — Resistenza instabilita' flesso-torsionale ────────────────────


class TestSteelLTBucklingResistance:
    """NTC18 §4.2.4.1.3.2, Formula [4.2.49]."""

    def test_basic(self):
        """M_b,Rd = chi_LT * W_y * f_yk / gamma_M1."""
        result = steel_lt_buckling_resistance(
            chi_LT=0.7, W_y=500e3, f_yk=355.0, gamma_M1=1.05
        )
        assert_allclose(result, 0.7 * 500e3 * 355.0 / 1.05, rtol=1e-3)

    def test_chi_one(self):
        """chi_LT = 1: nessuna riduzione."""
        result = steel_lt_buckling_resistance(
            chi_LT=1.0, W_y=400e3, f_yk=275.0, gamma_M1=1.05
        )
        assert_allclose(result, 400e3 * 275.0 / 1.05, rtol=1e-3)

    def test_ntc_ref(self):
        ref = get_ntc_ref(steel_lt_buckling_resistance)
        assert ref is not None
        assert ref.article == "4.2.4.1.3.2"


# ── [4.2.63-4.2.66] — Resistenza a taglio bulloni ───────────────────────────


class TestBoltShearResistance:
    """NTC18 §4.2.8.1.1, Formule [4.2.63-4.2.66]."""

    def test_class_88(self):
        """Classe 8.8: F_v,Rd = 0.6 * f_ub * A_s / gamma_M2."""
        result = bolt_shear_resistance(
            f_ub=800.0, A_s=245.0, bolt_class="8.8", gamma_M2=1.25
        )
        assert_allclose(result, 0.6 * 800.0 * 245.0 / 1.25, rtol=1e-3)

    def test_class_109(self):
        """Classe 10.9: F_v,Rd = 0.5 * f_ub * A_s / gamma_M2."""
        result = bolt_shear_resistance(
            f_ub=1000.0, A_s=245.0, bolt_class="10.9", gamma_M2=1.25
        )
        assert_allclose(result, 0.5 * 1000.0 * 245.0 / 1.25, rtol=1e-3)

    def test_class_46(self):
        """Classe 4.6: F_v,Rd = 0.6 * f_ub * A_s / gamma_M2."""
        result = bolt_shear_resistance(
            f_ub=400.0, A_s=157.0, bolt_class="4.6", gamma_M2=1.25
        )
        assert_allclose(result, 0.6 * 400.0 * 157.0 / 1.25, rtol=1e-3)

    def test_invalid_class_raises(self):
        with pytest.raises(ValueError, match="bolt_class"):
            bolt_shear_resistance(f_ub=800.0, A_s=245.0, bolt_class="12.9", gamma_M2=1.25)

    def test_ntc_ref(self):
        ref = get_ntc_ref(bolt_shear_resistance)
        assert ref is not None
        assert ref.article == "4.2.8.1.1"


# ── [4.2.68] — Resistenza a trazione bulloni ────────────────────────────────


class TestBoltTensionResistance:
    """NTC18 §4.2.8.1.1, Formula [4.2.68]."""

    def test_basic(self):
        """F_t,Rd = 0.9 * f_ub * A_s / gamma_M2."""
        result = bolt_tension_resistance(
            f_ub=800.0, A_s=245.0, gamma_M2=1.25
        )
        assert_allclose(result, 0.9 * 800.0 * 245.0 / 1.25, rtol=1e-3)

    def test_class_109(self):
        """Bullone 10.9, M20 (A_s=245)."""
        result = bolt_tension_resistance(
            f_ub=1000.0, A_s=245.0, gamma_M2=1.25
        )
        assert_allclose(result, 0.9 * 1000.0 * 245.0 / 1.25, rtol=1e-3)

    def test_ntc_ref(self):
        ref = get_ntc_ref(bolt_tension_resistance)
        assert ref is not None
        assert ref.article == "4.2.8.1.1"


# ── [4.2.71] — Interazione taglio + trazione bulloni ────────────────────────


class TestBoltShearTensionInteraction:
    """NTC18 §4.2.8.1.1, Formula [4.2.71]."""

    def test_passes(self):
        """F_v/F_vRd + F_t/F_tRd = 0.4 + 0.3 = 0.7 <= 1: passa."""
        passes, util = bolt_shear_tension_interaction(
            F_v_Ed=40.0, F_t_Ed=30.0, F_v_Rd=100.0, F_t_Rd=100.0
        )
        assert passes is True
        assert_allclose(util, 0.7, rtol=1e-3)

    def test_fails(self):
        """F_v/F_vRd + F_t/F_tRd > 1: non passa."""
        passes, util = bolt_shear_tension_interaction(
            F_v_Ed=60.0, F_t_Ed=50.0, F_v_Rd=100.0, F_t_Rd=100.0
        )
        assert passes is False
        assert util > 1.0

    def test_pure_shear(self):
        """Solo taglio: F_t_Ed = 0."""
        passes, util = bolt_shear_tension_interaction(
            F_v_Ed=80.0, F_t_Ed=0.0, F_v_Rd=100.0, F_t_Rd=100.0
        )
        assert passes is True
        assert_allclose(util, 0.8, rtol=1e-3)

    def test_ntc_ref(self):
        ref = get_ntc_ref(bolt_shear_tension_interaction)
        assert ref is not None
        assert ref.article == "4.2.8.1.1"


# ── [4.2.67] — Resistenza a rifollamento ────────────────────────────────────


class TestBoltBearingResistance:
    """NTC18 §4.2.8.1.1, Formula [4.2.67]."""

    def test_edge_bolt(self):
        """Bullone di bordo: esempio dal quaderno FPA (IPE430, M20, piastra 12mm).

        k1 = min(2.8*30/22 - 1.7, 2.5) = 2.12
        alpha_b = min(40/(3*22), 800/430, 1.0) = 0.61
        F_b,Rd = 2.12 * 0.61 * 430 * 20 * 12 / 1.25 = 107 kN
        """
        k1 = min(2.8 * 30 / 22 - 1.7, 2.5)
        alpha_b = min(40 / (3 * 22), 800 / 430, 1.0)
        result = bolt_bearing_resistance(
            k1=k1, alpha_b=alpha_b, f_u=430.0, d=20.0, t=12.0, gamma_M2=1.25
        )
        assert_allclose(result, k1 * alpha_b * 430.0 * 20.0 * 12.0 / 1.25, rtol=1e-3)

    def test_inner_bolt(self):
        """Bullone interno: esempio dal quaderno FPA (IPE430, M20, piastra 12mm).

        k1 = min(2.8*30/22 - 1.7, 2.5) = 2.12
        alpha_b = min(70/(3*22) - 0.25, 800/430, 1.0) = 0.81
        F_b,Rd = 2.12 * 0.81 * 430 * 20 * 12 / 1.25 = 142 kN
        """
        k1 = min(2.8 * 30 / 22 - 1.7, 2.5)
        alpha_b = min(70 / (3 * 22) - 0.25, 800 / 430, 1.0)
        result = bolt_bearing_resistance(
            k1=k1, alpha_b=alpha_b, f_u=430.0, d=20.0, t=12.0, gamma_M2=1.25
        )
        assert_allclose(result, k1 * alpha_b * 430.0 * 20.0 * 12.0 / 1.25, rtol=1e-3)

    def test_invalid_k1_raises(self):
        with pytest.raises(ValueError, match="k1"):
            bolt_bearing_resistance(k1=0.0, alpha_b=0.6, f_u=430.0, d=20.0, t=12.0, gamma_M2=1.25)

    def test_invalid_alpha_b_raises(self):
        with pytest.raises(ValueError, match="alpha_b"):
            bolt_bearing_resistance(k1=2.5, alpha_b=0.0, f_u=430.0, d=20.0, t=12.0, gamma_M2=1.25)

    def test_ntc_ref(self):
        ref = get_ntc_ref(bolt_bearing_resistance)
        assert ref is not None
        assert ref.article == "4.2.8.1.1"


# ── [4.2.70] — Resistenza a punzonamento ────────────────────────────────────


class TestBoltPunchingResistance:
    """NTC18 §4.2.8.1.1, Formula [4.2.70]."""

    def test_basic(self):
        """F_p,Rd = 0.6 * pi * d_m * t_p * f_u / gamma_M2."""
        result = bolt_punching_resistance(
            d_m=32.0, t_p=12.0, f_u=430.0, gamma_M2=1.25
        )
        expected = 0.6 * math.pi * 32.0 * 12.0 * 430.0 / 1.25
        assert_allclose(result, expected, rtol=1e-3)

    def test_invalid_dm_raises(self):
        with pytest.raises(ValueError, match="d_m"):
            bolt_punching_resistance(d_m=0.0, t_p=12.0, f_u=430.0, gamma_M2=1.25)

    def test_ntc_ref(self):
        ref = get_ntc_ref(bolt_punching_resistance)
        assert ref is not None
        assert ref.article == "4.2.8.1.1"


# ── [4.2.72] — Resistenza allo scorrimento (attrito) ────────────────────────


class TestBoltFrictionResistance:
    """NTC18 §4.2.8.1.1, Formula [4.2.72]."""

    def test_basic(self):
        """M20 cl.8.8: F_p,Cd = 0.7*800*245 = 137200 N, mu=0.5, n=1."""
        F_p_Cd = 0.7 * 800.0 * 245.0
        result = bolt_friction_resistance(
            n=1, mu=0.5, F_p_Cd=F_p_Cd, gamma_M3=1.25
        )
        expected = 1 * 0.5 * F_p_Cd / 1.25
        assert_allclose(result, expected, rtol=1e-3)

    def test_two_surfaces(self):
        """Due superfici di attrito: n=2."""
        F_p_Cd = 0.7 * 800.0 * 245.0
        result = bolt_friction_resistance(
            n=2, mu=0.4, F_p_Cd=F_p_Cd, gamma_M3=1.25
        )
        expected = 2 * 0.4 * F_p_Cd / 1.25
        assert_allclose(result, expected, rtol=1e-3)

    def test_invalid_mu_raises(self):
        with pytest.raises(ValueError, match="mu"):
            bolt_friction_resistance(n=1, mu=0.0, F_p_Cd=100000.0, gamma_M3=1.25)

    def test_ntc_ref(self):
        ref = get_ntc_ref(bolt_friction_resistance)
        assert ref is not None
        assert ref.article == "4.2.8.1.1"


# ── [4.2.73] — Resistenza allo scorrimento con trazione ─────────────────────


class TestBoltFrictionTensionResistance:
    """NTC18 §4.2.8.1.1, Formula [4.2.73]."""

    def test_basic(self):
        """F_s,Rd = n * mu * (F_p,Cd - 0.8 * F_t,Ed) / gamma_M3."""
        F_p_Cd = 0.7 * 800.0 * 245.0
        F_t_Ed = 50000.0
        result = bolt_friction_tension_resistance(
            n=1, mu=0.5, F_p_Cd=F_p_Cd, F_t_Ed=F_t_Ed, gamma_M3=1.25
        )
        expected = 1 * 0.5 * (F_p_Cd - 0.8 * F_t_Ed) / 1.25
        assert_allclose(result, expected, rtol=1e-3)

    def test_zero_tension(self):
        """Senza trazione: equivale a [4.2.72]."""
        F_p_Cd = 0.7 * 800.0 * 245.0
        result = bolt_friction_tension_resistance(
            n=1, mu=0.5, F_p_Cd=F_p_Cd, F_t_Ed=0.0, gamma_M3=1.25
        )
        expected = 1 * 0.5 * F_p_Cd / 1.25
        assert_allclose(result, expected, rtol=1e-3)

    def test_invalid_tension_raises(self):
        with pytest.raises(ValueError, match="F_t_Ed"):
            bolt_friction_tension_resistance(
                n=1, mu=0.5, F_p_Cd=100000.0, F_t_Ed=-1.0, gamma_M3=1.25
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(bolt_friction_tension_resistance)
        assert ref is not None
        assert ref.article == "4.2.8.1.1"


# ── [4.2.81-4.2.83] — Resistenza saldature a cordoni d'angolo ───────────────


class TestWeldFilletResistance:
    """NTC18 §4.2.8.2.4, Formule [4.2.81-4.2.83]."""

    def test_s235(self):
        """S235: beta_w=0.80, F_w,Rd = a * f_tk / (sqrt(3) * beta_w * gamma_M2)."""
        result = weld_fillet_resistance(
            a=5.0, f_tk=360.0, beta_w=0.80, gamma_M2=1.25
        )
        expected = 5.0 * 360.0 / (math.sqrt(3) * 0.80 * 1.25)
        assert_allclose(result, expected, rtol=1e-3)

    def test_s355(self):
        """S355: beta_w=0.90."""
        result = weld_fillet_resistance(
            a=6.0, f_tk=510.0, beta_w=0.90, gamma_M2=1.25
        )
        expected = 6.0 * 510.0 / (math.sqrt(3) * 0.90 * 1.25)
        assert_allclose(result, expected, rtol=1e-3)

    def test_zero_throat_raises(self):
        with pytest.raises(ValueError):
            weld_fillet_resistance(a=0.0, f_tk=360.0, beta_w=0.80, gamma_M2=1.25)

    def test_ntc_ref(self):
        ref = get_ntc_ref(weld_fillet_resistance)
        assert ref is not None
        assert ref.article == "4.2.8.2.4"


# ── [4.2.18-4.2.23] — Area resistente a taglio ───────────────────────────────


class TestSteelShearArea:
    """NTC18 §4.2.4.1.2.4, Formule [4.2.18]–[4.2.23]."""

    def test_I_H_rolled(self):
        # A=8000, b=200, t_f=12, t_w=8, r=15
        # A_v = 8000 - 2*200*12 + (8 + 2*15)*12 = 8000 - 4800 + 456 = 3656
        result = steel_shear_area("I_H_rolled", 8000.0, b=200.0, t_f=12.0, t_w=8.0, r=15.0)
        expected = 8000.0 - 2.0*200.0*12.0 + (8.0 + 2.0*15.0)*12.0
        assert_allclose(result, expected, rtol=1e-6)

    def test_I_H_weld(self):
        # A=7000, b=180, t_f=10, t_w=6, r=8
        # A_v = 7000 - 2*180*10 + (6 + 8)*10 = 7000 - 3600 + 140 = 3540
        result = steel_shear_area("I_H_weld", 7000.0, b=180.0, t_f=10.0, t_w=6.0, r=8.0)
        expected = 7000.0 - 2.0*180.0*10.0 + (6.0 + 8.0)*10.0
        assert_allclose(result, expected, rtol=1e-6)

    def test_box(self):
        # A=12000, hw_tw_sum = 2*300*8 = 4800
        result = steel_shear_area("box", 12000.0, hw_tw_sum=4800.0)
        assert_allclose(result, 12000.0 - 4800.0, rtol=1e-6)

    def test_T(self):
        # A=5000, b=150, t_f=10
        # A_v = 0.9*(5000 - 150*10) = 0.9*3500 = 3150
        result = steel_shear_area("T", 5000.0, b=150.0, t_f=10.0)
        assert_allclose(result, 0.9*(5000.0 - 150.0*10.0), rtol=1e-6)

    def test_rectangular_height(self):
        # A=b*h=200*400=80000, load parallel to height
        # A_v = A*h/(b+h) = 80000*400/600 = 53333.3
        result = steel_shear_area("rectangular", 80000.0, b=200.0, h=400.0, load_direction="height")
        assert_allclose(result, 80000.0*400.0/600.0, rtol=1e-6)

    def test_rectangular_width(self):
        result = steel_shear_area("rectangular", 80000.0, b=200.0, h=400.0, load_direction="width")
        assert_allclose(result, 80000.0*200.0/600.0, rtol=1e-6)

    def test_circular(self):
        # A=pi*(50^2)/4 = 1963.5, A_v = 2*A/pi = 2*1963.5/pi = 1250
        import math as _math
        A = _math.pi * 50.0**2 / 4.0
        result = steel_shear_area("circular", A)
        assert_allclose(result, 2.0*A/_math.pi, rtol=1e-6)

    def test_missing_params_raises(self):
        with pytest.raises(ValueError):
            steel_shear_area("I_H_rolled", 8000.0)

    def test_invalid_section_raises(self):
        with pytest.raises(ValueError):
            steel_shear_area("unknown", 8000.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(steel_shear_area)
        assert ref is not None
        assert ref.article == "4.2.4.1.2.4"


# ── [4.2.4] — Von Mises ──────────────────────────────────────────────────────


class TestSteelVonMisesCheck:
    """NTC18 §4.2.4.1.2, Formula [4.2.4]."""

    def test_safe_uniaxial(self):
        # Solo sigma_x, nessun tau → sigma_eq = sigma_x
        f_yk = 355.0
        ok, ratio = steel_von_mises_check(200.0, 0.0, 0.0, f_yk, 1.05)
        assert ok is True
        assert_allclose(ratio, 200.0 / (355.0/1.05), rtol=1e-6)

    def test_safe_combined(self):
        # sigma_x=100, sigma_y=50, tau=80, f_yk=355, γ=1.05
        import math as _math
        sigma_eq = _math.sqrt(100**2 + 50**2 - 100*50 + 3*80**2)
        f_limit = 355.0/1.05
        ok, ratio = steel_von_mises_check(100.0, 50.0, 80.0, 355.0, 1.05)
        assert_allclose(ratio, sigma_eq/f_limit, rtol=1e-6)
        assert ok == (sigma_eq <= f_limit)

    def test_unsafe(self):
        # σ_x = f_yk/γ → exactly at limit but sigma_y and tau push it over
        ok, ratio = steel_von_mises_check(300.0, 300.0, 200.0, 355.0, 1.05)
        assert ok is False
        assert ratio > 1.0

    def test_pure_shear_limit(self):
        # Per taglio puro: sigma_eq = sqrt(3)*tau = f_yk/γ
        import math as _math
        f_yk = 355.0
        gamma = 1.05
        tau = f_yk / (gamma * _math.sqrt(3))
        ok, ratio = steel_von_mises_check(0.0, 0.0, tau, f_yk, gamma)
        assert ok is True
        assert_allclose(ratio, 1.0, rtol=1e-6)

    def test_zero_fyk_raises(self):
        with pytest.raises(ValueError):
            steel_von_mises_check(100.0, 0.0, 0.0, 0.0, 1.05)

    def test_ntc_ref(self):
        ref = get_ntc_ref(steel_von_mises_check)
        assert ref is not None
        assert ref.article == "4.2.4.1.2"
        assert ref.formula == "4.2.4"


# ── [4.2.75] — Resistenza a taglio perno ─────────────────────────────────────


class TestPinShearResistance:
    """NTC18 §4.2.8.1.2, Formula [4.2.75]."""

    def test_basic(self):
        # f_upk=500, A=pi*(20^2)/4=314.2, gamma_M2=1.25
        import math as _math
        A = _math.pi * 20.0**2 / 4.0
        result = pin_shear_resistance(500.0, A, 1.25)
        assert_allclose(result, 0.6 * 500.0 * A / 1.25, rtol=1e-6)

    def test_zero_fupk_raises(self):
        with pytest.raises(ValueError):
            pin_shear_resistance(0.0, 314.0, 1.25)

    def test_ntc_ref(self):
        ref = get_ntc_ref(pin_shear_resistance)
        assert ref is not None
        assert ref.article == "4.2.8.1.2"
        assert ref.formula == "4.2.75"


# ── [4.2.76] — Resistenza a rifollamento perno ───────────────────────────────


class TestPinBearingResistance:
    """NTC18 §4.2.8.1.2, Formula [4.2.76]."""

    def test_basic(self):
        # t=20, d=30, f_y=355, gamma_M3=1.25
        result = pin_bearing_resistance(20.0, 30.0, 355.0, 1.25)
        assert_allclose(result, 1.5 * 20.0 * 30.0 * 355.0 / 1.25, rtol=1e-6)

    def test_zero_d_raises(self):
        with pytest.raises(ValueError):
            pin_bearing_resistance(20.0, 0.0, 355.0, 1.25)

    def test_ntc_ref(self):
        ref = get_ntc_ref(pin_bearing_resistance)
        assert ref is not None
        assert ref.article == "4.2.8.1.2"
        assert ref.formula == "4.2.76"


# ── [4.2.13] — Flessione sezione classe 3 ────────────────────────────────────


class TestSteelBendingResistanceClass3:
    """NTC18 §4.2.4.1.2.3, Formula [4.2.13]."""

    def test_basic(self):
        """M_el,Rd = W_el_min * f_yk / gamma_M0."""
        result = steel_bending_resistance_class3(100e3, 355.0)
        assert_allclose(result, 100e3 * 355.0 / 1.0, rtol=1e-6)

    def test_with_gamma(self):
        """Con gamma_M0 = 1.05."""
        result = steel_bending_resistance_class3(200e3, 275.0, gamma_M0=1.05)
        assert_allclose(result, 200e3 * 275.0 / 1.05, rtol=1e-6)

    def test_zero_W_raises(self):
        with pytest.raises(ValueError, match="W_el_min"):
            steel_bending_resistance_class3(0.0, 355.0)

    def test_zero_fyk_raises(self):
        with pytest.raises(ValueError, match="f_yk"):
            steel_bending_resistance_class3(100e3, 0.0)

    def test_zero_gamma_raises(self):
        with pytest.raises(ValueError, match="gamma_M0"):
            steel_bending_resistance_class3(100e3, 355.0, gamma_M0=0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(steel_bending_resistance_class3)
        assert ref is not None
        assert ref.formula == "4.2.13"
        assert ref.article == "4.2.4.1.2.3"


# ── [4.2.14] — Flessione sezione classe 4 ────────────────────────────────────


class TestSteelBendingResistanceClass4:
    """NTC18 §4.2.4.1.2.3, Formula [4.2.14]."""

    def test_basic(self):
        """M_eff,Rd = W_eff_min * f_yk / gamma_M0."""
        result = steel_bending_resistance_class4(80e3, 355.0)
        assert_allclose(result, 80e3 * 355.0 / 1.0, rtol=1e-6)

    def test_with_gamma(self):
        result = steel_bending_resistance_class4(150e3, 235.0, gamma_M0=1.05)
        assert_allclose(result, 150e3 * 235.0 / 1.05, rtol=1e-6)

    def test_zero_W_raises(self):
        with pytest.raises(ValueError, match="W_eff_min"):
            steel_bending_resistance_class4(0.0, 355.0)

    def test_zero_fyk_raises(self):
        with pytest.raises(ValueError, match="f_yk"):
            steel_bending_resistance_class4(80e3, 0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(steel_bending_resistance_class4)
        assert ref is not None
        assert ref.formula == "4.2.14"
        assert ref.article == "4.2.4.1.2.3"


# ── §4.2.4.1.2.5 — Torsione ──────────────────────────────────────────────────


class TestSteelTorsionResistance:
    """NTC18 §4.2.4.1.2.5 — Resistenza a torsione."""

    def test_basic(self):
        """T_Rd = W_t * f_yk / (sqrt(3) * gamma_M0)."""
        W_t, f_yk = 50e3, 355.0
        result = steel_torsion_resistance(W_t, f_yk)
        assert_allclose(result, W_t * f_yk / math.sqrt(3), rtol=1e-6)

    def test_with_gamma(self):
        W_t, f_yk, gM0 = 30e3, 275.0, 1.05
        result = steel_torsion_resistance(W_t, f_yk, gamma_M0=gM0)
        assert_allclose(result, W_t * f_yk / (math.sqrt(3) * gM0), rtol=1e-6)

    def test_zero_Wt_raises(self):
        with pytest.raises(ValueError, match="W_t"):
            steel_torsion_resistance(0.0, 355.0)

    def test_zero_fyk_raises(self):
        with pytest.raises(ValueError, match="f_yk"):
            steel_torsion_resistance(50e3, 0.0)

    def test_zero_gamma_raises(self):
        with pytest.raises(ValueError, match="gamma_M0"):
            steel_torsion_resistance(50e3, 355.0, gamma_M0=0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(steel_torsion_resistance)
        assert ref is not None
        assert ref.article == "4.2.4.1.2.5"


class TestSteelTorsionCheck:
    """NTC18 §4.2.4.1.2.5, Formula [4.2.28]."""

    def test_pass(self):
        ok, ratio = steel_torsion_check(T_Ed=80.0, T_Rd=100.0)
        assert ok is True
        assert_allclose(ratio, 0.8, rtol=1e-6)

    def test_fail(self):
        ok, ratio = steel_torsion_check(T_Ed=110.0, T_Rd=100.0)
        assert ok is False
        assert_allclose(ratio, 1.1, rtol=1e-6)

    def test_equal(self):
        ok, ratio = steel_torsion_check(T_Ed=100.0, T_Rd=100.0)
        assert ok is True
        assert_allclose(ratio, 1.0, rtol=1e-6)

    def test_zero_TRd_raises(self):
        with pytest.raises(ValueError, match="T_Rd"):
            steel_torsion_check(50.0, 0.0)

    def test_negative_TEd_raises(self):
        with pytest.raises(ValueError, match="T_Ed"):
            steel_torsion_check(-10.0, 100.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(steel_torsion_check)
        assert ref is not None
        assert ref.formula == "4.2.28"


# ── [4.2.45/4.2.46] — Snellezza adimensionale ────────────────────────────────


class TestSteelRelativeSlenderness:
    """NTC18 §4.2.4.1.3.1, Formule [4.2.45] e [4.2.46]."""

    def test_class1(self):
        """Classe 1: lambda_bar = sqrt(A * f_yk / N_cr)."""
        A, f_yk, N_cr = 5000.0, 355.0, 1e6
        result = steel_relative_slenderness(A, f_yk, N_cr, section_class=1)
        assert_allclose(result, math.sqrt(A * f_yk / N_cr), rtol=1e-6)

    def test_class3(self):
        """Classe 3 usa stessa formula della classe 1."""
        A, f_yk, N_cr = 4000.0, 275.0, 8e5
        result = steel_relative_slenderness(A, f_yk, N_cr, section_class=3)
        assert_allclose(result, math.sqrt(A * f_yk / N_cr), rtol=1e-6)

    def test_class4(self):
        """Classe 4: lambda_bar = sqrt(A_eff * f_yk / N_cr)."""
        A_eff, f_yk, N_cr = 3500.0, 355.0, 9e5
        result = steel_relative_slenderness(A_eff, f_yk, N_cr, section_class=4)
        assert_allclose(result, math.sqrt(A_eff * f_yk / N_cr), rtol=1e-6)

    def test_invalid_class_raises(self):
        with pytest.raises(ValueError, match="section_class"):
            steel_relative_slenderness(5000.0, 355.0, 1e6, section_class=5)

    def test_zero_area_raises(self):
        with pytest.raises(ValueError, match="A_or_A_eff"):
            steel_relative_slenderness(0.0, 355.0, 1e6)

    def test_zero_Ncr_raises(self):
        with pytest.raises(ValueError, match="N_cr"):
            steel_relative_slenderness(5000.0, 355.0, 0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(steel_relative_slenderness)
        assert ref is not None
        assert ref.article == "4.2.4.1.3.1"
        assert ref.formula == "4.2.45"


# ── [4.2.43] — Resistenza instabilita' sezione classe 4 ─────────────────────


class TestSteelBucklingResistanceClass4:
    """NTC18 §4.2.4.1.3.1, Formula [4.2.43]."""

    def test_basic(self):
        """N_b,Rd = chi * A_eff * f_yk / gamma_M1."""
        chi, A_eff, f_yk, gM1 = 0.75, 4000.0, 355.0, 1.05
        result = steel_buckling_resistance_class4(chi, A_eff, f_yk, gM1)
        assert_allclose(result, chi * A_eff * f_yk / gM1, rtol=1e-6)

    def test_chi_one(self):
        result = steel_buckling_resistance_class4(1.0, 3000.0, 235.0)
        assert_allclose(result, 3000.0 * 235.0, rtol=1e-6)

    def test_chi_zero_raises(self):
        with pytest.raises(ValueError, match="chi"):
            steel_buckling_resistance_class4(0.0, 4000.0, 355.0)

    def test_chi_over_one_raises(self):
        with pytest.raises(ValueError, match="chi"):
            steel_buckling_resistance_class4(1.1, 4000.0, 355.0)

    def test_zero_Aeff_raises(self):
        with pytest.raises(ValueError, match="A_eff"):
            steel_buckling_resistance_class4(0.8, 0.0, 355.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(steel_buckling_resistance_class4)
        assert ref is not None
        assert ref.formula == "4.2.43"
        assert ref.article == "4.2.4.1.3.1"


# ── [4.2.81] — Verifica combinata saldatura ───────────────────────────────────


class TestWeldCombinedStressCheck:
    """NTC18 §4.2.8.2.4, Formula [4.2.81]."""

    def test_pass(self):
        """Stato tensionale all'interno del limite."""
        # f_limit = 510 / (0.9 * 1.25) = 453.33
        # sigma_eq = sqrt(100^2 + 3*(80^2 + 60^2)) = sqrt(10000+3*10000) = sqrt(40000) ~ 200
        sigma_eq = math.sqrt(100.0**2 + 3.0 * (80.0**2 + 60.0**2))
        f_limit = 510.0 / (0.9 * 1.25)
        ok, ratio = weld_combined_stress_check(100.0, 80.0, 60.0, 510.0, 0.9)
        assert ok is True
        assert_allclose(ratio, sigma_eq / f_limit, rtol=1e-6)

    def test_fail(self):
        """Stato tensionale oltre il limite."""
        ok, ratio = weld_combined_stress_check(300.0, 200.0, 150.0, 360.0, 0.8)
        assert ok is False
        assert ratio > 1.0

    def test_zero_stresses(self):
        """Con tutti zero, sigma_eq = 0 -> ratio = 0, verifica OK."""
        ok, ratio = weld_combined_stress_check(0.0, 0.0, 0.0, 360.0, 0.8)
        assert ok is True
        assert_allclose(ratio, 0.0, atol=1e-10)

    def test_formula_components(self):
        """Verifica formula: sigma_perp=0, tau_par=tau -> sigma_eq = sqrt(3)*tau."""
        tau = 100.0
        f_u, beta_w, gM2 = 510.0, 0.9, 1.25
        ok, ratio = weld_combined_stress_check(0.0, 0.0, tau, f_u, beta_w, gM2)
        expected_sigma_eq = math.sqrt(3.0) * tau
        expected_ratio = expected_sigma_eq / (f_u / (beta_w * gM2))
        assert_allclose(ratio, expected_ratio, rtol=1e-6)

    def test_zero_fu_raises(self):
        with pytest.raises(ValueError, match="f_u"):
            weld_combined_stress_check(100.0, 50.0, 50.0, 0.0, 0.9)

    def test_zero_beta_raises(self):
        with pytest.raises(ValueError, match="beta_w"):
            weld_combined_stress_check(100.0, 50.0, 50.0, 510.0, 0.0)

    def test_zero_gamma_raises(self):
        with pytest.raises(ValueError, match="gamma_M2"):
            weld_combined_stress_check(100.0, 50.0, 50.0, 510.0, 0.9, gamma_M2=0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(weld_combined_stress_check)
        assert ref is not None
        assert ref.formula == "4.2.81"
        assert ref.article == "4.2.8.2.4"
