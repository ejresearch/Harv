# Step 2: Enhanced Memory System
# Save as: backend/app/memory_context_enhanced.py

from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from app.models import User, Module, Conversation, OnboardingSurvey
import json
from datetime import datetime

class DynamicMemoryAssembler:
    """Enhanced Memory System with Dynamic Data Injection"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def assemble_dynamic_context(
        self, 
        user_id: int, 
        module_id: int, 
        current_message: str = "",
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Main entry point - assembles optimized, dynamic memory context"""
        
        print(f"🧠 Assembling dynamic memory context for user {user_id}, module {module_id}")
        
        # Get core entities
        user = self.db.query(User).filter(User.id == user_id).first()
        module = self.db.query(Module).filter(Module.id == module_id).first()
        
        if not user or not module:
            return self._create_fallback_context(user_id, module_id)
        
        # Dynamic data injection from database
        system_data = self._inject_system_data(user)
        module_data = self._inject_module_data(module)
        conversation_data = self._inject_conversation_data(user_id, module_id, conversation_id)
        prior_knowledge = self._inject_prior_knowledge(user_id, module_id)
        
        # Dynamic prompt assembly
        assembled_prompt = self._assemble_optimized_prompt(
            system_data, module_data, conversation_data, prior_knowledge, current_message
        )
        
        # Calculate context metrics
        context_metrics = self._calculate_context_metrics(assembled_prompt)
        
        print(f"📚 Dynamic context assembled: {context_metrics['total_chars']} chars")
        
        return {
            'assembled_prompt': assembled_prompt,
            'context_metrics': context_metrics,
            'memory_layers': {
                'system_data': system_data,
                'module_data': module_data, 
                'conversation_data': conversation_data,
                'prior_knowledge': prior_knowledge
            },
            'conversation_id': conversation_id,
            'database_status': {
                'onboarding': bool(system_data.get('learning_profile')),
                'module_config': bool(module_data.get('teaching_configuration')),
                'conversation_analysis': bool(conversation_data.get('state')),
                'cross_module': bool(prior_knowledge.get('prior_module_insights'))
            }
        }
    
    def _inject_system_data(self, user: User) -> Dict[str, Any]:
        """Dynamic System Data Injection - Cross-course learning profile"""
        
        # Get onboarding survey
        onboarding = self.db.query(OnboardingSurvey).filter(
            OnboardingSurvey.user_id == user.id
        ).first()
        
        # Get completed conversations for cross-module insights
        completed_conversations = self.db.query(Conversation).filter(
            Conversation.user_id == user.id
        ).all()
        
        return {
            'learning_profile': {
                'style': getattr(onboarding, 'learning_style', 'adaptive') if onboarding else 'adaptive',
                'pace': getattr(onboarding, 'preferred_pace', 'moderate') if onboarding else 'moderate',
                'background': getattr(onboarding, 'background_knowledge', 'beginner') if onboarding else 'beginner'
            },
            'cross_module_mastery': [
                {
                    'module_id': conv.module_id,
                    'last_activity': conv.updated_at.isoformat() if conv.updated_at else None,
                    'message_count': len(json.loads(conv.messages_json)) if conv.messages_json else 0
                }
                for conv in completed_conversations[-5:]  # Last 5 conversations
            ]
        }
    
    def _inject_module_data(self, module: Module) -> Dict[str, Any]:
        """Dynamic Module Data Injection - Subject-specific context"""
        
        # Get module configuration (from your GUI)
        module_config = {
            'system_prompt': getattr(module, 'system_prompt', ''),
            'module_prompt': getattr(module, 'module_prompt', ''),
            'system_corpus': getattr(module, 'system_corpus', ''),
            'module_corpus': getattr(module, 'module_corpus', ''),
            'dynamic_corpus': getattr(module, 'dynamic_corpus', '')
        }
        
        return {
            'module_info': {
                'id': module.id,
                'title': module.title,
                'description': module.description
            },
            'teaching_configuration': module_config,
            'socratic_strategy': self._generate_socratic_strategy(module_config)
        }
    
    def _inject_conversation_data(self, user_id: int, module_id: int, conversation_id: Optional[str]) -> Dict[str, Any]:
        """Dynamic Conversation Data Injection - Real-time dialogue context"""
        
        # Get current conversation
        conversation = None
        if conversation_id:
            conversation = self.db.query(Conversation).filter(
                and_(
                    Conversation.id == conversation_id,
                    Conversation.user_id == user_id,
                    Conversation.module_id == module_id
                )
            ).first()
        
        if not conversation or not conversation.messages_json:
            return {
                'state': 'new_conversation',
                'message_history': [],
                'dialogue_context': 'Ready to begin Socratic exploration.'
            }
        
        # Parse conversation messages
        try:
            messages = json.loads(conversation.messages_json)
        except (json.JSONDecodeError, TypeError):
            messages = []
        
        return {
            'state': 'active_conversation',
            'message_history': messages[-10:],  # Last 10 messages
            'dialogue_context': self._extract_dialogue_context(messages),
            'conversation_analysis': self._analyze_conversation_patterns(messages)
        }
    
    def _inject_prior_knowledge(self, user_id: int, current_module_id: int) -> Dict[str, Any]:
        """Dynamic Prior Knowledge Injection - 1 per module conversation memory"""
        
        # Get most recent conversation from each other module
        other_modules_conversations = self.db.query(Conversation).filter(
            and_(
                Conversation.user_id == user_id,
                Conversation.module_id != current_module_id,
                Conversation.messages_json.isnot(None)
            )
        ).order_by(desc(Conversation.updated_at)).all()
        
        # Group by module_id and take most recent per module
        module_insights = {}
        for conv in other_modules_conversations:
            if conv.module_id not in module_insights:
                module = self.db.query(Module).filter(Module.id == conv.module_id).first()
                if module:
                    module_insights[conv.module_id] = {
                        'module_title': module.title,
                        'key_insight': f"Previous experience with {module.title}",
                        'message_count': len(json.loads(conv.messages_json)) if conv.messages_json else 0,
                        'last_activity': conv.updated_at.isoformat() if conv.updated_at else None
                    }
        
        return {
            'prior_module_insights': list(module_insights.values())[:3],  # Top 3 most recent
            'mastered_concepts': ['Communication fundamentals', 'Socratic questioning', 'Critical thinking']
        }
    
    def _assemble_optimized_prompt(
        self, 
        system_data: Dict, 
        module_data: Dict, 
        conversation_data: Dict, 
        prior_knowledge: Dict,
        current_message: str
    ) -> str:
        """Dynamic Prompt Assembly - Intelligently combines all memory layers"""
        
        prompt_sections = []
        
        # === DYNAMIC SYSTEM CONTEXT ===
        prompt_sections.append("=== HARV DYNAMIC MEMORY CONTEXT ===")
        
        # Learning Profile Injection
        learning_profile = system_data['learning_profile']
        prompt_sections.append(f"STUDENT PROFILE: {learning_profile['style']} learner, {learning_profile['pace']} pace, {learning_profile['background']} background")
        
        # Cross-module experience
        if system_data['cross_module_mastery']:
            mastery_count = len(system_data['cross_module_mastery'])
            prompt_sections.append(f"PRIOR EXPERIENCE: {mastery_count} previous module interactions")
        
        # === DYNAMIC MODULE CONTEXT ===
        module_info = module_data['module_info']
        teaching_config = module_data['teaching_configuration']
        
        prompt_sections.append(f"\nMODULE CONTEXT: {module_info['title']} - {module_info['description']}")
        
        # Inject your GUI configuration
        if teaching_config['system_prompt']:
            prompt_sections.append(f"TEACHING APPROACH: {teaching_config['system_prompt']}")
        
        if teaching_config['module_prompt']:
            prompt_sections.append(f"MODULE STRATEGY: {teaching_config['module_prompt']}")
        
        # === DYNAMIC CONVERSATION CONTEXT ===
        prompt_sections.append(f"\nCONVERSATION STATE: {conversation_data['state']}")
        prompt_sections.append(f"DIALOGUE CONTEXT: {conversation_data['dialogue_context']}")
        
        # === DYNAMIC PRIOR KNOWLEDGE ===
        if prior_knowledge['prior_module_insights']:
            for insight in prior_knowledge['prior_module_insights'][:2]:
                prompt_sections.append(f"PRIOR LEARNING: {insight['module_title']} - {insight['key_insight']}")
        
        # === SOCRATIC STRATEGY ===
        prompt_sections.append(f"\nSOCRATIC APPROACH: {module_data['socratic_strategy']}")
        
        # === CURRENT MESSAGE ===
        if current_message:
            prompt_sections.append(f"\nSTUDENT MESSAGE: {current_message}")
            approach = self._analyze_current_message(current_message)
            prompt_sections.append(f"RESPONSE STRATEGY: {approach}")
        
        prompt_sections.append("\nRemember: Use Socratic questioning to guide discovery. Never give direct answers.")
        
        return "\n".join(prompt_sections)
    
    def _generate_socratic_strategy(self, module_config: Dict[str, str]) -> str:
        """Generate dynamic Socratic teaching strategy"""
        strategies = ["Use strategic questions to guide discovery"]
        
        if 'example' in module_config.get('module_prompt', '').lower():
            strategies.append("encourage concrete examples")
        if 'theory' in module_config.get('module_prompt', '').lower():
            strategies.append("build theoretical understanding step-by-step")
        
        return " | ".join(strategies)
    
    def _extract_dialogue_context(self, messages: List[Dict]) -> str:
        """Extract recent dialogue context"""
        if not messages:
            return "Ready to begin Socratic exploration"
        
        recent = messages[-3:] if len(messages) >= 3 else messages
        context_parts = []
        for msg in recent:
            role = "Student" if msg.get('role') == 'user' else "Harv"
            content = msg.get('content', '')[:50]
            context_parts.append(f"{role}: {content}")
        
        return " | ".join(context_parts)
    
    def _analyze_conversation_patterns(self, messages: List[Dict]) -> Dict[str, Any]:
        """Analyze conversation for engagement patterns"""
        user_messages = [m for m in messages if m.get('role') == 'user']
        
        if not user_messages:
            return {'engagement_level': 'starting', 'understanding_indicators': []}
        
        recent_text = ' '.join([m.get('content', '').lower() for m in user_messages[-3:]])
        
        engagement_level = 'building_understanding'
        if 'interesting' in recent_text or 'tell me more' in recent_text:
            engagement_level = 'highly_engaged'
        elif 'confused' in recent_text or "don't understand" in recent_text:
            engagement_level = 'needs_support'
        
        return {
            'engagement_level': engagement_level,
            'understanding_indicators': ['making connections'] if 'understand' in recent_text else []
        }
    
    def _analyze_current_message(self, message: str) -> str:
        """Analyze current message for response strategy"""
        message_lower = message.lower()
        
        if '?' in message:
            if 'why' in message_lower:
                return "Explore underlying reasoning with follow-up questions"
            elif 'how' in message_lower:
                return "Break down process step-by-step through inquiry"
            else:
                return "Respond to question with clarifying questions"
        elif any(word in message_lower for word in ['confused', 'unclear', "don't understand"]):
            return "Use simpler questions and concrete examples"
        elif 'example' in message_lower:
            return "Ask student to generate their own examples first"
        else:
            return "Use Socratic questioning to deepen exploration"
    
    def _calculate_context_metrics(self, assembled_prompt: str) -> Dict[str, Any]:
        """Calculate metrics about assembled context"""
        return {
            'total_chars': len(assembled_prompt),
            'system_weight': 25,
            'module_weight': 35,
            'conversation_weight': 25,
            'prior_weight': 15,
            'optimization_score': min(100, len(assembled_prompt) / 50)
        }
    
    def _create_fallback_context(self, user_id: int, module_id: int) -> Dict[str, Any]:
        """Fallback context if user/module not found"""
        return {
            'assembled_prompt': f"=== HARV FALLBACK CONTEXT ===\nUser: {user_id}, Module: {module_id}\nUse Socratic questioning to guide learning.",
            'context_metrics': {'total_chars': 100, 'optimization_score': 50},
            'memory_layers': {
                'system_data': {'learning_profile': {'style': 'adaptive'}},
                'module_data': {'module_info': {'title': f'Module {module_id}'}},
                'conversation_data': {'state': 'new_conversation'},
                'prior_knowledge': {'prior_module_insights': []}
            },
            'database_status': {'onboarding': False, 'module_config': False, 'conversation_analysis': False, 'cross_module': False}
        }
