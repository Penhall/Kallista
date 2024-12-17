# templates/api/api_templates.py
from typing import Dict, Any
from pathlib import Path

class ApiTemplates:
    def __init__(self):
        self.templates_path = Path("templates/api")
        self.templates_path.mkdir(parents=True, exist_ok=True)

    def get_controller_template(self, config: Dict[str, Any]) -> str:
        """Gera template para Controller"""
        return f'''
using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using {config['namespace']}.Services;
using {config['namespace']}.DTOs;
using {config['namespace']}.Models;

namespace {config['namespace']}.Controllers
{{
    [ApiController]
    [Route("api/[controller]")]
    public class {config['name']}Controller : ControllerBase
    {{
        private readonly I{config['name']}Service _service;
        private readonly ILogger<{config['name']}Controller> _logger;

        public {config['name']}Controller(
            I{config['name']}Service service,
            ILogger<{config['name']}Controller> logger)
        {{
            _service = service;
            _logger = logger;
        }}

        [HttpGet]
        public async Task<ActionResult<IEnumerable<{config['name']}Dto>>> GetAll()
        {{
            try
            {{
                var items = await _service.GetAllAsync();
                return Ok(items);
            }}
            catch (Exception ex)
            {{
                _logger.LogError(ex, "Error getting all {name}", typeof({config['name']}));
                return StatusCode(500, "Internal server error");
            }}
        }}

        [HttpGet("{{id}}")]
        public async Task<ActionResult<{config['name']}Dto>> GetById(int id)
        {{
            try
            {{
                var item = await _service.GetByIdAsync(id);
                if (item == null)
                    return NotFound();

                return Ok(item);
            }}
            catch (Exception ex)
            {{
                _logger.LogError(ex, "Error getting {name} with id {{id}}", typeof({config['name']}), id);
                return StatusCode(500, "Internal server error");
            }}
        }}

        [HttpPost]
        public async Task<ActionResult<{config['name']}Dto>> Create([FromBody] Create{config['name']}Dto dto)
        {{
            try
            {{
                var created = await _service.CreateAsync(dto);
                return CreatedAtAction(
                    nameof(GetById),
                    new {{ id = created.Id }},
                    created
                );
            }}
            catch (Exception ex)
            {{
                _logger.LogError(ex, "Error creating {name}", typeof({config['name']}));
                return StatusCode(500, "Internal server error");
            }}
        }}

        [HttpPut("{{id}}")]
        public async Task<IActionResult> Update(int id, [FromBody] Update{config['name']}Dto dto)
        {{
            try
            {{
                await _service.UpdateAsync(id, dto);
                return NoContent();
            }}
            catch (KeyNotFoundException)
            {{
                return NotFound();
            }}
            catch (Exception ex)
            {{
                _logger.LogError(ex, "Error updating {name} with id {{id}}", typeof({config['name']}), id);
                return StatusCode(500, "Internal server error");
            }}
        }}

        [HttpDelete("{{id}}")]
        public async Task<IActionResult> Delete(int id)
        {{
            try
            {{
                await _service.DeleteAsync(id);
                return NoContent();
            }}
            catch (KeyNotFoundException)
            {{
                return NotFound();
            }}
            catch (Exception ex)
            {{
                _logger.LogError(ex, "Error deleting {name} with id {{id}}", typeof({config['name']}), id);
                return StatusCode(500, "Internal server error");
            }}
        }}
    }}
}}
'''

    def get_service_template(self, config: Dict[str, Any]) -> str:
        """Gera template para Service"""
        return f'''
using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using AutoMapper;
using {config['namespace']}.DTOs;
using {config['namespace']}.Models;
using {config['namespace']}.Interfaces;

namespace {config['namespace']}.Services
{{
    public class {config['name']}Service : I{config['name']}Service
    {{
        private readonly IUnitOfWork _unitOfWork;
        private readonly IMapper _mapper;
        private readonly ILogger<{config['name']}Service> _logger;

        public {config['name']}Service(
            IUnitOfWork unitOfWork,
            IMapper mapper,
            ILogger<{config['name']}Service> logger)
        {{
            _unitOfWork = unitOfWork;
            _mapper = mapper;
            _logger = logger;
        }}

        public async Task<IEnumerable<{config['name']}Dto>> GetAllAsync()
        {{
            var entities = await _unitOfWork.{config['name']}Repository.GetAllAsync();
            return _mapper.Map<IEnumerable<{config['name']}Dto>>(entities);
        }}

        public async Task<{config['name']}Dto> GetByIdAsync(int id)
        {{
            var entity = await _unitOfWork.{config['name']}Repository.GetByIdAsync(id);
            return _mapper.Map<{config['name']}Dto>(entity);
        }}

        public async Task<{config['name']}Dto> CreateAsync(Create{config['name']}Dto dto)
        {{
            var entity = _mapper.Map<{config['name']}>(dto);
            await _unitOfWork.{config['name']}Repository.AddAsync(entity);
            await _unitOfWork.SaveChangesAsync();
            return _mapper.Map<{config['name']}Dto>(entity);
        }}

        public async Task UpdateAsync(int id, Update{config['name']}Dto dto)
        {{
            var entity = await _unitOfWork.{config['name']}Repository.GetByIdAsync(id)
                ?? throw new KeyNotFoundException($"{config['name']} with id {{id}} not found");

            _mapper.Map(dto, entity);
            await _unitOfWork.{config['name']}Repository.UpdateAsync(entity);
            await _unitOfWork.SaveChangesAsync();
        }}

        public async Task DeleteAsync(int id)
        {{
            var entity = await _unitOfWork.{config['name']}Repository.GetByIdAsync(id)
                ?? throw new KeyNotFoundException($"{config['name']} with id {{id}} not found");

            await _unitOfWork.{config['name']}Repository.DeleteAsync(id);
            await _unitOfWork.SaveChangesAsync();
        }}
    }}
}}
'''

    def get_dto_template(self, config: Dict[str, Any]) -> str:
        """Gera template para DTOs"""
        return f'''
using System;
using System.ComponentModel.DataAnnotations;

namespace {config['namespace']}.DTOs
{{
    public class {config['name']}Dto
    {{
        public int Id {{ get; set; }}
        {self._generate_dto_properties(config)}
    }}

    public class Create{config['name']}Dto
    {{
        {self._generate_dto_properties(config, True)}
    }}

    public class Update{config['name']}Dto
    {{
        {self._generate_dto_properties(config, True)}
    }}
}}
'''

    def get_automapper_profile_template(self, config: Dict[str, Any]) -> str:
        """Gera template para perfil do AutoMapper"""
        return f'''
using AutoMapper;
using {config['namespace']}.Models;
using {config['namespace']}.DTOs;

namespace {config['namespace']}.Mappings
{{
    public class {config['name']}Profile : Profile
    {{
        public {config['name']}Profile()
        {{
            CreateMap<{config['name']}, {config['name']}Dto>();
            CreateMap<Create{config['name']}Dto, {config['name']}>();
            CreateMap<Update{config['name']}Dto, {config['name']}>();
        }}
    }}
}}
'''

    def get_validator_template(self, config: Dict[str, Any]) -> str:
        """Gera template para validadores"""
        return f'''
using FluentValidation;
using {config['namespace']}.DTOs;

namespace {config['namespace']}.Validators
{{
    public class Create{config['name']}DtoValidator : AbstractValidator<Create{config['name']}Dto>
    {{
        public Create{config['name']}DtoValidator()
        {{
            {self._generate_validation_rules(config)}
        }}
    }}

    public class Update{config['name']}DtoValidator : AbstractValidator<Update{config['name']}Dto>
    {{
        public Update{config['name']}DtoValidator()
        {{
            {self._generate_validation_rules(config)}
        }}
    }}
}}
'''

    def _generate_dto_properties(self, config: Dict[str, Any], include_validation: bool = False) -> str:
        """Gera propriedades para DTOs"""
        properties = []
        for prop in config.get('properties', []):
            if include_validation and prop.get('required', False):
                properties.append(f'''
        [Required(ErrorMessage = "{{prop['name']}} is required")]''')
            if include_validation and 'max_length' in prop:
                properties.append(f'''
        [StringLength({prop['max_length']}, ErrorMessage = "{{prop['name']}} cannot exceed {prop['max_length']} characters")]''')
            properties.append(f'''
        public {prop['type']} {prop['name']} {{ get; set; }}''')
        return '\n'.join(properties)

    def _generate_validation_rules(self, config: Dict[str, Any]) -> str:
        """Gera regras de validação para FluentValidation"""
        rules = []
        for prop in config.get('properties', []):
            if prop.get('required', False):
                rules.append(f'''
            RuleFor(x => x.{prop['name']})
                .NotEmpty().WithMessage("{prop['name']} is required");''')
            if 'max_length' in prop:
                rules.append(f'''
            RuleFor(x => x.{prop['name']})
                .MaximumLength({prop['max_length']}).WithMessage("{prop['name']} cannot exceed {prop['max_length']} characters");''')
            if prop.get('type') == 'string' and prop.get('min_length'):
                rules.append(f'''
            RuleFor(x => x.{prop['name']})
                .MinimumLength({prop['min_length']}).WithMessage("{prop['name']} must be at least {prop['min_length']} characters");''')
        return '\n'.join(rules)

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