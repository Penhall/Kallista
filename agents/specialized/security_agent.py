# agents/specialized/security_agent.py
from crewai import Agent
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime

class SecurityAgent(Agent):
    def __init__(self, llm):
        super().__init__(
            role='Security Specialist',
            goal='Analyze and implement security measures in WPF applications',
            backstory="""You are a security expert specialized in application security. 
            You excel at identifying vulnerabilities and implementing secure coding practices.""",
            llm=llm
        )

    async def analyze_security(self, structure: Dict) -> Dict:
        """Analisa segurança do projeto"""
        try:
            project_path = Path(structure['metadata'].get('path', '.'))
            
            results = {
                'vulnerabilities': [],
                'code_quality': [],
                'compliance': [],
                'dependencies': [],
                'timestamp': datetime.utcnow().isoformat()
            }

            results['vulnerabilities'] = await self._check_vulnerabilities(project_path, structure)
            results['code_quality'] = await self._analyze_code_quality(project_path, structure)
            results['compliance'] = await self._check_compliance(structure)
            results['dependencies'] = await self._check_dependencies(structure)

            return results
        except Exception as e:
            print(f"Erro na análise de segurança: {str(e)}")
            return {}

    async def _check_vulnerabilities(self, project_path: Path, structure: Dict) -> List[Dict]:
        """Verifica vulnerabilidades de segurança"""
        vulnerabilities = []

        # Verificar injeção SQL
        if structure.get('database', {}).get('type') == 'SQL':
            vulnerabilities.append({
                'type': 'SQL Injection',
                'severity': 'High',
                'recommendation': 'Use parameterized queries or an ORM',
                'mitigation': self._get_sql_injection_mitigation()
            })

        # Verificar XSS
        if structure.get('features', {}).get('user_input'):
            vulnerabilities.append({
                'type': 'Cross-site Scripting (XSS)',
                'severity': 'Medium',
                'recommendation': 'Validate and encode all user input',
                'mitigation': self._get_xss_mitigation()
            })

        # Verificar autenticação
        auth_config = structure.get('features', {}).get('authentication', {})
        if auth_config:
            vulnerabilities.extend(self._check_auth_vulnerabilities(auth_config))

        return vulnerabilities

    async def _analyze_code_quality(self, project_path: Path, structure: Dict) -> List[Dict]:
        """Analisa qualidade do código sob perspectiva de segurança"""
        quality_issues = []

        # Verificar práticas de codificação segura
        quality_issues.extend(self._check_secure_coding_practices(structure))

        # Verificar gestão de erros
        if 'error_handling' in structure.get('features', {}):
            quality_issues.extend(self._check_error_handling(structure))

        # Verificar logging
        if 'logging' in structure.get('features', {}):
            quality_issues.extend(self._check_logging_practices(structure))

        return quality_issues

    async def _check_compliance(self, structure: Dict) -> List[Dict]:
        """Verifica conformidade com padrões de segurança"""
        compliance_results = []

        # OWASP Top 10
        compliance_results.extend(self._check_owasp_compliance())

        # GDPR (se aplicável)
        if structure.get('features', {}).get('data_protection'):
            compliance_results.extend(self._check_gdpr_compliance())

        return compliance_results

    async def _check_dependencies(self, structure: Dict) -> List[Dict]:
        """Verifica segurança das dependências"""
        dependency_results = []

        # Verificar versões das dependências
        packages = structure.get('dependencies', {}).get('packages', [])
        for package in packages:
            dependency_results.extend(self._check_package_security(package))

        return dependency_results

    def _get_sql_injection_mitigation(self) -> Dict:
        """Retorna mitigação para SQL Injection"""
        return {
            'code_example': '''
            // Use Entity Framework
            using (var context = new AppDbContext())
            {
                var user = context.Users
                    .Where(u => u.Username == username)
                    .FirstOrDefault();
            }
            ''',
            'description': 'Use Entity Framework ou parâmetros para prevenir SQL Injection'
        }

    def _get_xss_mitigation(self) -> Dict:
        """Retorna mitigação para XSS"""
        return {
            'code_example': '''
            // Encode output
            using System.Web;
            string encodedValue = HttpUtility.HtmlEncode(userInput);
            ''',
            'description': 'Sempre encode dados de entrada do usuário'
        }

    def _check_auth_vulnerabilities(self, auth_config: Dict) -> List[Dict]:
        """Verifica vulnerabilidades de autenticação"""
        return [{
            'type': 'Authentication',
            'checks': [
                {
                    'name': 'Password Storage',
                    'status': 'Warning',
                    'recommendation': 'Use secure password hashing'
                },
                {
                    'name': 'Session Management',
                    'status': 'Info',
                    'recommendation': 'Implement proper session timeout'
                }
            ]
        }]

    def _check_secure_coding_practices(self, structure: Dict) -> List[Dict]:
        """Verifica práticas de codificação segura"""
        return [{
            'category': 'Secure Coding',
            'issues': [
                {
                    'type': 'Input Validation',
                    'severity': 'Medium',
                    'recommendation': 'Implement comprehensive input validation'
                },
                {
                    'type': 'Output Encoding',
                    'severity': 'Medium',
                    'recommendation': 'Encode all output to prevent XSS'
                }
            ]
        }]

    def _check_error_handling(self, structure: Dict) -> List[Dict]:
        """Verifica práticas de tratamento de erro"""
        return [{
            'category': 'Error Handling',
            'issues': [
                {
                    'type': 'Exception Management',
                    'severity': 'Medium',
                    'recommendation': 'Implement global error handling'
                }
            ]
        }]

    def _check_logging_practices(self, structure: Dict) -> List[Dict]:
        """Verifica práticas de logging"""
        return [{
            'category': 'Logging',
            'issues': [
                {
                    'type': 'Sensitive Data',
                    'severity': 'High',
                    'recommendation': 'Avoid logging sensitive information'
                }
            ]
        }]

    def _check_owasp_compliance(self) -> List[Dict]:
        """Verifica conformidade com OWASP Top 10"""
        return [{
            'standard': 'OWASP Top 10',
            'checks': [
                {
                    'id': 'A01:2021',
                    'name': 'Broken Access Control',
                    'status': 'Review Required'
                },
                {
                    'id': 'A02:2021',
                    'name': 'Cryptographic Failures',
                    'status': 'Review Required'
                }
            ]
        }]

    def _check_gdpr_compliance(self) -> List[Dict]:
        """Verifica conformidade com GDPR"""
        return [{
            'standard': 'GDPR',
            'checks': [
                {
                    'article': 'Art. 32',
                    'name': 'Security of Processing',
                    'status': 'Review Required'
                }
            ]
        }]

    def _check_package_security(self, package: Dict) -> List[Dict]:
        """Verifica segurança de um pacote"""
        return [{
            'package': package.get('name'),
            'version': package.get('version'),
            'status': 'Check Required',
            'recommendation': 'Verify package version for known vulnerabilities'
        }]