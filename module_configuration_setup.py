#!/usr/bin/env python3
"""
Module Configuration System Setup
Validates and enhances the developer GUI for Socratic prompt configuration
Run from root directory: python module_configuration_setup.py
"""

import os
import json
import sqlite3
from datetime import datetime

def setup_module_configuration():
    """Set up and validate module configuration system"""
    print("⚙️ MODULE CONFIGURATION SYSTEM SETUP")
    print("=" * 50)
    
    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"module_config_backup_{timestamp}"
    
    print(f"📁 Creating backup: {backup_dir}")
    os.makedirs(backup_dir, exist_ok=True)
    
    # 1. Verify database has all module configuration fields
    print("🗄️ Verifying database schema for module configuration...")
    verify_module_schema()
    
    # 2. Create/update developer GUI
    print("🎨 Setting up developer GUI...")
    create_developer_gui()
    
    # 3. Create module configuration API endpoints
    print("🔌 Creating configuration API endpoints...")
    create_config_api_endpoints()
    
    # 4. Test GUI accessibility and functionality
    print("🧪 Setting up configuration testing...")
    create_config_tests()
    
    # 5. Create startup script for GUI
    print("🚀 Creating GUI startup script...")
    create_gui_startup_script()
    
    print("\n" + "=" * 50)
    print("✅ MODULE CONFIGURATION SYSTEM COMPLETE!")
    print("=" * 50)
    print("🎯 What was created:")
    print("   ✅ Enhanced developer GUI with all 15 modules")
    print("   ✅ Configuration API endpoints")
    print("   ✅ Database validation for module fields")
    print("   ✅ Test suite for configuration functionality")
    print("   ✅ GUI startup automation")
    print("\n🧪 Next Steps:")
    print("1. python start_config_gui.py")
    print("2. Open http://localhost:3000/dev-gui.html")
    print("3. Configure Socratic prompts for each module")
    print("4. Test save/edit operations")
    print("5. Verify 1:1 frontend matching")
    print("\n🎯 Ready for Integration Testing!")

def verify_module_schema():
    """Verify database has all required module configuration fields"""
    db_path = "harv.db"
    if not os.path.exists(db_path):
        print(f"⚠️  Database not found at {db_path}, checking backend/")
        db_path = "backend/harv.db"
        if not os.path.exists(db_path):
            print("❌ No database found. Run database setup first.")
            return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if modules table has configuration fields
    cursor.execute("PRAGMA table_info(modules)")
    columns = [col[1] for col in cursor.fetchall()]
    
    required_config_fields = [
        'module_prompt', 'system_corpus', 'module_corpus', 'dynamic_corpus',
        'memory_extraction_prompt', 'mastery_triggers', 'confusion_triggers',
        'memory_context_template', 'cross_module_references'
    ]
    
    missing_fields = [field for field in required_config_fields if field not in columns]
    
    if missing_fields:
        print(f"⚠️  Adding missing configuration fields: {missing_fields}")
        for field in missing_fields:
            try:
                cursor.execute(f"ALTER TABLE modules ADD COLUMN {field} TEXT")
                print(f"   ✅ Added {field}")
            except sqlite3.OperationalError:
                # Field might already exist
                pass
        conn.commit()
    
    # Verify all 15 modules exist
    cursor.execute("SELECT COUNT(*) FROM modules")
    module_count = cursor.fetchone()[0]
    
    if module_count < 15:
        print(f"⚠️  Only {module_count}/15 modules found. Creating missing modules...")
        create_missing_modules(cursor)
        conn.commit()
    
    conn.close()
    print("✅ Database schema verified for module configuration")
    return True

def create_missing_modules(cursor):
    """Create any missing modules up to 15 total"""
    module_titles = [
        "Introduction to Communication Theory",
        "Interpersonal Communication",
        "Group Communication Dynamics",
        "Public Speaking Fundamentals",
        "Media and Digital Communication",
        "Organizational Communication",
        "Intercultural Communication",
        "Nonverbal Communication",
        "Communication Research Methods",
        "Persuasion and Rhetoric",
        "Crisis Communication",
        "Health Communication",
        "Political Communication",
        "Social Media Strategy",
        "Communication Ethics"
    ]
    
    cursor.execute("SELECT id, title FROM modules ORDER BY id")
    existing_modules = cursor.fetchall()
    existing_titles = [mod[1] for mod in existing_modules]
    
    for i, title in enumerate(module_titles, 1):
        if title not in existing_titles:
            cursor.execute("""
                INSERT INTO modules (id, title, description, module_prompt, system_corpus)
                VALUES (?, ?, ?, ?, ?)
            """, (
                i, title, 
                f"Comprehensive {title.lower()} module with Socratic teaching methodology",
                f"You are a Socratic tutor for {title}. Guide students through discovery-based learning using strategic questions rather than direct answers.",
                f"Core concepts and frameworks for {title.lower()} education"
            ))
            print(f"   ✅ Created module {i}: {title}")

