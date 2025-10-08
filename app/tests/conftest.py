import pytest
import os

@pytest.fixture(autouse=True)
def _patch_env(monkeypatch):
    # Valores seguros para testing (los usa app.core.config.settings)
    monkeypatch.setenv("SECRET_KEY", "secret-test")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    # Si en settings lees otros (ALGORITHM, etc.), añade aquí sus defaults.
    yield
