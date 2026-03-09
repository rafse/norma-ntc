"""Test per l'indice navigabile NTC18."""

import pytest

from pyntc.core.index import NTC18Index, ntc18


class TestNTC18IndexAccess:
    """Test accesso base all'indice."""

    def test_singleton_loads(self):
        assert len(ntc18) > 800

    def test_getitem_existing_section(self):
        s = ntc18["4.1"]
        assert s.number == "4.1"
        assert "CALCESTRUZZO" in s.title.upper()

    def test_getitem_deep_section(self):
        s = ntc18["4.1.2.3.5.1"]
        assert "taglio" in s.title.lower() or "armature" in s.title.lower()

    def test_getitem_missing_raises_keyerror(self):
        with pytest.raises(KeyError, match="99.99"):
            ntc18["99.99"]

    def test_get_returns_none_for_missing(self):
        assert ntc18.get("99.99") is None

    def test_get_returns_section_for_existing(self):
        s = ntc18.get("3.1")
        assert s is not None
        assert s.number == "3.1"

    def test_contains(self):
        assert "4.1" in ntc18
        assert "99.99" not in ntc18

    def test_trailing_dot_stripped(self):
        s = ntc18["4.1."]
        assert s.number == "4.1"


class TestSectionContent:
    """Test contenuto delle sezioni."""

    def test_section_has_title(self):
        s = ntc18["4.2"]
        assert s.title  # Non vuoto

    def test_section_with_formulas(self):
        s = ntc18["4.1.2.3.5.1"]
        assert len(s.formulas) > 0

    def test_section_with_tables(self):
        # §3.1 ha tabelle dei pesi propri
        s = ntc18["3.1"]
        # Le tabelle possono essere nelle sotto-sezioni
        has_tables = s.tables or any(
            ntc18.get(c) and ntc18[c].tables for c in s.children
        )
        assert has_tables

    def test_section_depth(self):
        assert ntc18["4"].depth == 1
        assert ntc18["4.1"].depth == 2
        assert ntc18["4.1.2.3.5.1"].depth == 6

    def test_section_summary(self):
        s = ntc18["4.1.2.3.5.1"]
        summary = s.summary()
        assert "§4.1.2.3.5.1" in summary


class TestHierarchy:
    """Test struttura gerarchica."""

    def test_chapter_has_children(self):
        s = ntc18["4"]
        assert len(s.children) > 0

    def test_parent_link(self):
        s = ntc18["4.1.2.3.5.1"]
        assert s.parent == "4.1.2.3.5"

    def test_top_level_no_parent(self):
        for ch in ntc18.chapters():
            assert ch.parent is None or ch.depth == 1

    def test_children_sorted(self):
        s = ntc18["4.1"]
        assert s.children == sorted(
            s.children, key=lambda x: [int(p) for p in x.split(".")]
        )


class TestPyntcFunctions:
    """Test collegamento funzioni pyntc."""

    def test_section_has_pyntc_functions(self):
        s = ntc18["4.1.2.3.5.1"]
        assert s.has_code
        assert any(f.name == "shear_resistance_no_stirrups" for f in s.pyntc_functions)

    def test_function_ref_has_signature(self):
        s = ntc18["4.1.2.3.5.1"]
        func = s.pyntc_functions[0]
        assert func.signature  # Non vuoto
        assert func.module.startswith("pyntc.")

    def test_functions_for_article(self):
        funcs = ntc18.functions_for_article("4.1")
        assert len(funcs) > 10  # concrete module ha molte funzioni

    def test_functions_for_article_exact(self):
        funcs = ntc18.functions_for_article("3.1.2")
        assert any(f.name == "unit_weight" for f in funcs)

    def test_total_functions(self):
        assert len(ntc18.functions) >= 150


class TestSearch:
    """Test ricerca."""

    def test_search_by_title(self):
        results = ntc18.search("taglio")
        assert len(results) > 0
        assert any("4.1.2.3.5" in s.number for s in results)

    def test_search_case_insensitive(self):
        r1 = ntc18.search("TAGLIO")
        r2 = ntc18.search("taglio")
        assert len(r1) == len(r2)

    def test_search_no_results(self):
        results = ntc18.search("zzzznonexistent")
        assert len(results) == 0

    def test_search_with_text(self):
        results = ntc18.search("punzonamento", include_text=True)
        assert len(results) > 0


class TestCoverage:
    """Test statistiche di copertura."""

    def test_coverage_structure(self):
        cov = ntc18.coverage()
        assert "total_sections" in cov
        assert "sections_with_code" in cov
        assert "total_functions" in cov
        assert "coverage_pct" in cov

    def test_coverage_values(self):
        cov = ntc18.coverage()
        assert cov["total_sections"] > 800
        assert cov["sections_with_code"] > 100
        assert cov["total_functions"] >= 150
