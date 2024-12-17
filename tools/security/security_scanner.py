# tools/security/security_scanner.py
from typing import Dict, List, Set
import re
from pathlib import Path
import ast

class SecurityScanner:
    def __init__(self):
        self.vulnerability_patterns = {
            'sql_injection': [
                r'string\.Format.*SELECT.*\{0\}',
                r'ExecuteNonQuery\s*\(\s*".*\+',
                r'ExecuteScalar\s*\(\s*".*\+'
            ],
            'xss': [
                r'Response\.Write\s*\(',
                r'innerHTML\s*=',
                r'document\.write\s*\('
            ],
            'hardcoded_credentials': [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'pwd\s*=\s*["\'][^"\']+["\']',
                r'connectionString\s*=\s*["\'][^"\']+["\']'
            ]
        }

    def scan_file(self, file_path: str) -> Dict:
        """Escaneia um arquivo em busca de vulnerabilidades"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return {
            'vulnerabilities': self._find_vulnerabilities(content),
            'security_metrics': self._calculate_security_metrics(content),
            'recommendations': self._generate_recommendations(content)
        }

    def _find_vulnerabilities(self, content: str) -> List[Dict]:
        """Encontra vulnerabilidades no código"""
        vulnerabilities = []
        for vuln_type, patterns in self.vulnerability_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.MULTILINE)
                for match in matches:
                    vulnerabilities.append({
                        'type': vuln_type,
                        'line': content.count('\n', 0, match.start()) + 1,
                        'code': match.group(),
                        'severity': self._determine_severity(vuln_type)
                    })
        return vulnerabilities

    def _calculate_security_metrics(self, content: str) -> Dict:
        """Calcula métricas de segurança"""
        return {
            'potential_vulnerabilities': len(self._find_vulnerabilities(content)),
            'sensitive_data_exposure': self._check_sensitive_data(content),
            'security_controls': self._identify_security_controls(content)
        }

    def _determine_severity(self, vuln_type: str) -> str:
        """Determina a severidade da vulnerabilidade"""
        severity_map = {
            'sql_injection': 'HIGH',
            'xss': 'MEDIUM',
            'hardcoded_credentials': 'HIGH'
        }
        return severity_map.get(vuln_type, 'LOW')

    def _check_sensitive_data(self, content: str) -> Dict:
        """Verifica exposição de dados sensíveis"""
        patterns = {
            'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'api_key': r'api[_-]?key.*=.*["\'][a-zA-Z0-9]{32,}["\']'
        }
        
        findings = {}
        for data_type, pattern in patterns.items():
            matches = re.finditer(pattern, content, re.MULTILINE)
            findings[data_type] = len(list(matches))
        
        return findings

    def _identify_security_controls(self, content: str) -> Dict:
        """Identifica controles de segurança implementados"""
        controls = {
            'input_validation': len(re.findall(r'Validate|Sanitize|Clean', content)),
            'encryption': len(re.findall(r'Encrypt|Decrypt|Hash', content)),
            'authentication': len(re.findall(r'Authenticate|Authorization|Identity', content))
        }
        return controls

    def _generate_recommendations(self, content: str) -> List[str]:
        """Gera recomendações de segurança baseadas na análise"""
        recommendations = []
        vulnerabilities = self._find_vulnerabilities(content)
        
        if any(v['type'] == 'sql_injection' for v in vulnerabilities):
            recommendations.append(
                "Utilize parâmetros em consultas SQL para prevenir injeção SQL"
            )
            
        if any(v['type'] == 'xss' for v in vulnerabilities):
            recommendations.append(
                "Implemente sanitização de entrada e escape de saída para prevenir XSS"
            )
            
        if any(v['type'] == 'hardcoded_credentials' for v in vulnerabilities):
            recommendations.append(
                "Mova credenciais para arquivos de configuração seguros ou use gerenciamento de segredos"
            )
            
        return recommendations