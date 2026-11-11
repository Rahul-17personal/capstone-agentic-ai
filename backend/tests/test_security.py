from app.security import create_access_token, decode_access_token, hash_password, verify_password


def test_password_hash_round_trip():
    password = "VeryStrongTestPassword123!"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong-password", hashed)


def test_access_token_round_trip():
    token = create_access_token("42")
    assert decode_access_token(token) == "42"
