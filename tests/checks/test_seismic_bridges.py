"""Test per seismic_bridges — NTC18 §7.9."""

import math

import pytest
import numpy as np
from numpy.testing import assert_allclose

from pyntc.checks.seismic_bridges import (
    bridge_behavior_factor_vk,
    bridge_confinement_check_circular,
    bridge_confinement_check_rectangular,
    bridge_confinement_omega_circular,
    bridge_confinement_omega_rectangular,
    bridge_confinement_omega_req,
    bridge_confinement_spacing_transverse,
    bridge_confinement_spacing_vertical,
    bridge_deck_capacity_shear,
    bridge_end_stop_force,
    bridge_overstrength_factor,
    bridge_overlap_length,
    bridge_period_multispan,
    bridge_period_single_mass,
    bridge_pier_capacity_shear,
    bridge_pier_design_shear,
    bridge_pier_shear_overstrength,
    bridge_regularity_factor,
    bridge_seismic_forces_multispan,
    bridge_tie_spacing_longitudinal,
)
from pyntc.core.reference import get_ntc_ref


# ── [7.9.1] — Fattore di comportamento ridotto per v_k ───────────────────────


class TestBridgeBehaviorFactorVk:
    """NTC18 §7.9.2.1, Formula [7.9.1]."""

    def test_vk_below_threshold_returns_qi(self):
        """v_k <= 0.3: q_i(v_k) = q_i invariato."""
        result = bridge_behavior_factor_vk(q_i=3.5, v_k=0.2)
        assert_allclose(result, 3.5, rtol=1e-6)

    def test_vk_equal_threshold_returns_qi(self):
        """v_k = 0.3: q_i(v_k) = q_i (nessuna riduzione)."""
        result = bridge_behavior_factor_vk(q_i=3.5, v_k=0.3)
        assert_allclose(result, 3.5, rtol=1e-6)

    def test_vk_above_threshold_reduces_q(self):
        """v_k = 0.45: q_i(v_k) = 3.5 - [0.45/0.3 - 1]*(3.5 - 1) = 3.5 - 0.5*2.5 = 2.25."""
        result = bridge_behavior_factor_vk(q_i=3.5, v_k=0.45)
        expected = 3.5 - (0.45 / 0.3 - 1.0) * (3.5 - 1.0)
        assert_allclose(result, expected, rtol=1e-6)

    def test_vk_max_value(self):
        """v_k = 0.6: q_i(v_k) = q_i - 1*(q_i - 1) = 1.0."""
        result = bridge_behavior_factor_vk(q_i=3.5, v_k=0.6)
        expected = 3.5 - (0.6 / 0.3 - 1.0) * (3.5 - 1.0)
        assert_allclose(result, expected, rtol=1e-6)
        assert result >= 1.0

    def test_qi_equals_1_no_reduction(self):
        """Se q_i = 1.0, q_i(v_k) = 1.0 per qualsiasi v_k."""
        result = bridge_behavior_factor_vk(q_i=1.0, v_k=0.5)
        assert_allclose(result, 1.0, rtol=1e-6)

    def test_vk_exceeds_max_raises(self):
        with pytest.raises(ValueError, match="0,6"):
            bridge_behavior_factor_vk(q_i=3.5, v_k=0.7)

    def test_vk_negative_raises(self):
        with pytest.raises(ValueError):
            bridge_behavior_factor_vk(q_i=3.5, v_k=-0.1)

    def test_qi_less_than_1_raises(self):
        with pytest.raises(ValueError):
            bridge_behavior_factor_vk(q_i=0.5, v_k=0.2)

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_behavior_factor_vk)
        assert ref is not None
        assert ref.article == "7.9.2.1"
        assert ref.formula == "7.9.1"


# ── [7.9.2] — Fattore di regolarita' K_R ──────────────────────────────────


