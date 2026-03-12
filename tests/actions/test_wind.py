"""Test per actions/wind — NTC18 §3.3.

Copre:
- Tab. 3.3.I   — zone vento e parametri (v_b,0, a_0, k_s)
- [3.3.1]      — velocita' base di riferimento v_b
- [3.3.2]      — velocita' di riferimento v_r
- [3.3.3]      — coefficiente di ritorno c_r
- [3.3.4]      — pressione del vento p
- [3.3.5]      — azione tangente del vento p_f
- [3.3.6]      — pressione cinetica di riferimento q_b
- Tab. 3.3.II  — parametri coefficiente di esposizione
- [3.3.7]      — coefficiente di esposizione c_e
"""

import math

import pytest
from numpy.testing import assert_allclose

from pyntc.actions.wind import (
    wind_base_velocity,
    wind_return_coefficient,
    wind_reference_velocity,
    wind_kinetic_pressure,
    wind_exposure_coefficient,
    wind_pressure,
    wind_friction_action,
    wind_terrain_roughness,
)
from pyntc.core.reference import get_ntc_ref


# ── Tab. 3.3.I + [3.3.1] — Velocita' base di riferimento ───────────────────

class TestWindBaseVelocity:
    """NTC18 §3.3.1, Tab. 3.3.I, Formula [3.3.1]."""

    @pytest.mark.parametrize("zone, expected_vb0", [
        (1, 25.0),
        (2, 25.0),
        (3, 27.0),
        (4, 28.0),
        (5, 28.0),
        (6, 28.0),
        (7, 28.0),
        (8, 30.0),
        (9, 31.0),
    ])
    def test_velocita_base_al_mare(self, zone, expected_vb0):
        """A quota 0 m s.l.m., v_b = v_b,0 (c_a = 1)."""
        assert_allclose(wind_base_velocity(zone, altitude=0.0), expected_vb0, rtol=1e-3)

    def test_altitudine_sotto_a0(self):
        """Per a_s <= a_0: c_a = 1, v_b = v_b,0."""
        # Zona 1: a_0 = 1000 m, a_s = 500 m -> c_a = 1
        assert_allclose(wind_base_velocity(1, altitude=500.0), 25.0, rtol=1e-3)

    def test_altitudine_sopra_a0(self):
        """Per a_0 < a_s <= 1500: c_a = 1 + k_s*(a_s/a_0 - 1)."""
        # Zona 1: a_0=1000, k_s=0.40, a_s=1500
        # c_a = 1 + 0.40*(1500/1000 - 1) = 1 + 0.40*0.5 = 1.20
        # v_b = 25 * 1.20 = 30.0
        assert_allclose(wind_base_velocity(1, altitude=1500.0), 30.0, rtol=1e-3)

    def test_altitudine_intermedia(self):
        """Zona 3 a 750 m s.l.m."""
        # Zona 3: a_0=500, k_s=0.37, a_s=750
        # c_a = 1 + 0.37*(750/500 - 1) = 1 + 0.37*0.5 = 1.185
        # v_b = 27 * 1.185 = 31.995
        assert_allclose(wind_base_velocity(3, altitude=750.0), 31.995, rtol=1e-3)

    def test_zona_invalida(self):
        """Zona fuori range [1, 9] solleva ValueError."""
        with pytest.raises(ValueError, match="zona"):
            wind_base_velocity(0)
        with pytest.raises(ValueError, match="zona"):
            wind_base_velocity(10)

    def test_altitudine_oltre_1500(self):
        """Altitudine > 1500 m non coperta dalla formula, solleva ValueError."""
        with pytest.raises(ValueError, match="1500"):
            wind_base_velocity(1, altitude=1600.0)

    def test_altitudine_negativa(self):
        """Altitudine negativa non ammessa."""
        with pytest.raises(ValueError):
            wind_base_velocity(1, altitude=-10.0)

    def test_ntc_ref(self):
        """Verifica riferimento normativo."""
        ref = get_ntc_ref(wind_base_velocity)
        assert ref is not None
        assert ref.article == "3.3.1"
        assert ref.table == "Tab.3.3.I"
        assert ref.formula == "3.3.1"


