"""Test per seismic_timber — NTC18 §7.7 (costruzioni di legno in zona sismica)."""

import pytest
from numpy.testing import assert_allclose

from pyntc.checks.seismic_timber import (
    seismic_timber_beam_hb_ratio,
    seismic_timber_behavior_factor,
    seismic_timber_bolt_diameter_check,
    seismic_timber_capacity_design,
    seismic_timber_carpentry_joint_shear,
    seismic_timber_connector_ductility,
    seismic_timber_cyclic_design_strength,
    seismic_timber_panel_thickness,
    seismic_timber_static_ductility_check,
)
from pyntc.core.reference import get_ntc_ref


# ── §7.7.3 — Fattore di comportamento ───────────────────────────────────────


class TestSeismicTimberBehaviorFactor:
    """NTC18 §7.7.3, Tab. 7.3.II."""

    def test_light_frame_nailed_cda_regular(self):
        """light_frame_nailed, CD'A', regolare: q = 5.0 * 1.0 = 5.0."""
        result = seismic_timber_behavior_factor(
            "light_frame_nailed", "A", regular_in_height=True
        )
        assert_allclose(result, 5.0, rtol=1e-3)

    def test_light_frame_nailed_cdb(self):
        """light_frame_nailed, CD'B': q = 3.0."""
        result = seismic_timber_behavior_factor("light_frame_nailed", "B")
        assert_allclose(result, 3.0, rtol=1e-3)

    def test_light_frame_glued_cda(self):
        """light_frame_glued, CD'A': q = 3.0."""
        result = seismic_timber_behavior_factor("light_frame_glued", "A")
        assert_allclose(result, 3.0, rtol=1e-3)

    def test_light_frame_glued_cdb(self):
        """light_frame_glued, CD'B': q = 2.0."""
        result = seismic_timber_behavior_factor("light_frame_glued", "B")
        assert_allclose(result, 2.0, rtol=1e-3)

    def test_portal_hyperstat_cda(self):
        """portal_hyperstat, CD'A': q = 4.0."""
        result = seismic_timber_behavior_factor("portal_hyperstat", "A")
        assert_allclose(result, 4.0, rtol=1e-3)

    def test_portal_hyperstat_cdb(self):
        """portal_hyperstat, CD'B': q = 2.5."""
        result = seismic_timber_behavior_factor("portal_hyperstat", "B")
        assert_allclose(result, 2.5, rtol=1e-3)

    def test_truss_same_both_classes(self):
        """truss: q = 2.5 per entrambe le classi."""
        assert_allclose(
            seismic_timber_behavior_factor("truss", "A"), 2.5, rtol=1e-3
        )
        assert_allclose(
            seismic_timber_behavior_factor("truss", "B"), 2.5, rtol=1e-3
        )

    def test_isostatic_same_both_classes(self):
        """isostatic: q = 1.5 per entrambe le classi."""
        assert_allclose(
            seismic_timber_behavior_factor("isostatic", "A"), 1.5, rtol=1e-3
        )
        assert_allclose(
            seismic_timber_behavior_factor("isostatic", "B"), 1.5, rtol=1e-3
        )

    def test_irregular_in_height_reduces_q(self):
        """Irregolare in altezza: K_R = 0.8 -> q ridotto."""
        q_reg = seismic_timber_behavior_factor(
            "light_frame_nailed", "A", regular_in_height=True
        )
        q_irr = seismic_timber_behavior_factor(
            "light_frame_nailed", "A", regular_in_height=False
        )
        assert_allclose(q_irr, q_reg * 0.8, rtol=1e-3)

    def test_nondissipative_returns_15(self):
        """Struttura non dissipativa: q = 1.5 indipendentemente dalla tipologia."""
        result = seismic_timber_behavior_factor("light_frame_nailed", "ND")
        assert_allclose(result, 1.5, rtol=1e-3)

    def test_invalid_structural_type_raises(self):
        with pytest.raises(ValueError):
            seismic_timber_behavior_factor("unknown_type", "A")

    def test_invalid_ductility_class_raises(self):
        with pytest.raises(ValueError):
            seismic_timber_behavior_factor("light_frame_nailed", "C")

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_timber_behavior_factor)
        assert ref is not None
        assert ref.article == "7.7.3"
        assert ref.table == "Tab.7.3.II"