class TestBridgeRegularityFactor:
    """NTC18 §7.9.2.1, Formula [7.9.2]."""

    def test_regular_bridge_r_bar_less_than_2(self):
        """r_bar < 2: K_R = 1.0 (ponte regolare)."""
        r_bar, K_R = bridge_regularity_factor(r_max=1.8, r_min=1.0)
        assert_allclose(r_bar, 1.8, rtol=1e-6)
        assert_allclose(K_R, 1.0, rtol=1e-6)

    def test_regular_bridge_boundary(self):
        """r_bar = 2.0 esattamente: irregolare, K_R = 2/2 = 1.0."""
        r_bar, K_R = bridge_regularity_factor(r_max=2.0, r_min=1.0)
        assert_allclose(r_bar, 2.0, rtol=1e-6)
        assert_allclose(K_R, 1.0, rtol=1e-6)

    def test_irregular_bridge(self):
        """r_bar = 3.0: K_R = 2/3 = 0.6667."""
        r_bar, K_R = bridge_regularity_factor(r_max=3.0, r_min=1.0)
        assert_allclose(r_bar, 3.0, rtol=1e-6)
        assert_allclose(K_R, 2.0 / 3.0, rtol=1e-6)

    def test_irregular_bridge_r_max_4(self):
        """r_bar = 4.0: K_R = 2/4 = 0.5."""
        r_bar, K_R = bridge_regularity_factor(r_max=4.0, r_min=1.0)
        assert_allclose(K_R, 0.5, rtol=1e-6)

    def test_uniform_piers(self):
        """Pile uniformi: r_max = r_min -> r_bar = 1.0 -> regolare."""
        r_bar, K_R = bridge_regularity_factor(r_max=1.5, r_min=1.5)
        assert_allclose(r_bar, 1.0, rtol=1e-6)
        assert_allclose(K_R, 1.0, rtol=1e-6)

    def test_r_min_zero_raises(self):
        with pytest.raises(ValueError):
            bridge_regularity_factor(r_max=2.0, r_min=0.0)

    def test_r_max_less_than_r_min_raises(self):
        with pytest.raises(ValueError):
            bridge_regularity_factor(r_max=0.5, r_min=1.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_regularity_factor)
        assert ref is not None
        assert ref.article == "7.9.2.1"
        assert ref.formula == "7.9.2"


# ── [7.9.4] — Periodo fondamentale a massa singola ──────────────────────────


class TestBridgePeriodSingleMass:
    """NTC18 §7.9.4.1, Formula [7.9.4]."""

    def test_basic(self):
        """T_1 = 2*pi*sqrt(M/K): M=1000 kN*s^2/m, K=10000 kN/m."""
        M = 1000.0 / 9.81  # [kN*s^2/m]
        K = 10000.0        # [kN/m]
        result = bridge_period_single_mass(M=M, K=K)
        expected = 2.0 * math.pi * math.sqrt(M / K)
        assert_allclose(result, expected, rtol=1e-6)

    def test_rigid_pier(self):
        """K molto grande -> T ~ 0."""
        M = 500.0 / 9.81
        K = 1e8
        result = bridge_period_single_mass(M=M, K=K)
        assert result < 0.01

    def test_flexible_pier(self):
        """K piccola -> T piu' grande."""
        M = 5000.0 / 9.81
        K = 500.0
        result = bridge_period_single_mass(M=M, K=K)
        expected = 2.0 * math.pi * math.sqrt(M / K)
        assert_allclose(result, expected, rtol=1e-6)
        assert result > 1.0

    def test_M_zero_raises(self):
        with pytest.raises(ValueError):
            bridge_period_single_mass(M=0.0, K=1000.0)

    def test_K_zero_raises(self):
        with pytest.raises(ValueError):
            bridge_period_single_mass(M=100.0, K=0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_period_single_mass)
        assert ref is not None
        assert ref.article == "7.9.4.1"
        assert ref.formula == "7.9.4"


# ── [7.9.6] — Periodo fondamentale multispan ─────────────────────────────────


class TestBridgePeriodMultispan:
    """NTC18 §7.9.4.1, Formula [7.9.6]."""

    def test_single_span(self):
        """Singola campata: T_1 = 2*pi*sqrt(d/g)."""
        G = np.array([1000.0])
        d = np.array([0.01])
        result = bridge_period_multispan(weights=G, displacements=d)
        # sum(G*d^2)/(g*sum(G*d)) = d/g
        expected = 2.0 * math.pi * math.sqrt(0.01 / 9.81)
        assert_allclose(result, expected, rtol=1e-6)

    def test_uniform_piers(self):
        """Pile uniformi (stessi G e d): T_1 = 2*pi*sqrt(d_i/g)."""
        G = np.array([1000.0, 1000.0, 1000.0])
        d = np.array([0.02, 0.02, 0.02])
        result = bridge_period_multispan(weights=G, displacements=d)
        expected = 2.0 * math.pi * math.sqrt(0.02 / 9.81)
        assert_allclose(result, expected, rtol=1e-6)

    def test_multispan_formula(self):
        """Verifica formula diretta con valori noti."""
        G = np.array([500.0, 800.0, 600.0])
        d = np.array([0.015, 0.025, 0.020])
        result = bridge_period_multispan(weights=G, displacements=d)
        num = float(np.sum(G * d**2))
        den = 9.81 * float(np.sum(G * d))
        expected = 2.0 * math.pi * math.sqrt(num / den)
        assert_allclose(result, expected, rtol=1e-6)

    def test_mismatch_raises(self):
        with pytest.raises(ValueError):
            bridge_period_multispan(
                weights=np.array([1000.0, 1000.0]),
                displacements=np.array([0.01]),
            )

    def test_zero_displacements_raises(self):
        with pytest.raises(ValueError):
            bridge_period_multispan(
                weights=np.array([1000.0]),
                displacements=np.array([0.0]),
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_period_multispan)
        assert ref is not None
        assert ref.article == "7.9.4.1"
        assert ref.formula == "7.9.6"


