"""Test per seismic_foundations — NTC18 §7.10–§7.11."""

import math

import pytest
from numpy.testing import assert_allclose

from pyntc.checks.seismic_foundations import (
    seismic_anchor_free_length,
    seismic_isolation_base_shear,
    seismic_isolation_displacement,
    seismic_isolation_torsion_amplification,
    seismic_isolation_torsional_radius,
    seismic_shallow_foundation_gamma_R,
    seismic_sheet_pile_acceleration,
    seismic_sheet_pile_displacement_limit,
    seismic_sheet_pile_site_acceleration,
    seismic_wall_coeff_horizontal,
    seismic_wall_coeff_vertical,
    seismic_wall_site_acceleration,
)
from pyntc.core.reference import get_ntc_ref


# ── §7.11.6.2.1 [7.11.6] — Coefficiente sismico orizzontale muri ────────────


class TestSeismicWallCoeffHorizontal:
    """NTC18 §7.11.6.2.1, Formula [7.11.6]."""

    def test_basic(self):
        """k_h = beta_m * a_max / g = 0.38 * 2.0 / 9.81."""
        result = seismic_wall_coeff_horizontal(a_max=2.0, beta_m=0.38)
        assert_allclose(result, 0.38 * 2.0 / 9.81, rtol=1e-5)

    def test_edge_case_zero_acceleration(self):
        """a_max = 0 -> k_h = 0."""
        result = seismic_wall_coeff_horizontal(a_max=0.0, beta_m=0.38)
        assert_allclose(result, 0.0, atol=1e-12)

    def test_fixed_wall_beta_unity(self):
        """Muro non libero di spostarsi: beta_m = 1.0."""
        result = seismic_wall_coeff_horizontal(a_max=1.5, beta_m=1.0)
        assert_allclose(result, 1.5 / 9.81, rtol=1e-5)

    def test_sld_beta(self):
        """SLD: beta_m = 0.47, a_max = 3.0 m/s^2."""
        result = seismic_wall_coeff_horizontal(a_max=3.0, beta_m=0.47)
        assert_allclose(result, 0.47 * 3.0 / 9.81, rtol=1e-5)

    def test_negative_a_max_raises(self):
        with pytest.raises(ValueError):
            seismic_wall_coeff_horizontal(a_max=-0.1, beta_m=0.38)

    def test_zero_beta_raises(self):
        with pytest.raises(ValueError):
            seismic_wall_coeff_horizontal(a_max=2.0, beta_m=0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_wall_coeff_horizontal)
        assert ref is not None
        assert ref.article == "7.11.6.2.1"
        assert ref.formula == "7.11.6"


# ── §7.11.6.2.1 [7.11.7] — Coefficiente sismico verticale muri ──────────────


class TestSeismicWallCoeffVertical:
    """NTC18 §7.11.6.2.1, Formula [7.11.7]."""

    def test_basic(self):
        """k_v = 0.5 * k_h = 0.5 * 0.1 = 0.05."""
        result = seismic_wall_coeff_vertical(k_h=0.1)
        assert_allclose(result, 0.05, rtol=1e-10)

    def test_edge_case_zero(self):
        """k_h = 0 -> k_v = 0."""
        result = seismic_wall_coeff_vertical(k_h=0.0)
        assert_allclose(result, 0.0, atol=1e-12)

    def test_consistency_with_horizontal(self):
        """k_v e' meta' di k_h."""
        k_h = seismic_wall_coeff_horizontal(a_max=2.0, beta_m=0.38)
        k_v = seismic_wall_coeff_vertical(k_h)
        assert_allclose(k_v, k_h / 2.0, rtol=1e-10)

    def test_negative_kh_raises(self):
        with pytest.raises(ValueError):
            seismic_wall_coeff_vertical(k_h=-0.05)

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_wall_coeff_vertical)
        assert ref is not None
        assert ref.article == "7.11.6.2.1"
        assert ref.formula == "7.11.7"


# ── §7.11.6.2.1 [7.11.8] — Accelerazione sito per muri ─────────────────────


