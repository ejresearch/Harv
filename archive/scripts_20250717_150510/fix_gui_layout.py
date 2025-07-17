#!/usr/bin/env python3
"""
Fix GUI Layout - Right Side Display
Fixes the right side display issue in the dev-gui.html
Run from harv root directory: python fix_gui_layout.py
"""

import os
import shutil
from datetime import datetime

def fix_gui_layout():
    """Fix the GUI layout issue"""
    
    print("🎨 Fixing GUI Layout - Right Side Display")
    print("=" * 50)
    
    gui_path = "tools/dev-gui.html"
    if not os.path.exists(gui_path):
        print(f"❌ {gui_path} not found")
        return
    
    # Create backup
    backup_path = f"{gui_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(gui_path, 'r') as f:
        content = f.read()
    
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"📁 Backup created: {backup_path}")
    
    # Fix CSS for better layout
    css_fixes = '''
    <style>
        /* Fix right side display issues */
        .main-container {
            display: flex;
            flex-direction: column;
            min-height: 100vh;
            max-width: 100%;
            overflow-x: hidden;
        }
        
        .header {
            flex-shrink: 0;
            width: 100%;
            padding: 1rem;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }
        
        .content-area {
            flex: 1;
            display: flex;
            width: 100%;
            max-width: 100%;
        }
        
        .sidebar {
            width: 300px;
            min-width: 300px;
            max-width: 300px;
            background: #f8f9fa;
            border-right: 1px solid #dee2e6;
            overflow-y: auto;
            height: calc(100vh - 80px);
        }
        
        .main-content {
            flex: 1;
            padding: 2rem;
            overflow-y: auto;
            height: calc(100vh - 80px);
            max-width: calc(100vw - 300px);
        }
        
        .form-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-bottom: 2rem;
        }
        
        .form-group {
            display: flex;
            flex-direction: column;
        }
        
        .form-group label {
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #495057;
        }
        
        .form-group textarea {
            min-height: 100px;
            padding: 0.75rem;
            border: 1px solid #ced4da;
            border-radius: 0.25rem;
            resize: vertical;
        }
        
        .form-group select {
            padding: 0.75rem;
            border: 1px solid #ced4da;
            border-radius: 0.25rem;
        }
        
        .context-toggles {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .toggle-group {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .test-section {
            margin-top: 2rem;
            padding: 1.5rem;
            background: #f8f9fa;
            border-radius: 0.5rem;
            border: 1px solid #dee2e6;
        }
        
        .test-input {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #ced4da;
            border-radius: 0.25rem;
            margin-bottom: 1rem;
        }
        
        .test-response {
            background: white;
            padding: 1rem;
            border-radius: 0.25rem;
            border: 1px solid #dee2e6;
            min-height: 100px;
        }
        
        .btn {
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 0.25rem;
            cursor: pointer;
            font-weight: 500;
        }
        
        .btn-primary {
            background: #007bff;
            color: white;
        }
        
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        
        .btn-success {
            background: #28a745;
            color: white;
        }
        
        /* Responsive adjustments */
        @media (max-width: 1200px) {
            .form-grid {
                grid-template-columns: 1fr;
            }
            
            .sidebar {
                width: 250px;
                min-width: 250px;
            }
            
            .main-content {
                max-width: calc(100vw - 250px);
            }
        }
        
        @media (max-width: 768px) {
            .content-area {
                flex-direction: column;
            }
            
            .sidebar {
                width: 100%;
                height: auto;
                max-height: 200px;
            }
            
            .main-content {
                max-width: 100%;
                height: auto;
            }
        }
    </style>
    '''
    
    # Replace or add the CSS
    if '<style>' in content:
        # Replace existing style block
        import re
        content = re.sub(r'<style>.*?</style>', css_fixes, content, flags=re.DOTALL)
    else:
        # Add CSS before </head>
        content = content.replace('</head>', css_fixes + '\n</head>')
    
    # Also fix the HTML structure if needed
    if 'main-container' not in content:
        # Add proper container structure
        content = content.replace('<body>', '''<body>
    <div class="main-container">
        <div class="header">
            <h1>Harv Module Configuration</h1>
        </div>
        <div class="content-area">''')
        
        content = content.replace('</body>', '''        </div>
    </div>
</body>''')
    
    # Write the fixed content
    with open(gui_path, 'w') as f:
        f.write(content)
    
    print("✅ GUI layout fixed")
    print("")
    print("🚀 Next Steps:")
    print("1. Refresh your browser: http://localhost:3000/dev-gui.html")
    print("2. Right side should now display properly")
    print("3. All form elements should be visible")
    print("")
    print("🎯 Your GUI should now be fully functional!")

if __name__ == "__main__":
    fix_gui_layout()
