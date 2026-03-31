from fastapi.testclient import TestClient
from app.main import app
import random
import string
import os

client = TestClient(app)

def test():
    print("Starting E2E testing...")
    
    # 1. Register User
    rand_str = lambda: ''.join(random.choices(string.ascii_lowercase, k=8))
    username = rand_str()
    email = f"{username}@e2e.com"
    password = "e2epassword"
    
    res = client.post("/auth/register", json={"username": username, "email": email, "password": password})
    assert res.status_code == 200, f"Register failed: {res.text}"
    print("User registered")
    
    # 2. Login
    res = client.post("/auth/login", data={"username": username, "password": password})
    assert res.status_code == 200, f"Login failed: {res.text}"
    token = res.json()["access_token"]
    print("User logged in")
    
    # 3. Create and Assign Role
    role_name = "Admin"
    # We might have created Admin before, so ignore 400
    res = client.post("/roles/create", json={"name": role_name}, headers={"Authorization": f"Bearer {token}"})
    if res.status_code != 200 and res.status_code != 400:
        assert False, f"Role create failed: {res.text}"
    
    from app.db.database import SessionLocal
    from app.models.user import User
    db = SessionLocal()
    user_id = db.query(User).filter(User.username == username).first().id
    db.close()
    
    res = client.post("/users/assign-role", json={"user_id": user_id, "role_name": role_name}, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200, f"Role assign failed: {res.text}"
    print("Admin role assigned")
    
    # 4. Upload Document
    with open("e2e_test.pdf", "wb") as f:
        f.write(b"E2E test document. This report describes high debt ratio and associated risks for Acme Corp.")
        
    with open("e2e_test.pdf", "rb") as f:
        res = client.post(
            "/documents/upload",
            headers={"Authorization": f"Bearer {token}"},
            data={"title": "E2E Report", "company_name": "Acme Corp", "document_type": "report"},
            files={"file": ("e2e_test.pdf", f, "application/pdf")}
        )
    assert res.status_code == 200, f"Upload failed: {res.text}"
    doc_id = res.json()["document_id"]
    print(f"Document uploaded. ID: {doc_id}")
    
    # 5. Index Document
    res = client.post("/rag/index-document", json={"document_id": doc_id}, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200, f"Index failed: {res.text}"
    print("Document indexed")
    
    # 6. Search
    res = client.post("/rag/search", json={"query": "risk associated with high debt"}, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200, f"Search failed: {res.text}"
    search_res = res.json()
    assert len(search_res) > 0, "No search results"
    print(f"Search successful. Top match score: {search_res[0]['score']}")
    
    # 7. Context retrieval
    res = client.get(f"/rag/context/{doc_id}", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200, f"Context retrieval failed: {res.text}"
    print("Context retrieved")
    
    # 8. Delete Document
    res = client.delete(f"/documents/{doc_id}", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200, f"Delete failed: {res.text}"
    print("Document deleted")
    
    # 9. Clean up test file
    os.remove("e2e_test.pdf")
    
    print("\nE2E testing completed successfully!")

if __name__ == "__main__":
    test()
