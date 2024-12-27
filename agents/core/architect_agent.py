# agents/core/architect_agent.py
from crewai import Agent
from typing import List, Dict

class ArchitectAgent(Agent):
    def __init__(self, llm):
        super().__init__(
            role='Software Architect',
            goal='Design and maintain the software architecture',
            backstory="""You are an experienced software architect with deep 
            knowledge of C#, WPF, and MVVM patterns. You ensure the system follows 
            best practices and maintains high quality standards.""",
            llm=llm,
            tools=self._get_tools(),
            allow_delegation=False
        )
        self.tools = []  # Será implementado posteriormente

    def analyze_requirements(self, project_specs: Dict) -> Dict:
        """Analisa os requisitos e retorna estrutura detalhada"""
        prompt = f"""
        Given these project specifications:
        {project_specs}

        Provide a detailed structure for implementing this WPF application.
        Include:
        1. Required Models with properties
        2. ViewModels and their interactions
        3. Views needed with their layouts
        4. Services and dependencies
        5. Design patterns to be used
        
        Return the structure in a valid JSON format.
        """
        return self.agent.execute_task(prompt)
        
        
    def validate_design(self, design: Dict) -> bool:
        """Valida se o design segue os padrões estabelecidos"""
        # Implementação inicial
        return True
    
    def _get_tools(self):
        """Define ferramentas disponíveis para o agente"""
        return []