class TestSeismicWallSiteAcceleration:
    """NTC18 §7.11.6.2.1, Formula [7.11.8]."""

    def test_basic(self):
        """a_max = S_g * S_f * a_g = 1.2 * 1.1 * 2.0 = 2.64 m/s^2."""
        result = seismic_wall_site_acceleration(a_g=2.0, S_g=1.2, S_f=1.1)
        assert_allclose(result, 2.64, rtol=1e-5)

    def test_no_topography(self):
        """S_f = 1.0 (default): a_max = S_g * a_g."""
        result = seismic_wall_site_acceleration(a_g=1.5, S_g=1.3)
        assert_allclose(result, 1.5 * 1.3, rtol=1e-10)

    def test_edge_case_zero_ag(self):
        """a_g = 0 -> a_max = 0."""
        result = seismic_wall_site_acceleration(a_g=0.0, S_g=1.2)
        assert_allclose(result, 0.0, atol=1e-12)

    def test_negative_ag_raises(self):
        with pytest.raises(ValueError):
            seismic_wall_site_acceleration(a_g=-1.0, S_g=1.2)

    def test_zero_Sg_raises(self):
        with pytest.raises(ValueError):
            seismic_wall_site_acceleration(a_g=1.0, S_g=0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_wall_site_acceleration)
        assert ref is not None
        assert ref.article == "7.11.6.2.1"
        assert ref.formula == "7.11.8"


# ── §7.11.6.3.1 [7.11.9] — Accelerazione equivalente paratie ───────────────


class TestSeismicSheetPileAcceleration:
    """NTC18 §7.11.6.3.1, Formula [7.11.9]."""

    def test_basic(self):
        """alpha=0.8, beta=0.5, alpha*beta=0.4 > 0.2."""
        k_h, a_h = seismic_sheet_pile_acceleration(a_max=3.0, alpha=0.8, beta=0.5)
        expected_k_h = 0.8 * 0.5 * 3.0 / 9.81
        assert_allclose(k_h, expected_k_h, rtol=1e-5)
        assert_allclose(a_h, expected_k_h * 9.81, rtol=1e-5)

    def test_edge_case_low_alpha_beta(self):
        """alpha*beta=0.1 <= 0.2 -> k_h = 0.2 * a_max / g."""
        k_h, a_h = seismic_sheet_pile_acceleration(a_max=2.0, alpha=0.2, beta=0.5)
        expected_k_h = 0.2 * 2.0 / 9.81
        assert_allclose(k_h, expected_k_h, rtol=1e-5)

    def test_alpha_beta_exactly_0_2(self):
        """alpha*beta = 0.2 esattamente -> k_h = 0.2 * a_max / g."""
        k_h, _ = seismic_sheet_pile_acceleration(a_max=4.0, alpha=0.4, beta=0.5)
        expected_k_h = 0.2 * 4.0 / 9.81
        assert_allclose(k_h, expected_k_h, rtol=1e-5)

    def test_alpha_out_of_range_raises(self):
        with pytest.raises(ValueError):
            seismic_sheet_pile_acceleration(a_max=2.0, alpha=1.5, beta=0.5)

    def test_beta_negative_raises(self):
        with pytest.raises(ValueError):
            seismic_sheet_pile_acceleration(a_max=2.0, alpha=0.8, beta=-0.1)

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_sheet_pile_acceleration)
        assert ref is not None
        assert ref.article == "7.11.6.3.1"
        assert ref.formula == "7.11.9"


# ── §7.11.6.3.1 [7.11.10] — Accelerazione sito per paratie ─────────────────


