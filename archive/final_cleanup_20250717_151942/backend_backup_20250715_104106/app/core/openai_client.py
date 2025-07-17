import openai
import os
import logging
from typing import Optional
from app.models import User, Module, Conversation

logger = logging.getLogger(__name__)

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

async def get_openai_response(
    message: str, 
    module: Module, 
    conversation: Conversation, 
    user: User
) -> str:
    """Get response from OpenAI with fallback handling"""
    
    # Check if API key is configured
    if not openai.api_key or openai.api_key.startswith("sk-proj-fake"):
        logger.info("Using fallback response - no valid OpenAI key")
        return get_fallback_response(message, module)
    
    try:
        # Build context from module and conversation
        system_prompt = module.system_prompt or f"You are a Socratic tutor for {module.title}. Guide students through discovery-based learning by asking thought-provoking questions rather than giving direct answers."
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
        
        # Call OpenAI API
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except openai.error.AuthenticationError:
        logger.error("OpenAI authentication failed - using fallback")
        return get_fallback_response(message, module)
        
    except openai.error.RateLimitError:
        logger.warning("OpenAI rate limit exceeded - using fallback")
        return get_fallback_response(message, module)
        
    except Exception as e:
        logger.error(f"OpenAI API error: {e} - using fallback")
        return get_fallback_response(message, module)

def get_fallback_response(message: str, module: Module) -> str:
    """Generate fallback response when OpenAI is unavailable"""
    
    # Socratic fallback responses based on module
    fallback_responses = {
        "introduction": [
            "That's an interesting point about {topic}. What do you think are the key elements that make communication 'mass' communication?",
            "You've raised a good question. How do you think {topic} relates to the broader field of mass communication?",
            "Let's explore that further. What examples from your daily life demonstrate the concept you're asking about?"
        ],
        "history": [
            "Excellent question about {topic}. How do you think this development changed the way people received information?",
            "That's a thoughtful inquiry. What factors do you think contributed to this historical change?",
            "Good observation. How might this historical development compare to changes we see in media today?"
        ],
        "theory": [
            "That's a complex theoretical question about {topic}. What evidence might support or challenge this theory?",
            "Interesting perspective. How do you think this theory applies to modern media situations?",
            "Good point to consider. What are the assumptions underlying this theoretical approach?"
        ]
    }
    
    # Simple keyword matching for module type
    module_type = "introduction"
    if "history" in module.title.lower():
        module_type = "history"
    elif "theory" in module.title.lower():
        module_type = "theory"
    
    import random
    response_template = random.choice(fallback_responses[module_type])
    
    # Extract key topic from message
    topic = message[:50] + "..." if len(message) > 50 else message
    
    return response_template.format(topic=topic)