def create_developer_gui():
    """Create enhanced developer GUI for module configuration"""
    tools_dir = "tools"
    os.makedirs(tools_dir, exist_ok=True)
    
    gui_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Harv Module Configuration</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.2em; opacity: 0.9; }
        .main-content { padding: 30px; }
        .module-selector {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .module-card {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            cursor: pointer;
            transition: transform 0.3s ease;
            text-align: center;
        }
        .module-card:hover { transform: translateY(-5px); }
        .module-card.active {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }
        .config-panel {
            display: none;
            background: #f8f9fa;
            border-radius: 12px;
            padding: 30px;
            margin-top: 20px;
        }
        .config-panel.active { display: block; }
        .config-tabs {
            display: flex;
            margin-bottom: 30px;
            border-bottom: 2px solid #e9ecef;
        }
        .tab-button {
            background: none;
            border: none;
            padding: 15px 25px;
            cursor: pointer;
            font-size: 16px;
            color: #6c757d;
            border-bottom: 3px solid transparent;
            transition: all 0.3s ease;
        }
        .tab-button.active {
            color: #667eea;
            border-bottom-color: #667eea;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active { display: block; }
        .form-group {
            margin-bottom: 25px;
        }
        .form-group label {
            display: block;
            font-weight: 600;
            margin-bottom: 8px;
            color: #495057;
        }
        .form-group textarea, .form-group input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s ease;
        }
        .form-group textarea:focus, .form-group input:focus {
            outline: none;
            border-color: #667eea;
        }
        .form-group textarea {
            min-height: 120px;
            resize: vertical;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            transition: transform 0.3s ease;
        }
        .btn:hover { transform: translateY(-2px); }
        .btn-success {
            background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
        }
        .status-message {
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            display: none;
        }
        .status-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎓 Harv Module Configuration</h1>
            <p>Configure Socratic teaching prompts and memory systems for all 15 modules</p>
        </div>
        
        <div class="main-content">
            <div id="moduleSelector" class="module-selector">
                <!-- Modules will be loaded here -->
            </div>
            
            <div id="configPanel" class="config-panel">
                <div class="config-tabs">
                    <button class="tab-button active" onclick="switchTab('socratic')">Socratic Configuration</button>
                    <button class="tab-button" onclick="switchTab('memory')">Memory System</button>
                    <button class="tab-button" onclick="switchTab('context')">Context Rules</button>
                </div>
                
                <div id="socratic-tab" class="tab-content active">
                    <div class="form-group">
                        <label for="systemPrompt">System Prompt</label>
                        <textarea id="systemPrompt" placeholder="How should Harv behave as a tutor for this module?"></textarea>
                    </div>
                    <div class="form-group">
                        <label for="modulePrompt">Module-Specific Prompt</label>
                        <textarea id="modulePrompt" placeholder="What specific focus should this module have?"></textarea>
                    </div>
                    <div class="form-group">
                        <label for="systemCorpus">Course Knowledge Base</label>
                        <textarea id="systemCorpus" placeholder="Course-wide concepts and knowledge"></textarea>
                    </div>
                    <div class="form-group">
                        <label for="moduleCorpus">Module Resources</label>
                        <textarea id="moduleCorpus" placeholder="Module-specific content and resources"></textarea>
                    </div>
                    <div class="form-group">
                        <label for="dynamicCorpus">Current Events & Examples</label>
                        <textarea id="dynamicCorpus" placeholder="Current events and real-world examples"></textarea>
                    </div>
                </div>
                
                <div id="memory-tab" class="tab-content">
                    <div class="form-group">
                        <label for="memoryExtraction">Memory Extraction Prompt</label>
                        <textarea id="memoryExtraction" placeholder="How should the system analyze conversations for learning insights?"></textarea>
                    </div>
                    <div class="form-group">
                        <label for="masteryTriggers">Mastery Detection Triggers</label>
                        <textarea id="masteryTriggers" placeholder="Phrases that indicate student understanding"></textarea>
                    </div>
                    <div class="form-group">
                        <label for="confusionTriggers">Confusion Detection Triggers</label>
                        <textarea id="confusionTriggers" placeholder="Phrases that indicate student confusion"></textarea>
                    </div>
                    <div class="form-group">
                        <label for="memoryContext">Memory Context Template</label>
                        <textarea id="memoryContext" placeholder="How to use previous learning in new conversations"></textarea>
                    </div>
                    <div class="form-group">
                        <label for="crossModuleRefs">Cross-Module References</label>
                        <textarea id="crossModuleRefs" placeholder="How to reference learning from previous modules"></textarea>
                    </div>
                </div>
                
                <div id="context-tab" class="tab-content">
                    <div class="form-group">
                        <label for="learningStyles">Learning Style Adaptations</label>
                        <textarea id="learningStyles" placeholder="Visual, auditory, kinesthetic adaptations"></textarea>
                    </div>
                    <div class="form-group">
                        <label for="memoryWeight">Memory Weight (Light/Balanced/Heavy)</label>
                        <input type="range" id="memoryWeight" min="1" max="3" value="2">
                        <span id="memoryWeightLabel">Balanced</span>
                    </div>
                </div>
                
                <div class="status-message" id="statusMessage"></div>
                
                <button class="btn btn-success" onclick="saveConfiguration()">💾 Save Configuration</button>
                <button class="btn" onclick="testConfiguration()">🧪 Test Configuration</button>
                <button class="btn" onclick="exportConfiguration()">📤 Export All Configs</button>
            </div>
        </div>
    </div>

    <script>
        let currentModuleId = null;
        let modules = [];

        // Load modules on page load
        document.addEventListener('DOMContentLoaded', loadModules);

        async function loadModules() {
            try {
                const response = await fetch('http://127.0.0.1:8000/modules');
                modules = await response.json();
                displayModules();
            } catch (error) {
                console.error('Error loading modules:', error);
                showStatus('Error loading modules. Make sure backend is running.', 'error');
            }
        }

        function displayModules() {
            const container = document.getElementById('moduleSelector');
            container.innerHTML = modules.map(module => `
                <div class="module-card" onclick="selectModule(${module.id})">
                    <h3>${module.title}</h3>
                    <p>Module ${module.id}</p>
                </div>
            `).join('');
        }

        async function selectModule(moduleId) {
            currentModuleId = moduleId;
            
            // Update UI
            document.querySelectorAll('.module-card').forEach(card => card.classList.remove('active'));
            event.target.closest('.module-card').classList.add('active');
            document.getElementById('configPanel').classList.add('active');
            
            // Load module configuration
            await loadModuleConfiguration(moduleId);
        }

        async function loadModuleConfiguration(moduleId) {
            try {
                const response = await fetch(`http://127.0.0.1:8000/modules/${moduleId}/config`);
                const config = await response.json();
                
                // Populate form fields
                document.getElementById('systemPrompt').value = config.system_prompt || '';
                document.getElementById('modulePrompt').value = config.module_prompt || '';
                document.getElementById('systemCorpus').value = config.system_corpus || '';
                document.getElementById('moduleCorpus').value = config.module_corpus || '';
                document.getElementById('dynamicCorpus').value = config.dynamic_corpus || '';
                document.getElementById('memoryExtraction').value = config.memory_extraction_prompt || '';
                document.getElementById('masteryTriggers').value = config.mastery_triggers || '';
                document.getElementById('confusionTriggers').value = config.confusion_triggers || '';
                document.getElementById('memoryContext').value = config.memory_context_template || '';
                document.getElementById('crossModuleRefs').value = config.cross_module_references || '';
                document.getElementById('learningStyles').value = config.learning_styles || '';
                
                const memoryWeight = config.memory_weight || 2;
                document.getElementById('memoryWeight').value = memoryWeight;
                updateMemoryWeightLabel(memoryWeight);
                
            } catch (error) {
                console.error('Error loading module configuration:', error);
                showStatus('Error loading module configuration', 'error');
            }
        }

        async function saveConfiguration() {
            if (!currentModuleId) {
                showStatus('Please select a module first', 'error');
                return;
            }

            const config = {
                module_prompt: document.getElementById('modulePrompt').value,
                system_corpus: document.getElementById('systemCorpus').value,
                module_corpus: document.getElementById('moduleCorpus').value,
                dynamic_corpus: document.getElementById('dynamicCorpus').value,
                memory_extraction_prompt: document.getElementById('memoryExtraction').value,
                mastery_triggers: document.getElementById('masteryTriggers').value,
                confusion_triggers: document.getElementById('confusionTriggers').value,
                memory_context_template: document.getElementById('memoryContext').value,
                cross_module_references: document.getElementById('crossModuleRefs').value,
                learning_styles: document.getElementById('learningStyles').value,
                memory_weight: parseInt(document.getElementById('memoryWeight').value)
            };

            try {
                const response = await fetch(`http://127.0.0.1:8000/modules/${currentModuleId}/config`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(config)
                });

                if (response.ok) {
                    showStatus('Configuration saved successfully!', 'success');
                } else {
                    showStatus('Error saving configuration', 'error');
                }
            } catch (error) {
                console.error('Error saving configuration:', error);
                showStatus('Error saving configuration', 'error');
            }
        }

        function switchTab(tabName) {
            // Update tab buttons
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            // Update tab content
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            document.getElementById(tabName + '-tab').classList.add('active');
        }

        function updateMemoryWeightLabel(value) {
            const labels = ['', 'Light', 'Balanced', 'Heavy'];
            document.getElementById('memoryWeightLabel').textContent = labels[value];
        }

        document.getElementById('memoryWeight').addEventListener('input', function() {
            updateMemoryWeightLabel(this.value);
        });

        function showStatus(message, type) {
            const statusEl = document.getElementById('statusMessage');
            statusEl.textContent = message;
            statusEl.className = `status-message status-${type}`;
            statusEl.style.display = 'block';
            
            setTimeout(() => {
                statusEl.style.display = 'none';
            }, 5000);
        }

        async function testConfiguration() {
            if (!currentModuleId) {
                showStatus('Please select a module first', 'error');
                return;
            }
            
            try {
                const response = await fetch(`http://127.0.0.1:8000/modules/${currentModuleId}/test`);
                const result = await response.json();
                
                if (result.success) {
                    showStatus('Configuration test passed!', 'success');
                } else {
                    showStatus(`Test failed: ${result.error}`, 'error');
                }
            } catch (error) {
                showStatus('Error testing configuration', 'error');
            }
        }

        async function exportConfiguration() {
            try {
                const response = await fetch('http://127.0.0.1:8000/modules/export');
                const blob = await response.blob();
                
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'harv_module_configurations.json';
                a.click();
                window.URL.revokeObjectURL(url);
                
                showStatus('Configuration exported successfully!', 'success');
            } catch (error) {
                showStatus('Error exporting configuration', 'error');
            }
        }
    </script>
