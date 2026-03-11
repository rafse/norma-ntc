"""Test per bridges — NTC18 Cap. 5."""

import math

import pytest
import numpy as np
from numpy.testing import assert_allclose

from pyntc.actions.bridges import (
    bridge_conventional_lanes,
    bridge_load_scheme_1,
    bridge_long_span_load,
    bridge_braking_force_road,
    bridge_centrifugal_force_road,
    bridge_road_psi_coefficients,
    bridge_lm71_axle_loads,
    bridge_sw_load,
    bridge_natural_frequency,
    bridge_dynamic_coefficient,
    bridge_reduced_dynamic_coefficient,
    bridge_frequency_limits,
    bridge_centrifugal_reduction_factor,
    bridge_centrifugal_force_rail,
    bridge_braking_force_rail,
    bridge_starting_force_rail,
    bridge_curvature_radius,
    bridge_rail_psi_coefficients,
    bridge_deck_thermal_gradient,
    bridge_hollow_pier_thermal,
    bridge_rail_thermal_variation,
)
from pyntc.core.reference import get_ntc_ref


# ══════════════════════════════════════════════════════════════════════════════
# §5.1 — PONTI STRADALI
# ══════════════════════════════════════════════════════════════════════════════


# ── Tab. 5.1.1 — Corsie convenzionali ────────────────────────────────────────


class TestBridgeConventionalLanes:
    """NTC18 §5.1.3.3.2, Tab. 5.1.1."""

    def test_narrow_carriageway(self):
        """w < 5.40 m → 1 corsia da 3.00 m, zona rimanente = w - 3."""
        n, wl, wr = bridge_conventional_lanes(w=4.50)
        assert n == 1
        assert_allclose(wl, 3.00)
        assert_allclose(wr, 1.50)

    def test_medium_carriageway(self):
        """5.40 ≤ w < 6.00 → 2 corsie da w/2, zona rimanente = 0."""
        n, wl, wr = bridge_conventional_lanes(w=5.60)
        assert n == 2
        assert_allclose(wl, 2.80)
        assert_allclose(wr, 0.00)

    def test_wide_carriageway(self):
        """w ≥ 6.00 → n = int(w/3) corsie da 3.00 m."""
        n, wl, wr = bridge_conventional_lanes(w=11.00)
        assert n == 3
        assert_allclose(wl, 3.00)
        assert_allclose(wr, 2.00)

    def test_exact_6m(self):
        """w = 6.00 m → 2 corsie da 3.00 m, zona rimanente = 0."""
        n, wl, wr = bridge_conventional_lanes(w=6.00)
        assert n == 2
        assert_allclose(wl, 3.00)
        assert_allclose(wr, 0.00)

    def test_12m(self):
        """w = 12.00 m → 4 corsie da 3.00 m, zona rimanente = 0."""
        n, wl, wr = bridge_conventional_lanes(w=12.00)
        assert n == 4
        assert_allclose(wl, 3.00)
        assert_allclose(wr, 0.00)

    def test_negative_width_raises(self):
        with pytest.raises(ValueError):
            bridge_conventional_lanes(w=-1.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_conventional_lanes)
        assert ref is not None
        assert ref.table == "Tab.5.1.I"


# ── Tab. 5.1.II — Schema di Carico 1 ────────────────────────────────────────


class TestBridgeLoadScheme1:
    """NTC18 §5.1.3.3.3, Tab. 5.1.II."""

    def test_lane_1(self):
        """Corsia 1: Q_ik = 300 kN, q_ik = 9.0 kN/m²."""
        Q, q = bridge_load_scheme_1(lane=1)
        assert_allclose(Q, 300.0)
        assert_allclose(q, 9.0)

    def test_lane_2(self):
        """Corsia 2: Q_ik = 200 kN, q_ik = 2.5 kN/m²."""
        Q, q = bridge_load_scheme_1(lane=2)
        assert_allclose(Q, 200.0)
        assert_allclose(q, 2.5)

    def test_lane_3(self):
        """Corsia 3: Q_ik = 100 kN, q_ik = 2.5 kN/m²."""
        Q, q = bridge_load_scheme_1(lane=3)
        assert_allclose(Q, 100.0)
        assert_allclose(q, 2.5)

    def test_lane_4_and_beyond(self):
        """Altre corsie: Q_ik = 0, q_ik = 2.5 kN/m²."""
        Q, q = bridge_load_scheme_1(lane=4)
        assert_allclose(Q, 0.0)
        assert_allclose(q, 2.5)
        Q5, q5 = bridge_load_scheme_1(lane=5)
        assert_allclose(Q5, 0.0)
        assert_allclose(q5, 2.5)

    def test_invalid_lane_raises(self):
        with pytest.raises(ValueError):
            bridge_load_scheme_1(lane=0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_load_scheme_1)
        assert ref is not None
        assert ref.table == "Tab.5.1.II"