# ── [3.3.3] — Coefficiente di ritorno ───────────────────────────────────────

class TestWindReturnCoefficient:
    """NTC18 §3.3.2, Formula [3.3.3]."""

    def test_tr_50_anni(self):
        """Per T_R = 50 anni, c_r ≈ 1.0."""
        result = wind_return_coefficient(50.0)
        assert_allclose(result, 1.0, atol=0.002)

    def test_tr_10_anni(self):
        """Per T_R = 10 anni, c_r ≈ 0.903."""
        # c_r = 0.75*sqrt(1 - 0.2*ln(-ln(1-1/10)))
        expected = 0.75 * math.sqrt(1 - 0.2 * math.log(-math.log(1 - 1 / 10)))
        result = wind_return_coefficient(10.0)
        assert_allclose(result, expected, rtol=1e-6)

    def test_tr_100_anni(self):
        """Per T_R = 100 anni, c_r > 1.0."""
        result = wind_return_coefficient(100.0)
        assert result > 1.0

    def test_tr_troppo_basso(self):
        """T_R < 1 anno non ammesso."""
        with pytest.raises(ValueError):
            wind_return_coefficient(0.5)

    def test_ntc_ref(self):
        """Verifica riferimento normativo."""
        ref = get_ntc_ref(wind_return_coefficient)
        assert ref is not None
        assert ref.article == "3.3.2"
        assert ref.formula == "3.3.3"


# ── [3.3.2] — Velocita' di riferimento ──────────────────────────────────────

class TestWindReferenceVelocity:
    """NTC18 §3.3.2, Formula [3.3.2]."""

    def test_tr_50_zona_1(self):
        """v_r = v_b * c_r; con T_R=50, c_r≈1 -> v_r ≈ v_b."""
        result = wind_reference_velocity(zone=1, altitude=0.0, return_period=50.0)
        assert_allclose(result, 25.0, atol=0.1)

    def test_tr_personalizzato(self):
        """v_r = v_b * c_r con T_R diverso da 50."""
        v_b = wind_base_velocity(3, altitude=0.0)
        c_r = wind_return_coefficient(100.0)
        expected = v_b * c_r
        result = wind_reference_velocity(zone=3, altitude=0.0, return_period=100.0)
        assert_allclose(result, expected, rtol=1e-6)

    def test_ntc_ref(self):
        """Verifica riferimento normativo."""
        ref = get_ntc_ref(wind_reference_velocity)
        assert ref is not None
        assert ref.article == "3.3.2"
        assert ref.formula == "3.3.2"


# ── [3.3.6] — Pressione cinetica di riferimento ─────────────────────────────

class TestWindKineticPressure:
    """NTC18 §3.3.6, Formula [3.3.6]."""

    def test_vr_25(self):
        """q_b = 0.5 * 1.25 * 25^2 = 390.625 N/m^2 = 0.3906 kN/m^2."""
        assert_allclose(wind_kinetic_pressure(25.0), 0.390625, rtol=1e-3)

    def test_vr_27(self):
        """q_b = 0.5 * 1.25 * 27^2 = 455.625 N/m^2 = 0.4556 kN/m^2."""
        assert_allclose(wind_kinetic_pressure(27.0), 0.455625, rtol=1e-3)

    def test_vr_zero(self):
        """v_r = 0 -> q_b = 0."""
        assert_allclose(wind_kinetic_pressure(0.0), 0.0)

    def test_vr_negativa(self):
        """Velocita' negativa non ammessa."""
        with pytest.raises(ValueError):
            wind_kinetic_pressure(-5.0)

    def test_ntc_ref(self):
        """Verifica riferimento normativo."""
        ref = get_ntc_ref(wind_kinetic_pressure)
        assert ref is not None
        assert ref.article == "3.3.6"
        assert ref.formula == "3.3.6"


