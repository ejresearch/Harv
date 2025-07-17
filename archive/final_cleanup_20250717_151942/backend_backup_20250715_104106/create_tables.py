# backend/create_tables.py

from sqlalchemy import create_engine
from app.models import Base
from app.models import Document  # import your new model

engine = create_engine("sqlite:///harv.db")
Base.metadata.create_all(bind=engine)

print("Tables created.")

