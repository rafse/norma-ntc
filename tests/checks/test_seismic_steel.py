"""Test per seismic_steel — NTC18 §7.5."""

import math
import pytest
from numpy.testing import assert_allclose

from pyntc.checks.seismic_steel import (
    seismic_steel_cbf_column_buckling_check,
    seismic_steel_cbf_diagonal_slenderness,
    seismic_steel_cbf_member_demand,
    seismic_steel_cbf_omega_homogeneity,
    seismic_steel_column_axial_ductility,
    seismic_steel_connection_resistance,
    seismic_steel_ebf_connection_demand,
    seismic_steel_ebf_link_bending_resistance,
    seismic_steel_ebf_link_bending_resistance_reduced,
    seismic_steel_ebf_link_classification,
    seismic_steel_ebf_link_length_limit,
    seismic_steel_ebf_link_shear_resistance,
    seismic_steel_ebf_link_shear_resistance_reduced,
    seismic_steel_ebf_member_demand,
    seismic_steel_ebf_omega_homogeneity,
    seismic_steel_mrf_beam_column_hierarchy,
    seismic_steel_mrf_column_demand_M,
    seismic_steel_mrf_column_demand_N,
    seismic_steel_mrf_column_demand_V,
    seismic_steel_mrf_connection_moment,
    seismic_steel_net_section_check,
    seismic_steel_section_class_check,
)
from pyntc.core.reference import get_ntc_ref


# ── [7.5.1] — Verifica collegamento in zona dissipativa ──────────────────────


class TestSeismicSteelConnectionResistance:
    """NTC18 §7.5.3.1, Formula [7.5.1]."""

    def test_basic_satisfied(self):
        """R_j,d = 200 kN, gamma_ov=1.25, R_p_LRd=100 kN -> R_U=137.5, ratio=1.455."""
        ok, ratio = seismic_steel_connection_resistance(
            R_j_d=200.0, gamma_ov=1.25, R_p_LRd=100.0
        )
        R_U = 1.1 * 1.25 * 100.0
        assert ok is True
        assert_allclose(ratio, 200.0 / R_U, rtol=1e-3)

    def test_not_satisfied(self):
        """R_j,d < 1.1 * gamma_ov * R_p_LRd -> verifica non soddisfatta."""
        ok, ratio = seismic_steel_connection_resistance(
            R_j_d=100.0, gamma_ov=1.25, R_p_LRd=100.0
        )
        assert ok is False
        assert ratio < 1.0

    def test_exact_boundary(self):
        """R_j,d = 1.1 * gamma_ov * R_p_LRd -> ratio = 1.0, soddisfatta."""
        R_U = 1.1 * 1.25 * 100.0
        ok, ratio = seismic_steel_connection_resistance(
            R_j_d=R_U, gamma_ov=1.25, R_p_LRd=100.0
        )
        assert ok is True
        assert_allclose(ratio, 1.0, rtol=1e-6)

    def test_edge_case_R_j_d_zero_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_connection_resistance(
                R_j_d=0.0, gamma_ov=1.25, R_p_LRd=100.0
            )

    def test_edge_case_gamma_ov_nonpositive_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_connection_resistance(
                R_j_d=200.0, gamma_ov=0.0, R_p_LRd=100.0
            )

    def test_edge_case_R_p_LRd_zero_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_connection_resistance(
                R_j_d=200.0, gamma_ov=1.25, R_p_LRd=0.0
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_steel_connection_resistance)
        assert ref is not None
        assert ref.article == "7.5.3.1"
        assert ref.formula == "7.5.1"


# ── [7.5.2] — Verifica sezione netta collegamenti bullonati ──────────────────


class TestSeismicSteelNetSectionCheck:
    """NTC18 §7.5.3.1, Formula [7.5.2]."""

    def test_basic_satisfied(self):
        """A_res/A = 0.9, 1.1*gamma_M2/gamma_M0 = 1.1*1.25/1.0 = 1.375 -> NOK."""
        # Con gamma_M0=1.0, gamma_M2=1.1: RHS = 1.1*1.1/1.0 = 1.21
        # A_res/A = 0.95 < 1.21 -> NOK
        ok, ratio = seismic_steel_net_section_check(
            A_res=950.0, A=1000.0, gamma_M0=1.0, gamma_M2=1.1
        )
        rhs = 1.1 * 1.1 / 1.0
        assert ok is False
        assert_allclose(ratio, (950.0 / 1000.0) / rhs, rtol=1e-3)

    def test_satisfied_high_A_res(self):
        """Caso soddisfatto con gamma_M0=1.05, gamma_M2=1.0: RHS=1.1*1.0/1.05=1.047."""
        # A_res/A = 1.0, RHS = 1.047 -> LHS < RHS -> NOT satisfied
        # Use A_res = A = 1000 (ratio = 1.0 > 1.047? No, 1.0 < 1.047)
        # Use gamma_M2 = 0.9 so RHS = 1.1*0.9/1.05 = 0.943 < 1.0 -> satisfied
        ok, ratio = seismic_steel_net_section_check(
            A_res=1000.0, A=1000.0, gamma_M0=1.05, gamma_M2=0.9
        )
        # LHS = 1.0, RHS = 1.1*0.9/1.05 = 0.943...
        assert ok is True
        assert ratio > 1.0

    def test_edge_case_A_res_greater_than_A_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_net_section_check(
                A_res=1100.0, A=1000.0, gamma_M0=1.0, gamma_M2=1.25
            )

    def test_edge_case_A_zero_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_net_section_check(
                A_res=800.0, A=0.0, gamma_M0=1.0, gamma_M2=1.25
            )

    def test_edge_case_gamma_M0_zero_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_net_section_check(
                A_res=800.0, A=1000.0, gamma_M0=0.0, gamma_M2=1.25
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_steel_net_section_check)
        assert ref is not None
        assert ref.formula == "7.5.2"


