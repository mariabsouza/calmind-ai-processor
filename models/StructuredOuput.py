from typing import List, Optional
from pydantic import BaseModel, Field

class ChunkContent(BaseModel):
    chunk_title: Optional[str]
    chunk_content: str


class StructuredOutput(BaseModel):
    content_title: str = Field(..., description="Content title")
    content_subtitle: Optional[str] = Field(..., description="Content subtitle")
    chunks: List[ChunkContent] = Field(..., description="Content")