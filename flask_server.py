#!/usr/bin/env python3
"""
Simple Flask Backend for Harv Platform
Run from backend directory: python flask_server.py
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os

def create_app():
    """Create and configure the Flask application"""
    
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
        """Health check endpoint"""
        return {"status": "healthy"}
    
    @app.route('/modules')
    def get_modules():
        """Get all available modules"""
        return jsonify(DEMO_MODULES)
    
    @app.route('/modules/<int:module_id>/config', methods=['GET'])
    def get_module_config(module_id):
        """Get configuration for specific module"""
        return jsonify({
            "system_prompt": "Use Socratic questioning to guide student discovery...",
            "module_prompt": f"Focus on Module {module_id} concepts through strategic questions...",
            "system_corpus": "Remember key insights and track learning progression",
            "module_corpus": "Core concepts and learning objectives for this module"
        })
    
    @app.route('/modules/<int:module_id>/config', methods=['PUT'])
    def update_module_config(module_id):
        """Update configuration for specific module"""
        config = request.get_json()
        print(f"✅ Updating Module {module_id} config:", config)
        return jsonify({"success": True, "message": "Configuration updated"})
    
    @app.route('/chat/', methods=['POST'])
    def chat_endpoint():
        """Handle chat messages"""
        data = request.get_json()
        message = data.get("message", "")
        module_id = data.get("module_id", 1)
        
        print(f"💬 Chat message: {message} (Module {module_id})")
        
        return jsonify({
            "reply": f"That's an interesting question about '{message}'. What do you think might be the key factors to consider here?",
            "conversation_id": "demo-conversation-123"
        })
    
    @app.route('/memory/<int:user_id>/<int:module_id>')
    def get_memory(user_id, module_id):
        """Get memory layers for user and module"""
        return jsonify({
            "memory_layers": {
                "system": {"user_profile": {"learning_style": "visual", "pace": "moderate"}},
                "module": {"module_info": {"title": f"Module {module_id}"}},
                "conversation": {"state": "active", "recent_conversations": 3},
                "prior": {"total_conversations": 12, "learning_trajectory": "progressive"}
            }
        })
    
    return app

def main():
    """Main function to run the Flask server"""
    print("🔧 Starting Harv Flask Backend...")
    
    # Check if we're in the right directory
    if not os.path.exists('app'):
        print("⚠️  Warning: 'app' directory not found. You might be in the wrong directory.")
    
    app = create_app()
    
    print("✅ Flask server configured")
    print("🧠 Demo mode with mock data active")
    print("🌐 Starting server on http://127.0.0.1:8000")
    print("🔗 API endpoints available:")
    print("   - /health")
    print("   - /modules") 
    print("   - /modules/{id}/config")
    print("   - /chat/")
    print("   - /memory/{user_id}/{module_id}")
    
    try:
        app.run(host="127.0.0.1", port=8000, debug=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    main()