# ── Tab. 3.3.II + [3.3.7] — Coefficiente di esposizione ────────────────────

class TestWindExposureCoefficient:
    """NTC18 §3.3.7, Tab. 3.3.II, Formula [3.3.7]."""

    def test_categoria_II_z_10(self):
        """Cat. II, z=10 m, c_t=1."""
        # k_r=0.19, z_0=0.05, z_min=4
        # ce = 0.19^2 * 1 * ln(10/0.05) * [7 + 1*ln(10/0.05)]
        # ce = 0.0361 * ln(200) * [7 + ln(200)]
        kr = 0.19
        z0 = 0.05
        lnz = math.log(10.0 / z0)
        expected = kr**2 * 1.0 * lnz * (7 + 1.0 * lnz)
        result = wind_exposure_coefficient(z=10.0, exposure_category=2)
        assert_allclose(result, expected, rtol=1e-3)

    def test_sotto_z_min(self):
        """Per z < z_min, ce(z) = ce(z_min)."""
        # Cat. IV: z_min = 8 m
        ce_zmin = wind_exposure_coefficient(z=8.0, exposure_category=4)
        ce_low = wind_exposure_coefficient(z=3.0, exposure_category=4)
        assert_allclose(ce_low, ce_zmin, rtol=1e-6)

    def test_categoria_I_z_10(self):
        """Cat. I, z=10 m, c_t=1."""
        kr = 0.17
        z0 = 0.01
        lnz = math.log(10.0 / z0)
        expected = kr**2 * 1.0 * lnz * (7 + 1.0 * lnz)
        result = wind_exposure_coefficient(z=10.0, exposure_category=1)
        assert_allclose(result, expected, rtol=1e-3)

    def test_coefficiente_topografia(self):
        """c_t diverso da 1 modifica il risultato."""
        ce_1 = wind_exposure_coefficient(z=10.0, exposure_category=2, c_t=1.0)
        ce_12 = wind_exposure_coefficient(z=10.0, exposure_category=2, c_t=1.2)
        assert ce_12 > ce_1

    def test_z_negativa(self):
        """Altezza negativa non ammessa."""
        with pytest.raises(ValueError):
            wind_exposure_coefficient(z=-1.0, exposure_category=2)

    def test_categoria_invalida(self):
        """Categoria di esposizione fuori range [1, 5]."""
        with pytest.raises(ValueError, match="categoria"):
            wind_exposure_coefficient(z=10.0, exposure_category=6)

    def test_ntc_ref(self):
        """Verifica riferimento normativo."""
        ref = get_ntc_ref(wind_exposure_coefficient)
        assert ref is not None
        assert ref.article == "3.3.7"
        assert ref.table == "Tab.3.3.II"
        assert ref.formula == "3.3.7"


# ── [3.3.4] — Pressione del vento ───────────────────────────────────────────

class TestWindPressure:
    """NTC18 §3.3.4, Formula [3.3.4]."""

    def test_formula(self):
        """p = q_b * c_e * c_p * c_d."""
        # q_b=0.39, c_e=2.35, c_p=0.8, c_d=1.0
        expected = 0.39 * 2.35 * 0.8 * 1.0
        result = wind_pressure(q_b=0.39, c_e=2.35, c_p=0.8, c_d=1.0)
        assert_allclose(result, expected, rtol=1e-6)

    def test_cd_default(self):
        """c_d di default = 1.0."""
        result = wind_pressure(q_b=0.39, c_e=2.35, c_p=0.8)
        expected = 0.39 * 2.35 * 0.8
        assert_allclose(result, expected, rtol=1e-6)

    def test_ntc_ref(self):
        """Verifica riferimento normativo."""
        ref = get_ntc_ref(wind_pressure)
        assert ref is not None
        assert ref.article == "3.3.4"
        assert ref.formula == "3.3.4"


# ── [3.3.5] — Azione tangente del vento ─────────────────────────────────────

class TestWindFrictionAction:
    """NTC18 §3.3.5, Formula [3.3.5]."""

    def test_formula(self):
        """p_f = q_b * c_e * c_f."""
        expected = 0.39 * 2.35 * 0.04
        result = wind_friction_action(q_b=0.39, c_e=2.35, c_f=0.04)
        assert_allclose(result, expected, rtol=1e-6)

    def test_ntc_ref(self):
        """Verifica riferimento normativo."""
        ref = get_ntc_ref(wind_friction_action)
        assert ref is not None
        assert ref.article == "3.3.5"
        assert ref.formula == "3.3.5"


# ── Tab. 3.3.III — Classi di rugosità del terreno ────────────────────────────

class TestWindTerrainRoughness:
    """NTC18 §3.3.7, Tab. 3.3.III."""

    @pytest.mark.parametrize("category, expected_z0, expected_zmin, expected_alpha", [
        ("0",   0.003,  1.0,  0.12),
        ("I",   0.01,   1.0,  0.14),
        ("II",  0.05,   2.0,  0.16),
        ("III", 0.30,   5.0,  0.22),
        ("IV",  1.00,  10.0,  0.28),
    ])
    def test_parametri_tabellati(self, category, expected_z0, expected_zmin, expected_alpha):
        """Verifica z_0, z_min e alpha da Tab. 3.3.III."""
        result = wind_terrain_roughness(category)
        assert_allclose(result["z_0"], expected_z0, rtol=1e-6)
        assert_allclose(result["z_min"], expected_zmin, rtol=1e-6)
        assert_allclose(result["alpha"], expected_alpha, rtol=1e-6)

    @pytest.mark.parametrize("category, expected_z0", [
        ("0",   0.003),
        ("I",   0.01),
        ("II",  0.05),
        ("III", 0.30),
        ("IV",  1.00),
    ])
    def test_kr_formula(self, category, expected_z0):
        """k_r = 0.19 * (z_0/0.05)^0.07."""
        result = wind_terrain_roughness(category)
        expected_kr = 0.19 * (expected_z0 / 0.05) ** 0.07
        assert_allclose(result["kr"], expected_kr, rtol=1e-6)

    def test_categoria_II_kr_esatto(self):
        """Cat. II ha z_0 = 0.05, quindi k_r = 0.19 esattamente."""
        result = wind_terrain_roughness("II")
        assert_allclose(result["kr"], 0.19, rtol=1e-9)

    def test_categoria_IV_kr_maggiore_di_II(self):
        """Cat. IV (piu' rugosa) ha k_r > Cat. II."""
        kr_ii = wind_terrain_roughness("II")["kr"]
        kr_iv = wind_terrain_roughness("IV")["kr"]
        assert kr_iv > kr_ii

    def test_categoria_0_kr_minore_di_II(self):
        """Cat. 0 (meno rugosa) ha k_r < Cat. II."""
        kr_0 = wind_terrain_roughness("0")["kr"]
        kr_ii = wind_terrain_roughness("II")["kr"]
        assert kr_0 < kr_ii

    def test_categoria_invalida(self):
        """Categoria non valida solleva ValueError."""
        with pytest.raises(ValueError, match="rugosita'"):
            wind_terrain_roughness("V")
        with pytest.raises(ValueError, match="rugosita'"):
            wind_terrain_roughness("A")

    def test_restituisce_dict_con_chiavi_corrette(self):
        """Il dizionario ha esattamente le chiavi z_0, z_min, kr, alpha."""
        result = wind_terrain_roughness("II")
        assert set(result.keys()) == {"z_0", "z_min", "kr", "alpha"}

    def test_ntc_ref(self):
        """Verifica riferimento normativo."""
        ref = get_ntc_ref(wind_terrain_roughness)
        assert ref is not None
        assert ref.article == "3.3.7"
        assert ref.table == "Tab.3.3.III"
