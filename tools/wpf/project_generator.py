# tools/wpf/project_generator.py

from .xaml_generator import XamlGenerator
from .style_generator import StyleGenerator
from .template_generator import TemplateGenerator
from templates.wpf.base_templates import WpfTemplates
from pathlib import Path
from typing import Dict, Any, List
import os

class WPFProjectGenerator:
    def __init__(self):
        self.xaml_generator = XamlGenerator()
        self.style_generator = StyleGenerator()
        self.template_generator = TemplateGenerator()
        self.wpf_templates = WpfTemplates()
        self.output_path = Path("output")
        self.output_path.mkdir(exist_ok=True)

    async def generate_project(self, project_structure: Dict) -> Dict:
        """Gera o projeto WPF completo"""
        try:
            project_name = project_structure['metadata']['name']
            project_path = self.output_path / project_name
            
            # Criar estrutura de diretórios
            self._create_project_structure(project_path)
            
            # Gerar arquivos do projeto
            await self._generate_solution_files(project_path, project_structure)
            await self._generate_core_files(project_path, project_structure)
            await self._generate_views(project_path, project_structure)
            await self._generate_viewmodels(project_path, project_structure)
            await self._generate_models(project_path, project_structure)
            await self._generate_styles(project_path, project_structure)
            await self._generate_resources(project_path, project_structure)
            
            return {
                'status': 'success',
                'path': str(project_path),
                'files_generated': self._get_generated_files(project_path)
            }
            
        except Exception as e:
            print(f"Erro na geração do projeto: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }

    def _create_project_structure(self, project_path: Path) -> None:
        """Cria estrutura de diretórios do projeto"""
        directories = [
            'Models',
            'ViewModels',
            'Views',
            'Services',
            'Infrastructure',
            'Resources',
            'Styles',
            'Properties'
        ]
        
        for directory in directories:
            (project_path / directory).mkdir(parents=True, exist_ok=True)

    async def _generate_solution_files(self, project_path: Path, structure: Dict) -> None:
        """Gera arquivos de solução e projeto"""
        project_name = structure['metadata']['name']
        
        # Gerar .sln
        sln_template = self.wpf_templates.get_solution_template({
            'name': project_name,
            'guid': self._generate_guid()
        })
        (project_path / f"{project_name}.sln").write_text(sln_template)
        
        # Gerar .csproj
        csproj_template = self.wpf_templates.get_project_template({
            'name': project_name,
            'target_framework': 'net6.0-windows'
        })
        (project_path / f"{project_name}.csproj").write_text(csproj_template)

    async def _generate_core_files(self, project_path: Path, structure: Dict) -> None:
        """Gera arquivos principais do projeto"""
        # App.xaml e App.xaml.cs
        app_config = {
            'namespace': structure['metadata']['name'],
            'startup_uri': 'Views/MainWindow.xaml'
        }
        app_xaml = self.xaml_generator.generate_window(app_config)
        (project_path / "App.xaml").write_text(app_xaml)
        
        app_cs = self.wpf_templates.get_app_code_behind_template(app_config)
        (project_path / "App.xaml.cs").write_text(app_cs)

        # AssemblyInfo.cs
        assembly_info = self.wpf_templates.get_assembly_info_template({
            'namespace': structure['metadata']['name'],
            'title': structure['metadata'].get('title', structure['metadata']['name'])
        })
        (project_path / "Properties/AssemblyInfo.cs").write_text(assembly_info)

    async def _generate_views(self, project_path: Path, structure: Dict) -> None:
        """Gera Views XAML"""
        views_path = project_path / "Views"
        views = structure.get('wpf_specs', {}).get('views', [])
        
        for view in views:
            # XAML
            view_config = {
                'window_properties': view.get('properties', {}),
                'resources': view.get('resources', {}),
                'layout': view.get('layout', {})
            }
            view_xaml = self.xaml_generator.generate_window(view_config)
            (views_path / f"{view['name']}.xaml").write_text(view_xaml)
            
            # Code-behind
            code_behind = self.wpf_templates.get_view_code_behind_template({
                'namespace': structure['metadata']['name'],
                'name': view['name']
            })
            (views_path / f"{view['name']}.xaml.cs").write_text(code_behind)

    async def _generate_viewmodels(self, project_path: Path, structure: Dict) -> None:
        """Gera ViewModels"""
        viewmodels_path = project_path / "ViewModels"
        viewmodels = structure.get('wpf_specs', {}).get('viewmodels', [])
        
        for vm in viewmodels:
            vm_code = self.wpf_templates.get_view_model_template({
                'namespace': structure['metadata']['name'],
                'name': vm['name'],
                'properties': vm.get('properties', []),
                'commands': vm.get('commands', [])
            })
            (viewmodels_path / f"{vm['name']}ViewModel.cs").write_text(vm_code)

    async def _generate_models(self, project_path: Path, structure: Dict) -> None:
        """Gera Models"""
        models_path = project_path / "Models"
        models = structure.get('db_specs', {}).get('entities', [])
        
        for model in models:
            model_code = self.wpf_templates.get_model_template({
                'namespace': structure['metadata']['name'],
                'name': model['name'],
                'properties': model.get('properties', [])
            })
            (models_path / f"{model['name']}.cs").write_text(model_code)

    async def _generate_styles(self, project_path: Path, structure: Dict) -> None:
        """Gera arquivos de estilo"""
        styles_path = project_path / "Styles"
        
        # Estilos base
        base_styles = self.style_generator.generate_styles(
            structure.get('ui_specs', {}).get('styles', {})
        )
        (styles_path / "BaseStyles.xaml").write_text(base_styles)
        
        # Temas
        theme_styles = self.style_generator.generate_styles(
            structure.get('ui_specs', {}).get('theme', {})
        )
        (styles_path / "Theme.xaml").write_text(theme_styles)

    async def _generate_resources(self, project_path: Path, structure: Dict) -> None:
        """Gera recursos do projeto"""
        resources_path = project_path / "Resources"
        
        # Templates de controle
        for template in structure.get('wpf_specs', {}).get('templates', []):
            template_xaml = self.template_generator.generate_control_template(template)
            (resources_path / f"{template['name']}Template.xaml").write_text(template_xaml)

    def _get_generated_files(self, project_path: Path) -> List[str]:
        """Retorna lista de arquivos gerados"""
        generated_files = []
        for root, _, files in os.walk(project_path):
            for file in files:
                file_path = Path(root) / file
                generated_files.append(str(file_path.relative_to(project_path)))
        return generated_files

    def _generate_guid(self) -> str:
        """Gera GUID para o projeto"""
        import uuid
        return str(uuid.uuid4())