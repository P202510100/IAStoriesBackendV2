from datetime import timedelta, datetime, timezone
from freezegun import freeze_time
from jose import jwt
from app.core.config import settings
from app.core import security

# ---------- Hashing ----------
def test_get_password_hash_and_verify_ok():
    raw = "S3guro_123!"
    hashed = security.get_password_hash(raw)
    assert isinstance(hashed, str)
    assert hashed != raw
    assert security.verify_password(raw, hashed) is True

def test_verify_password_wrong_returns_false():
    raw = "S3guro_123!"
    hashed = security.get_password_hash(raw)
    assert security.verify_password("otra_cosa", hashed) is False

def test_hash_format_looks_secure_min_length():
    hashed = security.get_password_hash("x")
    assert len(hashed) >= 50  # heurística mínima para bcrypt/argon

# ---------- Tokens: creación ----------
@freeze_time("2025-01-01 00:00:00")
def test_create_access_token_default_exp_uses_settings():
    token = security.create_access_token(subject="user@test.com")
    claims = jwt.get_unverified_claims(token)
    assert claims["sub"] == "user@test.com"

    exp_ts = claims["exp"]
    now_ts = int(datetime.now(timezone.utc).timestamp())
    delta = exp_ts - now_ts

    expected_delta = int(settings.ACCESS_TOKEN_EXPIRE_MINUTES) * 60
    assert expected_delta - 5 <= delta <= expected_delta + 5

@freeze_time("2025-01-01 12:00:00")
def test_create_access_token_with_custom_exp_and_decode_ok():
    token = security.create_access_token(subject="abc@x.com", expires_delta=timedelta(minutes=5))
    # decode_access_token debe validar firma y devolver payload
    payload = security.decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "abc@x.com"
    assert "exp" in payload

# ---------- Tokens: decodificación / errores ----------
def test_decode_access_token_with_invalid_signature_returns_none():
    # Creamos un token con otra SECRET_KEY para simular firma inválida
    bad_token = jwt.encode({"sub": "x", "exp": int(datetime.now(timezone.utc).timestamp()) + 3600},
                           "otra-secret-diferente", algorithm="HS256")
    assert security.decode_access_token(bad_token) is None

@freeze_time("2025-01-01 13:00:00")
def test_decode_access_token_expired_returns_none():
    # Creamos a las 13:00 con exp de 1 minuto
    token = security.create_access_token(subject="exp@test.com", expires_delta=timedelta(minutes=1))
    # Avanzamos 2 minutos: 13:02 => debe estar expirado y devolver None
    with freeze_time("2025-01-01 13:02:00"):
        assert security.decode_access_token(token) is None
