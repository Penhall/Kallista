# tools/code/analyzer.py
from typing import Dict, List, Set
import ast
import re
from pathlib import Path

class CodeAnalyzer:
    def __init__(self):
        self.patterns = {
            'mvvm_violations': [
                r'code_behind\..*',
                r'Window_Loaded',
                r'Button_Click'
            ],
            'naming_violations': [
                r'^[a-z]',  # Classes começando com minúscula
                r'[aeiou]$'  # Variáveis terminando em vogal
            ]
        }

    def analyze_csharp_file(self, file_path: str) -> Dict:
        """Analisa arquivo C# em busca de problemas e métricas"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return {
            'metrics': self._calculate_metrics(content),
            'violations': self._find_violations(content),
            'dependencies': self._extract_dependencies(content),
            'complexity': self._calculate_complexity(content)
        }

    def _calculate_metrics(self, content: str) -> Dict:
        """Calcula métricas do código"""
        lines = content.split('\n')
        return {
            'total_lines': len(lines),
            'code_lines': len([l for l in lines if l.strip() and not l.strip().startswith('//')]),
            'comment_lines': len([l for l in lines if l.strip().startswith('//')]),
            'classes': len(re.findall(r'class\s+\w+', content)),
            'methods': len(re.findall(r'(public|private|protected)\s+\w+\s+\w+\s*\(', content))
        }

    def _find_violations(self, content: str) -> List[Dict]:
        """Encontra violações de padrões no código"""
        violations = []
        for pattern_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.MULTILINE)
                for match in matches:
                    violations.append({
                        'type': pattern_type,
                        'line': content.count('\n', 0, match.start()) + 1,
                        'message': f'Violação do padrão {pattern_type}',
                        'code': match.group()
                    })
        return violations

    def _extract_dependencies(self, content: str) -> Set[str]:
        """Extrai dependências do código"""
        using_statements = re.findall(r'using\s+([\w\.]+);', content)
        return set(using_statements)

    def _calculate_complexity(self, content: str) -> int:
        """Calcula complexidade ciclomática"""
        complexity = 1  # Base complexity
        complexity += len(re.findall(r'\bif\b', content))
        complexity += len(re.findall(r'\bwhile\b', content))
        complexity += len(re.findall(r'\bfor\b', content))
        complexity += len(re.findall(r'\bforeach\b', content))
        complexity += len(re.findall(r'\b\?\b', content))  # Conditional operators
        complexity += len(re.findall(r'\b\|\|\b', content))  # Logical OR
        complexity += len(re.findall(r'\b&&\b', content))  # Logical AND
        return complexity