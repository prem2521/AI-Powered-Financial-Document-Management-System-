from fastapi.testclient import TestClient
from app.main import app
import random
import string
import os

client = TestClient(app)

def test():
    rand_str = lambda: ''.join(random.choices(string.ascii_lowercase, k=8))
    username = rand_str()
    email = f"{username}@example.com"
    password = "password123"

    client.post("/auth/register", json={"username": username, "email": email, "password": password})
    res = client.post("/auth/login", data={"username": username, "password": password})
    token = res.json()["access_token"]
    
    role_name = "Admin"
    client.post("/roles/create", json={"name": role_name}, headers={"Authorization": f"Bearer {token}"})
    
    from app.db.database import SessionLocal
    from app.models.user import User
    db = SessionLocal()
    user_id = db.query(User).filter(User.username == username).first().id
    db.close()
    
    client.post("/users/assign-role", json={"user_id": user_id, "role_name": role_name}, headers={"Authorization": f"Bearer {token}"})

    with open("dummy_search.pdf", "wb") as f:
        f.write(b"The financial risk related to high debt ratio is quite severe. The company's assets might be seized.")

    with open("dummy_search.pdf", "rb") as f:
        res = client.post(
            "/documents/upload",
            headers={"Authorization": f"Bearer {token}"},
            data={"title": "RAG Doc", "company_name": "RAG Co", "document_type": "report"},
            files={"file": ("dummy_search.pdf", f, "application/pdf")}
        )
    
    doc = res.json()
    doc_id = doc["document_id"]
    
    client.post("/rag/index-document", json={"document_id": doc_id}, headers={"Authorization": f"Bearer {token}"})
    
    # Test Context
    res = client.get(f"/rag/context/{doc_id}", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200, f"Context failed: {res.text}"
    assert len(res.json()["chunks"]) > 0
    
    # Test Search
    res = client.post("/rag/search", json={"query": "financial risk related to high debt ratio"}, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200, f"Search failed: {res.text}"
    search_results = res.json()
    assert len(search_results) > 0
    assert "content" in search_results[0]
    assert "score" in search_results[0]
    
    print("RAG search APIs tests passed.")
    os.remove("dummy_search.pdf")

if __name__ == "__main__":
    test()
