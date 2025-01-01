# tools/wpf/templates/services/navigation/navigation_service.py
class NavigationServiceTemplate:
    @staticmethod
    def implementation(project_name: str) -> str:
        return f'''using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Windows;
using Microsoft.Extensions.DependencyInjection;
using {project_name}.ViewModels;

namespace {project_name}.Services.Navigation
{{
    public class NavigationService : INavigationService
    {{
        private readonly IServiceProvider _serviceProvider;
        private readonly Dictionary<string, Type> _viewModelMap;
        private readonly Stack<string> _navigationStack;

        public NavigationService(IServiceProvider serviceProvider)
        {{
            _serviceProvider = serviceProvider;
            _viewModelMap = new Dictionary<string, Type>();
            _navigationStack = new Stack<string>();
        }}

        public bool CanNavigate(string viewName)
        {{
            return _viewModelMap.ContainsKey(viewName);
        }}

        public async Task NavigateToAsync(string viewName)
        {{
            await NavigateToAsync(viewName, null);
        }}

        public async Task NavigateToAsync(string viewName, object parameter)
        {{
            if (!CanNavigate(viewName))
                throw new ArgumentException($"View not registered: {{viewName}}");

            var viewModelType = _viewModelMap[viewName];
            var viewModel = _serviceProvider.GetService(viewModelType) as ViewModelBase;
            
            if (viewModel != null)
            {{
                if (parameter != null && viewModel is INavigationAware navAware)
                {{
                    navAware.OnNavigatedTo(parameter);
                }}

                await viewModel.LoadAsync();
                
                Application.Current.Dispatcher.Invoke(() =>
                {{
                    if (Application.Current.MainWindow is ShellView shell)
                    {{
                        shell.ViewModel.CurrentViewModel = viewModel;
                        _navigationStack.Push(viewName);
                    }}
                }});
            }}
        }}

        public async Task GoBackAsync()
        {{
            if (_navigationStack.Count > 1)
            {{
                _navigationStack.Pop(); // Remove current
                var previousView = _navigationStack.Peek();
                await NavigateToAsync(previousView);
            }}
        }}

        public void RegisterView(string viewName, Type viewModelType)
        {{
            if (!_viewModelMap.ContainsKey(viewName))
            {{
                _viewModelMap.Add(viewName, viewModelType);
            }}
        }}

        public async Task InitializeAsync()
        {{
            await NavigateToAsync("MainView");
        }}
    }}
}}'''