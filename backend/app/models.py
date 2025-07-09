from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String)
    onboarding_data = Column(Text)

class Module(Base):
    __tablename__ = "modules"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    resources = Column(Text)
    system_prompt = Column(Text)
    
    # New fields for GPT configuration
    module_prompt = Column(Text)
    system_corpus = Column(Text)
    module_corpus = Column(Text)
    dynamic_corpus = Column(Text)
    api_endpoint = Column(String, default="https://api.openai.com/v1/chat/completions")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    module_id = Column(Integer, ForeignKey("modules.id"))
    messages_json = Column(Text)

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"))
    filename = Column(String)
    content = Column(Text)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

class MemorySummary(Base):
    __tablename__ = "memory_summaries"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    module_id = Column(Integer, ForeignKey("modules.id"))
    what_learned = Column(Text)
    how_learned = Column(Text)
