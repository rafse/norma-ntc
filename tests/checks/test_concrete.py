"""Test per concrete — NTC18 §4.1."""

import math

import pytest
import numpy as np
from numpy.testing import assert_allclose

from pyntc.checks.concrete import (
    biaxial_bending_check,
    bond_design_strength,
    concrete_beam_min_reinforcement,
    concrete_column_min_reinforcement,
    concrete_confined_strength,
    concrete_design_compressive_strength,
    concrete_design_tensile_strength,
    concrete_prestress_stress_limits,
    concrete_slenderness,
    concrete_slenderness_limit,
    concrete_strain_limits,
    concrete_stress_limit,
    shear_resistance_no_stirrups,
    shear_resistance_with_stirrups,
    steel_design_strength,
    steel_stress_limit,
    torsion_resistance,
    torsion_shear_interaction,
)
from pyntc.core.reference import get_ntc_ref


# ── [4.1.3] — Resistenza di progetto a compressione del calcestruzzo ─────────


class TestConcreteDesignCompressiveStrength:
    """NTC18 §4.1.2.1.1.1, Formula [4.1.3]."""

    def test_c25(self):
        """C25/30: f_cd = 0.85 * 25 / 1.5 = 14.1667 MPa."""
        result = concrete_design_compressive_strength(f_ck=25.0)
        assert_allclose(result, 14.1667, rtol=1e-3)

    def test_c50(self):
        """C50/60: f_cd = 0.85 * 50 / 1.5 = 28.3333 MPa."""
        result = concrete_design_compressive_strength(f_ck=50.0)
        assert_allclose(result, 28.3333, rtol=1e-3)

    def test_reduced_gamma(self):
        """gamma_c=1.4 per produzioni controllate: f_cd = 0.85*25/1.4."""
        result = concrete_design_compressive_strength(f_ck=25.0, gamma_c=1.4)
        assert_allclose(result, 0.85 * 25.0 / 1.4, rtol=1e-3)

    def test_negative_fck_raises(self):
        with pytest.raises(ValueError):
            concrete_design_compressive_strength(f_ck=-5.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(concrete_design_compressive_strength)
        assert ref is not None
        assert ref.article == "4.1.2.1.1.1"


# ── [4.1.4] — Resistenza di progetto a trazione del calcestruzzo ─────────────


class TestConcreteDesignTensileStrength:
    """NTC18 §4.1.2.1.1.2, Formula [4.1.4]."""

    def test_c25(self):
        """f_ctk=1.8 MPa (C25): f_ctd = 1.8 / 1.5 = 1.2 MPa."""
        result = concrete_design_tensile_strength(f_ctk=1.8)
        assert_allclose(result, 1.2, rtol=1e-3)

    def test_c40(self):
        """f_ctk=2.5 MPa (C40): f_ctd = 2.5 / 1.5 = 1.6667 MPa."""
        result = concrete_design_tensile_strength(f_ctk=2.5)
        assert_allclose(result, 1.6667, rtol=1e-3)

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            concrete_design_tensile_strength(f_ctk=-1.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(concrete_design_tensile_strength)
        assert ref is not None
        assert ref.article == "4.1.2.1.1.2"


# ── [4.1.5] — Resistenza di progetto dell'acciaio ────────────────────────────


class TestSteelDesignStrength:
    """NTC18 §4.1.2.1.1.3, Formula [4.1.5]."""

    def test_b450c(self):
        """B450C: f_yd = 450 / 1.15 = 391.304 MPa."""
        result = steel_design_strength(f_yk=450.0)
        assert_allclose(result, 391.304, rtol=1e-3)

    def test_b500c(self):
        """B500C: f_yd = 500 / 1.15 = 434.783 MPa."""
        result = steel_design_strength(f_yk=500.0)
        assert_allclose(result, 434.783, rtol=1e-3)

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            steel_design_strength(f_yk=-100.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(steel_design_strength)
        assert ref is not None
        assert ref.article == "4.1.2.1.1.3"


# ── [4.1.6-7] — Aderenza acciaio-calcestruzzo ────────────────────────────────


class TestBondDesignStrength:
    """NTC18 §4.1.2.1.1.4, Formule [4.1.6]-[4.1.7]."""

    def test_good_bond_small_bar(self):
        """Buona aderenza, Phi<=32: f_bd = 2.25*1.0*1.0*1.8/1.5 = 2.7 MPa."""
        result = bond_design_strength(f_ctk=1.8, eta_1=1.0, eta_2=1.0)
        assert_allclose(result, 2.7, rtol=1e-3)

    def test_poor_bond(self):
        """Non buona aderenza: f_bd = 2.25*0.7*1.0*1.8/1.5 = 1.89 MPa."""
        result = bond_design_strength(f_ctk=1.8, eta_1=0.7, eta_2=1.0)
        assert_allclose(result, 1.89, rtol=1e-3)

    def test_large_diameter(self):
        """Phi=40mm: eta_2=(132-40)/100=0.92, f_bd=2.25*1.0*0.92*1.8/1.5."""
        eta_2 = (132 - 40) / 100
        result = bond_design_strength(f_ctk=1.8, eta_1=1.0, eta_2=eta_2)
        assert_allclose(result, 2.25 * 1.0 * 0.92 * 1.8 / 1.5, rtol=1e-3)

    def test_negative_fctk_raises(self):
        with pytest.raises(ValueError):
            bond_design_strength(f_ctk=-1.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(bond_design_strength)
        assert ref is not None
        assert ref.article == "4.1.2.1.1.4"


# ── §4.1.2.1.2.1 — Limiti di deformazione del calcestruzzo ───────────────────


class TestConcreteStrainLimits:
    """NTC18 §4.1.2.1.2.1."""

    def test_c25_le_c50(self):
        """C25 (<=C50/60): eps_c2=0.002, eps_cu2=0.0035."""
        eps_c2, eps_cu2, eps_c3, eps_cu3 = concrete_strain_limits(f_ck=25.0)
        assert_allclose(eps_c2, 0.002, rtol=1e-3)
        assert_allclose(eps_cu2, 0.0035, rtol=1e-3)
        assert_allclose(eps_c3, 0.00175, rtol=1e-3)
        assert_allclose(eps_cu3, 0.0035, rtol=1e-3)

    def test_c70_gt_c50(self):
        """C70 (>C50/60): formule EC2 Table 3.1."""
        eps_c2, eps_cu2, eps_c3, eps_cu3 = concrete_strain_limits(f_ck=70.0)
        # eps_c2 = (2.0 + 0.085*(70-50)^0.53) / 1000
        expected_c2 = (2.0 + 0.085 * (20 ** 0.53)) / 1000
        assert_allclose(eps_c2, expected_c2, rtol=1e-3)
        # eps_cu2 = (2.6 + 35*((90-70)/100)^4) / 1000
        expected_cu2 = (2.6 + 35.0 * (0.2 ** 4)) / 1000
        assert_allclose(eps_cu2, expected_cu2, rtol=1e-3)
        # eps_c3 = (1.75 + 0.55*(70-50)/40) / 1000
        expected_c3 = (1.75 + 0.55 * 20 / 40) / 1000
        assert_allclose(eps_c3, expected_c3, rtol=1e-3)
        # eps_cu3 = eps_cu2 per NTC18
        assert_allclose(eps_cu3, expected_cu2, rtol=1e-3)

    def test_c90(self):
        """C90 (limite superiore classi di resistenza)."""
        eps_c2, eps_cu2, eps_c3, eps_cu3 = concrete_strain_limits(f_ck=90.0)
        expected_c2 = (2.0 + 0.085 * (40 ** 0.53)) / 1000
        expected_cu2 = (2.6 + 35.0 * (0.0 ** 4)) / 1000  # (90-90)/100=0
        assert_allclose(eps_c2, expected_c2, rtol=1e-3)
        assert_allclose(eps_cu2, 0.0026, rtol=1e-3)

    def test_negative_fck_raises(self):
        with pytest.raises(ValueError):
            concrete_strain_limits(f_ck=-10.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(concrete_strain_limits)
        assert ref is not None
        assert ref.article == "4.1.2.1.2.1"


# ── [4.1.8-4.1.12] — Calcestruzzo confinato ──────────────────────────────────


class TestConcreteConfinedStrength:
    """NTC18 §4.1.2.1.2.1 (confinamento), Formule [4.1.8]-[4.1.11]."""

    def test_low_confinement(self):
        """sigma_2=1.0 <= 0.05*30=1.5: formula [4.1.8]."""
        f_ck_c, eps_c2_c, eps_cu_c = concrete_confined_strength(
            f_ck=30.0, sigma_2=1.0,
        )
        # f_ck_c = 30*(1 + 5*1/30) = 35.0
        assert_allclose(f_ck_c, 35.0, rtol=1e-3)
        # eps_c2_c = 0.002 * (35/30)^2
        assert_allclose(eps_c2_c, 0.002 * (35 / 30) ** 2, rtol=1e-3)
        # eps_cu_c = 0.0035 + 0.2 * 1/30
        assert_allclose(eps_cu_c, 0.0035 + 0.2 * 1 / 30, rtol=1e-3)

    def test_high_confinement(self):
        """sigma_2=3.0 > 0.05*30=1.5: formula [4.1.9]."""
        f_ck_c, eps_c2_c, eps_cu_c = concrete_confined_strength(
            f_ck=30.0, sigma_2=3.0,
        )
        # f_ck_c = 30*(1.125 + 2.5*3/30) = 30*1.375 = 41.25
        assert_allclose(f_ck_c, 41.25, rtol=1e-3)
        assert_allclose(eps_c2_c, 0.002 * (41.25 / 30) ** 2, rtol=1e-3)
        assert_allclose(eps_cu_c, 0.0035 + 0.2 * 3 / 30, rtol=1e-3)

    def test_boundary(self):
        """sigma_2 = 0.05*f_ck esatto: usa formula [4.1.8]."""
        f_ck_c, _, _ = concrete_confined_strength(f_ck=30.0, sigma_2=1.5)
        # f_ck_c = 30*(1+5*1.5/30) = 30*1.25 = 37.5
        assert_allclose(f_ck_c, 37.5, rtol=1e-3)

    def test_negative_sigma2_raises(self):
        with pytest.raises(ValueError):
            concrete_confined_strength(f_ck=30.0, sigma_2=-1.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(concrete_confined_strength)
        assert ref is not None
        assert ref.article == "4.1.2.1.2.1"


# ── [4.1.15-16] — Limite tensione calcestruzzo SLE ───────────────────────────


class TestConcreteStressLimit:
    """NTC18 §4.1.2.2.5.1, Formule [4.1.15]-[4.1.16]."""

    def test_characteristic(self):
        """Combinazione caratteristica: sigma_c_max = 0.60*25 = 15.0 MPa."""
        result = concrete_stress_limit(f_ck=25.0, combination="characteristic")
        assert_allclose(result, 15.0, rtol=1e-3)

    def test_quasi_permanent(self):
        """Combinazione quasi permanente: sigma_c_max = 0.45*25 = 11.25 MPa."""
        result = concrete_stress_limit(f_ck=25.0, combination="quasi_permanent")
        assert_allclose(result, 11.25, rtol=1e-3)

    def test_invalid_combination_raises(self):
        with pytest.raises(ValueError):
            concrete_stress_limit(f_ck=25.0, combination="invalid")

    def test_ntc_ref(self):
        ref = get_ntc_ref(concrete_stress_limit)
        assert ref is not None
        assert ref.article == "4.1.2.2.5.1"


# ── [4.1.17] — Limite tensione acciaio SLE ───────────────────────────────────


class TestSteelStressLimit:
    """NTC18 §4.1.2.2.5.2, Formula [4.1.17]."""

    def test_b450c(self):
        """B450C: sigma_s_max = 0.80*450 = 360 MPa."""
        result = steel_stress_limit(f_yk=450.0)
        assert_allclose(result, 360.0, rtol=1e-3)

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            steel_stress_limit(f_yk=-100.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(steel_stress_limit)
        assert ref is not None
        assert ref.article == "4.1.2.2.5.2"


# ── [4.1.23] — Taglio senza armature trasversali ─────────────────────────────


class TestShearResistanceNoStirrups:
    """NTC18 §4.1.2.3.5.1, Formula [4.1.23]."""

    def test_basic(self):
        """f_ck=25, d=400mm, bw=300mm, rho_l=0.01, sigma_cp=0.
        k = 1+sqrt(200/400)=1.7071
        Term1 = [0.12*1.7071*(100*0.01*25)^(1/3)]*300*400 = 71858 N
        """
        result = shear_resistance_no_stirrups(
            f_ck=25.0, d=400.0, bw=300.0, rho_l=0.01,
        )
        k = 1 + math.sqrt(200 / 400)
        term1 = (0.12 * k * (100 * 0.01 * 25) ** (1 / 3)) * 300 * 400
        assert_allclose(result, term1, rtol=1e-3)

    def test_with_compression(self):
        """sigma_cp=2.0 MPa aggiunge 0.15*sigma_cp al termine."""
        result = shear_resistance_no_stirrups(
            f_ck=25.0, d=400.0, bw=300.0, rho_l=0.01, sigma_cp=2.0,
        )
        k = 1 + math.sqrt(200 / 400)
        term1 = (0.12 * k * (100 * 0.01 * 25) ** (1 / 3) + 0.15 * 2.0) * 300 * 400
        v_min = 0.035 * k ** 1.5 * 25 ** 0.5
        term2 = (v_min + 0.15 * 2.0) * 300 * 400
        assert_allclose(result, max(term1, term2), rtol=1e-3)

    def test_vmin_controls(self):
        """rho_l molto basso: il termine v_min governa."""
        result = shear_resistance_no_stirrups(
            f_ck=25.0, d=400.0, bw=300.0, rho_l=0.001,
        )
        k = 1 + math.sqrt(200 / 400)
        term1 = (0.12 * k * (100 * 0.001 * 25) ** (1 / 3)) * 300 * 400
        v_min = 0.035 * k ** 1.5 * 25 ** 0.5
        term2 = v_min * 300 * 400
        # v_min deve governare
        assert result == pytest.approx(term2, rel=1e-3)
        assert term2 > term1

    def test_rho_capped_at_002(self):
        """rho_l=0.03 viene cappato a 0.02."""
        result1 = shear_resistance_no_stirrups(
            f_ck=25.0, d=400.0, bw=300.0, rho_l=0.03,
        )
        result2 = shear_resistance_no_stirrups(
            f_ck=25.0, d=400.0, bw=300.0, rho_l=0.02,
        )
        assert_allclose(result1, result2, rtol=1e-6)

    def test_low_d_k_capped(self):
        """d=100mm: k=1+sqrt(200/100)=2.414 -> cappato a 2.0."""
        result = shear_resistance_no_stirrups(
            f_ck=25.0, d=100.0, bw=300.0, rho_l=0.01,
        )
        k = 2.0  # cappato
        term1 = (0.12 * k * (100 * 0.01 * 25) ** (1 / 3)) * 300 * 100
        v_min = 0.035 * k ** 1.5 * 25 ** 0.5
        term2 = v_min * 300 * 100
        assert_allclose(result, max(term1, term2), rtol=1e-3)

    def test_negative_d_raises(self):
        with pytest.raises(ValueError):
            shear_resistance_no_stirrups(f_ck=25.0, d=-100.0, bw=300.0, rho_l=0.01)

    def test_ntc_ref(self):
        ref = get_ntc_ref(shear_resistance_no_stirrups)
        assert ref is not None
        assert ref.article == "4.1.2.3.5.1"


# ── [4.1.27-29] — Taglio con armature trasversali ────────────────────────────


class TestShearResistanceWithStirrups:
    """NTC18 §4.1.2.3.5.2, Formule [4.1.27]-[4.1.29]."""

    def test_vertical_cot1(self):
        """Staffe verticali, cot_theta=1 (theta=45deg). Acciaio governa.
        V_Rsd = 0.9*400*(200/200)*391.3*1*1 = 140868 N
        """
        result = shear_resistance_with_stirrups(
            d=400.0, bw=300.0, Asw=200.0, s=200.0,
            f_yd=391.3, f_cd=14.17, cot_theta=1.0,
        )
        V_Rsd = 0.9 * 400 * 1.0 * 391.3 * 1.0 * 1.0
        assert_allclose(result, V_Rsd, rtol=1e-3)

    def test_vertical_cot25_concrete_controls(self):
        """Staffe verticali, cot_theta=2.5. Cls governa con staffe forti.
        Asw=500, s=100 -> Asw/s=5.
        """
        result = shear_resistance_with_stirrups(
            d=400.0, bw=300.0, Asw=500.0, s=100.0,
            f_yd=391.3, f_cd=14.17, cot_theta=2.5,
        )
        V_Rsd = 0.9 * 400 * 5.0 * 391.3 * 2.5 * 1.0
        V_Rcd = (
            0.9 * 400 * 300 * 1.0 * 0.5 * 14.17 * 2.5 / (1 + 2.5 ** 2)
        )
        assert_allclose(result, min(V_Rsd, V_Rcd), rtol=1e-3)
        assert V_Rcd < V_Rsd  # calcestruzzo governa

    def test_inclined_stirrups(self):
        """Staffe inclinate alpha=45deg, cot_theta=1."""
        result = shear_resistance_with_stirrups(
            d=400.0, bw=300.0, Asw=200.0, s=200.0,
            f_yd=391.3, f_cd=14.17, cot_theta=1.0, alpha=45.0,
        )
        sin_a = math.sin(math.radians(45))
        cot_a = 1.0 / math.tan(math.radians(45))
        V_Rsd = 0.9 * 400 * 1.0 * 391.3 * (cot_a + 1.0) * sin_a
        assert_allclose(result, V_Rsd, rtol=1e-3)

    def test_with_compression(self):
        """sigma_cp=5.0 MPa, 0.25*f_cd < sigma_cp < 0.5*f_cd -> alpha_c=1.25.
        Staffe forti: cls governa.
        """
        result = shear_resistance_with_stirrups(
            d=400.0, bw=300.0, Asw=500.0, s=100.0,
            f_yd=391.3, f_cd=14.17, cot_theta=1.0, sigma_cp=5.0,
        )
        # 0.25*14.17=3.5425, 0.5*14.17=7.085, 5.0 is in between -> alpha_c=1.25
        V_Rcd = 0.9 * 400 * 300 * 1.25 * 0.5 * 14.17 * 1.0 / (1 + 1.0)
        V_Rsd = 0.9 * 400 * 5.0 * 391.3 * 1.0
        assert_allclose(result, min(V_Rsd, V_Rcd), rtol=1e-3)

    def test_cot_theta_out_of_range(self):
        with pytest.raises(ValueError):
            shear_resistance_with_stirrups(
                d=400.0, bw=300.0, Asw=200.0, s=200.0,
                f_yd=391.3, f_cd=14.17, cot_theta=3.0,
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(shear_resistance_with_stirrups)
        assert ref is not None
        assert ref.article == "4.1.2.3.5.2"


# ── [4.1.35-39] — Torsione ───────────────────────────────────────────────────


class TestTorsionResistance:
    """NTC18 §4.1.2.3.6, Formule [4.1.35]-[4.1.39]."""

    def test_basic_cot1(self):
        """A=160000mm2, t=100mm, Asw=100mm2, s=200mm, cot_theta=1.
        T_Rsd governa: 2*160000*0.5*391.3*1 = 62608000 N*mm.
        """
        result = torsion_resistance(
            A=160000.0, t=100.0, Asw=100.0, s=200.0,
            f_yd=391.3, f_cd=14.17,
            sum_Al=1200.0, um=1200.0, cot_theta=1.0,
        )
        T_Rcd = 2 * 160000 * 100 * 1.0 * 0.5 * 14.17 * 1.0 / 2
        T_Rsd = 2 * 160000 * (100 / 200) * 391.3 * 1.0
        T_Rld = 2 * 160000 * (1200 / 1200) * 391.3 / 1.0
        assert_allclose(result, min(T_Rcd, T_Rsd, T_Rld), rtol=1e-3)
        assert T_Rsd < T_Rcd  # staffe governano

    def test_cot2(self):
        """cot_theta=2.0: longitudinale governa."""
        result = torsion_resistance(
            A=160000.0, t=100.0, Asw=100.0, s=200.0,
            f_yd=391.3, f_cd=14.17,
            sum_Al=1200.0, um=1200.0, cot_theta=2.0,
        )
        T_Rsd = 2 * 160000 * (100 / 200) * 391.3 * 2.0
        T_Rld = 2 * 160000 * (1200 / 1200) * 391.3 / 2.0
        assert_allclose(result, min(T_Rsd, T_Rld), rtol=1e-3)

    def test_concrete_controls(self):
        """Staffe forti e armatura longitudinale forte: cls governa."""
        result = torsion_resistance(
            A=160000.0, t=50.0, Asw=500.0, s=100.0,
            f_yd=391.3, f_cd=14.17,
            sum_Al=5000.0, um=1200.0, cot_theta=1.0,
        )
        T_Rcd = 2 * 160000 * 50 * 1.0 * 0.5 * 14.17 * 1.0 / 2.0
        T_Rsd = 2 * 160000 * (500 / 100) * 391.3 * 1.0
        T_Rld = 2 * 160000 * (5000 / 1200) * 391.3 / 1.0
        assert_allclose(result, T_Rcd, rtol=1e-3)
        assert T_Rcd < T_Rsd

    def test_cot_theta_out_of_range(self):
        with pytest.raises(ValueError):
            torsion_resistance(
                A=160000.0, t=100.0, Asw=100.0, s=200.0,
                f_yd=391.3, f_cd=14.17,
                sum_Al=1200.0, um=1200.0, cot_theta=0.5,
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(torsion_resistance)
        assert ref is not None
        assert ref.article == "4.1.2.3.6"


# ── [4.1.40] — Interazione torsione-taglio ───────────────────────────────────


class TestTorsionShearInteraction:
    """NTC18 §4.1.2.3.6, Formula [4.1.40]."""

    def test_ok(self):
        """T_Ed/T_Rcd + V_Ed/V_Rcd = 0.3 + 0.5 = 0.8."""
        result = torsion_shear_interaction(
            T_Ed=30.0, T_Rcd=100.0, V_Ed=50.0, V_Rcd=100.0,
        )
        assert_allclose(result, 0.8, rtol=1e-3)

    def test_not_ok(self):
        """Ratio > 1.0."""
        result = torsion_shear_interaction(
            T_Ed=60.0, T_Rcd=100.0, V_Ed=70.0, V_Rcd=100.0,
        )
        assert_allclose(result, 1.3, rtol=1e-3)

    def test_boundary(self):
        """Ratio = 1.0 esattamente."""
        result = torsion_shear_interaction(
            T_Ed=50.0, T_Rcd=100.0, V_Ed=50.0, V_Rcd=100.0,
        )
        assert_allclose(result, 1.0, rtol=1e-3)

    def test_ntc_ref(self):
        ref = get_ntc_ref(torsion_shear_interaction)
        assert ref is not None
        assert ref.article == "4.1.2.3.6"


# ── [4.1.19] — Pressoflessione deviata ───────────────────────────────────────


class TestBiaxialBendingCheck:
    """NTC18 §4.1.2.3.4.2, Formula [4.1.19]."""

    def test_rectangular_ok(self):
        """Sezione rettangolare, N_Ed/N_Rd=0.25 -> alpha=1.125.
        (50/100)^1.125 + (30/80)^1.125 = 0.7902 < 1.0.
        """
        result = biaxial_bending_check(
            M_Edy=50.0, M_Rdy=100.0, M_Edz=30.0, M_Rdz=80.0,
            N_Ed=500.0, N_Rd=2000.0,
        )
        expected = 0.5 ** 1.125 + 0.375 ** 1.125
        assert_allclose(result, expected, rtol=1e-3)
        assert result < 1.0

    def test_rectangular_not_ok(self):
        """Sezione rettangolare, ratio > 1.0."""
        result = biaxial_bending_check(
            M_Edy=80.0, M_Rdy=100.0, M_Edz=70.0, M_Rdz=80.0,
            N_Ed=500.0, N_Rd=2000.0,
        )
        expected = 0.8 ** 1.125 + 0.875 ** 1.125
        assert_allclose(result, expected, rtol=1e-3)
        assert result > 1.0

    def test_circular(self):
        """Sezione circolare: alpha=2.0 sempre."""
        result = biaxial_bending_check(
            M_Edy=50.0, M_Rdy=100.0, M_Edz=30.0, M_Rdz=80.0,
            N_Ed=500.0, N_Rd=2000.0, section="circular",
        )
        expected = (50 / 100) ** 2 + (30 / 80) ** 2
        assert_allclose(result, expected, rtol=1e-3)

    def test_low_nu_alpha_1(self):
        """N_Ed/N_Rd <= 0.1 -> alpha=1.0 (interpolazione lineare)."""
        result = biaxial_bending_check(
            M_Edy=50.0, M_Rdy=100.0, M_Edz=30.0, M_Rdz=80.0,
            N_Ed=100.0, N_Rd=2000.0,
        )
        # nu=0.05 <= 0.1 -> alpha=1.0
        expected = 50 / 100 + 30 / 80
        assert_allclose(result, expected, rtol=1e-3)

    def test_high_nu_alpha_2(self):
        """N_Ed/N_Rd >= 1.0 -> alpha=2.0."""
        result = biaxial_bending_check(
            M_Edy=50.0, M_Rdy=100.0, M_Edz=30.0, M_Rdz=80.0,
            N_Ed=2000.0, N_Rd=2000.0,
        )
        expected = (50 / 100) ** 2 + (30 / 80) ** 2
        assert_allclose(result, expected, rtol=1e-3)

    def test_ntc_ref(self):
        ref = get_ntc_ref(biaxial_bending_check)
        assert ref is not None
        assert ref.article == "4.1.2.3.4.2"


# ── [4.1.42] — Snellezza ─────────────────────────────────────────────────────


class TestConcreteSlenderness:
    """NTC18 §4.1.2.3.9.2, Formula [4.1.42]."""

    def test_basic(self):
        # l_0=3000, i=100 → lambda = 30
        assert_allclose(concrete_slenderness(3000.0, 100.0), 30.0, rtol=1e-6)

    def test_slender(self):
        assert_allclose(concrete_slenderness(6000.0, 120.0), 50.0, rtol=1e-6)

    def test_zero_l0_raises(self):
        with pytest.raises(ValueError):
            concrete_slenderness(0.0, 100.0)

    def test_zero_i_raises(self):
        with pytest.raises(ValueError):
            concrete_slenderness(3000.0, 0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(concrete_slenderness)
        assert ref is not None
        assert ref.article == "4.1.2.3.9.2"
        assert ref.formula == "4.1.42"


# ── [4.1.41] — Snellezza limite ───────────────────────────────────────────────


class TestConcreteSlendernessLimit:
    """NTC18 §4.1.2.3.9.2, Formula [4.1.41]."""

    def test_v_1(self):
        # v=1.0 → lambda_lim = 25
        assert_allclose(concrete_slenderness_limit(1.0), 25.0, rtol=1e-6)

    def test_v_025(self):
        # v=0.25 → lambda_lim = 25/0.5 = 50
        assert_allclose(concrete_slenderness_limit(0.25), 50.0, rtol=1e-6)

    def test_v_zero_raises(self):
        with pytest.raises(ValueError):
            concrete_slenderness_limit(0.0)

    def test_v_gt_1_raises(self):
        with pytest.raises(ValueError):
            concrete_slenderness_limit(1.01)

    def test_ntc_ref(self):
        ref = get_ntc_ref(concrete_slenderness_limit)
        assert ref is not None
        assert ref.article == "4.1.2.3.9.2"
        assert ref.formula == "4.1.41"


# ── [4.1.45] — Armatura minima travi ─────────────────────────────────────────


class TestConcreteBeamMinReinforcement:
    """NTC18 §4.1.6.1.1, Formula [4.1.45]."""

    def test_formula_governs(self):
        # 0.26*f_ctm/f_yk*b*d > 0.0013*b*d
        # f_ctm=2.9, f_yk=450, b=300, d=500
        # a1 = 0.26*2.9/450*300*500 = 0.26*0.00644*300*500 = 251.7
        # a2 = 0.0013*300*500 = 195
        result = concrete_beam_min_reinforcement(2.9, 450.0, 300.0, 500.0)
        expected = 0.26 * (2.9 / 450.0) * 300.0 * 500.0
        assert_allclose(result, expected, rtol=1e-6)
        assert result > 0.0013 * 300.0 * 500.0

    def test_minimum_governs(self):
        # Con f_ctm molto basso: a2 = 0.0013*b*d governa
        # f_ctm=0.5, f_yk=500, b=200, d=400
        # a1 = 0.26*0.001*200*400 = 20.8
        # a2 = 0.0013*200*400 = 104
        result = concrete_beam_min_reinforcement(0.5, 500.0, 200.0, 400.0)
        expected = 0.0013 * 200.0 * 400.0
        assert_allclose(result, expected, rtol=1e-6)

    def test_zero_fctm_raises(self):
        with pytest.raises(ValueError):
            concrete_beam_min_reinforcement(0.0, 450.0, 300.0, 500.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(concrete_beam_min_reinforcement)
        assert ref is not None
        assert ref.article == "4.1.6.1.1"
        assert ref.formula == "4.1.45"


# ── [4.1.46] — Armatura minima pilastri ──────────────────────────────────────


class TestConcreteColumnMinReinforcement:
    """NTC18 §4.1.6.1.2, Formula [4.1.46]."""

    def test_ned_governs(self):
        # N_Ed=1000e3 N, f_yd=391.3 MPa, A_c=300*300=90e3 mm^2
        # a1 = 0.10*1000e3/391.3 = 255.6
        # a2 = 0.003*90e3 = 270 → a2 governa
        result = concrete_column_min_reinforcement(1000e3, 391.3, 90e3)
        expected = 0.003 * 90e3
        assert_allclose(result, expected, rtol=1e-3)

    def test_ned_formula_governs(self):
        # N_Ed=5000e3, f_yd=391.3, A_c=90e3
        # a1 = 0.10*5e6/391.3 = 1278
        # a2 = 270 → a1 governa
        result = concrete_column_min_reinforcement(5000e3, 391.3, 90e3)
        expected = 0.10 * 5000e3 / 391.3
        assert_allclose(result, expected, rtol=1e-3)

    def test_zero_ned(self):
        # N_Ed=0 → always a2=0.003*A_c
        result = concrete_column_min_reinforcement(0.0, 391.3, 90e3)
        assert_allclose(result, 0.003 * 90e3, rtol=1e-6)

    def test_zero_ac_raises(self):
        with pytest.raises(ValueError):
            concrete_column_min_reinforcement(1000.0, 391.3, 0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(concrete_column_min_reinforcement)
        assert ref is not None
        assert ref.article == "4.1.6.1.2"
        assert ref.formula == "4.1.46"


# ── [4.1.49] — Tensioni limite precompressione ───────────────────────────────


class TestConcretePrestressStressLimits:
    """NTC18 §4.1.8.15, Formula [4.1.49]."""

    def test_post_tensioned(self):
        lim_01k, lim_pk = concrete_prestress_stress_limits(1500.0, 1860.0, "post_tensioned")
        assert_allclose(lim_01k, 0.85 * 1500.0, rtol=1e-6)
        assert_allclose(lim_pk, 0.75 * 1860.0, rtol=1e-6)

    def test_pre_tensioned(self):
        lim_01k, lim_pk = concrete_prestress_stress_limits(1500.0, 1860.0, "pre_tensioned")
        assert_allclose(lim_01k, 0.90 * 1500.0, rtol=1e-6)
        assert_allclose(lim_pk, 0.80 * 1860.0, rtol=1e-6)

    def test_post_tighter_than_pre(self):
        lim_post_01k, _ = concrete_prestress_stress_limits(1500.0, 1860.0, "post_tensioned")
        lim_pre_01k, _ = concrete_prestress_stress_limits(1500.0, 1860.0, "pre_tensioned")
        assert lim_post_01k < lim_pre_01k

    def test_invalid_type_raises(self):
        with pytest.raises(ValueError):
            concrete_prestress_stress_limits(1500.0, 1860.0, "unknown")

    def test_ntc_ref(self):
        ref = get_ntc_ref(concrete_prestress_stress_limits)
        assert ref is not None
        assert ref.article == "4.1.8.15"
        assert ref.formula == "4.1.49"
