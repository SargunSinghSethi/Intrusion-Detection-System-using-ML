import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import upload, status, result, history

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="IDS Backend API",
    description="Intrusion Detection System Backend",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        # Add your production frontend URL here
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, tags=["Upload"])
app.include_router(status.router, tags=["Status"])
app.include_router(result.router, tags=["Results"])
app.include_router(history.router, tags=["History"])

@app.get("/")
def read_root():
    return {
        "message": "IDS Backend API",
        "version": "2.0.0",
        "endpoints": {
            "upload": "/upload",
            "status": "/status/{job_id}",
            "result": "/result/{job_id}",
            "history": "/history"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
