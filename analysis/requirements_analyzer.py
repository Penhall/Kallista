# analysis/requirements_analyzer.py
from typing import Dict, List, Any, Optional
from pathlib import Path
import json

class RequirementsAnalyzer:
    def __init__(self):
        self.domain_patterns_path = Path("templates/domain_patterns")
        self.domain_patterns_path.mkdir(parents=True, exist_ok=True)
        
        # Padrões conhecidos por domínio
        self.domain_patterns = {
            'business': {
                'patterns': ['CRUD', 'DocumentManagement', 'Reporting'],
                'common_features': ['Authentication', 'Authorization', 'Audit']
            },
            'data_analysis': {
                'patterns': ['Dashboard', 'Charts', 'DataGrid'],
                'common_features': ['RealTimeUpdates', 'Export', 'Filtering']
            },
            'workflow': {
                'patterns': ['StateMachine', 'TaskManagement', 'Timeline'],
                'common_features': ['Notification', 'Status', 'Progress']
            }
        }
    async def analyze_requirements(self, requirements: Dict) -> Dict[str, Any]:
        """Análise completa dos requisitos"""
        try:
            # Identificar domínio
            domain_analysis = self._analyze_domain(requirements)
            
            # Identificar padrões aplicáveis
            pattern_suggestions = self._identify_patterns(domain_analysis)
            
            # Analisar requisitos técnicos
            technical_requirements = self._analyze_technical_requirements(requirements)
            
            # Gerar recomendações
            recommendations = self._generate_recommendations(
                domain_analysis,
                pattern_suggestions,
                technical_requirements
            )

            return {
                'domain_analysis': domain_analysis,
                'patterns': pattern_suggestions,
                'technical': technical_requirements,
                'recommendations': recommendations
            }

        except Exception as e:
            print(f"Erro na análise de requisitos: {str(e)}")
            return {}

    def _analyze_domain(self, requirements: Dict) -> Dict:
        """Analisa e identifica o domínio da aplicação"""
        domain_scores = {
            'business': 0,
            'data_analysis': 0,
            'workflow': 0
        }

        # Analisa features para identificar domínio
        features = requirements.get('features', {})
        for feature in features:
            # Pontuação para features de negócio
            if any(kw in str(feature).lower() for kw in ['crud', 'document', 'report']):
                domain_scores['business'] += 1
            
            # Pontuação para análise de dados
            if any(kw in str(feature).lower() for kw in ['dashboard', 'chart', 'analysis']):
                domain_scores['data_analysis'] += 1
            
            # Pontuação para workflow
            if any(kw in str(feature).lower() for kw in ['task', 'workflow', 'status']):
                domain_scores['workflow'] += 1

        # Identifica domínio principal
        primary_domain = max(domain_scores.items(), key=lambda x: x[1])
        
        return {
            'primary_domain': primary_domain[0],
            'domain_scores': domain_scores,
            'confidence': self._calculate_confidence(domain_scores)
        }

    def _identify_patterns(self, domain_analysis: Dict) -> List[Dict]:
        """Identifica padrões aplicáveis baseado no domínio"""
        patterns = []
        domain = domain_analysis['primary_domain']
        
        if domain in self.domain_patterns:
            domain_info = self.domain_patterns[domain]
            
            for pattern in domain_info['patterns']:
                patterns.append({
                    'name': pattern,
                    'relevance': 'high' if pattern in domain_info['common_features'] else 'medium',
                    'description': self._get_pattern_description(pattern),
                    'requirements': self._get_pattern_requirements(pattern)
                })

        return patterns

    def _analyze_technical_requirements(self, requirements: Dict) -> Dict:
        """Analisa requisitos técnicos"""
        return {
            'architecture': {
                'type': 'MVVM',
                'layers': ['Presentation', 'Business', 'Data'],
                'patterns': self._identify_technical_patterns(requirements)
            },
            'infrastructure': {
                'database': self._analyze_database_requirements(requirements),
                'api': self._analyze_api_requirements(requirements),
                'security': self._analyze_security_requirements(requirements)
            },
            'ui': {
                'layout': self._analyze_layout_requirements(requirements),
                'controls': self._identify_required_controls(requirements),
                'styling': self._analyze_styling_requirements(requirements)
            }
        }

    def _generate_recommendations(self, 
                                domain_analysis: Dict,
                                patterns: List[Dict],
                                technical: Dict) -> Dict:
        """Gera recomendações baseadas nas análises"""
        return {
            'architecture_recommendations': self._get_architecture_recommendations(
                domain_analysis,
                technical
            ),
            'ui_recommendations': self._get_ui_recommendations(
                patterns,
                technical
            ),
            'implementation_recommendations': self._get_implementation_recommendations(
                patterns,
                technical
            )
        }

    def _calculate_confidence(self, scores: Dict) -> float:
        """Calcula nível de confiança da análise"""
        total = sum(scores.values())
        if total == 0:
            return 0.0
        
        max_score = max(scores.values())
        return max_score / total if total > 0 else 0.0

    def _get_pattern_description(self, pattern: str) -> str:
        """Retorna descrição de um padrão"""
        descriptions = {
            'CRUD': 'Operações básicas de Create, Read, Update, Delete',
            'Dashboard': 'Visualização de dados em tempo real',
            'StateMachine': 'Gerenciamento de estados e transições',
            # Adicionar outros padrões conforme necessário
        }
        return descriptions.get(pattern, '')

    def _get_pattern_requirements(self, pattern: str) -> List[str]:
        """Retorna requisitos para implementar um padrão"""
        requirements = {
            'CRUD': ['EntityModel', 'DataRepository', 'CRUDService'],
            'Dashboard': ['DataService', 'ChartComponents', 'RefreshStrategy'],
            'StateMachine': ['StateManager', 'TransitionRules', 'StateValidator'],
            # Adicionar outros padrões conforme necessário
        }
        return requirements.get(pattern, [])

    def _identify_technical_patterns(self, requirements: Dict) -> List[str]:
        """Identifica padrões técnicos necessários"""
        patterns = ['Repository', 'Factory']
        
        if requirements.get('features', {}).get('real_time'):
            patterns.append('Observer')
            
        if requirements.get('features', {}).get('undo'):
            patterns.append('Command')
            
        return patterns

    def _analyze_database_requirements(self, requirements: Dict) -> Dict:
        """Analisa requisitos de banco de dados"""
        return {
            'type': 'relational',
            'features': ['transactions', 'foreign_keys'],
            'scalability': 'medium'
        }

    def _analyze_api_requirements(self, requirements: Dict) -> Dict:
        """Analisa requisitos de API"""
        return {
            'type': 'REST',
            'authentication': True,
            'features': ['CRUD', 'filtering', 'pagination']
        }

    def _analyze_security_requirements(self, requirements: Dict) -> Dict:
        """Analisa requisitos de segurança"""
        return {
            'authentication': 'required',
            'authorization': 'role_based',
            'data_protection': 'encryption'
        }

    def _analyze_layout_requirements(self, requirements: Dict) -> Dict:
        """Analisa requisitos de layout"""
        return {
            'type': 'responsive',
            'structure': 'grid',
            'regions': ['header', 'navigation', 'content', 'footer']
        }

    def _identify_required_controls(self, requirements: Dict) -> List[str]:
        """Identifica controles WPF necessários"""
        return ['DataGrid', 'TabControl', 'TreeView']

    def _analyze_styling_requirements(self, requirements: Dict) -> Dict:
        """Analisa requisitos de estilo"""
        return {
            'theme': 'modern',
            'color_scheme': 'professional',
            'branding': True
        }

    def save_analysis(self, analysis: Dict) -> None:
        """Salva análise para referência futura"""
        analysis_file = self.domain_patterns_path / f"{analysis['domain_analysis']['primary_domain']}.json"
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=4)

    def load_analysis(self, domain: str) -> Optional[Dict]:
        """Carrega análise salva"""
        analysis_file = self.domain_patterns_path / f"{domain}.json"
        if analysis_file.exists():
            with open(analysis_file, 'r') as f:
                return json.load(f)
        return None
        
    def _get_architecture_recommendations(self, domain_analysis: Dict, technical: Dict) -> List[str]:
            """Gera recomendações de arquitetura"""
            recommendations = []
            domain = domain_analysis['primary_domain']
        
            # Recomendações base para qualquer domínio
            recommendations.append("Implementar arquitetura MVVM")
            recommendations.append("Utilizar injeção de dependência")
        
            # Recomendações específicas por domínio
            if domain == 'business':
                recommendations.extend([
                    "Implementar Repository Pattern para acesso a dados",
                    "Usar Unit of Work para transações"
                ])
            elif domain == 'data_analysis':
                recommendations.extend([
                    "Implementar Observer Pattern para atualizações em tempo real",
                    "Usar Strategy Pattern para diferentes visualizações"
                ])
            elif domain == 'workflow':
                recommendations.extend([
                    "Implementar State Pattern para gerenciamento de workflow",
                    "Usar Command Pattern para operações reversíveis"
                ])

            return recommendations

    def _get_ui_recommendations(self, patterns: List[Dict], technical: Dict) -> List[str]:
        """Gera recomendações de UI"""
        recommendations = []
        
        # Recomendações baseadas nos padrões
        for pattern in patterns:
            if pattern['name'] == 'CRUD':
                recommendations.extend([
                    "Usar DataGrid para listagens",
                    "Implementar formulários de edição modais"
                ])
            elif pattern['name'] == 'Dashboard':
                recommendations.extend([
                    "Usar layout em grid para widgets",
                    "Implementar atualização assíncrona de dados"
                ])
    
        return recommendations

    def _get_implementation_recommendations(self, patterns: List[Dict], technical: Dict) -> List[str]:
        """Gera recomendações de implementação"""
        recommendations = []
        
        # Recomendações técnicas gerais
        recommendations.extend([
            "Usar async/await para operações assíncronas",
            "Implementar logging abrangente",
            "Adicionar tratamento de exceções global"
        ])

        # Recomendações específicas por padrão
        for pattern in patterns:
            if pattern['relevance'] == 'high':
                recommendations.append(f"Priorizar implementação do padrão {pattern['name']}")
    
        return recommendations