# ── [7.9.5] — Forze sismiche multispan ───────────────────────────────────────


class TestBridgeSeismicForcesMultispan:
    """NTC18 §7.9.4.1, Formula [7.9.5]."""

    def test_basic(self):
        """F_i = 4*pi^2*S_d/T^2/g^2 * d_i * G_i."""
        S_d = 0.3 * 9.81
        T_1 = 0.8
        G = np.array([1000.0, 1500.0])
        d = np.array([0.02, 0.03])
        result = bridge_seismic_forces_multispan(
            S_d_T1=S_d, T_1=T_1, weights=G, displacements=d
        )
        coeff = 4.0 * math.pi**2 * S_d / (T_1**2 * 9.81**2)
        expected = coeff * d * G
        assert_allclose(result, expected, rtol=1e-6)

    def test_proportional_to_d_and_G(self):
        """Le forze sono proporzionali a d_i * G_i."""
        S_d = 0.25 * 9.81
        T_1 = 1.0
        G = np.array([1000.0, 2000.0])
        d = np.array([0.01, 0.02])
        result = bridge_seismic_forces_multispan(
            S_d_T1=S_d, T_1=T_1, weights=G, displacements=d
        )
        # F_0/F_1 = (d_0*G_0)/(d_1*G_1) = (0.01*1000)/(0.02*2000) = 0.25
        assert_allclose(result[0] / result[1], 0.25, rtol=1e-6)

    def test_T1_zero_raises(self):
        with pytest.raises(ValueError):
            bridge_seismic_forces_multispan(
                S_d_T1=2.0,
                T_1=0.0,
                weights=np.array([1000.0]),
                displacements=np.array([0.01]),
            )

    def test_mismatch_raises(self):
        with pytest.raises(ValueError):
            bridge_seismic_forces_multispan(
                S_d_T1=2.0,
                T_1=0.5,
                weights=np.array([1000.0, 2000.0]),
                displacements=np.array([0.01]),
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_seismic_forces_multispan)
        assert ref is not None
        assert ref.article == "7.9.4.1"
        assert ref.formula == "7.9.5"


# ── [7.9.7] — Fattore di sovraresistenza ─────────────────────────────────────


class TestBridgeOverstrengthFactor:
    """NTC18 §7.9.5, Formula [7.9.7]."""

    def test_q_15(self):
        """q = 1.5: gamma_id = 0.7 + 0.2*1.5 = 1.0."""
        result = bridge_overstrength_factor(q=1.5)
        assert_allclose(result, 1.0, rtol=1e-6)

    def test_q_35(self):
        """q = 3.5: gamma_id = 0.7 + 0.2*3.5 = 1.4."""
        result = bridge_overstrength_factor(q=3.5)
        assert_allclose(result, 1.4, rtol=1e-6)

    def test_clamped_to_1(self):
        """q = 1.0: 0.7 + 0.2*1 = 0.9 -> clampato a 1.0."""
        result = bridge_overstrength_factor(q=1.0)
        assert_allclose(result, 1.0, rtol=1e-6)

    def test_vk_amplification(self):
        """v_k = 0.2 > 0.1: gamma *= 1 + 2*(0.2-0.1)^2 = 1.002."""
        gamma_base = bridge_overstrength_factor(q=3.5, v_k=0.0)
        gamma_vk = bridge_overstrength_factor(q=3.5, v_k=0.2)
        factor = 1.0 + 2.0 * (0.2 - 0.1) ** 2
        assert_allclose(gamma_vk, gamma_base * factor, rtol=1e-6)

    def test_vk_below_threshold_no_amplification(self):
        """v_k = 0.1: nessuna amplificazione (soglia non superata)."""
        gamma_0 = bridge_overstrength_factor(q=3.5, v_k=0.0)
        gamma_01 = bridge_overstrength_factor(q=3.5, v_k=0.1)
        assert_allclose(gamma_0, gamma_01, rtol=1e-6)

    def test_q_less_than_1_raises(self):
        with pytest.raises(ValueError):
            bridge_overstrength_factor(q=0.5)

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_overstrength_factor)
        assert ref is not None
        assert ref.article == "7.9.5"
        assert ref.formula == "7.9.7"


