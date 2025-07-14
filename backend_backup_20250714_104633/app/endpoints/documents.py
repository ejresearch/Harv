# backend/app/endpoints/documents.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Document

router = APIRouter(prefix="/documents", tags=["documents"])

class DocumentUpload(BaseModel):
    module_id: int
    filename: str
    content: str

@router.post("/upload")
def upload_document(doc: DocumentUpload, db: Session = Depends(get_db)):
    db_doc = Document(
        module_id=doc.module_id,
        filename=doc.filename,
        content=doc.content
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return {"message": "Document uploaded", "document_id": db_doc.id}

@router.get("/{module_id}")
def get_documents(module_id: int, db: Session = Depends(get_db)):
    docs = db.query(Document).filter_by(module_id=module_id).all()
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "content": d.content,
            "uploaded_at": d.uploaded_at
        } for d in docs
    ]

