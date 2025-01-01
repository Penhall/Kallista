# tools/wpf/templates/viewmodels/base_viewmodel.py
class BaseViewModelTemplate:
    @staticmethod
    def implementation(project_name: str) -> str:
        return f'''using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System.ComponentModel;
using System.Threading.Tasks;
using {project_name}.Services.Navigation;

namespace {project_name}.ViewModels
{{
    public abstract partial class ViewModelBase : ObservableObject
    {{
        protected readonly INavigationService _navigationService;

        protected ViewModelBase(INavigationService navigationService)
        {{
            _navigationService = navigationService;
        }}

        // Status properties
        [ObservableProperty]
        private bool isBusy;

        [ObservableProperty]
        private string title = string.Empty;

        [ObservableProperty]
        private string statusMessage = string.Empty;

        [ObservableProperty]
        [NotifyPropertyChangedFor(nameof(HasErrors))]
        private string errorMessage = string.Empty;

        public bool HasErrors => !string.IsNullOrEmpty(ErrorMessage);

        // Navigation methods
        protected async Task NavigateToAsync(string viewName)
        {{
            await _navigationService.NavigateToAsync(viewName);
        }}

        protected async Task NavigateToAsync(string viewName, object parameter)
        {{
            await _navigationService.NavigateToAsync(viewName, parameter);
        }}

        protected async Task GoBackAsync()
        {{
            await _navigationService.GoBackAsync();
        }}

        // Lifecycle methods
        public virtual Task LoadAsync()
        {{
            return Task.CompletedTask;
        }}

        public virtual Task UnloadAsync()
        {{
            return Task.CompletedTask;
        }}

        // Helper methods
        protected async Task ExecuteAsync(Func<Task> operation)
        {{
            try
            {{
                IsBusy = true;
                ErrorMessage = string.Empty;
                StatusMessage = "Working...";

                await operation();

                StatusMessage = "Completed Successfully";
            }}
            catch (Exception ex)
            {{
                ErrorMessage = ex.Message;
                StatusMessage = "Error Occurred";
            }}
            finally
            {{
                IsBusy = false;
            }}
        }}

        protected void SetErrorMessage(string message)
        {{
            ErrorMessage = message;
            StatusMessage = "Error Occurred";
        }}

        protected void ClearMessages()
        {{
            ErrorMessage = string.Empty;
            StatusMessage = string.Empty;
        }}
    }}
}}'''