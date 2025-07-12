# REPLACE: backend/app/memory_context.py
# Enhanced Memory Context Assembler with 3-Layer System

from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from app.models import (
    User, Module, Conversation, OnboardingSurvey, 
    CourseCorpus, ModuleCorpusEntry, MemorySummary, UserProgress
)
import json
from datetime import datetime

class MemoryContextAssembler:
    """Assembles 3-layer memory context for personalized GPT prompts"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def assemble_full_context(
        self, 
        user: User, 
        module: Module, 
        conversation: Conversation
    ) -> Dict[str, Any]:
        """Assemble all 3 layers of memory context"""
        return {
            "system_memory": self._get_system_memory(user),
            "module_memory": self._get_module_memory(module),
            "conversation_memory": self._get_conversation_memory(conversation),
            "user_context": self._get_user_context(user)
        }
    
    def _get_system_memory(self, user: User) -> Dict[str, Any]:
        """Layer 1: System Memory (Cross-course learning profile)"""
        
        # Get onboarding survey (student profile)
        onboarding = self.db.query(OnboardingSurvey).filter(
            OnboardingSurvey.user_id == user.id
        ).first()
        
        # Get exported conversations from previous modules (finalized learning)
        exported_conversations = self.db.query(Conversation).filter(
            Conversation.user_id == user.id
        ).filter(
            Conversation.finalized == True if hasattr(Conversation, 'finalized') else False
        ).all()
        
        # Get memory summaries from completed modules
        memory_summaries = self.db.query(MemorySummary).filter(
            MemorySummary.user_id == user.id
        ).all()
        
        # Get course corpus (course-wide knowledge)
        course_corpus = self.db.query(CourseCorpus).order_by(CourseCorpus.order_index).all()
        
        return {
            "student_profile": {
                "name": user.name,
                "email": user.email,
                "learning_style": onboarding.learning_style if onboarding else "Mixed",
                "background": onboarding.background if onboarding else "General student",
                "reason": onboarding.reason if onboarding else "Learning mass communication",
                "familiarity": onboarding.familiarity if onboarding else "Beginner",
                "goals": onboarding.goals if onboarding else "Understanding course concepts"
            },
            "learning_journey": [
                {
                    "module": f"Module {summary.module_id}",
                    "concepts_mastered": summary.what_learned or "General concepts",
                    "effective_methods": summary.how_learned or "Socratic dialogue",
                    "key_insights": summary.key_concepts or "Course insights",
                    "completed_at": summary.created_at.isoformat() if summary.created_at else None
                }
                for summary in memory_summaries
            ],
            "exported_conversations": len(exported_conversations),
            "course_corpus": [
                {
                    "title": corpus.title,
                    "content": corpus.content,
                    "type": corpus.type
                }
                for corpus in course_corpus
            ]
        }
    
    def _get_module_memory(self, module: Module) -> Dict[str, Any]:
        """Layer 2: Module Memory (Current module configuration)"""
        
        # Get module-specific corpus entries
        module_corpus = self.db.query(ModuleCorpusEntry).filter(
            ModuleCorpusEntry.module_id == module.id
        ).order_by(ModuleCorpusEntry.order_index).all()
        
        return {
            "module_info": {
                "id": module.id,
                "title": module.title,
                "description": module.description,
                "learning_objectives": getattr(module, 'learning_objectives', None),
                "order": module.id
            },
            "socratic_configuration": {
                "system_prompt": getattr(module, 'system_prompt', None),
                "module_prompt": getattr(module, 'module_prompt', None),
                "teaching_approach": "Socratic questioning - guide discovery, never give direct answers"
            },
            "knowledge_base": {
                "system_corpus": getattr(module, 'system_corpus', None),
                "module_corpus": getattr(module, 'module_corpus', None),
                "dynamic_corpus": getattr(module, 'dynamic_corpus', None),
                "resources": module.resources
            },
            "module_corpus_entries": [
                {
                    "title": corpus.title,
                    "content": corpus.content,
                    "type": corpus.type,
                    "order": corpus.order_index
                }
                for corpus in module_corpus
            ],
            # Enhanced memory configuration
            "memory_config": self._get_module_memory_config(module)
        }
    
    def _get_module_memory_config(self, module: Module) -> Dict[str, Any]:
        """Get memory-specific configuration for this module"""
        return {
            "memory_extraction_prompt": getattr(module, 'memory_extraction_prompt', 
                "Analyze this conversation to extract: concepts mastered, learning breakthroughs, effective teaching methods"),
            "mastery_triggers": getattr(module, 'mastery_triggers', 
                "oh I see, that makes sense, so it means, I understand now, exactly, of course").split(','),
            "confusion_triggers": getattr(module, 'confusion_triggers',
                "I don't understand, this is confusing, what do you mean, I'm lost, huh?").split(','),
            "memory_context_template": getattr(module, 'memory_context_template',
                "Remember, this student previously mastered {concepts} and responds well to {teaching_methods}"),
            "cross_module_references": getattr(module, 'cross_module_references',
                "Remember when you discovered {concept} in Module {number}? How might that connect to what we're exploring now?"),
            "memory_weight": getattr(module, 'memory_weight', 'balanced'),
            "context_rules": {
                "include_system_memory": getattr(module, 'include_system_memory', True),
                "include_module_progress": getattr(module, 'include_module_progress', True),
                "include_learning_style": getattr(module, 'include_learning_style', True),
                "include_conversation_state": getattr(module, 'include_conversation_state', True),
                "include_recent_breakthroughs": getattr(module, 'include_recent_breakthroughs', True),
                "update_memory_on_response": getattr(module, 'update_memory_on_response', True),
                "track_understanding_level": getattr(module, 'track_understanding_level', True)
            }
        }
    
    def _get_conversation_memory(self, conversation: Conversation) -> Dict[str, Any]:
        """Layer 3: Conversation Memory (Real-time context)"""
        
        # Parse current conversation messages
        messages = []
        if conversation and conversation.messages_json:
            try:
                messages = json.loads(conversation.messages_json)
            except json.JSONDecodeError:
                messages = []
        
        # Get memory summaries for this specific conversation
        conversation_summaries = []
        if conversation and conversation.id:
            conversation_summaries = self.db.query(MemorySummary).filter(
                MemorySummary.conversation_id == conversation.id
            ).all()
        
        # Analyze current conversation state
        conversation_analysis = self._analyze_conversation_state(messages)
        
        return {
            "conversation_info": {
                "id": conversation.id if conversation else None,
                "title": conversation.title if conversation else "New Conversation",
                "current_grade": conversation.current_grade if conversation else None,
                "memory_summary": conversation.memory_summary if conversation else None,
                "finalized": getattr(conversation, 'finalized', False) if conversation else False,
                "message_count": len(messages),
                "created_at": conversation.created_at.isoformat() if conversation and conversation.created_at else None,
                "last_activity": conversation.updated_at.isoformat() if conversation and hasattr(conversation, 'updated_at') and conversation.updated_at else None
            },
            "chat_history": messages,
            "recent_messages": messages[-6:] if len(messages) > 6 else messages,  # Last 6 for context
            "conversation_analysis": conversation_analysis,
            "memory_summaries": [
                {
                    "what_learned": summary.what_learned,
                    "how_learned": summary.how_learned,
                    "key_concepts": summary.key_concepts,
                    "created_at": summary.created_at.isoformat() if summary.created_at else None
                }
                for summary in conversation_summaries
            ]
        }
    
    def _analyze_conversation_state(self, messages: List[Dict]) -> Dict[str, Any]:
        """Analyze current conversation for real-time insights"""
        
        if not messages:
            return {
                "state": "new_conversation",
                "engagement_level": "unknown",
                "understanding_indicators": [],
                "confusion_indicators": [],
                "message_count": 0,
                "last_user_message": None
            }
        
        # Get recent student messages
        user_messages = [msg for msg in messages if msg.get('role') == 'user']
        recent_user_text = " ".join([msg['content'].lower() for msg in user_messages[-3:]])
        
        # Detect understanding patterns
        understanding_phrases = ['i see', 'makes sense', 'understand', 'oh', 'so it means', 'exactly', 'of course', 'that clarifies']
        understanding_indicators = [phrase for phrase in understanding_phrases if phrase in recent_user_text]
        
        # Detect confusion patterns  
        confusion_phrases = ['don\'t understand', 'confusing', 'what do you mean', 'lost', 'huh?', 'unclear']
        confusion_indicators = [phrase for phrase in confusion_phrases if phrase in recent_user_text]
        
        # Determine engagement level
        if understanding_indicators:
            engagement_level = "high_understanding"
        elif confusion_indicators:
            engagement_level = "needs_support"
        elif len(user_messages) > 3:
            engagement_level = "actively_engaged"
        else:
            engagement_level = "getting_started"
        
        return {
            "state": engagement_level,
            "engagement_level": engagement_level,
            "understanding_indicators": understanding_indicators,
            "confusion_indicators": confusion_indicators,
            "message_count": len(messages),
            "user_message_count": len(user_messages),
            "last_user_message": user_messages[-1]['content'] if user_messages else None,
            "conversation_depth": len(messages) // 2,  # Rough measure of back-and-forth
            "patterns": {
                "asks_questions": sum(1 for msg in user_messages if '?' in msg['content']),
                "uses_examples": sum(1 for msg in user_messages if any(word in msg['content'].lower() for word in ['example', 'like', 'such as'])),
                "shows_enthusiasm": sum(1 for msg in user_messages if any(word in msg['content'].lower() for word in ['interesting', 'cool', 'wow', 'amazing']))
            }
        }
    
    def _get_user_context(self, user: User) -> Dict[str, Any]:
        """Layer 4: User Context (Overall learning progress)"""
        
        # Get user progress across all modules
        progress = self.db.query(UserProgress).filter(
            UserProgress.user_id == user.id
        ).all()
        
        # Get all conversations for learning pattern analysis
        conversations = self.db.query(Conversation).filter(
            Conversation.user_id == user.id
        ).all()
        
        # Calculate overall progress
        completed_modules = [p for p in progress if p.completed]
        
        return {
            "user_info": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "created_at": user.created_at.isoformat() if hasattr(user, 'created_at') and user.created_at else None
            },
            "overall_progress": {
                "completed_modules": len(completed_modules),
                "total_modules": 15,  # Course has 15 modules
                "completion_rate": round((len(completed_modules) / 15) * 100, 1),
                "average_grade": self._calculate_average_grade(completed_modules)
            },
            "progress_details": [
                {
                    "module_id": prog.module_id,
                    "completed": prog.completed,
                    "grade": prog.grade,
                    "completion_date": prog.completion_date.isoformat() if prog.completion_date else None,
                    "time_spent": getattr(prog, 'time_spent', 0),
                    "attempts": getattr(prog, 'attempts', 0)
                }
                for prog in progress
            ],
            "conversation_history": [
                {
                    "id": conv.id,
                    "module_id": conv.module_id,
                    "title": conv.title,
                    "current_grade": conv.current_grade,
                    "finalized": getattr(conv, 'finalized', False),
                    "message_count": len(json.loads(conv.messages_json)) if conv.messages_json else 0,
                    "created_at": conv.created_at.isoformat() if conv.created_at else None
                }
                for conv in conversations
            ],
            "learning_patterns": self._analyze_learning_patterns(conversations)
        }
    
    def _calculate_average_grade(self, completed_modules: List) -> Optional[str]:
        """Calculate average grade from completed modules"""
        grades_with_values = []
        grade_map = {'A': 4, 'B': 3, 'C': 2, 'D': 1, 'F': 0}
        
        for module in completed_modules:
            if module.grade and module.grade in grade_map:
                grades_with_values.append(grade_map[module.grade])
        
        if not grades_with_values:
            return None
        
        avg_value = sum(grades_with_values) / len(grades_with_values)
        reverse_map = {4: 'A', 3: 'B', 2: 'C', 1: 'D', 0: 'F'}
        return reverse_map.get(round(avg_value), 'C')
    
    def _analyze_learning_patterns(self, conversations: List[Conversation]) -> Dict[str, Any]:
        """Analyze learning patterns across all conversations"""
        
        total_messages = 0
        total_conversations = len(conversations)
        finalized_conversations = 0
        
        for conv in conversations:
            if conv.messages_json:
                messages = json.loads(conv.messages_json)
                total_messages += len(messages)
            
            if hasattr(conv, 'finalized') and conv.finalized:
                finalized_conversations += 1
        
        return {
            "total_conversations": total_conversations,
            "finalized_conversations": finalized_conversations,
            "total_messages": total_messages,
            "avg_messages_per_conversation": round(total_messages / max(total_conversations, 1), 1),
            "completion_rate": round((finalized_conversations / max(total_conversations, 1)) * 100, 1) if total_conversations > 0 else 0,
            "engagement_level": "high" if total_messages > 50 else "moderate" if total_messages > 20 else "getting_started"
        }
    
    def build_gpt_prompt(self, context: Dict[str, Any], user_message: str, module_config: Optional[Dict] = None) -> str:
        """Build comprehensive GPT prompt with full memory context"""
        
        system_memory = context["system_memory"]
        module_memory = context["module_memory"]
        conversation_memory = context["conversation_memory"]
        user_context = context["user_context"]
        
        # Build context sections
        prompt_sections = []
        
        # Memory-aware Socratic instructions (always first)
        prompt_sections.append("=== SOCRATIC TUTORING WITH MEMORY ===")
        prompt_sections.append("You are Harv, an AI tutor who uses Socratic questioning to guide discovery.")
        prompt_sections.append("NEVER give direct answers. Always respond with thoughtful questions that build on this student's learning journey.")
        prompt_sections.append("")
        
        # Student Profile Section (System Memory)
        if system_memory["student_profile"]:
            profile = system_memory["student_profile"]
            prompt_sections.append("=== STUDENT PROFILE ===")
            prompt_sections.append(f"Student: {profile['name']}")
            prompt_sections.append(f"Learning Style: {profile['learning_style']}")
            prompt_sections.append(f"Background: {profile['background']}")
            prompt_sections.append(f"Course Motivation: {profile['reason']}")
            prompt_sections.append(f"Familiarity Level: {profile['familiarity']}")
            prompt_sections.append("")
        
        # Learning Journey (System Memory - Previous Modules)
        if system_memory["learning_journey"]:
            prompt_sections.append("=== STUDENT'S LEARNING JOURNEY ===")
            for journey in system_memory["learning_journey"]:
                prompt_sections.append(f"✅ {journey['module']}: {journey['concepts_mastered']}")
                if journey['key_insights']:
                    prompt_sections.append(f"   Key insight: {journey['key_insights']}")
            prompt_sections.append("")
        
        # Current Module Context (Module Memory)
        module_info = module_memory["module_info"]
        prompt_sections.append("=== CURRENT MODULE ===")
        prompt_sections.append(f"Module: {module_info['title']}")
        if module_info["description"]:
            prompt_sections.append(f"Focus: {module_info['description']}")
        if module_info["learning_objectives"]:
            prompt_sections.append(f"Objectives: {module_info['learning_objectives']}")
        prompt_sections.append("")
        
        # Socratic Configuration (Module Memory)
        socratic_config = module_memory["socratic_configuration"]
        if socratic_config["system_prompt"]:
            prompt_sections.append("=== SOCRATIC APPROACH ===")
            prompt_sections.append(socratic_config["system_prompt"])
            prompt_sections.append("")
        
        if socratic_config["module_prompt"]:
            prompt_sections.append("=== MODULE FOCUS ===")
            prompt_sections.append(socratic_config["module_prompt"])
            prompt_sections.append("")
        
        # Knowledge Base (Module Memory)
        knowledge = module_memory["knowledge_base"]
        if knowledge["system_corpus"]:
            prompt_sections.append("=== COURSE KNOWLEDGE ===")
            prompt_sections.append(knowledge["system_corpus"])
            prompt_sections.append("")
        
        if knowledge["module_corpus"]:
            prompt_sections.append("=== MODULE CONTENT ===")
            prompt_sections.append(knowledge["module_corpus"])
            prompt_sections.append("")
        
        if knowledge["dynamic_corpus"]:
            prompt_sections.append("=== CURRENT EXAMPLES ===")
            prompt_sections.append(knowledge["dynamic_corpus"])
            prompt_sections.append("")
        
        # Conversation Context (Conversation Memory)
        conv_info = conversation_memory["conversation_info"]
        conv_analysis = conversation_memory["conversation_analysis"]
        
        if conv_analysis["state"] != "new_conversation":
            prompt_sections.append("=== CONVERSATION CONTEXT ===")
            prompt_sections.append(f"Current State: {conv_analysis['engagement_level']}")
            
            if conv_analysis["understanding_indicators"]:
                prompt_sections.append(f"Student shows understanding: {', '.join(conv_analysis['understanding_indicators'])}")
            
            if conv_analysis["confusion_indicators"]:
                prompt_sections.append(f"Student shows confusion: {', '.join(conv_analysis['confusion_indicators'])}")
            
            prompt_sections.append(f"Conversation depth: {conv_analysis['conversation_depth']} exchanges")
            prompt_sections.append("")
        
        # Recent Messages (Conversation Memory)
        if conversation_memory["recent_messages"]:
            prompt_sections.append("=== RECENT CONVERSATION ===")
            for msg in conversation_memory["recent_messages"]:
                role = "Student" if msg["role"] == "user" else "Harv"
                prompt_sections.append(f"{role}: {msg['content']}")
            prompt_sections.append("")
        
        # Memory-Enhanced Instructions
        prompt_sections.append("=== MEMORY-ENHANCED TUTORING GUIDELINES ===")
        
        # Learning style adaptation
        learning_style = system_memory["student_profile"]["learning_style"].lower()
        if "visual" in learning_style:
            prompt_sections.append("• Use visual language: 'imagine', 'picture this', 'what do you see'")
        elif "kinesthetic" in learning_style:
            prompt_sections.append("• Use action language: 'if you were to...', 'what would you do', hands-on scenarios")
        elif "auditory" in learning_style:
            prompt_sections.append("• Use discussion language: 'tell me about', 'how would you explain', dialogue-focused")
        
        # Previous learning connections
        if system_memory["learning_journey"]:
            prompt_sections.append("• Build on previous learning: Reference concepts they've already mastered")
            prompt_sections.append("• Make connections: Show how this module relates to their previous insights")
        
        # Conversation state adaptation
        if conv_analysis["understanding_indicators"]:
            prompt_sections.append("• Student is understanding well - ready for deeper questions")
        elif conv_analysis["confusion_indicators"]:
            prompt_sections.append("• Student needs support - simplify and use more examples")
        
        prompt_sections.append("")
        
        # Current Student Message
        prompt_sections.append("=== CURRENT STUDENT MESSAGE ===")
        prompt_sections.append(f'Student: "{user_message}"')
        prompt_sections.append("")
        
        # Final Instructions
        prompt_sections.append("=== RESPONSE INSTRUCTIONS ===")
        prompt_sections.append("Respond with a Socratic question that:")
        prompt_sections.append("1. Builds on their learning journey and profile")
        prompt_sections.append("2. Adapts to their current understanding level")
        prompt_sections.append("3. Guides discovery rather than giving answers")
        prompt_sections.append("4. Connects to their previous insights when relevant")
        prompt_sections.append("5. Uses their preferred learning style")
        
        return "\n".join(prompt_sections)
    
    def generate_memory_summary(self, messages: List[Dict]) -> str:
        """Generate a summary of conversation for memory storage"""
        if not messages:
            return "No conversation to summarize."
        
        user_messages = [msg for msg in messages if msg.get("role") == "user"]
        
        if not user_messages:
            return "No student responses to analyze."
        
        total_exchanges = len(user_messages)
        recent_topics = []
        
        # Extract key topics from recent user messages
        for msg in user_messages[-3:]:
            content = msg.get("content", "")
            if len(content) > 50:
                # Extract first 50 characters as topic indicator
                topic = content[:50].strip()
                if not topic.endswith('.'):
                    topic += "..."
                recent_topics.append(topic)
        
        summary = f"Conversation with {total_exchanges} student exchanges. "
        if recent_topics:
            summary += f"Recent focus: {'; '.join(recent_topics)}"
        else:
            summary += "General discussion on module concepts."
        
        return summary