# ── [7.9.10b] — Taglio di capacita' pila ─────────────────────────────────────


class TestBridgePierCapacityShear:
    """NTC18 §7.9.5.1.1, Formula [7.9.10b]."""

    def test_basic(self):
        """V_prc = (M_lpec + M_lprc) / l_p = (300 + 400) / 10 = 70 kN."""
        result = bridge_pier_capacity_shear(M_lpec=300.0, M_lprc=400.0, l_p=10.0)
        assert_allclose(result, 70.0, rtol=1e-6)

    def test_cantilever_pier(self):
        """Pila a mensola: M_lpec = 0 (nodo libero in sommita')."""
        result = bridge_pier_capacity_shear(M_lpec=0.0, M_lprc=500.0, l_p=8.0)
        assert_allclose(result, 62.5, rtol=1e-6)

    def test_l_p_zero_raises(self):
        with pytest.raises(ValueError):
            bridge_pier_capacity_shear(M_lpec=300.0, M_lprc=400.0, l_p=0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_pier_capacity_shear)
        assert ref is not None
        assert ref.article == "7.9.5.1.1"
        assert ref.formula == "7.9.10b"


# ── [7.9.11] — Fattore gamma_bd per taglio pila ──────────────────────────────


class TestBridgePierShearOverstrength:
    """NTC18 §7.9.5.1.1, Formula [7.9.11]."""

    def test_clamped_upper(self):
        """gamma_bd calcolato > 1.25: clampato a 1.25."""
        # gamma = 2.25 - q*(V_E/V_prc): con q=1.5, V_E/V_prc=0.1 -> 2.25-0.15=2.10 > 1.25
        result = bridge_pier_shear_overstrength(q=1.5, V_E=100.0, V_prc=1000.0)
        assert_allclose(result, 1.25, rtol=1e-6)

    def test_clamped_lower(self):
        """gamma_bd calcolato < 1.0: clampato a 1.0."""
        # q=3.5, V_E/V_prc=1.0: gamma = 2.25 - 3.5 = -1.25 -> clamp 1.0
        result = bridge_pier_shear_overstrength(q=3.5, V_E=1000.0, V_prc=1000.0)
        assert_allclose(result, 1.0, rtol=1e-6)

    def test_intermediate_value(self):
        """Valore intermedio: gamma = 2.25 - q*(V_E/V_prc)."""
        q = 2.0
        V_E = 500.0
        V_prc = 1000.0
        expected = max(1.0, min(2.25 - q * (V_E / V_prc), 1.25))
        result = bridge_pier_shear_overstrength(q=q, V_E=V_E, V_prc=V_prc)
        assert_allclose(result, expected, rtol=1e-6)

    def test_q_less_than_1_raises(self):
        with pytest.raises(ValueError):
            bridge_pier_shear_overstrength(q=0.5, V_E=100.0, V_prc=200.0)

    def test_V_prc_zero_raises(self):
        with pytest.raises(ValueError):
            bridge_pier_shear_overstrength(q=2.0, V_E=100.0, V_prc=0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_pier_shear_overstrength)
        assert ref is not None
        assert ref.article == "7.9.5.1.1"
        assert ref.formula == "7.9.11"


# ── [7.9.10a] — Domanda di taglio amplificata ────────────────────────────────


