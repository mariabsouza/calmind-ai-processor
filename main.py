import os
import time
from flask import jsonify
import json
import functions_framework
from google.genai import types
from google import genai
from models.StructuredOuput import StructuredOutput
from prompts.parser_agent import parser_agent_prompt

@functions_framework.http
def function_handler(request):
    
    data = request.get_json(silent=True)
    original_content = data.get("content", "Texto padrão se não vier nada para testes")
    
    generate_content_config = types.GenerateContentConfig(
        temperature=0.2,
        response_schema=StructuredOutput,
        thinking_config = types.ThinkingConfig(
            thinking_budget=0,
        ),
        response_mime_type="application/json")

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=parser_agent_prompt(original_content),
        config=generate_content_config
        
    )
    
    response_json = json.loads(response.text)
    
    return jsonify(response_json)