class TestSeismicSheetPileSiteAcceleration:
    """NTC18 §7.11.6.3.1, Formula [7.11.10]."""

    def test_basic(self):
        """a_max = S_S * S_T * a_g = 1.3 * 1.2 * 1.5 = 2.34."""
        result = seismic_sheet_pile_site_acceleration(a_g=1.5, S_S=1.3, S_T=1.2)
        assert_allclose(result, 1.3 * 1.2 * 1.5, rtol=1e-5)

    def test_no_topography(self):
        """S_T=1.0 (default): a_max = S_S * a_g."""
        result = seismic_sheet_pile_site_acceleration(a_g=2.0, S_S=1.4)
        assert_allclose(result, 2.0 * 1.4, rtol=1e-10)

    def test_edge_case_zero_ag(self):
        result = seismic_sheet_pile_site_acceleration(a_g=0.0, S_S=1.2)
        assert_allclose(result, 0.0, atol=1e-12)

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_sheet_pile_site_acceleration)
        assert ref is not None
        assert ref.article == "7.11.6.3.1"
        assert ref.formula == "7.11.10"


# ── §7.11.6.3.1 [7.11.11] — Spostamento limite paratia ─────────────────────


class TestSeismicSheetPileDisplacementLimit:
    """NTC18 §7.11.6.3.1, Formula [7.11.11]."""

    def test_basic(self):
        """H = 10 m -> u_s_max = 0.005 * 10 = 0.05 m."""
        result = seismic_sheet_pile_displacement_limit(H=10.0)
        assert_allclose(result, 0.05, rtol=1e-10)

    def test_edge_case_small_height(self):
        """H = 0.5 m -> u_s_max = 0.0025 m."""
        result = seismic_sheet_pile_displacement_limit(H=0.5)
        assert_allclose(result, 0.0025, rtol=1e-10)

    def test_large_height(self):
        """H = 20 m -> u_s_max = 0.10 m."""
        result = seismic_sheet_pile_displacement_limit(H=20.0)
        assert_allclose(result, 0.10, rtol=1e-10)

    def test_zero_H_raises(self):
        with pytest.raises(ValueError):
            seismic_sheet_pile_displacement_limit(H=0.0)

    def test_negative_H_raises(self):
        with pytest.raises(ValueError):
            seismic_sheet_pile_displacement_limit(H=-5.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_sheet_pile_displacement_limit)
        assert ref is not None
        assert ref.article == "7.11.6.3.1"
        assert ref.formula == "7.11.11"


# ── §7.11.6.4 [7.11.12] — Lunghezza libera sismica ancoraggio ───────────────


class TestSeismicAnchorFreeLength:
    """NTC18 §7.11.6.4, Formula [7.11.12]."""

    def test_basic(self):
        """L_s=5.0, a_max=2.0: L_qi = 5 * (1 + 1.5*2.0/9.81)."""
        result = seismic_anchor_free_length(L_s=5.0, a_max=2.0)
        expected = 5.0 * (1.0 + 1.5 * 2.0 / 9.81)
        assert_allclose(result, expected, rtol=1e-5)

    def test_zero_acceleration(self):
        """a_max = 0 -> L_qi = L_s."""
        result = seismic_anchor_free_length(L_s=3.0, a_max=0.0)
        assert_allclose(result, 3.0, rtol=1e-10)

    def test_edge_case_high_acceleration(self):
        """a_max = 9.81 -> L_qi = L_s * 2.5."""
        result = seismic_anchor_free_length(L_s=4.0, a_max=9.81)
        assert_allclose(result, 4.0 * 2.5, rtol=1e-5)

    def test_zero_Ls_raises(self):
        with pytest.raises(ValueError):
            seismic_anchor_free_length(L_s=0.0, a_max=1.0)

    def test_negative_a_max_raises(self):
        with pytest.raises(ValueError):
            seismic_anchor_free_length(L_s=3.0, a_max=-1.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_anchor_free_length)
        assert ref is not None
        assert ref.article == "7.11.6.4"
        assert ref.formula == "7.11.12"


# ── §7.11.5.3.1 Tab.7.11.II — Coefficienti parziali fondazioni superficiali ─


