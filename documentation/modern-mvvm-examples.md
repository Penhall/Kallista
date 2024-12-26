# 🎯 Kallista - Exemplos Práticos (Modern MVVM)

## Exemplo 1: Dashboard de Vendas

### Models
```csharp
public class Sale
{
    public int Id { get; init; }
    public DateTime Date { get; init; }
    public decimal Amount { get; init; }
    public int CustomerId { get; init; }
    public int ProductId { get; init; }
    
    public Customer Customer { get; init; }
    public Product Product { get; init; }
}

public class SalesSummary
{
    public decimal TotalAmount { get; init; }
    public int TotalSales { get; init; }
    public decimal AverageTicket { get; init; }
}
```

### ViewModel
```csharp
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace SalesApp.ViewModels;

[ObservableObject]
public partial class DashboardViewModel
{
    private readonly ISalesService _salesService;
    private readonly IDialogService _dialogService;

    [ObservableProperty]
    private ObservableCollection<Sale> recentSales;

    [ObservableProperty]
    private SalesSummary salesSummary;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(IsLoading))]
    private bool isDataLoaded;

    [ObservableProperty]
    private bool isLoading;

    [ObservableProperty]
    private string errorMessage;

    public DashboardViewModel(
        ISalesService salesService,
        IDialogService dialogService)
    {
        _salesService = salesService;
        _dialogService = dialogService;
    }

    [RelayCommand]
    private async Task LoadDataAsync(CancellationToken cancellationToken)
    {
        try
        {
            IsLoading = true;
            ErrorMessage = null;

            var sales = await _salesService.GetRecentSalesAsync(cancellationToken);
            RecentSales = new ObservableCollection<Sale>(sales);

            SalesSummary = new SalesSummary
            {
                TotalAmount = sales.Sum(s => s.Amount),
                TotalSales = sales.Count,
                AverageTicket = sales.Any() 
                    ? sales.Average(s => s.Amount) 
                    : 0
            };

            IsDataLoaded = true;
        }
        catch (OperationCanceledException)
        {
            ErrorMessage = "Operação cancelada";
        }
        catch (Exception ex)
        {
            ErrorMessage = "Erro ao carregar dados";
            await _dialogService.ShowErrorAsync(ex.Message);
        }
        finally
        {
            IsLoading = false;
        }
    }

    [RelayCommand]
    private async Task ExportReportAsync()
    {
        if (!RecentSales?.Any() ?? true)
        {
            await _dialogService.ShowWarningAsync("Não há dados para exportar");
            return;
        }

        try
        {
            var options = new ExportOptions
            {
                Format = ExportFormat.Excel,
                IncludeCharts = true
            };

            await _salesService.ExportReportAsync(RecentSales, options);
            await _dialogService.ShowSuccessAsync("Relatório exportado com sucesso");
        }
        catch (Exception ex)
        {
            await _dialogService.ShowErrorAsync($"Erro ao exportar: {ex.Message}");
        }
    }
}
```

### View
```xaml
<UserControl x:Class="SalesApp.Views.DashboardView"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
             xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
             xmlns:vm="clr-namespace:SalesApp.ViewModels"
             xmlns:converters="clr-namespace:SalesApp.Converters"
             mc:Ignorable="d"
             d:DataContext="{d:DesignInstance Type=vm:DashboardViewModel}">
    
    <Grid>
        <!-- Loading Overlay -->
        <Rectangle Fill="#80000000" 
                   Visibility="{Binding IsLoading, Converter={StaticResource BoolToVisibilityConverter}}"/>
        <ProgressBar IsIndeterminate="True" 
                    Visibility="{Binding IsLoading, Converter={StaticResource BoolToVisibilityConverter}}"/>

        <!-- Main Content -->
        <DockPanel LastChildFill="True">
            <!-- Header -->
            <StackPanel DockPanel.Dock="Top" Margin="20">
                <TextBlock Text="Dashboard de Vendas" 
                         Style="{StaticResource HeaderTextBlockStyle}"/>
                
                <!-- Actions -->
                <ToolBar>
                    <Button Content="Atualizar" 
                            Command="{Binding LoadDataCommand}"/>
                    <Button Content="Exportar" 
                            Command="{Binding ExportReportCommand}"
                            IsEnabled="{Binding IsDataLoaded}"/>
                </ToolBar>
                
                <!-- Error Message -->
                <TextBlock Text="{Binding ErrorMessage}"
                         Foreground="Red"
                         Visibility="{Binding ErrorMessage, Converter={StaticResource NullToVisibilityConverter}}"/>
            </StackPanel>

            <!-- Summary Cards -->
            <UniformGrid DockPanel.Dock="Top" 
                        Rows="1" 
                        Margin="20,0">
                <controls:SummaryCard 
                    Title="Total de Vendas"
                    Value="{Binding SalesSummary.TotalAmount, StringFormat=C2}"/>
                <controls:SummaryCard 
                    Title="Quantidade"
                    Value="{Binding SalesSummary.TotalSales, StringFormat=N0}"/>
                <controls:SummaryCard 
                    Title="Ticket Médio"
                    Value="{Binding SalesSummary.AverageTicket, StringFormat=C2}"/>
            </UniformGrid>

            <!-- Content -->
            <Grid DockPanel.Dock="Bottom">
                <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="*"/>
                    <ColumnDefinition Width="*"/>
                </Grid.ColumnDefinitions>

                <!-- Chart -->
                <charts:SalesChart 
                    Grid.Column="0"
                    Data="{Binding RecentSales}"/>

                <!-- Data Grid -->
                <DataGrid 
                    Grid.Column="1"
                    ItemsSource="{Binding RecentSales}"
                    AutoGenerateColumns="False"
                    IsReadOnly="True">
                    <DataGrid.Columns>
                        <DataGridTextColumn Header="Data" 
                                          Binding="{Binding Date, StringFormat=d}"/>
                        <DataGridTextColumn Header="Cliente" 
                                          Binding="{Binding Customer.Name}"/>
                        <DataGridTextColumn Header="Valor" 
                                          Binding="{Binding Amount, StringFormat=C2}"/>
                    </DataGrid.Columns>
                </DataGrid>
            </Grid>
        </DockPanel>
    </Grid>
</UserControl>
```

