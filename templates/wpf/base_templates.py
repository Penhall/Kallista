# templates/wpf/base_templates.py
from typing import Dict, Any
from pathlib import Path
import json

class WpfTemplates:
    def __init__(self):
        self.templates_path = Path("templates/wpf")
        self.templates_path.mkdir(parents=True, exist_ok=True)

    def get_window_template(self, config: Dict[str, Any]) -> str:
        """Gera template base para uma janela WPF"""
        return f'''
<Window x:Class="{config['namespace']}.{config['name']}"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
        xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
        xmlns:local="clr-namespace:{config['namespace']}"
        mc:Ignorable="d"
        Title="{config['title']}" Height="{config['height']}" Width="{config['width']}"
        WindowStartupLocation="CenterScreen">
    
    <Window.Resources>
        <ResourceDictionary>
            <ResourceDictionary.MergedDictionaries>
                <ResourceDictionary Source="/Styles/Colors.xaml"/>
                <ResourceDictionary Source="/Styles/Buttons.xaml"/>
                <ResourceDictionary Source="/Styles/TextBlocks.xaml"/>
            </ResourceDictionary.MergedDictionaries>
        </ResourceDictionary>
    </Window.Resources>

    <Grid>
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="*"/>
            <RowDefinition Height="Auto"/>
        </Grid.RowDefinitions>

        <!-- Header -->
        <Border Grid.Row="0" Style="{{StaticResource HeaderBorderStyle}}">
            <TextBlock Text="{config['title']}" Style="{{StaticResource HeaderTextStyle}}"/>
        </Border>

        <!-- Main Content -->
        <Grid Grid.Row="1" Margin="10">
            <!-- Content goes here -->
        </Grid>

        <!-- Footer -->
        <StatusBar Grid.Row="2">
            <StatusBarItem>
                <TextBlock Text="{{Binding StatusMessage}}"/>
            </StatusBarItem>
        </StatusBar>
    </Grid>
</Window>
'''

    def get_view_model_template(self, config: Dict[str, Any]) -> str:
        """Gera template base para um ViewModel"""
        return f'''
using System;
using System.Windows.Input;
using System.ComponentModel;
using System.Runtime.CompilerServices;
using System.Collections.ObjectModel;

namespace {config['namespace']}.ViewModels
{{
    public class {config['name']}ViewModel : INotifyPropertyChanged
    {{
        private readonly IServiceProvider _serviceProvider;
        private string _statusMessage;

        public {config['name']}ViewModel(IServiceProvider serviceProvider)
        {{
            _serviceProvider = serviceProvider;
            InitializeCommands();
        }}

        #region Properties

        public string StatusMessage
        {{
            get => _statusMessage;
            set
            {{
                _statusMessage = value;
                OnPropertyChanged();
            }}
        }}

        #endregion

        #region Commands

        public ICommand SaveCommand {{ get; private set; }}
        public ICommand LoadCommand {{ get; private set; }}

        private void InitializeCommands()
        {{
            SaveCommand = new RelayCommand(ExecuteSave, CanExecuteSave);
            LoadCommand = new RelayCommand(ExecuteLoad, CanExecuteLoad);
        }}

        #endregion

        #region Command Implementations

        private bool CanExecuteSave() => true;
        private bool CanExecuteLoad() => true;

        private async void ExecuteSave()
        {{
            try
            {{
                StatusMessage = "Salvando...";
                // Implementação
                StatusMessage = "Salvo com sucesso!";
            }}
            catch (Exception ex)
            {{
                StatusMessage = $"Erro: {{ex.Message}}";
            }}
        }}

        private async void ExecuteLoad()
        {{
            try
            {{
                StatusMessage = "Carregando...";
                // Implementação
                StatusMessage = "Carregado com sucesso!";
            }}
            catch (Exception ex)
            {{
                StatusMessage = $"Erro: {{ex.Message}}";
            }}
        }}

        #endregion

        #region INotifyPropertyChanged

        public event PropertyChangedEventHandler PropertyChanged;

        protected virtual void OnPropertyChanged([CallerMemberName] string propertyName = null)
        {{
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }}

        #endregion
    }}
}}
'''

    def get_model_template(self, config: Dict[str, Any]) -> str:
        """Gera template base para um Model"""
        return f'''
using System;
using System.ComponentModel.DataAnnotations;

namespace {config['namespace']}.Models
{{
    public class {config['name']}
    {{
        [Key]
        public int Id {{ get; set; }}

        [Required]
        [StringLength(100)]
        public string Name {{ get; set; }}

        public DateTime CreatedAt {{ get; set; }} = DateTime.UtcNow;
        public DateTime? UpdatedAt {{ get; set; }}

        // Add more properties here
    }}
}}
'''

    def get_service_interface_template(self, config: Dict[str, Any]) -> str:
        """Gera template base para uma interface de serviço"""
        return f'''
using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using {config['namespace']}.Models;

namespace {config['namespace']}.Services
{{
    public interface I{config['name']}Service
    {{
        Task<IEnumerable<{config['name']}>> GetAllAsync();
        Task<{config['name']}> GetByIdAsync(int id);
        Task<{config['name']}> CreateAsync({config['name']} entity);
        Task UpdateAsync({config['name']} entity);
        Task DeleteAsync(int id);
    }}
}}
'''

    def get_style_dictionary_template(self) -> str:
        """Gera template base para dicionário de estilos"""
        return '''
<ResourceDictionary xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
                    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
    
    <!-- Colors -->
    <Color x:Key="PrimaryColor">#007ACC</Color>
    <Color x:Key="SecondaryColor">#5C2D91</Color>
    <Color x:Key="BackgroundColor">#FFFFFF</Color>
    <Color x:Key="TextColor">#000000</Color>
    <Color x:Key="AccentColor">#FFB900</Color>

    <!-- Brushes -->
    <SolidColorBrush x:Key="PrimaryBrush" Color="{StaticResource PrimaryColor}"/>
    <SolidColorBrush x:Key="SecondaryBrush" Color="{StaticResource SecondaryColor}"/>
    <SolidColorBrush x:Key="BackgroundBrush" Color="{StaticResource BackgroundColor}"/>
    <SolidColorBrush x:Key="TextBrush" Color="{StaticResource TextColor}"/>
    <SolidColorBrush x:Key="AccentBrush" Color="{StaticResource AccentColor}"/>

    <!-- Text Styles -->
    <Style x:Key="HeaderTextStyle" TargetType="TextBlock">
        <Setter Property="FontFamily" Value="Segoe UI Light"/>
        <Setter Property="FontSize" Value="24"/>
        <Setter Property="Margin" Value="10"/>
        <Setter Property="Foreground" Value="{StaticResource TextBrush}"/>
    </Style>

    <!-- Button Styles -->
    <Style x:Key="DefaultButtonStyle" TargetType="Button">
        <Setter Property="Background" Value="{StaticResource PrimaryBrush}"/>
        <Setter Property="Foreground" Value="White"/>
        <Setter Property="Padding" Value="15,5"/>
        <Setter Property="BorderThickness" Value="0"/>
        <Setter Property="Template">
            <Setter.Value>
                <ControlTemplate TargetType="Button">
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
                <Setter Property="Background" Value="{StaticResource SecondaryBrush}"/>
            </Trigger>
        </Style.Triggers>
    </Style>
</ResourceDictionary>
'''

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