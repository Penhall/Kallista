# integrations/visual_studio/project_system.py
from typing import Dict, List
from pathlib import Path
import json

class VSProjectSystem:
    def __init__(self):
        self.templates_path = Path("ProjectTemplates")
        self.templates_path.mkdir(exist_ok=True)

    def generate_project_template(self, config: Dict) -> Dict[str, str]:
        """Gera template de projeto WPF"""
        templates = {}
        
        # Gera arquivo .vstemplate
        templates['template'] = self._generate_vstemplate(config)
        
        # Gera projeto .csproj
        templates['project'] = self._generate_csproj(config)
        
        # Gera arquivos base
        templates.update(self._generate_base_files(config))
        
        return templates

    def _generate_vstemplate(self, config: Dict) -> str:
        """Gera arquivo .vstemplate"""
        vstemplate = ET.Element("VSTemplate")
        vstemplate.set("Version", "3.0.0")
        vstemplate.set("Type", "Project")
        
        template_data = ET.SubElement(vstemplate, "TemplateData")
        
        name = ET.SubElement(template_data, "Name")
        name.text = config['name']
        
        description = ET.SubElement(template_data, "Description")
        description.text = config['description']
        
        project_type = ET.SubElement(template_data, "ProjectType")
        project_type.text = "CSharp"
        
        template_id = ET.SubElement(template_data, "TemplateID")
        template_id.text = config['template_id']
        
        # Template Content
        template_content = ET.SubElement(vstemplate, "TemplateContent")
        
        project = ET.SubElement(template_content, "Project")
        project.set("File", f"{config['name']}.csproj")
        project.set("ReplaceParameters", "true")
        
        return ET.tostring(vstemplate, encoding="unicode", method="xml")

    def _generate_csproj(self, config: Dict) -> str:
        """Gera arquivo .csproj"""
        return f'''<Project Sdk="Microsoft.NET.Sdk">
    <PropertyGroup>
        <OutputType>WinExe</OutputType>
        <TargetFramework>{config.get("target_framework", "net6.0-windows")}</TargetFramework>
        <UseWPF>true</UseWPF>
        <RootNamespace>$safeprojectname$</RootNamespace>
        <AssemblyName>$safeprojectname$</AssemblyName>
    </PropertyGroup>

    <ItemGroup>
        {self._generate_package_references(config)}
    </ItemGroup>

    <ItemGroup>
        {self._generate_item_groups(config)}
    </ItemGroup>
</Project>'''

    def _generate_package_references(self, config: Dict) -> str:
        """Gera referências de pacotes NuGet"""
        refs = []
        for package in config.get('packages', []):
            refs.append(
                f'<PackageReference Include="{package["name"]}" '
                f'Version="{package["version"]}" />'
            )
        return '\n        '.join(refs)

    def _generate_base_files(self, config: Dict) -> Dict[str, str]:
        """Gera arquivos base do projeto"""
        files = {}
        
        # App.xaml
        files['App.xaml'] = f'''<Application x:Class="$safeprojectname$.App"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             StartupUri="Views/MainWindow.xaml">
    <Application.Resources>
        <ResourceDictionary>
            <ResourceDictionary.MergedDictionaries>
                <ResourceDictionary Source="Themes/Colors.xaml"/>
                <ResourceDictionary Source="Themes/Styles.xaml"/>
            </ResourceDictionary.MergedDictionaries>
        </ResourceDictionary>
    </Application.Resources>
</Application>'''

        # App.xaml.cs
        files['App.xaml.cs'] = '''using System.Windows;

namespace $safeprojectname$
{
    public partial class App : Application
    {
        protected override void OnStartup(StartupEventArgs e)
        {
            base.OnStartup(e);
            ConfigureServices();
        }

        private void ConfigureServices()
        {
            // Configure DI and services here
        }
    }
}'''

        # MainWindow.xaml
        files['Views/MainWindow.xaml'] = f'''<Window x:Class="$safeprojectname$.Views.MainWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="{config['window_title']}" Height="450" Width="800">
    <Grid>
        <!-- Initial content -->
    </Grid>
</Window>'''

        # MainWindow.xaml.cs
        files['Views/MainWindow.xaml.cs'] = '''using System.Windows;

namespace $safeprojectname$.Views
{
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
        }
    }
}'''

        # Add other base files based on config
        if config.get('include_mvvm', True):
            files.update(self._generate_mvvm_files())
        
        return files

    def _generate_mvvm_files(self) -> Dict[str, str]:
        """Gera arquivos base para MVVM"""
        files = {}
        
        # Base ViewModel
        files['ViewModels/ViewModelBase.cs'] = '''using System.ComponentModel;
using System.Runtime.CompilerServices;

namespace $safeprojectname$.ViewModels
{
    public class ViewModelBase : INotifyPropertyChanged
    {
        public event PropertyChangedEventHandler PropertyChanged;

        protected virtual void OnPropertyChanged([CallerMemberName] string propertyName = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }
    }
}'''

        # MainViewModel
        files['ViewModels/MainViewModel.cs'] = '''namespace $safeprojectname$.ViewModels
{
    public class MainViewModel : ViewModelBase
    {
        public MainViewModel()
        {
            // Initialize properties and commands
        }
    }
}'''
        
        return files

    def save_templates(self, templates: Dict[str, str], name: str):
        """Salva templates em arquivos"""
        template_dir = self.templates_path / name
        template_dir.mkdir(exist_ok=True)
        
        for filename, content in templates.items():
            file_path = template_dir / filename
            file_path.parent.mkdir(exist_ok=True)
            file_path.write_text(content)