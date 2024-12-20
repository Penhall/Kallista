# tools/security/code_sanitizer.py
from typing import Dict, List, Optional
import asyncio
import logging
from datetime import datetime
from pathlib import Path
import re
import xml.etree.ElementTree as ET

class CodeSanitizer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.sanitization_rules = self._load_sanitization_rules()

    def _load_sanitization_rules(self) -> Dict:
        """Carrega regras de sanitização"""
        return {
            'input_validation': self._get_input_validation_rules(),
            'output_encoding': self._get_output_encoding_rules(),
            'data_protection': self._get_data_protection_rules()
        }

    async def sanitize_project(self, project_path: Path) -> Dict:
        """Realiza sanitização do projeto"""
        try:
            results = {
                'sanitized_files': [],
                'failed_files': [],
                'skipped_files': [],
                'timestamp': datetime.utcnow().isoformat()
            }

            # Analisa cada arquivo do projeto
            for file_path in project_path.rglob('*'):
                if not self._should_sanitize(file_path):
                    results['skipped_files'].append(str(file_path))
                    continue

                try:
                    sanitized = await self._sanitize_file(file_path)
                    if sanitized:
                        results['sanitized_files'].append({
                            'file': str(file_path),
                            'changes': sanitized
                        })
                except Exception as e:
                    self.logger.error(f"Failed to sanitize {file_path}: {str(e)}")
                    results['failed_files'].append({
                        'file': str(file_path),
                        'error': str(e)
                    })

            return results

        except Exception as e:
            self.logger.error(f"Project sanitization failed: {str(e)}")
            raise

    def _should_sanitize(self, file_path: Path) -> bool:
        """Verifica se o arquivo deve ser sanitizado"""
        excluded_patterns = [
            r'\.git',
            r'\.vs',
            r'bin',
            r'obj',
            r'packages',
            r'\.dll$',
            r'\.exe$',
            r'\.pdb$'
        ]
        
        # Verifica padrões de exclusão
        for pattern in excluded_patterns:
            if re.search(pattern, str(file_path)):
                return False
                
        # Verifica extensões permitidas
        allowed_extensions = ['.cs', '.xaml', '.config', '.json']
        return file_path.suffix in allowed_extensions

    async def _sanitize_file(self, file_path: Path) -> List[Dict]:
        """Sanitiza um arquivo específico"""
        changes = []
        
        try:
            content = file_path.read_text()
            sanitized_content = content
            
            # Aplica regras de sanitização baseado no tipo de arquivo
            if file_path.suffix == '.cs':
                changes.extend(await self._sanitize_csharp(sanitized_content))
            elif file_path.suffix == '.xaml':
                changes.extend(await self._sanitize_xaml(sanitized_content))
            elif file_path.suffix in ['.config', '.json']:
                changes.extend(await self._sanitize_config(sanitized_content))
                
            # Aplica as mudanças se necessário
            if changes:
                self._apply_changes(file_path, changes)
                
            return changes
            
        except Exception as e:
            self.logger.error(f"Failed to sanitize file {file_path}: {str(e)}")
            raise

    async def _sanitize_csharp(self, content: str) -> List[Dict]:
        """Sanitiza código C#"""
        changes = []
        
        # Aplica regras de validação de entrada
        for rule in self.sanitization_rules['input_validation']:
            if rule['language'] == 'csharp':
                matches = re.finditer(rule['pattern'], content)
                for match in matches:
                    changes.append({
                        'type': 'input_validation',
                        'line': content.count('\n', 0, match.start()) + 1,
                        'original': match.group(0),
                        'sanitized': rule['replacement'],
                        'description': rule['description']
                    })

        # Aplica regras de codificação de saída
        for rule in self.sanitization_rules['output_encoding']:
            if rule['language'] == 'csharp':
                matches = re.finditer(rule['pattern'], content)
                for match in matches:
                    changes.append({
                        'type': 'output_encoding',
                        'line': content.count('\n', 0, match.start()) + 1,
                        'original': match.group(0),
                        'sanitized': rule['replacement'],
                        'description': rule['description']
                    })

        # Aplica regras de proteção de dados
        for rule in self.sanitization_rules['data_protection']:
            if rule['language'] == 'csharp':
                matches = re.finditer(rule['pattern'], content)
                for match in matches:
                    changes.append({
                        'type': 'data_protection',
                        'line': content.count('\n', 0, match.start()) + 1,
                        'original': match.group(0),
                        'sanitized': rule['replacement'],
                        'description': rule['description']
                    })

        return changes

    async def _sanitize_xaml(self, content: str) -> List[Dict]:
        """Sanitiza código XAML"""
        changes = []
        
        # Parse XAML
        try:
            root = ET.fromstring(content)
            
            # Sanitiza bindings
            for elem in root.iter():
                for attr in elem.attrib:
                    if 'Binding' in attr:
                        changes.extend(self._sanitize_binding(elem, attr))
                        
            # Sanitiza event handlers
            for elem in root.iter():
                for attr in elem.attrib:
                    if attr.endswith('Click') or attr.endswith('Changed'):
                        changes.extend(self._sanitize_event_handler(elem, attr))
                        
        except ET.ParseError as e:
            self.logger.error(f"Failed to parse XAML: {str(e)}")
            
        return changes

    async def _sanitize_config(self, content: str) -> List[Dict]:
        """Sanitiza arquivos de configuração"""
        changes = []
        
        # Sanitiza connection strings
        changes.extend(self._sanitize_connection_strings(content))
        
        # Sanitiza app settings
        changes.extend(self._sanitize_app_settings(content))
        
        return changes

    def _apply_changes(self, file_path: Path, changes: List[Dict]) -> None:
        """Aplica mudanças ao arquivo"""
        try:
            content = file_path.read_text()
            updated_content = content
            
            # Aplica cada mudança
            for change in sorted(changes, key=lambda x: x['line'], reverse=True):
                lines = updated_content.splitlines()
                line_index = change['line'] - 1
                
                if 0 <= line_index < len(lines):
                    lines[line_index] = lines[line_index].replace(
                        change['original'],
                        change['sanitized']
                    )
                    updated_content = '\n'.join(lines)
            
            # Salva o arquivo atualizado
            file_path.write_text(updated_content)
            
        except Exception as e:
            self.logger.error(f"Failed to apply changes to {file_path}: {str(e)}")
            raise

   # tools/security/code_sanitizer.py (continuação)
    def _get_input_validation_rules(self) -> List[Dict]:
        """Retorna regras de validação de entrada"""
        return [
            {
                'language': 'csharp',
                'pattern': r'Request\[(.*?)\]',
                'replacement': 'Request.GetSanitizedValue($1)',
                'description': 'Sanitize request input values'
            },
            {
                'language': 'csharp',
                'pattern': r'Request\.Form\[(.*?)\]',
                'replacement': 'Request.Form.GetSanitizedValue($1)',
                'description': 'Sanitize form input values'
            },
            {
                'language': 'csharp',
                'pattern': r'Request\.QueryString\[(.*?)\]',
                'replacement': 'Request.QueryString.GetSanitizedValue($1)',
                'description': 'Sanitize query string values'
            },
            {
                'language': 'csharp',
                'pattern': r'Convert\.ToString\((.*?)\)',
                'replacement': 'SecurityHelper.SanitizeString($1)',
                'description': 'Sanitize string conversions'
            }
        ]

    def _get_output_encoding_rules(self) -> List[Dict]:
        """Retorna regras de codificação de saída"""
        return [
            {
                'language': 'csharp',
                'pattern': r'Response\.Write\((.*?)\)',
                'replacement': 'Response.WriteEncoded($1)',
                'description': 'Encode response output'
            },
            {
                'language': 'csharp',
                'pattern': r'<%=(.*?)%>',
                'replacement': '<%: $1 %>',
                'description': 'Use HTML encoding in Razor views'
            },
            {
                'language': 'xaml',
                'pattern': r'Text="{Binding (.*?)}"',
                'replacement': 'Text="{Binding $1, Converter={StaticResource HtmlEncoder}}"',
                'description': 'Encode bound text in XAML'
            },
            {
                'language': 'csharp',
                'pattern': r'Html\.Raw\((.*?)\)',
                'replacement': 'Html.Encode($1)',
                'description': 'Encode HTML output'
            }
        ]

    def _get_data_protection_rules(self) -> List[Dict]:
        """Retorna regras de proteção de dados"""
        return [
            {
                'language': 'csharp',
                'pattern': r'string\s+(\w+password\w*)\s*=\s*".*?"',
                'replacement': 'SecureString $1 = SecurityHelper.SecureStringFromString("***")',
                'description': 'Use SecureString for passwords'
            },
            {
                'language': 'csharp',
                'pattern': r'var\s+(\w*token\w*)\s*=\s*".*?"',
                'replacement': 'var $1 = SecurityHelper.EncryptToken("***")',
                'description': 'Encrypt security tokens'
            },
            {
                'language': 'config',
                'pattern': r'<add\s+key=".*?password.*?"\s+value=".*?"',
                'replacement': '<add key="$1" value="%%encrypted%%"',
                'description': 'Encrypt configuration passwords'
            },
            {
                'language': 'json',
                'pattern': r'"(\w*password\w*)"\s*:\s*".*?"',
                'replacement': '"$1": "%%encrypted%%"',
                'description': 'Encrypt JSON passwords'
            }
        ]

    def _sanitize_binding(self, element: ET.Element, attribute: str) -> List[Dict]:
        """Sanitiza um binding XAML"""
        changes = []
        binding_value = element.attrib[attribute]
        
        # Adiciona converter de segurança se necessário
        if 'Converter=' not in binding_value:
            changes.append({
                'type': 'binding_security',
                'line': 0,  # Precisa ser calculado do documento original
                'original': binding_value,
                'sanitized': binding_value.replace(
                    '}',
                    ', Converter={StaticResource SecurityConverter}}'
                ),
                'description': 'Add security converter to binding'
            })
        
        # Adiciona validação se for input
        if element.tag.endswith('TextBox'):
            changes.append({
                'type': 'input_validation',
                'line': 0,  # Precisa ser calculado do documento original
                'original': binding_value,
                'sanitized': binding_value.replace(
                    '}',
                    ', ValidatesOnDataErrors=True}'
                ),
                'description': 'Add input validation to TextBox'
            })
            
        return changes

    def _sanitize_event_handler(self, element: ET.Element, attribute: str) -> List[Dict]:
        """Sanitiza um event handler XAML"""
        changes = []
        handler_value = element.attrib[attribute]
        
        # Adiciona validação de entrada para event handlers
        if not handler_value.startswith('Secure'):
            changes.append({
                'type': 'event_security',
                'line': 0,  # Precisa ser calculado do documento original
                'original': handler_value,
                'sanitized': f'Secure{handler_value}',
                'description': 'Add security wrapper to event handler'
            })
            
        return changes

    def _sanitize_connection_strings(self, content: str) -> List[Dict]:
        """Sanitiza connection strings"""
        changes = []
        
        # Encontra e sanitiza connection strings em XML
        xml_pattern = r'<connectionStrings>.*?</connectionStrings>'
        if re.search(xml_pattern, content, re.DOTALL):
            changes.append({
                'type': 'connection_string',
                'line': 0,  # Precisa ser calculado
                'original': re.search(xml_pattern, content, re.DOTALL).group(0),
                'sanitized': '<!-- Connection strings moved to secure storage -->',
                'description': 'Move connection strings to secure storage'
            })
            
        # Encontra e sanitiza connection strings em JSON
        json_pattern = r'"ConnectionStrings"\s*:\s*{[^}]*}'
        if re.search(json_pattern, content):
            changes.append({
                'type': 'connection_string',
                'line': 0,  # Precisa ser calculado
                'original': re.search(json_pattern, content).group(0),
                'sanitized': '"ConnectionStrings": "%%secure_reference%%"',
                'description': 'Move connection strings to secure storage'
            })
            
        return changes

    def _sanitize_app_settings(self, content: str) -> List[Dict]:
        """Sanitiza configurações da aplicação"""
        changes = []
        
        # Sanitiza configurações sensíveis em XML
        xml_pattern = r'<add\s+key="(.*?password.*?)"\s+value=".*?"'
        for match in re.finditer(xml_pattern, content, re.IGNORECASE):
            changes.append({
                'type': 'app_setting',
                'line': content.count('\n', 0, match.start()) + 1,
                'original': match.group(0),
                'sanitized': f'<add key="{match.group(1)}" value="%%encrypted%%"',
                'description': 'Encrypt sensitive app setting'
            })
            
        # Sanitiza configurações sensíveis em JSON
        json_pattern = r'"(\w*password\w*)"\s*:\s*".*?"'
        for match in re.finditer(json_pattern, content, re.IGNORECASE):
            changes.append({
                'type': 'app_setting',
                'line': content.count('\n', 0, match.start()) + 1,
                'original': match.group(0),
                'sanitized': f'"{match.group(1)}": "%%encrypted%%"',
                'description': 'Encrypt sensitive app setting'
            })
            
        return changes