class TestBridgePierDesignShear:
    """NTC18 §7.9.5.1.1, Formula [7.9.10a]."""

    def test_basic(self):
        """V_Ed = gamma_bd * V_prc = 1.1 * 80 = 88 kN."""
        result = bridge_pier_design_shear(gamma_bd=1.1, V_prc=80.0)
        assert_allclose(result, 88.0, rtol=1e-6)

    def test_gamma_bd_1(self):
        """gamma_bd = 1.0: V_Ed = V_prc."""
        result = bridge_pier_design_shear(gamma_bd=1.0, V_prc=150.0)
        assert_allclose(result, 150.0, rtol=1e-6)

    def test_gamma_bd_less_than_1_raises(self):
        with pytest.raises(ValueError):
            bridge_pier_design_shear(gamma_bd=0.9, V_prc=100.0)

    def test_V_prc_zero_raises(self):
        with pytest.raises(ValueError):
            bridge_pier_design_shear(gamma_bd=1.1, V_prc=0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_pier_design_shear)
        assert ref is not None
        assert ref.article == "7.9.5.1.1"
        assert ref.formula == "7.9.10a"


# ── [7.9.12] — Taglio impalcato in direzione trasversale ─────────────────────


class TestBridgeDeckCapacityShear:
    """NTC18 §7.9.5.2.1, Formula [7.9.12]."""

    def test_basic(self):
        """V_Ed = V_E * gamma_bd * M_lprc / M_Rd <= V_E * q."""
        V_E = 100.0
        gamma_bd = 1.2
        M_lprc = 500.0
        M_Rd = 500.0
        q = 3.5
        V_Ed, V_max = bridge_deck_capacity_shear(
            V_E_i=V_E, gamma_bd=gamma_bd, M_lprc_i=M_lprc, M_Rd_base=M_Rd, q=q
        )
        assert_allclose(V_Ed, 120.0, rtol=1e-6)
        assert_allclose(V_max, 350.0, rtol=1e-6)

    def test_capped_by_q(self):
        """V_Ed_raw > V_E*q: si usa il limite superiore."""
        V_E = 100.0
        gamma_bd = 1.25
        M_lprc = 600.0
        M_Rd = 100.0  # rapporto M_lprc/M_Rd = 6 -> V_Ed_raw = 100*1.25*6=750
        q = 3.5        # limite = 350
        V_Ed, V_max = bridge_deck_capacity_shear(
            V_E_i=V_E, gamma_bd=gamma_bd, M_lprc_i=M_lprc, M_Rd_base=M_Rd, q=q
        )
        assert_allclose(V_max, 350.0, rtol=1e-6)
        assert_allclose(V_Ed, 350.0, rtol=1e-6)

    def test_V_E_zero(self):
        """V_E = 0: V_Ed = 0."""
        V_Ed, V_max = bridge_deck_capacity_shear(
            V_E_i=0.0, gamma_bd=1.2, M_lprc_i=500.0, M_Rd_base=500.0, q=3.5
        )
        assert_allclose(V_Ed, 0.0, atol=1e-10)
        assert_allclose(V_max, 0.0, atol=1e-10)

    def test_M_Rd_zero_raises(self):
        with pytest.raises(ValueError):
            bridge_deck_capacity_shear(
                V_E_i=100.0, gamma_bd=1.2, M_lprc_i=500.0, M_Rd_base=0.0, q=3.5
            )

    def test_q_less_than_1_raises(self):
        with pytest.raises(ValueError):
            bridge_deck_capacity_shear(
                V_E_i=100.0, gamma_bd=1.2, M_lprc_i=500.0, M_Rd_base=500.0, q=0.5
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_deck_capacity_shear)
        assert ref is not None
        assert ref.article == "7.9.5.2.1"
        assert ref.formula == "7.9.12"


# ── §7.9.5.3.3 — Forza dispositivi di fine corsa ─────────────────────────────


class TestBridgeEndStopForce:
    """NTC18 §7.9.5.3.3."""

    def test_basic(self):
        """F_fc = 1.5*S*a_0/g * Q = 1.5*1.2*0.25*9.81/9.81 * 500 = 225 kN."""
        S = 1.2
        a_0 = 0.25 * 9.81
        Q = 500.0
        result = bridge_end_stop_force(S=S, a_0=a_0, Q=Q)
        expected = 1.5 * S * a_0 / 9.81 * Q
        assert_allclose(result, expected, rtol=1e-6)

    def test_zero_acceleration(self):
        """a_0 = 0: F_fc = 0."""
        result = bridge_end_stop_force(S=1.2, a_0=0.0, Q=500.0)
        assert_allclose(result, 0.0, atol=1e-10)

    def test_zero_Q(self):
        """Q = 0: F_fc = 0."""
        result = bridge_end_stop_force(S=1.2, a_0=0.25 * 9.81, Q=0.0)
        assert_allclose(result, 0.0, atol=1e-10)

    def test_Q_negative_raises(self):
        with pytest.raises(ValueError):
            bridge_end_stop_force(S=1.2, a_0=0.25, Q=-100.0)

    def test_a_0_negative_raises(self):
        with pytest.raises(ValueError):
            bridge_end_stop_force(S=1.2, a_0=-0.1, Q=500.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_end_stop_force)
        assert ref is not None
        assert ref.article == "7.9.5.3.3"


