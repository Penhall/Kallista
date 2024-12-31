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