# templates/wpf/base_templates.py
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime

class WpfTemplates:
    def __init__(self):
        self.templates_path = Path("templates/wpf")
        self.templates_path.mkdir(parents=True, exist_ok=True)

    def get_solution_template(self, config: Dict[str, Any]) -> str:
        """Gera template para arquivo .sln"""
        return f'''
            Microsoft Visual Studio Solution File, Format Version 12.00
            # Visual Studio Version 17
            VisualStudioVersion = 17.0.31903.59
            MinimumVisualStudioVersion = 10.0.40219.1
            Project("{{{config['guid']}}}")") = "{config['name']}", "{config['name']}\{config['name']}.csproj", "{{{config['guid']}}}"
            EndProject
            Global
                GlobalSection(SolutionConfigurationPlatforms) = preSolution
                    Debug|Any CPU = Debug|Any CPU
                    Release|Any CPU = Release|Any CPU
                EndGlobalSection
                GlobalSection(ProjectConfigurationPlatforms) = postSolution
                    {{{config['guid']}}}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
                    {{{config['guid']}}}.Debug|Any CPU.Build.0 = Debug|Any CPU
                    {{{config['guid']}}}.Release|Any CPU.ActiveCfg = Release|Any CPU
                    {{{config['guid']}}}.Release|Any CPU.Build.0 = Release|Any CPU
                EndGlobalSection
            EndGlobal
            '''

    def get_project_template(self, config: Dict[str, Any]) -> str:
        """Gera template para arquivo .csproj"""
        return f'''
                <Project Sdk="Microsoft.NET.Sdk">
                
                  <PropertyGroup>
                    <OutputType>WinExe</OutputType>
                    <TargetFramework>{config['target_framework']}</TargetFramework>
                    <UseWPF>true</UseWPF>
                    <RootNamespace>{config['name']}</RootNamespace>
                    <AssemblyName>{config['name']}</AssemblyName>
                  </PropertyGroup>
                
                  <ItemGroup>
                    <PackageReference Include="Microsoft.Extensions.DependencyInjection" Version="6.0.0" />
                    <PackageReference Include="Microsoft.EntityFrameworkCore" Version="6.0.0" />
                    <PackageReference Include="CommunityToolkit.Mvvm" Version="8.0.0" />
                  </ItemGroup>
                
                </Project>
                '''

    def get_assembly_info_template(self, config: Dict[str, Any]) -> str:
        """Gera template para AssemblyInfo.cs"""
        return f'''
            using System.Reflection;
            using System.Runtime.CompilerServices;
            using System.Runtime.InteropServices;
            using System.Windows;
            
            [assembly: AssemblyTitle("{config['title']}")]
            [assembly: AssemblyDescription("{config.get('description', '')}")]
            [assembly: AssemblyConfiguration("")]
            [assembly: AssemblyCompany("{config.get('company', '')}")]
            [assembly: AssemblyProduct("{config['title']}")]
            [assembly: AssemblyCopyright("Copyright © {datetime.now().year}")]
            [assembly: AssemblyTrademark("")]
            [assembly: AssemblyCulture("")]
            
            [assembly: ComVisible(false)]
            [assembly: ThemeInfo(ResourceDictionaryLocation.None, ResourceDictionaryLocation.SourceAssembly)]
            
            [assembly: AssemblyVersion("1.0.0.0")]
            [assembly: AssemblyFileVersion("1.0.0.0")]
            '''

    def get_app_template(self, config: Dict[str, Any]) -> str:
        """Gera template para App.xaml"""
        return f'''
            <Application x:Class="{config['namespace']}.App"
                         xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
                         xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
                         StartupUri="{config['startup_uri']}">
                <Application.Resources>
                    <ResourceDictionary>
                        <ResourceDictionary.MergedDictionaries>
                            <ResourceDictionary Source="/Styles/Theme.xaml"/>
                            <ResourceDictionary Source="/Styles/BaseStyles.xaml"/>
                        </ResourceDictionary.MergedDictionaries>
                    </ResourceDictionary>
                </Application.Resources>
            </Application>
            '''

    def get_app_code_behind_template(self, config: Dict[str, Any]) -> str:
        """Gera template para App.xaml.cs"""
        return f'''
            using System;
            using System.Windows;
            using Microsoft.Extensions.DependencyInjection;
            
            namespace {config['namespace']}
            {{
                public partial class App : Application
                {{
                    private readonly IServiceProvider _serviceProvider;
            
                    public App()
                    {{
                        IServiceCollection services = new ServiceCollection();
                        ConfigureServices(services);
                        _serviceProvider = services.BuildServiceProvider();
                    }}
            
                    private void ConfigureServices(IServiceCollection services)
                    {{
                        // Register services here
                        RegisterViewModels(services);
                        RegisterServices(services);
                    }}
            
                    private void RegisterViewModels(IServiceCollection services)
                    {{
                        // Register ViewModels here
                    }}
            
                    private void RegisterServices(IServiceCollection services)
                    {{
                        // Register Services here
                    }}
            
                    protected override void OnStartup(StartupEventArgs e)
                    {{
                        base.OnStartup(e);
                    }}
                }}
            }}
            '''

    def get_view_model_template(self, config: Dict[str, Any]) -> str:
        """Gera template para ViewModel"""
        return f'''
            using System;
            using System.Windows.Input;
            using CommunityToolkit.Mvvm.ComponentModel;
            using CommunityToolkit.Mvvm.Input;
            
            namespace {config['namespace']}.ViewModels
            {{
                public partial class {config['name']}ViewModel : ObservableObject
                {{
                    public {config['name']}ViewModel()
                    {{
                        InitializeCommands();
                    }}
            
                    #region Properties
                    {self._generate_properties(config.get('properties', []))}
                    #endregion
            
                    #region Commands
                    {self._generate_commands(config.get('commands', []))}
                    #endregion
            
                    private void InitializeCommands()
                    {{
                        // Initialize commands here
                    }}
                }}
            }}
            '''

    def get_view_code_behind_template(self, config: Dict[str, Any]) -> str:
        """Gera template para code-behind de View"""
        return f'''
            using System.Windows;
            using {config['namespace']}.ViewModels;
            
            namespace {config['namespace']}.Views
            {{
                public partial class {config['name']} : Window
                {{
                    public {config['name']}()
                    {{
                        InitializeComponent();
                        DataContext = App.Current.Services.GetService<{config['name']}ViewModel>();
                    }}
                }}
            }}
            '''

    def get_model_template(self, config: Dict[str, Any]) -> str:
        """Gera template para Model"""
        return f'''
            using System;
            using System.ComponentModel.DataAnnotations;
            
            namespace {config['namespace']}.Models
            {{
                public class {config['name']}
                {{
                    [Key]
                    public int Id {{ get; set; }}
                    
                    {self._generate_model_properties(config.get('properties', []))}
            
                    public DateTime CreatedAt {{ get; set; }} = DateTime.UtcNow;
                    public DateTime? UpdatedAt {{ get; set; }}
                }}
            }}
            '''

    def _generate_properties(self, properties: List[Dict]) -> str:
        """Gera propriedades para ViewModel"""
        props = []
        for prop in properties:
            props.append(f'''
        [ObservableProperty]
        private {prop['type']} _{prop['name'].lower()};''')
        return '\n'.join(props)

    def _generate_commands(self, commands: List[Dict]) -> str:
        """Gera comandos para ViewModel"""
        cmds = []
        for cmd in commands:
            cmds.append(f'''
        [RelayCommand]
        private void {cmd['name']}()
        {{
            // Command implementation
        }}''')
        return '\n'.join(cmds)

    def _generate_model_properties(self, properties: List[Dict]) -> str:
        """Gera propriedades para Model"""
        props = []
        for prop in properties:
            if prop.get('required', False):
                props.append(f'''
        [Required]''')
            if prop.get('maxLength'):
                props.append(f'''
        [MaxLength({prop['maxLength']})]''')
            props.append(f'''
        public {prop['type']} {prop['name']} {{ get; set; }}''')
        return '\n'.join(props)

    def save_template(self, name: str, content: str):
        """Salva um template em arquivo"""
        template_file = self.templates_path / f"{name}.xaml"
        template_file.write_text(content)

    def load_template(self, name: str) -> str:
        """Carrega um template de arquivo"""
        template_file = self.templates_path / f"{name}.xaml"
        if template_file.exists():
            return template_file.read_text()
        return ""