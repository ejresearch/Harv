import os
import sys
sys.path.append('.')

from app.models import Base
from app.database import engine, DATABASE_URL

def recreate_database():
    # Remove existing database
    if os.path.exists("harv.db"):
        os.remove("harv.db")
        print("Removed existing database")
    
    # Create all tables with new schema
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Database created successfully!")

if __name__ == "__main__":
    recreate_database()
