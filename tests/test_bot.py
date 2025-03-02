import os
import pytest
from bot.bot import get_personality

def test_get_personality():
    """Test que la récupération de la personnalité fonctionne même si l'API est indisponible"""
    os.environ["FASTAPI_URL"] = "http://invalid-url"
    personality = get_personality()
    assert personality in ["neutre", "sombre", "bienveillant", "drôle"]