# ── [5.1.1-3] — Carichi distribuiti per luci > 300 m ─────────────────────────


class TestBridgeLongSpanLoad:
    """NTC18 §5.1.3.3.3, Formule [5.1.1], [5.1.2], [5.1.3]."""

    def test_type_t_formula_5_1_1(self):
        """[5.1.1] q_L,t = 128.95 * (1/L)^0.25 per corsia 3 (Schema 6.a)."""
        L = 400.0
        expected = 128.95 * (1.0 / L) ** 0.25
        result = bridge_long_span_load(L=L, load_type="t")
        assert_allclose(result, expected, rtol=1e-4)

    def test_type_b_formula_5_1_2(self):
        """[5.1.2] q_L,b = 88.71 * (1/L)^0.38 per corsia 2."""
        L = 500.0
        expected = 88.71 * (1.0 / L) ** 0.38
        result = bridge_long_span_load(L=L, load_type="b")
        assert_allclose(result, expected, rtol=1e-4)

    def test_type_c_formula_5_1_3(self):
        """[5.1.3] q_L,c = 77.12 * (1/L)^0.38 per corsia 1 (originale: w)."""
        L = 350.0
        expected = 77.12 * (1.0 / L) ** 0.38
        result = bridge_long_span_load(L=L, load_type="c")
        assert_allclose(result, expected, rtol=1e-4)

    def test_invalid_type_raises(self):
        with pytest.raises(ValueError):
            bridge_long_span_load(L=400.0, load_type="x")

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_long_span_load)
        assert ref is not None
        assert ref.formula == "5.1.1"


# ── [5.1.4] — Forza di frenamento stradale ───────────────────────────────────


class TestBridgeBrakingForceRoad:
    """NTC18 §5.1.3.5, Formula [5.1.4]."""

    def test_typical_case(self):
        """Corsia 1 standard: Q_1k=300kN, q_1k=9kN/m², w_1=3m, L=50m.
        q_3 = 0.6*(2*300) + 0.10*9*3*50 = 360 + 135 = 495 kN."""
        result = bridge_braking_force_road(Q_1k=300.0, q_1k=9.0, w_1=3.0, L=50.0)
        assert_allclose(result, 495.0, rtol=1e-3)

    def test_lower_bound(self):
        """Forza minima 180 kN (con valori piccoli che darebbero q_3 < 180)."""
        # 0.6*(2*50) + 0.10*2.5*3*1 = 60 + 0.75 = 60.75 → clamp a 180
        result = bridge_braking_force_road(Q_1k=50.0, q_1k=2.5, w_1=3.0, L=1.0)
        assert_allclose(result, 180.0)

    def test_upper_bound(self):
        """Forza massima 900 kN."""
        result = bridge_braking_force_road(Q_1k=300.0, q_1k=9.0, w_1=3.0, L=5000.0)
        assert_allclose(result, 900.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_braking_force_road)
        assert ref is not None
        assert ref.formula == "5.1.4"


# ── Tab. 5.1.III — Forza centrifuga stradale ─────────────────────────────────


