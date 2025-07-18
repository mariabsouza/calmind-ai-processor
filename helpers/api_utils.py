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

def format_output(parser_response : StructuredOutput, rewritten_chunks):
    optimized_content = OptimizedContent(
        content_title=parser_response.content_title,
        original_chunks=parser_response.original_chunks, 
        replaced_chunks=rewritten_chunks   
    )

    return optimized_content.model_dump()

def get_original_content(request):
    data = request.get_json(silent=True)
    original_content = data.get("content")
    title = data.get("title") 
    needs=data.get("dificultties")
    return f"Título: {title} - Conteúdo: {original_content}", needs