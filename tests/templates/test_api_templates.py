# tests/templates/test_api_templates.py
import unittest
from pathlib import Path
from templates.api.api_templates import ApiTemplates

class TestApiTemplates(unittest.TestCase):
    def setUp(self):
        self.templates = ApiTemplates()
        self.test_config = {
            'namespace': 'TestApp.API',
            'name': 'User',
            'properties': [
                {'name': 'Id', 'type': 'int', 'required': True},
                {'name': 'Name', 'type': 'string', 'required': True, 'max_length': 100},
                {'name': 'Email', 'type': 'string', 'required': True}
            ]
        }

    def test_controller_template_generation(self):
        """Testa geração de template de Controller"""
        template = self.templates.get_controller_template(self.test_config)
        
        # Verifica atributos e estrutura básica
        self.assertIn('[ApiController]', template)
        self.assertIn('[Route("api/[controller]")]', template)
        self.assertIn('public class UserController : ControllerBase', template)
        
        # Verifica injeção de dependências
        self.assertIn('private readonly IUserService _service', template)
        self.assertIn('private readonly ILogger<UserController> _logger', template)
        
        # Verifica métodos HTTP
        self.assertIn('[HttpGet]', template)
        self.assertIn('[HttpPost]', template)
        self.assertIn('[HttpPut("{id}")]', template)
        self.assertIn('[HttpDelete("{id}")]', template)
        
        # Verifica tratamento de erros
        self.assertIn('try', template)
        self.assertIn('catch (Exception ex)', template)
        self.assertIn('return StatusCode(500, "Internal server error")', template)

    def test_service_template_generation(self):
        """Testa geração de template de Service"""
        template = self.templates.get_service_template(self.test_config)
        
        # Verifica estrutura da classe
        self.assertIn(f'public class {self.test_config["name"]}Service', template)
        self.assertIn(f'I{self.test_config["name"]}Service', template)
        
        # Verifica injeção de dependências
        self.assertIn('private readonly IUnitOfWork _unitOfWork', template)
        self.assertIn('private readonly IMapper _mapper', template)
        self.assertIn('private readonly ILogger', template)
        
        # Verifica métodos CRUD
        self.assertIn('public async Task<IEnumerable<UserDto>> GetAllAsync()', template)
        self.assertIn('public async Task<UserDto> GetByIdAsync(int id)', template)
        self.assertIn('public async Task<UserDto> CreateAsync(CreateUserDto dto)', template)
        self.assertIn('public async Task UpdateAsync(int id, UpdateUserDto dto)', template)
        self.assertIn('public async Task DeleteAsync(int id)', template)

    def test_dto_template_generation(self):
        """Testa geração de template de DTOs"""
        template = self.templates.get_dto_template(self.test_config)
        
        # Verifica classes DTO
        self.assertIn('public class UserDto', template)
        self.assertIn('public class CreateUserDto', template)
        self.assertIn('public class UpdateUserDto', template)
        
        # Verifica propriedades e validações
        self.assertIn('[Required]', template)
        self.assertIn('[StringLength(100)]', template)
        self.assertIn('public string Name { get; set; }', template)
        self.assertIn('public string Email { get; set; }', template)

    def test_automapper_profile_template_generation(self):
        """Testa geração de template de AutoMapper Profile"""
        template = self.templates.get_automapper_profile_template(self.test_config)
        
        # Verifica configuração de mapeamento
        self.assertIn('public class UserProfile : Profile', template)
        self.assertIn('CreateMap<User, UserDto>()', template)
        self.assertIn('CreateMap<CreateUserDto, User>()', template)
        self.assertIn('CreateMap<UpdateUserDto, User>()', template)

    def test_validator_template_generation(self):
        """Testa geração de template de Validator"""
        template = self.templates.get_validator_template(self.test_config)
        
        # Verifica classes de validação
        self.assertIn('public class CreateUserDtoValidator', template)
        self.assertIn('public class UpdateUserDtoValidator', template)
        
        # Verifica regras de validação
        self.assertIn('RuleFor(x => x.Name)', template)
        self.assertIn('NotEmpty()', template)
        self.assertIn('MaximumLength(100)', template)
        self.assertIn('RuleFor(x => x.Email)', template)

    def test_template_file_operations(self):
        """Testa operações de arquivo de template"""
        test_content = "// Test API Template"
        test_name = "test_api_template"
        
        # Testa salvamento
        self.templates.save_template(test_name, test_content)
        template_file = self.templates.templates_path / f"{test_name}.cs"
        self.assertTrue(template_file.exists())
        
        # Testa carregamento
        loaded_content = self.templates.load_template(test_name)
        self.assertEqual(loaded_content, test_content)
        
        # Limpa arquivo de teste
        template_file.unlink()

    def test_validation_rules_generation(self):
        """Testa geração de regras de validação"""
        config = {
            'properties': [
                {
                    'name': 'Name',
                    'type': 'string',
                    'required': True,
                    'max_length': 100,
                    'min_length': 3
                }
            ]
        }
        rules = self.templates._generate_validation_rules(config)
        
        # Verifica regras geradas
        self.assertIn('RuleFor(x => x.Name)', rules)
        self.assertIn('NotEmpty()', rules)
        self.assertIn('MaximumLength(100)', rules)
        self.assertIn('MinimumLength(3)', rules)

    def test_invalid_config(self):
        """Testa comportamento com configuração inválida"""
        invalid_config = {}
        
        # Não deve lançar exceção
        template = self.templates.get_controller_template(invalid_config)
        self.assertIn('ControllerBase', template)

    def tearDown(self):
        """Limpa arquivos de teste"""
        if self.templates.templates_path.exists():
            for file in self.templates.templates_path.glob("test_*.cs"):
                file.unlink()