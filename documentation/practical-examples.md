# 🎯 Kallista - Exemplos Práticos

## Exemplo 1: Dashboard de Vendas

### Estrutura do Projeto
```
SalesApp/
├── Models/
│   ├── Sale.cs
│   ├── Product.cs
│   └── Customer.cs
├── ViewModels/
│   ├── DashboardViewModel.cs
│   └── ChartViewModel.cs
├── Views/
│   └── DashboardView.xaml
└── Services/
    ├── SalesService.cs
    └── ReportService.cs
```

### Código de Exemplo

#### 1. Model
```csharp
// Models/Sale.cs
public class Sale
{
    public int Id { get; set; }
    public DateTime Date { get; set; }
    public decimal Amount { get; set; }
    public int CustomerId { get; set; }
    public int ProductId { get; set; }
    
    public Customer Customer { get; set; }
    public Product Product { get; set; }
}
```

#### 2. ViewModel
```csharp
// ViewModels/DashboardViewModel.cs
public class DashboardViewModel : ViewModelBase
{
    private readonly ISalesService _salesService;
    private ObservableCollection<Sale> _recentSales;
    private decimal _totalSales;

    public DashboardViewModel(ISalesService salesService)
    {
        _salesService = salesService;
        LoadDataCommand = new AsyncRelayCommand(LoadData);
    }

    public ObservableCollection<Sale> RecentSales
    {
        get => _recentSales;
        set => SetProperty(ref _recentSales, value);
    }

    public decimal TotalSales
    {
        get => _totalSales;
        set => SetProperty(ref _totalSales, value);
    }

    public IAsyncRelayCommand LoadDataCommand { get; }

    private async Task LoadData()
    {
        var sales = await _salesService.GetRecentSales();
        RecentSales = new ObservableCollection<Sale>(sales);
        TotalSales = sales.Sum(s => s.Amount);
    }
}
```

#### 3. View
```xaml
<!-- Views/DashboardView.xaml -->
<UserControl x:Class="SalesApp.Views.DashboardView"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             xmlns:charts="clr-namespace:SalesApp.Controls.Charts">
    <Grid>
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="*"/>
        </Grid.RowDefinitions>

        <!-- Header -->
        <StackPanel Grid.Row="0" Margin="20">
            <TextBlock Text="Dashboard de Vendas" 
                     FontSize="24" 
                     FontWeight="Bold"/>
            <TextBlock Text="{Binding TotalSales, StringFormat='Total: R$ {0:N2}'}"
                     FontSize="18"/>
        </StackPanel>

        <!-- Content -->
        <Grid Grid.Row="1">
            <Grid.ColumnDefinitions>
                <ColumnDefinition Width="*"/>
                <ColumnDefinition Width="*"/>
            </Grid.ColumnDefinitions>

            <!-- Sales Chart -->
            <charts:SalesChart Grid.Column="0"
                             Data="{Binding RecentSales}"/>

            <!-- Sales List -->
            <DataGrid Grid.Column="1"
                      ItemsSource="{Binding RecentSales}"
                      AutoGenerateColumns="False">
                <DataGrid.Columns>
                    <DataGridTextColumn Header="Data" 
                                      Binding="{Binding Date, StringFormat=d}"/>
                    <DataGridTextColumn Header="Valor" 
                                      Binding="{Binding Amount, StringFormat=C2}"/>
                    <DataGridTextColumn Header="Cliente" 
                                      Binding="{Binding Customer.Name}"/>
                </DataGrid.Columns>
            </DataGrid>
        </Grid>
    </Grid>
</UserControl>
```

## Exemplo 2: Sistema de Login com MVVM

### Estrutura
```
Authentication/
├── Models/
│   └── User.cs
├── ViewModels/
│   └── LoginViewModel.cs
├── Views/
│   └── LoginView.xaml
└── Services/
    ├── AuthService.cs
    └── IAuthService.cs
```

### Implementação

