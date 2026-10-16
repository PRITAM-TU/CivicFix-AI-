"""Shared fixtures that keep tests isolated from external AI services."""
import pytest

from app.core.ai.factory import get_ai_provider
from app.core.config import AIMode, settings


@pytest.fixture(autouse=True)
def use_mock_ai_provider(monkeypatch):
    monkeypatch.setattr(settings, "ai_mode", AIMode.mock)
    monkeypatch.setattr(settings, "ai_provider", AIMode.mock)
    get_ai_provider.cache_clear()
    yield
    get_ai_provider.cache_clear()
