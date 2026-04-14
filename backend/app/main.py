from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path

from app.core.config import settings
from app.core.exceptions import AppException
from app.api.v1.router import api_router
from app.db.session import create_tables, AsyncSessionLocal
from app.repositories.category_repository import CategoryRepository


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await create_tables()
    async with AsyncSessionLocal() as db:
        await CategoryRepository(db).seed_defaults()
        await db.commit()
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="Income & Expense management with personal and group accounts",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# API routes
app.include_router(api_router)


# Global exception handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME}
