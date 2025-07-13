import asyncio
import os
import re
import time
from flask import jsonify
import json
import functions_framework
from google import genai
from helpers.api_utils import cors_headers, format_output
from models.FinalOutput import OptimizedContent
from models.StructuredOuput import StructuredOutput
from agents.parser_agent import ParserAgent
from agents.rewriter_agent import RewriterAgent

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

async def process_chunk_async(chunk_dict):

    rewriter_agent = RewriterAgent(chunk_dict["chunk_content"])

    response = await asyncio.to_thread(
        lambda: client.models.generate_content(
            model="gemini-2.5-flash",
            contents=rewriter_agent.prompt,
            config=rewriter_agent.agent_config
        )
    )

    return response.parsed

@functions_framework.http
def function_handler(request):
    if request.method == 'OPTIONS':
        return ('', 204, cors_headers())
    
    data = request.get_json(silent=True)
    original_content = data.get("content")
    
    tasks = []
    buffer = ""
    already_seen_chunks = set()

    parser_agent = ParserAgent(original_content)

    for chunk in client.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents=parser_agent.prompt,
        config=parser_agent.agent_config
    ):
        if not chunk.text:
            continue

        buffer += chunk.text

        if '"original_chunks":[' in buffer:
            for match in get_chunks_matches(buffer):
                chunk_str = match.group()
                try:
                    chunk_dict = json.loads(chunk_str)

                    chunk_id = chunk_dict.get("chunk_title") + chunk_dict.get("chunk_content")[:10]
                    if chunk_id in already_seen_chunks:
                        continue

                    already_seen_chunks.add(chunk_id)
                    tasks.append(process_chunk_async(chunk_dict))

                except Exception as e:
                    print("Erro ao parsear objeto:", e)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    rewritten_chunks = loop.run_until_complete(asyncio.gather(*tasks))

    response_json = format_output(buffer, rewritten_chunks)
    headers = {"Access-Control-Allow-Origin": "*"}
    return (jsonify(response_json), 200, headers)

def get_chunks_matches(buffer):
    array_start = buffer.find('"original_chunks":[') + len('"original_chunks":[')
    array_content = buffer[array_start:]

    chunk_object_regex = re.compile(r'\{[^{}]+\}(?=,|\])')
    return chunk_object_regex.finditer(array_content)
