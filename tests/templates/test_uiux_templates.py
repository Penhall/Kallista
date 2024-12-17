# tests/templates/test_uiux_templates.py
import unittest
from pathlib import Path
from templates.uiux.ui_templates import UiTemplates

class TestUiUxTemplates(unittest.TestCase):
    def setUp(self):
        self.templates = UiTemplates()
        self.test_config = {
            'primary_color': '#1E88E5',
            'secondary_color': '#5E35B1',
            'accent_color': '#FFB300',
            'background_color': '#FFFFFF',
            'surface_color': '#F5F5F5',
            'error_color': '#D32F2F',
            'success_color': '#388E3C',
            'warning_color': '#FFA000',
            'info_color': '#0288D1',
            'primary_font': 'Segoe UI',
            'secondary_font': 'Segoe UI Light',
            'mono_font': 'Consolas',
            'nav_width': '250'
        }

    def test_theme_template_generation(self):
        """Testa geração de template de tema"""
        template = self.templates.get_theme_template(self.test_config)
        
        # Verifica definição de cores
        self.assertIn('<Color x:Key="Primary">#1E88E5</Color>', template)
        self.assertIn('<Color x:Key="Secondary">#5E35B1</Color>', template)
        self.assertIn('<Color x:Key="Accent">#FFB300</Color>', template)
        
        # Verifica brushes
        self.assertIn('<SolidColorBrush x:Key="PrimaryBrush"', template)
        self.assertIn('<SolidColorBrush x:Key="SecondaryBrush"', template)
        
        # Verifica estilos de texto
        self.assertIn('<Style x:Key="HeadingLarge"', template)
        self.assertIn('<Style x:Key="BodyRegular"', template)
        
        # Verifica configurações de espaçamento
        self.assertIn('<Thickness x:Key="SpacingMedium">', template)

    def test_accessibility_template_generation(self):
        """Testa geração de template de acessibilidade"""
        template = self.templates.get_accessibility_template()
        
        # Verifica cores de alto contraste
        self.assertIn('HighContrastBackgroundBrush', template)
        self.assertIn('HighContrastForegroundBrush', template)
        
        # Verifica estilos focáveis
        self.assertIn('AccessibleFocusVisual', template)
        self.assertIn('FocusVisualStyle', template)
        
        # Verifica tamanhos mínimos
        self.assertIn('MinWidth="44"', template)
        self.assertIn('MinHeight="44"', template)
        
        # Verifica suporte a screen reader
        self.assertIn('AutomationProperties', template)
        self.assertIn('ScreenReaderOnly', template)

    def test_layout_template_generation(self):
        """Testa geração de template de layout"""
        template = self.templates.get_layout_template(self.test_config)
        
        # Verifica grids
        self.assertIn('<Style x:Key="StandardGrid"', template)
        self.assertIn('<Style x:Key="ResponsiveGrid"', template)
        
        # Verifica layouts de formulário
        self.assertIn('<Style x:Key="FormGrid"', template)
        
        # Verifica painéis de conteúdo
        self.assertIn('<Style x:Key="ContentPanel"', template)
        self.assertIn('<Style x:Key="NavigationPanel"', template)
        
        # Verifica responsividade
        self.assertIn('DataTrigger Binding="{{Binding ActualWidth', template)

    def test_interaction_template_generation(self):
        """Testa geração de template de interação"""
        template = self.templates.get_interaction_template()
        
        # Verifica botões interativos
        self.assertIn('<Style x:Key="InteractiveButton"', template)
        self.assertIn('Property="IsMouseOver"', template)
        
        # Verifica indicadores de loading
        self.assertIn('<Style x:Key="LoadingSpinner"', template)
        self.assertIn('RotateTransform', template)
        
        # Verifica overlays
        self.assertIn('<Style x:Key="FeedbackOverlay"', template)
        
        # Verifica tooltips
        self.assertIn('<Style x:Key="EnhancedTooltip"', template)
        
        # Verifica animações
        self.assertIn('FadeInAnimation', template)
        self.assertIn('SlideInAnimation', template)

    def test_component_template_generation(self):
        """Testa geração de template de componentes"""
        template = self.templates.get_component_template()
        
        # Verifica cards
        self.assertIn('<Style x:Key="Card"', template)
        
        # Verifica search box
        self.assertIn('<Style x:Key="SearchBox"', template)
        
        # Verifica empty states
        self.assertIn('<Style x:Key="EmptyState"', template)
        
        # Verifica message boxes
        self.assertIn('<Style x:Key="MessageBox"', template)
        self.assertIn('Property="Tag" Value="error"', template)
        self.assertIn('Property="Tag" Value="success"', template)

    def test_template_file_operations(self):
        """Testa operações de arquivo de template"""
        test_content = "<Style x:Key='TestStyle'/>"
        test_name = "test_style"
        
        # Testa salvamento
        self.templates.save_template(test_name, test_content)
        template_file = self.templates.templates_path / f"{test_name}.xaml"
        self.assertTrue(template_file.exists())
        
        # Testa carregamento
        loaded_content = self.templates.load_template(test_name)
        self.assertEqual(loaded_content, test_content)
        
        # Limpa arquivo de teste
        template_file.unlink()

    def test_resource_dictionary_structure(self):
        """Testa estrutura do ResourceDictionary"""
        template = self.templates.get_theme_template(self.test_config)
        
        # Verifica elementos XAML básicos
        self.assertIn('<ResourceDictionary', template)
        self.assertIn('xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"', template)
        self.assertIn('xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"', template)

    def test_color_consistency(self):
        """Testa consistência das cores"""
        template = self.templates.get_theme_template(self.test_config)
        
        # Verifica se cada cor tem seu brush correspondente
        colors = ['Primary', 'Secondary', 'Accent', 'Background', 'Surface']
        for color in colors:
            self.assertIn(f'<Color x:Key="{color}"', template)
            self.assertIn(f'<SolidColorBrush x:Key="{color}Brush"', template)

    def test_invalid_config(self):
        """Testa comportamento com configuração inválida"""
        invalid_config = {}
        
        # Não deve lançar exceção
        template = self.templates.get_theme_template(invalid_config)
        self.assertIn('ResourceDictionary', template)

    def test_accessibility_compliance(self):
        """Testa conformidade com diretrizes de acessibilidade"""
        template = self.templates.get_accessibility_template()
        
        # Verifica tamanhos mínimos para toque
        self.assertIn('MinWidth="44"', template)
        self.assertIn('MinHeight="44"', template)
        
        # Verifica suporte a screen reader
        self.assertIn('AutomationProperties.Name', template)
        self.assertIn('LiveSetting', template)

    def tearDown(self):
        """Limpa arquivos de teste"""
        if self.templates.templates_path.exists():
            for file in self.templates.templates_path.glob("test_*.xaml"):
                file.unlink()