# ── §7.7.3.1 — Duttilita' connettori ────────────────────────────────────────


class TestSeismicTimberConnectorDuctility:
    """NTC18 §7.7.3.1 — Requisiti di duttilita' connettori."""

    def test_timber_timber_full_cda_cdb(self):
        """d=10mm, t=105mm >= 10d=100mm -> A_B."""
        ok, dc = seismic_timber_connector_ductility(
            connector_diameter=10.0,
            member_thickness=105.0,
            connection_type="timber_timber",
        )
        assert ok is True
        assert dc == "A_B"

    def test_timber_timber_partial_b_only(self):
        """d=10mm, t=85mm: 8d=80 <= t < 10d=100 -> B_only."""
        ok, dc = seismic_timber_connector_ductility(
            connector_diameter=10.0,
            member_thickness=85.0,
            connection_type="timber_timber",
        )
        assert ok is True
        assert dc == "B_only"

    def test_timber_timber_insufficient(self):
        """d=10mm, t=70mm < 8d=80mm -> none."""
        ok, dc = seismic_timber_connector_ductility(
            connector_diameter=10.0,
            member_thickness=70.0,
            connection_type="timber_timber",
        )
        assert ok is False
        assert dc == "none"

    def test_timber_timber_diameter_exceeded(self):
        """d=14mm > 12mm -> none."""
        ok, dc = seismic_timber_connector_ductility(
            connector_diameter=14.0,
            member_thickness=200.0,
            connection_type="timber_timber",
        )
        assert ok is False
        assert dc == "none"

    def test_timber_timber_max_diameter(self):
        """d=12mm (limite esatto), t=125mm >= 10d=120mm -> A_B."""
        ok, dc = seismic_timber_connector_ductility(
            connector_diameter=12.0,
            member_thickness=125.0,
            connection_type="timber_timber",
        )
        assert ok is True
        assert dc == "A_B"

    def test_timber_steel_same_as_timber_timber(self):
        """timber_steel trattato come timber_timber."""
        ok, dc = seismic_timber_connector_ductility(
            connector_diameter=8.0,
            member_thickness=90.0,  # >= 10*8=80
            connection_type="timber_steel",
        )
        assert ok is True
        assert dc == "A_B"

    def test_light_frame_full_cda_cdb(self):
        """d=3.0mm, t=13mm >= 4d=12mm -> A_B."""
        ok, dc = seismic_timber_connector_ductility(
            connector_diameter=3.0,
            member_thickness=13.0,
            connection_type="light_frame",
        )
        assert ok is True
        assert dc == "A_B"

    def test_light_frame_partial_b_only(self):
        """d=3.0mm, t=10mm: 3d=9 <= t < 4d=12 -> B_only."""
        ok, dc = seismic_timber_connector_ductility(
            connector_diameter=3.0,
            member_thickness=10.0,
            connection_type="light_frame",
        )
        assert ok is True
        assert dc == "B_only"

    def test_light_frame_diameter_exceeded(self):
        """d=4.0mm > 3.1mm -> none."""
        ok, dc = seismic_timber_connector_ductility(
            connector_diameter=4.0,
            member_thickness=20.0,
            connection_type="light_frame",
        )
        assert ok is False
        assert dc == "none"

    def test_zero_diameter_raises(self):
        with pytest.raises(ValueError):
            seismic_timber_connector_ductility(0.0, 100.0)

    def test_zero_thickness_raises(self):
        with pytest.raises(ValueError):
            seismic_timber_connector_ductility(10.0, 0.0)

    def test_invalid_connection_type_raises(self):
        with pytest.raises(ValueError):
            seismic_timber_connector_ductility(10.0, 100.0, "invalid_type")

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_timber_connector_ductility)
        assert ref is not None
        assert ref.article == "7.7.3.1"


