# Harv Platform - Drag & Drop Deployment

## Quick Start
```bash
# 1. Run the complete deployment
bash deploy_harv_complete.sh

# 2. Start the platform
bash start_harv.sh

# 3. Open your browser
# GUI: http://localhost:3000/dev-gui.html
# Backend: http://localhost:8000
```

## Manual Steps (if needed)
```bash
# Install dependencies
pip install fastapi uvicorn sqlalchemy passlib[bcrypt] pydantic openai python-dotenv

# Start backend
cd backend
uvicorn app.main:app --reload

# Start GUI (new terminal)
cd tools
python3 -m http.server 3000
```

## Configuration
1. Edit `.env` file with your OpenAI API key
2. Open http://localhost:3000/dev-gui.html
3. Select a module and click "Edit"
4. Configure prompts and save
5. Test with sample messages

## Files Created
- `tools/dev-gui.html` - Clean minimal GUI
- `backend/app/endpoints/modules.py` - Module API
- `backend/app/endpoints/memory.py` - Memory API
- `start_harv.sh` - One-click startup script
- `.env` - Environment configuration