# ── [7.5.3] — Duttilita' colonne strutture a telaio ──────────────────────────


class TestSeismicSteelColumnAxialDuctility:
    """NTC18 §7.5.3.2, Formula [7.5.3]."""

    def test_basic_satisfied(self):
        """N_Ed/N_p_LRd = 0.25 <= 0.3 -> OK."""
        ok, ratio = seismic_steel_column_axial_ductility(
            N_Ed=250.0, N_p_LRd=1000.0
        )
        assert ok is True
        assert_allclose(ratio, 0.25, rtol=1e-3)

    def test_not_satisfied(self):
        """N_Ed/N_p_LRd = 0.4 > 0.3 -> NOK."""
        ok, ratio = seismic_steel_column_axial_ductility(
            N_Ed=400.0, N_p_LRd=1000.0
        )
        assert ok is False
        assert_allclose(ratio, 0.4, rtol=1e-3)

    def test_edge_case_exact_limit(self):
        """N_Ed/N_p_LRd = 0.3 esattamente -> OK (limite incluso)."""
        ok, ratio = seismic_steel_column_axial_ductility(
            N_Ed=300.0, N_p_LRd=1000.0
        )
        assert ok is True
        assert_allclose(ratio, 0.3, rtol=1e-6)

    def test_edge_case_zero_N_Ed(self):
        """N_Ed = 0 -> ratio = 0, OK."""
        ok, ratio = seismic_steel_column_axial_ductility(
            N_Ed=0.0, N_p_LRd=1000.0
        )
        assert ok is True
        assert_allclose(ratio, 0.0, atol=1e-10)

    def test_edge_case_negative_N_Ed_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_column_axial_ductility(N_Ed=-100.0, N_p_LRd=1000.0)

    def test_edge_case_N_p_LRd_zero_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_column_axial_ductility(N_Ed=100.0, N_p_LRd=0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_steel_column_axial_ductility)
        assert ref is not None
        assert ref.formula == "7.5.3"


# ── Tab.7.5.1 — Classe di sezione per elementi dissipativi ───────────────────


class TestSeismicSteelSectionClassCheck:
    """NTC18 §7.5.3.2, Tab. 7.5.1."""

    def test_cda_q0_gt4_class1_ok(self):
        """CD'A', q_0=4.5, classe 1 -> OK."""
        ok, req = seismic_steel_section_class_check(
            section_class=1, q_0=4.5, ductility_class="A"
        )
        assert ok is True
        assert req == "1"

    def test_cda_q0_gt4_class2_nok(self):
        """CD'A', q_0=5.0, classe 2 -> NOK."""
        ok, req = seismic_steel_section_class_check(
            section_class=2, q_0=5.0, ductility_class="A"
        )
        assert ok is False
        assert req == "1"

    def test_cdb_q0_mid_class2_ok(self):
        """CD'B', q_0=3.0, classe 2 -> OK."""
        ok, req = seismic_steel_section_class_check(
            section_class=2, q_0=3.0, ductility_class="B"
        )
        assert ok is True
        assert req == "1 o 2"

    def test_cdb_q0_mid_class3_nok(self):
        """CD'B', 2 < q_0 <= 4, classe 3 -> NOK."""
        ok, req = seismic_steel_section_class_check(
            section_class=3, q_0=3.5, ductility_class="B"
        )
        assert ok is False
        assert req == "1 o 2"

    def test_low_q0_no_restriction(self):
        """q_0 <= 2: nessuna prescrizione -> OK qualsiasi classe."""
        ok, req = seismic_steel_section_class_check(
            section_class=3, q_0=2.0, ductility_class="B"
        )
        assert ok is True
        assert req == "nessuna"

    def test_edge_case_invalid_class_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_section_class_check(
                section_class=5, q_0=4.5, ductility_class="A"
            )

    def test_edge_case_invalid_ductility_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_section_class_check(
                section_class=1, q_0=4.5, ductility_class="C"
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_steel_section_class_check)
        assert ref is not None
        assert ref.table == "Tab.7.5.1"


# ── [7.5.7] — Domanda a sforzo normale colonne MRF ───────────────────────────