# ── §7.9.5.3.4 — Lunghezza zona di sovrapposizione ───────────────────────────


class TestBridgeOverlapLength:
    """NTC18 §7.9.5.3.4."""

    def test_basic(self):
        """l_ov = d_rel + 0.400 = 0.15 + 0.4 = 0.55 m."""
        result = bridge_overlap_length(d_rel=0.15)
        assert_allclose(result, 0.55, rtol=1e-6)

    def test_minimum_400mm(self):
        """d_rel = 0: l_ov = 0.400 m (solo spazio appoggio)."""
        result = bridge_overlap_length(d_rel=0.0)
        assert_allclose(result, 0.400, rtol=1e-6)

    def test_large_displacement(self):
        """d_rel = 0.5 m: l_ov = 0.9 m."""
        result = bridge_overlap_length(d_rel=0.5)
        assert_allclose(result, 0.9, rtol=1e-6)

    def test_negative_d_rel_raises(self):
        with pytest.raises(ValueError):
            bridge_overlap_length(d_rel=-0.1)

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_overlap_length)
        assert ref is not None
        assert ref.article == "7.9.5.3.4"


# ── [7.9.16] — omega_w,req confinamento ───────────────────────────────────────


class TestBridgeConfinementOmegaReq:
    """NTC18 §7.9.6.1.2, Formula [7.9.16]."""

    def test_cda_basic(self):
        """CD'A': lambda=0.37, verifica formula diretta."""
        A_wc = 0.10
        A_ec = 0.08
        v_k = 0.4
        lambda_cd = 0.37
        f_sd = 391.0
        f_od = 16.67
        rho_L1 = 0.02
        result = bridge_confinement_omega_req(
            A_wc=A_wc, A_ec=A_ec, v_k=v_k, lambda_cd=lambda_cd,
            f_sd=f_sd, f_od=f_od, rho_L1=rho_L1
        )
        expected = (A_wc / A_ec) * lambda_cd * v_k + 0.13 * (f_sd / f_od) * (rho_L1 - 0.01)
        assert_allclose(result, expected, rtol=1e-6)

    def test_cdb_basic(self):
        """CD'B': lambda=0.28."""
        result = bridge_confinement_omega_req(
            A_wc=0.10, A_ec=0.08, v_k=0.3, lambda_cd=0.28,
            f_sd=391.0, f_od=16.67, rho_L1=0.015
        )
        expected = (0.10 / 0.08) * 0.28 * 0.3 + 0.13 * (391.0 / 16.67) * (0.015 - 0.01)
        assert_allclose(result, expected, rtol=1e-6)

    def test_invalid_lambda_raises(self):
        with pytest.raises(ValueError, match="lambda_cd"):
            bridge_confinement_omega_req(
                A_wc=0.10, A_ec=0.08, v_k=0.3, lambda_cd=0.30,
                f_sd=391.0, f_od=16.67, rho_L1=0.015
            )

    def test_A_ec_zero_raises(self):
        with pytest.raises(ValueError):
            bridge_confinement_omega_req(
                A_wc=0.10, A_ec=0.0, v_k=0.3, lambda_cd=0.37,
                f_sd=391.0, f_od=16.67, rho_L1=0.015
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_confinement_omega_req)
        assert ref is not None
        assert ref.article == "7.9.6.1.2"
        assert ref.formula == "7.9.16"


# ── [7.9.15] — Verifica confinamento rettangolare ────────────────────────────