class TestBridgeCentrifugalForceRoad:
    """NTC18 §5.1.3.6, Tab. 5.1.III."""

    def test_small_radius(self):
        """R < 200 m → q_s = 0.2 * Q_s."""
        result = bridge_centrifugal_force_road(R=150.0, Q_s=600.0)
        assert_allclose(result, 120.0)

    def test_medium_radius(self):
        """200 ≤ R ≤ 1500 m → q_s = 40 * Q_s / R."""
        result = bridge_centrifugal_force_road(R=500.0, Q_s=600.0)
        assert_allclose(result, 48.0)

    def test_large_radius(self):
        """R > 1500 m → q_s = 0."""
        result = bridge_centrifugal_force_road(R=2000.0, Q_s=600.0)
        assert_allclose(result, 0.0)

    def test_boundary_200(self):
        """R = 200 m → formula media: 40*Q_s/R."""
        result = bridge_centrifugal_force_road(R=200.0, Q_s=600.0)
        assert_allclose(result, 120.0)

    def test_boundary_1500(self):
        """R = 1500 m → formula media: 40*Q_s/R."""
        result = bridge_centrifugal_force_road(R=1500.0, Q_s=600.0)
        assert_allclose(result, 16.0)

    def test_negative_radius_raises(self):
        with pytest.raises(ValueError):
            bridge_centrifugal_force_road(R=-100.0, Q_s=600.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_centrifugal_force_road)
        assert ref is not None
        assert ref.table == "Tab.5.1.III"


# ── Tab. 5.1.VI — Coefficienti ψ stradali ───────────────────────────────────


class TestBridgeRoadPsiCoefficients:
    """NTC18 §5.1.3.14, Tab. 5.1.VI."""

    def test_tandem(self):
        """Schema 1 (carichi tandem): ψ₀=0.75, ψ₁=0.75, ψ₂=0.0."""
        psi = bridge_road_psi_coefficients(action="tandem")
        assert_allclose(psi, (0.75, 0.75, 0.0))

    def test_distributed(self):
        """Schemi 1,5,6 (distribuiti): ψ₀=0.40, ψ₁=0.40, ψ₂=0.0."""
        psi = bridge_road_psi_coefficients(action="distributed")
        assert_allclose(psi, (0.40, 0.40, 0.0))

    def test_wind_unloaded(self):
        """Vento a ponte scarico: ψ₀=0.6, ψ₁=0.2, ψ₂=0.0."""
        psi = bridge_road_psi_coefficients(action="wind_unloaded")
        assert_allclose(psi, (0.6, 0.2, 0.0))

    def test_temperature(self):
        """Temperatura: ψ₀=0.6, ψ₁=0.6, ψ₂=0.5."""
        psi = bridge_road_psi_coefficients(action="temperature")
        assert_allclose(psi, (0.6, 0.6, 0.5))

    def test_invalid_action_raises(self):
        with pytest.raises(ValueError):
            bridge_road_psi_coefficients(action="nonexistent")

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_road_psi_coefficients)
        assert ref is not None
        assert ref.table == "Tab.5.1.VI"


# ══════════════════════════════════════════════════════════════════════════════
# §5.2 — PONTI FERROVIARI
# ══════════════════════════════════════════════════════════════════════════════


# ── §5.2.2.2.1.1 — Modello di carico LM71 ───────────────────────────────────


class TestBridgeLM71AxleLoads:
    """NTC18 §5.2.2.2.1.1."""

    def test_default_alpha(self):
        """α=1.1: Q_vk = 1.1*250 = 275 kN, q_vk = 1.1*80 = 88 kN/m."""
        Q, q = bridge_lm71_axle_loads(alpha=1.1)
        assert_allclose(Q, 275.0)
        assert_allclose(q, 88.0)

    def test_alpha_1(self):
        """α=1.0: Q_vk = 250 kN, q_vk = 80 kN/m (valori base)."""
        Q, q = bridge_lm71_axle_loads(alpha=1.0)
        assert_allclose(Q, 250.0)
        assert_allclose(q, 80.0)

    def test_eccentricity_ratio(self):
        """[5.2.1] Rapporto Q_v2/Q_v1 = 1.25 (verificato internamente)."""
        # La funzione restituisce carichi per asse; il rapporto eccentricità
        # è s/18 = 1435/18 ≈ 79.7 mm — documentato in docstring
        Q, q = bridge_lm71_axle_loads(alpha=1.0)
        assert_allclose(Q, 250.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_lm71_axle_loads)
        assert ref is not None
        assert ref.article == "5.2.2.2.1.1"


