# templates/uiux/ui_templates.py
from typing import Dict, Any
from pathlib import Path

class UiTemplates:
    def __init__(self):
        self.templates_path = Path("templates/uiux")
        self.templates_path.mkdir(parents=True, exist_ok=True)

    def get_theme_template(self, config: Dict[str, Any]) -> str:
        """Gera template para tema de UI"""
        return f'''
<ResourceDictionary
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">

    <!-- Color Palette -->
    <Color x:Key="Primary">{config.get('primary_color', '#007ACC')}</Color>
    <Color x:Key="Secondary">{config.get('secondary_color', '#5C2D91')}</Color>
    <Color x:Key="Accent">{config.get('accent_color', '#FFB900')}</Color>
    <Color x:Key="Background">{config.get('background_color', '#FFFFFF')}</Color>
    <Color x:Key="Surface">{config.get('surface_color', '#F5F5F5')}</Color>
    <Color x:Key="Error">{config.get('error_color', '#DC3545')}</Color>
    <Color x:Key="Success">{config.get('success_color', '#28A745')}</Color>
    <Color x:Key="Warning">{config.get('warning_color', '#FFC107')}</Color>
    <Color x:Key="Info">{config.get('info_color', '#17A2B8')}</Color>

    <!-- Text Colors -->
    <Color x:Key="TextPrimary">{config.get('text_primary_color', '#212121')}</Color>
    <Color x:Key="TextSecondary">{config.get('text_secondary_color', '#757575')}</Color>
    <Color x:Key="TextDisabled">{config.get('text_disabled_color', '#9E9E9E')}</Color>

    <!-- Brushes -->
    <SolidColorBrush x:Key="PrimaryBrush" Color="{{StaticResource Primary}}"/>
    <SolidColorBrush x:Key="SecondaryBrush" Color="{{StaticResource Secondary}}"/>
    <SolidColorBrush x:Key="AccentBrush" Color="{{StaticResource Accent}}"/>
    <SolidColorBrush x:Key="BackgroundBrush" Color="{{StaticResource Background}}"/>
    <SolidColorBrush x:Key="SurfaceBrush" Color="{{StaticResource Surface}}"/>
    <SolidColorBrush x:Key="ErrorBrush" Color="{{StaticResource Error}}"/>
    <SolidColorBrush x:Key="SuccessBrush" Color="{{StaticResource Success}}"/>
    <SolidColorBrush x:Key="WarningBrush" Color="{{StaticResource Warning}}"/>
    <SolidColorBrush x:Key="InfoBrush" Color="{{StaticResource Info}}"/>
    <SolidColorBrush x:Key="TextPrimaryBrush" Color="{{StaticResource TextPrimary}}"/>
    <SolidColorBrush x:Key="TextSecondaryBrush" Color="{{StaticResource TextSecondary}}"/>
    <SolidColorBrush x:Key="TextDisabledBrush" Color="{{StaticResource TextDisabled}}"/>

    <!-- Typography -->
    <FontFamily x:Key="PrimaryFontFamily">{config.get('primary_font', 'Segoe UI')}</FontFamily>
    <FontFamily x:Key="SecondaryFontFamily">{config.get('secondary_font', 'Segoe UI Light')}</FontFamily>
    <FontFamily x:Key="MonoFontFamily">{config.get('mono_font', 'Consolas')}</FontFamily>

    <!-- Text Styles -->
    <Style x:Key="HeadingLarge" TargetType="TextBlock">
        <Setter Property="FontFamily" Value="{{StaticResource SecondaryFontFamily}}"/>
        <Setter Property="FontSize" Value="32"/>
        <Setter Property="FontWeight" Value="Light"/>
        <Setter Property="Foreground" Value="{{StaticResource TextPrimaryBrush}}"/>
    </Style>

    <Style x:Key="HeadingMedium" TargetType="TextBlock">
        <Setter Property="FontFamily" Value="{{StaticResource SecondaryFontFamily}}"/>
        <Setter Property="FontSize" Value="24"/>
        <Setter Property="FontWeight" Value="Light"/>
        <Setter Property="Foreground" Value="{{StaticResource TextPrimaryBrush}}"/>
    </Style>

    <Style x:Key="HeadingSmall" TargetType="TextBlock">
        <Setter Property="FontFamily" Value="{{StaticResource PrimaryFontFamily}}"/>
        <Setter Property="FontSize" Value="20"/>
        <Setter Property="FontWeight" Value="Regular"/>
        <Setter Property="Foreground" Value="{{StaticResource TextPrimaryBrush}}"/>
    </Style>

    <Style x:Key="BodyLarge" TargetType="TextBlock">
        <Setter Property="FontFamily" Value="{{StaticResource PrimaryFontFamily}}"/>
        <Setter Property="FontSize" Value="16"/>
        <Setter Property="FontWeight" Value="Regular"/>
        <Setter Property="Foreground" Value="{{StaticResource TextPrimaryBrush}}"/>
    </Style>

    <Style x:Key="BodyRegular" TargetType="TextBlock">
        <Setter Property="FontFamily" Value="{{StaticResource PrimaryFontFamily}}"/>
        <Setter Property="FontSize" Value="14"/>
        <Setter Property="FontWeight" Value="Regular"/>
        <Setter Property="Foreground" Value="{{StaticResource TextPrimaryBrush}}"/>
    </Style>

    <Style x:Key="Caption" TargetType="TextBlock">
        <Setter Property="FontFamily" Value="{{StaticResource PrimaryFontFamily}}"/>
        <Setter Property="FontSize" Value="12"/>
        <Setter Property="FontWeight" Value="Regular"/>
        <Setter Property="Foreground" Value="{{StaticResource TextSecondaryBrush}}"/>
    </Style>

    <!-- Spacing -->
    <Thickness x:Key="SpacingTiny">4</Thickness>
    <Thickness x:Key="SpacingSmall">8</Thickness>
    <Thickness x:Key="SpacingMedium">16</Thickness>
    <Thickness x:Key="SpacingLarge">24</Thickness>
    <Thickness x:Key="SpacingXLarge">32</Thickness>

    <!-- Elevations/Shadows -->
    <DropShadowEffect x:Key="ElevationLow" Direction="270" ShadowDepth="2" BlurRadius="4" Opacity="0.2"/>
    <DropShadowEffect x:Key="ElevationMedium" Direction="270" ShadowDepth="4" BlurRadius="8" Opacity="0.2"/>
    <DropShadowEffect x:Key="ElevationHigh" Direction="270" ShadowDepth="8" BlurRadius="16" Opacity="0.2"/>
</ResourceDictionary>
'''

    def get_accessibility_template(self) -> str:
        """Gera template para configurações de acessibilidade"""
        return '''
<ResourceDictionary
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">

    <!-- High Contrast Colors -->
    <SolidColorBrush x:Key="HighContrastBackgroundBrush" Color="#000000"/>
    <SolidColorBrush x:Key="HighContrastForegroundBrush" Color="#FFFFFF"/>
    <SolidColorBrush x:Key="HighContrastAccentBrush" Color="#FFB900"/>

    <!-- Focus Visual Styles -->
    <Style x:Key="AccessibleFocusVisual">
        <Setter Property="Control.Template">
            <Setter.Value>
                <ControlTemplate>
                    <Rectangle StrokeThickness="2" Stroke="{DynamicResource HighContrastAccentBrush}"
                             StrokeDashArray="1 2" SnapsToDevicePixels="true"/>
                </ControlTemplate>
            </Setter.Value>
        </Setter>
    </Style>

    <!-- Accessible Button Style -->
    <Style x:Key="AccessibleButton" TargetType="Button">
        <Setter Property="MinWidth" Value="44"/>
        <Setter Property="MinHeight" Value="44"/>
        <Setter Property="Padding" Value="16,8"/>
        <Setter Property="FocusVisualStyle" Value="{StaticResource AccessibleFocusVisual}"/>
        <Setter Property="AutomationProperties.Name" Value="{Binding Content, RelativeSource={RelativeSource Self}}"/>
    </Style>

    <!-- Accessible TextBox Style -->
    <Style x:Key="AccessibleTextBox" TargetType="TextBox">
        <Setter Property="MinHeight" Value="44"/>
        <Setter Property="Padding" Value="8,4"/>
        <Setter Property="FocusVisualStyle" Value="{StaticResource AccessibleFocusVisual}"/>
    </Style>

    <!-- Screen Reader Text -->
    <Style x:Key="ScreenReaderOnly" TargetType="TextBlock">
        <Setter Property="Visibility" Value="Collapsed"/>
        <Setter Property="AutomationProperties.LiveSetting" Value="Polite"/>
    </Style>
</ResourceDictionary>
'''

    def get_layout_template(self, config: Dict[str, Any]) -> str:
        """Gera template para layouts padrão"""
        return f'''
<ResourceDictionary
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">

    <!-- Grid Layout Templates -->
    <Style x:Key="StandardGrid" TargetType="Grid">
        <Setter Property="Margin" Value="{{StaticResource SpacingMedium}}"/>
        <Setter Property="HorizontalAlignment" Value="Stretch"/>
        <Setter Property="VerticalAlignment" Value="Stretch"/>
    </Style>

    <!-- Responsive Grid -->
    <Style x:Key="ResponsiveGrid" TargetType="Grid">
        <Style.Triggers>
            <DataTrigger Binding="{{Binding ActualWidth, RelativeSource={{RelativeSource FindAncestor, AncestorType={{x:Type Window}}}}}}">
                <DataTrigger.EnterActions>
                    <!-- Responsive layout actions -->
                </DataTrigger.EnterActions>
            </DataTrigger>
        </Style.Triggers>
    </Style>

    <!-- Form Layout -->
    <Style x:Key="FormGrid" TargetType="Grid">
        <Setter Property="Margin" Value="{{StaticResource SpacingMedium}}"/>
        <Setter Property="HorizontalAlignment" Value="Left"/>
        <Setter Property="Width" Value="Auto"/>
        <Setter Property="MaxWidth" Value="600"/>
    </Style>

    <!-- Content Panels -->
    <Style x:Key="ContentPanel" TargetType="StackPanel">
        <Setter Property="Margin" Value="{{StaticResource SpacingMedium}}"/>
        <Setter Property="Orientation" Value="Vertical"/>
        <Setter Property="HorizontalAlignment" Value="Stretch"/>
    </Style>

    <!-- Navigation Panel -->
    <Style x:Key="NavigationPanel" TargetType="StackPanel">
        <Setter Property="Orientation" Value="Vertical"/>
        <Setter Property="Background" Value="{{StaticResource SurfaceBrush}}"/>
        <Setter Property="Width" Value="{config.get('nav_width', '250')}"/>
    </Style>
</ResourceDictionary>
'''

    def get_interaction_template(self) -> str:
        """Gera template para padrões de interação"""
        return '''
<ResourceDictionary
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">

    <!-- Interactive Button -->
    <Style x:Key="InteractiveButton" TargetType="Button">
        <Setter Property="Background" Value="{DynamicResource PrimaryBrush}"/>
        <Setter Property="Foreground" Value="White"/>
        <Setter Property="Padding" Value="{DynamicResource SpacingSmall}"/>
        <Setter Property="BorderThickness" Value="0"/>
        <Setter Property="Template">
            <Setter.Value>
                <ControlTemplate TargetType="Button">
                    <Border Background="{TemplateBinding Background}"
                            BorderBrush="{TemplateBinding BorderBrush}"
                            BorderThickness="{TemplateBinding BorderThickness}"
                            CornerRadius="4">
                        <ContentPresenter HorizontalAlignment="Center" 
                                        VerticalAlignment="Center"/>
                    </Border>
                    <ControlTemplate.Triggers>
                        <Trigger Property="IsMouseOver" Value="True">
                            <Setter Property="Background" Value="{DynamicResource SecondaryBrush}"/>
                            <Setter Property="Cursor" Value="Hand"/>
                        </Trigger>
                        <Trigger Property="IsPressed" Value="True">
                            <Setter Property="Background" Value="{DynamicResource AccentBrush}"/>
                        </Trigger>
                        <Trigger Property="IsEnabled" Value="False">
                            <Setter Property="Opacity" Value="0.5"/>
                        </Trigger>
                    </ControlTemplate.Triggers>
                </ControlTemplate>
            </Setter.Value>
        </Setter>
    </Style>

    <!-- Loading Indicator -->
    <Style x:Key="LoadingSpinner" TargetType="Control">
        <Setter Property="Template">
            <Setter.Value>
                <ControlTemplate TargetType="Control">
                    <Grid>
                        <Ellipse Width="40" Height="40" 
                                Stroke="{DynamicResource PrimaryBrush}"
                                StrokeThickness="4">
                            <Ellipse.RenderTransform>
                                <RotateTransform x:Name="SpinnerRotate" 
                                               Angle="0"/>
                            </Ellipse.RenderTransform>
                        </Ellipse>
                    </Grid>
                    <ControlTemplate.Triggers>
                        <Trigger Property="IsVisible" Value="True">
                            <Trigger.EnterActions>
                                <BeginStoryboard>
                                    <Storyboard>
                                        <DoubleAnimation 
                                            Storyboard.TargetName="SpinnerRotate"
                                            Storyboard.TargetProperty="Angle"
                                            From="0" To="360" Duration="0:0:1"
                                            RepeatBehavior="Forever"/>
                                    </Storyboard>
                                </BeginStoryboard>
                            </Trigger.EnterActions>
                        </Trigger>
                    </ControlTemplate.Triggers>
                </ControlTemplate>
            </Setter.Value>
        </Setter>
    </Style>

 <!-- Feedback Overlay -->
    <Style x:Key="FeedbackOverlay" TargetType="Border">
        <Setter Property="Background" Value="#80000000"/>
        <Setter Property="Visibility" Value="Collapsed"/>
        <Setter Property="HorizontalAlignment" Value="Stretch"/>
        <Setter Property="VerticalAlignment" Value="Stretch"/>
        <Style.Triggers>
            <DataTrigger Binding="{Binding IsLoading}" Value="True">
                <Setter Property="Visibility" Value="Visible"/>
            </DataTrigger>
        </Style.Triggers>
    </Style>

    <!-- Tooltip Template -->
    <Style x:Key="EnhancedTooltip" TargetType="ToolTip">
        <Setter Property="Background" Value="{DynamicResource SurfaceBrush}"/>
        <Setter Property="Foreground" Value="{DynamicResource TextPrimaryBrush}"/>
        <Setter Property="BorderBrush" Value="{DynamicResource PrimaryBrush}"/>
        <Setter Property="BorderThickness" Value="1"/>
        <Setter Property="Padding" Value="{DynamicResource SpacingSmall}"/>
        <Setter Property="HasDropShadow" Value="True"/>
    </Style>

    <!-- Error Template -->
    <ControlTemplate x:Key="ErrorTemplate">
        <StackPanel>
            <Border BorderBrush="{DynamicResource ErrorBrush}" 
                    BorderThickness="1">
                <AdornedElementPlaceholder/>
            </Border>
            <TextBlock Foreground="{DynamicResource ErrorBrush}"
                       Text="{Binding [0].ErrorContent}"
                       Margin="0,4,0,0"/>
        </StackPanel>
    </ControlTemplate>

    <!-- Interactive ListView -->
    <Style x:Key="InteractiveListView" TargetType="ListView">
        <Setter Property="Background" Value="Transparent"/>
        <Setter Property="BorderThickness" Value="0"/>
        <Setter Property="ScrollViewer.HorizontalScrollBarVisibility" Value="Disabled"/>
        <Setter Property="ScrollViewer.VerticalScrollBarVisibility" Value="Auto"/>
        <Style.Triggers>
            <Trigger Property="IsMouseOver" Value="True">
                <Setter Property="BorderBrush" Value="{DynamicResource PrimaryBrush}"/>
            </Trigger>
            <Trigger Property="IsEnabled" Value="False">
                <Setter Property="Opacity" Value="0.5"/>
            </Trigger>
        </Style.Triggers>
    </Style>

    <!-- Notification Template -->
    <Style x:Key="NotificationPopup" TargetType="Border">
        <Setter Property="Background" Value="{DynamicResource SurfaceBrush}"/>
        <Setter Property="BorderBrush" Value="{DynamicResource PrimaryBrush}"/>
        <Setter Property="BorderThickness" Value="1"/>
        <Setter Property="CornerRadius" Value="4"/>
        <Setter Property="Padding" Value="{DynamicResource SpacingMedium}"/>
        <Setter Property="Effect">
            <Setter.Value>
                <DropShadowEffect Direction="270" BlurRadius="8" 
                                 ShadowDepth="2" Opacity="0.3"/>
            </Setter.Value>
        </Setter>
    </Style>

    <!-- Progress Indicator -->
    <Style x:Key="ProgressIndicator" TargetType="ProgressBar">
        <Setter Property="Height" Value="2"/>
        <Setter Property="Background" Value="{DynamicResource SurfaceBrush}"/>
        <Setter Property="Foreground" Value="{DynamicResource PrimaryBrush}"/>
        <Style.Triggers>
            <Trigger Property="IsIndeterminate" Value="True">
                <Setter Property="Opacity" Value="0.7"/>
            </Trigger>
        </Style.Triggers>
    </Style>

    <!-- Animation Templates -->
    <Storyboard x:Key="FadeInAnimation">
        <DoubleAnimation Storyboard.TargetProperty="Opacity"
                        From="0" To="1" Duration="0:0:0.2"/>
    </Storyboard>

    <Storyboard x:Key="FadeOutAnimation">
        <DoubleAnimation Storyboard.TargetProperty="Opacity"
                        From="1" To="0" Duration="0:0:0.2"/>
    </Storyboard>

    <Storyboard x:Key="SlideInAnimation">
        <ThicknessAnimation Storyboard.TargetProperty="Margin"
                           From="0,-50,0,0" To="0,0,0,0"
                           Duration="0:0:0.3">
            <ThicknessAnimation.EasingFunction>
                <CubicEase EasingMode="EaseOut"/>
            </ThicknessAnimation.EasingFunction>
        </ThicknessAnimation>
    </Storyboard>
</ResourceDictionary>
'''

    def get_component_template(self) -> str:
        """Gera template para componentes reutilizáveis"""
        return '''
<ResourceDictionary
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">

    <!-- Card Component -->
    <Style x:Key="Card" TargetType="Border">
        <Setter Property="Background" Value="{DynamicResource SurfaceBrush}"/>
        <Setter Property="BorderThickness" Value="0"/>
        <Setter Property="CornerRadius" Value="8"/>
        <Setter Property="Padding" Value="{DynamicResource SpacingMedium}"/>
        <Setter Property="Effect">
            <Setter.Value>
                <DropShadowEffect Direction="270" BlurRadius="8" 
                                 ShadowDepth="2" Opacity="0.2"/>
            </Setter.Value>
        </Setter>
    </Style>

    <!-- Search Box Component -->
    <Style x:Key="SearchBox" TargetType="TextBox">
        <Setter Property="Template">
            <Setter.Value>
                <ControlTemplate TargetType="TextBox">
                    <Border Background="{DynamicResource SurfaceBrush}"
                            BorderBrush="{DynamicResource PrimaryBrush}"
                            BorderThickness="1"
                            CornerRadius="20">
                        <Grid>
                            <TextBox Text="{Binding Text, 
                                     RelativeSource={RelativeSource TemplatedParent}}"
                                     Background="Transparent"
                                     BorderThickness="0"
                                     Padding="30,8,8,8"/>
                            <Path Data="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"
                                  Fill="{DynamicResource TextSecondaryBrush}"
                                  Width="16" Height="16"
                                  Stretch="Uniform"
                                  HorizontalAlignment="Left"
                                  Margin="8,0,0,0"/>
                        </Grid>
                    </Border>
                </ControlTemplate>
            </Setter.Value>
        </Setter>
    </Style>

    <!-- Empty State Component -->
    <Style x:Key="EmptyState" TargetType="StackPanel">
        <Setter Property="HorizontalAlignment" Value="Center"/>
        <Setter Property="VerticalAlignment" Value="Center"/>
        <Setter Property="Margin" Value="{DynamicResource SpacingLarge}"/>
    </Style>

    <!-- Message Box Component -->
    <Style x:Key="MessageBox" TargetType="Border">
        <Setter Property="Background" Value="{DynamicResource SurfaceBrush}"/>
        <Setter Property="BorderThickness" Value="1"/>
        <Setter Property="CornerRadius" Value="4"/>
        <Setter Property="Padding" Value="{DynamicResource SpacingMedium}"/>
        <Style.Triggers>
            <Trigger Property="Tag" Value="error">
                <Setter Property="BorderBrush" Value="{DynamicResource ErrorBrush}"/>
                <Setter Property="Background" Value="#1FDC3545"/>
            </Trigger>
            <Trigger Property="Tag" Value="success">
                <Setter Property="BorderBrush" Value="{DynamicResource SuccessBrush}"/>
                <Setter Property="Background" Value="#1F28A745"/>
            </Trigger>
            <Trigger Property="Tag" Value="warning">
                <Setter Property="BorderBrush" Value="{DynamicResource WarningBrush}"/>
                <Setter Property="Background" Value="#1FFFC107"/>
            </Trigger>
            <Trigger Property="Tag" Value="info">
                <Setter Property="BorderBrush" Value="{DynamicResource InfoBrush}"/>
                <Setter Property="Background" Value="#1F17A2B8"/>
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