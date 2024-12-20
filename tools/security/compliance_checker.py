# tools/security/compliance_checker.py
from typing import Dict, List, Optional
import asyncio
import logging
from datetime import datetime
from pathlib import Path
import json
import re

class ComplianceChecker:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.rules_file = Path("config/security/compliance_rules.json")
        self.rules = self._load_rules()

    def _load_rules(self) -> Dict:
        """Carrega regras de compliance"""
        try:
            if self.rules_file.exists():
                with open(self.rules_file) as f:
                    return json.load(f)
            return {
                'owasp': self._get_owasp_rules(),
                'gdpr': self._get_gdpr_rules(),
                'security_best_practices': self._get_security_best_practices()
            }
        except Exception as e:
            self.logger.error(f"Failed to load compliance rules: {str(e)}")
            return {}

    async def check_compliance(self, project_path: Path) -> Dict:
        """Verifica compliance do projeto"""
        try:
            results = {
                'owasp_compliance': [],
                'gdpr_compliance': [],
                'best_practices': [],
                'total_issues': 0,
                'compliance_score': 0.0,
                'timestamp': datetime.utcnow().isoformat()
            }

            # Verifica OWASP
            owasp_results = await self._check_owasp_compliance(project_path)
            results['owasp_compliance'] = owasp_results
            results['total_issues'] += len([
                r for r in owasp_results if not r['compliant']
            ])

            # Verifica GDPR
            gdpr_results = await self._check_gdpr_compliance(project_path)
            results['gdpr_compliance'] = gdpr_results
            results['total_issues'] += len([
                r for r in gdpr_results if not r['compliant']
            ])

            # Verifica melhores práticas
            bp_results = await self._check_security_best_practices(project_path)
            results['best_practices'] = bp_results
            results['total_issues'] += len([
                r for r in bp_results if not r['compliant']
            ])

            # Calcula score geral
            results['compliance_score'] = self._calculate_compliance_score(results)

            return results

        except Exception as e:
            self.logger.error(f"Compliance check failed: {str(e)}")
            raise

    async def _check_owasp_compliance(self, project_path: Path) -> List[Dict]:
        """Verifica compliance com OWASP"""
        results = []
        
        for rule in self.rules['owasp']:
            try:
                rule_results = await self._check_rule(
                    project_path,
                    rule
                )
                results.extend(rule_results)
            except Exception as e:
                self.logger.error(
                    f"Failed to check OWASP rule {rule['id']}: {str(e)}"
                )
                
        return results

    async def _check_gdpr_compliance(self, project_path: Path) -> List[Dict]:
        """Verifica compliance com GDPR"""
        results = []
        
        for rule in self.rules['gdpr']:
            try:
                rule_results = await self._check_rule(
                    project_path,
                    rule
                )
                results.extend(rule_results)
            except Exception as e:
                self.logger.error(
                    f"Failed to check GDPR rule {rule['id']}: {str(e)}"
                )
                
        return results

    async def _check_security_best_practices(self, project_path: Path) -> List[Dict]:
        """Verifica compliance com melhores práticas de segurança"""
        results = []
        
        for rule in self.rules['security_best_practices']:
            try:
                rule_results = await self._check_rule(
                    project_path,
                    rule
                )
                results.extend(rule_results)
            except Exception as e:
                self.logger.error(
                    f"Failed to check security best practice {rule['id']}: {str(e)}"
                )
                
        return results

    async def _check_rule(self, project_path: Path, rule: Dict) -> List[Dict]:
        """Verifica uma regra específica"""
        results = []
        
        # Verifica arquivos relevantes
        for file_path in project_path.rglob('*'):
            if not self._is_relevant_file(file_path, rule):
                continue

            try:
                content = file_path.read_text()
                
                # Verifica padrões da regra
                violations = self._check_patterns(
                    content,
                    rule['patterns']
                )
                
                if violations:
                    results.append({
                        'rule_id': rule['id'],
                        'category': rule['category'],
                        'severity': rule['severity'],
                        'file': str(file_path),
                        'violations': violations,
                        'compliant': False,
                        'description': rule['description'],
                        'recommendation': rule.get('recommendation', '')
                    })
                else:
                    results.append({
                        'rule_id': rule['id'],
                        'category': rule['category'],
                        'file': str(file_path),
                        'compliant': True
                    })
                    
            except Exception as e:
                self.logger.error(
                    f"Failed to check rule {rule['id']} for {file_path}: {str(e)}"
                )
                
        return results

    def _is_relevant_file(self, file_path: Path, rule: Dict) -> bool:
        """Verifica se o arquivo é relevante para a regra"""
        # Verifica extensões
        if 'file_types' in rule:
            return file_path.suffix in rule['file_types']
            
        # Verifica padrões de arquivo
        if 'file_patterns' in rule:
            return any(
                re.search(pattern, str(file_path))
                for pattern in rule['file_patterns']
            )
            
        return True

  # tools/security/compliance_checker.py (continuação)
    def _check_patterns(self, content: str, patterns: List[str]) -> List[Dict]:
        """Verifica padrões em um conteúdo"""
        violations = []
        
        for pattern in patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                violations.append({
                    'pattern': pattern,
                    'line': content.count('\n', 0, match.start()) + 1,
                    'match': match.group(0),
                    'context': self._get_context(content, match)
                })
                
        return violations

    def _get_context(self, content: str, match: re.Match, context_lines: int = 2) -> str:
        """Obtém o contexto de um match"""
        lines = content.splitlines()
        match_line = content.count('\n', 0, match.start())
        
        start_line = max(0, match_line - context_lines)
        end_line = min(len(lines), match_line + context_lines + 1)
        
        return '\n'.join(lines[start_line:end_line])

    def _calculate_compliance_score(self, results: Dict) -> float:
        """Calcula score geral de compliance"""
        total_checks = 0
        compliant_checks = 0
        
        # Conta checks OWASP
        total_checks += len(results['owasp_compliance'])
        compliant_checks += len([
            r for r in results['owasp_compliance']
            if r['compliant']
        ])
        
        # Conta checks GDPR
        total_checks += len(results['gdpr_compliance'])
        compliant_checks += len([
            r for r in results['gdpr_compliance']
            if r['compliant']
        ])
        
        # Conta melhores práticas
        total_checks += len(results['best_practices'])
        compliant_checks += len([
            r for r in results['best_practices']
            if r['compliant']
        ])
        
        return (compliant_checks / total_checks * 100) if total_checks > 0 else 0.0

    def _get_owasp_rules(self) -> List[Dict]:
        """Retorna regras OWASP padrão"""
        return [
            {
                'id': 'OWASP-A1',
                'category': 'Injection',
                'severity': 'high',
                'description': 'SQL Injection vulnerability check',
                'file_types': ['.cs', '.cshtml'],
                'patterns': [
                    r'string\.Format.*SELECT',
                    r'ExecuteQuery\s*\(',
                    r'Execute\s*\(\s*".*SELECT'
                ],
                'recommendation': 'Use parameterized queries or an ORM'
            },
            {
                'id': 'OWASP-A2',
                'category': 'Authentication',
                'severity': 'high',
                'description': 'Broken Authentication check',
                'file_types': ['.cs', '.config'],
                'patterns': [
                    r'FormsAuthentication\.',
                    r'ValidateUser\s*\(',
                    r'<authentication\s+mode="Forms"'
                ],
                'recommendation': 'Use ASP.NET Identity or IdentityServer4'
            },
            {
                'id': 'OWASP-A3',
                'category': 'Sensitive Data Exposure',
                'severity': 'high',
                'description': 'Sensitive data exposure check',
                'file_types': ['.cs', '.config', '.json'],
                'patterns': [
                    r'password\s*=\s*["\'].*["\']',
                    r'connectionString\s*=\s*["\'].*["\']',
                    r'private\s+key\s*=\s*["\'].*["\']'
                ],
                'recommendation': 'Use secure configuration and encryption'
            }
        ]

    def _get_gdpr_rules(self) -> List[Dict]:
        """Retorna regras GDPR padrão"""
        return [
            {
                'id': 'GDPR-1',
                'category': 'Personal Data',
                'severity': 'high',
                'description': 'Personal data storage check',
                'file_types': ['.cs', '.cshtml'],
                'patterns': [
                    r'class.*Person',
                    r'class.*User',
                    r'class.*Customer',
                    r'email|phone|address|name'
                ],
                'recommendation': 'Implement data protection and retention policies'
            },
            {
                'id': 'GDPR-2',
                'category': 'Consent',
                'severity': 'high',
                'description': 'User consent check',
                'file_types': ['.cs', '.cshtml'],
                'patterns': [
                    r'SaveUser',
                    r'CreateUser',
                    r'RegisterUser'
                ],
                'recommendation': 'Implement explicit consent mechanisms'
            },
            {
                'id': 'GDPR-3',
                'category': 'Data Protection',
                'severity': 'high',
                'description': 'Data protection measures check',
                'file_types': ['.cs', '.config'],
                'patterns': [
                    r'encrypt|decrypt',
                    r'hash|salt',
                    r'SecurityProtocol'
                ],
                'recommendation': 'Use strong encryption and secure protocols'
            }
        ]

    def _get_security_best_practices(self) -> List[Dict]:
        """Retorna regras de melhores práticas de segurança"""
        return [
            {
                'id': 'SEC-BP-1',
                'category': 'Input Validation',
                'severity': 'medium',
                'description': 'Input validation check',
                'file_types': ['.cs', '.cshtml'],
                'patterns': [
                    r'Request\.',
                    r'Form\[',
                    r'QueryString\['
                ],
                'recommendation': 'Implement comprehensive input validation'
            },
            {
                'id': 'SEC-BP-2',
                'category': 'Error Handling',
                'severity': 'medium',
                'description': 'Error handling check',
                'file_types': ['.cs'],
                'patterns': [
                    r'catch\s*\(\s*Exception\s+\w+\s*\)\s*{',
                    r'Server\.ClearError',
                    r'Response\.Write\s*\(\s*ex\.'
                ],
                'recommendation': 'Implement secure error handling'
            },
            {
                'id': 'SEC-BP-3',
                'category': 'Secure Configuration',
                'severity': 'medium',
                'description': 'Security configuration check',
                'file_types': ['.config'],
                'patterns': [
                    r'<customErrors\s+mode="Off"',
                    r'<compilation\s+debug="true"',
                    r'<trace\s+enabled="true"'
                ],
                'recommendation': 'Use secure configuration settings in production'
            }
        ]

    async def generate_compliance_report(self, results: Dict) -> Dict:
        """Gera relatório de compliance"""
        try:
            report = {
                'summary': self._generate_summary(results),
                'details': self._generate_details(results),
                'recommendations': self._generate_recommendations(results),
                'timestamp': datetime.utcnow().isoformat()
            }
            return report
        except Exception as e:
            self.logger.error(f"Failed to generate compliance report: {str(e)}")
            raise

    def _generate_summary(self, results: Dict) -> Dict:
        """Gera sumário dos resultados"""
        return {
            'compliance_score': results['compliance_score'],
            'total_issues': results['total_issues'],
            'owasp_issues': len([
                r for r in results['owasp_compliance']
                if not r['compliant']
            ]),
            'gdpr_issues': len([
                r for r in results['gdpr_compliance']
                if not r['compliant']
            ]),
            'best_practice_issues': len([
                r for r in results['best_practices']
                if not r['compliant']
            ])
        }

    def _generate_details(self, results: Dict) -> List[Dict]:
        """Gera detalhes dos resultados"""
        details = []
        categories = [
            ('OWASP', results['owasp_compliance']),
            ('GDPR', results['gdpr_compliance']),
            ('Best Practices', results['best_practices'])
        ]
        
        for category, items in categories:
            for item in items:
                if not item['compliant']:
                    details.append({
                        'category': category,
                        'rule_id': item['rule_id'],
                        'severity': item.get('severity', 'medium'),
                        'file': item['file'],
                        'violations': item.get('violations', []),
                        'description': item.get('description', '')
                    })
        
        return details

    def _generate_recommendations(self, results: Dict) -> List[Dict]:
        """Gera recomendações baseadas nos resultados"""
        recommendations = []
        
        # Agrupa recomendações por categoria
        by_category = {}
        
        for category in ['owasp_compliance', 'gdpr_compliance', 'best_practices']:
            for item in results[category]:
                if not item['compliant'] and 'recommendation' in item:
                    cat = item['category']
                    if cat not in by_category:
                        by_category[cat] = set()
                    by_category[cat].add(item['recommendation'])
        
        # Formata recomendações
        for category, items in by_category.items():
            recommendations.append({
                'category': category,
                'recommendations': list(items)
            })
        
        return recommendations