class TestSeismicSteelMrfColumnDemandN:
    """NTC18 §7.5.4.2, Formula [7.5.7]."""

    def test_basic(self):
        """N_Ed = 500 + 1.1*1.25*1.2*300 = 500 + 495 = 995 N."""
        result = seismic_steel_mrf_column_demand_N(
            N_Ed_G=500.0, gamma_ov=1.25, Omega=1.2, N_Ed_E=300.0
        )
        expected = 500.0 + 1.1 * 1.25 * 1.2 * 300.0
        assert_allclose(result, expected, rtol=1e-3)

    def test_zero_seismic_component(self):
        """N_Ed_E=0: N_Ed = N_Ed_G."""
        result = seismic_steel_mrf_column_demand_N(
            N_Ed_G=1000.0, gamma_ov=1.25, Omega=1.5, N_Ed_E=0.0
        )
        assert_allclose(result, 1000.0, rtol=1e-3)

    def test_edge_case_gamma_ov_zero_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_mrf_column_demand_N(
                N_Ed_G=500.0, gamma_ov=0.0, Omega=1.2, N_Ed_E=300.0
            )

    def test_edge_case_omega_zero_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_mrf_column_demand_N(
                N_Ed_G=500.0, gamma_ov=1.25, Omega=0.0, N_Ed_E=300.0
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_steel_mrf_column_demand_N)
        assert ref is not None
        assert ref.formula == "7.5.7"


# ── [7.5.8] — Domanda a flessione colonne MRF ────────────────────────────────


class TestSeismicSteelMrfColumnDemandM:
    """NTC18 §7.5.4.2, Formula [7.5.8]."""

    def test_basic(self):
        """M_Ed = 1000 + 1.1*1.25*1.0*500 = 1000 + 687.5 = 1687.5 N·mm."""
        result = seismic_steel_mrf_column_demand_M(
            M_Ed_G=1000.0, gamma_ov=1.25, Omega=1.0, M_Ed_E=500.0
        )
        expected = 1000.0 + 1.1 * 1.25 * 1.0 * 500.0
        assert_allclose(result, expected, rtol=1e-3)

    def test_edge_case_gamma_ov_negative_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_mrf_column_demand_M(
                M_Ed_G=1000.0, gamma_ov=-1.0, Omega=1.0, M_Ed_E=500.0
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_steel_mrf_column_demand_M)
        assert ref is not None
        assert ref.formula == "7.5.8"


# ── [7.5.9] — Domanda a taglio colonne MRF ───────────────────────────────────


class TestSeismicSteelMrfColumnDemandV:
    """NTC18 §7.5.4.2, Formula [7.5.9]."""

    def test_basic(self):
        """V_Ed = 200 + 1.1*1.25*1.1*100 = 200 + 151.25 = 351.25 N."""
        result = seismic_steel_mrf_column_demand_V(
            V_Ed_G=200.0, gamma_ov=1.25, Omega=1.1, V_Ed_E=100.0
        )
        expected = 200.0 + 1.1 * 1.25 * 1.1 * 100.0
        assert_allclose(result, expected, rtol=1e-3)

    def test_symmetry_with_demand_N(self):
        """Stessa formula di [7.5.7]: risultato identico con stessi numeri."""
        params = dict(gamma_ov=1.25, Omega=1.3)
        r_N = seismic_steel_mrf_column_demand_N(
            N_Ed_G=300.0, N_Ed_E=200.0, **params
        )
        r_V = seismic_steel_mrf_column_demand_V(
            V_Ed_G=300.0, V_Ed_E=200.0, **params
        )
        assert_allclose(r_N, r_V, rtol=1e-6)

    def test_edge_case_omega_negative_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_mrf_column_demand_V(
                V_Ed_G=200.0, gamma_ov=1.25, Omega=-1.0, V_Ed_E=100.0
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_steel_mrf_column_demand_V)
        assert ref is not None
        assert ref.formula == "7.5.9"


# ── [7.5.11] — Gerarchia delle resistenze ai nodi trave-colonna (MRF) ─────────


class TestSeismicSteelMrfBeamColumnHierarchy:
    """NTC18 §7.5.4.2, Formula [7.5.11]."""

    def test_satisfied(self):
        """Sum M_c = 700, gamma_Rd*Sum M_b = 1.3*400 = 520 -> ratio = 1.346."""
        ok, ratio = seismic_steel_mrf_beam_column_hierarchy(
            M_c_pl_Rd=[300.0, 400.0],
            M_b_pl_Rd=[200.0, 200.0],
            gamma_Rd=1.3,
        )
        assert ok is True
        assert_allclose(ratio, 700.0 / (1.3 * 400.0), rtol=1e-3)

    def test_not_satisfied(self):
        """Sum M_c = 300, gamma_Rd*Sum M_b = 1.3*400 = 520 -> ratio < 1."""
        ok, ratio = seismic_steel_mrf_beam_column_hierarchy(
            M_c_pl_Rd=[150.0, 150.0],
            M_b_pl_Rd=[200.0, 200.0],
            gamma_Rd=1.3,
        )
        assert ok is False
        assert ratio < 1.0

    def test_exact_boundary(self):
        """Sum M_c = gamma_Rd*Sum M_b -> ratio = 1.0."""
        demand = 1.3 * 400.0
        ok, ratio = seismic_steel_mrf_beam_column_hierarchy(
            M_c_pl_Rd=[demand / 2, demand / 2],
            M_b_pl_Rd=[200.0, 200.0],
            gamma_Rd=1.3,
        )
        assert ok is True
        assert_allclose(ratio, 1.0, rtol=1e-6)

    def test_edge_case_empty_M_c_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_mrf_beam_column_hierarchy(
                M_c_pl_Rd=[], M_b_pl_Rd=[200.0], gamma_Rd=1.3
            )

    def test_edge_case_empty_M_b_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_mrf_beam_column_hierarchy(
                M_c_pl_Rd=[300.0], M_b_pl_Rd=[], gamma_Rd=1.3
            )

    def test_edge_case_gamma_Rd_zero_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_mrf_beam_column_hierarchy(
                M_c_pl_Rd=[300.0], M_b_pl_Rd=[200.0], gamma_Rd=0.0
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_steel_mrf_beam_column_hierarchy)
        assert ref is not None
        assert ref.formula == "7.5.11"


