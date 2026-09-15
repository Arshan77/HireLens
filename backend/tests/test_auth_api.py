import pytest
from datetime import timedelta
from app.core.security import create_access_token, get_password_hash, verify_password


def test_register_user_success(client):
    payload = {
        "email": "Student.Alice@example.com",
        "password": "SecurePassword123!",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "student.alice@example.com"
    assert "id" in data
    assert "password" not in data
    assert "password_hash" not in data


def test_register_duplicate_email(client, create_test_user):
    create_test_user(email="alice@example.com")
    payload = {
        "email": "ALICE@example.com",
        "password": "AnotherPassword123!",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert "already exists" in data["detail"]


def test_register_oversized_password_rejected(client):
    # 73 ASCII characters = 73 UTF-8 bytes -> Must be rejected
    long_password = "A" * 73
    payload = {
        "email": "oversized@example.com",
        "password": long_password,
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("72 UTF-8 bytes" in err.get("msg", "") for err in errors)


def test_register_multibyte_unicode_password_valid(client):
    # 'P@sswørd⚡123!' -> 14 characters, 18 UTF-8 bytes -> Valid
    unicode_password = "P@sswørd⚡123!"
    payload = {
        "email": "unicode@example.com",
        "password": unicode_password,
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201

    # Verify login works with exact unicode password
    login_res = client.post(
        "/api/v1/auth/login",
        data={"username": "unicode@example.com", "password": unicode_password},
    )
    assert login_res.status_code == 200


def test_register_multibyte_unicode_password_exceeding_bytes(client):
    # '⚡' is 3 UTF-8 bytes. 25 copies = 75 bytes -> Must be rejected
    multibyte_long = "⚡" * 25
    payload = {
        "email": "multibyte_long@example.com",
        "password": multibyte_long,
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


def test_password_not_silently_truncated(client, create_test_user):
    # Base 70 characters + "12" = 72 bytes
    base_70 = "A" * 70
    pass1 = base_70 + "12"  # 72 bytes
    pass2 = base_70 + "34"  # 72 bytes (differs in last 2 characters)

    create_test_user(email="truncation_check@example.com", password=pass1)

    # Login with pass1 -> Success
    res_correct = client.post(
        "/api/v1/auth/login",
        data={"username": "truncation_check@example.com", "password": pass1},
    )
    assert res_correct.status_code == 200

    # Login with pass2 -> Fails (proves pass1 was NOT truncated to first 70 chars)
    res_wrong = client.post(
        "/api/v1/auth/login",
        data={"username": "truncation_check@example.com", "password": pass2},
    )
    assert res_wrong.status_code == 401


def test_login_success(client, create_test_user):
    user_info = create_test_user(email="bob@example.com", password="MySecretPassword123!")
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "bob@example.com", "password": "MySecretPassword123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, create_test_user):
    create_test_user(email="bob@example.com", password="MySecretPassword123!")
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "bob@example.com", "password": "WRONG_PASSWORD"},
    )
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_login_unknown_user(client):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "nobody@example.com", "password": "SomePassword"},
    )
    assert response.status_code == 401


def test_get_me_success(client, create_test_user):
    user_info = create_test_user(email="charlie@example.com")
    response = client.get("/api/v1/auth/me", headers=user_info["headers"])
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "charlie@example.com"
    assert data["id"] == user_info["user"].id
    assert "password_hash" not in data


def test_get_me_unauthorized(client):
    # No auth header
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

    # Invalid token header
    response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer INVALID_TOKEN"})
    assert response.status_code == 401


def test_get_me_expired_token(client, create_test_user):
    user_info = create_test_user(email="expired@example.com")
    expired_token = create_access_token(
        subject=user_info["user"].id, expires_delta=timedelta(seconds=-10)
    )
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401


def test_cors_preflight_and_registration_origin(client):
    # Test OPTIONS preflight request from http://localhost:5174
    headers = {
        "Origin": "http://localhost:5174",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type",
    }
    options_res = client.options("/api/v1/auth/register", headers=headers)
    assert options_res.status_code == 200
    assert options_res.headers.get("access-control-allow-origin") == "http://localhost:5174"
    assert options_res.headers.get("access-control-allow-credentials") == "true"

    # Test POST request with Origin header
    post_res = client.post(
        "/api/v1/auth/register",
        json={"email": "cors_test@example.com", "password": "Password123!"},
        headers={"Origin": "http://localhost:5174"},
    )
    assert post_res.status_code == 201
    assert post_res.headers.get("access-control-allow-origin") == "http://localhost:5174"

