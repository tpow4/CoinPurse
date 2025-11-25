"""
Main FastAPI application entry point
Run with: uvicorn main:app --reload --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference

from routers.institutions_router import router as institutions_router
from routers.accounts_router import router as accounts_router

# Create FastAPI app
app = FastAPI(
    title="CoinPurse API",
    description="Personal finance tracking application",
    version="1.0.0"
)

# Configure CORS for Svelte frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Svelte dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(institutions_router, prefix="/api")
app.include_router(accounts_router, prefix="/api")


@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "message": "Finance Tracker API", 
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check for monitoring"""
    return {"status": "healthy"}

@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        # Your OpenAPI document
        openapi_url=app.openapi_url,
        # Avoid CORS issues (optional)
        scalar_proxy_url="https://proxy.scalar.com",
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
