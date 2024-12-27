# cli/agent_integration.py

from crewai import Crew, Task
from langchain_openai import ChatOpenAI
from agents.specialized.wpf_agent import WpfAgent
from agents.specialized.api_agent import ApiAgent
from agents.specialized.database_agent import DatabaseAgent
from agents.specialized.security_agent import SecurityAgent
from agents.specialized.uiux_agent import UiUxAgent
import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Dict, List
import json

class AgentIntegrator:
    def __init__(self):
        load_dotenv()
        self.llm = ChatOpenAI(
            model="gpt-4",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        self.output_path = Path("output")
        self.output_path.mkdir(exist_ok=True)

    async def generate_project(self, project_structure: Dict):
        """Gera o projeto usando os agentes especializados"""
        print("\nIniciando geração com agentes...")
        try:
            # Criar agentes
            agents = self._create_agents()
            
            # Analisar requisitos
            specs = {}
            for agent_name, agent in agents.items():
                print(f"\nProcessando {agent_name}...")
                specs[agent_name] = await self._get_agent_specs(agent, project_structure)
            
            # Criar e executar tarefas
            tasks = self._create_tasks(agents, specs)
            crew = Crew(agents=list(agents.values()), tasks=tasks)
            
            # Executar projeto
            print("\nExecutando tarefas...")
            results = crew.kickoff()
            
            # Processar e salvar resultados
            return await self._process_results(results, project_structure)
            
        except Exception as e:
            print(f"Erro na geração: {str(e)}")
            return None

    def _create_agents(self) -> Dict:
        """Cria instâncias dos agentes especializados"""
        return {
            'wpf': WpfAgent(self.llm),
            'api': ApiAgent(self.llm),
            'database': DatabaseAgent(self.llm),
            'security': SecurityAgent(self.llm),
            'uiux': UiUxAgent(self.llm)
        }

    async def _get_agent_specs(self, agent, structure: Dict) -> Dict:
        """Obtém especificações de cada agente"""
        if isinstance(agent, UiUxAgent):
            return await agent.analyze_requirements(structure)
        elif isinstance(agent, WpfAgent):
            return await agent.design_interface(structure)
        elif isinstance(agent, DatabaseAgent):
            return await agent.design_database_schema(structure)
        elif isinstance(agent, ApiAgent):
            return await agent.design_service_layer(structure)
        elif isinstance(agent, SecurityAgent):
            return await agent.analyze_security(structure)
        return {}

    def _create_tasks(self, agents: Dict, specs: Dict) -> List[Task]:
        """Cria tarefas para os agentes"""
        return [
            Task(
                description="Design user interface and experience",
                agent=agents['uiux'],
                expected_output="UI/UX specifications and guidelines"
            ),
            Task(
                description="Implement WPF interface",
                agent=agents['wpf'],
                expected_output="WPF implementation details"
            ),
            Task(
                description="Design and implement database structure",
                agent=agents['database'],
                expected_output="Database schema and Entity Framework implementation"
            ),
            Task(
                description="Design and implement service layer",
                agent=agents['api'],
                expected_output="API specifications and implementation"
            ),
            Task(
                description="Analyze and implement security measures",
                agent=agents['security'],
                expected_output="Security analysis and recommendations"
            )
        ]

    async def _process_results(self, results: Dict, structure: Dict) -> Dict:
        """Processa os resultados dos agentes"""
        project_name = structure['metadata']['name']
        output_dir = self.output_path / project_name
        output_dir.mkdir(exist_ok=True)
        
        # Salvar resultados
        results_file = output_dir / "generation_results.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=4)
        
        print(f"\nResultados salvos em: {results_file}")
        
        return {
            "status": "success",
            "project_name": project_name,
            "output_directory": str(output_dir),
            "results": results
        }

    async def save_project_structure(self, structure: Dict):
        """Salva a estrutura do projeto"""
        structure_file = self.output_path / f"{structure['metadata']['name']}_structure.json"
        with open(structure_file, "w") as f:
            json.dump(structure, f, indent=4)