# tools/wpf/project_generator.py
from pathlib import Path
from typing import Dict, Any
from .generators.template_manager import TemplateManager

class WPFProjectGenerator:
    def __init__(self):
        self.template_manager = TemplateManager()
        self.output_path = Path("output")
        self.output_path.mkdir(exist_ok=True)

    async def generate_project(self, project_spec: Dict) -> Dict:
        """Gera a estrutura do projeto WPF"""
        try:
            project_name = project_spec['metadata']['name']
            output_path = Path("output") / project_name
            
            # Criar estrutura de diretórios
            directories = [
                'Views',
                'ViewModels',
                'Models',
                'Services/Navigation',
                'Styles',
                'Properties'
            ]
            
            for dir_name in directories:
                (output_path / dir_name).mkdir(parents=True, exist_ok=True)
    
            # Gerar arquivos base
            base_files = self.template_manager.get_base_templates(project_name)
            
            # Gerar cada arquivo
            files_generated = []
            for file_path, content in base_files.items():
                full_path = output_path / file_path
                full_path.parent.mkdir(exist_ok=True)
                full_path.write_text(content, encoding='utf-8')
                files_generated.append(file_path)
    
            return {
                'status': 'success',
                'path': str(output_path),
                'files_generated': files_generated,
                'project_spec': project_spec  # Retornando para uso pelos agentes
            }
    
        except Exception as e:
            print(f"Erro na geração do projeto: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }