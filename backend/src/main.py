"""FastAPI application entry point for the AI Todo Chatbot."""

import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from slowapi.errors import RateLimitExceeded

from src.db import init_db, close_db
from src.mcp.server import mcp_server
from src.core.exceptions import AuthException
from src.core.rate_limit import limiter

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup and shutdown."""
    # Startup
    logger.info("Starting AI Todo Chatbot...")

    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    # Initialize MCP server
    try:
        await mcp_server.initialize()
        logger.info("MCP server initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize MCP server: {e}")
        raise

    logger.info("AI Todo Chatbot started successfully!")

    yield

    # Shutdown
    logger.info("Shutting down AI Todo Chatbot...")
    await close_db()
    logger.info("Shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="AI Todo Chatbot",
    description="AI-Powered Todo Chatbot using MCP and OpenAI Agents SDK",
    version="1.0.0",
    lifespan=lifespan,
)

# Attach rate limiter to app state
app.state.limiter = limiter

# Configure CORS - must specify exact origins when using credentials
# Cannot use "*" with allow_credentials=True
ALLOWED_ORIGINS = [
    "http://localhost:3000",      # Next.js development
    "http://localhost:3001",      # Next.js fallback port
    "http://127.0.0.1:3000",      # Alternative localhost
    "http://127.0.0.1:3001",      # Alternative fallback
    os.getenv("FRONTEND_URL", ""),  # Production frontend URL
]
# Filter out empty strings
ALLOWED_ORIGINS = [origin for origin in ALLOWED_ORIGINS if origin]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Rate limit exceeded handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Handle rate limit exceeded errors."""
    # Get origin for CORS headers
    origin = request.headers.get("origin", "")
    headers = {}
    if origin in ALLOWED_ORIGINS:
        headers = {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
        }
    return JSONResponse(
        status_code=429,
        content={
            "code": "RATE_LIMITED",
            "message": "Too many requests. Please try again later.",
        },
        headers=headers,
    )


# Authentication exception handler
@app.exception_handler(AuthException)
async def auth_exception_handler(request: Request, exc: AuthException) -> JSONResponse:
    """Handle authentication exceptions with consistent error format."""
    # Merge CORS headers with exception headers
    origin = request.headers.get("origin", "")
    headers = dict(exc.headers) if exc.headers else {}
    if origin in ALLOWED_ORIGINS:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
        },
        headers=headers,
    )


# HTTPException handler with CORS headers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions with CORS headers."""
    origin = request.headers.get("origin", "")
    headers = dict(exc.headers) if exc.headers else {}
    if origin in ALLOWED_ORIGINS:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail if isinstance(exc.detail, dict) else {"detail": exc.detail},
        headers=headers,
    )


# Helper function to get CORS headers for error responses
def get_cors_headers(request: Request) -> dict[str, str]:
    """Get CORS headers based on the request origin."""
    origin = request.headers.get("origin", "")
    if origin in ALLOWED_ORIGINS:
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
        }
    return {}


# Global error handler for friendly error messages
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler that returns friendly error messages.

    Never exposes stack traces or technical details to users.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    # Return a friendly error message with CORS headers
    return JSONResponse(
        status_code=500,
        content={
            "detail": "I'm having trouble processing your request right now. Please try again."
        },
        headers=get_cors_headers(request),
    )


# Health check endpoint
@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "ai-todo-chatbot"}


# Import and register routers
from src.api.auth import router as auth_router
from src.api.chat import router as chat_router
from src.api.tasks import router as tasks_router

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(tasks_router)
