# integrations/visual_studio/code_generation.py
from typing import Dict, List, Optional, Union, Any
from enum import Enum
import logging
from pathlib import Path
import jinja2
import json

class CodeTemplateType(Enum):
    VIEW = "view"
    VIEW_MODEL = "viewmodel"
    MODEL = "model"
    SERVICE = "service"
    REPOSITORY = "repository"
    CUSTOM = "custom"

class CodeGenerator:
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.templates_path = Path(config.get('templates_path', 'templates/code'))
        self.templates_path.mkdir(parents=True, exist_ok=True)
        
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(self.templates_path)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        self._load_templates()

    def _load_templates(self):
        """Carrega templates disponíveis"""
        try:
            for template_type in CodeTemplateType:
                type_path = self.templates_path / template_type.value
                type_path.mkdir(exist_ok=True)
                
                # Carrega templates padrão se diretório estiver vazio
                if not any(type_path.iterdir()):
                    self._create_default_templates(template_type)
                    
        except Exception as e:
            self.logger.error(f"Failed to load templates: {str(e)}")
            raise

    async def generate_code(
        self,
        template_type: CodeTemplateType,
        template_name: str,
        data: Dict
    ) -> Dict:
        """Gera código a partir de template"""
        try:
            # Valida dados
            validation = self._validate_template_data(template_type, data)
            if not validation['valid']:
                raise ValueError(f"Invalid template data: {validation['errors']}")

            # Carrega template
            template = self.jinja_env.get_template(
                f"{template_type.value}/{template_name}.cstemplate"
            )

            # Gera código
            generated_code = template.render(**data)

            # Formata código
            formatted_code = self._format_code(generated_code)

            return {
                'template_type': template_type.value,
                'template_name': template_name,
                'code': formatted_code
            }

        except Exception as e:
            self.logger.error(f"Failed to generate code: {str(e)}")
            raise

    async def create_template(
        self,
        template_type: CodeTemplateType,
        template_name: str,
        template_content: str
    ) -> Dict:
        """Cria novo template"""
        try:
            # Valida template
            validation = self._validate_template_content(template_content)
            if not validation['valid']:
                raise ValueError(f"Invalid template content: {validation['errors']}")

            # Salva template
            template_path = (
                self.templates_path / 
                template_type.value / 
                f"{template_name}.cstemplate"
            )
            
            template_path.write_text(template_content)

            return {
                'template_type': template_type.value,
                'template_name': template_name,
                'path': str(template_path)
            }

        except Exception as e:
            self.logger.error(f"Failed to create template: {str(e)}")
            raise

    async def list_templates(
        self,
        template_type: Optional[CodeTemplateType] = None
    ) -> List[Dict]:
        """Lista templates disponíveis"""
        try:
            templates = []

            for t_type in CodeTemplateType if not template_type else [template_type]:
                type_path = self.templates_path / t_type.value
                
                for template_file in type_path.glob("*.cstemplate"):
                    template_info = self._get_template_info(t_type, template_file)
                    templates.append(template_info)

            return templates

        except Exception as e:
            self.logger.error(f"Failed to list templates: {str(e)}")
            raise

    def _create_default_templates(self, template_type: CodeTemplateType):
        """Cria templates padrão para um tipo"""
        if template_type == CodeTemplateType.VIEW:
            self._create_view_templates()
        elif template_type == CodeTemplateType.VIEW_MODEL:
            self._create_viewmodel_templates()
        elif template_type == CodeTemplateType.MODEL:
            self._create_model_templates()
        elif template_type == CodeTemplateType.SERVICE:
            self._create_service_templates()
        elif template_type == CodeTemplateType.REPOSITORY:
            self._create_repository_templates()

    def _create_view_templates(self):
        """Cria templates padrão para Views"""
        basic_view = """
<Window x:Class="{{ namespace }}.Views.{{ name }}View"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="{{ title }}" Height="{{ height }}" Width="{{ width }}">
    
    <Window.DataContext>
        <viewmodels:{{ name }}ViewModel/>
    </Window.DataContext>

    <Grid>
        {% for control in controls %}
        <{{ control.type }} 
            Grid.Row="{{ control.row }}"
            Grid.Column="{{ control.column }}"
            {{ control.properties|join(' ') }}/>
        {% endfor %}
    </Grid>
</Window>
"""
        self._save_default_template(
            CodeTemplateType.VIEW,
            "basic_view",
            basic_view
        )

    def _create_viewmodel_templates(self):
        """Cria templates padrão para ViewModels"""
        basic_viewmodel = """
using System.ComponentModel;
using System.Runtime.CompilerServices;

namespace {{ namespace }}.ViewModels
{
    public class {{ name }}ViewModel : INotifyPropertyChanged
    {
        public event PropertyChangedEventHandler PropertyChanged;

        {% for property in properties %}
        private {{ property.type }} _{{ property.name|lower }};
        public {{ property.type }} {{ property.name }}
        {
            get => _{{ property.name|lower }};
            set
            {
                _{{ property.name|lower }} = value;
                OnPropertyChanged();
            }
        }
        {% endfor %}

        protected virtual void OnPropertyChanged([CallerMemberName] string propertyName = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }
    }
}
"""
        self._save_default_template(
            CodeTemplateType.VIEW_MODEL,
            "basic_viewmodel",
            basic_viewmodel
        )

    def _create_model_templates(self):
        """Cria templates padrão para Models"""
        basic_model = """
using System;
using System.ComponentModel.DataAnnotations;

namespace {{ namespace }}.Models
{
    public class {{ name }}
    {
        {% for property in properties %}
        {% if property.required %}[Required]{% endif %}
        {% if property.maxLength %}[MaxLength({{ property.maxLength }})]{% endif %}
        public {{ property.type }} {{ property.name }} { get; set; }
        {% endfor %}
    }
}
"""
        self._save_default_template(
            CodeTemplateType.MODEL,
            "basic_model",
            basic_model
        )

    def _create_service_templates(self):
        """Cria templates padrão para Services"""
        basic_service = """
using System;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;

namespace {{ namespace }}.Services
{
    public interface I{{ name }}Service
    {
        {% for method in methods %}
        Task<{{ method.returnType }}> {{ method.name }}({{ method.parameters|join(', ') }});
        {% endfor %}
    }

    public class {{ name }}Service : I{{ name }}Service
    {
        private readonly ILogger<{{ name }}Service> _logger;

        public {{ name }}Service(ILogger<{{ name }}Service> logger)
        {
            _logger = logger;
        }

        {% for method in methods %}
        public async Task<{{ method.returnType }}> {{ method.name }}({{ method.parameters|join(', ') }})
        {
            try
            {
                // Implementation
                throw new NotImplementedException();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, $"Error in {{ method.name }}");
                throw;
            }
        }
        {% endfor %}
    }
}
"""
        self._save_default_template(
            CodeTemplateType.SERVICE,
            "basic_service",
            basic_service
        )

    def _create_repository_templates(self):
        """Cria templates padrão para Repositories"""
        basic_repository = """
using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;

namespace {{ namespace }}.Repositories
{
    public interface I{{ name }}Repository
    {
        Task<{{ entity }}> GetByIdAsync(int id);
        Task<IEnumerable<{{ entity }}>> GetAllAsync();
        Task<{{ entity }}> AddAsync({{ entity }} entity);
        Task UpdateAsync({{ entity }} entity);
        Task DeleteAsync(int id);
    }

    public class {{ name }}Repository : I{{ name }}Repository
    {
        private readonly ApplicationDbContext _context;

        public {{ name }}Repository(ApplicationDbContext context)
        {
            _context = context;
        }

        public async Task<{{ entity }}> GetByIdAsync(int id)
        {
            return await _context.{{ entity }}s.FindAsync(id);
        }

        public async Task<IEnumerable<{{ entity }}>> GetAllAsync()
        {
            return await _context.{{ entity }}s.ToListAsync();
        }

        public async Task<{{ entity }}> AddAsync({{ entity }} entity)
        {
            await _context.{{ entity }}s.AddAsync(entity);
            await _context.SaveChangesAsync();
            return entity;
        }

        public async Task UpdateAsync({{ entity }} entity)
        {
            _context.Entry(entity).State = EntityState.Modified;
            await _context.SaveChangesAsync();
        }

        public async Task DeleteAsync(int id)
        {
            var entity = await GetByIdAsync(id);
            if (entity != null)
            {
                _context.{{ entity }}s.Remove(entity);
                await _context.SaveChangesAsync();
            }
        }
    }
}
"""
        self._save_default_template(
            CodeTemplateType.REPOSITORY,
            "basic_repository",
            basic_repository
        )

    def _save_default_template(
        self,
        template_type: CodeTemplateType,
        template_name: str,
        content: str
    ):
        """Salva template padrão"""
        template_path = (
            self.templates_path / 
            template_type.value / 
            f"{template_name}.cstemplate"
        )
        template_path.write_text(content)

    def _validate_template_data(
        self,
        template_type: CodeTemplateType,
        data: Dict
    ) -> Dict:
        """Valida dados para um template"""
        errors = []
        
        if template_type == CodeTemplateType.VIEW:
            if 'namespace' not in data:
                errors.append("Missing namespace")
            if 'name' not in data:
                errors.append("Missing view name")
                
        elif template_type == CodeTemplateType.VIEW_MODEL:
            if 'namespace' not in data:
                errors.append("Missing namespace")
            if 'name' not in data:
                errors.append("Missing viewmodel name")
            if 'properties' not in data:
                errors.append("Missing properties")
                
        # Adicione validações para outros tipos...
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    def _validate_template_content(self, content: str) -> Dict:
        """Valida conteúdo de um template"""
        errors = []
        
        try:
            # Tenta compilar template
            self.jinja_env.from_string(content)
        except Exception as e:
            errors.append(f"Invalid template syntax: {str(e)}")
            
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    def _get_template_info(self, template_type: CodeTemplateType, template_file: Path) -> Dict:
        """Obtém informações sobre um template"""
        return {
            'type': template_type.value,
            'name': template_file.stem,
            'path': str(template_file),
            'modified': template_file.stat().st_mtime
        }

    def _format_code(self, code: str) -> str:
        """Formata código gerado"""
        # Aqui você pode integrar com um formatador de código C#
        # como o dotnet-format
        return code