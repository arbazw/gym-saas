# app/main.py

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.db import create_tables
from app.routes import users as users_router_module
from app.routes import gyms as gyms_router_module
from app.routes import trials as trials_router_module

logger = logging.getLogger("uvicorn.error")

def get_app() -> FastAPI:
    app = FastAPI(
        title="Gym SaaS API",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # CORS - allow env-driven origins (for dev default allow localhost)
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
    origins = [o.strip() for o in allowed_origins.split(",") if o.strip()]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(users_router_module.router)
    app.include_router(gyms_router_module.router)
    app.include_router(trials_router_module.router)

    # Startup handler to ensure tables exist
    @app.on_event("startup")
    def on_startup():
        logger.info("Creating database tables (if not exist)...")
        create_tables()
        logger.info("Startup complete.")

    return app


app = get_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEV_RELOAD", "true").lower() in ("1", "true", "yes"),
        log_level="info",
    )
