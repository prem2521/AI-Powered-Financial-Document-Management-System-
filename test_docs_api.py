from fastapi.testclient import TestClient
from app.main import app
import random
import string
import os

client = TestClient(app)

def test():
    # Helper to generate random string
    rand_str = lambda: ''.join(random.choices(string.ascii_lowercase, k=8))
    
    username = rand_str()
    email = f"{username}@example.com"
    password = "password123"

    # Register
    client.post("/auth/register", json={"username": username, "email": email, "password": password})
    
    # Login
    res = client.post("/auth/login", data={"username": username, "password": password})
    token = res.json()["access_token"]
    
    # Needs Admin role to upload
    role_name = "Admin"
    client.post("/roles/create", json={"name": role_name}, headers={"Authorization": f"Bearer {token}"})
    
    from app.db.database import SessionLocal
    from app.models.user import User
    db = SessionLocal()
    user_id = db.query(User).filter(User.username == username).first().id
    db.close()
    
    client.post("/users/assign-role", json={"user_id": user_id, "role_name": role_name}, headers={"Authorization": f"Bearer {token}"})

    # Upload document
    # Create dummy file
    with open("dummy.pdf", "wb") as f:
        f.write(b"Dummy PDF content")

    with open("dummy.pdf", "rb") as f:
        res = client.post(
            "/documents/upload",
            headers={"Authorization": f"Bearer {token}"},
            data={"title": "Test Doc", "company_name": "Test Co", "document_type": "invoice"},
            files={"file": ("dummy.pdf", f, "application/pdf")}
        )
    assert res.status_code == 200, f"Upload failed: {res.text}"
    doc = res.json()
    doc_id = doc["document_id"]
    
    # Retrieve all
    res = client.get("/documents", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert len(res.json()) >= 1
    
    # Get one
    res = client.get(f"/documents/{doc_id}", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["document_id"] == doc_id
    
    # Search
    res = client.get(f"/documents/search?title=Test", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert len(res.json()) >= 1
    
    # Delete
    res = client.delete(f"/documents/{doc_id}", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200, f"Delete failed: {res.text}"
    
    os.remove("dummy.pdf")
    print("Documents APIs tests passed.")

if __name__ == "__main__":
    test()
