# tools/code/generator.py
from typing import Dict, Optional, List
from pathlib import Path
import jinja2
import os

class CodeGenerator:
    def __init__(self, templates_dir: str = "templates"):
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(templates_dir)
        )
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)

    def generate_code(self, 
                     template_name: str, 
                     data: Dict, 
                     output_path: Optional[str] = None) -> str:
        """Gera código usando templates predefinidos"""
        try:
            template = self.template_env.get_template(template_name)
            generated_code = template.render(**data)
            
            if output_path:
                output_file = self.output_dir / output_path
                output_file.parent.mkdir(parents=True, exist_ok=True)
                output_file.write_text(generated_code)
                
            return generated_code
        except Exception as e:
            raise Exception(f"Erro na geração de código: {str(e)}")

    def generate_wpf_view(self, view_data: Dict) -> str:
        """Gera código XAML para views WPF"""
        template_data = {
            'view_name': view_data.get('name'),
            'controls': view_data.get('controls', []),
            'resources': view_data.get('resources', {}),
            'bindings': view_data.get('bindings', {})
        }
        return self.generate_code('wpf_view.xaml', template_data)

    def generate_view_model(self, vm_data: Dict) -> str:
        """Gera código para ViewModels"""
        template_data = {
            'class_name': vm_data.get('name'),
            'properties': vm_data.get('properties', []),
            'commands': vm_data.get('commands', []),
            'dependencies': vm_data.get('dependencies', [])
        }
        return self.generate_code('view_model.cs', template_data)