# agents/specialized/uiux_agent.py
from crewai import Agent
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
from datetime import datetime

class UiUxAgent(Agent):
    def __init__(self, llm):
        super().__init__(
            role='UI/UX Specialist',
            goal='Design and implement user interfaces with focus on usability and accessibility',
            backstory="""You are an experienced UI/UX designer specialized in desktop 
            applications. You have deep knowledge of user behavior, accessibility 
            standards, and modern design patterns. You excel at creating intuitive 
            and efficient user experiences.""",
            llm=llm
        )
        self.design_patterns_path = Path("templates/design_patterns")
        self.design_patterns_path.mkdir(parents=True, exist_ok=True)

    async def analyze_requirements(self, requirements: Dict) -> Dict[str, Any]:
        """Analisa requisitos e propõe soluções de UI/UX"""
        try:
            return {
                'user_flows': self._create_user_flows(requirements),
                'interaction_patterns': self._define_interaction_patterns(requirements),
                'accessibility': self._analyze_accessibility(requirements),
                'usability_guidelines': self._create_usability_guidelines(requirements),
                'validation': self._validate_requirements(requirements)
            }
        except Exception as e:
            raise Exception(f"Erro na análise de requisitos: {str(e)}")

    def _create_user_flows(self, requirements: Dict) -> List[Dict]:
        """Cria fluxos de usuário baseados nos requisitos"""
        flows = []
        for feature in requirements.get('features', []):
            flow = {
                'feature': feature['name'],
                'steps': self._define_flow_steps(feature),
                'interactions': self._define_interactions(feature),
                'feedback_points': self._define_feedback_points(feature),
                'error_handling': self._define_error_handling(feature)
            }
            flows.append(flow)
        return flows

    def _define_interaction_patterns(self, requirements: Dict) -> Dict:
        """Define padrões de interação para a interface"""
        return {
            'navigation': {
                'pattern': requirements.get('navigation_type', 'hierarchical'),
                'menu_style': requirements.get('menu_style', 'ribbon'),
                'shortcuts': self._define_shortcuts(requirements)
            },
            'data_entry': {
                'validation_feedback': 'immediate',
                'auto_save': requirements.get('auto_save', True),
                'input_masks': self._define_input_masks(requirements)
            },
            'feedback': {
                'loading_indicators': True,
                'success_messages': True,
                'error_messages': True,
                'confirmation_dialogs': self._define_confirmations(requirements)
            }
        }

    def _analyze_accessibility(self, requirements: Dict) -> Dict:
        """Analisa e define requisitos de acessibilidade"""
        return {
            'keyboard_navigation': {
                'enabled': True,
                'tab_order': self._define_tab_order(requirements),
                'shortcuts': self._define_accessibility_shortcuts()
            },
            'screen_readers': {
                'aria_labels': True,
                'reading_order': self._define_reading_order(requirements),
                'descriptions': self._generate_aria_descriptions(requirements)
            },
            'visual': {
                'contrast_ratios': self._check_contrast_ratios(requirements),
                'text_sizing': self._define_text_sizing(),
                'color_blindness': self._analyze_color_blindness(requirements)
            }
        }

    def _create_usability_guidelines(self, requirements: Dict) -> Dict:
        """Cria diretrizes de usabilidade"""
        return {
            'layout': {
                'consistency': self._define_layout_consistency(),
                'grouping': self._define_content_grouping(),
                'spacing': self._define_spacing_guidelines()
            },
            'feedback': {
                'response_time': self._define_response_times(),
                'error_prevention': self._define_error_prevention(),
                'recovery': self._define_error_recovery()
            },
            'efficiency': {
                'shortcuts': self._define_efficiency_shortcuts(),
                'defaults': self._define_smart_defaults(),
                'automation': self._define_automation_points()
            }
        }

    def _validate_requirements(self, requirements: Dict) -> Dict:
        """Valida requisitos contra boas práticas de UI/UX"""
        issues = []
        recommendations = []

        # Validar complexidade de navegação
        nav_depth = self._analyze_navigation_depth(requirements)
        if nav_depth > 3:
            issues.append("Navegação muito profunda")
            recommendations.append("Considere simplificar a estrutura de navegação")

        # Validar densidade de informação
        info_density = self._analyze_information_density(requirements)
        if info_density > 0.8:
            issues.append("Alta densidade de informação")
            recommendations.append("Divida informações em múltiplas views")

        # Validar consistência
        consistency_issues = self._check_consistency(requirements)
        issues.extend(consistency_issues)

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'recommendations': recommendations,
            'metrics': {
                'navigation_depth': nav_depth,
                'information_density': info_density,
                'consistency_score': self._calculate_consistency_score(requirements)
            }
        }

    def _define_flow_steps(self, feature: Dict) -> List[Dict]:
        """Define os passos do fluxo de usuário"""
        steps = []
        for action in feature.get('actions', []):
            steps.append({
                'action': action['name'],
                'screen': action.get('screen'),
                'inputs': action.get('inputs', []),
                'feedback': action.get('feedback', 'visual'),
                'next_steps': action.get('next_steps', [])
            })
        return steps

    def _define_interactions(self, feature: Dict) -> List[Dict]:
        """Define interações para uma feature"""
        return [
            {
                'type': interaction['type'],
                'trigger': interaction['trigger'],
                'response': interaction['response'],
                'feedback': interaction.get('feedback', 'immediate')
            }
            for interaction in feature.get('interactions', [])
        ]

    def _define_feedback_points(self, feature: Dict) -> List[Dict]:
        """Define pontos de feedback"""
        return [
            {
                'action': point['action'],
                'type': point['type'],
                'message': point['message'],
                'duration': point.get('duration', 'short')
            }
            for point in feature.get('feedback_points', [])
        ]

    def _define_error_handling(self, feature: Dict) -> Dict:
        """Define tratamento de erros"""
        return {
            'validation': {
                'timing': 'immediate',
                'style': 'inline',
                'messages': self._generate_error_messages(feature)
            },
            'recovery': {
                'auto_save': True,
                'undo': True,
                'suggestions': True
            }
        }

    async def generate_style_guide(self, requirements: Dict) -> Dict:
        """Gera guia de estilo baseado nos requisitos"""
        return {
            'colors': self._generate_color_palette(requirements),
            'typography': self._define_typography(),
            'spacing': self._define_spacing_system(),
            'components': self._define_component_styles(),
            'interactions': self._define_interaction_styles()
        }

    def save_design_pattern(self, pattern: Dict) -> None:
        """Salva um padrão de design para reuso"""
        pattern_file = self.design_patterns_path / f"{pattern['name']}.json"
        with open(pattern_file, 'w') as f:
            json.dump(pattern, f, indent=4)

    def load_design_pattern(self, pattern_name: str) -> Optional[Dict]:
        """Carrega um padrão de design"""
        pattern_file = self.design_patterns_path / f"{pattern_name}.json"
        if pattern_file.exists():
            with open(pattern_file, 'r') as f:
                return json.load(f)
        return None