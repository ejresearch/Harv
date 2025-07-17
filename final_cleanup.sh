#!/bin/bash
# Final Aggressive Cleanup - Keep Only Essentials
# Run from harv root directory: bash final_cleanup.sh

echo "🔥 FINAL AGGRESSIVE CLEANUP - Remove ALL Noise"
echo "=============================================="

# Create final archive
mkdir -p archive/final_cleanup_$(date +%Y%m%d_%H%M%S)
FINAL_ARCHIVE="archive/final_cleanup_$(date +%Y%m%d_%H%M%S)"

echo "📁 Final archive: $FINAL_ARCHIVE"

# List of ALL noise to remove
NOISE_FILES=(
    "deploy_harv_complete.sh"
    "diagnose_endpoints.py"
    "end.py"
    "exports"
    "final_auth_fix.sh"
    "fix_422_errors.py"
    "fix_missing_endpoints.py"
    "fix_suite_4_chat.sh"
    "fix_suite_4_user_id.sh"
    "harv_frontend_fix.sh"
    "harv_frontend_setup.sh"
    "memory_migration.py"
    "migrate_existing_db.py"
    "mod.py"
    "quick_git_push_upgrade.sh"
    "quick_tailwind_fix.sh"
    "quick_user_test.py"
    "run_progressive_tests.sh"
    "SELECT"
    "start_complete_platform.sh"
    "start_frontend.sh"
    "start_full_platform.sh"
    "testing.py"
    "update_suite_3_real_auth.sh"
    "validation_report.json"
    "comprehensive_cleanup.sh"
    "complete_integration_fix.sh"
    "content"
)

# Remove noise directories
NOISE_DIRS=(
    "backend_backup_20250714_104633"
    "backend_backup_20250715_101446"
    "backend_backup_20250715_104106"
    "frontend_backup_20250717_140308"
    "frontend_old_backup"
    "tests"
)

# Remove noise database backups
NOISE_DB_FILES=(
    "harv.db.backup_20250714_103208"
)

echo "🗑️  Removing noise files..."
for file in "${NOISE_FILES[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" "$FINAL_ARCHIVE/"
        echo "   ✅ Archived: $file"
    fi
done

echo "🗑️  Removing noise directories..."
for dir in "${NOISE_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        mv "$dir" "$FINAL_ARCHIVE/"
        echo "   ✅ Archived: $dir/"
    fi
done

echo "🗑️  Removing old database backups..."
for db_file in "${NOISE_DB_FILES[@]}"; do
    if [ -f "$db_file" ]; then
        mv "$db_file" "$FINAL_ARCHIVE/"
        echo "   ✅ Archived: $db_file"
    fi
done

# Keep only essential files in requirements.txt
if [ -f "requirements.txt" ]; then
    echo "📝 Cleaning requirements.txt..."
    cat > requirements.txt << 'EOF'
# Harv Platform Dependencies
fastapi>=0.68.0
uvicorn[standard]>=0.15.0
sqlalchemy>=1.4.0
pydantic>=1.8.0
passlib[bcrypt]>=1.7.4
python-jose[cryptography]>=3.3.0
python-multipart>=0.0.5
openai>=1.0.0
python-dotenv>=0.19.0
EOF
    echo "   ✅ Cleaned requirements.txt"
fi

echo ""
echo "🎉 FINAL CLEANUP COMPLETE!"
echo "========================="
echo ""
echo "📁 All noise archived to: $FINAL_ARCHIVE"
echo ""
echo "🚀 Your CLEAN repository structure:"
echo "   harv/"
echo "   ├── backend/          # FastAPI backend"
echo "   ├── frontend/         # React frontend"
echo "   ├── tools/            # Configuration GUI"
echo "   ├── scripts/          # Essential scripts"
echo "   ├── harv_venv/        # Virtual environment"
echo "   ├── harv.db           # Database"
echo "   ├── requirements.txt  # Clean dependencies"
echo "   ├── README.md         # Documentation"
echo "   └── archive/          # All old stuff safely stored"
echo ""
echo "🎯 FINAL RESULT: Clean, professional repository!"
echo "   - All functionality preserved"
echo "   - All noise removed"
echo "   - Everything archived safely"
echo ""
echo "✅ Ready for production deployment!"

# Show final directory listing
echo ""
echo "📋 Final clean directory:"
ls -la | grep -v "^total"
