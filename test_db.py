from app.db.database import engine, SessionLocal
from app.models.base import Base

def test():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    print("Database connection and session creation successful.")
    db.close()

if __name__ == "__main__":
    test()
