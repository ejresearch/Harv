# backend/app/models.py
"""
BACKWARD COMPATIBLE Models - Works with your existing database
REPLACE your existing models.py with this file
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

# User model (matches your existing database)
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String)
    onboarding_data = Column(Text)
    # Note: created_at, updated_at don't exist in your DB yet
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    progress = relationship("UserProgress", back_populates="user", cascade="all, delete-orphan")
    onboarding_survey = relationship("OnboardingSurvey", back_populates="user", uselist=False, cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    memory_summaries = relationship("MemorySummary", back_populates="user", cascade="all, delete-orphan")

# Module model (matches your migrated database)
class Module(Base):
    __tablename__ = "modules"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    resources = Column(Text)
    system_prompt = Column(Text)
    
    # Added by migration
    module_prompt = Column(Text)
    system_corpus = Column(Text)
    module_corpus = Column(Text)
    dynamic_corpus = Column(Text)
    api_endpoint = Column(String, default="https://api.openai.com/v1/chat/completions")
    learning_objectives = Column(Text)
    
    # Note: created_at, updated_at don't exist in your DB yet
    
    # Relationships
    conversations = relationship("Conversation", back_populates="module")
    progress = relationship("UserProgress", back_populates="module")
    module_corpus_entries = relationship("ModuleCorpusEntry", back_populates="module", cascade="all, delete-orphan")

# Conversation model (matches your existing database + added columns)
class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False)
    messages_json = Column(Text)
    created_at = Column(DateTime(timezone=True))  # This exists in your DB
    
    # Added by migration
    title = Column(String, default="New Conversation")
    current_grade = Column(String)
    memory_summary = Column(Text)
    finalized = Column(Boolean, default=False)
    updated_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    module = relationship("Module", back_populates="conversations")

# Document model (matches your existing database)
class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="CASCADE"))
    filename = Column(String)
    content = Column(Text)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Added by migration (might be NULL)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    
    # Relationships
    user = relationship("User", back_populates="documents")

# MemorySummary model (matches your existing database)
class MemorySummary(Base):
    __tablename__ = "memory_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="CASCADE"))
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"))
    what_learned = Column(Text)
    how_learned = Column(Text)
    key_concepts = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="memory_summaries")
    conversation = relationship("Conversation")

# UserProgress model (matches your existing database + added columns)
class UserProgress(Base):
    __tablename__ = "user_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False)
    completed = Column(Boolean, default=False)
    grade = Column(String)
    completion_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Added by migration (might be NULL)
    time_spent = Column(Integer, default=0)
    attempts = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="progress")
    module = relationship("Module", back_populates="progress")

# OnboardingSurvey model (matches your existing database)
class OnboardingSurvey(Base):
    __tablename__ = "onboarding_surveys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reason = Column(Text)
    familiarity = Column(String)
    learning_style = Column(String)
    goals = Column(Text)
    background = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="onboarding_survey")

# CourseCorpus model (matches your existing database)
class CourseCorpus(Base):
    __tablename__ = "course_corpus"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    type = Column(String, nullable=False)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# ModuleCorpusEntry model (matches your existing database)
class ModuleCorpusEntry(Base):
    __tablename__ = "module_corpus_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    type = Column(String, nullable=False)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    module = relationship("Module", back_populates="module_corpus_entries")
