# tests/system/test_security.py
import unittest
import asyncio
from pathlib import Path
import json
import shutil
from datetime import datetime
import hashlib
import secrets

from kallista.core import KallistaSystem
from tools.security.security_scanner import SecurityScanner
from tools.security.code_sanitizer import CodeSanitizer
from tools.security.vulnerability_scanner import VulnerabilityScanner
from tools.security.compliance_checker import ComplianceChecker

class TestKallistaSecurity(unittest.TestCase):
    def setUp(self):
        """Setup para os testes de segurança"""
        self.config = {
            'base_dir': 'test_security',
            'output_dir': 'test_output',
            'logs_dir': 'test_logs',
            'security_rules': 'security_rules.json',
            'security_thresholds': {
                'max_risk_score': 7.0,
                'min_compliance_score': 85.0
            }
        }
        
        # Cria diretórios necessários
        for dir_name in self.config.values():
            if isinstance(dir_name, str) and not dir_name.endswith('.json'):
                Path(dir_name).mkdir(exist_ok=True)
        
        # Inicializa sistema e ferramentas
        self.system = KallistaSystem(self.config)
        self.security_scanner = SecurityScanner()
        self.code_sanitizer = CodeSanitizer()
        self.vulnerability_scanner = VulnerabilityScanner()
        self.compliance_checker = ComplianceChecker()

    def tearDown(self):
        """Limpeza após os testes"""
        # Remove diretórios de teste
        for dir_name in self.config.values():
            if isinstance(dir_name, str) and not dir_name.endswith('.json'):
                if Path(dir_name).exists():
                    shutil.rmtree(dir_name)

    async def test_code_generation_security(self):
        """Testa segurança na geração de código"""
        # Projeto com dados sensíveis
        project_config = {
            'name': 'SecurityTest',
            'type': 'WPF',
            'features': [
                'user_authentication',
                'data_encryption',
                'secure_storage'
            ],
            'security': {
                'require_mfa': True,
                'password_policy': {
                    'min_length': 12,
                    'require_special': True,
                    'require_numbers': True
                }
            }
        }
        
        # Gera projeto
        result = await self.system.create_project(project_config)
        
        # Analisa segurança do código gerado
        security_analysis = await self.security_scanner.scan_project(
            Path(result['project_path'])
        )
        
        # Verifica análise
        self.assertTrue(security_analysis['passed'])
        self.assertLess(
            security_analysis['risk_score'],
            self.config['security_thresholds']['max_risk_score']
        )
        
        # Verifica práticas de segurança específicas
        practices = security_analysis['security_practices']
        
        # Verifica criptografia de senha
        self.assertTrue(practices['password_hashing'])
        self.assertEqual(
            practices['password_hash_algorithm'],
            'PBKDF2_SHA256'
        )
        
        # Verifica proteção contra SQL Injection
        self.assertTrue(practices['sql_injection_protection'])
        self.assertIn('parameterized_queries', practices['sql_protection_methods'])
        
        # Verifica proteção XSS
        self.assertTrue(practices['xss_protection'])
        self.assertIn('html_encoding', practices['xss_protection_methods'])

    async def test_data_security(self):
        """Testa segurança no tratamento de dados"""
        # Cria projeto com dados sensíveis
        project_config = {
            'name': 'DataSecurityTest',
            'type': 'WPF',
            'features': ['data_persistence'],
            'data': {
                'entities': [
                    {
                        'name': 'User',
                        'properties': [
                            {'name': 'Id', 'type': 'int', 'key': True},
                            {'name': 'Email', 'type': 'string', 'sensitive': True},
                            {'name': 'SSN', 'type': 'string', 'sensitive': True},
                            {'name': 'Password', 'type': 'string', 'sensitive': True}
                        ]
                    }
                ]
            }
        }
        
        # Gera projeto
        result = await self.system.create_project(project_config)
        
        # Analisa tratamento de dados sensíveis
        data_analysis = await self.security_scanner.analyze_data_security(
            Path(result['project_path'])
        )
        
        # Verifica proteções de dados
        self.assertTrue(data_analysis['data_protection']['encryption_at_rest'])
        self.assertTrue(data_analysis['data_protection']['encryption_in_transit'])
        
        # Verifica mascaramento de dados sensíveis
        self.assertTrue(data_analysis['data_masking']['enabled'])
        self.assertIn('Email', data_analysis['data_masking']['masked_fields'])
        self.assertIn('SSN', data_analysis['data_masking']['masked_fields'])
        
        # Verifica logs de acesso a dados sensíveis
        self.assertTrue(data_analysis['access_logging']['enabled'])
        self.assertIn('SSN', data_analysis['access_logging']['monitored_fields'])

    async def test_security_configuration(self):
        """Testa configurações de segurança"""
        # Configura projeto com várias features de segurança
        project_config = {
            'name': 'SecConfigTest',
            'type': 'WPF',
            'features': ['user_authentication'],
            'security': {
                'authentication': {
                    'type': 'oauth2',
                    'providers': ['google', 'microsoft'],
                    'mfa_required': True
                },
                'authorization': {
                    'type': 'role_based',
                    'roles': ['admin', 'user', 'guest']
                },
                'session': {
                    'timeout': 30,
                    'sliding_expiration': True
                }
            }
        }
        
        # Gera projeto
        result = await self.system.create_project(project_config)
        
        # Analisa configurações
        config_analysis = await self.security_scanner.analyze_security_config(
            Path(result['project_path'])
        )
        
        # Verifica configurações de autenticação
        auth_config = config_analysis['authentication']
        self.assertEqual(auth_config['type'], 'oauth2')
        self.assertTrue(auth_config['mfa']['enabled'])
        self.assertIn('google', auth_config['providers'])
        
        # Verifica configurações de autorização
        authz_config = config_analysis['authorization']
        self.assertEqual(authz_config['type'], 'role_based')
        self.assertIn('admin', authz_config['roles'])
        
        # Verifica gestão de sessão
        session_config = config_analysis['session']
        self.assertEqual(session_config['timeout'], 30)
        self.assertTrue(session_config['sliding_expiration'])

    async def test_compliance(self):
        """Testa conformidade com padrões de segurança"""
        # Gera projeto
        result = await self.system.create_project({
            'name': 'ComplianceTest',
            'type': 'WPF',
            'features': ['user_authentication', 'data_persistence']
        })
        
        # Verifica conformidade
        compliance_results = await self.compliance_checker.check_compliance(
            Path(result['project_path'])
        )
        
        # Verifica score geral
        self.assertGreater(
            compliance_results['compliance_score'],
            self.config['security_thresholds']['min_compliance_score']
        )
        
        # Verifica OWASP
        owasp = compliance_results['owasp_compliance']
        self.assertTrue(owasp['input_validation'])
        self.assertTrue(owasp['output_encoding'])
        self.assertTrue(owasp['sql_injection_prevention'])
        
        # Verifica GDPR
        gdpr = compliance_results['gdpr_compliance']
        self.assertTrue(gdpr['data_protection'])
        self.assertTrue(gdpr['consent_management'])
        self.assertTrue(gdpr['data_portability'])
        
        # Verifica PCI DSS (se aplicável)
        if 'payment_processing' in project_config['features']:
            pci = compliance_results['pci_compliance']
            self.assertTrue(pci['data_encryption'])
            self.assertTrue(pci['key_management'])

    async def test_security_updates(self):
        """Testa processo de atualização de segurança"""
        # Cria projeto inicial
        result = await self.system.create_project({
            'name': 'UpdateTest',
            'type': 'WPF',
            'features': ['user_authentication']
        })
        
        # Simula vulnerabilidade descoberta
        vulnerability = {
            'type': 'dependency',
            'package': 'Auth.Library',
            'version': '1.0.0',
            'severity': 'high',
            'cve': 'CVE-2024-1234'
        }
        
        # Aplica atualização de segurança
        update_result = await self.system.apply_security_update(
            result['project_id'],
            vulnerability
        )
        
        # Verifica atualização
        self.assertTrue(update_result['success'])
        self.assertEqual(
            update_result['updated_package']['version'],
            '1.0.1'  # Versão corrigida
        )
        
        # Verifica se vulnerabilidade foi resolvida
        post_update_scan = await self.vulnerability_scanner.scan_project(
            Path(result['project_path'])
        )
        self.assertNotIn(
            'CVE-2024-1234',
            [v['cve'] for v in post_update_scan['vulnerabilities']]
        )

if __name__ == '__main__':
    unittest.main()