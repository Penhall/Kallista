# tasks/code_generation_task.py
from typing import Dict, Any, List
from pathlib import Path
from .base_task import BaseTask

class CodeGenerationTask(BaseTask):
    def __init__(self, name: str, description: str, template_data: Dict[str, Any]):
        super().__init__(name, description)
        self.template_data = template_data
        self.metadata['type'] = 'code_generation'
        self.output_files: List[str] = []

    async def validate(self, context: Dict[str, Any]) -> bool:
        """Valida se os dados do template estão completos"""
        required_fields = ['template_type', 'output_path', 'parameters']
        return all(field in self.template_data for field in required_fields)

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Executa a geração de código"""
        self.start()
        try:
            generator = context.get('code_generator')
            if not generator:
                raise ValueError("Code generator not found in context")

            template_type = self.template_data['template_type']
            output_path = self.template_data['output_path']
            parameters = self.template_data['parameters']

            if template_type == 'view':
                code = await self._generate_view(generator, parameters)
            elif template_type == 'viewmodel':
                code = await self._generate_viewmodel(generator, parameters)
            elif template_type == 'model':
                code = await self._generate_model(generator, parameters)
            else:
                raise ValueError(f"Unknown template type: {template_type}")

            # Salva o código gerado
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(code)
            self.output_files.append(str(output_file))

            result = {
                'generated_files': self.output_files,
                'template_type': template_type,
                'parameters': parameters
            }
            self.complete(result)
            return result

        except Exception as e:
            self.fail(str(e))
            raise

    async def _generate_view(self, generator, parameters: Dict[str, Any]) -> str:
        """Gera código para uma View"""
        view_data = {
            'name': parameters.get('name'),
            'controls': parameters.get('controls', []),
            'resources': parameters.get('resources', {}),
            'bindings': parameters.get('bindings', {})
        }
        return generator.generate_wpf_view(view_data)

    async def _generate_viewmodel(self, generator, parameters: Dict[str, Any]) -> str:
        """Gera código para um ViewModel"""
        vm_data = {
            'name': parameters.get('name'),
            'properties': parameters.get('properties', []),
            'commands': parameters.get('commands', []),
            'dependencies': parameters.get('dependencies', [])
        }
        return generator.generate_view_model(vm_data)

    async def _generate_model(self, generator, parameters: Dict[str, Any]) -> str:
        """Gera código para um Model"""
        model_data = {
            'name': parameters.get('name'),
            'properties': parameters.get('properties', []),
            'validations': parameters.get('validations', []),
            'relationships': parameters.get('relationships', [])
        }
        return generator.generate_code('model.cs', model_data)