# ── §7.7.1 — Gerarchia delle resistenze ─────────────────────────────────────


class TestSeismicTimberCapacityDesign:
    """NTC18 §7.7.1 — Capacity design."""

    def test_satisfied_cdb(self):
        """R_nd >= 1.1 * R_d: verifica soddisfatta per CD'B'."""
        ok, ratio = seismic_timber_capacity_design(
            R_nondissipative=120.0, R_dissipative=100.0, ductility_class="B"
        )
        assert ok is True
        assert_allclose(ratio, 120.0 / 110.0, rtol=1e-3)

    def test_not_satisfied_cdb(self):
        """R_nd < 1.1 * R_d: verifica non soddisfatta per CD'B'."""
        ok, ratio = seismic_timber_capacity_design(
            R_nondissipative=100.0, R_dissipative=100.0, ductility_class="B"
        )
        assert ok is False
        assert_allclose(ratio, 100.0 / 110.0, rtol=1e-3)

    def test_satisfied_cda(self):
        """R_nd >= 1.3 * R_d: verifica soddisfatta per CD'A'."""
        ok, ratio = seismic_timber_capacity_design(
            R_nondissipative=150.0, R_dissipative=100.0, ductility_class="A"
        )
        assert ok is True
        assert_allclose(ratio, 150.0 / 130.0, rtol=1e-3)

    def test_exact_boundary_cda(self):
        """R_nd = 1.3 * R_d: al limite, verifica soddisfatta."""
        ok, ratio = seismic_timber_capacity_design(
            R_nondissipative=130.0, R_dissipative=100.0, ductility_class="A"
        )
        assert ok is True
        assert_allclose(ratio, 1.0, rtol=1e-3)

    def test_custom_gamma_rd(self):
        """gamma_Rd personalizzato (>= minimo normativo)."""
        ok, ratio = seismic_timber_capacity_design(
            R_nondissipative=160.0,
            R_dissipative=100.0,
            ductility_class="A",
            gamma_Rd=1.5,
        )
        assert ok is True
        assert_allclose(ratio, 160.0 / 150.0, rtol=1e-3)

    def test_gamma_rd_below_minimum_raises(self):
        """gamma_Rd < minimo normativo -> ValueError."""
        with pytest.raises(ValueError):
            seismic_timber_capacity_design(
                R_nondissipative=150.0,
                R_dissipative=100.0,
                ductility_class="A",
                gamma_Rd=1.2,  # < 1.3 per CD"A"
            )

    def test_negative_R_nondissipative_raises(self):
        with pytest.raises(ValueError):
            seismic_timber_capacity_design(-10.0, 100.0, "B")

    def test_zero_R_dissipative_raises(self):
        with pytest.raises(ValueError):
            seismic_timber_capacity_design(100.0, 0.0, "B")

    def test_invalid_ductility_class_raises(self):
        with pytest.raises(ValueError):
            seismic_timber_capacity_design(100.0, 80.0, "C")

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_timber_capacity_design)
        assert ref is not None
        assert ref.article == "7.7.1"


# ── §7.7.6 — Resistenza ridotta per cicli ───────────────────────────────────


