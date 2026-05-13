from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database.connection import db
from backend.api import shorts, blogs, articles, trending, domains
import uvicorn

app = FastAPI(
    title="StayingAhead News API",
    description="Production-grade API for AI-powered news intelligence delivery.",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lifecycle Events
@app.on_event("startup")
async def startup():
    await db.connect()

@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()

# Routes
app.include_router(shorts.router, prefix="/api")
app.include_router(blogs.router, prefix="/api")
app.include_router(articles.router, prefix="/api")
app.include_router(trending.router, prefix="/api")
app.include_router(domains.router, prefix="/api")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected" if db.pool else "disconnected"}

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
