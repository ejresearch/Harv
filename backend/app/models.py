from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

# Enhanced User model (maintains compatibility with existing)
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)  # Keeping your existing field name
    name = Column(String)
    onboarding_data = Column(Text)  # Your existing field
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user")
    progress = relationship("UserProgress", back_populates="user")
    onboarding_survey = relationship("OnboardingSurvey", back_populates="user", uselist=False)
    documents = relationship("Document", back_populates="user")
    memory_summaries = relationship("MemorySummary", back_populates="user")

# Enhanced Module model (maintains your GPT configuration fields)
class Module(Base):
    __tablename__ = "modules"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    resources = Column(Text)
    
    # Your existing GPT configuration fields (preserved)
    system_prompt = Column(Text)
    module_prompt = Column(Text)
    system_corpus = Column(Text)
    module_corpus = Column(Text)
    dynamic_corpus = Column(Text)
    api_endpoint = Column(String, default="https://api.openai.com/v1/chat/completions")
    
    # New enhanced fields
    learning_objectives = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    conversations = relationship("Conversation", back_populates="module")
    progress = relationship("UserProgress", back_populates="module")
    module_corpus_entries = relationship("ModuleCorpusEntry", back_populates="module")

# Enhanced Conversation model (maintains your existing structure)
class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    module_id = Column(Integer, ForeignKey("modules.id"))
    title = Column(String, default="New Conversation")
    messages_json = Column(Text)  # Your existing field name
    
    # New enhanced fields
    current_grade = Column(String)  # A, B, C, D, F
    memory_summary = Column(Text)
    finalized = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    module = relationship("Module", back_populates="conversations")

# Your existing Document model (preserved)
class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"))
    filename = Column(String)
    content = Column(Text)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Add user relationship for enhanced functionality
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="documents")

# Enhanced MemorySummary model (builds on your existing)
class MemorySummary(Base):
    __tablename__ = "memory_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    module_id = Column(Integer, ForeignKey("modules.id"))
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    
    # Your existing fields
    what_learned = Column(Text)
    how_learned = Column(Text)
    
    # Enhanced fields
    key_concepts = Column(Text)  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="memory_summaries")
    conversation = relationship("Conversation")

# NEW: User Progress tracking
class UserProgress(Base):
    __tablename__ = "user_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    module_id = Column(Integer, ForeignKey("modules.id"))
    completed = Column(Boolean, default=False)
    grade = Column(String)  # A, B, C, D, F
    completion_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="progress")
    module = relationship("Module", back_populates="progress")

# NEW: Structured onboarding (separate from your existing onboarding_data text field)
class OnboardingSurvey(Base):
    __tablename__ = "onboarding_surveys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    reason = Column(Text)
    familiarity = Column(String)  # "Not at all", "Somewhat", "Very"
    learning_style = Column(String)  # "Visual", "Auditory", etc.
    goals = Column(Text)
    background = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="onboarding_survey")

# NEW: Course-wide knowledge base (enhances your system_corpus)
class CourseCorpus(Base):
    __tablename__ = "course_corpus"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    type = Column(String, nullable=False)  # "syllabus", "policy", "objective"
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# NEW: Structured module content (enhances your module_corpus)
class ModuleCorpusEntry(Base):
    __tablename__ = "module_corpus_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"))
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    type = Column(String, nullable=False)  # "reading", "slide", "example", "case_study"
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    module = relationship("Module", back_populates="module_corpus_entries")
