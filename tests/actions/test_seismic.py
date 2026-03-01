"""Test per actions/seismic — NTC18 §3.2.

Copre:
- [3.2.0]     — periodo di ritorno T_R
- [3.2.4]     — fattore di smorzamento eta
- Tab. 3.2.IV — amplificazione stratigrafica S_s e C_c
- Tab. 3.2.V  — amplificazione topografica S_T
- [3.2.2]     — spettro di risposta elastico orizzontale Se(T)
"""

import math

import numpy as np
import pytest
from numpy.testing import assert_allclose

from pyntc.actions.seismic import (
    seismic_return_period,
    seismic_damping_factor,
    seismic_soil_amplification,
    seismic_topographic_amplification,
    elastic_response_spectrum,
)
from pyntc.core.reference import get_ntc_ref


# ── [3.2.0] — Periodo di ritorno ────────────────────────────────────────────

class TestSeismicReturnPeriod:
    """NTC18 §3.2.1, Formula [3.2.0] — T_R = -V_R / ln(1 - P_VR)."""

    def test_slv_50_anni(self):
        """SLV: P_VR=10%, V_R=50 -> T_R ≈ 475 anni."""
        result = seismic_return_period(v_r=50.0, p_vr=0.10)
        expected = -50.0 / math.log(1.0 - 0.10)
        assert_allclose(result, expected, rtol=1e-3)

    def test_sld_50_anni(self):
        """SLD: P_VR=63%, V_R=50 -> T_R ≈ 50 anni."""
        result = seismic_return_period(v_r=50.0, p_vr=0.63)
        expected = -50.0 / math.log(1.0 - 0.63)
        assert_allclose(result, expected, rtol=1e-3)

    def test_slo_50_anni(self):
        """SLO: P_VR=81%, V_R=50 -> T_R ≈ 30 anni."""
        result = seismic_return_period(v_r=50.0, p_vr=0.81)
        expected = -50.0 / math.log(1.0 - 0.81)
        assert_allclose(result, expected, rtol=1e-3)

    def test_slc_50_anni(self):
        """SLC: P_VR=5%, V_R=50 -> T_R ≈ 975 anni."""
        result = seismic_return_period(v_r=50.0, p_vr=0.05)
        expected = -50.0 / math.log(1.0 - 0.05)
        assert_allclose(result, expected, rtol=1e-3)

    def test_p_vr_fuori_range(self):
        """P_VR deve essere in (0, 1)."""
        with pytest.raises(ValueError):
            seismic_return_period(v_r=50.0, p_vr=0.0)
        with pytest.raises(ValueError):
            seismic_return_period(v_r=50.0, p_vr=1.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_return_period)
        assert ref is not None
        assert ref.article == "3.2.1"
        assert ref.formula == "3.2.0"


# ── [3.2.4] — Fattore di smorzamento ────────────────────────────────────────

class TestSeismicDampingFactor:
    """NTC18 §3.2.3.2.1, Formula [3.2.4] — eta = sqrt(10/(5+xi))."""

    def test_xi_5(self):
        """xi=5% -> eta = 1.0."""
        assert_allclose(seismic_damping_factor(5.0), 1.0, rtol=1e-6)

    def test_xi_10(self):
        """xi=10% -> eta = sqrt(10/15) ≈ 0.8165."""
        expected = math.sqrt(10.0 / 15.0)
        assert_allclose(seismic_damping_factor(10.0), expected, rtol=1e-3)

    def test_xi_2(self):
        """xi=2% -> eta = sqrt(10/7) ≈ 1.195."""
        expected = math.sqrt(10.0 / 7.0)
        assert_allclose(seismic_damping_factor(2.0), expected, rtol=1e-3)

    def test_floor_055(self):
        """eta non puo' scendere sotto 0.55."""
        # xi molto alto -> eta calcolato < 0.55 -> capped a 0.55
        result = seismic_damping_factor(50.0)
        assert_allclose(result, 0.55, rtol=1e-3)

    def test_xi_negativo(self):
        with pytest.raises(ValueError):
            seismic_damping_factor(-1.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_damping_factor)
        assert ref is not None
        assert ref.formula == "3.2.4"


