# tools/wpf/generators/base_generator.py
from pathlib import Path
from typing import Dict, Any

class BaseGenerator:
    def __init__(self):
        self.base_path = Path("tools/wpf")
        self.templates_path = self.base_path / "templates"
        
    def ensure_output_directory(self, path: Path) -> None:
        """Garante que o diretório de saída existe"""
        path.mkdir(parents=True, exist_ok=True)
        
    def load_template(self, template_path: str) -> str:
        """Carrega um template do arquivo"""
        template_file = self.templates_path / template_path
        if template_file.exists():
            return template_file.read_text(encoding='utf-8')
        return ""
        
    def save_generated_file(self, output_path: Path, content: str) -> None:
        """Salva o conteúdo gerado em um arquivo"""
        self.ensure_output_directory(output_path.parent)
        output_path.write_text(content, encoding='utf-8')

    def format_template(self, template: str, params: Dict[str, Any]) -> str:
        """Formata um template com os parâmetros fornecidos"""
        try:
            return template.format(**params)
        except KeyError as e:
            raise ValueError(f"Missing template parameter: {e}")