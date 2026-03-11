"""Test per seismic_design — NTC18 Cap. 7."""

import math

import pytest
import numpy as np
from numpy.testing import assert_allclose

from pyntc.checks.seismic_design import (
    anchor_free_length_seismic,
    approximate_period,
    beam_column_joint_shear,
    beam_reinforcement_ratio_limits,
    behavior_factor,
    behavior_factor_base,
    behavior_factor_nondissipative,
    capacity_design_columns,
    column_capacity_shear,
    column_confinement_requirement,
    column_reinforcement_ratio_check,
    confinement_effectiveness_rectangular,
    cqc_modal_combination,
    curvature_ductility_demand,
    displacement_ductility,
    equivalent_static_forces,
    joint_concrete_compression_check,
    joint_eta_factor,
    joint_horizontal_stirrups,
    pdelta_sensitivity,
    pseudostatic_coefficients,
    retaining_wall_seismic_coefficients,
    seismic_directional_combination,
    seismic_force_nonstructural,
    sheet_pile_displacement_limit,
    sheet_pile_pseudostatic_acceleration,
    wall_confinement_requirement,
    wall_critical_height,
)
from pyntc.core.reference import get_ntc_ref


# ── [7.2.1] — Forza sismica su elementi non strutturali ──────────────────────


class TestSeismicForceNonstructural:
    """NTC18 §7.2.3, Formula [7.2.1]."""

    def test_basic(self):
        """F_a = S_a * W_a / q_a = 0.5 * 10 / 2.0 = 2.5 kN."""
        result = seismic_force_nonstructural(S_a=0.5, W_a=10.0, q_a=2.0)
        assert_allclose(result, 2.5, rtol=1e-3)

    def test_unit_behavior_factor(self):
        """q_a = 1.0: F_a = S_a * W_a = 1.0 * 5.0 = 5.0 kN."""
        result = seismic_force_nonstructural(S_a=1.0, W_a=5.0, q_a=1.0)
        assert_allclose(result, 5.0, rtol=1e-3)

    def test_high_acceleration(self):
        """S_a = 3.0, W_a = 20.0, q_a = 1.5 -> 40.0 kN."""
        result = seismic_force_nonstructural(S_a=3.0, W_a=20.0, q_a=1.5)
        assert_allclose(result, 40.0, rtol=1e-3)

    def test_q_a_zero_raises(self):
        with pytest.raises(ValueError):
            seismic_force_nonstructural(S_a=0.5, W_a=10.0, q_a=0.0)

    def test_negative_q_a_raises(self):
        with pytest.raises(ValueError):
            seismic_force_nonstructural(S_a=0.5, W_a=10.0, q_a=-1.0)

    def test_negative_W_a_raises(self):
        with pytest.raises(ValueError):
            seismic_force_nonstructural(S_a=0.5, W_a=-10.0, q_a=2.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_force_nonstructural)
        assert ref is not None
        assert ref.article == "7.2.3"
        assert ref.formula == "7.2.1"


# ── Tab. 7.3.II — Fattore di comportamento base q_0 ─────────────────────────


class TestBehaviorFactorBase:
    """NTC18 §7.3.1, Tab. 7.3.II."""

    def test_rc_frame_cda(self):
        """C.a. telaio CD'A': q_0 = 4.5 * alpha_ratio."""
        result = behavior_factor_base("rc_frame", "A", alpha_ratio=1.3)
        assert_allclose(result, 4.5 * 1.3, rtol=1e-3)

    def test_rc_frame_cdb(self):
        """C.a. telaio CD'B': q_0 = 3.0 * alpha_ratio."""
        result = behavior_factor_base("rc_frame", "B", alpha_ratio=1.3)
        assert_allclose(result, 3.0 * 1.3, rtol=1e-3)

    def test_rc_wall_uncoupled_cda(self):
        """C.a. pareti non accoppiate CD'A': q_0 = 4.0 * alpha_ratio."""
        result = behavior_factor_base("rc_wall_uncoupled", "A", alpha_ratio=1.2)
        assert_allclose(result, 4.0 * 1.2, rtol=1e-3)

    def test_rc_wall_uncoupled_cdb(self):
        """C.a. pareti non accoppiate CD'B': q_0 = 3.0 (no alpha_ratio)."""
        result = behavior_factor_base("rc_wall_uncoupled", "B")
        assert_allclose(result, 3.0, rtol=1e-3)

    def test_rc_torsional_cda(self):
        """C.a. torsionalmente deformabile CD'A': q_0 = 3.0."""
        result = behavior_factor_base("rc_torsional", "A")
        assert_allclose(result, 3.0, rtol=1e-3)

    def test_rc_torsional_cdb(self):
        """C.a. torsionalmente deformabile CD'B': q_0 = 2.0."""
        result = behavior_factor_base("rc_torsional", "B")
        assert_allclose(result, 2.0, rtol=1e-3)

    def test_rc_inverted_pendulum_cda(self):
        result = behavior_factor_base("rc_inverted_pendulum", "A")
        assert_allclose(result, 2.0, rtol=1e-3)

    def test_rc_inverted_pendulum_cdb(self):
        result = behavior_factor_base("rc_inverted_pendulum", "B")
        assert_allclose(result, 1.5, rtol=1e-3)

    def test_rc_inverted_pendulum_framed_cda(self):
        result = behavior_factor_base("rc_inverted_pendulum_framed", "A")
        assert_allclose(result, 3.5, rtol=1e-3)

    def test_steel_frame_cda(self):
        """Acciaio telaio CD'A': q_0 = 5.0 * alpha_ratio."""
        result = behavior_factor_base("steel_frame", "A", alpha_ratio=1.2)
        assert_allclose(result, 5.0 * 1.2, rtol=1e-3)

    def test_steel_frame_cdb(self):
        """Acciaio telaio CD'B': q_0 = 4.0."""
        result = behavior_factor_base("steel_frame", "B")
        assert_allclose(result, 4.0, rtol=1e-3)

    def test_steel_braced_eccentric(self):
        """Controventi eccentrici CD'A' e CD'B': q_0 = 4.0."""
        assert_allclose(
            behavior_factor_base("steel_braced_eccentric", "A"), 4.0, rtol=1e-3
        )
        assert_allclose(
            behavior_factor_base("steel_braced_eccentric", "B"), 4.0, rtol=1e-3
        )

    def test_masonry_ordinary(self):
        """Muratura ordinaria: q_0 = 1.75 * alpha_ratio."""
        result = behavior_factor_base("masonry_ordinary", alpha_ratio=1.4)
        assert_allclose(result, 1.75 * 1.4, rtol=1e-3)

    def test_masonry_reinforced(self):
        """Muratura armata: q_0 = 2.5 * alpha_ratio."""
        result = behavior_factor_base("masonry_reinforced", alpha_ratio=1.3)
        assert_allclose(result, 2.5 * 1.3, rtol=1e-3)

    def test_bridge_rc_vertical_cda(self):
        """Ponte pile c.a. verticali CD'A': q_0 = 3.5 * lambda_factor."""
        result = behavior_factor_base(
            "bridge_rc_vertical", "A", lambda_factor=1.0
        )
        assert_allclose(result, 3.5, rtol=1e-3)

    def test_bridge_abutment(self):
        """Spalle: q_0 = 1.5 (CD'A') e 1.5 (CD'B')."""
        assert_allclose(
            behavior_factor_base("bridge_abutment", "A"), 1.5, rtol=1e-3
        )
        assert_allclose(
            behavior_factor_base("bridge_abutment", "B"), 1.5, rtol=1e-3
        )

    def test_bridge_abutment_soil(self):
        """Spalle con terreno: q_0 = 1.0."""
        assert_allclose(
            behavior_factor_base("bridge_abutment_soil", "A"), 1.0, rtol=1e-3
        )

    def test_alpha_ratio_default(self):
        """alpha_ratio=1.0 di default non modifica il risultato base."""
        result = behavior_factor_base("rc_frame", "A")
        assert_allclose(result, 4.5, rtol=1e-3)

    def test_invalid_type_raises(self):
        with pytest.raises(ValueError):
            behavior_factor_base("invalid_type", "A")

    def test_invalid_ductility_class_raises(self):
        with pytest.raises(ValueError):
            behavior_factor_base("rc_frame", "C")

    def test_ntc_ref(self):
        ref = get_ntc_ref(behavior_factor_base)
        assert ref is not None
        assert ref.article == "7.3.1"
        assert ref.table == "Tab.7.3.II"


