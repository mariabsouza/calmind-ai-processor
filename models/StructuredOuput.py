from pydantic import BaseModel, Field


class StructuredOutput(BaseModel):
    titulo: str = Field(..., description="Content title")
    subtitulo: str = Field(..., description="Content subtitle")
    conteudo: str = Field(..., description="Content")