class TestSeismicShallowFoundationGammaR:
    """NTC18 §7.11.5.3.1, Tab. 7.11.II."""

    def test_bearing(self):
        """Carico limite: gamma_R = 2.3."""
        result = seismic_shallow_foundation_gamma_R("bearing")
        assert_allclose(result, 2.3, rtol=1e-10)

    def test_sliding(self):
        """Scorrimento: gamma_R = 1.1."""
        result = seismic_shallow_foundation_gamma_R("sliding")
        assert_allclose(result, 1.1, rtol=1e-10)

    def test_lateral_resistance(self):
        """Resistenza superfici laterali: gamma_R = 1.3."""
        result = seismic_shallow_foundation_gamma_R("lateral_resistance")
        assert_allclose(result, 1.3, rtol=1e-10)

    def test_invalid_type_raises(self):
        with pytest.raises(ValueError):
            seismic_shallow_foundation_gamma_R("unknown")

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_shallow_foundation_gamma_R)
        assert ref is not None
        assert ref.article == "7.11.5.3.1"
        assert ref.table == "Tab.7.11.II"


# ── §7.10.5.3.1 [7.10.1] — Forza orizzontale isolamento ────────────────────


class TestSeismicIsolationBaseShear:
    """NTC18 §7.10.5.3.1, Formula [7.10.1]."""

    def test_basic(self):
        """F = M * S_x = 500 * 4.0 = 2000 kN."""
        result = seismic_isolation_base_shear(M=500.0, S_x=4.0)
        assert_allclose(result, 2000.0, rtol=1e-10)

    def test_edge_case_zero_sx(self):
        """S_x = 0 -> F = 0."""
        result = seismic_isolation_base_shear(M=300.0, S_x=0.0)
        assert_allclose(result, 0.0, atol=1e-12)

    def test_proportional_to_mass(self):
        """F proporzionale alla massa."""
        F1 = seismic_isolation_base_shear(M=100.0, S_x=3.0)
        F2 = seismic_isolation_base_shear(M=200.0, S_x=3.0)
        assert_allclose(F2, 2.0 * F1, rtol=1e-10)

    def test_zero_mass_raises(self):
        with pytest.raises(ValueError):
            seismic_isolation_base_shear(M=0.0, S_x=3.0)

    def test_negative_sx_raises(self):
        with pytest.raises(ValueError):
            seismic_isolation_base_shear(M=300.0, S_x=-1.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_isolation_base_shear)
        assert ref is not None
        assert ref.article == "7.10.5.3.1"
        assert ref.formula == "7.10.1"


# ── §7.10.5.3.1 [7.10.2] — Spostamento centro rigidezza isolamento ──────────


class TestSeismicIsolationDisplacement:
    """NTC18 §7.10.5.3.1, Formula [7.10.2]."""

    def test_basic(self):
        """d_uc = M * S_x / K_est_min = 500 * 4.0 / 2000 = 1.0 m."""
        result = seismic_isolation_displacement(M=500.0, S_x=4.0, K_est_min=2000.0)
        assert_allclose(result, 1.0, rtol=1e-10)

    def test_edge_case_zero_sx(self):
        """S_x = 0 -> d_uc = 0."""
        result = seismic_isolation_displacement(M=300.0, S_x=0.0, K_est_min=1000.0)
        assert_allclose(result, 0.0, atol=1e-12)

    def test_stiffer_system_smaller_displacement(self):
        """Sistema piu' rigido -> spostamento minore."""
        d1 = seismic_isolation_displacement(M=400.0, S_x=3.0, K_est_min=1000.0)
        d2 = seismic_isolation_displacement(M=400.0, S_x=3.0, K_est_min=2000.0)
        assert d1 > d2

    def test_zero_K_raises(self):
        with pytest.raises(ValueError):
            seismic_isolation_displacement(M=400.0, S_x=3.0, K_est_min=0.0)

    def test_zero_M_raises(self):
        with pytest.raises(ValueError):
            seismic_isolation_displacement(M=0.0, S_x=3.0, K_est_min=1000.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_isolation_displacement)
        assert ref is not None
        assert ref.article == "7.10.5.3.1"
        assert ref.formula == "7.10.2"


# ── §7.10.5.3.1 [7.10.4] — Amplificazione torsionale isolamento ─────────────


