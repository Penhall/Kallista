# tools/wpf/generators/template_manager.py
from ..templates.infrastructure.project import ProjectTemplates
from ..templates.infrastructure.app import AppTemplates
from ..templates.infrastructure.styles import StyleTemplates
from ..templates.services.navigation.navigation_interfaces import NavigationInterfaceTemplates
from ..templates.services.navigation.navigation_service import NavigationServiceTemplate
from ..templates.views.shell_view import ShellViewTemplate
from ..templates.views.main_window import MainWindowTemplate
from ..templates.viewmodels.base_viewmodel import BaseViewModelTemplate
from ..templates.viewmodels.shell_viewmodel import ShellViewModelTemplate
from ..templates.viewmodels.main_viewmodel import MainViewModelTemplate

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
        self.main_viewmodel = MainViewModelTemplate()

    def get_base_templates(self, project_name: str) -> dict:
        return {
            f'{project_name}.csproj': self.project_templates.csproj(project_name, self._get_base_packages()),
            f'{project_name}.sln': self.project_templates.solution(project_name, self._generate_guid()),
            'App.xaml': self.app_templates.xaml(project_name),
            'App.xaml.cs': self.app_templates.code_behind(project_name),
            'Styles/BaseStyles.xaml': self.style_templates.base_styles(),
            'Styles/Theme.xaml': self.style_templates.theme(),
            'Services/Navigation/INavigationService.cs': self.navigation_interfaces.navigation_service(project_name),
            'Services/Navigation/INavigationAware.cs': self.navigation_interfaces.navigation_aware(project_name),
            'Services/Navigation/NavigationService.cs': self.navigation_service.implementation(project_name),
            'Views/ShellView.xaml': self.shell_view.xaml(project_name),
            'Views/ShellView.xaml.cs': self.shell_view.code_behind(project_name),
            'Views/MainWindow.xaml': self.main_window.xaml(project_name),
            'Views/MainWindow.xaml.cs': self.main_window.code_behind(project_name),
            'ViewModels/ViewModelBase.cs': self.base_viewmodel.implementation(project_name),
            'ViewModels/ShellViewModel.cs': self.shell_viewmodel.implementation(project_name),
            'ViewModels/MainViewModel.cs': self.main_viewmodel.implementation(project_name)
        }

    def _get_base_packages(self) -> list:
        return [
            ('CommunityToolkit.Mvvm', '8.2.2'),
            ('Microsoft.Extensions.DependencyInjection', '8.0.0')
        ]

    def _generate_guid(self) -> str:
        import uuid
        return str(uuid.uuid4()).upper()