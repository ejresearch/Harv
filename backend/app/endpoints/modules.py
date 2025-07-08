from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models import Module
from app.database import get_db

router = APIRouter()

class ModuleOut(BaseModel):
    id: int
    title: str
    description: str
    resources: str
    class Config:
        orm_mode = True

@router.get("/modules", response_model=list[ModuleOut])
def get_modules(db: Session = Depends(get_db)):
    modules = db.query(Module).all()
    return modules

