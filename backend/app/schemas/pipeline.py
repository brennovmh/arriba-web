from pydantic import BaseModel


class PipelineDefinitionResponse(BaseModel):
    name: str
    version: str
    description: str
