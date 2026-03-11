"""Test per timber — NTC18 §4.4."""

import pytest
import numpy as np
from numpy.testing import assert_allclose

from pyntc.checks.timber import (
    timber_partial_safety_factor,
    timber_kmod,
    timber_kdef,
    timber_design_strength,
    timber_long_term_modulus,
    timber_km_factor,
    timber_biaxial_bending_check,
    timber_tension_bending_check,
    timber_compression_bending_check,
    timber_tension_check,
    timber_compression_check,
    timber_compression_perp_check,
    timber_shear_check,
    timber_torsion_shape_factor,
    timber_torsion_check,
    timber_shear_torsion_interaction,
    timber_beam_critical_factor,
    timber_beam_stability_check,
    timber_column_relative_slenderness,
    timber_column_critical_factor,
    timber_column_stability_check,
    timber_deflection_limits,
    timber_straightness_limit,
)
from pyntc.core.reference import get_ntc_ref


# ---------------------------------------------------------------------------
# 1. timber_partial_safety_factor — Tab.4.4.III
# ---------------------------------------------------------------------------
class TestTimberPartialSafetyFactor:
    """NTC18 Tab.4.4.III — Coefficienti parziali gamma_M."""

    def test_solid_timber(self):
        assert_allclose(timber_partial_safety_factor("solid"), 1.50)

    def test_solid_timber_controlled(self):
        assert_allclose(
            timber_partial_safety_factor("solid", controlled=True), 1.45
        )

    def test_glulam(self):
        assert_allclose(timber_partial_safety_factor("glulam"), 1.45)

    def test_glulam_controlled(self):
        assert_allclose(
            timber_partial_safety_factor("glulam", controlled=True), 1.35
        )

    def test_lvl(self):
        assert_allclose(timber_partial_safety_factor("lvl"), 1.40)

    def test_lvl_controlled(self):
        assert_allclose(
            timber_partial_safety_factor("lvl", controlled=True), 1.30
        )

    def test_panels(self):
        assert_allclose(timber_partial_safety_factor("panels"), 1.50)

    def test_panels_controlled(self):
        assert_allclose(
            timber_partial_safety_factor("panels", controlled=True), 1.40
        )

    def test_connections(self):
        assert_allclose(timber_partial_safety_factor("connections"), 1.50)

    def test_connections_controlled(self):
        assert_allclose(
            timber_partial_safety_factor("connections", controlled=True), 1.40
        )

    def test_exceptional(self):
        assert_allclose(timber_partial_safety_factor("exceptional"), 1.00)

    def test_invalid_material(self):
        with pytest.raises(ValueError):
            timber_partial_safety_factor("steel")

    def test_ntc_ref(self):
        ref = get_ntc_ref(timber_partial_safety_factor)
        assert ref is not None
        assert ref.table == "4.4.III"


