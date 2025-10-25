from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.routes import otp
from app.models.otp import HealthResponse
import datetime
import os

# Initialize FastAPI app
app = FastAPI(
    title="OTP Service API",
    description="Microservice for OTP generation, verification with in-memory storage",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(otp.router, prefix="/api")

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API information"""
    return {
        "service": "OTP Service",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "timestamp": datetime.datetime.now().isoformat()
    }

# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.datetime.now().isoformat(),
        service="OTP Service",
        version="1.0.0"
    )

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "detail": str(exc),
            "path": str(request.url),
            "timestamp": datetime.datetime.now().isoformat()
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Actions to perform on startup"""
    print("=" * 60)
    print("🚀 OTP Service Started!")
    print(f"📝 Documentation: http://localhost:{os.getenv('PORT', 8002)}/docs")
    print(f"❤️  Health Check: http://localhost:{os.getenv('PORT', 8002)}/health")
    print("=" * 60)
    print("✅ In-memory OTP storage initialized")
    print("✅ Rate limiting middleware active")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Actions to perform on shutdown"""
    from app.services.otp_service import otp_service
    from app.middleware.rate_limit import clear_all_rate_limits
    
    otp_count = otp_service.clear_storage()
    rate_limit_count = clear_all_rate_limits()
    
    print("\n" + "=" * 60)
    print("🛑 OTP Service Shutting Down...")
    print(f"🗑️  Cleared {otp_count} OTP records from memory")
    print(f"🗑️  Cleared {rate_limit_count} rate limit records")
    print("=" * 60)

# Run with: python -m app.main
if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8002))
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )