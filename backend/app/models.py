from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String)
    onboarding_data = Column(Text)

class Module(Base):
    __tablename__ = 'modules'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    system_prompt = Column(Text)
    resources = Column(Text)

class Conversation(Base):
    __tablename__ = 'conversations'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    module_id = Column(Integer, ForeignKey('modules.id'))
    messages_json = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MemorySummary(Base):
    __tablename__ = 'memory_summaries'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    module_id = Column(Integer, ForeignKey('modules.id'))
    what_learned = Column(Text)
    how_learned = Column(Text)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