## Exemplo 2: Sistema de Login

### ViewModel
```csharp
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace Authentication.ViewModels;

[ObservableObject]
public partial class LoginViewModel
{
    private readonly IAuthService _authService;
    private readonly INavigationService _navigationService;

    [ObservableProperty]
    [NotifyCanExecuteChangedFor(nameof(LoginCommand))]
    private string username;

    [ObservableProperty]
    private string errorMessage;

    [ObservableProperty]
    private bool isAuthenticating;

    private SecureString _password;
    public SecureString Password
    {
        get => _password;
        set
        {
            _password = value;
            LoginCommand.NotifyCanExecuteChanged();
        }
    }

    public LoginViewModel(
        IAuthService authService,
        INavigationService navigationService)
    {
        _authService = authService;
        _navigationService = navigationService;
    }

    [RelayCommand(CanExecute = nameof(CanLogin))]
    private async Task LoginAsync()
    {
        try
        {
            IsAuthenticating = true;
            ErrorMessage = null;

            var credentials = new LoginCredentials(Username, Password);
            var result = await _authService.LoginAsync(credentials);

            if (result.Success)
            {
                await _navigationService.NavigateToAsync(AppPages.Dashboard);
            }
            else
            {
                ErrorMessage = result.ErrorMessage ?? "Login inválido";
            }
        }
        catch (Exception ex)
        {
            ErrorMessage = "Erro ao realizar login";
            Logger.Error(ex, "Login failed for user {Username}", Username);
        }
        finally
        {
            IsAuthenticating = false;
        }
    }

    private bool CanLogin() =>
        !string.IsNullOrWhiteSpace(Username) && 
        Password?.Length > 0 &&
        !IsAuthenticating;

    [RelayCommand]
    private async Task RecoverPasswordAsync()
    {
        if (string.IsNullOrWhiteSpace(Username))
        {
            ErrorMessage = "Informe o usuário para recuperar a senha";
            return;
        }

        try
        {
            await _authService.RequestPasswordResetAsync(Username);
            await _dialogService.ShowInfoAsync(
                "Instruções de recuperação de senha foram enviadas para seu email.");
        }
        catch (Exception ex)
        {
            ErrorMessage = "Erro ao solicitar recuperação de senha";
            Logger.Error(ex, "Password recovery failed for user {Username}", Username);
        }
    }
}
```

### View
```xaml
<UserControl x:Class="Authentication.Views.LoginView"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             xmlns:materialDesign="http://materialdesigninxaml.net/winfx/xaml/themes">
    
    <materialDesign:Card Width="400" 
                        Padding="20"
                        UniformCornerRadius="8">
        <StackPanel>
            <!-- Logo -->
            <Image Source="{StaticResource LogoImage}"
                   Width="150"
                   Margin="0,0,0,20"/>
            
            <!-- Username -->
            <TextBox Text="{Binding Username, UpdateSourceTrigger=PropertyChanged}"
                     materialDesign:HintAssist.Hint="Usuário"
                     Style="{StaticResource MaterialDesignFloatingHintTextBox}"
                     Margin="0,0,0,15"/>
            
            <!-- Password -->
            <PasswordBox x:Name="PasswordBox"
                        materialDesign:HintAssist.Hint="Senha"
                        Style="{StaticResource MaterialDesignFloatingHintPasswordBox}"
                        Margin="0,0,0,20"/>
            
            <!-- Error Message -->
            <TextBlock Text="{Binding ErrorMessage}"
                      Foreground="{StaticResource ErrorBrush}"
                      TextWrapping="Wrap"
                      Margin="0,0,0,15"
                      Visibility="{Binding ErrorMessage, 
                                 Converter={StaticResource NullToVisibilityConverter}}"/>
            
            <!-- Login Button -->
            <Button Content="Entrar"
                    Command="{Binding LoginCommand}"
                    Style="{StaticResource MaterialDesignContainedButton}"
                    IsEnabled="{Binding IsAuthenticating, Converter={StaticResource InverseBoolConverter}}"
                    Height="40"/>
            
            <!-- Progress -->
            <ProgressBar IsIndeterminate="True"
                        Margin="0,10"
                        Visibility="{Binding IsAuthenticating, 
                                   Converter={StaticResource BoolToVisibilityConverter}}"/>
            
            <!-- Password Recovery -->
            <Button Content="Esqueci minha senha"
                    Command="{Binding RecoverPasswordCommand}"
                    Style="{StaticResource MaterialDesignFlatButton}"
                    Margin="0,10,0,0"/>
        </StackPanel>
    </materialDesign:Card>
</UserControl>
```

Estes exemplos agora utilizam os recursos modernos do CommunityToolkit.MVVM, incluindo:

1. Atributos Source Generators:
   - `[ObservableObject]`
   - `[ObservableProperty]`
   - `[RelayCommand]`
   - `[NotifyCanExecuteChangedFor]`
   - `[NotifyPropertyChangedFor]`

2. Features modernas:
   - Async command support
   - Strong typing
   - Property change notifications
   - Command enable/disable logic

3. Integração com Material Design:
   - Cards
   - Floating hint text boxes
   - Progress indicators
   - Modern styling

Gostaria que eu continue com o exemplo do Gerador de Relatórios também atualizado com CommunityToolkit.MVVM?