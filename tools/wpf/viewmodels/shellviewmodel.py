def _generate_shell_viewmodel_template(self, project_name: str) -> str:
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