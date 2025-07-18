from flask import Flask, jsonify, request
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Demo modules data
DEMO_MODULES = [
    {"id": 1, "title": "Introduction to Communication Theory", "description": "Basic communication concepts"},
    {"id": 2, "title": "Interpersonal Communication", "description": "One-on-one communication skills"},
    {"id": 3, "title": "Public Speaking", "description": "Presentation and speaking skills"},
    {"id": 4, "title": "Nonverbal Communication", "description": "Body language and visual cues"},
    {"id": 5, "title": "Digital Communication", "description": "Online and digital messaging"}
]

@app.route('/health')
def health_check():
    return {"status": "healthy"}

@app.route('/modules')
def get_modules():
    return jsonify(DEMO_MODULES)

@app.route('/modules/<int:module_id>/config', methods=['GET'])
def get_module_config(module_id):
    return jsonify({
        "system_prompt": "Use Socratic questioning to guide student discovery...",
        "module_prompt": f"Focus on Module {module_id} concepts through strategic questions...",
        "system_corpus": "Remember key insights and track learning progression",
        "module_corpus": "Core concepts and learning objectives for this module"
    })

@app.route('/modules/<int:module_id>/config', methods=['PUT'])
def update_module_config(module_id):
    config = request.get_json()
    print(f"Updating Module {module_id} config:", config)
    return jsonify({"success": True, "message": "Configuration updated"})

@app.route('/chat/', methods=['POST'])
def chat_endpoint():
    data = request.get_json()
    message = data.get("message", "")
    print(f"Chat message: {message}")
    return jsonify({
        "reply": f"That's an interesting question about '{message}'. What do you think might be the key factors to consider here?",
        "conversation_id": "demo-conversation-123"
    })

@app.route('/memory/<int:user_id>/<int:module_id>')
def get_memory(user_id, module_id):
    return jsonify({
        "memory_layers": {
            "system": {"user_profile": {"learning_style": "visual", "pace": "moderate"}},
            "module": {"module_info": {"title": f"Module {module_id}"}},
            "conversation": {"state": "active", "recent_conversations": 3},
            "prior": {"total_conversations": 12, "learning_trajectory": "progressive"}
        }
    })

if __name__ == "__main__":
    print("🚀 Starting Simple Harv Backend (Flask)...")
    print("✅ Demo mode with mock data")
    print("🌐 Server: http://127.0.0.1:8000")
    app.run(host="127.0.0.1", port=8000, debug=True)
