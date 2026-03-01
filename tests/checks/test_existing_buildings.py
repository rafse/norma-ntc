"""Test per existing_buildings — NTC18 Cap. 8."""

import pytest
from numpy.testing import assert_allclose

from pyntc.checks.existing_buildings import (
    adequacy_check,
    adequacy_required_load_increase,
    confidence_factor,
    existing_design_strength_brittle,
    existing_design_strength_ductile,
    improvement_check,
    safety_ratio_seismic,
    safety_ratio_vertical,
)
from pyntc.core.reference import get_ntc_ref


# ── §8.5.4 — Fattori di confidenza ──────────────────────────────────────────


class TestConfidenceFactor:
    """NTC18 §8.5.4 — Livelli di conoscenza e fattori di confidenza."""

    def test_lc1(self):
        """LC1 (conoscenza limitata): FC = 1.35."""
        assert_allclose(confidence_factor("LC1"), 1.35, rtol=1e-3)

    def test_lc2(self):
        """LC2 (conoscenza adeguata): FC = 1.20."""
        assert_allclose(confidence_factor("LC2"), 1.20, rtol=1e-3)

    def test_lc3(self):
        """LC3 (conoscenza accurata): FC = 1.00."""
        assert_allclose(confidence_factor("LC3"), 1.00, rtol=1e-3)

    def test_lowercase(self):
        """Accetta input case-insensitive."""
        assert_allclose(confidence_factor("lc2"), 1.20, rtol=1e-3)

    def test_invalid_level_raises(self):
        with pytest.raises(ValueError, match="LC1.*LC2.*LC3"):
            confidence_factor("LC4")

    def test_ntc_ref(self):
        ref = get_ntc_ref(confidence_factor)
        assert ref is not None
        assert ref.article == "8.5.4"


# ── §8.3 — Rapporto di sicurezza sismica ────────────────────────────────────