# ── [7.5.12] — Collegamento trave-colonna MRF ────────────────────────────────


class TestSeismicSteelMrfConnectionMoment:
    """NTC18 §7.5.4.3, Formula [7.5.12]."""

    def test_satisfied(self):
        """M_J=200, gamma_ov=1.25, M_b=100 -> demand=137.5, ratio=1.455."""
        ok, ratio = seismic_steel_mrf_connection_moment(
            M_J_Rd=200.0, gamma_ov=1.25, M_b_pl_Rd=100.0
        )
        assert ok is True
        assert_allclose(ratio, 200.0 / (1.1 * 1.25 * 100.0), rtol=1e-3)

    def test_not_satisfied(self):
        """M_J < 1.1*gamma_ov*M_b_pl_Rd -> NOK."""
        ok, ratio = seismic_steel_mrf_connection_moment(
            M_J_Rd=100.0, gamma_ov=1.25, M_b_pl_Rd=100.0
        )
        assert ok is False
        assert ratio < 1.0

    def test_edge_case_M_J_Rd_zero_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_mrf_connection_moment(
                M_J_Rd=0.0, gamma_ov=1.25, M_b_pl_Rd=100.0
            )

    def test_edge_case_M_b_zero_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_mrf_connection_moment(
                M_J_Rd=200.0, gamma_ov=1.25, M_b_pl_Rd=0.0
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_steel_mrf_connection_moment)
        assert ref is not None
        assert ref.formula == "7.5.12"


# ── Snellezza diagonali CBF ───────────────────────────────────────────────────


class TestSeismicSteelCbfDiagonalSlenderness:
    """NTC18 §7.5.5."""

    def test_x_brace_in_range(self):
        """lambda_bar = 1.6 in [1.3, 2.0] -> OK per controvento X."""
        ok, msg = seismic_steel_cbf_diagonal_slenderness(
            lambda_bar=1.6, brace_type="X"
        )
        assert ok is True
        assert "OK" in msg

    def test_x_brace_too_low(self):
        """lambda_bar = 1.0 < 1.3 -> NOK per controvento X."""
        ok, msg = seismic_steel_cbf_diagonal_slenderness(
            lambda_bar=1.0, brace_type="X"
        )
        assert ok is False
        assert "NOK" in msg

    def test_x_brace_too_high(self):
        """lambda_bar = 2.1 > 2.0 -> NOK per controvento X."""
        ok, msg = seismic_steel_cbf_diagonal_slenderness(
            lambda_bar=2.1, brace_type="X"
        )
        assert ok is False

    def test_v_brace_ok(self):
        """lambda_bar = 1.8 <= 2.0 -> OK per controvento V."""
        ok, msg = seismic_steel_cbf_diagonal_slenderness(
            lambda_bar=1.8, brace_type="V"
        )
        assert ok is True

    def test_v_brace_too_high(self):
        """lambda_bar = 2.5 > 2.0 -> NOK per controvento V."""
        ok, msg = seismic_steel_cbf_diagonal_slenderness(
            lambda_bar=2.5, brace_type="V"
        )
        assert ok is False

    def test_x_brace_exact_lower(self):
        """lambda_bar = 1.3 esattamente -> OK per controvento X."""
        ok, _ = seismic_steel_cbf_diagonal_slenderness(
            lambda_bar=1.3, brace_type="X"
        )
        assert ok is True

    def test_x_brace_exact_upper(self):
        """lambda_bar = 2.0 esattamente -> OK per controvento X."""
        ok, _ = seismic_steel_cbf_diagonal_slenderness(
            lambda_bar=2.0, brace_type="X"
        )
        assert ok is True

    def test_edge_case_invalid_type_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_cbf_diagonal_slenderness(
                lambda_bar=1.5, brace_type="K"
            )

    def test_edge_case_zero_slenderness_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_cbf_diagonal_slenderness(
                lambda_bar=0.0, brace_type="X"
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_steel_cbf_diagonal_slenderness)
        assert ref is not None
        assert ref.article == "7.5.5"


# ── Domanda amplificata per travi/colonne CBF ─────────────────────────────────


class TestSeismicSteelCbfMemberDemand:
    """NTC18 §7.5.5, Formula [7.5.7] applicata a CBF."""

    def test_basic(self):
        """N_Ed = 1000 + 1.1*1.25*1.5*500 = 1000+1031.25 = 2031.25 N."""
        result = seismic_steel_cbf_member_demand(
            N_Ed_G=1000.0, gamma_ov=1.25, Omega=1.5, N_Ed_E=500.0
        )
        expected = 1000.0 + 1.1 * 1.25 * 1.5 * 500.0
        assert_allclose(result, expected, rtol=1e-3)

    def test_edge_case_zero_N_Ed_E(self):
        """N_Ed_E=0 -> N_Ed = N_Ed_G."""
        result = seismic_steel_cbf_member_demand(
            N_Ed_G=2000.0, gamma_ov=1.25, Omega=1.5, N_Ed_E=0.0
        )
        assert_allclose(result, 2000.0, rtol=1e-3)

    def test_edge_case_gamma_ov_zero_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_cbf_member_demand(
                N_Ed_G=1000.0, gamma_ov=0.0, Omega=1.5, N_Ed_E=500.0
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_steel_cbf_member_demand)
        assert ref is not None
        assert ref.article == "7.5.5"


# ── [7.5.15] — Verifica instabilita' colonne CBF ─────────────────────────────


class TestSeismicSteelCbfColumnBucklingCheck:
    """NTC18 §7.5.5, Formula [7.5.15]."""

    def test_satisfied(self):
        """N_Ed=800, N_hRdp=1000 -> ratio=0.8 < 1.0 -> OK."""
        ok, ratio = seismic_steel_cbf_column_buckling_check(
            N_Ed=800.0, N_hRdp=1000.0
        )
        assert ok is True
        assert_allclose(ratio, 0.8, rtol=1e-3)

    def test_not_satisfied(self):
        """N_Ed=1200, N_hRdp=1000 -> ratio=1.2 > 1.0 -> NOK."""
        ok, ratio = seismic_steel_cbf_column_buckling_check(
            N_Ed=1200.0, N_hRdp=1000.0
        )
        assert ok is False
        assert_allclose(ratio, 1.2, rtol=1e-3)

    def test_exact_boundary(self):
        """N_Ed = N_hRdp -> ratio = 1.0 -> OK."""
        ok, ratio = seismic_steel_cbf_column_buckling_check(
            N_Ed=1000.0, N_hRdp=1000.0
        )
        assert ok is True
        assert_allclose(ratio, 1.0, rtol=1e-6)

    def test_edge_case_N_Ed_negative_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_cbf_column_buckling_check(N_Ed=-100.0, N_hRdp=1000.0)

    def test_edge_case_N_hRdp_zero_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_cbf_column_buckling_check(N_Ed=800.0, N_hRdp=0.0)

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_steel_cbf_column_buckling_check)
        assert ref is not None
        assert ref.formula == "7.5.15"


# ── Omogeneita' Omega CBF ────────────────────────────────────────────────────


class TestSeismicSteelCbfOmegaHomogeneity:
    """NTC18 §7.5.5."""

    def test_satisfied(self):
        """Omega = [1.5, 1.6, 1.8] -> (1.8-1.5)/1.5 = 0.2 <= 0.25 -> OK."""
        ok, disp = seismic_steel_cbf_omega_homogeneity([1.5, 1.6, 1.8])
        assert ok is True
        assert_allclose(disp, (1.8 - 1.5) / 1.5, rtol=1e-3)

    def test_not_satisfied(self):
        """Omega = [1.0, 2.0] -> (2.0-1.0)/1.0 = 1.0 > 0.25 -> NOK."""
        ok, disp = seismic_steel_cbf_omega_homogeneity([1.0, 2.0])
        assert ok is False
        assert_allclose(disp, 1.0, rtol=1e-3)

    def test_single_value(self):
        """Un solo Omega -> dispersion = 0 -> OK."""
        ok, disp = seismic_steel_cbf_omega_homogeneity([1.5])
        assert ok is True
        assert_allclose(disp, 0.0, atol=1e-10)

    def test_edge_case_empty_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_cbf_omega_homogeneity([])

    def test_edge_case_zero_omega_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_cbf_omega_homogeneity([0.0, 1.5])

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_steel_cbf_omega_homogeneity)
        assert ref is not None
        assert ref.article == "7.5.5"


# ── [7.5.17] — Capacita' a flessione link EBF ────────────────────────────────


