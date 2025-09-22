from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from collections import defaultdict
import time
import uvicorn

# Import your modules
from . import database, models
from .routers import users, expenses, categories, reports, export
from .config import settings

# Create tables
models.Base.metadata.create_all(bind=database.engine)

# Rate limiting middleware (simple implementation)
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        now = time.time()
        
        # Clean old entries
        self.clients[client_ip] = [
            timestamp for timestamp in self.clients[client_ip]
            if now - timestamp < self.period
        ]
        
        # Check rate limit
        if len(self.clients[client_ip]) >= self.calls:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Too many requests."
            )
        
        # Add current request
        self.clients[client_ip].append(now)
        
        response = await call_next(request)
        return response

# Initialize FastAPI app
app = FastAPI(
    title="💰 Expense Management API",
    description="""
    A comprehensive expense management API with the following features:
    
    ## 🚀 Features
    - **User Authentication** - JWT-based secure authentication
    - **Expense Tracking** - Create, read, update, delete expenses
    - **Categories** - Organize expenses by custom categories
    - **Reports** - Monthly and yearly expense reports
    - **Data Export** - Export data to CSV and Excel formats
    - **Rate Limiting** - API protection against abuse
    
    ## 📊 Analytics
    - Monthly spending breakdown
    - Category-wise expense analysis
    - Daily spending patterns
    - Year-over-year comparisons
    
    ## 🔒 Security
    - JWT token authentication
    - Password hashing with bcrypt
    - Rate limiting on sensitive endpoints
    - Input validation and sanitization
    """,
    version="0.1.0",
    contact={
        "name": "Expense API Support",
        "email": "amirdoustdar1@gmail.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    }
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(RateLimitMiddleware, calls=100, period=60)

# Include routers
app.include_router(users.router)
app.include_router(expenses.router)
app.include_router(categories.router)
app.include_router(reports.router)
app.include_router(export.router)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Expense Management API",
        "version": "3.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": time.time()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)