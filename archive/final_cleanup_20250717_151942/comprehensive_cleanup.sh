#!/bin/bash
# Comprehensive Directory Cleanup
# Removes ALL random scripts and keeps only essentials
# Run from harv root directory: bash comprehensive_cleanup.sh

echo "🔥 COMPREHENSIVE CLEANUP - Remove All Random Scripts"
echo "=================================================="

# Create archive directory for safety
mkdir -p archive/scripts_$(date +%Y%m%d_%H%M%S)
ARCHIVE_DIR="archive/scripts_$(date +%Y%m%d_%H%M%S)"

echo "📁 Creating archive directory: $ARCHIVE_DIR"

# List of random scripts to remove (from your terminal output)
SCRIPTS_TO_REMOVE=(
    "aggressive_cleanup.sh"
    "backend_api_standardization.py"
    "backend_connection_fix.sh"
    "check_and_fix_git_push.sh"
    "CHANGELOG.md"
    "check_endpoints.py"
    "complete_app_flow_fix.sh"
    "complete_harv_app.sh"
    "complete_system_fix.py"
    "config_api_fix.py"
    "cors_fix.py"
    "create_tables.py"
    "debug_backend_validation.py"
    "demo_mode_setup.sh"
    "DEPLOYMENT.md"
    "diagnose_form_issue.sh"
    "direct_endpoint_fix.py"
    "end_to_end_test_suites.py"
    "final_system_validation.py"
    "fix_422_auth_errors.py"
    "fix_config_api.py"
    "fix_database_schema.py"
    "fix_gui_layout.py"
    "fix_gui_single_button.py"
    "fix_import_errors.py"
    "fix_router_inclusion.py"
    "frontend_auth_oauth2_fix.sh"
    "frontend_integration.py"
    "github_push_module_config.sh"
    "harv_pre_alpha_release.sh"
    "memory_stats_fix.py"
    "memory_validation_fix.py"
    "minimal_fix_no_backup.py"
    "module_configuration_setup.py"
    "populate_module_configs.py"
    "project_cleanup.sh"
    "progressive_test_suites.sh"
    "quick_env_setup.sh"
    "restart_backend_demo.sh"
    "run_all_test_suites.py"
    "setup_database.py"
    "simple_chat_test.py"
    "start_backend.sh"
    "start_complete_app.sh"
    "start_config_gui.py"
    "start_demo.sh"
    "start_harv.sh"
    "start_harv_complete.sh"
    "syntax.py"
    "test_auth_formats.py"
    "test_backend_models.py"
    "test_connection.js"
    "test_fixed_auth.py"
    "test_frontend_auth.py"
    "test_frontend_connection.js"
    "test_models_fix.py"
    "test_suite_1_foundation.py"
    "test_suite_2_configuration.py"
    "test_suite_3_authentication.py"
    "test_suite_4_chat_ai.py"
    "test_suite_5_frontend.py"
    "update_suite_3_real_auth.py"
    "validation_script.py"
)

# Move random scripts to archive
echo "🗂️  Archiving random scripts..."
for script in "${SCRIPTS_TO_REMOVE[@]}"; do
    if [ -f "$script" ]; then
        mv "$script" "$ARCHIVE_DIR/"
        echo "   ✅ Archived: $script"
    fi
done

# Remove backup files
echo "🗑️  Removing backup files..."
find . -name "*.backup.*" -type f | while read file; do
    mv "$file" "$ARCHIVE_DIR/"
    echo "   ✅ Archived backup: $file"
done

# Clean up demo_frontend if it exists
if [ -d "demo_frontend" ]; then
    echo "🗑️  Removing demo_frontend directory..."
    mv "demo_frontend" "$ARCHIVE_DIR/"
    echo "   ✅ Archived: demo_frontend/"
fi

# Clean up any other random directories
DIRS_TO_CLEAN=(
    "cleanup"
    "logs"
    "temp"
    "test_output"
)

for dir in "${DIRS_TO_CLEAN[@]}"; do
    if [ -d "$dir" ]; then
        mv "$dir" "$ARCHIVE_DIR/"
        echo "   ✅ Archived: $dir/"
    fi
done

# Create essential scripts directory
mkdir -p scripts

# Create ONE setup script
cat > scripts/setup.sh << 'EOF'
#!/bin/bash
# Harv Platform Setup
echo "🌱 Setting up Harv Platform..."

# Create virtual environment if it doesn't exist
if [ ! -d "harv_venv" ]; then
    python3 -m venv harv_venv
    echo "✅ Created virtual environment"
fi

# Activate virtual environment
source harv_venv/bin/activate

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
pip install -q fastapi uvicorn sqlalchemy pydantic passlib[bcrypt] python-jose[cryptography] python-multipart openai python-dotenv
cd ..

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Create .env file if it doesn't exist
if [ ! -f "backend/.env" ]; then
    echo "📝 Creating .env template..."
    cat > backend/.env << 'ENVEOF'
# Add your OpenAI API key here
OPENAI_API_KEY=your_openai_key_here

# JWT Secret (auto-generated)
JWT_SECRET_KEY=harv_secret_key_change_in_production

# Database
DATABASE_URL=sqlite:///./harv.db
ENVEOF
    echo "⚠️  Please add your OpenAI API key to backend/.env"
fi

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Add your OpenAI API key to backend/.env"
echo "2. Run: bash scripts/start.sh"
EOF

# Create ONE start script
cat > scripts/start.sh << 'EOF'
#!/bin/bash
# Start Harv Platform
echo "🚀 Starting Harv Platform..."

# Check if virtual environment exists
if [ ! -d "harv_venv" ]; then
    echo "❌ Virtual environment not found. Run: bash scripts/setup.sh"
    exit 1
fi

# Activate virtual environment
source harv_venv/bin/activate

# Start backend in background
echo "🔧 Starting backend..."
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start GUI server in background
echo "🎨 Starting configuration GUI..."
cd tools
python3 -m http.server 3000 &
GUI_PID=$!
cd ..

# Start frontend
echo "⚛️  Starting React frontend..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "🎉 Harv Platform Started!"
echo "========================="
echo "🔧 Backend:       http://localhost:8000"
echo "🎨 GUI:           http://localhost:3000/dev-gui.html"
echo "⚛️  Frontend:     http://localhost:3000"
echo "📖 API Docs:     http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user to stop
wait
EOF

# Make scripts executable
chmod +x scripts/setup.sh
chmod +x scripts/start.sh

echo ""
echo "🎉 CLEANUP COMPLETE!"
echo "=================="
echo ""
echo "📁 Archived to: $ARCHIVE_DIR"
echo "   - All random scripts safely archived"
echo "   - All backup files archived"
echo "   - Demo directories archived"
echo ""
echo "🚀 Clean Structure Created:"
echo "   harv/"
echo "   ├── backend/          # FastAPI backend"
echo "   ├── frontend/         # React frontend"  
echo "   ├── tools/            # Configuration GUI"
echo "   ├── scripts/          # 2 essential scripts"
echo "   │   ├── setup.sh      # One-time setup"
echo "   │   └── start.sh      # Start platform"
echo "   ├── harv_venv/        # Virtual environment"
echo "   ├── harv.db           # Database"
echo "   └── README.md         # Documentation"
echo ""
echo "🎯 Next Steps:"
echo "   1. bash scripts/setup.sh     # Setup environment"
echo "   2. Add OpenAI key to backend/.env"
echo "   3. bash scripts/start.sh     # Start platform"
echo ""
echo "Your sophisticated platform functionality is preserved!"
echo "Now it's just clean and organized! 🌱"
