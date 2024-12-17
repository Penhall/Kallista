# tests/templates/test_database_templates.py
import unittest
from pathlib import Path
from templates.database.ef_templates import EntityFrameworkTemplates

class TestDatabaseTemplates(unittest.TestCase):
    def setUp(self):
        self.templates = EntityFrameworkTemplates()
        self.test_config = {
            'namespace': 'TestApp.Data',
            'entities': ['User', 'Product', 'Order'],
            'seeds': [
                {
                    'entity': 'User',
                    'data': [
                        {'Id': 1, 'Name': 'Admin'}
                    ]
                }
            ],
            'entity_name': 'User',
            'table_name': 'Users',
            'properties': [
                {'name': 'Name', 'required': True, 'max_length': 100},
                {'name': 'Email', 'required': True}
            ],
            'relationships': [
                {
                    'type': 'one_to_many',
                    'collection': 'Orders',
                    'reference': 'User',
                    'foreign_key': 'UserId'
                }
            ]
        }

    def test_db_context_template_generation(self):
        """Testa geração de template de DbContext"""
        template = self.templates.get_db_context_template(self.test_config)
        
        # Verifica estrutura básica
        self.assertIn('public class ApplicationDbContext : DbContext', template)
        self.assertIn('protected override void OnModelCreating(ModelBuilder modelBuilder)', template)
        
        # Verifica DbSet properties
        for entity in self.test_config['entities']:
            self.assertIn(f'public DbSet<{entity}>', template)
        
        # Verifica configurações
        self.assertIn('modelBuilder.ApplyConfigurationsFromAssembly', template)
        
        # Verifica seed data
        self.assertIn('modelBuilder.Entity<User>().HasData(', template)

    def test_entity_configuration_template_generation(self):
        """Testa geração de template de configuração de entidade"""
        template = self.templates.get_entity_configuration_template(self.test_config)
        
        # Verifica classe de configuração
        self.assertIn(f'public class {self.test_config["entity_name"]}Configuration', template)
        self.assertIn('IEntityTypeConfiguration<User>', template)
        
        # Verifica configurações básicas
        self.assertIn('builder.ToTable("Users")', template)
        self.assertIn('builder.HasKey(e => e.Id)', template)
        
        # Verifica configurações de propriedade
        self.assertIn('IsRequired()', template)
        self.assertIn('HasMaxLength(100)', template)
        
        # Verifica relacionamentos
        self.assertIn('HasMany(e => e.Orders)', template)
        self.assertIn('WithOne(e => e.User)', template)

    def test_repository_template_generation(self):
        """Testa geração de template de repositório"""
        template = self.templates.get_repository_template(self.test_config)
        
        # Verifica classe do repositório
        self.assertIn(f'public class {self.test_config["entity_name"]}Repository', template)
        self.assertIn(f'I{self.test_config["entity_name"]}Repository', template)
        
        # Verifica métodos CRUD
        self.assertIn('public async Task<IEnumerable<User>> GetAllAsync()', template)
        self.assertIn('public async Task<User> GetByIdAsync(int id)', template)
        self.assertIn('public async Task<User> AddAsync(User entity)', template)
        self.assertIn('public async Task UpdateAsync(User entity)', template)
        self.assertIn('public async Task DeleteAsync(int id)', template)
        
        # Verifica uso do DbContext
        self.assertIn('private readonly ApplicationDbContext _context', template)
        self.assertIn('await _context.SaveChangesAsync()', template)

    def test_unit_of_work_template_generation(self):
        """Testa geração de template de Unit of Work"""
        template = self.templates.get_unit_of_work_template(self.test_config)
        
        # Verifica interface e implementação
        self.assertIn('public class UnitOfWork : IUnitOfWork', template)
        
        # Verifica repositórios
        for entity in self.test_config['entities']:
            self.assertIn(f'private I{entity}Repository _{entity.lower()}Repository', template)
            self.assertIn(f'public I{entity}Repository {entity}Repository', template)
        
        # Verifica gerenciamento de transação
        self.assertIn('public async Task<int> SaveChangesAsync()', template)
        self.assertIn('public void Dispose()', template)

    def test_migration_template_generation(self):
        """Testa geração de template de migração"""
        template = self.templates.get_migration_template(self.test_config)
        
        # Verifica estrutura da migração
        self.assertIn('public partial class InitialCreate : Migration', template)
        self.assertIn('protected override void Up(MigrationBuilder migrationBuilder)', template)
        self.assertIn('protected override void Down(MigrationBuilder migrationBuilder)', template)

    def test_property_configurations_generation(self):
        """Testa geração de configurações de propriedades"""
        props = self.templates._generate_property_configurations(self.test_config)
        
        # Verifica configurações específicas
        self.assertIn('IsRequired()', props)
        self.assertIn('HasMaxLength(100)', props)

    def test_relationship_configurations_generation(self):
        """Testa geração de configurações de relacionamentos"""
        rels = self.templates._generate_relationship_configurations(self.test_config)
        
        # Verifica configurações de relacionamento
        self.assertIn('HasMany(e => e.Orders)', rels)
        self.assertIn('WithOne(e => e.User)', rels)
        self.assertIn('HasForeignKey', rels)

    def test_template_file_operations(self):
        """Testa operações de arquivo de template"""
        test_content = "// Test Database Template"
        test_name = "test_db_template"
        
        # Testa salvamento
        self.templates.save_template(test_name, test_content)
        template_file = self.templates.templates_path / f"{test_name}.cs"
        self.assertTrue(template_file.exists())
        
        # Testa carregamento
        loaded_content = self.templates.load_template(test_name)
        self.assertEqual(loaded_content, test_content)
        
        # Limpa arquivo de teste
        template_file.unlink()

    def test_invalid_config(self):
        """Testa comportamento com configuração inválida"""
        invalid_config = {}
        
        # Não deve lançar exceção
        template = self.templates.get_db_context_template(invalid_config)
        self.assertIn('DbContext', template)

    def tearDown(self):
        """Limpa arquivos de teste"""
        if self.templates.templates_path.exists():
            for file in self.templates.templates_path.glob("test_*.cs"):
                file.unlink()