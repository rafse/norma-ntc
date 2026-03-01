"""Test per actions/fire — NTC18 §3.6.

Copre:
- [3.6.1]         — carico d'incendio specifico di progetto
- [3.6.2]         — curva nominale standard ISO 834
- [3.6.3]         — curva nominale idrocarburi
- [3.6.4]         — curva nominale esterna
- [3.6.5a],[3.6.5b] — pressione statica equivalente esplosioni
- Tab. 3.6.III    — forze statiche equivalenti urti veicoli
- [3.6.9]         — forza urto carrello elevatore
"""

import math

import numpy as np
import pytest
from numpy.testing import assert_allclose

from pyntc.actions.fire import (
    fire_standard_curve,
    fire_hydrocarbon_curve,
    fire_external_curve,
    fire_design_load,
    explosion_equivalent_pressure,
    impact_vehicle_force,
    impact_forklift_force,
)
from pyntc.core.reference import get_ntc_ref


# ── [3.6.2] — Curva nominale standard ISO 834 ───────────────────────────────

class TestFireStandardCurve:
    """NTC18 §3.6.1.5.1, Formula [3.6.2] — theta = 20 + 345*log10(8t+1)."""

    def test_t_zero(self):
        """A t=0, theta = 20°C (temperatura ambiente)."""
        assert_allclose(fire_standard_curve(0.0), 20.0, rtol=1e-3)

    def test_t_30(self):
        """A t=30min, theta = 20 + 345*log10(241) ≈ 841.8°C."""
        expected = 20.0 + 345.0 * math.log10(8.0 * 30.0 + 1.0)
        assert_allclose(fire_standard_curve(30.0), expected, rtol=1e-3)

    def test_t_60(self):
        """A t=60min, theta = 20 + 345*log10(481) ≈ 945.3°C."""
        expected = 20.0 + 345.0 * math.log10(8.0 * 60.0 + 1.0)
        assert_allclose(fire_standard_curve(60.0), expected, rtol=1e-3)

    def test_t_120(self):
        """A t=120min."""
        expected = 20.0 + 345.0 * math.log10(8.0 * 120.0 + 1.0)
        assert_allclose(fire_standard_curve(120.0), expected, rtol=1e-3)

    def test_array(self):
        """Accetta array numpy."""
        t = np.array([0.0, 30.0, 60.0])
        result = fire_standard_curve(t)
        assert result.shape == (3,)
        assert_allclose(result[0], 20.0, rtol=1e-3)

    def test_t_negativo(self):
        with pytest.raises(ValueError):
            fire_standard_curve(-1.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(fire_standard_curve)
        assert ref is not None
        assert ref.formula == "3.6.2"


# ── [3.6.3] — Curva nominale idrocarburi ─────────────────────────────────────

class TestFireHydrocarbonCurve:
    """NTC18 §3.6.1.5.1, Formula [3.6.3]."""

    def test_t_zero(self):
        """A t=0, theta = 20°C."""
        assert_allclose(fire_hydrocarbon_curve(0.0), 20.0, rtol=1e-3)

    def test_t_30(self):
        """A t=30min, verifica con formula esplicita."""
        t = 30.0
        expected = 1080.0 * (1.0 - 0.325 * math.exp(-0.167 * t)
                             - 0.675 * math.exp(-2.5 * t)) + 20.0
        assert_allclose(fire_hydrocarbon_curve(t), expected, rtol=1e-3)

    def test_asintotico(self):
        """Per t molto grande, theta -> 1080 + 20 = 1100°C."""
        result = fire_hydrocarbon_curve(600.0)
        assert_allclose(result, 1100.0, rtol=1e-2)

    def test_array(self):
        t = np.array([0.0, 30.0, 60.0])
        result = fire_hydrocarbon_curve(t)
        assert result.shape == (3,)

    def test_t_negativo(self):
        with pytest.raises(ValueError):
            fire_hydrocarbon_curve(-1.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(fire_hydrocarbon_curve)
        assert ref is not None
        assert ref.formula == "3.6.3"


# ── [3.6.4] — Curva nominale esterna ─────────────────────────────────────────

class TestFireExternalCurve:
    """NTC18 §3.6.1.5.1, Formula [3.6.4]."""

    def test_t_zero(self):
        """A t=0, theta = 20°C."""
        assert_allclose(fire_external_curve(0.0), 20.0, rtol=1e-3)

    def test_t_30(self):
        t = 30.0
        expected = 660.0 * (1.0 - 0.687 * math.exp(-0.32 * t)
                            - 0.313 * math.exp(-3.8 * t)) + 20.0
        assert_allclose(fire_external_curve(t), expected, rtol=1e-3)

    def test_asintotico(self):
        """Per t molto grande, theta -> 660 + 20 = 680°C."""
        result = fire_external_curve(600.0)
        assert_allclose(result, 680.0, rtol=1e-2)

    def test_array(self):
        t = np.array([0.0, 30.0, 60.0])
        result = fire_external_curve(t)
        assert result.shape == (3,)

    def test_t_negativo(self):
        with pytest.raises(ValueError):
            fire_external_curve(-1.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(fire_external_curve)
        assert ref is not None
        assert ref.formula == "3.6.4"


# ── [3.6.1] — Carico d'incendio specifico di progetto ───────────────────────

class TestFireDesignLoad:
    """NTC18 §3.6.1.1, Formula [3.6.1] — q_{f,d} = q_f * dq1 * dq2 * dn."""

    def test_formula_base(self):
        """q_f=600, dq1=1.2, dq2=1.0, dn=0.6 -> 432 MJ/m²."""
        result = fire_design_load(q_f=600.0, delta_q1=1.2, delta_q2=1.0,
                                  delta_n=0.6)
        assert_allclose(result, 432.0, rtol=1e-3)

    def test_valori_unitari(self):
        """Con tutti i delta=1, q_{f,d} = q_f."""
        result = fire_design_load(q_f=500.0, delta_q1=1.0, delta_q2=1.0,
                                  delta_n=1.0)
        assert_allclose(result, 500.0, rtol=1e-3)

    def test_delta_q1_minimo(self):
        """delta_q1 deve essere >= 1.0."""
        with pytest.raises(ValueError, match="delta_q1"):
            fire_design_load(q_f=500.0, delta_q1=0.9, delta_q2=1.0,
                             delta_n=0.6)

    def test_delta_q2_minimo(self):
        """delta_q2 deve essere >= 0.8."""
        with pytest.raises(ValueError, match="delta_q2"):
            fire_design_load(q_f=500.0, delta_q1=1.0, delta_q2=0.7,
                             delta_n=0.6)

    def test_delta_n_minimo(self):
        """delta_n deve essere >= 0.2."""
        with pytest.raises(ValueError, match="delta_n"):
            fire_design_load(q_f=500.0, delta_q1=1.0, delta_q2=1.0,
                             delta_n=0.1)

    def test_q_f_negativo(self):
        with pytest.raises(ValueError, match="q_f"):
            fire_design_load(q_f=-100.0, delta_q1=1.0, delta_q2=1.0,
                             delta_n=0.6)

    def test_ntc_ref(self):
        ref = get_ntc_ref(fire_design_load)
        assert ref is not None
        assert ref.formula == "3.6.1"


# ── [3.6.5] — Pressione statica equivalente esplosioni ──────────────────────

class TestExplosionEquivalentPressure:
    """NTC18 §3.6.2.3, Formule [3.6.5a]-[3.6.5b]."""

    def test_formula_base(self):
        """p_v=5, A_v=5, V=100 -> A_v/V=0.05.
        p_d = 3+5 = 8, p_s = 3+2.5+0.04/0.0025 = 21.5 -> max=21.5."""
        result = explosion_equivalent_pressure(p_v=5.0, A_v=5.0, V=100.0)
        p_d = 3.0 + 5.0
        p_s = 3.0 + 5.0 / 2.0 + 0.04 / (5.0 / 100.0) ** 2
        assert_allclose(result, max(p_d, p_s), rtol=1e-3)

    def test_p_s_domina(self):
        """Quando A_v/V e' piccolo, p_s domina per il termine 0.04/(A_v/V)^2."""
        result = explosion_equivalent_pressure(p_v=3.0, A_v=5.0, V=100.0)
        p_d = 3.0 + 3.0
        p_s = 3.0 + 3.0 / 2.0 + 0.04 / (0.05) ** 2
        assert_allclose(result, max(p_d, p_s), rtol=1e-3)

    def test_rapporto_fuori_range_basso(self):
        """A_v/V < 0.05 solleva ValueError."""
        # A_v=4, V=100 -> A_v/V=0.04 < 0.05
        with pytest.raises(ValueError, match="rapporto"):
            explosion_equivalent_pressure(p_v=5.0, A_v=4.0, V=100.0)

    def test_rapporto_fuori_range_alto(self):
        """A_v/V > 0.15 solleva ValueError."""
        # A_v=16, V=100 -> A_v/V=0.16 > 0.15
        with pytest.raises(ValueError, match="rapporto"):
            explosion_equivalent_pressure(p_v=5.0, A_v=16.0, V=100.0)

    def test_volume_oltre_1000(self):
        """Volume > 1000 m³ solleva ValueError."""
        with pytest.raises(ValueError, match="volume"):
            explosion_equivalent_pressure(p_v=5.0, A_v=50.0, V=1001.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(explosion_equivalent_pressure)
        assert ref is not None
        assert ref.formula == "3.6.5"


# ── Tab. 3.6.III — Forze statiche equivalenti urti veicoli ──────────────────

class TestImpactVehicleForce:
    """NTC18 §3.6.3.3.1, Tab. 3.6.III."""

    @pytest.mark.parametrize("road_type, expected_Fdx", [
        ("highway", 1000.0),
        ("rural", 750.0),
        ("urban", 500.0),
        ("parking_car", 50.0),
        ("parking_truck", 150.0),
    ])
    def test_valori_tabellati(self, road_type, expected_Fdx):
        """Verifica F_{d,x} da Tab. 3.6.III."""
        f_dx, f_dy = impact_vehicle_force(road_type)
        assert_allclose(f_dx, expected_Fdx, rtol=1e-3)
        # F_{d,y} = 0.5 * F_{d,x} [3.6.7]
        assert_allclose(f_dy, 0.5 * expected_Fdx, rtol=1e-3)

    def test_tipo_invalido(self):
        with pytest.raises(ValueError, match="tipo"):
            impact_vehicle_force("bicycle")

    def test_ntc_ref(self):
        ref = get_ntc_ref(impact_vehicle_force)
        assert ref is not None
        assert ref.table == "Tab.3.6.III"


# ── [3.6.9] — Forza urto carrello elevatore ─────────────────────────────────

class TestImpactForkliftForce:
    """NTC18 §3.6.3.3.1, Formula [3.6.9] — F = 5*W."""

    def test_formula(self):
        """W=30 kN -> F = 150 kN."""
        assert_allclose(impact_forklift_force(30.0), 150.0, rtol=1e-3)

    def test_W_zero(self):
        assert_allclose(impact_forklift_force(0.0), 0.0, atol=1e-3)

    def test_W_negativo(self):
        with pytest.raises(ValueError):
            impact_forklift_force(-10.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(impact_forklift_force)
        assert ref is not None
        assert ref.formula == "3.6.9"