# ---------------------------------------------------------------------------
# 2. timber_kmod — Tab.4.4.IV
# ---------------------------------------------------------------------------
class TestTimberKmod:
    """NTC18 Tab.4.4.IV — Coefficiente di correzione k_mod."""

    def test_solid_sc1_permanent(self):
        assert_allclose(timber_kmod("solid", 1, "permanent"), 0.60)

    def test_solid_sc1_long_term(self):
        assert_allclose(timber_kmod("solid", 1, "long_term"), 0.70)

    def test_solid_sc1_medium_term(self):
        assert_allclose(timber_kmod("solid", 1, "medium_term"), 0.80)

    def test_solid_sc1_short_term(self):
        assert_allclose(timber_kmod("solid", 1, "short_term"), 0.90)

    def test_solid_sc1_instantaneous(self):
        assert_allclose(timber_kmod("solid", 1, "instantaneous"), 1.10)

    def test_solid_sc2_permanent(self):
        assert_allclose(timber_kmod("solid", 2, "permanent"), 0.60)

    def test_solid_sc2_medium_term(self):
        assert_allclose(timber_kmod("solid", 2, "medium_term"), 0.80)

    def test_solid_sc3_permanent(self):
        assert_allclose(timber_kmod("solid", 3, "permanent"), 0.50)

    def test_solid_sc3_short_term(self):
        assert_allclose(timber_kmod("solid", 3, "short_term"), 0.70)

    def test_glulam_sc1_permanent(self):
        assert_allclose(timber_kmod("glulam", 1, "permanent"), 0.60)

    def test_glulam_sc1_instantaneous(self):
        assert_allclose(timber_kmod("glulam", 1, "instantaneous"), 1.10)

    def test_glulam_sc3_permanent(self):
        assert_allclose(timber_kmod("glulam", 3, "permanent"), 0.50)

    def test_lvl_sc1_permanent(self):
        assert_allclose(timber_kmod("lvl", 1, "permanent"), 0.60)

    def test_lvl_sc2_short_term(self):
        assert_allclose(timber_kmod("lvl", 2, "short_term"), 0.90)

    def test_panels_plywood_sc1_permanent(self):
        assert_allclose(timber_kmod("plywood", 1, "permanent"), 0.60)

    def test_panels_plywood_sc1_short_term(self):
        assert_allclose(timber_kmod("plywood", 1, "short_term"), 0.90)

    def test_panels_osb3_sc1_permanent(self):
        assert_allclose(timber_kmod("osb3", 1, "permanent"), 0.40)

    def test_panels_osb3_sc2_short_term(self):
        assert_allclose(timber_kmod("osb3", 2, "short_term"), 0.70)

    def test_panels_particleboard_sc1_permanent(self):
        assert_allclose(timber_kmod("particleboard", 1, "permanent"), 0.30)

    def test_panels_fibreboard_hard_sc1_permanent(self):
        assert_allclose(timber_kmod("fibreboard_hard", 1, "permanent"), 0.30)

    def test_invalid_service_class(self):
        with pytest.raises(ValueError):
            timber_kmod("solid", 4, "permanent")

    def test_invalid_duration(self):
        with pytest.raises(ValueError):
            timber_kmod("solid", 1, "very_long")

    def test_invalid_material(self):
        with pytest.raises(ValueError):
            timber_kmod("steel", 1, "permanent")

    def test_ntc_ref(self):
        ref = get_ntc_ref(timber_kmod)
        assert ref is not None
        assert ref.table == "4.4.IV"


# ---------------------------------------------------------------------------
# 3. timber_kdef — Tab.4.4.V
# ---------------------------------------------------------------------------
class TestTimberKdef:
    """NTC18 Tab.4.4.V — Coefficiente di deformazione k_def."""

    def test_solid_sc1(self):
        assert_allclose(timber_kdef("solid", 1), 0.60)

    def test_solid_sc2(self):
        assert_allclose(timber_kdef("solid", 2), 0.80)

    def test_solid_sc3(self):
        assert_allclose(timber_kdef("solid", 3), 2.00)

    def test_glulam_sc1(self):
        assert_allclose(timber_kdef("glulam", 1), 0.60)

    def test_glulam_sc3(self):
        assert_allclose(timber_kdef("glulam", 3), 2.00)

    def test_lvl_sc1(self):
        assert_allclose(timber_kdef("lvl", 1), 0.60)

    def test_lvl_sc2(self):
        assert_allclose(timber_kdef("lvl", 2), 0.80)

    def test_plywood_sc1(self):
        assert_allclose(timber_kdef("plywood", 1), 0.80)

    def test_plywood_sc2(self):
        assert_allclose(timber_kdef("plywood", 2), 1.00)

    def test_plywood_sc3(self):
        assert_allclose(timber_kdef("plywood", 3), 2.50)

    def test_osb3_sc1(self):
        assert_allclose(timber_kdef("osb3", 1), 1.50)

    def test_osb3_sc2(self):
        assert_allclose(timber_kdef("osb3", 2), 2.25)

    def test_particleboard_sc1(self):
        assert_allclose(timber_kdef("particleboard", 1), 2.25)

    def test_fibreboard_hard_sc1(self):
        assert_allclose(timber_kdef("fibreboard_hard", 1), 2.25)

    def test_invalid_service_class(self):
        with pytest.raises(ValueError):
            timber_kdef("solid", 4)

    def test_invalid_material(self):
        with pytest.raises(ValueError):
            timber_kdef("steel", 1)

    def test_ntc_ref(self):
        ref = get_ntc_ref(timber_kdef)
        assert ref is not None
        assert ref.table == "4.4.V"


