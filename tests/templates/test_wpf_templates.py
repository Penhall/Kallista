# tests/templates/test_wpf_templates.py
import unittest
from pathlib import Path
from templates.wpf.base_templates import WpfTemplates

class TestWpfTemplates(unittest.TestCase):
    def setUp(self):
        self.templates = WpfTemplates()
        self.test_config = {
            'namespace': 'TestApp',
            'name': 'MainWindow',
            'title': 'Test Window',
            'height': '450',
            'width': '800'
        }

    def test_window_template_generation(self):
        """Testa geração de template de janela"""
        template = self.templates.get_window_template(self.test_config)
        
        # Verifica elementos essenciais
        self.assertIn('x:Class="TestApp.MainWindow"', template)
        self.assertIn('Title="Test Window"', template)
        self.assertIn('Height="450"', template)
        self.assertIn('Width="800"', template)
        
        # Verifica elementos estruturais
        self.assertIn('<Window.Resources>', template)
        self.assertIn('<Grid>', template)
        self.assertIn('<Grid.RowDefinitions>', template)

    def test_view_model_template_generation(self):
        """Testa geração de template de ViewModel"""
        vm_config = {
            'namespace': 'TestApp',
            'name': 'Main'
        }
        template = self.templates.get_view_model_template(vm_config)
        
        # Verifica implementação de INotifyPropertyChanged
        self.assertIn('INotifyPropertyChanged', template)
        self.assertIn('OnPropertyChanged', template)
        
        # Verifica comandos
        self.assertIn('public ICommand', template)
        self.assertIn('InitializeCommands', template)
        
        # Verifica tratamento de erros
        self.assertIn('try', template)
        self.assertIn('catch (Exception ex)', template)

    def test_model_template_generation(self):
        """Testa geração de template de Model"""
        model_config = {
            'namespace': 'TestApp',
            'name': 'User'
        }
        template = self.templates.get_model_template(model_config)
        
        # Verifica atributos e propriedades
        self.assertIn('[Key]', template)
        self.assertIn('[Required]', template)
        self.assertIn('public int Id { get; set; }', template)
        self.assertIn('public DateTime CreatedAt', template)

    def test_service_interface_template_generation(self):
        """Testa geração de template de interface de serviço"""
        service_config = {
            'namespace': 'TestApp',
            'name': 'User'
        }
        template = self.templates.get_service_interface_template(service_config)
        
        # Verifica métodos CRUD
        self.assertIn('Task<IEnumerable<User>> GetAllAsync()', template)
        self.assertIn('Task<User> GetByIdAsync(int id)', template)
        self.assertIn('Task<User> CreateAsync(User entity)', template)
        self.assertIn('Task UpdateAsync(User entity)', template)
        self.assertIn('Task DeleteAsync(int id)', template)

    def test_style_dictionary_template_generation(self):
        """Testa geração de dicionário de estilos"""
        template = self.templates.get_style_dictionary_template()
        
        # Verifica recursos visuais
        self.assertIn('<Color x:Key="PrimaryColor">', template)
        self.assertIn('<SolidColorBrush x:Key="PrimaryBrush"', template)
        self.assertIn('<Style x:Key="HeaderTextStyle"', template)
        self.assertIn('<Style x:Key="DefaultButtonStyle"', template)

    def test_template_file_operations(self):
        """Testa operações de arquivo de template"""
        test_content = "<TestTemplate>Content</TestTemplate>"
        test_name = "test_template"
        
        # Testa salvamento
        self.templates.save_template(test_name, test_content)
        template_file = self.templates.templates_path / f"{test_name}.xaml"
        self.assertTrue(template_file.exists())
        
        # Testa carregamento
        loaded_content = self.templates.load_template(test_name)
        self.assertEqual(loaded_content, test_content)
        
        # Limpa arquivo de teste
        template_file.unlink()

    def test_invalid_config(self):
        """Testa comportamento com configuração inválida"""
        invalid_config = {}
        
        # Não deve lançar exceção, mas gerar template com valores padrão
        template = self.templates.get_window_template(invalid_config)
        self.assertIn('Window', template)

    def test_template_validation(self):
        """Testa validação básica de template"""
        template = self.templates.get_window_template(self.test_config)
        
        # Verifica estrutura XML válida
        self.assertTrue(template.startswith('<Window'))
        self.assertTrue(template.strip().endswith('</Window>'))

    def test_resource_references(self):
        """Testa referências a recursos"""
        template = self.templates.get_style_dictionary_template()
        
        # Verifica referências de recursos
        self.assertIn('{StaticResource', template)
        self.assertIn('{DynamicResource', template)

    def tearDown(self):
        """Limpa arquivos de teste"""
        if self.templates.templates_path.exists():
            for file in self.templates.templates_path.glob("test_*.xaml"):
                file.unlink()