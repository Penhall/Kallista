# agents/specialized/database_agent.py
from crewai import Agent
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
from datetime import datetime

class DatabaseAgent(Agent):
    def __init__(self, llm):
        super().__init__(
            role='Database Specialist',
            goal='Design and implement efficient database structures and data access layers',
            backstory="""You are a database expert specialized in .NET/C# 
            environments. You excel at designing efficient database schemas, 
            implementing Entity Framework solutions, and creating optimized 
            data access patterns.""",
            llm=llm
        )
        self.schema_path = Path("templates/database")
        self.schema_path.mkdir(parents=True, exist_ok=True)

    async def design_database_schema(self, requirements: Dict) -> Dict[str, Any]:
        """Design database schema based on requirements"""
        try:
            return {
                'entities': self._design_entities(requirements),
                'relationships': self._design_relationships(requirements),
                'constraints': self._define_constraints(requirements),
                'indices': self._define_indices(requirements),
                'validations': self._validate_schema(requirements)
            }
        except Exception as e:
            raise Exception(f"Error in database design: {str(e)}")

    def _design_entities(self, requirements: Dict) -> List[Dict]:
        """Design database entities"""
        entities = []
        for entity in requirements.get('entities', []):
            entities.append({
                'name': entity['name'],
                'properties': self._define_properties(entity),
                'keys': self._define_keys(entity),
                'audit_fields': self._add_audit_fields(),
                'concurrency': entity.get('concurrency', True)
            })
        return entities

    def _design_relationships(self, requirements: Dict) -> List[Dict]:
        """Define relationships between entities"""
        relationships = []
        for rel in requirements.get('relationships', []):
            relationships.append({
                'from_entity': rel['from'],
                'to_entity': rel['to'],
                'type': rel['type'],  # OneToOne, OneToMany, ManyToMany
                'cascade_delete': rel.get('cascade_delete', False),
                'navigation_properties': self._define_navigation_properties(rel)
            })
        return relationships

    async def generate_entity_framework(self, schema: Dict) -> Dict[str, str]:
        """Generate Entity Framework code"""
        return {
            'context': self._generate_db_context(schema),
            'entities': self._generate_entity_classes(schema),
            'configurations': self._generate_entity_configurations(schema),
            'migrations': self._generate_migration_script(schema)
        }

    def _define_properties(self, entity: Dict) -> List[Dict]:
        """Define properties for an entity"""
        properties = []
        for prop in entity.get('properties', []):
            properties.append({
                'name': prop['name'],
                'type': self._map_to_csharp_type(prop['type']),
                'nullable': prop.get('nullable', False),
                'max_length': prop.get('max_length'),
                'precision': prop.get('precision'),
                'scale': prop.get('scale'),
                'default_value': prop.get('default'),
                'validations': self._define_property_validations(prop)
            })
        return properties

    def _define_property_validations(self, property: Dict) -> List[Dict]:
        """Define validations for a property"""
        validations = []
        if 'validations' in property:
            for validation in property['validations']:
                validations.append({
                    'type': validation['type'],
                    'parameters': validation.get('parameters', {}),
                    'error_message': validation.get('error_message', '')
                })
        return validations

    def _map_to_csharp_type(self, db_type: str) -> str:
        """Map database types to C# types"""
        type_mapping = {
            'string': 'string',
            'integer': 'int',
            'bigint': 'long',
            'decimal': 'decimal',
            'boolean': 'bool',
            'datetime': 'DateTime',
            'guid': 'Guid',
            'binary': 'byte[]'
        }
        return type_mapping.get(db_type.lower(), 'object')

    def _generate_db_context(self, schema: Dict) -> str:
        """Generate DbContext class"""
        context_code = []
        context_code.append("public class ApplicationDbContext : DbContext")
        context_code.append("{")
        
        # DbSet properties
        for entity in schema['entities']:
            context_code.append(f"    public DbSet<{entity['name']}> {entity['name']}s {{ get; set; }}")
        
        # OnModelCreating
        context_code.append("\n    protected override void OnModelCreating(ModelBuilder modelBuilder)")
        context_code.append("    {")
        
        # Apply configurations
        context_code.append("        base.OnModelCreating(modelBuilder);")
        for entity in schema['entities']:
            context_code.append(f"        modelBuilder.ApplyConfiguration(new {entity['name']}Configuration());")
        
        context_code.append("    }")
        context_code.append("}")
        
        return "\n".join(context_code)

    def _generate_entity_classes(self, schema: Dict) -> Dict[str, str]:
        """Generate entity classes"""
        entity_classes = {}
        for entity in schema['entities']:
            class_code = []
            class_code.append(f"public class {entity['name']}")
            class_code.append("{")
            
            # Properties
            for prop in entity['properties']:
                nullable = "?" if prop['nullable'] else ""
                class_code.append(f"    public {prop['type']}{nullable} {prop['name']} {{ get; set; }}")
            
            # Navigation properties
            for rel in schema['relationships']:
                if rel['from_entity'] == entity['name']:
                    if rel['type'] == 'OneToMany':
                        class_code.append(f"    public virtual ICollection<{rel['to_entity']}> {rel['to_entity']}s {{ get; set; }}")
                    else:
                        class_code.append(f"    public virtual {rel['to_entity']} {rel['to_entity']} {{ get; set; }}")
            
            class_code.append("}")
            entity_classes[entity['name']] = "\n".join(class_code)
        
        return entity_classes

    def _generate_entity_configurations(self, schema: Dict) -> Dict[str, str]:
        """Generate entity configurations"""
        configurations = {}
        for entity in schema['entities']:
            config_code = []
            config_code.append(f"public class {entity['name']}Configuration : IEntityTypeConfiguration<{entity['name']}>")
            config_code.append("{")
            config_code.append("    public void Configure(EntityTypeBuilder<{entity['name']}> builder)")
            config_code.append("    {")
            
            # Configure primary key
            config_code.append(f"        builder.HasKey(e => e.Id);")
            
            # Configure properties
            for prop in entity['properties']:
                if prop.get('max_length'):
                    config_code.append(f"        builder.Property(e => e.{prop['name']}).HasMaxLength({prop['max_length']});")
                if prop.get('precision'):
                    config_code.append(f"        builder.Property(e => e.{prop['name']}).HasPrecision({prop['precision']}, {prop['scale']});")
            
            config_code.append("    }")
            config_code.append("}")
            configurations[entity['name']] = "\n".join(config_code)
        
        return configurations

    def _generate_migration_script(self, schema: Dict) -> str:
        """Generate initial migration script"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"""
