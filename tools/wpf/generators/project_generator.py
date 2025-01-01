# tools/wpf/generators/project_generator.py
from typing import Dict, Any
from pathlib import Path
from .base_generator import BaseGenerator
from .style_generator import StyleGenerator
from .template_generator import TemplateGenerator
from .xaml_generator import XamlGenerator
from ..templates.views.shell_view import _generate_shell_view_template
from ..templates.viewmodels.shell_viewmodel import _generate_shell_viewmodel_template

class WPFProjectGenerator(BaseGenerator):
    def __init__(self):
        super().__init__()
        self.style_generator = StyleGenerator()
        self.template_generator = TemplateGenerator()
        self.xaml_generator = XamlGenerator()
        self.output_path = Path("output")
        self.output_path.mkdir(exist_ok=True)
        
        # Carregar templates específicos por tipo de projeto
        self.project_types = {
            'kanban': self._load_project_type_templates('kanban'),
            'crud': self._load_project_type_templates('crud'),
            'dashboard': self._load_project_type_templates('dashboard'),
            'report': self._load_project_type_templates('report')
        }

    def _load_project_type_templates(self, project_type: str) -> Dict[str, str]:
        """Carrega templates específicos para cada tipo de projeto"""
        type_path = self.templates_path / "project_types" / project_type
        templates = {}
        
        if type_path.exists():
            for template_file in type_path.glob("*.xaml"):
                templates[template_file.stem] = template_file.read_text(encoding='utf-8')
        
        return templates

    async def generate_project(self, project_spec: Dict) -> Dict:
        """Gera a estrutura do projeto WPF"""
        try:
            project_name = project_spec['metadata']['name']
            project_type = project_spec['type']
            
            output_path = self.output_path / project_name
            self.ensure_output_directory(output_path)
            
            # Criar estrutura de diretórios
            await self._create_directory_structure(output_path)
            
            # Gerar arquivos baseados no tipo de projeto
            await self._generate_project_files(
                output_path, 
                project_name, 
                project_type, 
                project_spec
            )
            
            return {
                'status': 'success',
                'path': str(output_path),
                'files_generated': self._get_generated_files(output_path)
            }
            
        except Exception as e:
            print(f"Erro na geração do projeto: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    
    async def _create_directory_structure(self, output_path: Path) -> None:
        """Cria estrutura de diretórios do projeto"""
        directories = [
            'Views',
            'ViewModels',
            'Models',
            'Services/Navigation',
            'Infrastructure',
            'Resources',
            'Styles',
            'Properties'
        ]
        
        for directory in directories:
            (output_path / directory).mkdir(parents=True, exist_ok=True)

    async def _generate_project_files(
        self, 
        output_path: Path, 
        project_name: str, 
        project_type: str,
        project_spec: Dict
    ) -> None:
        """Gera todos os arquivos do projeto"""
        
        # Carrega templates específicos do tipo de projeto
        type_templates = self.project_types.get(project_type, {})
        
        # Mapa de arquivos para gerar
        files_to_generate = {
            # Arquivos de projeto
            f'{project_name}.csproj': self._generate_csproj_template(project_name, project_spec),
            f'{project_name}.sln': self._generate_solution_template(project_name),
            
            # Views
            'Views/ShellView.xaml': self._generate_shell_view(project_name, type_templates),
            'Views/ShellView.xaml.cs': self._generate_shell_view_code(project_name),
            'Views/MainWindow.xaml': self._generate_main_window(project_name, type_templates),
            'Views/MainWindow.xaml.cs': self._generate_main_window_code(project_name),
            
            # ViewModels
            'ViewModels/ViewModelBase.cs': self._generate_viewmodel_base(project_name),
            'ViewModels/ShellViewModel.cs': self._generate_shell_viewmodel(project_name),
            'ViewModels/MainViewModel.cs': self._generate_main_viewmodel(project_name, project_type),
            
            # App
            'App.xaml': self._generate_app_xaml(project_name),
            'App.xaml.cs': self._generate_app_code(project_name),
            
            # Styles
            'Styles/BaseStyles.xaml': self._generate_base_styles(),
            'Styles/Theme.xaml': self._generate_theme(),
            
            # Services
            'Services/Navigation/INavigationService.cs': self._generate_navigation_interface(project_name),
            'Services/Navigation/NavigationService.cs': self._generate_navigation_service(project_name),
            'Services/Navigation/INavigationAware.cs': self._generate_navigation_aware(project_name)
        }
        
        # Adicionar arquivos específicos do tipo de projeto
        specific_files = self._get_project_type_files(project_type, project_name, project_spec)
        files_to_generate.update(specific_files)
        
        # Gerar cada arquivo
        for file_path, content in files_to_generate.items():
            full_path = output_path / file_path
            self.save_generated_file(full_path, content)

    def _get_project_type_files(self, project_type: str, project_name: str, project_spec: Dict) -> Dict[str, str]:
        """Retorna arquivos específicos para cada tipo de projeto"""
        
        specific_files = {}
        
        if project_type == 'kanban':
            specific_files.update({
                'Models/KanbanBoard.cs': self._generate_kanban_board_model(project_name),
                'Models/KanbanCard.cs': self._generate_kanban_card_model(project_name),
                'ViewModels/KanbanViewModel.cs': self._generate_kanban_viewmodel(project_name),
                'Views/KanbanView.xaml': self._generate_kanban_view(project_name),
                'Views/KanbanView.xaml.cs': self._generate_kanban_view_code(project_name)
            })
        
        elif project_type == 'crud':
            specific_files.update({
                'Models/Entity.cs': self._generate_crud_model(project_name),
                'ViewModels/CrudViewModel.cs': self._generate_crud_viewmodel(project_name),
                'Views/CrudView.xaml': self._generate_crud_view(project_name),
                'Views/CrudView.xaml.cs': self._generate_crud_view_code(project_name)
            })
        
        # Adicionar outros tipos de projeto conforme necessário
        
        return specific_files
        

    def _generate_csproj_template(self, project_name: str, project_spec: Dict) -> str:
        """Gera arquivo .csproj com dependências baseadas nas especificações"""
        
        # Base packages sempre necessários
        packages = [
            ('CommunityToolkit.Mvvm', '8.2.2'),
            ('Microsoft.Extensions.DependencyInjection', '8.0.0')
        ]
        
        # Adiciona packages baseado nas especificações
        if project_spec.get('metadata', {}).get('database', False):
            packages.extend([
                ('Microsoft.EntityFrameworkCore', '7.0.14'),
                ('Microsoft.EntityFrameworkCore.SqlServer', '7.0.14')
            ])
            
        if project_spec.get('metadata', {}).get('authentication', False):
            packages.append(('Microsoft.AspNetCore.Identity.EntityFrameworkCore', '7.0.14'))

        # Gera as referências de package
        package_refs = '\n'.join(
            f'        <PackageReference Include="{package}" Version="{version}" />'
            for package, version in packages
        )

        return f'''<Project Sdk="Microsoft.NET.Sdk">
            <PropertyGroup>
                <OutputType>WinExe</OutputType>
                <TargetFramework>net7.0-windows</TargetFramework>
                <Nullable>enable</Nullable>
                <UseWPF>true</UseWPF>
                <RootNamespace>{project_name}</RootNamespace>
                <AssemblyName>{project_name}</AssemblyName>
                <Version>1.0.0</Version>
                <Authors>Kallista Generator</Authors>
                <Company>Kallista</Company>
                <Product>{project_name}</Product>
                <Description>{project_spec.get('metadata', {}).get('description', '')}</Description>
            </PropertyGroup>
        
            <ItemGroup>
        {package_refs}
            </ItemGroup>
        </Project>'''

    def _generate_solution_template(self, project_name: str) -> str:
                """Gera arquivo .sln"""
                project_guid = self._generate_guid()
                solution_guid = self._generate_guid()
                
                return f'''Microsoft Visual Studio Solution File, Format Version 12.00
        # Visual Studio Version 17
        VisualStudioVersion = 17.0.31903.59
        MinimumVisualStudioVersion = 10.0.40219.1
        Project("{{{solution_guid}}}") = "{project_name}", "{project_name}.csproj", "{{{project_guid}}}"
        EndProject
        Global
            GlobalSection(SolutionConfigurationPlatforms) = preSolution
                Debug|Any CPU = Debug|Any CPU
                Release|Any CPU = Release|Any CPU
            EndGlobalSection
            GlobalSection(ProjectConfigurationPlatforms) = postSolution
                {{{project_guid}}}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
                {{{project_guid}}}.Debug|Any CPU.Build.0 = Debug|Any CPU
                {{{project_guid}}}.Release|Any CPU.ActiveCfg = Release|Any CPU
                {{{project_guid}}}.Release|Any CPU.Build.0 = Release|Any CPU
            EndGlobalSection
            GlobalSection(SolutionProperties) = preSolution
                HideSolutionNode = FALSE
            EndGlobalSection
        EndGlobal'''

    def _generate_guid(self) -> str:
        """Gera um GUID para uso no projeto"""
        import uuid
        return str(uuid.uuid4()).upper()
        
    