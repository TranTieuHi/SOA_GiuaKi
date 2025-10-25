from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.database import db
from app.routes import student, payment  # ✅ Import payment
import os
import uvicorn

app = FastAPI(
    title="Tuition Payment Service API",
    description="Microservice for handling student tuition payments",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Đảm bảo có dòng này
app.include_router(student.router, prefix="/api/students", tags=["Students"])
app.include_router(payment.router, prefix="/api/payments", tags=["Payments"])  # ✅ Quan trọng!

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - Service information"""
    return {
        "service": "Tuition Payment Service",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "students": "/api/students",
            "payments": "/api/payments"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        connection = db.get_connection()
        
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup"""
    print("=" * 60)
    print("🚀 Tuition Payment Service Started!")
    print(f"📝 Documentation: http://localhost:{os.getenv('PORT', 8001)}/docs")
    print(f"❤️  Health Check: http://localhost:{os.getenv('PORT', 8001)}/health")
    print("=" * 60)
    
    # Test database connection
    try:
        db.get_connection()
        print("✅ Database connection: OK")
    except Exception as e:
        print(f"⚠️  Database connection: FAILED - {e}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown"""
    try:
        db.close()
    except:
        pass
    print("🛑 Tuition Payment Service Stopped!")

# Run server
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )