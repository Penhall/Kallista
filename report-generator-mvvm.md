# 📊 Gerador de Relatórios (Modern MVVM)

## Models

```csharp
// Models/ReportTemplate.cs
public class ReportTemplate
{
    public int Id { get; init; }
    public string Name { get; init; }
    public string Description { get; init; }
    public List<ReportSection> Sections { get; init; } = new();
    public ReportOptions Options { get; init; }
}

// Models/ReportSection.cs
public class ReportSection
{
    public string Title { get; init; }
    public ReportSectionType Type { get; init; }
    public Dictionary<string, object> Properties { get; init; }
    public string DataSource { get; init; }
}

// Models/ReportOptions.cs
public record ReportOptions
{
    public string PaperSize { get; init; } = "A4";
    public string Orientation { get; init; } = "Portrait";
    public bool ShowPageNumbers { get; init; } = true;
    public string HeaderTemplate { get; init; }
    public string FooterTemplate { get; init; }
}

// Enums/ReportSectionType.cs
public enum ReportSectionType
{
    Table,
    Chart,
    Text,
    Image,
    PageBreak
}
```

## ViewModels

```csharp
// ViewModels/ReportDesignerViewModel.cs
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace ReportGenerator.ViewModels;

[ObservableObject]
public partial class ReportDesignerViewModel
{
    private readonly IReportService _reportService;
    private readonly IDialogService _dialogService;
    private readonly ITemplateManager _templateManager;

    [ObservableProperty]
    private ReportTemplate currentTemplate;

    [ObservableProperty]
    private ObservableCollection<ReportSection> availableSections;

    [ObservableProperty]
    private ReportSection selectedSection;

    [ObservableProperty]
    private bool isDirty;

    [ObservableProperty]
    private bool isSaving;

    [ObservableProperty]
    private string statusMessage;

    public ReportDesignerViewModel(
        IReportService reportService,
        IDialogService dialogService,
        ITemplateManager templateManager)
    {
        _reportService = reportService;
        _dialogService = dialogService;
        _templateManager = templateManager;
        
        availableSections = new ObservableCollection<ReportSection>();
    }

    [RelayCommand]
    private async Task LoadTemplateAsync(int templateId)
    {
        try
        {
            var template = await _reportService.GetTemplateAsync(templateId);
            CurrentTemplate = template;
            IsDirty = false;
        }
        catch (Exception ex)
        {
            await _dialogService.ShowErrorAsync("Erro ao carregar template", ex.Message);
        }
    }

    [RelayCommand]
    private void AddSection(ReportSectionType sectionType)
    {
        var section = new ReportSection
        {
            Title = $"Nova Seção {availableSections.Count + 1}",
            Type = sectionType,
            Properties = GetDefaultProperties(sectionType)
        };

        AvailableSections.Add(section);
        SelectedSection = section;
        IsDirty = true;
    }

    [RelayCommand]
    private void RemoveSection(ReportSection section)
    {
        if (AvailableSections.Remove(section))
        {
            if (SelectedSection == section)
                SelectedSection = AvailableSections.FirstOrDefault();
                
            IsDirty = true;
        }
    }

    [RelayCommand]
    private async Task SaveTemplateAsync()
    {
        try
        {
            IsSaving = true;
            StatusMessage = "Salvando template...";

            var template = new ReportTemplate
            {
                Id = CurrentTemplate.Id,
                Name = CurrentTemplate.Name,
                Description = CurrentTemplate.Description,
                Sections = AvailableSections.ToList(),
                Options = CurrentTemplate.Options
            };

            await _reportService.SaveTemplateAsync(template);
            
            IsDirty = false;
            StatusMessage = "Template salvo com sucesso!";
        }
        catch (Exception ex)
        {
            StatusMessage = "Erro ao salvar template";
            await _dialogService.ShowErrorAsync("Erro ao salvar", ex.Message);
        }
        finally
        {
            IsSaving = false;
        }
    }

    [RelayCommand]
    private async Task PreviewReportAsync()
    {
        try
        {
            var preview = await _reportService.GeneratePreviewAsync(CurrentTemplate);
            await _dialogService.ShowReportPreviewAsync(preview);
        }
        catch (Exception ex)
        {
            await _dialogService.ShowErrorAsync("Erro ao gerar preview", ex.Message);
        }
    }

    private Dictionary<string, object> GetDefaultProperties(ReportSectionType type) =>
        type switch
        {
            ReportSectionType.Table => new()
            {
                { "ShowHeaders", true },
                { "EnableSorting", true },
                { "EnableFiltering", false }
            },
            ReportSectionType.Chart => new()
            {
                { "ChartType", "Bar" },
                { "ShowLegend", true },
                { "Height", 300 }
            },
            ReportSectionType.Text => new()
            {
                { "FontSize", 12 },
                { "FontFamily", "Arial" },
                { "TextAlignment", "Left" }
            },
            _ => new Dictionary<string, object>()
        };
}

// ViewModels/ReportPreviewViewModel.cs
[ObservableObject]
public partial class ReportPreviewViewModel
{
    private readonly IReportService _reportService;
    private readonly IExportService _exportService;

    [ObservableProperty]
    private ReportPreview reportPreview;

    [ObservableProperty]
    private int currentPage;

    [ObservableProperty]
    private int totalPages;

    [ObservableProperty]
    private double zoomLevel = 1.0;

    public ReportPreviewViewModel(
        IReportService reportService,
        IExportService exportService)
    {
        _reportService = reportService;
        _exportService = exportService;
    }

    [RelayCommand]
    private void NavigateToPage(int page)
    {
        if (page >= 1 && page <= TotalPages)
            CurrentPage = page;
    }

    [RelayCommand]
    private async Task ExportReportAsync(ExportFormat format)
    {
        try
        {
            var options = new ExportOptions
            {
                Format = format,
                IncludeWatermark = format == ExportFormat.PDF,
                Quality = ExportQuality.High
            };

            var result = await _exportService.ExportAsync(ReportPreview, options);
            
            if (result.Success)
                await _dialogService.ShowSuccessAsync("Relatório exportado com sucesso!");
            else
                await _dialogService.ShowErrorAsync("Falha na exportação", result.ErrorMessage);
        }
        catch (Exception ex)
        {
            await _dialogService.ShowErrorAsync("Erro na exportação", ex.Message);
        }
    }

    [RelayCommand]
    private void AdjustZoom(ZoomAction action)
    {
        ZoomLevel = action switch
        {
            ZoomAction.In => Math.Min(ZoomLevel * 1.2, 3.0),
            ZoomAction.Out => Math.Max(ZoomLevel / 1.2, 0.5),
            ZoomAction.Fit => 1.0,
            _ => ZoomLevel
        };
    }
}
```

## Views

```xaml
<!-- Views/ReportDesignerView.xaml -->
<UserControl x:Class="ReportGenerator.Views.ReportDesignerView"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             xmlns:materialDesign="http://materialdesigninxaml.net/winfx/xaml/themes">
    
    <DockPanel>
        <!-- Toolbar -->
        <ToolBar DockPanel.Dock="Top">
            <Button Command="{Binding SaveTemplateCommand}"
                    ToolTip="Salvar Template">
                <materialDesign:PackIcon Kind="ContentSave" />
            </Button>
            <Separator />
            <Button Command="{Binding PreviewReportCommand}"
                    ToolTip="Visualizar Relatório">
                <materialDesign:PackIcon Kind="FileEye" />
            </Button>
            <ComboBox ItemsSource="{Binding ExportFormats}"
                     SelectedItem="{Binding SelectedExportFormat}"/>
            <Button Command="{Binding ExportReportCommand}"
                    CommandParameter="{Binding SelectedExportFormat}"
                    ToolTip="Exportar Relatório">
                <materialDesign:PackIcon Kind="Export" />
            </Button>
        </ToolBar>

        <!-- Status Bar -->
        <StatusBar DockPanel.Dock="Bottom">
            <TextBlock Text="{Binding StatusMessage}" />
            <ProgressBar IsIndeterminate="True"
                        Width="100"
                        Margin="10,0"
                        Visibility="{Binding IsSaving, Converter={StaticResource BoolToVisibilityConverter}}" />
        </StatusBar>

        <!-- Main Content -->
        <Grid>
            <Grid.ColumnDefinitions>
                <ColumnDefinition Width="250" />
                <ColumnDefinition Width="*" />
                <ColumnDefinition Width="300" />
            </Grid.ColumnDefinitions>

            <!-- Available Sections -->
            <DockPanel Grid.Column="0">
                <TextBlock DockPanel.Dock="Top"
                         Text="Seções Disponíveis"
                         Style="{StaticResource MaterialDesignHeadline6TextBlock}"
                         Margin="10" />
                
                <ListView ItemsSource="{Binding AvailableSections}"
                         SelectedItem="{Binding SelectedSection}">
                    <ListView.ItemTemplate>
                        <DataTemplate>
                            <StackPanel Orientation="Horizontal">
                                <materialDesign:PackIcon Kind="{Binding Type, 
                                    Converter={StaticResource SectionTypeToIconConverter}}" />
                                <TextBlock Text="{Binding Title}"
                                         Margin="10,0" />
                            </StackPanel>
                        </DataTemplate>
                    </ListView.ItemTemplate>
                </ListView>
            </DockPanel>

            <!-- Design Surface -->
            <ScrollViewer Grid.Column="1"
                         HorizontalScrollBarVisibility="Auto"
                         VerticalScrollBarVisibility="Auto">
                <ItemsControl ItemsSource="{Binding AvailableSections}">
                    <ItemsControl.ItemTemplate>
                        <DataTemplate>
                            <controls:ReportSectionDesigner 
                                Section="{Binding}" 
                                IsSelected="{Binding DataContext.SelectedSection, 
                                    RelativeSource={RelativeSource AncestorType=ItemsControl}, 
                                    Converter={StaticResource EqualityConverter}, 
                                    ConverterParameter={Binding}}" />
                        </DataTemplate>
                    </ItemsControl.ItemTemplate>
                </ItemsControl>
            </ScrollViewer>

            <!-- Properties -->
            <DockPanel Grid.Column="2">
                <TextBlock DockPanel.Dock="Top"
                         Text="Propriedades"
                         Style="{StaticResource MaterialDesignHeadline6TextBlock}"
                         Margin="10" />
                
                <ScrollViewer>
                    <controls:PropertyGrid 
                        SelectedObject="{Binding SelectedSection}" />
                </ScrollViewer>
            </DockPanel>
        </Grid>
    </DockPanel>
</UserControl>

<!-- Views/ReportPreviewView.xaml -->
<UserControl x:Class="ReportGenerator.Views.ReportPreviewView"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             xmlns:materialDesign="http://materialdesigninxaml.net/winfx/xaml/themes">
    
    <DockPanel>
        <!-- Preview Toolbar -->
        <ToolBar DockPanel.Dock="Top">
            <Button Command="{Binding NavigateToPageCommand}"
                    CommandParameter="{Binding CurrentPage, Converter={StaticResource DecrementConverter}}"
                    ToolTip="Página Anterior">
                <materialDesign:PackIcon Kind="ChevronLeft" />
            </Button>
            
            <TextBlock VerticalAlignment="Center"
                     Margin="10,0">
                <Run Text="Página" />
                <Run Text="{Binding CurrentPage}" />
                <Run Text="de" />
                <Run Text="{Binding TotalPages}" />
            </TextBlock>
            
            <Button Command="{Binding NavigateToPageCommand}"
                    CommandParameter="{Binding CurrentPage, Converter={StaticResource IncrementConverter}}"
                    ToolTip="Próxima Página">
                <materialDesign:PackIcon Kind="ChevronRight" />
            </Button>
            
            <Separator />
            
            <Button Command="{Binding AdjustZoomCommand}"
                    CommandParameter="ZoomIn"
                    ToolTip="Aumentar Zoom">
                <materialDesign:PackIcon Kind="MagnifyPlus" />
            </Button>
            
            <ComboBox SelectedValue="{Binding ZoomLevel}"
                     Width="80">
                <ComboBoxItem Content="50%" Value="0.5" />
                <ComboBoxItem Content="100%" Value="1.0" />
                <ComboBoxItem Content="150%" Value="1.5" />
                <ComboBoxItem Content="200%" Value="2.0" />
            </ComboBox>
            
            <Button Command="{Binding AdjustZoomCommand}"
                    CommandParameter="ZoomOut"
                    ToolTip="Diminuir Zoom">
                <materialDesign:PackIcon Kind="MagnifyMinus" />
            </Button>
        </ToolBar>

        <!-- Preview Content -->
        <ScrollViewer HorizontalScrollBarVisibility="Auto"
                     VerticalScrollBarVisibility="Auto">
            <controls:ReportPreviewControl 
                Report="{Binding ReportPreview}"
                CurrentPage="{Binding CurrentPage}"
                ZoomLevel="{Binding ZoomLevel}" />
        </ScrollViewer>
    </DockPanel>
</UserControl>
```

Este exemplo do Gerador de Relatórios demonstra:

1. **Uso avançado do CommunityToolkit.MVVM**
   - Source Generators para propriedades e comandos
   - Notificações automáticas de mudanças
   - Comandos assíncronos

2. **Padrões de Design**
   - MVVM completo
   - Injeção de Dependência
   - Separação de responsabilidades