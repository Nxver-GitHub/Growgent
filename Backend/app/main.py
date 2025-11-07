"""
FastAPI main application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Growgent API",
    description="Open-source agentic platform for climate-adaptive irrigation and wildfire management",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Growgent API", "version": "0.1.0"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

