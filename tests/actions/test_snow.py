"""Test per actions/snow — NTC18 §3.4.

Copre:
- [3.4.1]         — carico neve sulle coperture q_s
- [3.4.2]-[3.4.5] — carico di riferimento neve al suolo q_sk (4 zone)
- Tab. 3.4.II     — coefficiente di forma mu_1
- Tab. 3.4.I      — coefficiente di esposizione C_E
"""

import pytest
from numpy.testing import assert_allclose

from pyntc.actions.snow import (
    snow_ground_load,
    snow_shape_coefficient,
    snow_exposure_coefficient,
    snow_roof_load,
)
from pyntc.core.reference import get_ntc_ref


# ── [3.4.2]-[3.4.5] — Carico neve al suolo q_sk ────────────────────────────

class TestSnowGroundLoad:
    """NTC18 §3.4.2 — Carico di riferimento neve al suolo."""

    # Valori base (a_s <= 200 m)
    @pytest.mark.parametrize("zone, expected", [
        ("IA",  1.50),
        ("IM",  1.50),
        ("II",  1.00),
        ("III", 0.60),
    ])
    def test_quota_bassa(self, zone, expected):
        """A quota <= 200 m, q_sk = valore base della zona."""
        assert_allclose(snow_ground_load(zone, altitude=0.0), expected, rtol=1e-3)
        assert_allclose(snow_ground_load(zone, altitude=200.0), expected, rtol=1e-3)

    def test_zona_IA_alta_quota(self):
        """Zona I-Alpina, a_s=500 m: q_sk = 1.39*[1+(500/728)^2]."""
        expected = 1.39 * (1 + (500 / 728) ** 2)
        assert_allclose(snow_ground_load("IA", altitude=500.0), expected, rtol=1e-3)

    def test_zona_IM_alta_quota(self):
        """Zona I-Mediterranea, a_s=400 m: q_sk = 1.35*[1+(400/602)^2]."""
        expected = 1.35 * (1 + (400 / 602) ** 2)
        assert_allclose(snow_ground_load("IM", altitude=400.0), expected, rtol=1e-3)

    def test_zona_II_alta_quota(self):
        """Zona II, a_s=400 m: q_sk = 0.85*[1+(400/481)^2]."""
        expected = 0.85 * (1 + (400 / 481) ** 2)
        assert_allclose(snow_ground_load("II", altitude=400.0), expected, rtol=1e-3)

    def test_zona_III_alta_quota(self):
        """Zona III, a_s=400 m: q_sk = 0.51*[1+(400/481)^2]."""
        expected = 0.51 * (1 + (400 / 481) ** 2)
        assert_allclose(snow_ground_load("III", altitude=400.0), expected, rtol=1e-3)

    def test_zona_invalida(self):
        """Zona non valida solleva ValueError."""
        with pytest.raises(ValueError, match="zona"):
            snow_ground_load("IV", altitude=0.0)

    def test_altitudine_negativa(self):
        """Altitudine negativa non ammessa."""
        with pytest.raises(ValueError):
            snow_ground_load("IA", altitude=-10.0)

    def test_altitudine_oltre_1500(self):
        """Altitudine > 1500 m non coperta, solleva ValueError."""
        with pytest.raises(ValueError, match="1500"):
            snow_ground_load("IA", altitude=1600.0)

    def test_ntc_ref(self):
        """Verifica riferimento normativo."""
        ref = get_ntc_ref(snow_ground_load)
        assert ref is not None
        assert ref.article == "3.4.2"


# ── Tab. 3.4.II — Coefficiente di forma ─────────────────────────────────────

class TestSnowShapeCoefficient:
    """NTC18 §3.4.3, Tab. 3.4.II — Coefficiente di forma mu_1."""

    @pytest.mark.parametrize("alpha, expected", [
        (0.0,  0.8),    # 0 <= alpha <= 30
        (15.0, 0.8),    # 0 <= alpha <= 30
        (30.0, 0.8),    # limite superiore primo range
        (45.0, 0.4),    # 0.8*(60-45)/30 = 0.4
        (50.0, 0.8 * (60 - 50) / 30),  # interpolazione lineare
        (60.0, 0.0),    # limite
        (75.0, 0.0),    # alpha >= 60
    ])
    def test_valori_tabellati(self, alpha, expected):
        """Verifica Tab. 3.4.II per diversi angoli."""
        assert_allclose(snow_shape_coefficient(alpha), expected, atol=1e-6)

    def test_angolo_negativo(self):
        """Angolo negativo non ammesso."""
        with pytest.raises(ValueError):
            snow_shape_coefficient(-5.0)

    def test_ntc_ref(self):
        """Verifica riferimento normativo."""
        ref = get_ntc_ref(snow_shape_coefficient)
        assert ref is not None
        assert ref.article == "3.4.3"
        assert ref.table == "Tab.3.4.II"


# ── Tab. 3.4.I — Coefficiente di esposizione ────────────────────────────────

class TestSnowExposureCoefficient:
    """NTC18 §3.4.4, Tab. 3.4.I — Coefficiente di esposizione C_E."""

    @pytest.mark.parametrize("topography, expected", [
        ("windswept", 0.9),
        ("normal",    1.0),
        ("sheltered", 1.1),
    ])
    def test_valori_tabellati(self, topography, expected):
        """Verifica Tab. 3.4.I per le tre classi."""
        assert_allclose(snow_exposure_coefficient(topography), expected, rtol=1e-3)

    def test_topografia_invalida(self):
        """Topografia non valida solleva ValueError."""
        with pytest.raises(ValueError, match="topografia"):
            snow_exposure_coefficient("montagna")

    def test_ntc_ref(self):
        """Verifica riferimento normativo."""
        ref = get_ntc_ref(snow_exposure_coefficient)
        assert ref is not None
        assert ref.article == "3.4.4"
        assert ref.table == "Tab.3.4.I"


# ── [3.4.1] — Carico neve sulle coperture ───────────────────────────────────

class TestSnowRoofLoad:
    """NTC18 §3.4.1, Formula [3.4.1] — q_s = q_sk * mu_i * C_E * C_t."""

    def test_formula_base(self):
        """q_s = 1.50 * 0.8 * 1.0 * 1.0 = 1.20 kN/m^2."""
        result = snow_roof_load(q_sk=1.50, mu_i=0.8, c_e=1.0, c_t=1.0)
        assert_allclose(result, 1.20, rtol=1e-3)

    def test_defaults(self):
        """C_E e C_t di default sono 1.0."""
        result = snow_roof_load(q_sk=1.50, mu_i=0.8)
        assert_allclose(result, 1.20, rtol=1e-3)

    def test_con_esposizione_riparata(self):
        """q_s = 1.00 * 0.8 * 1.1 * 1.0 = 0.88."""
        result = snow_roof_load(q_sk=1.00, mu_i=0.8, c_e=1.1)
        assert_allclose(result, 0.88, rtol=1e-3)

    def test_ntc_ref(self):
        """Verifica riferimento normativo."""
        ref = get_ntc_ref(snow_roof_load)
        assert ref is not None
        assert ref.article == "3.4.1"
        assert ref.formula == "3.4.1"
