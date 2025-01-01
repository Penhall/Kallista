# tools/wpf/templates/services/navigation/navigation_interfaces.py
class NavigationInterfaceTemplates:
    @staticmethod
    def navigation_service(project_name: str) -> str:
        return f'''using System.Threading.Tasks;

namespace {project_name}.Services.Navigation
{{
    public interface INavigationService
    {{
        bool CanNavigate(string viewName);
        Task NavigateToAsync(string viewName);
        Task NavigateToAsync(string viewName, object parameter);
        Task GoBackAsync();
        void RegisterView(string viewName, System.Type viewModelType);
        Task InitializeAsync();
    }}
}}'''

    @staticmethod
    def navigation_aware(project_name: str) -> str:
        return f'''namespace {project_name}.Services.Navigation
{{
    public interface INavigationAware
    {{
        void OnNavigatedTo(object parameter);
    }}
}}'''