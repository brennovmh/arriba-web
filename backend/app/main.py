from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import analyses, auth, files, jobs, pipelines, system, worker_admin, worker_api
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.session import init_db

settings = get_settings()
configure_logging()

app = FastAPI(
    title="Lab NGS Platform API",
    version="0.1.0",
    description="MVP API for internal NGS analysis orchestration.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


app.include_router(system.router)
app.include_router(auth.router)
app.include_router(analyses.router)
app.include_router(jobs.router)
app.include_router(pipelines.router)
app.include_router(files.router)
app.include_router(worker_api.router)
app.include_router(worker_admin.router)
