# Create: backend/create_all_tables.py
import sys
import os
sys.path.append('.')

from app.models import Base
from app.database import engine

print("Creating all tables...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully!")
