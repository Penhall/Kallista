# templates/database/ef_templates.py
from typing import Dict, Any
from pathlib import Path

class EntityFrameworkTemplates:
    def __init__(self):
        self.templates_path = Path("templates/database")
        self.templates_path.mkdir(parents=True, exist_ok=True)

    def get_db_context_template(self, config: Dict[str, Any]) -> str:
        """Gera template para DbContext"""
        return f'''
using Microsoft.EntityFrameworkCore;
using {config['namespace']}.Models;
using {config['namespace']}.Configurations;

namespace {config['namespace']}.Data
{{
    public class ApplicationDbContext : DbContext
    {{
        public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
            : base(options)
        {{
        }}

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {{
            base.OnModelCreating(modelBuilder);

            // Apply configurations
            modelBuilder.ApplyConfigurationsFromAssembly(typeof(ApplicationDbContext).Assembly);

            // Seed data
            {self._generate_seed_data(config)}
        }}

        // DbSet properties
        {self._generate_dbset_properties(config)}
    }}
}}
'''

    def get_entity_configuration_template(self, config: Dict[str, Any]) -> str:
        """Gera template para configuração de entidade"""
        return f'''
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using {config['namespace']}.Models;

namespace {config['namespace']}.Configurations
{{
    public class {config['entity_name']}Configuration : IEntityTypeConfiguration<{config['entity_name']}>
    {{
        public void Configure(EntityTypeBuilder<{config['entity_name']}> builder)
        {{
            builder.ToTable("{config['table_name']}");

            builder.HasKey(e => e.Id);

            builder.Property(e => e.Id)
                   .ValueGeneratedOnAdd();

            {self._generate_property_configurations(config)}

            {self._generate_relationship_configurations(config)}
        }}
    }}
}}
'''

    def get_repository_template(self, config: Dict[str, Any]) -> str:
        """Gera template para repositório"""
        return f'''
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using {config['namespace']}.Models;
using {config['namespace']}.Data;
using {config['namespace']}.Interfaces;

namespace {config['namespace']}.Repositories
{{
    public class {config['entity_name']}Repository : I{config['entity_name']}Repository
    {{
        private readonly ApplicationDbContext _context;

        public {config['entity_name']}Repository(ApplicationDbContext context)
        {{
            _context = context;
        }}

        public async Task<IEnumerable<{config['entity_name']}>> GetAllAsync()
        {{
            return await _context.{config['entity_name']}s
                .AsNoTracking()
                .ToListAsync();
        }}

        public async Task<{config['entity_name']}> GetByIdAsync(int id)
        {{
            return await _context.{config['entity_name']}s
                .FirstOrDefaultAsync(e => e.Id == id);
        }}

        public async Task<{config['entity_name']}> AddAsync({config['entity_name']} entity)
        {{
            _context.{config['entity_name']}s.Add(entity);
            await _context.SaveChangesAsync();
            return entity;
        }}

        public async Task UpdateAsync({config['entity_name']} entity)
        {{
            _context.Entry(entity).State = EntityState.Modified;
            await _context.SaveChangesAsync();
        }}

        public async Task DeleteAsync(int id)
        {{
            var entity = await GetByIdAsync(id);
            if (entity != null)
            {{
                _context.{config['entity_name']}s.Remove(entity);
                await _context.SaveChangesAsync();
            }}
        }}

        {self._generate_custom_queries(config)}
    }}
}}
'''

    def get_unit_of_work_template(self, config: Dict[str, Any]) -> str:
        """Gera template para Unit of Work"""
        return f'''
using System;
using System.Threading.Tasks;
using {config['namespace']}.Data;
using {config['namespace']}.Interfaces;
using {config['namespace']}.Repositories;

namespace {config['namespace']}.Data
{{
    public class UnitOfWork : IUnitOfWork
    {{
        private readonly ApplicationDbContext _context;
        private bool _disposed;

        {self._generate_repository_fields(config)}

        public UnitOfWork(ApplicationDbContext context)
        {{
            _context = context;
        }}

        {self._generate_repository_properties(config)}

        public async Task<int> SaveChangesAsync()
        {{
            return await _context.SaveChangesAsync();
        }}

        protected virtual void Dispose(bool disposing)
        {{
            if (!_disposed && disposing)
            {{
                _context.Dispose();
            }}
            _disposed = true;
        }}

        public void Dispose()
        {{
            Dispose(true);
            GC.SuppressFinalize(this);
        }}
    }}
}}
'''

    def get_migration_template(self, config: Dict[str, Any]) -> str:
        """Gera template para migração inicial"""
        return f'''
using System;
using Microsoft.EntityFrameworkCore.Migrations;

namespace {config['namespace']}.Migrations
{{
    public partial class InitialCreate : Migration
    {{
        protected override void Up(MigrationBuilder migrationBuilder)
        {{
            {self._generate_create_tables(config)}
        }}

        protected override void Down(MigrationBuilder migrationBuilder)
        {{
            {self._generate_drop_tables(config)}
        }}
    }}
}}
'''

    def _generate_dbset_properties(self, config: Dict[str, Any]) -> str:
        """Gera propriedades DbSet para cada entidade"""
        properties = []
        for entity in config.get('entities', []):
            properties.append(f'public DbSet<{entity}> {entity}s {{ get; set; }}')
        return '\n        '.join(properties)

    def _generate_seed_data(self, config: Dict[str, Any]) -> str:
        """Gera código para seed de dados"""
        seeds = []
        for seed in config.get('seeds', []):
            seeds.append(f'''
            modelBuilder.Entity<{seed['entity']}>().HasData(
                {self._generate_seed_entries(seed)}
            );''')
        return '\n'.join(seeds)

    def _generate_property_configurations(self, config: Dict[str, Any]) -> str:
        """Gera configurações para propriedades da entidade"""
        configs = []
        for prop in config.get('properties', []):
            if prop.get('required', False):
                configs.append(f"builder.Property(e => e.{prop['name']}).IsRequired();")
            if 'max_length' in prop:
                configs.append(f"builder.Property(e => e.{prop['name']}).HasMaxLength({prop['max_length']});")
            if 'precision' in prop:
                configs.append(f"builder.Property(e => e.{prop['name']}).HasPrecision({prop['precision']}, {prop['scale']});")
        return '\n            '.join(configs)

    def _generate_relationship_configurations(self, config: Dict[str, Any]) -> str:
        """Gera configurações para relacionamentos"""
        configs = []
        for rel in config.get('relationships', []):
            if rel['type'] == 'one_to_many':
                configs.append(f'''
            builder.HasMany(e => e.{rel['collection']})
                   .WithOne(e => e.{rel['reference']})
                   .HasForeignKey(e => e.{rel['foreign_key']})
                   .OnDelete(DeleteBehavior.{rel.get('delete_behavior', 'Cascade')});''')
            elif rel['type'] == 'one_to_one':
                configs.append(f'''
            builder.HasOne(e => e.{rel['property']})
                   .WithOne(e => e.{rel['inverse_property']})
                   .HasForeignKey<{rel['dependent_type']}>(e => e.{rel['foreign_key']});''')
        return '\n            '.join(configs)

    def _generate_custom_queries(self, config: Dict[str, Any]) -> str:
        """Gera queries customizadas para o repositório"""
        queries = []
        for query in config.get('custom_queries', []):
            queries.append(f'''
        public async Task<IEnumerable<{config['entity_name']}>> {query['name']}({query.get('parameters', '')})
        {{
            return await _context.{config['entity_name']}s
                {query['implementation']}
        }}''')
        return '\n'.join(queries)

    def _generate_repository_fields(self, config: Dict[str, Any]) -> str:
        """Gera campos para repositórios no Unit of Work"""
        fields = []
        for repo in config.get('repositories', []):
            fields.append(f'private I{repo}Repository _{repo.lower()}Repository;')
        return '\n        '.join(fields)

    def _generate_repository_properties(self, config: Dict[str, Any]) -> str:
        """Gera propriedades para repositórios no Unit of Work"""
        properties = []
        for repo in config.get('repositories', []):
            properties.append(f'''
        public I{repo}Repository {repo}Repository
        {{
            get
            {{
                if (_{repo.lower()}Repository == null)
                    _{repo.lower()}Repository = new {repo}Repository(_context);
                return _{repo.lower()}Repository;
            }}
        }}''')
        return '\n'.join(properties)

    def save_template(self, name: str, content: str):
        """Salva um template em arquivo"""
        template_file = self.templates_path / f"{name}.cs"
        template_file.write_text(content)

    def load_template(self, name: str) -> str:
        """Carrega um template de arquivo"""
        template_file = self.templates_path / f"{name}.cs"
        if template_file.exists():
            return template_file.read_text()
        return ""