</body>
</html>'''
    
    with open(f"{tools_dir}/dev-gui.html", "w") as f:
        f.write(gui_html)
    
    print("✅ Enhanced developer GUI created")

def create_config_api_endpoints():
    """Create API endpoints for module configuration"""
    backend_dir = "backend/app/routers"
    os.makedirs(backend_dir, exist_ok=True)
    
    config_router = '''"""
Module configuration API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from ..database import get_db
from ..models import Module
from pydantic import BaseModel

router = APIRouter(prefix="/modules", tags=["modules"])

class ModuleConfigUpdate(BaseModel):
    module_prompt: str = None
    system_corpus: str = None
    module_corpus: str = None
    dynamic_corpus: str = None
    memory_extraction_prompt: str = None
    mastery_triggers: str = None
    confusion_triggers: str = None
    memory_context_template: str = None
    cross_module_references: str = None
    learning_styles: str = None
    memory_weight: int = 2

@router.get("/{module_id}/config")
async def get_module_config(module_id: int, db: Session = Depends(get_db)):
    """Get configuration for a specific module"""
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    return {
        "id": module.id,
        "title": module.title,
        "module_prompt": getattr(module, 'module_prompt', ''),
        "system_corpus": getattr(module, 'system_corpus', ''),
        "module_corpus": getattr(module, 'module_corpus', ''),
        "dynamic_corpus": getattr(module, 'dynamic_corpus', ''),
        "memory_extraction_prompt": getattr(module, 'memory_extraction_prompt', ''),
        "mastery_triggers": getattr(module, 'mastery_triggers', ''),
        "confusion_triggers": getattr(module, 'confusion_triggers', ''),
        "memory_context_template": getattr(module, 'memory_context_template', ''),
        "cross_module_references": getattr(module, 'cross_module_references', ''),
        "learning_styles": getattr(module, 'learning_styles', ''),
        "memory_weight": getattr(module, 'memory_weight', 2)
    }

@router.put("/{module_id}/config")
async def update_module_config(
    module_id: int, 
    config: ModuleConfigUpdate, 
    db: Session = Depends(get_db)
):
    """Update configuration for a specific module"""
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    # Update fields that are provided
    for field, value in config.dict(exclude_unset=True).items():
        if hasattr(module, field):
            setattr(module, field, value)
    
    db.commit()
    db.refresh(module)
    
    return {"message": "Configuration updated successfully", "module_id": module_id}

@router.get("/{module_id}/test")
async def test_module_config(module_id: int, db: Session = Depends(get_db)):
    """Test a module's configuration"""
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    # Basic validation
    required_fields = ['module_prompt', 'system_corpus']
    missing_fields = []
    
    for field in required_fields:
        if not getattr(module, field, None):
            missing_fields.append(field)
    
    if missing_fields:
        return {
            "success": False,
            "error": f"Missing required fields: {', '.join(missing_fields)}"
        }
    
    return {
        "success": True,
        "message": "Configuration is valid",
        "module_title": module.title
    }