class TestSeismicIsolationTorsionAmplification:
    """NTC18 §7.10.5.3.1, Formula [7.10.4]."""

    def test_basic(self):
        """delta = 1 + (e_tot / r_j^2) * coord = 1 + (0.5 / 4.0) * 2.0 = 1.25."""
        result = seismic_isolation_torsion_amplification(
            e_tot=0.5, r_j=2.0, coord=2.0
        )
        assert_allclose(result, 1.25, rtol=1e-10)

    def test_no_eccentricity(self):
        """e_tot = 0 -> delta = 1.0."""
        result = seismic_isolation_torsion_amplification(
            e_tot=0.0, r_j=3.0, coord=1.5
        )
        assert_allclose(result, 1.0, rtol=1e-10)

    def test_negative_coord(self):
        """Dispositivo sul lato opposto -> delta < 1.0."""
        result = seismic_isolation_torsion_amplification(
            e_tot=0.5, r_j=2.0, coord=-2.0
        )
        assert_allclose(result, 0.75, rtol=1e-10)

    def test_zero_rj_raises(self):
        with pytest.raises(ValueError):
            seismic_isolation_torsion_amplification(
                e_tot=0.5, r_j=0.0, coord=1.0
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_isolation_torsion_amplification)
        assert ref is not None
        assert ref.article == "7.10.5.3.1"
        assert ref.formula == "7.10.4"


# ── §7.10.5.3.1 [7.10.5] — Raggio torsionale isolamento ────────────────────


class TestSeismicIsolationTorsionalRadius:
    """NTC18 §7.10.5.3.1, Formula [7.10.5]."""

    def test_basic_rx(self):
        """Calcolo r_x con 2 dispositivi simmetrici."""
        # 2 dispositivi a +/- 2m in x, +/- 1m in y, K_x=K_y=500
        x = [2.0, -2.0]
        y = [1.0, -1.0]
        K_x = [500.0, 500.0]
        K_y = [500.0, 500.0]
        # numerator = sum(xi^2 * Kyi + yi^2 * Kxi) = (4*500+1*500) + (4*500+1*500) = 5000
        # denominator (rx) = sum(K_y) = 1000
        # r_x = sqrt(5000/1000) = sqrt(5)
        result = seismic_isolation_torsional_radius(x, y, K_x, K_y, direction="x")
        assert_allclose(result, math.sqrt(5.0), rtol=1e-5)

    def test_basic_ry(self):
        """Calcolo r_y con 2 dispositivi simmetrici."""
        x = [2.0, -2.0]
        y = [1.0, -1.0]
        K_x = [500.0, 500.0]
        K_y = [500.0, 500.0]
        # denominator (ry) = sum(K_x) = 1000
        result = seismic_isolation_torsional_radius(x, y, K_x, K_y, direction="y")
        assert_allclose(result, math.sqrt(5.0), rtol=1e-5)

    def test_edge_case_single_device(self):
        """Un solo dispositivo."""
        result = seismic_isolation_torsional_radius(
            [3.0], [2.0], [1000.0], [1000.0], direction="x"
        )
        # numerator = 9*1000 + 4*1000 = 13000; denominator = 1000
        assert_allclose(result, math.sqrt(13.0), rtol=1e-5)

    def test_mismatched_lengths_raises(self):
        with pytest.raises(ValueError):
            seismic_isolation_torsional_radius(
                [1.0, 2.0], [1.0], [500.0, 500.0], [500.0, 500.0]
            )

    def test_invalid_direction_raises(self):
        with pytest.raises(ValueError):
            seismic_isolation_torsional_radius(
                [1.0], [1.0], [500.0], [500.0], direction="z"
            )

    def test_empty_arrays_raises(self):
        with pytest.raises(ValueError):
            seismic_isolation_torsional_radius([], [], [], [])

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_isolation_torsional_radius)
        assert ref is not None
        assert ref.article == "7.10.5.3.1"
        assert ref.formula == "7.10.5"
