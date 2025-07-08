from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.endpoints import auth, modules, chat, memory, documents

app = FastAPI(
    title="Harv Backend",
    description="Lightweight, RAG-ready backend for GPT-powered modules",
    version="1.0.0"
)

# Optional: configure CORS if you expect to call the backend from a frontend on a different domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
app.include_router(auth.router)
app.include_router(modules.router)
app.include_router(chat.router)
app.include_router(memory.router)
app.include_router(documents.router)

# Health check endpoint
@app.get("/")
def root():
    return {"message": "Harv backend is running."}

