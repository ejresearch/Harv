from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from app.models import (
    User, Module, Conversation, OnboardingSurvey, 
    CourseCorpus, ModuleCorpusEntry, MemorySummary, UserProgress
)
import json
from datetime import datetime

class MemoryContextAssembler:
    """Assembles 4-layer memory context for GPT prompts"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def assemble_full_context(
        self, 
        user: User, 
        module: Module, 
        conversation: Conversation
    ) -> Dict[str, Any]:
        """Assemble all 4 layers of memory context"""
        return {
            "system_memory": self._get_system_memory(user),
            "module_memory": self._get_module_memory(module),
            "conversation_memory": self._get_conversation_memory(conversation),
            "user_context": self._get_user_context(user)
        }
    
    def _get_system_memory(self, user: User) -> Dict[str, Any]:
        """Layer 1: System Memory (Course-wide)"""
        # Get course corpus
        course_corpus = self.db.query(CourseCorpus).order_by(CourseCorpus.order_index).all()
        
        # Get onboarding survey
        onboarding = self.db.query(OnboardingSurvey).filter(
            OnboardingSurvey.user_id == user.id
        ).first()
        
        return {
            "course_corpus": [
                {
                    "title": corpus.title,
                    "content": corpus.content,
                    "type": corpus.type
                }
                for corpus in course_corpus
            ],
            "onboarding_data": {
                "reason": onboarding.reason if onboarding else None,
                "familiarity": onboarding.familiarity if onboarding else None,
                "learning_style": onboarding.learning_style if onboarding else None,
                "goals": onboarding.goals if onboarding else None,
                "background": onboarding.background if onboarding else None
            } if onboarding else None
        }
    
    def _get_module_memory(self, module: Module) -> Dict[str, Any]:
        """Layer 2: Module Memory (Module-specific)"""
        # Get module corpus entries
        module_corpus = self.db.query(ModuleCorpusEntry).filter(
            ModuleCorpusEntry.module_id == module.id
        ).order_by(ModuleCorpusEntry.order_index).all()
        
        return {
            "module_info": {
                "title": module.title,
                "description": module.description,
                "learning_objectives": module.learning_objectives,
                "order": module.id
            },
            "module_corpus": [
                {
                    "title": corpus.title,
                    "content": corpus.content,
                    "type": corpus.type
                }
                for corpus in module_corpus
            ],
            # Include your existing corpus fields for backward compatibility
            "existing_corpus": {
                "system_prompt": module.system_prompt,
                "module_prompt": module.module_prompt,
                "system_corpus": module.system_corpus,
                "module_corpus": module.module_corpus,
                "dynamic_corpus": module.dynamic_corpus
            }
        }
    
    def _get_conversation_memory(self, conversation: Conversation) -> Dict[str, Any]:
        """Layer 3: Conversation Memory (Student progress)"""
        # Parse messages
        messages = []
        if conversation and conversation.messages_json:
            try:
                messages = json.loads(conversation.messages_json)
            except json.JSONDecodeError:
                messages = []
        
        # Get memory summaries
        memory_summaries = []
        if conversation and conversation.id:
            memory_summaries = self.db.query(MemorySummary).filter(
                MemorySummary.conversation_id == conversation.id
            ).all()
        
        return {
            "conversation_info": {
                "title": conversation.title if conversation else "New Conversation",
                "current_grade": conversation.current_grade if conversation else None,
                "memory_summary": conversation.memory_summary if conversation else None,
                "finalized": conversation.finalized if conversation else False,
                "created_at": conversation.created_at.isoformat() if conversation and conversation.created_at else None,
                "updated_at": conversation.updated_at.isoformat() if conversation and conversation.updated_at else None
            },
            "chat_history": messages,
            "memory_summaries": [
                {
                    "summary": summary.what_learned,
                    "how_learned": summary.how_learned,
                    "key_concepts": summary.key_concepts,
                    "created_at": summary.created_at.isoformat()
                }
                for summary in memory_summaries
            ]
        }
    
    def _get_user_context(self, user: User) -> Dict[str, Any]:
        """Layer 4: User Context (Personalization)"""
        # Get user progress across all modules
        progress = self.db.query(UserProgress).filter(
            UserProgress.user_id == user.id
        ).all()
        
        # Get all conversations for learning pattern analysis
        conversations = self.db.query(Conversation).filter(
            Conversation.user_id == user.id
        ).all()
        
        return {
            "user_info": {
                "name": user.name,
                "email": user.email,
                "created_at": user.created_at.isoformat() if user.created_at else None
            },
            "progress": [
                {
                    "module_id": prog.module_id,
                    "completed": prog.completed,
                    "grade": prog.grade,
                    "completion_date": prog.completion_date.isoformat() if prog.completion_date else None
                }
                for prog in progress
            ],
            "conversation_history": [
                {
                    "id": conv.id,
                    "module_id": conv.module_id,
                    "title": conv.title,
                    "current_grade": conv.current_grade,
                    "finalized": conv.finalized,
                    "message_count": len(json.loads(conv.messages_json)) if conv.messages_json else 0,
                    "created_at": conv.created_at.isoformat() if conv.created_at else None
                }
                for conv in conversations
            ]
        }
    
    def build_gpt_prompt(self, context: Dict[str, Any], user_message: str) -> str:
        """Build comprehensive GPT prompt with full context"""
        system_memory = context["system_memory"]
        module_memory = context["module_memory"]
        conversation_memory = context["conversation_memory"]
        user_context = context["user_context"]
        
        # Build context sections
        prompt_sections = []
        
        # System Memory Section
        if system_memory["course_corpus"]:
            prompt_sections.append("=== COURSE CONTEXT ===")
            for corpus in system_memory["course_corpus"]:
                prompt_sections.append(f"[{corpus['type'].upper()}] {corpus['title']}")
                prompt_sections.append(corpus['content'])
                prompt_sections.append("")
        
        # User Background Section
        if system_memory["onboarding_data"]:
            onboarding = system_memory["onboarding_data"]
            prompt_sections.append("=== STUDENT BACKGROUND ===")
            if onboarding["reason"]:
                prompt_sections.append(f"Course Motivation: {onboarding['reason']}")
            if onboarding["familiarity"]:
                prompt_sections.append(f"Prior Knowledge: {onboarding['familiarity']}")
            if onboarding["learning_style"]:
                prompt_sections.append(f"Learning Style: {onboarding['learning_style']}")
            if onboarding["goals"]:
                prompt_sections.append(f"Goals: {onboarding['goals']}")
            prompt_sections.append("")
        
        # Module Context Section
        module_info = module_memory["module_info"]
        prompt_sections.append("=== CURRENT MODULE ===")
        prompt_sections.append(f"Module: {module_info['title']}")
        if module_info["description"]:
            prompt_sections.append(f"Description: {module_info['description']}")
        if module_info["learning_objectives"]:
            prompt_sections.append(f"Learning Objectives: {module_info['learning_objectives']}")
        prompt_sections.append("")
        
        # Existing corpus integration (backward compatibility)
        existing_corpus = module_memory["existing_corpus"]
        if existing_corpus["system_prompt"]:
            prompt_sections.append("=== SOCRATIC SYSTEM PROMPT ===")
            prompt_sections.append(existing_corpus["system_prompt"])
            prompt_sections.append("")
        
        if existing_corpus["module_prompt"]:
            prompt_sections.append("=== MODULE FOCUS ===")
            prompt_sections.append(existing_corpus["module_prompt"])
            prompt_sections.append("")
        
        if existing_corpus["system_corpus"]:
            prompt_sections.append("=== COURSE KNOWLEDGE BASE ===")
            prompt_sections.append(existing_corpus["system_corpus"])
            prompt_sections.append("")
        
        if existing_corpus["module_corpus"]:
            prompt_sections.append("=== MODULE RESOURCES ===")
            prompt_sections.append(existing_corpus["module_corpus"])
            prompt_sections.append("")
        
        if existing_corpus["dynamic_corpus"]:
            prompt_sections.append("=== CURRENT EXAMPLES & EVENTS ===")
            prompt_sections.append(existing_corpus["dynamic_corpus"])
            prompt_sections.append("")
        
        # Module Resources Section (new structured corpus)
        if module_memory["module_corpus"]:
            prompt_sections.append("=== ADDITIONAL MODULE RESOURCES ===")
            for corpus in module_memory["module_corpus"]:
                prompt_sections.append(f"[{corpus['type'].upper()}] {corpus['title']}")
                prompt_sections.append(corpus['content'])
                prompt_sections.append("")
        
        # Conversation Context Section
        conv_info = conversation_memory["conversation_info"]
        prompt_sections.append("=== CONVERSATION CONTEXT ===")
        prompt_sections.append(f"Conversation: {conv_info['title']}")
        if conv_info["current_grade"]:
            prompt_sections.append(f"Current Grade: {conv_info['current_grade']}")
        if conv_info["memory_summary"]:
            prompt_sections.append(f"Previous Discussion Summary: {conv_info['memory_summary']}")
        prompt_sections.append("")
        
        # Recent Messages Section
        if conversation_memory["chat_history"]:
            recent_messages = conversation_memory["chat_history"][-10:]  # Last 10 messages
            prompt_sections.append("=== RECENT CONVERSATION ===")
            for msg in recent_messages:
                role = "Student" if msg["role"] == "user" else "Harv"
                prompt_sections.append(f"{role}: {msg['content']}")
            prompt_sections.append("")
        
        # Student Progress Section
        progress_data = user_context["progress"]
        completed_modules = [p for p in progress_data if p["completed"]]
        if completed_modules:
            prompt_sections.append("=== STUDENT PROGRESS ===")
            prompt_sections.append(f"Completed Modules: {len(completed_modules)}")
            for prog in completed_modules:
                if prog["grade"]:
                    prompt_sections.append(f"Module {prog['module_id']}: Grade {prog['grade']}")
            prompt_sections.append("")
        
        # Socratic Instructions
        prompt_sections.append("=== SOCRATIC TUTORING INSTRUCTIONS ===")
        prompt_sections.append("You are Harv, a Socratic tutor. Your role is to:")
        prompt_sections.append("1. Guide students to discover insights through questions")
        prompt_sections.append("2. Never give direct answers - always ask thought-provoking questions")
        prompt_sections.append("3. Build on their previous knowledge and responses")
        prompt_sections.append("4. Encourage critical thinking about mass communication concepts")
        prompt_sections.append("5. Use the course and module context to create relevant examples")
        prompt_sections.append("6. Assess understanding and provide grades (A-F) when appropriate")
        prompt_sections.append("")
        
        # Current Message
        prompt_sections.append("=== CURRENT STUDENT MESSAGE ===")
        prompt_sections.append(user_message)
        prompt_sections.append("")
        prompt_sections.append("Respond as Harv with a thoughtful Socratic question or guidance:")
        
        return "\n".join(prompt_sections)
    
    def generate_memory_summary(self, messages: List[Dict]) -> str:
        """Generate a summary of recent conversation for memory"""
        if not messages:
            return ""
        
        user_messages = [msg for msg in messages if msg.get("role") == "user"]
        
        if not user_messages:
            return "No significant discussion points yet."
        
        # Simple summary generation
        total_exchanges = len(user_messages)
        recent_topics = []
        
        for msg in user_messages[-3:]:  # Last 3 user messages
            content = msg.get("content", "")
            if len(content) > 50:
                recent_topics.append(content[:100] + "...")
        
        summary = f"Discussion with {total_exchanges} student exchanges. "
        if recent_topics:
            summary += f"Recent topics: {'; '.join(recent_topics)}"
        
        return summary