class TestSeismicSteelEbfLinkBendingResistance:
    """NTC18 §7.5.6, Formula [7.5.17]."""

    def test_basic(self):
        """f_y=355, b=200, t_f=15, h=400: M = 355*200*15*(400-15) = 409.725e6 N·mm."""
        result = seismic_steel_ebf_link_bending_resistance(
            f_y=355.0, b=200.0, t_f=15.0, h=400.0
        )
        expected = 355.0 * 200.0 * 15.0 * (400.0 - 15.0)
        assert_allclose(result, expected, rtol=1e-3)

    def test_higher_grade(self):
        """f_y=460, b=150, t_f=12, h=300."""
        result = seismic_steel_ebf_link_bending_resistance(
            f_y=460.0, b=150.0, t_f=12.0, h=300.0
        )
        expected = 460.0 * 150.0 * 12.0 * (300.0 - 12.0)
        assert_allclose(result, expected, rtol=1e-3)

    def test_edge_case_h_le_tf_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_ebf_link_bending_resistance(
                f_y=355.0, b=200.0, t_f=15.0, h=15.0
            )

    def test_edge_case_f_y_zero_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_ebf_link_bending_resistance(
                f_y=0.0, b=200.0, t_f=15.0, h=400.0
            )

    def test_edge_case_b_zero_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_ebf_link_bending_resistance(
                f_y=355.0, b=0.0, t_f=15.0, h=400.0
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_steel_ebf_link_bending_resistance)
        assert ref is not None
        assert ref.formula == "7.5.17"


# ── [7.5.18] — Capacita' a taglio link EBF ───────────────────────────────────


class TestSeismicSteelEbfLinkShearResistance:
    """NTC18 §7.5.6, Formula [7.5.18]."""

    def test_basic(self):
        """f_y=355, t_w=10, h=400, t_f=15: V = 355/sqrt(3)*10*(400-15)."""
        result = seismic_steel_ebf_link_shear_resistance(
            f_y=355.0, t_w=10.0, h=400.0, t_f=15.0
        )
        expected = (355.0 / math.sqrt(3.0)) * 10.0 * (400.0 - 15.0)
        assert_allclose(result, expected, rtol=1e-3)

    def test_consistency_with_bending(self):
        """V_I,Rd deve essere sempre positivo e finito."""
        result = seismic_steel_ebf_link_shear_resistance(
            f_y=275.0, t_w=8.0, h=300.0, t_f=12.0
        )
        assert result > 0

    def test_edge_case_h_le_tf_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_ebf_link_shear_resistance(
                f_y=355.0, t_w=10.0, h=10.0, t_f=15.0
            )

    def test_edge_case_t_w_zero_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_ebf_link_shear_resistance(
                f_y=355.0, t_w=0.0, h=400.0, t_f=15.0
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_steel_ebf_link_shear_resistance)
        assert ref is not None
        assert ref.formula == "7.5.18"


# ── [7.5.21] — Taglio ridotto per sforzo normale EBF ─────────────────────────


class TestSeismicSteelEbfLinkShearResistanceReduced:
    """NTC18 §7.5.6, Formula [7.5.21]."""

    def test_basic(self):
        """V_I_Rd=1000, N_Ed=500, N_p_Rd=2000: n=0.25, V_r=1000*sqrt(1-0.0625)."""
        result = seismic_steel_ebf_link_shear_resistance_reduced(
            V_I_Rd=1000.0, N_Ed=500.0, N_p_Rd=2000.0
        )
        n = 0.25
        expected = 1000.0 * math.sqrt(1.0 - n**2)
        assert_allclose(result, expected, rtol=1e-3)

    def test_zero_axial(self):
        """N_Ed=0: V_r = V_I_Rd (nessuna riduzione)."""
        result = seismic_steel_ebf_link_shear_resistance_reduced(
            V_I_Rd=1000.0, N_Ed=0.0, N_p_Rd=2000.0
        )
        assert_allclose(result, 1000.0, rtol=1e-6)

    def test_high_axial(self):
        """N_Ed = 0.9*N_p_Rd: forte riduzione."""
        V_I_Rd = 1000.0
        n = 0.9
        result = seismic_steel_ebf_link_shear_resistance_reduced(
            V_I_Rd=V_I_Rd, N_Ed=n * 2000.0, N_p_Rd=2000.0
        )
        expected = V_I_Rd * math.sqrt(1.0 - n**2)
        assert_allclose(result, expected, rtol=1e-3)

    def test_edge_case_n_ge1_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_ebf_link_shear_resistance_reduced(
                V_I_Rd=1000.0, N_Ed=2000.0, N_p_Rd=2000.0
            )

    def test_edge_case_V_I_Rd_zero_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_ebf_link_shear_resistance_reduced(
                V_I_Rd=0.0, N_Ed=500.0, N_p_Rd=2000.0
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_steel_ebf_link_shear_resistance_reduced)
        assert ref is not None
        assert ref.formula == "7.5.21"


# ── [7.5.22] — Flessione ridotta per sforzo normale EBF ──────────────────────


