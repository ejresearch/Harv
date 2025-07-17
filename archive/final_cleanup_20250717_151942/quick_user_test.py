import sys
sys.path.append('backend')

from backend.app.models import User
from backend.app.database import SessionLocal
from backend.app.auth import get_password_hash

db = SessionLocal()

try:
    # Test exact User creation that matches your model
    hashed_password = get_password_hash("test123")
    
    user = User(
        email="simple@test.com",
        hashed_password=hashed_password,
        name="Simple Test"
    )
    
    print("✅ User object created!")
    db.add(user)
    db.commit()
    print("✅ User saved to database!")
    print(f"User ID: {user.id}, Email: {user.email}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
