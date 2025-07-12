
import json
from dotenv import load_dotenv
from crewai import LLM, Agent, Crew, Task
from models.StructuredOuput import StructuredOutput
from models.agents import ContentAgents

load_dotenv()

def lambda_handler(event, context):
    llm = LLM(
    model="gemini/gemini-2.0-flash",
    temperature=0.2)

    body = json.loads(event['body'])
    original_content = body['content']
    
    content_structurator = ContentAgents()
    agent = content_structurator.obter_agente(llm)


    structure_content = Task(
        description=(
            f"Analise o conteúdo recebido, e sem alterar nenhuma informação no texto, indique através de json, qual o título, subtítulo (apenas se houver, não crie um) e conteúdo. Conteúdo: {original_content}"
        ),
        agent=agent,
        expected_output="JSON estruturado com titulo, subtitulo e conteudo",
        output_json=StructuredOutput
    )

    crew = Crew(
        agents=[agent],
        tasks=[structure_content],
        verbose=True
    )


    resultados = crew.kickoff()

    return resultados