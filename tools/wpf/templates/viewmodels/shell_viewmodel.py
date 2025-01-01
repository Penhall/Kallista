# tools/wpf/templates/viewmodels/shell_viewmodel.py
class ShellViewModelTemplate:
    @staticmethod
    def implementation(project_name: str) -> str:
        return f'''using CommunityToolkit.Mvvm.ComponentModel;
using {project_name}.Services.Navigation;

namespace {project_name}.ViewModels
{{
    public partial class ShellViewModel : ViewModelBase
    {{
        [ObservableProperty]
        private ViewModelBase? currentViewModel;

        public ShellViewModel(INavigationService navigationService)
            : base(navigationService)
        {{
            Title = "{project_name}";
        }}

        public override async Task LoadAsync()
        {{
            await base.LoadAsync();
            await _navigationService.NavigateToAsync("MainView");
        }}
    }}
}}'''

    @staticmethod
    def create_kanban_shell(project_name: str) -> str:
        """Versão específica para projetos tipo Kanban"""
        return f'''using CommunityToolkit.Mvvm.ComponentModel;
using {project_name}.Services.Navigation;

namespace {project_name}.ViewModels
{{
    public partial class ShellViewModel : ViewModelBase
    {{
        [ObservableProperty]
        private ViewModelBase? currentViewModel;

        [ObservableProperty]
        private bool isAuthenticated;

        public ShellViewModel(INavigationService navigationService)
            : base(navigationService)
        {{
            Title = "{project_name} - Kanban Board";
        }}

        public override async Task LoadAsync()
        {{
            await base.LoadAsync();
            
            // Para projetos com autenticação, navegar para login
            // Caso contrário, ir direto para o quadro Kanban
            if (IsAuthenticated)
                await _navigationService.NavigateToAsync("KanbanBoardView");
            else
                await _navigationService.NavigateToAsync("LoginView");
        }}
    }}
}}'''

    @staticmethod
    def create_crud_shell(project_name: str) -> str:
        """Versão específica para projetos tipo CRUD"""
        return f'''using CommunityToolkit.Mvvm.ComponentModel;
using {project_name}.Services.Navigation;

namespace {project_name}.ViewModels
{{
    public partial class ShellViewModel : ViewModelBase
    {{
        [ObservableProperty]
        private ViewModelBase? currentViewModel;

        public ShellViewModel(INavigationService navigationService)
            : base(navigationService)
        {{
            Title = "{project_name} - Data Management";
        }}

        public override async Task LoadAsync()
        {{
            await base.LoadAsync();
            await _navigationService.NavigateToAsync("ListViewPage");
        }}
    }}
}}'''