# tools/wpf/templates/infrastructure/app.py
class AppTemplates:
    @staticmethod
    def xaml(project_name: str) -> str:
        return f'''<Application x:Class="{project_name}.App"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
    <Application.Resources>
        <ResourceDictionary>
            <ResourceDictionary.MergedDictionaries>
                <ResourceDictionary Source="Styles/BaseStyles.xaml"/>
                <ResourceDictionary Source="Styles/Theme.xaml"/>
            </ResourceDictionary.MergedDictionaries>

            <BooleanToVisibilityConverter x:Key="BooleanToVisibilityConverter"/>
        </ResourceDictionary>
    </Application.Resources>
</Application>'''

    @staticmethod
    def code_behind(project_name: str) -> str:
        return f'''using Microsoft.Extensions.DependencyInjection;
using System;
using System.Windows;
using {project_name}.ViewModels;
using {project_name}.Views;
using {project_name}.Services.Navigation;

namespace {project_name}
{{
    public partial class App : Application
    {{
        private IServiceProvider _serviceProvider;

        public App()
        {{
            _serviceProvider = ConfigureServices();
        }}

        private IServiceProvider ConfigureServices()
        {{
            var services = new ServiceCollection();

            // Register services
            services.AddSingleton<INavigationService, NavigationService>();

            // Register ViewModels
            services.AddTransient<ShellViewModel>();
            services.AddTransient<MainViewModel>();

            return services.BuildServiceProvider();
        }}

        protected override async void OnStartup(StartupEventArgs e)
        {{
            base.OnStartup(e);

            var navigationService = _serviceProvider.GetService<INavigationService>();
            
            // Register views
            navigationService?.RegisterView("MainView", typeof(MainViewModel));

            // Create and show the shell window
            var shellWindow = new ShellView();
            MainWindow = shellWindow;
            shellWindow.Show();

            // Initialize shell
            if (shellWindow.DataContext is ShellViewModel shellViewModel)
            {{
                await shellViewModel.LoadAsync();
            }}
        }}

        protected override void OnExit(ExitEventArgs e)
        {{
            base.OnExit(e);
            if (_serviceProvider is IDisposable disposable)
            {{
                disposable.Dispose();
            }}
        }}

        public static IServiceProvider ServiceProvider => ((App)Current)._serviceProvider;
    }}
}}'''