using Microsoft.EntityFrameworkCore.Migrations;

namespace YourNamespace.Migrations
{{
    public partial class InitialCreate_{timestamp} : Migration
    {{
        protected override void Up(MigrationBuilder migrationBuilder)
        {{
            {self._generate_create_tables(schema)}
        }}

        protected override void Down(MigrationBuilder migrationBuilder)
        {{
            {self._generate_drop_tables(schema)}
        }}
    }}
}}
"""

    def _generate_create_tables(self, schema: Dict) -> str:
        """Generate CREATE TABLE statements"""
        create_statements = []
        for entity in schema['entities']:
            create_statements.append(f"""
            migrationBuilder.CreateTable(
                name: "{entity['name']}s",
                columns: table => new
                {{
                    {self._generate_column_definitions(entity)}
                }},
                constraints: table =>
                {{
                    {self._generate_constraints(entity, schema)}
                }});
            """)
        return "\n".join(create_statements)

    def save_schema(self, schema: Dict) -> None:
        """Save database schema for reuse"""
        schema_file = self.schema_path / f"{schema['name']}.json"
        with open(schema_file, 'w') as f:
            json.dump(schema, f, indent=4)

    def load_schema(self, schema_name: str) -> Optional[Dict]:
        """Load a saved database schema"""
        schema_file = self.schema_path / f"{schema_name}.json"
        if schema_file.exists():
            with open(schema_file, 'r') as f:
                return json.load(f)
        return None