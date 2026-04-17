from app.config.settings import get_settings


def list_pipelines() -> list[dict]:
    return get_settings().available_pipelines_json


def get_pipeline(name: str) -> dict:
    pipeline = next((item for item in list_pipelines() if item["name"] == name), None)
    if not pipeline:
        raise ValueError(f"Unsupported pipeline for worker: {name}")
    return pipeline
