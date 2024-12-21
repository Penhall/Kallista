from crewai import Agent, Task, Crew
from langchain.llms import OpenAI
from agents.specialized.wpf_agent import WPFAgent
from agents.specialized.database_agent import DatabaseAgent
from agents.specialized.security_agent import SecurityAgent
from agents.specialized.api_agent import APIAgent
from agents.specialized.uiux_agent import UIUXAgent
from agents.core.architec_agent import ArchitectAgent

def main():
    try:
        # Inicializar os agentes
        architect = ArchitectAgent()
        wpf_agent = WPFAgent()
        database_agent = DatabaseAgent()
        security_agent = SecurityAgent()
        api_agent = APIAgent()
        uiux_agent = UIUXAgent()

        print("Kallista - Sistema de Desenvolvimento WPF")
        print("Inicializando agentes...")
        
        # Criar a crew com os agentes
        crew = Crew(
            agents=[
                architect,
                wpf_agent,
                database_agent,
                security_agent,
                api_agent,
                uiux_agent
            ]
        )

        print("Sistema inicializado com sucesso!")
        print("\nAgentes disponíveis:")
        for agent in crew.agents:
            print(f"- {agent.__class__.__name__}")

    except Exception as e:
        print(f"Erro ao inicializar o sistema: {str(e)}")

if __name__ == "__main__":
    main()