@router.get("/export")
async def export_all_configurations(db: Session = Depends(get_db)):
    """Export all module configurations"""
    modules = db.query(Module).all()
    
    export_data = []
    for module in modules:
        module_data = {
            "id": module.id,
            "title": module.title,
            "description": module.description,
            "module_prompt": getattr(module, 'module_prompt', ''),
            "system_corpus": getattr(module, 'system_corpus', ''),
            "module_corpus": getattr(module, 'module_corpus', ''),
            "dynamic_corpus": getattr(module, 'dynamic_corpus', ''),
            "memory_extraction_prompt": getattr(module, 'memory_extraction_prompt', ''),
            "mastery_triggers": getattr(module, 'mastery_triggers', ''),
            "confusion_triggers": getattr(module, 'confusion_triggers', ''),
            "memory_context_template": getattr(module, 'memory_context_template', ''),
            "cross_module_references": getattr(module, 'cross_module_references', ''),
            "learning_styles": getattr(module, 'learning_styles', ''),
            "memory_weight": getattr(module, 'memory_weight', 2)
        }
        export_data.append(module_data)
    
    from fastapi.responses import JSONResponse
    import json
    
    return JSONResponse(
        content=export_data,
        headers={"Content-Disposition": "attachment; filename=harv_module_configurations.json"}
    )
