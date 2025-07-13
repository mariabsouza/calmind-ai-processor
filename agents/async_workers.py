import asyncio
from agents.rewriter_agent import RewriterAgent


async def process_chunk_async(chunk_dict, client):

    rewriter_agent = RewriterAgent(chunk_dict["chunk_content"])

    response = await asyncio.to_thread(
        lambda: client.models.generate_content(
            model="gemini-2.5-flash",
            contents=rewriter_agent.prompt,
            config=rewriter_agent.agent_config
        )
    )

    return response.parsed