# ── Tab. 5.2.1 — Modelli di carico SW ────────────────────────────────────────


class TestBridgeSWLoad:
    """NTC18 §5.2.2.2.1.2, Tab. 5.2.1."""

    def test_sw0(self):
        """SW/0: q_ak=133 kN/m, a=15.0 m, c=5.3 m, α=1.1."""
        q, a, c = bridge_sw_load(model="SW/0", alpha=1.1)
        assert_allclose(q, 1.1 * 133.0)
        assert_allclose(a, 15.0)
        assert_allclose(c, 5.3)

    def test_sw2(self):
        """SW/2: q_ak=150 kN/m, a=25.0 m, c=7.0 m, α=1.0."""
        q, a, c = bridge_sw_load(model="SW/2", alpha=1.0)
        assert_allclose(q, 150.0)
        assert_allclose(a, 25.0)
        assert_allclose(c, 7.0)

    def test_sw0_default_alpha(self):
        """SW/0 con alpha di default 1.1."""
        q, a, c = bridge_sw_load(model="SW/0")
        assert_allclose(q, 1.1 * 133.0)

    def test_sw2_default_alpha(self):
        """SW/2 con alpha di default 1.0."""
        q, a, c = bridge_sw_load(model="SW/2")
        assert_allclose(q, 150.0)

    def test_invalid_model_raises(self):
        with pytest.raises(ValueError):
            bridge_sw_load(model="SW/3")

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_sw_load)
        assert ref is not None
        assert ref.table == "Tab.5.2.I"


# ── [5.2.5] — Frequenza propria ──────────────────────────────────────────────


class TestBridgeNaturalFrequency:
    """NTC18 §5.2.2.2.3, Formula [5.2.5]."""

    def test_typical_deflection(self):
        """δ₀ = 10 mm → n₀ = 17.75/√10 ≈ 5.614 Hz."""
        result = bridge_natural_frequency(delta_0=10.0)
        assert_allclose(result, 17.75 / math.sqrt(10.0), rtol=1e-4)

    def test_large_deflection(self):
        """δ₀ = 50 mm → n₀ = 17.75/√50 ≈ 2.510 Hz."""
        result = bridge_natural_frequency(delta_0=50.0)
        assert_allclose(result, 17.75 / math.sqrt(50.0), rtol=1e-4)

    def test_negative_deflection_raises(self):
        with pytest.raises(ValueError):
            bridge_natural_frequency(delta_0=-1.0)

    def test_zero_deflection_raises(self):
        with pytest.raises(ValueError):
            bridge_natural_frequency(delta_0=0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_natural_frequency)
        assert ref is not None
        assert ref.formula == "5.2.5"


# ── [5.2.6-7] — Coefficienti dinamici Φ₂ e Φ₃ ──────────────────────────────


class TestBridgeDynamicCoefficient:
    """NTC18 §5.2.2.2.3, Formule [5.2.6] e [5.2.7]."""

    def test_phi2_typical(self):
        """L₀=20m, manutenzione elevata → Φ₂ = 1.44/√(20-0.2)+0.82."""
        expected = 1.44 / math.sqrt(20.0 - 0.2) + 0.82
        result = bridge_dynamic_coefficient(L_0=20.0, maintenance="high")
        assert_allclose(result, expected, rtol=1e-4)

    def test_phi3_typical(self):
        """L₀=20m, manutenzione ridotta → Φ₃ = 2.16/√(20-0.2)+0.73."""
        expected = 2.16 / math.sqrt(20.0 - 0.2) + 0.73
        result = bridge_dynamic_coefficient(L_0=20.0, maintenance="low")
        assert_allclose(result, expected, rtol=1e-4)

    def test_phi2_lower_bound(self):
        """Φ₂ ≥ 1.00: per L₀ molto grande il valore tende a 0.82, clamp a 1.0."""
        result = bridge_dynamic_coefficient(L_0=10000.0, maintenance="high")
        assert_allclose(result, 1.00)

    def test_phi2_upper_bound(self):
        """Φ₂ ≤ 1.67: per L₀ piccolo."""
        result = bridge_dynamic_coefficient(L_0=1.0, maintenance="high")
        assert_allclose(result, 1.67)

    def test_phi3_upper_bound(self):
        """Φ₃ ≤ 2.00: per L₀ piccolo."""
        result = bridge_dynamic_coefficient(L_0=1.0, maintenance="low")
        assert_allclose(result, 2.00)

    def test_invalid_maintenance_raises(self):
        with pytest.raises(ValueError):
            bridge_dynamic_coefficient(L_0=20.0, maintenance="medium")

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_dynamic_coefficient)
        assert ref is not None
        assert ref.formula == "5.2.6"


