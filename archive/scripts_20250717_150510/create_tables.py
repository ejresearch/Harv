import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "backend", "app"))

from models import Base
from database import engine

print("Creating tables…")
Base.metadata.create_all(bind=engine)
print("Done.")

