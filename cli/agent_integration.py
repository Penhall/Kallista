# cli/agent_integration.py

from crewai import Crew, Task
from langchain_openai import ChatOpenAI
from agents.specialized.wpf_agent import WpfAgent
from agents.specialized.api_agent import ApiAgent
from agents.specialized.database_agent import DatabaseAgent
from agents.specialized.security_agent import SecurityAgent
from agents.specialized.uiux_agent import UiUxAgent
from tools.wpf.project_generator import WPFProjectGenerator
from analysis.agent_analyzer import AgentAnalyzer
from datetime import datetime
import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Dict, List, Any
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
        self.project_generator = WPFProjectGenerator()
        self.agent_analyzer = AgentAnalyzer()  # Novo analisador
            
        self.llm = ChatOpenAI(
            model="gpt-4",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        self.output_path = Path("output")
        self.output_path.mkdir(exist_ok=True)
        self.project_generator = WPFProjectGenerator()

    
    async def generate_project(self, project_structure: Dict):
        """Gera o projeto usando os agentes especializados"""
        print("\nIniciando geração com agentes...")
        try:
            # Análise inicial com o novo analisador
            analysis_result = await self.agent_analyzer.analyze_with_agents(project_structure)
            print("\nAnálise de requisitos concluída...")

            # Criar agentes com o contexto da análise
            agents = self._create_agents()
            
            # Criar e executar tarefas com contexto enriquecido
            enriched_structure = {
                **project_structure,
                'analysis': analysis_result
            }
            
            tasks = self._create_tasks(agents, enriched_structure)
            crew = Crew(agents=list(agents.values()), tasks=tasks)
            
            # Executar projeto
            print("\nExecutando tarefas...")
            results = crew.kickoff()
            
            # Gerar código usando WPFProjectGenerator
            generation_result = await self.project_generator.generate_project(
                self._merge_specs(enriched_structure, results)
            )
            
            # Processar e salvar resultados
            return await self._process_results(results, enriched_structure, generation_result)
            
        except Exception as e:
            print(f"Erro na geração: {str(e)}")
            return None

    def _create_tasks(self, agents: Dict, enriched_structure: Dict) -> List[Task]:
        """Cria tarefas para os agentes com contexto enriquecido"""
        project_name = enriched_structure['metadata']['name']
        analysis = enriched_structure.get('analysis', {})
        domain = analysis.get('domain_analysis', {}).get('primary_domain', 'generic')

        return [
            Task(
                description=f"Design user interface and experience for {project_name} ({domain} application)",
                agent=agents['uiux'],
                expected_output="UI/UX specifications and guidelines",
                context=analysis.get('agent_analyses', {}).get('uiux', {})
            ),
            Task(
                description=f"Implement WPF interface for {project_name} ({domain} application)",
                agent=agents['wpf'],
                expected_output="WPF implementation details",
                context=analysis.get('agent_analyses', {}).get('wpf', {})
            ),
            Task(
                description=f"Design and implement database structure for {project_name}",
                agent=agents['database'],
                expected_output="Database schema and Entity Framework implementation",
                context=analysis.get('agent_analyses', {}).get('database', {})
            ),
            Task(
                description=f"Design and implement service layer for {project_name}",
                agent=agents['api'],
                expected_output="API specifications and implementation",
                context=analysis.get('agent_analyses', {}).get('api', {})
            ),
            Task(
                description=f"Analyze and implement security measures for {project_name}",
                agent=agents['security'],
                expected_output="Security analysis and recommendations",
                context=analysis.get('agent_analyses', {}).get('security', {})
            )
        ]
    

    async def _get_agent_specs(self, agent: Any, structure: Dict) -> Dict:
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

    def _merge_specs(self, structure: Dict, results: Any) -> Dict:
        """Mescla especificações com resultados da análise"""
        return {
            'metadata': structure['metadata'],
            'type': structure['type'],
            'features': structure.get('features', {}),
            'analysis': structure.get('analysis', {}),
            'agent_results': str(results)
        }
   
    def _create_tasks(self, agents: Dict, project_structure: Dict) -> List[Task]:
        """Cria tarefas para os agentes"""
        project_name = project_structure['metadata']['name']
        project_type = project_structure['type']
        
        return [
            Task(
                description=f"Design user interface and experience for {project_name} ({project_type})",
                agent=agents['uiux'],
                expected_output="UI/UX specifications and guidelines"
            ),
            Task(
                description=f"Implement WPF interface for {project_name} ({project_type})",
                agent=agents['wpf'],
                expected_output="WPF implementation details"
            ),
            Task(
                description=f"Design and implement database structure for {project_name}",
                agent=agents['database'],
                expected_output="Database schema and Entity Framework implementation"
            ),
            Task(
                description=f"Design and implement service layer for {project_name}",
                agent=agents['api'],
                expected_output="API specifications and implementation"
            ),
            Task(
                description=f"Analyze and implement security measures for {project_name}",
                agent=agents['security'],
                expected_output="Security analysis and recommendations"
            )
        ]

    async def save_project_structure(self, structure: Dict):
        """Salva a estrutura do projeto"""
        structure_file = self.output_path / f"{structure['metadata']['name']}_structure.json"
        with open(structure_file, "w") as f:
            json.dump(structure, f, indent=4)

    async def _process_results(self, results: Any, structure: Dict, generation_result: Dict) -> Dict:
        """Processa os resultados dos agentes"""
        try:
            project_name = structure['metadata']['name']
            output_dir = self.output_path / project_name
            output_dir.mkdir(exist_ok=True)
            
            # Estruturar resultado
            results_dict = {
                'project': {
                    'name': project_name,
                    'type': structure['type'],
                    'metadata': structure['metadata']
                },
                'analysis': {
                    'security': self._parse_security_output(str(results)),
                    'implementation': self._parse_implementation_details(str(results))
                },
                'generation': generation_result,
                'timestamp': datetime.now().isoformat()
            }
            
            # Salvar resultados
            results_file = output_dir / "generation_results.json"
            with open(results_file, "w") as f:
                json.dump(results_dict, f, indent=4)
            
            return results_dict

        except Exception as e:
            print(f"Erro ao processar resultados: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }

    def _parse_security_output(self, output: str) -> Dict:
        """Parse do output de segurança"""
        return {
            'measures': [
                measure.strip()
                for measure in output.split('\n')
                if measure.strip().startswith(('1.', '2.', '3.', '4.', '5.'))
            ],
            'code_samples': self._extract_code_samples(output)
        }

    def _parse_implementation_details(self, output: str) -> Dict:
        """Parse dos detalhes de implementação"""
        return {
            'architecture': 'MVVM',
            'patterns': ['Repository', 'Command'],
            'frameworks': ['Entity Framework', 'WPF']
        }

    def _extract_code_samples(self, output: str) -> List[Dict]:
        """Extrai exemplos de código do output"""
        code_samples = []
        lines = output.split('\n')
        in_code_block = False
        current_code = []

        for line in lines:
            if line.startswith('```'):
                if in_code_block:
                    code_samples.append({
                        'language': 'csharp',
                        'code': '\n'.join(current_code)
                    })
                    current_code = []
                in_code_block = not in_code_block
                continue
            if in_code_block:
                current_code.append(line)

        return code_samples
    
            
    def _create_agents(self) -> Dict:
        """Cria instâncias dos agentes especializados"""
        return {
            'wpf': WpfAgent(self.llm),
            'api': ApiAgent(self.llm),
            'database': DatabaseAgent(self.llm),
            'security': SecurityAgent(self.llm),
            'uiux': UiUxAgent(self.llm)
        }