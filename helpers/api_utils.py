import json

from models.FinalOutput import OptimizedContent
from models.StructuredOuput import StructuredOutput


def cors_headers():
    return {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }

def format_output(buffer, rewritten_chunks):
    data = json.loads(buffer)
    parser_response = StructuredOutput(**data)

    optimized_content = OptimizedContent(
        content_title=parser_response.content_title,
        content_subtitle=parser_response.content_subtitle,
        original_chunks=parser_response.original_chunks, 
        replaced_chunks=rewritten_chunks   
    )

    return optimized_content.model_dump()

def get_original_content(request):
    data = request.get_json(silent=True)
    original_content = data.get("content")
    title = data.get("title") 
    return f"Título: {title} - Conteúdo: {original_content}"