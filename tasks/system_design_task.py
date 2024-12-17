# tasks/system_design_task.py
from typing import Dict, Any
from .base_task import BaseTask

class SystemDesignTask(BaseTask):
    def __init__(self, name: str, description: str, requirements: Dict[str, Any]):
        super().__init__(name, description)
        self.requirements = requirements
        self.metadata['type'] = 'system_design'

    async def validate(self, context: Dict[str, Any]) -> bool:
        """Valida se os requisitos estão completos"""
        required_fields = ['scope', 'constraints', 'components']
        return all(field in self.requirements for field in required_fields)

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Executa o design do sistema"""
        self.start()
        try:
            # Implementação do design do sistema
            design = {
                'architecture': self._design_architecture(),
                'components': self._design_components(),
                'interfaces': self._design_interfaces(),
                'data_model': self._design_data_model()
            }
            self.complete(design)
            return design
        except Exception as e:
            self.fail(str(e))
            raise

    def _design_architecture(self) -> Dict[str, Any]:
        """Define a arquitetura do sistema"""
        return {
            'pattern': 'MVVM',
            'layers': ['Presentation', 'Business', 'Data'],
            'communication': 'Message-Based'
        }

    def _design_components(self) -> Dict[str, Any]:
        """Define os componentes do sistema"""
        return {
            'views': self._extract_views(),
            'viewmodels': self._extract_viewmodels(),
            'models': self._extract_models(),
            'services': self._extract_services()
        }

    def _design_interfaces(self) -> Dict[str, Any]:
        """Define as interfaces do sistema"""
        return {
            'api': self._design_api_interfaces(),
            'ui': self._design_ui_interfaces(),
            'data': self._design_data_interfaces()
        }

    def _design_data_model(self) -> Dict[str, Any]:
        """Define o modelo de dados"""
        return {
            'entities': self._extract_entities(),
            'relationships': self._extract_relationships(),
            'validation_rules': self._extract_validation_rules()
        }

    def _extract_views(self) -> list:
        return self.requirements.get('views', [])

    def _extract_viewmodels(self) -> list:
        return [f"{view}ViewModel" for view in self._extract_views()]

    def _extract_models(self) -> list:
        return self.requirements.get('models', [])

    def _extract_services(self) -> list:
        return self.requirements.get('services', [])

    def _design_api_interfaces(self) -> Dict[str, Any]:
        return {
            'endpoints': self.requirements.get('api_endpoints', []),
            'methods': ['GET', 'POST', 'PUT', 'DELETE'],
            'authentication': self.requirements.get('authentication_type', 'JWT')
        }

    def _design_ui_interfaces(self) -> Dict[str, Any]:
        return {
            'layouts': self.requirements.get('layouts', []),
            'components': self.requirements.get('ui_components', []),
            'themes': self.requirements.get('themes', ['Light', 'Dark'])
        }

    def _design_data_interfaces(self) -> Dict[str, Any]:
        return {
            'repositories': [f"I{model}Repository" for model in self._extract_models()],
            'unit_of_work': 'IUnitOfWork',
            'data_context': 'IDataContext'
        }

    def _extract_entities(self) -> list:
        return self.requirements.get('entities', [])

    def _extract_relationships(self) -> list:
        return self.requirements.get('relationships', [])

    def _extract_validation_rules(self) -> Dict[str, Any]:
        return self.requirements.get('validation_rules', {})