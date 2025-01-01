# tools/wpf/templates/infrastructure/styles.py
class StyleTemplates:
    @staticmethod
    def base_styles() -> str:
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

    @staticmethod
    def theme() -> str:
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