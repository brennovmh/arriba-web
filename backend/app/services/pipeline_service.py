from fastapi import HTTPException

from app.core.config import get_settings


def list_pipelines() -> list[dict]:
    return get_settings().available_pipelines_json


def get_pipeline_or_400(name: str) -> dict:
    pipeline = next((item for item in list_pipelines() if item["name"] == name), None)
    if not pipeline:
        raise HTTPException(status_code=400, detail=f"Unsupported pipeline: {name}")
    return pipeline
