from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import student, payment

app = FastAPI(
    title="Tuition Service API",
    description="Microservice for student tuition management",
    version="1.0.0"
)

# ✅ CORS - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"]  # Expose all headers
)

# Register routes
app.include_router(student.router, tags=["Students"])
app.include_router(payment.router, tags=["Payments"])

@app.get("/")
async def root():
    return {"message": "Tuition Service API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "tuition-service",
        "version": "1.0.0"
    }

@app.on_event("startup")
async def startup_event():
    print("\n" + "=" * 70)
    print("🚀 TUITION SERVICE STARTED")
    print("=" * 70)
    print("📋 Registered Routes:")
    for route in app.routes:
        if hasattr(route, "methods"):
            methods = ", ".join(route.methods)
            print(f"   [{methods}] {route.path}")
    print("=" * 70 + "\n")