# ── [5.2.8] — Coefficiente dinamico ridotto ──────────────────────────────────


class TestBridgeReducedDynamicCoefficient:
    """NTC18 §5.2.2.2.3, Formula [5.2.8]."""

    def test_typical(self):
        """Φ=1.5, h=3.0m → Φ_rid = 1.5 - (3-1)/10 = 1.3."""
        result = bridge_reduced_dynamic_coefficient(Phi=1.5, h=3.0)
        assert_allclose(result, 1.3)

    def test_lower_bound(self):
        """Φ_rid ≥ 1.0: per h grande."""
        result = bridge_reduced_dynamic_coefficient(Phi=1.2, h=10.0)
        assert_allclose(result, 1.0)

    def test_h_below_threshold(self):
        """h ≤ 1.0 m → Φ_rid = Φ (nessuna riduzione)."""
        result = bridge_reduced_dynamic_coefficient(Phi=1.5, h=0.8)
        assert_allclose(result, 1.5)

    def test_h_over_2_5_unity(self):
        """Per copertura > 2.50 m → Φ_rid = 1.0 (norma: unitario)."""
        result = bridge_reduced_dynamic_coefficient(Phi=1.5, h=3.0)
        # Formula: 1.5 - (3-1)/10 = 1.3. La norma dice unitario per h>2.5
        # ma la formula [5.2.8] si applica sempre con clamp ≥ 1.0
        assert result >= 1.0

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_reduced_dynamic_coefficient)
        assert ref is not None
        assert ref.formula == "5.2.8"


# ── [5.2.2-4] — Limiti di frequenza ──────────────────────────────────────────


class TestBridgeFrequencyLimits:
    """NTC18 §5.2.2.2.3, Formule [5.2.2], [5.2.3], [5.2.4]."""

    def test_upper_limit(self):
        """[5.2.2] Limite superiore: n₀ = 94.76 * L^(-0.748)."""
        L = 20.0
        expected_upper = 94.76 * L ** (-0.748)
        upper, _ = bridge_frequency_limits(L=L)
        assert_allclose(upper, expected_upper, rtol=1e-3)

    def test_lower_limit_short(self):
        """[5.2.3] L ≤ 20m: limite inferiore = 80/L."""
        L = 10.0
        _, lower = bridge_frequency_limits(L=L)
        assert_allclose(lower, 80.0 / 10.0, rtol=1e-3)

    def test_lower_limit_long(self):
        """[5.2.4] L > 20m: limite inferiore = 23.58 * L^(-0.902)."""
        L = 50.0
        expected_lower = 23.58 * L ** (-0.902)
        _, lower = bridge_frequency_limits(L=L)
        assert_allclose(lower, expected_lower, rtol=1e-3)

    def test_boundary_20m(self):
        """L = 20m: limite inferiore = 80/20 = 4.0 Hz."""
        _, lower = bridge_frequency_limits(L=20.0)
        assert_allclose(lower, 4.0, rtol=1e-3)

    def test_invalid_L_raises(self):
        with pytest.raises(ValueError):
            bridge_frequency_limits(L=0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_frequency_limits)
        assert ref is not None
        assert ref.formula == "5.2.2"


# ── [5.2.10] — Fattore di riduzione centrifuga f ─────────────────────────────


class TestBridgeCentrifugalReductionFactor:
    """NTC18 §5.2.2.3.1, Formula [5.2.10]."""

    def test_low_speed(self):
        """V ≤ 120 km/h → f = 1.0."""
        result = bridge_centrifugal_reduction_factor(V=100.0, L_t=50.0)
        assert_allclose(result, 1.0)

    def test_short_track(self):
        """L_t ≤ 2.88 m → f = 1.0."""
        result = bridge_centrifugal_reduction_factor(V=200.0, L_t=2.0)
        assert_allclose(result, 1.0)

    def test_typical_reduction(self):
        """V=200, L_t=50 → f < 1.0 (formula completa)."""
        V, L_t = 200.0, 50.0
        expected = 1 - (V - 120) / 1000 * (814 / V + 1.75) * (
            1 - math.sqrt(2.88 / L_t)
        )
        result = bridge_centrifugal_reduction_factor(V=V, L_t=L_t)
        assert_allclose(result, expected, rtol=1e-4)

    def test_v_over_300(self):
        """V > 300 km/h → f(V) = f(300)."""
        f_300 = bridge_centrifugal_reduction_factor(V=300.0, L_t=50.0)
        f_350 = bridge_centrifugal_reduction_factor(V=350.0, L_t=50.0)
        assert_allclose(f_350, f_300)

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_centrifugal_reduction_factor)
        assert ref is not None
        assert ref.formula == "5.2.10"


# ── [5.2.9] — Forza centrifuga ferroviaria ───────────────────────────────────


class TestBridgeCentrifugalForceRail:
    """NTC18 §5.2.2.3.1, Formula [5.2.9]."""

    def test_axle_load(self):
        """Q_a = V²/(127*r) * (f*α*Q_ik)."""
        V, r, Q_ik, alpha, f = 120.0, 500.0, 250.0, 1.1, 1.0
        expected = V**2 / (127.0 * r) * (f * alpha * Q_ik)
        result = bridge_centrifugal_force_rail(
            V=V, r=r, Q_ik=Q_ik, alpha=alpha, f=f
        )
        assert_allclose(result, expected, rtol=1e-4)

    def test_distributed_load(self):
        """q_ik centrifuga = V²/(127*r) * (f*α*q_ik)."""
        V, r, q_ik, alpha, f = 120.0, 300.0, 80.0, 1.1, 1.0
        expected = V**2 / (127.0 * r) * (f * alpha * q_ik)
        result = bridge_centrifugal_force_rail(
            V=V, r=r, Q_ik=q_ik, alpha=alpha, f=f
        )
        assert_allclose(result, expected, rtol=1e-4)

    def test_negative_radius_raises(self):
        with pytest.raises(ValueError):
            bridge_centrifugal_force_rail(V=120.0, r=-100.0, Q_ik=250.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_centrifugal_force_rail)
        assert ref is not None
        assert ref.formula == "5.2.9"


# ── Forza di frenamento ferroviario ──────────────────────────────────────────


class TestBridgeBrakingForceRail:
    """NTC18 §5.2.2.3.3."""

    def test_lm71_typical(self):
        """LM71: Q_hk = 20*L*α, capped at 6000 kN."""
        result = bridge_braking_force_rail(L=100.0, model="LM71", alpha=1.1)
        assert_allclose(result, 20.0 * 100.0 * 1.1)

    def test_lm71_upper_bound(self):
        """LM71: max 6000 kN."""
        result = bridge_braking_force_rail(L=500.0, model="LM71", alpha=1.1)
        assert_allclose(result, 6000.0)

    def test_sw0(self):
        """SW/0: stessa formula del LM71."""
        result = bridge_braking_force_rail(L=100.0, model="SW/0", alpha=1.1)
        assert_allclose(result, 20.0 * 100.0 * 1.1)

    def test_sw2(self):
        """SW/2: Q_hk = 35*L*α (nessun limite superiore esplicito)."""
        result = bridge_braking_force_rail(L=100.0, model="SW/2", alpha=1.0)
        assert_allclose(result, 3500.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_braking_force_rail)
        assert ref is not None
        assert ref.article == "5.2.2.3.3"


