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

    async def generate_project(self, project_spec: Dict) -> Dict:
        """Gera a estrutura do projeto WPF"""
        try:
            project_name = project_spec['metadata']['name']
            output_path = Path("output") / project_name
            
            # Criar estrutura de diretórios
            directories = [
                'Views',
                'ViewModels',
                'Models',
                'Services/Navigation',
                'Styles',
                'Properties'
            ]
            
            for dir_name in directories:
                (output_path / dir_name).mkdir(parents=True, exist_ok=True)
    
            # Gerar arquivos
            files_to_generate = {
                f'{project_name}.csproj': self._generate_csproj_template(project_name),
                f'{project_name}.sln': self._generate_solution_template(project_name),
                'Views/ShellView.xaml': self._generate_shell_view_template(project_name),
                'Views/ShellView.xaml.cs': self._generate_shell_view_code_template(project_name),
                'Views/MainWindow.xaml': self._generate_main_window_template(project_name),
                'Views/MainWindow.xaml.cs': self._generate_main_window_code_template(project_name),
                'ViewModels/ViewModelBase.cs': self._generate_viewmodel_base_template(project_name),
                'ViewModels/ShellViewModel.cs': self._generate_shell_viewmodel_template(project_name),
                'ViewModels/MainViewModel.cs': self._generate_main_viewmodel_template(project_name),
                'App.xaml': self._generate_app_xaml_template(project_name),
                'App.xaml.cs': self._generate_app_code_template(project_name),
                'Styles/BaseStyles.xaml': self._generate_base_styles_template(),
                'Styles/Theme.xaml': self._generate_theme_template(),
                'Services/Navigation/INavigationService.cs': self._generate_navigation_service_interface(project_name),
                'Services/Navigation/NavigationService.cs': self._generate_navigation_service(project_name),
                'Services/Navigation/INavigationAware.cs': self._generate_navigation_aware_interface(project_name)
            }
    
            # Gerar cada arquivo
            files_generated = []
            for file_path, content in files_to_generate.items():
                full_path = output_path / file_path
                full_path.parent.mkdir(exist_ok=True)
                full_path.write_text(content, encoding='utf-8')
                files_generated.append(file_path)
    
            return {
                'status': 'success',
                'path': str(output_path),
                'files_generated': files_generated
            }
    
        except Exception as e:
            print(f"Erro na geração do projeto: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
            
            
    def _generate_shell_view_template(self, project_name: str) -> str:
        return f'''<Window x:Class="{project_name}.Views.ShellView"
                xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
                xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
                xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
                xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
                xmlns:viewModels="clr-namespace:{project_name}.ViewModels"
                mc:Ignorable="d"
                Title="{{Binding Title}}" Height="450" Width="800"
                WindowStartupLocation="CenterScreen">
        
            <Grid>
                <Grid.RowDefinitions>
                    <RowDefinition Height="Auto"/>
                    <RowDefinition Height="*"/>
                    <RowDefinition Height="Auto"/>
                </Grid.RowDefinitions>
        
                <!-- Header -->
                <Border Grid.Row="0" 
                        Background="{{StaticResource PrimaryBrush}}" 
                        Padding="10">
                    <TextBlock Text="{{Binding Title}}" 
                               Foreground="White" 
                               FontSize="20"/>
                </Border>
        
                <!-- Content Area -->
                <ContentControl Grid.Row="1" 
                                Content="{{Binding CurrentViewModel}}"/>
        
                <!-- StatusBar -->
                <StatusBar Grid.Row="2">
                    <StatusBarItem>
                        <TextBlock Text="{{Binding CurrentViewModel.StatusMessage}}"/>
                    </StatusBarItem>
                    <StatusBarItem HorizontalAlignment="Right">
                        <ProgressBar Width="100" 
                                    Height="15" 
                                    IsIndeterminate="{{Binding CurrentViewModel.IsBusy}}"/>
                    </StatusBarItem>
                </StatusBar>
            </Grid>
        </Window>'''

    def _generate_shell_view_code_template(self, project_name: str) -> str:
        return f'''using System.Windows;
            using Microsoft.Extensions.DependencyInjection;
            using {project_name}.ViewModels;
            
            namespace {project_name}.Views
            {{
                public partial class ShellView : Window
                {{
                    public ShellViewModel ViewModel => (ShellViewModel)DataContext;
            
                    public ShellView()
                    {{
                        InitializeComponent();
                        DataContext = App.ServiceProvider.GetService<ShellViewModel>();
                    }}
                }}
            }}'''

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
        
        
    def _generate_csproj_template(self, project_name: str) -> str:
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
                <Description>Generated by Kallista</Description>
            </PropertyGroup>
        
            <ItemGroup>
                <PackageReference Include="CommunityToolkit.Mvvm" Version="8.2.2" />
                <PackageReference Include="Microsoft.Extensions.DependencyInjection" Version="8.0.0" />
                <PackageReference Include="Microsoft.EntityFrameworkCore" Version="7.0.14" />
                <PackageReference Include="Microsoft.EntityFrameworkCore.SqlServer" Version="7.0.14" />
            </ItemGroup>
        
        </Project>'''

    def _generate_solution_template(self, project_name: str) -> str:
        return f'''Microsoft Visual Studio Solution File, Format Version 12.00
            # Visual Studio Version 17
            VisualStudioVersion = 17.0.31903.59
            MinimumVisualStudioVersion = 10.0.40219.1
            Project("{{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}}") = "{project_name}", "{project_name}.csproj", "{{A43FB6C0-8C99-4E08-B45E-7E5828039624}}"
            EndProject
            Global
            	GlobalSection(SolutionConfigurationPlatforms) = preSolution
            		Debug|Any CPU = Debug|Any CPU
            		Release|Any CPU = Release|Any CPU
            	EndGlobalSection
            	GlobalSection(ProjectConfigurationPlatforms) = postSolution
            		{{A43FB6C0-8C99-4E08-B45E-7E5828039624}}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
            		{{A43FB6C0-8C99-4E08-B45E-7E5828039624}}.Debug|Any CPU.Build.0 = Debug|Any CPU
            		{{A43FB6C0-8C99-4E08-B45E-7E5828039624}}.Release|Any CPU.ActiveCfg = Release|Any CPU
            		{{A43FB6C0-8C99-4E08-B45E-7E5828039624}}.Release|Any CPU.Build.0 = Release|Any CPU
            	EndGlobalSection
            EndGlobal'''
            
    def _generate_main_window_template(self, project_name: str) -> str:
        return f'''<Window x:Class="{project_name}.Views.MainWindow"
                    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
                    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
                    xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
                    xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
                    xmlns:viewModels="clr-namespace:{project_name}.ViewModels"
                    mc:Ignorable="d"
                    Title="{{Binding Title}}" Height="450" Width="800">
            
                <Grid Margin="10">
                    <Grid.RowDefinitions>
                        <RowDefinition Height="Auto"/>
                        <RowDefinition Height="*"/>
                        <RowDefinition Height="Auto"/>
                    </Grid.RowDefinitions>
            
                    <!-- Header -->
                    <StackPanel Grid.Row="0" Margin="0,0,0,10">
                        <TextBlock Text="{{Binding WelcomeMessage}}" 
                                   FontSize="24" 
                                   HorizontalAlignment="Center"/>
                        
                        <StackPanel Orientation="Horizontal" 
                                    HorizontalAlignment="Center" 
                                    Margin="0,10">
                            <TextBox Text="{{Binding UserName}}" 
                                     Width="200" 
                                     Margin="0,0,10,0"/>
                            <Button Content="Update Username" 
                                    Command="{{Binding UpdateUserNameCommand}}"
                                    CommandParameter="{{Binding UserName}}"/>
                        </StackPanel>
                    </StackPanel>
            
                    <!-- Content -->
                    <Grid Grid.Row="1">
                        <ListView ItemsSource="{{Binding RecentItems}}"
                                  Visibility="{{Binding IsInitialized, Converter={{StaticResource BooleanToVisibilityConverter}}}}"/>
                        
                        <ProgressBar IsIndeterminate="True" 
                                     Height="2" 
                                     Margin="0,10" 
                                     Visibility="{{Binding IsBusy, Converter={{StaticResource BooleanToVisibilityConverter}}}}"/>
                    </Grid>
            
                    <!-- Status Bar -->
                    <StatusBar Grid.Row="2">
                        <StatusBarItem>
                            <TextBlock Text="{{Binding StatusMessage}}"/>
                        </StatusBarItem>
                    </StatusBar>
                </Grid>
            </Window>'''
            
            
    def _generate_main_window_code_template(self, project_name: str) -> str:
        return f'''using System.Windows;
                    
            namespace {project_name}.Views
            {{
                public partial class MainWindow : Window
                {{
                    public MainWindow()
                    {{
                        InitializeComponent();
                    }}
                }}
            }}'''

    def _generate_viewmodel_base_template(self, project_name: str) -> str:
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
            
            
    def _generate_app_xaml_template(self, project_name: str) -> str:
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
        
    def _generate_app_code_template(self, project_name: str) -> str:
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

    def _generate_base_styles_template(self) -> str:
        return '''<ResourceDictionary
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
    
    <!-- Button Style -->
    <Style TargetType="{x:Type Button}">
        <Setter Property="Background" Value="#007ACC"/>
        <Setter Property="Foreground" Value="White"/>
        <Setter Property="Padding" Value="10,5"/>
        <Setter Property="BorderThickness" Value="0"/>
        <Setter Property="Template">
            <Setter.Value>
                <ControlTemplate TargetType="{x:Type Button}">
                    <Border Background="{TemplateBinding Background}"
                            BorderBrush="{TemplateBinding BorderBrush}"
                            BorderThickness="{TemplateBinding BorderThickness}"
                            CornerRadius="3">
                        <ContentPresenter HorizontalAlignment="Center" 
                                        VerticalAlignment="Center"/>
                    </Border>
                </ControlTemplate>
            </Setter.Value>
        </Setter>
        <Style.Triggers>
            <Trigger Property="IsMouseOver" Value="True">
                <Setter Property="Background" Value="#005A9E"/>
            </Trigger>
        </Style.Triggers>
    </Style>

</ResourceDictionary>'''

    def _generate_theme_template(self) -> str:
        return '''<ResourceDictionary
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
    
    <!-- Colors -->
    <Color x:Key="PrimaryColor">#007ACC</Color>
    <Color x:Key="SecondaryColor">#005A9E</Color>
    <Color x:Key="BackgroundColor">#FFFFFF</Color>
    <Color x:Key="TextColor">#323232</Color>
    
    <!-- Brushes -->
    <SolidColorBrush x:Key="PrimaryBrush" Color="{StaticResource PrimaryColor}"/>
    <SolidColorBrush x:Key="SecondaryBrush" Color="{StaticResource SecondaryColor}"/>
    <SolidColorBrush x:Key="BackgroundBrush" Color="{StaticResource BackgroundColor}"/>
    <SolidColorBrush x:Key="TextBrush" Color="{StaticResource TextColor}"/>

</ResourceDictionary>'''

    def _generate_main_viewmodel_template(self, project_name: str) -> str:
        return f'''using CommunityToolkit.Mvvm.ComponentModel;
            using CommunityToolkit.Mvvm.Input;
            using System.Collections.ObjectModel;
            using System.Threading.Tasks;
            using {project_name}.Services.Navigation;
            
            namespace {project_name}.ViewModels
            {{
                public partial class MainViewModel : ViewModelBase
                {{
                    // Observable Properties Example
                    [ObservableProperty]
                    [NotifyPropertyChangedFor(nameof(WelcomeMessage))]
                    private string userName = string.Empty;
            
                    [ObservableProperty]
                    private bool isInitialized;
            
                    public string WelcomeMessage => string.IsNullOrEmpty(UserName) 
                        ? "Welcome to {project_name}!" 
                        : $"Welcome, {{UserName}}!";
            
                    // Observable Collection Example
                    public ObservableCollection<string> RecentItems {{ get; }} = new();
            
                    public MainViewModel(INavigationService navigationService) : base(navigationService)
                    {{
                        Title = "{project_name}";
                        SetupCommands();
                    }}
            
                    // Commands
                    [RelayCommand]
                    private async Task InitializeAsync()
                    {{
                        await ExecuteAsync(async () =>
                        {{
                            // Simulating some initialization work
                            await Task.Delay(1000);
                            
                            RecentItems.Clear();
                            RecentItems.Add("Sample Item 1");
                            RecentItems.Add("Sample Item 2");
                            RecentItems.Add("Sample Item 3");
            
                            IsInitialized = true;
                            StatusMessage = "Application initialized successfully";
                        }});
                    }}
            
                    [RelayCommand(CanExecute = nameof(CanUpdateUserName))]
                    private void UpdateUserName(string newName)
                    {{
                        UserName = newName;
                        StatusMessage = "Username updated successfully";
                    }}
            
                    private bool CanUpdateUserName(string newName)
                    {{
                        return !string.IsNullOrEmpty(newName) && !IsBusy;
                    }}
            
                    // Lifecycle
                    public override async Task LoadAsync()
                    {{
                        await base.LoadAsync();
                        await InitializeAsync();
                    }}
            
                    private void SetupCommands()
                    {{
                        // Additional command setup if needed
                    }}
                }}
            }}'''