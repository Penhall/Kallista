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
        self._design_patterns_path = Path("templates/design_patterns")
        self._design_patterns_path.mkdir(parents=True, exist_ok=True)

    async def analyze_requirements(self, requirements: Dict) -> Dict[str, Any]:
        """Analisa requisitos e propõe soluções de UI/UX"""
        try:
            features = requirements.get('features', {})
            if isinstance(features, dict):
                feature_list = [{'name': k, **v} for k, v in features.items()]
            else:
                feature_list = features if isinstance(features, list) else []

            return {
                'user_flows': self._create_user_flows({'features': feature_list}),
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

    def _define_flow_steps(self, feature: Dict) -> List[Dict]:
        """Define os passos do fluxo de usuário"""
        try:
            steps = []
            actions = feature.get('actions', [])
            
            # Se actions é uma lista
            if isinstance(actions, list):
                for action in actions:
                    if isinstance(action, dict):
                        steps.append({
                            'action': action.get('name', 'unnamed action'),
                            'screen': action.get('screen', 'main'),
                            'inputs': action.get('inputs', []),
                            'feedback': action.get('feedback', 'visual'),
                            'next_steps': action.get('next_steps', [])
                        })
            # Se actions é um dicionário
            elif isinstance(actions, dict):
                for action_name, action_data in actions.items():
                    steps.append({
                        'action': action_name,
                        'screen': action_data.get('screen', 'main'),
                        'inputs': action_data.get('inputs', []),
                        'feedback': action_data.get('feedback', 'visual'),
                        'next_steps': action_data.get('next_steps', [])
                    })

            return steps
        except Exception as e:
            print(f"Erro ao definir passos do fluxo: {str(e)}")
            return []

    def _define_interactions(self, feature: Dict) -> List[Dict]:
        """Define interações para uma feature"""
        return [
            {
                'type': interaction.get('type', 'click'),
                'trigger': interaction.get('trigger', 'user'),
                'response': interaction.get('response', 'immediate'),
                'feedback': interaction.get('feedback', 'visual')
            }
            for interaction in feature.get('interactions', [])
        ]

    def _define_feedback_points(self, feature: Dict) -> List[Dict]:
        """Define pontos de feedback"""
        return [
            {
                'action': point.get('action', 'default'),
                'type': point.get('type', 'visual'),
                'message': point.get('message', ''),
                'duration': point.get('duration', 'short')
            }
            for point in feature.get('feedback_points', [])
        ]

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

    def _define_shortcuts(self, requirements: Dict) -> Dict:
        """Define atalhos de teclado"""
        return {
            'save': 'Ctrl+S',
            'new': 'Ctrl+N',
            'search': 'Ctrl+F'
        }

    def _define_input_masks(self, requirements: Dict) -> Dict:
        """Define máscaras de entrada"""
        return {
            'date': 'dd/MM/yyyy',
            'phone': '(99) 99999-9999',
            'currency': 'R$ #,##0.00'
        }

    def _define_confirmations(self, requirements: Dict) -> Dict:
        """Define diálogos de confirmação"""
        return {
            'delete': True,
            'save': False,
            'exit': True
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

    def _define_tab_order(self, requirements: Dict) -> List[str]:
        """Define ordem de tabulação"""
        return ['header', 'main-menu', 'content', 'footer']

    def _define_accessibility_shortcuts(self) -> Dict:
        """Define atalhos de acessibilidade"""
        return {
            'skip_to_content': 'Alt+1',
            'main_menu': 'Alt+2',
            'search': 'Alt+3'
        }

    def _define_reading_order(self, requirements: Dict) -> List[str]:
        """Define ordem de leitura"""
        return ['header', 'navigation', 'main', 'complementary', 'footer']

    def _generate_aria_descriptions(self, requirements: Dict) -> Dict:
        """Gera descrições ARIA"""
        return {
            'main': 'Main content area',
            'navigation': 'Main navigation menu',
            'search': 'Search input field'
        }

    def _check_contrast_ratios(self, requirements: Dict) -> Dict:
        """Verifica razões de contraste"""
        return {
            'text': 4.5,
            'large_text': 3.0,
            'ui_components': 3.0
        }

    def _define_text_sizing(self) -> Dict:
        """Define tamanhos de texto"""
        return {
            'base': '16px',
            'scale_factor': 1.25,
            'minimum': '12px'
        }

    def _analyze_color_blindness(self, requirements: Dict) -> Dict:
        """Analisa suporte para daltonismo"""
        return {
            'deuteranopia': True,
            'protanopia': True,
            'tritanopia': True
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

    def _define_layout_consistency(self) -> Dict:
        """Define consistência de layout"""
        return {
            'grid': '8px',
            'margins': '16px',
            'alignment': 'left'
        }

    def _define_content_grouping(self) -> Dict:
        """Define agrupamento de conteúdo"""
        return {
            'related_items': 'cards',
            'actions': 'toolbars',
            'information': 'sections'
        }

    def _define_spacing_guidelines(self) -> Dict:
        """Define diretrizes de espaçamento"""
        return {
            'component': '8px',
            'section': '24px',
            'page': '48px'
        }

    def _define_response_times(self) -> Dict:
        """Define tempos de resposta"""
        return {
            'immediate': '0.1s',
            'operation': '1.0s',
            'complex': '10.0s'
        }

    def _define_error_prevention(self) -> Dict:
        """Define prevenção de erros"""
        return {
            'validation': 'immediate',
            'confirmation': 'destructive',
            'undo': 'available'
        }

    def _define_error_recovery(self) -> Dict:
        """Define recuperação de erros"""
        return {
            'auto_save': True,
            'undo_steps': 10,
            'error_messages': 'clear'
        }

    def _define_efficiency_shortcuts(self) -> Dict:
        """Define atalhos de eficiência"""
        return {
            'keyboard': True,
            'context_menus': True,
            'quick_actions': True
        }

    def _define_smart_defaults(self) -> Dict:
        """Define padrões inteligentes"""
        return {
            'form_fields': True,
            'settings': True,
            'recent_items': True
        }

    def _define_automation_points(self) -> Dict:
        """Define pontos de automação"""
        return {
            'data_entry': True,
            'calculations': True,
            'validations': True
        }

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

    def _generate_error_messages(self, feature: Dict) -> Dict:
        """Gera mensagens de erro"""
        return {
            'required': 'This field is required',
            'invalid': 'Please enter a valid value',
            'exists': 'This value already exists'
        }

    def _validate_requirements(self, requirements: Dict) -> Dict:
        """Valida requisitos contra boas práticas de UI/UX"""
        issues = []
        warnings = []

        # Validações básicas
        if not requirements.get('features'):
            warnings.append("No features specified")

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }

    def save_design_pattern(self, pattern: Dict) -> None:
        """Salva um padrão de design para reuso"""
        pattern_file = self._design_patterns_path / f"{pattern['name']}.json"
        with open(pattern_file, 'w') as f:
            json.dump(pattern, f, indent=4)

    def load_design_pattern(self, pattern_name: str) -> Optional[Dict]:
        """Carrega um padrão de design"""
        pattern_file = self._design_patterns_path / f"{pattern_name}.json"
        if pattern_file.exists():
            with open(pattern_file, 'r') as f:
                return json.load(f)
        return None