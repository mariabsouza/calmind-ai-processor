import asyncio
import os
import re
import time
from dotenv import load_dotenv
from flask import jsonify
import json
import functions_framework
from google import genai
from helpers.api_utils import cors_headers, format_output, get_original_content
from agents.parser_agent import ParserAgent
from agents.rewriter_agent import RewriterAgent
from models.StructuredOuput import OriginalChunkContent, StructuredOutput

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

async def process_chunk_async(chunk: OriginalChunkContent, needs):

    rewriter_agent = RewriterAgent(chunk.chunk_content, needs)

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

    original_content, needs = get_original_content(request)

    tasks = []
    buffer = ""

    parser_agent = ParserAgent(original_content)

    for chunk in client.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents=parser_agent.prompt,
        config=parser_agent.agent_config
    ):
        if not chunk.text:
            continue

        buffer += chunk.text

    data = json.loads(buffer)
    parser_response = StructuredOutput(**data)

    for chunk in parser_response.original_chunks:
        tasks.append(process_chunk_async(chunk, needs))

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    rewritten_chunks = loop.run_until_complete(asyncio.gather(*tasks))

    response_json = format_output(parser_response, rewritten_chunks)
    headers = {"Access-Control-Allow-Origin": "*"}

    return (jsonify(response_json), 200, headers)
