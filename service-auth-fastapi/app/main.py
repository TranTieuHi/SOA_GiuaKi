from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth
from app.config.database import db
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Auth Service API",
    description="Authentication Service built with FastAPI",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(auth.router, prefix="/api")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "OK",
        "message": "Auth Service is running",
        "database": "connected" if db.get_connection().open else "disconnected"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    db.connect()
    print("🚀 Auth Service started successfully")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    db.close()
    print("👋 Auth Service stopped")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)