from fastapi import HTTPException
from app.auth.dependencies import get_current_user, RoleChecker, get_current_active_user
from app.auth.jwt import create_access_token
from app.models.user import User, Role

# Mock db and user
class MockQuery:
    def __init__(self, user):
        self.user = user
    def filter(self, *args):
        return self
    def first(self):
        return self.user

class MockDb:
    def __init__(self, user):
        self.user = user
    def query(self, *args):
        return MockQuery(self.user)

def test():
    user = User(username="testuser", is_active=True, roles=[Role(name="Admin")])
    db = MockDb(user)
    token = create_access_token({"sub": "testuser"})
    
    # Test get_current_user
    current_user = get_current_user(token=token, db=db)
    assert current_user.username == "testuser"
    
    # Test RoleChecker
    checker = RoleChecker(["Admin"])
    try:
        res = checker(user)
        assert res.username == "testuser"
    except HTTPException:
        assert False, "Should not raise HTTPException"

    checker2 = RoleChecker(["Client"])
    try:
        checker2(user)
        assert False, "Should raise HTTPException"
    except HTTPException as e:
        assert e.status_code == 403

    print("Auth dependencies tests passed.")

if __name__ == "__main__":
    test()
