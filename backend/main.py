"""
FastAPI Main Application
Todo Full-Stack Web App - Backend API

Features:
- JWT Authentication with Better Auth
- Multi-user task isolation
- Complete task CRUD operations
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from contextlib import asynccontextmanager

# Import routes and utilities
from routes.auth import router as auth_router
from routes.tasks import router as tasks_router
from db import engine, init_db
from middleware import verify_jwt_middleware
from config import HOST, PORT

# Create FastAPI app
app = FastAPI(
    title="Todo App API",
    description="Full-Stack Todo Application API with JWT Authentication",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# JWT Verification Middleware
@app.middleware("http")
async def jwt_middleware(request: Request, call_next):
    """
    Apply JWT verification middleware to protected requests only

    Excludes public routes: /auth/signup, /auth/signin, /health, /, /docs, /redoc
    """
    # Check if path is a public route (doesn't require authentication)
    public_paths = ["/auth/signup", "/auth/signin", "/health", "/", "/docs", "/redoc", "/openapi.json"]

    # Skip JWT verification for public paths
    if request.url.path in public_paths or request.url.path.startswith("/docs") or request.url.path.startswith("/redoc"):
        return await call_next(request)

    # For all other paths, verify JWT token
    await verify_jwt_middleware(request)
    response = await call_next(request)
    return response


# Database initialization on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup: Create database tables
    init_db()
    print("Database initialized successfully")

    yield

    # Shutdown: Cleanup (if needed)
    print("Application shutdown")


# Set lifespan
app.router.lifespan_context = lifespan


# Include routers
app.include_router(auth_router)
app.include_router(tasks_router)


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    Does not require JWT authentication
    """
    return {"status": "healthy", "service": "todo-api"}


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with API information
    """
    return {
        "name": "Todo App API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "auth": "/auth/*",
            "tasks": "/api/{user_id}/tasks/*"
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=True,
        log_level="info"
    )