class TestSeismicSteelEbfLinkBendingResistanceReduced:
    """NTC18 §7.5.6, Formula [7.5.22]."""

    def test_basic(self):
        """M_I_Rd=500e6, N_Ed=300, N_p_Rd=2000: n=0.15, M_r=500e6*0.85."""
        result = seismic_steel_ebf_link_bending_resistance_reduced(
            M_I_Rd=500.0e6, N_Ed=300.0, N_p_Rd=2000.0
        )
        expected = 500.0e6 * (1.0 - 300.0 / 2000.0)
        assert_allclose(result, expected, rtol=1e-3)

    def test_zero_axial(self):
        """N_Ed=0: M_r = M_I_Rd."""
        result = seismic_steel_ebf_link_bending_resistance_reduced(
            M_I_Rd=500.0e6, N_Ed=0.0, N_p_Rd=2000.0
        )
        assert_allclose(result, 500.0e6, rtol=1e-6)

    def test_edge_case_n_ge1_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_ebf_link_bending_resistance_reduced(
                M_I_Rd=500.0e6, N_Ed=2000.0, N_p_Rd=2000.0
            )

    def test_edge_case_M_I_Rd_zero_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_ebf_link_bending_resistance_reduced(
                M_I_Rd=0.0, N_Ed=300.0, N_p_Rd=2000.0
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_steel_ebf_link_bending_resistance_reduced)
        assert ref is not None
        assert ref.formula == "7.5.22"


# ── [7.5.23]-[7.5.24] — Lunghezza massima link EBF ───────────────────────────


class TestSeismicSteelEbfLinkLengthLimit:
    """NTC18 §7.5.6, Formule [7.5.23]-[7.5.24]."""

    def test_r_low_formula_7523(self):
        """R < 0.3: e_lim = 1.6 * M/V; e = 300, M=1e6, V=1000 -> e_lim=1600."""
        ok, e_lim, formula = seismic_steel_ebf_link_length_limit(
            e=300.0, M_I_Rd=1.0e6, V_I_Rd=1000.0, R=0.2
        )
        assert formula == "7.5.23"
        assert_allclose(e_lim, 1.6 * 1.0e6 / 1000.0, rtol=1e-3)
        assert ok is True

    def test_r_low_formula_7523_exceeded(self):
        """R < 0.3: e > e_lim -> NOK."""
        ok, e_lim, formula = seismic_steel_ebf_link_length_limit(
            e=2000.0, M_I_Rd=1.0e6, V_I_Rd=1000.0, R=0.2
        )
        assert formula == "7.5.23"
        assert ok is False

    def test_r_high_formula_7524(self):
        """R = 0.5 >= 0.3: e_lim = (1.15-0.5*0.5)*1.6*M/V = 0.9*1.6*M/V."""
        M = 1.0e6
        V = 1000.0
        R = 0.5
        ok, e_lim, formula = seismic_steel_ebf_link_length_limit(
            e=1300.0, M_I_Rd=M, V_I_Rd=V, R=R
        )
        expected_lim = (1.15 - 0.5 * R) * 1.6 * M / V
        assert formula == "7.5.24"
        assert_allclose(e_lim, expected_lim, rtol=1e-3)

    def test_exact_boundary_r(self):
        """R = 0.3 esattamente -> usa formula [7.5.24]."""
        _, _, formula = seismic_steel_ebf_link_length_limit(
            e=100.0, M_I_Rd=1.0e6, V_I_Rd=1000.0, R=0.3
        )
        assert formula == "7.5.24"

    def test_edge_case_e_zero_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_ebf_link_length_limit(
                e=0.0, M_I_Rd=1.0e6, V_I_Rd=1000.0, R=0.1
            )

    def test_edge_case_R_negative_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_ebf_link_length_limit(
                e=100.0, M_I_Rd=1.0e6, V_I_Rd=1000.0, R=-0.1
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_steel_ebf_link_length_limit)
        assert ref is not None
        assert ref.formula == "7.5.23"


# ── [7.5.16a-c] — Classificazione link EBF ───────────────────────────────────


class TestSeismicSteelEbfLinkClassification:
    """NTC18 §7.5.6, Formule [7.5.16a]-[7.5.16c]."""

    def test_short_link(self):
        """e = 500 <= 0.8*(1+1)*M/V = 1.6*M/V con M=1e6, V=1000 -> e_s=1600."""
        link_type = seismic_steel_ebf_link_classification(
            e=500.0, M_I_Rd=1.0e6, V_I_Rd=1000.0, alpha=1.0
        )
        assert link_type == "corto"

    def test_long_link(self):
        """e = 4000 >= 1.5*(1+1)*M/V = 3.0*M/V con M=1e6, V=1000 -> e_l=3000."""
        link_type = seismic_steel_ebf_link_classification(
            e=4000.0, M_I_Rd=1.0e6, V_I_Rd=1000.0, alpha=1.0
        )
        assert link_type == "lungo"

    def test_intermediate_link(self):
        """e tra e_s e e_l -> intermedio."""
        link_type = seismic_steel_ebf_link_classification(
            e=2000.0, M_I_Rd=1.0e6, V_I_Rd=1000.0, alpha=1.0
        )
        assert link_type == "intermedio"

    def test_alpha_zero(self):
        """alpha=0: e_s = 0.8*(1+0)*M/V = 0.8*M/V."""
        # e_s = 0.8*1000 = 800, e_l = 1.5*1000 = 1500
        assert seismic_steel_ebf_link_classification(
            e=500.0, M_I_Rd=1.0e6, V_I_Rd=1000.0, alpha=0.0
        ) == "corto"
        assert seismic_steel_ebf_link_classification(
            e=1000.0, M_I_Rd=1.0e6, V_I_Rd=1000.0, alpha=0.0
        ) == "intermedio"
        assert seismic_steel_ebf_link_classification(
            e=2000.0, M_I_Rd=1.0e6, V_I_Rd=1000.0, alpha=0.0
        ) == "lungo"

    def test_edge_case_invalid_alpha_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_ebf_link_classification(
                e=500.0, M_I_Rd=1.0e6, V_I_Rd=1000.0, alpha=1.5
            )

    def test_edge_case_e_zero_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_ebf_link_classification(
                e=0.0, M_I_Rd=1.0e6, V_I_Rd=1000.0
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_steel_ebf_link_classification)
        assert ref is not None
        assert ref.formula == "7.5.16a"


