from app.models import User
from app.database import get_db
from app.auth import get_password_hash
from datetime import datetime

def test_create_user():
    db = next(get_db())
    try:
        hashed_password = get_password_hash("testpassword123")
        user = User(
            email="direct@example.com",
            hashed_password=hashed_password,  # Correct field name!
            name="Direct User"
        )
        db.add(user)
        db.commit()
        print("User created successfully!")
        return user
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        return None

if __name__ == "__main__":
    test_create_user()
