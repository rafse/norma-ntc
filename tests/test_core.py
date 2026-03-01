"""Smoke test per il core pyntc."""

from pyntc.core.reference import ntc_ref, get_ntc_ref, NtcReference


def test_ntc_ref_decorator():
    """Verifica che @ntc_ref attacchi il riferimento normativo."""

    @ntc_ref(article="3.3.1", table="Tab.3.3.I", formula="3.3.1")
    def dummy():
        return 42

    assert dummy() == 42
    ref = get_ntc_ref(dummy)
    assert isinstance(ref, NtcReference)
    assert ref.article == "3.3.1"
    assert ref.table == "Tab.3.3.I"
    assert ref.formula == "3.3.1"
    assert ref.norm == "NTC18"


def test_ntc_ref_str():
    """Verifica rappresentazione stringa del riferimento."""
    ref = NtcReference(article="3.3.1", table="Tab.3.3.I")
    assert "NTC18" in str(ref)
    assert "3.3.1" in str(ref)


def test_get_ntc_ref_none():
    """Funzione senza decoratore restituisce None."""

    def plain():
        pass

    assert get_ntc_ref(plain) is None