class TestSeismicTimberCyclicDesignStrength:
    """NTC18 §7.7.6 — Riduzione del 20% per degrado ciclico."""

    def test_basic_reduction(self):
        """X_d = 20 N/mm^2 -> X_d,sism = 16.0 N/mm^2."""
        result = seismic_timber_cyclic_design_strength(X_d=20.0)
        assert_allclose(result, 16.0, rtol=1e-3)

    def test_zero_returns_zero(self):
        """X_d = 0 -> X_d,sism = 0."""
        result = seismic_timber_cyclic_design_strength(X_d=0.0)
        assert_allclose(result, 0.0, atol=1e-10)

    def test_factor_is_080(self):
        """Fattore di riduzione e' sempre 0.8."""
        for x in [5.0, 12.5, 30.0, 100.0]:
            assert_allclose(seismic_timber_cyclic_design_strength(x), 0.8 * x, rtol=1e-6)

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            seismic_timber_cyclic_design_strength(-1.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_timber_cyclic_design_strength)
        assert ref is not None
        assert ref.article == "7.7.6"


# ── §7.7.6 — Verifica taglio giunti di carpenteria ──────────────────────────


class TestSeismicTimberCarpentryJointShear:
    """NTC18 §7.7.6 — Taglio giunti di carpenteria con coeff. aggiuntivo 1.3."""

    def test_satisfied(self):
        """tau_d = 1.0, f_v_d = 1.5 -> f_v_d/1.3 = 1.154, ratio = 0.867 <= 1."""
        ok, ratio = seismic_timber_carpentry_joint_shear(tau_d=1.0, f_v_d=1.5)
        assert ok is True
        assert_allclose(ratio, 1.0 / (1.5 / 1.3), rtol=1e-3)

    def test_not_satisfied(self):
        """tau_d = 1.5 > f_v_d/1.3 = 1.154."""
        ok, ratio = seismic_timber_carpentry_joint_shear(tau_d=1.5, f_v_d=1.5)
        assert ok is False
        assert ratio > 1.0

    def test_exact_boundary(self):
        """tau_d = f_v_d/1.3: al limite."""
        f_v_d = 2.0
        tau_d = f_v_d / 1.3
        ok, ratio = seismic_timber_carpentry_joint_shear(tau_d=tau_d, f_v_d=f_v_d)
        assert ok is True
        assert_allclose(ratio, 1.0, rtol=1e-6)

    def test_additional_safety_factor(self):
        """Il coeff. aggiuntivo 1.3 e' quello normativo di §7.7.6."""
        # tau pari a f_v,d (verifica statica ok): sismica NON ok
        ok_seismic, _ = seismic_timber_carpentry_joint_shear(tau_d=1.0, f_v_d=1.0)
        assert ok_seismic is False  # perche' 1.0 > 1.0/1.3

    def test_zero_f_v_d_raises(self):
        with pytest.raises(ValueError):
            seismic_timber_carpentry_joint_shear(tau_d=1.0, f_v_d=0.0)

    def test_negative_tau_raises(self):
        with pytest.raises(ValueError):
            seismic_timber_carpentry_joint_shear(tau_d=-0.5, f_v_d=1.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_timber_carpentry_joint_shear)
        assert ref is not None
        assert ref.article == "7.7.6"


# ── §7.7.2 — Spessori pannelli strutturali ───────────────────────────────────


