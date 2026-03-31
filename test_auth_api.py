from fastapi.testclient import TestClient
from app.main import app
import random
import string

client = TestClient(app)

def test():
    # Generate random user info
    username = ''.join(random.choices(string.ascii_lowercase, k=8))
    email = f"{username}@example.com"
    password = "testpassword"

    # Register
    res = client.post("/auth/register", json={"username": username, "email": email, "password": password})
    assert res.status_code == 200, f"Register failed: {res.text}"
    token = res.json()["access_token"]
    
    # Login
    res = client.post("/auth/login", data={"username": username, "password": password})
    assert res.status_code == 200, f"Login failed: {res.text}"
    token2 = res.json()["access_token"]
    
    # Create Role
    role_name = f"Admin_{username}"
    res = client.post("/roles/create", json={"name": role_name}, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200, f"Role creation failed: {res.text}"
    
    # Get user id (Assuming it's the latest, or we just use 1 for now if DB is clean. We can find it via db, but let's assume it's simple.)
    # Instead let's write a small db query to get the user ID
    from app.db.database import SessionLocal
    from app.models.user import User
    db = SessionLocal()
    user_obj = db.query(User).filter(User.username == username).first()
    user_id = user_obj.id
    db.close()

    # Assign Role
    res = client.post("/users/assign-role", json={"user_id": user_id, "role_name": role_name}, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200, f"Role assignment failed: {res.text}"
    
    # Get Roles
    res = client.get(f"/users/{user_id}/roles", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200, f"Get roles failed: {res.text}"
    roles = res.json()
    assert len(roles) == 1
    assert roles[0]["name"] == role_name
    
    # Get Permissions
    res = client.get(f"/users/{user_id}/permissions", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200, f"Get permissions failed: {res.text}"
    
    print("Auth APIs tests passed.")

if __name__ == "__main__":
    test()
