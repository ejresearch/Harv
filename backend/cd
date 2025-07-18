from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Demo modules data
DEMO_MODULES = [
    {"id": 1, "title": "Introduction to Communication Theory", "description": "Basic communication concepts"},
    {"id": 2, "title": "Interpersonal Communication", "description": "One-on-one communication skills"},
    {"id": 3, "title": "Public Speaking", "description": "Presentation and speaking skills"},
    {"id": 4, "title": "Nonverbal Communication", "description": "Body language and visual cues"},
    {"id": 5, "title": "Digital Communication", "description": "Online and digital messaging"}
]

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/modules")
def get_modules():
    return DEMO_MODULES

@app.get("/modules/{module_id}/config")
def get_module_config(module_id: int):
    return {
        "system_prompt": "Use Socratic questioning to guide student discovery...",
        "module_prompt": f"Focus on Module {module_id} concepts through strategic questions...",
        "system_corpus": "Remember key insights and track learning progression",
        "module_corpus": "Core concepts and learning objectives for this module"
    }

@app.put("/modules/{module_id}/config")
def update_module_config(module_id: int, config: dict):
    return {"success": True, "message": "Configuration updated"}

@app.post("/chat/")
def chat_endpoint(message_data: dict):
    message = message_data.get("message", "")
    return {
        "reply": f"That's an interesting question about '{message}'. What do you think might be the key factors to consider here?",
        "conversation_id": "demo-conversation-123"
    }

@app.get("/memory/{user_id}/{module_id}")
def get_memory(user_id: int, module_id: int):
    return {
        "memory_layers": {
            "system": {"user_profile": {"learning_style": "visual", "pace": "moderate"}},
            "module": {"module_info": {"title": f"Module {module_id}"}},
            "conversation": {"state": "active", "recent_conversations": 3},
            "prior": {"total_conversations": 12, "learning_trajectory": "progressive"}
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Simple Harv Backend...")
    print("✅ Demo mode with mock data")
    print("🌐 Server: http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