# ── [7.5.25] — Domanda per colonne/diagonali EBF ─────────────────────────────


class TestSeismicSteelEbfMemberDemand:
    """NTC18 §7.5.6, Formula [7.5.25]."""

    def test_basic(self):
        """N_lim = 2000 + 1.1*1.25*1.8*500 = 2000+1237.5 = 3237.5 N."""
        result = seismic_steel_ebf_member_demand(
            N_Ed_G=2000.0, gamma_ov=1.25, Omega=1.8, N_Ed_E=500.0
        )
        expected = 2000.0 + 1.1 * 1.25 * 1.8 * 500.0
        assert_allclose(result, expected, rtol=1e-3)

    def test_edge_case_gamma_ov_zero_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_ebf_member_demand(
                N_Ed_G=2000.0, gamma_ov=0.0, Omega=1.8, N_Ed_E=500.0
            )

    def test_edge_case_omega_zero_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_ebf_member_demand(
                N_Ed_G=2000.0, gamma_ov=1.25, Omega=0.0, N_Ed_E=500.0
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_steel_ebf_member_demand)
        assert ref is not None
        assert ref.formula == "7.5.25"


# ── [7.5.26] — Domanda amplificata per collegamenti EBF ──────────────────────


class TestSeismicSteelEbfConnectionDemand:
    """NTC18 §7.5.6, Formula [7.5.26]."""

    def test_basic(self):
        """E_d = 100 + 1.1*1.25*2.0*50 = 100+137.5 = 237.5 N."""
        result = seismic_steel_ebf_connection_demand(
            E_d_G=100.0, gamma_ov=1.25, Omega_i=2.0, E_d_E=50.0
        )
        expected = 100.0 + 1.1 * 1.25 * 2.0 * 50.0
        assert_allclose(result, expected, rtol=1e-3)

    def test_zero_seismic_component(self):
        """E_d_E=0: E_d = E_d_G."""
        result = seismic_steel_ebf_connection_demand(
            E_d_G=200.0, gamma_ov=1.25, Omega_i=1.5, E_d_E=0.0
        )
        assert_allclose(result, 200.0, rtol=1e-3)

    def test_edge_case_gamma_ov_negative_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_ebf_connection_demand(
                E_d_G=100.0, gamma_ov=-1.0, Omega_i=1.5, E_d_E=50.0
            )

    def test_edge_case_omega_zero_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_ebf_connection_demand(
                E_d_G=100.0, gamma_ov=1.25, Omega_i=0.0, E_d_E=50.0
            )

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_steel_ebf_connection_demand)
        assert ref is not None
        assert ref.formula == "7.5.26"


# ── Omogeneita' Omega EBF ─────────────────────────────────────────────────────


class TestSeismicSteelEbfOmegaHomogeneity:
    """NTC18 §7.5.6."""

    def test_satisfied(self):
        """Omega = [1.6, 1.7, 1.9] -> (1.9-1.6)/1.6 = 0.1875 <= 0.25 -> OK."""
        ok, disp = seismic_steel_ebf_omega_homogeneity([1.6, 1.7, 1.9])
        assert ok is True
        assert_allclose(disp, (1.9 - 1.6) / 1.6, rtol=1e-3)

    def test_not_satisfied(self):
        """Omega = [1.0, 1.5] -> (1.5-1.0)/1.0 = 0.5 > 0.25 -> NOK."""
        ok, disp = seismic_steel_ebf_omega_homogeneity([1.0, 1.5])
        assert ok is False
        assert_allclose(disp, 0.5, rtol=1e-3)

    def test_exact_boundary(self):
        """Omega = [1.0, 1.25] -> dispersione = 0.25 esattamente -> OK."""
        ok, disp = seismic_steel_ebf_omega_homogeneity([1.0, 1.25])
        assert ok is True
        assert_allclose(disp, 0.25, rtol=1e-6)

    def test_edge_case_empty_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_ebf_omega_homogeneity([])

    def test_edge_case_zero_omega_raises(self):
        with pytest.raises(ValueError):
            seismic_steel_ebf_omega_homogeneity([0.0, 1.5])

    def test_ntc_ref(self):
        ref = get_ntc_ref(seismic_steel_ebf_omega_homogeneity)
        assert ref is not None
        assert ref.article == "7.5.6"
