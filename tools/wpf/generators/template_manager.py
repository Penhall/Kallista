# tools/wpf/generators/template_manager.py
from pathlib import Path
from ..templates.infrastructure.project import ProjectTemplates
from ..templates.infrastructure.app import AppTemplates
from ..templates.infrastructure.styles import StyleTemplates
from ..templates.services.navigation.navigation_interfaces import NavigationInterfaceTemplates
from ..templates.services.navigation.navigation_service import NavigationServiceTemplate
from ..templates.views.shell_view import ShellViewTemplate
from ..templates.views.main_window import MainWindowTemplate
from ..templates.viewmodels.base_viewmodel import BaseViewModelTemplate
from ..templates.viewmodels.shell_viewmodel import ShellViewModelTemplate

class TemplateManager:
    def __init__(self):
        self.project_templates = ProjectTemplates()
        self.app_templates = AppTemplates()
        self.style_templates = StyleTemplates()
        self.navigation_interfaces = NavigationInterfaceTemplates()
        self.navigation_service = NavigationServiceTemplate()
        self.shell_view = ShellViewTemplate()
        self.main_window = MainWindowTemplate()
        self.base_viewmodel = BaseViewModelTemplate()
        self.shell_viewmodel = ShellViewModelTemplate()

    def get_base_templates(self, project_name: str) -> dict:
        """Retorna os templates base para qualquer projeto WPF/MVVM"""
        return {
            # Infrastructure
            f'{project_name}.csproj': self.project_templates.csproj(
                project_name, 
                self._get_base_packages()
            ),
            f'{project_name}.sln': self.project_templates.solution(
                project_name, 
                self._generate_guid()
            ),
            
            # App
            'App.xaml': self.app_templates.xaml(project_name),
            'App.xaml.cs': self.app_templates.code_behind(project_name),
            
            # Styles
            'Styles/BaseStyles.xaml': self.style_templates.base_styles(),
            'Styles/Theme.xaml': self.style_templates.theme(),
            
            # Navigation
            'Services/Navigation/INavigationService.cs': 
                self.navigation_interfaces.navigation_service(project_name),
            'Services/Navigation/INavigationAware.cs': 
                self.navigation_interfaces.navigation_aware(project_name),
            'Services/Navigation/NavigationService.cs': 
                self.navigation_service.implementation(project_name),
            
            # Views
            'Views/ShellView.xaml': self.shell_view.xaml(project_name),
            'Views/ShellView.xaml.cs': self.shell_view.code_behind(project_name),
            'Views/MainWindow.xaml': self.main_window.xaml(project_name),
            'Views/MainWindow.xaml.cs': self.main_window.code_behind(project_name),
            
            # ViewModels
            'ViewModels/ViewModelBase.cs': self.base_viewmodel.implementation(project_name),
            'ViewModels/ShellViewModel.cs': self.shell_viewmodel.implementation(project_name)
        }

    def _get_base_packages(self) -> list:
        """Retorna os pacotes NuGet base necessários"""
        return [
            ('CommunityToolkit.Mvvm', '8.2.2'),
            ('Microsoft.Extensions.DependencyInjection', '8.0.0')
        ]

    def _generate_guid(self) -> str:
        """Gera um GUID para o projeto"""
        import uuid
        return str(uuid.uuid4()).upper()