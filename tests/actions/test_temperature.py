"""Test per actions/temperature — NTC18 §3.5.

Copre:
- [3.5.1]-[3.5.8] — temperature estreme dell'aria esterna
- Tab. 3.5.I      — incremento da irraggiamento solare
- Tab. 3.5.II     — variazione termica uniforme per edifici
"""

import pytest
from numpy.testing import assert_allclose

from pyntc.actions.temperature import (
    temperature_extremes,
    temperature_solar_increment,
    temperature_uniform_variation,
)
from pyntc.core.reference import get_ntc_ref


# ── [3.5.1]-[3.5.8] — Temperature estreme dell'aria esterna ─────────────────

class TestTemperatureExtremes:
    """NTC18 §3.5.2, Formule [3.5.1]-[3.5.8] — T_min e T_max."""

    # ── Zona I ────────────────────────────────────────────────────────────

    def test_zona_I_quota_zero(self):
        """Zona I, a_s=0m: T_min=-15°C, T_max=42°C."""
        t_min, t_max = temperature_extremes("I", altitude=0.0)
        assert_allclose(t_min, -15.0, rtol=1e-3)
        assert_allclose(t_max, 42.0, rtol=1e-3)

    def test_zona_I_quota_500(self):
        """Zona I, a_s=500m: T_min=-15-4*0.5=-17°C, T_max=42-6*0.5=39°C."""
        t_min, t_max = temperature_extremes("I", altitude=500.0)
        assert_allclose(t_min, -17.0, rtol=1e-3)
        assert_allclose(t_max, 39.0, rtol=1e-3)

    def test_zona_I_quota_1000(self):
        """Zona I, a_s=1000m: T_min=-19°C, T_max=36°C."""
        t_min, t_max = temperature_extremes("I", altitude=1000.0)
        assert_allclose(t_min, -19.0, rtol=1e-3)
        assert_allclose(t_max, 36.0, rtol=1e-3)

    # ── Zona II ───────────────────────────────────────────────────────────

    def test_zona_II_quota_zero(self):
        """Zona II, a_s=0m: T_min=-8°C, T_max=42°C."""
        t_min, t_max = temperature_extremes("II", altitude=0.0)
        assert_allclose(t_min, -8.0, rtol=1e-3)
        assert_allclose(t_max, 42.0, rtol=1e-3)

    def test_zona_II_quota_500(self):
        """Zona II, a_s=500m: T_min=-8-6*0.5=-11°C, T_max=42-2*0.5=41°C."""
        t_min, t_max = temperature_extremes("II", altitude=500.0)
        assert_allclose(t_min, -11.0, rtol=1e-3)
        assert_allclose(t_max, 41.0, rtol=1e-3)

    # ── Zona III ──────────────────────────────────────────────────────────

    def test_zona_III_quota_zero(self):
        """Zona III, a_s=0m: T_min=-8°C, T_max=42°C."""
        t_min, t_max = temperature_extremes("III", altitude=0.0)
        assert_allclose(t_min, -8.0, rtol=1e-3)
        assert_allclose(t_max, 42.0, rtol=1e-3)

    def test_zona_III_quota_500(self):
        """Zona III, a_s=500m: T_min=-8-7*0.5=-11.5°C, T_max=42-0.3*0.5=41.85°C."""
        t_min, t_max = temperature_extremes("III", altitude=500.0)
        assert_allclose(t_min, -11.5, rtol=1e-3)
        assert_allclose(t_max, 41.85, rtol=1e-3)

    # ── Zona IV ───────────────────────────────────────────────────────────

    def test_zona_IV_quota_zero(self):
        """Zona IV, a_s=0m: T_min=-2°C, T_max=42°C."""
        t_min, t_max = temperature_extremes("IV", altitude=0.0)
        assert_allclose(t_min, -2.0, rtol=1e-3)
        assert_allclose(t_max, 42.0, rtol=1e-3)

    def test_zona_IV_quota_500(self):
        """Zona IV, a_s=500m: T_min=-2-9*0.5=-6.5°C, T_max=42-2*0.5=41°C."""
        t_min, t_max = temperature_extremes("IV", altitude=500.0)
        assert_allclose(t_min, -6.5, rtol=1e-3)
        assert_allclose(t_max, 41.0, rtol=1e-3)

    # ── Edge cases ────────────────────────────────────────────────────────

    def test_zona_invalida(self):
        """Zona non valida solleva ValueError."""
        with pytest.raises(ValueError, match="zona"):
            temperature_extremes("V", altitude=0.0)

    def test_altitudine_negativa(self):
        """Altitudine negativa solleva ValueError."""
        with pytest.raises(ValueError, match="altitudine"):
            temperature_extremes("I", altitude=-10.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(temperature_extremes)
        assert ref is not None
        assert ref.article == "3.5.2"


# ── Tab. 3.5.I — Incremento irraggiamento solare ────────────────────────────

class TestTemperatureSolarIncrement:
    """NTC18 §3.5.4, Tab. 3.5.I — Contributo dell'irraggiamento solare."""

    # ── Estate, superficie riflettente ────────────────────────────────────

    def test_estate_riflettente_NE(self):
        result = temperature_solar_increment("reflective", "NE", "summer")
        assert_allclose(result, 0.0, atol=1e-3)

    def test_estate_riflettente_SW(self):
        result = temperature_solar_increment("reflective", "SW", "summer")
        assert_allclose(result, 18.0, rtol=1e-3)

    # ── Estate, superficie chiara ─────────────────────────────────────────

    def test_estate_chiara_NE(self):
        result = temperature_solar_increment("light", "NE", "summer")
        assert_allclose(result, 2.0, rtol=1e-3)

    def test_estate_chiara_SW(self):
        result = temperature_solar_increment("light", "SW", "summer")
        assert_allclose(result, 30.0, rtol=1e-3)

    # ── Estate, superficie scura ──────────────────────────────────────────

    def test_estate_scura_NE(self):
        result = temperature_solar_increment("dark", "NE", "summer")
        assert_allclose(result, 4.0, rtol=1e-3)

    def test_estate_scura_SW(self):
        result = temperature_solar_increment("dark", "SW", "summer")
        assert_allclose(result, 42.0, rtol=1e-3)

    # ── Inverno ───────────────────────────────────────────────────────────

    def test_inverno_qualsiasi(self):
        """In inverno, incremento = 0°C per tutte le superfici."""
        for surface in ("reflective", "light", "dark"):
            for orientation in ("NE", "SW"):
                result = temperature_solar_increment(
                    surface, orientation, "winter"
                )
                assert_allclose(result, 0.0, atol=1e-3)

    # ── Edge cases ────────────────────────────────────────────────────────

    def test_superficie_invalida(self):
        with pytest.raises(ValueError, match="superficie"):
            temperature_solar_increment("metallic", "NE", "summer")

    def test_orientamento_invalido(self):
        with pytest.raises(ValueError, match="orientamento"):
            temperature_solar_increment("light", "N", "summer")

    def test_stagione_invalida(self):
        with pytest.raises(ValueError, match="stagione"):
            temperature_solar_increment("light", "NE", "spring")

    def test_ntc_ref(self):
        ref = get_ntc_ref(temperature_solar_increment)
        assert ref is not None
        assert ref.table == "Tab.3.5.I"


# ── Tab. 3.5.II — Variazione termica uniforme per edifici ───────────────────

class TestTemperatureUniformVariation:
    """NTC18 §3.5.5, Tab. 3.5.II — DeltaT_u per edifici."""

    @pytest.mark.parametrize("structure_type, expected", [
        ("rc_exposed", 15.0),
        ("rc_protected", 10.0),
        ("steel_exposed", 25.0),
        ("steel_protected", 15.0),
    ])
    def test_valori_tabellati(self, structure_type, expected):
        """Valori da Tab. 3.5.II (valore assoluto ±)."""
        result = temperature_uniform_variation(structure_type)
        assert_allclose(result, expected, rtol=1e-3)

    def test_tipo_invalido(self):
        with pytest.raises(ValueError, match="tipo"):
            temperature_uniform_variation("timber_exposed")

    def test_ntc_ref(self):
        ref = get_ntc_ref(temperature_uniform_variation)
        assert ref is not None
        assert ref.article == "3.5.5"
        assert ref.table == "Tab.3.5.II"
