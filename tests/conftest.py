import pytest
from prometheus_client import REGISTRY

@pytest.fixture(autouse=True)
def clear_prometheus_registry():
    """Réinitialise le registre Prometheus pour éviter les erreurs de duplication"""
    collectors = list(REGISTRY._collector_to_names.keys())
    for collector in collectors:
        REGISTRY.unregister(collector)