# ── Tab. 3.2.IV — Amplificazione stratigrafica ──────────────────────────────

class TestSeismicSoilAmplification:
    """NTC18 §3.2.3.2.1, Tab. 3.2.IV — S_s e C_c."""

    def test_categoria_A(self):
        """Cat. A: S_s=1.0, C_c=1.0 sempre."""
        ss, cc = seismic_soil_amplification("A", ag=0.15, F0=2.5, Tc_star=0.30)
        assert_allclose(ss, 1.0)
        assert_allclose(cc, 1.0)

    def test_categoria_B(self):
        """Cat. B, ag=0.15, F0=2.5, Tc*=0.30."""
        # S_s = 1.40 - 0.40*2.5*0.15 = 1.25 -> clamped [1.0, 1.2] -> 1.20
        # C_c = 1.10 * 0.30^(-0.20)
        ss, cc = seismic_soil_amplification("B", ag=0.15, F0=2.5, Tc_star=0.30)
        assert_allclose(ss, 1.20, rtol=1e-3)
        expected_cc = 1.10 * 0.30 ** (-0.20)
        assert_allclose(cc, expected_cc, rtol=1e-3)

    def test_categoria_C(self):
        """Cat. C, ag=0.10, F0=2.5, Tc*=0.30."""
        # S_s = 1.70 - 0.60*2.5*0.10 = 1.55 -> clamped [1.0, 1.5] -> 1.50
        ss, cc = seismic_soil_amplification("C", ag=0.10, F0=2.5, Tc_star=0.30)
        assert_allclose(ss, 1.50, rtol=1e-3)
        expected_cc = 1.05 * 0.30 ** (-0.33)
        assert_allclose(cc, expected_cc, rtol=1e-3)

    def test_categoria_D(self):
        """Cat. D, ag=0.05, F0=2.5, Tc*=0.30."""
        # S_s = 2.40 - 1.50*2.5*0.05 = 2.2125 -> clamped [0.9, 1.8] -> 1.80
        ss, cc = seismic_soil_amplification("D", ag=0.05, F0=2.5, Tc_star=0.30)
        assert_allclose(ss, 1.80, rtol=1e-3)
        expected_cc = 1.25 * 0.30 ** (-0.50)
        assert_allclose(cc, expected_cc, rtol=1e-3)

    def test_categoria_E(self):
        """Cat. E, ag=0.10, F0=2.5, Tc*=0.30."""
        # S_s = 2.00 - 1.10*2.5*0.10 = 1.725 -> clamped [1.0, 1.6] -> 1.60
        ss, cc = seismic_soil_amplification("E", ag=0.10, F0=2.5, Tc_star=0.30)
        assert_allclose(ss, 1.60, rtol=1e-3)
        expected_cc = 1.15 * 0.30 ** (-0.40)
        assert_allclose(cc, expected_cc, rtol=1e-3)

    def test_categoria_invalida(self):
        with pytest.raises(ValueError, match="categoria"):
            seismic_soil_amplification("F", ag=0.15, F0=2.5, Tc_star=0.30)

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_soil_amplification)
        assert ref is not None
        assert ref.table == "Tab.3.2.IV"


# ── Tab. 3.2.V — Amplificazione topografica ─────────────────────────────────

class TestSeismicTopographicAmplification:
    """NTC18 §3.2.3.2.1, Tab. 3.2.V — S_T."""

    @pytest.mark.parametrize("category, expected", [
        ("T1", 1.0),
        ("T2", 1.2),
        ("T3", 1.2),
        ("T4", 1.4),
    ])
    def test_valori_tabellati(self, category, expected):
        assert_allclose(
            seismic_topographic_amplification(category), expected, rtol=1e-3
        )

    def test_categoria_invalida(self):
        with pytest.raises(ValueError, match="categoria"):
            seismic_topographic_amplification("T5")

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_topographic_amplification)
        assert ref is not None
        assert ref.table == "Tab.3.2.V"


# ── [3.2.2] — Spettro di risposta elastico orizzontale ──────────────────────

