
import json
from dotenv import load_dotenv
from crewai import LLM, Agent, Crew, Task
from models.StructuredOuput import StructuredOutput
from models.agents import ContentAgents
import functions_framework

load_dotenv()

@functions_framework.http
def function_handler(request):
    llm = LLM(
    model="gemini/gemini-2.0-flash",
    temperature=0.2)

    print(request)
    original_content = "Esse é um teste"
    
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