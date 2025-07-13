import os
from flask import jsonify
import json
import functions_framework
from google.genai import types
from google import genai
from models.FinalOutput import OptimizedChunkContent, OptimizedContent
from models.StructuredOuput import StructuredOutput
from prompts.parser_agent import parser_agent_prompt
from prompts.rewriter_agent import rewriter_agent_prompt

@functions_framework.http
def function_handler(request):
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    data = request.get_json(silent=True)
    original_content = data.get("content", "Texto padrão se não vier nada para testes")
    
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    

    ## ========== PARSER AGENT ====================
    parser_generate_content_config = types.GenerateContentConfig(
        temperature=0.2,
        response_schema=StructuredOutput,
        thinking_config = types.ThinkingConfig(
            thinking_budget=0,
        ),
        response_mime_type="application/json")

    parser_response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=parser_agent_prompt(original_content),
        config=parser_generate_content_config
    )

    parser_response: StructuredOutput = parser_response.parsed

    ## ============= REWRITER AGENT ===========================

    rewriter_generate_content_config = types.GenerateContentConfig(
        temperature=0.4,
        response_schema=list[OptimizedChunkContent],
        thinking_config = types.ThinkingConfig(
            thinking_budget=0,
        ),
        response_mime_type="application/json")


    rewriter_response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=rewriter_agent_prompt(parser_response.original_chunks),
        config=rewriter_generate_content_config
    )
    
    rewriter_response: list[OptimizedChunkContent] = rewriter_response.parsed

    optimized_content = OptimizedContent(
        content_title=parser_response.content_title,
        content_subtitle=parser_response.content_subtitle,
        original_chunks=parser_response.original_chunks, 
        replaced_chunks=rewriter_response   
    )

    response_json = optimized_content.model_dump()  # Converte o objeto Pydantic para dicionário

    headers = {"Access-Control-Allow-Origin": "*"}

    return (jsonify(response_json), 200, headers)
