from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, config

app = FastAPI(title="Harv Platform API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(config.router, tags=["config"])

@app.get("/")
async def root():
    return {"message": "Harv Platform API"}

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "Harv Platform API is running"}
