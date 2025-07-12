import os
from crewai import Agent
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI as LLM

class ContentAgents:

    def obter_agente(self, llm):
        return Agent(
            role="Parseador de conteúdo estruturado",
            goal="Estruturar o conteúdo recebido",
            backstory="Você é especialista em organizar informações de forma clara e padronizada, sem modificar o seu conteúdo",
            verbose=True,
            llm=llm
        )