class TestSeismicTimberPanelThickness:
    """NTC18 §7.7.2 — Spessori minimi pannelli strutturali."""

    def test_particleboard_ok(self):
        """Pannello di particelle: t=15mm >= 13mm."""
        ok, ratio = seismic_timber_panel_thickness("particleboard", 15.0)
        assert ok is True
        assert_allclose(ratio, 15.0 / 13.0, rtol=1e-3)

    def test_particleboard_too_thin(self):
        """Pannello di particelle: t=12mm < 13mm."""
        ok, ratio = seismic_timber_panel_thickness("particleboard", 12.0)
        assert ok is False
        assert_allclose(ratio, 12.0 / 13.0, rtol=1e-3)

    def test_particleboard_exact(self):
        """Pannello di particelle: t=13mm (limite esatto)."""
        ok, ratio = seismic_timber_panel_thickness("particleboard", 13.0)
        assert ok is True
        assert_allclose(ratio, 1.0, rtol=1e-6)

    def test_plywood_ok(self):
        """Compensato: t=12mm >= 9mm."""
        ok, ratio = seismic_timber_panel_thickness("plywood", 12.0)
        assert ok is True
        assert_allclose(ratio, 12.0 / 9.0, rtol=1e-3)

    def test_plywood_too_thin(self):
        """Compensato: t=8mm < 9mm."""
        ok, ratio = seismic_timber_panel_thickness("plywood", 8.0)
        assert ok is False

    def test_osb_single_ok(self):
        """OSB singolo: t=15mm (limite esatto)."""
        ok, ratio = seismic_timber_panel_thickness("osb", 15.0, osb_paired=False)
        assert ok is True
        assert_allclose(ratio, 1.0, rtol=1e-6)

    def test_osb_single_too_thin(self):
        """OSB singolo: t=12mm < 15mm."""
        ok, ratio = seismic_timber_panel_thickness("osb", 12.0, osb_paired=False)
        assert ok is False

    def test_osb_paired_ok(self):
        """OSB a coppia: t=12mm (limite esatto)."""
        ok, ratio = seismic_timber_panel_thickness("osb", 12.0, osb_paired=True)
        assert ok is True
        assert_allclose(ratio, 1.0, rtol=1e-6)

    def test_osb_paired_too_thin(self):
        """OSB a coppia: t=10mm < 12mm."""
        ok, ratio = seismic_timber_panel_thickness("osb", 10.0, osb_paired=True)
        assert ok is False

    def test_invalid_panel_type_raises(self):
        with pytest.raises(ValueError):
            seismic_timber_panel_thickness("steel", 10.0)

    def test_zero_thickness_raises(self):
        with pytest.raises(ValueError):
            seismic_timber_panel_thickness("plywood", 0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_timber_panel_thickness)
        assert ref is not None
        assert ref.article == "7.7.2"


# ── §7.7.7.1 — Limitazione diametro bulloni ─────────────────────────────────


class TestSeismicTimberBoltDiameterCheck:
    """NTC18 §7.7.7.1 — Diametro massimo bulloni in zona dissipativa."""

    def test_ok_within_limit(self):
        """d=16mm (limite esatto): ok."""
        ok, ratio = seismic_timber_bolt_diameter_check(16.0)
        assert ok is True
        assert_allclose(ratio, 1.0, rtol=1e-6)

    def test_ok_below_limit(self):
        """d=12mm < 16mm: ok."""
        ok, ratio = seismic_timber_bolt_diameter_check(12.0)
        assert ok is True
        assert_allclose(ratio, 12.0 / 16.0, rtol=1e-3)

    def test_exceed_limit(self):
        """d=20mm > 16mm: non ok."""
        ok, ratio = seismic_timber_bolt_diameter_check(20.0)
        assert ok is False
        assert_allclose(ratio, 20.0 / 16.0, rtol=1e-3)

    def test_closure_element_exempt(self):
        """Elemento di chiusura: d=24mm ma is_closure_element=True -> ok."""
        ok, ratio = seismic_timber_bolt_diameter_check(24.0, is_closure_element=True)
        assert ok is True
        assert_allclose(ratio, 24.0 / 16.0, rtol=1e-3)

    def test_zero_diameter_raises(self):
        with pytest.raises(ValueError):
            seismic_timber_bolt_diameter_check(0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_timber_bolt_diameter_check)
        assert ref is not None
        assert ref.article == "7.7.7.1"


# ── §7.7.7.2 — Rapporto h/b travi impalcato ─────────────────────────────────