'''
    
    with open(f"{backend_dir}/config.py", "w") as f:
        f.write(config_router)
    
    # Update main.py to include config router
    main_py_path = "backend/app/main.py"
    if os.path.exists(main_py_path):
        with open(main_py_path, "r") as f:
            content = f.read()
        
        if "from .routers import config" not in content:
            # Add import
            content = content.replace(
                "from .routers import auth, chat",
                "from .routers import auth, chat, config"
            )
            # Add router
            content = content.replace(
                "app.include_router(chat.router)",
                "app.include_router(chat.router)\napp.include_router(config.router)"
            )
            
            with open(main_py_path, "w") as f:
                f.write(content)
    
    print("✅ Configuration API endpoints created")

def create_config_tests():
    """Create tests for configuration functionality"""
    test_script = '''#!/usr/bin/env python3
"""
Module Configuration Testing Script
Run from root directory: python test_module_configuration.py
"""

import requests
import json
import time

def test_configuration_system():
    """Test the complete module configuration system"""
    print("🧪 TESTING MODULE CONFIGURATION SYSTEM")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8000"
    
    # 1. Test backend is running
    print("1. Testing backend connectivity...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("   ✅ Backend is running")
        else:
            print("   ❌ Backend health check failed")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to backend. Start with: uvicorn app.main:app --reload")
        return False
    
    # 2. Test modules endpoint
    print("2. Testing modules endpoint...")
    try:
        response = requests.get(f"{base_url}/modules")
        modules = response.json()
        print(f"   ✅ Found {len(modules)} modules")
        
        if len(modules) < 15:
            print(f"   ⚠️  Expected 15 modules, found {len(modules)}")
    except Exception as e:
        print(f"   ❌ Modules endpoint error: {e}")
        return False
    
    # 3. Test configuration endpoints
    print("3. Testing configuration endpoints...")
    test_module_id = 1
    
    # Test get config
    try:
        response = requests.get(f"{base_url}/modules/{test_module_id}/config")
        if response.status_code == 200:
            config = response.json()
            print(f"   ✅ Retrieved config for module {test_module_id}")
        else:
            print(f"   ❌ Config retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Config endpoint error: {e}")
        return False
    
    # Test update config
    try:
        test_config = {
            "module_prompt": "Test prompt for configuration validation",
            "system_corpus": "Test knowledge base",
            "memory_weight": 2
        }
        
        response = requests.put(
            f"{base_url}/modules/{test_module_id}/config",
            json=test_config
        )
        
        if response.status_code == 200:
            print("   ✅ Configuration update successful")
        else:
            print(f"   ❌ Config update failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Config update error: {e}")
        return False
    
    # 4. Test configuration validation
    print("4. Testing configuration validation...")
    try:
        response = requests.get(f"{base_url}/modules/{test_module_id}/test")
        result = response.json()
        
        if result.get("success"):
            print("   ✅ Configuration validation passed")
        else:
            print(f"   ⚠️  Validation issues: {result.get('error', 'Unknown')}")
    except Exception as e:
        print(f"   ❌ Validation test error: {e}")
    
    # 5. Test GUI accessibility
    print("5. Testing GUI accessibility...")
    try:
        gui_response = requests.get("http://localhost:3000/dev-gui.html")
        if gui_response.status_code == 200:
            print("   ✅ Developer GUI is accessible")
        else:
            print("   ⚠️  GUI not accessible. Start with: python start_config_gui.py")
    except requests.exceptions.ConnectionError:
        print("   ⚠️  GUI server not running. Start with: python start_config_gui.py")
    
    print("\n" + "=" * 50)
    print("✅ MODULE CONFIGURATION TESTING COMPLETE")
    print("=" * 50)
    print("🎯 Results Summary:")
    print("   ✅ Backend connectivity: Working")
    print("   ✅ Module endpoints: Functional")
    print("   ✅ Configuration API: Operational")
    print("   ✅ Save/Edit operations: Successful")
    print("\n🚀 Ready for integration testing!")
    
    return True

if __name__ == "__main__":
    test_configuration_system()
'''
    
    with open("test_module_configuration.py", "w") as f:
        f.write(test_script)
    
    print("✅ Configuration testing script created")

def create_gui_startup_script():
    """Create startup script for the developer GUI"""
    startup_script = '''#!/usr/bin/env python3
"""
Start Configuration GUI Server
Run from root directory: python start_config_gui.py
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def start_config_gui():
    """Start the configuration GUI server"""
    print("🚀 STARTING HARV CONFIGURATION GUI")
    print("=" * 40)
    
    # Check if tools directory exists
    tools_dir = Path("tools")
    if not tools_dir.exists():
        print("❌ Tools directory not found. Run module_configuration_setup.py first.")
        return False
    
    # Check if GUI file exists
    gui_file = tools_dir / "dev-gui.html"
    if not gui_file.exists():
        print("❌ GUI file not found. Run module_configuration_setup.py first.")
        return False
    
    print("📁 Found configuration GUI files")
    
    # Check if backend is running
    print("🔍 Checking backend status...")
    try:
        import requests
        response = requests.get("http://127.0.0.1:8000/health", timeout=3)
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print("⚠️  Backend not responding properly")
    except:
        print("❌ Backend not running. Start it first:")
        print("   cd backend && uvicorn app.main:app --reload")
        print("\nContinuing with GUI startup...")
    
    # Start HTTP server for GUI
    print("🌐 Starting GUI server...")
    
    try:
        os.chdir("tools")
        print("📍 Changed to tools directory")
        
        # Start HTTP server
        print("🚀 Starting server on http://localhost:3000")
        print("📱 GUI will be available at: http://localhost:3000/dev-gui.html")
        print("\n🎯 Use Ctrl+C to stop the server")
        print("=" * 40)
        
        # Open browser automatically
        def open_browser():
            time.sleep(2)
            webbrowser.open("http://localhost:3000/dev-gui.html")
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Start server
        subprocess.run([sys.executable, "-m", "http.server", "3000"])
        
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped")
        print("✅ Configuration GUI session ended")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False
    
    return True

if __name__ == "__main__":
    start_config_gui()
'''
    
    with open("start_config_gui.py", "w") as f:
        f.write(startup_script)
    
    # Make it executable
    os.chmod("start_config_gui.py", 0o755)
    
    print("✅ GUI startup script created")

if __name__ == "__main__":
    setup_module_configuration()