#### 1. Service Interface
```csharp
// Services/IAuthService.cs
public interface IAuthService
{
    Task<bool> LoginAsync(string username, string password);
    Task LogoutAsync();
    Task<User> GetCurrentUserAsync();
}
```

#### 2. ViewModel
```csharp
// ViewModels/LoginViewModel.cs
public class LoginViewModel : ViewModelBase
{
    private readonly IAuthService _authService;
    private readonly INavigationService _navigationService;
    private string _username;
    private string _errorMessage;

    public LoginViewModel(
        IAuthService authService,
        INavigationService navigationService)
    {
        _authService = authService;
        _navigationService = navigationService;
        LoginCommand = new AsyncRelayCommand(LoginAsync, CanLogin);
    }

    public string Username
    {
        get => _username;
        set
        {
            SetProperty(ref _username, value);
            LoginCommand.NotifyCanExecuteChanged();
        }
    }

    public string Password
    {
        private get => SecurePassword?.ToString();
        set
        {
            SecurePassword = value.ToSecureString();
            LoginCommand.NotifyCanExecuteChanged();
        }
    }

    public SecureString SecurePassword { get; private set; }

    public string ErrorMessage
    {
        get => _errorMessage;
        set => SetProperty(ref _errorMessage, value);
    }

    public IAsyncRelayCommand LoginCommand { get; }

    private bool CanLogin()
    {
        return !string.IsNullOrEmpty(Username) && 
               SecurePassword?.Length > 0;
    }

    private async Task LoginAsync()
    {
        try
        {
            ErrorMessage = null;
            var success = await _authService.LoginAsync(
                Username, 
                Password
            );

            if (success)
            {
                await _navigationService.NavigateToAsync("Dashboard");
            }
            else
            {
                ErrorMessage = "Login inválido";
            }
        }
        catch (Exception ex)
        {
            ErrorMessage = "Erro ao realizar login";
            Logger.Error(ex, "Login failed");
        }
    }
}
```

#### 3. View
```xaml
<!-- Views/LoginView.xaml -->
<UserControl x:Class="Authentication.Views.LoginView"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
    <Grid>
        <Border Background="White"
                BorderBrush="{StaticResource PrimaryBrush}"
                BorderThickness="1"
                CornerRadius="8"
                Width="400"
                Padding="20">
            <StackPanel>
                <!-- Logo -->
                <Image Source="/Assets/logo.png"
                       Width="150"
                       Margin="0,0,0,20"/>

                <!-- Username -->
                <TextBlock Text="Usuário"
                         Margin="0,0,0,5"/>
                <TextBox Text="{Binding Username, UpdateSourceTrigger=PropertyChanged}"
                         Margin="0,0,0,15"/>

                <!-- Password -->
                <TextBlock Text="Senha"
                         Margin="0,0,0,5"/>
                <PasswordBox x:Name="PasswordBox"
                           Margin="0,0,0,20"/>

                <!-- Error Message -->
                <TextBlock Text="{Binding ErrorMessage}"
                         Foreground="Red"
                         TextWrapping="Wrap"
                         Margin="0,0,0,15"
                         Visibility="{Binding ErrorMessage, 
                                    Converter={StaticResource NullToVisibilityConverter}}"/>

                <!-- Login Button -->
                <Button Content="Entrar"
                        Command="{Binding LoginCommand}"
                        Style="{StaticResource PrimaryButton}"
                        Height="40"/>
            </StackPanel>
        </Border>
    </Grid>
</UserControl>
```

## Exemplo 3: Gerador de Relatórios

### Estrutura
```
ReportGenerator/
├── Models/
│   ├── ReportTemplate.cs
│   └── ReportData.cs
├── ViewModels/
│   ├── ReportDesignerViewModel.cs
│   └── ReportPreviewViewModel.cs
├── Views/
│   ├── ReportDesignerView.xaml
│   └── ReportPreviewView.xaml
└── Services/
    ├── ReportService.cs
    └── ExportService.cs
```

[Continua com implementação detalhada do gerador de relatórios...]

Gostaria que eu continue com mais exemplos práticos ou podemos prosseguir com os Guias de Deployment?