class TestSeismicTimberBeamHbRatio:
    """NTC18 §7.7.7.2 — h/b <= 4 per travi senza controventi trasversali."""

    def test_satisfied_exactly(self):
        """h/b = 4.0: al limite, ok."""
        ok, ratio = seismic_timber_beam_hb_ratio(h=200.0, b=50.0)
        assert ok is True
        assert_allclose(ratio, 4.0, rtol=1e-6)

    def test_satisfied_below(self):
        """h/b = 3.0 < 4: ok."""
        ok, ratio = seismic_timber_beam_hb_ratio(h=150.0, b=50.0)
        assert ok is True
        assert_allclose(ratio, 3.0, rtol=1e-3)

    def test_not_satisfied(self):
        """h/b = 5.0 > 4: non ok."""
        ok, ratio = seismic_timber_beam_hb_ratio(h=250.0, b=50.0)
        assert ok is False
        assert_allclose(ratio, 5.0, rtol=1e-3)

    def test_square_section(self):
        """Sezione quadrata h/b = 1: sempre ok."""
        ok, ratio = seismic_timber_beam_hb_ratio(h=100.0, b=100.0)
        assert ok is True
        assert_allclose(ratio, 1.0, rtol=1e-6)

    def test_zero_b_raises(self):
        with pytest.raises(ValueError):
            seismic_timber_beam_hb_ratio(h=200.0, b=0.0)

    def test_zero_h_raises(self):
        with pytest.raises(ValueError):
            seismic_timber_beam_hb_ratio(h=0.0, b=50.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_timber_beam_hb_ratio)
        assert ref is not None
        assert ref.article == "7.7.7.2"


# ── §7.7.3.1 — Duttilita' statica zone dissipative ──────────────────────────


class TestSeismicTimberStaticDuctilityCheck:
    """NTC18 §7.7.3.1 — Duttilita' statica minima."""

    def test_cda_satisfied(self):
        """mu_s = 7 >= 6: ok per CD'A'."""
        ok, ratio = seismic_timber_static_ductility_check(mu_s=7.0, ductility_class="A")
        assert ok is True
        assert_allclose(ratio, 7.0 / 6.0, rtol=1e-3)

    def test_cda_not_satisfied(self):
        """mu_s = 5 < 6: non ok per CD'A'."""
        ok, ratio = seismic_timber_static_ductility_check(mu_s=5.0, ductility_class="A")
        assert ok is False
        assert_allclose(ratio, 5.0 / 6.0, rtol=1e-3)

    def test_cdb_satisfied(self):
        """mu_s = 5 >= 4: ok per CD'B'."""
        ok, ratio = seismic_timber_static_ductility_check(mu_s=5.0, ductility_class="B")
        assert ok is True
        assert_allclose(ratio, 5.0 / 4.0, rtol=1e-3)

    def test_cdb_not_satisfied(self):
        """mu_s = 3 < 4: non ok per CD'B'."""
        ok, ratio = seismic_timber_static_ductility_check(mu_s=3.0, ductility_class="B")
        assert ok is False
        assert_allclose(ratio, 3.0 / 4.0, rtol=1e-3)

    def test_cda_exact_boundary(self):
        """mu_s = 6.0 per CD'A': limite esatto, ok."""
        ok, ratio = seismic_timber_static_ductility_check(mu_s=6.0, ductility_class="A")
        assert ok is True
        assert_allclose(ratio, 1.0, rtol=1e-6)

    def test_cdb_exact_boundary(self):
        """mu_s = 4.0 per CD'B': limite esatto, ok."""
        ok, ratio = seismic_timber_static_ductility_check(mu_s=4.0, ductility_class="B")
        assert ok is True
        assert_allclose(ratio, 1.0, rtol=1e-6)

    def test_invalid_class_raises(self):
        with pytest.raises(ValueError):
            seismic_timber_static_ductility_check(mu_s=5.0, ductility_class="C")

    def test_zero_mu_raises(self):
        with pytest.raises(ValueError):
            seismic_timber_static_ductility_check(mu_s=0.0, ductility_class="B")

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_timber_static_ductility_check)
        assert ref is not None
        assert ref.article == "7.7.3.1"
