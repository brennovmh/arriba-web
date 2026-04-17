from fastapi import APIRouter

from app.schemas.pipeline import PipelineDefinitionResponse
from app.services.pipeline_service import list_pipelines

router = APIRouter(prefix="/pipelines", tags=["pipelines"])


@router.get("", response_model=list[PipelineDefinitionResponse])
def get_pipelines() -> list[PipelineDefinitionResponse]:
    return [PipelineDefinitionResponse.model_validate(item) for item in list_pipelines()]