# ── [7.3.1] — Fattore di comportamento limite ────────────────────────────────


class TestBehaviorFactor:
    """NTC18 §7.3.1, Formula [7.3.1]."""

    def test_regular(self):
        """q_lim = q_0 * 1.0 per strutture regolari in altezza."""
        result = behavior_factor(q_0=4.5, regular_in_height=True)
        assert_allclose(result, 4.5, rtol=1e-3)

    def test_irregular(self):
        """q_lim = q_0 * 0.8 per strutture non regolari in altezza."""
        result = behavior_factor(q_0=4.5, regular_in_height=False)
        assert_allclose(result, 3.6, rtol=1e-3)

    def test_irregular_steel(self):
        """q_lim = 5.0 * 0.8 = 4.0."""
        result = behavior_factor(q_0=5.0, regular_in_height=False)
        assert_allclose(result, 4.0, rtol=1e-3)

    def test_q0_nonpositive_raises(self):
        with pytest.raises(ValueError):
            behavior_factor(q_0=0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(behavior_factor)
        assert ref is not None
        assert ref.formula == "7.3.1"


# ── [7.3.2] — Fattore di comportamento non dissipativo ───────────────────────


class TestBehaviorFactorNondissipative:
    """NTC18 §7.3.1, Formula [7.3.2]."""

    def test_clamped_high(self):
        """q_CDB = 3.0: (2/3)*3.0 = 2.0 -> clamped to 1.5."""
        result = behavior_factor_nondissipative(q_cdb=3.0)
        assert_allclose(result, 1.5, rtol=1e-3)

    def test_middle_value(self):
        """q_CDB = 2.0: (2/3)*2.0 = 1.333."""
        result = behavior_factor_nondissipative(q_cdb=2.0)
        assert_allclose(result, 4.0 / 3.0, rtol=1e-3)

    def test_clamped_low(self):
        """q_CDB = 1.2: (2/3)*1.2 = 0.8 -> clamped to 1.0."""
        result = behavior_factor_nondissipative(q_cdb=1.2)
        assert_allclose(result, 1.0, rtol=1e-3)

    def test_exact_upper(self):
        """q_CDB = 2.25: (2/3)*2.25 = 1.5 exactly."""
        result = behavior_factor_nondissipative(q_cdb=2.25)
        assert_allclose(result, 1.5, rtol=1e-3)

    def test_exact_lower(self):
        """q_CDB = 1.5: (2/3)*1.5 = 1.0 exactly."""
        result = behavior_factor_nondissipative(q_cdb=1.5)
        assert_allclose(result, 1.0, rtol=1e-3)

    def test_q_cdb_nonpositive_raises(self):
        with pytest.raises(ValueError):
            behavior_factor_nondissipative(q_cdb=0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(behavior_factor_nondissipative)
        assert ref is not None
        assert ref.formula == "7.3.2"


# ── [7.3.3] — Sensibilita' agli effetti P-delta ──────────────────────────────


class TestPdeltaSensitivity:
    """NTC18 §7.3.1, Formula [7.3.3]."""

    def test_negligible(self):
        """theta = 5000*0.01/(500*3) = 0.0333 < 0.1 -> negligible."""
        theta, action, factor = pdelta_sensitivity(
            P=5000.0, d_r=0.01, V=500.0, h=3.0
        )
        assert_allclose(theta, 1.0 / 30.0, rtol=1e-3)
        assert action == "negligible"
        assert_allclose(factor, 1.0, rtol=1e-3)

    def test_amplify(self):
        """theta = 10000*0.05/(1000*3) = 0.1667, factor = 1/(1-0.1667)."""
        theta, action, factor = pdelta_sensitivity(
            P=10000.0, d_r=0.05, V=1000.0, h=3.0
        )
        expected_theta = 10000 * 0.05 / (1000 * 3.0)
        assert_allclose(theta, expected_theta, rtol=1e-3)
        assert action == "amplify"
        assert_allclose(factor, 1.0 / (1.0 - expected_theta), rtol=1e-3)

    def test_nonlinear(self):
        """theta = 15000*0.07/(1000*3.5) = 0.3 -> nonlinear."""
        theta, action, factor = pdelta_sensitivity(
            P=15000.0, d_r=0.07, V=1000.0, h=3.5
        )
        assert_allclose(theta, 0.3, rtol=1e-3)
        assert action == "nonlinear_required"

    def test_boundary_01(self):
        """theta = 0.1 esattamente -> amplify."""
        # P*d_r/(V*h) = 0.1 -> P=1000, d_r=0.01, V=1, h=100
        theta, action, _ = pdelta_sensitivity(
            P=1000.0, d_r=0.01, V=1.0, h=100.0
        )
        assert_allclose(theta, 0.1, rtol=1e-6)
        assert action == "amplify"

    def test_boundary_02(self):
        """theta = 0.2 esattamente -> amplify (incluso nel range 0.1-0.2)."""
        theta, action, factor = pdelta_sensitivity(
            P=2000.0, d_r=0.01, V=1.0, h=100.0
        )
        assert_allclose(theta, 0.2, rtol=1e-6)
        assert action == "amplify"
        assert_allclose(factor, 1.0 / 0.8, rtol=1e-3)

    def test_exceed_raises(self):
        """theta > 0.3 -> ValueError."""
        with pytest.raises(ValueError):
            pdelta_sensitivity(P=10000.0, d_r=0.10, V=100.0, h=3.0)

    def test_V_zero_raises(self):
        with pytest.raises(ValueError):
            pdelta_sensitivity(P=5000.0, d_r=0.01, V=0.0, h=3.0)

    def test_h_zero_raises(self):
        with pytest.raises(ValueError):
            pdelta_sensitivity(P=5000.0, d_r=0.01, V=500.0, h=0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(pdelta_sensitivity)
        assert ref is not None
        assert ref.formula == "7.3.3"


# ── [7.3.4]-[7.3.5] — Combinazione modale CQC ───────────────────────────────


class TestCqcModalCombination:
    """NTC18 §7.3.3.1, Formule [7.3.4]-[7.3.5b]."""

    def test_single_mode(self):
        """Singolo modo: E = E_1."""
        result = cqc_modal_combination(
            effects=np.array([75.0]),
            periods=np.array([0.5]),
            damping=0.05,
        )
        assert_allclose(result, 75.0, rtol=1e-3)

    def test_two_modes_separated(self):
        """Due modi ben separati T=[1.0, 0.3]: quasi SRSS."""
        effects = np.array([100.0, 40.0])
        periods = np.array([1.0, 0.3])
        result = cqc_modal_combination(effects, periods, damping=0.05)
        # SRSS: sqrt(10000 + 1600) = 107.70
        # CQC con rho_12 molto piccolo: poco piu' di SRSS
        assert result > 107.0
        assert result < 110.0

    def test_identical_modes(self):
        """Due modi identici T=[1.0, 1.0]: rho_12 = 1.0, E = E_1 + E_2."""
        effects = np.array([100.0, 50.0])
        periods = np.array([1.0, 1.0])
        result = cqc_modal_combination(effects, periods, damping=0.05)
        assert_allclose(result, 150.0, rtol=1e-3)

    def test_close_modes(self):
        """Due modi vicini T=[1.0, 0.95]: alta correlazione."""
        effects = np.array([100.0, 80.0])
        periods = np.array([1.0, 0.95])
        result = cqc_modal_combination(effects, periods, damping=0.05)
        # Alta correlazione: risultato piu' vicino alla somma (180)
        # che alla SRSS (128.06)
        assert result > 140.0
        assert result < 180.0

    def test_three_modes(self):
        """Tre modi: verifica strutturale del calcolo."""
        effects = np.array([100.0, 60.0, 20.0])
        periods = np.array([1.0, 0.4, 0.2])
        result = cqc_modal_combination(effects, periods, damping=0.05)
        # Modi ben separati: circa SRSS
        srss = math.sqrt(100**2 + 60**2 + 20**2)
        assert_allclose(result, srss, rtol=0.05)

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            cqc_modal_combination(np.array([]), np.array([]), damping=0.05)

    def test_mismatch_raises(self):
        with pytest.raises(ValueError):
            cqc_modal_combination(
                np.array([100.0, 50.0]),
                np.array([1.0]),
                damping=0.05,
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(cqc_modal_combination)
        assert ref is not None
        assert ref.formula == "7.3.4"


# ── [7.3.6] — Periodo approssimato ───────────────────────────────────────────


class TestApproximatePeriod:
    """NTC18 §7.3.3.2, Formula [7.3.6]."""

    def test_basic(self):
        """d = 0.01 m -> T = 2*sqrt(0.01) = 0.2 s."""
        result = approximate_period(d=0.01)
        assert_allclose(result, 0.2, rtol=1e-3)

    def test_larger_displacement(self):
        """d = 0.05 m -> T = 2*sqrt(0.05) = 0.4472 s."""
        result = approximate_period(d=0.05)
        assert_allclose(result, 2.0 * math.sqrt(0.05), rtol=1e-3)

    def test_zero(self):
        """d = 0 -> T = 0."""
        result = approximate_period(d=0.0)
        assert_allclose(result, 0.0, rtol=1e-3)

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            approximate_period(d=-0.01)

    def test_ntc_ref(self):
        ref = get_ntc_ref(approximate_period)
        assert ref is not None
        assert ref.formula == "7.3.6"


# ── [7.3.7] — Forze statiche equivalenti ─────────────────────────────────────


class TestEquivalentStaticForces:
    """NTC18 §7.3.3.2, Formula [7.3.7]."""

    def test_three_floors_lambda_085(self):
        """3 piani, T_1 < 2*T_c -> lambda = 0.85."""
        # S_d = 0.25g = 2.4525 m/s^2
        S_d = 0.25 * 9.81
        weights = np.array([100.0, 100.0, 100.0])
        heights = np.array([3.0, 6.0, 9.0])
        forces = equivalent_static_forces(
            S_d_T1=S_d, weights=weights, heights=heights,
            T_1=0.5, T_c=0.6, n_floors=3,
        )
        F_h = 0.25 * 300.0 * 0.85
        assert_allclose(forces[0], F_h * 300.0 / 1800.0, rtol=1e-3)
        assert_allclose(forces[1], F_h * 600.0 / 1800.0, rtol=1e-3)
        assert_allclose(forces[2], F_h * 900.0 / 1800.0, rtol=1e-3)
        assert_allclose(np.sum(forces), F_h, rtol=1e-3)

    def test_two_floors_lambda_10(self):
        """2 piani -> lambda = 1.0 (meno di 3 piani)."""
        S_d = 0.15 * 9.81
        weights = np.array([200.0, 200.0])
        heights = np.array([3.5, 7.0])
        forces = equivalent_static_forces(
            S_d_T1=S_d, weights=weights, heights=heights,
            T_1=1.5, T_c=0.5, n_floors=2,
        )
        F_h = 0.15 * 400.0 * 1.0
        assert_allclose(np.sum(forces), F_h, rtol=1e-3)

    def test_high_period_lambda_10(self):
        """T_1 >= 2*T_c -> lambda = 1.0 anche con 3+ piani."""
        S_d = 0.20 * 9.81
        weights = np.array([100.0, 100.0, 100.0])
        heights = np.array([3.0, 6.0, 9.0])
        forces = equivalent_static_forces(
            S_d_T1=S_d, weights=weights, heights=heights,
            T_1=1.2, T_c=0.5, n_floors=3,
        )
        # T_1 = 1.2 >= 2*0.5 = 1.0 -> lambda = 1.0
        F_h = 0.20 * 300.0 * 1.0
        assert_allclose(np.sum(forces), F_h, rtol=1e-3)

    def test_force_distribution_proportional_to_z_W(self):
        """Le forze devono essere proporzionali a z_i * W_i."""
        S_d = 0.3 * 9.81
        weights = np.array([150.0, 100.0, 50.0])
        heights = np.array([4.0, 8.0, 12.0])
        forces = equivalent_static_forces(
            S_d_T1=S_d, weights=weights, heights=heights,
            T_1=0.4, T_c=0.5, n_floors=3,
        )
        z_W = heights * weights
        ratios = forces / forces[0]
        expected_ratios = z_W / z_W[0]
        assert_allclose(ratios, expected_ratios, rtol=1e-3)

    def test_mismatch_raises(self):
        with pytest.raises(ValueError):
            equivalent_static_forces(
                S_d_T1=2.0, weights=np.array([100.0]),
                heights=np.array([3.0, 6.0]),
                T_1=0.5, T_c=0.5, n_floors=1,
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(equivalent_static_forces)
        assert ref is not None
        assert ref.formula == "7.3.7"


# ── [7.3.8]-[7.3.9] — Fattore di duttilita' in spostamento ──────────────────


class TestDisplacementDuctility:
    """NTC18 §7.3.3.3, Formule [7.3.8]-[7.3.9]."""

    def test_long_period(self):
        """T_1 >= T_c: mu_d = q = 4.0."""
        result = displacement_ductility(q=4.0, T_1=1.0, T_c=0.5)
        assert_allclose(result, 4.0, rtol=1e-3)

    def test_short_period(self):
        """T_1 < T_c: mu_d = 1 + (q-1)*T_c/T_1."""
        result = displacement_ductility(q=3.0, T_1=0.3, T_c=0.5)
        expected = 1.0 + (3.0 - 1.0) * 0.5 / 0.3
        assert_allclose(result, expected, rtol=1e-3)

    def test_equal_periods(self):
        """T_1 = T_c: mu_d = q (ramo lungo periodo)."""
        result = displacement_ductility(q=2.5, T_1=0.5, T_c=0.5)
        assert_allclose(result, 2.5, rtol=1e-3)

    def test_cap_5q_minus_4(self):
        """mu_d non deve superare 5q-4."""
        # q=2.0, T_1=0.1, T_c=0.5:
        # mu_d = 1 + (2-1)*0.5/0.1 = 6.0
        # 5*2-4 = 6 -> mu_d = 6.0 (at the cap)
        result = displacement_ductility(q=2.0, T_1=0.1, T_c=0.5)
        assert_allclose(result, 6.0, rtol=1e-3)

    def test_cap_active(self):
        """Cap attivo: mu_d calcolato > 5q-4."""
        # q=1.5, T_1=0.05, T_c=0.5:
        # mu_d = 1 + 0.5*10 = 6.0
        # 5*1.5-4 = 3.5 -> mu_d = 3.5
        result = displacement_ductility(q=1.5, T_1=0.05, T_c=0.5)
        assert_allclose(result, 3.5, rtol=1e-3)

    def test_q_less_than_1_raises(self):
        with pytest.raises(ValueError):
            displacement_ductility(q=0.5, T_1=1.0, T_c=0.5)

    def test_T1_nonpositive_raises(self):
        with pytest.raises(ValueError):
            displacement_ductility(q=3.0, T_1=0.0, T_c=0.5)

    def test_ntc_ref(self):
        ref = get_ntc_ref(displacement_ductility)
        assert ref is not None
        assert ref.formula == "7.3.8"


# ── [7.3.10] — Combinazione direzionale ──────────────────────────────────────


class TestSeismicDirectionalCombination:
    """NTC18 §7.3.5, Formula [7.3.10]."""

    def test_three_components(self):
        """1.00*E_x + 0.30*E_y + 0.30*E_z = 121."""
        combos = seismic_directional_combination(
            E_x=100.0, E_y=50.0, E_z=20.0
        )
        assert_allclose(combos[0], 100.0 + 15.0 + 6.0, rtol=1e-3)
        assert_allclose(combos[1], 30.0 + 50.0 + 6.0, rtol=1e-3)
        assert_allclose(combos[2], 30.0 + 15.0 + 20.0, rtol=1e-3)

    def test_two_components(self):
        """E_z = 0: solo componenti orizzontali."""
        combos = seismic_directional_combination(E_x=100.0, E_y=50.0)
        assert_allclose(combos[0], 100.0 + 15.0, rtol=1e-3)
        assert_allclose(combos[1], 30.0 + 50.0, rtol=1e-3)
        assert_allclose(combos[2], 30.0 + 15.0, rtol=1e-3)

    def test_permutation_symmetry(self):
        """Permutazione simmetrica: E_x = E_y = E_z."""
        combos = seismic_directional_combination(E_x=100.0, E_y=100.0, E_z=100.0)
        # Tutte e tre le combinazioni danno 100 + 30 + 30 = 160
        assert_allclose(combos[0], 160.0, rtol=1e-3)
        assert_allclose(combos[1], 160.0, rtol=1e-3)
        assert_allclose(combos[2], 160.0, rtol=1e-3)

    def test_negative_raises(self):
        """Effetti devono essere non negativi."""
        with pytest.raises(ValueError):
            seismic_directional_combination(E_x=-100.0, E_y=50.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_directional_combination)
        assert ref is not None
        assert ref.formula == "7.3.10"


# ── [7.4.3] — Domanda di duttilita' in curvatura ─────────────────────────────


class TestCurvatureDuctilityDemand:
    """NTC18 §7.4.4.1.2, Formula [7.4.3]."""

    def test_long_period(self):
        """T_1 >= T_c: mu_phi0 = 1.2*(2*q_0-1)."""
        result = curvature_ductility_demand(q_0=4.5, T_1=1.0, T_c=0.5)
        assert_allclose(result, 1.2 * (2 * 4.5 - 1), rtol=1e-3)

    def test_short_period(self):
        """T_1 < T_c: mu_phi0 = 1 + 2*(q_0-1)*T_c/T_1."""
        result = curvature_ductility_demand(q_0=3.0, T_1=0.3, T_c=0.5)
        expected = 1.0 + 2.0 * (3.0 - 1.0) * 0.5 / 0.3
        assert_allclose(result, expected, rtol=1e-3)

    def test_equal_periods(self):
        """T_1 = T_c: usa il ramo T_1 >= T_c."""
        result = curvature_ductility_demand(q_0=1.5, T_1=0.5, T_c=0.5)
        assert_allclose(result, 1.2 * (2 * 1.5 - 1), rtol=1e-3)

    def test_low_q0(self):
        """q_0 = 1.0: mu_phi0 = 1.2*(2-1) = 1.2."""
        result = curvature_ductility_demand(q_0=1.0, T_1=1.0, T_c=0.5)
        assert_allclose(result, 1.2, rtol=1e-3)

    def test_q0_less_than_1_raises(self):
        with pytest.raises(ValueError):
            curvature_ductility_demand(q_0=0.5, T_1=1.0, T_c=0.5)

    def test_ntc_ref(self):
        ref = get_ntc_ref(curvature_ductility_demand)
        assert ref is not None
        assert ref.formula == "7.4.3"


# ── [7.4.4] — Gerarchia delle resistenze ai nodi trave-pilastro ──────────────


class TestCapacityDesignColumns:
    """NTC18 §7.4.4.2.1, Formula [7.4.4]."""

    def test_not_satisfied(self):
        """Somma M_c < gamma_Rd * Somma M_b."""
        satisfied, ratio = capacity_design_columns(
            M_c=np.array([200.0, 300.0]),
            M_b=np.array([150.0, 250.0]),
            gamma_Rd=1.3,
        )
        assert satisfied is False
        assert_allclose(ratio, 500.0 / (1.3 * 400.0), rtol=1e-3)

    def test_satisfied(self):
        """Somma M_c >= gamma_Rd * Somma M_b."""
        satisfied, ratio = capacity_design_columns(
            M_c=np.array([300.0, 400.0]),
            M_b=np.array([150.0, 250.0]),
            gamma_Rd=1.3,
        )
        assert satisfied is True
        assert_allclose(ratio, 700.0 / (1.3 * 400.0), rtol=1e-3)

    def test_exact_boundary(self):
        """Somma M_c = gamma_Rd * Somma M_b -> satisfied."""
        satisfied, ratio = capacity_design_columns(
            M_c=np.array([260.0, 260.0]),
            M_b=np.array([200.0, 200.0]),
            gamma_Rd=1.3,
        )
        assert satisfied is True
        assert_allclose(ratio, 1.0, rtol=1e-3)

    def test_single_beam_single_column(self):
        """Caso semplice: un pilastro e una trave."""
        satisfied, ratio = capacity_design_columns(
            M_c=np.array([500.0]),
            M_b=np.array([300.0]),
            gamma_Rd=1.3,
        )
        assert satisfied is True
        assert_allclose(ratio, 500.0 / (1.3 * 300.0), rtol=1e-3)

    def test_gamma_Rd_nonpositive_raises(self):
        with pytest.raises(ValueError):
            capacity_design_columns(
                M_c=np.array([200.0]),
                M_b=np.array([100.0]),
                gamma_Rd=0.0,
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(capacity_design_columns)
        assert ref is not None
        assert ref.formula == "7.4.4"


# ── [7.11.3]-[7.11.5] — Coefficienti pseudostatici per pendii ────────────────


class TestPseudostaticCoefficients:
    """NTC18 §7.11.3.5.2, Formule [7.11.3]-[7.11.5]."""

    def test_basic(self):
        """a_g=0.25g, S_s=1.2, S_t=1.0, beta_s=0.38."""
        k_h, k_v, a_max = pseudostatic_coefficients(
            a_g=0.25 * 9.81, S_s=1.2, S_t=1.0, beta_s=0.38
        )
        expected_amax = 1.2 * 1.0 * 0.25 * 9.81
        expected_kh = 0.38 * expected_amax / 9.81
        expected_kv = 0.5 * expected_kh
        assert_allclose(a_max, expected_amax, rtol=1e-3)
        assert_allclose(k_h, expected_kh, rtol=1e-3)
        assert_allclose(k_v, expected_kv, rtol=1e-3)

    def test_high_amplification(self):
        """a_g=0.15g, S_s=1.5, S_t=1.2, beta_s=0.41."""
        k_h, k_v, a_max = pseudostatic_coefficients(
            a_g=0.15 * 9.81, S_s=1.5, S_t=1.2, beta_s=0.41
        )
        expected_amax = 1.5 * 1.2 * 0.15 * 9.81
        expected_kh = 0.41 * expected_amax / 9.81
        assert_allclose(a_max, expected_amax, rtol=1e-3)
        assert_allclose(k_h, expected_kh, rtol=1e-3)
        assert_allclose(k_v, 0.5 * expected_kh, rtol=1e-3)

    def test_no_amplification(self):
        """S_s=1.0, S_t=1.0: a_max = a_g."""
        k_h, k_v, a_max = pseudostatic_coefficients(
            a_g=0.35 * 9.81, S_s=1.0, S_t=1.0, beta_s=0.30
        )
        assert_allclose(a_max, 0.35 * 9.81, rtol=1e-3)
        assert_allclose(k_h, 0.30 * 0.35, rtol=1e-3)

    def test_beta_s_zero(self):
        """beta_s = 0: k_h = 0, k_v = 0."""
        k_h, k_v, _ = pseudostatic_coefficients(
            a_g=0.25 * 9.81, S_s=1.2, S_t=1.0, beta_s=0.0
        )
        assert_allclose(k_h, 0.0, atol=1e-10)
        assert_allclose(k_v, 0.0, atol=1e-10)

    def test_a_g_negative_raises(self):
        with pytest.raises(ValueError):
            pseudostatic_coefficients(
                a_g=-0.1, S_s=1.2, S_t=1.0, beta_s=0.38
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(pseudostatic_coefficients)
        assert ref is not None
        assert ref.formula == "7.11.3"


# ── [7.4.5] — Taglio di progetto in capacita' per pilastri ───────────────────


class TestColumnCapacityShear:
    """NTC18 §7.4.4.2.1, Formula [7.4.5]."""

    def test_basic(self):
        """V = gamma_Rd * (M_top + M_bot) / l_p = 1.2 * (200+150) / 3.5."""
        result = column_capacity_shear(
            M_top=200.0, M_bot=150.0, l_p=3.5, gamma_Rd=1.2
        )
        assert_allclose(result, 1.2 * 350.0 / 3.5, rtol=1e-3)

    def test_symmetric_moments(self):
        """Momenti uguali agli estremi."""
        result = column_capacity_shear(
            M_top=300.0, M_bot=300.0, l_p=4.0, gamma_Rd=1.3
        )
        assert_allclose(result, 1.3 * 600.0 / 4.0, rtol=1e-3)

    def test_edge_cases(self):
        """gamma_Rd = 1.0 (CD'B')."""
        result = column_capacity_shear(
            M_top=100.0, M_bot=80.0, l_p=2.8, gamma_Rd=1.0
        )
        assert_allclose(result, 180.0 / 2.8, rtol=1e-3)

    def test_lp_zero_raises(self):
        with pytest.raises(ValueError):
            column_capacity_shear(M_top=200.0, M_bot=150.0, l_p=0.0, gamma_Rd=1.2)

    def test_negative_gamma_raises(self):
        with pytest.raises(ValueError):
            column_capacity_shear(M_top=200.0, M_bot=150.0, l_p=3.0, gamma_Rd=-1.0)

    def test_negative_moment_raises(self):
        with pytest.raises(ValueError):
            column_capacity_shear(M_top=-200.0, M_bot=150.0, l_p=3.0, gamma_Rd=1.2)

    def test_ntc_ref(self):
        ref = get_ntc_ref(column_capacity_shear)
        assert ref is not None
        assert ref.formula == "7.4.5"


# ── [7.4.6/7.4.7] — Taglio nodo trave-pilastro ───────────────────────────────


class TestBeamColumnJointShear:
    """NTC18 §7.4.4.3.1, Formule [7.4.6] e [7.4.7]."""

    def test_interior_node(self):
        """Nodo interno: V_jd = gamma_Rd*(A_s1+A_s2)*f_yd - V_C."""
        # A_s1=20e-4 m^2, A_s2=15e-4 m^2, f_yd=434e3 kN/m^2, V_C=100 kN
        result = beam_column_joint_shear(
            A_s1=20e-4, A_s2=15e-4, f_yd=434e3, V_C=100.0, gamma_Rd=1.2
        )
        expected = 1.2 * (20e-4 + 15e-4) * 434e3 - 100.0
        assert_allclose(result, expected, rtol=1e-3)

    def test_exterior_node(self):
        """Nodo esterno: V_jd = gamma_Rd*A_s1*f_yd - V_C."""
        result = beam_column_joint_shear(
            A_s1=20e-4, A_s2=15e-4, f_yd=434e3, V_C=80.0,
            gamma_Rd=1.2, interior=False,
        )
        expected = 1.2 * 20e-4 * 434e3 - 80.0
        assert_allclose(result, expected, rtol=1e-3)

    def test_zero_vc(self):
        """V_C = 0: contributo pieno."""
        result = beam_column_joint_shear(
            A_s1=10e-4, A_s2=10e-4, f_yd=391e3, V_C=0.0, gamma_Rd=1.0
        )
        assert_allclose(result, 2 * 10e-4 * 391e3, rtol=1e-3)

    def test_invalid_fyd_raises(self):
        with pytest.raises(ValueError):
            beam_column_joint_shear(
                A_s1=20e-4, A_s2=15e-4, f_yd=0.0, V_C=100.0, gamma_Rd=1.2
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(beam_column_joint_shear)
        assert ref is not None
        assert ref.formula == "7.4.6"


# ── [7.4.8] — Verifica compressione puntone nodo ─────────────────────────────


class TestJointConcreteCompressionCheck:
    """NTC18 §7.4.4.3.1, Formula [7.4.8]."""

    def test_satisfied(self):
        """V_jd <= V_Rd -> verificato."""
        # eta=0.504, f_sd=17000 kN/m^2, b_j=0.4, h_js=0.4, v_d=0.2
        eta = 0.504
        f_sd = 17000.0
        b_j, h_js = 0.4, 0.4
        v_d = 0.2
        V_Rd = eta * f_sd * b_j * h_js * math.sqrt(1 - v_d / eta)
        V_jd = 0.8 * V_Rd
        satisfied, ratio = joint_concrete_compression_check(
            V_jd=V_jd, eta=eta, f_sd=f_sd, b_j=b_j, h_js=h_js, v_d=v_d
        )
        assert satisfied is True
        assert_allclose(ratio, 0.8, rtol=1e-3)

    def test_not_satisfied(self):
        """V_jd > V_Rd -> non verificato."""
        eta = 0.504
        f_sd = 17000.0
        b_j, h_js = 0.4, 0.4
        v_d = 0.2
        V_Rd = eta * f_sd * b_j * h_js * math.sqrt(1 - v_d / eta)
        V_jd = 1.2 * V_Rd
        satisfied, ratio = joint_concrete_compression_check(
            V_jd=V_jd, eta=eta, f_sd=f_sd, b_j=b_j, h_js=h_js, v_d=v_d
        )
        assert satisfied is False
        assert_allclose(ratio, 1.2, rtol=1e-3)

    def test_invalid_vd_raises(self):
        """v_d >= eta deve sollevare ValueError."""
        with pytest.raises(ValueError):
            joint_concrete_compression_check(
                V_jd=500.0, eta=0.5, f_sd=17000.0, b_j=0.4, h_js=0.4, v_d=0.6
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(joint_concrete_compression_check)
        assert ref is not None
        assert ref.formula == "7.4.8"


# ── [7.4.9] — Coefficiente eta per il nodo ───────────────────────────────────


class TestJointEtaFactor:
    """NTC18 §7.4.4.3.1, Formula [7.4.9]."""

    def test_c30_interior(self):
        """a_j=0.60, f_ck=30 MPa: eta = 0.60*(1-30/250) = 0.528."""
        result = joint_eta_factor(a_j=0.60, f_ck=30.0)
        assert_allclose(result, 0.60 * (1.0 - 30.0 / 250.0), rtol=1e-3)

    def test_c25_exterior(self):
        """a_j=0.48, f_ck=25 MPa: eta = 0.48*(1-25/250) = 0.432."""
        result = joint_eta_factor(a_j=0.48, f_ck=25.0)
        assert_allclose(result, 0.48 * (1.0 - 25.0 / 250.0), rtol=1e-3)

    def test_invalid_aj_raises(self):
        with pytest.raises(ValueError):
            joint_eta_factor(a_j=0.0, f_ck=25.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(joint_eta_factor)
        assert ref is not None
        assert ref.formula == "7.4.9"


# ── [7.4.11/7.4.12] — Armatura minima orizzontale nel nodo ───────────────────


class TestJointHorizontalStirrups:
    """NTC18 §7.4.4.3.1, Formule [7.4.11] e [7.4.12]."""

    def test_interior_node(self):
        """Nodo interno: A_sh*f_ywd >= gamma_Rd*(A_s1+A_s2)*f_yd*(1-0.8*v_d)."""
        result = joint_horizontal_stirrups(
            A_s1=20e-4, A_s2=15e-4, f_yd=434e3,
            gamma_Rd=1.2, v_d=0.25, interior=True
        )
        expected = 1.2 * (20e-4 + 15e-4) * 434e3 * (1.0 - 0.8 * 0.25)
        assert_allclose(result, expected, rtol=1e-3)

    def test_exterior_node(self):
        """Nodo esterno: A_sh*f_ywd >= gamma_Rd*A_s2*f_yd*(1-0.8*v_d)."""
        result = joint_horizontal_stirrups(
            A_s1=20e-4, A_s2=15e-4, f_yd=434e3,
            gamma_Rd=1.2, v_d=0.25, interior=False
        )
        expected = 1.2 * 15e-4 * 434e3 * (1.0 - 0.8 * 0.25)
        assert_allclose(result, expected, rtol=1e-3)

    def test_vd_zero(self):
        """v_d = 0: fattore (1-0.8*0) = 1."""
        result = joint_horizontal_stirrups(
            A_s1=10e-4, A_s2=10e-4, f_yd=391e3,
            gamma_Rd=1.0, v_d=0.0
        )
        assert_allclose(result, 2 * 10e-4 * 391e3, rtol=1e-3)

    def test_invalid_vd_raises(self):
        with pytest.raises(ValueError):
            joint_horizontal_stirrups(
                A_s1=10e-4, A_s2=10e-4, f_yd=391e3,
                gamma_Rd=1.0, v_d=1.5
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(joint_horizontal_stirrups)
        assert ref is not None
        assert ref.formula == "7.4.11"


# ── [7.4.13] — Altezza zona dissipativa pareti ───────────────────────────────


class TestWallCriticalHeight:
    """NTC18 §7.4.4.5.1, Formula [7.4.13]."""

    def test_basic_6floors(self):
        """h_cr = max(l_w, h_w/6), con limite 2*l_w per n<=6 piani."""
        # l_w=4.0, h_w=18.0 -> max(4.0, 3.0) = 4.0 -> min(4.0, 8.0) = 4.0
        result = wall_critical_height(l_w=4.0, h_w=18.0, n_floors=5)
        assert_allclose(result, 4.0, rtol=1e-3)

    def test_hw_governs_6floors(self):
        """h_w/6 > l_w, con limite 2*l_w per n<=6 piani."""
        # l_w=2.0, h_w=18.0 -> max(2.0, 3.0) = 3.0 -> min(3.0, 4.0) = 3.0
        result = wall_critical_height(l_w=2.0, h_w=18.0, n_floors=6)
        assert_allclose(result, 3.0, rtol=1e-3)

    def test_cap_active_6floors(self):
        """Cap 2*l_w attivo con pochi piani."""
        # l_w=1.0, h_w=30.0 -> max(1.0, 5.0)=5.0 -> min(5.0, 2.0)=2.0
        result = wall_critical_height(l_w=1.0, h_w=30.0, n_floors=4)
        assert_allclose(result, 2.0, rtol=1e-3)

    def test_7_floors_cap_hw(self):
        """Per n>=7 piani il cap e' h_w."""
        # l_w=3.0, h_w=24.0 -> max(3.0, 4.0)=4.0 -> min(4.0, 24.0)=4.0
        result = wall_critical_height(l_w=3.0, h_w=24.0, n_floors=7)
        assert_allclose(result, 4.0, rtol=1e-3)

    def test_invalid_lw_raises(self):
        with pytest.raises(ValueError):
            wall_critical_height(l_w=0.0, h_w=18.0, n_floors=5)

    def test_ntc_ref(self):
        ref = get_ntc_ref(wall_critical_height)
        assert ref is not None
        assert ref.formula == "7.4.13"


# ── [7.4.26] — Limiti armatura tesa nelle travi sismiche ─────────────────────


class TestBeamReinforcementRatioLimits:
    """NTC18 §7.4.6.2.1, Formula [7.4.26]."""

    def test_b500_no_compression(self):
        """f_yk=500 MPa, rho_comp=0: [1.4/500, 3.5/500] = [0.0028, 0.007]."""
        rho_min, rho_max = beam_reinforcement_ratio_limits(f_yk=500.0, rho_comp=0.0)
        assert_allclose(rho_min, 1.4 / 500.0, rtol=1e-3)
        assert_allclose(rho_max, 3.5 / 500.0, rtol=1e-3)

    def test_with_compression(self):
        """rho_comp=0.005: rho_max = 0.005 + 3.5/500 = 0.012."""
        rho_min, rho_max = beam_reinforcement_ratio_limits(f_yk=500.0, rho_comp=0.005)
        assert_allclose(rho_max, 0.005 + 3.5 / 500.0, rtol=1e-3)

    def test_b450(self):
        """f_yk=450 MPa."""
        rho_min, rho_max = beam_reinforcement_ratio_limits(f_yk=450.0, rho_comp=0.0)
        assert_allclose(rho_min, 1.4 / 450.0, rtol=1e-3)
        assert_allclose(rho_max, 3.5 / 450.0, rtol=1e-3)

    def test_invalid_fyk_raises(self):
        with pytest.raises(ValueError):
            beam_reinforcement_ratio_limits(f_yk=0.0, rho_comp=0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(beam_reinforcement_ratio_limits)
        assert ref is not None
        assert ref.formula == "7.4.26"


# ── [7.4.28] — Controllo percentuale armatura pilastri ───────────────────────


class TestColumnReinforcementRatioCheck:
    """NTC18 §7.4.6.2.2, Formula [7.4.28]."""

    def test_within_limits(self):
        """rho = 0.02 (2%) -> soddisfatto."""
        satisfied, rho_min, rho_max = column_reinforcement_ratio_check(rho=0.02)
        assert satisfied is True
        assert_allclose(rho_min, 0.01, rtol=1e-6)
        assert_allclose(rho_max, 0.04, rtol=1e-6)

    def test_at_lower_limit(self):
        """rho = 0.01 esattamente."""
        satisfied, _, _ = column_reinforcement_ratio_check(rho=0.01)
        assert satisfied is True

    def test_at_upper_limit(self):
        """rho = 0.04 esattamente."""
        satisfied, _, _ = column_reinforcement_ratio_check(rho=0.04)
        assert satisfied is True

    def test_below_lower(self):
        """rho = 0.005 < 0.01 -> non soddisfatto."""
        satisfied, _, _ = column_reinforcement_ratio_check(rho=0.005)
        assert satisfied is False

    def test_above_upper(self):
        """rho = 0.05 > 0.04 -> non soddisfatto."""
        satisfied, _, _ = column_reinforcement_ratio_check(rho=0.05)
        assert satisfied is False

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            column_reinforcement_ratio_check(rho=-0.01)

    def test_ntc_ref(self):
        ref = get_ntc_ref(column_reinforcement_ratio_check)
        assert ref is not None
        assert ref.formula == "7.4.28"


# ── [7.4.29] — Confinamento pilastri ─────────────────────────────────────────


class TestColumnConfinementRequirement:
    """NTC18 §7.4.6.2.2, Formula [7.4.29]."""

    def test_basic(self):
        """Caso tipico: mu_e=9, v_d=0.3, eps_yd=0.00217, b_s=0.4, b_o=0.35, alpha=0.8."""
        result = column_confinement_requirement(
            mu_e=9.0, v_d=0.3, eps_yd=0.00217,
            b_s=0.4, b_o=0.35, alpha=0.8
        )
        demand = 30.0 * 9.0 * 0.3 * 0.00217 * (0.4 / 0.35) - 0.035
        expected = max(demand, 0.0) / 0.8
        assert_allclose(result, expected, rtol=1e-3)

    def test_low_ductility_zero_requirement(self):
        """Domanda negativa: omega_sd_min = 0."""
        result = column_confinement_requirement(
            mu_e=1.0, v_d=0.1, eps_yd=0.002, b_s=0.3, b_o=0.28, alpha=1.0
        )
        assert result >= 0.0

    def test_mu_e_less_than_one_raises(self):
        with pytest.raises(ValueError):
            column_confinement_requirement(
                mu_e=0.5, v_d=0.3, eps_yd=0.002, b_s=0.4, b_o=0.35, alpha=0.8
            )

    def test_invalid_vd_raises(self):
        with pytest.raises(ValueError):
            column_confinement_requirement(
                mu_e=9.0, v_d=0.0, eps_yd=0.002, b_s=0.4, b_o=0.35, alpha=0.8
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(column_confinement_requirement)
        assert ref is not None
        assert ref.formula == "7.4.29"


# ── [7.4.31] — Coefficiente efficacia confinamento rettangolare ───────────────


class TestConfinementEffectivenessRectangular:
    """NTC18 §7.4.6.2.2, Formule [7.4.31a] e [7.4.31b]."""

    def test_basic(self):
        """Sezione rettangolare 40x40 cm, 4 barre d16, s=10 cm."""
        # 4 distanze tra barre consecutive = 4 * 0.10 m
        b_si_list = [0.10, 0.10, 0.10, 0.10]
        b_o, h_o, s = 0.35, 0.35, 0.10

        alpha_n, alpha_s, alpha = confinement_effectiveness_rectangular(
            b_si_list=b_si_list, b_o=b_o, h_o=h_o, s=s
        )
        n = 4
        sum_bsi2 = 4 * 0.10 ** 2
        expected_alpha_n = 1.0 - sum_bsi2 / (n * 2.0 * b_o * h_o)
        expected_alpha_s = (1.0 - s / (2.0 * b_o)) * (1.0 - s / (2.0 * h_o))
        assert_allclose(alpha_n, expected_alpha_n, rtol=1e-3)
        assert_allclose(alpha_s, expected_alpha_s, rtol=1e-3)
        assert_allclose(alpha, expected_alpha_n * expected_alpha_s, rtol=1e-3)

    def test_large_spacing_formula(self):
        """Passo elevato: verifica formula [7.4.31b] con valori esatti."""
        b_si_list = [0.05]
        b_o, h_o, s = 0.20, 0.20, 0.30
        result_n, result_s, result_total = confinement_effectiveness_rectangular(
            b_si_list=b_si_list, b_o=b_o, h_o=h_o, s=s
        )
        expected_n = max(1.0 - (0.05 ** 2) / (1 * 2 * 0.20 * 0.20), 0.0)
        expected_s = max((1.0 - 0.30 / (2 * 0.20)) * (1.0 - 0.30 / (2 * 0.20)), 0.0)
        assert_allclose(result_n, expected_n, rtol=1e-3)
        assert_allclose(result_s, expected_s, rtol=1e-3)
        assert_allclose(result_total, expected_n * expected_s, rtol=1e-3)

    def test_empty_bsi_raises(self):
        with pytest.raises(ValueError):
            confinement_effectiveness_rectangular(
                b_si_list=[], b_o=0.35, h_o=0.35, s=0.10
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(confinement_effectiveness_rectangular)
        assert ref is not None
        assert ref.formula == "7.4.31"


# ── [7.4.32] — Confinamento pareti ───────────────────────────────────────────


class TestWallConfinementRequirement:
    """NTC18 §7.4.6.2.4, Formula [7.4.32]."""

    def test_basic(self):
        """Caso tipico per parete CD'A'."""
        result = wall_confinement_requirement(
            mu_k=10.0, v_g=0.2, omega_v=0.05,
            eps_yd=0.00217, b_x=0.25, b_0=0.20, alpha=0.75
        )
        demand = 30.0 * 10.0 * (0.2 + 0.05) * 0.00217 * (0.25 / 0.20) - 0.035
        expected = max(demand, 0.0) / 0.75
        assert_allclose(result, expected, rtol=1e-3)

    def test_zero_omega_v(self):
        """omega_v = 0: contributo solo da v_g."""
        result = wall_confinement_requirement(
            mu_k=8.0, v_g=0.25, omega_v=0.0,
            eps_yd=0.002, b_x=0.3, b_0=0.25, alpha=0.8
        )
        assert result >= 0.0

    def test_mu_k_less_than_one_raises(self):
        with pytest.raises(ValueError):
            wall_confinement_requirement(
                mu_k=0.5, v_g=0.2, omega_v=0.0,
                eps_yd=0.002, b_x=0.3, b_0=0.25, alpha=0.8
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(wall_confinement_requirement)
        assert ref is not None
        assert ref.formula == "7.4.32"


# ── [7.11.6]-[7.11.8] — Coefficienti sismici muri di sostegno ────────────────


class TestRetainingWallSeismicCoefficients:
    """NTC18 §7.11.6.2.1, Formule [7.11.6]-[7.11.8]."""

    def test_slv(self):
        """SLV: beta_m=0.38, a_g=0.25g, S_g=1.2, S_f=1.0."""
        k_h, k_v, a_max = retaining_wall_seismic_coefficients(
            a_g=0.25 * 9.81, S_g=1.2, S_f=1.0, beta_m=0.38
        )
        expected_amax = 1.2 * 1.0 * 0.25 * 9.81
        expected_kh = 0.38 * expected_amax / 9.81
        assert_allclose(a_max, expected_amax, rtol=1e-3)
        assert_allclose(k_h, expected_kh, rtol=1e-3)
        assert_allclose(k_v, 0.5 * expected_kh, rtol=1e-3)

    def test_sld(self):
        """SLD: beta_m=0.47."""
        k_h, k_v, a_max = retaining_wall_seismic_coefficients(
            a_g=0.15 * 9.81, S_g=1.3, S_f=1.0, beta_m=0.47
        )
        expected_amax = 1.3 * 1.0 * 0.15 * 9.81
        assert_allclose(a_max, expected_amax, rtol=1e-3)
        assert_allclose(k_v, 0.5 * k_h, rtol=1e-3)

    def test_fixed_wall_beta1(self):
        """Muro non libero di spostarsi: beta_m=1.0."""
        k_h, k_v, a_max = retaining_wall_seismic_coefficients(
            a_g=0.20 * 9.81, S_g=1.0, S_f=1.0, beta_m=1.0
        )
        assert_allclose(k_h, 0.20, rtol=1e-3)

    def test_a_g_negative_raises(self):
        with pytest.raises(ValueError):
            retaining_wall_seismic_coefficients(
                a_g=-0.1, S_g=1.2, S_f=1.0, beta_m=0.38
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(retaining_wall_seismic_coefficients)
        assert ref is not None
        assert ref.formula == "7.11.6"


# ── [7.11.9] — Accelerazione pseudostatica per paratie ───────────────────────


class TestSheetPilePseudostaticAcceleration:
    """NTC18 §7.11.6.3.1, Formula [7.11.9]."""

    def test_basic(self):
        """alpha=0.8, beta=0.5, a_max=2.5 m/s^2."""
        a_h, k_h = sheet_pile_pseudostatic_acceleration(
            alpha=0.8, beta=0.5, a_max=2.5
        )
        # alpha*beta = 0.4 > 0.2, quindi k_h = 0.4 * 2.5 / 9.81
        assert_allclose(k_h, 0.4 * 2.5 / 9.81, rtol=1e-3)
        assert_allclose(a_h, k_h * 9.81, rtol=1e-3)

    def test_minimum_kh_rule(self):
        """alpha*beta <= 0.2: k_h = max(alpha*beta*a_max/g, 0.2*a_max/g)."""
        # alpha*beta = 0.1 <= 0.2 -> k_h = 0.2*a_max/g
        a_h, k_h = sheet_pile_pseudostatic_acceleration(
            alpha=0.2, beta=0.5, a_max=3.0
        )
        assert_allclose(k_h, 0.2 * 3.0 / 9.81, rtol=1e-3)

    def test_alpha_one_beta_one(self):
        """alpha=1, beta=1: a_h = a_max."""
        a_h, k_h = sheet_pile_pseudostatic_acceleration(
            alpha=1.0, beta=1.0, a_max=2.0
        )
        assert_allclose(a_h, 2.0, rtol=1e-3)

    def test_invalid_alpha_raises(self):
        with pytest.raises(ValueError):
            sheet_pile_pseudostatic_acceleration(alpha=1.5, beta=0.5, a_max=2.5)

    def test_ntc_ref(self):
        ref = get_ntc_ref(sheet_pile_pseudostatic_acceleration)
        assert ref is not None
        assert ref.formula == "7.11.9"


# ── [7.11.11] — Limite spostamento paratia ───────────────────────────────────


class TestSheetPileDisplacementLimit:
    """NTC18 §7.11.6.3.1, Formula [7.11.11]."""

    def test_basic(self):
        """H=10 m: u_s_max = 0.005*10 = 0.05 m."""
        result = sheet_pile_displacement_limit(H=10.0)
        assert_allclose(result, 0.05, rtol=1e-6)

    def test_larger_wall(self):
        """H=20 m: u_s_max = 0.005*20 = 0.10 m."""
        result = sheet_pile_displacement_limit(H=20.0)
        assert_allclose(result, 0.10, rtol=1e-6)

    def test_invalid_H_raises(self):
        with pytest.raises(ValueError):
            sheet_pile_displacement_limit(H=0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(sheet_pile_displacement_limit)
        assert ref is not None
        assert ref.formula == "7.11.11"


# ── [7.11.12] — Lunghezza libera ancoraggio sismica ──────────────────────────


class TestAnchorFreeLengthSeismic:
    """NTC18 §7.11.6.4, Formula [7.11.12]."""

    def test_basic(self):
        """L_s=5.0 m, a_max=0.3g: L_q,i = 5.0*(1+1.5*0.3) = 7.25 m."""
        result = anchor_free_length_seismic(L_s=5.0, a_max=0.3 * 9.81)
        expected = 5.0 * (1.0 + 1.5 * 0.3)
        assert_allclose(result, expected, rtol=1e-3)

    def test_zero_acceleration(self):
        """a_max=0: L_q,i = L_s."""
        result = anchor_free_length_seismic(L_s=4.0, a_max=0.0)
        assert_allclose(result, 4.0, rtol=1e-6)

    def test_high_acceleration(self):
        """a_max=0.5g: L_q,i = L_s*(1+1.5*0.5) = 1.75*L_s."""
        L_s = 6.0
        result = anchor_free_length_seismic(L_s=L_s, a_max=0.5 * 9.81)
        assert_allclose(result, 1.75 * L_s, rtol=1e-3)

    def test_invalid_Ls_raises(self):
        with pytest.raises(ValueError):
            anchor_free_length_seismic(L_s=0.0, a_max=2.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(anchor_free_length_seismic)
        assert ref is not None
        assert ref.formula == "7.11.12"
