# README.md

# Primer Initiative — GPT Tutor Configuration Tool

This is a developer tool for the Primer Initiative Platform, an Introduction to Mass Communication course delivered by 15 GPT-powered Socratic tutoring modules.  
It enables Content & Training teams to configure, test, and refine Socratic prompts that guide students through educational dialogue rather than simply giving answers.

## Quick Start

### Clone the Repo and Enter Project
```
git clone https://github.com/ejresearch/Harv.git
cd Harv
```

### Set Up Virtual Environment
```
python3 -m venv harv_venv
source harv_venv/bin/activate
```

### Install Dependencies
```
pip install -r requirements.txt
```

### Set Your OpenAI API Key
```
export OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
```

## Run the Platform

### Every Time (Development)

#### Terminal 1: Backend
```
cd harv/backend
source ../harv_venv/bin/activate
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

#### Terminal 2: Frontend
```
cd harv/tools
python3 -m http.server 3000
```

You should see:
```
Serving HTTP on :: port 3000 (http://[::]:3000/) ...
```

Open your browser:  
http://localhost:3000/dev-gui.html

## Optional: One-Command Launch Script

Create `start.sh`:
```
#!/bin/bash
echo "Starting Primer Initiative..."

cd backend && source ../harv_venv/bin/activate && uvicorn app.main:app --reload &

cd ../tools && python3 -m http.server 3000 &

echo "Servers started"
echo "Backend: http://127.0.0.1:8000"
echo "GUI: http://localhost:3000/dev-gui.html"
echo "Press Ctrl+C to stop"
wait
```

Make executable and run:
```
chmod +x start.sh
./start.sh
```

## Requirements

Python 3.9 or higher (3.12 recommended)  
OpenAI API Key  
Modern web browser  
Basic terminal access

## Architecture

Backend: FastAPI + SQLite + OpenAI  
Frontend: HTML/JS + TailwindCSS  
Database Schema: Includes GPT prompt fields and resources per module  
API Endpoints:
- `/modules` (GET/PUT)
- `/chat` (POST)
- `/modules/populate` (POST)

## Workflow

Select one of the 15 modules  
Configure and test Socratic prompts  
Upload course materials  
Test tutor behavior live  
Save configurations for use in student platform

## 15 Modules

1. Introduction to Mass Communication
2. History and Evolution of Media
3. Media Theory and Effects
4. Print Media and Journalism
5. Broadcasting: Radio and Television
6. Digital Media and the Internet
7. Social Media and New Platforms
8. Media Ethics and Responsibility
9. Media Law and Regulation
10. Advertising and Public Relations
11. Media Economics and Business Models
12. Global Media and Cultural Impact
13. Media Literacy and Critical Analysis
14. Future of Mass Communication
15. Capstone: Integrating Knowledge

For more details, see the `docs/` folder if available.

Repository: [https://github.com/ejresearch/Harv.git](https://github.com/ejresearch/Harv.git)

---

# requirements.txt

```
fastapi>=0.95.0
uvicorn>=0.20.0
pydantic>=1.10.0
sqlalchemy>=1.4.0
openai>=0.27.0
jinja2>=3.1.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.5

