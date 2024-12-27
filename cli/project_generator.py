# cli/project_generator.py

from integrations.visual_studio.code_generation import CodeGenerator, CodeTemplateType
from integrations.visual_studio.code_generator import VSCodeGenerator
from pathlib import Path
import logging
import json

class ProjectCodeGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = {
            'templates_path': 'templates/code',
            'output_path': 'output'
        }
        self.code_generator = CodeGenerator(self.config)
        self.vs_generator = VSCodeGenerator()

    async def generate_project(self, project_structure, agent_output):
        """
        Gera o projeto baseado na estrutura definida pelos agentes
        
        Args:
            project_structure: Especificações do projeto
            agent_output: Output do LLM contendo detalhes da implementação
        """
        try:
            project_name = project_structure['metadata']['name']
            print(f"\nGerando projeto: {project_name}")

            # Parse da saída do LLM para estrutura de projeto
            implementation_details = self._parse_agent_output(agent_output)

            # Gerar estrutura baseada na interpretação do agente
            await self._generate_project_structure(project_name, implementation_details)

            print(f"Projeto gerado com sucesso em: {self.config['output_path']}/{project_name}")
            return True

        except Exception as e:
            self.logger.error(f"Erro ao gerar projeto: {str(e)}")
            return False

    def _parse_agent_output(self, agent_output):
        """
        Converte o output do LLM em uma estrutura de implementação
        """
        try:
            # TODO: Implementar parser mais robusto
            # Por enquanto assume que o agente retorna JSON válido
            return json.loads(agent_output)
        except:
            # Se não for JSON, tenta extrair informações do texto
            self.logger.warning("Falha ao parse JSON, processando texto...")
            return self._extract_implementation_from_text(agent_output)

    async def _generate_project_structure(self, project_name, implementation):
        """
        Gera a estrutura do projeto baseada na interpretação do agente
        """
        base_path = Path(self.config['output_path']) / project_name

        # Criar estrutura de diretórios
        for folder in implementation.get('folders', []):
            (base_path / folder).mkdir(parents=True, exist_ok=True)

        # Gerar cada componente especificado pelo agente
        for component in implementation.get('components', []):
            if component['type'] == 'model':
                await self._generate_model(component)
            elif component['type'] == 'viewmodel':
                await self._generate_viewmodel(component)
            elif component['type'] == 'view':
                await self._generate_view(component)
            elif component['type'] == 'service':
                await self._generate_service(component)

    def _extract_implementation_from_text(self, text):
        """
        Extrai especificações de implementação do texto do agente
        """
        # TODO: Implementar extração mais robusta
        # Por enquanto retorna uma estrutura básica
        return {
            'folders': ['Models', 'ViewModels', 'Views', 'Services'],
            'components': []
        }

    async def _generate_model(self, model_spec):
        await self.code_generator.generate_code(
            CodeTemplateType.MODEL,
            "basic_model",
            model_spec
        )

    async def _generate_viewmodel(self, vm_spec):
        await self.code_generator.generate_code(
            CodeTemplateType.VIEW_MODEL,
            "basic_viewmodel",
            vm_spec
        )

    async def _generate_view(self, view_spec):
        await self.code_generator.generate_code(
            CodeTemplateType.VIEW,
            "basic_view",
            view_spec
        )

    async def _generate_service(self, service_spec):
        await self.code_generator.generate_code(
            CodeTemplateType.SERVICE,
            "basic_service",
            service_spec
        )
        