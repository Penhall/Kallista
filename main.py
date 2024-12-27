from crewai import Agent, Task, Crew
from dotenv import load_dotenv
import os
from typing import Dict, List
import asyncio


from langchain_openai import ChatOpenAI

# Importa os agentes
from agents.core.architect_agent  import ArchitectAgent
from agents.specialized.wpf_agent import WpfAgent
from agents.specialized.uiux_agent import UiUxAgent
from agents.specialized.database_agent import DatabaseAgent
from agents.specialized.api_agent import ApiAgent




load_dotenv()
def create_agents(llm):
    """Cria os agentes necessários"""
    return {
        'architect': ArchitectAgent(llm),
        'wpf': WpfAgent(llm),
        'uiux': UiUxAgent(llm),
        'database': DatabaseAgent(llm),
        'api': ApiAgent(llm)
    }

def create_tasks(agents: Dict[str, Agent]) -> List[Task]:
    """Cria as tarefas para os agentes"""
    return [
        Task(
            description="Setup Project Architecture",
            agent=agents['architect'],
            expected_output="Project structure and patterns definition"
        ),
        Task(
            description="Design WPF Interface",
            agent=agents['wpf'],
            expected_output="WPF interface implementation"
        )
        # Adicionar mais tarefas conforme necessário
    ]

def main():
    # Configurar LLM
    llm = ChatOpenAI(
        model="gpt-4",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    # Criar agentes
    agents = create_agents(llm)

    # Criar tarefas
    tasks = create_tasks(agents)

    # Criar crew
    crew = Crew(
        agents=list(agents.values()),
        tasks=tasks
    )
    
  

    # Executar
    result = crew.kickoff()

if __name__ == "__main__":
    main()
