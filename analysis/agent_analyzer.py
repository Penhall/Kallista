# analysis/agent_analyzer.py
from typing import Dict, List, Any
from .requirements_analyzer import RequirementsAnalyzer
from agents.specialized.uiux_agent import UiUxAgent
from agents.specialized.wpf_agent import WpfAgent
from agents.specialized.database_agent import DatabaseAgent
from agents.specialized.api_agent import ApiAgent
from agents.specialized.security_agent import SecurityAgent

class AgentAnalyzer:
    def __init__(self):
        self.requirements_analyzer = RequirementsAnalyzer()

    async def analyze_with_agents(self, project_structure: Dict) -> Dict[str, Any]:
        """Coordena análise entre RequirementsAnalyzer e agentes"""
        try:
            # Primeira análise de requisitos
            initial_analysis = await self.requirements_analyzer.analyze_requirements(project_structure)

            # Enriquece o project_structure com a análise inicial
            enriched_structure = {
                **project_structure,
                'domain_analysis': initial_analysis['domain_analysis'],
                'suggested_patterns': initial_analysis['patterns']
            }

            # Coleta análises específicas dos agentes
            agent_analyses = await self._collect_agent_analyses(enriched_structure)

            # Combina todas as análises
            final_analysis = self._combine_analyses(
                initial_analysis,
                agent_analyses,
                project_structure
            )

            return final_analysis

        except Exception as e:
            print(f"Erro na análise com agentes: {str(e)}")
            return {}

    async def _collect_agent_analyses(self, enriched_structure: Dict) -> Dict[str, Any]:
        """Coleta análises de cada agente especializado"""
        analyses = {}

        try:
            # UI/UX Analysis
            uiux_agent = UiUxAgent(None)  # O LLM será injetado posteriormente
            analyses['uiux'] = await uiux_agent.analyze_requirements(enriched_structure)

            # WPF Implementation Analysis
            wpf_agent = WpfAgent(None)
            analyses['wpf'] = await wpf_agent.design_interface(enriched_structure)

            # Database Analysis
            db_agent = DatabaseAgent(None)
            analyses['database'] = await db_agent.design_database_schema(enriched_structure)

            # API Analysis
            api_agent = ApiAgent(None)
            analyses['api'] = await api_agent.design_service_layer(enriched_structure)

            # Security Analysis
            security_agent = SecurityAgent(None)
            analyses['security'] = await security_agent.analyze_security(enriched_structure)

        except Exception as e:
            print(f"Erro ao coletar análises dos agentes: {str(e)}")

        return analyses

    def _combine_analyses(self, 
                         initial_analysis: Dict,
                         agent_analyses: Dict,
                         project_structure: Dict) -> Dict[str, Any]:
        """Combina análises em uma estrutura coesa"""
        return {
            'project_info': {
                'name': project_structure.get('metadata', {}).get('name', ''),
                'type': project_structure.get('type', ''),
                'description': project_structure.get('metadata', {}).get('description', '')
            },
            'domain_analysis': initial_analysis['domain_analysis'],
            'patterns': initial_analysis['patterns'],
            'technical_requirements': initial_analysis['technical'],
            'agent_analyses': agent_analyses,
            'recommendations': self._merge_recommendations(
                initial_analysis['recommendations'],
                agent_analyses
            )
        }

    def _merge_recommendations(self, 
                             initial_recommendations: Dict,
                             agent_analyses: Dict) -> Dict[str, Any]:
        """Mescla recomendações de todas as fontes"""
        merged = {
            'architecture': initial_recommendations['architecture_recommendations'],
            'ui': initial_recommendations['ui_recommendations'],
            'implementation': initial_recommendations['implementation_recommendations'],
            'security': [],
            'database': [],
            'api': []
        }

        # Adiciona recomendações específicas dos agentes
        if 'security' in agent_analyses:
            merged['security'] = self._extract_security_recommendations(
                agent_analyses['security']
            )

        if 'database' in agent_analyses:
            merged['database'] = self._extract_database_recommendations(
                agent_analyses['database']
            )

        if 'api' in agent_analyses:
            merged['api'] = self._extract_api_recommendations(
                agent_analyses['api']
            )

        return merged

    def _extract_security_recommendations(self, security_analysis: Dict) -> List[str]:
        """Extrai recomendações de segurança"""
        recommendations = []
        if 'vulnerabilities' in security_analysis:
            for vuln in security_analysis['vulnerabilities']:
                recommendations.append(f"Security: {vuln['recommendation']}")
        return recommendations

    def _extract_database_recommendations(self, db_analysis: Dict) -> List[str]:
        """Extrai recomendações de banco de dados"""
        recommendations = []
        if 'entities' in db_analysis:
            recommendations.append(f"Database: Suggested {len(db_analysis['entities'])} entities")
        return recommendations

    def _extract_api_recommendations(self, api_analysis: Dict) -> List[str]:
        """Extrai recomendações de API"""
        recommendations = []
        if 'interfaces' in api_analysis:
            recommendations.append(f"API: Suggested {len(api_analysis['interfaces'])} interfaces")
        return recommendations
