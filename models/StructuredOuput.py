from typing import List, Optional
from pydantic import BaseModel, Field

class OriginalChunkContent(BaseModel):
    chunk_title: Optional[str]
    chunk_content: str


class StructuredOutput(BaseModel):
    content_title: str = Field(..., description="Content title")
    content_subtitle: Optional[str] = Field(..., description="Content subtitle")
    original_chunks: List[OriginalChunkContent] = Field(..., description="Content")