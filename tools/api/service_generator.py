# tools/api/service_generator.py
from typing import Dict, List, Any
from pathlib import Path
import json

class ServiceGenerator:
    def __init__(self):
        self.output_path = Path("output/services")
        self.output_path.mkdir(parents=True, exist_ok=True)

    def generate_service(self, service_config: Dict) -> Dict[str, str]:
        """Gera código para um serviço completo"""
        return {
            'interface': self.generate_interface(service_config),
            'implementation': self.generate_implementation(service_config),
            'dto': self.generate_dtos(service_config),
            'validator': self.generate_validator(service_config)
        }

    def generate_interface(self, config: Dict) -> str:
        """Gera código para a interface do serviço"""
        code = []
        
        # Imports
        code.extend([
            "using System;",
            "using System.Collections.Generic;",
            "using System.Threading.Tasks;",
            "using YourNamespace.DTOs;",
            ""
        ])

        # Interface
        code.append(f"namespace {config.get('namespace', 'YourNamespace.Services')}")
        code.append("{")
        code.append(f"    public interface I{config['name']}Service")
        code.append("    {")

        # Métodos
        for method in config.get('methods', []):
            code.extend(self._generate_interface_method(method))

        code.append("    }")
        code.append("}")

        return "\n".join(code)

    def generate_implementation(self, config: Dict) -> str:
        """Gera código para a implementação do serviço"""
        code = []
        
        # Imports
        code.extend([
            "using System;",
            "using System.Collections.Generic;",
            "using System.Threading.Tasks;",
            "using AutoMapper;",
            "using Microsoft.Extensions.Logging;",
            "using YourNamespace.DTOs;",
            "using YourNamespace.Entities;",
            "using YourNamespace.Repositories;",
            ""
        ])

        # Classe
        code.append(f"namespace {config.get('namespace', 'YourNamespace.Services')}")
        code.append("{")
        code.append(f"    public class {config['name']}Service : I{config['name']}Service")
        code.append("    {")

        # Dependências
        code.extend(self._generate_dependencies(config))
        
        # Construtor
        code.extend(self._generate_constructor(config))

        # Métodos
        for method in config.get('methods', []):
            code.extend(self._generate_implementation_method(method))

        code.append("    }")
        code.append("}")

        return "\n".join(code)

    def generate_dtos(self, config: Dict) -> Dict[str, str]:
        """Gera DTOs para o serviço"""
        dtos = {}
        
        for dto in config.get('dtos', []):
            code = []
            
            # Imports
            code.extend([
                "using System;",
                "using System.ComponentModel.DataAnnotations;",
                ""
            ])

            # Classe DTO
            code.append(f"namespace {config.get('namespace', 'YourNamespace')}.DTOs")
            code.append("{")
            code.append(f"    public class {dto['name']}")
            code.append("    {")

            # Propriedades
            for prop in dto.get('properties', []):
                code.extend(self._generate_dto_property(prop))

            code.append("    }")
            code.append("}")

            dtos[dto['name']] = "\n".join(code)

        return dtos

    def generate_validator(self, config: Dict) -> str:
        """Gera validador para os DTOs do serviço"""
        code = []
        
        # Imports
        code.extend([
            "using FluentValidation;",
            "using YourNamespace.DTOs;",
            ""
        ])

        # Classe Validator
        code.append(f"namespace {config.get('namespace', 'YourNamespace.Validators')}")
        code.append("{")
        
        for dto in config.get('dtos', []):
            code.extend(self._generate_dto_validator(dto))

        code.append("}")

        return "\n".join(code)

    def _generate_interface_method(self, method: Dict) -> List[str]:
        """Gera código para um método de interface"""
        params = ", ".join([f"{p['type']} {p['name']}" for p in method.get('parameters', [])])
        return [f"        Task<{method['return_type']}> {method['name']}({params});"]

    def _generate_dependencies(self, config: Dict) -> List[str]:
        """Gera código para as dependências do serviço"""
        deps = []
        deps.append("        private readonly ILogger<{config['name']}Service> _logger;")
        deps.append("        private readonly IMapper _mapper;")
        
        for dep in config.get('dependencies', []):
            deps.append(f"        private readonly {dep['type']} _{dep['name'].lower()};")
            
        return deps

    def _generate_constructor(self, config: Dict) -> List[str]:
        """Gera código para o construtor do serviço"""
        code = []
        
        # Parâmetros do construtor
        params = [
            "ILogger<{config['name']}Service> logger",
            "IMapper mapper"
        ]
        
        for dep in config.get('dependencies', []):
            params.append(f"{dep['type']} {dep['name'].lower()}")
            
        param_str = ", ".join(params)
        
        code.append(f"        public {config['name']}Service({param_str})")
        code.append("        {")
        code.append("            _logger = logger;")
        code.append("            _mapper = mapper;")
        
        for dep in config.get('dependencies', []):
            code.append(f"            _{dep['name'].lower()} = {dep['name'].lower()};")
            
        code.append("        }")
        code.append("")
        
        return code

    def _generate_implementation_method(self, method: Dict) -> List[str]:
        """Gera código para um método de implementação"""
        code = []
        
        params = ", ".join([f"{p['type']} {p['name']}" for p in method.get('parameters', [])])
        code.append(f"        public async Task<{method['return_type']}> {method['name']}({params})")
        code.append("        {")
        
        # Logging
        code.append(f'            _logger.LogInformation($"Executing {method["name"]}");')
        
        # Try-catch
        code.append("            try")
        code.append("            {")
        
        # Implementação
        if method.get('implementation'):
            code.extend([f"                {line}" for line in method['implementation']])
        else:
            code.append("                throw new NotImplementedException();")
            
        code.append("            }")
        code.append("            catch (Exception ex)")
        code.append("            {")
        code.append(f'                _logger.LogError(ex, $"Error executing {method["name"]}");')
        code.append("                throw;")
        code.append("            }")
        
        code.append("        }")
        code.append("")
        
        return code

    def _generate_dto_property(self, prop: Dict) -> List[str]:
        """Gera código para uma propriedade de DTO"""
        code = []
        
        # Validação
        if validations := prop.get('validations', []):
            for validation in validations:
                code.append(f"        [{validation}]")
                
        # Propriedade
        code.append(f"        public {prop['type']} {prop['name']} {{ get; set; }}")
        
        return code

    def _generate_dto_validator(self, dto: Dict) -> List[str]:
        """Gera código para um validador de DTO"""
        code = []
        
        code.append(f"    public class {dto['name']}Validator : AbstractValidator<{dto['name']}>")
        code.append("    {")
        code.append(f"        public {dto['name']}Validator()")
        code.append("        {")
        
        for rule in dto.get('validation_rules', []):
            code.append(f"            {rule};")
            
        code.append("        }")
        code.append("    }")
        code.append("")
        
        return code

    def save_service(self, name: str, service_code: Dict[str, str]):
        """Salva código do serviço em arquivos"""
        service_dir = self.output_path / name
        service_dir.mkdir(exist_ok=True)
        
        for file_name, content in service_code.items():
            file_path = service_dir / f"{file_name}.cs"
            with open(file_path, 'w') as f:
                f.write(content)