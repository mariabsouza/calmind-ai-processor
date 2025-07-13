from typing import Optional
from pydantic import BaseModel, Field

from models.StructuredOuput import OriginalChunkContent

class OptimizedChunkContent(BaseModel):
    chunk_title: str
    chunk_content: str


class OptimizedContent(BaseModel):
    content_title: str = Field(..., description="Content title")
    content_subtitle: Optional[str] = Field(..., description="Content subtitle")
    original_chunks: list[OriginalChunkContent] = Field(..., description="Original Content")
    replaced_chunks: list[OptimizedChunkContent] = Field(..., description="Replaced Content")