class TestBridgeConfinementCheckRectangular:
    """NTC18 §7.9.6.1.2, Formula [7.9.15]."""

    def test_satisfied_cda(self):
        """CD'A': omega_wd_t >= max(omega_w_req; 0.67*0.18)."""
        omega_w_req = 0.08
        demand = max(omega_w_req, 0.67 * 0.18)
        satisfied, d = bridge_confinement_check_rectangular(
            omega_wd_t=demand + 0.01,
            omega_w_req=omega_w_req,
            ductility_class="A",
        )
        assert satisfied is True
        assert_allclose(d, demand, rtol=1e-6)

    def test_not_satisfied_cdb(self):
        """CD'B': omega_wd_t < max(omega_w_req; 0.67*0.12)."""
        omega_w_req = 0.05
        demand = max(omega_w_req, 0.67 * 0.12)
        satisfied, d = bridge_confinement_check_rectangular(
            omega_wd_t=demand - 0.01,
            omega_w_req=omega_w_req,
            ductility_class="B",
        )
        assert satisfied is False

    def test_exact_boundary_satisfied(self):
        """omega_wd_t = demand esattamente: satisfied."""
        omega_w_req = 0.10
        demand = max(omega_w_req, 0.67 * 0.18)
        satisfied, d = bridge_confinement_check_rectangular(
            omega_wd_t=demand, omega_w_req=omega_w_req, ductility_class="A"
        )
        assert satisfied is True

    def test_invalid_class_raises(self):
        with pytest.raises(ValueError):
            bridge_confinement_check_rectangular(
                omega_wd_t=0.15, omega_w_req=0.10, ductility_class="C"
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_confinement_check_rectangular)
        assert ref is not None
        assert ref.article == "7.9.6.1.2"
        assert ref.formula == "7.9.15"


# ── [7.9.17] — Verifica confinamento circolare ────────────────────────────────


class TestBridgeConfinementCheckCircular:
    """NTC18 §7.9.6.1.2, Formula [7.9.17]."""

    def test_satisfied_cda(self):
        """CD'A': omega_wd_c >= max(1.4*omega_w_req; omega_w_min=0.18)."""
        omega_w_req = 0.15
        demand = max(1.4 * omega_w_req, 0.18)
        satisfied, d = bridge_confinement_check_circular(
            omega_wd_c=demand + 0.01,
            omega_w_req=omega_w_req,
            ductility_class="A",
        )
        assert satisfied is True
        assert_allclose(d, demand, rtol=1e-6)

    def test_not_satisfied_cdb(self):
        """CD'B': omega_wd_c < max(1.4*omega_w_req; 0.12)."""
        omega_w_req = 0.05
        demand = max(1.4 * omega_w_req, 0.12)
        satisfied, d = bridge_confinement_check_circular(
            omega_wd_c=0.05, omega_w_req=omega_w_req, ductility_class="B"
        )
        assert satisfied is False

    def test_invalid_class_raises(self):
        with pytest.raises(ValueError):
            bridge_confinement_check_circular(
                omega_wd_c=0.20, omega_w_req=0.10, ductility_class="X"
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_confinement_check_circular)
        assert ref is not None
        assert ref.article == "7.9.6.1.2"
        assert ref.formula == "7.9.17"


# ── [7.9.18] — omega_wd,t sezioni rettangolari ───────────────────────────────


class TestBridgeConfinementOmegaRectangular:
    """NTC18 §7.9.6.1.2, Formula [7.9.18]."""

    def test_basic(self):
        """omega_wd_t = (A_wc / (s*b)) * (f_sd/f_od)."""
        A_wc = 2 * 78.5  # 2 bracci d10 [mm^2]
        s = 100.0         # passo [mm]
        b = 400.0         # larghezza nucleo [mm]
        f_sd = 391.0      # [MPa]
        f_od = 16.67      # [MPa]
        result = bridge_confinement_omega_rectangular(
            A_wc=A_wc, s=s, b=b, f_sd=f_sd, f_od=f_od
        )
        expected = (A_wc / (s * b)) * (f_sd / f_od)
        assert_allclose(result, expected, rtol=1e-6)

    def test_s_zero_raises(self):
        with pytest.raises(ValueError):
            bridge_confinement_omega_rectangular(
                A_wc=157.0, s=0.0, b=400.0, f_sd=391.0, f_od=16.67
            )

    def test_b_zero_raises(self):
        with pytest.raises(ValueError):
            bridge_confinement_omega_rectangular(
                A_wc=157.0, s=100.0, b=0.0, f_sd=391.0, f_od=16.67
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_confinement_omega_rectangular)
        assert ref is not None
        assert ref.article == "7.9.6.1.2"
        assert ref.formula == "7.9.18"


# ── [7.9.19] — omega_wd,c sezioni circolari ───────────────────────────────────