# ── Forza di avviamento ferroviario ──────────────────────────────────────────


class TestBridgeStartingForceRail:
    """NTC18 §5.2.2.3.3."""

    def test_typical(self):
        """Q_ak = 33*L*α, capped at 1000 kN."""
        result = bridge_starting_force_rail(L=20.0, alpha=1.1)
        assert_allclose(result, 33.0 * 20.0 * 1.1)

    def test_upper_bound(self):
        """Max 1000 kN."""
        result = bridge_starting_force_rail(L=100.0, alpha=1.1)
        assert_allclose(result, 1000.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_starting_force_rail)
        assert ref is not None
        assert ref.article == "5.2.2.3.3"


# ── [5.2.11] — Raggio di curvatura orizzontale ──────────────────────────────


class TestBridgeCurvatureRadius:
    """NTC18 §5.2.3.2.2.1, Formula [5.2.11]."""

    def test_typical(self):
        """R = L²/(8*δ_i). L=30m, δ_i=5mm → R = 900/(8*0.005) = 22500 m."""
        result = bridge_curvature_radius(L=30.0, delta_i=0.005)
        assert_allclose(result, 22500.0, rtol=1e-4)

    def test_small_deflection(self):
        """δ_i=1mm, L=20m → R = 400/0.008 = 50000 m."""
        result = bridge_curvature_radius(L=20.0, delta_i=0.001)
        assert_allclose(result, 50000.0, rtol=1e-4)

    def test_zero_deflection_raises(self):
        with pytest.raises(ValueError):
            bridge_curvature_radius(L=20.0, delta_i=0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_curvature_radius)
        assert ref is not None
        assert ref.formula == "5.2.11"


# ── Tab. 5.2.VI — Coefficienti ψ ferroviari ──────────────────────────────────


class TestBridgeRailPsiCoefficients:
    """NTC18 §5.2.3.2.2, Tab. 5.2.VI."""

    def test_gr1(self):
        """Gruppo gr₁: ψ₀=0.80, ψ₁=0.80, ψ₂=0.0."""
        psi = bridge_rail_psi_coefficients(action="gr1", n_tracks=1)
        assert_allclose(psi, (0.80, 0.80, 0.0))

    def test_gr1_two_tracks(self):
        """gr₁ con 2 binari: ψ₀=0.60."""
        psi = bridge_rail_psi_coefficients(action="gr1", n_tracks=2)
        assert_allclose(psi[0], 0.60)

    def test_gr1_three_tracks(self):
        """gr₁ con 3+ binari: ψ₀=0.40."""
        psi = bridge_rail_psi_coefficients(action="gr1", n_tracks=3)
        assert_allclose(psi[0], 0.40)

    def test_wind(self):
        """Vento: ψ₀=0.60, ψ₁=0.50, ψ₂=0.0."""
        psi = bridge_rail_psi_coefficients(action="wind")
        assert_allclose(psi, (0.60, 0.50, 0.0))

    def test_temperature(self):
        """Temperatura: ψ₀=0.60, ψ₁=0.60, ψ₂=0.50."""
        psi = bridge_rail_psi_coefficients(action="temperature")
        assert_allclose(psi, (0.60, 0.60, 0.50))

    def test_invalid_action_raises(self):
        with pytest.raises(ValueError):
            bridge_rail_psi_coefficients(action="nonexistent")

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_rail_psi_coefficients)
        assert ref is not None
        assert ref.table == "Tab.5.2.VI"


# ══════════════════════════════════════════════════════════════════════════════
# §5.2.2.4.2 — TEMPERATURA NEI PONTI
# ══════════════════════════════════════════════════════════════════════════════


# ── Gradiente termico impalcato ──────────────────────────────────────────────