# ---------------------------------------------------------------------------
# 4. timber_design_strength — [4.4.1]
# ---------------------------------------------------------------------------
class TestTimberDesignStrength:
    """NTC18 [4.4.1] — X_d = k_mod * X_k / gamma_M."""

    def test_basic(self):
        # X_k=24 MPa, k_mod=0.8, gamma_M=1.45
        expected = 0.8 * 24.0 / 1.45
        assert_allclose(timber_design_strength(24.0, 0.8, 1.45), expected, rtol=1e-6)

    def test_unit_kmod(self):
        # k_mod=1.0 => X_d = X_k / gamma_M
        assert_allclose(timber_design_strength(30.0, 1.0, 1.50), 20.0, rtol=1e-6)

    def test_zero_Xk(self):
        assert_allclose(timber_design_strength(0.0, 0.8, 1.45), 0.0)

    def test_negative_Xk_raises(self):
        with pytest.raises(ValueError):
            timber_design_strength(-10.0, 0.8, 1.45)

    def test_zero_gamma_raises(self):
        with pytest.raises(ValueError):
            timber_design_strength(24.0, 0.8, 0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(timber_design_strength)
        assert ref is not None
        assert ref.formula == "4.4.1"


# ---------------------------------------------------------------------------
# 5. timber_long_term_modulus — §4.4.7
# ---------------------------------------------------------------------------
class TestTimberLongTermModulus:
    """NTC18 §4.4.7 — E_fin = E_mean / (1 + k_def)."""

    def test_basic(self):
        # E=12000 MPa, k_def=0.60 => 12000/1.60 = 7500
        assert_allclose(timber_long_term_modulus(12000.0, 0.60), 7500.0, rtol=1e-6)

    def test_zero_kdef(self):
        assert_allclose(timber_long_term_modulus(12000.0, 0.0), 12000.0)

    def test_large_kdef(self):
        assert_allclose(timber_long_term_modulus(12000.0, 2.0), 4000.0, rtol=1e-6)

    def test_ntc_ref(self):
        ref = get_ntc_ref(timber_long_term_modulus)
        assert ref is not None
        assert ref.article == "4.4.7"


# ---------------------------------------------------------------------------
# 6. timber_km_factor — §4.4.8.1.6
# ---------------------------------------------------------------------------
class TestTimberKmFactor:
    """NTC18 §4.4.8.1.6 — k_m per flessione deviata."""

    def test_rectangular(self):
        assert_allclose(timber_km_factor("rectangular"), 0.7)

    def test_circular(self):
        assert_allclose(timber_km_factor("circular"), 1.0)

    def test_other(self):
        assert_allclose(timber_km_factor("other"), 1.0)

    def test_invalid(self):
        with pytest.raises(ValueError):
            timber_km_factor("hexagonal")

    def test_ntc_ref(self):
        ref = get_ntc_ref(timber_km_factor)
        assert ref is not None
        assert ref.article == "4.4.8.1.6"


# ---------------------------------------------------------------------------
# 7. timber_biaxial_bending_check — [4.4.5a/b]
# ---------------------------------------------------------------------------
class TestTimberBiaxialBendingCheck:
    """NTC18 [4.4.5a/b] — Verifica flessione deviata."""

    def test_safe(self):
        # sigma_y=5, f_y=20, sigma_z=3, f_z=20, k_m=0.7
        # eq_a: 5/20 + 0.7*3/20 = 0.25+0.105=0.355
        # eq_b: 0.7*5/20 + 3/20 = 0.175+0.15=0.325
        ok, ratio = timber_biaxial_bending_check(5.0, 20.0, 3.0, 20.0, 0.7)
        assert ok is True
        assert_allclose(ratio, 0.355, rtol=1e-3)

    def test_unsafe(self):
        ok, ratio = timber_biaxial_bending_check(18.0, 20.0, 15.0, 20.0, 0.7)
        assert ok is False
        assert ratio > 1.0

    def test_uniaxial_y(self):
        # sigma_z = 0 => ratio = sigma_y/f_y
        ok, ratio = timber_biaxial_bending_check(10.0, 20.0, 0.0, 20.0, 0.7)
        assert ok is True
        assert_allclose(ratio, 0.5, rtol=1e-6)

    def test_uniaxial_z(self):
        ok, ratio = timber_biaxial_bending_check(0.0, 20.0, 10.0, 20.0, 0.7)
        assert ok is True
        assert_allclose(ratio, 0.5, rtol=1e-6)

    def test_km_1(self):
        # k_m=1.0, sigma_y=10, sigma_z=10, f=20
        # eq_a = eq_b = 10/20 + 1.0*10/20 = 1.0
        ok, ratio = timber_biaxial_bending_check(10.0, 20.0, 10.0, 20.0, 1.0)
        assert ok is True
        assert_allclose(ratio, 1.0, rtol=1e-6)

    def test_ntc_ref(self):
        ref = get_ntc_ref(timber_biaxial_bending_check)
        assert ref is not None
        assert ref.formula == "4.4.5"


# ---------------------------------------------------------------------------
# 8. timber_tension_bending_check — [4.4.6a/b]
# ---------------------------------------------------------------------------
class TestTimberTensionBendingCheck:
    """NTC18 [4.4.6a/b] — Verifica tensoflessione."""

    def test_safe(self):
        # sigma_t=2, f_t=14, sigma_y=5, f_y=20, sigma_z=3, f_z=20, k_m=0.7
        # eq_a: 2/14 + 5/20 + 0.7*3/20 = 0.143+0.25+0.105 = 0.498
        ok, ratio = timber_tension_bending_check(2.0, 14.0, 5.0, 20.0, 3.0, 20.0, 0.7)
        assert ok is True
        assert_allclose(ratio, 0.498, rtol=1e-2)

    def test_unsafe(self):
        ok, ratio = timber_tension_bending_check(10.0, 14.0, 15.0, 20.0, 10.0, 20.0, 0.7)
        assert ok is False

    def test_no_bending(self):
        # Solo trazione pura
        ok, ratio = timber_tension_bending_check(7.0, 14.0, 0.0, 20.0, 0.0, 20.0, 0.7)
        assert ok is True
        assert_allclose(ratio, 0.5, rtol=1e-6)

    def test_ntc_ref(self):
        ref = get_ntc_ref(timber_tension_bending_check)
        assert ref is not None
        assert ref.formula == "4.4.6"


# ---------------------------------------------------------------------------
# 9. timber_compression_bending_check — [4.4.7a/b]
# ---------------------------------------------------------------------------
class TestTimberCompressionBendingCheck:
    """NTC18 [4.4.7a/b] — Verifica pressoflessione (termine compressione al quadrato)."""

    def test_safe(self):
        # sigma_c=5, f_c=20 => (5/20)^2 = 0.0625
        # sigma_y=5, f_y=20, sigma_z=3, f_z=20, k_m=0.7
        # eq_a: 0.0625 + 0.25 + 0.105 = 0.4175
        ok, ratio = timber_compression_bending_check(5.0, 20.0, 5.0, 20.0, 3.0, 20.0, 0.7)
        assert ok is True
        assert_allclose(ratio, 0.4175, rtol=1e-3)

    def test_compression_squared(self):
        # Verifica che il termine di compressione sia effettivamente al quadrato
        # sigma_c=10, f_c=20 => (10/20)^2 = 0.25 (NON 0.5 se fosse lineare)
        ok, ratio = timber_compression_bending_check(10.0, 20.0, 0.0, 20.0, 0.0, 20.0, 0.7)
        assert ok is True
        assert_allclose(ratio, 0.25, rtol=1e-6)

    def test_unsafe(self):
        ok, ratio = timber_compression_bending_check(18.0, 20.0, 15.0, 20.0, 10.0, 20.0, 0.7)
        assert ok is False

    def test_pure_compression(self):
        # Solo compressione
        ok, ratio = timber_compression_bending_check(15.0, 20.0, 0.0, 20.0, 0.0, 20.0, 0.7)
        assert ok is True
        assert_allclose(ratio, (15.0 / 20.0) ** 2, rtol=1e-6)

    def test_ntc_ref(self):
        ref = get_ntc_ref(timber_compression_bending_check)
        assert ref is not None
        assert ref.formula == "4.4.7"


# ---------------------------------------------------------------------------
# 10. timber_shear_check — [4.4.8]
# ---------------------------------------------------------------------------
class TestTimberShearCheck:
    """NTC18 [4.4.8] — tau_d <= f_v,d."""

    def test_safe(self):
        ok, ratio = timber_shear_check(1.5, 3.0)
        assert ok is True
        assert_allclose(ratio, 0.5, rtol=1e-6)

    def test_limit(self):
        ok, ratio = timber_shear_check(3.0, 3.0)
        assert ok is True
        assert_allclose(ratio, 1.0, rtol=1e-6)

    def test_unsafe(self):
        ok, ratio = timber_shear_check(4.0, 3.0)
        assert ok is False
        assert_allclose(ratio, 4.0 / 3.0, rtol=1e-6)

    def test_ntc_ref(self):
        ref = get_ntc_ref(timber_shear_check)
        assert ref is not None
        assert ref.formula == "4.4.8"


# ---------------------------------------------------------------------------
# 11. timber_torsion_shape_factor — §4.4.8.1.10
# ---------------------------------------------------------------------------
class TestTimberTorsionShapeFactor:
    """NTC18 §4.4.8.1.10 — k_sh per torsione."""

    def test_circular(self):
        assert_allclose(timber_torsion_shape_factor("circular"), 1.2)

    def test_rectangular_square(self):
        # h/b = 1 => 1 + 0.15*1 = 1.15
        assert_allclose(timber_torsion_shape_factor("rectangular", h=200.0, b=200.0), 1.15, rtol=1e-3)

    def test_rectangular_tall(self):
        # h/b = 3 => 1 + 0.15*3 = 1.45
        assert_allclose(timber_torsion_shape_factor("rectangular", h=300.0, b=100.0), 1.45, rtol=1e-3)

    def test_rectangular_capped(self):
        # h/b = 10 => 1 + 0.15*10 = 2.50 => capped at 2.0
        assert_allclose(timber_torsion_shape_factor("rectangular", h=1000.0, b=100.0), 2.0, rtol=1e-3)

    def test_other(self):
        assert_allclose(timber_torsion_shape_factor("other"), 1.0)

    def test_rectangular_missing_dims(self):
        with pytest.raises(ValueError):
            timber_torsion_shape_factor("rectangular")

    def test_ntc_ref(self):
        ref = get_ntc_ref(timber_torsion_shape_factor)
        assert ref is not None
        assert ref.article == "4.4.8.1.10"


# ---------------------------------------------------------------------------
# 12. timber_torsion_check — [4.4.9]
# ---------------------------------------------------------------------------
class TestTimberTorsionCheck:
    """NTC18 [4.4.9] — tau_tor,d <= k_sh * f_v,d."""

    def test_safe(self):
        ok, ratio = timber_torsion_check(2.0, 3.0, 1.2)
        assert ok is True
        assert_allclose(ratio, 2.0 / (1.2 * 3.0), rtol=1e-6)

    def test_unsafe(self):
        ok, ratio = timber_torsion_check(5.0, 3.0, 1.0)
        assert ok is False

    def test_ntc_ref(self):
        ref = get_ntc_ref(timber_torsion_check)
        assert ref is not None
        assert ref.formula == "4.4.9"


# ---------------------------------------------------------------------------
# 13. timber_shear_torsion_interaction — [4.4.10]
# ---------------------------------------------------------------------------
class TestTimberShearTorsionInteraction:
    """NTC18 [4.4.10] — Interazione taglio-torsione."""

    def test_safe(self):
        # (tau_tor / (k_sh*f_v))^2 + (tau_d / f_v)^2 <= 1
        # tau_tor=1, f_v=3, k_sh=1.2: (1/(1.2*3))^2 = (1/3.6)^2 = 0.0772
        # tau_d=1, f_v=3: (1/3)^2 = 0.1111
        # total = 0.1883
        ok, ratio = timber_shear_torsion_interaction(1.0, 3.0, 1.0, 1.2)
        assert ok is True
        assert ratio < 1.0

    def test_unsafe(self):
        ok, ratio = timber_shear_torsion_interaction(3.0, 3.0, 3.0, 1.0)
        assert ok is False

    def test_pure_shear(self):
        # tau_tor=0 => (tau_d/f_v)^2
        ok, ratio = timber_shear_torsion_interaction(2.0, 3.0, 0.0, 1.2)
        assert ok is True
        assert_allclose(ratio, (2.0 / 3.0) ** 2, rtol=1e-6)

    def test_pure_torsion(self):
        # tau_d=0 => (tau_tor/(k_sh*f_v))^2
        ok, ratio = timber_shear_torsion_interaction(0.0, 3.0, 2.0, 1.2)
        assert ok is True
        assert_allclose(ratio, (2.0 / (1.2 * 3.0)) ** 2, rtol=1e-6)

    def test_ntc_ref(self):
        ref = get_ntc_ref(timber_shear_torsion_interaction)
        assert ref is not None
        assert ref.formula == "4.4.10"


# ---------------------------------------------------------------------------
# 14. timber_beam_critical_factor — [4.4.12]
# ---------------------------------------------------------------------------
class TestTimberBeamCriticalFactor:
    """NTC18 [4.4.12] — k_crit,m per instabilita' trave."""

    def test_low_slenderness(self):
        # lambda_rel_m <= 0.75 => k_crit = 1.0
        assert_allclose(timber_beam_critical_factor(0.5), 1.0)

    def test_boundary_075(self):
        assert_allclose(timber_beam_critical_factor(0.75), 1.0)

    def test_mid_range(self):
        # 0.75 < lambda <= 1.4 => 1.56 - 0.75*lambda
        # lambda=1.0 => 1.56 - 0.75 = 0.81
        assert_allclose(timber_beam_critical_factor(1.0), 0.81, rtol=1e-6)

    def test_boundary_14(self):
        # lambda=1.4 => 1.56 - 0.75*1.4 = 1.56-1.05 = 0.51
        assert_allclose(timber_beam_critical_factor(1.4), 0.51, rtol=1e-6)

    def test_high_slenderness(self):
        # lambda > 1.4 => 1/lambda^2
        # lambda=2.0 => 1/4 = 0.25
        assert_allclose(timber_beam_critical_factor(2.0), 0.25, rtol=1e-6)

    def test_very_high(self):
        # lambda=3.0 => 1/9
        assert_allclose(timber_beam_critical_factor(3.0), 1.0 / 9.0, rtol=1e-6)

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            timber_beam_critical_factor(-0.5)

    def test_ntc_ref(self):
        ref = get_ntc_ref(timber_beam_critical_factor)
        assert ref is not None
        assert ref.formula == "4.4.12"


# ---------------------------------------------------------------------------
# 15. timber_beam_stability_check — [4.4.11]
# ---------------------------------------------------------------------------
class TestTimberBeamStabilityCheck:
    """NTC18 [4.4.11] — sigma_m,d / (k_crit,m * f_m,d) <= 1."""

    def test_safe(self):
        # sigma=5, f_m=20, lambda_rel=0.5 => k_crit=1.0
        # ratio = 5/(1.0*20) = 0.25
        ok, ratio = timber_beam_stability_check(5.0, 20.0, 0.5)
        assert ok is True
        assert_allclose(ratio, 0.25, rtol=1e-3)

    def test_unsafe(self):
        ok, ratio = timber_beam_stability_check(15.0, 20.0, 2.0)
        assert ok is False

    def test_at_limit(self):
        # sigma=5, f_m=20, lambda_rel=1.0 => k_crit=0.81
        # ratio = 5/(0.81*20) = 0.3086
        ok, ratio = timber_beam_stability_check(5.0, 20.0, 1.0)
        assert ok is True
        assert_allclose(ratio, 5.0 / (0.81 * 20.0), rtol=1e-3)

    def test_ntc_ref(self):
        ref = get_ntc_ref(timber_beam_stability_check)
        assert ref is not None
        assert ref.formula == "4.4.11"


# ---------------------------------------------------------------------------
# 16. timber_column_relative_slenderness — [4.4.14]
# ---------------------------------------------------------------------------
class TestTimberColumnRelativeSlenderness:
    """NTC18 [4.4.14] — lambda_rel,c = (lambda/pi) * sqrt(f_c,0,k / E_0,05)."""

    def test_basic(self):
        # lambda=100, f_c=21 MPa, E_005=7400 MPa
        # (100/pi)*sqrt(21/7400) = 31.831*0.05325 = 1.695
        expected = (100.0 / np.pi) * np.sqrt(21.0 / 7400.0)
        result = timber_column_relative_slenderness(100.0, 21.0, 7400.0)
        assert_allclose(result, expected, rtol=1e-6)

    def test_low_slenderness(self):
        # lambda=20, f_c=21, E=7400
        expected = (20.0 / np.pi) * np.sqrt(21.0 / 7400.0)
        result = timber_column_relative_slenderness(20.0, 21.0, 7400.0)
        assert_allclose(result, expected, rtol=1e-6)

    def test_negative_lambda_raises(self):
        with pytest.raises(ValueError):
            timber_column_relative_slenderness(-10.0, 21.0, 7400.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(timber_column_relative_slenderness)
        assert ref is not None
        assert ref.formula == "4.4.14"


# ---------------------------------------------------------------------------
# 17. timber_column_critical_factor — [4.4.15]/[4.4.16]
# ---------------------------------------------------------------------------
class TestTimberColumnCriticalFactor:
    """NTC18 [4.4.15]/[4.4.16] — k_crit,c per instabilita' colonna."""

    def test_low_slenderness(self):
        # lambda_rel <= 0.3 => k_crit = 1.0
        assert_allclose(timber_column_critical_factor(0.2, material="solid"), 1.0)

    def test_boundary_03(self):
        assert_allclose(timber_column_critical_factor(0.3, material="solid"), 1.0)

    def test_solid_timber(self):
        # lambda_rel=1.0, beta_c=0.2
        # k = 0.5*(1 + 0.2*(1.0-0.3) + 1.0^2) = 0.5*(1+0.14+1) = 1.07
        # k_crit = 1/(1.07 + sqrt(1.07^2 - 1.0^2)) = 1/(1.07 + sqrt(1.1449-1))
        # = 1/(1.07 + sqrt(0.1449)) = 1/(1.07+0.3806) = 1/1.4506 = 0.6894
        k = 0.5 * (1.0 + 0.2 * (1.0 - 0.3) + 1.0**2)
        expected = 1.0 / (k + np.sqrt(k**2 - 1.0**2))
        result = timber_column_critical_factor(1.0, material="solid")
        assert_allclose(result, expected, rtol=1e-4)

    def test_glulam(self):
        # lambda_rel=1.0, beta_c=0.1
        # k = 0.5*(1 + 0.1*(1.0-0.3) + 1.0^2) = 0.5*(1+0.07+1) = 1.035
        # k_crit = 1/(1.035 + sqrt(1.035^2 - 1.0^2))
        k = 0.5 * (1.0 + 0.1 * (1.0 - 0.3) + 1.0**2)
        expected = 1.0 / (k + np.sqrt(k**2 - 1.0**2))
        result = timber_column_critical_factor(1.0, material="glulam")
        assert_allclose(result, expected, rtol=1e-4)

    def test_high_slenderness(self):
        # lambda_rel=2.0, beta_c=0.2 (solid)
        # k = 0.5*(1 + 0.2*(2.0-0.3) + 4) = 0.5*(1+0.34+4) = 2.67
        # k_crit = 1/(2.67 + sqrt(2.67^2 - 4)) = 1/(2.67+sqrt(7.1289-4))
        # = 1/(2.67+sqrt(3.1289)) = 1/(2.67+1.769) = 1/4.439 = 0.2253
        k = 0.5 * (1.0 + 0.2 * (2.0 - 0.3) + 2.0**2)
        expected = 1.0 / (k + np.sqrt(k**2 - 2.0**2))
        result = timber_column_critical_factor(2.0, material="solid")
        assert_allclose(result, expected, rtol=1e-4)

    def test_glulam_better_than_solid(self):
        # Con stessa snellezza, glulam ha k_crit maggiore (meno imperfezioni)
        k_solid = timber_column_critical_factor(1.5, material="solid")
        k_glulam = timber_column_critical_factor(1.5, material="glulam")
        assert k_glulam > k_solid

    def test_ntc_ref(self):
        ref = get_ntc_ref(timber_column_critical_factor)
        assert ref is not None
        assert ref.formula == "4.4.15"


# ---------------------------------------------------------------------------
# 18. timber_column_stability_check — [4.4.13]
# ---------------------------------------------------------------------------
class TestTimberColumnStabilityCheck:
    """NTC18 [4.4.13] — sigma_c,0,d / (k_crit,c * f_c,0,d) <= 1."""

    def test_safe(self):
        # sigma_c=5, f_c=20, k_crit=0.7
        ok, ratio = timber_column_stability_check(5.0, 20.0, 0.7)
        assert ok is True
        assert_allclose(ratio, 5.0 / (0.7 * 20.0), rtol=1e-6)

    def test_unsafe(self):
        ok, ratio = timber_column_stability_check(18.0, 20.0, 0.5)
        assert ok is False

    def test_full_strength(self):
        # k_crit=1.0 => ratio = sigma/f
        ok, ratio = timber_column_stability_check(10.0, 20.0, 1.0)
        assert ok is True
        assert_allclose(ratio, 0.5, rtol=1e-6)

    def test_ntc_ref(self):
        ref = get_ntc_ref(timber_column_stability_check)
        assert ref is not None
        assert ref.formula == "4.4.13"


# ---------------------------------------------------------------------------
# 19. timber_deflection_limits — §4.4.7
# ---------------------------------------------------------------------------
class TestTimberDeflectionLimits:
    """NTC18 §4.4.7 — Limiti di deformabilita'."""

    def test_beam_instantaneous(self):
        # L/300 per freccia istantanea
        limit = timber_deflection_limits(6000.0, "instantaneous")
        assert_allclose(limit, 20.0, rtol=1e-6)

    def test_beam_final(self):
        # L/200 per freccia finale (quasi-permanente)
        limit = timber_deflection_limits(6000.0, "final")
        assert_allclose(limit, 30.0, rtol=1e-6)

    def test_cantilever_instantaneous(self):
        # L/150 per mensola istantanea
        limit = timber_deflection_limits(3000.0, "instantaneous", cantilever=True)
        assert_allclose(limit, 20.0, rtol=1e-6)

    def test_cantilever_final(self):
        # L/100 per mensola finale
        limit = timber_deflection_limits(3000.0, "final", cantilever=True)
        assert_allclose(limit, 30.0, rtol=1e-6)

    def test_invalid_type(self):
        with pytest.raises(ValueError):
            timber_deflection_limits(6000.0, "creep")

    def test_ntc_ref(self):
        ref = get_ntc_ref(timber_deflection_limits)
        assert ref is not None
        assert ref.article == "4.4.7"


# ---------------------------------------------------------------------------
# 20. timber_straightness_limit — §4.4.15
# ---------------------------------------------------------------------------
class TestTimberStraightnessLimit:
    """NTC18 §4.4.15 — Limite rettilineita'."""

    def test_glulam(self):
        # 1/500 per legno lamellare
        assert_allclose(timber_straightness_limit(5000.0, "glulam"), 10.0, rtol=1e-6)

    def test_solid(self):
        # 1/300 per legno massiccio
        assert_allclose(timber_straightness_limit(3000.0, "solid"), 10.0, rtol=1e-6)

    def test_invalid(self):
        with pytest.raises(ValueError):
            timber_straightness_limit(5000.0, "steel")

    def test_ntc_ref(self):
        ref = get_ntc_ref(timber_straightness_limit)
        assert ref is not None
        assert ref.article == "4.4.15"


# ---------------------------------------------------------------------------
# 21. timber_tension_check — [4.4.2]
# ---------------------------------------------------------------------------
class TestTimberTensionCheck:
    """NTC18 [4.4.2] — Verifica a trazione parallela."""

    def test_safe(self):
        ok, ratio = timber_tension_check(8.0, 10.0)
        assert ok is True
        assert_allclose(ratio, 0.8, rtol=1e-6)

    def test_limit(self):
        ok, ratio = timber_tension_check(10.0, 10.0)
        assert ok is True
        assert_allclose(ratio, 1.0, rtol=1e-6)

    def test_unsafe(self):
        ok, ratio = timber_tension_check(12.0, 10.0)
        assert ok is False
        assert_allclose(ratio, 1.2, rtol=1e-6)

    def test_ntc_ref(self):
        ref = get_ntc_ref(timber_tension_check)
        assert ref is not None
        assert ref.article == "4.4.8.1.1"
        assert ref.formula == "4.4.2"


# ---------------------------------------------------------------------------
# 22. timber_compression_check — [4.4.3]
# ---------------------------------------------------------------------------
class TestTimberCompressionCheck:
    """NTC18 [4.4.3] — Verifica a compressione parallela."""

    def test_safe(self):
        ok, ratio = timber_compression_check(15.0, 20.0)
        assert ok is True
        assert_allclose(ratio, 0.75, rtol=1e-6)

    def test_limit(self):
        ok, ratio = timber_compression_check(20.0, 20.0)
        assert ok is True
        assert_allclose(ratio, 1.0, rtol=1e-6)

    def test_unsafe(self):
        ok, ratio = timber_compression_check(25.0, 20.0)
        assert ok is False
        assert_allclose(ratio, 1.25, rtol=1e-6)

    def test_ntc_ref(self):
        ref = get_ntc_ref(timber_compression_check)
        assert ref is not None
        assert ref.article == "4.4.8.1.3"
        assert ref.formula == "4.4.3"


# ---------------------------------------------------------------------------
# 23. timber_compression_perp_check — [4.4.4]
# ---------------------------------------------------------------------------
class TestTimberCompressionPerpCheck:
    """NTC18 [4.4.4] — Verifica a compressione perpendicolare."""

    def test_safe_default_kc90(self):
        ok, ratio = timber_compression_perp_check(2.0, 3.0)
        assert ok is True
        assert_allclose(ratio, 2.0 / 3.0, rtol=1e-6)

    def test_safe_with_kc90(self):
        # sigma=2.5, f=2.0, kc90=1.5 → ratio = 2.5/(1.5*2.0) = 0.833
        ok, ratio = timber_compression_perp_check(2.5, 2.0, k_c_90=1.5)
        assert ok is True
        assert_allclose(ratio, 2.5 / 3.0, rtol=1e-6)

    def test_unsafe(self):
        ok, ratio = timber_compression_perp_check(4.0, 3.0, k_c_90=1.0)
        assert ok is False
        assert_allclose(ratio, 4.0 / 3.0, rtol=1e-6)

    def test_limit(self):
        ok, ratio = timber_compression_perp_check(3.0, 2.0, k_c_90=1.5)
        assert ok is True
        assert_allclose(ratio, 1.0, rtol=1e-6)

    def test_ntc_ref(self):
        ref = get_ntc_ref(timber_compression_perp_check)
        assert ref is not None
        assert ref.article == "4.4.8.1.4"
        assert ref.formula == "4.4.4"
