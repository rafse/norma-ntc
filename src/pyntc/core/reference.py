"""Decoratore @ntc_ref per tracciabilita' normativa.

Ogni funzione o classe che implementa un requisito NTC18 deve essere
decorata con @ntc_ref indicando articolo, tabella e/o formula di riferimento.
"""

from __future__ import annotations

import functools
from dataclasses import dataclass


@dataclass(frozen=True)
class NtcReference:
    """Riferimento a un articolo della norma."""

    article: str
    table: str | None = None
    formula: str | None = None
    norm: str = "NTC18"

    def __str__(self) -> str:
        parts = [f"{self.norm} §{self.article}"]
        if self.table:
            parts.append(self.table)
        if self.formula:
            parts.append(f"[{self.formula}]")
        return " - ".join(parts)


def ntc_ref(
    article: str,
    table: str | None = None,
    formula: str | None = None,
    norm: str = "NTC18",
):
    """Decoratore per tracciabilita' normativa.

    Aggiunge un attributo ``_ntc_ref`` alla funzione decorata contenente
    il riferimento normativo strutturato.

    Parameters
    ----------
    article : str
        Numero dell'articolo (es. "3.3.1").
    table : str, optional
        Riferimento tabella (es. "Tab.3.3.I").
    formula : str, optional
        Numero formula (es. "3.3.1").
    norm : str
        Norma di riferimento, default "NTC18".

    Example
    -------
    >>> @ntc_ref(article="3.3.1", table="Tab.3.3.I")
    ... def wind_base_velocity(zone: int) -> float:
    ...     ...
    """

    ref = NtcReference(article=article, table=table, formula=formula, norm=norm)

    def decorator(func):
        func._ntc_ref = ref

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


def get_ntc_ref(func) -> NtcReference | None:
    """Restituisce il riferimento normativo di una funzione decorata, o None."""
    return getattr(func, "_ntc_ref", None)
