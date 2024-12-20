# tests/security/test_security_agent.py
import unittest
import asyncio
from unittest.mock import MagicMock, patch
from pathlib import Path
from datetime import datetime, timedelta

from tools.security.security_agent import SecurityAgent

class TestSecurityAgent(unittest.TestCase):
    def setUp(self):
        self.config = {
            'scan_interval': 3600,
            'max_retries': 3,
            'log_level': 'INFO'
        }
        self.agent = SecurityAgent(self.config)
        self.test_path = Path("test_project")

    def tearDown(self):
        # Limpa arquivos de teste
        if self.test_path.exists():
            import shutil
            shutil.rmtree(self.test_path)

    async def asyncSetUp(self):
        # Setup assíncrono se necessário
        self.test_path.mkdir(exist_ok=True)
        
        # Cria alguns arquivos de teste
        (self.test_path / "test.cs").write_text('''
            public class TestClass {
                private string password = "123456";  // Vulnerabilidade de teste
                public void TestMethod() {
                    string query = "SELECT * FROM Users WHERE id = " + userId;  // Vulnerabilidade de teste
                }
            }
        ''')

    def test_init(self):
        """Testa inicialização do agente"""
        self.assertIsNotNone(self.agent)
        self.assertEqual(self.agent.config, self.config)
        self.assertIsNotNone(self.agent.logger)

    @patch('tools.security.security_agent.SecurityAgent._scan_vulnerabilities')
    async def test_analyze_security(self, mock_scan):
        """Testa análise de segurança completa"""
        # Mock de vulnerabilidades
        mock_scan.return_value = [{
            'type': 'hardcoded_credential',
            'severity': 'high',
            'file': 'test.cs',
            'line': 2
        }]

        results = await self.agent.analyze_security(self.test_path)
        
        self.assertIn('vulnerabilities', results)
        self.assertIn('code_quality', results)
        self.assertIn('compliance', results)
        self.assertIn('timestamp', results)

        # Verifica se encontrou vulnerabilidades
        self.assertTrue(len(results['vulnerabilities']) > 0)
        
        # Verifica formatação do resultado
        vuln = results['vulnerabilities'][0]
        self.assertIn('type', vuln)
        self.assertIn('severity', vuln)
        self.assertIn('file', vuln)
        self.assertIn('line', vuln)

    async def test_scan_security_patterns(self):
        """Testa scan de padrões de segurança"""
        await self.asyncSetUp()
        
        patterns = [
            {'pattern': r'password\s*=\s*["\'].*["\']', 'severity': 'high'},
            {'pattern': r'string\.Format.*SELECT', 'severity': 'high'}
        ]
        
        results = await self.agent._scan_patterns(self.test_path, patterns)
        
        # Deve encontrar as duas vulnerabilidades de teste
        self.assertEqual(len(results), 2)
        
        # Verifica primeira vulnerabilidade
        self.assertEqual(results[0]['severity'], 'high')
        self.assertIn('password', results[0]['match'])
        
        # Verifica segunda vulnerabilidade
        self.assertEqual(results[1]['severity'], 'high')
        self.assertIn('SELECT', results[1]['match'])

    @patch('tools.security.security_agent.SecurityAgent._check_owasp_compliance')
    async def test_check_compliance(self, mock_check):
        """Testa verificação de compliance"""
        # Mock de resultados OWASP
        mock_check.return_value = [{
            'rule_id': 'A1',
            'compliant': False,
            'description': 'SQL Injection vulnerability found'
        }]

        results = await self.agent._check_compliance(self.test_path)
        
        self.assertTrue(len(results) > 0)
        self.assertIn('rule_id', results[0])
        self.assertIn('compliant', results[0])
        self.assertIn('description', results[0])

    async def test_generate_security_report(self):
        """Testa geração de relatório de segurança"""
        analysis_results = {
            'vulnerabilities': [{
                'type': 'sql_injection',
                'severity': 'high',
                'file': 'test.cs',
                'line': 4
            }],
            'code_quality': [],
            'compliance': [{
                'rule_id': 'A1',
                'compliant': False
            }]
        }

        report = await self.agent.generate_security_report(analysis_results)
        
        # Verifica estrutura do relatório
        self.assertIn('summary', report)
        self.assertIn('details', report)
        self.assertIn('recommendations', report)
        self.assertIn('timestamp', report)
        
        # Verifica contagem de issues
        self.assertEqual(
            report['summary']['total_issues'],
            len(analysis_results['vulnerabilities']) +
            len(analysis_results['compliance'])
        )

    def test_severity_counts(self):
        """Testa contagem por severidade"""
        results = {
            'vulnerabilities': [
                {'severity': 'high'},
                {'severity': 'medium'},
                {'severity': 'high'}
            ]
        }
        
        high_count = self.agent._count_severity(results, 'high')
        medium_count = self.agent._count_severity(results, 'medium')
        low_count = self.agent._count_severity(results, 'low')
        
        self.assertEqual(high_count, 2)
        self.assertEqual(medium_count, 1)
        self.assertEqual(low_count, 0)

if __name__ == '__main__':
    unittest.main()