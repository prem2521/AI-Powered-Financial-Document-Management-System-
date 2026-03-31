from app.auth.jwt import create_access_token, verify_token
from app.auth.security import get_password_hash, verify_password

def test():
    # Test Password hashing
    password = "secretpassword"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)
    
    # Test JWT
    data = {"sub": "user123", "roles": ["Admin"]}
    token = create_access_token(data)
    decoded = verify_token(token)
    assert decoded["sub"] == "user123"
    assert decoded["roles"] == ["Admin"]
    assert "exp" in decoded

    print("JWT and Security utilities tests passed.")

if __name__ == "__main__":
    test()
