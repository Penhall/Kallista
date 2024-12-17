# tools/database/schema_generator.py
from typing import Dict, List, Any
from pathlib import Path
import json
from datetime import datetime

class SchemaGenerator:
    def __init__(self):
        self.output_path = Path("output/database")
        self.output_path.mkdir(parents=True, exist_ok=True)

    def generate_entity_schema(self, entity_config: Dict) -> str:
        """Gera código C# para uma entidade"""
        code = []
        
        # Adiciona imports
        code.extend([
            "using System;",
            "using System.ComponentModel.DataAnnotations;",
            "using System.ComponentModel.DataAnnotations.Schema;",
            ""
        ])

        # Adiciona namespace
        code.append(f"namespace {entity_config.get('namespace', 'YourNamespace.Domain.Entities')}")
        code.append("{")

        # Adiciona classe
        code.append(f"    public class {entity_config['name']}")
        code.append("    {")

        # Adiciona propriedades
        for prop in entity_config.get('properties', []):
            code.extend(self._generate_property(prop))

        # Adiciona navegação
        for nav in entity_config.get('navigation_properties', []):
            code.extend(self._generate_navigation_property(nav))

        code.append("    }")
        code.append("}")

        return "\n".join(code)

    def _generate_property(self, prop: Dict) -> List[str]:
        """Gera código para uma propriedade"""
        code = []
        
        # Adiciona atributos
        if attributes := self._generate_attributes(prop):
            code.extend(attributes)

        # Adiciona a propriedade
        nullable = "?" if prop.get('nullable', False) else ""
        code.append(f"        public {prop['type']}{nullable} {prop['name']} {{ get; set; }}")
        
        return code

    def _generate_attributes(self, prop: Dict) -> List[str]:
        """Gera atributos para uma propriedade"""
        attributes = []
        
        if prop.get('key', False):
            attributes.append("        [Key]")
            
        if prop.get('required', False):
            attributes.append("        [Required]")
            
        if max_length := prop.get('max_length'):
            attributes.append(f"        [MaxLength({max_length})]")
            
        if column_name := prop.get('column_name'):
            attributes.append(f'        [Column("{column_name}")]')
            
        return attributes

    def _generate_navigation_property(self, nav: Dict) -> List[str]:
        """Gera código para uma propriedade de navegação"""
        code = []
        
        if nav['type'] == 'one_to_many':
            code.append(f"        public virtual ICollection<{nav['entity']}> {nav['name']} {{ get; set; }}")
        else:
            code.append(f"        public virtual {nav['entity']} {nav['name']} {{ get; set; }}")
            
        return code

    def generate_db_context(self, context_config: Dict) -> str:
        """Gera código do DbContext"""
        code = []
        
        # Adiciona imports
        code.extend([
            "using Microsoft.EntityFrameworkCore;",
            "using System;",
            "using System.Linq;",
            ""
        ])

        # Adiciona namespace
        code.append(f"namespace {context_config.get('namespace', 'YourNamespace.Infrastructure')}")
        code.append("{")

        # Adiciona classe
        code.append(f"    public class {context_config.get('name', 'ApplicationDbContext')} : DbContext")
        code.append("    {")

        # Construtor
        code.append(f"        public {context_config.get('name', 'ApplicationDbContext')}(DbContextOptions options)")
        code.append("            : base(options)")
        code.append("        {")
        code.append("        }")

        # DbSets
        for entity in context_config.get('entities', []):
            code.append(f"        public DbSet<{entity}> {entity}s {{ get; set; }}")

        # OnModelCreating
        code.append("")
        code.append("        protected override void OnModelCreating(ModelBuilder modelBuilder)")
        code.append("        {")
        code.append("            base.OnModelCreating(modelBuilder);")
        code.append("")
        code.append("            // Entity configurations")
        for entity in context_config.get('entities', []):
            code.append(f"            modelBuilder.ApplyConfiguration(new {entity}Configuration());")
        code.append("        }")

        code.append("    }")
        code.append("}")

        return "\n".join(code)

    def generate_repository(self, repo_config: Dict) -> str:
        """Gera código para um repositório"""
        code = []
        
        # Adiciona imports
        code.extend([
            "using System;",
            "using System.Collections.Generic;",
            "using System.Linq;",
            "using System.Threading.Tasks;",
            "using Microsoft.EntityFrameworkCore;",
            ""
        ])

        # Interface
        code.extend(self._generate_repository_interface(repo_config))
        code.append("")

        # Implementação
        code.extend(self._generate_repository_implementation(repo_config))

        return "\n".join(code)

    def _generate_repository_interface(self, repo_config: Dict) -> List[str]:
        """Gera código para a interface do repositório"""
        code = []
        entity_name = repo_config['entity']
        
        code.append(f"public interface I{entity_name}Repository")
        code.append("{")
        code.append(f"    Task<{entity_name}> GetByIdAsync(int id);")
        code.append(f"    Task<IEnumerable<{entity_name}>> GetAllAsync();")
        code.append(f"    Task<{entity_name}> AddAsync({entity_name} entity);")
        code.append(f"    Task UpdateAsync({entity_name} entity);")
        code.append(f"    Task DeleteAsync(int id);")
        code.append("}")
        
        return code

    def _generate_repository_implementation(self, repo_config: Dict) -> List[str]:
        """Gera código para a implementação do repositório"""
        code = []
        entity_name = repo_config['entity']
        
        code.append(f"public class {entity_name}Repository : I{entity_name}Repository")
        code.append("{")
        code.append("    private readonly ApplicationDbContext _context;")
        code.append("")
        code.append(f"    public {entity_name}Repository(ApplicationDbContext context)")
        code.append("    {")
        code.append("        _context = context;")
        code.append("    }")
        code.append("")
        
        # Implementação dos métodos
        code.extend(self._generate_repository_methods(entity_name))
        
        code.append("}")
        return code

    def _generate_repository_methods(self, entity_name: str) -> List[str]:
        """Gera código para os métodos do repositório"""
        return [
            f"    public async Task<{entity_name}> GetByIdAsync(int id)",
            "    {",
            f"        return await _context.{entity_name}s.FindAsync(id);",
            "    }",
            "",
            f"    public async Task<IEnumerable<{entity_name}>> GetAllAsync()",
            "    {",
            f"        return await _context.{entity_name}s.ToListAsync();",
            "    }",
            "",
            f"    public async Task<{entity_name}> AddAsync({entity_name} entity)",
            "    {",
            f"        await _context.{entity_name}s.AddAsync(entity);",
            "        await _context.SaveChangesAsync();",
            "        return entity;",
            "    }",
            "",
            f"    public async Task UpdateAsync({entity_name} entity)",
            "    {",
            f"        _context.{entity_name}s.Update(entity);",
            "        await _context.SaveChangesAsync();",
            "    }",
            "",
            "    public async Task DeleteAsync(int id)",
            "    {",
            f"        var entity = await _context.{entity_name}s.FindAsync(id);",
            "        if (entity != null)",
            "        {",
            f"            _context.{entity_name}s.Remove(entity);",
            "            await _context.SaveChangesAsync();",
            "        }",
            "    }"
        ]

    def save_schema(self, name: str, schema: Dict):
        """Salva schema em arquivo"""
        schema_file = self.output_path / f"{name}.json"
        with open(schema_file, 'w') as f:
            json.dump(schema, f, indent=4)

    def load_schema(self, name: str) -> Dict:
        """Carrega schema de arquivo"""
        schema_file = self.output_path / f"{name}.json"
        if schema_file.exists():
            with open(schema_file, 'r') as f:
                return json.load(f)
        return {}