class TestElasticResponseSpectrum:
    """NTC18 §3.2.3.2.1, Formula [3.2.2] — Se(T) orizzontale."""

    # Parametri di test: ag=0.15g, F0=2.5, Tc*=0.30s, Cat.B, T1, xi=5%
    # S_s=1.20, C_c=1.10*0.3^(-0.20)≈1.3995, S_T=1.0, S=1.20, eta=1.0
    # T_C = C_c*Tc* ≈ 0.4198s, T_B = T_C/3 ≈ 0.1399s
    # T_D = 4.0*0.15 + 1.6 = 2.2s
    # Plateau: ag*S*eta*F0 = 0.15*1.20*1.0*2.5 = 0.45g

    def test_T_zero(self):
        """A T=0, Se = ag*S (PGA)."""
        result = elastic_response_spectrum(
            T=0.0, ag=0.15, F0=2.5, Tc_star=0.30,
            soil_category="B", topo_category="T1",
        )
        # Se(0) = ag * S * eta * F0 * [0 + 1/(eta*F0)] = ag * S
        assert_allclose(result, 0.15 * 1.20, rtol=1e-3)

    def test_plateau(self):
        """Nel tratto T_B <= T < T_C, Se = ag*S*eta*F0 = 0.45g."""
        result = elastic_response_spectrum(
            T=0.30, ag=0.15, F0=2.5, Tc_star=0.30,
            soil_category="B", topo_category="T1",
        )
        assert_allclose(result, 0.45, rtol=1e-2)

    def test_tratto_discendente(self):
        """Nel tratto T_C <= T < T_D, Se = plateau * T_C/T."""
        # T=1.0s, T_C ≈ 0.4198
        result = elastic_response_spectrum(
            T=1.0, ag=0.15, F0=2.5, Tc_star=0.30,
            soil_category="B", topo_category="T1",
        )
        ss, cc = seismic_soil_amplification("B", 0.15, 2.5, 0.30)
        Tc = cc * 0.30
        expected = 0.15 * ss * 1.0 * 2.5 * (Tc / 1.0)
        assert_allclose(result, expected, rtol=1e-3)

    def test_tratto_lungo_periodo(self):
        """Nel tratto T >= T_D, Se = plateau * T_C*T_D/T^2."""
        # T=3.0s, T_D=2.2s
        result = elastic_response_spectrum(
            T=3.0, ag=0.15, F0=2.5, Tc_star=0.30,
            soil_category="B", topo_category="T1",
        )
        ss, cc = seismic_soil_amplification("B", 0.15, 2.5, 0.30)
        Tc = cc * 0.30
        Td = 4.0 * 0.15 + 1.6
        expected = 0.15 * ss * 1.0 * 2.5 * (Tc * Td / 3.0**2)
        assert_allclose(result, expected, rtol=1e-3)

    def test_array_periodi(self):
        """Accetta array numpy di periodi."""
        T = np.array([0.0, 0.3, 1.0, 3.0])
        result = elastic_response_spectrum(
            T=T, ag=0.15, F0=2.5, Tc_star=0.30,
            soil_category="B", topo_category="T1",
        )
        assert result.shape == (4,)
        # Valori crescenti fino al plateau, poi decrescenti
        assert result[1] > result[0]   # plateau > PGA
        assert result[2] < result[1]   # discendente < plateau
        assert result[3] < result[2]   # lungo periodo < discendente

    def test_suolo_A(self):
        """Spettro su suolo A (S_s=1, C_c=1)."""
        result = elastic_response_spectrum(
            T=0.0, ag=0.15, F0=2.5, Tc_star=0.30,
            soil_category="A", topo_category="T1",
        )
        # PGA su suolo A: ag * S = ag * 1.0 * 1.0 = ag
        assert_allclose(result, 0.15, rtol=1e-3)

    def test_T_negativo(self):
        with pytest.raises(ValueError):
            elastic_response_spectrum(
                T=-0.1, ag=0.15, F0=2.5, Tc_star=0.30,
                soil_category="A", topo_category="T1",
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(elastic_response_spectrum)
        assert ref is not None
        assert ref.article == "3.2.3.2.1"
        assert ref.formula == "3.2.2"
