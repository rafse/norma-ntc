"""Fixture comuni per i test pyntc."""

import pytest

# Tolleranza per confronti numerici (valori ingegneristici)
NTC_RTOL = 1e-3  # 0.1%
NTC_ATOL = 1e-6


@pytest.fixture
def rtol():
    """Tolleranza relativa standard per verifiche NTC."""
    return NTC_RTOL


@pytest.fixture
def atol():
    """Tolleranza assoluta standard per verifiche NTC."""
    return NTC_ATOL