class TestSafetyRatioSeismic:
    """NTC18 §8.3 — ζ_E = capacita' / domanda sismica."""

    def test_basic(self):
        """ζ_E = 150 / 200 = 0.75."""
        assert_allclose(safety_ratio_seismic(150.0, 200.0), 0.75, rtol=1e-3)

    def test_equal(self):
        """Capacita' = domanda: ζ_E = 1.0."""
        assert_allclose(safety_ratio_seismic(100.0, 100.0), 1.0, rtol=1e-3)

    def test_exceeds(self):
        """Capacita' > domanda: ζ_E = 1.5."""
        assert_allclose(safety_ratio_seismic(300.0, 200.0), 1.5, rtol=1e-3)

    def test_zero_demand_raises(self):
        with pytest.raises(ValueError):
            safety_ratio_seismic(100.0, 0.0)

    def test_negative_capacity_raises(self):
        with pytest.raises(ValueError):
            safety_ratio_seismic(-100.0, 200.0)

    def test_negative_demand_raises(self):
        with pytest.raises(ValueError):
            safety_ratio_seismic(100.0, -200.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(safety_ratio_seismic)
        assert ref is not None
        assert ref.article == "8.3"


# ── §8.3 — Rapporto di sicurezza carichi verticali ──────────────────────────


class TestSafetyRatioVertical:
    """NTC18 §8.3 — ζ_v = capacita' / domanda carichi variabili."""

    def test_basic(self):
        """ζ_v = 8.0 / 10.0 = 0.80."""
        assert_allclose(safety_ratio_vertical(8.0, 10.0), 0.80, rtol=1e-3)

    def test_full_capacity(self):
        """ζ_v = 1.0 quando capacita' = domanda."""
        assert_allclose(safety_ratio_vertical(5.0, 5.0), 1.0, rtol=1e-3)

    def test_surplus(self):
        """ζ_v = 1.2 quando capacita' > domanda."""
        assert_allclose(safety_ratio_vertical(12.0, 10.0), 1.2, rtol=1e-3)

    def test_zero_demand_raises(self):
        with pytest.raises(ValueError):
            safety_ratio_vertical(5.0, 0.0)

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            safety_ratio_vertical(-5.0, 10.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(safety_ratio_vertical)
        assert ref is not None
        assert ref.article == "8.3"


# ── §8.4.2 — Verifica miglioramento ─────────────────────────────────────────


class TestImprovementCheck:
    """NTC18 §8.4.2 — Soglie minime per interventi di miglioramento."""

    def test_class_iv_passes(self):
        """Classe IV con ζ_E = 0.7 >= 0.6: passa."""
        passes, threshold = improvement_check(0.7, use_class=4)
        assert passes is True
        assert_allclose(threshold, 0.6, rtol=1e-3)

    def test_class_iv_fails(self):
        """Classe IV con ζ_E = 0.5 < 0.6: non passa."""
        passes, threshold = improvement_check(0.5, use_class=4)
        assert passes is False
        assert_allclose(threshold, 0.6, rtol=1e-3)

    def test_class_iii_school_passes(self):
        """Classe III scolastico con ζ_E = 0.65 >= 0.6: passa."""
        passes, threshold = improvement_check(
            0.65, use_class=3, is_school=True
        )
        assert passes is True
        assert_allclose(threshold, 0.6, rtol=1e-3)

    def test_class_iii_school_fails(self):
        """Classe III scolastico con ζ_E = 0.55 < 0.6: non passa."""
        passes, threshold = improvement_check(
            0.55, use_class=3, is_school=True
        )
        assert passes is False
        assert_allclose(threshold, 0.6, rtol=1e-3)

    def test_class_ii_increment_passes(self):
        """Classe II: incremento ζ_E = 0.6 - 0.4 = 0.2 >= 0.1: passa."""
        passes, threshold = improvement_check(
            0.6, use_class=2, zeta_E_pre=0.4
        )
        assert passes is True
        assert_allclose(threshold, 0.5, rtol=1e-3)  # 0.4 + 0.1

    def test_class_ii_increment_fails(self):
        """Classe II: incremento ζ_E = 0.45 - 0.4 = 0.05 < 0.1: non passa."""
        passes, threshold = improvement_check(
            0.45, use_class=2, zeta_E_pre=0.4
        )
        assert passes is False
        assert_allclose(threshold, 0.5, rtol=1e-3)  # 0.4 + 0.1

    def test_class_iii_non_school_increment(self):
        """Classe III non scolastico: segue regola incremento >= 0.1."""
        passes, threshold = improvement_check(
            0.55, use_class=3, is_school=False, zeta_E_pre=0.3
        )
        assert passes is True
        assert_allclose(threshold, 0.4, rtol=1e-3)  # 0.3 + 0.1

    def test_isolation_passes(self):
        """Con isolamento: ζ_E >= 1.0."""
        passes, threshold = improvement_check(
            1.05, use_class=2, is_isolation=True
        )
        assert passes is True
        assert_allclose(threshold, 1.0, rtol=1e-3)

    def test_isolation_fails(self):
        """Con isolamento: ζ_E = 0.9 < 1.0."""
        passes, threshold = improvement_check(
            0.9, use_class=2, is_isolation=True
        )
        assert passes is False
        assert_allclose(threshold, 1.0, rtol=1e-3)

    def test_class_ii_no_pre_raises(self):
        """Classe II senza ζ_E_pre: deve alzare errore."""
        with pytest.raises(ValueError, match="zeta_E_pre"):
            improvement_check(0.6, use_class=2)

    def test_invalid_class_raises(self):
        with pytest.raises(ValueError, match="use_class"):
            improvement_check(0.5, use_class=5)

    def test_ntc_ref(self):
        ref = get_ntc_ref(improvement_check)
        assert ref is not None
        assert ref.article == "8.4.2"


# ── §8.4.3 — Verifica adeguamento ───────────────────────────────────────────


class TestAdequacyCheck:
    """NTC18 §8.4.3 — Soglie minime per interventi di adeguamento."""

    def test_case_a_passes(self):
        """Caso a) sopraelevazione: ζ_E = 1.1 >= 1.0."""
        passes, threshold = adequacy_check(1.1, "a")
        assert passes is True
        assert_allclose(threshold, 1.0, rtol=1e-3)

    def test_case_a_fails(self):
        """Caso a) sopraelevazione: ζ_E = 0.9 < 1.0."""
        passes, threshold = adequacy_check(0.9, "a")
        assert passes is False
        assert_allclose(threshold, 1.0, rtol=1e-3)

    def test_case_b(self):
        """Caso b) ampliamento: soglia 1.0."""
        passes, threshold = adequacy_check(1.0, "b")
        assert passes is True
        assert_allclose(threshold, 1.0, rtol=1e-3)

    def test_case_c_passes(self):
        """Caso c) cambio d'uso: ζ_E = 0.85 >= 0.80."""
        passes, threshold = adequacy_check(0.85, "c")
        assert passes is True
        assert_allclose(threshold, 0.80, rtol=1e-3)

    def test_case_c_fails(self):
        """Caso c) cambio d'uso: ζ_E = 0.75 < 0.80."""
        passes, threshold = adequacy_check(0.75, "c")
        assert passes is False
        assert_allclose(threshold, 0.80, rtol=1e-3)

    def test_case_d(self):
        """Caso d) trasformazione strutturale: soglia 1.0."""
        passes, threshold = adequacy_check(1.05, "d")
        assert passes is True
        assert_allclose(threshold, 1.0, rtol=1e-3)

    def test_case_e_passes(self):
        """Caso e) cambio classe d'uso: ζ_E = 0.80 >= 0.80."""
        passes, threshold = adequacy_check(0.80, "e")
        assert passes is True
        assert_allclose(threshold, 0.80, rtol=1e-3)

    def test_case_e_fails(self):
        """Caso e) cambio classe d'uso: ζ_E = 0.79 < 0.80."""
        passes, threshold = adequacy_check(0.79, "e")
        assert passes is False
        assert_allclose(threshold, 0.80, rtol=1e-3)

    def test_invalid_case_raises(self):
        with pytest.raises(ValueError, match="intervention_case"):
            adequacy_check(1.0, "f")

    def test_ntc_ref(self):
        ref = get_ntc_ref(adequacy_check)
        assert ref is not None
        assert ref.article == "8.4.3"


# ── §8.4.3.c — Adeguamento per incremento carichi ───────────────────────────


class TestAdequacyRequiredLoadIncrease:
    """NTC18 §8.4.3.c — Incremento carichi verticali > 10%."""

    def test_under_10_percent(self):
        """Incremento 5%: adeguamento NON richiesto."""
        assert adequacy_required_load_increase(100.0, 105.0) is False

    def test_exactly_10_percent(self):
        """Incremento esattamente 10%: adeguamento NON richiesto (superiore, non uguale)."""
        assert adequacy_required_load_increase(100.0, 110.0) is False

    def test_over_10_percent(self):
        """Incremento 15%: adeguamento richiesto."""
        assert adequacy_required_load_increase(100.0, 115.0) is True

    def test_marginal_over(self):
        """Incremento 10.1%: adeguamento richiesto."""
        assert adequacy_required_load_increase(100.0, 110.1) is True

    def test_no_change(self):
        """Nessun incremento: adeguamento NON richiesto."""
        assert adequacy_required_load_increase(100.0, 100.0) is False

    def test_decrease(self):
        """Diminuzione carichi: adeguamento NON richiesto."""
        assert adequacy_required_load_increase(100.0, 90.0) is False

    def test_zero_pre_raises(self):
        with pytest.raises(ValueError):
            adequacy_required_load_increase(0.0, 100.0)

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            adequacy_required_load_increase(-10.0, 100.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(adequacy_required_load_increase)
        assert ref is not None
        assert ref.article == "8.4.3"


# ── §8.7.2 — Resistenza di progetto meccanismi duttili ──────────────────────


class TestExistingDesignStrengthDuctile:
    """NTC18 §8.7.2 — f_d = f_mean / FC per meccanismi duttili."""

    def test_lc1(self):
        """f_mean = 25 MPa, FC = 1.35 → f_d = 18.519 MPa."""
        result = existing_design_strength_ductile(25.0, 1.35)
        assert_allclose(result, 25.0 / 1.35, rtol=1e-3)

    def test_lc2(self):
        """f_mean = 25 MPa, FC = 1.20 → f_d = 20.833 MPa."""
        result = existing_design_strength_ductile(25.0, 1.20)
        assert_allclose(result, 25.0 / 1.20, rtol=1e-3)

    def test_lc3(self):
        """f_mean = 25 MPa, FC = 1.00 → f_d = 25.0 MPa."""
        result = existing_design_strength_ductile(25.0, 1.00)
        assert_allclose(result, 25.0, rtol=1e-3)

    def test_zero_fc_raises(self):
        with pytest.raises(ValueError):
            existing_design_strength_ductile(25.0, 0.0)

    def test_negative_f_mean_raises(self):
        with pytest.raises(ValueError):
            existing_design_strength_ductile(-25.0, 1.35)

    def test_ntc_ref(self):
        ref = get_ntc_ref(existing_design_strength_ductile)
        assert ref is not None
        assert ref.article == "8.7.2"


# ── §8.7.2 — Resistenza di progetto meccanismi fragili ──────────────────────


class TestExistingDesignStrengthBrittle:
    """NTC18 §8.7.2 — f_d = f_mean / (gamma_m * FC) per meccanismi fragili."""

    def test_lc1_concrete(self):
        """f_mean=25 MPa, gamma_m=1.5, FC=1.35 → f_d = 12.346 MPa."""
        result = existing_design_strength_brittle(25.0, 1.5, 1.35)
        assert_allclose(result, 25.0 / (1.5 * 1.35), rtol=1e-3)

    def test_lc2_steel(self):
        """f_mean=450 MPa, gamma_m=1.15, FC=1.20 → f_d = 326.087 MPa."""
        result = existing_design_strength_brittle(450.0, 1.15, 1.20)
        assert_allclose(result, 450.0 / (1.15 * 1.20), rtol=1e-3)

    def test_lc3(self):
        """FC=1.0: riduce solo per gamma_m."""
        result = existing_design_strength_brittle(30.0, 1.5, 1.0)
        assert_allclose(result, 30.0 / 1.5, rtol=1e-3)

    def test_zero_gamma_raises(self):
        with pytest.raises(ValueError):
            existing_design_strength_brittle(25.0, 0.0, 1.35)

    def test_zero_fc_raises(self):
        with pytest.raises(ValueError):
            existing_design_strength_brittle(25.0, 1.5, 0.0)

    def test_negative_f_mean_raises(self):
        with pytest.raises(ValueError):
            existing_design_strength_brittle(-25.0, 1.5, 1.35)

    def test_ntc_ref(self):
        ref = get_ntc_ref(existing_design_strength_brittle)
        assert ref is not None
        assert ref.article == "8.7.2"
