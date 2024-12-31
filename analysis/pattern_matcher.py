# analysis/pattern_matcher.py
from typing import Dict, List, Any, Optional
from pathlib import Path
import json

class PatternMatcher:
    def __init__(self):
        self.patterns_path = Path("templates/patterns")
        self.patterns_path.mkdir(parents=True, exist_ok=True)
        
        # Base de conhecimento de padrões
        self.patterns_db = {
            'architectural': {
                'mvvm': {
                    'name': 'MVVM',
                    'description': 'Model-View-ViewModel pattern for WPF',
                    'use_cases': ['user_interface', 'data_binding', 'state_management'],
                    'components': ['ViewModels', 'Models', 'Commands', 'DataBinding'],
                    'examples': ['Dashboard', 'CRUD', 'Forms']
                },
                'repository': {
                    'name': 'Repository',
                    'description': 'Data access abstraction',
                    'use_cases': ['data_access', 'crud_operations'],
                    'components': ['Repositories', 'DbContext', 'Entities'],
                    'examples': ['UserRepository', 'ProductRepository']
                },
                'service_locator': {
                    'name': 'Service Locator',
                    'description': 'Central registry for application services',
                    'use_cases': ['dependency_injection', 'service_management'],
                    'components': ['IServiceLocator', 'ServiceRegistry'],
                    'examples': ['ApplicationServices', 'DIContainer']
                },
                'unit_of_work': {
                    'name': 'Unit of Work',
                    'description': 'Manage database transactions and changes',
                    'use_cases': ['transaction_management', 'data_consistency'],
                    'components': ['IUnitOfWork', 'TransactionScope'],
                    'examples': ['OrderProcessing', 'BatchUpdates']
                }
            },
            
            'ui': {
                'master_detail': {
                    'name': 'Master-Detail',
                    'description': 'Two-panel interface pattern',
                    'use_cases': ['data_exploration', 'crud_operations'],
                    'components': ['ListView', 'DetailView', 'Navigation'],
                    'examples': ['Email Client', 'Document Manager']
                },
                'dashboard': {
                    'name': 'Dashboard',
                    'description': 'Multi-panel information display',
                    'use_cases': ['data_visualization', 'monitoring'],
                    'components': ['Widgets', 'Charts', 'Cards'],
                    'examples': ['Analytics Dashboard', 'Admin Panel']
                },
                'wizard': {
                    'name': 'Wizard Pattern',
                    'description': 'Step-by-step user interface flow',
                    'use_cases': ['complex_input', 'guided_setup'],
                    'components': ['WizardControl', 'StepNavigation'],
                    'examples': ['Installation', 'Registration']
                },
                'document_workspace': {
                    'name': 'Document Workspace',
                    'description': 'MDI-style document management',
                    'use_cases': ['document_editing', 'multi_window'],
                    'components': ['DocumentHost', 'Workspace'],
                    'examples': ['TextEditor', 'DiagramEditor']
                },
                'ribbon': {
                    'name': 'Ribbon Interface',
                    'description': 'Office-style command organization',
                    'use_cases': ['command_rich', 'categorized_interface'],
                    'components': ['RibbonControl', 'TabGroups'],
                    'examples': ['ProductivityTools', 'ContentCreation']
                }
            },'interaction': {
                'command': {
                    'name': 'Command Pattern',
                    'description': 'Encapsulate operations as objects',
                    'use_cases': ['undo_redo', 'action_queue'],
                    'components': ['ICommand', 'CommandManager'],
                    'examples': ['TextEditor', 'Drawing App']
                },
                'observer': {
                    'name': 'Observer Pattern',
                    'description': 'Event-based communication',
                    'use_cases': ['real_time_updates', 'loose_coupling'],
                    'components': ['EventAggregator', 'MessageBus'],
                    'examples': ['Stock Ticker', 'Chat Application']
                },
                'mediator': {
                    'name': 'Mediator Pattern',
                    'description': 'Centralized component communication',
                    'use_cases': ['decoupled_communication', 'event_coordination'],
                    'components': ['IMediator', 'EventAggregator'],
                    'examples': ['ChatRoom', 'WorkflowCoordination']
                },
                'state': {
                    'name': 'State Pattern',
                    'description': 'Manage component state transitions',
                    'use_cases': ['workflow_management', 'complex_state'],
                    'components': ['IState', 'StateManager'],
                    'examples': ['DocumentFlow', 'ProcessManagement']
                }
            },
            'wpf_specific': {
                'mvvm_toolkit': {
                    'name': 'CommunityToolkit.Mvvm',
                    'description': 'Modern MVVM implementation with source generators',
                    'use_cases': [
                        'modern_mvvm',
                        'source_generation',
                        'observable_properties',
                        'commands',
                        'messaging'
                    ],
                    'components': [
                        'ObservableObject',
                        'RelayCommand',
                        'IMessenger',
                        'ObservableProperty',
                        'NotifyPropertyChangedFor'
                    ],
                    'features': {
                        'source_generators': [
                            'ObservableProperty',
                            'RelayCommand',
                            'INotifyPropertyChanged'
                        ],
                        'messaging': [
                            'WeakReferenceMessenger',
                            'StrongReferenceMessenger'
                        ],
                        'commands': [
                            'RelayCommand',
                            'AsyncRelayCommand',
                            'IRelayCommand'
                        ]
                    },
                    'examples': [
                        'MainViewModel : ObservableObject',
                        '[ObservableProperty] private string _name;',
                        '[RelayCommand] private Task SaveAsync()',
                        'WeakReferenceMessenger.Default.Send(new MessageType())'
                    ]
                },
                'behavior': {
                    'name': 'Behavior Pattern',
                    'description': 'Reusable UI behavior components',
                    'use_cases': ['interactive_behavior', 'ui_reuse'],
                    'components': ['Behavior', 'Interaction'],
                    'examples': ['DragDrop', 'InputValidation']
                },
                'value_converter': {
                    'name': 'Value Converter',
                    'description': 'Data conversion for UI binding',
                    'use_cases': ['data_conversion', 'formatting'],
                    'components': ['IValueConverter', 'Converter'],
                    'examples': ['DateFormat', 'BooleanVisibility']
                },
                'template_selector': {
                    'name': 'Template Selector',
                    'description': 'Dynamic template selection',
                    'use_cases': ['dynamic_ui', 'conditional_display'],
                    'components': ['DataTemplateSelector', 'Templates'],
                    'examples': ['MessageTypes', 'ContentTypes']
                }
            }
        }
        
        
    def match_patterns(self, requirements: Dict) -> Dict[str, Any]:
        """Encontra padrões que melhor se adequam aos requisitos"""
        try:
            matches = {
                'architectural': self._match_architectural_patterns(requirements),
                'ui': self._match_ui_patterns(requirements),
                'interaction': self._match_interaction_patterns(requirements),
                'wpf_specific': self._match_wpf_patterns(requirements)
            }
            
            scored_matches = self._score_matches(matches, requirements)
            recommendations = self._generate_pattern_recommendations(scored_matches)
            implementation_guide = self._create_wpf_implementation_guide(scored_matches)
            
            return {
                'matches': scored_matches,
                'recommendations': recommendations,
                'implementation_guide': implementation_guide
            }
            
        except Exception as e:
            print(f"Erro no pattern matching: {str(e)}")
            return {}

    def _match_architectural_patterns(self, requirements: Dict) -> List[Dict]:
        """Identifica padrões arquiteturais adequados"""
        matches = []
        features = requirements.get('features', {})
        
        for pattern_id, pattern in self.patterns_db['architectural'].items():
            score = 0
            reasons = []
            
            for use_case in pattern['use_cases']:
                if self._requirement_matches_use_case(features, use_case):
                    score += 1
                    reasons.append(f"Supports {use_case}")
            
            if score > 0:
                matches.append({
                    'pattern': pattern,
                    'score': score,
                    'reasons': reasons
                })
        
        return sorted(matches, key=lambda x: x['score'], reverse=True)

    def _match_ui_patterns(self, requirements: Dict) -> List[Dict]:
        """Identifica padrões de UI adequados"""
        matches = []
        features = requirements.get('features', {})
        
        for pattern_id, pattern in self.patterns_db['ui'].items():
            score = 0
            reasons = []
            
            if self._requires_components(features, pattern['components']):
                score += 2
                reasons.append("Required components match")
            
            for use_case in pattern['use_cases']:
                if self._requirement_matches_use_case(features, use_case):
                    score += 1
                    reasons.append(f"Supports {use_case}")
            
            if score > 0:
                matches.append({
                    'pattern': pattern,
                    'score': score,
                    'reasons': reasons
                })
        
        return sorted(matches, key=lambda x: x['score'], reverse=True)

    def _match_interaction_patterns(self, requirements: Dict) -> List[Dict]:
        """Identifica padrões de interação adequados"""
        matches = []
        features = requirements.get('features', {})
        
        for pattern_id, pattern in self.patterns_db['interaction'].items():
            score = 0
            reasons = []
            
            for use_case in pattern['use_cases']:
                if self._requirement_matches_use_case(features, use_case):
                    score += 1
                    reasons.append(f"Supports {use_case}")
            
            if score > 0:
                matches.append({
                    'pattern': pattern,
                    'score': score,
                    'reasons': reasons
                })
        
        return sorted(matches, key=lambda x: x['score'], reverse=True)

    def _match_wpf_patterns(self, requirements: Dict) -> List[Dict]:
        """Identifica padrões específicos de WPF adequados"""
        matches = []
        features = requirements.get('features', {})
        ui_requirements = requirements.get('ui', {})
        
        for pattern_id, pattern in self.patterns_db['wpf_specific'].items():
            score = 0
            reasons = []
            
            if self._requires_wpf_features(features, pattern):
                score += 2
                reasons.append("WPF features match")
            
            for use_case in pattern.get('use_cases', []):
                if self._requirement_matches_use_case(features, use_case):
                    score += 1
                    reasons.append(f"Supports {use_case}")
            
            if self._matches_ui_requirements(ui_requirements, pattern):
                score += 1
                reasons.append("UI requirements match")
            
            if score > 0:
                matches.append({
                    'pattern': pattern,
                    'score': score,
                    'reasons': reasons
                })
        
        return sorted(matches, key=lambda x: x['score'], reverse=True)
        
    def _score_matches(self, matches: Dict, requirements: Dict) -> Dict:
        """Calcula pontuação final dos matches"""
        scored = {}
        
        for category, category_matches in matches.items():
            scored[category] = []
            for match in category_matches:
                final_score = self._calculate_final_score(match, requirements)
                scored[category].append({
                    **match,
                    'final_score': final_score
                })
        
        return scored

    def _generate_pattern_recommendations(self, scored_matches: Dict) -> Dict[str, List[str]]:
        """Gera recomendações baseadas nos matches"""
        recommendations = {
            'architectural': [],
            'ui': [],
            'interaction': [],
            'wpf_specific': []
        }
        
        for category, matches in scored_matches.items():
            if matches:
                top_matches = matches[:2]  # Pega os 2 melhores matches
                for match in top_matches:
                    pattern = match['pattern']
                    recommendations[category].append(
                        f"Use {pattern['name']}: {pattern['description']}"
                    )
                    if pattern.get('examples'):
                        recommendations[category].append(
                            f"Example: {pattern['examples'][0]}"
                        )

        # Adiciona recomendações específicas do MVVM Toolkit
        recommendations['wpf_specific'].extend(
            self._get_mvvm_toolkit_recommendations(scored_matches)
        )
        
        return recommendations

    def _get_mvvm_toolkit_recommendations(self, scored_matches: Dict) -> List[str]:
        """Gera recomendações específicas para uso do CommunityToolkit.MVVM"""
        toolkit_matches = [
            m for m in scored_matches.get('wpf_specific', [])
            if m['pattern']['name'] == 'CommunityToolkit.Mvvm'
        ]
        
        if not toolkit_matches:
            return []

        recommendations = [
            "Use [ObservableProperty] instead of manual INotifyPropertyChanged",
            "Implement RelayCommand with [RelayCommand] attribute",
            "Utilize WeakReferenceMessenger for loose coupling",
            "Configure source generators in .csproj",
            "Use ObservableValidator for input validation"
        ]

        return recommendations

    def _create_wpf_implementation_guide(self, scored_matches: Dict) -> Dict:
        """Cria guia de implementação específico para WPF"""
        guide = {
            'setup': self._get_wpf_setup_steps(),
            'patterns': self._get_pattern_implementation_steps(scored_matches),
            'mvvm_toolkit': {
                'base_setup': [
                    "Enable nullable reference types",
                    "Add Microsoft.Extensions.DependencyInjection",
                    "Configure MVVM Toolkit source generators"
                ],
                'code_examples': self._get_mvvm_code_examples()
            },
            'best_practices': self._get_wpf_best_practices()
        }
        
        return guide

    def _get_wpf_setup_steps(self) -> List[str]:
        """Retorna passos de setup para WPF"""
        return [
            "1. Install CommunityToolkit.Mvvm NuGet package",
            "2. Configure source generators in .csproj",
            "3. Setup base ViewModelBase class",
            "4. Configure dependency injection",
            "5. Setup navigation service",
            "6. Configure messaging system"
        ]

    def _get_pattern_implementation_steps(self, scored_matches: Dict) -> Dict[str, List[str]]:
        """Gera passos de implementação para os padrões selecionados"""
        steps = {}
        
        for category, matches in scored_matches.items():
            if matches:
                top_pattern = matches[0]['pattern']
                steps[category] = [
                    f"1. Implement {top_pattern['name']}",
                    f"2. Setup required components: {', '.join(top_pattern['components'])}",
                    "3. Configure interfaces and base classes",
                    "4. Implement core functionality",
                    "5. Add error handling and logging",
                    "6. Write unit tests"
                ]
        
        return steps
    
    def _get_wpf_best_practices(self) -> List[str]:
        """Retorna melhores práticas para WPF"""
        return [
            "Use source generators instead of runtime reflection",
            "Prefer ObservableProperty over manual property changed",
            "Use RelayCommand attributes for commands",
            "Implement INavigationAware when needed",
            "Use WeakReferenceMessenger by default",
            "Follow naming conventions for generated code",
            "Implement proper disposal patterns",
            "Use async/await for long-running operations",
            "Implement proper validation",
            "Use resource dictionaries for styles"
        ]

    def _get_mvvm_code_examples(self) -> Dict[str, str]:
        """Retorna exemplos de código MVVM"""
        return {
            'view_model': '''
public partial class MainViewModel : ObservableObject
{
    [ObservableProperty]
    private string? name;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(FullName))]
    private string? lastName;

    public string FullName => $"{Name} {LastName}";

    [RelayCommand]
    private async Task SaveAsync()
    {
        // Implementation
    }
}
''',
            'messaging': '''
// Sender
WeakReferenceMessenger.Default.Send(new UserMessage(user));

// Receiver
WeakReferenceMessenger.Default.Register<UserMessage>(this, (r, m) => 
{
    // Handle message
});
''',
            'validation': '''
public partial class UserViewModel : ObservableValidator
{
    [ObservableProperty]
    [NotifyDataErrorInfo]
    [Required(ErrorMessage = "Name is required")]
    [MinLength(2, ErrorMessage = "Name must be at least 2 characters")]
    private string? name;

    [ObservableProperty]
    [NotifyDataErrorInfo]
    [EmailAddress(ErrorMessage = "Invalid email format")]
    private string? email;
}
'''
        }

    def _requirement_matches_use_case(self, features: Dict, use_case: str) -> bool:
        """Verifica se um requisito corresponde a um caso de uso"""
        if not features:
            return False
            
        use_case_keywords = use_case.split('_')
        features_str = json.dumps(features).lower()
        
        return all(keyword in features_str for keyword in use_case_keywords)

    def _requires_components(self, features: Dict, components: List[str]) -> bool:
        """Verifica se os componentes necessários estão nos requisitos"""
        if not features:
            return False
            
        features_str = json.dumps(features).lower()
        return any(
            component.lower() in features_str 
            for component in components
        )

    def _requires_wpf_features(self, features: Dict, pattern: Dict) -> bool:
        """Verifica necessidades específicas de WPF"""
        if not features:
            return False
        
        # Obtém features do padrão
        pattern_features = pattern.get('features', {})
        if isinstance(pattern_features, dict):
            # Se features é um dicionário, flatten ele
            feature_list = []
            for feature_group in pattern_features.values():
                if isinstance(feature_group, list):
                    feature_list.extend(feature_group)
        else:
            feature_list = pattern_features if isinstance(pattern_features, list) else []
        
        features_str = json.dumps(features).lower()
        return any(
            feature.lower() in features_str 
            for feature in feature_list
        )

    def _matches_ui_requirements(self, ui_requirements: Dict, pattern: Dict) -> bool:
        """Verifica compatibilidade com requisitos de UI"""
        if not ui_requirements:
            return False
        
        ui_str = json.dumps(ui_requirements).lower()
        pattern_str = json.dumps(pattern).lower()
        
        return any(
            keyword in ui_str 
            for keyword in pattern_str.split()
        )

    def _calculate_final_score(self, match: Dict, requirements: Dict) -> float:
        """Calcula pontuação final considerando o contexto"""
        base_score = match['score']
        
        complexity = requirements.get('metadata', {}).get('complexity', 'medium')
        if complexity == 'high':
            base_score *= 1.2
        elif complexity == 'low':
            base_score *= 0.8
        
        return round(base_score, 2)

    def save_pattern(self, pattern: Dict) -> None:
        """Salva um novo padrão na base de conhecimento"""
        pattern_file = self.patterns_path / f"{pattern['name'].lower()}.json"
        with open(pattern_file, 'w') as f:
            json.dump(pattern, f, indent=4)

    def load_pattern(self, pattern_name: str) -> Optional[Dict]:
        """Carrega um padrão da base de conhecimento"""
        pattern_file = self.patterns_path / f"{pattern_name.lower()}.json"
        if pattern_file.exists():
            with open(pattern_file, 'r') as f:
                return json.load(f)
        return None