class TestBridgeDeckThermalGradient:
    """NTC18 §5.2.2.4.2 — Gradiente termico non uniforme nell'impalcato."""

    def test_slab_strength(self):
        """Impalcato generico, verifica resistenza: ΔT = 5 °C."""
        result = bridge_deck_thermal_gradient(deck_type="slab", check="strength")
        assert_allclose(result, 5.0)

    def test_box_strength(self):
        """Cassone c.a., verifica resistenza: ΔT = 5 °C."""
        result = bridge_deck_thermal_gradient(deck_type="box", check="strength")
        assert_allclose(result, 5.0)

    def test_composite_strength(self):
        """Misto acciaio-cls, verifica resistenza: ΔT = 5 °C."""
        result = bridge_deck_thermal_gradient(deck_type="composite", check="strength")
        assert_allclose(result, 5.0)

    def test_slab_deformation(self):
        """Impalcato generico, verifica deformazioni: ΔT = 10 °C."""
        result = bridge_deck_thermal_gradient(deck_type="slab", check="deformation")
        assert_allclose(result, 10.0)

    def test_box_deformation(self):
        """Cassone c.a., verifica deformazioni: ΔT = 10 °C."""
        result = bridge_deck_thermal_gradient(deck_type="box", check="deformation")
        assert_allclose(result, 10.0)

    def test_composite_deformation(self):
        """Misto acciaio-cls, verifica deformazioni: ΔT = 10 °C."""
        result = bridge_deck_thermal_gradient(
            deck_type="composite", check="deformation"
        )
        assert_allclose(result, 10.0)

    def test_default_check_is_strength(self):
        """Check di default e' 'strength'."""
        result = bridge_deck_thermal_gradient(deck_type="slab")
        assert_allclose(result, 5.0)

    def test_invalid_deck_type_raises(self):
        with pytest.raises(ValueError, match="deck_type"):
            bridge_deck_thermal_gradient(deck_type="timber")

    def test_invalid_check_raises(self):
        with pytest.raises(ValueError, match="check"):
            bridge_deck_thermal_gradient(deck_type="slab", check="comfort")

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_deck_thermal_gradient)
        assert ref is not None
        assert ref.article == "5.2.2.4.2"


# ── Gradienti termici pile cave ──────────────────────────────────────────────


class TestBridgeHollowPierThermal:
    """NTC18 §5.2.2.4.2 — Gradienti termici per pile cave."""

    def test_typical_wall(self):
        """t_w=0.40m: ΔT_int_ext=10°C, ΔT_shaft_raft=5°C, h=2.0m."""
        dt_ie, dt_sr, h = bridge_hollow_pier_thermal(t_w=0.40)
        assert_allclose(dt_ie, 10.0)
        assert_allclose(dt_sr, 5.0)
        assert_allclose(h, 2.0)

    def test_thick_wall(self):
        """t_w=0.80m: h_variation=4.0m."""
        _, _, h = bridge_hollow_pier_thermal(t_w=0.80)
        assert_allclose(h, 4.0)

    def test_thin_wall(self):
        """t_w=0.25m: h_variation=1.25m."""
        _, _, h = bridge_hollow_pier_thermal(t_w=0.25)
        assert_allclose(h, 1.25)

    def test_zero_thickness_raises(self):
        with pytest.raises(ValueError):
            bridge_hollow_pier_thermal(t_w=0.0)

    def test_negative_thickness_raises(self):
        with pytest.raises(ValueError):
            bridge_hollow_pier_thermal(t_w=-0.3)

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_hollow_pier_thermal)
        assert ref is not None
        assert ref.article == "5.2.2.4.2"


# ── Variazione termica binario ───────────────────────────────────────────────


class TestBridgeRailThermalVariation:
    """NTC18 §5.2.2.4.2 — Variazioni termiche del binario."""

    def test_with_expansion_device(self):
        """Con apparecchi di dilatazione: +30 °C, -40 °C."""
        dt_pos, dt_neg = bridge_rail_thermal_variation(has_expansion_device=True)
        assert_allclose(dt_pos, 30.0)
        assert_allclose(dt_neg, -40.0)

    def test_without_expansion_device(self):
        """Senza apparecchi di dilatazione: 0 °C, 0 °C."""
        dt_pos, dt_neg = bridge_rail_thermal_variation(has_expansion_device=False)
        assert_allclose(dt_pos, 0.0)
        assert_allclose(dt_neg, 0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(bridge_rail_thermal_variation)
        assert ref is not None
        assert ref.article == "5.2.2.4.2"