class TestBridgeConfinementOmegaCircular:
    """NTC18 §7.9.6.1.2, Formula [7.9.19]."""

    def test_basic(self):
        """omega_wd_c = 4*A_ep*f_yd/(D_sp*s*f_el)."""
        A_ep = 78.5        # d10 [mm^2]
        D_sp = 600.0       # diametro nucleo [mm]
        s = 100.0          # passo [mm]
        f_yd = 391.0       # [MPa]
        f_el = 16.67       # [MPa]
        result = bridge_confinement_omega_circular(
            A_ep=A_ep, D_sp=D_sp, s=s, f_yd=f_yd, f_el=f_el
        )
        expected = 4.0 * A_ep * f_yd / (D_sp * s * f_el)
        assert_allclose(result, expected, rtol=1e-6)

    def test_D_sp_zero_raises(self):
        with pytest.raises(ValueError):
            bridge_confinement_omega_circular(
                A_ep=78.5, D_sp=0.0, s=100.0, f_yd=391.0, f_el=16.67
            )

    def test_s_zero_raises(self):
        with pytest.raises(ValueError):
            bridge_confinement_omega_circular(
                A_ep=78.5, D_sp=600.0, s=0.0, f_yd=391.0, f_el=16.67
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_confinement_omega_circular)
        assert ref is not None
        assert ref.article == "7.9.6.1.2"
        assert ref.formula == "7.9.19"


# ── [7.9.20] — Passo verticale confinamento ───────────────────────────────────


class TestBridgeConfinementSpacingVertical:
    """NTC18 §7.9.6.1.2, Formula [7.9.20]."""

    def test_limited_by_d_SL(self):
        """min(6*d_SL; 1.5*b_star): 6*20=120 < 1.5*500=750 -> 120."""
        result = bridge_confinement_spacing_vertical(d_SL=20.0, b_star=500.0)
        assert_allclose(result, 120.0, rtol=1e-6)

    def test_limited_by_b_star(self):
        """min(6*d_SL; 1.5*b_star): 6*30=180 > 1.5*100=150 -> 150."""
        result = bridge_confinement_spacing_vertical(d_SL=30.0, b_star=100.0)
        assert_allclose(result, 150.0, rtol=1e-6)

    def test_d_SL_zero_raises(self):
        with pytest.raises(ValueError):
            bridge_confinement_spacing_vertical(d_SL=0.0, b_star=300.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_confinement_spacing_vertical)
        assert ref is not None
        assert ref.article == "7.9.6.1.2"
        assert ref.formula == "7.9.20"


# ── [7.9.21] — Passo trasversale confinamento ─────────────────────────────────


class TestBridgeConfinementSpacingTransverse:
    """NTC18 §7.9.6.1.2, Formula [7.9.21]."""

    def test_limited_by_200mm(self):
        """b_star/3 > 200 mm: passo = 200."""
        result = bridge_confinement_spacing_transverse(b_star=900.0)
        assert_allclose(result, 200.0, rtol=1e-6)

    def test_limited_by_b_star_third(self):
        """b_star/3 < 200 mm: passo = b_star/3."""
        result = bridge_confinement_spacing_transverse(b_star=450.0)
        assert_allclose(result, 150.0, rtol=1e-6)

    def test_exact_boundary(self):
        """b_star = 600 mm: b_star/3 = 200 -> passo = 200."""
        result = bridge_confinement_spacing_transverse(b_star=600.0)
        assert_allclose(result, 200.0, rtol=1e-6)

    def test_b_star_zero_raises(self):
        with pytest.raises(ValueError):
            bridge_confinement_spacing_transverse(b_star=0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_confinement_spacing_transverse)
        assert ref is not None
        assert ref.article == "7.9.6.1.2"
        assert ref.formula == "7.9.21"


# ── [7.9.22] — Passo barre longitudinali contro instabilita' ──────────────────


class TestBridgeTieSpacingLongitudinal:
    """NTC18 §7.9.6.1.2, Formula [7.9.22]."""

    def test_basic(self):
        """S_L_max = 6 * d_BL = 6 * 20 = 120 mm."""
        result = bridge_tie_spacing_longitudinal(d_BL=20.0)
        assert_allclose(result, 120.0, rtol=1e-6)

    def test_small_bar(self):
        """d_BL = 12: S_L_max = 72 mm."""
        result = bridge_tie_spacing_longitudinal(d_BL=12.0)
        assert_allclose(result, 72.0, rtol=1e-6)

    def test_d_BL_zero_raises(self):
        with pytest.raises(ValueError):
            bridge_tie_spacing_longitudinal(d_BL=0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_tie_spacing_longitudinal)
        assert ref is not None
        assert ref.article == "7.9.6.1.2"
        assert ref.formula == "7.9.22"
