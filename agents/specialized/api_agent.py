# agents/specialized/api_agent.py
from crewai import Agent
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
from datetime import datetime

class ApiAgent(Agent):
    def __init__(self, llm):
        super().__init__(
            role='API Specialist',
            goal='Design and implement service layers and APIs for WPF applications',
            backstory="""You are an API architect specialized in .NET/C# service 
            layers. You excel at creating clean, efficient, and secure service 
            architectures following best practices like SOLID principles and 
            clean architecture.""",
            llm=llm
        )
        self.templates_path = Path("templates/api")
        self.templates_path.mkdir(parents=True, exist_ok=True)

    async def design_service_layer(self, requirements: Dict) -> Dict[str, Any]:
        """Design service layer architecture"""
        try:
            return {
                'interfaces': self._design_interfaces(requirements),
                'services': self._design_services(requirements),
                'dtos': self._design_dtos(requirements),
                'validators': self._design_validators(requirements),
                'middleware': self._design_middleware(requirements)
            }
        except Exception as e:
            raise Exception(f"Error in service layer design: {str(e)}")

    def _design_interfaces(self, requirements: Dict) -> List[Dict]:
        """Design service interfaces"""
        interfaces = []
        for service in requirements.get('services', []):
            interfaces.append({
                'name': f"I{service['name']}Service",
                'methods': self._define_service_methods(service),
                'events': self._define_service_events(service),
                'dependencies': self._define_service_dependencies(service)
            })
        return interfaces

    def _design_services(self, requirements: Dict) -> List[Dict]:
        """Design service implementations"""
        services = []
        for service in requirements.get('services', []):
            services.append({
                'name': f"{service['name']}Service",
                'interface': f"I{service['name']}Service",
                'implementation': self._define_service_implementation(service),
                'error_handling': self._define_error_handling(service),
                'logging': self._define_logging_strategy(service)
            })
        return services

    async def generate_service_code(self, design: Dict) -> Dict[str, str]:
        """Generate service layer code"""
        return {
            'interfaces': self._generate_interfaces(design),
            'implementations': self._generate_implementations(design),
            'dtos': self._generate_dtos(design),
            'validators': self._generate_validators(design)
        }

    def _generate_interfaces(self, design: Dict) -> Dict[str, str]:
        """Generate interface code"""
        interfaces = {}
        for interface in design['interfaces']:
            code = []
            code.append(f"public interface {interface['name']}")
            code.append("{")

            # Add methods
            for method in interface['methods']:
                params = ", ".join([f"{p['type']} {p['name']}" for p in method['parameters']])
                code.append(f"    Task<{method['return_type']}> {method['name']}({params});")

            # Add events
            for event in interface.get('events', []):
                code.append(f"    event EventHandler<{event['type']}> {event['name']};")

            code.append("}")
            interfaces[interface['name']] = "\n".join(code)
        return interfaces

    def _generate_implementations(self, design: Dict) -> Dict[str, str]:
        """Generate service implementation code"""
        implementations = {}
        for service in design['services']:
            code = []
            code.append(f"public class {service['name']} : {service['interface']}")
            code.append("{")

            # Add dependencies
            self._add_dependencies(code, service)

            # Add constructor
            self._add_constructor(code, service)

            # Add method implementations
            for method in service['implementation']['methods']:
                self._add_method_implementation(code, method)

            # Add event implementations
            for event in service.get('events', []):
                code.append(f"    public event EventHandler<{event['type']}> {event['name']};")

            code.append("}")
            implementations[service['name']] = "\n".join(code)
        return implementations

    def _add_dependencies(self, code: List[str], service: Dict) -> None:
        """Add service dependencies"""
        for dep in service.get('dependencies', []):
            code.append(f"    private readonly {dep['type']} _{dep['name'].lower()};")

    def _add_constructor(self, code: List[str], service: Dict) -> None:
        """Add service constructor"""
        deps = service.get('dependencies', [])
        params = ", ".join([f"{d['type']} {d['name'].lower()}" for d in deps])
        
        code.append(f"    public {service['name']}({params})")
        code.append("    {")
        for dep in deps:
            code.append(f"        _{dep['name'].lower()} = {dep['name'].lower()};")
        code.append("    }")

    def _add_method_implementation(self, code: List[str], method: Dict) -> None:
        """Add method implementation"""
        params = ", ".join([f"{p['type']} {p['name']}" for p in method['parameters']])
        code.append(f"    public async Task<{method['return_type']}> {method['name']}({params})")
        code.append("    {")
        
        # Add validation
        self._add_validation_code(code, method)
        
        # Add logging
        self._add_logging_code(code, method)
        
        # Add error handling
        self._add_error_handling_code(code, method)
        
        # Add actual implementation
        code.extend(method['implementation'])
        
        code.append("    }")

    def _design_dtos(self, requirements: Dict) -> List[Dict]:
        """Design Data Transfer Objects"""
        dtos = []
        for entity in requirements.get('entities', []):
            dtos.extend([
                {
                    'name': f"{entity['name']}Dto",
                    'properties': self._map_entity_to_dto_properties(entity),
                    'validations': self._define_dto_validations(entity)
                },
                {
                    'name': f"Create{entity['name']}Dto",
                    'properties': self._map_create_dto_properties(entity),
                    'validations': self._define_dto_validations(entity)
                },
                {
                    'name': f"Update{entity['name']}Dto",
                    'properties': self._map_update_dto_properties(entity),
                    'validations': self._define_dto_validations(entity)
                }
            ])
        return dtos

    def _design_validators(self, requirements: Dict) -> List[Dict]:
        """Design validators for DTOs"""
        validators = []
        for dto in self._design_dtos(requirements):
            validators.append({
                'name': f"{dto['name']}Validator",
                'rules': self._define_validation_rules(dto)
            })
        return validators

    def _design_middleware(self, requirements: Dict) -> List[Dict]:
        """Design middleware components"""
        return [
            {
                'name': 'ExceptionMiddleware',
                'order': 1,
                'handlers': self._define_exception_handlers()
            },
            {
                'name': 'LoggingMiddleware',
                'order': 2,
                'config': self._define_logging_config()
            },
            {
                'name': 'ValidationMiddleware',
                'order': 3,
                'validators': self._get_validators_list()
            }
        ]

    async def generate_api_documentation(self, design: Dict) -> str:
        """Generate API documentation"""
        doc = []
        doc.append("# Service Layer Documentation\n")

        # Add overview
        doc.append("## Overview\n")
        doc.append("This document describes the service layer architecture and available services.\n")

        # Add services documentation
        doc.append("## Services\n")
        for service in design['services']:
            doc.append(f"### {service['name']}\n")
            doc.append(f"Interface: {service['interface']}\n")
            
            doc.append("#### Methods\n")
            for method in service['implementation']['methods']:
                doc.append(f"##### {method['name']}\n")
                doc.append(f"Return type: {method['return_type']}\n")
                doc.append("Parameters:")
                for param in method['parameters']:
                    doc.append(f"- {param['name']}: {param['type']}")
                doc.append("\n")

        return "\n".join(doc)

    def save_api_design(self, design: Dict) -> None:
        """Save API design for reuse"""
        design_file = self.templates_path / f"{design['name']}.json"
        with open(design_file, 'w') as f:
            json.dump(design, f, indent=4)

    def load_api_design(self, design_name: str) -> Optional[Dict]:
        """Load a saved API design"""
        design_file = self.templates_path / f"{design_name}.json"
        if design_file.exists():
            with open(design_file, 'r') as f:
                return json.load(f)
        return None