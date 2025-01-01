# tools/wpf/templates/views/main_window.py
class MainWindowTemplate:
    @staticmethod
    def xaml(project_name: str) -> str:
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

    @staticmethod
    def code_behind(project_name: str) -> str:
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