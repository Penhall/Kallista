# integrations/visual_studio/code_generator.py
from typing import Dict, List
from pathlib import Path
import json

class VSCodeGenerator:
    def __init__(self):
        self.snippets_path = Path("Snippets")
        self.snippets_path.mkdir(exist_ok=True)
        self.item_templates_path = Path("ItemTemplates")
        self.item_templates_path.mkdir(exist_ok=True)

    def generate_code_snippet(self, config: Dict) -> str:
        """Gera snippet de código"""
        return f'''<?xml version="1.0" encoding="utf-8"?>
<CodeSnippets xmlns="http://schemas.microsoft.com/VisualStudio/2005/CodeSnippet">
    <CodeSnippet Format="1.0.0">
        <Header>
            <Title>{config['title']}</Title>
            <Author>{config['author']}</Author>
            <Description>{config['description']}</Description>
            <Shortcut>{config['shortcut']}</Shortcut>
        </Header>
        <Snippet>
            <Declarations>
                {self._generate_declarations(config)}
            </Declarations>
            <Code Language="{config['language']}" Kind="method body">
                <![CDATA[{config['code']}]]>
            </Code>
        </Snippet>
    </CodeSnippet>
</CodeSnippets>'''

    def generate_item_template(self, config: Dict) -> Dict[str, str]:
        """Gera template de item"""
        templates = {}
        
        # Template Definition
        templates['vstemplate'] = f'''<?xml version="1.0" encoding="utf-8"?>
<VSTemplate Version="3.0.0" Type="Item" xmlns="http://schemas.microsoft.com/developer/vstemplate/2005">
    <TemplateData>
        <Name>{config['name']}</Name>
        <Description>{config['description']}</Description>
        <ProjectType>CSharp</ProjectType>
        <DefaultName>{config['default_name']}</DefaultName>
        <SortOrder>10</SortOrder>
        <Icon>icon.png</Icon>
    </TemplateData>
    <TemplateContent>
        {self._generate_template_content(config)}
    </TemplateContent>
</VSTemplate>'''

        # Template Files
        templates.update(self._generate_template_files(config))
        
        return templates

    def _generate_declarations(self, config: Dict) -> str:
        """Gera declarações para snippets"""
        declarations = []
        for literal in config.get('literals', []):
            declarations.append(f'''<Literal>
                <ID>{literal['id']}</ID>
                <ToolTip>{literal['tooltip']}</ToolTip>
                <Default>{literal['default']}</Default>
            </Literal>''')
        return '\n            '.join(declarations)

    def _generate_template_content(self, config: Dict) -> str:
        """Gera conteúdo do template"""
        content = []
        for file in config.get('files', []):
            content.append(f'<ProjectItem ReplaceParameters="true">{file}</ProjectItem>')
        return '\n        '.join(content)

    def save_snippet(self, name: str, content: str):
        """Salva snippet em arquivo"""
        snippet_file = self.snippets_path / f"{name}.snippet"
        snippet_file.write_text(content)

    def save_item_template(self, name: str, templates: Dict[str, str]):
        """Salva template de item em arquivos"""
        template_dir = self.item_templates_path / name
        template_dir.mkdir(exist_ok=True)
        
        for filename, content in templates.items():
            file_path = template_dir / filename
            file_path.write_text(content)