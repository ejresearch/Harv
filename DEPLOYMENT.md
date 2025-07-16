# Harv Platform Deployment Guide

## Pre-Alpha Release Deployment

### Quick Start
```bash
# 1. Start backend
cd backend
uvicorn app.main:app --reload

# 2. Start configuration GUI
cd tools
python3 -m http.server 3000

# 3. Validate system
bash run_progressive_tests.sh
```

### Production Deployment Checklist

#### Database Setup
- [ ] Run database schema migration
- [ ] Populate 15 communication modules
- [ ] Verify memory system tables
- [ ] Test database connectivity

#### Environment Configuration
- [ ] Set OpenAI API key
- [ ] Configure JWT secret
- [ ] Set CORS origins
- [ ] Verify environment loading

#### Backend Deployment
- [ ] Install Python dependencies
- [ ] Start FastAPI server
- [ ] Verify API endpoints
- [ ] Test authentication system

#### System Validation
- [ ] Run progressive test suite
- [ ] Verify AI integration
- [ ] Test memory persistence
- [ ] Validate configuration GUI

### Service URLs
- Backend API: http://localhost:8000
- Configuration GUI: http://localhost:3000/dev-gui.html
- API Documentation: http://localhost:8000/docs
- Frontend (optional): http://localhost:5173

### System Requirements
- Python 3.8+
- Node.js 16+ (for frontend)
- SQLite 3
- OpenAI API key
- 2GB RAM minimum
- 1GB disk space

### Monitoring
- API health: GET /health
- Memory statistics: GET /memory/stats/{module_id}
- Module accessibility: GET /modules
- Authentication status: POST /auth/login
